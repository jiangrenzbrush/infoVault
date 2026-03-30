from __future__ import annotations

import base64
import ctypes
import sqlite3
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

from infovault_i18n import (
    APP_PROTECT_NAME,
    DB_PATH,
    category_storage_value,
    color_storage_value,
    ensure_data_dir,
    importance_key,
    importance_storage_value,
)


class DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


crypt32 = ctypes.windll.crypt32
kernel32 = ctypes.windll.kernel32
crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(DataBlob),
    wintypes.LPCWSTR,
    ctypes.POINTER(DataBlob),
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(DataBlob),
]
crypt32.CryptProtectData.restype = wintypes.BOOL
crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(DataBlob),
    ctypes.POINTER(wintypes.LPWSTR),
    ctypes.POINTER(DataBlob),
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(DataBlob),
]
crypt32.CryptUnprotectData.restype = wintypes.BOOL
kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
kernel32.LocalFree.restype = wintypes.HLOCAL


def _blob_from_bytes(data: bytes) -> tuple[DataBlob, ctypes.Array]:
    buffer = ctypes.create_string_buffer(data)
    blob = DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    return blob, buffer


def protect_text(text: str) -> str:
    if not text:
        return ""

    in_blob, in_buffer = _blob_from_bytes(text.encode("utf-8"))
    out_blob = DataBlob()
    if not crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        APP_PROTECT_NAME,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()

    try:
        encrypted = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return "enc:" + base64.b64encode(encrypted).decode("ascii")
    finally:
        kernel32.LocalFree(out_blob.pbData)
        del in_buffer


def unprotect_text(value: str | None) -> str:
    if not value:
        return ""
    if not value.startswith("enc:"):
        return value

    in_blob, in_buffer = _blob_from_bytes(base64.b64decode(value[4:]))
    out_blob = DataBlob()
    description = wintypes.LPWSTR()
    if not crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        ctypes.byref(description),
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()

    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData).decode("utf-8")
    finally:
        if description:
            kernel32.LocalFree(description)
        kernel32.LocalFree(out_blob.pbData)
        del in_buffer


def today_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return datetime.min


class VaultDatabase:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        ensure_data_dir()
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'cat:other',
                importance TEXT NOT NULL DEFAULT 'imp:medium',
                color_tag TEXT NOT NULL DEFAULT 'clr:auto',
                info_date TEXT NOT NULL,
                website TEXT,
                username TEXT,
                password TEXT,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        columns = {
            row["name"]
            for row in self.conn.execute("PRAGMA table_info(records)").fetchall()
        }
        if "color_tag" not in columns:
            self.conn.execute(
                "ALTER TABLE records ADD COLUMN color_tag TEXT NOT NULL DEFAULT 'clr:auto'"
            )
        self.conn.commit()

    def list_records(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM records").fetchall()
        records: list[dict] = []
        for row in rows:
            category_value = row["category"] or "cat:other"
            importance_value = row["importance"] or "imp:medium"
            records.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "category_value": category_value,
                    "importance_value": importance_value,
                    "importance_key": importance_key(importance_value),
                    "color_value": row["color_tag"] or "clr:auto",
                    "info_date": row["info_date"] or "",
                    "website": unprotect_text(row["website"]),
                    "username": unprotect_text(row["username"]),
                    "password": unprotect_text(row["password"]),
                    "note": unprotect_text(row["note"]),
                    "created_at": row["created_at"] or "",
                    "updated_at": row["updated_at"] or "",
                }
            )
        return records

    def export_backup_payload(self) -> dict:
        return {
            "format": "InfoVaultBackup",
            "version": 1,
            "exported_at": now_string(),
            "records": [
                {
                    "title": record["title"],
                    "category_value": record["category_value"],
                    "importance_value": record["importance_value"],
                    "color_value": record.get("color_value", "clr:auto"),
                    "info_date": record["info_date"],
                    "website": record["website"],
                    "username": record["username"],
                    "password": record["password"],
                    "note": record["note"],
                    "created_at": record["created_at"],
                    "updated_at": record["updated_at"],
                }
                for record in self.list_records()
            ],
        }

    def save_record(self, record_id: int | None, payload: dict) -> int:
        timestamp = now_string()
        data = {
            "title": payload["title"].strip(),
            "category": category_storage_value(payload["category"]),
            "importance": importance_storage_value(payload["importance"]),
            "color_tag": color_storage_value(payload.get("color")),
            "info_date": payload["info_date"].strip() or today_string(),
            "website": protect_text(payload["website"].strip()),
            "username": protect_text(payload["username"].strip()),
            "password": protect_text(payload["password"].strip()),
            "note": protect_text(payload["note"].strip()),
            "updated_at": timestamp,
        }

        if record_id is None:
            cursor = self.conn.execute(
                """
                INSERT INTO records (
                    title, category, importance, color_tag, info_date,
                    website, username, password, note, created_at, updated_at
                )
                VALUES (
                    :title, :category, :importance, :color_tag, :info_date,
                    :website, :username, :password, :note, :created_at, :updated_at
                )
                """,
                {**data, "created_at": timestamp},
            )
            self.conn.commit()
            return int(cursor.lastrowid)

        self.conn.execute(
            """
            UPDATE records
            SET title = :title,
                category = :category,
                importance = :importance,
                color_tag = :color_tag,
                info_date = :info_date,
                website = :website,
                username = :username,
                password = :password,
                note = :note,
                updated_at = :updated_at
            WHERE id = :id
            """,
            {**data, "id": record_id},
        )
        self.conn.commit()
        return record_id

    def import_backup_records(
        self,
        records: list[dict],
        *,
        replace_existing: bool = False,
    ) -> int:
        imported_count = 0
        with self.conn:
            if replace_existing:
                self.conn.execute("DELETE FROM records")

            for raw_record in records:
                title = str(raw_record.get("title", "")).strip()
                if not title:
                    continue

                info_date = str(raw_record.get("info_date") or today_string()).strip()
                created_at = str(raw_record.get("created_at") or now_string()).strip()
                updated_at = str(raw_record.get("updated_at") or now_string()).strip()
                category_value = raw_record.get("category_value") or raw_record.get("category")
                importance_value = raw_record.get("importance_value") or raw_record.get("importance")
                color_value = raw_record.get("color_value") or raw_record.get("color")

                self.conn.execute(
                    """
                    INSERT INTO records (
                        title, category, importance, color_tag, info_date,
                        website, username, password, note, created_at, updated_at
                    )
                    VALUES (
                        :title, :category, :importance, :color_tag, :info_date,
                        :website, :username, :password, :note, :created_at, :updated_at
                    )
                    """,
                    {
                        "title": title,
                        "category": category_storage_value(category_value),
                        "importance": importance_storage_value(importance_value),
                        "color_tag": color_storage_value(color_value),
                        "info_date": info_date,
                        "website": protect_text(str(raw_record.get("website", "")).strip()),
                        "username": protect_text(str(raw_record.get("username", "")).strip()),
                        "password": protect_text(str(raw_record.get("password", "")).strip()),
                        "note": protect_text(str(raw_record.get("note", "")).strip()),
                        "created_at": created_at,
                        "updated_at": updated_at,
                    },
                )
                imported_count += 1

        return imported_count

    def delete_record(self, record_id: int) -> None:
        self.conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

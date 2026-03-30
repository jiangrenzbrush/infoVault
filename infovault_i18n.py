from __future__ import annotations

import json
import sys
from pathlib import Path


DEFAULT_LANGUAGE = "zh-CN"
LANGUAGE_ORDER = ["zh-CN", "en-US"]
APP_PROTECT_NAME = "InfoVault"


TEXT = {
    "zh-CN": {
        "language_name": "\u7b80\u4f53\u4e2d\u6587",
        "app_name": "\u4fe1\u606f\u7ba1\u5bb6",
        "window_title": "\u4fe1\u606f\u7ba1\u5bb6 - \u672c\u5730\u91cd\u8981\u4fe1\u606f\u8bb0\u5f55",
        "subtitle": "\u628a\u804a\u5929\u91cc\u96f6\u6563\u7684\u91cd\u8981\u4fe1\u606f\u96c6\u4e2d\u653e\u5230\u672c\u673a\uff0c\u6309\u65e5\u671f\u3001\u5206\u7c7b\u548c\u91cd\u8981\u7ea7\u522b\u5feb\u901f\u627e\u5230\u3002",
        "language_label": "\u754c\u9762\u8bed\u8a00",
        "filters_title": "\u67e5\u627e\u4e0e\u7b5b\u9009",
        "keyword_label": "\u5173\u952e\u8bcd",
        "category_label": "\u5206\u7c7b",
        "importance_label": "\u91cd\u8981\u7ea7\u522b",
        "color_label": "\u989c\u8272\u6807\u8bb0",
        "date_from_label": "\u8d77\u59cb\u65e5\u671f",
        "date_to_label": "\u7ed3\u675f\u65e5\u671f",
        "filter_button": "\u7b5b\u9009",
        "reset_button": "\u91cd\u7f6e",
        "new_record_button": "\u65b0\u5efa\u8bb0\u5f55",
        "record_list_title": "\u8bb0\u5f55\u5217\u8868",
        "record_count": "{count} \u6761",
        "details_title": "\u8be6\u7ec6\u4fe1\u606f",
        "title_label": "\u6807\u9898",
        "date_label": "\u65e5\u671f",
        "website_label": "\u7f51\u7ad9",
        "open_website_button": "\u6253\u5f00\u7f51\u7ad9",
        "username_label": "\u8d26\u53f7",
        "copy_username_button": "\u590d\u5236\u8d26\u53f7",
        "password_label": "\u5bc6\u7801",
        "toggle_password_button": "\u663e\u793a / \u9690\u85cf",
        "copy_password_button": "\u590d\u5236\u5bc6\u7801",
        "note_label": "\u5907\u6ce8",
        "color_hint": "\u5de6\u4fa7\u5217\u8868\u4f1a\u6309\u8fd9\u91cc\u7684\u989c\u8272\u9ad8\u4eae\u663e\u793a\u3002",
        "color_auto_label": "\u8ddf\u968f\u5206\u7c7b",
        "color_preview_auto": "\u5f53\u524d\u989c\u8272\uff1a\u8ddf\u968f\u5206\u7c7b\uff08{color}\uff09",
        "color_preview_manual": "\u5f53\u524d\u989c\u8272\uff1a{color}",
        "date_hint": "\u65e5\u671f\u683c\u5f0f\u8bf7\u7528 YYYY-MM-DD\uff0c\u4f8b\u5982 2026-03-30\u3002",
        "save_button": "\u4fdd\u5b58\u8bb0\u5f55",
        "delete_button": "\u5220\u9664\u8bb0\u5f55",
        "clear_button": "\u6e05\u7a7a\u8868\u5355",
        "refresh_button": "\u5237\u65b0\u5217\u8868",
        "export_button": "\u5bfc\u51fa\u5907\u4efd",
        "import_button": "\u5bfc\u5165\u5907\u4efd",
        "import_docx_button": "\u5bfc\u5165 DOCX",
        "all_option": "\u5168\u90e8",
        "status_secure": "\u654f\u611f\u5b57\u6bb5\u4ec5\u4fdd\u5b58\u5728\u672c\u673a\uff0c\u5e76\u7ed1\u5b9a\u5f53\u524d Windows \u8d26\u6237\u52a0\u5bc6\u3002",
        "status_filters_reset": "\u7b5b\u9009\u6761\u4ef6\u5df2\u91cd\u7f6e\u3002",
        "status_no_records": "\u6ca1\u6709\u7b26\u5408\u5f53\u524d\u7b5b\u9009\u6761\u4ef6\u7684\u8bb0\u5f55\u3002",
        "status_loaded": "\u8bb0\u5f55\u5df2\u8f7d\u5165\uff0c\u53ef\u4ee5\u76f4\u63a5\u67e5\u770b\u3001\u4fee\u6539\u6216\u590d\u5236\u8d26\u53f7\u5bc6\u7801\u3002",
        "status_saved": "\u8bb0\u5f55\u5df2\u4fdd\u5b58\u5230\u672c\u5730\u6570\u636e\u5e93\u3002",
        "status_saved_overwrite": "\u5df2\u8986\u76d6\u539f\u6709\u8bb0\u5f55\u3002",
        "status_saved_new": "\u5df2\u4fdd\u5b58\u4e3a\u65b0\u8bb0\u5f55\u3002",
        "status_deleted": "\u8bb0\u5f55 #{record_id} \u5df2\u5220\u9664\u3002",
        "status_password_visible": "\u5bc6\u7801\u5df2\u663e\u793a\u3002",
        "status_password_hidden": "\u5bc6\u7801\u5df2\u9690\u85cf\u3002",
        "status_username_copied": "\u8d26\u53f7\u5df2\u590d\u5236\u5230\u526a\u8d34\u677f\u3002",
        "status_password_copied": "\u5bc6\u7801\u5df2\u590d\u5236\u5230\u526a\u8d34\u677f\u3002",
        "status_website_opened": "\u5df2\u5c1d\u8bd5\u5728\u6d4f\u89c8\u5668\u4e2d\u6253\u5f00\u7f51\u7ad9\u3002",
        "status_new_mode": "\u5df2\u5207\u6362\u5230\u65b0\u5efa\u6a21\u5f0f\u3002",
        "status_language_changed": "\u754c\u9762\u8bed\u8a00\u5df2\u5207\u6362\u3002",
        "status_exported": "\u5df2\u5bfc\u51fa {count} \u6761\u8bb0\u5f55\u3002",
        "status_imported_append": "\u5df2\u5bfc\u5165 {count} \u6761\u8bb0\u5f55\uff0c\u5df2\u8ffd\u52a0\u5230\u73b0\u6709\u5217\u8868\u3002",
        "status_imported_replace": "\u5df2\u5bfc\u5165 {count} \u6761\u8bb0\u5f55\uff0c\u5e76\u7528\u5907\u4efd\u5185\u5bb9\u91cd\u5efa\u5217\u8868\u3002",
        "status_docx_imported_append": "\u5df2\u4ece DOCX \u5bfc\u5165 {count} \u6761\u8bb0\u5f55\uff0c\u5df2\u8ffd\u52a0\u5230\u73b0\u6709\u5217\u8868\u3002",
        "status_docx_imported_replace": "\u5df2\u4ece DOCX \u5bfc\u5165 {count} \u6761\u8bb0\u5f55\uff0c\u5e76\u7528\u8fd9\u4e9b\u8bb0\u5f55\u91cd\u5efa\u5217\u8868\u3002",
        "meta_new": "\u65b0\u5efa\u8bb0\u5f55",
        "meta_selected": "\u5df2\u9009\u4e2d #{record_id}  \u00b7  \u521b\u5efa {created_at}  \u00b7  \u66f4\u65b0 {updated_at}",
        "fill_title_warning": "\u8bf7\u5148\u586b\u5199\u6807\u9898\uff0c\u4f8b\u5982\u201c\u82f1\u8bed\u5b66\u4e60\u7f51\u7ad9\u8d26\u53f7\u201d\u3002",
        "save_failed": "\u4fdd\u5b58\u5931\u8d25\uff1a{error}",
        "no_selected_record": "\u5f53\u524d\u6ca1\u6709\u9009\u4e2d\u7684\u8bb0\u5f55\u3002",
        "confirm_delete": "\u786e\u5b9a\u5220\u9664\u8fd9\u6761\u8bb0\u5f55\u5417\uff1f\u5220\u9664\u540e\u65e0\u6cd5\u6062\u590d\u3002",
        "save_choice_title": "\u9009\u62e9\u4fdd\u5b58\u65b9\u5f0f",
        "save_choice_message": "\u4f60\u5f53\u524d\u6b63\u5728\u7f16\u8f91\u4e00\u6761\u5df2\u6709\u8bb0\u5f55\u3002\u8fd9\u6b21\u4fdd\u5b58\uff0c\u4f60\u60f3\u8981\u8986\u76d6\u539f\u8bb0\u5f55\uff0c\u8fd8\u662f\u53e6\u5b58\u4e3a\u65b0\u8bb0\u5f55\uff1f",
        "save_choice_overwrite": "\u8986\u76d6\u5f53\u524d\u8bb0\u5f55",
        "save_choice_duplicate": "\u4fdd\u5b58\u4e3a\u65b0\u8bb0\u5f55",
        "save_choice_cancel": "\u53d6\u6d88",
        "export_title": "\u5bfc\u51fa\u5907\u4efd",
        "export_warning": "\u5bfc\u51fa\u6587\u4ef6\u4f1a\u5305\u542b\u660e\u6587\u7684\u8d26\u53f7\u548c\u5bc6\u7801\uff0c\u4fbf\u4e8e\u5728\u5176\u4ed6\u7535\u8111\u5bfc\u5165\u3002\u8bf7\u786e\u4fdd\u59a5\u5584\u4fdd\u7ba1\u8fd9\u4e2a\u5907\u4efd\u6587\u4ef6\u3002\n\n\u786e\u5b9a\u7ee7\u7eed\u5bfc\u51fa\u5417\uff1f",
        "export_no_records": "\u5f53\u524d\u6ca1\u6709\u53ef\u5bfc\u51fa\u7684\u8bb0\u5f55\u3002",
        "export_failed": "\u5bfc\u51fa\u5931\u8d25\uff1a{error}",
        "import_title": "\u5bfc\u5165\u5907\u4efd",
        "import_invalid": "\u8fd9\u4e2a\u6587\u4ef6\u683c\u5f0f\u65e0\u6548\uff0c\u65e0\u6cd5\u5bfc\u5165\u3002",
        "import_no_records": "\u8fd9\u4e2a\u6587\u4ef6\u91cc\u6ca1\u6709\u53ef\u5bfc\u5165\u7684\u8bb0\u5f55\u3002",
        "import_failed": "\u5bfc\u5165\u5931\u8d25\uff1a{error}",
        "import_choice_title": "\u9009\u62e9\u5bfc\u5165\u65b9\u5f0f",
        "import_choice_message": "\u8fd9\u4e2a\u5bfc\u5165\u6587\u4ef6\u5305\u542b {count} \u6761\u8bb0\u5f55\u3002\n\n\u4f60\u60f3\u628a\u5b83\u4eec\u8ffd\u52a0\u5230\u73b0\u6709\u5217\u8868\uff0c\u8fd8\u662f\u5148\u6e05\u7a7a\u73b0\u6709\u8bb0\u5f55\u518d\u5bfc\u5165\u8fd9\u4e9b\u5185\u5bb9\uff1f",
        "import_choice_append": "\u8ffd\u52a0\u5bfc\u5165",
        "import_choice_replace": "\u6e05\u7a7a\u540e\u5bfc\u5165",
        "import_choice_cancel": "\u53d6\u6d88",
        "import_docx_title": "\u5bfc\u5165 DOCX \u6587\u6863",
        "import_docx_failed": "DOCX \u5bfc\u5165\u5931\u8d25\uff1a{error}",
        "import_docx_no_records": "\u8fd9\u4e2a DOCX \u6587\u6863\u91cc\u6ca1\u6709\u8bc6\u522b\u51fa\u53ef\u5bfc\u5165\u7684\u8bb0\u5f55\u3002",
        "no_username": "\u5f53\u524d\u6ca1\u6709\u53ef\u590d\u5236\u7684\u8d26\u53f7\u3002",
        "no_password": "\u5f53\u524d\u6ca1\u6709\u53ef\u590d\u5236\u7684\u5bc6\u7801\u3002",
        "no_website": "\u5f53\u524d\u6ca1\u6709\u53ef\u6253\u5f00\u7684\u7f51\u7ad9\u5730\u5740\u3002",
        "date_empty": "\u65e5\u671f\u4e0d\u80fd\u4e3a\u7a7a\uff0c\u8bf7\u4f7f\u7528 YYYY-MM-DD \u683c\u5f0f\u3002",
        "date_invalid": "\u65e5\u671f\u683c\u5f0f\u4e0d\u6b63\u786e\uff0c\u8bf7\u4f7f\u7528 YYYY-MM-DD\uff0c\u4f8b\u5982 2026-03-30\u3002",
        "date_range_invalid": "\u7ed3\u675f\u65e5\u671f\u4e0d\u80fd\u65e9\u4e8e\u8d77\u59cb\u65e5\u671f\u3002",
        "windows_only": "\u8fd9\u4e2a\u7248\u672c\u5f53\u524d\u53ea\u652f\u6301 Windows\u3002",
        "col_date": "\u65e5\u671f",
        "col_category": "\u5206\u7c7b",
        "col_importance": "\u7ea7\u522b",
        "col_title": "\u6807\u9898",
        "col_username": "\u8d26\u53f7",
    },
    "en-US": {
        "language_name": "English",
        "app_name": "InfoVault",
        "window_title": "InfoVault - Local Important Information",
        "subtitle": "Keep scattered important information in one local place and find it quickly by date, category, and priority.",
        "language_label": "Language",
        "filters_title": "Search And Filters",
        "keyword_label": "Keyword",
        "category_label": "Category",
        "importance_label": "Priority",
        "color_label": "Color Tag",
        "date_from_label": "From Date",
        "date_to_label": "To Date",
        "filter_button": "Filter",
        "reset_button": "Reset",
        "new_record_button": "New Record",
        "record_list_title": "Records",
        "record_count": "{count} records",
        "details_title": "Details",
        "title_label": "Title",
        "date_label": "Date",
        "website_label": "Website",
        "open_website_button": "Open Website",
        "username_label": "Username",
        "copy_username_button": "Copy Username",
        "password_label": "Password",
        "toggle_password_button": "Show / Hide",
        "copy_password_button": "Copy Password",
        "note_label": "Notes",
        "color_hint": "The record list on the left will highlight rows with this color.",
        "color_auto_label": "Follow Category",
        "color_preview_auto": "Current color: follow category ({color})",
        "color_preview_manual": "Current color: {color}",
        "date_hint": "Use YYYY-MM-DD for dates, for example 2026-03-30.",
        "save_button": "Save Record",
        "delete_button": "Delete Record",
        "clear_button": "Clear Form",
        "refresh_button": "Refresh List",
        "export_button": "Export Backup",
        "import_button": "Import Backup",
        "import_docx_button": "Import DOCX",
        "all_option": "All",
        "status_secure": "Sensitive fields stay on this computer and are encrypted for the current Windows account.",
        "status_filters_reset": "Filters were reset.",
        "status_no_records": "No records match the current filters.",
        "status_loaded": "Record loaded. You can review, edit, or copy the username and password.",
        "status_saved": "Record saved to the local database.",
        "status_saved_overwrite": "The existing record was overwritten.",
        "status_saved_new": "Saved as a new record.",
        "status_deleted": "Record #{record_id} was deleted.",
        "status_password_visible": "Password is now visible.",
        "status_password_hidden": "Password is now hidden.",
        "status_username_copied": "Username copied to the clipboard.",
        "status_password_copied": "Password copied to the clipboard.",
        "status_website_opened": "Tried opening the website in your browser.",
        "status_new_mode": "Switched to new record mode.",
        "status_language_changed": "Interface language updated.",
        "status_exported": "Exported {count} records.",
        "status_imported_append": "Imported {count} records and added them to the current list.",
        "status_imported_replace": "Imported {count} records and rebuilt the list from the backup.",
        "status_docx_imported_append": "Imported {count} records from DOCX and added them to the current list.",
        "status_docx_imported_replace": "Imported {count} records from DOCX and rebuilt the list with them.",
        "meta_new": "New record",
        "meta_selected": "Selected #{record_id}  ·  Created {created_at}  ·  Updated {updated_at}",
        "fill_title_warning": "Please enter a title first, for example \"English learning site account\".",
        "save_failed": "Save failed: {error}",
        "no_selected_record": "There is no selected record.",
        "confirm_delete": "Delete this record? This action cannot be undone.",
        "save_choice_title": "Choose Save Mode",
        "save_choice_message": "You are editing an existing record. Do you want to overwrite the current record or save this as a new record?",
        "save_choice_overwrite": "Overwrite Current Record",
        "save_choice_duplicate": "Save As New Record",
        "save_choice_cancel": "Cancel",
        "export_title": "Export Backup",
        "export_warning": "The exported file will contain usernames and passwords in plain text so it can be imported on another computer. Please keep the backup file somewhere safe.\n\nDo you want to continue?",
        "export_no_records": "There are no records to export.",
        "export_failed": "Export failed: {error}",
        "import_title": "Import Backup",
        "import_invalid": "This file format is invalid and cannot be imported.",
        "import_no_records": "This file does not contain any records to import.",
        "import_failed": "Import failed: {error}",
        "import_choice_title": "Choose Import Mode",
        "import_choice_message": "This import file contains {count} records.\n\nDo you want to append them to the current list, or clear the current list and import these records?",
        "import_choice_append": "Append Import",
        "import_choice_replace": "Clear And Import",
        "import_choice_cancel": "Cancel",
        "import_docx_title": "Import DOCX Document",
        "import_docx_failed": "DOCX import failed: {error}",
        "import_docx_no_records": "No importable records were detected in this DOCX document.",
        "no_username": "There is no username to copy.",
        "no_password": "There is no password to copy.",
        "no_website": "There is no website address to open.",
        "date_empty": "Date cannot be empty. Please use YYYY-MM-DD.",
        "date_invalid": "Date format is invalid. Please use YYYY-MM-DD, for example 2026-03-30.",
        "date_range_invalid": "The end date cannot be earlier than the start date.",
        "windows_only": "This version currently supports Windows only.",
        "col_date": "Date",
        "col_category": "Category",
        "col_importance": "Priority",
        "col_title": "Title",
        "col_username": "Username",
    },
}


CATEGORY_KEYS = [
    "learning_sites",
    "work_materials",
    "family_tasks",
    "finance_accounts",
    "shopping_platforms",
    "software_licenses",
    "document_info",
    "other",
]

CATEGORY_LABELS = {
    "zh-CN": {
        "learning_sites": "\u5b66\u4e60\u7f51\u7ad9",
        "work_materials": "\u5de5\u4f5c\u8d44\u6599",
        "family_tasks": "\u5bb6\u5ead\u4e8b\u52a1",
        "finance_accounts": "\u91d1\u878d\u8d26\u53f7",
        "shopping_platforms": "\u8d2d\u7269\u5e73\u53f0",
        "software_licenses": "\u8f6f\u4ef6\u6388\u6743",
        "document_info": "\u8bc1\u4ef6\u4fe1\u606f",
        "other": "\u5176\u4ed6",
    },
    "en-US": {
        "learning_sites": "Learning Sites",
        "work_materials": "Work Materials",
        "family_tasks": "Family Tasks",
        "finance_accounts": "Finance Accounts",
        "shopping_platforms": "Shopping Platforms",
        "software_licenses": "Software Licenses",
        "document_info": "Document Info",
        "other": "Other",
    },
}

IMPORTANCE_KEYS = ["urgent", "high", "medium", "low"]
IMPORTANCE_LABELS = {
    "zh-CN": {
        "urgent": "\u7d27\u6025",
        "high": "\u9ad8",
        "medium": "\u4e2d",
        "low": "\u4f4e",
    },
    "en-US": {
        "urgent": "Urgent",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    },
}
IMPORTANCE_ORDER = {"urgent": 3, "high": 2, "medium": 1, "low": 0}

COLOR_KEYS = ["auto", "red", "orange", "yellow", "green", "blue", "purple", "pink", "gray"]
COLOR_LABELS = {
    "zh-CN": {
        "auto": "\u8ddf\u968f\u5206\u7c7b",
        "red": "\u7ea2\u8272",
        "orange": "\u6a59\u8272",
        "yellow": "\u9ec4\u8272",
        "green": "\u7eff\u8272",
        "blue": "\u84dd\u8272",
        "purple": "\u7d2b\u8272",
        "pink": "\u7c89\u8272",
        "gray": "\u7070\u8272",
    },
    "en-US": {
        "auto": "Follow Category",
        "red": "Red",
        "orange": "Orange",
        "yellow": "Yellow",
        "green": "Green",
        "blue": "Blue",
        "purple": "Purple",
        "pink": "Pink",
        "gray": "Gray",
    },
}
COLOR_HEX = {
    "red": "#FEE2E2",
    "orange": "#FFEDD5",
    "yellow": "#FEF3C7",
    "green": "#DCFCE7",
    "blue": "#DBEAFE",
    "purple": "#EDE9FE",
    "pink": "#FCE7F3",
    "gray": "#E5E7EB",
}
CATEGORY_COLOR_MAP = {
    "learning_sites": "blue",
    "work_materials": "green",
    "family_tasks": "pink",
    "finance_accounts": "orange",
    "shopping_platforms": "purple",
    "software_licenses": "yellow",
    "document_info": "red",
    "other": "gray",
}


def runtime_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_DIR = runtime_base_dir()
DATA_DIR = APP_DIR / "data"
DB_PATH = DATA_DIR / "vault.db"
SETTINGS_PATH = DATA_DIR / "settings.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict:
    ensure_data_dir()
    if not SETTINGS_PATH.exists():
        return {}
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_settings(settings: dict) -> None:
    ensure_data_dir()
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def alias_key(value: str) -> str:
    return value.strip().casefold()


def category_key(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if text.startswith("cat:"):
        key = text[4:]
        return key if key in CATEGORY_KEYS else None
    for language in LANGUAGE_ORDER:
        for key, label in CATEGORY_LABELS[language].items():
            if alias_key(label) == alias_key(text):
                return key
    return None


def category_display(value: str | None, language: str) -> str:
    key = category_key(value)
    if key:
        return CATEGORY_LABELS[language][key]
    return (value or "").strip()


def category_storage_value(value: str | None) -> str:
    key = category_key(value)
    if key:
        return f"cat:{key}"
    return (value or "").strip() or "cat:other"


def importance_key(value: str | None) -> str:
    if not value:
        return "medium"
    text = value.strip()
    if text.startswith("imp:"):
        key = text[4:]
        return key if key in IMPORTANCE_KEYS else "medium"
    for language in LANGUAGE_ORDER:
        for key, label in IMPORTANCE_LABELS[language].items():
            if alias_key(label) == alias_key(text):
                return key
    return "medium"


def importance_display(value: str | None, language: str) -> str:
    return IMPORTANCE_LABELS[language][importance_key(value)]


def importance_storage_value(value: str | None) -> str:
    return f"imp:{importance_key(value)}"


def color_key(value: str | None) -> str:
    if not value:
        return "auto"
    text = value.strip()
    if text.startswith("clr:"):
        key = text[4:]
        return key if key in COLOR_KEYS else "auto"
    for language in LANGUAGE_ORDER:
        for key, label in COLOR_LABELS[language].items():
            if alias_key(label) == alias_key(text):
                return key
    return "auto"


def color_display(value: str | None, language: str) -> str:
    return COLOR_LABELS[language][color_key(value)]


def color_storage_value(value: str | None) -> str:
    return f"clr:{color_key(value)}"


def resolve_color_key(color_value: str | None, category_value: str | None) -> str:
    selected = color_key(color_value)
    if selected != "auto":
        return selected
    category = category_key(category_value)
    if category and category in CATEGORY_COLOR_MAP:
        return CATEGORY_COLOR_MAP[category]
    return "gray"


def resolve_color_hex(color_value: str | None, category_value: str | None) -> str:
    return COLOR_HEX[resolve_color_key(color_value, category_value)]

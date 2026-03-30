from __future__ import annotations

import re
import zipfile
from datetime import datetime
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
WORD_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

DATE_RE = re.compile(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
LICENSE_RE = re.compile(r"\b[A-Z0-9]{3,}(?:-[A-Z0-9]{3,}){2,}\b", re.IGNORECASE)
STRICT_EMAIL_RE = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.(?:COM|NET|ORG|CA|IO|EDU|ME|CO|LIVE|APP|AI)(?![A-Z0-9])",
    re.IGNORECASE,
)
GLUED_EMAIL_RE = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.(?:COM|NET|ORG|CA|IO|EDU|ME|CO|LIVE|APP|AI)(?=[A-Z0-9@#&!_+\-]|$)",
    re.IGNORECASE,
)
URL_RE = re.compile(
    r"\b(?:https?://)?(?:www\.)?[A-Z0-9][A-Z0-9-]*(?:\.[A-Z0-9-]+)+(?:/[^\s]*)?\b",
    re.IGNORECASE,
)

FIELD_ALIASES = {
    "title": [
        "\u6807\u9898",
        "\u540d\u79f0",
        "\u5e73\u53f0",
        "\u7f51\u7ad9\u540d",
        "\u9879\u76ee",
        "title",
        "name",
        "platform",
        "service",
    ],
    "website": [
        "\u7f51\u7ad9",
        "\u7f51\u5740",
        "\u94fe\u63a5",
        "\u5730\u5740",
        "url",
        "website",
        "web",
        "login url",
    ],
    "username": [
        "\u8d26\u53f7",
        "\u7528\u6237\u540d",
        "\u90ae\u7bb1",
        "\u767b\u5f55\u540d",
        "\u767b\u5f55\u8d26\u53f7",
        "user",
        "username",
        "account",
        "email",
        "login",
        "id",
    ],
    "password": [
        "\u5bc6\u7801",
        "\u53e3\u4ee4",
        "pass",
        "password",
        "pwd",
        "pin",
        "serial",
        "license",
    ],
    "note": [
        "\u5907\u6ce8",
        "\u8bf4\u660e",
        "\u8865\u5145",
        "note",
        "notes",
        "memo",
        "remark",
        "remarks",
        "info",
        "\u4fe1\u606f",
    ],
    "category": ["\u5206\u7c7b", "\u7c7b\u522b", "category", "type"],
    "importance": ["\u91cd\u8981\u7ea7\u522b", "\u4f18\u5148\u7ea7", "\u7ea7\u522b", "priority", "importance", "level"],
    "date": ["\u65e5\u671f", "\u65f6\u95f4", "date", "updated", "created"],
}

HEADER_ALIASES = {
    "title": FIELD_ALIASES["title"],
    "website": FIELD_ALIASES["website"],
    "username": FIELD_ALIASES["username"],
    "password": FIELD_ALIASES["password"],
    "note": FIELD_ALIASES["note"],
    "category": FIELD_ALIASES["category"],
    "importance": FIELD_ALIASES["importance"],
    "date": FIELD_ALIASES["date"],
}

PLATFORM_KEYWORDS = {
    "icloud",
    "epic",
    "yoco",
    "microsoft",
    "micsoft",
    "meta",
    "instagram",
    "idm",
    "erzi",
    "cibc",
    "pinterest",
    "ftq.re",
    "paypal",
    "artstation",
    "daz",
    "ea",
    "gog",
    "facebook",
    "sock",
    "vampire",
    "autodesk",
    "auto desk",
    "twitter",
    "linked",
    "linkedin",
    "windows",
    "face",
    "fibershop",
    "roblox",
    "ubisoft",
    "steam",
    "activision",
    "nintendo",
    "patreon",
    "\u96c5\u601d",
    "\u6218\u7f51",
    "\u4efb\u5929\u5802",
    "\u6ef4\u6ef4\u51fa\u884c\u4f01\u4e1a\u7248",
}
PLATFORM_KEYWORDS_FLAT = {re.sub(r"\s+", "", item.casefold()) for item in PLATFORM_KEYWORDS}

CATEGORY_RULES = [
    (
        "document_info",
        [
            "passport",
            "id card",
            "driver license",
            "visa",
            "\u62a4\u7167",
            "\u8eab\u4efd\u8bc1",
            "\u9a7e\u7167",
            "\u8bc1\u4ef6",
            "\u7b7e\u8bc1",
        ],
    ),
    (
        "software_licenses",
        [
            "license",
            "serial",
            "activation",
            "product key",
            "adobe",
            "microsoft",
            "windows",
            "autodesk",
            "idm",
            "epic",
            "ea",
            "gog",
            "steam",
            "ubisoft",
            "activision",
            "roblox",
            "daz",
            "zbrush",
            "fibershop",
            "patreon",
            "\u8f6f\u4ef6",
            "\u6388\u6743",
            "\u5e8f\u5217\u53f7",
            "\u6fc0\u6d3b\u7801",
            "\u6ce8\u518c\u7801",
            "\u6218\u7f51",
            "\u4efb\u5929\u5802",
        ],
    ),
    (
        "finance_accounts",
        [
            "bank",
            "paypal",
            "visa",
            "mastercard",
            "amex",
            "stripe",
            "finance",
            "cibc",
            "bmo",
            "\u94f6\u884c",
            "\u4fe1\u7528\u5361",
            "\u94f6\u884c\u5361",
            "\u652f\u4ed8",
            "\u8499\u7279\u5229\u5c14\u94f6\u884c",
        ],
    ),
    (
        "shopping_platforms",
        [
            "amazon",
            "taobao",
            "tmall",
            "jd",
            "ebay",
            "temu",
            "aliexpress",
            "shop",
            "\u8d2d\u7269",
            "\u5546\u57ce",
            "\u8ba2\u5355",
        ],
    ),
    (
        "learning_sites",
        [
            "coursera",
            "udemy",
            "edx",
            "classroom",
            "academy",
            "course",
            "lesson",
            "tutorial",
            "school",
            "study",
            "learn",
            "ielts",
            "\u5b66\u4e60",
            "\u8bfe\u7a0b",
            "\u6559\u80b2",
            "\u57f9\u8bad",
            "\u96c5\u601d",
        ],
    ),
    (
        "work_materials",
        [
            "work",
            "office",
            "company",
            "jira",
            "confluence",
            "slack",
            "notion",
            "sharepoint",
            "github",
            "gitlab",
            "twitter",
            "facebook",
            "linkedin",
            "instagram",
            "artstation",
            "pinterest",
            "\u5de5\u4f5c",
            "\u529e\u516c",
            "\u516c\u53f8",
            "\u9879\u76ee",
        ],
    ),
    (
        "family_tasks",
        [
            "family",
            "home",
            "kid",
            "kids",
            "house",
            "erzi",
            "\u5bb6\u5ead",
            "\u5bb6\u4eba",
            "\u5b69\u5b50",
            "\u7236\u6bcd",
            "\u5bb6\u91cc",
            "\u513f\u5b50",
        ],
    ),
]

URGENT_TERMS = ["urgent", "critical", "important", "\u7d27\u6025", "\u9a6c\u4e0a", "\u91cd\u8981"]


def parse_docx_records(file_path: str) -> list[dict]:
    items = _read_docx_items(file_path)
    records: list[dict] = []
    buffered_lines: list[str] = []

    for item_type, payload in items:
        if item_type == "paragraph":
            buffered_lines.append(str(payload))
            continue

        if buffered_lines:
            records.extend(_records_from_lines(buffered_lines))
            buffered_lines = []

        records.extend(_records_from_table(payload))

    if buffered_lines:
        records.extend(_records_from_lines(buffered_lines))

    finalized: list[dict] = []
    for index, record in enumerate(records, start=1):
        normalized = _finalize_record(record, index)
        if normalized:
            finalized.append(normalized)
    return finalized


def _read_docx_items(file_path: str) -> list[tuple[str, object]]:
    try:
        with zipfile.ZipFile(file_path) as archive:
            xml_data = archive.read("word/document.xml")
    except (FileNotFoundError, KeyError, OSError, zipfile.BadZipFile) as exc:
        raise ValueError("invalid_docx") from exc

    root = ET.fromstring(xml_data)
    body = root.find("w:body", WORD_NS)
    if body is None:
        return []

    items: list[tuple[str, object]] = []
    for child in body:
        if child.tag == f"{WORD_TAG}p":
            items.append(("paragraph", _paragraph_text(child)))
        elif child.tag == f"{WORD_TAG}tbl":
            table_rows: list[list[str]] = []
            for row in child.findall("w:tr", WORD_NS):
                cells: list[str] = []
                for cell in row.findall("w:tc", WORD_NS):
                    cell_lines = [_paragraph_text(p) for p in cell.findall("w:p", WORD_NS)]
                    cell_text = "\n".join(line for line in cell_lines if line).strip()
                    cells.append(cell_text)
                table_rows.append(cells)
            items.append(("table", table_rows))
    return items


def _paragraph_text(paragraph: ET.Element) -> str:
    text = "".join(node.text or "" for node in paragraph.findall(".//w:t", WORD_NS))
    return _normalize_line(text)


def _records_from_table(table_rows: list[list[str]]) -> list[dict]:
    if not table_rows:
        return []

    header_map = [_header_field_name(cell) for cell in table_rows[0]]
    header_count = sum(1 for item in header_map if item)
    if header_count >= 2 and any(item in {"title", "website", "username", "password"} for item in header_map):
        records: list[dict] = []
        for row in table_rows[1:]:
            if not any(_normalize_line(cell) for cell in row):
                continue
            record = _empty_record()
            extras: list[str] = []
            for index, cell in enumerate(row):
                value = _normalize_line(cell)
                if not value:
                    continue
                field_name = header_map[index] if index < len(header_map) else None
                if not field_name:
                    extras.append(value)
                elif field_name == "note":
                    _append_note(record, value)
                else:
                    _merge_field(record, field_name, value)
            for value in extras:
                _append_note(record, value)
            records.append(record)
        return records

    fallback_lines: list[str] = []
    for row in table_rows:
        cleaned = [_normalize_line(cell) for cell in row if _normalize_line(cell)]
        if not cleaned:
            fallback_lines.append("")
        elif len(cleaned) == 2 and _field_name(cleaned[0]):
            fallback_lines.append(f"{cleaned[0]}: {cleaned[1]}")
        else:
            fallback_lines.append(" | ".join(cleaned))
    return _records_from_lines(fallback_lines)


def _records_from_lines(lines: list[str]) -> list[dict]:
    records: list[dict] = []
    current = _empty_record()

    for line in (_normalize_line(item) for item in lines):
        if not line:
            if _record_has_content(current):
                records.append(current)
            current = _empty_record()
            continue

        if _record_has_content(current) and _should_start_new_record(current, line):
            records.append(current)
            current = _empty_record()

        _apply_line(current, line)

    if _record_has_content(current):
        records.append(current)
    return records


def _empty_record() -> dict[str, str]:
    return {
        "title": "",
        "website": "",
        "username": "",
        "password": "",
        "note": "",
        "category": "",
        "importance": "",
        "date": "",
    }


def _record_has_content(record: dict[str, str]) -> bool:
    return any(str(record.get(field, "")).strip() for field in record)


def _record_needs_followup(record: dict[str, str]) -> bool:
    has_title = bool(record["title"])
    has_access = bool(record["username"] or record["website"])
    has_password = bool(record["password"])

    if has_title and not has_access:
        return True
    if has_title and not has_password:
        return True
    if not has_title and has_access and not has_password:
        return True
    if not has_title and has_password and not has_access:
        return True
    return False


def _should_start_new_record(record: dict[str, str], line: str) -> bool:
    parsed = _parse_inline_bits(line)
    current_needs_followup = _record_needs_followup(record)
    email_only = bool(parsed["username"]) and _normalize_line(line).casefold() == str(parsed["username"]).casefold()

    if current_needs_followup:
        if record["title"] and record["password"] and (
            parsed["title"] or parsed["website"] or (parsed["username"] and parsed["password"])
        ):
            return True
        if not record["title"] and parsed["title"] and (record["username"] or record["password"]):
            return True
        return False

    if parsed["title"] or parsed["website"]:
        return True
    if email_only:
        return True
    if not record["title"] and (parsed["username"] or parsed["password"]):
        return True
    return False


def _apply_line(record: dict[str, str], line: str) -> None:
    field_name, value = _split_labeled_line(line)
    if field_name:
        if field_name == "note":
            _append_note(record, value)
        else:
            _merge_field(record, field_name, value)
        return

    parsed = _parse_inline_bits(line)
    for name in ("title", "website", "username", "password"):
        _merge_field(record, name, parsed[name])
    for extra in parsed["notes"]:
        _append_note(record, str(extra))


def _parse_inline_bits(line: str) -> dict[str, object]:
    result: dict[str, object] = {
        "title": "",
        "website": "",
        "username": "",
        "password": "",
        "notes": [],
    }

    working = _normalize_line(line)
    for index, email in enumerate(_find_emails(working)):
        if index == 0:
            result["username"] = email
        else:
            result["notes"].append(email)
        working = working.replace(email, " ", 1)

    raw_url, normalized_url = _extract_url_bits(working)
    if normalized_url:
        result["website"] = normalized_url
        working = working.replace(raw_url, " ", 1)

    working = _normalize_line(working)
    working, trailing_password = _split_trailing_password(working)
    if trailing_password:
        result["password"] = trailing_password

    tokens = working.split()
    if not tokens:
        return result

    if result["username"] or result["website"]:
        leading_password, remaining_tokens = _consume_password_prefix(tokens)
        if leading_password and not result["password"]:
            result["password"] = leading_password
            tokens = remaining_tokens
        elif tokens and _looks_like_password(tokens[-1]) and not result["password"]:
            result["password"] = tokens[-1]
            tokens = tokens[:-1]

        title_text = " ".join(tokens).strip()
        if title_text:
            if result["website"] and len(tokens) == 1 and not _looks_like_title_phrase(title_text):
                result["notes"].append(title_text)
            else:
                result["title"] = title_text
        return result

    if tokens and _looks_like_password(tokens[-1]) and not result["password"]:
        result["password"] = tokens[-1]
        tokens = tokens[:-1]
        _assign_tokens_with_password(result, tokens)
        return result

    if result["password"]:
        _assign_tokens_with_password(result, tokens)
        return result

    if len(tokens) == 1:
        token = tokens[0]
        if _looks_like_password(token):
            result["password"] = token
        elif _looks_like_title_phrase(token):
            result["title"] = token
        else:
            result["username"] = token
        return result

    joined = " ".join(tokens)
    last_token = tokens[-1]
    prefix = " ".join(tokens[:-1]).strip()
    if len(tokens) == 2 and _looks_like_username_token(tokens[0]) and _looks_like_soft_password(tokens[1]):
        result["username"] = tokens[0]
        result["password"] = tokens[1]
    elif _looks_like_title_phrase(joined):
        result["title"] = joined
    elif prefix and _looks_like_title_phrase(prefix) and _looks_like_username_token(last_token):
        result["title"] = prefix
        result["username"] = last_token
    else:
        result["username"] = joined
    return result


def _assign_tokens_with_password(result: dict[str, object], tokens: list[str]) -> None:
    if not tokens:
        return

    if len(tokens) == 1:
        token = tokens[0]
        if _looks_like_title_phrase(token):
            result["title"] = token
        elif _looks_like_username_token(token):
            result["username"] = token
        else:
            result["notes"].append(token)
        return

    joined = " ".join(tokens)
    last_token = tokens[-1]
    prefix = " ".join(tokens[:-1]).strip()
    joined_flat = re.sub(r"\s+", "", joined.casefold())
    if prefix and _looks_like_title_phrase(prefix) and _looks_like_username_token(last_token) and joined_flat not in PLATFORM_KEYWORDS_FLAT:
        result["title"] = prefix
        result["username"] = last_token
    elif _looks_like_title_phrase(joined):
        result["title"] = joined
    else:
        result["username"] = joined


def _consume_password_prefix(tokens: list[str]) -> tuple[str, list[str]]:
    if tokens and _looks_like_password(tokens[0]):
        return tokens[0], tokens[1:]
    return "", tokens


def _merge_field(record: dict[str, str], field_name: str, value: object) -> None:
    normalized = _normalize_line(str(value or ""))
    if not normalized:
        return

    if field_name == "website":
        _raw_url, normalized_website = _extract_url_bits(normalized)
        normalized = normalized_website or normalized

    current = record[field_name]
    if not current:
        record[field_name] = normalized
        return

    if current.casefold() == normalized.casefold():
        return

    _append_note(record, f"{field_name}: {normalized}")


def _append_note(record: dict[str, str], value: str) -> None:
    normalized = _normalize_line(value)
    if not normalized:
        return
    existing = [item.strip() for item in record["note"].splitlines() if item.strip()]
    if any(item.casefold() == normalized.casefold() for item in existing):
        return
    existing.append(normalized)
    record["note"] = "\n".join(existing)


def _split_trailing_password(text: str) -> tuple[str, str]:
    if not text or " " in text:
        return text, ""

    matched = re.match(r"^(.*?)([A-Z0-9@#&!_+\-]{6,})$", text, re.IGNORECASE)
    if not matched:
        return text, ""

    prefix = matched.group(1).strip()
    candidate = matched.group(2).strip()
    if not prefix or not _looks_like_password(candidate):
        return text, ""
    if not (_looks_like_title_phrase(prefix) or CJK_RE.search(prefix)):
        return text, ""
    return prefix, candidate


def _find_emails(text: str) -> list[str]:
    normalized = _normalize_line(text)
    candidates: list[str] = []
    seen: set[str] = set()
    for pattern in (STRICT_EMAIL_RE, GLUED_EMAIL_RE):
        for matched in pattern.finditer(normalized):
            email = matched.group(0)
            key = email.casefold()
            if key in seen:
                continue
            seen.add(key)
            candidates.append(email)
    return candidates


def _extract_url_bits(text: str) -> tuple[str, str]:
    masked = text
    for email in _find_emails(masked):
        masked = masked.replace(email, " ", 1)

    matched = URL_RE.search(masked)
    if not matched:
        return "", ""

    raw_value = matched.group(0).strip().rstrip(".,;")
    if "@" in raw_value:
        return "", ""
    normalized = raw_value if raw_value.startswith(("http://", "https://")) else f"https://{raw_value}"
    return raw_value, normalized


def _split_labeled_line(line: str) -> tuple[str | None, str]:
    patterns = [
        re.match(r"^\s*([^:：|]{1,24})\s*[:：|]\s*(.+)$", line),
        re.match(r"^\s*([^ ]{1,16})\s+(.+)$", line),
    ]
    for matched in patterns:
        if not matched:
            continue
        label = matched.group(1).strip()
        value = matched.group(2).strip()
        field_name = _field_name(label)
        if field_name and value:
            return field_name, value
    return None, line.strip()


def _field_name(label: str) -> str | None:
    normalized = _normalize_alias(label)
    for field_name, aliases in FIELD_ALIASES.items():
        if any(normalized == _normalize_alias(alias) for alias in aliases):
            return field_name
    return None


def _header_field_name(label: str) -> str | None:
    normalized = _normalize_alias(label)
    for field_name, aliases in HEADER_ALIASES.items():
        if any(normalized == _normalize_alias(alias) for alias in aliases):
            return field_name
    return None


def _normalize_alias(value: str) -> str:
    return re.sub(r"\s+", "", value or "").strip().casefold()


def _normalize_line(value: str) -> str:
    text = (value or "").replace("\u3000", " ")
    text = text.replace("\uff1a", ":").replace("\uff5c", "|").replace("\u3002", " ")
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\.\s+", ".", text)
    text = re.sub(r"\.([A-Za-z]{2})\s+([A-Za-z])\b", r".\1\2", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _looks_like_password(token: str) -> bool:
    value = token.strip()
    if not value or " " in value:
        return False
    if STRICT_EMAIL_RE.fullmatch(value) or GLUED_EMAIL_RE.fullmatch(value):
        return False
    if URL_RE.fullmatch(value):
        return False
    if LICENSE_RE.fullmatch(value):
        return True

    letters = sum(character.isalpha() for character in value)
    digits = sum(character.isdigit() for character in value)
    password_symbols = sum(character in "@#&!$%*_-+=?" for character in value)
    other_symbols = sum(not character.isalnum() and character not in "@#&!$%*_-+=?" for character in value)

    if digits >= 6 and letters == 0 and password_symbols + other_symbols <= 1:
        return True
    if password_symbols > 0:
        return len(value) >= 5 and (letters > 0 or digits > 0)
    if letters > 0 and digits > 0:
        if value[0].isdigit():
            return True
        if any(character.isupper() for character in value) and digits >= 2:
            return True
        return False
    if digits > 0 and other_symbols > 0:
        return len(value) >= 5
    return False


def _looks_like_username_token(token: str) -> bool:
    value = token.strip()
    if not value or " " in value:
        return False
    if STRICT_EMAIL_RE.fullmatch(value) or GLUED_EMAIL_RE.fullmatch(value):
        return True
    if URL_RE.fullmatch(value):
        return False
    if _looks_like_password(value):
        return False
    if CJK_RE.search(value):
        return False
    return bool(re.fullmatch(r"[A-Z0-9._@-]+", value, re.IGNORECASE))


def _looks_like_soft_password(token: str) -> bool:
    value = token.strip()
    if not value or " " in value:
        return False
    if STRICT_EMAIL_RE.fullmatch(value) or GLUED_EMAIL_RE.fullmatch(value):
        return False
    if URL_RE.fullmatch(value):
        return False
    if _looks_like_password(value):
        return True

    letters = sum(character.isalpha() for character in value)
    digits = sum(character.isdigit() for character in value)
    if letters > 0 and digits >= 4 and value[-1].isdigit():
        return True
    return False


def _looks_like_title_phrase(text: str) -> bool:
    value = _normalize_line(text)
    if not value:
        return False
    if STRICT_EMAIL_RE.fullmatch(value) or GLUED_EMAIL_RE.fullmatch(value):
        return False
    if URL_RE.fullmatch(value):
        return True
    if CJK_RE.search(value):
        return True

    flat_value = re.sub(r"\s+", "", value.casefold())
    if flat_value in PLATFORM_KEYWORDS_FLAT:
        return True

    words = value.split()
    if any(word.casefold() in PLATFORM_KEYWORDS for word in words):
        return True
    if len(words) == 1 and words[0].isalpha() and len(words[0]) <= 4:
        return True
    if "." in value and "@" not in value:
        return True
    return False


def _finalize_record(record: dict[str, str], index: int) -> dict | None:
    title = _normalize_line(record.get("title", ""))
    raw_website = _normalize_line(record.get("website", ""))
    _raw_url, website = _extract_url_bits(raw_website)
    username = _normalize_line(record.get("username", ""))
    password = _normalize_line(record.get("password", ""))
    note = record.get("note", "").strip()
    category_value = _normalize_line(record.get("category", ""))
    importance_value = _normalize_line(record.get("importance", ""))
    info_date = _normalize_date_value(record.get("date", ""))

    if not title:
        title = _title_from_website(website) or username or f"Imported Record {index}"

    if not any([title, website, username, password, note]):
        return None

    auto_category = _infer_category(" ".join(filter(None, [title, website, username, note])))
    auto_importance = _infer_importance(" ".join(filter(None, [title, note])))

    return {
        "title": title,
        "category_value": category_value or f"cat:{auto_category}",
        "importance_value": importance_value or f"imp:{auto_importance}",
        "color_value": "clr:auto",
        "info_date": info_date,
        "website": website,
        "username": username,
        "password": password,
        "note": note,
    }


def _title_from_website(website: str) -> str:
    if not website:
        return ""
    parsed = urlparse(website if website.startswith(("http://", "https://")) else f"https://{website}")
    host = (parsed.netloc or parsed.path).strip().casefold()
    if host.startswith("www."):
        host = host[4:]
    return host


def _normalize_date_value(value: str) -> str:
    matched = DATE_RE.search(str(value or ""))
    if not matched:
        return datetime.now().strftime("%Y-%m-%d")
    year, month, day = matched.groups()
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _infer_category(text: str) -> str:
    normalized = _normalize_line(text).casefold()
    for category_key, keywords in CATEGORY_RULES:
        if any(keyword.casefold() in normalized for keyword in keywords):
            return category_key
    return "other"


def _infer_importance(text: str) -> str:
    normalized = _normalize_line(text).casefold()
    if any(term.casefold() in normalized for term in URGENT_TERMS):
        return "high"
    return "medium"

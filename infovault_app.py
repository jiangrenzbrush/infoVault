from __future__ import annotations

import json
import sys
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from infovault_docx_import import parse_docx_records
from infovault_i18n import (
    CATEGORY_KEYS,
    COLOR_HEX,
    COLOR_KEYS,
    DEFAULT_LANGUAGE,
    IMPORTANCE_KEYS,
    IMPORTANCE_ORDER,
    LANGUAGE_ORDER,
    TEXT,
    category_display,
    category_key,
    color_display,
    color_key,
    importance_display,
    importance_key,
    load_settings,
    resolve_color_hex,
    resolve_color_key,
    save_settings,
)
from infovault_storage import VaultDatabase, normalize_date, today_string


class SaveChoiceDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        message: str,
        overwrite_label: str,
        duplicate_label: str,
        cancel_label: str,
        overwrite_choice: str = "overwrite",
        duplicate_choice: str = "duplicate",
    ) -> None:
        super().__init__(parent)
        self.choice: str | None = None
        self.overwrite_choice = overwrite_choice
        self.duplicate_choice = duplicate_choice
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda _event: self._cancel())

        container = ttk.Frame(self, padding=18)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        ttk.Label(
            container,
            text=message,
            wraplength=420,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        buttons = ttk.Frame(container)
        buttons.grid(row=1, column=0, sticky="e", pady=(16, 0))
        ttk.Button(
            buttons,
            text=overwrite_label,
            command=lambda: self._close(self.overwrite_choice),
        ).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(
            buttons,
            text=duplicate_label,
            command=lambda: self._close(self.duplicate_choice),
        ).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(buttons, text=cancel_label, command=self._cancel).grid(
            row=0, column=2
        )

        self.update_idletasks()
        self._center_on_parent(parent)
        self.grab_set()

    def _center_on_parent(self, parent: tk.Tk) -> None:
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _close(self, choice: str) -> None:
        self.choice = choice
        self.destroy()

    def _cancel(self) -> None:
        self.choice = None
        self.destroy()

    def show(self) -> str | None:
        self.wait_window()
        return self.choice


class InfoVaultApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        settings = load_settings()
        self.language_code = settings.get("language", DEFAULT_LANGUAGE)
        if self.language_code not in LANGUAGE_ORDER:
            self.language_code = DEFAULT_LANGUAGE

        self.db = VaultDatabase()
        self.current_record_id: int | None = None
        self.all_records: list[dict] = []
        self.password_visible = False

        self.language_name_var = tk.StringVar(value=self.language_name(self.language_code))
        self.filter_keyword_var = tk.StringVar()
        self.filter_category_var = tk.StringVar(value=self.text("all_option"))
        self.filter_importance_var = tk.StringVar(value=self.text("all_option"))
        self.filter_date_from_var = tk.StringVar()
        self.filter_date_to_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.info_date_var = tk.StringVar(value=today_string())
        self.category_var = tk.StringVar(value=category_display("cat:learning_sites", self.language_code))
        self.importance_var = tk.StringVar(value=importance_display("imp:medium", self.language_code))
        self.color_value = "clr:auto"
        self.color_preview_var = tk.StringVar()
        self.website_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value=self.text("status_secure"))
        self.meta_var = tk.StringVar(value=self.text("meta_new"))

        self.geometry("1280x800")
        self.minsize(1080, 680)
        self.title(self.text("window_title"))
        self._build_style()
        self._build_ui()
        self.category_var.trace_add("write", self._on_category_change)
        self._refresh_categories()
        self.refresh_records(select_id=None)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def text(self, key: str, **kwargs: object) -> str:
        return TEXT[self.language_code][key].format(**kwargs)

    def language_name(self, language_code: str) -> str:
        return TEXT[language_code]["language_name"]

    def _build_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("Hint.TLabel", foreground="#4B5563")
        style.configure("Meta.TLabel", foreground="#2563EB")
        style.configure("Treeview", rowheight=30, font=("Microsoft YaHei UI", 10))
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("TButton", font=("Microsoft YaHei UI", 10))
        style.configure("TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("TEntry", font=("Microsoft YaHei UI", 10))
        style.configure("TCombobox", font=("Microsoft YaHei UI", 10))

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self, padding=(20, 16, 20, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text=self.text("app_name"), style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=self.text("subtitle"), style="Hint.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        language_box = ttk.Frame(header)
        language_box.grid(row=0, column=1, rowspan=2, sticky="e")
        ttk.Label(language_box, text=self.text("language_label")).grid(row=0, column=0, sticky="e")
        self.language_combo = ttk.Combobox(
            language_box,
            textvariable=self.language_name_var,
            values=[self.language_name(code) for code in LANGUAGE_ORDER],
            state="readonly",
            width=12,
        )
        self.language_combo.grid(row=0, column=1, padx=(8, 0))
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        filters = ttk.LabelFrame(self, text=self.text("filters_title"), padding=14)
        filters.grid(row=1, column=0, sticky="ew", padx=20)
        for index in range(10):
            filters.columnconfigure(index, weight=1 if index in {1, 3, 5} else 0)

        ttk.Label(filters, text=self.text("keyword_label")).grid(row=0, column=0, sticky="w")
        keyword_entry = ttk.Entry(filters, textvariable=self.filter_keyword_var, width=26)
        keyword_entry.grid(row=0, column=1, sticky="ew", padx=(8, 16))
        keyword_entry.bind("<Return>", lambda _event: self.refresh_records())

        ttk.Label(filters, text=self.text("category_label")).grid(row=0, column=2, sticky="w")
        self.filter_category_combo = ttk.Combobox(filters, textvariable=self.filter_category_var, state="readonly", width=14)
        self.filter_category_combo.grid(row=0, column=3, sticky="ew", padx=(8, 16))

        ttk.Label(filters, text=self.text("importance_label")).grid(row=0, column=4, sticky="w")
        self.filter_importance_combo = ttk.Combobox(
            filters,
            textvariable=self.filter_importance_var,
            values=[self.text("all_option")] + [importance_display(f"imp:{key}", self.language_code) for key in IMPORTANCE_KEYS],
            state="readonly",
            width=12,
        )
        self.filter_importance_combo.grid(row=0, column=5, sticky="ew", padx=(8, 16))

        ttk.Label(filters, text=self.text("date_from_label")).grid(row=0, column=6, sticky="w")
        ttk.Entry(filters, textvariable=self.filter_date_from_var, width=14).grid(row=0, column=7, sticky="ew", padx=(8, 16))
        ttk.Label(filters, text=self.text("date_to_label")).grid(row=0, column=8, sticky="w")
        ttk.Entry(filters, textvariable=self.filter_date_to_var, width=14).grid(row=0, column=9, sticky="ew", padx=(8, 12))

        actions = ttk.Frame(filters)
        actions.grid(row=0, column=10, sticky="e")
        ttk.Button(actions, text=self.text("filter_button"), command=self.refresh_records).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text=self.text("reset_button"), command=self.reset_filters).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text=self.text("new_record_button"), command=self.new_record).grid(row=0, column=2)

        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=2, column=0, sticky="nsew", padx=20, pady=16)

        left = ttk.Frame(body, padding=(0, 0, 10, 0))
        right = ttk.Frame(body)
        body.add(left, weight=5)
        body.add(right, weight=7)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        right.columnconfigure(1, weight=1)
        right.rowconfigure(8, weight=1)

        list_header = ttk.Frame(left)
        list_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        list_header.columnconfigure(0, weight=1)
        ttk.Label(list_header, text=self.text("record_list_title"), font=("Microsoft YaHei UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.count_label = ttk.Label(list_header, text=self.text("record_count", count=0))
        self.count_label.grid(row=0, column=1, sticky="e")

        tree_frame = ttk.Frame(left)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("info_date", "category", "importance", "title", "username")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.heading("info_date", text=self.text("col_date"))
        self.tree.heading("category", text=self.text("col_category"))
        self.tree.heading("importance", text=self.text("col_importance"))
        self.tree.heading("title", text=self.text("col_title"))
        self.tree.heading("username", text=self.text("col_username"))
        self.tree.column("info_date", width=95, anchor="center")
        self.tree.column("category", width=130, anchor="center")
        self.tree.column("importance", width=80, anchor="center")
        self.tree.column("title", width=240, anchor="w")
        self.tree.column("username", width=180, anchor="w")
        for color_name, color_hex in COLOR_HEX.items():
            self.tree.tag_configure(color_name, background=color_hex)
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=y_scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        detail_header = ttk.Frame(right)
        detail_header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        detail_header.columnconfigure(0, weight=1)
        ttk.Label(detail_header, text=self.text("details_title"), font=("Microsoft YaHei UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(detail_header, textvariable=self.meta_var, style="Meta.TLabel").grid(row=0, column=1, sticky="e")

        ttk.Label(right, text=self.text("title_label")).grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(right, textvariable=self.title_var).grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 8), padx=(8, 0))

        ttk.Label(right, text=self.text("date_label")).grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(right, textvariable=self.info_date_var, width=20).grid(row=2, column=1, sticky="w", pady=(0, 8), padx=(8, 12))
        ttk.Label(right, text=self.text("category_label")).grid(row=2, column=1, sticky="e", pady=(0, 8))
        self.category_combo = ttk.Combobox(right, textvariable=self.category_var, state="normal", width=18)
        self.category_combo.grid(row=2, column=2, sticky="ew", pady=(0, 8), padx=(8, 0))

        ttk.Label(right, text=self.text("importance_label")).grid(row=3, column=0, sticky="w", pady=(0, 8))
        self.importance_combo = ttk.Combobox(
            right,
            textvariable=self.importance_var,
            values=[importance_display(f"imp:{key}", self.language_code) for key in IMPORTANCE_KEYS],
            state="readonly",
            width=18,
        )
        self.importance_combo.grid(row=3, column=1, sticky="w", pady=(0, 8), padx=(8, 12))

        ttk.Label(right, text=self.text("color_label")).grid(row=4, column=0, sticky="nw", pady=(0, 8))
        color_frame = ttk.Frame(right)
        color_frame.grid(row=4, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(0, 8))
        color_frame.columnconfigure(1, weight=1)

        palette_frame = ttk.Frame(color_frame)
        palette_frame.grid(row=0, column=0, sticky="w")
        self.color_buttons: dict[str, tk.Button] = {}

        auto_button = tk.Button(
            palette_frame,
            text=self.text("color_auto_label"),
            command=lambda: self.set_color_selection("auto"),
            relief="raised",
            bd=1,
            padx=8,
        )
        auto_button.grid(row=0, column=0, padx=(0, 8))
        self.color_buttons["auto"] = auto_button

        for index, color_name in enumerate(COLOR_KEYS[1:], start=1):
            button = tk.Button(
                palette_frame,
                width=3,
                height=1,
                bg=COLOR_HEX[color_name],
                activebackground=COLOR_HEX[color_name],
                relief="raised",
                bd=1,
                command=lambda key=color_name: self.set_color_selection(key),
            )
            button.grid(row=0, column=index, padx=(0, 6))
            self.color_buttons[color_name] = button

        preview_frame = ttk.Frame(color_frame)
        preview_frame.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.color_chip = tk.Label(preview_frame, width=3, relief="solid", bd=1)
        self.color_chip.grid(row=0, column=0, padx=(0, 8))
        ttk.Label(preview_frame, textvariable=self.color_preview_var, style="Hint.TLabel").grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(color_frame, text=self.text("color_hint"), style="Hint.TLabel").grid(
            row=2, column=0, sticky="w", pady=(6, 0)
        )

        ttk.Label(right, text=self.text("website_label")).grid(row=5, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(right, textvariable=self.website_var).grid(row=5, column=1, sticky="ew", pady=(0, 8), padx=(8, 12))
        ttk.Button(right, text=self.text("open_website_button"), command=self.open_website).grid(row=5, column=2, sticky="ew", pady=(0, 8), padx=(8, 0))

        ttk.Label(right, text=self.text("username_label")).grid(row=6, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(right, textvariable=self.username_var).grid(row=6, column=1, sticky="ew", pady=(0, 8), padx=(8, 12))
        ttk.Button(right, text=self.text("copy_username_button"), command=self.copy_username).grid(row=6, column=2, sticky="ew", pady=(0, 8), padx=(8, 0))

        ttk.Label(right, text=self.text("password_label")).grid(row=7, column=0, sticky="w", pady=(0, 8))
        self.password_entry = ttk.Entry(right, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=7, column=1, sticky="ew", pady=(0, 8), padx=(8, 12))
        password_actions = ttk.Frame(right)
        password_actions.grid(row=7, column=2, sticky="ew", pady=(0, 8), padx=(8, 0))
        password_actions.columnconfigure(0, weight=1)
        password_actions.columnconfigure(1, weight=1)
        ttk.Button(password_actions, text=self.text("toggle_password_button"), command=self.toggle_password_visibility).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(password_actions, text=self.text("copy_password_button"), command=self.copy_password).grid(row=0, column=1, sticky="ew")

        ttk.Label(right, text=self.text("note_label")).grid(row=8, column=0, sticky="nw", pady=(0, 8))
        note_frame = ttk.Frame(right)
        note_frame.grid(row=8, column=1, columnspan=2, sticky="nsew", padx=(8, 0))
        note_frame.columnconfigure(0, weight=1)
        note_frame.rowconfigure(0, weight=1)
        self.note_text = tk.Text(note_frame, wrap="word", font=("Microsoft YaHei UI", 10), relief="solid", borderwidth=1)
        self.note_text.grid(row=0, column=0, sticky="nsew")
        note_scroll = ttk.Scrollbar(note_frame, orient="vertical", command=self.note_text.yview)
        note_scroll.grid(row=0, column=1, sticky="ns")
        self.note_text.configure(yscrollcommand=note_scroll.set)

        ttk.Label(right, text=self.text("date_hint"), style="Hint.TLabel").grid(row=9, column=0, columnspan=3, sticky="w", pady=(10, 12))

        button_bar = ttk.Frame(right)
        button_bar.grid(row=10, column=0, columnspan=3, sticky="ew")
        button_bar.columnconfigure(7, weight=1)
        ttk.Button(button_bar, text=self.text("save_button"), command=self.save_record).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_bar, text=self.text("delete_button"), command=self.delete_record).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_bar, text=self.text("clear_button"), command=self.new_record).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(button_bar, text=self.text("refresh_button"), command=self.refresh_records).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(button_bar, text=self.text("export_button"), command=self.export_backup).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(button_bar, text=self.text("import_button"), command=self.import_backup).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(button_bar, text=self.text("import_docx_button"), command=self.import_docx).grid(row=0, column=6, padx=(0, 8))

        status = ttk.Label(self, textvariable=self.status_var, relief="solid", anchor="w", padding=(12, 8))
        status.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.refresh_color_controls()

    def on_language_change(self, _event: object | None = None) -> None:
        name_to_code = {self.language_name(code): code for code in LANGUAGE_ORDER}
        new_language = name_to_code.get(self.language_name_var.get(), self.language_code)
        if new_language == self.language_code:
            return

        snapshot = self._capture_form_state()
        self.language_code = new_language
        self.language_name_var.set(self.language_name(new_language))
        save_settings({"language": new_language})
        self._rebuild_ui(snapshot)
        self.set_status(self.text("status_language_changed"))

    def _capture_form_state(self) -> dict:
        current = self._record_by_id(self.current_record_id)
        return {
            "current_record_id": self.current_record_id,
            "title": self.title_var.get(),
            "info_date": self.info_date_var.get(),
            "category": self.category_var.get(),
            "importance": self.importance_var.get(),
            "color_value": self.color_value,
            "website": self.website_var.get(),
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "note": self.note_text.get("1.0", tk.END),
            "filter_keyword": self.filter_keyword_var.get(),
            "filter_category": self.filter_category_var.get(),
            "filter_importance": self.filter_importance_var.get(),
            "filter_date_from": self.filter_date_from_var.get(),
            "filter_date_to": self.filter_date_to_var.get(),
            "password_visible": self.password_visible,
            "created_at": current["created_at"] if current else "-",
            "updated_at": current["updated_at"] if current else "-",
        }

    def _rebuild_ui(self, snapshot: dict) -> None:
        translated = dict(snapshot)
        translated["category"] = category_display(snapshot["category"], self.language_code)
        translated["importance"] = importance_display(snapshot["importance"], self.language_code)
        translated["filter_category"] = (
            self.text("all_option")
            if snapshot["filter_category"] in {TEXT["zh-CN"]["all_option"], TEXT["en-US"]["all_option"], ""}
            else category_display(snapshot["filter_category"], self.language_code)
        )
        translated["filter_importance"] = (
            self.text("all_option")
            if snapshot["filter_importance"] in {TEXT["zh-CN"]["all_option"], TEXT["en-US"]["all_option"], ""}
            else importance_display(snapshot["filter_importance"], self.language_code)
        )

        for child in self.winfo_children():
            child.destroy()

        self.title(self.text("window_title"))
        self._build_style()
        self._build_ui()
        self._restore_form_state(translated)
        self.refresh_records(select_id=translated["current_record_id"], preserve_form=True)
        self._restore_form_state(translated)
        self._refresh_meta(
            translated["current_record_id"],
            translated["created_at"],
            translated["updated_at"],
        )

    def _restore_form_state(self, snapshot: dict) -> None:
        self.current_record_id = snapshot["current_record_id"]
        self.title_var.set(snapshot["title"])
        self.info_date_var.set(snapshot["info_date"])
        self.category_var.set(snapshot["category"])
        self.importance_var.set(snapshot["importance"])
        self.color_value = snapshot["color_value"]
        self.website_var.set(snapshot["website"])
        self.username_var.set(snapshot["username"])
        self.password_var.set(snapshot["password"])
        self.filter_keyword_var.set(snapshot["filter_keyword"])
        self.filter_category_var.set(snapshot["filter_category"])
        self.filter_importance_var.set(snapshot["filter_importance"])
        self.filter_date_from_var.set(snapshot["filter_date_from"])
        self.filter_date_to_var.set(snapshot["filter_date_to"])
        self.password_visible = snapshot["password_visible"]
        self.password_entry.configure(show="" if self.password_visible else "*")
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", snapshot["note"])
        self.refresh_color_controls()

    def _on_category_change(self, *_args: object) -> None:
        self.refresh_color_controls()

    def set_color_selection(self, color_name: str) -> None:
        self.color_value = f"clr:{color_name}"
        self.refresh_color_controls()

    def refresh_color_controls(self) -> None:
        if not hasattr(self, "color_buttons"):
            return

        selected_key = color_key(self.color_value)
        actual_key = resolve_color_key(self.color_value, self.category_var.get())
        for key, button in self.color_buttons.items():
            is_selected = key == selected_key
            if isinstance(button, tk.Button):
                button.configure(
                    relief="sunken" if is_selected else "raised",
                    bd=2 if is_selected else 1,
                )
            else:
                button.state(["pressed"] if is_selected else ["!pressed"])

        self.color_chip.configure(bg=COLOR_HEX[actual_key])
        if selected_key == "auto":
            self.color_preview_var.set(
                self.text(
                    "color_preview_auto",
                    color=color_display(f"clr:{actual_key}", self.language_code),
                )
            )
        else:
            self.color_preview_var.set(
                self.text(
                    "color_preview_manual",
                    color=color_display(self.color_value, self.language_code),
                )
            )

    def _record_by_id(self, record_id: int | None) -> dict | None:
        return next((item for item in self.all_records if item["id"] == record_id), None)

    def _refresh_categories(self) -> None:
        categories = {
            category_display(record["category_value"], self.language_code)
            for record in self.db.list_records()
            if category_display(record["category_value"], self.language_code)
        }
        categories.update(category_display(f"cat:{key}", self.language_code) for key in CATEGORY_KEYS)
        values = sorted(categories)
        self.category_combo.configure(values=values)
        self.filter_category_combo.configure(values=[self.text("all_option"), *values])

    def _refresh_meta(self, record_id: int | None, created_at: str = "-", updated_at: str = "-") -> None:
        if record_id is None:
            self.meta_var.set(self.text("meta_new"))
            return
        self.meta_var.set(
            self.text(
                "meta_selected",
                record_id=record_id,
                created_at=created_at or "-",
                updated_at=updated_at or "-",
            )
        )

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def reset_filters(self) -> None:
        self.filter_keyword_var.set("")
        self.filter_category_var.set(self.text("all_option"))
        self.filter_importance_var.set(self.text("all_option"))
        self.filter_date_from_var.set("")
        self.filter_date_to_var.set("")
        self.refresh_records(select_id=self.current_record_id)
        self.set_status(self.text("status_filters_reset"))

    def refresh_records(self, select_id: int | None = None, preserve_form: bool = False) -> None:
        try:
            date_from = self._validated_date(self.filter_date_from_var.get().strip(), allow_blank=True)
            date_to = self._validated_date(self.filter_date_to_var.get().strip(), allow_blank=True)
        except ValueError as exc:
            messagebox.showerror(self.text("app_name"), str(exc))
            return

        if date_from and date_to and date_from > date_to:
            messagebox.showerror(self.text("app_name"), self.text("date_range_invalid"))
            return

        self.all_records = self.db.list_records()
        filtered_records = self._filter_records(self.all_records, date_from, date_to)

        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        for record in filtered_records:
            username_preview = record["username"][:26] + ("..." if len(record["username"]) > 26 else "")
            row_color_key = resolve_color_key(record.get("color_value"), record["category_value"])
            self.tree.insert(
                "",
                "end",
                iid=str(record["id"]),
                values=(
                    record["info_date"],
                    category_display(record["category_value"], self.language_code),
                    importance_display(record["importance_value"], self.language_code),
                    record["title"],
                    username_preview,
                ),
                tags=(row_color_key,),
            )

        self.count_label.configure(text=self.text("record_count", count=len(filtered_records)))
        self._refresh_categories()

        if not filtered_records:
            if not preserve_form:
                self.new_record(clear_status=False)
            self.set_status(self.text("status_no_records"))
            return

        target_id = str(select_id or self.current_record_id or filtered_records[0]["id"])
        if not self.tree.exists(target_id):
            target_id = str(filtered_records[0]["id"])

        self.tree.selection_set(target_id)
        self.tree.focus(target_id)
        self.tree.see(target_id)
        if not preserve_form:
            self.load_record(int(target_id))

    def _filter_records(self, records: list[dict], date_from: str, date_to: str) -> list[dict]:
        keyword = self.filter_keyword_var.get().strip().casefold()
        filter_category = self.filter_category_var.get().strip()
        filter_importance = self.filter_importance_var.get().strip()
        all_values = {TEXT["zh-CN"]["all_option"], TEXT["en-US"]["all_option"], ""}

        filtered: list[dict] = []
        for record in records:
            if filter_category not in all_values:
                if category_key(filter_category):
                    if category_key(filter_category) != category_key(record["category_value"]):
                        continue
                elif filter_category not in {
                    category_display(record["category_value"], self.language_code),
                    record["category_value"],
                }:
                    continue

            if filter_importance not in all_values:
                if importance_key(filter_importance) != importance_key(record["importance_value"]):
                    continue

            if date_from and record["info_date"] < date_from:
                continue
            if date_to and record["info_date"] > date_to:
                continue

            haystack = " ".join(
                [
                    record["title"],
                    record["info_date"],
                    record["website"],
                    record["username"],
                    record["password"],
                    record["note"],
                    record["category_value"],
                    category_display(record["category_value"], "zh-CN"),
                    category_display(record["category_value"], "en-US"),
                    importance_display(record["importance_value"], "zh-CN"),
                    importance_display(record["importance_value"], "en-US"),
                ]
            ).casefold()
            if keyword and keyword not in haystack:
                continue
            filtered.append(record)

        filtered.sort(
            key=lambda item: (
                normalize_date(item["info_date"]),
                IMPORTANCE_ORDER.get(item["importance_key"], 0),
                item["updated_at"],
            ),
            reverse=True,
        )
        return filtered

    def on_tree_select(self, _event: object | None = None) -> None:
        selection = self.tree.selection()
        if selection:
            self.load_record(int(selection[0]))

    def load_record(self, record_id: int) -> None:
        record = self._record_by_id(record_id)
        if not record:
            return

        self.current_record_id = record_id
        self.title_var.set(record["title"])
        self.info_date_var.set(record["info_date"])
        self.category_var.set(category_display(record["category_value"], self.language_code))
        self.importance_var.set(importance_display(record["importance_value"], self.language_code))
        self.color_value = record.get("color_value", "clr:auto")
        self.website_var.set(record["website"])
        self.username_var.set(record["username"])
        self.password_var.set(record["password"])
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", record["note"])
        self.refresh_color_controls()
        self._refresh_meta(record_id, record["created_at"], record["updated_at"])
        self.set_status(self.text("status_loaded"))

    def new_record(self, clear_status: bool = True) -> None:
        self.current_record_id = None
        self.title_var.set("")
        self.info_date_var.set(today_string())
        self.category_var.set(category_display("cat:learning_sites", self.language_code))
        self.importance_var.set(importance_display("imp:medium", self.language_code))
        self.color_value = "clr:auto"
        self.website_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.note_text.delete("1.0", tk.END)
        self.refresh_color_controls()
        self._refresh_meta(None)
        self.tree.selection_remove(self.tree.selection())
        if clear_status:
            self.set_status(self.text("status_new_mode"))

    def gather_form_data(self) -> dict:
        return {
            "title": self.title_var.get(),
            "info_date": self.info_date_var.get(),
            "category": self.category_var.get(),
            "importance": self.importance_var.get(),
            "color": self.color_value,
            "website": self.website_var.get(),
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "note": self.note_text.get("1.0", tk.END),
        }

    def _choose_save_mode(self) -> str | None:
        if self.current_record_id is None:
            return "new"

        dialog = SaveChoiceDialog(
            self,
            title=self.text("save_choice_title"),
            message=self.text("save_choice_message"),
            overwrite_label=self.text("save_choice_overwrite"),
            duplicate_label=self.text("save_choice_duplicate"),
            cancel_label=self.text("save_choice_cancel"),
        )
        return dialog.show()

    def _choose_import_mode(self, record_count: int) -> str | None:
        dialog = SaveChoiceDialog(
            self,
            title=self.text("import_choice_title"),
            message=self.text("import_choice_message", count=record_count),
            overwrite_label=self.text("import_choice_append"),
            duplicate_label=self.text("import_choice_replace"),
            cancel_label=self.text("import_choice_cancel"),
            overwrite_choice="append",
            duplicate_choice="replace",
        )
        return dialog.show()

    def export_backup(self) -> None:
        records = self.db.list_records()
        if not records:
            messagebox.showinfo(self.text("app_name"), self.text("export_no_records"))
            return

        if not messagebox.askyesno(self.text("export_title"), self.text("export_warning")):
            return

        file_path = filedialog.asksaveasfilename(
            title=self.text("export_title"),
            defaultextension=".txt",
            initialfile=f"infovault_backup_{today_string()}.txt",
            filetypes=[
                ("Text Backup", "*.txt"),
                ("JSON", "*.json"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            payload = self.db.export_backup_payload()
            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self.text("export_title"), self.text("export_failed", error=exc))
            return

        self.set_status(self.text("status_exported", count=len(payload["records"])))

    def import_backup(self) -> None:
        file_path = filedialog.askopenfilename(
            title=self.text("import_title"),
            filetypes=[
                ("Backup Files", "*.txt;*.json"),
                ("Text Backup", "*.txt"),
                ("JSON", "*.json"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self.text("import_title"), self.text("import_failed", error=exc))
            return

        if isinstance(payload, dict):
            records = payload.get("records")
        elif isinstance(payload, list):
            records = payload
        else:
            records = None

        if not isinstance(records, list):
            messagebox.showerror(self.text("import_title"), self.text("import_invalid"))
            return
        if not records:
            messagebox.showinfo(self.text("import_title"), self.text("import_no_records"))
            return

        import_mode = self._choose_import_mode(len(records))
        if import_mode is None:
            return

        try:
            imported_count = self.db.import_backup_records(
                records,
                replace_existing=(import_mode == "replace"),
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self.text("import_title"), self.text("import_failed", error=exc))
            return

        if imported_count <= 0:
            messagebox.showinfo(self.text("import_title"), self.text("import_no_records"))
            return

        self.refresh_records(select_id=None)
        if import_mode == "replace":
            self.set_status(self.text("status_imported_replace", count=imported_count))
        else:
            self.set_status(self.text("status_imported_append", count=imported_count))

    def import_docx(self) -> None:
        file_path = filedialog.askopenfilename(
            title=self.text("import_docx_title"),
            filetypes=[
                ("Word Document", "*.docx"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            records = parse_docx_records(file_path)
        except Exception as exc:  # noqa: BLE001
            if isinstance(exc, ValueError) and str(exc) == "invalid_docx":
                error_text = self.text("import_invalid")
            else:
                error_text = self.text("import_docx_failed", error=exc)
            messagebox.showerror(
                self.text("import_docx_title"),
                error_text,
            )
            return

        if not records:
            messagebox.showinfo(
                self.text("import_docx_title"),
                self.text("import_docx_no_records"),
            )
            return

        import_mode = self._choose_import_mode(len(records))
        if import_mode is None:
            return

        try:
            imported_count = self.db.import_backup_records(
                records,
                replace_existing=(import_mode == "replace"),
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                self.text("import_docx_title"),
                self.text("import_docx_failed", error=exc),
            )
            return

        if imported_count <= 0:
            messagebox.showinfo(
                self.text("import_docx_title"),
                self.text("import_docx_no_records"),
            )
            return

        self.refresh_records(select_id=None)
        if import_mode == "replace":
            self.set_status(self.text("status_docx_imported_replace", count=imported_count))
        else:
            self.set_status(self.text("status_docx_imported_append", count=imported_count))

    def save_record(self) -> None:
        data = self.gather_form_data()
        if not data["title"].strip():
            messagebox.showwarning(self.text("app_name"), self.text("fill_title_warning"))
            return

        try:
            self._validated_date(data["info_date"], allow_blank=False)
        except ValueError as exc:
            messagebox.showerror(self.text("app_name"), str(exc))
            return

        save_mode = self._choose_save_mode()
        if save_mode is None:
            return

        try:
            target_record_id = self.current_record_id if save_mode == "overwrite" else None
            saved_id = self.db.save_record(target_record_id, data)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self.text("app_name"), self.text("save_failed", error=exc))
            return

        self.current_record_id = saved_id
        self.refresh_records(select_id=saved_id)
        if save_mode == "overwrite":
            self.set_status(self.text("status_saved_overwrite"))
        elif save_mode in {"duplicate", "new"}:
            self.set_status(self.text("status_saved_new"))
        else:
            self.set_status(self.text("status_saved"))

    def delete_record(self) -> None:
        if self.current_record_id is None:
            messagebox.showinfo(self.text("app_name"), self.text("no_selected_record"))
            return

        if not messagebox.askyesno(self.text("app_name"), self.text("confirm_delete")):
            return

        record_id = self.current_record_id
        self.db.delete_record(record_id)
        self.current_record_id = None
        self.refresh_records(select_id=None)
        self.set_status(self.text("status_deleted", record_id=record_id))

    def toggle_password_visibility(self) -> None:
        self.password_visible = not self.password_visible
        self.password_entry.configure(show="" if self.password_visible else "*")
        key = "status_password_visible" if self.password_visible else "status_password_hidden"
        self.set_status(self.text(key))

    def copy_username(self) -> None:
        username = self.username_var.get().strip()
        if not username:
            messagebox.showinfo(self.text("app_name"), self.text("no_username"))
            return
        self.clipboard_clear()
        self.clipboard_append(username)
        self.set_status(self.text("status_username_copied"))

    def copy_password(self) -> None:
        password = self.password_var.get()
        if not password:
            messagebox.showinfo(self.text("app_name"), self.text("no_password"))
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        self.set_status(self.text("status_password_copied"))

    def open_website(self) -> None:
        website = self.website_var.get().strip()
        if not website:
            messagebox.showinfo(self.text("app_name"), self.text("no_website"))
            return
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"
        webbrowser.open(website)
        self.set_status(self.text("status_website_opened"))

    def _validated_date(self, value: str, allow_blank: bool) -> str:
        text = value.strip()
        if not text and allow_blank:
            return ""
        if not text:
            raise ValueError(self.text("date_empty"))
        try:
            from datetime import datetime

            datetime.strptime(text, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(self.text("date_invalid")) from exc
        return text

    def on_close(self) -> None:
        self.db.close()
        self.destroy()


def main() -> int:
    if sys.platform != "win32":
        messagebox.showerror(TEXT[DEFAULT_LANGUAGE]["app_name"], TEXT[DEFAULT_LANGUAGE]["windows_only"])
        return 1

    if "--self-test" in sys.argv:
        app = InfoVaultApp()
        app.update_idletasks()
        app.destroy()
        print("self-test-ok")
        return 0

    app = InfoVaultApp()
    app.mainloop()
    return 0

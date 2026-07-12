"""Tkinter interface for TIPS Prompt Manager."""

from __future__ import annotations

import ctypes
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .auth import (
    create_password_config,
    is_boot_session_authenticated,
    load_config,
    mark_boot_session_authenticated,
    save_config,
    verify_password,
)
from .i18n import TEXT, load_language, save_language
from .meta import APP_VERSION, AUTHOR, EMAIL, GITHUB, HOMEPAGE
from .paths import database_path
from .storage import DEFAULT_CATEGORY, PromptRepository

COLOR_BG = "#0f172a"
COLOR_SURFACE = "#111827"
COLOR_PANEL = "#1e293b"
COLOR_PANEL_ALT = "#162033"
COLOR_INPUT = "#0b1220"
COLOR_BORDER = "#334155"
COLOR_TEXT = "#e5e7eb"
COLOR_MUTED = "#94a3b8"
COLOR_PRIMARY = "#38bdf8"
COLOR_PRIMARY_DARK = "#0284c7"
COLOR_ACCENT = "#22c55e"
COLOR_DANGER = "#ef4444"
COLOR_DANGER_DARK = "#b91c1c"
COLOR_MATCH_ROW = "#2b3d37"
COLOR_MATCH_BG = "#facc15"
COLOR_MATCH_FG = "#111827"
WINDOW_FRAME_COLORREF = 0x002A170F


def tr(language: str, key: str, **values: object) -> str:
    return TEXT[language][key].format(**values)


def set_dark_window_frame(window: tk.Tk | tk.Toplevel) -> None:
    if not hasattr(ctypes, "windll"):
        return
    try:
        window.update_idletasks()
        hwnd = window.winfo_id()
        top_hwnd = hwnd
        user32 = ctypes.windll.user32
        while hwnd:
            top_hwnd = hwnd
            hwnd = user32.GetParent(hwnd)

        value = ctypes.c_int(1)
        border_color = ctypes.c_int(WINDOW_FRAME_COLORREF)
        caption_color = ctypes.c_int(WINDOW_FRAME_COLORREF)
        text_color = ctypes.c_int(0x00EBE7E5)
        for attribute in (20, 19):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                top_hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)
            )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            top_hwnd, 34, ctypes.byref(border_color), ctypes.sizeof(border_color)
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            top_hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color)
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            top_hwnd, 36, ctypes.byref(text_color), ctypes.sizeof(text_color)
        )
    except Exception:
        return


class LocalizedDialog(simpledialog.Dialog):
    def __init__(self, parent: tk.Tk, language: str, title_key: str):
        self.language = language
        super().__init__(parent, tr(language, title_key))

    def text(self, key: str, **values: object) -> str:
        return tr(self.language, key, **values)


class SetupPasswordDialog(LocalizedDialog):
    def __init__(self, parent: tk.Tk, language: str):
        self.result: str | None = None
        super().__init__(parent, language, "setup_title")

    def body(self, master: tk.Frame) -> tk.Widget:
        ttk.Label(master, text=self.text("setup_intro")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        ttk.Label(master, text=self.text("password")).grid(row=1, column=0, sticky="e", padx=(0, 8))
        ttk.Label(master, text=self.text("confirm_password")).grid(
            row=2, column=0, sticky="e", padx=(0, 8), pady=(8, 0)
        )
        self.password_entry = ttk.Entry(master, show="*", width=30)
        self.confirm_entry = ttk.Entry(master, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky="ew")
        self.confirm_entry.grid(row=2, column=1, sticky="ew", pady=(8, 0))
        ttk.Label(master, text=self.text("local_password_note")).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )
        return self.password_entry

    def validate(self) -> bool:
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        if len(password) < 4:
            messagebox.showerror(
                self.text("password_too_short_title"),
                self.text("password_too_short"),
                parent=self,
            )
            return False
        if password != confirm:
            messagebox.showerror(
                self.text("password_mismatch_title"),
                self.text("password_mismatch"),
                parent=self,
            )
            return False
        self.result = password
        return True


class VerifyPasswordDialog(LocalizedDialog):
    def __init__(self, parent: tk.Tk, language: str, config: dict[str, object]):
        self.config_data = config
        self.attempts_left = 5
        self.result = False
        super().__init__(parent, language, "verify_title")

    def body(self, master: tk.Frame) -> tk.Widget:
        ttk.Label(master, text=self.text("verify_intro")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        ttk.Label(master, text=self.text("password")).grid(row=1, column=0, sticky="e", padx=(0, 8))
        self.password_entry = ttk.Entry(master, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky="ew")
        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        return self.password_entry

    def validate(self) -> bool:
        if verify_password(self.password_entry.get(), self.config_data):
            self.result = True
            return True
        self.attempts_left -= 1
        if self.attempts_left <= 0:
            messagebox.showerror(
                self.text("too_many_attempts_title"),
                self.text("too_many_attempts"),
                parent=self,
            )
            self.result = False
            self.cancel()
            return False
        self.status_label.configure(text=self.text("attempts_left", count=self.attempts_left))
        self.password_entry.delete(0, tk.END)
        return False


class CategoryDialog(LocalizedDialog):
    def __init__(self, parent: tk.Tk, language: str, title: str, initial_value: str = ""):
        self.initial_value = initial_value
        self.result: str | None = None
        self.dialog_title = title
        super().__init__(parent, language, "category_name")

    def body(self, master: tk.Frame) -> tk.Widget:
        self.title(self.dialog_title)
        ttk.Label(master, text=self.text("category_name")).grid(row=0, column=0, sticky="e", padx=(0, 8))
        self.name_entry = ttk.Entry(master, width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew")
        self.name_entry.insert(0, self.initial_value)
        self.name_entry.select_range(0, tk.END)
        return self.name_entry

    def validate(self) -> bool:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror(self.text("empty_name_title"), self.text("empty_name"), parent=self)
            return False
        self.result = name
        return True


class PromptManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language = load_language()
        self.repository = PromptRepository(database_path())
        self.current_prompt_id: int | None = None
        self.selected_category_id: int | None = None
        self.category_rows = []
        self.category_name_to_id: dict[str, int] = {}

        self.title(tr(self.language, "app_title"))
        self.geometry("1280x820")
        self.minsize(1060, 700)
        self.configure(bg=COLOR_BG)

        self._configure_style()
        self._build_layout()
        self._bind_shortcuts()
        self.apply_language()
        self.refresh_categories()
        self.refresh_prompt_list()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(120, lambda: set_dark_window_frame(self))

    def text(self, key: str, **values: object) -> str:
        return tr(self.language, key, **values)

    def category_display(self, name: str) -> str:
        return self.text("default_category") if name == DEFAULT_CATEGORY else name

    def category_actual(self, value: str) -> str:
        if value in {self.text("default_category"), DEFAULT_CATEGORY}:
            return DEFAULT_CATEGORY
        return value

    def _configure_style(self) -> None:
        self.option_add("*Font", ("Microsoft YaHei UI", 10))
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        self.style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT)
        self.style.configure("TFrame", background=COLOR_BG)
        self.style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT)
        self.style.configure("Panel.TFrame", background=COLOR_PANEL)
        self.style.configure("Muted.TLabel", background=COLOR_BG, foreground=COLOR_MUTED)
        self.style.configure("Panel.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXT)
        self.style.configure("PanelMuted.TLabel", background=COLOR_PANEL, foreground=COLOR_MUTED)
        self.style.configure("TButton", padding=(12, 7))
        self.style.configure("Primary.TButton", background=COLOR_PRIMARY_DARK, foreground="#ffffff")
        self.style.configure("Accent.TButton", background=COLOR_ACCENT, foreground="#052e16")
        self.style.configure("Danger.TButton", background=COLOR_DANGER, foreground="#ffffff")
        self.style.map("Primary.TButton", background=[("active", COLOR_PRIMARY)])
        self.style.map("Accent.TButton", background=[("active", "#16a34a")])
        self.style.map("Danger.TButton", background=[("active", COLOR_DANGER_DARK)])
        self.style.layout("Dark.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        self.style.configure(
            "Dark.Treeview",
            background=COLOR_PANEL,
            fieldbackground=COLOR_PANEL,
            foreground=COLOR_TEXT,
            rowheight=32,
            borderwidth=0,
            relief=tk.FLAT,
            font=("Microsoft YaHei UI", 10),
        )
        self.style.configure(
            "Dark.Treeview.Heading",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            font=("Microsoft YaHei UI", 10, "bold"),
            padding=(8, 8),
        )
        self.style.map(
            "Dark.Treeview",
            background=[("selected", COLOR_PRIMARY_DARK)],
            foreground=[("selected", "#ffffff")],
        )
        self.style.configure(
            "Dark.TCombobox",
            fieldbackground=COLOR_INPUT,
            background=COLOR_INPUT,
            foreground=COLOR_TEXT,
            arrowcolor=COLOR_TEXT,
            bordercolor=COLOR_INPUT,
            lightcolor=COLOR_INPUT,
            darkcolor=COLOR_INPUT,
            borderwidth=0,
            relief=tk.FLAT,
            padding=7,
        )
        self.style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", COLOR_INPUT)],
            foreground=[("readonly", COLOR_TEXT)],
        )

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        self._build_header(root)
        self._build_filter_bar(root)
        self._build_main_area(root)

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title_block = ttk.Frame(header)
        title_block.grid(row=0, column=0, sticky="w")
        self.title_label = ttk.Label(title_block, font=("Microsoft YaHei UI", 20, "bold"))
        self.title_label.pack(anchor="w")
        self.subtitle_label = ttk.Label(title_block, style="Muted.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        actions = ttk.Frame(header)
        actions.grid(row=0, column=1, sticky="e")
        self.new_button = ttk.Button(actions, command=self.new_prompt)
        self.save_button = ttk.Button(actions, command=self.save_prompt, style="Primary.TButton")
        self.copy_button = ttk.Button(actions, command=self.copy_prompt, style="Accent.TButton")
        self.delete_button = ttk.Button(actions, command=self.delete_prompt, style="Danger.TButton")
        self.language_button = ttk.Button(actions, command=self.toggle_language)
        self.about_button = ttk.Button(actions, command=self.show_about)
        for index, button in enumerate(
            [
                self.new_button,
                self.save_button,
                self.copy_button,
                self.delete_button,
                self.language_button,
                self.about_button,
            ]
        ):
            button.pack(side=tk.LEFT, padx=(8 if index else 0, 0))

    def _build_filter_bar(self, parent: ttk.Frame) -> None:
        panel = tk.Frame(parent, bg=COLOR_PANEL)
        panel.grid(row=1, column=0, sticky="ew", pady=(14, 12))
        panel.columnconfigure(4, weight=1)

        self.filter_category_label = tk.Label(panel, bg=COLOR_PANEL, fg=COLOR_MUTED)
        self.filter_category_label.grid(row=0, column=0, sticky="w", padx=(14, 8), pady=12)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(
            panel, textvariable=self.filter_category_var, state="readonly", width=20, style="Dark.TCombobox"
        )
        self.filter_category_combo.grid(row=0, column=1, sticky="w", pady=12)
        self.filter_category_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        self.add_category_button = ttk.Button(panel, command=self.add_category)
        self.rename_category_button = ttk.Button(panel, command=self.rename_category)
        self.delete_category_button = ttk.Button(panel, command=self.delete_category)
        self.add_category_button.grid(row=0, column=2, sticky="w", padx=(10, 0), pady=10)
        self.rename_category_button.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=10)
        self.delete_category_button.grid(row=0, column=4, sticky="w", padx=(8, 18), pady=10)

        search_group = tk.Frame(panel, bg=COLOR_PANEL)
        search_group.grid(row=0, column=5, sticky="e", padx=(10, 14), pady=10)
        self.search_label = tk.Label(search_group, bg=COLOR_PANEL, fg=COLOR_MUTED)
        self.search_label.pack(side=tk.LEFT, padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_group,
            textvariable=self.search_var,
            width=34,
            relief=tk.FLAT,
            bg=COLOR_INPUT,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            selectbackground=COLOR_PRIMARY_DARK,
            selectforeground="#ffffff",
            font=("Microsoft YaHei UI", 10),
        )
        self.search_entry.pack(side=tk.LEFT, ipady=7)
        self.search_var.trace_add("write", lambda *_: self.on_search_change())
        self.clear_button = ttk.Button(search_group, command=self.clear_search)
        self.clear_button.pack(side=tk.LEFT, padx=(8, 0))

    def _build_main_area(self, parent: ttk.Frame) -> None:
        main = ttk.Frame(parent)
        main.grid(row=2, column=0, sticky="nsew")
        main.columnconfigure(0, weight=2, minsize=420)
        main.columnconfigure(1, weight=4, minsize=600)
        main.rowconfigure(0, weight=1)
        self._build_left_panel(main)
        self._build_content_panel(main)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        panel = tk.Frame(parent, bg=COLOR_PANEL)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        title_row = tk.Frame(panel, bg=COLOR_PANEL)
        title_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))
        title_row.columnconfigure(0, weight=1)
        self.prompt_list_label = tk.Label(
            title_row, bg=COLOR_PANEL, fg=COLOR_TEXT, font=("Microsoft YaHei UI", 12, "bold")
        )
        self.prompt_list_label.grid(row=0, column=0, sticky="w")
        self.list_count_var = tk.StringVar()
        tk.Label(
            title_row,
            textvariable=self.list_count_var,
            bg=COLOR_PANEL,
            fg=COLOR_MUTED,
            font=("Microsoft YaHei UI", 10),
        ).grid(row=0, column=1, sticky="e")

        table_wrap = tk.Frame(panel, bg=COLOR_PANEL)
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)
        self.prompt_tree = ttk.Treeview(
            table_wrap, columns=("title", "category"), show="headings", selectmode="browse", style="Dark.Treeview"
        )
        self.prompt_tree.column("title", minwidth=220, width=320, stretch=True)
        self.prompt_tree.column("category", minwidth=90, width=130, stretch=False)
        self.prompt_tree.tag_configure("even", background=COLOR_PANEL)
        self.prompt_tree.tag_configure("odd", background=COLOR_PANEL_ALT)
        self.prompt_tree.tag_configure("match", background=COLOR_MATCH_ROW)
        self.prompt_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll = ttk.Scrollbar(table_wrap, command=self.prompt_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.prompt_tree.configure(yscrollcommand=tree_scroll.set)
        self.prompt_tree.bind("<<TreeviewSelect>>", self.on_prompt_select)

        info = tk.Frame(panel, bg=COLOR_PANEL)
        info.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        info.columnconfigure(0, weight=1)
        self.basic_info_label = tk.Label(
            info, bg=COLOR_PANEL, fg=COLOR_TEXT, font=("Microsoft YaHei UI", 11, "bold")
        )
        self.basic_info_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.title_field_label = tk.Label(info, bg=COLOR_PANEL, fg=COLOR_MUTED)
        self.title_field_label.grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.title_var = tk.StringVar()
        self.title_entry = self._entry(info, self.title_var)
        self.title_entry.grid(row=2, column=0, sticky="ew", ipady=7)
        self.editor_category_label = tk.Label(info, bg=COLOR_PANEL, fg=COLOR_MUTED)
        self.editor_category_label.grid(row=3, column=0, sticky="w", pady=(12, 6))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            info, textvariable=self.category_var, state="readonly", style="Dark.TCombobox"
        )
        self.category_combo.grid(row=4, column=0, sticky="ew")
        self.updated_var = tk.StringVar()
        tk.Label(
            info, textvariable=self.updated_var, bg=COLOR_PANEL, fg=COLOR_MUTED, font=("Microsoft YaHei UI", 9)
        ).grid(row=5, column=0, sticky="w", pady=(12, 0))

    def _build_content_panel(self, parent: ttk.Frame) -> None:
        panel = tk.Frame(parent, bg=COLOR_PANEL)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        header = tk.Frame(panel, bg=COLOR_PANEL)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))
        header.columnconfigure(0, weight=1)
        self.content_label = tk.Label(
            header, bg=COLOR_PANEL, fg=COLOR_TEXT, font=("Microsoft YaHei UI", 12, "bold")
        )
        self.content_label.grid(row=0, column=0, sticky="w")
        self.match_count_var = tk.StringVar()
        tk.Label(
            header, textvariable=self.match_count_var, bg=COLOR_PANEL, fg=COLOR_MUTED, font=("Microsoft YaHei UI", 10)
        ).grid(row=0, column=1, sticky="e", padx=(12, 0))
        self.status_var = tk.StringVar()
        tk.Label(
            header, textvariable=self.status_var, bg=COLOR_PANEL, fg=COLOR_MUTED, font=("Microsoft YaHei UI", 10)
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        text_shell = tk.Frame(panel, bg=COLOR_INPUT)
        text_shell.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        text_shell.columnconfigure(0, weight=1)
        text_shell.rowconfigure(0, weight=1)
        self.content_text = tk.Text(
            text_shell,
            wrap=tk.WORD,
            undo=True,
            borderwidth=0,
            relief=tk.FLAT,
            bg=COLOR_INPUT,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            selectbackground=COLOR_PRIMARY_DARK,
            selectforeground="#ffffff",
            padx=14,
            pady=14,
            spacing1=2,
            spacing3=6,
            font=("Microsoft YaHei UI", 11),
        )
        self.content_text.tag_configure("search_match", background=COLOR_MATCH_BG, foreground=COLOR_MATCH_FG)
        self.content_text.grid(row=0, column=0, sticky="nsew")
        self.content_text.bind("<KeyRelease>", lambda _event: self._highlight_search_matches())
        content_scroll = ttk.Scrollbar(text_shell, command=self.content_text.yview)
        content_scroll.grid(row=0, column=1, sticky="ns")
        self.content_text.configure(yscrollcommand=content_scroll.set)

    def _entry(self, parent: tk.Frame, textvariable: tk.StringVar) -> tk.Entry:
        return tk.Entry(
            parent,
            textvariable=textvariable,
            relief=tk.FLAT,
            bg=COLOR_INPUT,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            selectbackground=COLOR_PRIMARY_DARK,
            selectforeground="#ffffff",
            font=("Microsoft YaHei UI", 10),
        )

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-n>", lambda _event: self.new_prompt())
        self.bind("<Control-s>", lambda _event: self.save_prompt())
        self.bind("<Control-f>", lambda _event: self.focus_search())
        self.prompt_tree.bind("<Delete>", lambda _event: self.delete_prompt())

    def apply_language(self) -> None:
        self.title(self.text("app_title"))
        self.title_label.configure(text=self.text("app_title"))
        self.subtitle_label.configure(text=self.text("subtitle"))
        self.new_button.configure(text=self.text("new"))
        self.save_button.configure(text=self.text("save"))
        self.copy_button.configure(text=self.text("copy"))
        self.delete_button.configure(text=self.text("delete"))
        self.language_button.configure(text=self.text("language"))
        self.about_button.configure(text=self.text("about"))
        self.filter_category_label.configure(text=self.text("category"))
        self.add_category_button.configure(text=self.text("add_category"))
        self.rename_category_button.configure(text=self.text("rename"))
        self.delete_category_button.configure(text=self.text("delete_category"))
        self.search_label.configure(text=self.text("search"))
        self.clear_button.configure(text=self.text("clear"))
        self.prompt_list_label.configure(text=self.text("prompt_list"))
        self.prompt_tree.heading("title", text=self.text("title"))
        self.prompt_tree.heading("category", text=self.text("category"))
        self.basic_info_label.configure(text=self.text("basic_info"))
        self.title_field_label.configure(text=self.text("title"))
        self.editor_category_label.configure(text=self.text("category"))
        self.content_label.configure(text=self.text("content"))
        if not self.status_var.get():
            self.status_var.set(self.text("ready"))
        if not self.updated_var.get():
            self.updated_var.set(self.text("updated_at", value="-"))
        self._highlight_search_matches()

    def toggle_language(self) -> None:
        self.language = "en" if self.language == "zh" else "zh"
        save_language(self.language)
        self.apply_language()
        self.refresh_categories()
        self.refresh_prompt_list()

    def show_about(self) -> None:
        messagebox.showinfo(
            self.text("about"),
            self.text(
                "about_text",
                version=APP_VERSION,
                author=AUTHOR,
                email=EMAIL,
                home=HOMEPAGE,
                github=GITHUB,
            ),
            parent=self,
        )

    def focus_search(self) -> str:
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
        return "break"

    def refresh_categories(self) -> None:
        self.category_rows = self.repository.list_categories()
        self.category_name_to_id = {row["name"]: int(row["id"]) for row in self.category_rows}
        names = [row["name"] for row in self.category_rows]
        display_names = [self.category_display(name) for name in names]

        actual_filter = self.category_actual(self.filter_category_var.get() or "")
        filter_values = [self.text("all_categories"), *display_names]
        self.filter_category_combo.configure(values=filter_values)
        if actual_filter in names:
            self.filter_category_var.set(self.category_display(actual_filter))
        else:
            self.filter_category_var.set(self.text("all_categories"))
        self._update_selected_category()

        actual_editor = self.category_actual(self.category_var.get() or DEFAULT_CATEGORY)
        self.category_combo.configure(values=display_names)
        if actual_editor in names:
            self.category_var.set(self.category_display(actual_editor))
        elif DEFAULT_CATEGORY in names:
            self.category_var.set(self.category_display(DEFAULT_CATEGORY))
        elif display_names:
            self.category_var.set(display_names[0])

    def _update_selected_category(self) -> None:
        category_name = self.category_actual(self.filter_category_var.get())
        if not category_name or self.filter_category_var.get() == self.text("all_categories"):
            self.selected_category_id = None
        else:
            self.selected_category_id = self.category_name_to_id.get(category_name)

    def on_filter_change(self, _event: object | None = None) -> None:
        self._update_selected_category()
        self.refresh_prompt_list()

    def on_search_change(self) -> None:
        query = self.search_var.get().strip()
        self.search_entry.configure(bg="#13233a" if query else COLOR_INPUT)
        self.refresh_prompt_list()
        self._highlight_search_matches()

    def refresh_prompt_list(self) -> None:
        selected = self.prompt_tree.selection()
        selected_id = selected[0] if selected else None
        for item in self.prompt_tree.get_children():
            self.prompt_tree.delete(item)

        query = self.search_var.get().strip()
        rows = self.repository.list_prompts(self.selected_category_id, query)
        for index, row in enumerate(rows):
            tag = "match" if query else ("odd" if index % 2 else "even")
            self.prompt_tree.insert(
                "",
                tk.END,
                iid=str(row["id"]),
                values=(row["title"], self.category_display(row["category_name"])),
                tags=(tag,),
            )
        self.list_count_var.set(self.text("count", count=len(rows)))
        if selected_id and self.prompt_tree.exists(selected_id):
            self.prompt_tree.selection_set(selected_id)

    def _highlight_search_matches(self) -> None:
        self.content_text.tag_remove("search_match", "1.0", tk.END)
        query = self.search_var.get().strip()
        if not query:
            self.match_count_var.set(self.text("no_search"))
            return
        count = 0
        start = "1.0"
        while True:
            index = self.content_text.search(query, start, tk.END, nocase=True)
            if not index:
                break
            end = f"{index}+{len(query)}c"
            self.content_text.tag_add("search_match", index, end)
            start = end
            count += 1
        self.match_count_var.set(self.text("content_matches", count=count))

    def clear_search(self) -> None:
        self.search_var.set("")

    def on_prompt_select(self, _event: object | None = None) -> None:
        selection = self.prompt_tree.selection()
        if not selection:
            return
        prompt = self.repository.get_prompt(int(selection[0]))
        if not prompt:
            return
        self.current_prompt_id = int(prompt["id"])
        self.title_var.set(prompt["title"])
        self.category_var.set(self.category_display(prompt["category_name"]))
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", prompt["content"])
        self.updated_var.set(self.text("updated_at", value=prompt["updated_at"]))
        self.status_var.set(self.text("editing", title=prompt["title"]))
        self._highlight_search_matches()

    def new_prompt(self) -> None:
        self.current_prompt_id = None
        selection = self.prompt_tree.selection()
        if selection:
            self.prompt_tree.selection_remove(*selection)
        self.title_var.set("")
        editor_category = self.category_actual(self.filter_category_var.get())
        if not editor_category or self.filter_category_var.get() == self.text("all_categories"):
            editor_category = DEFAULT_CATEGORY
        self.category_var.set(self.category_display(editor_category))
        self.content_text.delete("1.0", tk.END)
        self.updated_var.set(self.text("updated_at", value="-"))
        self.title_entry.focus_set()
        self.status_var.set(self.text("new_prompt"))
        self._highlight_search_matches()

    def save_prompt(self) -> None:
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        category_name = self.category_actual(self.category_var.get().strip() or DEFAULT_CATEGORY)
        category_id = self.category_name_to_id.get(category_name)
        if not title:
            messagebox.showerror(self.text("missing_title_title"), self.text("missing_title"), parent=self)
            self.title_entry.focus_set()
            return
        if not content:
            messagebox.showerror(self.text("missing_content_title"), self.text("missing_content"), parent=self)
            self.content_text.focus_set()
            return
        if not category_id:
            messagebox.showerror(self.text("invalid_category_title"), self.text("invalid_category"), parent=self)
            return
        self.current_prompt_id = self.repository.save_prompt(self.current_prompt_id, title, content, category_id)
        self.refresh_prompt_list()
        if self.prompt_tree.exists(str(self.current_prompt_id)):
            self.prompt_tree.selection_set(str(self.current_prompt_id))
            self.prompt_tree.see(str(self.current_prompt_id))
        saved = self.repository.get_prompt(self.current_prompt_id)
        if saved:
            self.updated_var.set(self.text("updated_at", value=saved["updated_at"]))
        self.status_var.set(self.text("saved"))
        self._highlight_search_matches()

    def copy_prompt(self) -> None:
        content = self.content_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo(self.text("empty_copy_title"), self.text("empty_copy"), parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        self.status_var.set(self.text("copied"))

    def delete_prompt(self) -> None:
        if not self.current_prompt_id:
            return
        title = self.title_var.get().strip() or self.text("title")
        confirmed = messagebox.askyesno(
            self.text("confirm_delete_title"), self.text("confirm_delete", title=title), parent=self
        )
        if not confirmed:
            return
        self.repository.delete_prompt(self.current_prompt_id)
        self.current_prompt_id = None
        self.new_prompt()
        self.refresh_prompt_list()
        self.status_var.set(self.text("deleted_prompt"))

    def add_category(self) -> None:
        dialog = CategoryDialog(self, self.language, self.text("add_category"))
        if not dialog.result:
            return
        name = dialog.result
        if self.repository.get_category_by_name(name):
            messagebox.showerror(self.text("category_exists_title"), self.text("category_exists"), parent=self)
            return
        self.repository.add_category(name)
        self.refresh_categories()
        self.filter_category_var.set(self.category_display(name))
        self.category_var.set(self.category_display(name))
        self.on_filter_change()
        self.status_var.set(self.text("added_category", name=name))

    def _selected_filter_category(self) -> dict[str, object] | None:
        if self.filter_category_var.get() == self.text("all_categories"):
            return None
        name = self.category_actual(self.filter_category_var.get())
        category_id = self.category_name_to_id.get(name)
        if not category_id:
            return None
        return {"id": category_id, "name": name}

    def rename_category(self) -> None:
        category = self._selected_filter_category()
        if not category:
            messagebox.showinfo(self.text("choose_category_title"), self.text("choose_category"), parent=self)
            return
        if category["name"] == DEFAULT_CATEGORY:
            messagebox.showinfo(self.text("system_category_title"), self.text("system_category_rename"), parent=self)
            return
        old_name = str(category["name"])
        dialog = CategoryDialog(self, self.language, self.text("rename"), old_name)
        if not dialog.result:
            return
        name = dialog.result
        existing = self.repository.get_category_by_name(name)
        if existing and int(existing["id"]) != int(category["id"]):
            messagebox.showerror(self.text("category_exists_title"), self.text("category_exists"), parent=self)
            return
        self.repository.rename_category(int(category["id"]), name)
        if self.category_actual(self.category_var.get()) == old_name:
            self.category_var.set(self.category_display(name))
        self.filter_category_var.set(self.category_display(name))
        self.refresh_categories()
        self.refresh_prompt_list()
        self.status_var.set(self.text("renamed_category", name=name))

    def delete_category(self) -> None:
        category = self._selected_filter_category()
        if not category:
            messagebox.showinfo(self.text("choose_category_title"), self.text("choose_category"), parent=self)
            return
        if category["name"] == DEFAULT_CATEGORY:
            messagebox.showinfo(self.text("system_category_title"), self.text("system_category_delete"), parent=self)
            return
        name = str(category["name"])
        confirmed = messagebox.askyesno(
            self.text("confirm_delete_title"),
            self.text("confirm_delete_category", name=name, fallback=self.category_display(DEFAULT_CATEGORY)),
            parent=self,
        )
        if not confirmed:
            return
        self.repository.delete_category(int(category["id"]))
        self.filter_category_var.set(self.text("all_categories"))
        self.category_var.set(self.category_display(DEFAULT_CATEGORY))
        self.refresh_categories()
        self.refresh_prompt_list()
        self.status_var.set(self.text("deleted_category"))

    def on_close(self) -> None:
        self.repository.close()
        self.destroy()


def ensure_authenticated(root: tk.Tk, language: str) -> bool:
    config = load_config()
    if not config.get("password_hash"):
        dialog = SetupPasswordDialog(root, language)
        if not dialog.result:
            return False
        config = create_password_config(dialog.result)
        save_config(config)
        mark_boot_session_authenticated(config)
        return True
    if is_boot_session_authenticated(config):
        return True
    dialog = VerifyPasswordDialog(root, language, config)
    if dialog.result:
        mark_boot_session_authenticated(config)
        return True
    return False


def main() -> None:
    language = load_language()
    auth_root = tk.Tk()
    auth_root.withdraw()
    if not ensure_authenticated(auth_root, language):
        auth_root.destroy()
        return
    auth_root.destroy()
    app = PromptManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()

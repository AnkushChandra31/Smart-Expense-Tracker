import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os


def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_expense_db(amount, category, description):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)",
        (amount, category, description)
    )
    conn.commit()
    conn.close()

def update_expense_db(expense_id, amount, category, description):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET amount=?, category=?, description=? WHERE id=?",
        (amount, category, description, expense_id)
    )
    conn.commit()
    conn.close()

def delete_expense_db(expense_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

def export_to_csv(filepath):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    conn.close()
    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Amount", "Category", "Description"])
        writer.writerows(expenses)
    return len(expenses)

def id_exists(expense_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM expenses WHERE id=?", (expense_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

BG         = "#0F1117"
PANEL      = "#1A1D27"
CARD       = "#22263A"
ACCENT     = "#7C6AF7"
ACCENT2    = "#A78BFA"
SUCCESS    = "#34D399"
DANGER     = "#F87171"
WARNING    = "#FBBF24"
TEXT       = "#E8E8F0"
SUBTEXT    = "#8B8FA8"
BORDER     = "#2E3250"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 11)

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Expense Tracker")
        self.root.geometry("980x680")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(860, 580)

        self.selected_id = None
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        sidebar = tk.Frame(self.root, bg=PANEL, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg=PANEL, pady=24)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="", font=("Segoe UI", 28),
                 bg=PANEL, fg=ACCENT2).pack()
        tk.Label(logo_frame, text="Expense Tracker", font=FONT_HEADER,
                 bg=PANEL, fg=TEXT).pack()
        tk.Label(logo_frame, text="Smart spending, clear records",
                 font=FONT_SMALL, bg=PANEL, fg=SUBTEXT).pack(pady=(2, 0))

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=8)

        self.nav_buttons = {}
        nav_items = [
            ("", "View All",    self.show_view),
            ("", "Add Expense", self.show_add),
            ("",  "Edit Expense", self.show_edit),
            ("", "Delete",      self.show_delete),
            ("", "Export CSV",  self.show_export),
        ]
        for icon, label, cmd in nav_items:
            btn = self._sidebar_btn(sidebar, icon, label, cmd)
            self.nav_buttons[label] = btn

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=16)
        self.summary_label = tk.Label(sidebar, text="", font=FONT_SMALL,
                                      bg=PANEL, fg=SUBTEXT, justify="left")
        self.summary_label.pack(padx=20, anchor="w")

        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(side="right", fill="both", expand=True)

        topbar = tk.Frame(self.main_frame, bg=BG, pady=14)
        topbar.pack(fill="x", padx=28)
        self.page_title = tk.Label(topbar, text="All Expenses",
                                   font=FONT_TITLE, bg=BG, fg=TEXT)
        self.page_title.pack(side="left")
        self.status_bar = tk.Label(topbar, text="", font=FONT_SMALL,
                                   bg=BG, fg=SUBTEXT)
        self.status_bar.pack(side="right", padx=4)

        self.content = tk.Frame(self.main_frame, bg=BG)
        self.content.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        self._build_view_panel()
        self._build_add_panel()
        self._build_edit_panel()
        self._build_delete_panel()
        self._build_export_panel()

        self.show_view()

    def _sidebar_btn(self, parent, icon, label, cmd):
        frame = tk.Frame(parent, bg=PANEL, cursor="hand2")
        frame.pack(fill="x", padx=12, pady=2)

        def on_click():
            self._set_active_nav(label)
            cmd()

        def on_enter(e):
            if self.active_nav != label:
                frame.config(bg="#252840")
                lbl_icon.config(bg="#252840")
                lbl_text.config(bg="#252840")

        def on_leave(e):
            if self.active_nav != label:
                frame.config(bg=PANEL)
                lbl_icon.config(bg=PANEL)
                lbl_text.config(bg=PANEL)

        lbl_icon = tk.Label(frame, text=icon, font=("Segoe UI", 14),
                            bg=PANEL, fg=ACCENT2, width=3)
        lbl_icon.pack(side="left", padx=(8, 0), pady=10)
        lbl_text = tk.Label(frame, text=label, font=FONT_BODY,
                            bg=PANEL, fg=TEXT, anchor="w")
        lbl_text.pack(side="left", padx=6)

        for w in (frame, lbl_icon, lbl_text):
            w.bind("<Button-1>", lambda e: on_click())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        frame._icon  = lbl_icon
        frame._text  = lbl_text
        frame._label = label
        self.active_nav = None
        return frame

    def _set_active_nav(self, label):
        self.active_nav = label
        for lbl, frame in self.nav_buttons.items():
            if lbl == label:
                frame.config(bg=ACCENT)
                frame._icon.config(bg=ACCENT, fg="#fff")
                frame._text.config(bg=ACCENT, fg="#fff")
            else:
                frame.config(bg=PANEL)
                frame._icon.config(bg=PANEL, fg=ACCENT2)
                frame._text.config(bg=PANEL, fg=TEXT)

    def _hide_all_panels(self):
        for w in self.content.winfo_children():
            w.pack_forget()

    def _build_view_panel(self):
        self.view_panel = tk.Frame(self.content, bg=BG)

        stats_row = tk.Frame(self.view_panel, bg=BG)
        stats_row.pack(fill="x", pady=(0, 16))
        self.stat_count = self._stat_card(stats_row, "Total Expenses", "0", "")
        self.stat_total = self._stat_card(stats_row, "Total Spent",    "₹0", "")
        self.stat_avg   = self._stat_card(stats_row, "Average",        "₹0", "")

        table_frame = tk.Frame(self.view_panel, bg=CARD,
                               highlightbackground=BORDER, highlightthickness=1)
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Amount (₹)", "Category", "Description")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=38,
                        font=FONT_BODY, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                        background=PANEL, foreground=ACCENT2,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])

        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", style="Custom.Treeview")
        widths = {"ID": 60, "Amount (₹)": 120, "Category": 160, "Description": 340}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], anchor="center" if col in ("ID","Amount (₹)") else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

        self.empty_label = tk.Label(self.view_panel,
                                    text="No expenses yet — add your first one!",
                                    font=("Segoe UI", 13), bg=BG, fg=SUBTEXT)

    def _stat_card(self, parent, title, value, icon):
        card = tk.Frame(parent, bg=CARD, padx=18, pady=14,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", expand=True, fill="x", padx=(0, 12))
        tk.Label(card, text=icon + "  " + title, font=FONT_SMALL,
                 bg=CARD, fg=SUBTEXT).pack(anchor="w")
        lbl = tk.Label(card, text=value, font=("Segoe UI", 20, "bold"),
                       bg=CARD, fg=TEXT)
        lbl.pack(anchor="w", pady=(4, 0))
        return lbl

    def show_view(self):
        self._hide_all_panels()
        self.page_title.config(text="All Expenses")
        self.view_panel.pack(fill="both", expand=True)
        self.refresh_table()

    def refresh_table(self):
        rows = get_all_expenses()
        count = len(rows)
        total = sum(r[1] for r in rows)
        avg   = total / count if count else 0
        self.stat_count.config(text=str(count))
        self.stat_total.config(text="₹{:,.2f}".format(total))
        self.stat_avg.config(text="₹{:,.2f}".format(avg))

        self.summary_label.config(
            text="Records : {}\nTotal    : ₹{:,.0f}".format(count, total)
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        if rows:
            self.empty_label.pack_forget()
            self.tree.master.pack(fill="both", expand=True, padx=1, pady=1)
            for r in rows:
                self.tree.insert("", "end",
                                 values=(r[0], "₹{:,.2f}".format(r[1]), r[2], r[3]))
        else:
            self.tree.master.pack_forget()
            self.empty_label.pack(pady=60)

        self._set_status("{} record{}".format(count, "s" if count != 1 else ""))

    def _build_add_panel(self):
        self.add_panel = tk.Frame(self.content, bg=BG)
        card = tk.Frame(self.add_panel, bg=CARD, padx=32, pady=28,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="Fill in the details below",
                 font=FONT_BODY, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0,18))

        self.add_amount = self._form_field(card, "Amount (₹)", "e.g. 350")
        self.add_cat    = self._form_field(card, "Category",   "e.g. Food, Travel, Bills")
        self.add_desc   = self._form_field(card, "Description","e.g. Lunch at Zomato")

        self.add_feedback = tk.Label(card, text="", font=FONT_BODY, bg=CARD)
        self.add_feedback.pack(pady=(8, 0), anchor="w")

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.pack(anchor="w", pady=(12, 0))
        self._action_btn(btn_row, "Add Expense", SUCCESS, "#fff",
                         self._do_add).pack(side="left")
        self._action_btn(btn_row, "  Clear  ", CARD, SUBTEXT,
                         self._clear_add, border=BORDER).pack(side="left", padx=(10, 0))

    def show_add(self):
        self._hide_all_panels()
        self.page_title.config(text="Add Expense")
        self.add_panel.pack(fill="both", expand=True)
        self._clear_add()

    def _do_add(self):
        amount_str  = self.add_amount.get().strip()
        category    = self.add_cat.get().strip()
        description = self.add_desc.get().strip()
        if not amount_str:
            return self._feedback(self.add_feedback, "Amount is required.", DANGER)
        try:
            amount = float(amount_str)
        except ValueError:
            return self._feedback(self.add_feedback, "Enter a valid number for amount.", DANGER)
        if amount <= 0:
            return self._feedback(self.add_feedback, "Amount must be greater than zero.", DANGER)
        if not category:
            return self._feedback(self.add_feedback, "Category cannot be empty.", DANGER)
        if not description:
            return self._feedback(self.add_feedback, "Description cannot be empty.", DANGER)

        add_expense_db(amount, category, description)
        self._feedback(self.add_feedback, "Expense added successfully!", SUCCESS)
        self._clear_add()
        self.refresh_table()

    def _clear_add(self):
        self.add_amount.delete(0, "end")
        self.add_cat.delete(0, "end")
        self.add_desc.delete(0, "end")
        self.add_feedback.config(text="")

    def _build_edit_panel(self):
        self.edit_panel = tk.Frame(self.content, bg=BG)
        card = tk.Frame(self.edit_panel, bg=CARD, padx=32, pady=28,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="Enter the Expense ID you want to update",
                 font=FONT_BODY, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 16))

        id_row = tk.Frame(card, bg=CARD)
        id_row.pack(fill="x", pady=(0, 4))
        tk.Label(id_row, text="Expense ID", font=FONT_BODY,
                 bg=CARD, fg=SUBTEXT, width=14, anchor="w").pack(side="left")
        self.edit_id = tk.Entry(id_row, font=FONT_MONO, bg=BG, fg=TEXT,
                                insertbackground=TEXT, relief="flat",
                                highlightbackground=BORDER, highlightthickness=1,
                                width=10)
        self.edit_id.pack(side="left", ipady=7, padx=(0, 8))
        self._action_btn(id_row, " Load ", ACCENT, "#fff",
                         self._load_expense_for_edit).pack(side="left")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=16)

        self.edit_amount = self._form_field(card, "Amount (₹)", "")
        self.edit_cat    = self._form_field(card, "Category",   "")
        self.edit_desc   = self._form_field(card, "Description","")

        self.edit_feedback = tk.Label(card, text="", font=FONT_BODY, bg=CARD)
        self.edit_feedback.pack(pady=(8, 0), anchor="w")

        self._action_btn(card, "Save Changes", WARNING, "#000",
                         self._do_edit).pack(anchor="w", pady=(12, 0))

    def show_edit(self):
        self._hide_all_panels()
        self.page_title.config(text="Edit Expense")
        self.edit_panel.pack(fill="both", expand=True)
        self.edit_feedback.config(text="")

    def _load_expense_for_edit(self):
        id_str = self.edit_id.get().strip()
        if not id_str:
            return self._feedback(self.edit_feedback, "Enter an Expense ID.", DANGER)
        try:
            eid = int(id_str)
        except ValueError:
            return self._feedback(self.edit_feedback, "ID must be a number.", DANGER)
        if not id_exists(eid):
            return self._feedback(self.edit_feedback,
                                  "No expense found with ID {}.".format(eid), DANGER)

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id=?", (eid,))
        row = cursor.fetchone()
        conn.close()

        self.edit_amount.delete(0, "end"); self.edit_amount.insert(0, str(row[1]))
        self.edit_cat.delete(0, "end");    self.edit_cat.insert(0, row[2])
        self.edit_desc.delete(0, "end");   self.edit_desc.insert(0, row[3])
        self._feedback(self.edit_feedback, "Loaded expense #{}.".format(eid), SUCCESS)

    def _do_edit(self):
        id_str      = self.edit_id.get().strip()
        amount_str  = self.edit_amount.get().strip()
        category    = self.edit_cat.get().strip()
        description = self.edit_desc.get().strip()

        if not id_str:
            return self._feedback(self.edit_feedback, "Enter an Expense ID.", DANGER)
        try:
            eid = int(id_str)
        except ValueError:
            return self._feedback(self.edit_feedback, "ID must be a number.", DANGER)
        if not id_exists(eid):
            return self._feedback(self.edit_feedback,
                                  "No expense found with ID {}.".format(eid), DANGER)
        if not amount_str:
            return self._feedback(self.edit_feedback, "Amount is required.", DANGER)
        try:
            amount = float(amount_str)
        except ValueError:
            return self._feedback(self.edit_feedback, "Enter a valid number for amount.", DANGER)
        if amount <= 0:
            return self._feedback(self.edit_feedback, "Amount must be greater than zero.", DANGER)
        if not category:
            return self._feedback(self.edit_feedback, "Category cannot be empty.", DANGER)
        if not description:
            return self._feedback(self.edit_feedback, "Description cannot be empty.", DANGER)

        update_expense_db(eid, amount, category, description)
        self._feedback(self.edit_feedback, "Expense #{} updated successfully!".format(eid), SUCCESS)
        self.refresh_table()

    def _build_delete_panel(self):
        self.delete_panel = tk.Frame(self.content, bg=BG)
        card = tk.Frame(self.delete_panel, bg=CARD, padx=32, pady=28,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="Enter the Expense ID to permanently delete",
                 font=FONT_BODY, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 16))

        id_row = tk.Frame(card, bg=CARD)
        id_row.pack(fill="x", pady=(0, 4))
        tk.Label(id_row, text="Expense ID", font=FONT_BODY,
                 bg=CARD, fg=SUBTEXT, width=14, anchor="w").pack(side="left")
        self.del_id = tk.Entry(id_row, font=FONT_MONO, bg=BG, fg=TEXT,
                               insertbackground=TEXT, relief="flat",
                               highlightbackground=BORDER, highlightthickness=1,
                               width=10)
        self.del_id.pack(side="left", ipady=7)

        self.del_feedback = tk.Label(card, text="", font=FONT_BODY, bg=CARD)
        self.del_feedback.pack(pady=(16, 0), anchor="w")

        self._action_btn(card, "Delete Expense", DANGER, "#fff",
                         self._do_delete).pack(anchor="w", pady=(12, 0))

        tk.Frame(self.delete_panel, bg=BORDER, height=1).pack(fill="x", pady=16)
        tk.Label(self.delete_panel, text="Current Expenses",
                 font=FONT_HEADER, bg=BG, fg=SUBTEXT).pack(anchor="w")
        self.del_tree_frame = tk.Frame(self.delete_panel, bg=CARD,
                                       highlightbackground=BORDER, highlightthickness=1)
        self.del_tree_frame.pack(fill="both", expand=True, pady=(8, 0))

        cols = ("ID", "Amount (₹)", "Category", "Description")
        self.del_tree = ttk.Treeview(self.del_tree_frame, columns=cols,
                                      show="headings", style="Custom.Treeview",
                                      height=8)
        widths = {"ID": 60, "Amount (₹)": 120, "Category": 160, "Description": 340}
        for col in cols:
            self.del_tree.heading(col, text=col)
            self.del_tree.column(col, width=widths[col],
                                  anchor="center" if col in ("ID","Amount (₹)") else "w")
        self.del_tree.pack(fill="both", expand=True, padx=1, pady=1)
        self.del_tree.bind("<<TreeviewSelect>>", self._on_del_select)

    def show_delete(self):
        self._hide_all_panels()
        self.page_title.config(text="Delete Expense")
        self.delete_panel.pack(fill="both", expand=True)
        self._refresh_del_tree()
        self.del_feedback.config(text="")

    def _refresh_del_tree(self):
        for item in self.del_tree.get_children():
            self.del_tree.delete(item)
        for r in get_all_expenses():
            self.del_tree.insert("", "end",
                                  values=(r[0], "₹{:,.2f}".format(r[1]), r[2], r[3]))

    def _on_del_select(self, event):
        sel = self.del_tree.selection()
        if sel:
            row_id = self.del_tree.item(sel[0])["values"][0]
            self.del_id.delete(0, "end")
            self.del_id.insert(0, str(row_id))

    def _do_delete(self):
        id_str = self.del_id.get().strip()
        if not id_str:
            return self._feedback(self.del_feedback, "  Enter an Expense ID.", DANGER)
        try:
            eid = int(id_str)
        except ValueError:
            return self._feedback(self.del_feedback, "  ID must be a number.", DANGER)
        if not id_exists(eid):
            return self._feedback(self.del_feedback,
                                  " No expense found with ID {}.".format(eid), DANGER)

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Permanently delete expense #{}?\nThis cannot be undone.".format(eid)
        )
        if confirm:
            delete_expense_db(eid)
            self._feedback(self.del_feedback,
                           " Expense #{} deleted.".format(eid), SUCCESS)
            self.del_id.delete(0, "end")
            self._refresh_del_tree()
            self.refresh_table()

    def _build_export_panel(self):
        self.export_panel = tk.Frame(self.content, bg=BG)

        card = tk.Frame(self.export_panel, bg=CARD, padx=32, pady=28,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="Export all your expenses to a CSV file you can open in Excel or Google Sheets.",
                 font=FONT_BODY, bg=CARD, fg=SUBTEXT, wraplength=560, justify="left").pack(anchor="w", pady=(0, 20))

        path_row = tk.Frame(card, bg=CARD)
        path_row.pack(fill="x", pady=(0, 6))
        tk.Label(path_row, text="Save location", font=FONT_BODY,
                 bg=CARD, fg=SUBTEXT, width=14, anchor="w").pack(side="left")
        self.export_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "expenses_report.csv"))
        self.export_path_entry = tk.Entry(path_row, textvariable=self.export_path_var,
                                          font=FONT_SMALL, bg=BG, fg=TEXT,
                                          insertbackground=TEXT, relief="flat",
                                          highlightbackground=BORDER, highlightthickness=1,
                                          width=42)
        self.export_path_entry.pack(side="left", ipady=7, padx=(0, 8))
        self._action_btn(path_row, " Browse ", ACCENT, "#fff",
                         self._browse_export_path).pack(side="left")

        self.export_feedback = tk.Label(card, text="", font=FONT_BODY, bg=CARD)
        self.export_feedback.pack(pady=(14, 0), anchor="w")

        self._action_btn(card, "Export to CSV", SUCCESS, "#fff",
                         self._do_export).pack(anchor="w", pady=(14, 0))

        tk.Frame(self.export_panel, bg=BORDER, height=1).pack(fill="x", pady=16)

        preview_hdr = tk.Frame(self.export_panel, bg=BG)
        preview_hdr.pack(fill="x")
        tk.Label(preview_hdr, text="Data Preview", font=FONT_HEADER,
                 bg=BG, fg=SUBTEXT).pack(side="left")
        self.export_count_label = tk.Label(preview_hdr, text="", font=FONT_SMALL,
                                            bg=BG, fg=SUBTEXT)
        self.export_count_label.pack(side="left", padx=12)

        preview_frame = tk.Frame(self.export_panel, bg=CARD,
                                  highlightbackground=BORDER, highlightthickness=1)
        preview_frame.pack(fill="both", expand=True, pady=(8, 0))

        cols = ("ID", "Amount (₹)", "Category", "Description")
        self.export_tree = ttk.Treeview(preview_frame, columns=cols,
                                         show="headings", style="Custom.Treeview", height=8)
        widths = {"ID": 60, "Amount (₹)": 120, "Category": 160, "Description": 340}
        for col in cols:
            self.export_tree.heading(col, text=col)
            self.export_tree.column(col, width=widths[col],
                                     anchor="center" if col in ("ID", "Amount (₹)") else "w")
        exp_scroll = ttk.Scrollbar(preview_frame, orient="vertical",
                                    command=self.export_tree.yview)
        self.export_tree.configure(yscrollcommand=exp_scroll.set)
        exp_scroll.pack(side="right", fill="y")
        self.export_tree.pack(fill="both", expand=True, padx=1, pady=1)

    def show_export(self):
        self._hide_all_panels()
        self.page_title.config(text="Export to CSV")
        self.export_panel.pack(fill="both", expand=True)
        self.export_feedback.config(text="")
        self._refresh_export_preview()

    def _refresh_export_preview(self):
        for item in self.export_tree.get_children():
            self.export_tree.delete(item)
        rows = get_all_expenses()
        for r in rows:
            self.export_tree.insert("", "end",
                                     values=(r[0], "₹{:,.2f}".format(r[1]), r[2], r[3]))
        count = len(rows)
        self.export_count_label.config(
            text="({} record{} will be exported)".format(count, "s" if count != 1 else "")
        )

    def _browse_export_path(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="expenses_report.csv",
            title="Save CSV as"
        )
        if filepath:
            self.export_path_var.set(filepath)

    def _do_export(self):
        filepath = self.export_path_var.get().strip()
        if not filepath:
            return self._feedback(self.export_feedback, "  Please choose a save location.", DANGER)

        rows = get_all_expenses()
        if not rows:
            return self._feedback(self.export_feedback,
                                  "No expenses to export. Add some first!", WARNING)

        try:
            count = export_to_csv(filepath)
            self._feedback(self.export_feedback,
                           "  {} record{} exported to: {}".format(
                               count, "s" if count != 1 else "", os.path.basename(filepath)), SUCCESS)
        except Exception as e:
            self._feedback(self.export_feedback, "Export failed: {}".format(str(e)), DANGER)

    def _form_field(self, parent, label, placeholder):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, font=FONT_BODY,
                 bg=CARD, fg=SUBTEXT, width=14, anchor="w").pack(side="left")
        entry = tk.Entry(row, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1,
                         width=38)
        entry.pack(side="left", ipady=8, padx=(0, 8))
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=SUBTEXT)
            def on_focus_in(e, en=entry, ph=placeholder):
                if en.get() == ph:
                    en.delete(0, "end")
                    en.config(fg=TEXT)
            def on_focus_out(e, en=entry, ph=placeholder):
                if not en.get():
                    en.insert(0, ph)
                    en.config(fg=SUBTEXT)
            entry.bind("<FocusIn>",  on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            _orig_get = entry.get
            def smart_get(ph=placeholder, en=entry):
                val = _orig_get()
                return "" if val == ph else val
            entry.get = smart_get
        return entry

    def _action_btn(self, parent, text, bg, fg, cmd, border=None):
        btn = tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
                       bg=bg, fg=fg, cursor="hand2", padx=4, pady=8)
        if border:
            btn.config(highlightbackground=border, highlightthickness=1, relief="flat")
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.config(bg=self._lighten(bg)))
        btn.bind("<Leave>",    lambda e: btn.config(bg=bg))
        return btn

    def _lighten(self, hex_color):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        r = min(255, r + 28)
        g = min(255, g + 28)
        b = min(255, b + 28)
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    def _feedback(self, label, msg, color):
        label.config(text=msg, fg=color)

    def _set_status(self, msg):
        self.status_bar.config(text=msg)



if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
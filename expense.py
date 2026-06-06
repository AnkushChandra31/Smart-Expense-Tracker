import sqlite3


# ─────────────────────────────────────────
#  Helper: pretty-print a single expense row
# ─────────────────────────────────────────
def print_expense(row):
    print("""
================================
Expense ID : {}
Amount     : ₹{}
Category   : {}
Description: {}
================================""".format(row[0], row[1], row[2], row[3]))


# ─────────────────────────────────────────
#  Helper: check if an ID actually exists
# ─────────────────────────────────────────
def id_exists(cursor, expense_id):
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    return cursor.fetchone() is not None


# ─────────────────────────────────────────
#  ADD
# ─────────────────────────────────────────
def add_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # --- Amount validation ---
    while True:
        try:
            amount = float(input("Enter Amount: "))
            if amount <= 0:
                print("❌ Amount must be a positive number. Try again.")
                continue
            break
        except ValueError:
            print("❌ Invalid amount. Please enter a valid number.")

    # --- Category validation ---
    while True:
        category = input("Enter Category: ").strip()
        if not category:
            print("❌ Category cannot be empty. Try again.")
        else:
            break

    # --- Description validation ---
    while True:
        description = input("Enter Description: ").strip()
        if not description:
            print("❌ Description cannot be empty. Try again.")
        else:
            break

    cursor.execute(
        "INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)",
        (amount, category, description)
    )
    conn.commit()
    print("\n✅ Expense added successfully!")
    conn.close()


# ─────────────────────────────────────────
#  VIEW
# ─────────────────────────────────────────
def view_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    if not rows:
        print("\n📭 No expenses found. Start by adding one!\n")
    else:
        print("\n📋 All Expenses:")
        for row in rows:
            print_expense(row)

    conn.close()
    return rows   # useful for delete to reuse


# ─────────────────────────────────────────
#  UPDATE
# ─────────────────────────────────────────
def update_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # Show current expenses first
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    if not rows:
        print("\n📭 No expenses found. Nothing to update.\n")
        conn.close()
        return

    print("\n📋 Current Expenses:")
    for row in rows:
        print_expense(row)

    # --- ID validation ---
    while True:
        try:
            expense_id = int(input("Enter Expense ID to Update: "))
            if not id_exists(cursor, expense_id):
                print("❌ No expense found with ID {}. Try again.".format(expense_id))
            else:
                break
        except ValueError:
            print("❌ Invalid ID. Please enter a number.")

    # --- New Amount validation ---
    while True:
        try:
            new_amount = float(input("Updated Amount: "))
            if new_amount <= 0:
                print("❌ Amount must be a positive number. Try again.")
                continue
            break
        except ValueError:
            print("❌ Invalid amount. Please enter a valid number.")

    # --- New Category validation ---
    while True:
        new_category = input("New Category: ").strip()
        if not new_category:
            print("❌ Category cannot be empty. Try again.")
        else:
            break

    # --- New Description validation ---
    while True:
        new_description = input("New Description: ").strip()
        if not new_description:
            print("❌ Description cannot be empty. Try again.")
        else:
            break

    cursor.execute(
        "UPDATE expenses SET amount = ?, category = ?, description = ? WHERE id = ?",
        (new_amount, new_category, new_description, expense_id)
    )
    conn.commit()
    print("\n✅ Expense updated successfully!")
    conn.close()


# ─────────────────────────────────────────
#  DELETE
# ─────────────────────────────────────────
def delete_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    if not rows:
        print("\n📭 No expenses found. Nothing to delete.\n")
        conn.close()
        return

    print("\n📋 Current Expenses:")
    for row in rows:
        print_expense(row)

    # --- ID validation ---
    while True:
        try:
            expense_id = int(input("Enter Expense ID to Delete: "))
            if not id_exists(cursor, expense_id):
                print("❌ No expense found with ID {}. Try again.".format(expense_id))
            else:
                break
        except ValueError:
            print("❌ Invalid ID. Please enter a number.")

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    print("\n✅ Expense deleted successfully!")
    conn.close()

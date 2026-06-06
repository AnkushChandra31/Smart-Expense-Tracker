import sqlite3


def print_expense(row):
    print("""
================================
Expense ID : {}
Amount     : ₹{}
Category   : {}
Description: {}
================================""".format(row[0], row[1], row[2], row[3]))


def id_exists(cursor, expense_id):
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    return cursor.fetchone() is not None


def add_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # --- Amount validation ---
    while True:
        try:
            amount = float(input("Enter Amount: "))
            if amount <= 0:
                print("Amount must be a positive number. Try again.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a valid number.")

    while True:
        category = input("Enter Category: ").strip()
        if not category:
            print("Category cannot be empty. Try again.")
        else:
            break

    while True:
        description = input("Enter Description: ").strip()
        if not description:
            print("Description cannot be empty. Try again.")
        else:
            break

    cursor.execute(
        "INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)",
        (amount, category, description)
    )
    conn.commit()
    print("\nExpense added successfully!")
    conn.close()


def view_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    if not rows:
        print("\nNo expenses found. Start by adding one!\n")
    else:
        print("\nAll Expenses:")
        for row in rows:
            print_expense(row)

    conn.close()
    return rows   

def update_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    if not rows:
        print("\nNo expenses found. Nothing to update.\n")
        conn.close()
        return

    print("\nCurrent Expenses:")
    for row in rows:
        print_expense(row)

    while True:
        try:
            expense_id = int(input("Enter Expense ID to Update: "))
            if not id_exists(cursor, expense_id):
                print("No expense found with ID {}. Try again.".format(expense_id))
            else:
                break
        except ValueError:
            print("Invalid ID. Please enter a number.")

    while True:
        try:
            new_amount = float(input("Updated Amount: "))
            if new_amount <= 0:
                print("Amount must be a positive number. Try again.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a valid number.")

    while True:
        new_category = input("New Category: ").strip()
        if not new_category:
            print("Category cannot be empty. Try again.")
        else:
            break

    while True:
        new_description = input("New Description: ").strip()
        if not new_description:
            print("Description cannot be empty. Try again.")
        else:
            break

    cursor.execute(
        "UPDATE expenses SET amount = ?, category = ?, description = ? WHERE id = ?",
        (new_amount, new_category, new_description, expense_id)
    )
    conn.commit()
    print("\nExpense updated successfully!")
    conn.close()


def delete_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    if not rows:
        print("\n📭 No expenses found. Nothing to delete.\n")
        conn.close()
        return

    print("\nCurrent Expenses:")
    for row in rows:
        print_expense(row)

    while True:
        try:
            expense_id = int(input("Enter Expense ID to Delete: "))
            if not id_exists(cursor, expense_id):
                print("No expense found with ID {}. Try again.".format(expense_id))
            else:
                break
        except ValueError:
            print("Invalid ID. Please enter a number.")

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    print("\nExpense deleted successfully!")
    conn.close()

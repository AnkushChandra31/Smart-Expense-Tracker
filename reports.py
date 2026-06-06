import sqlite3
import csv

def export_to_csv():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    with open("expenses_report.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(["ID", "Amount", "Category", "Description"])

        writer.writerows(expenses)

    conn.close()

    print("Data Exported Successfully to expenses_report.csv")
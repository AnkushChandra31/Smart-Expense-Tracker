from database import *
from expense import add_expenses, view_expenses, update_expenses, delete_expenses
from reports import export_to_csv

while True:
    print("""
======== Welcome To Smart Expense Tracker ========

  1. Add Expense
  2. View Expenses
  3. Update Expense
  4. Delete Expense
  5. Export to CSV
  6. Exit
""")

    choice = input("Enter Your Choice: ").strip()

    if choice == "1":
        add_expenses()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        update_expenses()

    elif choice == "4":
        delete_expenses()

    elif choice == "5":
        export_to_csv()

    elif choice == "6":
        print("\nThanks for using Smart Expense Tracker. Goodbye!\n")
        break                  
    else:
        print("Invalid choice. Please enter a number between 1 and 5.")

#!/home/fcurcio/anaconda3/envs/ML/bin/python3

import argparse
from BudgetTracker import BudgetTracker
from datetime import datetime, timedelta
import readline
import atexit
HIST_FILE = ".tracker_history"

def main():
    try:
        readline.read_history_file(HIST_FILE)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, HIST_FILE)
    parser = argparse.ArgumentParser(description="Budget Tracker CLI")
    parser.add_argument("--add", nargs=4, metavar=('DATE', 'CATEGORY', 'DESCRIPTION', 'AMOUNT'), help="Add a transaction")
    parser.add_argument("--view", action='store_true', help="View summary")
    parser.add_argument("--balance", action='store_true', help="Calculate balance")
    parser.add_argument("--print", action='store_true', help="Print transactions")
    parser.add_argument("--delete", metavar='ID', type=int, help="Delete a transaction by ID")
    parser.add_argument("--modify", nargs=5, metavar=('ID', 'DATE', 'CATEGORY', 'DESCRIPTION', 'AMOUNT'), help="Modify a transaction")
    parser.add_argument("--filter", nargs=3, metavar=('CATEGORY', 'START_DATE', 'END_DATE'),
                    help="Filter transactions by category and/or date range")

    args = parser.parse_args()

    tracker = BudgetTracker()

    if args.add:
        date, category, description, amount = args.add
        if date.lower() == "today":
            date = datetime.today().strftime('%Y-%m-%d')
        elif date.lower() == "yesterday":
            date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        amount = float(amount)
        tracker.add_transaction(date, category, description, amount)
        print("Transaction added successfully!")

    elif args.view:
        tracker.view_summary()

    elif args.balance:
        tracker.calculate_balance()

    elif args.print:
        tracker.print_transactions()

    elif args.delete:
        tracker.delete_transaction(args.delete)

    elif args.modify:
        transaction_id, date, category, description, amount = args.modify
        date = date if date != 'None' else None
        category = category if category != 'None' else None
        description = description if description != 'None' else None
        amount = float(amount) if amount != 'None' else None
        tracker.modify_transaction(transaction_id, date, category, description, amount)
    
    elif args.filter:
        category, start_date, end_date = args.filter
        category = None if category == "None" else category
        start_date = None if start_date == "None" else start_date
        end_date = None if end_date == "None" else end_date
        tracker.filter_transactions(category, start_date, end_date)


    else:
        while True:
            try:
                print("\nBudget Tracker Options:")
                print("0. Add Transaction")
                print("1. View Summary")
                print("2. Calculate Balance")
                print("3. Print Transactions")
                print("4. Delete Transaction")
                print("5. Modify Transaction")
                print("6. Filter Transactions")
                print("7. Exit")

                choice = input("Enter your choice: ")

                if choice == "0":
                    date_input = input("Enter the date (YYYY-MM-DD) or 'today'/'yesterday': ")
                    if date_input.lower() == "today":
                        date = datetime.today().strftime('%Y-%m-%d')
                    elif date_input.lower() == "yesterday":
                        date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                    else:
                        date = date_input
                    categories = tracker.get_categories()
                    print("Select a category from the list or enter a new one:")
                    for i, cat in enumerate(categories):
                        print(f"{i}. {cat}")
                    category_input = input("Enter the category number or a new category: ")
                    if category_input.isdigit() and int(category_input) < len(categories):
                        category = categories[int(category_input)]
                    else:
                        category = category_input
                    description = input("Enter a description: ")
                    amount = float(input("Enter the amount (use negative for expenses): "))
                    tracker.add_transaction(date, category, description, amount)
                    print("Transaction added successfully!")

                elif choice == "1":
                    start_date_input = input("Enter start date (YYYY-MM-DD, 'today', 'yesterday', leave blank for no start date): ") or None
                    if start_date_input and start_date_input.lower() == "today":
                        start_date = datetime.today().strftime('%Y-%m-%d')
                    elif start_date_input and start_date_input.lower() == "yesterday":
                        start_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                    else:
                        start_date = start_date_input

                    end_date_input = input("Enter end date (YYYY-MM-DD, 'today', 'yesterday', leave blank for no end date): ") or None
                    if end_date_input and end_date_input.lower() == "today":
                        end_date = datetime.today().strftime('%Y-%m-%d')
                    elif end_date_input and end_date_input.lower() == "yesterday":
                        end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                    else:
                        end_date = end_date_input
                    tracker.view_summary(start_date, end_date)

                elif choice == "2":
                    tracker.calculate_balance()

                elif choice == "3":
                    tracker.print_transactions()

                elif choice == "4":
                    transaction_id = int(input("Enter the transaction ID to delete: "))
                    tracker.delete_transaction(transaction_id)

                elif choice == "5":
                    transaction_id = int(input("Enter the transaction ID to modify: "))
                    date = input("Enter the new date (leave blank to keep unchanged): ") or None
                    category = input("Enter the new category (leave blank to keep unchanged): ") or None
                    description = input("Enter the new description (leave blank to keep unchanged): ") or None
                    amount = input("Enter the new amount (leave blank to keep unchanged): ")
                    amount = float(amount) if amount else None
                    tracker.modify_transaction(transaction_id, date, category, description, amount)
                
                elif choice == "6":
                    category = input("Enter category to filter (leave blank for all): ") or None
                    start_date = input("Enter start date (YYYY-MM-DD, leave blank for no start date): ") or None
                    end_date = input("Enter end date (YYYY-MM-DD, leave blank for no end date): ") or None
                    tracker.filter_transactions(category, start_date, end_date)

                elif choice == "7":
                    print("Exiting Budget Tracker. Goodbye!")
                    break

                else:
                    print("Invalid choice. Please try again.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Budget Tracker. Goodbye!")
                break

if __name__ == "__main__":
    main()
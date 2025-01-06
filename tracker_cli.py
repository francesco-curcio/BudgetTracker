#!/home/fcurcio/anaconda3/envs/ML/bin/python3

import argparse
from BudgetTracker import BudgetTracker
from datetime import datetime, timedelta
import readline
import atexit

HIST_FILE = ".tracker_history"

def formatted_input(prompt: str, example: str = "", separator: str = "-") -> str:
    print(separator * 50)
    print(f"{prompt}")
    if example:
        print(f"Example: {example}")
    print(separator * 50)
    return input("> ")

def setup_readline():
    try:
        readline.read_history_file(HIST_FILE)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, HIST_FILE)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Budget Tracker CLI")
    parser.add_argument("--add", nargs=4, metavar=('DATE', 'CATEGORY', 'DESCRIPTION', 'AMOUNT'), help="Add a transaction")
    parser.add_argument("--view", action='store_true', help="View summary")
    parser.add_argument("--balance", action='store_true', help="Calculate balance")
    parser.add_argument("--print", action='store_true', help="Print transactions")
    parser.add_argument("--delete", metavar='ID', type=int, help="Delete a transaction by ID")
    parser.add_argument("--modify", nargs=5, metavar=('ID', 'DATE', 'CATEGORY', 'DESCRIPTION', 'AMOUNT'), help="Modify a transaction")
    parser.add_argument("--filter", nargs=3, metavar=('CATEGORY', 'START_DATE', 'END_DATE'), help="Filter transactions by category and/or date range")
    return parser.parse_args()

def handle_add(tracker, args):
    date, category, description, amount = args.add
    date = resolve_date(date)
    amount = float(amount)
    tracker.add_transaction(date, category, description, amount)
    print("Transaction added successfully!")

def resolve_date(date_str):
    if date_str.lower() == "today":
        return datetime.today().strftime('%Y-%m-%d')
    elif date_str.lower() == "yesterday":
        return (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    return date_str

def handle_modify(tracker, args):
    transaction_id, date, category, description, amount = args.modify
    date = date if date != 'None' else None
    category = category if category != 'None' else None
    description = description if description != 'None' else None
    amount = float(amount) if amount != 'None' else None
    tracker.modify_transaction(transaction_id, date, category, description, amount)

def handle_filter(tracker, args):
    category, start_date, end_date = args.filter
    category = None if category == "None" else category
    start_date = None if start_date == "None" else start_date
    end_date = None if end_date == "None" else end_date
    tracker.filter_transactions(category, start_date, end_date)

def interactive_mode(tracker, first_time):
    while True:
        try:
            print("=" * 50)
            if first_time:
                print(" " * 15 + "WELCOME TO BUDGET TRACKER")
                print("=" * 50)
                first_time = False
            else:
                print(" " * 15 + "MAIN MENU")
                print("=" * 50)
            print("Your personal tool to track and manage finances efficiently.\n")
            print("Here are your options:\n")
            print("  [0] Add Transaction     - Record an income or expense")
            print("  [1] View Summary        - See an overview of expenses by category")
            print("  [2] Calculate Balance   - Check your current account balance")
            print("  [3] Print Transactions  - List all recorded transactions")
            print("  [4] Delete Transaction  - Remove a transaction by its ID")
            print("  [5] Modify Transaction  - Update details of an existing transaction")
            print("  [6] Filter Transactions - View specific transactions by category/date")
            print("  [7] Exit                - Close the application")
            print("\n" + "=" * 50)
            print("Use the numbers above to choose an action and press Enter.")
            print("Type 'Ctrl+C'/'Ctrl+D' at any time to exit.\n")

            choice = formatted_input("Enter your choice: ")

            if choice == "0":
                handle_interactive_add(tracker)
            elif choice == "1":
                handle_interactive_view(tracker)
            elif choice == "2":
                tracker.calculate_balance()
            elif choice == "3":
                tracker.print_transactions()
            elif choice == "4":
                transaction_id = int(input("Enter the transaction ID to delete: "))
                tracker.delete_transaction(transaction_id)
            elif choice == "5":
                handle_interactive_modify(tracker)
            elif choice == "6":
                handle_interactive_filter(tracker)
            elif choice == "7":
                print("Exiting Budget Tracker. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Budget Tracker. Goodbye!")
            break

def handle_interactive_add(tracker):
    date_input = formatted_input(
        "Enter the date (YYYY-MM-DD) or 'today'/'yesterday': ",
        example="2025-01-01")
    date = resolve_date(date_input)
    categories = tracker.get_categories()
    print("Select a category from the list or enter a new one:")
    for i, cat in enumerate(categories):
        print(f"{i}. {cat}")
    category_input = formatted_input("Enter the category number or a new category: ")
    category = categories[int(category_input)] if category_input.isdigit() and int(category_input) < len(categories) else category_input
    description = formatted_input(
        "Enter a short description of the transaction: ",
        example="Lunch with friends")
    amount = float(formatted_input(
        "Enter the amount (use negative for expenses, postive for income): ",
        example="-25.50"))
    tracker.add_transaction(date, category, description, amount)
    print("Transaction added successfully!")

def handle_interactive_view(tracker):
    start_date = resolve_date_input("Enter start date (YYYY-MM-DD, 'today', 'yesterday', leave blank for no start date): ")
    end_date = resolve_date_input("Enter end date (YYYY-MM-DD, 'today', 'yesterday', leave blank for no end date): ")
    future_days_input = formatted_input("Enter the number of days to predict (0 for no prediction, leave blank for no prediction): ")
    future_days = int(future_days_input) if future_days_input else None
    tracker.view_summary(start_date, end_date, future_days)

def resolve_date_input(prompt):
    date_input = formatted_input(prompt) or None
    return resolve_date(date_input) if date_input else None

def handle_interactive_modify(tracker):
    transaction_id = int(formatted_input("Enter the transaction ID to modify: "))
    date_input = formatted_input("Enter the new date (leave blank to keep unchanged, 'today', 'yesterday'): ") or None
    date = resolve_date(date_input) if date_input else None
    category = formatted_input("Enter the new category (leave blank to keep unchanged): ") or None
    description = formatted_input("Enter the new description (leave blank to keep unchanged): ") or None
    amount = formatted_input("Enter the new amount (leave blank to keep unchanged): ")
    amount = float(amount) if amount else None
    tracker.modify_transaction(transaction_id, date, category, description, amount)

def handle_interactive_filter(tracker):
    category = formatted_input("Enter category to filter (leave blank for all): ") or None
    start_date = formatted_input("Enter start date (YYYY-MM-DD, leave blank for no start date): ") or None
    end_date = formatted_input("Enter end date (YYYY-MM-DD, leave blank for no end date): ") or None
    tracker.filter_transactions(category, start_date, end_date)

def main():
    setup_readline()
    args = parse_arguments()
    tracker = BudgetTracker()
    first_time = True

    if args.add:
        handle_add(tracker, args)
    elif args.view:
        tracker.view_summary()
    elif args.balance:
        tracker.calculate_balance()
    elif args.print:
        tracker.print_transactions()
    elif args.delete:
        tracker.delete_transaction(args.delete)
    elif args.modify:
        handle_modify(tracker, args)
    elif args.filter:
        handle_filter(tracker, args)
    else:
        interactive_mode(tracker, first_time)

if __name__ == "__main__":
    main()

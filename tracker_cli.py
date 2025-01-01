#!/home/fcurcio/anaconda3/envs/ML/bin/python3

from BudgetTracker import BudgetTracker
from datetime import datetime, timedelta

if __name__ == "__main__":
    tracker = BudgetTracker()

    while True:
        try:
            print("\nBudget Tracker Options:")
            print("0. Add Transaction")
            print("1. View Summary")
            print("2. Calculate Balance")
            print("3. Print Transactions")
            print("4. Delete Transaction")
            print("5. Modify Transaction")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if choice == "0":
                date_input = input("Enter the date (YYYY-MM-DD) or 'today'/'yesterday': ")
                if date_input.lower() == "today":
                    date = datetime.today().strftime('%Y-%m-%d')
                elif date_input.lower() == "yesterday":
                    date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    date = date_input
                # read categories from db
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
                tracker.view_summary()

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
                print("Exiting Budget Tracker. Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\nExiting Budget Tracker. Goodbye!")
            break
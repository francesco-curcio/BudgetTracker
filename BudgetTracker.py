import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

class BudgetTracker:
    def __init__(self, db_file="budget_data.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()
        self.initialize_data_file()

    def create_table(self):
        """Create the transactions table if it doesn't exist."""
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL
            )
            """)

    def initialize_data_file(self):
        """Initialize the database with the initial amount if the table is empty."""
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT COUNT(*) FROM transactions")
        count = self.cursor.fetchone()[0]
        if count == 0:
            initial_amount = float(input("Enter the initial amount of money in the account: "))
            if initial_amount < 0:
                raise ValueError("Initial amount must be a positive number.")
            today = pd.Timestamp("today").strftime('%Y-%m-%d')
            initial_transaction = (today, "Initial", "Initial Amount", initial_amount)
            with self.conn:
                self.conn.execute("""
                    INSERT INTO transactions (date, category, description, amount)
                    VALUES (?, ?, ?, ?)
                """, initial_transaction)

    def add_transaction(self, date, category, description, amount):
        """Add a new transaction to the database."""
        new_transaction = (date, category, description, amount)
        with self.conn:
            self.conn.execute("""
                INSERT INTO transactions (date, category, description, amount)
                VALUES (?, ?, ?, ?)
            """, new_transaction)

    def view_summary(self):
        """Visualize a summary of expenses by category."""
        summary_query = """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE category != 'Initial'
            GROUP BY category;
        """
        self.cursor.execute(summary_query)
        summary = self.cursor.fetchall()

        categories = [row[0] for row in summary]
        totals = [abs(row[1]) for row in summary]  # Use absolute value to account for negative expenses

        print("\nExpense Summary by Category:")
        for category, total in zip(categories, totals):
            print(f"{category}: {total:.2f}")

        # Visualization
        plt.figure(figsize=(8, 6))
        plt.bar(categories, totals, color="skyblue")
        plt.xlabel("Category")
        plt.ylabel("Total Amount")
        plt.title("Expenses by Category")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def calculate_balance(self):
        """Calculate the current balance (total income - total expenses)."""
        df = pd.read_sql_query("SELECT SUM(amount) as balance FROM transactions", self.conn)
        balance = df['balance'].iloc[0]
        print(f"\nCurrent Balance: {balance:.2f}")
    
    def print_transactions(self):
        """Print all transactions in the database."""
        df = pd.read_sql_query("SELECT * FROM transactions", self.conn, index_col='id')
        print("\nAll Transactions:")
        print(df)
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by its ID."""
        delete_query = "DELETE FROM transactions WHERE id = ?;"
        self.cursor.execute(delete_query, (transaction_id,))
        self.conn.commit()
        print(f"Transaction with ID {transaction_id} deleted successfully.")
    
    def modify_transaction(self, transaction_id, date=None, category=None, description=None, amount=None):
        """Modify an existing transaction."""
        update_query = "UPDATE transactions SET "
        updates = []
        params = []

        if date:
            updates.append("date = ?")
            params.append(date)
        if category:
            updates.append("category = ?")
            params.append(category)
        if description:
            updates.append("description = ?")
            params.append(description)
        if amount:
            updates.append("amount = ?")
            params.append(amount)

        update_query += ", ".join(updates) + " WHERE id = ?;"
        params.append(transaction_id)

        self.cursor.execute(update_query, params)
        self.conn.commit()
        print(f"Transaction with ID {transaction_id} updated successfully.")
    
    def get_categories(self):
        """Retrieve a list of unique categories from the database."""
        categories_query = "SELECT DISTINCT category FROM transactions;"
        self.cursor.execute(categories_query)
        categories = [row[0] for row in self.cursor.fetchall()]
        return categories
    
    def filter_transactions(self, category=None, start_date=None, end_date=None):
        """Filter transactions by category and/or date range."""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        df = pd.read_sql_query(query, self.conn, params=params)
        print("\nFiltered Transactions:")
        print(df)
    
    def get_all_transactions(self):
        """Retrieve all transactions from the database."""
        df = pd.read_sql_query("SELECT * FROM transactions", self.conn)
        return df.values.tolist()  # Restituisce una lista di transazioni

    def get_filtered_transactions(self, category=None, date=None):
        """Retrieve transactions filtered by category and/or date."""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if date:
            query += " AND date = ?"
            params.append(date)

        self.cursor.execute(query, params)
        transactions = self.cursor.fetchall()
        return transactions


    
    def __del__(self):
        """Close the database connection when the object is deleted."""
        self.conn.close()
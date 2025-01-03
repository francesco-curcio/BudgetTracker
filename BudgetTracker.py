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

    def view_summary(self, start_date=None, end_date=None):
        """Visualize a summary of expenses by category with optional filters."""
        summary_query = """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE 1=1
        """
        params = []

        if start_date:
            summary_query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            summary_query += " AND date <= ?"
            params.append(end_date)

        summary_query += " GROUP BY category;"
        df_summary = pd.read_sql_query(summary_query, self.conn, params=params)

        print("\nExpense Summary by Category:")
        for _, row in df_summary.iterrows():
            print(f"{row['category']}: {row['total']:.2f}")

        # Visualization
        fig, axs = plt.subplots(2, 2, figsize=(18, 10))

        # Bar plot
        colors = ['green' if total >= 0 else 'red' for total in df_summary['total']]
        axs[0, 0].bar(df_summary['category'], df_summary['total'], color=colors)
        axs[0, 0].set_xlabel("Category")
        axs[0, 0].set_ylabel("Total Amount")
        axs[0, 0].set_title("Expenses by Category")

        # Pie chart
        expenses = df_summary[df_summary['total'] < 0]
        axs[0, 1].pie(abs(expenses['total']), labels=expenses['category'], autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.3))
        axs[0, 1].axis('equal')
        axs[0, 1].set_title("Expense Distribution by Category")

        # Time graph of account balance
        balance_query = """
            SELECT date, SUM(amount) OVER (ORDER BY date) as balance
            FROM transactions
            WHERE 1=1
        """
        if start_date:
            balance_query += " AND date >= ?"
        if end_date:
            balance_query += " AND date <= ?"

        df_balance = pd.read_sql_query(balance_query, self.conn, params=params)
        df_balance['date'] = pd.to_datetime(df_balance['date'])

        axs[1, 0].plot(df_balance['date'], df_balance['balance'], marker='o')
        axs[1, 0].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d-%m-%Y'))
        if len(df_balance['date'].dt.date.unique()) < 10:
            axs[1, 0].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=1))
        axs[1, 0].set_xlabel("Date")
        axs[1, 0].set_ylabel("Balance")
        axs[1, 0].set_title("Account Balance Over Time")
        axs[1, 0].tick_params(axis='x', rotation=45)

        # as last plot show the a bar plot with a red bar that sums all the negative values and a green bar that sums all the positive values
        total_income = df_summary[df_summary['total'] > 0]['total'].sum()
        total_expenses = abs(df_summary[df_summary['total'] < 0]['total'].sum())
        total_values = [total_income, total_expenses]
        colors = ['green', 'red']
        axs[1, 1].bar(['Income', 'Expenses'], total_values, color=colors, width=1.)
        axs[1, 1].set_xlabel("Category")
        axs[1, 1].set_ylabel("Total Amount")
        axs[1, 1].set_title("Total Income vs Total Expenses")

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
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple

class BudgetTracker:
    def __init__(self, db_file: str = "budget_data.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()
        self.initialize_data_file()

    def create_table(self) -> None:
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

    def initialize_data_file(self, initial_amount: Optional[float] = None) -> None:
        """Initialize the database with the initial amount if the table is empty."""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            if count == 0:
                if initial_amount is None:
                    initial_amount = float(input("Enter the initial amount of money in the account: "))
                if initial_amount < 0:
                    raise ValueError("Initial amount must be a positive number.")
                today = pd.Timestamp("today").strftime('%Y-%m-%d')
                initial_transaction = (today, "Initial", "Initial Amount", initial_amount)
                cursor.execute("""
                    INSERT INTO transactions (date, category, description, amount)
                    VALUES (?, ?, ?, ?)
                """, initial_transaction)

    def add_transaction(self, date: str, category: str, description: str, amount: float) -> None:
        """Add a new transaction to the database."""
        new_transaction = (date, category, description, amount)
        with self.conn:
            self.conn.execute("""
                INSERT INTO transactions (date, category, description, amount)
                VALUES (?, ?, ?, ?)
            """, new_transaction)

    def view_summary(self, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, 
                     future_days: Optional[int] = None) -> None:
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
        axs[0, 0].xaxis.set_tick_params(rotation=45)

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

        # Remove duplicate dates
        df_balance = df_balance.drop_duplicates(subset='date')

        # Ensure dates are spaced by 1 day
        all_dates = pd.date_range(start=df_balance['date'].min(), end=df_balance['date'].max())
        df_balance = df_balance.set_index('date').reindex(all_dates, method='ffill').reset_index()
        df_balance.columns = ['date', 'balance']

        axs[1, 0].plot(df_balance['date'], df_balance['balance'], marker='o')
        axs[1, 0].set_xlabel("Date")
        axs[1, 0].set_ylabel("Balance")
        axs[1, 0].set_title("Account Balance Over Time")
        axs[1, 0].tick_params(axis='x', rotation=45)

        # Naive prediction of future balance
        if not df_balance.empty and future_days is not None:
            last_balance = df_balance['balance'].iloc[-1]
            daily_max_change = df_balance['balance'].diff().max()
            # daily_min_change = df_balance['balance'].diff().min()
            daily_mean_change = df_balance['balance'].diff().mean()
            future_dates = pd.date_range(df_balance['date'].iloc[-1] + pd.Timedelta(days=1), periods=future_days)
            future_max_balances = [last_balance + daily_max_change * i for i in range(1, future_days + 1)]
            # future_min_balances = [last_balance + daily_min_change * i for i in range(1, future_days + 1)]
            future_mean_balances = [last_balance + daily_mean_change * i for i in range(1, future_days + 1)]

            # Connect the last point with the future lines
            future_dates = pd.to_datetime([df_balance['date'].iloc[-1]] + list(future_dates))
            future_max_balances = [last_balance] + future_max_balances
            # future_min_balances = [last_balance] + future_min_balances
            future_mean_balances = [last_balance] + future_mean_balances

            axs[1, 0].plot(future_dates, future_max_balances, linestyle='--', color='orange', label='Max Predicted Balance')
            # axs[1, 0].plot(future_dates, future_min_balances, linestyle='--', color='blue', label='Min Predicted Balance')
            axs[1, 0].plot(future_dates, future_mean_balances, linestyle='--', color='green', label='Mean Predicted Balance')
            axs[1, 0].legend()

        # line at 0
        axs[1, 0].axhline(y=0, color='black', linestyle='--')

        axs[1, 0].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d-%m-%Y'))
        n_days = len(df_balance['date'].dt.date.unique()) + future_days if future_days is not None else len(df_balance['date'].dt.date.unique())
        if n_days < 10:
            axs[1, 0].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=1))
        else:
            axs[1, 0].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=5))

        # Total Income vs Total Expenses
        total_income = df_summary[df_summary['total'] > 0]['total'].sum()
        total_expenses = abs(df_summary[df_summary['total'] < 0]['total'].sum())
        total_values = [total_income, total_expenses]
        colors = ['green', 'red']
        axs[1, 1].bar(['Income', 'Expenses'], total_values, color=colors, width=1.0)
        axs[1, 1].set_xlabel("Category")
        axs[1, 1].set_ylabel("Total Amount")
        axs[1, 1].set_title("Total Income vs Total Expenses")

        plt.tight_layout()
        plt.show()

    def calculate_balance(self) -> None:
        """Calculate the current balance (total income - total expenses)."""
        df = pd.read_sql_query("SELECT SUM(amount) as balance FROM transactions", self.conn)
        balance = df['balance'].iloc[0]
        print(f"\nCurrent Balance: {balance:.2f}")

    def print_transactions(self) -> None:
        """Print all transactions in the database."""
        df = pd.read_sql_query("SELECT * FROM transactions", self.conn, index_col='id')
        print("\nAll Transactions:")
        print(df)

    def delete_transaction(self, transaction_id: int) -> None:
        """Delete a transaction by its ID."""
        with self.conn:
            self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        print(f"Transaction with ID {transaction_id} deleted successfully.")

    def modify_transaction(self, transaction_id: int, date: Optional[str] = None, category: Optional[str] = None, description: Optional[str] = None, amount: Optional[float] = None) -> None:
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

        with self.conn:
            self.conn.execute(update_query, params)
        print(f"Transaction with ID {transaction_id} updated successfully.")

    def get_categories(self) -> List[str]:
        """Retrieve a list of unique categories from the database."""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM transactions;")
            categories = [row[0] for row in cursor.fetchall()]
        return categories

    def filter_transactions(self, category: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
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

    def get_all_transactions(self) -> List[Tuple]:
        """Retrieve all transactions from the database."""
        df = pd.read_sql_query("SELECT * FROM transactions", self.conn)
        return df.values.tolist()

    def get_filtered_transactions(self, category: Optional[str] = None, date: Optional[str] = None) -> List[Tuple]:
        """Retrieve transactions filtered by category and/or date."""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if date:
            query += " AND date = ?"
            params.append(date)

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            transactions = cursor.fetchall()
        return transactions

    def __del__(self):
        """Close the database connection when the object is deleted."""
        self.conn.close()
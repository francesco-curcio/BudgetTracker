# Budget Tracker

## Overview
The Budget Tracker project is a Python-based Command Line Interface (CLI) application for managing personal finances. It allows users to track transactions, view summaries, calculate balances, and filter data based on various criteria. The application uses SQLite for storing transaction data and provides both a scripted and an interactive mode.

## Features
- **Add Transactions**: Record income or expenses with details such as date, category, description, and amount.
- **View Summary**: Display expense summaries by category and visualize data with graphs.
- **Calculate Balance**: Show the current account balance based on all recorded transactions.
- **Filter Transactions**: Filter data by category, date range, or both.
- **Interactive Mode**: User-friendly interactive prompts for managing your budget.
- **Modify/Delete Transactions**: Update or remove existing entries.

## Requirements
- Python 3.8+
- Libraries:
  - `sqlite3` (built-in with Python)
  - `pandas`
  - `matplotlib`

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd budget-tracker
   ```
2. Set up a virtual environment (optional):
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   ```
3. Install required dependencies:
   ```bash
   pip install pandas matplotlib
   ```

## Usage
### Command Line Options
Run the application with various options to perform specific actions:
```bash
python tracker_cli.py [OPTIONS]
```

#### Options:
- `--add DATE CATEGORY DESCRIPTION AMOUNT`:
  Add a transaction (e.g., `--add today Food "Lunch at cafe" -15.50`).
- `--view`:
  View summary of transactions by category.
- `--balance`:
  Calculate and display the current account balance.
- `--print`:
  Print all transactions.
- `--delete ID`:
  Delete a transaction by its ID.
- `--modify ID DATE CATEGORY DESCRIPTION AMOUNT`:
  Modify an existing transaction (use `None` to skip fields).
- `--filter CATEGORY START_DATE END_DATE`:
  Filter transactions based on category and/or date range.

### Interactive Mode
Launch the interactive mode to use the application without command-line arguments:
```bash
python tracker_cli.py
```
Follow the on-screen prompts to perform various operations.

### Example
Adding a new transaction:
```bash
python tracker_cli.py --add today Groceries "Weekly shopping" -50.00
```
Viewing the account balance:
```bash
python tracker_cli.py --balance
```

## Data Storage
The application stores all transactions in an SQLite database (`budget_data.db`). This file is created automatically in the current directory if it does not exist.

## Development
### File Structure
- `BudgetTracker.py`: Contains the main `BudgetTracker` class with core functionality.
- `tracker_cli.py`: CLI interface for interacting with the budget tracker.

### Contribution
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## Future Improvements
- Export/import transactions in CSV format.
- Set monthly budgets with notifications for overspending.
- Additional analytics, such as spending trends.
# database.py

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import atexit
import logging

# Setup logging
logging.basicConfig(
    filename='database.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Connect to SQLite database
conn = sqlite3.connect('finance_app.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
def create_tables():
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                FOREIGN KEY(user) REFERENCES users(username)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS expense (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                FOREIGN KEY(user) REFERENCES users(username)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                FOREIGN KEY(user) REFERENCES users(username)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS recurring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                type TEXT NOT NULL, -- 'income' or 'expense'
                date TEXT NOT NULL, -- Next occurrence date
                category TEXT NOT NULL,
                subcategory TEXT,
                amount REAL NOT NULL,
                frequency TEXT NOT NULL, -- 'daily', 'weekly', 'monthly'
                currency TEXT NOT NULL DEFAULT 'USD',
                FOREIGN KEY(user) REFERENCES users(username)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                type TEXT NOT NULL, -- 'income' or 'expense'
                category TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS subcategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                tag TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS transaction_tags (
                transaction_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY(transaction_id) REFERENCES income(id),
                FOREIGN KEY(tag_id) REFERENCES tags(id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                goal_amount REAL NOT NULL,
                target_date TEXT NOT NULL,
                achieved INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(user) REFERENCES users(username)
            )
        ''')

        # Create indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_income_user ON income (user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_expense_user ON expense (user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_budget_user ON budget (user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_recurring_user ON recurring (user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_categories_user ON categories (user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_subcategories_user ON subcategories (user)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tags_user ON tags (user)")
        conn.commit()
        logging.info("Database tables created or verified successfully.")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

create_tables()

# Close the connection when the app stops
@atexit.register
def close_connection():
    try:
        conn.close()
        logging.info("Database connection closed.")
    except Exception as e:
        logging.error(f"Error closing database connection: {e}")

# Database Interaction Functions

def add_income(user, date, category, subcategory, amount, currency='USD'):
    try:
        c.execute("""
            INSERT INTO income (user, date, category, subcategory, amount, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user, date, category, subcategory, amount, currency))
        conn.commit()
        logging.info(f"Income added for user {user}: {amount} {currency} on {date}")
        return True, "Income added successfully."
    except Exception as e:
        logging.error(f"Error adding income for user {user}: {e}")
        return False, f"Error adding income: {e}"

def add_expense(user, date, category, subcategory, amount, currency='USD'):
    try:
        c.execute("""
            INSERT INTO expense (user, date, category, subcategory, amount, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user, date, category, subcategory, amount, currency))
        conn.commit()
        logging.info(f"Expense added for user {user}: {amount} {currency} on {date}")
        return True, "Expense added successfully."
    except Exception as e:
        logging.error(f"Error adding expense for user {user}: {e}")
        return False, f"Error adding expense: {e}"

def set_budget(user, category, subcategory, amount, currency='USD'):
    try:
        c.execute("""
            INSERT INTO budget (user, category, subcategory, amount, currency)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user, category, subcategory) DO UPDATE SET amount=excluded.amount
        """, (user, category, subcategory, amount, currency))
        conn.commit()
        logging.info(f"Budget set for user {user}: {amount} {currency} for {category}/{subcategory}")
        return True, "Budget set successfully."
    except Exception as e:
        logging.error(f"Error setting budget for user {user}: {e}")
        return False, f"Error setting budget: {e}"

def add_recurring(user, trans_type, date, category, subcategory, amount, frequency, currency='USD'):
    try:
        c.execute("""
            INSERT INTO recurring (user, type, date, category, subcategory, amount, frequency, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user, trans_type, date, category, subcategory, amount, frequency, currency))
        conn.commit()
        logging.info(f"Recurring {trans_type} added for user {user}: {amount} {currency} on {date} with frequency {frequency}")
        return True, "Recurring transaction added successfully."
    except Exception as e:
        logging.error(f"Error adding recurring transaction for user {user}: {e}")
        return False, f"Error adding recurring transaction: {e}"

def add_category(user, trans_type, category):
    try:
        c.execute("""
            INSERT INTO categories (user, type, category)
            VALUES (?, ?, ?)
        """, (user, trans_type, category))
        conn.commit()
        logging.info(f"Category '{category}' added for user {user} under '{trans_type}'")
        return True, "Category added successfully."
    except Exception as e:
        logging.error(f"Error adding category for user {user}: {e}")
        return False, f"Error adding category: {e}"

def get_categories(user, trans_type):
    c.execute("""
        SELECT category FROM categories 
        WHERE user = ? AND type = ?
    """, (user, trans_type))
    custom_categories = [row[0] for row in c.fetchall()]
    default_categories = {
        'income': ["Salary", "Bonus", "Investment", "Other"],
        'expense': ["Food", "Rent", "Utilities", "Entertainment", "Transportation", "Healthcare", "Other"]
    }
    return default_categories[trans_type] + custom_categories

def add_subcategory(user, category, subcategory):
    try:
        c.execute("""
            INSERT INTO subcategories (user, category, subcategory)
            VALUES (?, ?, ?)
        """, (user, category, subcategory))
        conn.commit()
        logging.info(f"Subcategory '{subcategory}' added under '{category}' for user {user}")
        return True, "Subcategory added successfully."
    except Exception as e:
        logging.error(f"Error adding subcategory for user {user}: {e}")
        return False, f"Error adding subcategory: {e}"

def get_subcategories(user, category):
    c.execute("""
        SELECT subcategory FROM subcategories 
        WHERE user = ? AND category = ?
    """, (user, category))
    return [row[0] for row in c.fetchall()]

def add_tag(user, tag):
    try:
        c.execute("""
            INSERT INTO tags (user, tag)
            VALUES (?, ?)
        """, (user, tag))
        conn.commit()
        logging.info(f"Tag '{tag}' added for user {user}")
        return True, "Tag added successfully."
    except Exception as e:
        logging.error(f"Error adding tag for user {user}: {e}")
        return False, f"Error adding tag: {e}"

def get_tags(user):
    c.execute("""
        SELECT tag FROM tags 
        WHERE user = ?
    """, (user,))
    return [row[0] for row in c.fetchall()]

def associate_tag(transaction_id, tag_id):
    try:
        c.execute("""
            INSERT INTO transaction_tags (transaction_id, tag_id)
            VALUES (?, ?)
        """, (transaction_id, tag_id))
        conn.commit()
        logging.info(f"Tag ID {tag_id} associated with Transaction ID {transaction_id}")
        return True, "Tag associated successfully."
    except Exception as e:
        logging.error(f"Error associating tag ID {tag_id} with Transaction ID {transaction_id}: {e}")
        return False, f"Error associating tag: {e}"

def add_savings_goal(user, goal_amount, target_date):
    try:
        c.execute("""
            INSERT INTO savings_goals (user, goal_amount, target_date)
            VALUES (?, ?, ?)
        """, (user, goal_amount, target_date))
        conn.commit()
        logging.info(f"Savings goal of {goal_amount} set for user {user} with target date {target_date}")
        return True, "Savings goal set successfully."
    except Exception as e:
        logging.error(f"Error setting savings goal for user {user}: {e}")
        return False, f"Error setting savings goal: {e}"

def get_savings_goals(user):
    c.execute("""
        SELECT id, goal_amount, target_date, achieved 
        FROM savings_goals 
        WHERE user = ?
    """, (user,))
    return c.fetchall()

def get_recent_transactions(user, trans_type, limit=5):
    query = f"""
        SELECT date AS Date, category AS Category, subcategory AS Subcategory, amount AS Amount, currency AS Currency
        FROM {trans_type}
        WHERE user = ?
        ORDER BY id DESC
        LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(user, limit))

def get_all_budgets(user):
    query = """
        SELECT category, subcategory, amount, currency 
        FROM budget 
        WHERE user = ?
    """
    return pd.read_sql_query(query, conn, params=(user,))

def get_spent_per_category(user):
    query = """
        SELECT category, subcategory, SUM(amount) AS Spent 
        FROM expense 
        WHERE user = ? 
        GROUP BY category, subcategory
    """
    return pd.read_sql_query(query, conn, params=(user,))

def get_total_income(user):
    query = """
        SELECT SUM(amount) AS Total_Income 
        FROM income 
        WHERE user = ?
    """
    total = pd.read_sql_query(query, conn, params=(user,))['Total_Income'][0]
    return 0.0 if pd.isna(total) else total

def get_total_expenses(user):
    query = """
        SELECT SUM(amount) AS Total_Expenses 
        FROM expense 
        WHERE user = ?
    """
    total = pd.read_sql_query(query, conn, params=(user,))['Total_Expenses'][0]
    return 0.0 if pd.isna(total) else total

def get_income_over_time(user, start_date=None, end_date=None):
    query = """
        SELECT date, SUM(amount) AS Amount 
        FROM income 
        WHERE user = ?
    """
    params = [user]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " GROUP BY date ORDER BY date"
    return pd.read_sql_query(query, conn, params=tuple(params))

def get_expenses_over_time(user, start_date=None, end_date=None):
    query = """
        SELECT date, SUM(amount) AS Amount 
        FROM expense 
        WHERE user = ?
    """
    params = [user]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " GROUP BY date ORDER BY date"
    return pd.read_sql_query(query, conn, params=tuple(params))

def get_expenses_by_category(user):
    query = """
        SELECT category, subcategory, SUM(amount) AS Amount 
        FROM expense 
        WHERE user = ?
        GROUP BY category, subcategory
    """
    return pd.read_sql_query(query, conn, params=(user,))

def get_transaction_tags(user, trans_type):
    query = f"""
        SELECT e.id, e.date, e.category, e.subcategory, e.amount, e.currency, GROUP_CONCAT(t.tag, ', ') AS Tags
        FROM {trans_type} e
        LEFT JOIN transaction_tags tt ON e.id = tt.transaction_id
        LEFT JOIN tags t ON tt.tag_id = t.id
        WHERE e.user = ?
        GROUP BY e.id
        ORDER BY e.id DESC
    """
    return pd.read_sql_query(query, conn, params=(user,))

def get_monthly_summary(user, start_date=None, end_date=None):
    query = """
        SELECT strftime('%Y-%m', date) AS Month, 
               SUM(amount) AS Total_Income 
        FROM income 
        WHERE user = ?
    """
    params = [user]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " GROUP BY Month ORDER BY Month"
    income = pd.read_sql_query(query, conn, params=tuple(params))
    
    query = """
        SELECT strftime('%Y-%m', date) AS Month, 
               SUM(amount) AS Total_Expenses 
        FROM expense 
        WHERE user = ?
    """
    params = [user]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " GROUP BY Month ORDER BY Month"
    expenses = pd.read_sql_query(query, conn, params=tuple(params))
    
    monthly_df = pd.merge(income, expenses, on='Month', how='outer').fillna(0)
    monthly_df['Balance'] = monthly_df['Total_Income'] - monthly_df['Total_Expenses']
    return monthly_df

def get_yearly_summary(user):
    query = """
        SELECT strftime('%Y', date) AS Year, 
               SUM(amount) AS Total_Income 
        FROM income 
        WHERE user = ?
        GROUP BY Year 
        ORDER BY Year
    """
    income = pd.read_sql_query(query, conn, params=(user,))
    
    query = """
        SELECT strftime('%Y', date) AS Year, 
               SUM(amount) AS Total_Expenses 
        FROM expense 
        WHERE user = ?
        GROUP BY Year 
        ORDER BY Year
    """
    expenses = pd.read_sql_query(query, conn, params=(user,))
    
    yearly_df = pd.merge(income, expenses, on='Year', how='outer').fillna(0)
    yearly_df['Balance'] = yearly_df['Total_Income'] - yearly_df['Total_Expenses']
    return yearly_df

def get_current_savings(user):
    query = """
        SELECT SUM(amount) AS Current_Savings 
        FROM income 
        WHERE user = ?
    """
    total = pd.read_sql_query(query, conn, params=(user,))['Current_Savings'][0]
    return 0.0 if pd.isna(total) else total

# hash_passwords.py

import bcrypt

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt()).decode()

# Example usage:
if __name__ == "__main__":
    users = {
        "johndoe": "password123",
        "janedoe": "securepassword"
    }
    
    for username, password in users.items():
        hashed = hash_password(password)
        print(f"{username}: {hashed}")

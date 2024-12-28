# process_recurring.py

import sqlite3
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    filename='process_recurring.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def process_recurring_transactions():
    try:
        # Connect to the database
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        
        today = datetime.today().strftime("%Y-%m-%d")
        
        # Fetch all recurring transactions due today or earlier
        c.execute("""
            SELECT id, user, type, date, category, subcategory, amount, frequency, currency
            FROM recurring
            WHERE date <= ?
        """, (today,))
        
        recurrings = c.fetchall()
        
        for recurring in recurrings:
            rec_id, user, type_, date, category, subcategory, amount, frequency, currency = recurring
            # Insert into income or expense
            if type_ == 'income':
                c.execute("""
                    INSERT INTO income (user, date, category, subcategory, amount, currency)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user, date, category, subcategory, amount, currency))
                logging.info(f"Recurring income added for user {user}: {amount} {currency} on {date}")
            elif type_ == 'expense':
                c.execute("""
                    INSERT INTO expense (user, date, category, subcategory, amount, currency)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user, date, category, subcategory, amount, currency))
                logging.info(f"Recurring expense added for user {user}: {amount} {currency} on {date}")
            
            # Calculate next date based on frequency
            last_date = datetime.strptime(date, "%Y-%m-%d")
            if frequency == 'daily':
                next_date = last_date + timedelta(days=1)
            elif frequency == 'weekly':
                next_date = last_date + timedelta(weeks=1)
            elif frequency == 'monthly':
                month = last_date.month
                year = last_date.year
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                try:
                    next_date = last_date.replace(year=year, month=month)
                except ValueError:
                    # Handle end-of-month issues
                    next_date = last_date + timedelta(days=31)
                    next_date = next_date.replace(day=1) - timedelta(days=1)
            else:
                # Default to monthly if frequency is unknown
                month = last_date.month
                year = last_date.year
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                try:
                    next_date = last_date.replace(year=year, month=month)
                except ValueError:
                    next_date = last_date + timedelta(days=31)
                    next_date = next_date.replace(day=1) - timedelta(days=1)
            
            c.execute("""
                UPDATE recurring
                SET date = ?
                WHERE id = ?
            """, (next_date.strftime("%Y-%m-%d"), rec_id))
            logging.info(f"Recurring transaction ID {rec_id} updated to next date {next_date.strftime('%Y-%m-%d')}")
        
        conn.commit()
        conn.close()
        logging.info("Recurring transactions processed successfully.")
    except Exception as e:
        logging.error(f"Error processing recurring transactions: {e}")

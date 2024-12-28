# modules/income.py

import streamlit as st
from database import add_income, get_categories, get_subcategories, get_tags, associate_tag, get_recent_transactions_cached
import logging
from datetime import datetime
import pandas as pd
from modules.utils import get_exchange_rates
import database  # Added import for database

def add_income_form(user):
    st.header("➕ Add Income")
    with st.form("income_form"):
        date = st.date_input("Date", datetime.today())
        category = st.selectbox("Category", get_categories(user, 'income'))
        subcategory = st.selectbox("Subcategory", ["None"] + get_subcategories(user, category))
        tags = st.multiselect("Tags", get_tags(user))
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0)
        submitted = st.form_submit_button("Add Income")
        if submitted:
            try:
                final_subcategory = subcategory if subcategory != "None" else None
                success, message = add_income(user, date.strftime("%Y-%m-%d"), category, final_subcategory, amount, currency)
                if success:
                    # Associate tags
                    if tags:
                        c = database.conn.cursor()
                        c.execute("SELECT last_insert_rowid()")
                        transaction_id = c.fetchone()[0]
                        for tag in tags:
                            c.execute("SELECT id FROM tags WHERE user = ? AND tag = ?", (user, tag))
                            tag_id = c.fetchone()[0]
                            associate_tag(transaction_id, tag_id)
                        database.conn.commit()
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error("An unexpected error occurred while adding the income.")
                logging.error(f"Unexpected error in add_income_form for user {user}: {e}")

def manage_incomes(user):
    st.header("📝 Manage Incomes")
    
    try:
        # Fetch all incomes using cached function
        income_df = get_recent_transactions_cached(user, 'income', limit=1000)
        if income_df.empty:
            st.info("No income entries to manage.")
            return
        
        # Pagination settings
        items_per_page = 10
        total_pages = (len(income_df) // items_per_page) + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = income_df.iloc[start_idx:end_idx]
        
        # Display paginated data with edit/delete options
        for index, row in paginated_df.iterrows():
            with st.expander(f"Income ID: {row['id']} - {row['Category']} - ${row['Amount']:.2f} on {row['Date']}"):
                new_category = st.text_input("Category", value=row['Category'], key=f"category_{row['id']}")
                new_subcategory = st.text_input("Subcategory", value=row['Subcategory'] if pd.notna(row['Subcategory']) else "", key=f"subcategory_{row['id']}")
                new_amount = st.number_input("Amount", min_value=0.0, value=row['Amount'], format="%.2f", key=f"amount_{row['id']}")
                new_date = st.date_input("Date", pd.to_datetime(row['Date']), key=f"date_{row['id']}")
                new_currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0, key=f"currency_{row['id']}")
                tags = st.multiselect("Tags", get_tags(user), default=row['Tags'].split(', ') if pd.notna(row['Tags']) else [])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"update_income_{row['id']}"):
                        try:
                            c = database.conn.cursor()
                            c.execute("""
                                UPDATE income 
                                SET date = ?, category = ?, subcategory = ?, amount = ?, currency = ?
                                WHERE id = ?
                            """, (new_date.strftime("%Y-%m-%d"), new_category, new_subcategory if new_subcategory else None, new_amount, new_currency, row['id']))
                            database.conn.commit()
                            
                            # Update tags
                            # First, delete existing associations
                            c.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (row['id'],))
                            # Associate new tags
                            for tag in tags:
                                c.execute("SELECT id FROM tags WHERE user = ? AND tag = ?", (user, tag))
                                tag_id = c.fetchone()[0]
                                associate_tag(row['id'], tag_id)
                            database.conn.commit()
                            
                            st.success("Income updated successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error("An unexpected error occurred while updating the income.")
                            logging.error(f"Error updating income ID {row['id']}: {e}")
                with col2:
                    if st.button("Delete", key=f"delete_income_{row['id']}"):
                        try:
                            c = database.conn.cursor()
                            c.execute("DELETE FROM income WHERE id = ?", (row['id'],))
                            # Also delete associated tags
                            c.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (row['id'],))
                            database.conn.commit()
                            st.success("Income deleted successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error("An unexpected error occurred while deleting the income.")
                            logging.error(f"Error deleting income ID {row['id']}: {e}")
    except Exception as e:
        st.error("An unexpected error occurred while managing incomes.")
        logging.error(f"Error in manage_incomes: {e}")

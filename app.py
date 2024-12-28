# app.py

import streamlit as st
from modules.authentication import load_config, get_authenticator, authenticate_user, register_preauthorized_users
from modules.income import add_income_form, manage_incomes
from modules.expense import add_expense_form, manage_expenses
from modules.reporting import dashboard, generate_report
from modules.utils import (
    toggle_dark_mode, set_currency, get_exchange_rates, convert_currency
)
from modules.scheduler import start_scheduler
import logging

# Setup logging as before...

def main():
    start_scheduler()
    config = load_config()
    authenticator = get_authenticator(config)
    name, authentication_status, username = authenticate_user(authenticator)
    if 'registered_preauth_users' not in st.session_state:
        register_preauthorized_users(authenticator)
        st.session_state['registered_preauth_users'] = True
    if authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.title(f'Welcome *{name}*')
        st.set_page_config(page_title="Personal Finance App", layout="wide", page_icon="💰")
        toggle_dark_mode()
        set_currency(username)
        menu = ["Dashboard", "Add Income", "Add Expense", "Manage Incomes", "Manage Expenses", "Reports", "Export Data", "Backup & Restore", "Expense Prediction"]
        choice = st.sidebar.selectbox("Menu", menu)
    
        if choice == "Dashboard":
            dashboard(username)
        elif choice == "Add Income":
            add_income_form(username)
        elif choice == "Add Expense":
            add_expense_form(username)
        elif choice == "Manage Incomes":
            manage_incomes(username)
        elif choice == "Manage Expenses":
            manage_expenses(username)
        elif choice == "Reports":
            generate_report(username)
        elif choice == "Export Data":
            export_data(username)
        elif choice == "Backup & Restore":
            backup_restore(username)
        elif choice == "Expense Prediction":
            expense_prediction(username)
    
    else:
        if authentication_status == False:
            st.error('Username/password is incorrect')
            logging.warning(f"Failed login attempt for user.")
        elif authentication_status == None:
            st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()

# app.py

import streamlit as st
from modules.authentication import load_config, get_authenticator, authenticate_user
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
    # Start the scheduler
    start_scheduler()
    
    # =========================
    # Authentication Setup
    # =========================
    config = load_config()
    authenticator = get_authenticator(config)
    name, authentication_status, username = authenticate_user(authenticator)
    
    if authentication_status:
        # Logout button
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.title(f'Welcome *{name}*')
        
        # =========================
        # Streamlit App Setup
        # =========================
    
        # Set page configuration
        st.set_page_config(page_title="Personal Finance App", layout="wide", page_icon="💰")
    
        # Theme Toggle
        toggle_dark_mode()
    
        # Currency Settings
        set_currency(username)
    
        # Navigation Menu
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

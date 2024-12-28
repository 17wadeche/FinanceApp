import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from database import (
    add_income, add_expense, set_budget, add_recurring, add_category,
    get_categories, add_subcategory, get_subcategories, add_tag, get_tags,
    associate_tag, add_savings_goal, get_savings_goals, get_recent_transactions,
    get_all_budgets, get_spent_per_category, get_total_income, get_total_expenses,
    get_income_over_time, get_expenses_over_time, get_expenses_by_category,
    get_transaction_tags, get_monthly_summary, get_yearly_summary, get_current_savings
)
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import bcrypt
from io import BytesIO
import os
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter

# =========================
# Authentication Setup
# =========================

# Load configuration from config.yaml
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

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
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    def toggle_dark_mode():
        st.sidebar.header("🌙 Theme")
        theme = st.sidebar.radio("Choose Theme", ["Light", "Dark"])
        if theme == "Dark":
            local_css("dark.css")
        else:
            local_css("light.css")

    toggle_dark_mode()

    # Currency Settings
    def get_exchange_rates(base_currency='USD'):
        # Placeholder for exchange rates API integration
        # For demonstration, using static rates
        return {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.75,
            'JPY': 110.0,
            'CAD': 1.25
            # Add more currencies as needed
        }

    def set_currency(user):
        st.sidebar.header("💱 Currency Settings")
        rates = get_exchange_rates()
        currency = st.sidebar.selectbox("Select your preferred currency", sorted(rates.keys()), index=0)
        st.session_state['currency'] = currency
        st.session_state['rates'] = rates

    set_currency(username)

    # Navigation Menu
    menu = ["Dashboard", "Add Income", "Add Expense", "Add Category", "Add Subcategory",
            "Add Tag", "Set Budget", "Add Recurring Transaction", "Set Savings Goal",
            "Track Budget", "Savings Tracker", "Reports", "Manage Entries", "Export Data",
            "Backup & Restore", "Expense Prediction"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Dashboard":
        dashboard(username)
    elif choice == "Add Income":
        add_income_form(username)
    elif choice == "Add Expense":
        add_expense_form(username)
    elif choice == "Add Category":
        add_category_form(username)
    elif choice == "Add Subcategory":
        add_subcategory_form(username)
    elif choice == "Add Tag":
        add_tag_form(username)
    elif choice == "Set Budget":
        set_budget_form(username)
    elif choice == "Add Recurring Transaction":
        add_recurring_form(username)
    elif choice == "Set Savings Goal":
        set_savings_goal_form(username)
    elif choice == "Track Budget":
        track_budget(username)
    elif choice == "Savings Tracker":
        savings_tracker(username)
    elif choice == "Reports":
        generate_report(username)
    elif choice == "Manage Entries":
        manage_entries_menu(username)
    elif choice == "Export Data":
        export_data(username)
    elif choice == "Backup & Restore":
        backup_restore(username)
    elif choice == "Expense Prediction":
        expense_prediction(username)

else:
    if authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

# =========================
# Function Definitions
# =========================

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
            final_subcategory = subcategory if subcategory != "None" else None
            success, message = add_income(user, date.strftime("%Y-%m-%d"), category, final_subcategory, amount, currency)
            if success:
                # Associate tags
                if tags:
                    # Fetch transaction ID
                    c.execute("SELECT last_insert_rowid()")
                    transaction_id = c.fetchone()[0]
                    for tag in tags:
                        c.execute("SELECT id FROM tags WHERE user = ? AND tag = ?", (user, tag))
                        tag_id = c.fetchone()[0]
                        associate_tag(transaction_id, tag_id)
                st.success(message)
                st.cache_data.clear()
            else:
                st.error(message)

def add_expense_form(user):
    st.header("➖ Add Expense")
    with st.form("expense_form"):
        date = st.date_input("Date", datetime.today())
        category = st.selectbox("Category", get_categories(user, 'expense'))
        subcategory = st.selectbox("Subcategory", ["None"] + get_subcategories(user, category))
        tags = st.multiselect("Tags", get_tags(user))
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0)
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            final_subcategory = subcategory if subcategory != "None" else None
            success, message = add_expense(user, date.strftime("%Y-%m-%d"), category, final_subcategory, amount, currency)
            if success:
                # Associate tags
                if tags:
                    # Fetch transaction ID
                    c.execute("SELECT last_insert_rowid()")
                    transaction_id = c.fetchone()[0]
                    for tag in tags:
                        c.execute("SELECT id FROM tags WHERE user = ? AND tag = ?", (user, tag))
                        tag_id = c.fetchone()[0]
                        associate_tag(transaction_id, tag_id)
                st.success(message)
                st.cache_data.clear()
            else:
                st.error(message)

def add_category_form(user):
    st.header("🗂️ Add Custom Category")
    with st.form("category_form"):
        trans_type = st.selectbox("Type", ["Income", "Expense"])
        category = st.text_input("Category Name")
        submitted = st.form_submit_button("Add Category")
        if submitted:
            if category.strip() == "":
                st.error("Category name cannot be empty.")
            else:
                success, message = add_category(user, trans_type.lower(), category.strip())
                if success:
                    st.success(message)
                    st.cache_data.clear()
                else:
                    st.error(message)

def add_subcategory_form(user):
    st.header("📂 Add Subcategory")
    with st.form("subcategory_form"):
        category = st.selectbox("Parent Category", get_categories(user, 'expense') + get_categories(user, 'income'))
        subcategory = st.text_input("Subcategory Name")
        submitted = st.form_submit_button("Add Subcategory")
        if submitted:
            if subcategory.strip() == "":
                st.error("Subcategory name cannot be empty.")
            else:
                success, message = add_subcategory(user, category, subcategory.strip())
                if success:
                    st.success(message)
                    st.cache_data.clear()
                else:
                    st.error(message)

def add_tag_form(user):
    st.header("🏷️ Add Tag")
    with st.form("tag_form"):
        tag = st.text_input("Tag Name")
        submitted = st.form_submit_button("Add Tag")
        if submitted:
            if tag.strip() == "":
                st.error("Tag name cannot be empty.")
            else:
                success, message = add_tag(user, tag.strip())
                if success:
                    st.success(message)
                    st.cache_data.clear()
                else:
                    st.error(message)

def set_budget_form(user):
    st.header("🎯 Set Budget")
    with st.form("budget_form"):
        category = st.selectbox("Category", get_categories(user, 'expense') + get_categories(user, 'income'))
        subcategory = st.selectbox("Subcategory", ["None"] + get_subcategories(user, category))
        amount = st.number_input("Budget Amount", min_value=0.0, format="%.2f")
        currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0)
        submitted = st.form_submit_button("Set Budget")
        if submitted:
            final_subcategory = subcategory if subcategory != "None" else None
            success, message = set_budget(user, category, final_subcategory, amount, currency)
            if success:
                st.success(message)
                st.cache_data.clear()
            else:
                st.error(message)

def add_recurring_form(user):
    st.header("🔄 Add Recurring Transaction")
    with st.form("recurring_form"):
        trans_type = st.selectbox("Type", ["Income", "Expense"])
        date = st.date_input("Start Date", datetime.today())
        category = st.selectbox("Category", get_categories(user, trans_type.lower()))
        subcategory = st.selectbox("Subcategory", ["None"] + get_subcategories(user, category))
        tags = st.multiselect("Tags", get_tags(user))
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
        currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0)
        submitted = st.form_submit_button("Add Recurring Transaction")
        if submitted:
            final_subcategory = subcategory if subcategory != "None" else None
            success, message = add_recurring(user, trans_type.lower(), date.strftime("%Y-%m-%d"), category, final_subcategory, amount, frequency.lower(), currency)
            if success:
                st.success(message)
                st.cache_data.clear()
            else:
                st.error(message)

def set_savings_goal_form(user):
    st.header("💰 Set Savings Goal")
    with st.form("savings_form"):
        goal_amount = st.number_input("Savings Goal Amount", min_value=0.0, format="%.2f")
        target_date = st.date_input("Target Date", datetime.today() + timedelta(days=180))
        submitted = st.form_submit_button("Set Goal")
        if submitted:
            if goal_amount <= 0:
                st.error("Goal amount must be greater than zero.")
            else:
                success, message = add_savings_goal(user, goal_amount, target_date.strftime("%Y-%m-%d"))
                if success:
                    st.success(message)
                    st.cache_data.clear()
                else:
                    st.error(message)

def dashboard(user):
    st.header("📊 Dashboard")
    
    # Fetch recent incomes
    st.subheader("Recent Incomes")
    try:
        income_df = get_recent_transactions(user, 'income', limit=5)
        st.dataframe(income_df)
    except Exception as e:
        st.error(f"Error fetching income data: {e}")
    
    # Fetch recent expenses
    st.subheader("Recent Expenses")
    try:
        expense_df = get_recent_transactions(user, 'expense', limit=5)
        st.dataframe(expense_df)
    except Exception as e:
        st.error(f"Error fetching expense data: {e}")
    
    # Display Current Savings
    st.subheader("Current Savings")
    try:
        current_savings = get_current_savings(user)
        st.metric("Total Savings", f"${current_savings:,.2f}")
    except Exception as e:
        st.error(f"Error fetching savings data: {e}")

def track_budget(user):
    st.header("📈 Track Budget")
    
    try:
        # Fetch all budgets
        budget_df = get_all_budgets(user)
        
        if budget_df.empty:
            st.info("No budgets set. Please set a budget first.")
            return
        
        # Calculate spent per category
        spent_df = get_spent_per_category(user)
        
        # Merge budget and spent data
        merged_df = pd.merge(budget_df, spent_df, on=['category', 'subcategory'], how='left').fillna(0)
        merged_df.rename(columns={'category': 'Category', 'subcategory': 'Subcategory', 'amount': 'Budgeted', 'Spent': 'Spent'}, inplace=True)
        merged_df['Remaining'] = merged_df['Budgeted'] - merged_df['Spent']
        
        # Determine status
        def determine_status(row):
            if row['Remaining'] < 0:
                return "Over Budget"
            elif row['Remaining'] < 0.1 * row['Budgeted']:
                return "Almost Over"
            else:
                return "Within Budget"
        
        merged_df['Status'] = merged_df.apply(determine_status, axis=1)
        
        # Filters
        status_filter = st.multiselect("Filter by Status", options=["Over Budget", "Almost Over", "Within Budget"], default=["Over Budget", "Almost Over", "Within Budget"])
        category_filter = st.multiselect("Filter by Category", options=merged_df['Category'].unique())
        
        if category_filter:
            merged_df = merged_df[merged_df['Category'].isin(category_filter)]
        
        if status_filter:
            merged_df = merged_df[merged_df['Status'].isin(status_filter)]
        
        st.dataframe(merged_df)
        
        # Plotting with Plotly for Interactivity
        fig = px.bar(merged_df, x='Category', y=['Budgeted', 'Spent', 'Remaining'], 
                     title='Budget vs Spent', barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Notifications
        over_budget = merged_df[merged_df['Status'] == "Over Budget"]
        almost_over = merged_df[merged_df['Status'] == "Almost Over"]
        
        if not almost_over.empty:
            st.warning("You are almost over your budget in the following categories:")
            st.write(almost_over[['Category', 'Subcategory', 'Remaining']])
        
        if not over_budget.empty:
            st.error("You have exceeded your budget in the following categories:")
            st.write(over_budget[['Category', 'Subcategory', 'Remaining']])
        
    except Exception as e:
        st.error(f"Error tracking budget: {e}")

def savings_tracker(user):
    st.header("💰 Savings Tracker")
    
    try:
        # Fetch savings goals
        savings_goals = get_savings_goals(user)
        if not savings_goals:
            st.info("No savings goals set.")
            return
        
        # Calculate current savings
        current_savings = get_current_savings(user)
        
        for goal in savings_goals:
            goal_id, goal_amount, target_date, achieved = goal
            progress = (current_savings / goal_amount) * 100 if goal_amount > 0 else 0
            st.subheader(f"Savings Goal ID: {goal_id}")
            st.write(f"**Goal Amount:** ${goal_amount:,.2f}")
            st.write(f"**Target Date:** {target_date}")
            st.progress(min(progress, 100))
            st.write(f"**Current Savings:** ${current_savings:,.2f} ({progress:.2f}%)")
            
            if progress >= 100 and not achieved:
                st.success("Congratulations! You've achieved your savings goal.")
                # Update the goal as achieved
                c.execute("UPDATE savings_goals SET achieved = 1 WHERE id = ?", (goal_id,))
                conn.commit()
    except Exception as e:
        st.error(f"Error tracking savings: {e}")

def generate_report(user):
    st.header("📄 Financial Report")
    
    try:
        # Fetch exchange rates
        rates = st.session_state.get('rates', get_exchange_rates())
        preferred_currency = st.session_state.get('currency', 'USD')
        
        # Total Income
        total_income = get_total_income(user)
        total_income_converted = convert_currency(total_income, 'USD', preferred_currency, rates)
        
        # Total Expenses
        total_expenses = get_total_expenses(user)
        total_expenses_converted = convert_currency(total_expenses, 'USD', preferred_currency, rates)
        
        # Balance
        balance = total_income_converted - total_expenses_converted
        
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"{preferred_currency} ${total_income_converted:,.2f}")
        col2.metric("Total Expenses", f"{preferred_currency} ${total_expenses_converted:,.2f}")
        col3.metric("Balance", f"{preferred_currency} ${balance:,.2f}")
        
        # Income and Expenses Over Time with Date Range Filter
        st.subheader("Income and Expenses Over Time")
        
        with st.expander("Filter Date Range"):
            start_date = st.date_input("Start Date", datetime.today() - pd.DateOffset(months=6))
            end_date = st.date_input("End Date", datetime.today())
        
        income_over_time = get_income_over_time(user, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        expenses_over_time = get_expenses_over_time(user, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        # Plotting with Plotly
        fig = px.line(title='Income vs Expenses Over Time', width=800, height=400)
        if not income_over_time.empty:
            income_over_time['Amount'] = income_over_time['Amount'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            fig.add_scatter(x=pd.to_datetime(income_over_time['date']), y=income_over_time['Amount'], mode='lines+markers', name='Income')
        if not expenses_over_time.empty:
            expenses_over_time['Amount'] = expenses_over_time['Amount'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            fig.add_scatter(x=pd.to_datetime(expenses_over_time['date']), y=expenses_over_time['Amount'], mode='lines+markers', name='Expenses')
        st.plotly_chart(fig, use_container_width=True)
        
        # Expenses by Category with Drill-Down
        st.subheader("Expenses by Category")
        
        expenses_by_category = get_expenses_by_category(user)
        if not expenses_by_category.empty:
            expenses_by_category['Amount'] = expenses_by_category.apply(lambda row: convert_currency(row['Amount'], 'USD', preferred_currency, rates), axis=1)
            fig = px.pie(expenses_by_category, names='category', values='Amount', title='Expenses by Category', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
            
            # Drill-Down: Show transactions in a category when selected
            selected_category = st.selectbox("Select a category to view transactions", [""] + expenses_by_category['category'].unique().tolist())
            if selected_category:
                transactions = get_transaction_tags(user, 'expense')
                filtered_transactions = transactions[transactions['Category'] == selected_category]
                if not filtered_transactions.empty:
                    # Convert currency
                    filtered_transactions['Amount'] = filtered_transactions.apply(
                        lambda row: convert_currency(row['Amount'], row['Currency'], preferred_currency, rates), axis=1
                    )
                    st.subheader(f"Transactions for {selected_category}")
                    st.dataframe(filtered_transactions[['Date', 'Category', 'Subcategory', 'Amount', 'Tags']])
                else:
                    st.info("No transactions found for this category.")
        else:
            st.info("No expenses to display.")
        
        # Monthly and Yearly Summaries
        st.subheader("Monthly Summary")
        monthly_df = get_monthly_summary(user, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if not monthly_df.empty:
            monthly_df['Total_Income'] = monthly_df['Total_Income'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            monthly_df['Total_Expenses'] = monthly_df['Total_Expenses'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            monthly_df['Balance'] = monthly_df['Balance'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            fig = px.bar(monthly_df, x='Month', y=['Total_Income', 'Total_Expenses', 'Balance'], 
                         barmode='group', title='Monthly Summary')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data to display.")
        
        st.subheader("Yearly Summary")
        yearly_df = get_yearly_summary(user)
        if not yearly_df.empty:
            yearly_df['Total_Income'] = yearly_df['Total_Income'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            yearly_df['Total_Expenses'] = yearly_df['Total_Expenses'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            yearly_df['Balance'] = yearly_df['Balance'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            fig = px.bar(yearly_df, x='Year', y=['Total_Income', 'Total_Expenses', 'Balance'], 
                         barmode='group', title='Yearly Summary')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No yearly data to display.")
        
    except Exception as e:
        st.error(f"Error generating report: {e}")

def manage_entries_menu(user):
    manage_menu = ["Manage Incomes", "Manage Expenses", "Manage Budgets", "Manage Savings Goals"]
    manage_choice = st.selectbox("Manage Entries", manage_menu)
    
    if manage_choice == "Manage Incomes":
        manage_incomes(user)
    elif manage_choice == "Manage Expenses":
        manage_expenses(user)
    elif manage_choice == "Manage Budgets":
        manage_budgets(user)
    elif manage_choice == "Manage Savings Goals":
        manage_savings_goals(user)

def manage_incomes(user):
    st.header("📝 Manage Incomes")
    
    try:
        # Fetch all incomes
        income_df = get_recent_transactions(user, 'income', limit=1000)
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
                            c.execute("""
                                UPDATE income 
                                SET date = ?, category = ?, subcategory = ?, amount = ?, currency = ?
                                WHERE id = ?
                            """, (new_date.strftime("%Y-%m-%d"), new_category, new_subcategory if new_subcategory else None, new_amount, new_currency, row['id']))
                            conn.commit()
                            
                            # Update tags
                            # First, delete existing associations
                            c.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (row['id'],))
                            # Associate new tags
                            for tag in tags:
                                c.execute("SELECT id FROM tags WHERE user = ? AND tag = ?", (user, tag))
                                tag_id = c.fetchone()[0]
                                associate_tag(row['id'], tag_id)
                            
                            st.success("Income updated successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error updating income: {e}")
                with col2:
                    if st.button("Delete", key=f"delete_income_{row['id']}"):
                        try:
                            c.execute("DELETE FROM income WHERE id = ?", (row['id'],))
                            # Also delete associated tags
                            c.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (row['id'],))
                            conn.commit()
                            st.success("Income deleted successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error deleting income: {e}")
    except Exception as e:
        st.error(f"Error managing incomes: {e}")

def manage_expenses(user):
    st.header("📝 Manage Expenses")
    
    try:
        # Fetch all expenses
        expense_df = get_recent_transactions(user, 'expense', limit=1000)
        if expense_df.empty:
            st.info("No expense entries to manage.")
            return
        
        # Pagination settings
        items_per_page = 10
        total_pages = (len(expense_df) // items_per_page) + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = expense_df.iloc[start_idx:end_idx]
        
        # Display paginated data with edit/delete options
        for index, row in paginated_df.iterrows():
            with st.expander(f"Expense ID: {row['id']} - {row['Category']} - ${row['Amount']:.2f} on {row['Date']}"):
                new_category = st.text_input("Category", value=row['Category'], key=f"category_{row['id']}")
                new_subcategory = st.text_input("Subcategory", value=row['Subcategory'] if pd.notna(row['Subcategory']) else "", key=f"subcategory_{row['id']}")
                new_amount = st.number_input("Amount", min_value=0.0, value=row['Amount'], format="%.2f", key=f"amount_{row['id']}")
                new_date = st.date_input("Date", pd.to_datetime(row['Date']), key=f"date_{row['id']}")
                new_currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0, key=f"currency_{row['id']}")
                tags = st.multiselect("Tags", get_tags(user), default=row['Tags'].split(', ') if pd.notna(row['Tags']) else [])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"update_expense_{row['id']}"):
                        try:
                            c.execute("""
                                UPDATE expense 
                                SET date = ?, category = ?, subcategory = ?, amount = ?, currency = ?
                                WHERE id = ?
                            """, (new_date.strftime("%Y-%m-%d"), new_category, new_subcategory if new_subcategory else None, new_amount, new_currency, row['id']))
                            conn.commit()
                            
                            # Update tags
                            # First, delete existing associations
                            c.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (row['id'],))
                            # Associate new tags
                            for tag in tags:
                                c.execute("SELECT id FROM tags WHERE user = ? AND tag = ?", (user, tag))
                                tag_id = c.fetchone()[0]
                                associate_tag(row['id'], tag_id)
                            
                            st.success("Expense updated successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error updating expense: {e}")
                with col2:
                    if st.button("Delete", key=f"delete_expense_{row['id']}"):
                        try:
                            c.execute("DELETE FROM expense WHERE id = ?", (row['id'],))
                            # Also delete associated tags
                            c.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (row['id'],))
                            conn.commit()
                            st.success("Expense deleted successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error deleting expense: {e}")
    except Exception as e:
        st.error(f"Error managing expenses: {e}")

def manage_budgets(user):
    st.header("📝 Manage Budgets")
    
    try:
        budget_df = get_all_budgets(user)
        if budget_df.empty:
            st.info("No budgets set.")
            return
        
        # Pagination settings
        items_per_page = 10
        total_pages = (len(budget_df) // items_per_page) + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = budget_df.iloc[start_idx:end_idx]
        
        # Display paginated data with edit/delete options
        for index, row in paginated_df.iterrows():
            with st.expander(f"Budget ID: {row['id']} - {row['category']} - ${row['amount']:.2f}"):
                new_category = st.text_input("Category", value=row['category'], key=f"category_budget_{row['id']}")
                new_subcategory = st.text_input("Subcategory", value=row['subcategory'] if pd.notna(row['subcategory']) else "", key=f"subcategory_budget_{row['id']}")
                new_amount = st.number_input("Budget Amount", min_value=0.0, value=row['amount'], format="%.2f", key=f"amount_budget_{row['id']}")
                new_currency = st.selectbox("Currency", sorted(get_exchange_rates().keys()), index=0, key=f"currency_budget_{row['id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"update_budget_{row['id']}"):
                        try:
                            c.execute("""
                                UPDATE budget 
                                SET category = ?, subcategory = ?, amount = ?, currency = ?
                                WHERE id = ?
                            """, (new_category, new_subcategory if new_subcategory else None, new_amount, new_currency, row['id']))
                            conn.commit()
                            st.success("Budget updated successfully.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error updating budget: {e}")
                with col2:
                    if st.button("Delete", key=f"delete_budget_{row['id']}"):
                        try:
                            c.execute("DELETE FROM budget WHERE id = ?", (row['id'],))
                            conn.commit()
                            st.success("Budget deleted successfully.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error deleting budget: {e}")
    except Exception as e:
        st.error(f"Error managing budgets: {e}")

def manage_savings_goals(user):
    st.header("📝 Manage Savings Goals")
    
    try:
        savings_goals = get_savings_goals(user)
        if not savings_goals:
            st.info("No savings goals set.")
            return
        
        # Pagination settings
        items_per_page = 10
        total_pages = (len(savings_goals) // items_per_page) + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_goals = savings_goals[start_idx:end_idx]
        
        for goal in paginated_goals:
            goal_id, goal_amount, target_date, achieved = goal
            progress = (get_current_savings(user) / goal_amount) * 100 if goal_amount > 0 else 0
            with st.expander(f"Savings Goal ID: {goal_id}"):
                st.write(f"**Goal Amount:** ${goal_amount:,.2f}")
                st.write(f"**Target Date:** {target_date}")
                st.progress(min(progress, 100))
                st.write(f"**Current Savings:** ${get_current_savings(user):,.2f} ({progress:.2f}%)")
                
                if progress >= 100 and not achieved:
                    st.success("Congratulations! You've achieved your savings goal.")
                    # Update the goal as achieved
                    c.execute("UPDATE savings_goals SET achieved = 1 WHERE id = ?", (goal_id,))
                    conn.commit()
    except Exception as e:
        st.error(f"Error managing savings goals: {e}")

def generate_report(user):
    st.header("📄 Financial Report")
    
    try:
        # Fetch exchange rates
        rates = st.session_state.get('rates', get_exchange_rates())
        preferred_currency = st.session_state.get('currency', 'USD')
        
        # Total Income
        total_income = get_total_income(user)
        total_income_converted = convert_currency(total_income, 'USD', preferred_currency, rates)
        
        # Total Expenses
        total_expenses = get_total_expenses(user)
        total_expenses_converted = convert_currency(total_expenses, 'USD', preferred_currency, rates)
        
        # Balance
        balance = total_income_converted - total_expenses_converted
        
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"{preferred_currency} ${total_income_converted:,.2f}")
        col2.metric("Total Expenses", f"{preferred_currency} ${total_expenses_converted:,.2f}")
        col3.metric("Balance", f"{preferred_currency} ${balance:,.2f}")
        
        # Income and Expenses Over Time with Date Range Filter
        st.subheader("Income and Expenses Over Time")
        
        with st.expander("Filter Date Range"):
            start_date = st.date_input("Start Date", datetime.today() - timedelta(days=180))
            end_date = st.date_input("End Date", datetime.today())
        
        income_over_time = get_income_over_time(user, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        expenses_over_time = get_expenses_over_time(user, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        # Convert amounts
        if not income_over_time.empty:
            income_over_time['Amount'] = income_over_time['Amount'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
        if not expenses_over_time.empty:
            expenses_over_time['Amount'] = expenses_over_time['Amount'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
        
        # Plotting with Plotly
        fig = px.line(title='Income vs Expenses Over Time', width=800, height=400)
        if not income_over_time.empty:
            fig.add_scatter(x=pd.to_datetime(income_over_time['date']), y=income_over_time['Amount'], mode='lines+markers', name='Income')
        if not expenses_over_time.empty:
            fig.add_scatter(x=pd.to_datetime(expenses_over_time['date']), y=expenses_over_time['Amount'], mode='lines+markers', name='Expenses')
        st.plotly_chart(fig, use_container_width=True)
        
        # Expenses by Category with Drill-Down
        st.subheader("Expenses by Category")
        
        expenses_by_category = get_expenses_by_category(user)
        if not expenses_by_category.empty:
            expenses_by_category['Amount'] = expenses_by_category.apply(lambda row: convert_currency(row['Amount'], 'USD', preferred_currency, rates), axis=1)
            fig = px.pie(expenses_by_category, names='category', values='Amount', title='Expenses by Category', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
            
            # Drill-Down: Show transactions in a category when selected
            selected_category = st.selectbox("Select a category to view transactions", [""] + expenses_by_category['category'].unique().tolist())
            if selected_category:
                transactions = get_transaction_tags(user, 'expense')
                filtered_transactions = transactions[transactions['Category'] == selected_category]
                if not filtered_transactions.empty:
                    # Convert currency
                    filtered_transactions['Amount'] = filtered_transactions.apply(
                        lambda row: convert_currency(row['Amount'], row['Currency'], preferred_currency, rates), axis=1
                    )
                    st.subheader(f"Transactions for {selected_category}")
                    st.dataframe(filtered_transactions[['Date', 'Category', 'Subcategory', 'Amount', 'Tags']])
                else:
                    st.info("No transactions found for this category.")
        else:
            st.info("No expenses to display.")
        
        # Monthly and Yearly Summaries
        st.subheader("Monthly Summary")
        monthly_df = get_monthly_summary(user, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if not monthly_df.empty:
            monthly_df['Total_Income'] = monthly_df['Total_Income'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            monthly_df['Total_Expenses'] = monthly_df['Total_Expenses'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            monthly_df['Balance'] = monthly_df['Balance'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            fig = px.bar(monthly_df, x='Month', y=['Total_Income', 'Total_Expenses', 'Balance'], 
                         barmode='group', title='Monthly Summary')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data to display.")
        
        st.subheader("Yearly Summary")
        yearly_df = get_yearly_summary(user)
        if not yearly_df.empty:
            yearly_df['Total_Income'] = yearly_df['Total_Income'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            yearly_df['Total_Expenses'] = yearly_df['Total_Expenses'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            yearly_df['Balance'] = yearly_df['Balance'].apply(lambda x: convert_currency(x, 'USD', preferred_currency, rates))
            fig = px.bar(yearly_df, x='Year', y=['Total_Income', 'Total_Expenses', 'Balance'], 
                         barmode='group', title='Yearly Summary')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No yearly data to display.")
        
    except Exception as e:
        st.error(f"Error generating report: {e}")

def manage_entries_menu(user):
    manage_menu = ["Manage Incomes", "Manage Expenses", "Manage Budgets", "Manage Savings Goals"]
    manage_choice = st.selectbox("Manage Entries", manage_menu)
    
    if manage_choice == "Manage Incomes":
        manage_incomes(user)
    elif manage_choice == "Manage Expenses":
        manage_expenses(user)
    elif manage_choice == "Manage Budgets":
        manage_budgets(user)
    elif manage_choice == "Manage Savings Goals":
        manage_savings_goals(user)

def export_data(user):
    st.header("📤 Export Data")
    
    data_type = st.selectbox("Select Data to Export", ["Income", "Expenses", "Budget", "Tags", "Savings Goals"])
    
    try:
        if data_type == "Income":
            df = get_transaction_tags(user, 'income')
        elif data_type == "Expenses":
            df = get_transaction_tags(user, 'expense')
        elif data_type == "Budget":
            df = get_all_budgets(user)
        elif data_type == "Tags":
            df = pd.DataFrame(get_tags(user), columns=['Tags'])
        elif data_type == "Savings Goals":
            df = pd.read_sql_query("SELECT * FROM savings_goals WHERE user = ?", conn, params=(user,))
        else:
            df = pd.DataFrame()
        
        if not df.empty:
            # Export as CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{data_type.lower()}_data_{datetime.today().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )
            
            # Export as Excel
            try:
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    label="Download Excel",
                    data=excel_buffer,
                    file_name=f"{data_type.lower()}_data_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
            except Exception as e:
                st.warning("Excel export requires openpyxl library. Install it via pip install openpyxl.")
            
            # Export as JSON
            json_data = df.to_json(orient='records')
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{data_type.lower()}_data_{datetime.today().strftime('%Y%m%d')}.json",
                mime='application/json',
            )
            
            # Export as PDF
            try:
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                table_data = [df.columns.tolist()] + df.values.tolist()
                table = Table(table_data)
                doc.build([table])
                pdf = pdf_buffer.getvalue()
                pdf_buffer.close()
                st.download_button(
                    label="Download PDF",
                    data=pdf,
                    file_name=f"{data_type.lower()}_data_{datetime.today().strftime('%Y%m%d')}.pdf",
                    mime='application/pdf',
                )
            except ImportError:
                st.warning("PDF export requires reportlab library. Install it via pip install reportlab.")
        else:
            st.info("No data available to export.")
    except Exception as e:
        st.error(f"Error exporting data: {e}")

def backup_restore(user):
    st.header("📤 Backup & Restore")
    
    # Backup
    st.subheader("💾 Backup Database")
    if st.button("Download Database Backup"):
        try:
            with open('finance_app.db', 'rb') as f:
                db_data = f.read()
            st.download_button(
                label="Download Backup",
                data=db_data,
                file_name=f"finance_app_backup_{datetime.today().strftime('%Y%m%d')}.db",
                mime='application/octet-stream',
            )
        except Exception as e:
            st.error(f"Error creating backup: {e}")
    
    # Restore
    st.subheader("🔄 Restore Database")
    uploaded_file = st.file_uploader("Upload your backup database file", type=["db"])
    if uploaded_file is not None:
        try:
            with open('finance_app.db', 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("Database restored successfully. Please refresh the app.")
            st.stop()
        except Exception as e:
            st.error(f"Error restoring database: {e}")

def expense_prediction(user):
    st.header("🔮 Expense Prediction")
    
    try:
        # Data Preparation
        expense_df = pd.read_sql_query("""
            SELECT date, amount 
            FROM expense 
            WHERE user = ?
            ORDER BY date
        """, conn, params=(user,))
        
        if expense_df.empty or len(expense_df) < 10:
            st.info("Not enough data for prediction.")
            return
        
        # Convert dates to ordinal
        expense_df['date'] = pd.to_datetime(expense_df['date'])
        expense_df['date_ordinal'] = expense_df['date'].apply(lambda date: date.toordinal())
        
        X = expense_df[['date_ordinal']]
        y = expense_df['amount']
        
        # Train-Test Split
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predict for next 30 days
        last_date = expense_df['date'].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 31)]
        future_ordinals = [[date.toordinal()] for date in future_dates]
        predictions = model.predict(future_ordinals)
        
        # Convert predictions to preferred currency
        preferred_currency = st.session_state.get('currency', 'USD')
        rates = st.session_state.get('rates', get_exchange_rates())
        predictions_converted = [convert_currency(x, 'USD', preferred_currency, rates) for x in predictions]
        
        prediction_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Expense': predictions_converted
        })
        
        fig = px.line(prediction_df, x='Date', y='Predicted Expense', title='Predicted Expenses for the Next 30 Days')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in expense prediction: {e}")

def add_recurring_transaction(user, type_, date, category, subcategory, amount, frequency, currency='USD'):
    success, message = add_recurring(user, type_, date, category, subcategory, amount, frequency, currency)
    return success, message

def manage_savings_goals(user):
    st.header("📝 Manage Savings Goals")
    
    try:
        savings_goals = get_savings_goals(user)
        if not savings_goals:
            st.info("No savings goals set.")
            return
        
        # Pagination settings
        items_per_page = 10
        total_pages = (len(savings_goals) // items_per_page) + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_goals = savings_goals[start_idx:end_idx]
        
        for goal in paginated_goals:
            goal_id, goal_amount, target_date, achieved = goal
            current_savings = get_current_savings(user)
            progress = (current_savings / goal_amount) * 100 if goal_amount > 0 else 0
            with st.expander(f"Savings Goal ID: {goal_id}"):
                st.write(f"**Goal Amount:** ${goal_amount:,.2f}")
                st.write(f"**Target Date:** {target_date}")
                st.progress(min(progress, 100))
                st.write(f"**Current Savings:** ${current_savings:,.2f} ({progress:.2f}%)")
                
                if progress >= 100 and not achieved:
                    st.success("Congratulations! You've achieved your savings goal.")
                    # Update the goal as achieved
                    c.execute("UPDATE savings_goals SET achieved = 1 WHERE id = ?", (goal_id,))
                    conn.commit()
    except Exception as e:
        st.error(f"Error managing savings goals: {e}")

def convert_currency(amount, from_currency, to_currency, rates):
    if from_currency == to_currency:
        return amount
    try:
        return amount * rates[to_currency] / rates[from_currency]
    except KeyError:
        return amount  # If currency not found, return the original amount

# =========================
# Run the App
# =========================   credentials:
  usernames:
    johndoe:
      name: John Doe
      password: "$2b$12$KIX0eC...hashedpassword..."
    janedoe:
      name: Jane Doe
      password: "$2b$12$ABC0eC...hashedpassword..."
cookie:
  expiry_days: 30
  key: some_signature_key
  name: some_cookie_name
preauthorized:
  emails:
    - johndoe@example.com
    - janedoe@example.com   /* dark.css */

body {
    background-color: #2E2E2E;
    color: white;
}

.css-1d391kg {
    background-color: #2E2E2E;
    color: white;
}   # database.py

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import atexit

# Connect to SQLite database
conn = sqlite3.connect('finance_app.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
def create_tables():
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

create_tables()

# Close the connection when the app stops
@atexit.register
def close_connection():
    conn.close()

# Database Interaction Functions

def add_income(user, date, category, subcategory, amount, currency='USD'):
    try:
        c.execute("""
            INSERT INTO income (user, date, category, subcategory, amount, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user, date, category, subcategory, amount, currency))
        conn.commit()
        return True, "Income added successfully."
    except Exception as e:
        return False, f"Error adding income: {e}"

def add_expense(user, date, category, subcategory, amount, currency='USD'):
    try:
        c.execute("""
            INSERT INTO expense (user, date, category, subcategory, amount, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user, date, category, subcategory, amount, currency))
        conn.commit()
        return True, "Expense added successfully."
    except Exception as e:
        return False, f"Error adding expense: {e}"

def set_budget(user, category, subcategory, amount, currency='USD'):
    try:
        c.execute("""
            INSERT INTO budget (user, category, subcategory, amount, currency)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user, category, subcategory) DO UPDATE SET amount=excluded.amount
        """, (user, category, subcategory, amount, currency))
        conn.commit()
        return True, "Budget set successfully."
    except Exception as e:
        return False, f"Error setting budget: {e}"

def add_recurring(user, trans_type, date, category, subcategory, amount, frequency, currency='USD'):
    try:
        c.execute("""
            INSERT INTO recurring (user, type, date, category, subcategory, amount, frequency, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user, trans_type, date, category, subcategory, amount, frequency, currency))
        conn.commit()
        return True, "Recurring transaction added successfully."
    except Exception as e:
        return False, f"Error adding recurring transaction: {e}"

def add_category(user, trans_type, category):
    try:
        c.execute("""
            INSERT INTO categories (user, type, category)
            VALUES (?, ?, ?)
        """, (user, trans_type, category))
        conn.commit()
        return True, "Category added successfully."
    except Exception as e:
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
        return True, "Subcategory added successfully."
    except Exception as e:
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
        return True, "Tag added successfully."
    except Exception as e:
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
        return True, "Tag associated successfully."
    except Exception as e:
        return False, f"Error associating tag: {e}"

def add_savings_goal(user, goal_amount, target_date):
    try:
        c.execute("""
            INSERT INTO savings_goals (user, goal_amount, target_date)
            VALUES (?, ?, ?)
        """, (user, goal_amount, target_date))
        conn.commit()
        return True, "Savings goal set successfully."
    except Exception as e:
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
    return 0.0 if pd.isna(total) else total   # hash_passwords.py

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
        print(f"{username}: {hashed}")   /* light.css */

body {
    background-color: #FFFFFF;
    color: black;
}

.css-1d391kg {
    background-color: #FFFFFF;
    color: black;
}   # process_recurring.py

import sqlite3
from datetime import datetime, timedelta
import sys

def process_recurring_transactions():
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
        elif type_ == 'expense':
            c.execute("""
                INSERT INTO expense (user, date, category, subcategory, amount, currency)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user, date, category, subcategory, amount, currency))
        
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
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    process_recurring_transactions()
    sys.exit()
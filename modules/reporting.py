# modules/reporting.py

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from database import (
    get_total_income,
    get_total_expenses,
    get_spent_per_category,
    get_monthly_summary,
    get_yearly_summary,
    get_transaction_tags,
    get_savings_goals
)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler('reporting.log')
file_handler.setLevel(logging.INFO)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
file_handler.setFormatter(formatter)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(file_handler)

def dashboard(user):
    """
    Display the financial dashboard with key metrics and visualizations.
    """
    st.header("📊 Financial Dashboard")
    
    try:
        # Fetch data
        total_income = get_total_income(user)
        total_expenses = get_total_expenses(user)
        balance = total_income - total_expenses
        spent_per_category = get_spent_per_category(user)
        monthly_summary = get_monthly_summary(user)
        yearly_summary = get_yearly_summary(user)
        savings_goals = get_savings_goals(user)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"${total_income:,.2f}")
        col2.metric("Total Expenses", f"${total_expenses:,.2f}")
        col3.metric("Balance", f"${balance:,.2f}")
        
        st.markdown("---")
        
        # Expenses by Category Pie Chart
        st.subheader("💸 Expenses by Category")
        if not spent_per_category.empty:
            fig = px.pie(
                spent_per_category,
                names='category',
                values='Spent',
                title='Expenses Distribution by Category',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available to display.")
        
        st.markdown("---")
        
        # Income and Expenses Over Time Line Chart
        st.subheader("📈 Income and Expenses Over Time")
        if not monthly_summary.empty:
            fig = px.line(
                monthly_summary,
                x='Month',
                y=['Total_Income', 'Total_Expenses', 'Balance'],
                title='Monthly Income vs. Expenses',
                labels={'value': 'Amount ($)', 'Month': 'Month'},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No financial data available to display over time.")
        
        st.markdown("---")
        
        # Savings Goals Progress
        st.subheader("🎯 Savings Goals")
        if not savings_goals:
            st.info("No savings goals set.")
        else:
            for goal in savings_goals:
                goal_id, goal_amount, target_date, achieved = goal
                progress = (achieved / goal_amount) * 100 if goal_amount else 0
                st.write(f"**Goal:** ${goal_amount:,.2f} by {target_date}")
                st.progress(min(progress, 100))
        
    except Exception as e:
        st.error("An error occurred while generating the dashboard.")
        logger.error(f"Error generating dashboard for user {user}: {e}")

def generate_report(user):
    """
    Allow users to download their financial data as CSV or Excel files.
    """
    st.header("📝 Generate Report")
    
    try:
        # Options for report type
        report_type = st.selectbox("Select Report Type", ["Income", "Expenses", "All Transactions"])
        
        # Date Range Filter
        st.subheader("Filter by Date Range")
        start_date = st.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
        end_date = st.date_input("End Date", value=pd.to_datetime("today"))
        
        if start_date > end_date:
            st.error("Start Date must be before End Date.")
            return
        
        # Fetch data based on report type
        if report_type == "Income":
            data = get_transaction_tags(user, 'income')
        elif report_type == "Expenses":
            data = get_transaction_tags(user, 'expense')
        else:
            income = get_transaction_tags(user, 'income')
            expenses = get_transaction_tags(user, 'expense')
            data = pd.concat([income, expenses], ignore_index=True)
        
        # Filter data based on date range
        data['Date'] = pd.to_datetime(data['Date'])
        mask = (data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))
        filtered_data = data.loc[mask]
        
        if filtered_data.empty:
            st.info("No data available for the selected criteria.")
            return
        
        st.dataframe(filtered_data)
        
        # Download Options
        st.subheader("Download Report")
        file_format = st.selectbox("Select File Format", ["CSV", "Excel"])
        
        if file_format == "CSV":
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{report_type}_report_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        else:
            excel = filtered_data.to_excel(index=False)
            st.download_button(
                label="Download Excel",
                data=excel,
                file_name=f"{report_type}_report_{start_date}_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
    except Exception as e:
        st.error("An error occurred while generating the report.")
        logger.error(f"Error generating report for user {user}: {e}")

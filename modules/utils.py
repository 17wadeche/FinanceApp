# modules/utils.py

import streamlit as st
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler('utils.log')
file_handler.setLevel(logging.INFO)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
file_handler.setFormatter(formatter)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(file_handler)

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        logger.info(f"Loaded CSS file: {file_name}")
    except Exception as e:
        logger.error(f"Error loading CSS file {file_name}: {e}")

def toggle_dark_mode():
    st.sidebar.header("🌙 Theme")
    theme = st.sidebar.radio("Choose Theme", ["Light", "Dark"])
    if theme == "Dark":
        local_css("styles/dark.css")
        logger.info("Dark mode enabled.")
    else:
        local_css("styles/light.css")
        logger.info("Light mode enabled.")

def get_exchange_rates(base_currency='USD'):
    # Placeholder for exchange rates API integration
    # For demonstration, using static rates
    rates = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.75,
        'JPY': 110.0,
        'CAD': 1.25
        # Add more currencies as needed
    }
    logger.info(f"Exchange rates fetched with base currency {base_currency}.")
    return rates

def set_currency(user):
    st.sidebar.header("💱 Currency Settings")
    rates = get_exchange_rates()
    currency = st.sidebar.selectbox("Select your preferred currency", sorted(rates.keys()), index=0)
    st.session_state['currency'] = currency
    st.session_state['rates'] = rates
    logger.info(f"User {user} set currency to {currency}.")

def convert_currency(amount, from_currency, to_currency, rates):
    if from_currency == to_currency:
        return amount
    try:
        converted_amount = amount * rates[to_currency] / rates[from_currency]
        logger.info(f"Converted {amount} from {from_currency} to {converted_amount} {to_currency}.")
        return converted_amount
    except KeyError as e:
        logger.error(f"Currency conversion error: {e}")
        return amount  # If currency not found, return the original amount

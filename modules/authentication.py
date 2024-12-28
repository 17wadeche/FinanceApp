# modules/authentication.py

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
import os
import bcrypt

# Load environment variables
load_dotenv()

def load_config():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt()).decode()

def get_authenticator(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        st.secrets["cookie"]["key"],  # Use st.secrets for deployed apps
        config['cookie']['expiry_days']
        # Removed config['preauthorized']
    )
    return authenticator

def authenticate_user(authenticator):
    name, authentication_status, username = authenticator.login('Login', 'main')
    return name, authentication_status, username

def register_preauthorized_users(authenticator):
    preauthorized_emails = st.secrets["preauthorized"]["emails"]  # Fetch from Streamlit secrets
    for email in preauthorized_emails:
        name = email.split('@')[0].capitalize()
        username = email.split('@')[0]
        password = "default_password"  # Replace with secure password handling
        hashed_password = hash_password(password)

        try:
            authenticator.register_user(
                name=name,
                email=email,
                username=username,
                password=hashed_password,
                preauthorized=True
            )
            st.success(f"Pre-authorized user {username} registered successfully.")
        except Exception as e:
            st.error(f"Error registering user {username}: {e}")

# modules/authentication.py

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_config():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def get_authenticator(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        os.getenv('COOKIE_KEY'),  # Fetch from environment variable
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    return authenticator

def authenticate_user(authenticator):
    name, authentication_status, username = authenticator.login('Login', 'main')
    return name, authentication_status, username

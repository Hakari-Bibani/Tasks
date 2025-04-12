import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def setup_auth():
    # Get authentication configuration from secrets
    auth_config = {
        "credentials": {
            "usernames": yaml.load(st.secrets["auth"]["usernames"], Loader=SafeLoader)
        },
        "cookie": {
            "name": st.secrets["cookie"]["name"],
            "key": st.secrets["cookie"]["key"],
            "expiry_days": st.secrets["cookie"]["expiry_days"]
        }
    }
    
    # Create the authenticator
    authenticator = stauth.Authenticate(
        auth_config["credentials"],
        auth_config["cookie"]["name"],
        auth_config["cookie"]["key"],
        auth_config["cookie"]["expiry_days"]
    )
    
    return authenticator

def display_auth(authenticator):
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status == False:
        st.error('Username/password is incorrect')
        return False
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        return False
    
    st.sidebar.write(f'Welcome *{name}*')
    if authenticator.logout('Logout', 'sidebar'):
        st.session_state.clear()
        st.experimental_rerun()
    
    return True

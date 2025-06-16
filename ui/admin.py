import streamlit as st
import os
import sys

# Add project root folder to sys.path so we can import utils module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import update_env_variable  # Function to update variables in .env file

# Dummy admin credentials dictionary (in production use a secure method)
ADMIN_USERS = {
    "admin": "admin123"
}

def admin_login():
    """
    Display admin login form if not authenticated.
    Checks credentials against ADMIN_USERS dictionary.
    """
    if not st.session_state.get("admin_authenticated", False):
        st.title("🔐 Admin Login")

        # Input fields for admin username and password with unique keys to avoid session conflicts
        username_input = st.text_input("Username", key="admin_username_input")
        password_input = st.text_input("Password", type="password", key="admin_password_input")

        # Login button triggers authentication
        if st.button("Login"):
            if ADMIN_USERS.get(username_input) == password_input:
                # Set session state on successful login
                st.session_state["admin_authenticated"] = True
                st.session_state["admin_username"] = username_input
                st.success("Admin login successful!")
                st.rerun()  # Reload app to reflect login status
            else:
                st.error("Invalid admin username or password")

        # Stop execution to show only login form until authenticated
        st.stop()

def admin_panel():
    """
    Display admin settings panel after successful login.
    Allows updating environment variables like the OpenAI API key.
    Provides logout functionality.
    """
    st.title("⚙️ Admin Settings")

    # Check if admin is logged in; if not, prompt login
    if not st.session_state.get("admin_authenticated", False):
        admin_login()

    # Show welcome message with admin username
    st.write("Welcome, Admin:", st.session_state.get("admin_username", "Unknown"))

    st.write("Update your environment settings here.")

    # Get current OpenAI API key from environment variables
    current_key = os.getenv("OPENAI_API_KEY", "")
    # Input box for updating the API key, password masked
    new_key = st.text_input("OpenAI API Key", value=current_key, type="password", key="openai_api_input")

    # Button to update API key in .env file
    if st.button("Update API Key"):
        if new_key.strip() == "":
            st.error("API Key cannot be empty.")
        else:
            try:
                # Update .env file with new API key using utility function
                update_env_variable(".env", "OPENAI_API_KEY", new_key.strip())
                st.success("OPENAI_API_KEY updated successfully! Please restart the app.")
            except Exception as e:
                st.error(f"Failed to update .env file: {e}")

    # Logout button clears admin session and reloads app
    if st.button("Logout"):
        for key in ["admin_authenticated", "admin_username", "admin_username_input", "admin_password_input"]:
            st.session_state.pop(key, None)
        st.rerun()

def main():
    """
    Entry point of the admin script.
    Runs admin login and panel display.
    """
    admin_login()
    admin_panel()

if __name__ == "__main__":
    main()

import streamlit as st

# Dummy user database with usernames, passwords, and roles
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "userpass", "role": "user"},
}

def login():
    """
    Display login form if the user is not authenticated.
    Validate credentials against USERS dictionary.
    On successful login, store authentication info in session_state.
    """
    if not st.session_state.get("authenticated", False):
        st.title("🔐 Login")

        # Input fields for username and password
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # Login button triggers authentication
        if st.button("Login"):
            user = USERS.get(username)  # Fetch user details from USERS dictionary
            if user and user["password"] == password:
                # Save authentication state and user info in session_state
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.success(f"Login successful! Logged in as {user['role']}")
                st.rerun()  # Refresh app to reflect login status
            else:
                st.error("Invalid username or password")

        # Stop further execution until login is successful
        st.stop()

def logout():
    """
    Clear authentication-related data from session_state to log out the user.
    Then rerun the app to update the UI accordingly.
    """
    for key in ["authenticated", "username", "role"]:
        st.session_state.pop(key, None)
    st.rerun()

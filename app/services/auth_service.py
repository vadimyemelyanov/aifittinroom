import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        with st.form("login"):
            st.title("Admin Login (admin/admin)")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit and username == "admin" and password == "admin":  # Replace with secure authentication
                st.session_state.authenticated = True
                st.rerun()
        return False
    return True 
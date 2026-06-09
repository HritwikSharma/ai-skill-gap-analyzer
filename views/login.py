import streamlit as st

# Helper functions (Replace these with your actual database/JSON logic)
def check_if_user_exists(email):
    # e.g., check your database or user file
    # return True if email exists, False otherwise
    return False 

def register_new_user(email):
    # e.g., insert email into your database/file
    pass


# --- STEP 1: THE BACKEND CHECK (Runs when returning from Google) ---
if st.user.is_logged_in:
    user_email = st.user.email
    
    # The check happens here natively in Python
    if check_if_user_exists(user_email):
        # Existing User -> Route straight to dashboard
        st.toast(f"Welcome back, {user_email}!")
        st.switch_page("views/dashboard.py")
    else:
        # New User -> Automatically register them, then route
        register_new_user(user_email)
        st.toast("Account created successfully!")
        st.switch_page("views/dashboard.py")


# --- STEP 2: THE UI (Only shows if they aren't logged in yet) ---
else:
    st.markdown("## AI Skill Gap Analyzer")
    st.write("Sign in or create your account instantly using Google.")
    
    # One unified button that handles both entry points seamlessly
    if st.button("💡 Continue with Google", type="primary", use_container_width=True):
        st.login()

import streamlit as st

# 1. Create native tabs
tab1, tab2 = st.tabs(["🔒 Sign In", "✨ Create Account"])

with tab1:
    st.markdown("### Welcome Back")
    st.write("Sign in to access your skill gap analysis.")
    # We store the intent in a variable or session state
    if st.button("Continue with Google", key="sign_in_btn"):
        st.session_state.auth_intent = "sign_in"
        st.login()

with tab2:
    st.markdown("### Join Us")
    st.write("Create an account to start tracking your skills.")
    if st.button("Sign up with Google", key="sign_up_btn"):
        st.session_state.auth_intent = "sign_up"
        st.login()

# 2. The Check: What happens AFTER they select their Google Account
if st.user.is_logged_in:
    user_email = st.user.email
    
    # Placeholder functions: Replace these with your actual database/file checks
    user_exists = check_if_user_exists_in_db(user_email) 
    
    intent = st.session_state.get("auth_intent", "sign_in")
    
    if intent == "sign_up":
        if user_exists:
            st.error("An account with this email already exists. Please use the Sign In tab.")
            st.logout() # Log them out of the session so they can try again
        else:
            # Create the user profile in your database here
            register_new_user(user_email)
            st.success("Account created successfully!")
            st.switch_page("views/dashboard.py")
            
    elif intent == "sign_in":
        if not user_exists:
            st.error("No account found with this email. Please use the Create Account tab first.")
            st.logout()
        else:
            st.success("Logged in successfully!")
            st.switch_page("views/dashboard.py")

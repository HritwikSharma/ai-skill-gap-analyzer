import streamlit as st

st.set_page_config(page_title="TalentPulse", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: #F3F2EF !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.6, 1])
with col2:

    # Brand header
    st.markdown("""
    <div style="background:#0A66C2;border-radius:12px 12px 0 0;padding:28px;text-align:center;">
        <div style="font-size:1.4rem;font-weight:600;color:#fff;letter-spacing:-0.02em;">TalentPulse</div>
        <div style="font-size:0.8rem;color:rgba(255,255,255,0.7);margin-top:4px;">India Tech Market Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    # Card body
    st.markdown("""
    <div style="background:#fff;border:1px solid #E0DFDC;border-top:none;border-radius:0 0 12px 12px;padding:28px 28px 24px;">
    """, unsafe_allow_html=True)

    # Tabs via radio
    tab = st.radio("", ["Sign in", "Create account"], horizontal=True, label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid #E0DFDC;margin:16px 0;'>", unsafe_allow_html=True)

    if tab == "Sign in":
        st.markdown("<p style='font-size:0.85rem;color:#666;margin-bottom:16px;'>Welcome back. Sign in to access your dashboard.</p>", unsafe_allow_html=True)
        st.button("Continue with Google →", on_click=st.login, use_container_width=True, type="primary")

    else:
        st.markdown("""
        <div style="background:#F3F2EF;border-radius:8px;padding:14px 16px;margin-bottom:16px;">
            <div style="font-size:0.8rem;color:#444;line-height:1.8;">
                ✅ &nbsp;Live job market analytics across India<br>
                ✅ &nbsp;Salary insights & hiring trend data<br>
                ✅ &nbsp;Skill gap analysis powered by AI
            </div>
        </div>
        <p style="font-size:0.82rem;color:#666;margin-bottom:16px;">
            Create your free account with Google — no password needed.
        </p>
        """, unsafe_allow_html=True)
        st.button("Sign up with Google →", on_click=st.login, use_container_width=True, type="primary")
        st.markdown("<p style='font-size:0.78rem;color:#999;text-align:center;margin-top:12px;'>Already have an account? Switch to <strong>Sign in</strong> above.</p>", unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:0.72rem;color:#aaa;text-align:center;margin-top:16px;'>
        🔒 Secure sign-in · Your data is never shared
    </p>
    </div>
    """, unsafe_allow_html=True)

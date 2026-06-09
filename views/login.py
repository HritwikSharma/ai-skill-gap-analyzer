import streamlit as st

st.set_page_config(page_title="TalentPulse", layout="centered")

if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .block-container {
    background: #1a1a1a !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 1rem !important;
    max-width: 460px !important;
    margin: 0 auto !important;
}
/* Tab buttons */
.tab-btn {
    all: unset;
    flex: 1;
    text-align: center;
    padding: 13px;
    font-size: 14px;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    color: #888;
}
.tab-btn.active {
    color: #1A56DB;
    border-bottom: 2px solid #1A56DB;
    font-weight: 500;
}
/* Google button */
.google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    padding: 11px;
    border-radius: 8px;
    border: 1px solid #444;
    background: #2a2a2a;
    color: #fff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Brand header + tab row + panel in ONE markdown block
tab = st.session_state.auth_tab
signin_active = "active" if tab == "signin" else ""
create_active = "active" if tab == "create" else ""

st.markdown(f"""
<div style="border-radius:12px 12px 0 0;overflow:hidden;margin-top:2rem;">
  <div style="background:#1A56DB;padding:28px;text-align:center;">
    <div style="font-size:20px;font-weight:600;color:#fff;letter-spacing:-0.02em;">TalentPulse</div>
    <div style="font-size:13px;color:rgba(255,255,255,0.75);margin-top:5px;">India Tech Market Intelligence</div>
  </div>
  <div style="background:#2a2a2a;border:1px solid #333;border-top:none;border-radius:0 0 12px 12px;">
    <div style="display:flex;border-bottom:1px solid #444;">
      <div class="tab-btn {signin_active}">Sign in</div>
      <div class="tab-btn {create_active}">Create account</div>
    </div>
    <div style="padding:24px;">
""", unsafe_allow_html=True)

# Actual interactive buttons (Streamlit handles clicks)
col1, col2 = st.columns(2)
with col1:
    if st.button("Sign in", use_container_width=True, type="secondary"):
        st.session_state.auth_tab = "signin"
        st.rerun()
with col2:
    if st.button("Create account", use_container_width=True, type="secondary"):
        st.session_state.auth_tab = "create"
        st.rerun()

if tab == "signin":
    st.markdown("<p style='font-size:14px;color:#aaa;margin:8px 0 16px;'>Welcome back. Sign in to access your dashboard.</p>", unsafe_allow_html=True)
    st.button("🔵 Continue with Google →", on_click=st.login, use_container_width=True, type="primary")
else:
    st.markdown("""
    <div style="background:#333;border-radius:8px;padding:14px;margin-bottom:14px;font-size:13px;color:#ccc;line-height:2;">
        ✅ Live job market analytics across India<br>
        ✅ Salary insights & hiring trend data<br>
        ✅ Skill gap analysis powered by AI
    </div>
    <p style="font-size:13px;color:#aaa;margin-bottom:16px;">Create your free account — no password needed.</p>
    """, unsafe_allow_html=True)
    st.button("🔵 Sign up with Google →", on_click=st.login, use_container_width=True, type="primary")

st.markdown("""
      <p style='font-size:11px;color:#666;text-align:center;margin-top:16px;'>
        🔒 Secure sign-in · Your data is never shared
      </p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

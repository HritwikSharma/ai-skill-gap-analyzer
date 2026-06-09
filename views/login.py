import streamlit as st

st.set_page_config(page_title="TalentPulse", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .block-container { 
    background: #F3F2EF !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1rem !important; max-width: 460px !important; margin: 0 auto !important; }

/* Blue button instead of red */
.stButton > button[kind="primary"] {
    background: #0A66C2 !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    height: 44px !important;
}
.stButton > button[kind="primary"]:hover {
    background: #004182 !important;
}

/* Radio tab styling */
[data-testid="stRadio"] > div {
    display: flex !important;
    gap: 0 !important;
    border-bottom: 1px solid #E0DFDC !important;
    margin-bottom: 0 !important;
}
[data-testid="stRadio"] label {
    flex: 1 !important;
    text-align: center !important;
    padding: 12px !important;
    font-size: 0.88rem !important;
    border-bottom: 2px solid transparent !important;
    cursor: pointer !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    color: #0A66C2 !important;
    border-bottom: 2px solid #0A66C2 !important;
    font-weight: 500 !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem !important;
}
/* Hide radio circles */
[data-testid="stRadio"] input[type="radio"] { display: none !important; }
[data-testid="stRadio"] [data-testid="stWidgetLabel"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Brand header
st.markdown("""
<div style="background:#0A66C2;border-radius:12px 12px 0 0;padding:28px;text-align:center;margin-top:2rem;">
    <div style="font-size:1.4rem;font-weight:600;color:#fff;letter-spacing:-0.02em;">TalentPulse</div>
    <div style="font-size:0.8rem;color:rgba(255,255,255,0.7);margin-top:4px;">India Tech Market Intelligence</div>
</div>
<div style="background:#fff;border:1px solid #E0DFDC;border-top:none;border-radius:0 0 12px 12px;padding:24px 28px 28px;">
""", unsafe_allow_html=True)

tab = st.radio("", ["Sign in", "Create account"], horizontal=True, label_visibility="collapsed")

st.markdown("<hr style='border:none;border-top:1px solid #E0DFDC;margin:16px 0;'>", unsafe_allow_html=True)

if tab == "Sign in":
    st.markdown("<p style='font-size:0.85rem;color:#555;margin-bottom:16px;'>Welcome back. Sign in to access your dashboard.</p>", unsafe_allow_html=True)
    st.button("Continue with Google →", on_click=st.login, use_container_width=True, type="primary")
else:
    st.markdown("""
    <div style="background:#F3F2EF;border-radius:8px;padding:14px 16px;margin-bottom:16px;font-size:0.82rem;color:#444;line-height:1.9;">
        ✅ &nbsp;Live job market analytics across India<br>
        ✅ &nbsp;Salary insights &amp; hiring trend data<br>
        ✅ &nbsp;Skill gap analysis powered by AI
    </div>
    <p style="font-size:0.82rem;color:#666;margin-bottom:16px;">Create your free account — no password needed.</p>
    """, unsafe_allow_html=True)
    st.button("Sign up with Google →", on_click=st.login, use_container_width=True, type="primary")
    st.markdown("<p style='font-size:0.78rem;color:#999;text-align:center;margin-top:8px;'>Already have an account? Switch to <b>Sign in</b> above.</p>", unsafe_allow_html=True)

st.markdown("""
<p style='font-size:0.72rem;color:#aaa;text-align:center;margin-top:20px;'>
    🔒 Secure sign-in · Your data is never shared
</p>
</div>
""", unsafe_allow_html=True)

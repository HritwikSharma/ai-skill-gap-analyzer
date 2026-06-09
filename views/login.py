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

.block-container {
    max-width: 440px !important;
    margin: 4rem auto 0 !important;
    padding: 0 !important;
    background: #fff !important;
    border-radius: 12px !important;
    border: 1px solid #E0DFDC !important;
    overflow: hidden !important;
}

/* Blue button */
.stButton > button {
    background: #0A66C2 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    height: 44px !important;
    width: 100% !important;
}
.stButton > button:hover { background: #004182 !important; }

/* Hide radio dots */
[data-testid="stRadio"] input[type="radio"] { display: none !important; }
[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    gap: 0 !important;
    border-bottom: 1px solid #E0DFDC !important;
    padding: 0 !important;
}
[data-testid="stRadio"] label {
    flex: 1 !important;
    text-align: center !important;
    padding: 12px 8px !important;
    font-size: 0.88rem !important;
    color: #666 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    cursor: pointer !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    color: #0A66C2 !important;
    border-bottom: 2px solid #0A66C2 !important;
    font-weight: 600 !important;
}
[data-testid="stWidgetLabel"] { display: none !important; }

/* Padding inside card body */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0 !important;
}
section[data-testid="stMain"] > div > div > div {
    padding: 0 28px 28px !important;
}
</style>
""", unsafe_allow_html=True)

# Brand bar — sits inside block-container naturally
st.markdown("""
<div style="background:#0A66C2;padding:28px;text-align:center;margin:-0px;">
    <div style="font-size:1.4rem;font-weight:600;color:#fff;letter-spacing:-0.02em;">TalentPulse</div>
    <div style="font-size:0.8rem;color:rgba(255,255,255,0.7);margin-top:4px;">India Tech Market Intelligence</div>
</div>
<div style="padding: 0 28px;">
""", unsafe_allow_html=True)

tab = st.radio("", ["Sign in", "Create account"], horizontal=True, label_visibility="collapsed")

st.markdown("<hr style='border:none;border-top:1px solid #E0DFDC;margin:16px 0;'>", unsafe_allow_html=True)

if tab == "Sign in":
    st.markdown("<p style='font-size:0.85rem;color:#555;margin-bottom:16px;'>Welcome back. Sign in to access your dashboard.</p>", unsafe_allow_html=True)
    st.button("Continue with Google →", on_click=st.login)
else:
    st.markdown("""
    <div style="background:#F3F2EF;border-radius:8px;padding:14px 16px;margin-bottom:16px;font-size:0.82rem;color:#444;line-height:1.9;">
        ✅ &nbsp;Live job market analytics across India<br>
        ✅ &nbsp;Salary insights &amp; hiring trend data<br>
        ✅ &nbsp;Skill gap analysis powered by AI
    </div>
    <p style="font-size:0.82rem;color:#666;margin-bottom:16px;">Create your free account — no password needed.</p>
    """, unsafe_allow_html=True)
    st.button("Sign up with Google →", on_click=st.login)
    st.markdown("<p style='font-size:0.78rem;color:#999;text-align:center;margin-top:8px;'>Already have an account? Switch to <b>Sign in</b> above.</p>", unsafe_allow_html=True)

st.markdown("<p style='font-size:0.72rem;color:#aaa;text-align:center;margin-top:20px;padding-bottom:8px;'>🔒 Secure sign-in · Your data is never shared</p>", unsafe_allow_html=True)

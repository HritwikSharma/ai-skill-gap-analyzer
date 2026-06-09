import streamlit as st

st.set_page_config(page_title="Sign In — TalentPulse", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Inter:wght@400;500&display=swap');
body, .stApp { background: #F3F2EF !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.4, 1])
with col2:
    st.markdown("""
    <div style="background:#fff;border:1px solid #E0DFDC;border-radius:12px;
                padding:40px 36px;box-shadow:0 4px 20px rgba(0,0,0,0.08);text-align:center;">
        <div style="font-family:'Sora',sans-serif;font-size:1.5rem;
                    font-weight:700;color:#0A66C2;margin-bottom:4px;">
            TalentPulse
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:0.85rem;
                    color:#666;margin-bottom:28px;">
            India Tech Market Intelligence
        </div>
        <hr style="border:none;border-top:1px solid #E0DFDC;margin-bottom:24px;">
        <p style="font-family:'Inter',sans-serif;font-size:0.9rem;color:#333;margin-bottom:20px;">
            Sign in to access live market analytics,<br>salary insights & hiring trends.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:-1px;'>", unsafe_allow_html=True)
    st.button("Continue with Google", on_click=st.login, use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.caption("🔒 Secure sign-in · Your data is never shared")

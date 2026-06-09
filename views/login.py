import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TalentPulse", layout="centered")

st.markdown("""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .block-container {
    background: #0f0f0f !important;
    padding: 0 !important;
    margin: 0 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Target the full Streamlit button column/row wrapper chain */
.stMainBlockContainer,
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}

/* The immediate button parent */
div[data-testid="stButton"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    margin-top: -8px !important;
}

div[data-testid="stButton"] > button {
    background: #252528 !important;
    border: 1px solid #333 !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    width: 364px !important;
    padding: 12px 16px !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
}
div[data-testid="stButton"] > button:hover {
    background: #2e2e32 !important;
    border-color: #444 !important;
    color: #fff !important;
}

/* Google G icon via ::before */
div[data-testid="stButton"] > button::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'%3E%3Cpath d='M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z' fill='%234285F4'/%3E%3Cpath d='M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z' fill='%2334A853'/%3E%3Cpath d='M3.964 10.707A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z' fill='%23FBBC05'/%3E%3Cpath d='M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.163 6.656 3.58 9 3.58z' fill='%23EA4335'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-size: contain;
}

/* Streamlit's inner button layout wrappers — force them to center too */
div[data-testid="stButton"] > button > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Inter', sans-serif;
    background: #0f0f0f;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-top: 40px;
  }
  .card { width: 420px; border-radius: 16px; overflow: hidden; border: 1px solid #2a2a2a; box-shadow: 0 24px 60px rgba(0,0,0,0.6); }
  .card-header { background: #1A56DB; padding: 32px 28px; text-align: center; }
  .card-header h1 { font-size: 22px; font-weight: 600; color: #fff; letter-spacing: -0.03em; }
  .card-header p { font-size: 13px; color: rgba(255,255,255,0.65); margin-top: 6px; }
  .card-body { background: #1c1c1e; }
  .tabs { display: flex; border-bottom: 1px solid #2e2e2e; }
  .tab { flex: 1; padding: 14px; text-align: center; font-size: 14px; color: #666; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; transition: color 0.15s, border-color 0.15s; user-select: none; }
  .tab.active { color: #4d9fff; border-bottom: 2px solid #4d9fff; font-weight: 500; }
  .panel { display: none; padding: 28px 28px 20px; }
  .panel.active { display: block; }
  .panel p.subtitle { font-size: 14px; color: #888; margin-bottom: 12px; line-height: 1.5; }
  .features { background: #252528; border-radius: 10px; padding: 16px 18px; margin-bottom: 16px; border: 1px solid #2e2e2e; }
  .feature-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #bbb; padding: 5px 0; }
  .feature-item .check { color: #4d9fff; font-size: 15px; flex-shrink: 0; }
  .footer-note { font-size: 11px; color: #444; text-align: center; padding: 4px 28px 16px; display: flex; align-items: center; justify-content: center; gap: 5px; }
</style>
</head>
<body>
<div class="card">
  <div class="card-header">
    <h1>TalentPulse</h1>
    <p>India Tech Market Intelligence</p>
  </div>
  <div class="card-body">
    <div class="tabs">
      <div class="tab active" id="tab-signin" onclick="switchTab('signin')">Sign in</div>
      <div class="tab" id="tab-create" onclick="switchTab('create')">Create account</div>
    </div>
    <div class="panel active" id="panel-signin">
      <p class="subtitle">Welcome back. Sign in to access your dashboard.</p>
    </div>
    <div class="panel" id="panel-create">
      <div class="features">
        <div class="feature-item"><span class="check">✦</span> Live job market analytics across India</div>
        <div class="feature-item"><span class="check">✦</span> Salary insights &amp; hiring trend data</div>
        <div class="feature-item"><span class="check">✦</span> Skill gap analysis powered by AI</div>
      </div>
      <p class="subtitle">Create your free account — no password needed.</p>
    </div>
    <div style="padding: 0 28px 8px;">
      <button style="
        width: 100%; padding: 12px 16px; background: #252528;
        border: 1px solid #333; border-radius: 10px; color: #fff;
        font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500;
        cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px;
      ">
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'%3E%3Cpath d='M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z' fill='%234285F4'/%3E%3Cpath d='M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z' fill='%2334A853'/%3E%3Cpath d='M3.964 10.707A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z' fill='%23FBBC05'/%3E%3Cpath d='M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.163 6.656 3.58 9 3.58z' fill='%23EA4335'/%3E%3C/svg%3E" width="18" height="18">
        Continue with Google
      </button>
    </div>
    <div class="footer-note">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
      Secure sign-in · Your data is never shared
    </div>
  </div>
</div>
<script>
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.getElementById('panel-' + tab).classList.add('active');
}
</script>
</body>
</html>
""", height=480, scrolling=False)


st.markdown("<style>div[data-testid='stButton']{display:none}</style>", unsafe_allow_html=True)
if st.button("google_login"):
    st.login()







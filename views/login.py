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
div[data-testid="stButton"] {
    display: flex;
    justify-content: center;
    margin-top: -8px;
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
}
div[data-testid="stButton"] > button:hover {
    background: #2e2e32 !important;
    border-color: #444 !important;
    color: #fff !important;
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
  .footer-note { font-size: 11px; color: #444; text-align: center; padding: 12px 28px 18px; display: flex; align-items: center; justify-content: center; gap: 5px; }
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
""", height=360, scrolling=False)

# THIS is the real button — only this can call st.login()
if st.button("Continue with Google", use_container_width=False):
    st.login()

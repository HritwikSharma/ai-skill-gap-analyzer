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

/* Hide the real Streamlit button visually but keep it clickable via JS */
div[data-testid="stButton"] {
    position: absolute;
    top: -9999px;
    left: -9999px;
}
</style>
""", unsafe_allow_html=True)

# Hidden real Streamlit button — triggered by JS below
if st.button("login_trigger", key="login_btn"):
    st.login()

# Listen for postMessage from iframe and click the hidden button
components.html("""
<script>
window.addEventListener('message', function(e) {
    if (e.data === 'trigger_google_login') {
        // Find the hidden Streamlit button and click it
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.innerText.trim() === 'login_trigger') {
                btn.click();
            }
        });
    }
});
</script>
""", height=0)

# Your beautiful HTML card with the Google button intact
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
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .card {
    width: 420px;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #2a2a2a;
    box-shadow: 0 24px 60px rgba(0,0,0,0.6);
  }
  .card-header {
    background: #1A56DB;
    padding: 32px 28px;
    text-align: center;
  }
  .card-header h1 {
    font-size: 22px;
    font-weight: 600;
    color: #fff;
    letter-spacing: -0.03em;
  }
  .card-header p {
    font-size: 13px;
    color: rgba(255,255,255,0.65);
    margin-top: 6px;
  }
  .card-body { background: #1c1c1e; padding: 0; }
  .tabs { display: flex; border-bottom: 1px solid #2e2e2e; }
  .tab {
    flex: 1; padding: 14px; text-align: center;
    font-size: 14px; color: #666; cursor: pointer;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
    transition: color 0.15s, border-color 0.15s; user-select: none;
  }
  .tab.active { color: #4d9fff; border-bottom: 2px solid #4d9fff; font-weight: 500; }
  .panel { display: none; padding: 28px; }
  .panel.active { display: block; }
  .panel p.subtitle {
    font-size: 14px; color: #888;
    margin-bottom: 22px; line-height: 1.5;
  }
  .google-btn {
    display: flex; align-items: center; justify-content: center;
    gap: 10px; width: 100%; padding: 12px 16px;
    border-radius: 10px; border: 1px solid #333;
    background: #252528; color: #fff;
    font-size: 14px; font-weight: 500;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.1s;
    font-family: 'Inter', sans-serif;
  }
  .google-btn:hover { background: #2e2e32; border-color: #444; }
  .google-btn:active { transform: scale(0.98); }
  .features {
    background: #252528; border-radius: 10px;
    padding: 16px 18px; margin-bottom: 20px;
    border: 1px solid #2e2e2e;
  }
  .feature-item {
    display: flex; align-items: center; gap: 10px;
    font-size: 13px; color: #bbb; padding: 5px 0;
  }
  .feature-item .check { color: #4d9fff; font-size: 15px; flex-shrink: 0; }
  .footer-note {
    font-size: 11px; color: #444; text-align: center;
    margin-top: 20px; display: flex;
    align-items: center; justify-content: center; gap: 5px;
  }
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
      <button class="google-btn" onclick="triggerLogin()">
        <svg width="18" height="18" viewBox="0 0 48 48">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
        </svg>
        Continue with Google
      </button>
      <div class="footer-note">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        Secure sign-in · Your data is never shared
      </div>
    </div>

    <div class="panel" id="panel-create">
      <div class="features">
        <div class="feature-item"><span class="check">✦</span> Live job market analytics across India</div>
        <div class="feature-item"><span class="check">✦</span> Salary insights &amp; hiring trend data</div>
        <div class="feature-item"><span class="check">✦</span> Skill gap analysis powered by AI</div>
      </div>
      <p class="subtitle">Create your free account — no password needed.</p>
      <button class="google-btn" onclick="triggerLogin()">
        <svg width="18" height="18" viewBox="0 0 48 48">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
        </svg>
        Sign up with Google
      </button>
      <div class="footer-note" style="margin-top:16px;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        Secure sign-in · Your data is never shared
      </div>
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

function triggerLogin() {
  // Send message to the listener iframe above
  window.parent.postMessage('trigger_google_login', '*');
}
</script>
</body>
</html>
""", height=520, scrolling=False)

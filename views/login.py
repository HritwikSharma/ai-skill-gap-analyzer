import streamlit as st
import streamlit.components.v1 as components

def render_login(auth_url: str):
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
    
    .stMainBlockContainer,
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
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
        padding-top: 0px;
      }
      .card { width: 420px; border-radius: 0; overflow: hidden; border: none; box-shadow: none; }
      .card-header { background: #0f0f0f; padding: 32px 28px 16px; text-align: center; }
      .card-header h1 { font-size: 22px; font-weight: 600; color: #fff; letter-spacing: -0.03em; }
      .card-header p { font-size: 13px; color: rgba(255,255,255,0.4); margin-top: 6px; }
      .card-body { background: #0f0f0f; }
      .tabs { display: flex; border-bottom: 1px solid #1e1e1e; }
      .tab { flex: 1; padding: 14px; text-align: center; font-size: 14px; color: #555; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; transition: color 0.15s, border-color 0.15s; user-select: none; }
      .tab.active { color: #4d9fff; border-bottom: 2px solid #4d9fff; font-weight: 500; }
      .panel { display: none; padding: 28px 28px 20px; }
      .panel.active { display: block; }
      .panel p.subtitle { font-size: 14px; color: #666; margin-bottom: 12px; line-height: 1.5; }
      .features { background: #141414; border-radius: 10px; padding: 16px 18px; margin-bottom: 16px; border: 1px solid #1e1e1e; }
      .feature-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #bbb; padding: 5px 0; }
      .feature-item .check { color: #4d9fff; font-size: 15px; flex-shrink: 0; }
      .footer-note { font-size: 11px; color: #333; text-align: center; padding: 4px 28px 16px; display: flex; align-items: center; justify-content: center; gap: 5px; }
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
          <div class="features">
            <div class="feature-item"><span class="check">✦</span> Live job market analytics across India</div>
            <div class="feature-item"><span class="check">✦</span> Salary insights &amp; hiring trend data</div>
            <div class="feature-item"><span class="check">✦</span> Skill gap analysis powered by AI</div>
          </div>
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
    """, height=420, scrolling=False)

    # RENDER THE PUBLIC AUTHENTICATION LINK BUTTON
    left_co, cent_co, last_co = st.columns([2, 1, 2])
    with cent_co:
        st.markdown(
            f'''
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <div style="
                    background: #141414; 
                    border: 1px solid #1e1e1e; 
                    color: #fff; 
                    font-family: 'Inter', sans-serif; 
                    font-size: 14px; 
                    font-weight: 500; 
                    width: 364px; 
                    padding: 12px 16px; 
                    border-radius: 10px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    gap: 10px;
                    margin-left: -110px;
                    cursor: pointer;
                    transition: background 0.15s, border-color 0.15s;
                " onmouseover="this.style.background='#1a1a1a'; this.style.borderColor='#333';" 
                  onmouseout="this.style.background='#141414'; this.style.borderColor='#1e1e1e';">
                    <svg width="18" height="18" viewBox="0 0 18 18" style="flex-shrink: 0;">
                        <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
                        <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
                        <path d="M3.964 10.707A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z" fill="#FBBC05"/>
                        <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
                    </svg>
                    <span>Continue with Google</span>
                </div>
            </a>
            ''',
            unsafe_allow_html=True
        )

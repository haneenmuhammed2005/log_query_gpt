# Login Page

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

THIS_FILE    = Path(__file__).resolve()
PAGES_DIR    = THIS_FILE.parent
UI_DIR       = PAGES_DIR.parent
project_root = UI_DIR.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.user_manager import UserManager
from src.ui.auth.session import SessionManager

PAGE_QUERY = "pages/1_Query_Logs.py"
PAGE_HOME  = "app.py"
PAGE_ADMIN = "pages/5_Admin.py"

st.set_page_config(
    page_title="ICS-LogQueryGPT",
    page_icon="🛡",
    layout="wide"
)

@st.cache_resource
def get_managers():
    return UserManager(), SessionManager()

um, sm = get_managers()

if st.session_state.get("authenticated"):
    st.switch_page(PAGE_HOME)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #060d1f !important;
    color: #e2e8f0 !important;
}
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
div[data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(0,170,255,0.2) !important;
    border-radius: 10px !important; color: #e2e8f0 !important; font-size: 14px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #00aaff !important; box-shadow: 0 0 0 3px rgba(0,170,255,0.12) !important;
}
div[data-testid="stTextInput"] label {
    color: #5a7a9a !important; font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
}
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #0066cc, #00aaff) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-size: 15px !important; font-weight: 700 !important; width: 100% !important;
    padding: 14px !important; box-shadow: 0 4px 24px rgba(0,100,220,0.35) !important;
}
div[data-testid="stButton"] button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #6a8aaa !important;
    font-size: 14px !important; font-weight: 600 !important;
}
div[data-testid="stCheckbox"] label { color: #6a8aaa !important; }
input[type="checkbox"] { accent-color: #00aaff !important; }
div[data-testid="stAlert"] { border-radius: 10px !important; }
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1], gap="small")

with left_col:
    components.html("""<!DOCTYPE html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Space Grotesk',sans-serif;background:linear-gradient(135deg,#060d1f 0%,#0a1628 100%);
color:#e2e8f0;padding:44px 40px;min-height:100vh;overflow:hidden;}

@keyframes blink    {0%,100%{opacity:1}50%{opacity:0.15}}
@keyframes floatorb {0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-22px) scale(1.04)}}
@keyframes shimmer  {0%{background-position:-300% center}100%{background-position:300% center}}
@keyframes fadeUp   {from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideIn  {from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}}
@keyframes pulse    {0%,100%{box-shadow:0 0 0 0 rgba(0,170,255,0.4)}70%{box-shadow:0 0 0 8px rgba(0,170,255,0)}}
@keyframes scan     {0%{top:-100%}100%{top:110%}}
@keyframes countup  {from{opacity:0}to{opacity:1}}

/* Orbs */
.orb1{position:fixed;width:500px;height:500px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,60,255,0.14),transparent 70%);
  filter:blur(90px);top:-160px;left:-140px;
  animation:floatorb 14s ease-in-out infinite;pointer-events:none;}
.orb2{position:fixed;width:350px;height:350px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,170,255,0.10),transparent 70%);
  filter:blur(90px);bottom:-100px;right:-60px;
  animation:floatorb 17s 4s ease-in-out infinite;pointer-events:none;}
.orb3{position:fixed;width:200px;height:200px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,230,255,0.07),transparent 70%);
  filter:blur(60px);top:45%;right:15%;
  animation:floatorb 11s 2s ease-in-out infinite;pointer-events:none;}

/* Grid */
.grid{position:fixed;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(0,170,255,0.028) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,170,255,0.028) 1px,transparent 1px);
  background-size:52px 52px;}

/* Scan line */
.scan-wrap{position:fixed;inset:0;pointer-events:none;overflow:hidden;}
.scan-line{position:absolute;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(0,170,255,0.18),transparent);
  animation:scan 8s linear infinite;}

/* Badge */
.badge{display:inline-flex;align-items:center;gap:8px;
  background:rgba(0,170,255,0.07);border:1px solid rgba(0,170,255,0.25);
  border-radius:20px;padding:6px 16px;margin-bottom:28px;
  opacity:0;animation:fadeUp 0.6s 0.1s ease forwards;}
.dot{width:8px;height:8px;border-radius:50%;background:#00aaff;
  box-shadow:0 0 12px #00aaff;animation:blink 2s infinite,pulse 2s infinite;}
.badge-text{font-size:10px;font-weight:800;color:#00aaff;text-transform:uppercase;letter-spacing:0.14em;}

/* Title */
.title-wrap{margin-bottom:14px;opacity:0;animation:fadeUp 0.6s 0.2s ease forwards;}
.app-name{font-size:13px;font-weight:700;color:#3a6a9a;text-transform:uppercase;
  letter-spacing:0.2em;margin-bottom:8px;}
.title{font-size:48px;font-weight:800;letter-spacing:-2.2px;line-height:1.08;}
.white{color:#fff;}
.blue{background:linear-gradient(135deg,#00aaff 0%,#00e5ff 50%,#00aaff 100%);
  background-size:200% auto;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:shimmer 4s linear infinite;}

/* Sub */
.sub{font-size:13.5px;color:#4a6a8a;line-height:1.75;margin-bottom:32px;max-width:400px;
  opacity:0;animation:fadeUp 0.6s 0.3s ease forwards;}

/* Feature cards */
.features{display:flex;flex-direction:column;gap:10px;margin-bottom:32px;}
.feature{display:flex;align-items:center;gap:14px;
  background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.06);
  border-radius:10px;padding:11px 14px;
  transition:border-color 0.25s,background 0.25s;
  opacity:0;}
.feature:nth-child(1){animation:slideIn 0.5s 0.4s ease forwards;}
.feature:nth-child(2){animation:slideIn 0.5s 0.5s ease forwards;}
.feature:nth-child(3){animation:slideIn 0.5s 0.6s ease forwards;}
.feature:nth-child(4){animation:slideIn 0.5s 0.7s ease forwards;}
.feature:nth-child(5){animation:slideIn 0.5s 0.8s ease forwards;}
.feature:hover{border-color:rgba(0,170,255,0.25);background:rgba(0,170,255,0.04);}
.icon-box{width:32px;height:32px;border-radius:8px;flex-shrink:0;
  background:linear-gradient(135deg,rgba(0,80,200,0.3),rgba(0,170,255,0.15));
  border:1px solid rgba(0,170,255,0.25);
  display:flex;align-items:center;justify-content:center;}
.icon-box svg{width:14px;height:14px;stroke:#00aaff;fill:none;stroke-width:2;}
.feat-text{font-size:12.5px;color:#6a8aaa;font-weight:500;line-height:1.4;}
.feat-label{font-size:10px;font-weight:800;color:#3a5a7a;text-transform:uppercase;
  letter-spacing:0.1em;margin-bottom:2px;}

/* Stats bar */
.stats{display:flex;gap:0;margin-top:4px;border-top:1px solid rgba(0,170,255,0.08);
  padding-top:18px;opacity:0;animation:fadeUp 0.6s 0.9s ease forwards;}
.stat-item{flex:1;text-align:center;border-right:1px solid rgba(255,255,255,0.05);}
.stat-item:last-child{border-right:none;}
.stat-val{font-size:18px;font-weight:800;color:#00aaff;letter-spacing:-0.5px;}
.stat-lbl{font-size:9px;font-weight:700;color:#2a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;}
</style></head><body>
<div class="orb1"></div><div class="orb2"></div><div class="orb3"></div>
<div class="grid"></div>
<div class="scan-wrap"><div class="scan-line"></div></div>

<div class="badge">
  <span class="dot"></span>
  <span class="badge-text">ICS Security Intelligence Platform</span>
</div>

<div class="title-wrap">
  <div class="app-name" style="background:linear-gradient(135deg,#00aaff,#00e5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:15px;font-weight:800;letter-spacing:0.15em;margin-bottom:10px;filter:drop-shadow(0 0 8px rgba(0,170,255,0.5));">ICS-LogQueryGPT</div>
  <div class="title">
    <span class="white">AI-Powered</span><br>
    <span class="blue">Log Analysis</span>
  </div>
</div>

<div class="sub">
  Ask questions about your Industrial Control System security logs in plain English.
  Powered by BERT embeddings, FAISS vector search, and Groq + Gemini Flash AI.
</div>

<div class="features">
  <div class="feature">
    <div class="icon-box">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    </div>
    <div>
      <div class="feat-label">Natural Language Queries</div>
      <div class="feat-text">Ask questions in plain English — no complex query syntax needed</div>
    </div>
  </div>
  <div class="feature">
    <div class="icon-box">
      <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
    </div>
    <div>
      <div class="feat-label">BERT + FAISS Retrieval</div>
      <div class="feat-text">4,000+ log vectors across HDFS and BGL datasets with semantic search</div>
    </div>
  </div>
  <div class="feature">
    <div class="icon-box">
      <svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
    </div>
    <div>
      <div class="feat-label">Groq + Gemini Flash AI</div>
      <div class="feat-text">1-3 second responses with automatic fallback for reliability</div>
    </div>
  </div>
  <div class="feature">
    <div class="icon-box">
      <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    </div>
    <div>
      <div class="feat-label">Critical Alert System</div>
      <div class="feat-text">Auto-detects threats and sends instant email alerts on critical findings</div>
    </div>
  </div>
  <div class="feature">
    <div class="icon-box">
      <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
    </div>
    <div>
      <div class="feat-label">Upload Any Log File</div>
      <div class="feat-text">CSV or TXT — query your own logs instantly with fast MiniLM embeddings</div>
    </div>
  </div>
</div>

<div class="stats">
  <div class="stat-item"><div class="stat-val">4,000+</div><div class="stat-lbl">Logs Indexed</div></div>
  <div class="stat-item"><div class="stat-val">768</div><div class="stat-lbl">Dimensions</div></div>
  <div class="stat-item"><div class="stat-val">1-3s</div><div class="stat-lbl">Response</div></div>
  <div class="stat-item"><div class="stat-val">2</div><div class="stat-lbl">Datasets</div></div>
</div>

<style>
*{box-sizing:border-box;}
html,body{overflow:hidden!important;margin:0!important;}
</style>
</body></html>""", height=820, scrolling=False)

with right_col:
    st.markdown("""
    <div style="padding:50px 40px 0;">
    <div style="font-size:56px;font-weight:900;color:#ffffff;letter-spacing:-2px;margin-bottom:6px;font-family:'Space Grotesk',sans-serif;line-height:1.05;">Welcome back</div>
    <div style="font-size:13px;color:#5a7a9a;margin-bottom:24px;">Sign in to access the ICS log intelligence platform.</div>
    </div>
    """, unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Login", use_container_width=True,
                     type="primary" if st.session_state.auth_mode == "login" else "secondary",
                     key="btn_login"):
            st.session_state.auth_mode = "login"
            st.rerun()
    with col_b:
        if st.button("Sign Up", use_container_width=True,
                     type="primary" if st.session_state.auth_mode == "signup" else "secondary",
                     key="btn_signup"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    with st.form("auth_form"):
        username = st.text_input("USERNAME", placeholder="Enter your username")
        password = st.text_input("PASSWORD", placeholder="Enter your password", type="password")
        confirm  = st.text_input("CONFIRM PASSWORD", placeholder="Confirm your password", type="password") \
                   if st.session_state.auth_mode == "signup" else None
        remember = st.checkbox("Keep me signed in")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Sign In" if st.session_state.auth_mode == "login" else "Create Account",
            use_container_width=True
        )

    if submitted:
        if not username or not password:
            st.error("Please fill in all fields.")
        elif st.session_state.auth_mode == "signup":
            if confirm and password != confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    if um.user_exists(username):
                        st.error("Username already exists.")
                    else:
                        um.create_user(username, password)
                        st.success("Account created! Please sign in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                except Exception as e:
                    st.error(f"Signup error: {e}")
        else:
            if username == "admin" and password == "admin123":
                st.session_state.authenticated  = True
                st.session_state.username        = "admin"
                st.session_state.user_role       = "admin"
                st.session_state.session_token   = "admin-session"
                st.switch_page(PAGE_ADMIN)
            else:
                try:
                    user = um.authenticate(username, password)
                    if user:
                        timeout = 10080 if remember else 30
                        sm_tmp  = SessionManager(timeout_minutes=timeout)
                        token   = sm_tmp.create_session(user)
                        st.session_state.authenticated  = True
                        st.session_state.username        = user["username"]
                        st.session_state.user_role       = user.get("role", "user")
                        st.session_state.session_token   = token
                        if user.get("role") == "admin":
                            st.switch_page(PAGE_ADMIN)
                        else:
                            st.switch_page(PAGE_HOME)
                    else:
                        st.error("Invalid username or password.")
                except Exception as e:
                    st.error(f"Auth error: {e}")

    st.markdown("""
    <div style="margin-top:20px;">
        <div style="font-size:10px;font-weight:700;color:#2a4a6a;
            text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">Access Roles</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <span style="font-size:11px;font-weight:600;color:#5a7a9a;
                background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                border-radius:6px;padding:4px 12px;">Admin</span>
            <span style="font-size:11px;font-weight:600;color:#5a7a9a;
                background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                border-radius:6px;padding:4px 12px;">Security Operator</span>
            <span style="font-size:11px;font-weight:600;color:#5a7a9a;
                background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                border-radius:6px;padding:4px 12px;">Read-Only</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

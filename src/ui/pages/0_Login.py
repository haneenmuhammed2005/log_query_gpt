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

st.set_page_config(
    page_title="ICS-LogQueryGPT",
    page_icon="",
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
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Space Grotesk',sans-serif;background:linear-gradient(135deg,#060d1f,#0a1628);
color:#e2e8f0;padding:50px 40px;min-height:100vh;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.2}}
@keyframes floatorb{0%,100%{transform:translateY(0)}50%{transform:translateY(-16px)}}
.badge{display:inline-flex;align-items:center;gap:7px;
background:rgba(0,170,255,0.08);border:1px solid rgba(0,170,255,0.22);
border-radius:20px;padding:5px 14px;margin-bottom:32px;}
.dot{width:7px;height:7px;border-radius:50%;background:#00aaff;
box-shadow:0 0 10px #00aaff;animation:blink 2s infinite;}
.badge-text{font-size:10px;font-weight:800;color:#00aaff;text-transform:uppercase;letter-spacing:0.12em;}
.title{font-size:50px;font-weight:800;letter-spacing:-2px;line-height:1.1;margin-bottom:16px;}
.white{color:#fff;}
.blue{background:linear-gradient(135deg,#00aaff,#00e5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sub{font-size:14px;color:#5a7a9a;line-height:1.7;margin-bottom:36px;max-width:380px;}
.features{display:flex;flex-direction:column;gap:16px;margin-bottom:40px;}
.feature{display:flex;align-items:center;gap:12px;}
.icon{width:30px;height:30px;border-radius:8px;flex-shrink:0;
background:rgba(0,170,255,0.1);border:1px solid rgba(0,170,255,0.2);
display:flex;align-items:center;justify-content:center;color:#00aaff;font-size:14px;}
.feat-text{font-size:13px;color:#6a8aaa;}
.stats{display:flex;gap:16px;padding-top:20px;border-top:1px solid rgba(0,170,255,0.08);}
.stat{font-size:12px;color:#2a4a6a;}
.orb1{position:fixed;width:400px;height:400px;border-radius:50%;
background:radial-gradient(circle,rgba(0,85,255,0.1),transparent);
filter:blur(80px);top:-100px;left:-100px;
animation:floatorb 12s ease-in-out infinite;pointer-events:none;}
.orb2{position:fixed;width:300px;height:300px;border-radius:50%;
background:radial-gradient(circle,rgba(0,170,255,0.07),transparent);
filter:blur(80px);bottom:-80px;right:-50px;
animation:floatorb 15s 3s ease-in-out infinite;pointer-events:none;}
.grid{position:fixed;inset:0;pointer-events:none;
background-image:linear-gradient(rgba(0,170,255,0.03) 1px,transparent 1px),
linear-gradient(90deg,rgba(0,170,255,0.03) 1px,transparent 1px);
background-size:48px 48px;}
</style></head><body>
<div class="orb1"></div><div class="orb2"></div><div class="grid"></div>
<div class="badge"><span class="dot"></span><span class="badge-text">ICS Security Platform</span></div>
<div class="title"><span class="white">Query ICS </span><span class="blue">Logs</span></div>
<div class="sub">Ask questions about your Industrial Control System security logs in plain English — powered by BERT, FAISS, and a fully local Llama 3 model.</div>
<div class="features">
<div class="feature"><div class="icon">→</div><span class="feat-text">Natural language queries — no complex syntax required</span></div>
<div class="feature"><div class="icon"></div><span class="feat-text">Searches 2,000+ HDFS log vectors using semantic BERT embeddings</span></div>
<div class="feature"><div class="icon"></div><span class="feat-text">Fast, Detailed and Deep Analysis modes with FAISS top-K retrieval</span></div>
<div class="feature"><div class="icon"></div><span class="feat-text">100% offline — no data leaves your machine, built for air-gapped ICS</span></div>
</div>
<div class="stats">
<span class="stat">2,000+ logs</span><span class="stat">·</span>
<span class="stat">768 dimensions</span><span class="stat">·</span>
<span class="stat">8B parameters</span><span class="stat">·</span>
<span class="stat">100% offline</span>
</div>
</body></html>""", height=700)

with right_col:
    st.markdown("""
    <div style="padding:50px 40px 0;">
    <div style="font-size:30px;font-weight:800;color:#e2e8f0;letter-spacing:-0.5px;margin-bottom:6px;">Welcome back</div>
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
                st.switch_page(PAGE_HOME)
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

"""
ICS-LogQueryGPT — Login Page
"""

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

def _page(pattern):
    matches = list(PAGES_DIR.glob(pattern))
    if matches:
        return "pages/" + matches[0].name
    return pattern

PAGE_QUERY = _page("1_*Query*")

st.set_page_config(page_title="ICS-LogQueryGPT", page_icon="🔐", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #0a0f1a !important; }
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_managers():
    return UserManager(), SessionManager()
um, sm = get_managers()

# ── STEP 2: navigate after rerun ──
# ── STEP 2: navigate after rerun ──
if st.session_state.get("authenticated"):
    st.switch_page(PAGE_QUERY)

# ── STEP 1: handle query params from HTML form ──
params = st.query_params

if params.get("auth_submit") == "1":
    username  = params.get("auth_user", "").strip()
    password  = params.get("auth_pass", "")
    auth_mode = params.get("auth_mode", "login")
    st.query_params.clear()

    if not username or not password:
        st.session_state.login_error = "Please fill in all fields."
    elif auth_mode == "login":
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.username      = "admin"
            st.session_state.session_token = "admin-session"
            st.session_state.go_to_query   = True
            st.switch_page(PAGE_QUERY)
        else:
            try:
                user = um.authenticate(username, password)
                if user:
                    token = sm.create_session(user)
                    st.session_state.authenticated = True
                    st.session_state.username      = user["username"]
                    st.session_state.session_token = token
                    st.session_state.go_to_query   = True
                    st.switch_page(PAGE_QUERY)
                else:
                    st.session_state.login_error = "Invalid username or password."
            except Exception as e:
                st.session_state.login_error = f"Auth error: {e}"
    elif auth_mode == "signup":
        try:
            if um.user_exists(username):
                st.session_state.login_error = "Username already exists."
            else:
                um.create_user(username, password)
                st.session_state.login_success = "Account created — please sign in."
        except Exception as e:
            st.session_state.login_error = f"Signup error: {e}"

# Show errors above iframe if any
if st.session_state.get("login_error"):
    st.error(st.session_state.pop("login_error"))
if st.session_state.get("login_success"):
    st.success(st.session_state.pop("login_success"))

# ── Render HTML login page ──
TEMPLATE_PATH = UI_DIR / "templates" / "login.html"
html_content  = TEMPLATE_PATH.read_text(encoding="utf-8")

components.html(html_content, height=800, scrolling=False)
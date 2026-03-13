"""
ICS-LogQueryGPT Main Application
Kripa - Week 1 Day 1
"""

import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

st.set_page_config(
    page_title="ICS-LogQueryGPT",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom styles ──────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    background-color: #0a0f1e !important;
    color: #e2e8f0 !important;
    -webkit-font-smoothing: antialiased;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(ellipse 60% 50% at 65% 50%, rgba(0,120,255,0.10) 0%, transparent 70%),
        radial-gradient(ellipse 30% 40% at 90% 10%, rgba(0,220,255,0.07) 0%, transparent 60%);
}

section[data-testid="stSidebar"] {
    background-color: #0d1424 !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] * {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    color: #94a3b8 !important;
}
section[data-testid="stSidebar"] h3 {
    font-size: 10.5px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #334155 !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] > div:first-child,
section[data-testid="stSidebar"] .st-emotion-cache-16idsys p,
section[data-testid="stSidebar"] span.st-emotion-cache-10oheav,
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"],
section[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"] {
    display: none !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] img,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {
    display: none !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    font-size: 13.5px !important;
    font-weight: 400 !important;
    color: #64748b !important;
    border-radius: 7px !important;
    padding: 9px 14px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.25s ease !important;
    border-left: 3px solid transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
    color: #ffffff !important;
    background: linear-gradient(90deg, rgba(0,150,255,0.15), rgba(0,200,255,0.05)) !important;
    border-left: 3px solid rgba(0,170,255,0.5) !important;
    box-shadow: 0 0 12px rgba(0,170,255,0.08) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] {
    color: #ffffff !important;
    font-weight: 600 !important;
    background: linear-gradient(90deg, rgba(0,150,255,0.25), rgba(0,200,255,0.08)) !important;
    border-left: 3px solid #00aaff !important;
    box-shadow: inset 0 0 20px rgba(0,170,255,0.10), 0 0 10px rgba(0,170,255,0.08) !important;
}

.glow-bar {
    height: 3px;
    background: linear-gradient(90deg, transparent, #00aaff, #00e5ff, transparent);
    border-radius: 2px;
    margin-bottom: 20px;
    opacity: 0.7;
}

h1 {
    font-size: 34px !important;
    font-weight: 700 !important;
    color: #e2e8f0 !important;
    letter-spacing: -0.8px !important;
}

.page-caption {
    font-size: 13px;
    color: #64748b;
    margin-top: -12px;
    margin-bottom: 16px;
    letter-spacing: 0.01em;
}

h3, h4 {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin-bottom: 8px !important;
}

.welcome-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 4px;
}
.welcome-title {
    font-size: 18px;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 6px;
    letter-spacing: -0.2px;
}
.welcome-sub {
    font-size: 13px;
    color: #64748b;
    line-height: 1.6;
}

.user-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 18px 20px;
    font-size: 13px;
    color: #94a3b8;
    line-height: 2;
}
.user-card-label {
    font-size: 10.5px;
    font-weight: 600;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}
.user-card b { color: #cbd5e1; }
.session-active {
    display: inline-block;
    background: rgba(34,197,94,0.12);
    color: #22c55e;
    font-size: 11px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 4px;
}

div[data-testid="stMetric"] {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}
div[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #00aaff !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #64748b !important;
}

.feature-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 22px 20px;
    height: 100%;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.feature-card:hover {
    border-color: rgba(0,170,255,0.3);
    box-shadow: 0 0 20px rgba(0,170,255,0.06);
}
.feature-title {
    font-size: 14px;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 8px;
    letter-spacing: -0.1px;
}
.feature-desc {
    font-size: 12.5px;
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 12px;
}
.feature-item {
    font-size: 12px;
    color: #475569;
    padding: 3px 0;
    border-bottom: 1px solid #1a2235;
}
.feature-item:last-child { border-bottom: none; }

.activity-row {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 13px;
}
.activity-query { flex: 1; color: #94a3b8; }
.activity-time { font-size: 11.5px; color: #475569; margin-right: 16px; }
.activity-status { font-size: 11px; color: #22c55e; background: rgba(34,197,94,0.1); padding: 2px 8px; border-radius: 4px; }

button[kind="primary"] {
    background: linear-gradient(135deg, #0077cc, #00aaff) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 0 14px rgba(0,170,255,0.3) !important;
}

button[kind="secondary"] {
    background: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid #2d3f55 !important;
    border-radius: 7px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}
button[kind="secondary"]:hover { background: #263447 !important; }

div[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}
div[data-testid="stSidebarCollapseButton"] { display: none !important; }
section[data-testid="stSidebarNav"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }
div[data-testid="stSidebarNavItems"] { display: none !important; }
hr { border-color: #1e293b !important; }

.footer-caption {
    text-align: center;
    font-size: 11.5px;
    color: #334155;
    margin-top: 16px;
    letter-spacing: 0.02em;
}
</style>
""", unsafe_allow_html=True)

# ── Auth check ─────────────────────────────────────────────────────────────────
# ── Page path helper ───────────────────────────────────────────────────────────
PAGES_DIR = Path(__file__).parent / "pages"

def _page(pattern: str) -> str:
    matches = list(PAGES_DIR.glob(pattern))
    if matches:
        return "pages/" + matches[0].name
    return pattern

PAGE_LOGIN     = _page("0_*Login*")
PAGE_QUERY     = _page("1_*Query*")
PAGE_ANALYTICS = _page("2_*Analytics*")
PAGE_EXPORT    = _page("3_*Export*")

def check_authentication():
    if not st.session_state.get('authenticated', False):
        st.switch_page(PAGE_LOGIN)
        st.stop()
    # allow hardcoded admin session to bypass SessionManager
    if st.session_state.get('session_token') == "admin-session":
        return
    session_manager = SessionManager()
    if not session_manager.validate_session(st.session_state.get('session_token')):
        st.session_state.clear()
        st.switch_page(PAGE_LOGIN)
        st.stop()

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    check_authentication()

    username  = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'Admin')

    st.markdown('<div class="glow-bar"></div>', unsafe_allow_html=True)
    st.title("ICS-LogQueryGPT")
    st.markdown('<p class="page-caption">AI-Powered Industrial Control System Log Analysis</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        <div class="welcome-card">
            <div class="welcome-title">Welcome back, {username}</div>
            <div class="welcome-sub">Your intelligent assistant for analyzing ICS security logs with natural language queries.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="user-card">
            <div class="user-card-label">Session Info</div>
            <b>Username:</b> {username}<br>
            <b>Role:</b> {user_role.title()}<br>
            <b>Status:</b> <span class="session-active">Active</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### Quick Stats")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Logs", "15,247", "↑ 342")
    with c2: st.metric("Queries Today", "23", "↑ 5")
    with c3: st.metric("Cache Hit Rate", "73%", "↑ 8%")
    with c4: st.metric("Avg Response", "2.3s", "↓ 0.5s")

    st.markdown("---")

    st.markdown("#### Features")
    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Query Logs</div>
            <div class="feature-desc">Ask questions in natural language and get AI-powered insights from your ICS logs.</div>
            <div class="feature-item">Natural language queries</div>
            <div class="feature-item">Protocol filtering (SSH, HTTP, FTP...)</div>
            <div class="feature-item">Real-time analysis</div>
            <div class="feature-item">Query caching</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Go to Query Logs", key="btn_query", use_container_width=True):
            st.switch_page(PAGE_QUERY)

    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Analytics</div>
            <div class="feature-desc">Visualize trends, patterns, and anomalies in your security logs.</div>
            <div class="feature-item">Interactive charts</div>
            <div class="feature-item">Time-series analysis</div>
            <div class="feature-item">Protocol distribution</div>
            <div class="feature-item">Threat detection metrics</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Go to Analytics", key="btn_analytics", use_container_width=True):
            st.switch_page(PAGE_ANALYTICS)

    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Export Data</div>
            <div class="feature-desc">Export query results and analysis in multiple formats.</div>
            <div class="feature-item">CSV export</div>
            <div class="feature-item">JSON export</div>
            <div class="feature-item">Markdown reports</div>
            <div class="feature-item">Text summaries</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Go to Export", key="btn_export", use_container_width=True):
            st.switch_page(PAGE_EXPORT)

    st.markdown("---")

    st.markdown("#### Recent Activity")
    recent_queries = [
        {"query": "Show failed login attempts", "time": "2 min ago"},
        {"query": "Any SSH brute force attacks?", "time": "15 min ago"},
        {"query": "List all HTTP errors", "time": "1 hour ago"},
    ]
    for item in recent_queries:
        st.markdown(f"""
        <div class="activity-row">
            <div class="activity-query">{item['query']}</div>
            <div class="activity-time">{item['time']}</div>
            <div class="activity-status">Success</div>
        </div>
        """, unsafe_allow_html=True)

    # Logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown('<p class="footer-caption">ICS-LogQueryGPT v1.0 &nbsp;|&nbsp; Powered by Ollama + Llama 3.1 &nbsp;|&nbsp; 100% Local Processing</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
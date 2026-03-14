# Admin Dashboard Page
import os
os.environ["HF_HOME"]                    = "D:/Projects/log_query_gpt/.cache/huggingface"
os.environ["TRANSFORMERS_CACHE"]         = "D:/Projects/log_query_gpt/.cache/huggingface"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "D:/Projects/log_query_gpt/.cache/sentence_transformers"

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.user_manager import UserManager
from src.ui.auth.session import SessionManager

PAGE_HOME    = "app.py"
PAGE_QUERY   = "pages/1_Query_Logs.py"
PAGE_ANALYTICS = "pages/2_Analytics.py"
PAGE_EXPORT  = "pages/3_Export.py"
PAGE_LOGIN   = "pages/0_Login.py"

st.set_page_config(
    page_title="Admin Dashboard - ICS-LogQueryGPT",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject(html: str):
    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)

def inject_styles():
    inject("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #060d1f !important;
    color: #e2e8f0 !important;
    -webkit-font-smoothing: antialiased;
}
/* Hide ALL default Streamlit nav */
section[data-testid="stSidebarNav"],
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavItems"],
div[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
span[data-testid="stIconMaterial"],
[data-testid="stSidebarHeader"],
header[data-testid="stHeader"], footer, #MainMenu,
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] { display: none !important; }

@keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes floatorb { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-16px)} }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
@keyframes shimmer { 0%{background-position:-300% center} 100%{background-position:300% center} }

.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(0,170,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,170,255,0.022) 1px, transparent 1px);
    background-size: 52px 52px;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(3,8,22,0.99) 0%, rgba(2,6,18,0.99) 100%) !important;
    border-right: 1px solid rgba(0,170,255,0.10) !important;
}
section[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }
section[data-testid="stSidebar"] {
    transform: none !important; width: 21rem !important;
    min-width: 21rem !important; display: block !important;
}
div.block-container {
    padding-top: 0 !important; padding-left: 2.5rem !important;
    padding-right: 2.5rem !important; padding-bottom: 2rem !important;
    max-width: 100% !important;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid rgba(255,255,255,0.065) !important;
    border-radius: 11px !important; padding: 16px 18px !important;
}
div[data-testid="stMetricValue"] {
    font-size: 24px !important; font-weight: 700 !important;
    color: #00aaff !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 9px !important; color: #3a5a7a !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
    font-weight: 700 !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0040aa 0%, #0077cc 45%, #00aaff 100%) !important;
    border: none !important; border-radius: 9px !important;
    color: #fff !important; font-size: 13px !important; font-weight: 700 !important;
    height: 44px !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important; color: #5a7a9a !important;
}
div[data-testid="stTextInput"] > div {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
div[data-testid="stTextInput"] input {
    background: transparent !important; color: #c8d8e8 !important;
    font-size: 13px !important;
}
div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #8ab0d0 !important;
}
div[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.065) !important;
}
div[data-testid="stAlert"] { border-radius: 9px !important; }
hr { border-color: rgba(255,255,255,0.05) !important; }
section[data-testid="stSidebar"] h3 {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a7a !important; text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
}
</style>
""")

# ── Auth check — admin only ────────────────────────────────────────────────────
def check_admin():
    if not st.session_state.get('authenticated', False):
        st.switch_page(PAGE_LOGIN)
        st.stop()
    role = st.session_state.get('user_role', '')
    if role != 'admin':
        try:
            st.html("""
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap" rel="stylesheet">
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:60vh;font-family:'Space Grotesk',sans-serif;text-align:center;padding:40px;">
                <div style="width:72px;height:72px;border-radius:50%;
                    background:rgba(248,113,113,0.12);border:2px solid rgba(248,113,113,0.35);
                    display:flex;align-items:center;justify-content:center;margin-bottom:24px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                        stroke="#f87171" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="15" y1="9" x2="9" y2="15"/>
                        <line x1="9" y1="9" x2="15" y2="15"/>
                    </svg>
                </div>
                <div style="font-size:28px;font-weight:800;color:#f87171;
                    letter-spacing:-0.5px;margin-bottom:10px;">Access Denied</div>
                <div style="font-size:14px;color:#4a6a8a;max-width:360px;line-height:1.7;margin-bottom:28px;">
                    This page is restricted to administrators only.<br>
                    Please contact your admin if you need access.
                </div>
            </div>
            """)
        except:
            st.error("Access denied. Admin only.")
        st.stop()

@st.cache_resource
def get_managers():
    return UserManager(), SessionManager()

def get_session_history():
    """Pull all sessions from DB for activity log"""
    try:
        import sqlite3
        conn = sqlite3.connect("data/sessions.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, user_role, created_at, last_activity, expires_at, active
            FROM sessions
            ORDER BY created_at DESC
            LIMIT 100
        """)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=[
            "Username", "Role", "Login Time", "Last Activity", "Expires At", "Active"
        ])
    except Exception as e:
        return pd.DataFrame()

def main():
    check_admin()
    inject_styles()

    um, sm = get_managers()

    # Ambient orbs
    inject("""
    <div style="pointer-events:none;position:fixed;inset:0;z-index:0;overflow:hidden;">
        <div style="position:absolute;width:500px;height:500px;border-radius:50%;
            background:radial-gradient(circle,#0055ff,#001577);opacity:0.10;
            filter:blur(110px);top:-150px;left:-100px;
            animation:floatorb 13s ease-in-out infinite;"></div>
        <div style="position:absolute;width:300px;height:300px;border-radius:50%;
            background:radial-gradient(circle,#00aaff,#004499);opacity:0.08;
            filter:blur(110px);bottom:-80px;right:4%;
            animation:floatorb 15s 5s ease-in-out infinite;"></div>
    </div>
    """)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        inject("""
        <div style="height:2px;background:linear-gradient(90deg,transparent,#00aaff 50%,transparent);opacity:0.55;"></div>
        <div style="padding:20px 20px 16px;border-bottom:1px solid rgba(255,255,255,0.04);margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:9px;margin-bottom:4px;">
                <div style="width:28px;height:28px;border-radius:7px;
                    background:linear-gradient(135deg,#0044bb,#00aaff);
                    display:flex;align-items:center;justify-content:center;
                    box-shadow:0 0 16px rgba(0,170,255,0.35);flex-shrink:0;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <span style="font-size:13.5px;font-weight:700;letter-spacing:-0.4px;
                    background:linear-gradient(135deg,#fff 30%,#00aaff 100%);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-family:'Space Grotesk',sans-serif;">ICS-LogQueryGPT</span>
            </div>
            <div style="font-size:9.5px;color:#3a6090;letter-spacing:0.1em;text-transform:uppercase;
                padding-left:37px;font-family:'Space Grotesk',sans-serif;">Admin Panel</div>
        </div>
        """)

        st.markdown("### Navigation")
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.switch_page(PAGE_HOME)
        if st.button("Query Logs", use_container_width=True, key="nav_query"):
            st.switch_page(PAGE_QUERY)
        if st.button("Analytics", use_container_width=True, key="nav_analytics"):
            st.switch_page(PAGE_ANALYTICS)
        if st.button("Export", use_container_width=True, key="nav_export"):
            st.switch_page(PAGE_EXPORT)
        if st.button("Benchmark", use_container_width=True, key="nav_benchmark"):
            st.switch_page("pages/6_Benchmark.py")

        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:10px 0;"></div>')

        if st.button("Logout", use_container_width=True, key="nav_logout"):
            st.session_state.clear()
            st.switch_page(PAGE_LOGIN)

        inject(f"""
        <div style="font-size:10px;color:#5a8ab0;margin:10px 4px 4px;
            font-family:'Space Grotesk',sans-serif;">
            Logged in as:
            <span style="color:#00aaff;font-weight:700;">
                {st.session_state.get('username','admin')}
            </span>
            <span style="margin-left:6px;font-size:9px;background:rgba(0,170,255,0.15);
                border:1px solid rgba(0,170,255,0.3);border-radius:4px;
                padding:1px 6px;color:#00aaff;font-weight:700;">ADMIN</span>
        </div>
        """)

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    inject("""
    <div style="height:2px;background:linear-gradient(90deg,transparent,#0088cc 20%,#00aaff 45%,#00e5ff 55%,#00aaff 80%,transparent);
        opacity:0.9;margin-bottom:28px;border-radius:2px;"></div>
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(0,170,255,0.06);border:1px solid rgba(0,170,255,0.2);
        border-radius:20px;padding:5px 14px 5px 10px;
        font-size:10px;font-weight:700;color:#00aaff;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:13px;font-family:'Space Grotesk',sans-serif;">
        <span style="width:7px;height:7px;border-radius:50%;background:#00aaff;
            box-shadow:0 0 14px #00aaff;display:inline-block;
            animation:blink 2.3s ease-in-out infinite;"></span>
        Admin Panel
    </div>
    <div style="margin-bottom:8px;">
        <span style="font-size:40px;font-weight:800;letter-spacing:-2.2px;
            background:linear-gradient(135deg,#ffffff 20%,#8fa8c8 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            font-family:'Space Grotesk',sans-serif;">Admin&nbsp;</span><span
            style="font-size:40px;font-weight:800;letter-spacing:-2.2px;
            background:linear-gradient(135deg,#00aaff 0%,#00e5ff 50%,#00aaff 100%);
            background-size:200% auto;
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            animation:shimmer 4s linear infinite;
            font-family:'Space Grotesk',sans-serif;">Dashboard</span>
    </div>
    <div style="font-size:13px;color:#4a6a8a;margin-bottom:24px;font-family:'Space Grotesk',sans-serif;">
        Manage users, monitor activity and control access
    </div>
    """)

    st.markdown("---")

    # ── QUICK STATS ───────────────────────────────────────────────────────────
    users = um.list_users()
    sessions_df = get_session_history()
    active_sessions = sm.get_active_sessions()
    total_users = len(users)
    active_users = sum(1 for u in users if u['active'])
    admin_count = sum(1 for u in users if u['role'] == 'admin')

    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:11px;font-family:'Space Grotesk',sans-serif;">
        Overview</div>""")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Users", total_users)
    with c2: st.metric("Active Users", active_users)
    with c3: st.metric("Active Sessions", active_sessions)
    with c4: st.metric("Admins", admin_count)

    st.markdown("---")

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["User Management", "Activity Log", "Create User"])

    # ── TAB 1: USER MANAGEMENT ────────────────────────────────────────────────
    with tab1:
        inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
            letter-spacing:0.15em;margin:16px 0 12px;font-family:'Space Grotesk',sans-serif;">
            All Registered Users</div>""")

        if not users:
            st.info("No users found.")
        else:
            for user in users:
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 2, 1.5, 1.5])

                status_color = "#00aaff" if user['active'] else "#f87171"
                status_text  = "Active" if user['active'] else "Disabled"
                role_color   = "#fbbf24" if user['role'] == 'admin' else "#8ab0d0"

                with col1:
                    inject(f"""
                    <div style="padding:12px 0;font-family:'Space Grotesk',sans-serif;">
                        <div style="font-size:13px;font-weight:700;color:#c8d8e8;">{user['username']}</div>
                        <div style="font-size:10px;color:#3a5a7a;">ID: {user['id']}</div>
                    </div>""")
                with col2:
                    inject(f"""
                    <div style="padding:14px 0;">
                        <span style="font-size:11px;font-weight:700;color:{role_color};
                            background:rgba(255,255,255,0.05);border-radius:5px;
                            padding:3px 10px;font-family:'Space Grotesk',sans-serif;">
                            {user['role'].upper()}
                        </span>
                    </div>""")
                with col3:
                    last_login = user.get('last_login') or "Never"
                    inject(f"""
                    <div style="padding:12px 0;font-family:'Space Grotesk',sans-serif;">
                        <div style="font-size:10px;color:#3a5a7a;text-transform:uppercase;
                            letter-spacing:0.1em;margin-bottom:2px;">Last Login</div>
                        <div style="font-size:12px;color:#8ab0d0;">{last_login}</div>
                    </div>""")
                with col4:
                    inject(f"""
                    <div style="padding:14px 0;">
                        <span style="font-size:11px;font-weight:700;color:{status_color};
                            background:rgba(255,255,255,0.05);border-radius:5px;
                            padding:3px 10px;font-family:'Space Grotesk',sans-serif;">
                            {status_text}
                        </span>
                    </div>""")
                with col5:
                    if user['username'] != 'admin':
                        if user['active']:
                            if st.button("Disable", key=f"dis_{user['id']}", use_container_width=True):
                                try:
                                    import sqlite3
                                    conn = sqlite3.connect("data/users.db")
                                    conn.execute("UPDATE users SET active=0 WHERE id=?", (user['id'],))
                                    conn.commit(); conn.close()
                                    st.success(f"{user['username']} disabled.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                        else:
                            if st.button("Enable", key=f"en_{user['id']}", use_container_width=True):
                                try:
                                    import sqlite3
                                    conn = sqlite3.connect("data/users.db")
                                    conn.execute("UPDATE users SET active=1 WHERE id=?", (user['id'],))
                                    conn.commit(); conn.close()
                                    st.success(f"{user['username']} enabled.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                    else:
                        inject('<div style="padding:14px 0;font-size:11px;color:#3a5a7a;">Protected</div>')

                inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:2px 0;"></div>')

    # ── TAB 2: ACTIVITY LOG ───────────────────────────────────────────────────
    with tab2:
        inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
            letter-spacing:0.15em;margin:16px 0 12px;font-family:'Space Grotesk',sans-serif;">
            Login Activity — Last 100 Sessions</div>""")

        if st.button("Refresh Activity Log", key="refresh_log"):
            st.rerun()

        if sessions_df.empty:
            st.info("No session history found. Users need to log in for activity to appear here.")
        else:
            # Color Active column
            sessions_df["Status"] = sessions_df["Active"].apply(
                lambda x: "Active" if x else "Ended"
            )
            sessions_df = sessions_df.drop(columns=["Active"])

            st.dataframe(
                sessions_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Username":      st.column_config.TextColumn("Username", width="small"),
                    "Role":          st.column_config.TextColumn("Role", width="small"),
                    "Login Time":    st.column_config.TextColumn("Login Time", width="medium"),
                    "Last Activity": st.column_config.TextColumn("Last Active", width="medium"),
                    "Expires At":    st.column_config.TextColumn("Expires At", width="medium"),
                    "Status":        st.column_config.TextColumn("Status", width="small"),
                }
            )

            inject(f"""
            <div style="font-size:10px;color:#3a5a7a;margin-top:8px;
                font-family:'Space Grotesk',sans-serif;">
                Showing {len(sessions_df)} sessions
            </div>""")

    # ── TAB 3: CREATE USER ────────────────────────────────────────────────────
    with tab3:
        inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
            letter-spacing:0.15em;margin:16px 0 12px;font-family:'Space Grotesk',sans-serif;">
            Create New User</div>""")

        col_form, col_info = st.columns([1, 1])

        with col_form:
            new_username = st.text_input("Username", placeholder="Enter username (min 3 chars)", key="new_username")
            new_password = st.text_input("Password", placeholder="Enter password (min 6 chars)", type="password", key="new_password")
            new_role = st.selectbox("Role", ["analyst", "viewer", "admin"], key="new_role",
                help="analyst: can query logs | viewer: read only | admin: full access")

            if st.button("Create User", type="primary", use_container_width=True, key="create_user_btn"):
                if not new_username or not new_password:
                    st.error("Please fill in both username and password.")
                elif len(new_username) < 3:
                    st.error("Username must be at least 3 characters.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif um.user_exists(new_username):
                    st.error(f"Username '{new_username}' already exists.")
                else:
                    success = um.create_user(new_username, new_password, role=new_role)
                    if success:
                        st.success(f"User '{new_username}' created successfully with role '{new_role}'.")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Please try again.")

        with col_info:
            inject("""
            <div style="padding:20px;background:rgba(0,170,255,0.04);
                border:1px solid rgba(0,170,255,0.15);border-radius:12px;margin-top:4px;">
                <div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
                    letter-spacing:0.15em;margin-bottom:14px;font-family:'Space Grotesk',sans-serif;">
                    Role Permissions
                </div>
                <div style="display:flex;flex-direction:column;gap:12px;">
                    <div>
                        <div style="font-size:12px;font-weight:700;color:#fbbf24;
                            font-family:'Space Grotesk',sans-serif;margin-bottom:4px;">Admin</div>
                        <div style="font-size:11px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">
                            Full access — manage users, view all data, query logs, export
                        </div>
                    </div>
                    <div style="height:1px;background:rgba(255,255,255,0.04);"></div>
                    <div>
                        <div style="font-size:12px;font-weight:700;color:#00aaff;
                            font-family:'Space Grotesk',sans-serif;margin-bottom:4px;">Analyst</div>
                        <div style="font-size:11px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">
                            Can query logs, view analytics, export results
                        </div>
                    </div>
                    <div style="height:1px;background:rgba(255,255,255,0.04);"></div>
                    <div>
                        <div style="font-size:12px;font-weight:700;color:#8ab0d0;
                            font-family:'Space Grotesk',sans-serif;margin-bottom:4px;">Viewer</div>
                        <div style="font-size:11px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">
                            Read-only access — can view results but not query
                        </div>
                    </div>
                </div>
            </div>""")

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("---")
    inject("""
    <div style="padding:11px 18px;background:rgba(0,170,255,0.03);
        border:1px solid rgba(0,170,255,0.09);border-radius:11px;
        display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:11px;color:#3a5a7a;font-weight:600;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;
                box-shadow:0 0 10px rgba(34,197,94,0.9);display:inline-block;margin-right:6px;"></span>
            System online
        </span>
        <span style="font-size:11px;color:#3a5a7a;font-weight:600;font-family:'Space Grotesk',sans-serif;">
            ICS-LogQueryGPT v1.0 — Admin Panel
        </span>
    </div>
    """)


if __name__ == "__main__":
    main()

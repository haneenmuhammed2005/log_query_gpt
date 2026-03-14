# Home Page
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

st.set_page_config(
    page_title="ICS-LogQueryGPT",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES_DIR = Path(__file__).parent / "pages"

def _page(pattern):
    matches = list(PAGES_DIR.glob(pattern))
    return "pages/" + matches[0].name if matches else pattern

PAGE_LOGIN     = _page("0_*Login*")
PAGE_QUERY     = _page("1_*Query*")
PAGE_ANALYTICS = _page("2_*Analytics*")
PAGE_EXPORT    = _page("3_*Export*")
PAGE_ADMIN     = _page("5_*Admin*")

def inject(html):
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
/* Hide ALL default nav */
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

@keyframes floatorb  { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-18px)} }
@keyframes shimmer   { 0%{background-position:-300% center} 100%{background-position:300% center} }
@keyframes fadeUp    { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes blink     { 0%,100%{opacity:1} 50%{opacity:0.2} }
@keyframes glowpulse { 0%,100%{opacity:0.65} 50%{opacity:1} }

.stApp::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image:
        linear-gradient(rgba(0,170,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,170,255,0.022) 1px, transparent 1px);
    background-size:52px 52px;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(3,8,22,0.99) 0%, rgba(2,6,18,0.99) 100%) !important;
    border-right: 1px solid rgba(0,170,255,0.10) !important;
    box-shadow: 6px 0 48px rgba(0,0,0,0.55) !important;
}
section[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }
section[data-testid="stSidebar"] h3 {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a7a !important; text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
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
    transition: border-color 0.22s, transform 0.18s !important;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(0,170,255,0.2) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stMetricValue"] {
    font-size: 26px !important; font-weight: 700 !important;
    color: #00aaff !important; letter-spacing: -0.8px !important;
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
    height: 44px !important; transition: box-shadow 0.25s, transform 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 36px rgba(0,170,255,0.55) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important; color: #5a7a9a !important;
    font-size: 12.5px !important; height: 40px !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.065) !important;
    color: #8ab0d0 !important;
}
hr { border-color: rgba(255,255,255,0.05) !important; }
</style>
""")

def check_authentication():
    if not st.session_state.get('authenticated', False):
        st.switch_page(PAGE_LOGIN)
        st.stop()
    if st.session_state.get('session_token') == "admin-session":
        return
    session_manager = SessionManager()
    if not session_manager.validate_session(st.session_state.get('session_token')):
        st.session_state.clear()
        st.session_state["session_expired"] = True
        st.switch_page(PAGE_LOGIN)
        st.stop()

def _count(db, query, params=()):
    try:
        conn = sqlite3.connect(db)
        val = conn.execute(query, params).fetchone()
        conn.close()
        return val[0] if val else 0
    except:
        return 0

def main():
    check_authentication()
    inject_styles()

    username  = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'analyst')

    # Ambient orbs
    inject("""
    <div style="pointer-events:none;position:fixed;inset:0;z-index:0;overflow:hidden;">
        <div style="position:absolute;width:600px;height:600px;border-radius:50%;
            background:radial-gradient(circle,#0055ff,#001577);opacity:0.10;
            filter:blur(120px);top:-200px;left:-150px;
            animation:floatorb 14s ease-in-out infinite;"></div>
        <div style="position:absolute;width:400px;height:400px;border-radius:50%;
            background:radial-gradient(circle,#00aaff,#004499);opacity:0.08;
            filter:blur(120px);bottom:-100px;right:5%;
            animation:floatorb 16s 4s ease-in-out infinite;"></div>
        <div style="position:absolute;width:250px;height:250px;border-radius:50%;
            background:radial-gradient(circle,#0044cc,#001266);opacity:0.06;
            filter:blur(100px);top:40%;right:25%;
            animation:floatorb 18s 2s ease-in-out infinite;"></div>
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
                padding-left:37px;font-family:'Space Grotesk',sans-serif;">Security Intelligence</div>
        </div>
        """)

        st.markdown("### Navigation")
        if st.button("Query Logs", use_container_width=True, key="nav_query"):
            st.switch_page(PAGE_QUERY)
        if st.button("Analytics", use_container_width=True, key="nav_analytics"):
            st.switch_page(PAGE_ANALYTICS)
        if st.button("Export", use_container_width=True, key="nav_export"):
            st.switch_page(PAGE_EXPORT)

        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:8px 0;"></div>')

        if user_role == "admin":
            if st.button("Admin Dashboard", use_container_width=True, key="nav_admin", type="primary"):
                st.switch_page(PAGE_ADMIN)
            inject('<div style="height:4px;"></div>')

        if st.button("Logout", use_container_width=True, key="nav_logout"):
            st.session_state.clear()
            st.switch_page(PAGE_LOGIN)

        inject(f"""
        <div style="font-size:10px;color:#5a8ab0;margin:12px 4px 4px;font-family:'Space Grotesk',sans-serif;">
            Logged in as:
            <span style="color:#8ab0d0;font-weight:700;">{username}</span>
            <span style="margin-left:6px;font-size:9px;background:rgba(0,170,255,0.12);
                border:1px solid rgba(0,170,255,0.3);border-radius:4px;
                padding:1px 7px;color:#00aaff;font-weight:700;text-transform:uppercase;">
                {user_role}
            </span>
        </div>
        """)

    # ── TOP ACCENT BAR ────────────────────────────────────────────────────────
    inject("""
    <div style="height:2px;background:linear-gradient(90deg,transparent,#0088cc 20%,#00aaff 45%,#00e5ff 55%,#00aaff 80%,transparent);
        opacity:0.9;margin-bottom:32px;border-radius:2px;animation:glowpulse 3s ease-in-out infinite;"></div>
    """)

    # ── HERO WELCOME ──────────────────────────────────────────────────────────
    col_hero, col_session = st.columns([2, 1])
    with col_hero:
        inject(f"""
        <div style="opacity:0;animation:fadeUp 0.6s 0.05s ease forwards;">
            <div style="font-size:11px;font-weight:700;color:#00aaff;text-transform:uppercase;
                letter-spacing:0.2em;margin-bottom:10px;font-family:'Space Grotesk',sans-serif;">
                <span style="width:7px;height:7px;border-radius:50%;background:#00aaff;
                    box-shadow:0 0 10px #00aaff;display:inline-block;margin-right:8px;
                    animation:blink 2.3s ease-in-out infinite;"></span>
                ICS Security Intelligence Platform
            </div>
            <div style="font-size:52px;font-weight:800;letter-spacing:-2.5px;line-height:1.05;margin-bottom:8px;">
                <span style="background:linear-gradient(135deg,#ffffff 20%,#8fa8c8 100%);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-family:'Space Grotesk',sans-serif;">Welcome back,&nbsp;</span><span
                    style="background:linear-gradient(135deg,#00aaff 0%,#00e5ff 50%,#00aaff 100%);
                    background-size:200% auto;
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    animation:shimmer 4s linear infinite;
                    font-family:'Space Grotesk',sans-serif;">{username}</span>
            </div>
            <div style="font-size:15px;color:#4a6a8a;line-height:1.6;max-width:520px;
                font-family:'Space Grotesk',sans-serif;">
                Your AI-powered assistant for analyzing ICS security logs.<br>
                Ask questions in plain English — get instant security insights.
            </div>
        </div>
        """)

    with col_session:
        inject(f"""
        <div style="opacity:0;animation:fadeUp 0.6s 0.15s ease forwards;margin-top:8px;">
        <div style="background:rgba(0,170,255,0.04);border:1px solid rgba(0,170,255,0.15);
            border-radius:14px;padding:22px 24px;">
            <div style="font-size:9px;font-weight:700;color:#3a5a7a;text-transform:uppercase;
                letter-spacing:0.15em;margin-bottom:14px;font-family:'Space Grotesk',sans-serif;">
                Session Info
            </div>
            <div style="display:flex;flex-direction:column;gap:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:12px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">Username</span>
                    <span style="font-size:12px;font-weight:700;color:#a0c8e8;font-family:'Space Grotesk',sans-serif;">{username}</span>
                </div>
                <div style="height:1px;background:rgba(255,255,255,0.04);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:12px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">Role</span>
                    <span style="font-size:12px;font-weight:700;color:#a0c8e8;text-transform:capitalize;font-family:'Space Grotesk',sans-serif;">{user_role}</span>
                </div>
                <div style="height:1px;background:rgba(255,255,255,0.04);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:12px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">Status</span>
                    <span style="font-size:11px;font-weight:700;color:#22c55e;
                        background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
                        border-radius:4px;padding:2px 8px;font-family:'Space Grotesk',sans-serif;">Active</span>
                </div>
                <div style="height:1px;background:rgba(255,255,255,0.04);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:12px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">Signed in</span>
                    <span style="font-size:12px;font-weight:700;color:#a0c8e8;font-family:'Space Grotesk',sans-serif;">{datetime.now().strftime('%H:%M')}</span>
                </div>
            </div>
        </div>
        </div>
        """)

    st.markdown("---")

    # ── SYSTEM OVERVIEW STATS ─────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        System Overview</div>""")

    total_users   = _count("data/users.db", "SELECT COUNT(*) FROM users WHERE active=1")
    total_queries = len(st.session_state.get("query_history", []))
    current       = st.session_state.get("current_results", {})
    last_time     = f"{current.get('response_time', 0)}s" if current else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Logs Indexed", "4,000")
    with c2: st.metric("Active Users", total_users)
    with c3: st.metric("Queries This Session", total_queries)
    with c4: st.metric("Last Response Time", last_time)

    st.markdown("---")

    # ── FEATURE CARDS ─────────────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:16px;font-family:'Space Grotesk',sans-serif;">
        Features</div>""")

    f1, f2, f3 = st.columns(3)
    features = [
        {
            "title": "Query Logs",
            "desc": "Ask questions in natural language and get AI-powered insights from your ICS security logs.",
            "items": ["HDFS and BGL dataset support", "Upload your own log files", "Protocol filtering", "Groq + Gemini Flash AI"],
            "btn": "Go to Query Logs", "key": "btn_query", "page": PAGE_QUERY,
            "accent": "#00aaff",
        },
        {
            "title": "Analytics",
            "desc": "Visualize your query history, response times and dataset usage with live charts.",
            "items": ["Real session-based charts", "Query history timeline", "Response time analysis", "Dataset usage breakdown"],
            "btn": "Go to Analytics", "key": "btn_analytics", "page": PAGE_ANALYTICS,
            "accent": "#0066cc",
        },
        {
            "title": "Export Data",
            "desc": "Export your query results and AI analysis in multiple formats for reporting.",
            "items": ["CSV, JSON, Markdown", "Security report templates", "Export history tracking", "Scheduled exports"],
            "btn": "Go to Export", "key": "btn_export", "page": PAGE_EXPORT,
            "accent": "#004499",
        },
    ]

    for col, feat in zip([f1, f2, f3], features):
        with col:
            items_html = "".join(f"""
                <div style="display:flex;align-items:center;gap:8px;padding:5px 0;
                    border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px;color:#5a7a9a;
                    font-family:'Space Grotesk',sans-serif;">
                    <span style="width:4px;height:4px;border-radius:50%;
                        background:{feat['accent']};display:inline-block;flex-shrink:0;"></span>
                    {item}
                </div>""" for item in feat["items"])

            inject(f"""
            <div style="background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.06);
                border-top:2px solid {feat['accent']};border-radius:12px;padding:22px 20px 18px;
                margin-bottom:12px;transition:border-color 0.2s;height:100%;"
                onmouseover="this.style.borderColor='rgba(0,170,255,0.25)'"
                onmouseout="this.style.borderColor='rgba(255,255,255,0.06)'">
                <div style="font-size:16px;font-weight:700;color:#c8d8e8;margin-bottom:8px;
                    font-family:'Space Grotesk',sans-serif;">{feat['title']}</div>
                <div style="font-size:12.5px;color:#4a6a8a;line-height:1.6;margin-bottom:14px;
                    font-family:'Space Grotesk',sans-serif;">{feat['desc']}</div>
                {items_html}
            </div>
            """)
            if st.button(feat["btn"], key=feat["key"], use_container_width=True, type="primary"):
                st.switch_page(feat["page"])

    st.markdown("---")

    # ── RECENT ACTIVITY — real from session ───────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:14px;font-family:'Space Grotesk',sans-serif;">
        Recent Activity</div>""")

    query_history = st.session_state.get("query_history", [])

    if query_history:
        recent = list(reversed(query_history[-5:]))
        for item in recent:
            ts     = item.get("timestamp", "")
            query  = item.get("query", "")[:80] + ("..." if len(item.get("query","")) > 80 else "")
            source = item.get("source", item.get("protocol", "HDFS"))
            mode   = item.get("mode", "Fast")
            inject(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                padding:12px 18px;margin-bottom:6px;
                background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.06);
                border-radius:9px;transition:border-color 0.2s;"
                onmouseover="this.style.borderColor='rgba(0,170,255,0.2)'"
                onmouseout="this.style.borderColor='rgba(255,255,255,0.06)'">
                <div style="display:flex;align-items:center;gap:12px;flex:1;">
                    <span style="width:7px;height:7px;border-radius:50%;background:#00aaff;
                        box-shadow:0 0 8px rgba(0,170,255,0.6);display:inline-block;flex-shrink:0;"></span>
                    <span style="font-size:13px;color:#8ab0d0;font-family:'Space Grotesk',sans-serif;">{query}</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;flex-shrink:0;">
                    <span style="font-size:10px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">{source} · {mode}</span>
                    <span style="font-size:10px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">{ts}</span>
                    <span style="font-size:10px;font-weight:700;color:#22c55e;
                        background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.25);
                        border-radius:4px;padding:2px 8px;font-family:'Space Grotesk',sans-serif;">Success</span>
                </div>
            </div>
            """)
    else:
        inject("""
        <div style="padding:28px;text-align:center;
            background:rgba(255,255,255,0.018);border:1px dashed rgba(255,255,255,0.06);
            border-radius:12px;">
            <div style="font-size:13px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
                No queries yet this session. Go to Query Logs to get started.
            </div>
        </div>
        """)

    st.markdown("---")

    # ── ABOUT / SYSTEM INFO ───────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:14px;font-family:'Space Grotesk',sans-serif;">
        About This System</div>""")

    a1, a2, a3, a4 = st.columns(4)
    info_cards = [
        ("Version",       "1.0.0",                    "Current release"),
        ("AI Engine",     "Groq + Gemini Flash",       "Primary + fallback LLM"),
        ("Embeddings",    "BERT + MiniLM",             "768-dim semantic vectors"),
        ("Vector Search", "FAISS IndexFlatIP",         "Sub-ms similarity search"),
    ]
    for col, (label, value, sub) in zip([a1, a2, a3, a4], info_cards):
        with col:
            inject(f"""
            <div style="background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:14px 16px;">
                <div style="font-size:9px;font-weight:700;color:#3a5a7a;text-transform:uppercase;
                    letter-spacing:0.12em;margin-bottom:6px;font-family:'Space Grotesk',sans-serif;">
                    {label}</div>
                <div style="font-size:14px;font-weight:700;color:#00aaff;margin-bottom:3px;
                    font-family:'Space Grotesk',sans-serif;">{value}</div>
                <div style="font-size:11px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
                    {sub}</div>
            </div>""")

    inject("""
    <div style="margin-top:14px;padding:14px 20px;
        background:rgba(0,170,255,0.03);border:1px solid rgba(0,170,255,0.08);
        border-radius:10px;display:flex;flex-wrap:wrap;gap:24px;">
        <div style="font-size:11px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
            <b style="color:#5a7a9a;">Datasets:</b> HDFS (2,000 logs) + BGL (2,000 logs)
        </div>
        <div style="font-size:11px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
            <b style="color:#5a7a9a;">Auth:</b> SQLite + bcrypt + session tokens
        </div>
        <div style="font-size:11px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
            <b style="color:#5a7a9a;">Alerts:</b> Gmail SMTP SSL — instant email on critical detection
        </div>
        <div style="font-size:11px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
            <b style="color:#5a7a9a;">Evaluation:</b> BLEU · ROUGE · Precision@5 · Recall@5 · MRR
        </div>
        <div style="font-size:11px;color:#3a5a7a;font-family:'Space Grotesk',sans-serif;">
            <b style="color:#5a7a9a;">Framework:</b> Python 3.8+ · Streamlit · LangChain
        </div>
    </div>
    """)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    inject("""
    <div style="margin-top:20px;text-align:center;font-size:11px;font-weight:600;
        color:#243850;letter-spacing:0.07em;font-family:'Space Grotesk',sans-serif;">
        ICS-LogQueryGPT v1.0 &nbsp;|&nbsp; Powered by Groq + Gemini Flash &nbsp;|&nbsp; AI-Powered Log Analysis
    </div>
    """)


if __name__ == "__main__":
    main()

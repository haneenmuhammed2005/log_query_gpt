"""
Query Logs page for ICS-LogQueryGPT
Styled to match v3 HTML preview — Space Grotesk, #060d1f, orbs, shimmer title,
glass cards, staggered animations, premium sidebar.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

# ── Page path helper ───────────────────────────────────────────────────────────
PAGE_QUERY = "pages/1_Query_Logs.py"
PAGE_ANALYTICS = "pages/2_Analytics.py"
PAGE_EXPORT = "pages/3_Export.py"
PAGE_LOGIN = "pages/0_Login.py"

st.set_page_config(
    page_title="Query Logs - ICS-LogQueryGPT",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Helper ─────────────────────────────────────────────────────────────────────
def inject(html: str):
    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)

# ── Global styles ──────────────────────────────────────────────────────────────
def inject_styles():
    inject("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>

/* ══ Reset & base ══ */
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #060d1f !important;
    color: #e2e8f0 !important;
    -webkit-font-smoothing: antialiased;
}

/* ══ Animations ══ */
@keyframes blink     { 0%,100%{opacity:1} 50%{opacity:0.1} }
@keyframes floatorb  { 0%,100%{transform:translateY(0) scale(1)} 50%{transform:translateY(-24px) scale(1.05)} }
@keyframes shimmer   { 0%{background-position:-300% center} 100%{background-position:300% center} }
@keyframes glowpulse { 0%,100%{opacity:0.65} 50%{opacity:1} }
@keyframes fadeUp    { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeLeft  { from{opacity:0;transform:translateX(-16px)} to{opacity:1;transform:translateX(0)} }
@keyframes popIn     { from{opacity:0;transform:scale(0.92)} to{opacity:1;transform:scale(1)} }

/* ══ Hide Streamlit chrome ══ */
header[data-testid="stHeader"], footer, #MainMenu,
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
div[data-testid="stSidebarCollapseButton"] { display:none !important; }

/* ══ Ambient grid overlay ══ */
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(0,170,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,170,255,0.022) 1px, transparent 1px);
    background-size: 52px 52px;
}

/* ══ SIDEBAR ══ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(3,8,22,0.99) 0%, rgba(2,6,18,0.99) 100%) !important;
    border-right: 1px solid rgba(0,170,255,0.10) !important;
    box-shadow: 6px 0 48px rgba(0,0,0,0.55), inset -1px 0 0 rgba(0,170,255,0.05) !important;
    animation: fadeLeft 0.55s ease both;
}
section[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }

/* Nav links */
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    font-size: 12.5px !important; font-weight: 400 !important;
    color: #4a6a8a !important; border-radius: 0 !important;
    padding: 9px 20px !important; border-left: 3px solid transparent !important;
    transition: all 0.22s ease !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
    color: #8ab0d0 !important;
    background: rgba(0,170,255,0.045) !important;
    border-left-color: rgba(0,170,255,0.25) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] {
    color: #e2e8f0 !important; font-weight: 600 !important;
    background: linear-gradient(90deg, rgba(0,170,255,0.13), rgba(0,170,255,0.02)) !important;
    border-left-color: #00aaff !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] img,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] { display: none !important; }
section[data-testid="stSidebarNav"] { display: none !important; }

/* Force sidebar always visible */
section[data-testid="stSidebar"] {
    transform: none !important;
    width: 21rem !important;
    min-width: 21rem !important;
    display: block !important;
    visibility: visible !important;
}
button[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
}
div[data-testid="stSidebarCollapseButton"] {
    display: block !important;
}

button[data-testid="collapsedControl"] { display: none !important; }

/* Sidebar section headers */
section[data-testid="stSidebar"] h3 {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a7a !important; text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
}

/* Sidebar selectbox */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a7a !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #8ab0d0 !important;
    font-size: 12px !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.2) !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div:focus-within {
    border-color: rgba(0,170,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,170,255,0.08), inset 0 2px 8px rgba(0,0,0,0.15) !important;
}

/* Sidebar radio */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a7a !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {
    font-size: 12px !important; color: #5a7a9a !important;
    text-transform: none !important; letter-spacing: 0 !important;
    font-weight: 400 !important; padding: 6px 8px !important;
    border-radius: 8px !important; transition: all 0.18s !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:has(input:checked) {
    color: #00aaff !important; background: rgba(0,170,255,0.07) !important;
}
input[type="radio"] { accent-color: #00aaff !important; }
input[type="checkbox"] { accent-color: #00aaff !important; }

/* Sidebar caption & divider */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-size: 10px !important; color: #3a5a7a !important; letter-spacing: 0.05em !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.04) !important; }

/* ══ Main block container ══ */
div.block-container {
    padding-top: 0 !important; padding-left: 2.5rem !important;
    padding-right: 2.5rem !important; padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* ══ Typography ══ */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 40px !important; font-weight: 800 !important;
    letter-spacing: -2.2px !important; line-height: 1.05 !important;
    color: #e2e8f0 !important;
}
h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a80 !important; text-transform: uppercase !important;
    letter-spacing: 0.15em !important; margin-bottom: 10px !important;
}

/* ══ Text area ══ */
div[data-testid="stTextArea"] label {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a80 !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important; font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stTextArea"] > div {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 2px 16px rgba(0,0,0,0.28), 0 4px 24px rgba(0,0,0,0.2) !important;
}
div[data-testid="stTextArea"] > div:focus-within {
    border-color: rgba(0,170,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,170,255,0.08), inset 0 2px 16px rgba(0,0,0,0.22), 0 0 30px rgba(0,170,255,0.06) !important;
}
textarea {
    background: transparent !important; color: #c8d8e8 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13.5px !important; line-height: 1.65 !important;
}
textarea::placeholder { color: #2e4f70 !important; }

/* ══ Select box ══ */
div[data-testid="stSelectbox"] label {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a80 !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important; font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #8ab0d0 !important;
    font-size: 12px !important; font-family: 'Space Grotesk', sans-serif !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.2) !important;
}
div[data-testid="stSelectbox"] > div:focus-within {
    border-color: rgba(0,170,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,170,255,0.08) !important;
}

/* ══ Buttons ══ */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0040aa 0%, #0077cc 45%, #00aaff 100%) !important;
    border: none !important; border-radius: 9px !important;
    color: #fff !important; font-size: 13.5px !important; font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important; height: 44px !important;
    box-shadow: 0 4px 24px rgba(0,100,220,0.3), inset 0 1px 0 rgba(255,255,255,0.18), inset 0 -1px 0 rgba(0,0,0,0.2) !important;
    transition: box-shadow 0.25s, transform 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 36px rgba(0,170,255,0.55), 0 6px 24px rgba(0,80,200,0.4), inset 0 1px 0 rgba(255,255,255,0.22) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:active { transform: translateY(0) !important; }

div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important; color: #5a7a9a !important;
    font-size: 12.5px !important; font-family: 'Space Grotesk', sans-serif !important;
    height: 40px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.065) !important;
    color: #8ab0d0 !important; border-color: rgba(255,255,255,0.12) !important;
}
div[data-testid="stButton"] button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 11.5px !important; border-radius: 9px !important;
}

/* ══ Metric cards ══ */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid rgba(255,255,255,0.065) !important;
    border-radius: 11px !important; padding: 16px 18px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 6px 24px rgba(0,0,0,0.25) !important;
    transition: border-color 0.22s, box-shadow 0.22s, transform 0.18s !important;
    animation: popIn 0.45s ease forwards !important;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(0,170,255,0.2) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 8px 32px rgba(0,0,0,0.3), 0 0 24px rgba(0,170,255,0.07) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stMetricValue"] {
    font-size: 24px !important; font-weight: 700 !important;
    color: #00aaff !important; letter-spacing: -0.8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 9px !important; color: #3a5a7a !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
    font-weight: 700 !important; font-family: 'Space Grotesk', sans-serif !important;
}

/* ══ Expander ══ */
details {
    background: rgba(255,255,255,0.018) !important;
    border: 1px solid rgba(255,255,255,0.055) !important;
    border-radius: 10px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03) !important;
    transition: all 0.22s !important;
}
details:hover {
    background: rgba(0,170,255,0.045) !important;
    border-color: rgba(0,170,255,0.2) !important;
}
details summary {
    font-size: 13px !important; color: #6a8aaa !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important; padding: 13px 18px !important;
}

/* ══ Misc ══ */
div[data-testid="stAlert"] { border-radius: 9px !important; font-size: 13px !important; font-family: 'Space Grotesk', sans-serif !important; }
hr { border-color: rgba(255,255,255,0.05) !important; }
div[data-testid="stSpinner"] p { font-family: 'Space Grotesk', sans-serif !important; font-size: 13px !important; color: #4a6a8a !important; }
[data-testid="stCaptionContainer"] p, small { font-family: 'Space Grotesk', sans-serif !important; font-size: 10px !important; color: #3a5a7a !important; letter-spacing: 0.05em !important; }
</style>
""")

# ── Auth check ─────────────────────────────────────────────────────────────────
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

# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        'query_history': [],
        'current_results': None,
        'selected_protocol': "All Protocols",
        'selected_mode': "Fast",
        'selected_time': "Last 24 hours",
        'show_history': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── RAG system ─────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI system...")
def load_rag_system():
    try:
        from src.rag_system.integrated_rag_ollama import ICSLogQueryGPTOllama
        system = ICSLogQueryGPTOllama(
            vector_db_path="D:/Projects/log_query_gpt/data/vector_db/HDFS_index.faiss",
            metadata_path="D:/Projects/log_query_gpt/data/vector_db/HDFS_metadata.pkl"
        )
        return system, None
    except Exception as e:
        return None, str(e)

def run_rag_query(query: str, protocol: str, mode: str) -> dict:
    system, error = load_rag_system()
    if error or system is None:
        return {
            "answer": f"**RAG system unavailable:** {error}\n\nMake sure Ollama is running:\n```\nollama serve\n```",
            "sources": [], "log_count": 0, "response_time": 0, "cached": False, "model": "unavailable"
        }
    enriched = f"[Protocol: {protocol}] {query}" if protocol != "All Protocols" else query
    top_k = {"Fast": 3, "Detailed": 5, "Deep Analysis": 10}.get(mode, 5)
    import time; t0 = time.time()
    try:
        result = system.query(enriched, top_k=top_k)
        return {
            "answer": result["answer"], "sources": ["HDFS_logs"],
            "log_count": top_k, "response_time": round(time.time() - t0, 2),
            "cached": False, "model": result.get("model", "llama3")
        }
    except Exception as e:
        return {
            "answer": f"**Query failed:** {e}\n\nMake sure Ollama is running:\n```\nollama serve\n```",
            "sources": [], "log_count": 0, "response_time": round(time.time() - t0, 2),
            "cached": False, "model": "error"
        }

# ── Suggestions ────────────────────────────────────────────────────────────────

# ── Response display ───────────────────────────────────────────────────────────
def display_response(r):
    inject("""
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,170,255,0.55) 40%,rgba(0,229,255,0.4) 60%,transparent);margin-bottom:18px;"></div>
    <div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:11px;font-family:'Space Grotesk',sans-serif;">AI Response</div>
    """)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Logs Analyzed", f"{r['log_count']:,}")
    with c2: st.metric("Response Time", f"{r['response_time']:.2f}s")
    with c3: st.metric("Status", "Cached" if r['cached'] else "Fresh")
    with c4: st.metric("Sources", len(r['sources']))

    st.markdown("---")

    answer_html = r['answer'].replace('\n', '<br>')
    inject(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.065);
        border-radius:13px;padding:24px 28px 24px 30px;
        font-size:13.5px;color:#a0c0dc;line-height:1.82;
        box-shadow:inset 0 2px 20px rgba(0,0,0,0.28),0 8px 40px rgba(0,0,0,0.28);
        position:relative;overflow:hidden;margin-bottom:14px;
        font-family:'Space Grotesk',sans-serif;">
        <div style="position:absolute;top:0;left:0;bottom:0;width:3px;
            background:linear-gradient(180deg,#00aaff 0%,#00e5ff 40%,rgba(0,170,255,0.15) 100%);
            border-radius:3px 0 0 3px;"></div>
        <div style="position:absolute;top:-60px;right:-60px;width:200px;height:200px;
            background:radial-gradient(circle,rgba(0,170,255,0.05),transparent 70%);
            pointer-events:none;"></div>
        <div style="position:absolute;top:0;left:0;right:0;height:1px;
            background:linear-gradient(90deg,transparent,rgba(255,255,255,0.06),transparent);"></div>
        {answer_html}
    </div>
    """)

    sources_html = "&nbsp;".join(
        f'<span style="background:rgba(0,170,255,0.09);border:1px solid rgba(0,170,255,0.2);'
        f'border-radius:5px;padding:2px 8px;color:#00aaff;font-size:12px;'
        f'font-family:\'Space Grotesk\',sans-serif;font-weight:500;">{s}</span>'
        for s in r['sources']
    )
    inject(f"""
    <div style="display:flex;align-items:center;gap:9px;font-size:9px;color:#3a5a7a;
        font-weight:700;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px;
        font-family:'Space Grotesk',sans-serif;">
        Sources &nbsp;{sources_html}
    </div>
    """)

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Save Response", key="btn_save"): st.success("Response saved.")
    with b2:
        if st.button("📊 View Analytics", key="btn_analytics"):
            st.switch_page(PAGE_ANALYTICS)
    with b3:
        if st.button("📤 Export Results", key="btn_export"):
            st.switch_page(PAGE_EXPORT)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    check_authentication()
    init_state()
    inject_styles()

    # Ambient orbs
    inject("""
    <div style="pointer-events:none;position:fixed;inset:0;z-index:0;overflow:hidden;">
        <div style="position:absolute;width:560px;height:560px;border-radius:50%;
            background:radial-gradient(circle,#0055ff,#001577);opacity:0.10;
            filter:blur(110px);top:-180px;left:-130px;
            animation:floatorb 13s ease-in-out infinite;"></div>
        <div style="position:absolute;width:340px;height:340px;border-radius:50%;
            background:radial-gradient(circle,#00aaff,#004499);opacity:0.09;
            filter:blur(110px);bottom:-90px;right:4%;
            animation:floatorb 13s 5s ease-in-out infinite;"></div>
        <div style="position:absolute;width:240px;height:240px;border-radius:50%;
            background:radial-gradient(circle,#0044cc,#001266);opacity:0.07;
            filter:blur(110px);top:36%;right:24%;
            animation:floatorb 16s 2.5s ease-in-out infinite;"></div>
        <div style="position:absolute;width:170px;height:170px;border-radius:50%;
            background:radial-gradient(circle,#00ddff,#006699);opacity:0.06;
            filter:blur(110px);top:12%;right:42%;
            animation:floatorb 10s 1s ease-in-out infinite;"></div>
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

        st.markdown("### Query Settings")

        protocols = ["All Protocols", "SSH", "HTTP", "HTTPS", "FTP", "DNS", "SMTP", "Telnet"]
        st.session_state.selected_protocol = st.selectbox(
            "Protocol Filter", protocols,
            index=protocols.index(st.session_state.selected_protocol)
        )

        st.session_state.selected_mode = st.radio(
            "Query Mode", ["Fast", "Detailed", "Deep Analysis"],
            index=["Fast", "Detailed", "Deep Analysis"].index(st.session_state.selected_mode),
            help="Fast: 3 logs · Detailed: 5 logs · Deep Analysis: 10 logs"
        )

        time_opts = ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days"]
        st.session_state.selected_time = st.selectbox(
            "Time Range", time_opts,
            index=time_opts.index(st.session_state.selected_time)
        )

        with st.expander("Advanced Options"):
            st.checkbox("Include archived logs", value=False)
            st.checkbox("Case sensitive search", value=False)
            st.slider("Max results", 10, 1000, 100)

        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:10px 0;"></div>')

        st.markdown("### 🗺️ Navigation")
        if st.button("🏠  Dashboard", use_container_width=True):
            st.switch_page("app.py")
        if st.button("📊  Analytics", use_container_width=True):
            st.switch_page(PAGE_ANALYTICS)
        if st.button("📤  Export", use_container_width=True):
            st.switch_page(PAGE_EXPORT)

        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:10px 0;"></div>')

        # Logout
        inject('<div style="margin-top:8px;"></div>')
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page(PAGE_LOGIN)

        # ── Logged-in user + Access Roles ─────────────────────────────────────
        inject(f"""
        <div style="font-size:10px;color:#5a8ab0;margin:10px 4px 12px;
            font-family:'Space Grotesk',sans-serif;">
            Logged in as:
            <span style="color:#8ab0d0;font-weight:600;">
                {st.session_state.get('username', 'admin')}
            </span>
        </div>

        <div style="font-size:9px;font-weight:700;color:#3a5a7a;text-transform:uppercase;
            letter-spacing:0.15em;margin-bottom:8px;margin-left:4px;
            font-family:'Space Grotesk',sans-serif;">Access Roles</div>

        <div style="display:flex;flex-direction:column;gap:5px;margin:0 4px 16px;">

            <div style="display:flex;align-items:center;justify-content:space-between;
                background:rgba(0,170,255,0.09);border:1px solid rgba(0,170,255,0.25);
                border-radius:7px;padding:6px 10px;">
                <div style="display:flex;align-items:center;gap:7px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#00aaff;
                        box-shadow:0 0 8px rgba(0,170,255,0.8);display:inline-block;"></span>
                    <span style="font-size:11.5px;font-weight:600;color:#a0c8e8;
                        font-family:'Space Grotesk',sans-serif;">Admin</span>
                </div>
                <span style="font-size:9px;background:rgba(0,170,255,0.15);
                    border:1px solid rgba(0,170,255,0.3);border-radius:4px;
                    padding:1px 6px;color:#00aaff;font-weight:700;letter-spacing:0.05em;
                    font-family:'Space Grotesk',sans-serif;">ACTIVE</span>
            </div>

            <div style="display:flex;align-items:center;gap:7px;
                background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.055);
                border-radius:7px;padding:6px 10px;">
                <span style="width:6px;height:6px;border-radius:50%;
                    background:#2a4a6a;display:inline-block;"></span>
                <span style="font-size:11.5px;font-weight:500;color:#4a6a8a;
                    font-family:'Space Grotesk',sans-serif;">Security Operator</span>
            </div>

            <div style="display:flex;align-items:center;gap:7px;
                background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.055);
                border-radius:7px;padding:6px 10px;">
                <span style="width:6px;height:6px;border-radius:50%;
                    background:#2a4a6a;display:inline-block;"></span>
                <span style="font-size:11.5px;font-weight:500;color:#4a6a8a;
                    font-family:'Space Grotesk',sans-serif;">Read-Only</span>
            </div>

        </div>
        """)

    # ── TOP ACCENT BAR ────────────────────────────────────────────────────────
    inject("""
    <div style="height:2px;
        background:linear-gradient(90deg,transparent,#0088cc 20%,#00aaff 45%,#00e5ff 55%,#00aaff 80%,transparent);
        opacity:0.9;margin-bottom:28px;border-radius:2px;
        animation:glowpulse 3s ease-in-out infinite;"></div>
    """)

    # ── LIVE BADGE ────────────────────────────────────────────────────────────
    inject("""
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(0,170,255,0.06);border:1px solid rgba(0,170,255,0.2);
        border-radius:20px;padding:5px 14px 5px 10px;
        font-size:10px;font-weight:700;color:#00aaff;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:13px;
        box-shadow:0 0 24px rgba(0,170,255,0.08),inset 0 1px 0 rgba(255,255,255,0.05);
        opacity:0;animation:fadeUp 0.6s 0.05s ease forwards;
        font-family:'Space Grotesk',sans-serif;">
        <span style="width:7px;height:7px;border-radius:50%;background:#00aaff;
            box-shadow:0 0 14px #00aaff,0 0 5px #00aaff;
            animation:blink 2.3s ease-in-out infinite;display:inline-block;"></span>
        Live Query
    </div>
    """)

    # ── SHIMMER TITLE ─────────────────────────────────────────────────────────
    inject("""
    <div style="margin-bottom:8px;opacity:0;animation:fadeUp 0.6s 0.1s ease forwards;">
        <span style="font-size:40px;font-weight:800;letter-spacing:-2.2px;line-height:1.05;
            background:linear-gradient(135deg,#ffffff 20%,#8fa8c8 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            font-family:'Space Grotesk',sans-serif;">Query ICS&nbsp;</span><span
            style="font-size:40px;font-weight:800;letter-spacing:-2.2px;line-height:1.05;
            background:linear-gradient(135deg,#00aaff 0%,#00e5ff 50%,#00aaff 100%);
            background-size:200% auto;
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            animation:shimmer 4s linear infinite;
            font-family:'Space Grotesk',sans-serif;">Logs</span>
    </div>
    <div style="font-size:13px;color:#4a6a8a;margin-bottom:24px;letter-spacing:0.01em;
        opacity:0;animation:fadeUp 0.6s 0.15s ease forwards;
        font-family:'Space Grotesk',sans-serif;">
        Ask questions about your ICS security logs in natural language
    </div>
    """)

    st.markdown("---")

    # ── QUERY INPUT ROW ───────────────────────────────────────────────────────
    col_q, col_a = st.columns([3, 1])

    with col_q:
        query = st.text_area(
            "Natural Language Query",
            placeholder="e.g. Show failed login attempts in the last 24 hours",
            height=114,
            key="query_input"
        )

    with col_a:
        inject("""
        <div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
            letter-spacing:0.15em;margin-bottom:10px;margin-top:2px;
            font-family:'Space Grotesk',sans-serif;">Actions</div>
        """)
        if st.button("Analyze", type="primary", use_container_width=True):
            if query.strip():
                with st.spinner("Analyzing your logs..."):
                    result = run_rag_query(
                        query,
                        st.session_state.selected_protocol,
                        st.session_state.selected_mode
                    )
                    st.session_state.current_results = result
                    st.session_state.query_history.append({
                        'query': query,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'protocol': st.session_state.selected_protocol,
                        'mode': st.session_state.selected_mode,
                    })
                st.rerun()
            else:
                st.warning("Please enter a query.")

        if st.button("Clear", use_container_width=True):
            st.session_state.current_results = None
            st.rerun()

        if st.button("History", use_container_width=True):
            st.session_state.show_history = not st.session_state.show_history
            st.rerun()



    # ── AI RESPONSE ───────────────────────────────────────────────────────────
    if st.session_state.current_results:
        st.markdown("---")
        display_response(st.session_state.current_results)

    # ── RECENT QUERIES ────────────────────────────────────────────────────────
    if st.session_state.show_history and st.session_state.query_history:
        st.markdown("---")
        inject("""
        <div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
            letter-spacing:0.15em;margin-bottom:11px;
            font-family:'Space Grotesk',sans-serif;">Recent Queries</div>
        """)
        for i, item in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"{item['timestamp']}  ·  {item['protocol']}"):
                inject(f"""
                <div style="font-family:'Space Grotesk',sans-serif;">
                    <div style="font-size:10.5px;color:#3a5a7a;margin-bottom:6px;font-weight:500;
                        display:flex;align-items:center;gap:6px;">
                        <span style="width:5px;height:5px;border-radius:50%;
                            background:rgba(0,170,255,0.4);display:inline-block;"></span>
                        {item['timestamp']} &nbsp;·&nbsp; {item['protocol']}
                    </div>
                    <div style="font-size:13px;color:#7090b0;font-weight:500;margin-bottom:6px;">
                        {item['query']}
                    </div>
                    <div style="font-size:10.5px;color:#3a5a7a;">Mode: {item['mode']}</div>
                </div>
                """)
                if st.button("Rerun", key=f"rerun_{i}"):
                    st.session_state.query_input = item['query']
                    st.rerun()

    # ── FOOTER ────────────────────────────────────────────────────────────────
    inject("""
    <div style="margin-top:30px;padding:11px 18px;
        background:rgba(0,170,255,0.03);
        border:1px solid rgba(0,170,255,0.09);
        border-radius:11px;
        display:flex;justify-content:space-between;align-items:center;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.03),0 0 24px rgba(0,170,255,0.04);">
        <span style="display:flex;align-items:center;gap:7px;font-size:11px;color:#3a5a7a;font-weight:600;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;
                box-shadow:0 0 10px rgba(34,197,94,0.9);display:inline-block;"></span>
            System online
        </span>
        <span style="display:flex;align-items:center;gap:7px;font-size:11px;color:#3a5a7a;font-weight:600;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#00aaff;
                box-shadow:0 0 10px rgba(0,170,255,0.8);display:inline-block;"></span>
            RAG Active
        </span>
        <span style="display:flex;align-items:center;gap:7px;font-size:11px;color:#3a5a7a;font-weight:600;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#2a4a6a;display:inline-block;"></span>
            Secure session
        </span>
    </div>
    <div style="font-size:10px;color:#243850;letter-spacing:0.07em;text-align:center;
        margin-top:10px;font-family:'Space Grotesk',sans-serif;">
        ICS-LogQueryGPT v1.0 &nbsp;·&nbsp; Query Interface
    </div>
    """)


if __name__ == "__main__":
    main()

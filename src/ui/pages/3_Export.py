# Export Page

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

#  Page path helper 
PAGE_HOME  = "app.py"
PAGE_QUERY = "pages/1_Query_Logs.py"
PAGE_ANALYTICS = "pages/2_Analytics.py"
PAGE_LOGIN = "pages/0_Login.py"

def check_authentication():
    if not st.session_state.get('authenticated', False):
        st.switch_page(PAGE_LOGIN)
        st.stop()
    if st.session_state.get('session_token') == "admin-session":
        return
    session_manager = SessionManager()
    if not session_manager.validate_session(st.session_state.get('session_token')):
        st.session_state.clear()
        st.switch_page(PAGE_LOGIN)
        st.stop()

def logout_user():
    st.session_state.clear()

st.set_page_config(
    page_title="Export — ICS-LogQueryGPT",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
        background: #060d1f !important;
        color: #a0c0dc !important;
    }
    .stApp { background: #060d1f !important; }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #060d1f; }
    ::-webkit-scrollbar-thumb { background: rgba(0,170,255,0.3); border-radius: 2px; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080f22 0%, #060d1f 100%) !important;
        border-right: 1px solid rgba(0,170,255,0.10) !important;
    }
    [data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }
    section[data-testid="stSidebarNav"],
    [data-testid="stSidebarNavLink"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarHeader"],
    div[data-testid="stSidebarCollapseButton"],
    button[data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    span[data-testid="stIconMaterial"] { display: none !important; }

    [data-testid="stSidebar"] a {
        color: #6a8aaa !important; font-weight: 500 !important;
        text-decoration: none !important; font-size: 13px !important;
    }
    [data-testid="stSidebar"] a:hover { color: #a0c8e8 !important; }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #5a7a9a !important; font-size: 10px !important;
        font-weight: 800 !important; text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
        background: rgba(0,170,255,0.06) !important;
        border: 1px solid rgba(0,170,255,0.18) !important;
        border-radius: 8px !important; color: #a0c0dc !important; font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #6a8aaa !important; font-size: 12px !important; font-weight: 600 !important;
        text-transform: none !important; letter-spacing: normal !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(0,170,255,0.08) !important;
        border: 1px solid rgba(0,170,255,0.22) !important;
        color: #8ab0cc !important; font-weight: 600 !important; font-size: 12px !important;
        border-radius: 8px !important; width: 100% !important; transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0,170,255,0.15) !important; color: #c0ddf0 !important;
        border-color: rgba(0,170,255,0.4) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, rgba(0,170,255,0.18), rgba(0,100,220,0.22)) !important;
        border: 1px solid rgba(0,170,255,0.35) !important; color: #a0c8e8 !important;
        font-weight: 700 !important; font-size: 13px !important; border-radius: 10px !important;
        padding: 10px 24px !important; transition: all 0.2s ease !important;
        font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0.03em !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0,170,255,0.28), rgba(0,120,240,0.32)) !important;
        border-color: rgba(0,170,255,0.55) !important; color: #c0ddf0 !important;
        box-shadow: 0 0 18px rgba(0,170,255,0.25) !important; transform: translateY(-1px) !important;
    }

    .stSelectbox label {
        color: #5a7a9a !important; font-weight: 800 !important; font-size: 10px !important;
        text-transform: uppercase !important; letter-spacing: 0.12em !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(0,170,255,0.06) !important; border: 1px solid rgba(0,170,255,0.18) !important;
        color: #a0c0dc !important; font-weight: 600 !important; border-radius: 8px !important;
    }
    .stCheckbox label { color: #6a8aaa !important; font-weight: 600 !important; font-size: 13px !important; }

    .stTextInput label {
        color: #5a7a9a !important; font-weight: 800 !important; font-size: 10px !important;
        text-transform: uppercase !important; letter-spacing: 0.12em !important;
    }
    .stTextInput input {
        background: rgba(0,170,255,0.05) !important; border: 1px solid rgba(0,170,255,0.18) !important;
        color: #a0c0dc !important; font-weight: 600 !important; border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    .stTextInput input::placeholder { color: #2e4f70 !important; }
    .stTextInput input:focus {
        border-color: rgba(0,170,255,0.4) !important;
        box-shadow: 0 0 0 3px rgba(0,170,255,0.06) !important;
    }

    .stTimeInput label {
        color: #5a7a9a !important; font-weight: 800 !important; font-size: 10px !important;
        text-transform: uppercase !important; letter-spacing: 0.12em !important;
    }
    .stTimeInput input {
        background: rgba(0,170,255,0.05) !important; border: 1px solid rgba(0,170,255,0.18) !important;
        color: #a0c0dc !important; font-weight: 600 !important; border-radius: 8px !important;
    }

    .stDataFrame { border: 1px solid rgba(0,170,255,0.15) !important; border-radius: 10px !important; overflow: hidden !important; }
    .stDataFrame thead tr th {
        background: rgba(0,20,50,0.95) !important; color: #c0ddf0 !important;
        font-weight: 800 !important; font-size: 11px !important;
        text-transform: uppercase !important; letter-spacing: 0.1em !important;
        border-bottom: 1px solid rgba(0,170,255,0.2) !important;
    }
    .stDataFrame tbody tr:nth-child(even) td { background: rgba(0,170,255,0.025) !important; }
    .stDataFrame tbody tr td {
        color: #a0bfd8 !important; font-size: 12.5px !important; font-weight: 500 !important;
        border-bottom: 1px solid rgba(0,170,255,0.06) !important;
    }
    .stDataFrame tbody tr:hover td { background: rgba(0,170,255,0.06) !important; }

    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, rgba(0,130,220,0.22), rgba(0,80,180,0.26)) !important;
        border: 1px solid rgba(0,170,255,0.38) !important; color: #c8e8ff !important;
        font-weight: 800 !important; font-size: 14px !important; border-radius: 11px !important;
        padding: 14px 28px !important; width: 100% !important;
        box-shadow: 0 2px 12px rgba(0,170,255,0.12) !important;
        transition: all 0.2s ease !important; letter-spacing: 0.05em !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, rgba(0,150,230,0.30), rgba(0,100,200,0.34)) !important;
        border-color: rgba(0,170,255,0.55) !important;
        box-shadow: 0 4px 20px rgba(0,170,255,0.22) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stMetricValue"] { color: #c0ddf0 !important; font-weight: 800 !important; font-size: 1.6rem !important; }
    [data-testid="stMetricLabel"] {
        color: #6a8aaa !important; font-weight: 800 !important; font-size: 10px !important;
        text-transform: uppercase !important; letter-spacing: 0.1em !important;
    }
    [data-testid="stMetricDelta"] { font-weight: 600 !important; font-size: 12px !important; }

    .stSuccess { background: rgba(0,255,136,0.08) !important; border: 1px solid rgba(0,255,136,0.25) !important; color: #00e87a !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stWarning { background: rgba(255,170,0,0.08) !important; border: 1px solid rgba(255,170,0,0.25) !important; color: #ffb300 !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stInfo    { background: rgba(0,170,255,0.08) !important; border: 1px solid rgba(0,170,255,0.25) !important; color: #5ab8ff !important; border-radius: 8px !important; font-weight: 600 !important; }

    hr { border-color: rgba(0,170,255,0.1) !important; margin: 16px 0 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding: 1.5rem 2rem 4rem 2rem !important; max-width: 1400px !important; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 0 22px;border-bottom:1px solid rgba(0,170,255,0.12);margin-bottom:20px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:linear-gradient(135deg,rgba(0,170,255,0.25),rgba(0,80,200,0.3));
                    border:1px solid rgba(0,170,255,0.35);border-radius:10px;display:flex;align-items:center;
                    justify-content:center;font-size:18px;"></div>
                <div>
                    <div style="font-size:13.5px;font-weight:700;letter-spacing:-0.4px;background:linear-gradient(135deg,#fff 30%,#00aaff 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">ICS-LogQueryGPT</div>
                    <div style="font-size:9.5px;color:#3a6090;letter-spacing:0.1em;text-transform:uppercase;">Security Intelligence</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:9px;font-weight:700;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)
        if st.button("Home", use_container_width=True, key="sidebar_home"):
            st.switch_page(PAGE_HOME)
        if st.button("Query Logs", use_container_width=True, key="sidebar_query"):
            st.switch_page(PAGE_QUERY)
        if st.button("Analytics", use_container_width=True, key="sidebar_analytics"):
            st.switch_page(PAGE_ANALYTICS)

        st.markdown("<hr style='border-color:rgba(0,170,255,0.1);margin:12px 0;'>", unsafe_allow_html=True)

        st.markdown('<div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:10px;">Export Format</div>', unsafe_allow_html=True)
        export_format = st.selectbox("Format", ["CSV (.csv)","JSON (.json)","Markdown (.md)","Plain Text (.txt)"], label_visibility="collapsed")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:10px;">Include In Export</div>', unsafe_allow_html=True)
        inc_meta = st.checkbox("Metadata",       value=True)
        inc_ts   = st.checkbox("Timestamps",     value=True)
        inc_src  = st.checkbox("Source IPs",     value=True)
        inc_sev  = st.checkbox("Severity Levels",value=True)

        st.markdown("<hr style='border-color:rgba(0,170,255,0.1);margin:12px 0;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:10px;">Data Source</div>', unsafe_allow_html=True)
        data_source = st.radio("Source", ["All Logs","Filtered Logs","Query Results","Alerts Only"], label_visibility="collapsed")

        st.markdown("<hr style='border-color:rgba(0,170,255,0.1);margin:12px 0;'>", unsafe_allow_html=True)



        st.markdown("<hr style='border-color:rgba(0,170,255,0.1);margin:12px 0;'>", unsafe_allow_html=True)

        _username = st.session_state.get('username', 'user')
        _role     = st.session_state.get('user_role', 'analyst').lower()
        _all_roles = [('Admin','admin'), ('Analyst','analyst'), ('Read-Only','viewer')]
        _rows_html = ""
        for label, key in _all_roles:
            is_active = (_role == key)
            if is_active:
                _rows_html += f'''<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(0,170,255,0.09);border:1px solid rgba(0,170,255,0.25);border-radius:7px;padding:6px 10px;margin-bottom:5px;"><div style="display:flex;align-items:center;gap:7px;"><span style="width:6px;height:6px;border-radius:50%;background:#00aaff;box-shadow:0 0 8px rgba(0,170,255,0.8);display:inline-block;"></span><span style="font-size:11.5px;font-weight:600;color:#a0c8e8;">{label}</span></div><span style="font-size:9px;background:rgba(0,170,255,0.15);border:1px solid rgba(0,170,255,0.3);border-radius:4px;padding:1px 6px;color:#00aaff;font-weight:700;">ACTIVE</span></div>'''
            else:
                _rows_html += f'''<div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.055);border-radius:7px;padding:6px 10px;margin-bottom:5px;"><span style="width:6px;height:6px;border-radius:50%;background:#2a4a6a;display:inline-block;"></span><span style="font-size:11.5px;font-weight:500;color:#4a6a8a;">{label}</span></div>'''
        st.markdown(f"""
        <div style="font-size:10px;color:#5a8ab0;margin:10px 2px 10px;">
            Logged in as: <span style="color:#8ab0d0;font-weight:700;">{_username}</span>
        </div>
        <div style="font-size:9px;font-weight:700;color:#3a5a7a;text-transform:uppercase;
            letter-spacing:0.15em;margin-bottom:8px;">Access Roles</div>
        <div style="margin-bottom:12px;">{_rows_html}</div>
        """, unsafe_allow_html=True)



        st.markdown("---")
        if st.button("Logout", use_container_width=True, key="nav_logout"):
            st.session_state.clear()
            st.switch_page(PAGE_LOGIN)

    return export_format, inc_meta, inc_ts, inc_src, inc_sev, data_source


def render_page_header():
    st.markdown("""
    <style>
    @keyframes shimmer { 0%{background-position:-400px 0;} 100%{background-position:400px 0;} }
    @keyframes blink   { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
    @keyframes float1  { 0%,100%{transform:translateY(0)scale(1);} 50%{transform:translateY(-28px)scale(1.04);} }
    @keyframes float2  { 0%,100%{transform:translateY(0)scale(1);} 50%{transform:translateY(22px)scale(0.96);} }
    @keyframes fadeUp  { from{opacity:0;transform:translateY(14px);} to{opacity:1;transform:translateY(0);} }
    </style>
    <div style="position:relative;overflow:visible;padding:0 0 28px 0;margin-bottom:4px;">
        <div style="position:absolute;top:-60px;right:10%;width:300px;height:300px;
            background:radial-gradient(circle,rgba(0,170,255,.06) 0%,transparent 70%);
            border-radius:50%;pointer-events:none;animation:float1 11s ease-in-out infinite;"></div>
        <div style="position:absolute;top:-30px;right:38%;width:180px;height:180px;
            background:radial-gradient(circle,rgba(0,80,200,.05) 0%,transparent 70%);
            border-radius:50%;pointer-events:none;animation:float2 14s ease-in-out infinite;"></div>
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;animation:fadeUp .6s ease forwards;">
            <span style="font-size:36px;font-weight:900;color:#fff;letter-spacing:-.02em;line-height:1;">Export</span>
            <span style="font-size:36px;font-weight:900;letter-spacing:-.02em;line-height:1;
                background:linear-gradient(90deg,#00aaff,#0066ff,#00aaff,#40c8ff);background-size:400px 100%;
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                animation:shimmer 3.5s linear infinite;">Center</span>
            <div style="display:flex;align-items:center;gap:5px;background:rgba(0,255,136,.10);
                border:1px solid rgba(0,255,136,.28);border-radius:20px;padding:4px 10px;margin-left:6px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#00ff88;animation:blink 1.5s ease infinite;"></span>
                <span style="font-size:10px;font-weight:800;color:#00cc6a;letter-spacing:.1em;text-transform:uppercase;">Ready</span>
            </div>
        </div>
        <div style="font-size:13px;font-weight:500;color:#6a8aaa;animation:fadeUp .6s ease .15s both;max-width:520px;">
            Download filtered log data, schedule automated exports, and manage export templates.
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_sample_data():
    return pd.DataFrame({
        "Timestamp": ["2024-01-15 08:23:11","2024-01-15 09:14:52","2024-01-15 10:05:33",
                      "2024-01-15 11:22:07","2024-01-15 12:48:19","2024-01-15 13:31:44",
                      "2024-01-15 14:17:28","2024-01-15 15:09:55","2024-01-15 16:42:01","2024-01-15 17:58:39"],
        "Source IP": ["192.168.1.101","10.0.0.45","172.16.0.12","192.168.1.205",
                      "10.0.0.88","172.16.0.77","192.168.2.14","10.0.1.33","172.16.1.9","192.168.1.55"],
        "Protocol": ["SSH","HTTP","MODBUS","SSH","FTP","HTTPS","MODBUS","SSH","HTTP","DNSP3"],
        "Event":    ["Login attempt","GET /api/data","Register read","Auth failure",
                     "File transfer","POST /upload","Coil write","Session start","GET /status","Data poll"],
        "Severity": ["HIGH","LOW","MEDIUM","CRITICAL","MEDIUM","LOW","HIGH","LOW","LOW","MEDIUM"],
        "Status":   ["BLOCKED","ALLOWED","ALLOWED","BLOCKED","ALLOWED","ALLOWED","FLAGGED","ALLOWED","ALLOWED","ALLOWED"],
    })


def render_preview_and_export(df, export_format, inc_ts, inc_src, inc_sev, feed_label="Your Data"):
    col_left, col_right = st.columns([3, 2], gap="large")
    total = len(df)

    with col_left:
        st.markdown(f"""
        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;"> Data Preview</div>
        <div style="background:rgba(0,15,45,0.65);border:1px solid rgba(0,170,255,0.18);border-radius:12px;overflow:hidden;margin-bottom:14px;">
            <div style="display:flex;align-items:center;justify-content:space-between;
                padding:10px 14px 8px;border-bottom:1px solid rgba(0,170,255,0.12);background:rgba(0,25,55,0.8);">
                <span style="font-size:11px;font-weight:700;color:#7aa0c0;">{feed_label}</span>
                <span style="font-size:10px;font-weight:700;color:#3a5a7a;background:rgba(0,170,255,0.08);
                    border:1px solid rgba(0,170,255,0.15);border-radius:4px;padding:2px 8px;">{total} records</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show all available columns
        display_cols = list(df.columns)
        if not inc_ts:  display_cols = [c for c in display_cols if c.lower() not in ["timestamp","time","login time"]]
        if not inc_src: display_cols = [c for c in display_cols if c.lower() not in ["source ip","source"]]
        if not inc_sev: display_cols = [c for c in display_cols if c.lower() not in ["severity"]]
        display_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(df[display_cols], use_container_width=True, height=260, hide_index=True)

        fmt_name = export_format.split("(")[0].strip()
        # Stats based on actual columns available
        has_severity = "Severity" in df.columns
        has_status   = "Status" in df.columns
        critical = len(df[df["Severity"] == "CRITICAL"]) if has_severity else 0
        blocked  = len(df[df["Status"]   == "BLOCKED"])  if has_status  else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Records", f"{total:,}")
        with m2:
            if has_severity:
                st.metric("Critical Events", critical)
            else:
                st.metric("Datasets Used", len(set(df.get("Source", df.get("source", pd.Series(["N/A"]))).tolist())) if "Source" in df.columns or "source" in df.columns else "N/A")
        with m3:
            if has_status:
                st.metric("Blocked", blocked)
            else:
                st.metric("Queries", total)
        with m4: st.metric("Format", fmt_name)

    with col_right:
        fmt_clean = export_format.split("(")[0].strip()
        ext_map   = {"CSV":"csv","JSON":"json","Markdown":"md","Plain Text":"txt"}
        ext       = ext_map.get(fmt_clean, "csv")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename  = f"ics_logs_{timestamp}.{ext}"
        size_kb   = round(total * (0.8 if ext == "csv" else 1.4), 1)
        num_cols  = len(display_cols)

        st.markdown(f"""
        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;"> Export Options</div>
        <div style="background:rgba(0,15,45,0.65);border:1px solid rgba(0,170,255,0.22);border-radius:14px;padding:20px;margin-bottom:14px;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
                <div style="background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.15);border-radius:9px;padding:12px 14px;">
                    <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">Records</div>
                    <div style="font-size:22px;font-weight:800;color:#c0ddf0;">{total:,}</div>
                </div>
                <div style="background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.15);border-radius:9px;padding:12px 14px;">
                    <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">Est. Size</div>
                    <div style="font-size:22px;font-weight:800;color:#c0ddf0;">{size_kb} KB</div>
                </div>
                <div style="background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.15);border-radius:9px;padding:12px 14px;">
                    <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">Format</div>
                    <div style="font-size:20px;font-weight:800;color:#00aaff;">{fmt_clean}</div>
                </div>
                <div style="background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.15);border-radius:9px;padding:12px 14px;">
                    <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">Columns</div>
                    <div style="font-size:22px;font-weight:800;color:#c0ddf0;">{num_cols}</div>
                </div>
            </div>
            <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px;">Output Filename</div>
            <div style="background:rgba(0,0,0,.4);border:1px solid rgba(0,170,255,.2);border-radius:7px;
                padding:9px 12px;font-family:monospace;font-size:11px;color:#00aaff;font-weight:600;
                letter-spacing:.03em;word-break:break-all;">{filename}</div>
        </div>
        """, unsafe_allow_html=True)

        if fmt_clean == "CSV":
            export_data = df[display_cols].to_csv(index=False).encode("utf-8")
            mime = "text/csv"
        elif fmt_clean == "JSON":
            export_data = df[display_cols].to_json(orient="records", indent=2).encode("utf-8")
            mime = "application/json"
        elif fmt_clean == "Markdown":
            export_data = df[display_cols].to_markdown(index=False).encode("utf-8")
            mime = "text/markdown"
        else:
            export_data = df[display_cols].to_string(index=False).encode("utf-8")
            mime = "text/plain"

        clicked = st.download_button(
            label=f"Download {fmt_clean}",
            data=export_data,
            file_name=filename,
            mime=mime,
            use_container_width=True,
            key="main_download",
        )
        if clicked:
            if "export_history" not in st.session_state:
                st.session_state.export_history = []
            st.session_state.export_history.append({
                "Date":    datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Format":  fmt_clean,
                "Records": total,
                "Size":    f"{size_kb} KB",
                "Trigger": "Manual",
                "Status":  "SUCCESS",
            })


def render_templates():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;">Export Templates</div>', unsafe_allow_html=True)

    query_history = st.session_state.get("query_history", [])
    current = st.session_state.get("current_results", {})

    # Build real data from session for templates
    def get_template_df(template_type):
        if not query_history:
            return pd.DataFrame(), 0
        rows = []
        for q in query_history:
            row = {
                "Timestamp":     q.get("timestamp", ""),
                "Query":         q.get("query", ""),
                "Source":        q.get("source", q.get("protocol", "")),
                "Mode":          q.get("mode", ""),
                "Response Time": current.get("response_time","") if q == query_history[-1] and current else "",
            }
            if template_type == "security" and current and q == query_history[-1]:
                row["Answer"] = current.get("answer","")[:300]
            elif template_type == "traffic":
                row.pop("Response Time", None)
            elif template_type == "incident":
                row["Logs Analyzed"] = current.get("log_count","") if q == query_history[-1] and current else ""
            rows.append(row)
        df = pd.DataFrame(rows)
        return df, len(df)

    templates = [
        {
            "name": "Security Report",
            "desc": "All queries with AI answers — ideal for security incident documentation.",
            "fields": "Timestamp, Query, Source, Answer",
            "accent": "#ff4444",
            "type": "security",
        },
        {
            "name": "Traffic Analysis",
            "desc": "Query timeline with dataset sources and modes used.",
            "fields": "Timestamp, Query, Source, Mode",
            "accent": "#00aaff",
            "type": "traffic",
        },
        {
            "name": "Incident Report",
            "desc": "Full query log with response times and logs analyzed count.",
            "fields": "Timestamp, Query, Source, Response Time, Logs Analyzed",
            "accent": "#ffaa00",
            "type": "incident",
        },
    ]

    cols = st.columns(3, gap="medium")
    for col, t in zip(cols, templates):
        with col:
            df_tmpl, count = get_template_df(t["type"])
            records_label = f"{count} records" if count > 0 else "No queries yet"
            st.markdown(f"""
            <div style="background:rgba(0,12,35,0.7);border:1px solid rgba(255,255,255,.07);
                border-radius:13px;overflow:hidden;">
                <div style="height:4px;background:linear-gradient(90deg,{t['accent']},transparent);"></div>
                <div style="padding:16px 18px;">
                    <div style="font-size:13.5px;font-weight:800;color:#c0ddf0;margin-bottom:8px;">{t['name']}</div>
                    <div style="font-size:12px;font-weight:500;color:#6a8aaa;line-height:1.5;margin-bottom:12px;">{t['desc']}</div>
                    <div style="font-size:10px;font-weight:700;color:#3a5a7a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Fields</div>
                    <div style="font-size:11px;font-weight:600;color:#5a7a9a;margin-bottom:10px;">{t['fields']}</div>
                    <div style="display:inline-block;font-size:10px;font-weight:700;color:{t['accent']};
                        background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
                        border-radius:5px;padding:2px 8px;">{records_label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if count > 0:
                # Make Use Template actually download the right data
                csv_data = df_tmpl.to_csv(index=False).encode("utf-8")
                fname = f"ics_{t['type']}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                st.download_button(
                    label="Use Template",
                    data=csv_data,
                    file_name=fname,
                    mime="text/csv",
                    key=f"tmpl_{t['type']}",
                    use_container_width=True
                )
            else:
                st.button("Use Template — run queries first", key=f"tmpl_{t['type']}_empty",
                          use_container_width=True, disabled=True)


def render_scheduled_exports():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;">⏰ Scheduled Exports</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2], gap="large")

    with col_a:
        st.markdown("""
        <div style="background:rgba(0,12,35,0.7);border:1px solid rgba(255,255,255,.07);border-radius:13px;padding:22px 22px 8px;">
            <div style="font-size:12px;font-weight:700;color:#a0c0dc;margin-bottom:18px;display:flex;align-items:center;gap:8px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#3a5a7a;display:inline-block;"></span>
                Configure a recurring automated export
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: frequency    = st.selectbox("Frequency", ["Daily","Weekly","Monthly","Every 6 Hours"], key="sched_freq")
        with c2: export_time  = st.time_input("Time (UTC)", value=None, key="sched_time")
        sched_format = st.selectbox("Export Format", ["CSV (.csv)","JSON (.json)","Markdown (.md)"], key="sched_fmt")
        email        = st.text_input("Delivery Email", placeholder="security@company.com", key="sched_email")
        enabled      = st.checkbox("Enable scheduled export", value=False, key="sched_enable")
        if st.button("Save Schedule", key="save_schedule"):
            if enabled and not email:
                st.warning("Please enter a delivery email address.")
            else:
                st.session_state.sched_enabled_saved = enabled
                st.session_state.sched_saved = True
                if enabled and email:
                    st.success(f"Schedule saved — {frequency.lower()} export will be sent to {email}")
                else:
                    st.info("Schedule saved (disabled). Check the box to activate.")
                st.rerun()

    with col_b:
        # Read actual selections from session state
        sel_freq    = st.session_state.get("sched_freq", "Daily")
        sel_time    = st.session_state.get("sched_time", None)
        sel_fmt     = st.session_state.get("sched_fmt", "CSV (.csv)").split("(")[0].strip()
        sel_email   = st.session_state.get("sched_email", "")
        sel_enabled = st.session_state.get("sched_enabled_saved", False)
        sel_saved   = st.session_state.get("sched_saved", False)
        deliveries  = st.session_state.get("sched_deliveries", 0)
        last_export = st.session_state.get("sched_last_export", "Never")

        # Compute next run based on selections
        from datetime import datetime, timedelta
        now = datetime.now()
        if sel_time:
            next_run_str = f"Today {sel_time} UTC" if sel_time > now.time() else f"Tomorrow {sel_time} UTC"
        else:
            next_run_str = "Not set"

        status_color = "rgba(0,170,255,.12)', border:'1px solid rgba(0,170,255,.3)', color:'#00aaff" if sel_enabled else "rgba(255,170,0,.12)', border:'1px solid rgba(255,170,0,.3)', color:'#ffaa00"
        status_text  = "ACTIVE" if sel_enabled else "INACTIVE"
        status_bg    = "rgba(0,170,255,.12)" if sel_enabled else "rgba(255,170,0,.12)"
        status_border= "rgba(0,170,255,.3)"  if sel_enabled else "rgba(255,170,0,.3)"
        status_clr   = "#00aaff"             if sel_enabled else "#ffaa00"
        footer_msg   = "Schedule is active — exports will run automatically" if sel_enabled else "Schedule not yet active — toggle to enable"

        st.markdown(f"""
        <div style="background:rgba(0,170,255,.06);border:1px solid rgba(0,170,255,.18);border-radius:13px;padding:20px;">
            <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.15em;margin-bottom:8px;">Schedule Status</div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Status</span>
                <span style="font-size:11px;font-weight:700;background:{status_bg};border:1px solid {status_border};color:{status_clr};border-radius:5px;padding:2px 8px;">{status_text}</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Frequency</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">{sel_freq}</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Next Run</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">{next_run_str}</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Email</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">{sel_email if sel_email else "Not set"}</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Last Export</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">{last_export}</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Deliveries</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">{deliveries} sent</span>
            </div>
            <div style="padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Format</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">{sel_fmt}</span>
            </div>
            <div style="margin-top:8px;padding-top:12px;border-top:1px solid rgba(0,170,255,.07);
                font-size:10px;font-weight:600;color:#3a5a7a;display:flex;align-items:center;gap:6px;">
                <span style="width:5px;height:5px;border-radius:50%;background:{'#00aaff' if sel_enabled else '#3a5a7a'};display:inline-block;"></span>
                {footer_msg}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_export_history():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Track downloads in session state
    if "export_history" not in st.session_state:
        st.session_state.export_history = []

    history = st.session_state.export_history
    total_kb = sum(e.get("size_kb", 0) for e in history)

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;">Export History</div>
        <div style="font-size:11px;font-weight:600;color:#4a6a8a;background:rgba(0,170,255,0.06);
            border:1px solid rgba(0,170,255,0.12);border-radius:6px;padding:4px 12px;">
            {len(history)} exports this session · {round(total_kb,1)} KB total
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not history:
        st.info("No exports yet this session. Download a file above to see history here.")
    else:
        df_hist = pd.DataFrame(history)
        st.dataframe(
            df_hist,
            use_container_width=True,
            height=230,
            hide_index=True,
            column_config={
                "Date":    st.column_config.TextColumn("Date",    width="medium"),
                "Format":  st.column_config.TextColumn("Format",  width="small"),
                "Records": st.column_config.NumberColumn("Records", width="small"),
                "Size":    st.column_config.TextColumn("Size",    width="small"),
                "Trigger": st.column_config.TextColumn("Trigger", width="small"),
                "Status":  st.column_config.TextColumn("Status",  width="small"),
            }
        )


def render_footer():
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;right:0;z-index:999;
        background:rgba(6,13,31,0.96);backdrop-filter:blur(14px);
        border-top:1px solid rgba(0,170,255,0.10);
        padding:10px 32px;display:flex;align-items:center;gap:24px;">
        <div style="display:flex;align-items:center;gap:6px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#00ff88;box-shadow:0 0 8px rgba(0,255,136,.7);"></span>
            <span style="font-size:11px;font-weight:700;color:#7aa0c0;">System Online</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#00aaff;box-shadow:0 0 8px rgba(0,170,255,.7);"></span>
            <span style="font-size:11px;font-weight:700;color:#7aa0c0;">Export Ready</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#ffaa00;box-shadow:0 0 8px rgba(255,170,0,.7);"></span>
            <span style="font-size:11px;font-weight:700;color:#7aa0c0;">Secure Session</span>
        </div>
        <div style="margin-left:auto;font-size:10px;font-weight:600;color:#3a5a7a;">
            ICS-LogQueryGPT · Export Center · v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    check_authentication()
    inject_styles()

    export_format, inc_meta, inc_ts, inc_src, inc_sev, data_source = render_sidebar()
    render_page_header()

    query_history = st.session_state.get("query_history", [])
    current       = st.session_state.get("current_results", {})

    if query_history:
        # Build export from real query history
        rows = []
        for q in query_history:
            rows.append({
                "Timestamp":   q.get("timestamp", ""),
                "Query":       q.get("query", ""),
                "Source":      q.get("source", q.get("protocol", "")),
                "Mode":        q.get("mode", ""),
                "Response Time": str(current.get("response_time","")) if q == query_history[-1] and current else "",
                "Answer":      current.get("answer","")[:200] if q == query_history[-1] and current else "",
            })
        df = pd.DataFrame(rows)
        feed_label = f"Query History — {len(rows)} queries from this session"
    else:
        df = get_sample_data()
        feed_label = "Sample Data — run queries to export real results"

    render_preview_and_export(df, export_format, inc_ts, inc_src, inc_sev, feed_label)
    render_templates()
    render_scheduled_exports()
    render_export_history()
    render_footer()


if __name__ == "__main__":
    main()

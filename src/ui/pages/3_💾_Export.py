"""
Export page for ICS-LogQueryGPT
Redesigned to match Space Grotesk / #060d1f design system.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import check_authentication, get_current_user, logout_user

st.set_page_config(
    page_title="Export — ICS LogQuery GPT",
    page_icon="📤",
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
                    justify-content:center;font-size:18px;">🛡️</div>
                <div>
                    <div style="font-size:14px;font-weight:800;color:#c0ddf0;letter-spacing:0.04em;line-height:1.2;">ICS LogQuery</div>
                    <div style="font-size:10px;font-weight:600;color:#3a5a7a;letter-spacing:0.1em;text-transform:uppercase;">GPT Platform</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:10px;">Navigation</div>', unsafe_allow_html=True)
        for icon, label, active in [("🔍","Query Logs",False),("📊","Analytics",False),("📤","Export",True)]:
            if active:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:9px 12px;
                    background:rgba(0,170,255,0.12);border:1px solid rgba(0,170,255,0.28);
                    border-radius:8px;margin-bottom:4px;">
                    <span style="font-size:14px;">{icon}</span>
                    <span style="font-size:13px;font-weight:700;color:#a0c8e8;">{label}</span>
                    <span style="margin-left:auto;width:6px;height:6px;border-radius:50%;
                        background:#00aaff;box-shadow:0 0 8px rgba(0,170,255,0.8);"></span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;margin-bottom:4px;"
                    onmouseover="this.style.background='rgba(0,170,255,0.07)'"
                    onmouseout="this.style.background='transparent'">
                    <span style="font-size:14px;">{icon}</span>
                    <span style="font-size:13px;font-weight:500;color:#6a8aaa;">{label}</span>
                </div>""", unsafe_allow_html=True)

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

        username = st.session_state.get("username", "admin")
        st.markdown(f"""
        <div style="font-size:10px;font-weight:600;color:#7aa0c0;margin-bottom:10px;">
            Logged in as: <span style="color:#a0c8e8;">{username}</span>
        </div>
        <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:8px;">Access Roles</div>
        <div style="display:flex;flex-direction:column;gap:5px;margin-bottom:14px;">
            <div style="display:flex;align-items:center;justify-content:space-between;
                background:rgba(0,170,255,0.09);border:1px solid rgba(0,170,255,0.25);border-radius:7px;padding:6px 10px;">
                <div style="display:flex;align-items:center;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#00aaff;
                        box-shadow:0 0 8px rgba(0,170,255,0.8);display:inline-block;margin-right:7px;"></span>
                    <span style="font-size:11.5px;font-weight:700;color:#c0ddf0;">Admin</span>
                </div>
                <span style="font-size:9px;background:rgba(0,170,255,0.15);border:1px solid rgba(0,170,255,0.3);
                    border-radius:4px;padding:1px 6px;color:#00aaff;font-weight:800;letter-spacing:0.05em;">ACTIVE</span>
            </div>
            <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.018);
                border:1px solid rgba(255,255,255,0.055);border-radius:7px;padding:6px 10px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#2a4a6a;display:inline-block;"></span>
                <span style="font-size:11.5px;font-weight:600;color:#4a6a8a;">Security Operator</span>
            </div>
            <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.018);
                border:1px solid rgba(255,255,255,0.055);border-radius:7px;padding:6px 10px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#2a4a6a;display:inline-block;"></span>
                <span style="font-size:11.5px;font-weight:600;color:#4a6a8a;">Read-Only</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", key="logout_btn"):
            logout_user()
            st.rerun()

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


def render_preview_and_export(df, export_format, inc_ts, inc_src, inc_sev):
    col_left, col_right = st.columns([3, 2], gap="large")
    total = len(df)

    with col_left:
        st.markdown(f"""
        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;">📋 Data Preview</div>
        <div style="background:rgba(0,15,45,0.65);border:1px solid rgba(0,170,255,0.18);border-radius:12px;overflow:hidden;margin-bottom:14px;">
            <div style="display:flex;align-items:center;justify-content:space-between;
                padding:10px 14px 8px;border-bottom:1px solid rgba(0,170,255,0.12);background:rgba(0,25,55,0.8);">
                <span style="font-size:11px;font-weight:700;color:#7aa0c0;">Log Feed — Jan 15, 2024</span>
                <span style="font-size:10px;font-weight:700;color:#3a5a7a;background:rgba(0,170,255,0.08);
                    border:1px solid rgba(0,170,255,0.15);border-radius:4px;padding:2px 8px;">{total} records</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        display_cols = ["Timestamp","Source IP","Protocol","Event","Severity","Status"]
        if not inc_ts:  display_cols = [c for c in display_cols if c != "Timestamp"]
        if not inc_src: display_cols = [c for c in display_cols if c != "Source IP"]
        if not inc_sev: display_cols = [c for c in display_cols if c != "Severity"]

        st.dataframe(df[display_cols], use_container_width=True, height=260, hide_index=True)

        critical = len(df[df["Severity"] == "CRITICAL"])
        blocked  = len(df[df["Status"]   == "BLOCKED"])
        fmt_name = export_format.split("(")[0].strip()
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Records",  f"{total:,}")
        with m2: st.metric("Critical Events", critical, delta="↑ 2 new", delta_color="inverse")
        with m3: st.metric("Blocked",         blocked)
        with m4: st.metric("Format",          fmt_name)

    with col_right:
        fmt_clean = export_format.split("(")[0].strip()
        ext_map   = {"CSV":"csv","JSON":"json","Markdown":"md","Plain Text":"txt"}
        ext       = ext_map.get(fmt_clean, "csv")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename  = f"ics_logs_{timestamp}.{ext}"
        size_kb   = round(total * (0.8 if ext == "csv" else 1.4), 1)
        num_cols  = len(display_cols)

        st.markdown(f"""
        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;">📤 Export Options</div>
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

        st.download_button(
            label=f"⬇️  Download  {fmt_clean}",
            data=export_data,
            file_name=filename,
            mime=mime,
            use_container_width=True,
            key="main_download",
        )


def render_templates():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px;">⚡ Export Templates</div>', unsafe_allow_html=True)

    templates = [
        {"name":"Security Report",  "desc":"All CRITICAL and HIGH severity events with source IPs, protocols, and block status.",
         "fields":"Timestamp, Source IP, Protocol, Severity, Status","records":"~240 records","accent":"#ff4444","icon":"🛡️"},
        {"name":"Traffic Analysis", "desc":"Full protocol breakdown with event types. Ideal for network forensics investigations.",
         "fields":"Timestamp, Protocol, Event, Source IP","records":"~1,200 records","accent":"#00aaff","icon":"🌐"},
        {"name":"Incident Report",  "desc":"Blocked and flagged events only with full metadata for compliance filing.",
         "fields":"All fields + metadata","records":"~85 records","accent":"#ffaa00","icon":"⚠️"},
    ]

    cols = st.columns(3, gap="medium")
    for col, t in zip(cols, templates):
        with col:
            st.markdown(f"""
            <div style="background:rgba(0,12,35,0.7);border:1px solid rgba(255,255,255,.07);
                border-radius:13px;overflow:hidden;transition:border-color .2s,box-shadow .2s;cursor:pointer;"
                onmouseover="this.style.borderColor='rgba(0,170,255,.28)';this.style.boxShadow='0 4px 18px rgba(0,170,255,.09)'"
                onmouseout="this.style.borderColor='rgba(255,255,255,.07)';this.style.boxShadow='none'">
                <div style="height:4px;background:linear-gradient(90deg,{t['accent']},transparent);"></div>
                <div style="padding:16px 18px;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                        <span style="font-size:18px;">{t['icon']}</span>
                        <span style="font-size:13.5px;font-weight:800;color:#c0ddf0;">{t['name']}</span>
                    </div>
                    <div style="font-size:12px;font-weight:500;color:#6a8aaa;line-height:1.5;margin-bottom:12px;">{t['desc']}</div>
                    <div style="font-size:10px;font-weight:700;color:#3a5a7a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;">Fields</div>
                    <div style="font-size:11px;font-weight:600;color:#5a7a9a;margin-bottom:10px;">{t['fields']}</div>
                    <div style="display:inline-block;font-size:10px;font-weight:700;color:{t['accent']};
                        background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
                        border-radius:5px;padding:2px 8px;">{t['records']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Use Template", key=f"tmpl_{t['name']}", use_container_width=True)


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
        if st.button("💾  Save Schedule", key="save_schedule"):
            if enabled and email:
                st.success(f"✅ Scheduled {frequency.lower()} export → {email}")
            elif not email:
                st.warning("Please enter a delivery email address.")
            else:
                st.info("Schedule saved (disabled).")

    with col_b:
        st.markdown("""
        <div style="background:rgba(0,170,255,.06);border:1px solid rgba(0,170,255,.18);border-radius:13px;padding:20px;">
            <div style="font-size:9px;font-weight:800;color:#3a5a7a;text-transform:uppercase;letter-spacing:.15em;margin-bottom:8px;">Schedule Status</div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Status</span>
                <span style="font-size:11px;font-weight:700;background:rgba(255,170,0,.12);border:1px solid rgba(255,170,0,.3);color:#ffaa00;border-radius:5px;padding:2px 8px;">INACTIVE</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Frequency</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">Daily</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Next Run</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">Tomorrow 06:00 UTC</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Last Export</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">Never</span>
            </div>
            <div style="border-bottom:1px solid rgba(0,170,255,.07);padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Deliveries</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">0 sent</span>
            </div>
            <div style="padding:10px 0;display:flex;justify-content:space-between;">
                <span style="font-size:12px;font-weight:600;color:#5a7a9a;">Format</span>
                <span style="font-size:12px;font-weight:700;color:#8ab0cc;">CSV</span>
            </div>
            <div style="margin-top:8px;padding-top:12px;border-top:1px solid rgba(0,170,255,.07);
                font-size:10px;font-weight:600;color:#3a5a7a;display:flex;align-items:center;gap:6px;">
                <span style="width:5px;height:5px;border-radius:50%;background:#3a5a7a;display:inline-block;"></span>
                Schedule not yet active — toggle to enable
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_export_history():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;letter-spacing:.18em;">📁 Export History</div>
        <div style="font-size:11px;font-weight:600;color:#4a6a8a;background:rgba(0,170,255,0.06);
            border:1px solid rgba(0,170,255,0.12);border-radius:6px;padding:4px 12px;">
            5 exports · Last 7 days · 228 KB total
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_hist = pd.DataFrame({
        "Date":    ["2024-01-14 22:01","2024-01-13 06:00","2024-01-12 06:00","2024-01-11 06:00","2024-01-10 14:35"],
        "Format":  ["CSV","JSON","CSV","Markdown","CSV"],
        "Records": [1204, 856, 1100, 932, 740],
        "Size":    ["48 KB","71 KB","42 KB","38 KB","29 KB"],
        "Trigger": ["Manual","Auto","Auto","Auto","Manual"],
        "Status":  ["SUCCESS","SUCCESS","SUCCESS","SUCCESS","SUCCESS"],
    })
    st.dataframe(
        df_hist,
        use_container_width=True,
        height=230,
        hide_index=True,
        column_config={
            "Date":    st.column_config.TextColumn("Date",    width="medium"),
            "Format":  st.column_config.TextColumn("Format",  width="small"),
            "Records": st.column_config.NumberColumn("Records", width="small", format="%d"),
            "Size":    st.column_config.TextColumn("Size",    width="small"),
            "Trigger": st.column_config.TextColumn("Trigger", width="small"),
            "Status":  st.column_config.TextColumn("Status",  width="medium"),
        },
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
    # DEV BYPASS — remove before production
    st.session_state["authenticated"] = True
    st.session_state["session_token"] = "admin-session"
    st.session_state["username"]      = "admin"

    check_authentication()
    inject_styles()

    export_format, inc_meta, inc_ts, inc_src, inc_sev, data_source = render_sidebar()
    render_page_header()

    df = get_sample_data()

    render_preview_and_export(df, export_format, inc_ts, inc_src, inc_sev)
    render_templates()
    render_scheduled_exports()
    render_export_history()
    render_footer()


if __name__ == "__main__":
    main()
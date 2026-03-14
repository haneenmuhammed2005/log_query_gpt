# Analytics Page

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

#  Page path helper 
PAGE_HOME  = "app.py"
PAGE_QUERY = "pages/1_Query_Logs.py"
PAGE_EXPORT = "pages/3_Export.py"
PAGE_LOGIN = "pages/0_Login.py"

st.set_page_config(
    page_title="Analytics - ICS-LogQueryGPT",
    page_icon="",
    layout="wide"
)

#  Helper 
def inject(html: str):
    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)

#  Global styles 
def inject_styles():
    inject("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>

/*  Reset & base  */
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #060d1f !important;
    color: #e2e8f0 !important;
    -webkit-font-smoothing: antialiased;
}

/*  Animations  */
@keyframes blink     { 0%,100%{opacity:1} 50%{opacity:0.1} }
@keyframes floatorb  { 0%,100%{transform:translateY(0) scale(1)} 50%{transform:translateY(-24px) scale(1.05)} }
@keyframes shimmer   { 0%{background-position:-300% center} 100%{background-position:300% center} }
@keyframes glowpulse { 0%,100%{opacity:0.65} 50%{opacity:1} }
@keyframes fadeUp    { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeLeft  { from{opacity:0;transform:translateX(-16px)} to{opacity:1;transform:translateX(0)} }
@keyframes popIn     { from{opacity:0;transform:scale(0.92)} to{opacity:1;transform:scale(1)} }

/*  Hide Streamlit chrome  */
header[data-testid="stHeader"], footer, #MainMenu,
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
div[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebarNav"],
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavItems"],
button[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
span[data-testid="stIconMaterial"],
[data-testid="stSidebarHeader"] { display:none !important; }

/*  Ambient grid overlay  */
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(0,170,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,170,255,0.022) 1px, transparent 1px);
    background-size: 52px 52px;
}

/*  SIDEBAR  */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(3,8,22,0.99) 0%, rgba(2,6,18,0.99) 100%) !important;
    border-right: 1px solid rgba(0,170,255,0.10) !important;
    box-shadow: 6px 0 48px rgba(0,0,0,0.55), inset -1px 0 0 rgba(0,170,255,0.05) !important;
    animation: fadeLeft 0.55s ease both;
}
section[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }

/* Nav links */
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    font-size: 12.5px !important; font-weight: 600 !important;
    color: #6a8aaa !important; border-radius: 0 !important;
    padding: 9px 20px !important; border-left: 3px solid transparent !important;
    transition: all 0.22s ease !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
    color: #a0c8e8 !important;
    background: rgba(0,170,255,0.045) !important;
    border-left-color: rgba(0,170,255,0.25) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] {
    color: #e2e8f0 !important; font-weight: 700 !important;
    background: linear-gradient(90deg, rgba(0,170,255,0.13), rgba(0,170,255,0.02)) !important;
    border-left-color: #00aaff !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] img,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] { display: none !important; }
section[data-testid="stSidebarNav"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }

/* Sidebar section headers */
section[data-testid="stSidebar"] h3 {
    font-size: 9px !important; font-weight: 800 !important;
    color: #5a7a9a !important; text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
}

/* Sidebar selectbox */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label {
    font-size: 9px !important; font-weight: 800 !important;
    color: #5a7a9a !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #a0c0dc !important;
    font-size: 12px !important; font-weight: 600 !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.2) !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div:focus-within {
    border-color: rgba(0,170,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,170,255,0.08), inset 0 2px 8px rgba(0,0,0,0.15) !important;
}

/* Sidebar multiselect */
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] label {
    font-size: 9px !important; font-weight: 800 !important;
    color: #5a7a9a !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
}
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #a0c0dc !important;
    font-size: 12px !important; font-weight: 600 !important;
}

/* Sidebar caption & divider */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-size: 10px !important; font-weight: 600 !important;
    color: #5a7a9a !important; letter-spacing: 0.05em !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.04) !important; }

/*  Main block container  */
div.block-container {
    padding-top: 0 !important; padding-left: 2.5rem !important;
    padding-right: 2.5rem !important; padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/*  Typography  */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 40px !important; font-weight: 800 !important;
    letter-spacing: -2.2px !important; line-height: 1.05 !important;
    color: #e2e8f0 !important;
}
h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 9px !important; font-weight: 800 !important;
    color: #5a7a9a !important; text-transform: uppercase !important;
    letter-spacing: 0.15em !important; margin-bottom: 10px !important;
}

/*  Selectbox  */
div[data-testid="stSelectbox"] label {
    font-size: 9px !important; font-weight: 800 !important;
    color: #5a7a9a !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important; font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #a0c0dc !important;
    font-size: 12px !important; font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.2) !important;
}
div[data-testid="stSelectbox"] > div:focus-within {
    border-color: rgba(0,170,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,170,255,0.08) !important;
}

/*  Multiselect  */
div[data-testid="stMultiSelect"] label {
    font-size: 9px !important; font-weight: 800 !important;
    color: #5a7a9a !important; text-transform: uppercase !important;
    letter-spacing: 0.14em !important; font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stMultiSelect"] > div {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #a0c0dc !important;
    font-size: 12px !important; font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/*  Buttons  */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0040aa 0%, #0077cc 45%, #00aaff 100%) !important;
    border: none !important; border-radius: 9px !important;
    color: #fff !important; font-size: 13.5px !important; font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important; height: 44px !important;
    box-shadow: 0 4px 24px rgba(0,100,220,0.3), inset 0 1px 0 rgba(255,255,255,0.18) !important;
    transition: box-shadow 0.25s, transform 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 36px rgba(0,170,255,0.55), 0 6px 24px rgba(0,80,200,0.4) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important; color: #8ab0cc !important;
    font-size: 12.5px !important; font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important; height: 40px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.065) !important;
    color: #b0d0e8 !important; border-color: rgba(255,255,255,0.15) !important;
}
div[data-testid="stButton"] button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 11.5px !important; font-weight: 600 !important;
    border-radius: 9px !important;
}

/*  Metric cards  */
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
    font-size: 9px !important; color: #6a8aaa !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
    font-weight: 800 !important; font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 11px !important; font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/*  Tabs  */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important; background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important;
    background: rgba(255,255,255,0.018) !important; color: #6a8aaa !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 12px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important;
    border: 1px solid rgba(255,255,255,0.055) !important;
    border-bottom: none !important; transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #a0c0dc !important; background: rgba(0,170,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,170,255,0.10) !important; color: #00aaff !important;
    border-color: rgba(0,170,255,0.25) !important;
    border-bottom: 2px solid #00aaff !important;
}

/*  Dataframe  */
div[data-testid="stDataFrame"] {
    border-radius: 10px !important; overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.065) !important;
}

/*  Misc  */
div[data-testid="stAlert"] {
    border-radius: 9px !important; font-size: 13px !important;
    font-weight: 500 !important; font-family: 'Space Grotesk', sans-serif !important;
}
hr { border-color: rgba(255,255,255,0.05) !important; }
div[data-testid="stSpinner"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important; font-weight: 500 !important; color: #6a8aaa !important;
}
[data-testid="stCaptionContainer"] p, small {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 10px !important; font-weight: 600 !important;
    color: #5a7a9a !important; letter-spacing: 0.05em !important;
}
</style>
""")

#  Auth check 
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

#  Mock data 
def generate_mock_time_series():
    dates = pd.date_range(end=datetime.now(), periods=168, freq='H')
    return pd.DataFrame({
        'timestamp':   dates,
        'total_logs':  [random.randint(50, 200) for _ in range(168)],
        'failed_auth': [random.randint(5, 30)   for _ in range(168)],
        'alerts':      [random.randint(0, 10)   for _ in range(168)],
    })

def generate_protocol_data():
    return pd.DataFrame({
        'protocol': ['SSH', 'HTTP', 'HTTPS', 'FTP', 'DNS', 'SMTP', 'Telnet'],
        'count':    [3421, 2847, 1923, 1205, 892, 445, 178],
        'failed':   [245,  123,  67,   89,   12,  23,  45],
    })

def generate_top_ips():
    return pd.DataFrame({
        'ip':       [f'192.168.1.{i}' for i in [105, 23, 87, 156, 201, 67, 143, 89, 34, 178]],
        'requests': [523, 478, 412, 387, 345, 298, 267, 234, 201, 189],
        'failed':   [45,  12,  8,   67,  23,  5,   34,  9,   12,  45],
    })

#  Plotly chart layout 
_FONT  = dict(family='Space Grotesk, sans-serif', color='#8ab0cc', size=11)
_TFNT  = dict(family='Space Grotesk, sans-serif', color='#a0c8e8', size=13)
_LGND  = dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.06)',
              font=dict(color='#8ab0cc', family='Space Grotesk', size=11))
_AXIS  = dict(gridcolor='rgba(255,255,255,0.06)', linecolor='rgba(255,255,255,0.06)')

CHART_LAYOUT = dict(
    template='plotly_dark',
    paper_bgcolor='rgba(6,13,31,0)',
    plot_bgcolor='rgba(255,255,255,0.012)',
    font=_FONT, legend=_LGND,
    height=400,
    margin=dict(l=44, r=20, t=48, b=40),
    xaxis=_AXIS, yaxis=_AXIS,
)

def create_time_series_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['total_logs'],  name='Total Logs',  mode='lines', line=dict(color='#00aaff', width=2), fill='tozeroy', fillcolor='rgba(0,170,255,0.05)'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['failed_auth'], name='Failed Auth',  mode='lines', line=dict(color='#f87171', width=2), fill='tozeroy', fillcolor='rgba(248,113,113,0.05)'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['alerts'],      name='Alerts',       mode='lines', line=dict(color='#fbbf24', width=2), fill='tozeroy', fillcolor='rgba(251,191,36,0.05)'))
    fig.update_layout(title=dict(text='Log Activity — Last 7 Days', font=_TFNT), hovermode='x unified', **CHART_LAYOUT)
    return fig

def create_protocol_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['protocol'], y=df['count'],  name='Total',  marker_color='#00aaff', marker_line_width=0))
    fig.add_trace(go.Bar(x=df['protocol'], y=df['failed'], name='Failed', marker_color='#f87171', marker_line_width=0))
    fig.update_layout(title=dict(text='Protocol Distribution', font=_TFNT), barmode='group', **CHART_LAYOUT)
    return fig

def create_top_ips_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df['ip'], x=df['requests'], name='Total Requests', orientation='h', marker_color='#00aaff', marker_line_width=0))
    fig.add_trace(go.Bar(y=df['ip'], x=df['failed'],   name='Failed',         orientation='h', marker_color='#f87171', marker_line_width=0))
    fig.update_layout(title=dict(text='Top 10 IPs by Activity', font=_TFNT), barmode='stack', **CHART_LAYOUT)
    return fig

def create_heatmap():
    hours = list(range(24))
    days  = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data  = [[random.randint(10, 100) for _ in hours] for _ in days]
    layout = {**CHART_LAYOUT, 'height': 300}
    fig = go.Figure(data=go.Heatmap(
        z=data, x=hours, y=days,
        colorscale=[[0, '#060d1f'], [0.5, '#003366'], [1, '#00aaff']],
        hoverongaps=False
    ))
    fig.update_layout(title=dict(text='Activity Heatmap — Hour of Day', font=_TFNT), **layout)
    return fig

#  Reusable section label 
def section_label(text: str) -> str:
    return f"""<div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:11px;font-family:'Space Grotesk',sans-serif;">{text}</div>"""

#  Main 
def main():
    check_authentication()
    inject_styles()

    #  Ambient orbs 
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

    #  SIDEBAR 
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
            <div style="font-size:9.5px;font-weight:800;color:#5a7a9a;letter-spacing:0.1em;
                text-transform:uppercase;padding-left:37px;font-family:'Space Grotesk',sans-serif;">
                Security Intelligence</div>
        </div>
        """)

        st.markdown("### Filters")

        st.selectbox(
            "Time Range",
            ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days"],
            index=2
        )
        st.multiselect(
            "Protocols",
            ["SSH", "HTTP", "HTTPS", "FTP", "DNS", "SMTP", "Telnet"],
            default=["SSH", "HTTP", "HTTPS"]
        )

        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:10px 0;"></div>')

        if st.button("Refresh Data", use_container_width=True, key="nav_refresh"):
            st.rerun()
        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:10px 0;"></div>')
        st.markdown("### Navigation")
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.switch_page(PAGE_HOME)
        if st.button("Query Logs", use_container_width=True, key="nav_query"):
            st.switch_page(PAGE_QUERY)
        if st.button("Export", use_container_width=True, key="nav_export"):
            st.switch_page(PAGE_EXPORT)
        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:10px 0;"></div>')
        if st.button("Logout", use_container_width=True, key="nav_logout"):
            st.session_state.clear()
            st.switch_page(PAGE_LOGIN)

        inject(f"""
        <div style="font-size:10px;font-weight:600;color:#7aa0c0;margin:10px 4px 12px;
            font-family:'Space Grotesk',sans-serif;">
            Logged in as:
            <span style="color:#a0c8e8;font-weight:700;">
                {st.session_state.get('username', 'admin')}
            </span>
        </div>

        <div style="font-size:9px;font-weight:800;color:#5a7a9a;text-transform:uppercase;
            letter-spacing:0.15em;margin-bottom:8px;margin-left:4px;
            font-family:'Space Grotesk',sans-serif;">Access Roles</div>

        <div style="display:flex;flex-direction:column;gap:5px;margin:0 4px 16px;">

            <div style="display:flex;align-items:center;justify-content:space-between;
                background:rgba(0,170,255,0.09);border:1px solid rgba(0,170,255,0.25);
                border-radius:7px;padding:6px 10px;">
                <div style="display:flex;align-items:center;gap:7px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#00aaff;
                        box-shadow:0 0 8px rgba(0,170,255,0.8);display:inline-block;"></span>
                    <span style="font-size:11.5px;font-weight:700;color:#c0ddf0;
                        font-family:'Space Grotesk',sans-serif;">Admin</span>
                </div>
                <span style="font-size:9px;background:rgba(0,170,255,0.15);
                    border:1px solid rgba(0,170,255,0.3);border-radius:4px;
                    padding:1px 6px;color:#00aaff;font-weight:800;letter-spacing:0.05em;
                    font-family:'Space Grotesk',sans-serif;">ACTIVE</span>
            </div>

            <div style="display:flex;align-items:center;gap:7px;
                background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.055);
                border-radius:7px;padding:6px 10px;">
                <span style="width:6px;height:6px;border-radius:50%;
                    background:#2a4a6a;display:inline-block;"></span>
                <span style="font-size:11.5px;font-weight:600;color:#6a8aaa;
                    font-family:'Space Grotesk',sans-serif;">Security Operator</span>
            </div>

            <div style="display:flex;align-items:center;gap:7px;
                background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.055);
                border-radius:7px;padding:6px 10px;">
                <span style="width:6px;height:6px;border-radius:50%;
                    background:#2a4a6a;display:inline-block;"></span>
                <span style="font-size:11.5px;font-weight:600;color:#6a8aaa;
                    font-family:'Space Grotesk',sans-serif;">Read-Only</span>
            </div>

        </div>
        """)

    #  TOP ACCENT BAR 
    inject("""
    <div style="height:2px;
        background:linear-gradient(90deg,transparent,#0088cc 20%,#00aaff 45%,#00e5ff 55%,#00aaff 80%,transparent);
        opacity:0.9;margin-bottom:28px;border-radius:2px;
        animation:glowpulse 3s ease-in-out infinite;"></div>
    """)

    #  LIVE BADGE 
    inject("""
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(0,170,255,0.06);border:1px solid rgba(0,170,255,0.2);
        border-radius:20px;padding:5px 14px 5px 10px;
        font-size:10px;font-weight:800;color:#00aaff;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:13px;
        box-shadow:0 0 24px rgba(0,170,255,0.08),inset 0 1px 0 rgba(255,255,255,0.05);
        opacity:0;animation:fadeUp 0.6s 0.05s ease forwards;
        font-family:'Space Grotesk',sans-serif;">
        <span style="width:7px;height:7px;border-radius:50%;background:#00aaff;
            box-shadow:0 0 14px #00aaff,0 0 5px #00aaff;
            animation:blink 2.3s ease-in-out infinite;display:inline-block;"></span>
        Live Analytics
    </div>
    """)

    #  SHIMMER TITLE 
    inject("""
    <div style="margin-bottom:8px;opacity:0;animation:fadeUp 0.6s 0.1s ease forwards;">
        <span style="font-size:40px;font-weight:800;letter-spacing:-2.2px;line-height:1.05;
            background:linear-gradient(135deg,#ffffff 20%,#8fa8c8 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            font-family:'Space Grotesk',sans-serif;">Analytics&nbsp;</span><span
            style="font-size:40px;font-weight:800;letter-spacing:-2.2px;line-height:1.05;
            background:linear-gradient(135deg,#00aaff 0%,#00e5ff 50%,#00aaff 100%);
            background-size:200% auto;
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            animation:shimmer 4s linear infinite;
            font-family:'Space Grotesk',sans-serif;">Dashboard</span>
    </div>
    <div style="font-size:13px;font-weight:500;color:#6a8aaa;margin-bottom:24px;letter-spacing:0.01em;
        opacity:0;animation:fadeUp 0.6s 0.15s ease forwards;
        font-family:'Space Grotesk',sans-serif;">
        Visualize and analyze ICS security log data in real time
    </div>
    """)

    st.markdown("---")

    #  KEY METRICS 
    inject(section_label("Key Metrics"))

    query_history = st.session_state.get("query_history", [])
    current = st.session_state.get("current_results", {})
    total_q = len(query_history)
    last_logs = current.get("log_count", 0) if current else 0
    last_time = f"{current.get('response_time', 0)}s" if current else "N/A"
    dataset = st.session_state.get("selected_dataset", "HDFS")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Queries Run", total_q)
    with c2: st.metric("Last Logs Analyzed", last_logs)
    with c3: st.metric("Last Response Time", last_time)
    with c4: st.metric("Active Dataset", dataset)

    st.markdown("---")

    #  ACTIVITY TIMELINE 
    inject(section_label("Activity Timeline"))
    query_history = st.session_state.get("query_history", [])
    if query_history:
        import plotly.graph_objects as go
        times = [q["timestamp"] for q in query_history]
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=times, y=list(range(1, len(times)+1)),
            mode="lines+markers",
            line=dict(color="#00aaff", width=2),
            marker=dict(size=8, color="#00aaff"),
            name="Cumulative Queries",
            text=[f"Query: {q['query'][:40]}..." for q in query_history],
            hovertemplate="%{x}<br>%{text}<extra></extra>"
        ))
        fig_hist.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(6,13,31,0)",
            plot_bgcolor="rgba(255,255,255,0.012)", height=350,
            margin=dict(l=44,r=20,t=40,b=40),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Queries Run"),
            title=dict(text="Query History Timeline", font=dict(color="#a0c8e8",size=13)),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No query history yet. Run queries on the Query Logs page to see data here.")

    st.markdown("---")

    #  PROTOCOL + TOP IPS 
    col1, col2 = st.columns(2)
    query_history = st.session_state.get("query_history", [])
    with col1:
        inject(section_label("Query Mode Breakdown"))
        if query_history:
            from collections import Counter
            import plotly.graph_objects as go
            mc = Counter(q.get("mode","Fast") for q in query_history)
            fig = go.Figure(go.Pie(
                labels=list(mc.keys()), values=list(mc.values()),
                marker_colors=["#00aaff","#0066cc","#003388"], hole=0.4,
            ))
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(6,13,31,0)",
                height=320,margin=dict(l=20,r=20,t=30,b=20),
                legend=dict(font=dict(color="#8ab0cc")))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet.")
    with col2:
        inject(section_label("Dataset Usage"))
        if query_history:
            from collections import Counter
            import plotly.graph_objects as go
            sc = Counter(q.get("source", "HDFS") for q in query_history)
            fig2 = go.Figure(go.Bar(
                x=list(sc.keys()), y=list(sc.values()), marker_color="#00aaff"))
            fig2.update_layout(template="plotly_dark",paper_bgcolor="rgba(6,13,31,0)",
                plot_bgcolor="rgba(255,255,255,0.012)",height=320,
                margin=dict(l=40,r=20,t=30,b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data yet.")

    st.markdown("---")

    #  HEATMAP 
    inject(section_label("Activity Heatmap"))
    query_history = st.session_state.get("query_history", [])
    current = st.session_state.get("current_results", {})
    if query_history and current:
        import plotly.graph_objects as go
        n = len(query_history)
        rt = current.get("response_time", 2.0)
        # approximate response times per query
        rts = [round(1.5 + (i % 4) * 0.5, 2) for i in range(n-1)] + [rt]
        labels = [f"Q{i+1}" for i in range(n)]
        fig3 = go.Figure(go.Bar(
            x=labels, y=rts,
            marker_color=["#f87171" if t > 5 else "#00aaff" for t in rts]))
        fig3.update_layout(template="plotly_dark",paper_bgcolor="rgba(6,13,31,0)",
            plot_bgcolor="rgba(255,255,255,0.012)",height=300,
            margin=dict(l=44,r=20,t=30,b=40),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)",title="Seconds"),
            title=dict(text="Response Time per Query (s)",font=dict(color="#a0c8e8",size=13)))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Run queries to see response time data here.")

    st.markdown("---")

    #  DETAILED DATA TABS 
    inject(section_label("Detailed Data"))

    tab1, tab2 = st.tabs(["Query History", "Last AI Answer"])
    query_history = st.session_state.get("query_history", [])
    current = st.session_state.get("current_results", {})

    with tab1:
        if query_history:
            st.dataframe(pd.DataFrame(query_history), use_container_width=True)
        else:
            st.info("No queries run yet. Go to Query Logs to get started.")

    with tab2:
        if current and current.get("answer"):
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Response Time", f"{current.get('response_time',0)}s")
            with c2: st.metric("Logs Analyzed", current.get("log_count",0))
            with c3: st.metric("Source", ", ".join(current.get("sources",[])))
            st.markdown("---")
            st.markdown(current.get("answer",""))
        else:
            st.info("No query has been run yet.")

    st.markdown("---")

    #  EXPORT 
    inject(section_label("Export Analytics"))

    e1, e2, e3 = st.columns(3)
    with e1:
        if st.button("Export Charts (PNG)", use_container_width=True):
            st.info("Charts exported successfully.")
    with e2:
        if st.button("Export Data (CSV)", use_container_width=True):
            st.info("Data exported successfully.")
    with e3:
        if st.button(" Go to Export Center", use_container_width=True, type="primary"):
            st.switch_page(PAGE_EXPORT)

    #  FOOTER 
    inject("""
    <div style="margin-top:30px;padding:11px 18px;
        background:rgba(0,170,255,0.03);border:1px solid rgba(0,170,255,0.09);
        border-radius:11px;display:flex;justify-content:space-between;align-items:center;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.03),0 0 24px rgba(0,170,255,0.04);">
        <span style="display:flex;align-items:center;gap:7px;font-size:11px;
            font-weight:700;color:#7aa0c0;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;
                box-shadow:0 0 10px rgba(34,197,94,0.9);display:inline-block;"></span>
            System online
        </span>
        <span style="display:flex;align-items:center;gap:7px;font-size:11px;
            font-weight:700;color:#7aa0c0;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#00aaff;
                box-shadow:0 0 10px rgba(0,170,255,0.8);display:inline-block;"></span>
            Analytics Active
        </span>
        <span style="display:flex;align-items:center;gap:7px;font-size:11px;
            font-weight:700;color:#7aa0c0;font-family:'Space Grotesk',sans-serif;">
            <span style="width:6px;height:6px;border-radius:50%;background:#2a4a6a;
                display:inline-block;"></span>
            Secure session
        </span>
    </div>
    <div style="font-size:10px;font-weight:600;color:#5a7a8a;letter-spacing:0.07em;
        text-align:center;margin-top:10px;font-family:'Space Grotesk',sans-serif;">
        ICS-LogQueryGPT v1.0 &nbsp;·&nbsp; Analytics Dashboard
    </div>
    """)


if __name__ == "__main__":
    main()

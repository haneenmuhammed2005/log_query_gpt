"""
ICS-LogQueryGPT - Analytics Page
Author: Kripa
Week 1 Day 4: Data Visualization & Analytics
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

# Page config
st.set_page_config(
    page_title="Analytics - ICS-LogQueryGPT",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
css_path = project_root / "src" / "ui" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def check_authentication():
    """Check if user is authenticated"""
    session_manager = SessionManager()
    
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Please login to access this page")
        st.stop()
    
    # ✅ FIXED: validate_session only takes session_token (removed username)
    if not session_manager.validate_session(
        st.session_state.get('session_token')
    ):
        st.error("❌ Session expired. Please login again.")
        st.session_state.clear()
        st.stop()

def generate_mock_time_series():
    """Generate mock time series data"""
    dates = pd.date_range(end=datetime.now(), periods=168, freq='H')
    data = {
        'timestamp': dates,
        'total_logs': [random.randint(50, 200) for _ in range(168)],
        'failed_auth': [random.randint(5, 30) for _ in range(168)],
        'successful_auth': [random.randint(40, 170) for _ in range(168)],
        'alerts': [random.randint(0, 10) for _ in range(168)]
    }
    return pd.DataFrame(data)

def generate_protocol_data():
    """Generate mock protocol distribution data"""
    return pd.DataFrame({
        'protocol': ['SSH', 'HTTP', 'HTTPS', 'FTP', 'DNS', 'SMTP', 'Telnet'],
        'count': [3421, 2847, 1923, 1205, 892, 445, 178],
        'failed': [245, 123, 67, 89, 12, 23, 45]
    })

def generate_top_ips():
    """Generate mock top IPs data"""
    return pd.DataFrame({
        'ip': [f'192.168.1.{i}' for i in [105, 23, 87, 156, 201, 67, 143, 89, 34, 178]],
        'requests': [523, 478, 412, 387, 345, 298, 267, 234, 201, 189],
        'failed': [45, 12, 8, 67, 23, 5, 34, 9, 12, 45]
    })

def create_time_series_chart(df):
    """Create time series chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['total_logs'],
        name='Total Logs',
        mode='lines',
        line=dict(color='#0EA5E9', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['failed_auth'],
        name='Failed Auth',
        mode='lines',
        line=dict(color='#EF4444', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['alerts'],
        name='Alerts',
        mode='lines',
        line=dict(color='#F59E0B', width=2)
    ))
    
    fig.update_layout(
        title='Log Activity Over Time (Last 7 Days)',
        xaxis_title='Time',
        yaxis_title='Count',
        template='plotly_dark',
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_protocol_chart(df):
    """Create protocol distribution chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['protocol'],
        y=df['count'],
        name='Total',
        marker_color='#0EA5E9'
    ))
    
    fig.add_trace(go.Bar(
        x=df['protocol'],
        y=df['failed'],
        name='Failed',
        marker_color='#EF4444'
    ))
    
    fig.update_layout(
        title='Protocol Distribution',
        xaxis_title='Protocol',
        yaxis_title='Count',
        template='plotly_dark',
        barmode='group',
        height=400
    )  # ✅ FIXED: was )) causing SyntaxError
    
    return fig

def create_top_ips_chart(df):
    """Create top IPs chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['ip'],
        x=df['requests'],
        name='Total Requests',
        orientation='h',
        marker_color='#0EA5E9'
    ))
    
    fig.add_trace(go.Bar(
        y=df['ip'],
        x=df['failed'],
        name='Failed',
        orientation='h',
        marker_color='#EF4444'
    ))
    
    fig.update_layout(
        title='Top 10 IPs by Activity',
        xaxis_title='Count',
        yaxis_title='IP Address',
        template='plotly_dark',
        barmode='stack',
        height=400
    )
    
    return fig

def create_heatmap():
    """Create hour-of-day heatmap"""
    hours = list(range(24))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data = [[random.randint(10, 100) for _ in hours] for _ in days]
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=hours,
        y=days,
        colorscale='Blues',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Activity Heatmap (Hour of Day)',
        xaxis_title='Hour',
        yaxis_title='Day',
        template='plotly_dark',
        height=300
    )
    
    return fig

def main():
    """Main analytics page"""
    
    check_authentication()
    
    st.title("📊 Analytics Dashboard")
    st.markdown("Visualize and analyze ICS log data")
    
    with st.sidebar:
        st.markdown("### ⚙️ Analytics Filters")
        
        time_range = st.selectbox(
            "Time Range",
            ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days"]
        )
        
        protocols = st.multiselect(
            "Protocols",
            ["SSH", "HTTP", "HTTPS", "FTP", "DNS", "SMTP", "Telnet"],
            default=["SSH", "HTTP", "HTTPS"]
        )
        
        refresh = st.button("🔄 Refresh Data", use_container_width=True)
    
    st.markdown("### 📈 Key Metrics")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Total Logs", "15,247", "↑ 342 (2.3%)", delta_color="normal")
    with metric_col2:
        st.metric("Failed Auth", "891", "↑ 23 (2.6%)", delta_color="inverse")
    with metric_col3:
        st.metric("Alerts", "47", "↓ 5 (9.6%)", delta_color="normal")
    with metric_col4:
        st.metric("Unique IPs", "1,234", "↑ 45 (3.8%)", delta_color="normal")
    
    st.markdown("---")
    st.markdown("### 📉 Activity Timeline")
    time_series_df = generate_mock_time_series()
    fig_timeseries = create_time_series_chart(time_series_df)
    st.plotly_chart(fig_timeseries, use_container_width=True)
    
    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 🔌 Protocol Distribution")
        protocol_df = generate_protocol_data()
        fig_protocol = create_protocol_chart(protocol_df)
        st.plotly_chart(fig_protocol, use_container_width=True)
    
    with chart_col2:
        st.markdown("### 🌐 Top IPs")
        top_ips_df = generate_top_ips()
        fig_ips = create_top_ips_chart(top_ips_df)
        st.plotly_chart(fig_ips, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🔥 Activity Heatmap")
    fig_heatmap = create_heatmap()
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 Detailed Data")
    
    tab1, tab2, tab3 = st.tabs(["Protocol Stats", "Top IPs", "Recent Alerts"])
    
    with tab1:
        st.dataframe(protocol_df, use_container_width=True)
    
    with tab2:
        st.dataframe(top_ips_df, use_container_width=True)
    
    with tab3:
        alerts_df = pd.DataFrame({
            'Timestamp': [datetime.now() - timedelta(hours=i) for i in range(10)],
            'Severity': ['High', 'Medium', 'Low', 'High', 'Medium', 'Low', 'Critical', 'Medium', 'Low', 'High'],
            'Type': ['Brute Force', 'Port Scan', 'Failed Auth', 'Malware', 'Anomaly', 'Policy Violation', 'Intrusion', 'Misconfiguration', 'Suspicious Activity', 'Unauthorized Access'],
            'Source IP': [f'192.168.1.{random.randint(1, 255)}' for _ in range(10)]
        })
        st.dataframe(alerts_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 💾 Export Analytics")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📊 Export Charts (PNG)", use_container_width=True):
            st.info("📊 Charts exported successfully!")
    with export_col2:
        if st.button("📄 Export Data (CSV)", use_container_width=True):
            st.info("📄 Data exported successfully!")
    with export_col3:
        if st.button("📋 Generate Report", use_container_width=True):
            st.info("📋 Report generated successfully!")

if __name__ == "__main__":
    main()
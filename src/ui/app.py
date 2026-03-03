"""
ICS-LogQueryGPT Main Application
Author: Kripa
Week 1 Day 1: App Structure & Landing Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

# Page config
st.set_page_config(
    page_title="ICS-LogQueryGPT",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_authentication():
    """Check if user is authenticated"""
    session_manager = SessionManager()
    
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Please login to access the application")
        st.info("👉 Use the Login page from the sidebar")
        st.stop()
    
    # Validate session
    if not session_manager.validate_session(
        st.session_state.get('session_token'),
        st.session_state.get('username')
    ):
        st.error("❌ Session expired. Please login again.")
        st.session_state.clear()
        st.stop()

def main():
    """Main application landing page"""
    
    # Check authentication
    check_authentication()
    
    # Get user info
    username = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'user')
    
    # Header
    st.title("🔍 ICS-LogQueryGPT")
    st.markdown("### AI-Powered Industrial Control System Log Analysis")
    
    # Welcome section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ## Welcome back, **{username}**! 👋
        
        Your intelligent assistant for analyzing ICS security logs with natural language queries.
        """)
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Total Logs", "15,247", "↑ 342")
        
        with metric_col2:
            st.metric("Queries Today", "23", "↑ 5")
        
        with metric_col3:
            st.metric("Cache Hit Rate", "73%", "↑ 8%")
        
        with metric_col4:
            st.metric("Avg Response", "2.3s", "↓ 0.5s")
    
    with col2:
        st.info(f"""
        **User Info**
        - **Username**: {username}
        - **Role**: {user_role.title()}
        - **Session**: Active ✅
        """)
    
    # Feature cards
    st.markdown("---")
    st.markdown("### 🚀 Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        #### 🔍 Query Logs
        Ask questions in natural language and get AI-powered insights from your ICS logs.
        
        **Key Features:**
        - Natural language queries
        - Protocol filtering (SSH, HTTP, FTP, etc.)
        - Real-time analysis
        - Query caching
        """)
        if st.button("→ Go to Query Logs", key="btn_query"):
            st.switch_page("pages/1_🔍_Query_Logs.py")
    
    with feature_col2:
        st.markdown("""
        #### 📊 Analytics
        Visualize trends, patterns, and anomalies in your security logs.
        
        **Key Features:**
        - Interactive charts
        - Time-series analysis
        - Protocol distribution
        - Threat detection metrics
        """)
        if st.button("→ Go to Analytics", key="btn_analytics"):
            st.switch_page("pages/2_📊_Analytics.py")
    
    with feature_col3:
        st.markdown("""
        #### 💾 Export Data
        Export query results and analysis in multiple formats.
        
        **Key Features:**
        - CSV export
        - JSON export
        - Markdown reports
        - Text summaries
        """)
        if st.button("→ Go to Export", key="btn_export"):
            st.switch_page("pages/3_💾_Export.py")
    
    # Recent activity
    st.markdown("---")
    st.markdown("### 📝 Recent Activity")
    
    # Sample recent queries (in real app, fetch from session/cache)
    recent_queries = [
        {"query": "Show failed login attempts", "time": "2 min ago", "status": "✅"},
        {"query": "Any SSH brute force attacks?", "time": "15 min ago", "status": "✅"},
        {"query": "List all HTTP errors", "time": "1 hour ago", "status": "✅"},
    ]
    
    for i, activity in enumerate(recent_queries):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.text(f"💬 {activity['query']}")
        with col2:
            st.text(f"⏰ {activity['time']}")
        with col3:
            st.text(activity['status'])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>ICS-LogQueryGPT v1.0 | Powered by Ollama + Llama 3.1 | 100% Local Processing</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
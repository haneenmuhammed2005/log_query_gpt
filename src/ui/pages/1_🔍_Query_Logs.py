"""
ICS-LogQueryGPT - Query Logs Page
Author: Kripa
Week 1 Day 3: Natural Language Query Interface
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

# Page config
st.set_page_config(
    page_title="Query Logs - ICS-LogQueryGPT",
    page_icon="🔍",
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

def initialize_session_state():
    """Initialize session state variables"""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = "All"
    if 'selected_mode' not in st.session_state:
        st.session_state.selected_mode = "Fast"

def get_query_suggestions():
    """Return common query suggestions"""
    return [
        "Show failed login attempts in the last 24 hours",
        "List all SSH connections",
        "Any brute force attacks detected?",
        "Show HTTP 500 errors",
        "Display unauthorized access attempts",
        "Find suspicious FTP activity",
        "Show all critical alerts",
        "List failed authentication by protocol",
    ]

# -------------------------------------------------------
# REAL RAG INTEGRATION
# -------------------------------------------------------

@st.cache_resource(show_spinner="Loading AI system...")
def load_rag_system():
    try:
        from src.rag_system.integrated_rag_ollama import ICSLogQueryGPTOllama
        system = ICSLogQueryGPTOllama(
            vector_db_path="data/vector_db/HDFS_index.faiss",
            metadata_path="data/vector_db/HDFS_metadata.pkl"
        )
        return system, None
    except Exception as e:
        return None, str(e)

def real_rag_query(query: str, protocol: str = "All", mode: str = "Fast") -> dict:
    system, error = load_rag_system()
    if error or system is None:
        return {
            "answer": f"⚠️ RAG system unavailable: {error}\n\nMake sure Ollama is running:\n```\nollama serve\n```",
            "sources": [],
            "log_count": 0,
            "response_time": 0,
            "cached": False,
            "model": "unavailable"
        }

    enriched_query = f"[Protocol: {protocol}] {query}" if protocol != "All" else query
    top_k = {"Fast": 3, "Detailed": 5, "Deep Analysis": 10}.get(mode, 5)

    import time
    start = time.time()
    try:
        result = system.query(enriched_query, top_k=top_k)
        return {
            "answer": result["answer"],
            "sources": ["HDFS_logs"],
            "log_count": top_k,
            "response_time": round(time.time() - start, 2),
            "cached": False,
            "model": result.get("model", "llama3")
        }
    except Exception as e:
        return {
            "answer": f"❌ Query failed: {e}\n\nMake sure Ollama is running:\n```\nollama serve\n```",
            "sources": [],
            "log_count": 0,
            "response_time": round(time.time() - start, 2),
            "cached": False,
            "model": "error"
        }

# -------------------------------------------------------

def display_response(response_data):
    """Display query response in formatted card"""
    
    st.markdown("### 🤖 AI Response")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Logs Analyzed", f"{response_data['log_count']:,}")
    with col2:
        st.metric("Response Time", f"{response_data['response_time']:.2f}s")
    with col3:
        status = "⚡ Cached" if response_data['cached'] else "🔄 Fresh"
        st.metric("Status", status)
    with col4:
        st.metric("Sources", len(response_data['sources']))
    
    st.markdown("---")
    st.markdown(response_data['answer'])
    
    st.markdown("---")
    st.markdown("**📂 Sources:**")
    sources_text = ", ".join(f"`{src}`" for src in response_data['sources'])
    st.markdown(sources_text)
    
    st.markdown("---")
    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if st.button("💾 Save Response", key="save_response"):
            st.success("✅ Response saved to history!")
    with action_col2:
        if st.button("📊 View Analytics", key="view_analytics"):
            st.info("📊 Redirecting to Analytics...")
    with action_col3:
        if st.button("📤 Export Results", key="export_results"):
            st.info("📤 Redirecting to Export...")

def main():
    """Main query logs page"""
    
    check_authentication()
    initialize_session_state()
    
    st.title("🔍 Query ICS Logs")
    st.markdown("Ask questions about your ICS security logs in natural language")
    
    with st.sidebar:
        st.markdown("### ⚙️ Query Settings")
        
        st.markdown("#### 🔌 Protocol Filter")
        protocols = ["All", "SSH", "HTTP", "HTTPS", "FTP", "DNS", "SMTP", "Telnet"]
        selected_protocol = st.selectbox(
            "Select Protocol",
            protocols,
            index=protocols.index(st.session_state.selected_protocol),
            key="protocol_select"
        )
        st.session_state.selected_protocol = selected_protocol
        
        st.markdown("#### ⚡ Query Mode")
        mode = st.radio(
            "Select Mode",
            ["Fast", "Detailed", "Deep Analysis"],
            index=["Fast", "Detailed", "Deep Analysis"].index(st.session_state.selected_mode),
            help="Fast: Quick answers, Detailed: More context, Deep: Comprehensive analysis"
        )
        st.session_state.selected_mode = mode
        
        st.markdown("#### 📅 Time Range")
        time_range = st.selectbox(
            "Select Time Range",
            ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days", "Custom"],
        )
        
        with st.expander("🔧 Advanced Options"):
            include_archived = st.checkbox("Include archived logs", value=False)
            case_sensitive = st.checkbox("Case sensitive search", value=False)
            max_results = st.slider("Max results", 10, 1000, 100)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_area(
            "💬 Enter your query:",
            placeholder="Example: Show failed login attempts in the last 24 hours",
            height=100,
            key="query_input"
        )
    
    with col2:
        st.markdown("#### 💡 Quick Actions")
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if query.strip():
                with st.spinner("🤖 AI is analyzing your logs..."):
                    response = real_rag_query(
                        query,
                        st.session_state.selected_protocol,
                        st.session_state.selected_mode
                    )
                    st.session_state.current_results = response
                    st.session_state.query_history.append({
                        'query': query,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'protocol': st.session_state.selected_protocol,
                        'mode': st.session_state.selected_mode
                    })
                st.rerun()
            else:
                st.warning("⚠️ Please enter a query")
        
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.current_results = None
            st.rerun()
        
        if st.button("📝 History", use_container_width=True):
            st.info("📝 Query history feature coming soon!")
    
    st.markdown("---")
    st.markdown("#### 💡 Query Suggestions")
    
    suggestions = get_query_suggestions()
    suggestion_cols = st.columns(4)
    
    for idx, suggestion in enumerate(suggestions[:8]):
        with suggestion_cols[idx % 4]:
            if st.button(
                suggestion[:30] + "..." if len(suggestion) > 30 else suggestion,
                key=f"suggestion_{idx}",
                use_container_width=True
            ):
                st.session_state.query_input = suggestion
                st.rerun()
    
    if st.session_state.current_results:
        st.markdown("---")
        display_response(st.session_state.current_results)
    
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📜 Recent Queries")
        
        for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"🕐 {item['timestamp']} - {item['protocol']}"):
                st.markdown(f"**Query:** {item['query']}")
                st.markdown(f"**Mode:** {item['mode']}")
                if st.button("🔄 Rerun", key=f"rerun_{idx}"):
                    st.session_state.query_input = item['query']
                    st.rerun()

if __name__ == "__main__":
    main()
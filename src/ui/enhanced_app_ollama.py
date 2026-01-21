import streamlit as st
import sys
sys.path.append('src')

from rag_system.enhanced_rag_ollama import EnhancedRAGOllama
from vector_db.optimized_search import OptimizedVectorDB
from embeddings.enhanced_embedder import EnhancedEmbedder
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="ICS-LogQueryGPT Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .log-entry {
        background-color: #f8f9fa;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_queries': 0,
        'total_logs_retrieved': 0,
        'avg_generation_time': 0
    }

# Load system components
@st.cache_resource
def load_system():
    """Load all system components"""
    try:
        # Load embeddings and metadata
        embeddings = np.load('data/embeddings/HDFS_enhanced.npy')
        metadata = pd.read_csv('data/processed_logs/HDFS_enhanced.csv')
        
        # Create vector DB
        db = OptimizedVectorDB()
        db.build_index(embeddings, metadata)
        
        # Create embedder
        embedder = EnhancedEmbedder()
        
        # Create Enhanced RAG with your model
        rag = EnhancedRAGOllama(model_name='llama3:8b-instruct-q4_0')
        
        return db, embedder, rag, metadata
    except Exception as e:
        st.error(f"Error loading system: {e}")
        st.stop()

try:
    db, embedder, rag, metadata = load_system()
    system_loaded = True
except Exception as e:
    st.error(f"❌ Failed to load system: {e}")
    st.info("Make sure you've completed Week 2 setup and Ollama is running!")
    system_loaded = False
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Model settings
    model_choice = st.selectbox(
        "🤖 Model",
        ["llama3:8b-instruct-q4_0", "llama3.1:8b", "llama3.1:70b"],
        help="Q4_0: Fast, quantized\n8B: Faster, lower resource\n70B: More accurate, requires powerful GPU"
    )
    
    # Retrieval settings
    st.markdown("#### 🔍 Retrieval Settings")
    num_logs = st.slider(
        "Logs to retrieve",
        min_value=1,
        max_value=20,
        value=5,
        help="More logs = better context but slower generation"
    )
    
    min_similarity = st.slider(
        "Minimum similarity",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="Filter out low-relevance logs"
    )
    
    # Protocol filter
    protocol_options = ["All"] + sorted(metadata['protocols'].unique().tolist())
    protocol_filter = st.selectbox(
        "🔌 Protocol Filter",
        protocol_options,
        help="Filter logs by ICS protocol"
    )
    
    # Severity filter
    severity_options = ["All"] + sorted(metadata['severity'].unique().tolist())
    severity_filter = st.selectbox(
        "⚠️ Severity Filter",
        severity_options,
        help="Filter logs by severity level"
    )
    
    st.divider()
    
    # Analysis mode
    st.markdown("#### 🧠 Analysis Mode")
    analysis_mode = st.selectbox(
        "Mode",
        ["analysis", "summary", "security", "troubleshooting"],
        help="Choose analysis approach"
    )
    
    # Temperature control
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative, Lower = more focused"
    )
    
    st.divider()
    
    # Conversation controls
    st.markdown("#### 💬 Conversation")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            rag.clear_history()
            st.session_state.conversation_started = False
            st.rerun()
    
    with col2:
        if st.button("💾 Export", use_container_width=True):
            if st.session_state.messages:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conversation_{timestamp}.json"
                rag.export_conversation(filename)
                st.success(f"Saved to {filename}")
    
    # Show conversation stats
    if rag.conversation_history:
        summary = rag.get_conversation_summary()
        st.markdown("#### 📊 Session Stats")
        st.metric("Exchanges", summary['total_exchanges'])
        st.metric("Logs Analyzed", summary['total_logs_analyzed'])
        st.caption(f"Started: {summary['start_time'][:19] if summary['start_time'] else 'N/A'}")
    
    st.divider()
    
    # Quick tips
    st.markdown("#### 💡 Quick Tips")
    with st.expander("Example Questions"):
        st.caption("• Show me authentication failures")
        st.caption("• What Modbus errors occurred?")
        st.caption("• Summarize critical events")
        st.caption("• Find DNP3 communication issues")
        st.caption("• Are there any security concerns?")
    
    with st.expander("Protocol Keywords"):
        st.caption("• modbus, dnp3, snmp, bacnet")
        st.caption("• http, ssh, ftp, telnet")
        st.caption("• authentication, timeout, error")
    
    st.divider()
    
    # System status
    st.markdown("#### 🔋 System Status")
    st.success("🟢 Ollama Connected")
    st.info(f"📦 Model: {model_choice}")
    st.info(f"📊 {len(metadata):,} logs indexed")
    
    st.divider()
    st.caption("🤖 100% Local • No API Costs • Private & Secure")

# Main content area
st.markdown('<p class="main-header">🔍 ICS-LogQueryGPT Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Industrial Control System Log Analysis powered by Llama 3 + RAG</p>', unsafe_allow_html=True)

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "Total Queries",
        st.session_state.stats['total_queries'],
        delta=None
    )
with col2:
    st.metric(
        "Logs Retrieved",
        st.session_state.stats['total_logs_retrieved'],
        delta=None
    )
with col3:
    avg_time = st.session_state.stats['avg_generation_time']
    st.metric(
        "Avg Response Time",
        f"{avg_time:.2f}s" if avg_time > 0 else "N/A",
        delta=None
    )
with col4:
    st.metric(
        "Conversation Length",
        len(st.session_state.messages) // 2,
        delta=None
    )

st.divider()

# Chat interface
chat_container = st.container()
with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show retrieved logs for assistant messages
            if message["role"] == "assistant" and "logs" in message:
                with st.expander(f"📋 Retrieved Logs ({len(message['logs'])})"):
                    for i, log in enumerate(message["logs"], 1):
                        severity_emoji = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢',
                            'info': 'ℹ️'
                        }.get(log.get('severity', 'info'), 'ℹ️')
                        
                        st.markdown(f"""
                        <div class="log-entry">
                            <strong>Log {i}</strong> {severity_emoji}<br>
                            <strong>Text:</strong> {log['log_text']}<br>
                            <strong>Protocols:</strong> {log['protocols']}<br>
                            <strong>Severity:</strong> {log.get('severity', 'unknown')}<br>
                            <strong>Score:</strong> {log['similarity_score']:.3f}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                meta = message["metadata"]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"⏱️ {meta.get('generation_time', 0):.2f}s")
                with col2:
                    st.caption(f"🔧 {meta.get('mode', 'unknown').title()}")
                with col3:
                    st.caption(f"🤖 {meta.get('model', 'unknown')}")

# User input
if question := st.chat_input("Ask a question about ICS logs...", key="user_input"):
    # Start conversation if not started
    if not st.session_state.conversation_started:
        rag.start_conversation()
        st.session_state.conversation_started = True
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })
    
    with st.chat_message("user"):
        st.markdown(question)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner(f"🤖 Analyzing with {model_choice}..."):
            # Embed query
            query_emb = embedder.embedder.embed_single_log(question)
            
            # Apply filters
            prot_filter = None if protocol_filter == "All" else protocol_filter
            sev_filter = None if severity_filter == "All" else severity_filter
            
            # Search
            logs = db.search_with_filter(
                query_emb,
                k=num_logs,
                protocol_filter=prot_filter,
                severity_filter=sev_filter,
                min_score=min_similarity
            )
            
            # Update model
            rag.model_name = model_choice
            
            # Generate answer
            result = rag.generate_with_context(
                question,
                logs,
                mode=analysis_mode
            )
            
            if result.get('error'):
                error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                st.error(error_msg)
                st.info("💡 Make sure Ollama is running: `ollama serve`")
                
                # Add error to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            else:
                # Display answer
                answer = result['answer']
                st.markdown(answer)
                
                # Show retrieved logs
                with st.expander(f"📋 Retrieved Logs ({len(logs)})"):
                    for i, log in enumerate(logs, 1):
                        severity_emoji = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢',
                            'info': 'ℹ️'
                        }.get(log.get('severity', 'info'), 'ℹ️')
                        
                        st.markdown(f"""
                        <div class="log-entry">
                            <strong>Log {i}</strong> {severity_emoji}<br>
                            <strong>Text:</strong> {log['log_text']}<br>
                            <strong>Protocols:</strong> {log['protocols']}<br>
                            <strong>Severity:</strong> {log.get('severity', 'unknown')}<br>
                            <strong>Score:</strong> {log['similarity_score']:.3f}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if i < len(logs):
                            st.divider()
                
                # Show metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"⏱️ Generation: {result.get('generation_time', 0):.2f}s")
                with col2:
                    st.caption(f"🔧 Mode: {result.get('mode', 'unknown').title()}")
                with col3:
                    st.caption(f"💬 Exchange #{result.get('conversation_length', 0)}")
                
                # Update stats
                st.session_state.stats['total_queries'] += 1
                st.session_state.stats['total_logs_retrieved'] += len(logs)
                
                # Update average generation time
                old_avg = st.session_state.stats['avg_generation_time']
                n = st.session_state.stats['total_queries']
                new_time = result.get('generation_time', 0)
                st.session_state.stats['avg_generation_time'] = (old_avg * (n-1) + new_time) / n
                
                # Add to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "logs": logs,
                    "metadata": {
                        'generation_time': result.get('generation_time', 0),
                        'mode': result.get('mode', 'unknown'),
                        'model': result.get('model', 'unknown')
                    }
                })

# Analytics tab (bottom of page)
with st.expander("📊 Analytics & Insights"):
    if len(metadata) > 0:
        tab1, tab2, tab3 = st.tabs(["Protocol Distribution", "Severity Analysis", "Dataset Stats"])
        
        with tab1:
            # Protocol distribution chart
            protocol_counts = {}
            for protocols in metadata['protocols']:
                for p in protocols.split(','):
                    protocol_counts[p] = protocol_counts.get(p, 0) + 1
            
            fig = px.bar(
                x=list(protocol_counts.keys()),
                y=list(protocol_counts.values()),
                labels={'x': 'Protocol', 'y': 'Count'},
                title='Protocol Distribution in Dataset'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Severity distribution
            severity_counts = metadata['severity'].value_counts()
            
            colors = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#28a745',
                'info': '#17a2b8'
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                marker=dict(colors=[colors.get(s, '#6c757d') for s in severity_counts.index])
            )])
            fig.update_layout(title='Severity Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### Dataset Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Logs", f"{len(metadata):,}")
                st.metric("Unique Protocols", len(metadata['protocols'].unique()))
            
            with col2:
                st.metric("Severity Levels", len(metadata['severity'].unique()))
                st.metric("Vector Dimension", 768)
            
            with col3:
                critical_count = len(metadata[metadata['severity'] == 'critical'])
                st.metric("Critical Events", critical_count)
                st.metric("Index Type", db.index_type)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>ICS-LogQueryGPT Pro</strong> | 
    Powered by Llama 3 + FAISS + BERT | 
    100% Local & Private | 
    <a href="https://github.com/haneenmuhammed2005/ICS-LogQueryGPT" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
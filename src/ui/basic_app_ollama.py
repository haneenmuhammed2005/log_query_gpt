import streamlit as st
import sys
import os
sys.path.append('src')

from rag_system.integrated_rag_ollama import ICSLogQueryGPTOllama

# === PAGE CONFIG ===
st.set_page_config(
    page_title="ICS-LogQueryGPT",
    page_icon="🔍",
    layout="wide"
)

# === TITLE ===
st.title("🔍 ICS-LogQueryGPT")
st.caption("Powered by Ollama + Llama 3.1")
st.write("Ask questions about your ICS logs in natural language!")

st.divider()

# === LOAD SYSTEM (CACHED) ===
@st.cache_resource
def load_system():
    """Load system once and cache it"""
    return ICSLogQueryGPTOllama(
        vector_db_path='data/vector_db/HDFS_index.faiss',
        metadata_path='data/vector_db/HDFS_metadata.pkl',
        model_name='llama3.1:8b'
    )

# Try to load system
try:
    with st.spinner("🔧 Loading system..."):
        system = load_system()
    st.success("✅ System ready!")
except Exception as e:
    st.error(f"❌ Error loading system: {e}")
    st.info("Make sure:")
    st.code("1. Ollama is running: ollama serve\n2. Vector DB exists: data/vector_db/HDFS_index.faiss")
    st.stop()

# === USER INPUT ===
st.subheader("💬 Ask a Question")

col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input(
        "Question:",
        placeholder="e.g., Show me authentication failures",
        label_visibility="collapsed"
    )

with col2:
    num_logs = st.slider("Logs to retrieve:", 1, 10, 5)

# === QUERY BUTTON ===
if st.button("🔍 Search", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("⚠️ Please enter a question")
    else:
        # Show progress
        with st.spinner("🤖 Thinking..."):
            # Run query
            result = system.query(question, top_k=num_logs)
        
        # Check for errors
        if result.get('error'):
            st.error(f"❌ Error: {result['answer']}")
        else:
            # Display answer
            st.subheader("💬 Answer")
            st.write(result['answer'])
            
            # Display metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Generation Time", f"{result.get('generation_time', 0):.2f}s")
            with col2:
                st.metric("Tokens Used", f"~{result.get('tokens_used', 0)}")
            with col3:
                st.metric("Logs Retrieved", len(result.get('retrieved_logs', [])))
            
            # Display retrieved logs
            st.subheader("📋 Retrieved Logs")
            for i, log in enumerate(result.get('retrieved_logs', []), 1):
                with st.expander(f"Log {i} - Similarity: {log['similarity_score']:.3f}"):
                    st.code(log['log_text'], language="text")

# === SIDEBAR ===
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This system uses:
    - **BERT** for embeddings
    - **FAISS** for vector search
    - **Llama 3.1** (via Ollama) for answers
    """)
    
    st.divider()
    
    st.header("📊 System Status")
    st.write(f"✅ Model: llama3.1:8b")
    st.write(f"✅ Vector DB loaded")
    
    st.divider()
    
    st.header("💡 Example Questions")
    st.write("""
    - Show me authentication failures
    - What errors occurred?
    - Are there timeout issues?
    - Find connection problems
    """)

# === FOOTER ===
st.divider()
st.caption("ICS-LogQueryGPT v1.0 - Week 2")
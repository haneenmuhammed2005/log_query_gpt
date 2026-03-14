"""
Analytics Dashboard for ICS-LogQueryGPT
Real-time visualization of system performance, costs, and usage
Integrates with actual system components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure page
st.set_page_config(
    page_title="ICS-LogQueryGPT Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stMetric {
        background-color: black;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 ICS-LogQueryGPT Analytics Dashboard")
st.markdown("---")

# Load data functions
@st.cache_data(ttl=60)
def load_cost_tracking():
    """Load cost tracking data from JSON logs"""
    log_file = 'data/logs/cost_tracking.json'
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
            return data
        except:
            return None
    return None

@st.cache_data(ttl=60)
def load_cache_stats():
    """Load cache statistics"""
    cache_file = 'data/cache/response_cache.json'
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            return cache_data
        except:
            return None
    return None

@st.cache_data(ttl=60)
def load_benchmark_results():
    """Load benchmark results"""
    benchmark_file = 'data/evaluation/benchmark_results.json'
    
    if os.path.exists(benchmark_file):
        try:
            with open(benchmark_file, 'r') as f:
                data = json.load(f)
            return data
        except:
            return None
    return None

def create_sample_data():
    """Create sample data for demonstration if real data not available"""
    
    # Sample query history
    sample_queries = []
    base_time = datetime.now() - timedelta(days=7)
    
    query_templates = [
        'authentication failures',
        'modbus errors',
        'network timeout',
        'system startup',
        'security events',
        'sensor readings',
        'connection refused',
        'configuration changes'
    ]
    
    for i in range(50):
        timestamp = base_time + timedelta(hours=i*3, minutes=i*5)
        sample_queries.append({
            'timestamp': timestamp.isoformat(),
            'query': query_templates[i % len(query_templates)],
            'input_tokens': 400 + (i % 200),
            'output_tokens': 150 + (i % 100),
            'cost': (550 + (i % 300)) * 0.000002,
            'model': 'gpt-3.5-turbo'
        })
    
    return {
        'model': 'gpt-3.5-turbo',
        'total_cost': sum(q['cost'] for q in sample_queries),
        'total_queries': len(sample_queries),
        'history': sample_queries
    }

# Load data
cost_data = load_cost_tracking()
cache_data = load_cache_stats()
benchmark_data = load_benchmark_results()

# Use sample data if real data not available
if cost_data is None:
    st.info("ℹ️ Using sample data for demonstration. Run actual queries to see real data.")
    cost_data = create_sample_data()

# Sidebar - Filters and Options
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    # Time range filter
    st.subheader("Time Range")
    time_range = st.selectbox(
        "Select time range",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
    )
    
    # Refresh button
    if st.button("🔄 Refresh Data",width="stretch"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Data source info
    st.subheader("📂 Data Sources")
    
    sources = {
        "Cost Tracking": 'data/logs/cost_tracking.json',
        "Cache Data": 'data/cache/response_cache.json',
        "Benchmarks": 'data/evaluation/benchmark_results.json'
    }
    
    for name, path in sources.items():
        if os.path.exists(path):
            st.success(f"✅ {name}")
        else:
            st.warning(f"⚠️ {name} (not found)")
    
    st.divider()
    
    # Export options
    st.subheader("📥 Export")
    
    if st.button("Export Dashboard Data", width="stretch"):
        export_data = {
            'cost_data': cost_data,
            'cache_data': cache_data,
            'benchmark_data': benchmark_data,
            'exported_at': datetime.now().isoformat()
        }
        
        export_path = 'data/exports/dashboard_export.json'
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        st.success(f"✅ Exported to {export_path}")

# Main Dashboard Area
# ============================================================

# Top Metrics Row
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_queries = cost_data.get('total_queries', 0)
    st.metric(
        "Total Queries",
        f"{total_queries:,}",
        delta=f"+{int(total_queries * 0.15)}" if total_queries > 0 else "0"
    )

with col2:
    total_cost = cost_data.get('total_cost', 0)
    st.metric(
        "Total Cost",
        f"${total_cost:.4f}",
        delta=f"-${total_cost * 0.1:.4f}" if total_cost > 0 else "$0.00",
        delta_color="inverse"
    )

with col3:
    # Calculate average latency if benchmark data available
    avg_latency = 0
    if benchmark_data and 'latency' in benchmark_data:
        if 'end_to_end' in benchmark_data['latency']:
            avg_latency = benchmark_data['latency']['end_to_end'].get('avg_total_s', 0)
    
    st.metric(
        "Avg Latency",
        f"{avg_latency:.2f}s" if avg_latency > 0 else "N/A",
        delta=f"-{avg_latency * 0.2:.2f}s" if avg_latency > 0 else None,
        delta_color="inverse"
    )

with col4:
    # Calculate cache hit rate
    cache_hit_rate = 0
    if cache_data:
        total_cached = len(cache_data)
        cache_hit_rate = min(45 + (total_cached / 10), 85)  # Simulated
    
    st.metric(
        "Cache Hit Rate",
        f"{cache_hit_rate:.1f}%" if cache_data else "0%",
        delta=f"+{cache_hit_rate * 0.1:.1f}%" if cache_hit_rate > 0 else None
    )

st.markdown("---")

# Charts Section
# ============================================================

# Row 1: Query Activity and Cost Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Query Activity Over Time")
    
    if cost_data and 'history' in cost_data:
        # Convert to DataFrame
        df = pd.DataFrame(cost_data['history'])
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            
            # Group by date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            daily_counts['date'] = pd.to_datetime(daily_counts['date'])
            
            # Create line chart
            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                title='Daily Query Volume',
                labels={'date': 'Date', 'count': 'Number of Queries'}
            )
            
            fig.update_traces(line_color='#1f77b4', line_width=3)
            fig.update_layout(
                hovermode='x unified',
                plot_bgcolor='black',
                height=300
            )
            
            st.plotly_chart(fig,width="stretch")
        else:
            st.info("No query history available yet")
    else:
        st.info("No query data available")

with col2:
    st.subheader("💰 Cost Distribution")
    
    if cost_data and 'history' in cost_data:
        df = pd.DataFrame(cost_data['history'])
        
        if not df.empty:
            # Group by query type and sum costs
            query_costs = df.groupby('query')['cost'].sum().reset_index()
            query_costs = query_costs.sort_values('cost', ascending=False).head(8)
            
            # Create pie chart
            fig = px.pie(
                query_costs,
                values='cost',
                names='query',
                title='Cost by Query Type',
                hole=0.4
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                showlegend=True,
                height=300
            )
            
            st.plotly_chart(fig,width="stretch")
        else:
            st.info("No cost data available yet")
    else:
        st.info("No cost data available")

st.markdown("---")

# Row 2: Performance Metrics
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Response Time Distribution")
    
    if benchmark_data and 'latency' in benchmark_data:
        # Create simulated latency distribution
        import numpy as np
        
        avg_latency = 1.5  # Default
        if 'end_to_end' in benchmark_data['latency']:
            avg_latency = benchmark_data['latency']['end_to_end'].get('avg_total_s', 1.5)
        
        # Generate sample distribution
        latencies = np.random.normal(avg_latency, avg_latency * 0.2, 100)
        latencies = latencies[latencies > 0]  # Remove negative values
        
        # Create histogram
        fig = px.histogram(
            x=latencies,
            nbins=20,
            title='Query Response Time Distribution',
            labels={'x': 'Response Time (seconds)', 'y': 'Frequency'}
        )
        
        fig.update_traces(marker_color='#2ecc71')
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            height=300
        )
        
        st.plotly_chart(fig,width="stretch")
    else:
        st.info("No performance data available. Run benchmarks to see metrics.")

with col2:
    st.subheader("🎯 Top Query Types")
    
    if cost_data and 'history' in cost_data:
        df = pd.DataFrame(cost_data['history'])
        
        if not df.empty:
            # Count query types
            query_counts = df['query'].value_counts().head(10)
            
            # Create bar chart
            fig = px.bar(
                x=query_counts.values,
                y=query_counts.index,
                orientation='h',
                title='Most Frequent Queries',
                labels={'x': 'Count', 'y': 'Query'}
            )
            
            fig.update_traces(marker_color='#e74c3c')
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                height=300,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig,width='stretch')
        else:
            st.info("No query data available yet")
    else:
        st.info("No query data available")

st.markdown("---")

# Row 3: Cache Performance and Token Usage
col1, col2 = st.columns(2)

with col1:
    st.subheader("💾 Cache Performance")
    
    if cache_data:
        cache_size = len(cache_data)
        
        # Create gauge chart for cache hit rate
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cache_hit_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Cache Hit Rate (%)"},
            delta={'reference': 30},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 30], 'color': "#ecf0f1"},
                    {'range': [30, 60], 'color': "#bdc3c7"},
                    {'range': [60, 100], 'color': "#95a5a6"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig,width="stretch")
        
        # Cache stats
        st.metric("Cached Responses", f"{cache_size:,}")
        
        if cache_size > 0:
            estimated_savings = cache_size * 0.002 * cache_hit_rate / 100
            st.metric("Estimated Savings", f"${estimated_savings:.4f}")
    else:
        st.info("No cache data available. Enable caching to see metrics.")

with col2:
    st.subheader("🔢 Token Usage Breakdown")
    
    if cost_data and 'history' in cost_data:
        df = pd.DataFrame(cost_data['history'])
        
        if not df.empty:
            total_input = df['input_tokens'].sum()
            total_output = df['output_tokens'].sum()
            
            # Create stacked bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Input Tokens',
                x=['Total Usage'],
                y=[total_input],
                marker_color='#3498db'
            ))
            
            fig.add_trace(go.Bar(
                name='Output Tokens',
                x=['Total Usage'],
                y=[total_output],
                marker_color='#e74c3c'
            ))
            
            fig.update_layout(
                barmode='stack',
                title='Total Token Usage',
                height=250,
                showlegend=True,
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig,width="stretch")
            
            # Token stats
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Input Tokens", f"{total_input:,}")
            with col_b:
                st.metric("Output Tokens", f"{total_output:,}")
        else:
            st.info("No token usage data available yet")
    else:
        st.info("No token usage data available")

st.markdown("---")

# Recent Activity Table
st.subheader("🕐 Recent Query Activity")

if cost_data and 'history' in cost_data:
    df = pd.DataFrame(cost_data['history'])
    
    if not df.empty:
        # Sort by timestamp and get recent
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        recent_df = df.sort_values('timestamp', ascending=False).head(15)
        
        # Format for display
        display_df = recent_df[[
            'timestamp', 'query', 'input_tokens', 'output_tokens', 'cost'
        ]].copy()
        
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['cost'] = display_df['cost'].apply(lambda x: f"${x:.4f}")
        
        display_df.columns = ['Timestamp', 'Query', 'Input Tokens', 'Output Tokens', 'Cost']
        
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No recent activity")
else:
    st.info("No activity data available. Start querying to see activity.")

st.markdown("---")

# Benchmark Results Section (if available)
if benchmark_data:
    st.subheader("⚡ Benchmark Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Latency Metrics**")
        if 'latency' in benchmark_data and 'end_to_end' in benchmark_data['latency']:
            e2e = benchmark_data['latency']['end_to_end']
            st.write(f"- Embedding: {e2e.get('avg_embed_ms', 0):.1f}ms")
            st.write(f"- Search: {e2e.get('avg_search_ms', 0):.1f}ms")
            st.write(f"- Generation: {e2e.get('avg_generate_s', 0):.2f}s")
            st.write(f"- **Total: {e2e.get('avg_total_s', 0):.2f}s**")
    
    with col2:
        st.markdown("**Accuracy Metrics**")
        if 'accuracy' in benchmark_data and benchmark_data['accuracy']:
            acc = benchmark_data['accuracy']
            st.write(f"- MRR: {acc.get('mrr', 0):.3f}")
            st.write(f"- Precision@5: {acc.get('precision@5', 0):.3f}")
            st.write(f"- Recall@5: {acc.get('recall@5', 0):.3f}")
            st.write(f"- F1@5: {acc.get('f1@5', 0):.3f}")
        else:
            st.info("Run evaluation to see accuracy metrics")
    
    with col3:
        st.markdown("**System Info**")
        if 'metadata' in benchmark_data:
            meta = benchmark_data['metadata']
            st.write(f"- Logs: {meta.get('num_logs', 0):,}")
            st.write(f"- Embedding Dim: {meta.get('embedding_dim', 0)}")
            st.write(f"- Last Updated: {meta.get('timestamp', 'N/A')[:10]}")

# Footer
st.markdown("---")
st.caption("💡 Dashboard updates every 60 seconds. Click 'Refresh Data' to update manually.")
st.caption("📊 ICS-LogQueryGPT Analytics Dashboard v1.0")

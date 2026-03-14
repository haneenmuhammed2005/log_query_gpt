"""
Response Card Component
Author: Kripa - Week 1 Day 5
"""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime

class ResponseCard:
    """Reusable response card component for displaying query results"""
    
    @staticmethod
    def render(
        response_data: Dict,
        show_actions: bool = True,
        show_metrics: bool = True,
        show_sources: bool = True,
        key: str = "response_card"
    ):
        """
        Render a response card
        
        Args:
            response_data: Dictionary containing response information
            show_actions: Show action buttons
            show_metrics: Show response metrics
            show_sources: Show data sources
            key: Unique key for the component
        """
        
        # Header
        st.markdown("### 🤖 AI Response")
        
        # Metrics row
        if show_metrics:
            ResponseCard._render_metrics(response_data)
        
        # Main response
        st.markdown("---")
        
        # Status indicator
        if response_data.get('cached', False):
            st.success("⚡ **Cached Response** - Retrieved from cache")
        else:
            st.info("🔄 **Fresh Analysis** - New query processed")
        
        # Response content
        st.markdown(response_data.get('answer', 'No response available'))
        
        # Sources
        if show_sources and 'sources' in response_data:
            ResponseCard._render_sources(response_data['sources'])
        
        # Actions
        if show_actions:
            ResponseCard._render_actions(key)
    
    @staticmethod
    def _render_metrics(response_data: Dict):
        """Render response metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            log_count = response_data.get('log_count', 0)
            st.metric("Logs Analyzed", f"{log_count:,}")
        
        with col2:
            response_time = response_data.get('response_time', 0)
            st.metric("Response Time", f"{response_time:.2f}s")
        
        with col3:
            cached = response_data.get('cached', False)
            status = "⚡ Cached" if cached else "🔄 Fresh"
            st.metric("Status", status)
        
        with col4:
            sources_count = len(response_data.get('sources', []))
            st.metric("Sources", sources_count)
    
    @staticmethod
    def _render_sources(sources: List[str]):
        """Render data sources"""
        st.markdown("---")
        st.markdown("**📂 Data Sources:**")
        
        # Display sources as tags
        sources_html = " ".join([
            f'<span style="background-color: #1E293B; padding: 4px 12px; border-radius: 6px; margin-right: 8px; display: inline-block; margin-bottom: 8px;">'
            f'📄 {source}'
            f'</span>'
            for source in sources
        ])
        
        st.markdown(sources_html, unsafe_allow_html=True)
    
    @staticmethod
    def _render_actions(key: str):
        """Render action buttons"""
        st.markdown("---")
        st.markdown("**⚡ Actions:**")
        
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("💾 Save", key=f"{key}_save", use_container_width=True):
                st.success("✅ Response saved!")
        
        with action_col2:
            if st.button("📊 Analytics", key=f"{key}_analytics", use_container_width=True):
                st.switch_page("pages/2_📊_Analytics.py")
        
        with action_col3:
            if st.button("📤 Export", key=f"{key}_export", use_container_width=True):
                st.switch_page("pages/3_💾_Export.py")
        
        with action_col4:
            if st.button("🔄 Rerun", key=f"{key}_rerun", use_container_width=True):
                st.info("🔄 Rerunning query...")
    
    @staticmethod
    def render_compact(
        response_data: Dict,
        key: str = "compact_card"
    ):
        """
        Render a compact response card (for history/previews)
        
        Args:
            response_data: Dictionary containing response information
            key: Unique key for the component
        """
        with st.expander(f"🤖 Response - {response_data.get('timestamp', 'Unknown')}", expanded=False):
            # Quick metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.text(f"📊 {response_data.get('log_count', 0):,} logs")
            
            with metric_col2:
                st.text(f"⏱️ {response_data.get('response_time', 0):.2f}s")
            
            with metric_col3:
                cached = "⚡ Cached" if response_data.get('cached', False) else "🔄 Fresh"
                st.text(cached)
            
            # Truncated response
            answer = response_data.get('answer', '')
            truncated = answer[:200] + "..." if len(answer) > 200 else answer
            st.markdown(truncated)
            
            # View full button
            if st.button("👁️ View Full", key=f"{key}_view"):
                st.session_state.viewing_response = response_data
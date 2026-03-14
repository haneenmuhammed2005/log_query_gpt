"""
Metrics Display Component
Author: Kripa - Week 1 Day 5
"""

import streamlit as st
from typing import List, Dict, Optional

class MetricsDisplay:
    """Reusable metrics display component"""
    
    @staticmethod
    def render_kpi_row(
        metrics: List[Dict],
        columns: Optional[int] = None
    ):
        """
        Render a row of KPI metrics
        
        Args:
            metrics: List of metric dictionaries with keys: label, value, delta, delta_color
            columns: Number of columns (defaults to len(metrics))
        """
        if not metrics:
            return
        
        num_cols = columns or len(metrics)
        cols = st.columns(num_cols)
        
        for idx, metric in enumerate(metrics[:num_cols]):
            with cols[idx]:
                st.metric(
                    label=metric.get('label', ''),
                    value=metric.get('value', ''),
                    delta=metric.get('delta'),
                    delta_color=metric.get('delta_color', 'normal')
                )
    
    @staticmethod
    def render_stat_cards(
        stats: List[Dict],
        columns: int = 3
    ):
        """
        Render statistic cards with icons
        
        Args:
            stats: List of stat dictionaries with keys: icon, label, value, description
            columns: Number of columns
        """
        cols = st.columns(columns)
        
        for idx, stat in enumerate(stats):
            with cols[idx % columns]:
                st.markdown(f"""
                <div style="background-color: #1E293B; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #0EA5E9; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{stat.get('icon', '📊')}</div>
                    <div style="font-size: 0.875rem; color: #94A3B8; margin-bottom: 0.5rem;">{stat.get('label', '')}</div>
                    <div style="font-size: 1.75rem; font-weight: bold; margin-bottom: 0.5rem;">{stat.get('value', '')}</div>
                    <div style="font-size: 0.75rem; color: #64748B;">{stat.get('description', '')}</div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_metrics(
        metrics: List[Dict],
        show_percentage: bool = True
    ):
        """
        Render metrics with progress bars
        
        Args:
            metrics: List of metric dicts with keys: label, value, max_value, color
            show_percentage: Show percentage text
        """
        for metric in metrics:
            label = metric.get('label', '')
            value = metric.get('value', 0)
            max_value = metric.get('max_value', 100)
            color = metric.get('color', '#0EA5E9')
            
            # Calculate percentage
            percentage = (value / max_value * 100) if max_value > 0 else 0
            
            # Label and value
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{label}**")
            with col2:
                if show_percentage:
                    st.markdown(f"`{percentage:.1f}%`")
            
            # Progress bar
            st.progress(percentage / 100)
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    @staticmethod
    def render_comparison_metrics(
        current: Dict,
        previous: Dict,
        labels: List[str]
    ):
        """
        Render comparison metrics (current vs previous)
        
        Args:
            current: Current period metrics
            previous: Previous period metrics
            labels: List of metric labels
        """
        st.markdown("### 📊 Period Comparison")
        
        # Create comparison table
        comparison_data = []
        
        for label in labels:
            curr_val = current.get(label, 0)
            prev_val = previous.get(label, 0)
            
            # Calculate change
            if prev_val > 0:
                change = ((curr_val - prev_val) / prev_val) * 100
                change_str = f"{change:+.1f}%"
                indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            else:
                change_str = "N/A"
                indicator = "➡️"
            
            comparison_data.append({
                'Metric': label,
                'Current': f"{curr_val:,}",
                'Previous': f"{prev_val:,}",
                'Change': f"{indicator} {change_str}"
            })
        
        # Display as formatted table
        for row in comparison_data:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{row['Metric']}**")
            with col2:
                st.markdown(row['Current'])
            with col3:
                st.markdown(row['Previous'])
            with col4:
                st.markdown(row['Change'])
    
    @staticmethod
    def render_status_indicators(
        services: List[Dict]
    ):
        """
        Render service status indicators
        
        Args:
            services: List of service dicts with keys: name, status, uptime
        """
        st.markdown("### 🟢 System Status")
        
        for service in services:
            name = service.get('name', '')
            status = service.get('status', 'unknown')
            uptime = service.get('uptime', 'N/A')
            
            # Status emoji
            if status == 'operational':
                emoji = '🟢'
                color = '#10B981'
            elif status == 'degraded':
                emoji = '🟡'
                color = '#F59E0B'
            elif status == 'down':
                emoji = '🔴'
                color = '#EF4444'
            else:
                emoji = '⚪'
                color = '#64748B'
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"{emoji} **{name}**")
            with col2:
                st.markdown(f"<span style='color: {color};'>{status.title()}</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"`{uptime}`")
"""
Query Suggestions Component
Author: Kripa - Week 1 Day 5
"""

import streamlit as st
from typing import List, Optional, Callable

class QuerySuggestions:
    """Reusable query suggestions component"""
    
    DEFAULT_SUGGESTIONS = [
        "Show failed login attempts in the last 24 hours",
        "List all SSH connections",
        "Any brute force attacks detected?",
        "Show HTTP 500 errors",
        "Display unauthorized access attempts",
        "Find suspicious FTP activity",
        "Show all critical alerts",
        "List failed authentication by protocol",
        "Show connections from external IPs",
        "Display port scan attempts",
        "Find malware indicators",
        "Show data exfiltration patterns"
    ]
    
    CATEGORY_SUGGESTIONS = {
        "Authentication": [
            "Show failed login attempts",
            "List successful authentications",
            "Find brute force attacks",
            "Show password policy violations",
            "Display multi-factor auth failures"
        ],
        "Network": [
            "Show external connections",
            "List port scan attempts",
            "Find unusual traffic patterns",
            "Display bandwidth anomalies",
            "Show blocked connections"
        ],
        "Security": [
            "Find malware indicators",
            "Show critical alerts",
            "List security policy violations",
            "Display intrusion attempts",
            "Find data exfiltration"
        ],
        "Protocol": [
            "Analyze SSH activity",
            "Show HTTP errors",
            "List FTP transfers",
            "Display DNS queries",
            "Analyze SMTP traffic"
        ]
    }
    
    @staticmethod
    def render_simple(
        key: str = "suggestions",
        suggestions: Optional[List[str]] = None,
        columns: int = 4,
        on_click_callback: Optional[Callable] = None
    ):
        """
        Render simple query suggestions
        
        Args:
            key: Unique key for the component
            suggestions: List of suggestions (uses defaults if None)
            columns: Number of columns
            on_click_callback: Callback when suggestion is clicked
        """
        if suggestions is None:
            suggestions = QuerySuggestions.DEFAULT_SUGGESTIONS
        
        st.markdown("#### 💡 Query Suggestions")
        
        cols = st.columns(columns)
        
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % columns]:
                # Truncate long suggestions
                display_text = (suggestion[:35] + "...") if len(suggestion) > 35 else suggestion
                
                if st.button(
                    display_text,
                    key=f"{key}_{idx}",
                    use_container_width=True,
                    help=suggestion if len(suggestion) > 35 else None
                ):
                    if on_click_callback:
                        on_click_callback(suggestion)
                    else:
                        st.session_state.query_input = suggestion
    
    @staticmethod
    def render_categorized(
        key: str = "cat_suggestions",
        on_click_callback: Optional[Callable] = None
    ):
        """
        Render categorized query suggestions
        
        Args:
            key: Unique key for the component
            on_click_callback: Callback when suggestion is clicked
        """
        st.markdown("#### 💡 Query Suggestions by Category")
        
        # Category selector
        selected_category = st.selectbox(
            "Select Category",
            list(QuerySuggestions.CATEGORY_SUGGESTIONS.keys()),
            key=f"{key}_category"
        )
        
        # Display suggestions for selected category
        suggestions = QuerySuggestions.CATEGORY_SUGGESTIONS[selected_category]
        
        cols = st.columns(3)
        
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % 3]:
                if st.button(
                    suggestion,
                    key=f"{key}_{selected_category}_{idx}",
                    use_container_width=True
                ):
                    if on_click_callback:
                        on_click_callback(suggestion)
                    else:
                        st.session_state.query_input = suggestion
    
    @staticmethod
    def render_compact(
        key: str = "compact_suggestions",
        max_display: int = 6,
        on_click_callback: Optional[Callable] = None
    ):
        """
        Render compact query suggestions (as chips)
        
        Args:
            key: Unique key for the component
            max_display: Maximum suggestions to display
            on_click_callback: Callback when suggestion is clicked
        """
        st.markdown("💡 **Quick Suggestions:**")
        
        suggestions = QuerySuggestions.DEFAULT_SUGGESTIONS[:max_display]
        
        # Display as inline buttons
        cols = st.columns(len(suggestions))
        
        for idx, suggestion in enumerate(suggestions):
            with cols[idx]:
                short_text = suggestion.split()[0:3]
                display_text = " ".join(short_text) + "..."
                
                if st.button(
                    display_text,
                    key=f"{key}_{idx}",
                    help=suggestion
                ):
                    if on_click_callback:
                        on_click_callback(suggestion)
                    else:
                        st.session_state.query_input = suggestion
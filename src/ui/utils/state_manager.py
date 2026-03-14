"""
State Manager - Centralized Session State Management
Author: Kripa - Week 1 Day 6
"""

import streamlit as st
from typing import Any, Optional, Dict, List
from datetime import datetime

class StateManager:
    """Centralized state management for the application"""
    
    # State keys
    AUTHENTICATED = 'authenticated'
    USERNAME = 'username'
    USER_ROLE = 'user_role'
    SESSION_TOKEN = 'session_token'
    QUERY_HISTORY = 'query_history'
    CURRENT_RESULTS = 'current_results'
    SELECTED_PROTOCOL = 'selected_protocol'
    SELECTED_MODE = 'selected_mode'
    CURRENT_PAGE = 'current_page'
    PREFERENCES = 'user_preferences'
    CACHE_STATS = 'cache_stats'
    
    @staticmethod
    def initialize():
        """Initialize all required session state variables"""
        
        # Authentication
        if StateManager.AUTHENTICATED not in st.session_state:
            st.session_state[StateManager.AUTHENTICATED] = False
        
        if StateManager.USERNAME not in st.session_state:
            st.session_state[StateManager.USERNAME] = None
        
        if StateManager.USER_ROLE not in st.session_state:
            st.session_state[StateManager.USER_ROLE] = 'user'
        
        if StateManager.SESSION_TOKEN not in st.session_state:
            st.session_state[StateManager.SESSION_TOKEN] = None
        
        # Query state
        if StateManager.QUERY_HISTORY not in st.session_state:
            st.session_state[StateManager.QUERY_HISTORY] = []
        
        if StateManager.CURRENT_RESULTS not in st.session_state:
            st.session_state[StateManager.CURRENT_RESULTS] = None
        
        # Filters
        if StateManager.SELECTED_PROTOCOL not in st.session_state:
            st.session_state[StateManager.SELECTED_PROTOCOL] = "All"
        
        if StateManager.SELECTED_MODE not in st.session_state:
            st.session_state[StateManager.SELECTED_MODE] = "Fast"
        
        # Navigation
        if StateManager.CURRENT_PAGE not in st.session_state:
            st.session_state[StateManager.CURRENT_PAGE] = "Home"
        
        # User preferences
        if StateManager.PREFERENCES not in st.session_state:
            st.session_state[StateManager.PREFERENCES] = {
                'theme': 'dark',
                'results_per_page': 10,
                'auto_refresh': False,
                'notifications': True
            }
        
        # Cache statistics
        if StateManager.CACHE_STATS not in st.session_state:
            st.session_state[StateManager.CACHE_STATS] = {
                'hits': 0,
                'misses': 0,
                'total_saved_time': 0
            }
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from session state
        
        Args:
            key: State key
            default: Default value if key doesn't exist
            
        Returns:
            Value from state or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """
        Set value in session state
        
        Args:
            key: State key
            value: Value to set
        """
        st.session_state[key] = value
    
    @staticmethod
    def delete(key: str):
        """
        Delete key from session state
        
        Args:
            key: State key to delete
        """
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def clear_all():
        """Clear all session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get(StateManager.AUTHENTICATED, False)
    
    @staticmethod
    def login(username: str, user_role: str, session_token: str):
        """
        Set login state
        
        Args:
            username: Username
            user_role: User role
            session_token: Session token
        """
        StateManager.set(StateManager.AUTHENTICATED, True)
        StateManager.set(StateManager.USERNAME, username)
        StateManager.set(StateManager.USER_ROLE, user_role)
        StateManager.set(StateManager.SESSION_TOKEN, session_token)
    
    @staticmethod
    def logout():
        """Clear login state"""
        StateManager.clear_all()
        StateManager.initialize()
    
    @staticmethod
    def add_to_history(query: str, protocol: str, mode: str, results: Optional[Dict] = None):
        """
        Add query to history
        
        Args:
            query: Query text
            protocol: Selected protocol
            mode: Query mode
            results: Query results (optional)
        """
        history = StateManager.get(StateManager.QUERY_HISTORY, [])
        
        history_item = {
            'query': query,
            'protocol': protocol,
            'mode': mode,
            'timestamp': datetime.now().isoformat(),
            'results_summary': {
                'log_count': results.get('log_count', 0) if results else 0,
                'response_time': results.get('response_time', 0) if results else 0,
                'cached': results.get('cached', False) if results else False
            } if results else None
        }
        
        history.append(history_item)
        
        # Keep only last 50 queries
        if len(history) > 50:
            history = history[-50:]
        
        StateManager.set(StateManager.QUERY_HISTORY, history)
    
    @staticmethod
    def get_recent_queries(limit: int = 10) -> List[Dict]:
        """
        Get recent queries from history
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of recent queries
        """
        history = StateManager.get(StateManager.QUERY_HISTORY, [])
        return list(reversed(history[-limit:]))
    
    @staticmethod
    def update_cache_stats(hit: bool, time_saved: float = 0):
        """
        Update cache statistics
        
        Args:
            hit: Whether it was a cache hit
            time_saved: Time saved by cache hit
        """
        stats = StateManager.get(StateManager.CACHE_STATS, {
            'hits': 0,
            'misses': 0,
            'total_saved_time': 0
        })
        
        if hit:
            stats['hits'] += 1
            stats['total_saved_time'] += time_saved
        else:
            stats['misses'] += 1
        
        StateManager.set(StateManager.CACHE_STATS, stats)
    
    @staticmethod
    def get_cache_hit_rate() -> float:
        """
        Calculate cache hit rate
        
        Returns:
            Cache hit rate as percentage
        """
        stats = StateManager.get(StateManager.CACHE_STATS, {
            'hits': 0,
            'misses': 0,
            'total_saved_time': 0
        })
        
        total = stats['hits'] + stats['misses']
        if total == 0:
            return 0.0
        
        return (stats['hits'] / total) * 100
    
    @staticmethod
    def set_preference(key: str, value: Any):
        """
        Set user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        prefs = StateManager.get(StateManager.PREFERENCES, {})
        prefs[key] = value
        StateManager.set(StateManager.PREFERENCES, prefs)
    
    @staticmethod
    def get_preference(key: str, default: Any = None) -> Any:
        """
        Get user preference
        
        Args:
            key: Preference key
            default: Default value
            
        Returns:
            Preference value or default
        """
        prefs = StateManager.get(StateManager.PREFERENCES, {})
        return prefs.get(key, default)
    
    @staticmethod
    def export_state() -> Dict:
        """
        Export current state as dictionary
        
        Returns:
            Dictionary of current state
        """
        return {
            'authenticated': StateManager.get(StateManager.AUTHENTICATED),
            'username': StateManager.get(StateManager.USERNAME),
            'query_history_count': len(StateManager.get(StateManager.QUERY_HISTORY, [])),
            'cache_stats': StateManager.get(StateManager.CACHE_STATS),
            'preferences': StateManager.get(StateManager.PREFERENCES),
            'current_protocol': StateManager.get(StateManager.SELECTED_PROTOCOL),
            'current_mode': StateManager.get(StateManager.SELECTED_MODE)
        }
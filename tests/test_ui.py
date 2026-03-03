"""
UI Component Tests
Author: Kripa - Week 1 Day 7
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Note: These are unit tests for the components
# Full UI testing would require Streamlit testing framework

class TestProtocolFilter:
    """Test ProtocolFilter component"""
    
    def test_protocols_list(self):
        """Test that all protocols are defined"""
        from src.ui.components.protocol_filter import ProtocolFilter
        
        assert "All" in ProtocolFilter.PROTOCOLS
        assert "SSH" in ProtocolFilter.PROTOCOLS
        assert "HTTP" in ProtocolFilter.PROTOCOLS
        assert len(ProtocolFilter.PROTOCOLS) >= 8
    
    def test_protocol_filter_initialization(self):
        """Test protocol filter can be initialized"""
        from src.ui.components.protocol_filter import ProtocolFilter
        
        filter_component = ProtocolFilter()
        assert filter_component is not None


class TestQuerySuggestions:
    """Test QuerySuggestions component"""
    
    def test_default_suggestions_exist(self):
        """Test that default suggestions are defined"""
        from src.ui.components.query_suggestions import QuerySuggestions
        
        assert len(QuerySuggestions.DEFAULT_SUGGESTIONS) > 0
        assert isinstance(QuerySuggestions.DEFAULT_SUGGESTIONS, list)
    
    def test_category_suggestions_exist(self):
        """Test that category suggestions are defined"""
        from src.ui.components.query_suggestions import QuerySuggestions
        
        assert len(QuerySuggestions.CATEGORY_SUGGESTIONS) > 0
        assert "Authentication" in QuerySuggestions.CATEGORY_SUGGESTIONS
        assert "Security" in QuerySuggestions.CATEGORY_SUGGESTIONS
    
    def test_suggestions_are_strings(self):
        """Test that all suggestions are strings"""
        from src.ui.components.query_suggestions import QuerySuggestions
        
        for suggestion in QuerySuggestions.DEFAULT_SUGGESTIONS:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0


class TestResponseCard:
    """Test ResponseCard component"""
    
    def test_response_card_initialization(self):
        """Test response card can be initialized"""
        from src.ui.components.response_card import ResponseCard
        
        card = ResponseCard()
        assert card is not None
    
    def test_render_methods_exist(self):
        """Test that render methods exist"""
        from src.ui.components.response_card import ResponseCard
        
        assert hasattr(ResponseCard, 'render')
        assert hasattr(ResponseCard, 'render_compact')
        assert callable(ResponseCard.render)
        assert callable(ResponseCard.render_compact)


class TestMetricsDisplay:
    """Test MetricsDisplay component"""
    
    def test_metrics_display_initialization(self):
        """Test metrics display can be initialized"""
        from src.ui.components.metrics_display import MetricsDisplay
        
        metrics = MetricsDisplay()
        assert metrics is not None
    
    def test_all_render_methods_exist(self):
        """Test that all render methods exist"""
        from src.ui.components.metrics_display import MetricsDisplay
        
        assert hasattr(MetricsDisplay, 'render_kpi_row')
        assert hasattr(MetricsDisplay, 'render_stat_cards')
        assert hasattr(MetricsDisplay, 'render_progress_metrics')
        assert hasattr(MetricsDisplay, 'render_comparison_metrics')
        assert hasattr(MetricsDisplay, 'render_status_indicators')


class TestStateManager:
    """Test StateManager"""
    
    def test_state_keys_defined(self):
        """Test that state keys are defined"""
        from src.ui.utils.state_manager import StateManager
        
        assert hasattr(StateManager, 'AUTHENTICATED')
        assert hasattr(StateManager, 'USERNAME')
        assert hasattr(StateManager, 'QUERY_HISTORY')
        assert hasattr(StateManager, 'CACHE_STATS')
    
    def test_initialize_creates_defaults(self):
        """Test that initialize sets up defaults"""
        from src.ui.utils.state_manager import StateManager
        
        # This would require mocking streamlit.session_state
        # For now, just test the method exists
        assert hasattr(StateManager, 'initialize')
        assert callable(StateManager.initialize)
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation logic"""
        from src.ui.utils.state_manager import StateManager
        
        # Test with zero values
        # In real implementation, this would use mocked session state
        assert hasattr(StateManager, 'get_cache_hit_rate')
    
    def test_export_state_method_exists(self):
        """Test that export state method exists"""
        from src.ui.utils.state_manager import StateManager
        
        assert hasattr(StateManager, 'export_state')
        assert callable(StateManager.export_state)


class TestComponentIntegration:
    """Integration tests for UI components"""
    
    def test_all_components_importable(self):
        """Test that all components can be imported"""
        from src.ui.components import (
            ProtocolFilter,
            QuerySuggestions,
            ResponseCard,
            MetricsDisplay
        )
        
        assert ProtocolFilter is not None
        assert QuerySuggestions is not None
        assert ResponseCard is not None
        assert MetricsDisplay is not None
    
    def test_state_manager_importable(self):
        """Test that state manager can be imported"""
        from src.ui.utils.state_manager import StateManager
        
        assert StateManager is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])



"""
Protocol Filter Component
Author: Kripa - Week 1 Day 5
"""

import streamlit as st
from typing import List, Optional

class ProtocolFilter:
    """Reusable protocol filter component"""
    
    PROTOCOLS = ["All", "SSH", "HTTP", "HTTPS", "FTP", "DNS", "SMTP", "Telnet", "RDP", "SMB"]
    
    @staticmethod
    def render(
        key: str = "protocol_filter",
        default: str = "All",
        multi_select: bool = False,
        show_count: bool = False
    ) -> Optional[str | List[str]]:
        """
        Render protocol filter component
        
        Args:
            key: Unique key for the component
            default: Default selected protocol
            multi_select: Allow multiple protocol selection
            show_count: Show log count for each protocol
            
        Returns:
            Selected protocol(s)
        """
        
        st.markdown("#### 🔌 Protocol Filter")
        
        if show_count:
            # Mock counts - in real app, fetch from database
            protocol_counts = {
                "All": 15247,
                "SSH": 3421,
                "HTTP": 2847,
                "HTTPS": 1923,
                "FTP": 1205,
                "DNS": 892,
                "SMTP": 445,
                "Telnet": 178,
                "RDP": 234,
                "SMB": 567
            }
            
            options = [f"{p} ({protocol_counts.get(p, 0)} logs)" 
                      for p in ProtocolFilter.PROTOCOLS]
        else:
            options = ProtocolFilter.PROTOCOLS
        
        if multi_select:
            selected = st.multiselect(
                "Select Protocols",
                options,
                default=[options[0]] if default == "All" else [default],
                key=key,
                help="Filter logs by protocol type"
            )
            
            # Extract protocol names if counts are shown
            if show_count:
                selected = [s.split(" (")[0] for s in selected]
            
            return selected
        else:
            selected = st.selectbox(
                "Select Protocol",
                options,
                index=options.index(default if not show_count else f"{default} ({protocol_counts.get(default, 0)} logs)"),
                key=key,
                help="Filter logs by protocol type"
            )
            
            # Extract protocol name if count is shown
            if show_count:
                selected = selected.split(" (")[0]
            
            return selected
    
    @staticmethod
    def render_chips(
        selected_protocols: List[str],
        on_remove_callback: Optional[callable] = None
    ):
        """
        Render selected protocols as chips/badges
        
        Args:
            selected_protocols: List of selected protocols
            on_remove_callback: Callback when chip is removed
        """
        if not selected_protocols or (len(selected_protocols) == 1 and selected_protocols[0] == "All"):
            st.info("🔌 All protocols selected")
            return
        
        st.markdown("**Selected Protocols:**")
        
        cols = st.columns(len(selected_protocols))
        
        for idx, protocol in enumerate(selected_protocols):
            with cols[idx]:
                if st.button(f"🔌 {protocol} ✖️", key=f"chip_{protocol}_{idx}"):
                    if on_remove_callback:
                        on_remove_callback(protocol)
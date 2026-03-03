"""
ICS-LogQueryGPT - Export Page
Author: Kripa
Week 1 Day 4: Data Export Functionality
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

# Page config
st.set_page_config(
    page_title="Export - ICS-LogQueryGPT",
    page_icon="💾",
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

def generate_sample_data():
    """Generate sample export data"""
    return pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=100, freq='H'),
        'ip_address': [f'192.168.1.{i%255}' for i in range(100)],
        'protocol': ['SSH', 'HTTP', 'FTP', 'HTTPS', 'DNS'] * 20,
        'action': ['SUCCESS', 'FAILED', 'SUCCESS', 'FAILED', 'SUCCESS'] * 20,
        'user': ['admin', 'user1', 'operator', 'root', 'guest'] * 20,
        'details': [f'Log entry {i}' for i in range(100)]
    })

def export_to_csv(df):
    """Export dataframe to CSV"""
    return df.to_csv(index=False).encode('utf-8')

def export_to_json(df):
    """Export dataframe to JSON"""
    return df.to_json(orient='records', indent=2).encode('utf-8')

def export_to_markdown(df, title="ICS Log Export"):
    """Export to markdown format"""
    md_content = f"# {title}\n\n"
    md_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += f"**Total Records:** {len(df)}\n\n"
    md_content += "## Data\n\n"
    md_content += df.to_markdown(index=False)
    return md_content.encode('utf-8')

def export_to_text(df):
    """Export to plain text format"""
    text_content = f"ICS-LogQueryGPT Export\n"
    text_content += f"{'='*50}\n\n"
    text_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text_content += f"Total Records: {len(df)}\n\n"
    text_content += df.to_string(index=False)
    return text_content.encode('utf-8')

def main():
    """Main export page"""
    
    check_authentication()
    
    st.title("💾 Export Data")
    st.markdown("Export query results and analytics in multiple formats")
    
    with st.sidebar:
        st.markdown("### ⚙️ Export Settings")
        
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "JSON", "Markdown", "Text"]
        )
        
        include_metadata = st.checkbox("Include metadata", value=True)
        include_timestamp = st.checkbox("Include timestamp in filename", value=True)
        
        st.markdown("---")
        st.markdown("### 📊 Data Source")
        
        data_source = st.radio(
            "Select data to export:",
            ["Current Query Results", "Analytics Data", "Query History", "Custom Selection"]
        )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Preview Data")
        sample_df = generate_sample_data()
        st.dataframe(sample_df.head(10), use_container_width=True)
        st.info(f"📊 Total records available: {len(sample_df)}")
    
    with col2:
        st.markdown("### 📥 Export Options")
        
        st.markdown(f"**Format:** {export_format}")
        st.markdown(f"**Records:** {len(sample_df)}")
        st.markdown(f"**Size:** ~{len(sample_df) * 0.1:.2f} KB")
        
        timestamp_str = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if include_timestamp else ""
        filename = f"ics_logs{timestamp_str}"
        
        if export_format == "CSV":
            data = export_to_csv(sample_df)
            st.download_button(
                label="📥 Download CSV",
                data=data,
                file_name=f"{filename}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        elif export_format == "JSON":
            data = export_to_json(sample_df)
            st.download_button(
                label="📥 Download JSON",
                data=data,
                file_name=f"{filename}.json",
                mime="application/json",
                use_container_width=True
            )
        
        elif export_format == "Markdown":
            data = export_to_markdown(sample_df)
            st.download_button(
                label="📥 Download Markdown",
                data=data,
                file_name=f"{filename}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        elif export_format == "Text":
            data = export_to_text(sample_df)
            st.download_button(
                label="📥 Download Text",
                data=data,
                file_name=f"{filename}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    st.markdown("---")
    st.markdown("### 📝 Export Templates")
    
    template_col1, template_col2, template_col3 = st.columns(3)
    
    with template_col1:
        st.markdown("#### 🔍 Security Report")
        st.markdown("""
        - Failed authentication attempts
        - Suspicious IP addresses
        - Security alerts
        - Recommended actions
        """)
        if st.button("Use Template", key="security_template", use_container_width=True):
            st.success("✅ Security report template applied!")
    
    with template_col2:
        st.markdown("#### 📊 Traffic Analysis")
        st.markdown("""
        - Protocol distribution
        - Top sources/destinations
        - Bandwidth usage
        - Peak hours
        """)
        if st.button("Use Template", key="traffic_template", use_container_width=True):
            st.success("✅ Traffic analysis template applied!")
    
    with template_col3:
        st.markdown("#### ⚠️ Incident Report")
        st.markdown("""
        - Incident timeline
        - Affected systems
        - Impact assessment
        - Mitigation steps
        """)
        if st.button("Use Template", key="incident_template", use_container_width=True):
            st.success("✅ Incident report template applied!")
    
    st.markdown("---")
    st.markdown("### ⏰ Scheduled Exports")
    
    schedule_col1, schedule_col2 = st.columns([2, 1])
    
    with schedule_col1:
        st.markdown("Configure automatic exports for regular reporting")
        
        schedule_enabled = st.checkbox("Enable scheduled exports")
        
        if schedule_enabled:
            frequency = st.selectbox(
                "Export Frequency",
                ["Daily", "Weekly", "Monthly"]
            )
            
            export_time = st.time_input("Export Time")
            
            email_recipients = st.text_input(
                "Email Recipients (comma-separated)",
                placeholder="admin@example.com, security@example.com"
            )
            
            if st.button("💾 Save Schedule", use_container_width=True):
                st.success("✅ Export schedule saved!")
    
    with schedule_col2:
        st.info("""
        **Schedule Status**
        
        Next export: Not scheduled
        
        Last export: Never
        
        Total exports: 0
        """)
    
    st.markdown("---")
    st.markdown("### 📜 Export History")
    
    history_df = pd.DataFrame({
        'Timestamp': [datetime.now() for _ in range(5)],
        'Format': ['CSV', 'JSON', 'Markdown', 'Text', 'CSV'],
        'Records': [100, 250, 75, 150, 200],
        'Status': ['✅ Success'] * 5
    })
    
    st.dataframe(history_df, use_container_width=True)

if __name__ == "__main__":
    main()
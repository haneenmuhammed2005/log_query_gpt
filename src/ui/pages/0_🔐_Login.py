"""
Login Page - User authentication interface
Author: Haneen
Created: Week 5 Day 3
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.user_manager import UserManager
from src.ui.auth.session import SessionManager

# Page configuration
st.set_page_config(
    page_title="Login - ICS-LogQueryGPT",
    page_icon="🔐",
    layout="centered"
)

# Initialize managers
@st.cache_resource
def get_managers():
    """Initialize and cache auth managers"""
    um = UserManager()
    sm = SessionManager()
    return um, sm

um, sm = get_managers()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'session_token' not in st.session_state:
    st.session_state['session_token'] = None

# Check if already authenticated
if st.session_state.get('authenticated', False):
    # Validate session
    session_token = st.session_state.get('session_token')
    user = sm.validate_session(session_token)
    
    if user:
        # Already logged in, show message and redirect option
        st.success(f"✅ Already logged in as **{user['username']}** ({user['role']})")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Go to Query Page", type="primary"):
                st.switch_page("pages/1_🔍_Query_Logs.py")
        with col2:
            if st.button("🚪 Logout"):
                # Destroy session
                sm.destroy_session(session_token)
                st.session_state['authenticated'] = False
                st.session_state['username'] = None
                st.session_state['user_role'] = None
                st.session_state['session_token'] = None
                st.rerun()
        
        st.stop()
    else:
        # Session expired
        st.session_state['authenticated'] = False

# Login UI
st.title("🔐 ICS-LogQueryGPT Login")
st.markdown("---")

# Show info message
st.info("💡 **Default credentials**: Username: `admin` | Password: `admin123`")
st.warning("⚠️ Change default password after first login!")

st.markdown("###")

# Login form
with st.form("login_form"):
    st.subheader("Please enter your credentials")
    
    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        max_chars=50
    )
    
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        max_chars=100
    )
    
    remember_me = st.checkbox("Remember me for 7 days", value=False)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
    with col2:
        clear = st.form_submit_button("🔄 Clear", use_container_width=True)

# Handle form submission
if submit:
    if not username or not password:
        st.error("❌ Please enter both username and password")
    else:
        with st.spinner("Authenticating..."):
            # Authenticate user
            user = um.authenticate(username, password)
            
            if user:
                # Authentication successful
                # Create session
                session_timeout = 10080 if remember_me else 30  # 7 days or 30 min
                sm_temp = SessionManager(timeout_minutes=session_timeout)
                session_token = sm_temp.create_session(user)
                
                # Store in session state
                st.session_state['authenticated'] = True
                st.session_state['username'] = user['username']
                st.session_state['user_role'] = user['role']
                st.session_state['session_token'] = session_token
                
                # Show success
                st.success(f"✅ Login successful! Welcome, **{user['username']}**")
                st.balloons()

                # Show message instead of redirect
                st.info("👉 Query Logs page will be available once Kripa completes frontend!")
                st.markdown("### ✅ Authentication System Working!")
                st.markdown("You are successfully logged in. Session is active.")

                # Show user info
                with st.expander("Session Details"):
                    st.json({
                        'username': user['username'],
                        'role': user['role'],
                        'session_token': st.session_state.get('session_token', 'N/A')[:20] + '...'
                    })
            else:
                # Authentication failed
                st.error("❌ Invalid username or password")

if clear:
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>ICS-LogQueryGPT v1.0 | Secure Authentication</p>
    <p>🔒 All passwords are encrypted with bcrypt</p>
</div>
""", unsafe_allow_html=True)

# Sidebar info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    This is a secure login system for ICS-LogQueryGPT.
    
    **Features:**
    - 🔐 Bcrypt password hashing
    - ⏱️ Session timeout (30 min)
    - 🔄 Remember me option
    - 🛡️ Role-based access
    
    **Roles:**
    - **Admin**: Full access
    - **Analyst**: Query & analysis
    - **Viewer**: Read-only
    """)
    
    st.markdown("---")
    st.markdown("### 📊 System Status")
    active_sessions = sm.get_active_sessions()
    total_users = um.get_user_count()
    
    st.metric("Active Sessions", active_sessions)
    st.metric("Total Users", total_users)
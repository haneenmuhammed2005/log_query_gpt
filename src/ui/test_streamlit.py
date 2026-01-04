import streamlit as st

st.title("🔍 ICS-LogQueryGPT")
st.write("## Test Streamlit App")

user_input = st.text_input("Enter a test message:")

if st.button("Submit"):
    st.success(f"You entered: {user_input}")
    st.balloons()

with st.sidebar:
    st.header("Settings")
    num_logs = st.slider("Number of logs", 1, 100, 10)
    st.write(f"Will retrieve {num_logs} logs")

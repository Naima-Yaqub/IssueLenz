import streamlit as st
from dotenv import load_dotenv
import os  

# Page config
st.set_page_config(
    page_title="IssueLenz",
    page_icon="images/github2.png"
)

load_dotenv()

# Inject custom CSS for better styling
st.markdown("""
    <style>
        .title {text-align: center; color: #2e3a59; font-size: 36px; font-weight: 600;}
        .subtitle {text-align: center; font-size: 18px; color: #5e6a84; margin-bottom: 30px;}
        .button-container {display: flex; justify-content: center; gap: 20px;}
        .stButton>button {background-color: #ADD8E6; color: white; border-radius: 8px; border: none; font-size: 16px;
                          padding: 12px 24px; width: 200px; cursor: pointer; transition: background-color 0.3s;}
        .stButton>button:hover {background-color: #87CEEB;}
    </style>
""", unsafe_allow_html=True)

# Title of the page
st.markdown('<div class="title">🔑 Personal Access Token (PAT) Settings</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Enter your GitHub PAT. It will be stored only for this session.</div>', unsafe_allow_html=True)
pat = st.text_input("Enter your GitHub Personal Access Token:", type="password") # Text input for entering the PAT

if st.button("Save Token"):
    if pat:
        st.session_state.personal_access_token = pat  # Store token in session state
        st.success("✅ Personal Access Token saved successfully!")
        os.environ["PERSONAL_ACCESS_TOKEN"] = pat
    else:
        st.error("⚠️ Please enter a valid token.")
if st.button("Cancel"):
    st.switch_page("locallama.py")
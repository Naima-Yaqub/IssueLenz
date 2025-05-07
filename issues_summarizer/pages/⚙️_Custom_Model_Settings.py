import streamlit as st
import os  

# Page config
st.set_page_config(
    page_title="IssueLenz",
    page_icon="images/github2.png"
)

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
st.markdown('<div class="title">🤖Custom Model Configuration</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Enter your custom model credentials. These will be stored only for this session.</div>', unsafe_allow_html=True)

# Initialize session state for models if not already present
if "models" not in st.session_state:
    st.session_state.models = ["llama3.2", "deepseek->r1.1.5b"]  # Default models with '->' as separator

# Tabs for model selection
tab1, tab2, tab3 = st.tabs(["GPT Integration", "Hugging Face Model", "Deepseek Model Integration"])

def add_model_to_session(model_with_prefix):
    """Helper function to add a model to the session state and persist across pages."""
    if model_with_prefix not in st.session_state.models:
        st.session_state.models.append(model_with_prefix)
        st.session_state["models"] = list(set(st.session_state.models))  # Ensure persistence
        st.success(f"Custom model '{model_with_prefix}' saved!")

with tab1:
    st.markdown('<h3 style="text-align:center;">GPT Model Configuration</h3>', unsafe_allow_html=True)
    custom_model_name = st.text_input("Custom GPT Model Name", key="custom_model_name")
    api_key = st.text_input("API Key", type="password", key="api_key")

    if st.button("Save GPT Model"):
        if custom_model_name:
            model_with_prefix = f"gpt->{custom_model_name}"  # Using '->' as separator
            add_model_to_session(model_with_prefix)
            os.environ["OPENAI_MODEL_NAME"] = custom_model_name
            os.environ["OPENAI_API_KEY"] = api_key

with tab2:
    st.markdown('<h3 style="text-align:center;">Hugging Face Model Configuration</h3>', unsafe_allow_html=True)
    hf_model_name = st.text_input("Hugging Face Model Name", key="hf_model_name")
    hf_api_key = st.text_input("Hugging Face API Key", type="password", key="hf_api_key")
    hf_endpoint = st.text_input("Hugging Face Inference API Endpoint", key="hf_endpoint")

    if st.button("Save Hugging Face Model"):
        if hf_model_name:
            model_with_prefix = f"hf->{hf_model_name}"  # Using '->' as separator
            add_model_to_session(model_with_prefix)
            os.environ["HF_MODEL_NAME"] = hf_model_name
            os.environ["HF_API_KEY"] = hf_api_key
            os.environ["HF_ENDPOINT"] = hf_endpoint

with tab3:
    st.markdown('<h3 style="text-align:center;">Deepseek/Ollama Model Configuration</h3>', unsafe_allow_html=True)
    ds_model_name = st.text_input("Deepseek Model Name", key="ds_model_name")
    ds_api_key = st.text_input("Deepseek API Key", type="password", key="ds_api_key")

    if st.button("Save Deepseek Model"):
        if ds_model_name:
            model_with_prefix = f"ds->{ds_model_name}"  # Using '->' as separator
            add_model_to_session(model_with_prefix)
            os.environ["DS_MODEL_NAME"] = ds_model_name
            os.environ["DS_API_KEY"] = ds_api_key

if st.button("Cancel"):
    st.switch_page("locallama.py")  # Redirect to main page

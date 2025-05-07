import os
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama, OpenAI
from huggingface_hub import InferenceClient

from Extract_owner_and_repo_name import get_owner_repo_from_url, get_date_range_from_user
from fetching_issues import fetch_github_issues, format_issues, fetch_github_labels
from export_summaries import export_summaries

st.set_page_config(
    page_title="IssueLenz",
    page_icon="images/github2.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'About': "This is a web app that helps you summarize issues from a GitHub repository."}
)

load_dotenv()

# Ensure session state for models persists
if "models" not in st.session_state:
    st.session_state.models = ["llama3.2", "deepseek-r1:1.5b","Custom model"]  # Default models

if "persisted_models" in st.session_state:
    st.session_state.models = st.session_state["persisted_models"]

@st.cache_resource
def get_model(model_name):
    prefix, actual_model_name = model_name.split("->", 1) if "->" in model_name else (None, model_name)
    if prefix == "gpt":
        return OpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
    elif prefix == "hf":
        return InferenceClient(model=actual_model_name, token=os.getenv("HF_API_KEY"))
    elif prefix == "ds" or actual_model_name.startswith(("llama", "deepseek")):
        return Ollama(model=actual_model_name)
    else:
        raise ValueError(f"Invalid model: {model_name}")


@st.cache_data(persist=True)
def get_summary(issue_number: int, repo_name: str, model_name: str):
    llm = get_model(model_name)
    issue_text = next((issue for issue in st.session_state.formatted_issues if issue['number'] == issue_number), None)
    if not issue_text:
        return "No issue text found."

    issue_text_str = (
        f"Issue #{issue_text['number']}: {issue_text['title']}\n"
        f"Description: {issue_text['description']}\n"
        f"Created At: {issue_text['created_at']}\n"
        f"Labels: {', '.join(issue_text['labels']) if issue_text['labels'] else 'No label'}"
    )

    if isinstance(llm, InferenceClient):
        return llm.text_generation(issue_text_str, max_length=200)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Summarize the issue clearly and also suggest solution for it."),
        #("system", "You are a helpful assistant. Summarize the GitHub issue clearly, and also suggest a possible solution or next step to resolve it."),
        ("user", "{issues}")
    ])
    return (prompt | llm | StrOutputParser()).invoke({"issues": issue_text_str}).strip()

# Initialize session state variables if not already set
for key in ["summarized_issues", "formatted_issues", "fetch_clicked"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "summarized_issues" else [] if key == "formatted_issues" else False

# Load images
def load_base64_image(image_path):
    return base64.b64encode(open(image_path, "rb").read()).decode()

github_img = load_base64_image("images/github2.png")
ollama_img = load_base64_image("images/llama1.png")
st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="data:image/png;base64,{github_img}" width="60">
            <img src="data:image/png;base64,{ollama_img}" width="50">
            <h1 style="margin: 0; display: inline-block;">IssueLenz: Github Issue Scraper</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""<div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;"><h2>🔍 Input Section</h2>""", unsafe_allow_html=True)
    
    selected_model = st.selectbox("Choose Model", st.session_state.models, index=0)
    
    if selected_model == "Custom model":
        st.switch_page("pages/⚙️_Custom_Model_Settings.py")
    
    repo_url = st.text_input("Repository link:", placeholder="Enter Github Repo Link")
    owner, repo = get_owner_repo_from_url(repo_url) if repo_url else (None, None)
    
    labels = fetch_github_labels(owner, repo) if owner and repo else None
    selected_labels = st.multiselect("Labels (Optional):", options=labels) if labels else None
    
    start_date, end_date = get_date_range_from_user(owner, repo)
    if start_date > end_date:
        st.error("Start date cannot be later than end date!")
    
    export_format = st.selectbox("Choose export format:", ["None", "Excel", "Word", "JSON"])
    
    if st.button("Fetch Issues"):
        st.session_state.fetch_clicked = True
        st.session_state.formatted_issues = format_issues(fetch_github_issues(owner, repo, start_date, end_date, selected_labels), owner, repo) if owner and repo else []

with col2:
    st.markdown("""<div style="background-color: #e6f7ff; padding: 20px; border-radius: 10px;"><h2>📜 Summaries</h2></div>""", unsafe_allow_html=True)
    
    if st.session_state.fetch_clicked and st.session_state.formatted_issues:
        for issue in st.session_state.formatted_issues:
            summary = st.session_state.summarized_issues.get(issue['number'], get_summary(issue['number'], repo, selected_model))
            st.session_state.summarized_issues[issue['number']] = summary  
            
            st.markdown(f"### Issue #{issue['number']}: {issue['title']}")
            st.markdown(f"Labels: {', '.join(issue['labels']) if issue['labels'] else 'No label'}")
            st.markdown(f"Summary: {summary}")
            st.markdown(f"[View Issue on GitHub]({issue['url']})")
            st.write("---")
    
    if st.session_state.fetch_clicked and st.session_state.formatted_issues:
        col3, col4 = st.columns([1, 1])
        with col3:
            if export_format != "None":
                export_summaries(export_format, st.session_state.formatted_issues)
        with col4:
            if st.button("Clear All"):
                st.session_state.clear()
                st.rerun()

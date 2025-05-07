from datetime import datetime, timedelta
from urllib.parse import urlparse
import streamlit as st
import requests

def get_owner_repo_from_url(repo_url):
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 2:
        owner = path_parts[0]
        repo = path_parts[1]
        return owner, repo
    else:
        st.error("Invalid GitHub repository URL")
        return None, None

def get_repo_creation_date(owner, repo):
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url)
        if response.status_code == 200:
            repo_data = response.json()
            creation_date = datetime.strptime(repo_data['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            return creation_date
        else:
            st.error("Failed to fetch repository creation date.")
            return None
    except Exception as e:
        st.error(f"Error fetching repository creation date: {e}")
        return None
    
import streamlit as st
from datetime import datetime, timedelta

import streamlit as st
from datetime import datetime, timedelta

def get_date_range_from_user(owner, repo):
    today = datetime.now()
    one_month_ago = today - timedelta(days=30)

    if owner and repo:
        repo_creation_date = get_repo_creation_date(owner, repo)  # Fetch repo creation date
        if repo_creation_date:
            default_start = one_month_ago
        else:
            default_start = one_month_ago
    else:
        default_start = one_month_ago

    # Separate date input boxes for start and end dates
    start_date = st.date_input(
        "Select start date:",
        value=default_start,
        min_value=datetime(2000, 1, 1),
        max_value=today
    )
    
    end_date = st.date_input(
        "Select end date:",
        value=today,
        min_value=start_date,
        max_value=today
    )
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.min.time())

    return start_datetime, end_datetime
import requests
import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import time

load_dotenv()

# Store the token in session state to persist it across requests
if "personal_access_token" not in st.session_state:
    st.session_state.personal_access_token = os.getenv('PERSONAL_ACCESS_TOKEN', None)

# Store fetched labels in session state to reduce redundant API calls
if "cached_labels" not in st.session_state:
    st.session_state.cached_labels = {}

def check_rate_limit():
    """Check GitHub API rate limit and redirect user to PAT settings if needed."""

    # Ensure personal access token is initialized
    if "personal_access_token" not in st.session_state:
        st.session_state.personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN", "")

    github_token = st.session_state.personal_access_token
    headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}

    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        rate_limit_data = response.json()
        remaining = rate_limit_data["rate"]["remaining"]
        reset_timestamp = rate_limit_data["rate"]["reset"]

        # Convert Unix timestamp to human-readable time
        reset_time = datetime.utcfromtimestamp(reset_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

        if remaining == 0:
            st.warning(f"⚠️ API rate limit exceeded. Try again after **{reset_time}**.")
            st.warning("⚠️ To continue using the app, configure a Personal Access Token (PAT).")

            if st.button("🔑 Configure Personal Access Token"):
                st.switch_page("pages/🔑_Personal_Access_Token_Settings.py")

            return False

        return True
    else:
        st.error(f"❌ Failed to check rate limit. HTTP {response.status_code}")
        return False
    

def fetch_github_issues(owner, repo, since_date, until_date, labels=None):
    """Fetch GitHub issues with proper error handling and date filtering."""
    
    if not check_rate_limit():
        return []

    github_token = st.session_state.personal_access_token
    headers = {
        'User-Agent': "Github-Issues_Scraper_&_Summarizer",
        'Authorization': f'Bearer {github_token}' if github_token else ''
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {
        "since": since_date.isoformat(),
        "state": "all",
        "per_page": 100
    }

    if labels:
        params["labels"] = ",".join(labels)

    issues = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 403:
            st.error("⚠️ Rate limit exceeded. Retrying after reset...")
            return []
        elif response.status_code == 401:
            st.error("❌ Invalid GitHub token. Please check your token.")
            return []
        elif response.status_code != 200:
            st.error(f"❌ Failed to fetch issues. HTTP Status: {response.status_code} - {response.text}")
            return []

        new_issues = response.json()

        if not new_issues:
            break  # No more issues to fetch
        
        # Convert `until_date` to naive datetime
        until_date_dt = until_date.replace(tzinfo=None) if until_date.tzinfo else until_date

        # Filter issues based on `created_at`
        filtered_issues = [
            issue for issue in new_issues 
            if "created_at" in issue and since_date <= datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ") <= until_date_dt
        ]

        issues.extend(filtered_issues)

        # Stop pagination if the last fetched issue is older than `until_date`
        last_issue_date = datetime.strptime(new_issues[-1]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        if last_issue_date < until_date:
            break

        page += 1

    # Count pull requests (PRs have the "pull_request" key in the response)
    pull_requests = sum(1 for issue in issues if "pull_request" in issue)

    # Filter out pull requests from issues
    non_pr_issues = [issue for issue in issues if "pull_request" not in issue]

    # Count open and closed issues (excluding pull requests)
    open_issues = sum(1 for issue in non_pr_issues if issue.get("state") == "open")
    closed_issues = sum(1 for issue in non_pr_issues if issue.get("state") == "closed")

    # Display the result in a styled box
    st.markdown(f"""
    <div style="background-color: #EEF9F1; padding: 10px; border-radius: 5px;">
       <h3 style="color: #3C763D;">✅ Fetched Issues Details</h3>
       <p>📊 <b>Total Fetched Issues:</b> {len(issues)}</p>
       <p>🔄 <b>Pull Requests:</b> {pull_requests}</p>
       <p>🔴 <b>Open Issues:</b> {open_issues}</p>
       <p>🟢 <b>Closed Issues:</b> {closed_issues}</p>
    </div>
    """, unsafe_allow_html=True)

    
    return issues

def fetch_github_labels(owner, repo):
    """Fetch GitHub labels and cache results to optimize performance."""
    
    if "cached_labels" not in st.session_state:
        st.session_state.cached_labels = {}  # Ensure it is initialized

    cache_key = f"{owner}/{repo}"

    if cache_key in st.session_state.cached_labels:
        return st.session_state.cached_labels[cache_key]

    if not check_rate_limit():
        return []

    github_token = st.session_state.personal_access_token
    headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}

    url = f"https://api.github.com/repos/{owner}/{repo}/labels"
    labels = []
    page = 1

    while True:
        params = {"page": page, "per_page": 100}
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            labels.extend([label['name'] for label in data])
            page += 1
        else:
            st.error(f"❌ Failed to fetch labels. HTTP {response.status_code}")
            break

    relevant_keywords = ['bug', 'priority', 'kind', 'enhancement', 'help wanted', 'good first issue']
    relevant_labels = [label for label in labels if any(keyword in label.lower() for keyword in relevant_keywords)]

    # Cache labels for future use
    st.session_state.cached_labels[cache_key] = relevant_labels if relevant_labels else labels
    return st.session_state.cached_labels[cache_key]

def format_issues(issues, owner, repo):
    """Formats issues into a structured dictionary."""
    return [
        {
            "number": issue.get("number"),
            "title": issue.get("title"),
            "description": issue.get("body", "(No description provided)"),
            "created_at": issue.get("created_at", ""),
            "url": f"https://github.com/{owner}/{repo}/issues/{issue.get('number')}",
            "labels": [label['name'] for label in issue.get('labels', [])]
        }
        #for issue in issues if "pull_request" not in issue

        for issue in issues if issue.get("state") == "open" and "pull_request" not in issue
    ]

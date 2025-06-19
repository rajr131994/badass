import os
import requests
from vertexai.preview.generative_models import GenerativeModel
import vertexai
import json

# Init Gemini
vertexai.init(project="BADASS", location="us-central1")
model = GenerativeModel("gemini-1.5-pro")

# Load secrets from environment
JIRA_TOKEN = os.getenv("ATATT3xFfGF0w2Bj0bnXtD4lQ5FE4fHC92sjgZIWT0hdWXv2-saLffMqgLgT9smzdpdvf7nePnsj0-qDFrk55HegKI1I8I1DfpGHaSCj3BuPb0nCG2tV-Q7wQyAbK-zZbHnHIVe6zx2qUMiumgFCKCAHyASjs0sdwfFaTG7DnbWo4yCxiSslWoY=E6F2F661")
JIRA_DOMAIN = os.getenv("badassbot.atlassian.net")
CONFLUENCE_TOKEN = os.getenv("ATATT3xFfGF0w2Bj0bnXtD4lQ5FE4fHC92sjgZIWT0hdWXv2-saLffMqgLgT9smzdpdvf7nePnsj0-qDFrk55HegKI1I8I1DfpGHaSCj3BuPb0nCG2tV-Q7wQyAbK-zZbHnHIVe6zx2qUMiumgFCKCAHyASjs0sdwfFaTG7DnbWo4yCxiSslWoY=E6F2F661")
CONFLUENCE_SPACE = os.getenv("badass")
CONFLUENCE_DOMAIN = os.getenv("blsi.atlassian.net/wiki")
TICKET_ID = os.getenv("OPS-5")  # e.g., ENG-100

# Get JIRA Issue
jira_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{TICKET_ID}"
headers = {"Authorization": f"Bearer {JIRA_TOKEN}", "Accept": "application/json"}
issue = requests.get(jira_url, headers=headers).json()

title = issue["fields"]["summary"]
desc = issue["fields"].get("description", {}).get("content", [{}])[0]
reporter = issue["fields"]["reporter"]["displayName"]

# Prompt Gemini
prompt = f"""
Generate a documentation page for this JIRA ticket:

Title: {title}
Description: {desc}
Reporter: {reporter}
JIRA Link: https://{JIRA_DOMAIN}/browse/{TICKET_ID}

Sections: Overview, Context, Steps, Owners, References
"""

response = model.generate_content(prompt)
confluence_content = response.text

# Post to Confluence
confluence_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/"
headers = {
    "Authorization": f"Bearer {CONFLUENCE_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "type": "page",
    "title": f"[AutoDoc] {title}",
    "space": {"key": CONFLUENCE_SPACE},
    "body": {
        "storage": {
            "value": confluence_content,
            "representation": "storage"
        }
    }
}
res = requests.post(confluence_url, headers=headers, json=payload)
print(res.status_code, res.json())

import os
import requests
from vertexai.preview.generative_models import GenerativeModel
import vertexai
import json

# Init Gemini
vertexai.init(project="BADASS", location="us-central1")
model = GenerativeModel("gemini-2.0-flash")

# Load secrets from environment
JIRA_TOKEN = os.getenv("ATATT3xFfGF06ZVLWXo4-kAbV5tfJ4A9EqYjBBML4tz9AR6T8ZEZOjxY6o9vqLj28J5WgJtqFSEXXj7sMk7Q7xRF23oF73uylZKBfyHtQr5LiiQxqiuD7Lv7MHUUBseq3obmGYUMrVbQAqm89Lhf2FT-95MFSR0ReJki_099Ns0AaW9hQevc-U4=CFC639D9")
JIRA_DOMAIN = os.getenv("badassbot.atlassian.net")
CONFLUENCE_TOKEN = os.getenv("ATATT3xFfGF06ZVLWXo4-kAbV5tfJ4A9EqYjBBML4tz9AR6T8ZEZOjxY6o9vqLj28J5WgJtqFSEXXj7sMk7Q7xRF23oF73uylZKBfyHtQr5LiiQxqiuD7Lv7MHUUBseq3obmGYUMrVbQAqm89Lhf2FT-95MFSR0ReJki_099Ns0AaW9hQevc-U4=CFC639D9")
CONFLUENCE_SPACE = os.getenv("badass")
CONFLUENCE_DOMAIN = os.getenv("badassbot.atlassian.net/wiki")
TICKET_ID = os.getenv("OPS-5")  # e.g., ENG-100

print("JIRA_DOMAIN:", os.getenv("JIRA_DOMAIN"))
print("TICKET_ID:", os.getenv("TICKET_ID"))

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

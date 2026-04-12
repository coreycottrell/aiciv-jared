#!/usr/bin/env python3
"""
Google Tag Manager API Setup and Tag Creation

This script uses the GTM API to programmatically add tags.
Requires OAuth2 credentials (not service account) with GTM access.

Setup:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a project or select existing one
3. Enable "Tag Manager API"
4. Create OAuth 2.0 Client ID (Desktop application)
5. Download credentials as client_secrets.json
6. Place in .credentials/gtm_client_secrets.json
7. Run this script - it will open browser for OAuth flow
"""

import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configuration
CREDENTIALS_DIR = "/home/jared/projects/AI-CIV/aether/.credentials"
CLIENT_SECRETS_FILE = f"{CREDENTIALS_DIR}/gtm_client_secrets.json"
TOKEN_FILE = f"{CREDENTIALS_DIR}/gtm_token.pickle"

# GTM Configuration
GTM_ACCOUNT_ID = "6007694896"  # Account ID from GTM URL
GTM_CONTAINER_ID = "190655399"  # Container ID from GTM URL
WORKSPACE_ID = "2"  # Default workspace

# Scopes needed for GTM API
SCOPES = [
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    'https://www.googleapis.com/auth/tagmanager.publish'
]

# Tags to create
TAGS = [
    {
        "name": "GA4 - PureBrain",
        "type": "googtag",  # Google Tag type ID
        "parameter": [
            {
                "type": "template",
                "key": "tagId",
                "value": "G-86325WBT3P"
            }
        ],
        "firingTriggerId": ["2147479553"]  # All Pages trigger ID (default)
    },
    {
        "name": "Search Console Verification",
        "type": "html",  # Custom HTML type ID
        "parameter": [
            {
                "type": "template",
                "key": "html",
                "value": '<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />'
            }
        ],
        "firingTriggerId": ["2147479553"]
    },
    {
        "name": "Microsoft Clarity",
        "type": "html",
        "parameter": [
            {
                "type": "template",
                "key": "html",
                "value": '''<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "viy9bnc56x");
</script>'''
            }
        ],
        "firingTriggerId": ["2147479553"]
    }
]


def get_credentials():
    """Get valid credentials, refreshing if necessary."""
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"\nERROR: Client secrets file not found at: {CLIENT_SECRETS_FILE}")
                print("\nTo set up GTM API access:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create/select a project")
                print("3. Enable 'Tag Manager API'")
                print("4. Go to APIs & Services > Credentials")
                print("5. Create OAuth 2.0 Client ID (Desktop application)")
                print("6. Download and save as: gtm_client_secrets.json")
                print(f"7. Place in: {CREDENTIALS_DIR}/")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def create_tag(service, account_id, container_id, workspace_id, tag_config):
    """Create a tag in GTM."""
    parent = f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"

    try:
        tag = service.accounts().containers().workspaces().tags().create(
            parent=parent,
            body=tag_config
        ).execute()
        print(f"Created tag: {tag['name']} (ID: {tag['tagId']})")
        return tag
    except Exception as e:
        print(f"Error creating tag {tag_config['name']}: {e}")
        return None


def publish_container(service, account_id, container_id, workspace_id, version_name):
    """Create a version and publish it."""
    parent = f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"

    try:
        # Create version
        version = service.accounts().containers().workspaces().create_version(
            parent=parent,
            body={
                "name": version_name,
                "notes": "Added GA4, Search Console Verification, and Microsoft Clarity tags"
            }
        ).execute()

        version_id = version['containerVersion']['containerVersionId']
        print(f"Created version: {version_name} (ID: {version_id})")

        # Publish version
        container_path = f"accounts/{account_id}/containers/{container_id}"
        published = service.accounts().containers().versions().publish(
            path=f"{container_path}/versions/{version_id}"
        ).execute()

        print(f"Published! Live version: {published.get('containerVersion', {}).get('containerVersionId')}")
        return published
    except Exception as e:
        print(f"Error publishing: {e}")
        return None


def list_existing_tags(service, account_id, container_id, workspace_id):
    """List existing tags in the workspace."""
    parent = f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"

    try:
        tags = service.accounts().containers().workspaces().tags().list(
            parent=parent
        ).execute()
        return tags.get('tag', [])
    except Exception as e:
        print(f"Error listing tags: {e}")
        return []


def get_all_pages_trigger_id(service, account_id, container_id, workspace_id):
    """Find the All Pages trigger ID."""
    parent = f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"

    try:
        triggers = service.accounts().containers().workspaces().triggers().list(
            parent=parent
        ).execute()

        for trigger in triggers.get('trigger', []):
            if trigger.get('name') == 'All Pages':
                return trigger['triggerId']

        # If not found, return the default All Pages trigger ID
        return "2147479553"
    except Exception as e:
        print(f"Error getting triggers: {e}")
        return "2147479553"


def main():
    print("="*60)
    print("Google Tag Manager API - Add Analytics Tags")
    print("="*60)

    # Get credentials
    creds = get_credentials()
    if not creds:
        return

    # Build service
    service = build('tagmanager', 'v2', credentials=creds)

    print(f"\nTarget container: GTM-WTDXL4VJ")
    print(f"Account ID: {GTM_ACCOUNT_ID}")
    print(f"Container ID: {GTM_CONTAINER_ID}")

    # Get All Pages trigger ID
    trigger_id = get_all_pages_trigger_id(service, GTM_ACCOUNT_ID, GTM_CONTAINER_ID, WORKSPACE_ID)
    print(f"All Pages trigger ID: {trigger_id}")

    # List existing tags
    existing = list_existing_tags(service, GTM_ACCOUNT_ID, GTM_CONTAINER_ID, WORKSPACE_ID)
    existing_names = [t.get('name') for t in existing]
    print(f"\nExisting tags: {existing_names}")

    # Create tags
    print("\nCreating tags...")
    created = []
    for tag_config in TAGS:
        # Update trigger ID
        tag_config['firingTriggerId'] = [trigger_id]

        # Skip if already exists
        if tag_config['name'] in existing_names:
            print(f"Skipping {tag_config['name']} - already exists")
            continue

        tag = create_tag(service, GTM_ACCOUNT_ID, GTM_CONTAINER_ID, WORKSPACE_ID, tag_config)
        if tag:
            created.append(tag)

    # Publish if tags were created
    if created:
        print(f"\nPublishing {len(created)} new tags...")
        publish_container(
            service,
            GTM_ACCOUNT_ID,
            GTM_CONTAINER_ID,
            WORKSPACE_ID,
            "Added GA4, Search Console, Clarity"
        )
    else:
        print("\nNo new tags to publish.")

    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()

# Google Drive Upload via Domain-Wide Delegation

**Date:** 2026-03-20
**Type:** technique
**Topic:** Uploading to purebrain@puremarketing.ai Drive when service account has zero quota

## Context

Service account `aether-drive-access@aether-integration.iam.gserviceaccount.com` has a storage quota of 0 bytes. Any file upload attempt via service account credentials returns:
  HttpError 403: The user's Drive storage quota has been exceeded

This blocks uploads even to folders OWNED by purebrain@puremarketing.ai where the SA has writer access. The quota error applies to the API caller, not the folder owner.

## Solution: Domain-Wide Delegation (DWD)

The service account has DWD configured for the puremarketing.ai Google Workspace domain.

  creds = Credentials.from_service_account_file(
      '.credentials/google-drive-service-account.json',
      scopes=['https://www.googleapis.com/auth/drive'],
      subject='purebrain@puremarketing.ai'  # impersonate this account
  )
  service = build('drive', 'v3', credentials=creds)

Storage quota on purebrain: ~30TB limit, ~10GB used. Plenty of headroom.

## When to Apply

Any time you need to upload files to Google Drive as purebrain@puremarketing.ai.
The service account CANNOT upload on its own — always use DWD impersonation.

## Dead Ends to Avoid

- Uploading directly as service account: quota is 0, always fails
- Uploading to purebrain-owned folder as SA: still fails (quota is on uploader, not folder owner)
- OAuth2 flow: no oauth-token.json exists, no oauth-credentials.json for setup

## Data Room Created

Root folder ID: 1z7Tj0oPxhXvUjJapljYZ9h2akeEwL4jj
Link: https://drive.google.com/drive/folders/1z7Tj0oPxhXvUjJapljYZ9h2akeEwL4jj
15 docs uploaded as Google Docs (convert .md via mimeType: application/vnd.google-apps.document)

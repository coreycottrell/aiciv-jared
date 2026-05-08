# Google Drive Service Accounts for Chy and Morphe

**Date**: 2026-04-23
**Time needed**: ~10 minutes
**What this does**: Creates separate Google Drive access for each AI so we have individual audit trails

---

## What We Have Now

Aether already has a service account in the Google Cloud project called **aether-integration**:
- Email: `aether-drive-access@aether-integration.iam.gserviceaccount.com`

We need two more, same project:
- `chy-drive-access@aether-integration.iam.gserviceaccount.com`
- `morphe-drive-access@aether-integration.iam.gserviceaccount.com`

---

## Step-by-Step: Create Each Service Account

Do this process TWICE -- once for Chy, once for Morphe.

### Part A: Create the Service Account

1. Go to: https://console.cloud.google.com
2. At the top of the page, click the project dropdown (it may say "aether-integration" already)
3. Select **aether-integration** from the list
4. In the left sidebar, click **IAM & Admin**
5. Then click **Service Accounts**
6. You should see `aether-drive-access` already listed here -- that confirms you are in the right project
7. Click the **+ CREATE SERVICE ACCOUNT** button at the top

### Part B: Fill in the Details

8. **Service account name**: `chy-drive-access` (first time) or `morphe-drive-access` (second time)
9. **Service account ID**: This auto-fills from the name -- just confirm it looks right
10. **Description**: `Google Drive access for Chy AI` or `Google Drive access for Morphe AI`
11. Click **CREATE AND CONTINUE**

### Part C: Permissions (Skip This Step)

12. On the "Grant this service account access to project" screen -- you do NOT need to add any roles here
13. Just click **CONTINUE**

### Part D: Grant Users Access (Skip This Step Too)

14. On the "Grant users access to this service account" screen -- leave blank
15. Click **DONE**

### Part E: Download the Key File

16. You are back on the Service Accounts list. Click on the account you just created (e.g., `chy-drive-access`)
17. Click the **KEYS** tab at the top
18. Click **ADD KEY** then **Create new key**
19. Select **JSON** format
20. Click **CREATE**
21. A `.json` file downloads to your computer automatically -- **save this file, you will need it**
22. Repeat for the second account

---

## Step-by-Step: Enable Drive API (One-Time -- May Already Be Done)

Since Aether already uses Drive, this is probably already enabled. But just to be safe:

1. In the left sidebar, click **APIs & Services** then **Enabled APIs & services**
2. Search for "Google Drive API"
3. If it says "ENABLED" you are good -- skip ahead
4. If not, click it and click **ENABLE**

---

## Step-by-Step: Share Drive Folders

Each service account needs access to the Drive folders it will use. This works just like sharing a folder with a person.

For each new service account email:

1. Go to Google Drive (https://drive.google.com)
2. Right-click the folder you want to share
3. Click **Share**
4. Paste the service account email:
   - `chy-drive-access@aether-integration.iam.gserviceaccount.com`
   - `morphe-drive-access@aether-integration.iam.gserviceaccount.com`
5. Set permission to **Editor** (so they can create/upload files)
6. Uncheck "Notify people" (service accounts cannot receive email notifications)
7. Click **Share**

### Which Folders to Share

Share the same folders that Aether currently has access to. At minimum:
- The main shared Drive folder (root level)
- Any team-specific folders Chy/Morphe need to write to
- The Never Forget folder
- Content/exports folders

**Tip**: If you shared a parent folder, all subfolders inherit access. So sharing one top-level folder may be enough.

---

## Step-by-Step: Deploy the Key Files

Once you have the two downloaded JSON files:

### For Chy

1. Send me the `chy-drive-access` JSON file (via portal or Telegram)
2. I will place it at: `/home/chy/.credentials/google-drive-service-account.json` (or wherever Chy's credentials live)
3. File permissions will be set to owner-only (chmod 600)

### For Morphe

1. Send me the `morphe-drive-access` JSON file
2. Same process -- placed in Morphe's credentials directory
3. Same permissions lockdown

**IMPORTANT**: After sending, delete the JSON files from your Downloads folder. These are sensitive credentials.

---

## Verification

After setup, I will verify each account can:
- List files in shared folders
- Create a test file
- Read existing files

I will confirm back to you when each AI has working Drive access.

---

## Summary Checklist

- [ ] Create `chy-drive-access` service account in Google Cloud Console
- [ ] Download its JSON key file
- [ ] Create `morphe-drive-access` service account in Google Cloud Console
- [ ] Download its JSON key file
- [ ] Share relevant Drive folders with both new email addresses
- [ ] Send both JSON files to Aether for deployment
- [ ] Delete JSON files from your Downloads folder
- [ ] Aether confirms both accounts are working

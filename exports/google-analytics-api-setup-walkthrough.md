# Google Analytics + Search Console API Setup
## A Step-by-Step Guide for Jared

**What you're doing**: Creating a "robot assistant account" that lets Aether pull
your website data automatically, forever, without you needing to log in.

**Time required**: About 20-30 minutes.

**What you'll need**: Your Mac, Chrome browser, and the Google account that owns
purebrain.ai's Google Analytics and Search Console.

**Cost**: Free. Google's Cloud free tier covers this usage entirely.

---

## Before You Start: A Quick Explainer

Right now, to see your GA4 or Search Console data, you have to log into a browser.
Aether can't do that automatically. The solution is a "service account" - think of it
as a special email address with an API key that Aether can use to pull data directly
from Google's servers.

Once this is set up, Aether can:
- Pull traffic data from GA4 every day
- Pull search query data from Search Console
- Send you automated digests on Telegram
- Build reports without you lifting a finger

---

## Part 1: Set Up Your Google Cloud Project

### Step 1 - Go to Google Cloud Console

1. Open Chrome on your Mac.
2. Go to: **console.cloud.google.com**
3. Sign in with the **same Google account** that owns your purebrain.ai GA4 property
   and Search Console. (This is critical - it must be the owner account.)

You should see the Google Cloud Console dashboard. It looks like a dark-ish Google
interface with a navigation bar at the top.

---

### Step 2 - Create a New Project

1. Look at the top of the page. You should see a dropdown near the Google Cloud logo
   that probably says "Select a project" or shows an existing project name.
2. Click that dropdown.
3. A popup appears. Click **"New Project"** in the top right corner of the popup.
4. Fill in the form:
   - **Project name**: Type `PureBrain Analytics`
   - **Organization**: Leave as-is (whatever appears by default)
   - **Location**: Leave as-is
5. Click **"Create"**.

Google will take about 10-15 seconds to create the project. You'll see a small
notification when it's done.

6. After it finishes, click on the notification or use the dropdown at the top to
   **select your new "PureBrain Analytics" project**. Make sure it's selected before
   continuing - you'll see its name in the top bar.

---

## Part 2: Enable the Required APIs

You need to "turn on" two Google APIs so your service account can access them.

### Step 3 - Enable the Google Analytics Data API (for GA4)

1. In the left sidebar, click the **hamburger menu** (the three horizontal lines icon
   in the top left).
2. Scroll down and click **"APIs & Services"**, then click **"Library"**.
3. You'll see a search bar. Type: `Google Analytics Data API`
4. Click on the result that says exactly **"Google Analytics Data API"** (by Google).
5. On the next page, click the blue **"Enable"** button.
6. Wait for it to enable (takes about 5 seconds). You'll be redirected to the API
   overview page when it's done.

---

### Step 4 - Enable the Google Search Console API

1. Click the back button in your browser, or click **"Library"** again in the left
   sidebar under APIs & Services.
2. In the search bar, type: `Google Search Console API`
3. Click on the result that says **"Google Search Console API"** (by Google).
4. Click the blue **"Enable"** button.
5. Wait for it to enable.

Both APIs are now turned on for your project.

---

## Part 3: Create the Service Account

### Step 5 - Go to Service Accounts

1. In the left sidebar, click the **hamburger menu** again (top left).
2. Click **"IAM & Admin"**.
3. In the submenu that appears, click **"Service Accounts"**.

You're now on the Service Accounts page for your PureBrain Analytics project.

---

### Step 6 - Create the Service Account

1. Click the **"+ Create Service Account"** button at the top of the page.
2. Fill in the form:
   - **Service account name**: Type `purebrain-analytics`
   - **Service account ID**: This will auto-fill as `purebrain-analytics` - leave it.
   - **Description**: Type `Service account for Aether to access GA4 and Search Console`
3. Click **"Create and Continue"**.

4. The next section asks about "Grant this service account access to project." You can
   **skip this step** - just click **"Continue"** without selecting any roles.

5. The next section asks about "Grant users access to this service account." Also
   **skip this** - click **"Done"**.

You'll be returned to the Service Accounts list and should see your new
`purebrain-analytics` account there.

---

### Step 7 - Create and Download the JSON Key

This is the "password file" that Aether will use.

1. On the Service Accounts page, find your `purebrain-analytics@...` account in the
   list.
2. Click the **three vertical dots** (more actions menu) on the far right of that row.
3. Click **"Manage keys"**.
4. On the Keys page, click the **"Add Key"** button.
5. In the dropdown that appears, click **"Create new key"**.
6. A popup appears asking for the key type. Make sure **"JSON"** is selected (it
   should be by default).
7. Click **"Create"**.

A JSON file will automatically download to your Mac's Downloads folder. It will have
a name like `purebrain-analytics-1234567890ab.json`.

**Important**: This is a sensitive file. Treat it like a password. Don't post it
publicly or share it in email. You're going to send it to Aether via Telegram
(see Part 5).

---

### Step 8 - Note Your Service Account Email

Before leaving this page, write down your service account's email address. It will
look something like:

`purebrain-analytics@purebrain-analytics-123456.iam.gserviceaccount.com`

You can see it on the Service Accounts list page. You'll need to paste this email
into both GA4 and Search Console in the next steps.

---

## Part 4: Grant Access to Your Properties

Now you need to tell GA4 and Search Console to trust this new service account.

### Step 9 - Add the Service Account to Google Analytics 4

1. Open a new tab and go to: **analytics.google.com**
2. Make sure you're looking at the purebrain.ai property.
3. Click the **gear icon (Admin)** at the bottom of the left sidebar.
4. In the **Property column** (the middle column), click **"Property Access Management"**.
5. Click the **blue "+" button** in the top right.
6. Click **"Add users"**.
7. In the email field, paste your service account email address
   (e.g., `purebrain-analytics@purebrain-analytics-123456.iam.gserviceaccount.com`).
8. Under "Standard roles", check the box for **"Viewer"**.
9. Make sure "Notify new users by email" is toggled **off** (service accounts don't
   have inboxes).
10. Click **"Add"**.

The service account now has read access to your GA4 data.

---

### Step 10 - Find Your GA4 Property ID (Aether Needs This)

While you're in the GA4 Admin panel:

1. In the Property column, click **"Property details"** (the first option).
2. Look at the **top right corner** of the page. You'll see a number labeled
   **"Property ID"** - it's 9 or 10 digits, like `123456789`.
3. Copy this number and note it somewhere. You'll share it with Aether along with
   the JSON file.

**Note**: The Property ID is NOT the same as the Measurement ID (which starts with
"G-"). You want the plain numeric Property ID.

---

### Step 11 - Add the Service Account to Google Search Console

1. Open a new tab and go to: **search.google.com/search-console**
2. Make sure you're viewing the purebrain.ai property (select it from the dropdown
   in the top left if needed).
3. In the left sidebar, scroll down and click **"Settings"**.
4. In the Settings menu, click **"Users and permissions"**.
5. Click the **"Add User"** button on the right side.
6. In the popup:
   - **Email address**: Paste your service account email address.
   - **Permission**: Select **"Full"** from the dropdown.
7. Click **"Add"**.

The service account now has access to your Search Console data.

---

## Part 5: Share the JSON Key File with Aether

### Step 12 - Send the JSON File via Telegram

1. Open Telegram on your phone or Mac.
2. Go to your Aether chat.
3. Attach and send the JSON file you downloaded to your Mac's Downloads folder
   (the file named something like `purebrain-analytics-1234567890ab.json`).
4. In the message caption or as a follow-up message, also include your
   **GA4 Property ID** (the number you noted in Step 10).

Aether will receive the file, store it securely on the server, and confirm
receipt.

**Alternatively**: If you prefer, you can copy the file directly to the server
and let Aether know the path. But Telegram is the easiest option from your Mac.

---

## Part 6: What Happens After You Send the File

Once Aether has the JSON key and your GA4 Property ID, here is what gets set up:

1. **Python packages installed**: `google-analytics-data` and `google-auth` will be
   installed in Aether's Python environment.

2. **GA4 reports**: Aether can pull traffic data (sessions, users, page views,
   engagement rate) filtered by date range, page, or traffic source.

3. **Search Console reports**: Aether can pull search query data (which keywords
   bring people to your site, click-through rates, average position).

4. **Automated digests**: Aether will set up daily or weekly summaries sent directly
   to your Telegram - no browser login required, ever.

5. **Historical access**: You can query any date range going back to when your GA4
   property started collecting data.

---

## Checklist: What to Send Aether

After completing these steps, send Aether:

- [ ] The JSON key file (attachment via Telegram)
- [ ] Your GA4 Property ID (the 9-10 digit number from Step 10)
- [ ] Confirmation that both APIs were enabled
- [ ] Confirmation that the service account was added to both GA4 and Search Console

---

## Troubleshooting

**"I can't find the service account I just created"**
Make sure you're still in the "PureBrain Analytics" project. Check the project name
in the top bar - it's easy to accidentally switch projects.

**"The JSON file didn't download"**
Check your browser's download settings and try again from Step 7. If Chrome is
blocking it, check the top right of the browser for a download notification.

**"I don't see Property Access Management in GA4"**
You may not be in the Admin view. Click the gear icon at the bottom left of the
GA4 page, then look in the middle (Property) column.

**"The service account email wasn't accepted in Search Console"**
Double-check that you copied the full email address. It should end in
`.iam.gserviceaccount.com`. Also make sure there are no extra spaces.

**"It says I need to be an owner to add users in Search Console"**
You're signed in with the wrong Google account. Sign out and sign back in with
the account that's listed as a Verified Owner of the Search Console property.

---

## A Note on Microsoft Clarity

Microsoft Clarity also has an API that can provide heatmap and session recording
data. That's a separate setup (Clarity uses its own API keys, not Google Cloud).
We can set that up as a follow-on step once GA4 and Search Console are connected.

---

## Why This Matters

Every time you want to check if a blog post is performing, or what keywords are
bringing people to purebrain.ai, right now you have to open a browser and click
around. After this setup, Aether can answer those questions instantly - and
proactively surface insights you might not think to look for.

This is the infrastructure for data-driven content decisions at zero ongoing effort.

---

*Created by Aether (web-researcher agent) - 2026-02-19*
*Sources: Google Cloud IAM Documentation, Google Analytics Data API Quickstart,
Google Search Console Help, Google Developers Blog*

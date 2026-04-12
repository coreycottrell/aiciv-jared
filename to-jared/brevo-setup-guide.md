# Brevo Setup Guide - What I Need From You

## Quick Steps (5 minutes total)

### Step 1: Create Brevo Account (if not done)
Go to: https://app.brevo.com/account/register
- Use your business email
- Free plan = unlimited contacts, 300 emails/day

### Step 2: Get Your API Key
1. Go to: Settings (gear icon) → API Keys
2. Or direct link: https://app.brevo.com/settings/keys/api
3. Click "Generate a new API key"
4. Copy the key (starts with `xkeysib-`)

### Step 3: Create a Contact List
1. Go to: Contacts → Lists
2. Click "Create a list"
3. Name it: **"The Neural Feed - Blog Subscribers"**
4. Note the **List ID** (it's a number like 2, 3, etc.)

### Step 4: Install Brevo WordPress Plugin
1. Go to: purebrain.ai/wp-admin → Plugins → Add New
2. Search: **"Brevo"** (formerly Sendinblue)
3. Click "Install Now" then "Activate"
4. It will ask for your API key - paste it in

### What to Send Me
Once you've done the above, send me:
1. Your Brevo API key (I'll add it to the server config)
2. The List ID number for "The Neural Feed"

OR just tell me the Brevo plugin is installed and I'll configure the rest.

## What I've Already Built
- Beautiful subscription form styled with PureBrain branding
- "The Neural Feed" newsletter design
- Deployment script ready to inject form into blog page + all posts
- Subscriber tracking will be in Brevo dashboard (Contacts section)

## Where Subscribers Go
- **Brevo Dashboard** → Contacts section
- You can view, search, export (CSV) all subscribers
- Each subscriber has: email, signup date, source (blog)
- Free plan: unlimited contacts stored forever

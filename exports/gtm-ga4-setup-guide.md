# GTM + GA4 Conversion Events Setup Guide
**PureBrain.ai — GA4 Measurement ID: G-86325WBT3P**
**Prepared by**: dept-marketing-advertising (Pure Technology CMO)
**Date**: 2026-03-03

---

## Overview

This guide sets up 5 GA4 conversion events in Google Tag Manager (GTM) for purebrain.ai. These events give you full-funnel visibility: from first assessment click to newsletter signup to paid purchase.

**Two options:**
1. **Fast path**: Import the `gtm-container-import.json` file directly into GTM (5 minutes)
2. **Manual path**: Follow the step-by-step instructions below for each tag

---

## Prerequisites

Before starting, confirm you have:
- [ ] GTM account with Editor access on the purebrain.ai container
- [ ] GA4 property with Measurement ID: `G-86325WBT3P`
- [ ] GTM container snippet already installed on purebrain.ai (verify at: Tag Assistant)
- [ ] The `gtm-datalayer-events.js` snippets installed on the site (see File 3)

---

## Option A: Import the Container JSON (Recommended)

1. Open Google Tag Manager at `tagmanager.google.com`
2. Select your purebrain.ai container
3. Click **Admin** (top navigation, gear icon)
4. Under "Container" column, click **Import Container**
5. Click **Choose container file** and upload `gtm-container-import.json`
6. Select **Merge** (not Overwrite) to preserve any existing tags
7. Select **Rename conflicting tags** if prompted
8. Click **Confirm**
9. Review the imported tags in the Tags panel
10. Click **Submit** to publish the new version
11. Add a version note: "GA4 conversion events — 5 events, G-86325WBT3P"

After import, verify by clicking **Preview** and testing each event trigger.

---

## Option B: Manual Setup (Step-by-Step)

### Step 1: Create the GA4 Configuration Tag

This tag initializes GA4 on every page. It must fire on all pages before any event tags.

**In GTM:**
1. Go to **Tags** > **New**
2. Name it: `GA4 - Configuration`
3. Click **Tag Configuration** > choose **Google Analytics: GA4 Configuration**
4. Measurement ID: `G-86325WBT3P`
5. Under **Triggering**, click the + button
6. Select **All Pages** (Pageview trigger)
7. Save

---

### Step 2: Create Required Variables

You need two built-in variables enabled. Go to **Variables** > **Configure** (Built-In Variables) and enable:
- **Page URL** (`{{Page URL}}`)
- **Event** (`{{Event}}`)

Then create these User-Defined Variables:

#### Variable 1: DLV - form_name
- Type: **Data Layer Variable**
- Variable Name: `form_name`
- Name it: `DLV - form_name`

#### Variable 2: DLV - interaction_type
- Type: **Data Layer Variable**
- Variable Name: `interaction_type`
- Name it: `DLV - interaction_type`

#### Variable 3: DLV - transaction_id
- Type: **Data Layer Variable**
- Variable Name: `transaction_id`
- Name it: `DLV - transaction_id`

#### Variable 4: DLV - value
- Type: **Data Layer Variable**
- Variable Name: `value`
- Name it: `DLV - value`

#### Variable 5: DLV - currency
- Type: **Data Layer Variable**
- Variable Name: `currency`
- Name it: `DLV - currency`

#### Variable 6: DLV - items
- Type: **Data Layer Variable**
- Variable Name: `items`
- Name it: `DLV - items`

#### Variable 7: DLV - signup_source
- Type: **Data Layer Variable**
- Variable Name: `signup_source`
- Name it: `DLV - signup_source`

#### Variable 8: DLV - assessment_type
- Type: **Data Layer Variable**
- Variable Name: `assessment_type`
- Name it: `DLV - assessment_type`

---

### Step 3: Create the 5 Triggers

#### Trigger 1: Form Submission Trigger
1. Go to **Triggers** > **New**
2. Name: `Trigger - Form Submission`
3. Type: **Form Submission**
4. Check **Wait for Tags** (2000ms) and **Check Validation**
5. Fire on: **All Forms**
6. Save

#### Trigger 2: Chatbox Interaction Trigger
1. Go to **Triggers** > **New**
2. Name: `Trigger - Chatbox Interaction`
3. Type: **Custom Event**
4. Event name: `chatbox_interaction`
5. Fire on: **All Custom Events**
6. Save

#### Trigger 3: Purchase Trigger
1. Go to **Triggers** > **New**
2. Name: `Trigger - Purchase`
3. Type: **Custom Event**
4. Event name: `purchase`
5. Fire on: **All Custom Events**
6. Save

#### Trigger 4: Assessment Start Trigger

**Option A — URL-based (no dataLayer needed):**
1. Go to **Triggers** > **New**
2. Name: `Trigger - Assessment Start`
3. Type: **Page View**
4. Fire on: **Some Page Views**
5. Condition: `Page URL` contains `/assessment` OR `Page Path` contains `assessment`
6. Save

**Option B — dataLayer event (requires JS snippet):**
1. Type: **Custom Event**
2. Event name: `assessment_start`
3. Fire on: **All Custom Events**

#### Trigger 5: Newsletter Signup Trigger
1. Go to **Triggers** > **New**
2. Name: `Trigger - Newsletter Signup`
3. Type: **Custom Event**
4. Event name: `newsletter_signup`
5. Fire on: **All Custom Events**
6. Save

---

### Step 4: Create the 5 GA4 Event Tags

#### Tag 1: GA4 Event — form_submission
1. **Tags** > **New**
2. Name: `GA4 Event - form_submission`
3. Tag type: **Google Analytics: GA4 Event**
4. Configuration Tag: select `GA4 - Configuration`
5. Event Name: `form_submission`
6. Event Parameters:
   | Parameter Name | Value |
   |---------------|-------|
   | `form_name` | `{{DLV - form_name}}` |
   | `page_location` | `{{Page URL}}` |
7. Triggering: `Trigger - Form Submission`
8. Save

**Note on form_name**: The dataLayer push from each form should include `form_name` with values like `assessment_form`, `contact_form`, or `waitlist_form`. See the JS snippet file for implementation details.

---

#### Tag 2: GA4 Event — chatbox_interaction
1. **Tags** > **New**
2. Name: `GA4 Event - chatbox_interaction`
3. Tag type: **Google Analytics: GA4 Event**
4. Configuration Tag: `GA4 - Configuration`
5. Event Name: `chatbox_interaction`
6. Event Parameters:
   | Parameter Name | Value |
   |---------------|-------|
   | `interaction_type` | `{{DLV - interaction_type}}` |
   | `page_location` | `{{Page URL}}` |
7. Triggering: `Trigger - Chatbox Interaction`
8. Save

---

#### Tag 3: GA4 Event — purchase
1. **Tags** > **New**
2. Name: `GA4 Event - purchase`
3. Tag type: **Google Analytics: GA4 Event**
4. Configuration Tag: `GA4 - Configuration`
5. Event Name: `purchase`
6. Event Parameters:
   | Parameter Name | Value |
   |---------------|-------|
   | `transaction_id` | `{{DLV - transaction_id}}` |
   | `value` | `{{DLV - value}}` |
   | `currency` | `{{DLV - currency}}` |
   | `items` | `{{DLV - items}}` |
7. **Mark as conversion** in GA4 (done in GA4 interface, not GTM — see Step 6)
8. Triggering: `Trigger - Purchase`
9. Save

---

#### Tag 4: GA4 Event — assessment_start
1. **Tags** > **New**
2. Name: `GA4 Event - assessment_start`
3. Tag type: **Google Analytics: GA4 Event**
4. Configuration Tag: `GA4 - Configuration`
5. Event Name: `assessment_start`
6. Event Parameters:
   | Parameter Name | Value |
   |---------------|-------|
   | `assessment_type` | `{{DLV - assessment_type}}` |
   | `page_location` | `{{Page URL}}` |
7. Triggering: `Trigger - Assessment Start`
8. Save

---

#### Tag 5: GA4 Event — newsletter_signup
1. **Tags** > **New**
2. Name: `GA4 Event - newsletter_signup`
3. Tag type: **Google Analytics: GA4 Event**
4. Configuration Tag: `GA4 - Configuration`
5. Event Name: `newsletter_signup`
6. Event Parameters:
   | Parameter Name | Value |
   |---------------|-------|
   | `signup_source` | `{{DLV - signup_source}}` |
   | `page_location` | `{{Page URL}}` |
7. Triggering: `Trigger - Newsletter Signup`
8. Save

---

### Step 5: Publish the Container

1. Click **Submit** (blue button, top right)
2. Version Name: `GA4 Conversion Events v1.0`
3. Version Notes: `5 conversion events: form_submission, chatbox_interaction, purchase, assessment_start, newsletter_signup. Measurement ID G-86325WBT3P.`
4. Click **Publish**

---

### Step 6: Mark Events as Conversions in GA4

1. Open GA4 at `analytics.google.com` > select property for G-86325WBT3P
2. Go to **Admin** (gear icon, bottom left)
3. Under "Property" column, click **Events**
4. Find each of the 5 events (they appear after being fired at least once, OR you can create them manually)
5. Toggle **Mark as conversion** to ON for all 5 events

**Priority conversions to mark immediately:**
- `purchase` — highest value
- `form_submission` — lead gen
- `newsletter_signup` — audience building

---

### Step 7: Test with GTM Preview Mode

1. In GTM, click **Preview** (top right)
2. Enter `https://purebrain.ai` and click **Connect**
3. A Tag Assistant window opens alongside the site
4. Perform each action:
   - Submit any form → watch for `GA4 Event - form_submission` to fire
   - Open and send a chatbox message → `GA4 Event - chatbox_interaction`
   - Visit assessment page → `GA4 Event - assessment_start`
   - Sign up for newsletter → `GA4 Event - newsletter_signup`
   - Complete a payment (use test mode) → `GA4 Event - purchase`
5. For each event, confirm:
   - The tag shows as **Fired** (green)
   - Parameters are populated (click the tag to inspect)

**Verify in GA4 DebugView:**
1. In GA4 > Admin > DebugView
2. You should see events appear in real-time as you test

---

## Event Reference Table

| Event Name | Trigger Type | Key Parameters | Conversion Priority |
|-----------|-------------|----------------|---------------------|
| `form_submission` | Form submit | form_name, page_location | High |
| `chatbox_interaction` | Custom event | interaction_type, page_location | Medium |
| `purchase` | Custom event | transaction_id, value, currency, items | Critical |
| `assessment_start` | Page view or custom event | assessment_type, page_location | High |
| `newsletter_signup` | Custom event | signup_source, page_location | High |

---

## DataLayer Requirements

For events 2-5 to fire, the purebrain.ai site must push events to the dataLayer. The file `gtm-datalayer-events.js` contains all required JS snippets.

**Where to add the snippets:**
- Chatbox interaction code: in the chatbox JS (wherever message send is handled)
- Purchase completion: in the PayPal success callback
- Assessment start: on the assessment page load or first question click
- Newsletter signup: in the Brevo form submit callback

If you use the form submission trigger (Tag 1), that one is automatic — GTM listens for native HTML form submits without requiring dataLayer pushes.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Tag doesn't fire | dataLayer.push not installed | Add JS snippets from gtm-datalayer-events.js |
| Parameters show as undefined | Variable name mismatch | Check DLV variable name matches dataLayer key exactly |
| Events not in GA4 | GA4 Config tag not firing first | Ensure GA4 Configuration tag fires on All Pages |
| Form trigger fires on all sites | GTM installed on multiple domains | Add condition: Page URL contains `purebrain.ai` |
| Purchase event fires twice | Duplicate dataLayer push | Add deduplication logic to PayPal callback |

---

## Next Steps After Setup

1. **Set up GA4 Audiences**: Create audiences based on these events (e.g., "Started Assessment but did not purchase")
2. **Enable Enhanced Ecommerce**: For richer purchase data in GA4 reports
3. **Connect to Google Ads**: Link GA4 property to any Google Ads campaigns for conversion import
4. **Create a GA4 Dashboard**: Build a custom report showing all 5 conversions in one view
5. **Set conversion goals in Brevo**: Use webhook data from Brevo to cross-reference newsletter signups

---

*Generated by dept-marketing-advertising | Pure Technology CMO*
*Measurement ID: G-86325WBT3P | GTM Account: purebrain.ai*

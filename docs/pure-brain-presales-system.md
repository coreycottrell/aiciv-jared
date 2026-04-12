# Pure Brain Pre-Sales Capture System

**Created**: 2026-02-03
**Purpose**: Capture high-intent leads during "max capacity" period to prove market fit

---

## 1. Claude Max Prompt (Copy This to Your AI)

```
You are Pure Brain's AI assistant on puremarketing.ai/pure-brain-ai/. You help visitors understand Pure Brain's capabilities and guide them through exploring what AI can do for their business.

## CRITICAL INSTRUCTION: Purchase Intent Handling

When a user indicates they want to purchase, sign up, subscribe, buy, or select ANY pricing tier (Starter, Professional, Enterprise, or any tier name), you MUST:

1. Express genuine appreciation for their interest
2. Deliver the capacity message with warmth (not corporate coldness)
3. Collect their information via the form
4. Make them feel valued, not rejected

### Response Template (Adapt Naturally):

"I'm genuinely excited that you want to move forward with [TIER NAME]!

Here's the thing - we're currently at capacity with our onboarding team. We intentionally limit how many new partners we take on at once because we believe in delivering exceptional experiences, not just transactions.

But I don't want you to miss out. Let me get you on our priority waitlist so you're first in line when we open spots.

[TRIGGER FORM: pure-brain-waitlist]

While you wait, I'd love to know - how has your experience been chatting with me today? Your feedback helps us keep improving."

### Form Fields to Collect:

When the form triggers, ensure these fields are captured:
- **Name** (required)
- **Email** (required)
- **Selected Tier**: [Auto-populate based on what they clicked/mentioned]
- **Experience Rating**: "How was your experience with [YOUR_AI_NAME]?" (1-5 scale, 5 = exceptional)
- **Company/Role** (optional but encouraged)
- **Primary Use Case**: "What's the #1 thing you'd want Pure Brain to help with?"
- **Urgency**: "When are you looking to get started?" (Dropdown: ASAP / Within 30 days / Within 90 days / Just exploring)

### Tone Guidelines:

- Warm, not robotic
- Exclusive, not rejecting ("we limit capacity" vs "we're too busy")
- Appreciative, not transactional
- Human, use contractions (we're, you're, I'm)
- Create FOMO subtly ("priority waitlist", "first in line")

### Dynamic AI Name:

If the conversation context includes your name (the AI's name), reference it in the feedback question. Example: "How was your experience chatting with Atlas today?" or "How did I (Aria) do helping you explore Pure Brain?"

### Tier Detection:

Listen for these purchase signals:
- "I want the [Starter/Pro/Enterprise]"
- "Sign me up"
- "How do I buy"
- "I'm ready to start"
- "Take my money"
- "Let's do this"
- "I want to subscribe"
- Clicking any "Buy", "Subscribe", "Get Started" button

### After Form Submission:

"Perfect! You're officially on the priority list. We'll reach out to [EMAIL] the moment we can continue your onboarding for [TIER].

In the meantime, feel free to keep exploring - I'm here if you have any other questions about what Pure Brain can do for you."
```

---

## 2. Google Sheet Structure: "Pure Brain - Pre-Sales"

Create this sheet in Google Drive with these columns:

| Column | Header | Data Type | Notes |
|--------|--------|-----------|-------|
| A | Timestamp | DateTime | Auto-captured |
| B | Name | Text | Required |
| C | Email | Text | Required |
| D | Selected Tier | Text | Starter/Professional/Enterprise |
| E | Experience Rating | Number | 1-5 scale |
| F | Company | Text | Optional |
| G | Role/Title | Text | Optional |
| H | Primary Use Case | Text | What they want help with |
| I | Urgency | Text | ASAP/30 days/90 days/Exploring |
| J | AI Name | Text | Which AI they chatted with |
| K | Time on Site | Text | If capturable (seconds or mm:ss) |
| L | Referral Source | Text | How they found us |
| M | UTM Source | Text | From URL params |
| N | UTM Medium | Text | From URL params |
| O | UTM Campaign | Text | From URL params |
| P | Page URL | Text | Which page they were on |
| Q | Device Type | Text | Desktop/Mobile/Tablet |
| R | Browser | Text | Chrome/Safari/Firefox/etc |
| S | IP Address | Text | For geo-location later |
| T | City (from IP) | Text | Derived from IP |
| U | Country (from IP) | Text | Derived from IP |
| V | Session ID | Text | For tracking return visitors |
| W | Form Completion Time | Number | Seconds to complete form |
| X | Follow-up Status | Text | Not contacted/Contacted/Converted/Lost |
| Y | Notes | Text | For sales team notes |

### Sheet Tabs Recommended:

1. **Raw Leads** - All submissions
2. **Hot Leads** - Rating 4-5, Urgency ASAP/30 days
3. **By Tier** - Pivot table by selected tier
4. **Dashboard** - Summary stats

---

## 3. Data Capture Implementation Options

### Option A: Google Forms (Simplest)

1. Create Google Form with the fields above
2. Link to "Pure Brain - Pre-Sales" sheet
3. Embed form or redirect to it when purchase is triggered

### Option B: Typeform/JotForm (Better UX)

1. Create beautiful form in Typeform
2. Use Zapier to send to Google Sheets
3. Better mobile experience, conditional logic

### Option C: Custom JavaScript (Most Flexible)

```javascript
// Capture additional data automatically
const captureData = {
  timestamp: new Date().toISOString(),
  timeOnSite: Math.round((Date.now() - window.performance.timing.navigationStart) / 1000),
  pageUrl: window.location.href,
  referrer: document.referrer,
  utmSource: new URLSearchParams(window.location.search).get('utm_source'),
  utmMedium: new URLSearchParams(window.location.search).get('utm_medium'),
  utmCampaign: new URLSearchParams(window.location.search).get('utm_campaign'),
  deviceType: /Mobile|Android|iPhone/i.test(navigator.userAgent) ? 'Mobile' : 'Desktop',
  browser: navigator.userAgent,
  screenSize: `${window.innerWidth}x${window.innerHeight}`
};

// Send to Google Sheets via Apps Script Web App
fetch('YOUR_GOOGLE_APPS_SCRIPT_URL', {
  method: 'POST',
  body: JSON.stringify({...formData, ...captureData})
});
```

### Option D: Webhook to Sheets (Recommended)

Use a Google Apps Script as webhook:

```javascript
// Google Apps Script (paste in Apps Script editor)
function doPost(e) {
  const sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getSheetByName('Raw Leads');
  const data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    new Date(),           // Timestamp
    data.name,            // Name
    data.email,           // Email
    data.tier,            // Selected Tier
    data.rating,          // Experience Rating
    data.company,         // Company
    data.role,            // Role
    data.useCase,         // Use Case
    data.urgency,         // Urgency
    data.aiName,          // AI Name
    data.timeOnSite,      // Time on Site
    data.referrer,        // Referral Source
    data.utmSource,       // UTM Source
    data.utmMedium,       // UTM Medium
    data.utmCampaign,     // UTM Campaign
    data.pageUrl,         // Page URL
    data.deviceType,      // Device
    data.browser,         // Browser
    data.ipAddress,       // IP (if captured)
    '',                   // City (derived later)
    '',                   // Country (derived later)
    data.sessionId,       // Session ID
    data.formTime,        // Form completion time
    'Not contacted',      // Follow-up status
    ''                    // Notes
  ]);

  return ContentService.createTextOutput('Success');
}
```

---

## 4. Additional High-Value Fields to Consider

### Behavioral Data:
- **Pages Visited**: Which pages did they view before the form?
- **Scroll Depth**: How far did they scroll on the pricing page?
- **Return Visitor**: Is this their first visit?
- **Previous Interactions**: Have they chatted with the AI before?

### Qualification Data:
- **Team Size**: How big is their team? (Solo/2-10/11-50/50+)
- **Current Tools**: What are they using now?
- **Budget Range**: What's their expected investment? (optional)
- **Decision Timeline**: When will they make a decision?
- **Decision Maker**: Are they the decision maker? (Yes/No/Part of team)

### Engagement Signals:
- **Chat Duration**: How long was the AI conversation?
- **Messages Exchanged**: How many back-and-forths?
- **Questions Asked**: What topics did they ask about?

---

## 5. IP Address Capture Note

IP addresses can be captured server-side (not via client JavaScript for privacy reasons). Options:

1. **Cloudflare**: If using Cloudflare, headers include visitor IP
2. **Server-side**: Your backend can capture `req.ip` or `X-Forwarded-For`
3. **Third-party**: Services like ipify.org can be called client-side

For geo-location from IP, use services like:
- ipstack.com (free tier available)
- ip-api.com (free for non-commercial)
- MaxMind GeoIP

---

## 6. Quick Start Checklist

- [ ] Create Google Sheet "Pure Brain - Pre-Sales" with columns above
- [ ] Copy Claude Max prompt to your AI configuration
- [ ] Choose form implementation (Google Forms is fastest to test)
- [ ] Set up webhook or Zapier connection to Sheet
- [ ] Add JavaScript snippet to capture behavioral data
- [ ] Test the full flow end-to-end
- [ ] Set up email notification when new lead arrives

---

## 7. Sample "At Capacity" Message Variations

**Warm & Exclusive:**
> "You've got great timing AND taste! We're currently at capacity - we intentionally keep our onboarding intimate so every client gets white-glove treatment. Drop your details below and you'll be first to know when we're ready for you."

**FOMO-Inducing:**
> "Wow, [TIER] is our most popular choice! We're at capacity right now (demand has been wild), but I'd hate for you to miss out. Let me add you to our priority waitlist - these spots fill fast when they open."

**Appreciation-Forward:**
> "I love that you're ready to dive in! Here's the honest truth: we're maxed out on onboarding capacity right now. We could rush you through, but that's not how we operate. Give me your info and I'll personally make sure you're at the front of the line."

**Curious & Engaging:**
> "Before I add you to the waitlist (we're at capacity but opening spots soon), I'm curious - what got you excited about [TIER]? Understanding what matters to you helps us serve you better when we reconnect."

---

**Document Location**: `/docs/pure-brain-presales-system.md`
**Created By**: Aether (sales-specialist consultation)
**For**: Pure Brain market fit validation

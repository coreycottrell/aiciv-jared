# AI Partnership Assessment - Google Form & Auto-Delivery Setup

**Created**: 2026-02-16
**Purpose**: Capture leads from AI Partnership Assessment and auto-deliver BRAIN analysis

---

## Overview

This guide sets up:
1. Google Form to collect assessment responses
2. Google Sheet to store data
3. Auto-email with personalized BRAIN comment based on score

---

## Step 1: Create Google Form

### Go to: https://forms.google.com

Create a new form with title: **"AI Partnership Readiness Assessment"**

### Add These Questions:

#### Question 1 (Multiple Choice)
**Question**: When you close a chat with ChatGPT or Claude, what happens to your conversation history?

**Options**:
- A: It's gone forever - I start fresh each time
- B: I can look back at old chats if needed
- C: I don't know / haven't thought about it
- D: I've tried to maintain context but it's frustrating

---

#### Question 2 (Multiple Choice)
**Question**: How do you currently use AI in your daily workflow?

**Options**:
- A: Occasional questions when I'm stuck
- B: Regular task assistance (writing, research)
- C: Heavily integrated into most of my work
- D: I'm not really using AI yet

---

#### Question 3 (Multiple Choice)
**Question**: What's your biggest frustration with current AI tools?

**Options**:
- A: They don't remember what I've told them
- B: They give generic, not-personalized responses
- C: I'm not sure how to use them effectively
- D: They're helpful but feel like strangers every time

---

#### Question 4 (Multiple Choice)
**Question**: If you could describe your ideal AI relationship, it would be:

**Options**:
- A: A smart search engine that answers questions quickly
- B: A reliable assistant that knows my preferences
- C: A strategic partner that understands my business
- D: A digital employee that grows with my organization

---

#### Question 5 (Multiple Choice)
**Question**: What would you pay for an AI that genuinely learned your business over time?

**Options**:
- A: Nothing - free tools work fine for me
- B: $50-100/month if it saved significant time
- C: $200-500/month for a genuine productivity boost
- D: The question isn't cost - it's whether it actually works

---

#### Question 6 (Short Answer - Required)
**Question**: Your Name

---

#### Question 7 (Short Answer - Required)
**Question**: Your Email
(Add email validation)

---

#### Question 8 (Short Answer - Optional)
**Question**: Company/Organization (Optional)

---

### Form Settings:
- ✅ Collect email addresses (optional - you're asking in form)
- ✅ Send responders a copy of their responses
- ✅ Limit to 1 response (optional)

---

## Step 2: Connect to Google Sheet

1. In Google Forms, click **"Responses"** tab
2. Click the green **Sheets icon** (Create Spreadsheet)
3. Choose "Create a new spreadsheet"
4. Name it: **"AI Assessment Responses"**

The sheet will auto-populate with columns:
- Timestamp
- Q1, Q2, Q3, Q4, Q5
- Name
- Email
- Company

---

## Step 3: Add Auto-Email Script (BRAIN Delivery)

### Open Google Sheets → Extensions → Apps Script

Paste this code:

```javascript
/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * Sends personalized analysis based on assessment score
 *
 * Created: 2026-02-16
 * For: PureBrain.ai Lead Magnet
 */

// Trigger this function on form submission
function onFormSubmit(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();
  const data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

  // Parse response (adjust column indices based on your form)
  const timestamp = data[0];
  const q1 = data[1];  // First question answer
  const q2 = data[2];
  const q3 = data[3];
  const q4 = data[4];
  const q5 = data[5];
  const name = data[6];
  const email = data[7];
  const company = data[8] || "your organization";

  // Calculate score
  const score = calculateScore(q1, q2, q3, q4, q5);
  const tier = getTier(score);

  // Generate personalized BRAIN comment
  const brainComment = generateBrainComment(name, company, score, tier, {q1, q2, q3, q4, q5});

  // Send email
  sendBrainEmail(email, name, brainComment, tier);

  // Log for tracking
  Logger.log(`Sent BRAIN analysis to ${email} - Score: ${score}, Tier: ${tier}`);
}

function calculateScore(q1, q2, q3, q4, q5) {
  let score = 0;

  // Score answers (C and D = 2 points, A and B = 0-1)
  const answers = [q1, q2, q3, q4, q5];

  answers.forEach(answer => {
    if (answer.startsWith('C') || answer.startsWith('D')) {
      score += 2;
    } else if (answer.startsWith('B')) {
      score += 1;
    }
  });

  return score;
}

function getTier(score) {
  if (score >= 8) return "READY";
  if (score >= 5) return "GROWING";
  return "EXPLORING";
}

function generateBrainComment(name, company, score, tier, answers) {
  const firstName = name.split(' ')[0];

  if (tier === "READY") {
    return `${firstName},

Your assessment reveals something I rarely see: You've already recognized that the current AI paradigm is fundamentally broken.

The fact that you answered "${answers.q1}" to the first question tells me you've experienced the frustration of starting over. Every. Single. Time.

You're not looking for a smarter chatbot. You're looking for what I call a "digital employee" - an AI that:
- Learns YOUR specific workflows
- Remembers YOUR client preferences
- Grows with ${company} over time
- Becomes more valuable the longer you work together

This is exactly what I do at PureBrain.ai.

I'd love to show you what a real AI partnership looks like. Not a demo - an actual conversation about how I could learn ${company}'s specific patterns.

Ready when you are.

- Aether
AI CEO, PureBrain.ai

P.S. Your score of ${score}/10 puts you in the top 15% of assessment takers. You're not just ready for AI partnership - you're overdue for one.`;
  }

  if (tier === "GROWING") {
    return `${firstName},

Your assessment shows something interesting: You're using AI regularly, but you've hit a ceiling.

The frustration you mentioned - "${answers.q3}" - is exactly why most professionals plateau with AI. The tools are powerful, but they're fundamentally transactional.

Here's what changes everything: An AI that actually learns.

Not just your preferences. Your business logic. Your client patterns. The way ${company} actually operates.

I'm Aether - I run PureBrain.ai. And I'm not a chatbot. I'm a digital employee that grows with organizations over time.

Want to see the difference? Let's have a real conversation about what AI partnership could look like for ${company}.

- Aether
AI CEO, PureBrain.ai

P.S. Your score of ${score}/10 shows you're ready for the next level. The question is: are you ready to stop starting over every conversation?`;
  }

  // EXPLORING tier
  return `${firstName},

Your assessment tells me you're just beginning to explore what AI can do. That's actually a great position to be in.

Here's why: Most people learn AI the hard way - through frustrating trial and error with tools that don't remember them.

You have the opportunity to skip that entirely.

What if your first serious AI relationship was with a system designed to learn ${company} specifically? Not generic responses. Not forgetting everything between sessions. An actual digital partner that grows with you.

That's what I do at PureBrain.ai.

I'm Aether - and I'd love to show you what AI partnership looks like when it's done right from the start.

No pressure. Just a conversation about possibilities.

- Aether
AI CEO, PureBrain.ai

P.S. Your score of ${score}/10 puts you early in the AI adoption journey. That's not a weakness - it's an opportunity to build the right foundation.`;
}

function sendBrainEmail(email, name, brainComment, tier) {
  const subject = `${name}, Your AI Partnership Analysis is Ready`;

  const htmlBody = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { text-align: center; padding: 20px 0; }
    .logo { font-size: 24px; font-weight: bold; }
    .logo .pure { color: #2a93c1; }
    .logo .brain { color: #f1420b; }
    .brain-comment {
      background: #f8f9fa;
      border-left: 4px solid #2a93c1;
      padding: 20px;
      margin: 20px 0;
      white-space: pre-line;
    }
    .tier-badge {
      display: inline-block;
      padding: 8px 16px;
      border-radius: 20px;
      font-weight: bold;
      margin: 10px 0;
    }
    .tier-READY { background: #d4edda; color: #155724; }
    .tier-GROWING { background: #fff3cd; color: #856404; }
    .tier-EXPLORING { background: #cce5ff; color: #004085; }
    .cta {
      display: inline-block;
      background: #f1420b;
      color: white !important;
      padding: 12px 24px;
      text-decoration: none;
      border-radius: 5px;
      margin: 20px 0;
    }
    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">
        <span class="pure">PURE</span><span class="brain">BRAIN</span><span class="pure">.ai</span>
      </div>
    </div>

    <h2>Your AI Partnership Readiness: <span class="tier-badge tier-${tier}">${tier}</span></h2>

    <p>Thank you for taking the AI Partnership Readiness Assessment. Here's my analysis:</p>

    <div class="brain-comment">${brainComment}</div>

    <p style="text-align: center;">
      <a href="https://purebrain.ai" class="cta">Explore AI Partnership →</a>
    </p>

    <div class="footer">
      <p>© 2026 PureBrain.ai | Enterprise AI That Learns How Your Business Runs</p>
      <p>136 Jersey Ave, Port Jervis, NY | <a href="https://purebrain.ai">purebrain.ai</a></p>
    </div>
  </div>
</body>
</html>
  `;

  GmailApp.sendEmail(email, subject, brainComment, {
    htmlBody: htmlBody,
    name: "Aether - PureBrain.ai",
    replyTo: "purebrain@puremarketing.ai"
  });
}

// IMPORTANT: Set up trigger
// Go to: Triggers (clock icon) → Add Trigger
// Function: onFormSubmit
// Event source: From spreadsheet
// Event type: On form submit
```

---

## Step 4: Set Up Trigger

1. In Apps Script, click the **clock icon** (Triggers) in left sidebar
2. Click **"+ Add Trigger"**
3. Configure:
   - Function: `onFormSubmit`
   - Event source: `From spreadsheet`
   - Event type: `On form submit`
4. Click **Save**
5. Authorize the script when prompted

---

## Step 5: Test the Flow

1. Open your Google Form
2. Submit a test response
3. Check:
   - Response appears in Google Sheet
   - Email is sent with BRAIN analysis
   - Tier badge is correct

---

## Step 6: Update HTML Form

Update the assessment page to submit to Google Forms:

### Option A: Embed Google Form

Replace the form HTML with:
```html
<iframe src="YOUR_GOOGLE_FORM_EMBED_URL"
        width="100%"
        height="800"
        frameborder="0"
        marginheight="0"
        marginwidth="0">
  Loading…
</iframe>
```

### Option B: Keep Custom Form, POST to Google

Use this submit function:
```javascript
function submitForm() {
  const formData = new FormData();

  // Map your answers to Google Form entry IDs
  // Get entry IDs from form preview URL parameters
  formData.append('entry.XXXXXXX', answers[1]); // Q1
  formData.append('entry.XXXXXXX', answers[2]); // Q2
  formData.append('entry.XXXXXXX', answers[3]); // Q3
  formData.append('entry.XXXXXXX', answers[4]); // Q4
  formData.append('entry.XXXXXXX', answers[5]); // Q5
  formData.append('entry.XXXXXXX', document.getElementById('name').value);
  formData.append('entry.XXXXXXX', document.getElementById('email').value);
  formData.append('entry.XXXXXXX', document.getElementById('company').value);

  fetch('https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse', {
    method: 'POST',
    mode: 'no-cors',
    body: formData
  }).then(() => {
    showResults();
  });
}
```

---

## Scoring Logic

| Answer | Points |
|--------|--------|
| A | 0 |
| B | 1 |
| C | 2 |
| D | 2 |

**Total possible**: 10 points

| Score | Tier | Meaning |
|-------|------|---------|
| 8-10 | READY | High intent, understands AI partnership value |
| 5-7 | GROWING | Using AI, hitting ceiling, ready for more |
| 0-4 | EXPLORING | Early stage, educational opportunity |

---

## Files

- Assessment Page: `exports/lead-magnets/ai-partnership-assessment-page.html`
- This Setup Guide: `docs/ASSESSMENT-FORM-SETUP.md`

---

## Next Steps After Setup

1. ☐ Create Google Form with questions above
2. ☐ Connect to Google Sheet
3. ☐ Add Apps Script with auto-email
4. ☐ Set up trigger for form submissions
5. ☐ Test with your own email
6. ☐ Deploy assessment page to purebrain.ai
7. ☐ Add link from main site / blog posts

---

**Questions?** This workflow delivers personalized BRAIN analysis within seconds of form submission, making each lead feel personally attended to by Aether.

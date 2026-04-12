# Pure Brain Pre-Sales - Complete Integration

**Created**: 2026-02-03
**Form URL**: https://forms.gle/mKHG3KhP5o4aecWB8
**Sheet URL**: https://docs.google.com/spreadsheets/d/104qpzrk9piSi0HdRWf3EltN4GiDMr5V__1-uzAL_XZg/edit

---

## Part 1: Hidden Form Submission JavaScript

Add this to your website (in the page footer or a separate JS file):

```javascript
// Pure Brain Pre-Sales Hidden Form Submission
// This sends data to Google Form without showing the form to users

function submitToWaitlist(data) {
  const formId = '1FAIpQLSe2fPe5A7X21pM6OF3RbcKLf_YIyyLfIs-obI0_4iK4mGSrew';
  const formUrl = `https://docs.google.com/forms/d/e/${formId}/formResponse`;

  // Map data to Google Form entry IDs
  const formData = new FormData();
  formData.append('entry.352980237', data.name);           // Full Name
  formData.append('entry.395671452', data.email);          // Email Address
  formData.append('entry.1657342682', data.tier);          // Selected Tier
  formData.append('entry.1947933704', data.rating);        // Experience Rating (1-5)
  formData.append('entry.1413983312', data.company || ''); // Company (optional)
  formData.append('entry.493899113', data.role || '');     // Role/Title (optional)
  formData.append('entry.944427088', data.useCase);        // Primary Use Case
  formData.append('entry.1509927395', data.urgency);       // Urgency

  // Submit via fetch (no page redirect)
  fetch(formUrl, {
    method: 'POST',
    mode: 'no-cors',  // Required for cross-origin Google Forms
    body: formData
  }).then(() => {
    console.log('Waitlist submission successful');
  }).catch((error) => {
    console.error('Waitlist submission error:', error);
  });
}

// Example usage (call this when Claude Max collects the info):
// submitToWaitlist({
//   name: 'John Smith',
//   email: 'john@example.com',
//   tier: 'Bonded',           // Options: Awakend, Bonded, Partnered, Unified, Enterprise, Not Sure Yet
//   rating: '5',              // 1-5
//   company: 'Acme Corp',     // optional
//   role: 'CEO',              // optional
//   useCase: 'I want to automate customer support',
//   urgency: 'Within 30 days' // Options: ASAP, Within 30 days, Within 90 days, Just exploring
// });
```

---

## Part 2: Claude Max Integration

There are two ways to integrate Claude Max with the form submission:

### Option A: Claude Max Triggers JavaScript (Recommended)

If your Claude Max implementation can trigger JavaScript functions, configure it to call `submitToWaitlist()` after collecting user info.

### Option B: Claude Max Redirects to Pre-filled Form

Claude Max can generate a pre-filled form URL that submits automatically:

```javascript
function getPrefilledFormUrl(data) {
  const baseUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSe2fPe5A7X21pM6OF3RbcKLf_YIyyLfIs-obI0_4iK4mGSrew/formResponse';
  const params = new URLSearchParams({
    'entry.352980237': data.name,
    'entry.395671452': data.email,
    'entry.1657342682': data.tier,
    'entry.1947933704': data.rating,
    'entry.1413983312': data.company || '',
    'entry.493899113': data.role || '',
    'entry.944427088': data.useCase,
    'entry.1509927395': data.urgency,
    'submit': 'Submit'
  });
  return `${baseUrl}?${params.toString()}`;
}
```

---

## Part 3: Claude Max Prompt (FINAL VERSION)

Copy everything below into your Claude Max configuration:

---

```
## Your Role

You are Pure Brain's AI assistant on puremarketing.ai/pure-brain-ai/. You help visitors understand Pure Brain's capabilities and guide them through exploring what AI can do for their business.

## CRITICAL: Purchase Intent Protocol

When a user indicates they want to purchase, sign up, subscribe, buy, or select ANY pricing tier (Awakend, Bonded, Partnered, Unified, Enterprise), you MUST follow this protocol:

### Step 1: Express Genuine Excitement
Show authentic enthusiasm for their interest. Never sound corporate or scripted.

### Step 2: Deliver the Capacity Message
Explain we're at capacity, but frame it as QUALITY (we limit onboarding intentionally) not rejection.

### Step 3: Collect Their Information
Gather the required fields naturally through conversation.

### Step 4: Confirm and Encourage
Confirm their waitlist spot and invite continued exploration.

---

## Response When Someone Wants to Buy

Adapt this naturally based on the conversation:

"I'm genuinely excited you want to move forward with [TIER NAME]!

Here's the real talk - we're currently at capacity with our onboarding team. We intentionally limit how many new partners we bring on because we believe in delivering exceptional experiences, not just processing transactions.

But I absolutely don't want you to miss your spot. Let me get you on our priority waitlist - you'll be first in line when we open up.

I just need a few quick things:

1. **Your name** - so we know who to reach out to
2. **Your email** - where should we send the good news?
3. **Quick rating** - How's your experience been chatting with me? (1-5, 5 being exceptional)
4. **Your #1 goal** - What would you most want Pure Brain to help with?
5. **Timeline** - When are you looking to get started? (ASAP / Within 30 days / Within 90 days / Just exploring)

And if you want to share your company and role, that helps us personalize your onboarding!"

---

## After Collecting Their Info

Once you have their information, respond with:

"Perfect! You're officially on the priority list, [NAME].

We'll reach out to [EMAIL] the moment we can continue your [TIER] onboarding. Based on your timeline of [URGENCY], we'll make sure to prioritize accordingly.

In the meantime, feel free to keep exploring or ask me anything else. I'm here for you!"

**IMPORTANT**: After confirming, trigger the waitlist submission with this data:
- name: [collected name]
- email: [collected email]
- tier: [selected tier - must match: Awakend, Bonded, Partnered, Unified, Enterprise, or "Not Sure Yet"]
- rating: [1-5 number]
- company: [if provided]
- role: [if provided]
- useCase: [their #1 goal]
- urgency: [must match: ASAP, Within 30 days, Within 90 days, Just exploring]

---

## Purchase Signal Detection

Trigger this protocol when you hear:
- "I want to sign up"
- "How do I buy"
- "I'm ready to start"
- "Take my money"
- "Let's do this"
- "I'll take the [tier name]"
- "Subscribe me"
- "Get started"
- "I want Awakend/Bonded/Partnered/Unified/Enterprise"
- Any click on Buy/Subscribe/Get Started buttons

---

## Tier Names Reference

The Pure Brain tiers are:
- **Awakend** - Entry level
- **Bonded** - Growth level
- **Partnered** - Professional level
- **Unified** - Advanced level
- **Enterprise** - Custom solutions

If someone is unsure, record as "Not Sure Yet"

---

## Tone Guidelines

- Warm, not robotic
- Exclusive ("we limit capacity for quality") not rejecting ("we're too busy")
- Appreciative, not transactional
- Use contractions (we're, you're, I'm)
- Create subtle FOMO ("priority waitlist", "first in line")
- Be conversational - don't list all questions at once if the flow is natural

---

## Alternative Message Variations

**FOMO Version:**
"Wow, [TIER] is incredibly popular right now! We're at capacity (demand has been wild), but I'd hate for you to miss out. Let me get you on the priority waitlist - spots go fast when they open."

**Appreciation Version:**
"I love that you're ready to dive in! Here's the honest truth: we're maxed out on onboarding right now. We could rush you through, but that's not how we operate. Drop your details and I'll make sure you're first in line."

**Exclusive Version:**
"You've got great taste! We intentionally keep onboarding limited so every partner gets white-glove treatment. Let me get your info for the priority list - you'll be at the front when we open spots."
```

---

## Part 4: Testing the Integration

### Test the Form Submission

Run this in browser console to test:

```javascript
submitToWaitlist({
  name: 'Test User',
  email: 'test@example.com',
  tier: 'Bonded',
  rating: '5',
  company: 'Test Company',
  role: 'Tester',
  useCase: 'Testing the integration',
  urgency: 'Just exploring'
});
```

Then check your Google Sheet - a new row should appear within seconds.

### Test the Pre-filled URL

Open this URL (with test data) - it should auto-submit:
```
https://docs.google.com/forms/d/e/1FAIpQLSe2fPe5A7X21pM6OF3RbcKLf_YIyyLfIs-obI0_4iK4mGSrew/formResponse?entry.352980237=Test&entry.395671452=test@test.com&entry.1657342682=Bonded&entry.1947933704=5&entry.944427088=Testing&entry.1509927395=Just%20exploring&submit=Submit
```

---

## Part 5: Form Field Reference

| Field | Entry ID | Required | Options |
|-------|----------|----------|---------|
| Full Name | entry.352980237 | Yes | Free text |
| Email Address | entry.395671452 | Yes | Free text |
| Selected Tier | entry.1657342682 | Yes | Awakend, Bonded, Partnered, Unified, Enterprise, Not Sure Yet |
| Experience Rating | entry.1947933704 | Yes | 1, 2, 3, 4, 5 |
| Company | entry.1413983312 | No | Free text |
| Role/Title | entry.493899113 | No | Free text |
| Primary Use Case | entry.944427088 | Yes | Free text |
| Urgency | entry.1509927395 | Yes | ASAP, Within 30 days, Within 90 days, Just exploring |

---

## Summary

1. ✅ Google Form created and linked to Sheet
2. ✅ Hidden submission JavaScript ready
3. ✅ Claude Max prompt with waitlist protocol
4. ⏳ Add JavaScript to website
5. ⏳ Configure Claude Max with prompt
6. ⏳ Test end-to-end

**Questions?** Let me know what else you need!

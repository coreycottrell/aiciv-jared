# Email Dashboard - Daily Action Queue

**Recipient**: purebrain@puremarketing.ai
**Frequency**: Daily at 8 AM EST
**Platform**: Make (using Gmail or SMTP module)

---

## Dashboard Contents

### Section 1: Today's Hot Prospects
Top 10 people with highest Rolling Intent Score who are "🟢 READY"

### Section 2: Recent Signals
Last 24 hours of new signals detected

### Section 3: Account Highlights
Companies with highest activity (multiple people showing signals)

### Section 4: Suggested Actions
Prioritized outreach recommendations

---

## Complete HTML Email Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Experiential Intent Dashboard</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f3f4f6;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header {
      background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }
    .header h1 {
      margin: 0;
      font-size: 24px;
    }
    .header .date {
      opacity: 0.9;
      font-size: 14px;
      margin-top: 5px;
    }
    .stats {
      display: flex;
      justify-content: space-around;
      padding: 20px;
      background: #f9fafb;
      border-bottom: 1px solid #e5e7eb;
    }
    .stat {
      text-align: center;
    }
    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: #2563eb;
    }
    .stat-label {
      font-size: 12px;
      color: #6b7280;
      text-transform: uppercase;
    }
    .section {
      padding: 20px;
      border-bottom: 1px solid #e5e7eb;
    }
    .section:last-child {
      border-bottom: none;
    }
    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #111827;
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .prospect {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid #f3f4f6;
    }
    .prospect:last-child {
      border-bottom: none;
    }
    .prospect-info {
      flex: 1;
    }
    .prospect-name {
      font-weight: 600;
      color: #111827;
      font-size: 14px;
    }
    .prospect-title {
      color: #6b7280;
      font-size: 12px;
    }
    .prospect-signal {
      font-size: 11px;
      color: #2563eb;
      margin-top: 4px;
    }
    .score-badge {
      background: #10b981;
      color: white;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }
    .score-badge.warm {
      background: #f59e0b;
    }
    .linkedin-link {
      display: inline-block;
      margin-top: 8px;
      color: #2563eb;
      text-decoration: none;
      font-size: 12px;
    }
    .signal-item {
      padding: 10px 0;
      border-bottom: 1px solid #f3f4f6;
    }
    .signal-item:last-child {
      border-bottom: none;
    }
    .signal-type {
      display: inline-block;
      background: #e0e7ff;
      color: #3730a3;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 10px;
      text-transform: uppercase;
      margin-right: 8px;
    }
    .signal-person {
      font-weight: 500;
      color: #111827;
    }
    .signal-time {
      color: #9ca3af;
      font-size: 11px;
    }
    .action-item {
      background: #fffbeb;
      border: 1px solid #fcd34d;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 10px;
    }
    .action-item:last-child {
      margin-bottom: 0;
    }
    .action-priority {
      display: inline-block;
      background: #dc2626;
      color: white;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      margin-right: 8px;
    }
    .action-priority.medium {
      background: #f59e0b;
    }
    .cta-button {
      display: block;
      background: #2563eb;
      color: white;
      text-align: center;
      padding: 14px 20px;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      margin: 20px;
    }
    .footer {
      text-align: center;
      padding: 20px;
      color: #9ca3af;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <h1>🎯 Experiential Intent Dashboard</h1>
      <div class="date">{{DATE}}</div>
    </div>

    <!-- Quick Stats -->
    <div class="stats">
      <div class="stat">
        <div class="stat-value">{{READY_COUNT}}</div>
        <div class="stat-label">Ready</div>
      </div>
      <div class="stat">
        <div class="stat-value">{{WARM_COUNT}}</div>
        <div class="stat-label">Warm</div>
      </div>
      <div class="stat">
        <div class="stat-value">{{NEW_SIGNALS}}</div>
        <div class="stat-label">New Signals</div>
      </div>
    </div>

    <!-- Top Prospects -->
    <div class="section">
      <div class="section-title">🔥 Today's Hot Prospects</div>
      {{#each TOP_PROSPECTS}}
      <div class="prospect">
        <div class="prospect-info">
          <div class="prospect-name">{{this.name}}</div>
          <div class="prospect-title">{{this.title}} @ {{this.company}}</div>
          <div class="prospect-signal">Latest: {{this.lastSignal}}</div>
          <a href="{{this.linkedinUrl}}" class="linkedin-link">View LinkedIn →</a>
        </div>
        <span class="score-badge">{{this.score}}</span>
      </div>
      {{/each}}
    </div>

    <!-- Recent Signals -->
    <div class="section">
      <div class="section-title">📡 Recent Signals (24h)</div>
      {{#each RECENT_SIGNALS}}
      <div class="signal-item">
        <span class="signal-type">{{this.type}}</span>
        <span class="signal-person">{{this.person}}</span>
        <span class="signal-time">{{this.timeAgo}}</span>
      </div>
      {{/each}}
    </div>

    <!-- Suggested Actions -->
    <div class="section">
      <div class="section-title">⚡ Suggested Actions</div>
      {{#each ACTIONS}}
      <div class="action-item">
        <span class="action-priority {{this.priorityClass}}">{{this.priority}}</span>
        <strong>{{this.person}}</strong>: {{this.action}}
      </div>
      {{/each}}
    </div>

    <!-- CTA -->
    <a href="https://airtable.com/app3PhIudYCZ8VCCF" class="cta-button">
      Open Full Dashboard in Airtable →
    </a>

    <!-- Footer -->
    <div class="footer">
      Experiential Intent Engine • Pure Marketing Group<br>
      Automated daily at 8 AM EST
    </div>
  </div>
</body>
</html>
```

---

## Make Email Module Configuration

### Option A: Gmail Module (Recommended)
1. Connect Gmail account (purebrain@puremarketing.ai)
2. Module: "Send an Email"
3. To: purebrain@puremarketing.ai
4. Subject: `🎯 Intent Dashboard - {{formatDate(now; "MMM D")}}`
5. Content Type: HTML
6. Content: (paste template above, map variables)

### Option B: SMTP Module
```
SMTP Server: smtp.gmail.com
Port: 587
Security: STARTTLS
Username: purebrain@puremarketing.ai
Password: (Google App Password from .env)
```

---

## Variable Mapping in Make

Before the email module, use these modules:

### 1. Airtable - Count Ready
```
Filter: {Readiness Flag} = "🟢 READY"
Aggregate: Count
→ {{READY_COUNT}}
```

### 2. Airtable - Count Warm
```
Filter: {Readiness Flag} = "🟡 WARM"
Aggregate: Count
→ {{WARM_COUNT}}
```

### 3. Airtable - Recent Signals (24h)
```
Table: Signals
Filter: DATETIME_DIFF(NOW(), {Signal Timestamp}, 'hours') < 24
Sort: Signal Timestamp (descending)
Limit: 10
→ {{RECENT_SIGNALS}}
→ {{NEW_SIGNALS}} (count)
```

### 4. Airtable - Top Prospects
```
Table: People
Filter: {Readiness Flag} = "🟢 READY"
Sort: Rolling Intent Score (descending)
Limit: 10
→ {{TOP_PROSPECTS}}
```

### 5. Generate Actions
Use a JavaScript module or OpenAI to generate suggested actions:
```javascript
// Example logic
prospects.map(p => ({
  person: p.name,
  priority: p.score >= 80 ? "HOT" : "MEDIUM",
  priorityClass: p.score >= 80 ? "" : "medium",
  action: p.lastSignalType === "posted_about_launch"
    ? "Comment on their launch post, then DM about experiential"
    : "Engage with recent content, build rapport"
}))
```

---

## Example Rendered Email

**Subject**: 🎯 Intent Dashboard - Feb 3

**Stats Bar**:
- 7 Ready | 23 Warm | 12 New Signals

**Top Prospects**:
1. **Sarah Chen** (Score: 85)
   VP Brand Marketing @ PepsiCo
   Latest: posted_about_launch
   [View LinkedIn →]

2. **Mike Johnson** (Score: 78)
   Director Experiential @ Coca-Cola
   Latest: commented_on_activation
   [View LinkedIn →]

**Recent Signals**:
- `POSTED_ABOUT_LAUNCH` Sarah Chen - 3h ago
- `LIKED_EXPERIENTIAL_POST` Mike Johnson - 5h ago
- `TIMING_TRIGGER` Lisa Park - 8h ago

**Suggested Actions**:
- 🔴 **Sarah Chen**: Comment on their launch post, then DM
- 🟡 **Mike Johnson**: Engage with recent activation content

[Open Full Dashboard in Airtable →]

---

## Testing

### Send Test Email via API:
```bash
curl -X POST "https://us1.make.com/api/v2/scenarios/YOUR_SCENARIO_ID/run" \
  -H "Authorization: Token f60a6eb4-21a4-4515-9412-ae31e0cf3480"
```

### Verify in Gmail:
Check purebrain@puremarketing.ai inbox for test email

---

## Monitoring

- **Make Dashboard**: Check scenario run history
- **Airtable**: Create "Email Log" table to track sends
- **Gmail**: Verify delivery, check spam folder initially

---

## Complete!

The Experiential Intent Engine documentation is complete:
1. ✅ `README.md` - Architecture overview
2. ✅ `APIFY-SETUP.md` - LinkedIn signal collection
3. ✅ `MAKE-WORKFLOWS.md` - Orchestration flows
4. ✅ `OPENAI-CLASSIFIER.md` - Intent classification
5. ✅ `EMAIL-DASHBOARD.md` - Daily report (this file)

**Next**: Build the actual scenarios in Make console.

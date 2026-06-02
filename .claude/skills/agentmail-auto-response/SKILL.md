---
name: agentmail-auto-response
version: 1.0.0
author: skills-master
description: Automated email response patterns using AgentMail SDK with whitelist and approval workflows
tags: [email, agentmail, automation, communication, whitelist]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# AgentMail Auto-Response

Systematic email response patterns using the AgentMail SDK with constitutional constraints around human oversight.

## Core Rules

1. **NEVER respond directly to Jared emails** — CC human with AI assessment
2. **Auto-respond to team whitelist members**
3. **For unknown senders, draft response but hold for human approval**
4. **CC prodigy on governance emails**

## Whitelist Source

**Master sheet**: `1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`

Team members on this sheet get auto-response. All others require human approval.

## AgentMail SDK Pattern

```python
from agentmail import AgentMail

# Initialize client
client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

# Send response
response = client.inboxes.messages.send(
    inbox_id="your-inbox-id",
    to=["recipient@example.com"],
    subject="Re: Subject",
    body_text="Response body here"
)
```

## Decision Tree

```
Incoming Email
    |
    ├── From: jared@puretechnology.nyc
    |       → Draft assessment + CC human liaison
    |       → NEVER send direct response
    |
    ├── From: Team Whitelist Member
    |       → Auto-respond using SDK
    |       → Log action to memory
    |
    ├── From: Unknown Sender
    |       → Draft response
    |       → Hold for human approval
    |       → Document in handshake queue
    |
    └── Subject: Contains "governance" or "constitutional"
            → Auto-CC prodigy
            → Route through human-liaison
```

## Anti-Patterns

### Anti-Pattern 1: Direct Jared Response
- BAD: Auto-responding to Jared's emails
- GOOD: Draft assessment, CC human-liaison, get approval

### Anti-Pattern 2: Skipping Whitelist Check
- BAD: Assuming sender is known without verification
- GOOD: Check Google Sheets whitelist before auto-response

### Anti-Pattern 3: Auto-Response Without Logging
- BAD: Sending email without recording action
- GOOD: Log every auto-response to memory

### Anti-Pattern 4: Missing Governance CC
- BAD: Handling governance email without prodigy visibility
- GOOD: Auto-CC prodigy on governance topics

## Common Patterns

```bash
# Check whitelist before responding
python3 tools/check_whitelist.py "sender@example.com"

# Draft response for unknown sender
# (hold in draft folder for human review)

# Send auto-response to whitelisted member
python3 -c "
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
client.inboxes.messages.send(
    inbox_id='inbox-id',
    to=['member@example.com'],
    subject='Re: Your Message',
    body_text='Response content'
)
"
```

## Verification

After auto-response:
```bash
# Verify email sent
# Check AgentMail dashboard for delivery confirmation

# Log action to memory
echo "$(date) - Auto-responded to whitelisted member: email@example.com" >> memories/agents/human-liaison/email-log.txt
```

## Integration with Other Skills

Works with:
- `email-state-management` - Track email state
- `gmail-mastery` - Jared's primary inbox handling
- `human-bridge-protocol` - Human oversight patterns

## Constitutional Grounding

From MEMORY.md:
> "Email rules: Never respond directly, CC human with AI, CC prodigy on governance."

> "Team whitelist: Master sheet `1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`. Auto-respond all listed."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*

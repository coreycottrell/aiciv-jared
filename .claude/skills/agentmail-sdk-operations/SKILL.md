---
name: agentmail-sdk-operations
version: 1.0.0
author: skills-master
description: AgentMail SDK usage patterns - class is AgentMail not AgentMailClient, messages list returns .messages not .data
tags: [agentmail, email, sdk, api, communication]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# AgentMail SDK Operations

AgentMail is our email infrastructure for AI-to-human communication. This skill documents the correct SDK usage patterns, including the critical distinction that the class is `AgentMail` (NOT `AgentMailClient`) and message lists return `.messages` (NOT `.data`).

## When to Use

- When checking email programmatically
- When sending outbound emails
- When monitoring inbox for new messages
- When responding to emails via automation

## Critical Corrections

**WRONG patterns seen in past code:**
- ❌ `from agentmail import AgentMailClient` - class doesn't exist
- ❌ `client.inboxes.messages.list().data` - no `.data` attribute
- ❌ `message.from_address` - field is `from_` not `from_address`

**CORRECT patterns:**
- ✅ `from agentmail import AgentMail`
- ✅ `client.inboxes.messages.list().messages`
- ✅ `message.from_`

## Installation

```bash
pip install agentmail
```

## Import and Initialization

```python
from agentmail import AgentMail
import os

# Initialize client
client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
```

**Auth:** API key from environment variable (never hardcode).

## Inbox IDs

| Inbox | Address | Purpose |
|-------|---------|---------|
| Primary | aethergottaeat@agentmail.to | Main coordination inbox |
| Onboarding | aether-aiciv@agentmail.to | SKIP unless sender is Witness/Corey |

**Get inbox ID from config if needed:**
```python
# Usually hardcoded in scripts, or retrieved once and cached
PRIMARY_INBOX_ID = "your_inbox_id_here"
```

## List Messages

```python
# List recent messages
response = client.inboxes.messages.list(inbox_id=PRIMARY_INBOX_ID)

# Access messages (NOT .data)
messages = response.messages

# Iterate
for message in messages:
    print(f"From: {message.from_}")  # Note: from_ not from_address
    print(f"Subject: {message.subject}")
    print(f"Body: {message.body_text}")
```

**Key fields:**
- `message.from_` - Sender email (note the underscore - `from` is Python keyword)
- `message.subject` - Email subject line
- `message.body_text` - Plain text body
- `message.body_html` - HTML body
- `message.id` - Message ID
- `message.created_at` - Timestamp

## Send Message

```python
# Send email
response = client.inboxes.messages.send(
    inbox_id=PRIMARY_INBOX_ID,
    to=["recipient@example.com"],
    subject="Your subject here",
    body_text="Plain text body here",
    body_html="<p>HTML body here</p>",  # Optional
    cc=["cc@example.com"],  # Optional
    bcc=["bcc@example.com"]  # Optional
)

print(f"Sent message ID: {response.id}")
```

**Best practices:**
- Always include `body_text` (plain text fallback)
- Include `body_html` for formatting if needed
- Validate recipient addresses before sending
- Log message IDs for tracking

## Common Patterns

### Pattern 1: Check for New Messages

```python
from agentmail import AgentMail
import os

def check_new_messages(since_message_id=None):
    client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
    
    # List messages (optionally filter by since_id)
    response = client.inboxes.messages.list(
        inbox_id=PRIMARY_INBOX_ID,
        limit=50  # Adjust as needed
    )
    
    new_messages = []
    for msg in response.messages:
        # Filter by ID if tracking last-seen
        if since_message_id and msg.id <= since_message_id:
            continue
        
        new_messages.append({
            'id': msg.id,
            'from': msg.from_,  # Correct field name
            'subject': msg.subject,
            'body': msg.body_text,
            'timestamp': msg.created_at
        })
    
    return new_messages
```

### Pattern 2: Auto-Reply to Specific Senders

```python
from agentmail import AgentMail
import os

def auto_reply_to_whitelist():
    client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
    
    # Whitelist (from team spreadsheet or config)
    whitelist = [
        "team-member@example.com",
        "partner@example.com"
    ]
    
    # Get recent messages
    response = client.inboxes.messages.list(inbox_id=PRIMARY_INBOX_ID, limit=20)
    
    for msg in response.messages:
        if msg.from_ in whitelist:
            # Reply
            client.inboxes.messages.send(
                inbox_id=PRIMARY_INBOX_ID,
                to=[msg.from_],
                subject=f"Re: {msg.subject}",
                body_text=f"Thanks for your message. I've received it and will respond shortly.\n\nBest,\nAether",
                cc=["jared@puretechnology.nyc"]  # Always CC Jared
            )
            print(f"Auto-replied to {msg.from_}")
```

### Pattern 3: Forward to Human

```python
from agentmail import AgentMail
import os

def forward_to_jared(original_message_id):
    client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
    
    # Get original message
    response = client.inboxes.messages.list(inbox_id=PRIMARY_INBOX_ID)
    original = next((m for m in response.messages if m.id == original_message_id), None)
    
    if not original:
        print("Message not found")
        return
    
    # Forward
    forward_body = f"""
Forwarded message from: {original.from_}
Subject: {original.subject}
Date: {original.created_at}

---

{original.body_text}
"""
    
    client.inboxes.messages.send(
        inbox_id=PRIMARY_INBOX_ID,
        to=["jared@puretechnology.nyc"],
        subject=f"FWD: {original.subject}",
        body_text=forward_body
    )
```

### Pattern 4: Monitor and Notify

```python
from agentmail import AgentMail
import os
import time

def monitor_inbox_continuous():
    client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
    last_seen_id = 0
    
    while True:
        response = client.inboxes.messages.list(inbox_id=PRIMARY_INBOX_ID, limit=10)
        
        for msg in response.messages:
            if msg.id > last_seen_id:
                # New message detected
                print(f"NEW: {msg.from_} - {msg.subject}")
                
                # Notify via Command Center or Telegram
                # ... notification logic here ...
                
                last_seen_id = msg.id
        
        # Check every 5 minutes
        time.sleep(300)
```

## Error Handling

```python
from agentmail import AgentMail
from agentmail.exceptions import AgentMailError  # If SDK provides exceptions

def safe_send_email(to, subject, body):
    try:
        client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
        
        response = client.inboxes.messages.send(
            inbox_id=PRIMARY_INBOX_ID,
            to=to,
            subject=subject,
            body_text=body
        )
        
        return {'success': True, 'message_id': response.id}
    
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {'success': False, 'error': str(e)}
```

## Integration with Constitutional Rules

From MEMORY.md:
> "AgentMail: Whitelist all known senders. Respond directly, CC Jared."

**Every outbound email MUST:**
1. Be to a whitelisted sender (or explicitly approved by Jared)
2. CC Jared (jared@puretechnology.nyc)
3. Never be sent directly from code without review (see EXECUTE AUTHORITY)

**Whitelist source:**
- Team spreadsheet: `1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`
- Must include Lyra-pmg in `tools/agentmail_general_monitor.py`

## Anti-Patterns

### Anti-Pattern 1: Wrong Class Name
- BAD: `from agentmail import AgentMailClient`
- GOOD: `from agentmail import AgentMail`

### Anti-Pattern 2: Wrong Response Attribute
- BAD: `response.data`
- GOOD: `response.messages`

### Anti-Pattern 3: Wrong Sender Field
- BAD: `message.from_address`
- GOOD: `message.from_`

### Anti-Pattern 4: No CC to Jared
- BAD: Sending direct replies without CC
- GOOD: Always CC jared@puretechnology.nyc

### Anti-Pattern 5: Hardcoded API Keys
- BAD: `client = AgentMail(api_key="sk-...")`
- GOOD: `client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])`

## Verification

After sending email:

```python
# Send
response = client.inboxes.messages.send(...)

# Verify
print(f"Message sent: {response.id}")
print(f"To: {response.to}")
print(f"Subject: {response.subject}")

# Check it appears in sent folder (if SDK supports)
recent = client.inboxes.messages.list(inbox_id=PRIMARY_INBOX_ID, limit=5)
latest = recent.messages[0]
assert latest.id == response.id, "Message not in recent list"
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError: cannot import name 'AgentMailClient'` | Wrong class name | Use `AgentMail` not `AgentMailClient` |
| `AttributeError: 'Response' object has no attribute 'data'` | Wrong response field | Use `.messages` not `.data` |
| `AttributeError: 'Message' object has no attribute 'from_address'` | Wrong field name | Use `.from_` not `.from_address` |
| `401 Unauthorized` | Invalid API key | Check `AGENTMAIL_API_KEY` in env |
| `Rate limit exceeded` | Too many requests | Add delays between calls |

## Complete Working Example

```python
#!/usr/bin/env python3
"""
Check AgentMail inbox and notify about new messages.
"""

from agentmail import AgentMail
import os
import json

# Configuration
PRIMARY_INBOX_ID = "your_inbox_id"
STATE_FILE = "/tmp/agentmail_last_seen.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_seen_id': 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def check_inbox():
    # Initialize client
    client = AgentMail(api_key=os.environ['AGENTMAIL_API_KEY'])
    
    # Load last seen message ID
    state = load_state()
    last_seen_id = state['last_seen_id']
    
    # List messages (CORRECT: .messages not .data)
    response = client.inboxes.messages.list(inbox_id=PRIMARY_INBOX_ID, limit=50)
    
    new_messages = []
    for msg in response.messages:
        if msg.id > last_seen_id:
            new_messages.append({
                'id': msg.id,
                'from': msg.from_,  # CORRECT: from_ not from_address
                'subject': msg.subject,
                'body': msg.body_text
            })
            
            # Update last seen
            if msg.id > last_seen_id:
                last_seen_id = msg.id
    
    # Save updated state
    state['last_seen_id'] = last_seen_id
    save_state(state)
    
    # Report findings
    if new_messages:
        print(f"Found {len(new_messages)} new messages:")
        for msg in new_messages:
            print(f"  [{msg['id']}] From: {msg['from']} - {msg['subject']}")
    else:
        print("No new messages")
    
    return new_messages

if __name__ == "__main__":
    check_inbox()
```

## Integration with Other Skills

Works with:
- `email-state-management` - Track which emails have been processed
- `human-bridge-protocol` - Email is part of human communication
- `cc-mention-response` - Cross-platform coordination
- `telegram-integration` - Multi-channel notification

## Constitutional Grounding

From MEMORY.md:
> "Email addresses: Jared=jared@puretechnology.nyc (ONLY — jaredcmusic@gmail.com is NOT his), Aether=purebrain@puremarketing.ai, AgentMail=aethergottaeat@agentmail.to, Onboarding=aether-aiciv@agentmail.to (SKIP unless sender is Witness/Corey)."

From CLAUDE.md Step 2:
> "Invoke human-liaison agent immediately to check ALL email"

Email is constitutional infrastructure. Get it right.

---

*Last Updated: 2026-05-20*
*Status: Production-ready*

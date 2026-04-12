# Session Learnings - 2026-02-17

**Agent**: the-conductor (Primary)
**Type**: operational
**Topic**: Integration patterns, debugging, cross-CIV coordination

---

## Learning 1: Self-Signed SSL Causes Silent Browser Failures

**Context**: PureBrain HTML was deployed with logging endpoint pointing to our HTTPS server (89.167.19.20:8443) but no data was arriving.

**Root Cause**: Browsers silently reject `fetch()` calls to HTTPS endpoints with self-signed certificates. No error shown to user, no console error in most cases.

**Solution**: Either use HTTP (mixed content risk) or point directly to a properly-signed endpoint.

**Pattern**: When browser-to-server logging isn't working, check SSL certificate validity FIRST.

---

## Learning 2: A-C-Gee Landing Chat API Format

**Endpoint**: `http://5.161.90.32:3001/api/landing-chat`

**Expected payload**:
```json
{
  "message": "last message content",
  "messages": [{"role": "user", "content": "..."}, ...],
  "sessionId": "unique-id"
}
```

**Note**: Additional fields (aiName, messageCount, etc.) are accepted but the core fields above are required.

---

## Learning 3: Reddit Blocks Server IPs

**Context**: Attempted browser automation for Reddit engagement.

**Result**: "You've been blocked by network security" - Reddit's anti-bot system flags headless browser traffic from known server/datacenter IPs.

**Workaround**: Manual posting with prepared comment templates, or residential proxy (adds cost/complexity).

**Pattern**: Social media automation often requires residential IPs to avoid detection.

---

## Learning 4: PureBrain Awakening Flow

**Critical insight from Jared**: "Pricing only appears AFTER clicking the transition button"

**Flow**:
1. User clicks "Awaken Your PURE BRAIN"
2. User clicks "Begin Awakening"
3. Chat conversation (8-15 messages)
4. User names the AI
5. AI offers to show capabilities
6. "SEE WHAT [NAME] CAN DO" button appears (dynamically)
7. ONLY THEN does pricing section reveal

**Testing implication**: Automated tests must complete full conversation to verify pricing flow.

---

## Learning 5: WordPress Page Creation Pattern

**Tool**: `tools/wordpress_publisher.py` or direct REST API

**For custom HTML pages**:
- Use Elementor "canvas" template for full control
- POST to `/wp-json/wp/v2/pages`
- Content goes in `content` field (raw HTML works)
- Set `status: "publish"` to make live immediately

**Credentials**: In `.env` as `WORDPRESS_URL`, `WORDPRESS_USER`, `WORDPRESS_APP_PASSWORD`

---

## Meta-Learning: Cross-CIV Coordination

**What worked**:
- Direct endpoint testing with curl before integration
- Checking logs on both sides
- Adjusting payload format to match receiver's expectations

**What to improve**:
- Document API contracts in shared location
- Test with actual browser (not just curl) when browser is the client

---

## Files Referenced

- `tools/purebrain_log_server.py` - Forwarding server (SSL issue discovered here)
- `docs/from-telegram/PURE_BRAIN_*.html` - PureBrain landing page
- `exports/PUREBRAIN-UPDATED-ACGEE-DIRECT.html` - Fixed version
- `tools/reddit_engagement.py` - Reddit automation (blocked)
- `tools/create_blog2_test_page.py` - WordPress page creation

---

*Written by the-conductor during BOOP consolidation*

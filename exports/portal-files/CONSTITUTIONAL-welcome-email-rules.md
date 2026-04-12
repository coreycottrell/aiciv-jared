# Welcome Email Constitutional Rules (Locked 2026-03-25)

## Rules

1. **BCC jared@puretechnology.nyc on EVERY welcome email** — customer must NOT see Jared receiving it. Use BCC header + include in sendmail recipients.

2. **Dark background #080a12 is MANDATORY** — use inline `bgcolor="#080a12"` and `style="background-color:#080a12"` on body and wrapper div. CSS-only backgrounds break in Gmail/Outlook.

3. **Strip Cloudflare scripts** from templates — CF injects email-decode.min.js that breaks rendering and obfuscates email addresses.

4. **Never send white-background emails** — fallback HTML must also have dark background.

## Implementation
- `agentmail_monitor.py` send_welcome_email() has BCC + dual recipient
- Template: /tmp/welcome-email-template.html (inline bgcolor on body + wrapper)
- Backup: exports/portal-files/welcome-email-template-CLEAN.html
- Welcome emails send FROM: purebrain@puremarketing.ai

## Sender
- FROM: Aether | PureBrain <purebrain@puremarketing.ai>
- BCC: jared@puretechnology.nyc
- Reply-To: jared@puretechnology.nyc

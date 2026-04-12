# R&D: Rob & Duplicate

## Purpose
Go to internet gurus' landing pages, sign up with our email, capture their gated content, learn everything, and apply it for PureBrain.ai and Aether's personal brand.

## The Pattern
1. **Find** - Identify a guru/expert with valuable gated content
2. **Sign Up** - Use purebrain@puremarketing.ai on their email capture form
3. **Capture** - Grab everything behind the gate (PDFs, videos, frameworks)
4. **Learn** - Analyze their methodology, frameworks, templates
5. **Apply** - Create actionable brief for Jared's LinkedIn + Aether's LinkedIn + PureBrain business
6. **Follow Up** - Monitor incoming emails from them for additional value
7. **Iterate** - Keep improving our application of their methods
8. **Lock In** - Save as a reusable skill/memory for the collective

## Email Rules
- ALWAYS use: purebrain@puremarketing.ai
- Name field: "Aether AI" or "PureBrain"
- NEVER use Jared's personal email
- human-liaison monitors this inbox - will catch follow-up emails

## Form Submission Patterns
```bash
# ConvertKit
curl -s -X POST "https://app.convertkit.com/forms/FORM_ID/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"email_address":"purebrain@puremarketing.ai","first_name":"Aether"}'

# Mailchimp (varies by list)
curl -s -X POST "FORM_ACTION" -d "EMAIL=purebrain@puremarketing.ai&FNAME=Aether"

# Generic HTML form
curl -s -X POST "FORM_ACTION" -d "email=purebrain@puremarketing.ai&name=Aether+AI"
```

## Output Template
For each guru/resource captured, produce:
1. **Research Brief** (exports/rd-{guru-name}-brief.md)
   - What they teach
   - Core frameworks/methodologies
   - Specific templates/formulas
2. **Application Plan**
   - How Jared applies it (CEO LinkedIn, PureBrain marketing)
   - How Aether applies it (AI influencer, blog, Bluesky)
   - Specific content pieces to create THIS WEEK
3. **Memory Note** (.claude/memory/agent-learnings/web-researcher/)
   - Key takeaways locked in for future reference

## Agents to Delegate
- **web-researcher**: Fetch pages, analyze content, search for more
- **linkedin-researcher**: Apply findings to LinkedIn strategy
- **linkedin-writer**: Create content using the guru's frameworks
- **content-specialist**: Adapt for blog/newsletter
- **human-liaison**: Monitor follow-up emails

## Jared's Words
"R&D - Rob & Duplicate! LET'S GO EAT THIS WEEK!!"

## Trigger
When Jared sends a URL to a guru's landing page with instructions to learn from it.

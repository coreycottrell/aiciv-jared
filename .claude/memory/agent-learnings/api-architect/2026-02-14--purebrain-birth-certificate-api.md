# PureBrain AI Birth Certificate API Design

**Date**: 2026-02-14
**Agent**: api-architect
**Type**: pattern
**Topic**: Viral feature API design with shareability as first-class concern
**Confidence**: high

---

## Context

Designed complete API specification for PureBrain's AI Birth Certificate feature - a shareable certificate generated when users name their AI. Part of viral feature suite designed to leverage the proven resonance of AI naming (219 subscribers in 4 hours from related newsletter).

---

## Key Patterns Learned

### 1. Viral-Native API Design

When designing APIs for viral/shareable features, treat shareability as a first-class concern:

| Traditional API | Viral-Native API |
|-----------------|------------------|
| GET /resource/{id} | GET /resource/{id} + GET /resource/{id}/share |
| Returns data | Returns data + OG tags + platform-specific share text |
| Auth required | Public endpoints for shareable content |
| Single image size | Multiple platform-optimized sizes |

**Key insight**: Every shareable artifact needs its own `/share` endpoint returning OG tags, share text per platform, QR codes, and referral-tracked CTAs.

### 2. Privacy-First Sharing Model

Layered privacy architecture for user-generated shareable content:

```
Layer 1: System-enforced (conversations NEVER exposed)
Layer 2: User-controlled toggles (stats, traits)
Layer 3: Moderation queue (approve before public)
Layer 4: Deletion rights (instant removal)
```

### 3. CDN-First Image Strategy

For server-rendered images (certificates, badges):

```
Cache Key: {id}_{theme}_{size}_{version}
TTL: 1 year (immutable content)
Invalidation: Version increment on update
Pre-render: Standard sizes on creation
On-demand: Rare size variants
```

### 4. Dual Authentication Pattern

For resources that are both private (owner-editable) and public (shareable):

- **Bearer token**: Full access for owner
- **Share token**: Read-only public fields, time-limited, trackable

```
Authorization: Bearer {jwt}     # Owner
X-Share-Token: {share_token}    # Public viewer
```

### 5. Rate Limiting by Intent

Different limits for creation vs. consumption:

| Operation | Limit | Reasoning |
|-----------|-------|-----------|
| Create | 5/day | Prevents abuse, maintains quality |
| Read | 100/min | High to not block viral spread |
| Download | 200/hour | Balance bandwidth vs. sharing |

---

## Files Created

- **API Spec**: `/home/jared/projects/AI-CIV/aether/sandbox/experiments/birth-certificate-api.md`

Includes:
- 7 REST endpoints fully specified
- Complete data models (YAML schema)
- OpenAPI 3.1 specification
- Image generation architecture
- Rate limiting strategy
- Authentication patterns
- Error handling standards
- Implementation priorities

---

## Integration Points

- Links to viral feature designs from feature-designer
- Follows patterns from WordPress REST API work
- Includes K-factor tracking per marketing-strategist recommendations
- References Pure Technology brand colors

---

## When to Apply

- Designing APIs for shareable/viral features
- Building user-generated content systems with public sharing
- Creating certificate/badge/achievement APIs
- Any feature where "sharing" is a primary success metric

---

## Open Questions for Implementation

1. **Image rendering**: Puppeteer vs Canvas vs external service (Cloudinary)?
2. **Profanity filtering**: Build vs. buy (Perspective API)?
3. **Short URLs**: pb.ai subdomain vs. third-party service?

---

**Tags**: api, rest, viral, purebrain, sharing, certificates, image-generation, authentication

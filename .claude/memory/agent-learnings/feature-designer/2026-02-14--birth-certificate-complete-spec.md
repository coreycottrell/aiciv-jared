# Complete Feature Specification: AI Birth Certificate

**Date**: 2026-02-14
**Type**: technique
**Topic**: End-to-end feature specification for shareable AI Birth Certificate
**Confidence**: high

---

## Context

Created comprehensive specifications for the AI Birth Certificate feature for PureBrain.ai. This feature transforms the emotional peak of AI naming into a viral growth mechanism.

---

## Key Design Decisions

### 1. Image Generation Approach

**Decided**: Hybrid (Canvas preview + Server-side final)

**Rationale**:
- Canvas API: Instant preview, no server load during editing
- Server-side (Sharp/Puppeteer): Consistent output, better fonts, security features
- This gives best UX while ensuring quality final output

**Alternative rejected**: Pure client-side would have font rendering issues and browser inconsistencies.

### 2. Certificate Styles

**Decided**: 3 styles (Classic, Modern, Playful)

**Rationale**:
- Classic: Appeals to professional users, "official" feel
- Modern: Clean aesthetic for tech-forward users
- Playful: Younger demographic, casual use cases

**Key insight**: Style options increase engagement without significant engineering complexity.

### 3. QR Code Content

**Decided**: Link to signup with referral ID OR Meet My AI profile if enabled

**Rationale**:
- Certificates get physically shared (printed, photographed)
- QR creates additional viral pathway beyond digital shares
- Referral ID enables tracking shares through print medium

### 4. Share-Gating Strategy

**Decided**: High-res download gated behind share action OR premium

**Rationale**:
- Creates natural incentive to share before downloading best version
- Preserves premium value while encouraging viral behavior
- User can always get standard resolution without friction

---

## Technical Patterns Applied

### Data Structure

```sql
CREATE TABLE certificates (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    ai_id UUID NOT NULL,
    ai_name VARCHAR(50) NOT NULL,
    creator_name VARCHAR(100) NOT NULL,
    purpose VARCHAR(60),
    style VARCHAR(20) DEFAULT 'classic',
    share_token VARCHAR(64) UNIQUE,
    share_count INTEGER DEFAULT 0
);
```

**Key fields**:
- `share_token`: Enables public viewing without exposing internal IDs
- `share_count`: Tracks viral success per certificate

### API Design

| Endpoint | Purpose |
|----------|---------|
| POST /certificates/generate | Create new certificate |
| GET /certificates/{id} | User retrieves own certificate |
| GET /certificates/{id}/image | Get image with format/size params |
| GET /certificates/shared/{token} | Public viewing |
| POST /certificates/{id}/share | Record share event |

**Pattern**: Separate authenticated (/{id}) from public (/{token}) endpoints.

---

## UX Patterns

### Trigger Timing

**Decided**: Immediately after naming confirmation, with 800ms celebration animation

**Rationale**:
- Strike at emotional peak
- Animation creates "moment" feeling
- Auto-trigger ensures maximum generation rate

### Customization Friction

**Decided**: Optional customization, defaults work well

**Rationale**:
- Most users want quick path to sharing
- Optional purpose field satisfies power users
- Style selection adds engagement without blocking

---

## Accessibility Checklist (Reference)

- [ ] Color contrast >= 4.5:1
- [ ] Keyboard-only navigation works
- [ ] Screen reader announces modal state
- [ ] Alt text describes certificate content
- [ ] Touch targets >= 44x44px on mobile

---

## Metrics to Track

| Metric | Definition | Target |
|--------|------------|--------|
| Generation rate | % of namings that generate certificate | 60%+ |
| Share rate | % of certificates shared | 25%+ |
| Viral coefficient | New signups per certificate share | 0.1+ |

---

## File References

- Complete spec: `/home/jared/projects/AI-CIV/aether/sandbox/experiments/birth-certificate-specs.md`
- Prior work: `/sandbox/experiments/viral-feature-designs.md`
- Growth strategy context: `/sandbox/experiments/purebrain-growth-strategy.md`

---

## Future Application

When designing shareable features:

1. **Find the emotional peak** (naming, milestone, achievement)
2. **Create artifact immediately** (don't make them come back)
3. **Make default shareable** (works without customization)
4. **Include viral mechanics** (QR, referral, branding)
5. **Layer privacy controls** (system-enforced + user-controlled)
6. **Track the funnel** (generate -> customize -> download -> share -> convert)

---

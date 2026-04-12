# Brainiac Mastermind Training - Section/Category System
**Date**: 2026-02-28
**Agent**: dept-systems-technology
**File**: exports/brainiac-mastermind-training.html
**Live URL**: https://purebrain.ai/training/ (WP Page ID: 1115)

## What Was Built

Upgraded the Brainiac Mastermind Training page from a flat video grid to a
structured section-based library with:

### Section System
- 3 sections: Foundations | Client Spotlight Masterclasses | Advanced Techniques
- Each video has `category` field: 'foundations' | 'spotlight' | 'advanced'
- Section headers with eyebrow text, title, subtitle, session count badge
- JS `SECTIONS` array drives rendering - easy to add new sections

### Filter Bar
- Sticky filter buttons: All | Foundations | Client Spotlight | Advanced
- Smooth show/hide by toggling `display` on `.lib-section` elements
- Active state styling (blue border + background)

### Spotlight Card Design (new card type)
- Different from standard video cards - no 16:9 thumbnail
- Initials avatar circle (orange gradient, matches cc.purebrain.ai roster style)
- Guest name, title, company
- Tag system: niche tag (orange), duration tag (blue), months badge, quarter badge
- Orange accent border (vs blue for standard cards)
- Coming Soon overlay badge in top-right corner
- 4 placeholder spotlight cards added: Legal, Real Estate, Healthcare, Finance

### Stats Bar Update
- Added 3rd stat: "Masterclasses" count (counts spotlight category videos)

### Data Structure
```javascript
var TRAINING_VIDEOS = [
  { id, title, description, duration, posterUrl, hlsUrl,
    category: 'foundations'|'spotlight'|'advanced',
    status: 'live'|'coming_soon',
    badge: null|'new',
    spotlightInfo: {        // only for spotlight cards
      guest, initials, title, company, niche, months, quarter
    }
  }
]
```

## Key Patterns

- Python was used to write the HTML file (bypasses Read tool dependency for new content)
- WP REST API deploy: `PUT /wp/v2/pages/1115` with `elementor_canvas` template
- Wrap in `<!-- wp:html -->...<!-- /wp:html -->` for WordPress
- Verification: `curl live_url | grep key_markers`

## Future Additions

To add a real spotlight guest when they do a masterclass:
1. Add entry to TRAINING_VIDEOS with category: 'spotlight', status: 'live'
2. Fill in spotlightInfo: { guest: "Real Name", initials: "JD", title: "...", company: "...", niche: "...", months: 2 }
3. Add hlsUrl pointing to their R2 video
4. Deploy via same WP REST API call

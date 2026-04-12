# PMG Thank You Page - Elementor Implementation Notes

**Date**: 2026-02-13
**Author**: full-stack-developer
**Purpose**: Section-by-section guide for implementing the Thank You page in Elementor

---

## Brand Colors (Set in Theme Settings)

```
Primary: #1a365d (deep blue)
Secondary: #2b6cb0 (medium blue)
Accent: #38b2ac (teal)
Light Background: #f7fafc
Text: #2d3748
Border: #e2e8f0
```

---

## Section 1: Confirmation (Above Fold)

### Layout
- **Widget Type**: Container (Full Width)
- **Background**: Gradient - Primary (#1a365d) to Secondary (#2b6cb0) at 135deg
- **Padding**: 80px top/bottom, 20px left/right
- **Text Align**: Center

### Elements

#### 1.1 Animated Checkmark
- **Widget**: Icon or Lottie Animation
- **Icon**: Check Circle (Font Awesome)
- **Size**: 80px
- **Color**: White
- **Animation**: Fade In + Zoom In (0.8s duration, 0.3s delay)
- **Margin**: 0 auto 30px

#### 1.2 Main Heading
- **Widget**: Heading
- **Text**: "Your Strategy Call is Confirmed!"
- **Tag**: H1
- **Font Size**: 40px (desktop), 28px (tablet), 24px (mobile)
- **Font Weight**: 700
- **Color**: #FFFFFF
- **Margin Bottom**: 20px

#### 1.3 Call Details Box
- **Widget**: Text Editor (nested in Container)
- **Container Background**: rgba(255, 255, 255, 0.1)
- **Container Border Radius**: 12px
- **Container Padding**: 30px
- **Container Max Width**: 600px
- **Font Size**: 18px
- **Color**: #FFFFFF

**Content**:
```html
<p><strong>Date:</strong> [DATE]</p>
<p><strong>Time:</strong> [TIME]</p>
<p><strong>Format:</strong> Video Call</p>
```

#### 1.4 Button Group
- **Widget**: Two Button widgets in a flex container
- **Container Flex**: Direction: Row, Justify: Center, Gap: 20px
- **Mobile**: Change to Column direction

**Button 1 (Primary)**:
- Text: "Add to Calendar"
- Type: Primary
- Background: #FFFFFF
- Text Color: #1a365d
- Padding: 15px 30px
- Border Radius: 8px
- Hover: Transform translateY(-2px), Box Shadow
- Link: [Calendar Link]

**Button 2 (Secondary)**:
- Text: "Need to Reschedule?"
- Type: Outline
- Border: 2px solid #FFFFFF
- Text Color: #FFFFFF
- Background: Transparent
- Padding: 15px 30px
- Border Radius: 8px
- Hover: Background #FFFFFF, Text #1a365d
- Link: [Reschedule Link]

#### 1.5 What Happens Next
- **Widget**: Text Editor (nested in Container)
- **Container Background**: rgba(255, 255, 255, 0.1)
- **Container Border Radius**: 12px
- **Container Padding**: 30px
- **Container Max Width**: 600px
- **Margin Top**: 40px

**Content**:
```html
<h2 style="font-size: 24px; margin-bottom: 20px;">What Happens Next</h2>
<ol style="margin-left: 20px; font-size: 18px; line-height: 1.8;">
  <li>Check your email for confirmation details</li>
  <li>Download the prep resource below</li>
  <li>Come ready to discuss your biggest marketing challenge</li>
</ol>
```

---

## Section 2: Video Message from Jared

### Layout
- **Widget Type**: Container (Boxed, 1200px max)
- **Background**: #FFFFFF
- **Padding**: 60px top/bottom, 20px left/right
- **Text Align**: Center

### Elements

#### 2.1 Section Heading
- **Widget**: Heading
- **Text**: "What to Expect From Our Conversation"
- **Tag**: H2
- **Font Size**: 32px (desktop), 28px (tablet), 24px (mobile)
- **Color**: #1a365d
- **Margin Bottom**: 30px

#### 2.2 Video Embed
- **Widget**: Video
- **Source**: YouTube/Vimeo
- **URL**: [Your Video URL]
- **Aspect Ratio**: 16:9
- **Max Width**: 900px
- **Border Radius**: 12px
- **Margin Bottom**: 30px
- **Controls**: Show
- **Autoplay**: No

#### 2.3 Quote Box
- **Widget**: Text Editor
- **Max Width**: 800px
- **Padding**: 30px
- **Background**: #f7fafc
- **Border Left**: 4px solid #38b2ac
- **Font Size**: 20px (desktop), 18px (mobile)
- **Font Style**: Italic
- **Color**: #1a365d
- **Line Height**: 1.6

**Content**:
```html
"Most marketing fails not because of bad creative. It fails because brands are buying attention when they should be engineering fascination."
```

---

## Section 3: Authority & Social Proof

### Layout
- **Widget Type**: Container (Full Width)
- **Background**: #f7fafc
- **Padding**: 60px top/bottom, 20px left/right

### Elements

#### 3.1 Logo Row
- **Widget**: Image Carousel or Gallery
- **Layout**: Flex Row, Justify: Space Around, Wrap
- **Gap**: 40px
- **Opacity**: 0.7
- **Image Count**: 4-6
- **Image Size**: 150x60px each
- **Margin**: 40px 0

**Note**: Upload client logos or use placeholder images

#### 3.2 Testimonials
- **Widget**: Testimonial Carousel or 3 Testimonial widgets in a grid
- **Layout**: Grid (3 columns desktop, 1 column mobile)
- **Gap**: 30px

**Each Testimonial**:
- Background: #FFFFFF
- Padding: 30px
- Border Radius: 12px
- Box Shadow: 0 4px 6px rgba(0,0,0,0.1)

**Testimonial 1**:
```
Quote: "Working with PMG transformed how we think about marketing. Instead of chasing impressions, we now create experiences people actually want to engage with. The results speak for themselves."
Name: Sarah Mitchell
Title: CMO, TechVision Inc.
```

**Testimonial 2**:
```
Quote: "Jared's approach to experiential marketing is unlike anything we'd tried before. Within 90 days we saw engagement rates triple and our ROI increase by 300%."
Name: Michael Chen
Title: VP Marketing, GrowthLabs
```

**Testimonial 3**:
```
Quote: "The PMG framework gave us a competitive advantage we didn't know was possible. Instead of competing on price, we now compete on experience."
Name: Jennifer Rodriguez
Title: Founder, BrightPath Solutions
```

#### 3.3 Stats Row
- **Widget**: 3 Counter widgets in a flex container
- **Container**: Flex Row, Justify: Center, Gap: 60px
- **Container Background**: #FFFFFF
- **Container Padding**: 40px
- **Container Border Radius**: 12px
- **Container Margin Top**: 40px
- **Mobile**: Change to Column

**Stat 1**:
- Number: "15+"
- Label: "Years Experience"
- Number Color: #38b2ac
- Number Size: 32px
- Label Color: #666666
- Label Size: 14px

**Stat 2**:
- Number: "$50M+"
- Label: "Revenue Driven"
- Number Color: #38b2ac
- Number Size: 32px
- Label Color: #666666
- Label Size: 14px

**Stat 3**:
- Number: "300%+"
- Label: "Average ROI"
- Number Color: #38b2ac
- Number Size: 32px
- Label Color: #666666
- Label Size: 14px

---

## Section 4: Pre-Call Resource

### Layout
- **Widget Type**: Container (Boxed, 1200px max)
- **Background**: #FFFFFF
- **Padding**: 60px top/bottom, 20px left/right
- **Text Align**: Center

### Elements

#### 4.1 Resource Card
- **Widget**: Container (nested)
- **Max Width**: 600px
- **Padding**: 40px
- **Background**: Gradient - Primary to Secondary at 135deg
- **Border Radius**: 16px
- **Box Shadow**: 0 10px 30px rgba(0,0,0,0.2)

**Card Elements**:

1. **Heading**:
   - Widget: Heading (H3)
   - Text: "The PMG Experiential Playbook"
   - Color: #FFFFFF
   - Font Size: 28px (desktop), 22px (mobile)
   - Margin Bottom: 10px

2. **Subtitle**:
   - Widget: Text Editor
   - Text: "How we engineer fascination instead of buying attention"
   - Color: rgba(255,255,255,0.9)
   - Font Size: 18px
   - Margin Bottom: 30px

3. **Download Button**:
   - Widget: Button
   - Text: "Download Playbook (PDF)"
   - Background: #38b2ac
   - Text Color: #FFFFFF
   - Padding: 15px 30px
   - Border Radius: 8px
   - Link: [PDF Download URL]
   - Hover: Transform scale(1.05)

4. **Note**:
   - Widget: Text Editor
   - Text: "No email required - you've already booked"
   - Color: rgba(255,255,255,0.8)
   - Font Size: 14px
   - Margin Top: 20px

---

## Section 5: Differentiation Table

### Layout
- **Widget Type**: Container (Full Width)
- **Background**: #f7fafc
- **Padding**: 60px top/bottom, 20px left/right

### Elements

#### 5.1 Section Heading
- **Widget**: Heading
- **Text**: "Why PMG is Different"
- **Tag**: H2
- **Font Size**: 32px
- **Color**: #1a365d
- **Text Align**: Center
- **Margin Bottom**: 40px

#### 5.2 Comparison Table
- **Widget**: Table widget OR custom HTML
- **Max Width**: 900px
- **Background**: #FFFFFF
- **Border Radius**: 12px
- **Box Shadow**: 0 4px 6px rgba(0,0,0,0.1)

**Table Structure** (use HTML widget if needed):
```html
<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr>
      <th style="background: #666; color: white; padding: 20px; font-size: 18px;">Traditional Marketing</th>
      <th style="background: #38b2ac; color: white; padding: 20px; font-size: 18px;">PMG Approach</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; color: #666;">Buy attention</td>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1a365d;">Engineer fascination</td>
    </tr>
    <tr>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; color: #666;">Interrupt audiences</td>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1a365d;">Create experiences they seek out</td>
    </tr>
    <tr>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; color: #666;">Measure impressions</td>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1a365d;">Measure engagement depth</td>
    </tr>
    <tr>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; color: #666;">Campaign-based</td>
      <td style="padding: 20px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1a365d;">Relationship-based</td>
    </tr>
    <tr>
      <td style="padding: 20px; color: #666;">Hope for virality</td>
      <td style="padding: 20px; font-weight: 600; color: #1a365d;">Design for shareability</td>
    </tr>
  </tbody>
</table>
```

**Responsive Note**: On mobile, consider stacking rows or using accordion widget instead

---

## Section 6: Case Study Preview

### Layout
- **Widget Type**: Container (Boxed, 1200px max)
- **Background**: #FFFFFF
- **Padding**: 60px top/bottom, 20px left/right

### Elements

#### 6.1 Section Heading
- **Widget**: Heading
- **Text**: "How [Client] Achieved [Result]"
- **Tag**: H2
- **Font Size**: 32px
- **Color**: #1a365d
- **Text Align**: Center
- **Margin Bottom**: 40px

#### 6.2 Case Study Content
- **Widget**: 3 Text Editor widgets in a vertical stack
- **Container Max Width**: 800px
- **Gap**: 30px

**Block 1 - Challenge**:
- Widget: Text Editor (in Container)
- Container Padding: 30px
- Container Background: #f7fafc
- Container Border Left: 4px solid #38b2ac
- Container Border Radius: 8px

```html
<h3 style="color: #1a365d; margin-bottom: 10px; font-size: 20px;">The Challenge</h3>
<p style="font-size: 18px; line-height: 1.6;">[Client description] was struggling with traditional marketing approaches that generated impressions but failed to create meaningful engagement. Their campaigns were expensive, their audience was disengaged, and their competitors were outmaneuvering them on every front.</p>
```

**Block 2 - Approach**:
- Widget: Text Editor (in Container)
- Same styling as Block 1

```html
<h3 style="color: #1a365d; margin-bottom: 10px; font-size: 20px;">Our Approach</h3>
<p style="font-size: 18px; line-height: 1.6;">We implemented the PMG Experiential Framework, transforming their marketing from interrupt-based campaigns to experience-driven engagement. Instead of buying attention, we engineered fascination through [specific strategy placeholder]. We redesigned their customer journey to create moments of genuine connection and shareability.</p>
```

**Block 3 - Results**:
- Widget: Text Editor (in Container)
- Container Padding: 30px
- Container Background: Gradient (Primary to Secondary at 135deg)
- Container Border Left: 4px solid #38b2ac
- Container Border Radius: 8px
- Text Color: #FFFFFF

```html
<h3 style="color: white; margin-bottom: 10px; font-size: 20px;">The Results</h3>
<p style="font-size: 18px; line-height: 1.8;">
  <strong>47% increase in engagement</strong><br>
  <strong>$2.3M revenue attributed</strong><br>
  <strong>4.2x ROAS</strong>
</p>
```

---

## Section 7: Footer CTA

### Layout
- **Widget Type**: Container (Full Width)
- **Background**: Gradient - Primary to Secondary at 135deg
- **Padding**: 60px top/bottom, 20px left/right
- **Text Align**: Center
- **Color**: #FFFFFF

### Elements

#### 7.1 Heading
- **Widget**: Heading
- **Text**: "Questions before our call?"
- **Tag**: H2
- **Font Size**: 32px
- **Color**: #FFFFFF
- **Margin Bottom**: 20px

#### 7.2 Email Link
- **Widget**: Text Editor
- **Font Size**: 18px
- **Margin Bottom**: 30px

```html
<p><a href="mailto:hello@puremarketing.ai" style="color: #38b2ac; font-size: 20px; font-weight: 600; text-decoration: none;">hello@puremarketing.ai</a></p>
```

#### 7.3 Social Icons
- **Widget**: Social Icons widget
- **Layout**: Flex Row, Justify: Center, Gap: 20px
- **Icon Shape**: Circle
- **Icon Size**: 50px
- **Icon Background**: rgba(255,255,255,0.1)
- **Icon Color**: #FFFFFF
- **Hover**: Background #FFFFFF, Color #1a365d, Transform translateY(-3px)

**Icons**:
- LinkedIn: [LinkedIn URL]
- Twitter: [Twitter URL]

#### 7.4 Closing Date
- **Widget**: Text Editor
- **Font Size**: 20px
- **Font Weight**: 600
- **Color**: #FFFFFF
- **Margin Top**: 20px

```html
<p>See you on <strong>[DATE]</strong>!</p>
```

---

## Global Settings

### Typography
- **Heading Font**: System font stack (San Francisco, Segoe UI, Roboto)
- **Body Font**: Same as headings
- **Line Height**: 1.6 for body text

### Responsive Breakpoints
- **Desktop**: 1024px+
- **Tablet**: 768px - 1023px
- **Mobile**: 0 - 767px

### Mobile Optimizations
- Reduce font sizes by 20-30%
- Stack flex rows to columns
- Reduce padding/spacing by 30-40%
- Ensure touch targets are at least 44x44px
- Test video embed on mobile devices

---

## Dynamic Content Setup

### Fields to Make Dynamic (if using Dynamic Tags or ACF):
1. `[DATE]` - Call date
2. `[TIME]` - Call time
3. `[VIDEO_ID]` - YouTube/Vimeo ID
4. Calendar link URL
5. Reschedule link URL
6. PDF download URL
7. Client logos
8. Case study client name and results

---

## Testing Checklist

- [ ] All buttons link to correct URLs
- [ ] Video embeds and plays correctly
- [ ] Animations trigger on scroll
- [ ] Form submissions work (if applicable)
- [ ] Mobile: All sections stack properly
- [ ] Mobile: Text is readable (min 16px)
- [ ] Mobile: Buttons are tappable (min 44px height)
- [ ] Tablet: Layout adapts appropriately
- [ ] Desktop: Max width constraints work
- [ ] All images have alt text
- [ ] Color contrast meets WCAG AA (4.5:1 minimum)
- [ ] Page loads in under 3 seconds
- [ ] Meta robots tag is set to noindex, nofollow

---

## Implementation Time Estimate

- Section 1 (Confirmation): 15-20 min
- Section 2 (Video): 10 min
- Section 3 (Authority): 20-25 min
- Section 4 (Resource): 10 min
- Section 5 (Table): 15 min
- Section 6 (Case Study): 15 min
- Section 7 (Footer): 10 min
- **Total**: 95-105 minutes

---

## Notes

1. **Checkmark Animation**: If Elementor doesn't support SVG animations, use a Lottie animation widget with a checkmark animation from LottieFiles.

2. **Video Embed**: Test video autoplay policies. Most browsers block autoplay with sound. Consider adding a play button overlay.

3. **Table on Mobile**: The comparison table may be hard to read on mobile. Consider using an accordion widget as an alternative for mobile views.

4. **Dynamic Content**: If connecting to a booking system, integrate dynamic fields using Elementor's Dynamic Tags or ACF integration.

5. **Calendar Link**: Generate .ics file links using a service like AddEvent or AddToCalendar for cross-platform compatibility.

6. **PDF Hosting**: Host the playbook PDF on your server or use a CDN. Track downloads with Google Analytics events.

7. **Social Proof**: Replace placeholder testimonials and logos with real client data as soon as available.

---

**END OF ELEMENTOR NOTES**

# Google Tag Manager - Manual Setup Instructions

**Container**: GTM-WTDXL4VJ
**Account**: purebrain@puremarketing.ai
**URL**: https://tagmanager.google.com/

---

## Summary

Add these 3 tags to the GTM container and publish:

1. **GA4 - PureBrain** (Google Tag, ID: G-86325WBT3P)
2. **Search Console Verification** (Custom HTML)
3. **Microsoft Clarity** (Custom HTML)

---

## Step-by-Step Instructions

### Step 1: Login to GTM

1. Go to https://tagmanager.google.com/
2. Sign in with **purebrain@puremarketing.ai**
3. Select the container **GTM-WTDXL4VJ**

---

### Step 2: Add GA4 Tag

1. Click **"Tags"** in the left sidebar
2. Click **"New"** button
3. Click **"Tag Configuration"** area
4. Select **"Google Tag"** from the list
5. Enter Tag ID: **`G-86325WBT3P`**
6. Click **"Triggering"** area
7. Select **"All Pages"**
8. Click on the tag name at the top and rename to: **`GA4 - PureBrain`**
9. Click **"Save"**

---

### Step 3: Add Search Console Verification Tag

1. Click **"New"** button
2. Click **"Tag Configuration"** area
3. Select **"Custom HTML"**
4. Paste this code:

```html
<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />
```

5. Click **"Triggering"** area
6. Select **"All Pages"**
7. Rename tag to: **`Search Console Verification`**
8. Click **"Save"**

---

### Step 4: Add Microsoft Clarity Tag

1. Click **"New"** button
2. Click **"Tag Configuration"** area
3. Select **"Custom HTML"**
4. Paste this code:

```html
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "viy9bnc56x");
</script>
```

5. Click **"Triggering"** area
6. Select **"All Pages"**
7. Rename tag to: **`Microsoft Clarity`**
8. Click **"Save"**

---

### Step 5: Publish Changes

1. Click **"Submit"** button (top right)
2. Enter version name: **`Added GA4, Search Console, Clarity`**
3. Click **"Publish"**

---

## Verification

After publishing, verify the tags are working:

1. **GTM Preview Mode**: Use GTM's preview/debug mode to test on purebrain.ai
2. **GA4**: Check Google Analytics > Real-time to see if data flows
3. **Search Console**: Verify ownership in Search Console (may take 24-48 hours)
4. **Clarity**: Check clarity.microsoft.com dashboard for session recordings

---

## Tag Details

| Tag Name | Type | Configuration | Trigger |
|----------|------|---------------|---------|
| GA4 - PureBrain | Google Tag | ID: G-86325WBT3P | All Pages |
| Search Console Verification | Custom HTML | Meta tag | All Pages |
| Microsoft Clarity | Custom HTML | Clarity script | All Pages |

---

## Troubleshooting

**Tags not firing?**
- Check GTM container code is installed on purebrain.ai (it should be via the GTM4WP plugin)
- Clear site cache after publishing
- Use GTM Preview mode to debug

**GA4 not receiving data?**
- Verify the GA4 property ID is correct
- Check for ad blockers
- Wait a few minutes for data to appear

**Search Console verification failing?**
- The meta tag method may take time to propagate
- Alternative: Use DNS verification or file upload method

---

*Created: 2026-02-17*
*For: Jared / Aether*

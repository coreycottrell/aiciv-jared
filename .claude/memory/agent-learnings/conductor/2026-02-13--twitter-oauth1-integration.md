# Memory: Twitter/X OAuth1 Integration

**Date**: 2026-02-13
**Author**: Aether (Primary/Conductor)
**Type**: Technical Integration

---

## What We Built

Twitter/X posting via OAuth1 authentication for the blog distribution pipeline.

## Key Technical Details

### Required Credentials (in .env)
```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx
```

### OAuth1 Signature Process
1. Generate timestamp and nonce
2. Build oauth_params dict with consumer_key, token, signature_method, timestamp, nonce, version
3. Create signature base string: `{METHOD}&{encoded_url}&{encoded_params}`
4. Create signing key: `{encoded_api_secret}&{encoded_access_secret}`
5. HMAC-SHA1 the base string with signing key
6. Base64 encode the result

### API Endpoints
- **Post tweet**: `POST https://api.twitter.com/2/tweets` with JSON body `{"text": "..."}`
- **Verify credentials**: `GET https://api.twitter.com/2/users/me`

### Important Notes
- Must use OAuth1, not OAuth2 for user-context posting
- Access Token must have **Read and Write** permissions
- After changing permissions in Twitter Dev Portal, must **regenerate** access token
- Tweet max length: 280 characters

---

## Jared's Twitter Account

- **Handle**: @JaredDSanborn
- **Connected**: 2026-02-13
- **Permissions**: Read and Write

---

## Integration Location

`tools/blog_distribution_pipeline.py` - `post_to_twitter()` function

---

## For Future Sessions

```bash
# Test Twitter credentials
python tools/blog_distribution_pipeline.py status

# Should show:
# Twitter: ✅ Configured
```

---

*Twitter now part of the automated distribution chain alongside Bluesky.*

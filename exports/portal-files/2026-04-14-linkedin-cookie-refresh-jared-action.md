# LinkedIn Cookie Refresh — 5-Minute Action for Jared

**Why**: LinkedIn automated posting is failing because the `li_at` session cookie in `.env` expired. Lyra confirmed this is the sole root cause. Fresh cookie = autopilot back online.

---

## Do This (4 steps, <5 minutes)

1. **Open Chrome** (logged into your LinkedIn account as Jared Sanborn) → go to https://www.linkedin.com
2. **Open DevTools**: Press `F12` (or right-click → Inspect) → click the **Application** tab → left sidebar: **Storage → Cookies → https://www.linkedin.com**
3. **Copy these 2 cookie values** (click the row, copy the Value column):
   - `li_at` (the big one — starts with `AQE...`)
   - `JSESSIONID` (starts with `ajax:`)
4. **Send them back via portal** in this exact format (one line each):

```
li_at=AQEDA...paste full value here
JSESSIONID=ajax:...paste full value here
```

That's it. I'll rotate them into `.env`, restart the LinkedIn scheduler, and verify a live post within 10 minutes of receipt.

---

## Cookie Lifespan Note

LinkedIn `li_at` cookies last ~365 days but get invalidated early if:
- You log out on any device
- LinkedIn detects automation (rare with our pacing)
- Password change

Next expected refresh: April 2027. I'll alert 30 days out.

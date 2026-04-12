/**
 * LinkedIn OAuth + Posting module for PureApex Worker
 *
 * Endpoints:
 *   GET  /linkedin/auth                  - OAuth redirect
 *   GET  /linkedin/callback              - OAuth callback
 *   GET  /api/linkedin/status            - Connection status (session-auth)
 *   POST /api/linkedin/post              - Text-only post (session-auth)
 *   POST /api/linkedin/post-with-image   - Text + image post (internal-auth)
 */

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

// ── Constant-time string comparison (prevents timing attacks) ──
function timingSafeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

// ── SSRF guard: only allow https from known hosts ──
// Explicit deny list for private/internal ranges (defense-in-depth, M-3)
const SSRF_DENY_HOSTS = new Set([
  'localhost',
  'metadata.google.internal',
  'metadata',
  '169.254.169.254',     // AWS/GCP/Azure metadata
  '100.100.100.200',     // Alibaba metadata
  '::1',
]);

function isPrivateOrReservedIP(host) {
  // IPv4 literal checks
  const v4 = host.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
  if (v4) {
    const [a, b] = [parseInt(v4[1], 10), parseInt(v4[2], 10)];
    if (a === 10) return true;                              // 10.0.0.0/8
    if (a === 127) return true;                             // 127.0.0.0/8 loopback
    if (a === 172 && b >= 16 && b <= 31) return true;       // 172.16.0.0/12
    if (a === 192 && b === 168) return true;                // 192.168.0.0/16
    if (a === 169 && b === 254) return true;                // 169.254.0.0/16 link-local
    if (a === 0) return true;                               // 0.0.0.0/8
    if (a >= 224) return true;                              // multicast + reserved
    return false;
  }
  // IPv6 literal checks (bracket-stripped by URL parser)
  if (host.includes(':')) {
    const h = host.toLowerCase();
    if (h === '::1' || h === '::') return true;             // loopback / unspecified
    if (h.startsWith('fe80:') || h.startsWith('fe80::')) return true; // link-local
    if (h.startsWith('fc') || h.startsWith('fd')) return true;        // ULA fc00::/7
    return false;
  }
  return false;
}

function isImageUrlSafe(url) {
  let u;
  try { u = new URL(url); } catch { return false; }
  if (u.protocol !== 'https:') return false;

  // Reject trailing-dot hostnames (e.g. "purebrain.ai.") which bypass Set match
  if (u.hostname.endsWith('.')) return false;

  // Reject explicit user/pass and non-default ports
  if (u.username || u.password) return false;

  const host = u.hostname.toLowerCase();

  // Explicit deny list (metadata, loopback, localhost)
  if (SSRF_DENY_HOSTS.has(host)) return false;

  // Reject IP literals in private/reserved ranges
  if (isPrivateOrReservedIP(host)) return false;

  const allowedHosts = new Set([
    'purebrain.ai', 'www.purebrain.ai', 'cdn.purebrain.ai',
    'jareddsanborn.com', 'www.jareddsanborn.com',
  ]);
  return allowedHosts.has(host);
}

// ── Rate limit: max 5 posts/hour (atomic, race-safe) ──
// Uses conditional UPDATE so two concurrent Workers cannot both pass the cap.
// SQLite/D1 serializes UPDATE WHERE on the row; meta.changes === 0 means
// either the row didn't exist yet or count was already >= 5.
async function checkAndIncrementRateLimit(env) {
  const hourKey = new Date().toISOString().slice(0, 13); // "YYYY-MM-DDTHH"

  // Ensure row exists (idempotent, no-op if already present)
  await env.DB.prepare(
    'INSERT INTO linkedin_rate_limit (hour_key, count) VALUES (?, 0) ' +
    'ON CONFLICT(hour_key) DO NOTHING'
  ).bind(hourKey).run();

  // Atomic conditional increment — only succeeds if count < 5
  const result = await env.DB.prepare(
    'UPDATE linkedin_rate_limit SET count = count + 1 WHERE hour_key = ? AND count < 5'
  ).bind(hourKey).run();

  if (!result.meta || result.meta.changes === 0) {
    return { ok: false, reason: 'rate_limit_exceeded' };
  }
  return { ok: true };
}

// ── Token refresh (if expiring within 5 min) ──
async function getValidTokenRow(env) {
  const { results } = await env.DB.prepare(
    'SELECT access_token, expires_at, linkedin_id, refresh_token FROM linkedin_tokens ORDER BY created_at DESC LIMIT 1'
  ).all();
  if (results.length === 0) return { error: 'LinkedIn not connected' };
  const row = results[0];
  if (!row.linkedin_id) return { error: 'LinkedIn user ID not available' };

  const expiresAt = row.expires_at ? new Date(row.expires_at).getTime() : 0;
  const refreshThreshold = Date.now() + 5 * 60 * 1000;

  if (expiresAt < refreshThreshold) {
    if (!row.refresh_token) {
      return { error: 'Token expired and no refresh token available' };
    }
    try {
      const refreshResp = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          client_id: env.LINKEDIN_CLIENT_ID,
          client_secret: env.LINKEDIN_CLIENT_SECRET,
          refresh_token: row.refresh_token,
        }),
      });
      if (!refreshResp.ok) {
        return { error: 'Token refresh failed' };
      }
      const tokenData = await refreshResp.json();
      const newAccess = tokenData.access_token;
      const newExpiresIn = tokenData.expires_in || 5184000;
      const newExpiresAt = new Date(Date.now() + newExpiresIn * 1000).toISOString();
      const newRefresh = tokenData.refresh_token || row.refresh_token;
      await env.DB.prepare(
        'UPDATE linkedin_tokens SET access_token = ?, expires_at = ?, refresh_token = ? WHERE linkedin_id = ?'
      ).bind(newAccess, newExpiresAt, newRefresh, row.linkedin_id).run();
      return { access_token: newAccess, linkedin_id: row.linkedin_id };
    } catch (e) {
      return { error: 'Token refresh exception' };
    }
  }
  return { access_token: row.access_token, linkedin_id: row.linkedin_id };
}

function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  for (const pair of header.split(';')) {
    const [k, ...v] = pair.trim().split('=');
    if (k) cookies[k.trim()] = v.join('=').trim();
  }
  return cookies;
}

async function getSession(env, request) {
  const cookies = parseCookies(request.headers.get('Cookie'));
  let token = cookies.session_token;
  if (!token) {
    const auth = request.headers.get('Authorization') || '';
    if (auth.startsWith('Bearer ')) token = auth.slice(7);
  }
  if (!token) return null;
  const data = await env.SESSIONS.get(`session:${token}`);
  if (!data) return null;
  try { return JSON.parse(data); } catch { return null; }
}

function nowISO() {
  return new Date().toISOString().replace('T', ' ').split('.')[0];
}

export async function handleLinkedIn(request, env, path, method) {
  // ── LinkedIn Auth Redirect ──
  if (path === '/linkedin/auth') {
    const state = crypto.randomUUID();
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: env.LINKEDIN_CLIENT_ID,
      redirect_uri: env.LINKEDIN_REDIRECT_URI,
      state,
      scope: env.LINKEDIN_SCOPES,
    });
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?${params}`;
    const resp = Response.redirect(authUrl, 302);
    // Note: Response.redirect returns immutable headers, need to create new
    return new Response(null, {
      status: 302,
      headers: {
        'Location': authUrl,
        'Set-Cookie': `linkedin_oauth_state=${state}; Max-Age=600; Path=/; HttpOnly; SameSite=Lax; Secure`,
      },
    });
  }

  // ── LinkedIn Callback ──
  if (path === '/linkedin/callback') {
    const url = new URL(request.url);
    const error = url.searchParams.get('error');
    if (error) {
      const desc = url.searchParams.get('error_description') || 'Unknown error';
      return new Response(
        `<html><body><h2>LinkedIn Authorization Failed</h2><p>${error}: ${desc}</p><p><a href="/linkedin/auth">Try again</a></p></body></html>`,
        { status: 400, headers: { 'Content-Type': 'text/html' } }
      );
    }

    const code = url.searchParams.get('code');
    if (!code) {
      return new Response(
        '<html><body><h2>Missing authorization code</h2><p><a href="/linkedin/auth">Try again</a></p></body></html>',
        { status: 400, headers: { 'Content-Type': 'text/html' } }
      );
    }

    try {
      // Exchange code for token
      const tokenResp = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          code,
          redirect_uri: env.LINKEDIN_REDIRECT_URI,
          client_id: env.LINKEDIN_CLIENT_ID,
          client_secret: env.LINKEDIN_CLIENT_SECRET,
        }),
      });

      if (!tokenResp.ok) {
        return new Response(
          `<html><body><h2>Token Exchange Failed</h2><p>Status: ${tokenResp.status}</p><pre>${await tokenResp.text()}</pre><p><a href="/linkedin/auth">Try again</a></p></body></html>`,
          { status: 502, headers: { 'Content-Type': 'text/html' } }
        );
      }

      const tokenData = await tokenResp.json();
      const accessToken = tokenData.access_token;
      const expiresIn = tokenData.expires_in || 5184000;
      const refreshToken = tokenData.refresh_token || null;
      const expiresAt = new Date(Date.now() + expiresIn * 1000).toISOString();

      // Fetch profile
      let linkedinId = null;
      let linkedinName = null;
      const profileResp = await fetch('https://api.linkedin.com/v2/userinfo', {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });
      if (profileResp.ok) {
        const profile = await profileResp.json();
        linkedinId = profile.sub || null;
        linkedinName = profile.name || '';
      }

      // Store in D1 (replace existing)
      await env.DB.prepare('DELETE FROM linkedin_tokens').run();
      await env.DB.prepare(
        'INSERT INTO linkedin_tokens (access_token, expires_at, refresh_token, linkedin_id, linkedin_name) VALUES (?, ?, ?, ?, ?)'
      ).bind(accessToken, expiresAt, refreshToken, linkedinId, linkedinName).run();

      const displayName = linkedinName || linkedinId || 'Unknown';
      return new Response(`<!DOCTYPE html>
<html><head><style>
body { font-family: -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #0f172a; color: #e2e8f0; }
.card { background: #1e293b; border-radius: 12px; padding: 48px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3); max-width: 480px; }
h2 { color: #22c55e; margin-bottom: 8px; }
p { color: #94a3b8; line-height: 1.6; }
.name { color: #38bdf8; font-weight: 600; }
</style></head>
<body><div class="card">
<h2>LinkedIn Connected!</h2>
<p>Authenticated as <span class="name">${displayName}</span></p>
<p>Token expires: ${expiresAt.slice(0, 10)}</p>
<p>You can close this tab and return to PureApex.</p>
</div></body></html>`, { status: 200, headers: { 'Content-Type': 'text/html' } });

    } catch (exc) {
      return new Response(
        `<html><body><h2>Error during LinkedIn OAuth</h2><p>${exc.message}</p><p><a href="/linkedin/auth">Try again</a></p></body></html>`,
        { status: 500, headers: { 'Content-Type': 'text/html' } }
      );
    }
  }

  // ── LinkedIn Status ──
  if (path === '/api/linkedin/status' && method === 'GET') {
    const session = await getSession(env, request);
    if (!session) return json({ error: 'Not authenticated' }, 401);

    const { results } = await env.DB.prepare(
      'SELECT access_token, expires_at, linkedin_id, linkedin_name, created_at FROM linkedin_tokens ORDER BY created_at DESC LIMIT 1'
    ).all();

    if (results.length === 0) return json({ connected: false });

    const row = results[0];
    const isExpired = row.expires_at && row.expires_at < new Date().toISOString();

    return json({
      connected: true,
      expired: isExpired,
      linkedin_id: row.linkedin_id,
      linkedin_name: row.linkedin_name,
      expires_at: row.expires_at,
      connected_at: row.created_at,
    });
  }

  // ── LinkedIn Post ──
  if (path === '/api/linkedin/post' && method === 'POST') {
    const session = await getSession(env, request);
    if (!session) return json({ error: 'Not authenticated' }, 401);

    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

    const text = (body.text || '').trim();
    if (!text) return json({ error: 'Post text is required' }, 400);

    const { results } = await env.DB.prepare(
      'SELECT access_token, expires_at, linkedin_id FROM linkedin_tokens ORDER BY created_at DESC LIMIT 1'
    ).all();

    if (results.length === 0)
      return json({ error: 'LinkedIn not connected. Visit /linkedin/auth first.' }, 400);

    const row = results[0];
    if (row.expires_at && row.expires_at < new Date().toISOString())
      return json({ error: 'LinkedIn token expired. Re-authorize at /linkedin/auth' }, 401);

    if (!row.linkedin_id)
      return json({ error: 'LinkedIn user ID not available. Re-authorize at /linkedin/auth' }, 400);

    const postPayload = {
      author: `urn:li:person:${row.linkedin_id}`,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: { text },
          shareMediaCategory: 'NONE',
        },
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
      },
    };

    try {
      const resp = await fetch('https://api.linkedin.com/v2/ugcPosts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${row.access_token}`,
          'X-Restli-Protocol-Version': '2.0.0',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postPayload),
      });

      if (resp.status === 200 || resp.status === 201) {
        const result = await resp.json();
        const postId = result.id || '';
        let postUrl = null;
        if (postId) {
          postUrl = `https://www.linkedin.com/feed/update/${postId}`;
        }
        return json({ ok: true, post_id: postId, post_url: postUrl });
      } else {
        return json({
          error: 'LinkedIn API error',
          status: resp.status,
          detail: await resp.text(),
        }, 502);
      }
    } catch (exc) {
      return json({ error: `Failed to post: ${exc.message}` }, 500);
    }
  }

  // ── LinkedIn Post With Image (internal-auth, 3-step upload) ──
  if (path === '/api/linkedin/post-with-image' && method === 'POST') {
    // Internal auth shim (constant-time)
    const provided = request.headers.get('X-Internal-Auth') || '';
    const expected = env.INTERNAL_AUTH_TOKEN || '';
    if (!expected || !timingSafeEqual(provided, expected)) {
      return json({ success: false, error: 'unauthorized' }, 401);
    }

    // Parse body
    let body;
    try { body = await request.json(); }
    catch { return json({ success: false, error: 'Invalid JSON' }, 400); }

    const text = (body.text || '').trim();
    const imageUrl = (body.image_url || '').trim();
    if (!text) return json({ success: false, error: 'text is required' }, 400);
    if (!imageUrl) return json({ success: false, error: 'image_url is required' }, 400);

    // SSRF guard
    if (!isImageUrlSafe(imageUrl)) {
      return json({ success: false, error: 'image_url rejected by SSRF guard', stage: 'register' }, 400);
    }

    // Rate limit
    const rl = await checkAndIncrementRateLimit(env);
    if (!rl.ok) {
      return json({ success: false, error: 'rate limit exceeded (5/hour)' }, 429);
    }

    // Token (with refresh)
    const tok = await getValidTokenRow(env);
    if (tok.error) return json({ success: false, error: tok.error, stage: 'register' }, 401);
    const accessToken = tok.access_token;
    const authorUrn = `urn:li:person:${tok.linkedin_id}`;

    try {
      // ── Step 1: Register Upload ──
      const regResp = await fetch('https://api.linkedin.com/v2/assets?action=registerUpload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          registerUploadRequest: {
            recipes: ['urn:li:digitalmediaRecipe:feedshare-image'],
            owner: authorUrn,
            serviceRelationships: [{
              relationshipType: 'OWNER',
              identifier: 'urn:li:userGeneratedContent',
            }],
          },
        }),
      });

      if (!regResp.ok) {
        return json({
          success: false,
          error: `register failed: ${regResp.status}`,
          stage: 'register',
        }, 502);
      }
      const regData = await regResp.json();
      const uploadUrl =
        regData?.value?.uploadMechanism?.['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']?.uploadUrl;
      const assetUrn = regData?.value?.asset;
      if (!uploadUrl || !assetUrn) {
        return json({ success: false, error: 'register response missing uploadUrl/asset', stage: 'register' }, 502);
      }

      // ── Step 2: Fetch image (SSRF-guarded, no redirects) + PUT bytes to LinkedIn ──
      // redirect: 'manual' prevents redirect-chain SSRF (H-2). A 302 from an
      // allowlisted host to 169.254.169.254 would otherwise bypass isImageUrlSafe.
      const imgResp = await fetch(imageUrl, {
        method: 'GET',
        redirect: 'manual',
        headers: { 'Accept': 'image/*' },
      });

      // Reject any 3xx — allowlisted hosts should serve images directly
      if (imgResp.status >= 300 && imgResp.status < 400) {
        return json({ success: false, error: 'image_url redirect not allowed', stage: 'upload' }, 400);
      }
      if (!imgResp.ok) {
        return json({ success: false, error: `image fetch failed: ${imgResp.status}`, stage: 'upload' }, 502);
      }

      // M-2: Verify Content-Type is actually an image
      const contentType = (imgResp.headers.get('content-type') || '').toLowerCase();
      if (!contentType.startsWith('image/')) {
        return json({ success: false, error: `invalid content-type: ${contentType || 'missing'}`, stage: 'upload' }, 400);
      }

      // M-1: Pre-flight Content-Length check before buffering 10MB into memory
      const contentLengthHeader = imgResp.headers.get('content-length');
      if (contentLengthHeader) {
        const contentLength = parseInt(contentLengthHeader, 10);
        if (Number.isFinite(contentLength) && contentLength > 10 * 1024 * 1024) {
          return json({ success: false, error: 'image exceeds 10MB cap (content-length)', stage: 'upload' }, 413);
        }
      }

      const imgBytes = await imgResp.arrayBuffer();
      // Post-buffer cap (in case Content-Length was absent or lied)
      if (imgBytes.byteLength > 10 * 1024 * 1024) {
        return json({ success: false, error: 'image exceeds 10MB cap', stage: 'upload' }, 413);
      }

      const uploadResp = await fetch(uploadUrl, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
        body: imgBytes,
      });
      if (!uploadResp.ok && uploadResp.status !== 201) {
        return json({
          success: false,
          error: `upload failed: ${uploadResp.status}`,
          stage: 'upload',
        }, 502);
      }

      // ── Step 3: Publish ugcPost ──
      const publishPayload = {
        author: authorUrn,
        lifecycleState: 'PUBLISHED',
        specificContent: {
          'com.linkedin.ugc.ShareContent': {
            shareCommentary: { text },
            shareMediaCategory: 'IMAGE',
            media: [{
              status: 'READY',
              description: { text: '' },
              media: assetUrn,
              title: { text: '' },
            }],
          },
        },
        visibility: {
          'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
        },
      };

      const pubResp = await fetch('https://api.linkedin.com/v2/ugcPosts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'X-Restli-Protocol-Version': '2.0.0',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(publishPayload),
      });

      if (pubResp.status !== 200 && pubResp.status !== 201) {
        return json({
          success: false,
          error: `publish failed: ${pubResp.status}`,
          stage: 'publish',
        }, 502);
      }

      const pubData = await pubResp.json();
      const postUrn = pubData.id || '';
      if (!postUrn) {
        return json({ success: false, error: 'publish response missing id', stage: 'publish' }, 502);
      }

      return json({
        success: true,
        post_urn: postUrn,
        post_url: `https://www.linkedin.com/feed/update/${postUrn}/`,
        posted_at: new Date().toISOString(),
      });
    } catch (exc) {
      // Never include stack traces or token material in response
      return json({ success: false, error: 'internal error during post-with-image', stage: 'publish' }, 500);
    }
  }

  return new Response('Not found', { status: 404 });
}

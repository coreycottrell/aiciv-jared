/**
 * Prospect Pages module for PureApex Worker
 * Password-protected custom pages at /p/{slug}
 */

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function htmlResp(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: { 'Content-Type': 'text/html; charset=utf-8', ...headers },
  });
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

export async function handleProspectPages(request, env, path, method) {

  // ── /p/{slug} GET — View prospect page ──
  const viewMatch = path.match(/^\/p\/([a-z0-9][a-z0-9-]*[a-z0-9]|[a-z0-9])$/);
  if (viewMatch && method === 'GET') {
    const slug = viewMatch[1];

    const { results } = await env.DB.prepare(
      'SELECT * FROM prospect_pages WHERE slug = ? AND is_active = 1'
    ).bind(slug).all();

    if (results.length === 0) {
      return htmlResp(
        '<html><body style="font-family:-apple-system,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#0f172a;color:#94a3b8;"><div style="text-align:center;"><h1 style="color:#e2e8f0;">Page Not Found</h1><p>This page does not exist or is no longer available.</p></div></body></html>',
        404
      );
    }

    const page = results[0];

    // Check if authenticated via KV session
    const cookies = parseCookies(request.headers.get('Cookie'));
    const ppToken = cookies[`pp_${slug}`];
    if (ppToken) {
      const valid = await env.SESSIONS.get(`pp:${slug}:${ppToken}`);
      if (valid) {
        // Authenticated - increment view count and show content
        await env.DB.prepare(
          'UPDATE prospect_pages SET view_count = view_count + 1 WHERE slug = ?'
        ).bind(slug).run();
        return htmlResp(page.html_content);
      }
    }

    // Show password gate
    const url = new URL(request.url);
    const hasError = url.searchParams.get('error');
    const errorHtml = hasError
      ? '<p style="color:#ef4444;margin-bottom:16px;font-size:14px;">Incorrect password. Please try again.</p>'
      : '';

    return htmlResp(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${page.company_name} | PureBrain</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #0f172a; color: #e2e8f0; }
        .card { background: #1e293b; border-radius: 16px; padding: 48px 40px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.4); max-width: 420px; width: 90%; }
        .logo { font-size: 28px; font-weight: 700; color: #38bdf8; margin-bottom: 8px; letter-spacing: -0.5px; }
        .logo span { color: #22c55e; }
        .subtitle { color: #64748b; font-size: 13px; margin-bottom: 32px; text-transform: uppercase; letter-spacing: 1px; }
        .exclusive { color: #94a3b8; font-size: 15px; margin-bottom: 24px; line-height: 1.5; }
        .exclusive strong { color: #f1f5f9; }
        form { display: flex; flex-direction: column; gap: 12px; }
        input[type="password"] { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 14px 16px; color: #e2e8f0; font-size: 16px; outline: none; transition: border-color 0.2s; }
        input[type="password"]:focus { border-color: #38bdf8; }
        input[type="password"]::placeholder { color: #475569; }
        button { background: linear-gradient(135deg, #38bdf8, #22c55e); border: none; border-radius: 8px; padding: 14px; color: #0f172a; font-size: 16px; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">Pure<span>Brain</span></div>
        <div class="subtitle">Pure Technology</div>
        <p class="exclusive">This page was prepared exclusively for<br><strong>${page.company_name}</strong></p>
        ${errorHtml}
        <form method="POST" action="/p/${slug}/auth">
            <input type="password" name="password" placeholder="Enter access password" required autofocus>
            <button type="submit">Access Page</button>
        </form>
    </div>
</body>
</html>`);
  }

  // ── /p/{slug}/auth POST — Authenticate ──
  const authMatch = path.match(/^\/p\/([a-z0-9][a-z0-9-]*[a-z0-9]|[a-z0-9])\/auth$/);
  if (authMatch && method === 'POST') {
    const slug = authMatch[1];

    const formData = await request.formData();
    const password = formData.get('password') || '';

    const { results } = await env.DB.prepare(
      'SELECT password FROM prospect_pages WHERE slug = ? AND is_active = 1'
    ).bind(slug).all();

    if (results.length === 0) {
      return Response.redirect(new URL(`/p/${slug}`, request.url).toString(), 303);
    }

    if (password !== results[0].password) {
      return Response.redirect(new URL(`/p/${slug}?error=1`, request.url).toString(), 303);
    }

    // Create prospect page session in KV
    const token = crypto.randomUUID();
    await env.SESSIONS.put(`pp:${slug}:${token}`, '1', { expirationTtl: 86400 * 7 });

    return new Response(null, {
      status: 303,
      headers: {
        'Location': `/p/${slug}`,
        'Set-Cookie': `pp_${slug}=${token}; Max-Age=${86400 * 7}; Path=/; HttpOnly; SameSite=Lax; Secure`,
      },
    });
  }

  // ── /api/prospect-pages GET — List all ──
  if (path === '/api/prospect-pages' && method === 'GET') {
    const session = await getSession(env, request);
    if (!session) return json({ error: 'Not authenticated' }, 401);

    const { results } = await env.DB.prepare(
      'SELECT id, slug, company_name, is_active, view_count, created_by, created_at, updated_at FROM prospect_pages ORDER BY created_at DESC'
    ).all();

    return json(results);
  }

  // ── /api/prospect-pages POST — Create ──
  if (path === '/api/prospect-pages' && method === 'POST') {
    const session = await getSession(env, request);
    if (!session) return json({ error: 'Not authenticated' }, 401);

    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

    const slug = (body.slug || '').trim().toLowerCase();
    const companyName = (body.company_name || '').trim();
    const password = (body.password || '').trim();
    const htmlContent = (body.html_content || '').trim();

    if (!slug) return json({ error: 'Slug is required' }, 400);
    if (!companyName) return json({ error: 'Company name is required' }, 400);
    if (!password) return json({ error: 'Password is required' }, 400);
    if (!htmlContent) return json({ error: 'HTML content is required' }, 400);

    if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(slug) && slug.length > 1) {
      return json({ error: 'Slug must contain only lowercase letters, numbers, and hyphens' }, 400);
    }

    // Check duplicate
    const { results: existing } = await env.DB.prepare(
      'SELECT id FROM prospect_pages WHERE slug = ?'
    ).bind(slug).all();
    if (existing.length > 0) return json({ error: 'A page with this slug already exists' }, 409);

    const now = nowISO();
    const { meta } = await env.DB.prepare(
      'INSERT INTO prospect_pages (slug, company_name, password, html_content, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)'
    ).bind(slug, companyName, password, htmlContent, session.display_name, now, now).run();

    const { results } = await env.DB.prepare(
      'SELECT id, slug, company_name, is_active, view_count, created_by, created_at, updated_at FROM prospect_pages WHERE id = ?'
    ).bind(meta.last_row_id).all();

    return json(results[0], 201);
  }

  // ── /api/prospect-pages/{slug} PUT — Update ──
  const updateMatch = path.match(/^\/api\/prospect-pages\/([a-z0-9][a-z0-9-]*[a-z0-9]|[a-z0-9])$/);
  if (updateMatch && method === 'PUT') {
    const slug = updateMatch[1];
    const session = await getSession(env, request);
    if (!session) return json({ error: 'Not authenticated' }, 401);

    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

    const { results: existing } = await env.DB.prepare(
      'SELECT * FROM prospect_pages WHERE slug = ?'
    ).bind(slug).all();

    if (existing.length === 0) return json({ error: 'Page not found' }, 404);
    const page = existing[0];

    const now = nowISO();
    await env.DB.prepare(
      'UPDATE prospect_pages SET company_name = ?, password = ?, html_content = ?, is_active = ?, updated_at = ? WHERE slug = ?'
    ).bind(
      body.company_name !== undefined ? body.company_name : page.company_name,
      body.password !== undefined ? body.password : page.password,
      body.html_content !== undefined ? body.html_content : page.html_content,
      body.is_active !== undefined ? (body.is_active ? 1 : 0) : page.is_active,
      now,
      slug
    ).run();

    const { results } = await env.DB.prepare(
      'SELECT id, slug, company_name, is_active, view_count, created_by, created_at, updated_at FROM prospect_pages WHERE slug = ?'
    ).bind(slug).all();

    return json(results[0]);
  }

  return new Response('Not found', { status: 404 });
}

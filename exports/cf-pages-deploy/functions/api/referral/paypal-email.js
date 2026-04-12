/**
 * POST /api/referral/paypal-email — Save PayPal email for a referrer.
 *
 * Body: { email, paypal_email, password?, session_token? }
 * Auth: portal bearer, affiliate session token, or password
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  checkPortalAuth,
  verifyAffiliateSession,
  verifyPassword,
  generateUniqueCode,
  hashPassword,
} from './_shared.js';

export async function onRequestOptions(context) {
  return corsResponse(context.request);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const db = env.REFERRAL_DB;

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'invalid json' }, 400, request);
  }

  const email = String(body.email || '').trim().toLowerCase();
  const paypalEmail = String(body.paypal_email || '').trim().toLowerCase();
  const password = String(body.password || '').trim();

  if (!email || !email.includes('@')) {
    return jsonResponse({ error: 'invalid email' }, 400, request);
  }
  if (!paypalEmail || !paypalEmail.includes('@')) {
    return jsonResponse({ error: 'invalid paypal_email' }, 400, request);
  }

  const portalAuthed = checkPortalAuth(request, env);

  if (!portalAuthed) {
    const sessionToken = String(body.session_token || '').trim() || request.headers.get('X-Affiliate-Session') || '';
    const sessionCode = await verifyAffiliateSession(db, sessionToken);

    if (!sessionCode) {
      // Fallback to password
      const row = await db
        .prepare('SELECT password_hash FROM referrers WHERE user_email = ? COLLATE NOCASE')
        .bind(email)
        .first();

      if (!row) {
        return jsonResponse({ error: 'referrer not found' }, 404, request);
      }
      if (row.password_hash && !(await verifyPassword(password, row.password_hash))) {
        return jsonResponse({ error: 'incorrect password or session required' }, 401, request);
      }
    }
  }

  // Update PayPal email
  const result = await db
    .prepare('UPDATE referrers SET paypal_email = ? WHERE user_email = ? COLLATE NOCASE')
    .bind(paypalEmail, email)
    .run();

  if (result.meta.changes === 0) {
    // If portal-authed and no row exists, auto-create referrer
    if (portalAuthed) {
      const code = await generateUniqueCode(db);
      const now = new Date().toISOString();
      const name = email.split('@')[0];
      const arr = new Uint8Array(16);
      crypto.getRandomValues(arr);
      const randomPw = Array.from(arr).map((b) => b.toString(36)).join('').substring(0, 20);
      const pwHash = await hashPassword(randomPw);
      await db
        .prepare(
          'INSERT INTO referrers (user_name, user_email, referral_code, password_hash, paypal_email, created_at) VALUES (?, ?, ?, ?, ?, ?)'
        )
        .bind(name, email, code, pwHash, paypalEmail, now)
        .run();
    } else {
      return jsonResponse({ error: 'referrer not found' }, 404, request);
    }
  }

  return jsonResponse({ ok: true }, 200, request);
}

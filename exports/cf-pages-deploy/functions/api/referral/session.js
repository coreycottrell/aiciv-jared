/**
 * POST /api/referral/session — Login and receive a session token for dashboard access.
 *
 * Body: { email?, referral_code?, password }
 * Returns: { ok, session_token, referral_code, expires_in }
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  verifyPassword,
  hashPassword,
  createAffiliateSession,
  isRateLimited,
  getClientIP,
  hashIP,
  SESSION_TTL_SECS,
  LOGIN_MAX_ATTEMPTS,
  LOGIN_WINDOW_SECS,
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

  const code = String(body.referral_code || '').trim().toUpperCase();
  const email = String(body.email || '').trim().toLowerCase();
  const password = String(body.password || '').trim();

  if (!password) {
    return jsonResponse({ error: 'password required' }, 400, request);
  }
  if (!code && !email) {
    return jsonResponse({ error: 'referral_code or email required' }, 400, request);
  }

  // Rate limit by IP
  const clientIP = getClientIP(request);
  const ipHash = await hashIP(clientIP);
  const limited = await isRateLimited(db, `login:${ipHash}`, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECS);
  if (limited) {
    return jsonResponse({ error: 'too many login attempts. Please wait 15 minutes.' }, 429, request);
  }

  // Look up referrer
  let row;
  if (code) {
    row = await db
      .prepare('SELECT referral_code, password_hash FROM referrers WHERE referral_code = ? COLLATE NOCASE')
      .bind(code)
      .first();
  } else {
    row = await db
      .prepare('SELECT referral_code, password_hash FROM referrers WHERE user_email = ? COLLATE NOCASE')
      .bind(email)
      .first();
  }

  if (!row) {
    return jsonResponse({ error: 'account not found' }, 404, request);
  }

  const storedHash = row.password_hash;

  if (!storedHash) {
    // First login — set the password
    const newHash = await hashPassword(password);
    await db
      .prepare('UPDATE referrers SET password_hash = ? WHERE referral_code = ? COLLATE NOCASE')
      .bind(newHash, row.referral_code)
      .run();
    console.log(`[SECURITY] First-login password claim for affiliate code ${row.referral_code}`);
  } else {
    const valid = await verifyPassword(password, storedHash);
    if (!valid) {
      // If bcrypt hash, suggest password reset
      if (storedHash.startsWith('$2b$') || storedHash.startsWith('$2a$')) {
        return jsonResponse(
          { error: 'Your account requires a password reset. Please use the "Forgot Password" link.' },
          401,
          request
        );
      }
      return jsonResponse({ error: 'incorrect password' }, 401, request);
    }

    // Auto-migrate legacy hashes to PBKDF2
    if (!storedHash.startsWith('pbkdf2:')) {
      const migratedHash = await hashPassword(password);
      await db
        .prepare('UPDATE referrers SET password_hash = ? WHERE referral_code = ? COLLATE NOCASE')
        .bind(migratedHash, row.referral_code)
        .run();
    }
  }

  // Create session
  const sessionToken = await createAffiliateSession(db, row.referral_code);

  return jsonResponse(
    {
      ok: true,
      session_token: sessionToken,
      referral_code: row.referral_code,
      expires_in: SESSION_TTL_SECS,
    },
    200,
    request
  );
}

/**
 * POST /api/referral/forgot-password — Send a password reset email.
 *
 * Body: { email }
 * D1 binding: REFERRAL_DB
 * Env: RESEND_API_KEY
 */
import {
  corsResponse,
  jsonResponse,
  sendResetEmail,
  PASSWORD_RESET_EXPIRY,
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
  if (!email || !email.includes('@')) {
    return jsonResponse({ error: 'valid email required' }, 400, request);
  }

  // Always return success to prevent email enumeration
  const successMsg = { ok: true, message: 'If that email is registered, a reset link has been sent.' };

  // Check if referrer exists
  const row = await db
    .prepare('SELECT referral_code FROM referrers WHERE user_email = ? COLLATE NOCASE')
    .bind(email)
    .first();

  if (!row) {
    return jsonResponse(successMsg, 200, request);
  }

  // Generate reset token
  const arr = new Uint8Array(32);
  crypto.getRandomValues(arr);
  const token = Array.from(arr)
    .map((b) => b.toString(36).padStart(2, '0'))
    .join('')
    .substring(0, 43);

  const now = Math.floor(Date.now() / 1000);
  const expiresAt = now + PASSWORD_RESET_EXPIRY;

  // Store in D1
  await db
    .prepare('INSERT INTO password_reset_tokens (token, email, expires_at) VALUES (?, ?, ?)')
    .bind(token, email, expiresAt)
    .run();

  // Clean up expired tokens
  await db
    .prepare('DELETE FROM password_reset_tokens WHERE expires_at < ?')
    .bind(now)
    .run();

  const resetUrl = `https://purebrain.ai/refer/?reset=${token}`;
  const sent = await sendResetEmail(env, email, resetUrl);
  if (!sent) {
    console.error(`[reset] Failed to send reset email to ${email}`);
  }

  return jsonResponse(successMsg, 200, request);
}

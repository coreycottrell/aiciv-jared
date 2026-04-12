/**
 * POST /api/referral/reset-password — Set new password using reset token.
 *
 * Body: { token, password }
 * D1 binding: REFERRAL_DB
 */
import { corsResponse, jsonResponse, hashPassword } from './_shared.js';

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

  const token = String(body.token || '').trim();
  const newPassword = String(body.password || '').trim();

  if (!token) {
    return jsonResponse({ error: 'reset token required' }, 400, request);
  }
  if (!newPassword || newPassword.length < 6) {
    return jsonResponse({ error: 'password must be at least 6 characters' }, 400, request);
  }

  // Look up token
  const tokenData = await db
    .prepare('SELECT email, expires_at FROM password_reset_tokens WHERE token = ?')
    .bind(token)
    .first();

  if (!tokenData) {
    return jsonResponse({ error: 'invalid or expired reset link. Please request a new one.' }, 400, request);
  }

  const now = Math.floor(Date.now() / 1000);
  if (now > tokenData.expires_at) {
    await db.prepare('DELETE FROM password_reset_tokens WHERE token = ?').bind(token).run();
    return jsonResponse({ error: 'reset link has expired. Please request a new one.' }, 400, request);
  }

  const email = tokenData.email;
  const pwHash = await hashPassword(newPassword);

  await db
    .prepare('UPDATE referrers SET password_hash = ? WHERE user_email = ? COLLATE NOCASE')
    .bind(pwHash, email)
    .run();

  // Consume the token
  await db.prepare('DELETE FROM password_reset_tokens WHERE token = ?').bind(token).run();

  return jsonResponse({ ok: true, message: 'Password updated successfully. You can now log in.' }, 200, request);
}

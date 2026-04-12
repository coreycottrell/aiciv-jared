/**
 * Shared utilities for the Referral System CF Pages Functions.
 *
 * Environment bindings required:
 *   REFERRAL_DB  - D1 database binding
 *   RESEND_API_KEY - Resend API key for sending emails
 *   PORTAL_BEARER_TOKEN - Portal admin bearer token
 *
 * File naming: _shared.js (underscore prefix) is NOT routed as a Pages Function.
 */

// ── CORS ────────────────────────────────────────────────────────────────────

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://purebrain-staging.pages.dev',
];

export function getCorsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Affiliate-Session, X-Admin-Token',
    'Access-Control-Max-Age': '86400',
  };
}

export function corsResponse(request) {
  return new Response(null, { status: 204, headers: getCorsHeaders(request) });
}

export function jsonResponse(data, status, request) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...getCorsHeaders(request),
    },
  });
}

// ── Constants ───────────────────────────────────────────────────────────────

export const REFERRAL_CODE_PREFIX = 'PB-';
export const REFERRAL_CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
export const REFERRAL_CODE_LENGTH = 4;
export const REFERRAL_COMMISSION_RATE = 0.05;
export const PAYOUT_MIN_AMOUNT = 25.0;
export const PAYOUT_AUTO_APPROVE_LIMIT = 1000.0;
export const PAYOUT_COOLDOWN_DAYS = 30;
export const SESSION_TTL_SECS = 86400 * 7; // 7 days
export const LOGIN_MAX_ATTEMPTS = 10;
export const LOGIN_WINDOW_SECS = 900; // 15 minutes
export const TRACK_MAX_PER_WINDOW = 30;
export const TRACK_WINDOW_SECS = 300; // 5 minutes
export const PASSWORD_RESET_EXPIRY = 3600; // 1 hour

// ── Auth Helpers ────────────────────────────────────────────────────────────

export function checkPortalAuth(request, env) {
  const token = env.PORTAL_BEARER_TOKEN;
  if (!token) return false;
  const auth = request.headers.get('Authorization') || '';
  if (auth.startsWith('Bearer ')) {
    return auth.slice(7).trim() === token;
  }
  return false;
}

export async function verifyAffiliateSession(db, token) {
  if (!token) return null;
  const row = await db
    .prepare('SELECT referral_code, expires_at FROM affiliate_sessions WHERE token = ?')
    .bind(token)
    .first();
  if (!row) return null;
  const now = Math.floor(Date.now() / 1000);
  if (now > row.expires_at) {
    // Clean up expired session
    await db.prepare('DELETE FROM affiliate_sessions WHERE token = ?').bind(token).run();
    return null;
  }
  return row.referral_code;
}

export function getSessionToken(request, body) {
  // Check multiple sources for session token
  return (
    (body && body.session_token) ||
    request.headers.get('X-Affiliate-Session') ||
    new URL(request.url).searchParams.get('session') ||
    ''
  ).trim();
}

// ── Password Hashing (Web Crypto API — PBKDF2) ─────────────────────────────
// Workers runtime does not have bcrypt. We use PBKDF2-SHA256 with 100k iterations.
// Format: "pbkdf2:iterations:salt_hex:hash_hex"
// Also supports verifying legacy bcrypt ($2b$) and SHA-256 (salt:hash) formats.

const PBKDF2_ITERATIONS = 100000;

export async function hashPassword(password) {
  const salt = new Uint8Array(16);
  crypto.getRandomValues(salt);
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(password),
    'PBKDF2',
    false,
    ['deriveBits']
  );
  const derivedBits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: PBKDF2_ITERATIONS, hash: 'SHA-256' },
    keyMaterial,
    256
  );
  const saltHex = bufToHex(salt);
  const hashHex = bufToHex(new Uint8Array(derivedBits));
  return `pbkdf2:${PBKDF2_ITERATIONS}:${saltHex}:${hashHex}`;
}

export async function verifyPassword(password, storedHash) {
  if (!storedHash) return false;

  // New PBKDF2 format
  if (storedHash.startsWith('pbkdf2:')) {
    const parts = storedHash.split(':');
    if (parts.length !== 4) return false;
    const iterations = parseInt(parts[1], 10);
    const salt = hexToBuf(parts[2]);
    const expectedHash = parts[3];
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(password),
      'PBKDF2',
      false,
      ['deriveBits']
    );
    const derivedBits = await crypto.subtle.deriveBits(
      { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
      keyMaterial,
      256
    );
    return bufToHex(new Uint8Array(derivedBits)) === expectedHash;
  }

  // Legacy bcrypt ($2b$ or $2a$) — cannot verify in Workers, deny gracefully.
  // User must use forgot-password flow to reset.
  if (storedHash.startsWith('$2b$') || storedHash.startsWith('$2a$')) {
    return false; // Force password reset for bcrypt users
  }

  // Legacy SHA-256 format: salt:hexdigest
  if (storedHash.includes(':') && !storedHash.startsWith('pbkdf2:')) {
    const idx = storedHash.indexOf(':');
    const saltVal = storedHash.substring(0, idx);
    const expectedHex = storedHash.substring(idx + 1);
    const data = new TextEncoder().encode(`${saltVal}:${password}`);
    const digest = await crypto.subtle.digest('SHA-256', data);
    return bufToHex(new Uint8Array(digest)) === expectedHex;
  }

  return false;
}

function bufToHex(buf) {
  return Array.from(buf)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function hexToBuf(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}

// ── Referral Code Generation ────────────────────────────────────────────────

export function generateReferralCode() {
  const chars = REFERRAL_CODE_CHARS;
  let suffix = '';
  const arr = new Uint8Array(REFERRAL_CODE_LENGTH);
  crypto.getRandomValues(arr);
  for (let i = 0; i < REFERRAL_CODE_LENGTH; i++) {
    suffix += chars[arr[i] % chars.length];
  }
  return `${REFERRAL_CODE_PREFIX}${suffix}`;
}

export async function generateUniqueCode(db) {
  for (let i = 0; i < 50; i++) {
    const code = generateReferralCode();
    const existing = await db
      .prepare('SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE')
      .bind(code)
      .first();
    if (!existing) return code;
  }
  throw new Error('Could not generate unique referral code after 50 attempts');
}

export function referralLink(code, baseUrl = 'https://purebrain.ai') {
  return `${baseUrl}/?ref=${code}`;
}

// ── Rate Limiting (D1-backed) ───────────────────────────────────────────────
// Uses a rate_limits table in D1. Each entry has: key, count, window_start.

export async function isRateLimited(db, key, maxPerWindow, windowSecs) {
  const now = Math.floor(Date.now() / 1000);
  const row = await db
    .prepare('SELECT count, window_start FROM rate_limits WHERE key = ?')
    .bind(key)
    .first();

  if (!row) {
    await db
      .prepare('INSERT OR REPLACE INTO rate_limits (key, count, window_start) VALUES (?, 1, ?)')
      .bind(key, now)
      .run();
    return false;
  }

  if (now - row.window_start > windowSecs) {
    // Window expired, reset
    await db
      .prepare('UPDATE rate_limits SET count = 1, window_start = ? WHERE key = ?')
      .bind(now, key)
      .run();
    return false;
  }

  if (row.count >= maxPerWindow) {
    return true;
  }

  await db
    .prepare('UPDATE rate_limits SET count = count + 1 WHERE key = ?')
    .bind(key)
    .run();
  return false;
}

// ── IP Hashing ──────────────────────────────────────────────────────────────

export async function hashIP(ip) {
  const data = new TextEncoder().encode(ip);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return bufToHex(new Uint8Array(digest)).substring(0, 16);
}

export function getClientIP(request) {
  return request.headers.get('CF-Connecting-IP') || request.headers.get('X-Forwarded-For') || '0.0.0.0';
}

// ── Email Sending (Resend API) ──────────────────────────────────────────────

export async function sendResetEmail(env, toEmail, resetUrl) {
  const apiKey = env.RESEND_API_KEY;
  if (!apiKey) {
    console.error('[referral] RESEND_API_KEY not configured');
    return false;
  }

  const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="background:#080a12;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:32px;">
<div style="max-width:500px;margin:0 auto;background:#0d1120;border:1px solid #1e2a40;border-radius:12px;padding:40px;">
  <div style="text-align:center;margin-bottom:24px;">
    <span style="font-size:22px;font-weight:700;">
      <span style="color:#2a93c1;">PUREBR</span><span style="color:#f1420b;">AI</span><span style="color:#2a93c1;">N</span>
    </span>
  </div>
  <h2 style="color:#fff;font-size:20px;margin:0 0 16px;">Reset Your Password</h2>
  <p style="color:#9ca3af;font-size:14px;line-height:1.6;margin:0 0 24px;">
    Click the button below to reset your affiliate dashboard password. This link expires in 1 hour.
  </p>
  <div style="text-align:center;margin:32px 0;">
    <a href="${resetUrl}" style="display:inline-block;background:linear-gradient(135deg,#2a93c1,#1d6e99);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;box-shadow:0 4px 16px rgba(42,147,193,0.4);">
      Reset Password
    </a>
  </div>
  <p style="color:#6b7280;font-size:12px;text-align:center;">If you didn't request this, you can safely ignore this email.</p>
</div>
</body></html>`;

  const text = `Reset your PureBrain affiliate password:\n\n${resetUrl}\n\nThis link expires in 1 hour. If you didn't request this, ignore this email.`;

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        from: 'PureBrain <noreply@purebrain.ai>',
        to: [toEmail],
        subject: 'Reset Your PureBrain Affiliate Password',
        html,
        text,
      }),
    });
    if (!res.ok) {
      const err = await res.text();
      console.error('[referral] Resend error:', res.status, err);
      return false;
    }
    return true;
  } catch (err) {
    console.error('[referral] Email send error:', err);
    return false;
  }
}

// ── Session Creation ────────────────────────────────────────────────────────

export async function createAffiliateSession(db, referralCode) {
  // Generate a secure random token
  const arr = new Uint8Array(32);
  crypto.getRandomValues(arr);
  const token = bufToHex(arr);
  const now = Math.floor(Date.now() / 1000);
  const expiresAt = now + SESSION_TTL_SECS;

  await db
    .prepare(
      'INSERT INTO affiliate_sessions (token, referral_code, expires_at) VALUES (?, ?, ?)'
    )
    .bind(token, referralCode.toUpperCase(), expiresAt)
    .run();

  return token;
}

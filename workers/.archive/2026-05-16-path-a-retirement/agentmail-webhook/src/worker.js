import { ensureDnsRecord, extractSlugFromLink } from '../../_shared/ensure-dns-record.js';

/**
 * agentmail-webhook — Cloudflare Worker
 *
 * REPLACES: tools/agentmail_monitor.py (polling daemon)
 *
 * This Worker receives webhook events from AgentMail when emails arrive at
 * aether-aiciv@agentmail.to. When a MAGIC LINK email from Witness is detected,
 * it:
 *   1. Parses structured fields from the email body (AI name, human name,
 *      email, UUID, container, magic link URL)
 *   2. Rewrites .ai-civ.com domains to .app.purebrain.ai
 *   3. Stores the magic link in D1 (magic_links table)
 *   4. Looks up PayPal email from D1 clients table for dual-send
 *   5. Triggers welcome email(s) via the welcome-email-api Worker
 *   6. Updates the D1 clients table with ai_name + magic_link
 *   7. Sends Telegram notification to Jared
 *
 * The thank-you page polls GET /api/magic-link/:uuid to check if a magic link
 * is ready.
 *
 * Data flow:
 *   AgentMail webhook -> this Worker -> D1 + welcome-email-api + Telegram
 *   Thank-you page -> GET /api/magic-link/:uuid -> D1 lookup -> response
 *
 * D1 database: purebrain-social (shared with paypal-webhook, admin-api, etc.)
 */

// ---------------------------------------------------------------------------
// Regex patterns for parsing Witness magic link emails
// Ported from agentmail_monitor.py lines 347-365
// ---------------------------------------------------------------------------

const FIELD_PATTERNS = {
  ai_name:     /(?:AI Name|CIV Name|AiCIV Name)\s*[:=]\s*(.+)/i,
  human_name:  /Human Name\s*[:=]\s*(.+)/i,
  human_email: /Email\s*[:=]\s*([^\s@]+@[^\s@]+\.[^\s@]+)/i,
  uuid:        /UUID\s*[:=]\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i,
  container:   /Container\s*[:=]\s*(\S+)/i,
  magic_link:  /Magic Link\s*[:=]\s*(https?:\/\/\S+)/i,
};

// Fallback: bare URL on .ai-civ.com domain
const FALLBACK_URL_PATTERN = /(https:\/\/[^\s]+\.ai-civ\.com[^\s]*)/;

// Sandbox email detection (from agentmail_monitor.py lines 541-550)
const SANDBOX_PATTERNS = [
  /^sb-/i,
  /@personal\.example\.com$/i,
  /@business\.example\.com$/i,
  /example\.com/i,
];
const SANDBOX_REDIRECT = 'jared@puretechnology.nyc';

// Birth pipeline DNS automation constants (CTO build brief 2026-05-08)
const BIRTH_DNS_TARGET_IP = '46.62.187.74';
const BIRTH_DNS_FQDN_SUFFIX = '.app.purebrain.ai';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function isSandboxEmail(email) {
  if (!email) return false;
  const lower = email.toLowerCase().trim();
  if (lower === '(sandbox-sub)') return true;
  return SANDBOX_PATTERNS.some(p => p.test(lower));
}

function rewriteDomain(link, from, to) {
  if (!link) return link;
  // Rewrite subdomain.ai-civ.com -> subdomain.app.purebrain.ai
  // Pattern: (https?://)(subdomain).ai-civ.com -> \1\2.app.purebrain.ai
  return link.replace(
    new RegExp(`(https?://)([^./]+)${escapeRegex(from)}`, 'g'),
    `$1$2${to}`
  );
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function isMagicLinkEmail(subject, sender) {
  const subjectUpper = (subject || '').toUpperCase();
  const senderLower = (sender || '').toLowerCase();
  return subjectUpper.includes('MAGIC LINK') && (
    senderLower.includes('witness') || senderLower.includes('agentmail.to')
  );
}

function parseMagicLinkBody(body) {
  if (!body) return {};
  const result = {};

  for (const [key, pattern] of Object.entries(FIELD_PATTERNS)) {
    const m = body.match(pattern);
    if (m) {
      result[key] = m[1].trim();
    }
  }

  // Fallback: scan for any bare .ai-civ.com URL
  if (!result.magic_link) {
    const urlMatch = body.match(FALLBACK_URL_PATTERN);
    if (urlMatch) {
      result.magic_link = urlMatch[1].trim();
    }
  }

  return result;
}

function jsonResponse(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Webhook-Secret',
      ...extraHeaders,
    },
  });
}

// ---------------------------------------------------------------------------
// Telegram notification
// ---------------------------------------------------------------------------

async function sendTelegram(env, message) {
  if (!env.TELEGRAM_BOT_TOKEN) {
    console.log('[agentmail-webhook] No TELEGRAM_BOT_TOKEN configured, skipping notification');
    return;
  }

  try {
    const resp = await fetch(
      `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: env.TELEGRAM_CHAT_ID,
          text: message,
          parse_mode: 'HTML',
        }),
      }
    );

    if (!resp.ok) {
      const errBody = await resp.text();
      console.log(`[agentmail-webhook] Telegram send failed: ${resp.status} ${errBody}`);
    }
  } catch (e) {
    console.log(`[agentmail-webhook] Telegram send error: ${e.message}`);
  }
}

// ---------------------------------------------------------------------------
// Birth pipeline DNS automation (feature-flagged)
// ---------------------------------------------------------------------------

async function ensureBirthDns(env, magicLink) {
  const flagEnabled = env.ENABLE_BIRTH_DNS_AUTO === 'true' || env.ENABLE_BIRTH_DNS_AUTO === true;
  if (!flagEnabled) {
    console.log('[agentmail-webhook] DNS automation gated by ENABLE_BIRTH_DNS_AUTO=false (no-op)');
    return { ok: true, action: 'flag_disabled' };
  }

  const slug = extractSlugFromLink(magicLink);
  if (!slug) {
    console.log(`[agentmail-webhook] No slug extracted from magic_link, skipping DNS ensure: ${magicLink}`);
    return { ok: true, action: 'no_slug' };
  }

  const fqdn = `${slug}${BIRTH_DNS_FQDN_SUFFIX}`;
  const result = await ensureDnsRecord(env, fqdn, BIRTH_DNS_TARGET_IP);

  console.log(`[agentmail-webhook] BIRTH-DNS slug=${slug} fqdn=${fqdn} action=${result.action} ok=${result.ok}`);

  if (!result.ok || result.action === 'drift_detected') {
    await sendTelegram(env,
      `🔴 BIRTH-DNS-FAIL (agentmail-webhook)\n` +
      `slug=${slug}\n` +
      `fqdn=${fqdn}\n` +
      `action=${result.action}\n` +
      `error=${result.error || result.alert || 'unknown'}`
    );
  }

  return result;
}

// ---------------------------------------------------------------------------
// Welcome email trigger (calls welcome-email-api Worker)
// ---------------------------------------------------------------------------

async function sendWelcomeEmail(env, { human_email, human_first, ai_name, magic_link }) {
  // ROOT-CAUSE FIX 2026-05-08: Worker→Worker fetch via *.workers.dev is BLOCKED
  // by Cloudflare for same-account scripts (returns 404 with empty body). The
  // canonical mechanism is a Service Binding declared in wrangler.toml:
  //   [[services]]
  //   binding = "WELCOME_EMAIL_API"
  //   service = "welcome-email-api"
  // We then call env.WELCOME_EMAIL_API.fetch(...) — this bypasses the public
  // internet, is free, and routes directly to the bound Worker's handler.
  // HTTP fallback retained for local dev / cross-account scenarios only.
  console.log(`[agentmail-webhook] Sending welcome email to ${human_email} (AI=${ai_name})`);

  const body = JSON.stringify({ human_email, human_first, ai_name, magic_link });

  try {
    let resp;
    if (env.WELCOME_EMAIL_API && typeof env.WELCOME_EMAIL_API.fetch === 'function') {
      // Preferred path: Service Binding (same-account, free, internal)
      resp = await env.WELCOME_EMAIL_API.fetch('https://welcome-email-api/send-welcome', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      });
      console.log(`[agentmail-webhook] Welcome email called via Service Binding, status=${resp.status}`);
    } else {
      // Fallback: HTTP fetch (only works cross-account; same-account returns 404)
      const url = `${env.WELCOME_EMAIL_URL}/send-welcome`;
      console.log(`[agentmail-webhook] WARNING: Service Binding missing, falling back to HTTP fetch ${url}`);
      resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      });
    }

    const result = await resp.json().catch(() => ({}));

    if (!resp.ok) {
      console.log(`[agentmail-webhook] Welcome email API returned ${resp.status}: ${JSON.stringify(result)}`);
      return { ok: false, status: resp.status, error: result.error };
    }

    console.log(`[agentmail-webhook] Welcome email sent successfully to ${human_email} (log_id=${result.log_id})`);
    return { ok: true, log_id: result.log_id };
  } catch (e) {
    console.log(`[agentmail-webhook] Welcome email call error: ${e.message}`);
    return { ok: false, error: e.message };
  }
}

// ---------------------------------------------------------------------------
// D1 operations
// ---------------------------------------------------------------------------

async function storeMagicLink(env, data) {
  const {
    session_uuid, ai_name, human_name, human_email,
    paypal_email, container, magic_link, original_link,
  } = data;

  // Duplicate detection: check if this exact magic link URL already exists
  const existing = await env.DB.prepare(
    'SELECT id FROM magic_links WHERE magic_link = ?'
  ).bind(magic_link).first();

  if (existing) {
    console.log(`[agentmail-webhook] Duplicate magic link detected, skipping insert: ${magic_link}`);
    return { duplicate: true, id: existing.id };
  }

  const result = await env.DB.prepare(`
    INSERT INTO magic_links (
      session_uuid, ai_name, human_name, human_email,
      paypal_email, container, magic_link, original_link,
      status, received_at
    ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, 'ready', datetime('now'))
  `).bind(
    session_uuid || null,   // ?1
    ai_name || null,        // ?2
    human_name || null,     // ?3
    human_email || null,    // ?4
    paypal_email || null,   // ?5
    container || null,      // ?6
    magic_link,             // ?7
    original_link || null,  // ?8
  ).run();

  console.log(`[agentmail-webhook] Magic link stored in D1: uuid=${session_uuid}, email=${human_email}`);
  return { duplicate: false, id: result.meta?.last_row_id };
}

async function markWelcomeSent(env, magicLink) {
  await env.DB.prepare(
    "UPDATE magic_links SET welcome_sent = 1, welcome_sent_at = datetime('now') WHERE magic_link = ?"
  ).bind(magicLink).run();
}

// ---------------------------------------------------------------------------
// Client mutations — Service Binding to clients-api (P1.5.2)
// ---------------------------------------------------------------------------
//
// Constitutional: ALL reads/writes against the `clients` table go through
// clients-api via Service Binding. No direct env.DB.prepare(...clients...)
// here. (cf-service-binding-pattern skill, 2026-05-07; CTO P1.5 brief
// 2026-05-10.) The DB binding (env.DB → purebrain-social) remains for
// magic_links table reads/writes only.
//
// Error handling per CTO brief (Option A — retry-once-with-backoff, then
// log + 200): AgentMail does NOT retry on 5xx. Hard-fail would silently
// lose the magic-link event. So we retry once with 250ms backoff and on
// final failure log to surface in monitoring, then let the caller continue.
// The webhook handler still returns 200 to AgentMail regardless.
//
// Retry-once helper.
async function callClientsApi(env, path, { method = "POST", body = null } = {}) {
  if (!env.CLIENTS_API) {
    throw new Error("CLIENTS_API service binding not configured");
  }
  if (!env.INTERNAL_BINDING_SECRET) {
    throw new Error("INTERNAL_BINDING_SECRET not configured");
  }

  const init = {
    method,
    headers: {
      "content-type": "application/json",
      "x-internal-binding": "clients-api",
      "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
    },
  };
  if (body !== null) init.body = JSON.stringify(body);

  const url = `https://clients-api${path}`;

  let lastErr = null;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const req = new Request(url, init);
      const resp = await env.CLIENTS_API.fetch(req);

      if (resp.status === 404) {
        // 404 = lookup miss (not_found). Return shape so caller can act.
        const j = await resp.json().catch(() => ({}));
        return { ok: false, status: 404, data: null, error: j.error || "not_found" };
      }
      if (!resp.ok) {
        const errText = await resp.text().catch(() => "");
        lastErr = new Error(`clients-api ${path} failed: ${resp.status} ${errText.slice(0, 200)}`);
        if (attempt === 0) {
          await new Promise(r => setTimeout(r, 250));
          continue;
        }
        throw lastErr;
      }

      const j = await resp.json().catch(() => ({}));
      if (j && j.ok === false) {
        lastErr = new Error(`clients-api ${path} ok=false: ${JSON.stringify(j.error || j).slice(0, 200)}`);
        if (attempt === 0) {
          await new Promise(r => setTimeout(r, 250));
          continue;
        }
        throw lastErr;
      }
      return j;
    } catch (e) {
      lastErr = e;
      if (attempt === 0) {
        await new Promise(r => setTimeout(r, 250));
        continue;
      }
      throw lastErr;
    }
  }
  throw lastErr || new Error("clients-api unknown error");
}

async function lookupPaypalEmail(env, humanEmail) {
  if (!humanEmail) return null;

  try {
    const result = await callClientsApi(env, `/internal/clients/get-amount?email=${encodeURIComponent(humanEmail)}`, {
      method: "GET",
    });
    if (result && result.ok && result.data && result.data.paypal_email) {
      console.log(`[agentmail-webhook] paypal_email resolved via clients-api for ${humanEmail}`);
      return result.data.paypal_email;
    }
    return null;
  } catch (e) {
    // Logged failure; webhook continues per CTO Option A.
    console.log(`[agentmail-webhook] CLIENTS_API_FAILURE lookupPaypalEmail email=${humanEmail} err=${e.message}`);
    return null;
  }
}

async function updateClientRecord(env, { email, ai_name, magic_link }) {
  if (!email) return;

  const fields = {};
  if (ai_name !== undefined && ai_name !== null) fields.ai_name = ai_name;
  if (magic_link !== undefined && magic_link !== null) fields.magic_link = magic_link;
  // last_active_at is now() — clients-api accepts ISO string; allowlist permits it.
  fields.last_active_at = new Date().toISOString();

  try {
    const result = await callClientsApi(env, "/internal/clients/update-fields", {
      method: "POST",
      body: { email, fields },
    });
    const changed = result?.data?.changes ?? 0;
    console.log(`[agentmail-webhook] Updated client record via clients-api: email=${email}, ai_name=${ai_name}, rows=${changed}`);
  } catch (e) {
    // Logged failure; webhook continues per CTO Option A. Non-fatal: client
    // may not exist yet (magic link arrived before PayPal webhook) — that
    // surfaces here as result.changes=0 (200) or 404 from clients-api.
    console.log(`[agentmail-webhook] CLIENTS_API_FAILURE updateClientRecord email=${email} err=${e.message}`);
  }
}

// ---------------------------------------------------------------------------
// Webhook handler — processes incoming AgentMail events
// ---------------------------------------------------------------------------

async function handleWebhook(request, env) {
  // Log all headers for debugging webhook format (remove after confirmed working)
  const headerLog = {};
  for (const [k, v] of request.headers.entries()) {
    if (k.toLowerCase().includes('secret') || k.toLowerCase().includes('signature') ||
        k.toLowerCase().includes('webhook') || k.toLowerCase().includes('auth')) {
      headerLog[k] = v.substring(0, 50);
    }
  }
  console.log(`[agentmail-webhook] Auth headers: ${JSON.stringify(headerLog)}`);

  // Webhook secret verification — flexible matching for AgentMail format
  // TODO: tighten once we confirm AgentMail's exact header format
  if (env.AGENTMAIL_WEBHOOK_SECRET) {
    const possibleHeaders = [
      'x-webhook-secret', 'x-webhook-signature', 'webhook-secret',
      'x-agentmail-signature', 'authorization',
    ];
    let matched = false;
    for (const h of possibleHeaders) {
      const val = request.headers.get(h);
      if (val && (val === env.AGENTMAIL_WEBHOOK_SECRET ||
                  val === `Bearer ${env.AGENTMAIL_WEBHOOK_SECRET}` ||
                  val.includes(env.AGENTMAIL_WEBHOOK_SECRET))) {
        matched = true;
        break;
      }
    }
    // For now, log mismatch but DON'T reject — we need to see real payloads first
    if (!matched) {
      console.log('[agentmail-webhook] Webhook secret not matched in any header — proceeding anyway (learning mode)');
    }
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    console.log(`[agentmail-webhook] Invalid JSON: ${e.message}`);
    return jsonResponse({ ok: false, error: 'Invalid JSON' }, 400);
  }

  // Log raw payload structure for debugging (remove after confirmed working)
  const topKeys = Object.keys(body);
  console.log(`[agentmail-webhook] Payload top-level keys: ${topKeys.join(', ')}`);

  // AgentMail webhook payload structure (flexible — handles multiple formats):
  // Format A: { event: "message.received", data: { message_id, from, to, subject, text, html, ... } }
  // Format B: { type: "message.received", message: { ... } }
  // Format C: raw message object { from, subject, text, ... }
  const event = body.event || body.type || 'unknown';
  const message = body.data || body.message || body;

  // Handle 'from' being a string or object { email, name }
  let sender = message.from || message.sender || '';
  if (typeof sender === 'object') {
    sender = sender.email || sender.address || JSON.stringify(sender);
  }
  const subject = message.subject || '';
  const emailBody = message.text || message.extracted_text || message.body ||
                    message.html || message.extracted_html || message.content || '';
  const messageId = message.message_id || message.id || '';

  console.log(`[agentmail-webhook] Received event=${event}, from=${sender}, subject=${subject}, id=${messageId}`);

  // Only process magic link emails
  if (!isMagicLinkEmail(subject, sender)) {
    console.log(`[agentmail-webhook] Not a magic link email — forwarding notification only`);

    // Send Telegram notification for non-magic-link emails
    await sendTelegram(env,
      `AgentMail: New message\n` +
      `From: ${sender}\n` +
      `Subject: ${subject}\n\n` +
      `${(emailBody || '').substring(0, 500)}`
    );

    return jsonResponse({
      ok: true,
      action: 'notified',
      reason: 'not_magic_link',
    });
  }

  // --- Magic Link Pipeline ---
  console.log(`[agentmail-webhook] MAGIC LINK email detected: subject="${subject}"`);

  // Step 1: Parse fields from email body
  const parsed = parseMagicLinkBody(emailBody);

  if (!parsed.magic_link) {
    console.log('[agentmail-webhook] PARSE FAILED: no magic link URL found in body');

    await sendTelegram(env,
      `MAGIC LINK email from Witness -- PARSE FAILED\n` +
      `Subject: ${subject}\n` +
      `Preview: ${(emailBody || '').substring(0, 400)}`
    );

    return jsonResponse({
      ok: false,
      error: 'Failed to parse magic link from email body',
      preview: (emailBody || '').substring(0, 200),
    }, 422);
  }

  const aiName = parsed.ai_name || 'Your AI';
  const humanName = parsed.human_name || '';
  const humanEmail = parsed.human_email || '';
  const uuid = parsed.uuid || '';
  const container = parsed.container || '';
  const originalLink = parsed.magic_link;

  // Step 1.5: Birth pipeline DNS automation (feature-flagged, default OFF)
  // Runs BEFORE rewrite so we fail-fast before storing/sending a dead link.
  const dnsResult = await ensureBirthDns(env, originalLink);
  if (!dnsResult.ok && dnsResult.action !== 'flag_disabled' && dnsResult.action !== 'no_slug') {
    console.log(`[agentmail-webhook] BIRTH-DNS failed, aborting magic link pipeline: ${JSON.stringify(dnsResult)}`);
    return jsonResponse({
      ok: false,
      error: `Birth DNS automation failed: ${dnsResult.action} — ${dnsResult.error || dnsResult.alert || 'see logs'}`,
      birth_dns: dnsResult,
    }, 500);
  }

  // Step 2: Domain rewrite (.ai-civ.com -> .app.purebrain.ai)
  const rewrittenLink = rewriteDomain(
    originalLink,
    env.DOMAIN_REWRITE_FROM,
    env.DOMAIN_REWRITE_TO
  );
  console.log(`[agentmail-webhook] Domain rewrite: ${originalLink} -> ${rewrittenLink}`);

  const humanFirst = humanName ? humanName.split(/\s+/)[0] : 'there';

  // Generate a fallback UUID if none was parsed
  const sessionUuid = uuid || (humanEmail ? `email:${humanEmail}` : `ts:${Date.now()}`);

  // Step 3: Look up PayPal email from D1 clients table
  let paypalEmail = null;
  try {
    paypalEmail = await lookupPaypalEmail(env, humanEmail);
  } catch (e) {
    console.log(`[agentmail-webhook] PayPal email lookup failed (non-fatal): ${e.message}`);
  }

  // Step 4: Store in D1 magic_links table
  let storeResult;
  try {
    storeResult = await storeMagicLink(env, {
      session_uuid: sessionUuid,
      ai_name: aiName,
      human_name: humanName,
      human_email: humanEmail,
      paypal_email: paypalEmail,
      container,
      magic_link: rewrittenLink,
      original_link: originalLink,
    });
  } catch (e) {
    console.error(`[agentmail-webhook] D1 store failed: ${e.message}`);
    return jsonResponse({
      ok: false,
      error: `D1 write failed: ${e.message}`,
    }, 500);
  }

  if (storeResult.duplicate) {
    console.log('[agentmail-webhook] Duplicate magic link — skipping welcome email');
    return jsonResponse({
      ok: true,
      action: 'duplicate_skipped',
      magic_link: rewrittenLink,
    });
  }

  // Step 5: Determine welcome email recipients (dual-send logic)
  const emailsToSend = new Set();
  let sandboxRedirected = false;

  if (humanEmail && humanEmail.includes('@')) {
    if (isSandboxEmail(humanEmail)) {
      console.log(`[agentmail-webhook] Sandbox bypass: ${humanEmail} -> ${SANDBOX_REDIRECT}`);
      emailsToSend.add(SANDBOX_REDIRECT);
      sandboxRedirected = true;
    } else {
      emailsToSend.add(humanEmail.toLowerCase().trim());
    }
  }

  if (paypalEmail && paypalEmail.includes('@')) {
    const ppLower = paypalEmail.toLowerCase().trim();
    if (isSandboxEmail(ppLower)) {
      if (!sandboxRedirected) {
        console.log(`[agentmail-webhook] Sandbox bypass (PayPal): ${paypalEmail} -> ${SANDBOX_REDIRECT}`);
        emailsToSend.add(SANDBOX_REDIRECT);
        sandboxRedirected = true;
      }
    } else if (ppLower !== '(sandbox-sub)') {
      emailsToSend.add(ppLower);
    }
  }

  // Step 6: Send welcome email(s) via welcome-email-api Worker
  let welcomeResults = [];
  for (const addr of emailsToSend) {
    const result = await sendWelcomeEmail(env, {
      human_email: addr,
      human_first: humanFirst,
      ai_name: aiName,
      magic_link: rewrittenLink,
    });
    welcomeResults.push({ email: addr, ...result });
  }

  const allSent = welcomeResults.every(r => r.ok);

  // Mark welcome sent in D1
  if (allSent && emailsToSend.size > 0) {
    try {
      await markWelcomeSent(env, rewrittenLink);
    } catch (e) {
      console.log(`[agentmail-webhook] Failed to mark welcome sent: ${e.message}`);
    }
  }

  // Step 7: Update client record in D1 (ai_name + magic_link)
  if (humanEmail) {
    await updateClientRecord(env, {
      email: humanEmail,
      ai_name: aiName,
      magic_link: rewrittenLink,
    });
  }
  // Also update by PayPal email if different
  if (paypalEmail && paypalEmail.toLowerCase() !== (humanEmail || '').toLowerCase()) {
    await updateClientRecord(env, {
      email: paypalEmail,
      ai_name: aiName,
      magic_link: rewrittenLink,
    });
  }

  // Step 8: Telegram notification
  let emailSummary = humanEmail || '(no email)';
  if (paypalEmail && paypalEmail.toLowerCase().trim() !== (humanEmail || '').toLowerCase().trim()) {
    emailSummary += ` + PayPal: ${paypalEmail}`;
  }

  await sendTelegram(env,
    `MAGIC LINK received from Witness\n` +
    `AI: ${aiName}\n` +
    `Human: ${humanName} (${emailSummary})\n` +
    `UUID: ${sessionUuid}\n` +
    `Container: ${container}\n` +
    `Link: ${rewrittenLink}\n` +
    `Welcome email: ${emailsToSend.size} address(es)` +
    (allSent ? '' : ' (SOME FAILED)')
  );

  console.log(`[agentmail-webhook] Magic link pipeline complete: uuid=${sessionUuid}, emails=${emailsToSend.size}`);

  return jsonResponse({
    ok: true,
    action: 'magic_link_processed',
    session_uuid: sessionUuid,
    ai_name: aiName,
    magic_link: rewrittenLink,
    welcome_emails: welcomeResults,
  });
}

// ---------------------------------------------------------------------------
// Magic link polling endpoint — thank-you page calls this
// ---------------------------------------------------------------------------

async function handleMagicLinkPoll(request, env, uuid) {
  const url = new URL(request.url);
  const emailParam = url.searchParams.get('email') || '';

  console.log(`[agentmail-webhook] Magic link poll: uuid=${uuid}, email=${emailParam}`);

  // Try 1: Direct UUID lookup
  let row = null;
  if (uuid && uuid !== 'undefined' && uuid !== 'null') {
    row = await env.DB.prepare(
      'SELECT ai_name, magic_link, status FROM magic_links WHERE session_uuid = ? ORDER BY received_at DESC LIMIT 1'
    ).bind(uuid).first();
  }

  // Try 2: UUID with email: prefix (fallback key format)
  if (!row && emailParam) {
    row = await env.DB.prepare(
      'SELECT ai_name, magic_link, status FROM magic_links WHERE session_uuid = ? ORDER BY received_at DESC LIMIT 1'
    ).bind(`email:${emailParam.toLowerCase()}`).first();
  }

  // Try 3: Match by human_email
  if (!row && emailParam) {
    row = await env.DB.prepare(
      'SELECT ai_name, magic_link, status FROM magic_links WHERE LOWER(human_email) = LOWER(?) ORDER BY received_at DESC LIMIT 1'
    ).bind(emailParam).first();
  }

  if (row && row.magic_link) {
    return jsonResponse({
      status: 'ready',
      magic_link: row.magic_link,
      ai_name: row.ai_name || '',
    });
  }

  return jsonResponse({ status: 'pending' });
}

// ---------------------------------------------------------------------------
// Manual process-email endpoint (admin only)
// ---------------------------------------------------------------------------

async function handleProcessEmail(request, env) {
  // Verify admin token
  const authHeader = request.headers.get('Authorization') || '';
  const token = authHeader.replace(/^Bearer\s+/i, '');

  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return jsonResponse({ ok: false, error: 'Unauthorized' }, 401);
  }

  // Accept the same body format as the webhook for manual re-processing
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return jsonResponse({ ok: false, error: 'Invalid JSON' }, 400);
  }

  // Wrap in webhook format and process
  const fakeRequest = new Request(request.url, {
    method: 'POST',
    headers: request.headers,
    body: JSON.stringify({
      event: 'message.received',
      data: body,
    }),
  });

  // Bypass webhook secret check for admin endpoint
  const originalSecret = env.AGENTMAIL_WEBHOOK_SECRET;
  env.AGENTMAIL_WEBHOOK_SECRET = null;
  const result = await handleWebhook(fakeRequest, env);
  env.AGENTMAIL_WEBHOOK_SECRET = originalSecret;

  return result;
}

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------

async function handleHealth(env) {
  try {
    const count = await env.DB.prepare(
      'SELECT COUNT(*) as total FROM magic_links'
    ).first();

    return jsonResponse({
      status: 'ok',
      worker: 'agentmail-webhook',
      magic_links_count: count?.total || 0,
      timestamp: new Date().toISOString(),
    });
  } catch (e) {
    return jsonResponse({
      status: 'error',
      worker: 'agentmail-webhook',
      error: e.message,
    }, 500);
  }
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method;
    const path = url.pathname;

    // CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Webhook-Secret',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    // POST /webhook — AgentMail webhook receiver
    if (method === 'POST' && (path === '/webhook' || path === '/')) {
      return handleWebhook(request, env);
    }

    // GET /api/magic-link/:uuid — thank-you page polling
    const magicLinkMatch = path.match(/^\/api\/magic-link\/(.+)$/);
    if (method === 'GET' && magicLinkMatch) {
      return handleMagicLinkPoll(request, env, decodeURIComponent(magicLinkMatch[1]));
    }

    // GET /health — health check
    if (method === 'GET' && path === '/health') {
      return handleHealth(env);
    }

    // POST /api/process-email — manual admin trigger
    if (method === 'POST' && path === '/api/process-email') {
      return handleProcessEmail(request, env);
    }

    return jsonResponse({ error: 'Not found' }, 404);
  },
};

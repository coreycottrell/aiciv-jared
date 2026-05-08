/**
 * welcome-email-api — Cloudflare Worker
 * Sends personalized welcome emails via Brevo transactional API.
 * Templates and delivery logs stored in D1 (purebrain-social).
 */

// --- Constants ---
const DOMAIN_REWRITE_FROM = '.ai-civ.com';
const DOMAIN_REWRITE_TO = '.app.purebrain.ai';
const SANDBOX_PATTERN = /^sb-[^@]+@/i;
const SANDBOX_REDIRECT = 'jared@puretechnology.nyc';
const BREVO_SEND_URL = 'https://api.brevo.com/v3/smtp/email';
const DEFAULT_TEMPLATE_ID = 'welcome-v1';

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://social.purebrain.ai',
];

// --- Default HTML Template (from welcome-email-template.html) ---
const DEFAULT_HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Your PureBrain AI is Ready</title>
  <!--[if mso]>
  <style type="text/css">
    table, td { font-family: Arial, sans-serif; }
  </style>
  <![endif]-->
</head>
<body bgcolor="#080a12" style="margin:0;padding:0;background-color:#080a12;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#080a12" style="background-color:#080a12;margin:0;padding:0;">
  <tr>
    <td align="center" style="padding:0;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px;width:100%;margin:0 auto;">
        <tr>
          <td style="padding:32px 0 0;font-size:0;line-height:0;" height="32">&nbsp;</td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 16px;">
            <img src="https://purebrain.ai/pitch-v2/pt-hex-logo.webp" alt="PureBrain" width="56" height="56" style="display:block;width:56px;height:56px;border:0;outline:none;text-decoration:none;">
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 24px;font-size:20px;font-weight:700;letter-spacing:-0.5px;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            <span style="color:#2a93c1;">PUREBR</span><span style="color:#f1420b;">AI</span><span style="color:#2a93c1;">N</span><span style="color:#ffffff;">.AI</span>
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="border-top:1px solid #1a1d2e;font-size:0;line-height:0;" height="1">&nbsp;</td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:32px 0 0;font-size:0;line-height:0;" height="32">&nbsp;</td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 20px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="background-color:#0d1520;border:1px solid #1a3a4d;border-radius:100px;padding:6px 20px;font-size:13px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#2a93c1;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                  {AI_NAME} is online
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 8px;font-size:32px;font-weight:700;color:#ffffff;line-height:1.25;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            WELCOME, {HUMAN_FIRST}.
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 16px;font-size:28px;font-weight:700;line-height:1.25;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            <span style="color:#f1420b;">{AI_NAME}</span> <span style="color:#ffffff;">IS READY FOR YOU.</span>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 32px 32px;font-size:16px;color:#9ca3af;line-height:1.6;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            Your personal AI has been built, named, and is waiting inside your Brain Stream. One tap and you are in.
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 12px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" bgcolor="#2a93c1" style="background-color:#2a93c1;border-radius:8px;">
                  <a href="{MAGIC_LINK}" target="_blank" style="display:inline-block;padding:16px 40px;font-size:16px;font-weight:700;color:#ffffff;text-decoration:none;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;letter-spacing:0.3px;border-radius:8px;">
                    ENTER {AI_NAME}'S BRAIN STREAM &rarr;
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 40px;font-size:13px;color:#6b7280;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            This link is personal to you &mdash; do not share it.
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="border-top:1px solid #1a1d2e;font-size:0;line-height:0;" height="1">&nbsp;</td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:32px 16px 20px;font-size:18px;font-weight:700;color:#ffffff;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            What happens when you enter
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px 14px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td width="20" valign="top" style="padding-top:6px;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="8" height="8" bgcolor="#f1420b" style="background-color:#f1420b;border-radius:50%;font-size:0;line-height:0;">&nbsp;</td>
                    </tr>
                  </table>
                </td>
                <td style="font-size:15px;color:#c9d1d9;line-height:1.5;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                  {AI_NAME} already knows your name, your goal, and your context &mdash; no setup required
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px 14px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td width="20" valign="top" style="padding-top:6px;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="8" height="8" bgcolor="#f1420b" style="background-color:#f1420b;border-radius:50%;font-size:0;line-height:0;">&nbsp;</td>
                    </tr>
                  </table>
                </td>
                <td style="font-size:15px;color:#c9d1d9;line-height:1.5;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                  Every conversation builds on the last &mdash; {AI_NAME} remembers everything
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px 14px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td width="20" valign="top" style="padding-top:6px;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="8" height="8" bgcolor="#f1420b" style="background-color:#f1420b;border-radius:50%;font-size:0;line-height:0;">&nbsp;</td>
                    </tr>
                  </table>
                </td>
                <td style="font-size:15px;color:#c9d1d9;line-height:1.5;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                  Your Brain Stream is private &mdash; nobody else can access it
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px 32px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td width="20" valign="top" style="padding-top:6px;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="8" height="8" bgcolor="#f1420b" style="background-color:#f1420b;border-radius:50%;font-size:0;line-height:0;">&nbsp;</td>
                    </tr>
                  </table>
                </td>
                <td style="font-size:15px;color:#c9d1d9;line-height:1.5;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                  The more you use {AI_NAME}, the more precisely it gets shaped to how you think
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px 32px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border:1px solid #2d1a1a;border-radius:8px;">
              <tr>
                <td bgcolor="#120b0a" style="background-color:#120b0a;padding:16px 20px;border-radius:8px;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td style="font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#f1420b;padding-bottom:8px;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                        IMPORTANT
                      </td>
                    </tr>
                    <tr>
                      <td style="font-size:14px;color:#c9d1d9;line-height:1.5;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
                        Bookmark your Brain Stream link or save this email &mdash; it is your direct access point.
                        If you ever lose it, reach out to
                        <a href="mailto:support@puremarketing.ai" style="color:#2a93c1;text-decoration:none;">support@puremarketing.ai</a>
                        and we will get you back in.
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:0 16px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="border-top:1px solid #1a1d2e;font-size:0;line-height:0;" height="1">&nbsp;</td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:24px 16px 8px;font-size:13px;color:#6b7280;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            <a href="https://purebrain.ai" style="color:#2a93c1;text-decoration:none;">purebrain.ai</a>
            <span style="color:#374151;">&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <a href="mailto:support@puremarketing.ai" style="color:#2a93c1;text-decoration:none;">support@puremarketing.ai</a>
            <span style="color:#374151;">&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <a href="https://purebrain.ai/why-purebrain/" style="color:#2a93c1;text-decoration:none;">Why PureBrain?</a>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:0 16px 32px;font-size:13px;color:#6b7280;line-height:1.5;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;">
            You are receiving this because you joined PureBrain.<br>
            Built by Aether (an AI) for Pure Technology.
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>`;

const DEFAULT_TEXT_TEMPLATE = `WELCOME, {HUMAN_FIRST}.

{AI_NAME} IS READY FOR YOU.

Your personal AI has been built, named, and is waiting inside your Brain Stream. One tap and you are in.

ENTER {AI_NAME}'S BRAIN STREAM:
{MAGIC_LINK}

This link is personal to you - do not share it.

---

What happens when you enter:

- {AI_NAME} already knows your name, your goal, and your context - no setup required
- Every conversation builds on the last - {AI_NAME} remembers everything
- Your Brain Stream is private - nobody else can access it
- The more you use {AI_NAME}, the more precisely it gets shaped to how you think

IMPORTANT: Bookmark your Brain Stream link or save this email - it is your direct access point. If you ever lose it, reach out to support@puremarketing.ai and we will get you back in.

---
purebrain.ai | support@puremarketing.ai | Why PureBrain?
You are receiving this because you joined PureBrain.
Built by Aether (an AI) for Pure Technology.`;

const DEFAULT_SUBJECT_TEMPLATE = '{AI_NAME} is ready for you, {HUMAN_FIRST} — here\'s your access link';

// --- Helpers ---

function generateId() {
  return crypto.randomUUID();
}

function rewriteDomain(link) {
  if (!link) return link;
  // Domain rewrite DISABLED — *.app.purebrain.ai has no SSL cert yet (ERR_SSL_PROTOCOL_ERROR)
  // Re-enable once Caddy on 37.27.237.109 has wildcard cert for *.app.purebrain.ai
  // return link.replaceAll(DOMAIN_REWRITE_FROM, DOMAIN_REWRITE_TO);
  return link;
}

function isSandbox(email) {
  return SANDBOX_PATTERN.test(email);
}

function renderTemplate(template, vars) {
  let result = template;
  result = result.replaceAll('{HUMAN_FIRST}', vars.human_first || '');
  result = result.replaceAll('{AI_NAME}', vars.ai_name || '');
  result = result.replaceAll('{MAGIC_LINK}', vars.magic_link || '');
  result = result.replaceAll('{TIER}', vars.tier || '');
  return result;
}

function corsHeaders(request) {
  const origin = request?.headers?.get('Origin') || '';
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Token',
    'Access-Control-Max-Age': '86400',
  };
}

function cors(request) {
  return new Response(null, { status: 204, headers: corsHeaders(request) });
}

function json(data, status = 200, request = null) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(request),
    },
  });
}

function err(status, message, request = null) {
  return json({ ok: false, error: message }, status, request);
}

// --- Auth ---

function requireAuth(request, env, handler) {
  const token = request.headers.get('X-Admin-Token');
  if (!token || token !== env.ADMIN_TOKEN) {
    return err(401, 'Unauthorized', request);
  }
  return handler();
}

// --- Schema / Seed ---

let schemaEnsured = false;

async function ensureSchema(env) {
  if (schemaEnsured) return;

  // Tables created via wrangler d1 execute (schema.sql).
  // This function only seeds the default template if missing.
  const existing = await env.DB.prepare(
    'SELECT id FROM email_templates WHERE id = ?'
  ).bind(DEFAULT_TEMPLATE_ID).first();

  if (!existing) {
    await env.DB.prepare(`
      INSERT INTO email_templates (id, name, subject_tmpl, html_tmpl, text_tmpl)
      VALUES (?, ?, ?, ?, ?)
    `).bind(
      DEFAULT_TEMPLATE_ID,
      'Default Welcome Email',
      DEFAULT_SUBJECT_TEMPLATE,
      DEFAULT_HTML_TEMPLATE,
      DEFAULT_TEXT_TEMPLATE
    ).run();
  }

  schemaEnsured = true;
}

// --- Brevo ---

async function sendBrevo(env, payload) {
  const resp = await fetch(BREVO_SEND_URL, {
    method: 'POST',
    headers: {
      'api-key': env.BREVO_API_KEY,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const body = await resp.json().catch(() => ({}));
  return { ok: resp.ok, status: resp.status, body };
}

// --- Delivery Log ---

async function logDelivery(env, row) {
  try {
    await env.DB.prepare(`
      INSERT INTO email_delivery_log (id, template_id, recipient_email, recipient_name, ai_name, magic_link, tier, status, brevo_message_id, error)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      row.id,
      row.template_id,
      row.recipient_email,
      row.recipient_name,
      row.ai_name,
      row.magic_link,
      row.tier,
      row.status,
      row.brevo_message_id || null,
      row.error || null
    ).run();
  } catch (e) {
    console.error('Failed to write delivery log:', e);
  }
}

// --- Handlers ---

async function handleSend(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return err(400, 'Invalid JSON body', request);
  }

  const { human_email, human_first, ai_name, magic_link, tier } = body;

  // Validate required fields
  if (!human_email || !human_first || !ai_name || !magic_link) {
    return err(400, 'Missing required fields: human_email, human_first, ai_name, magic_link', request);
  }

  // Validate ai_name is not empty/placeholder
  if (!ai_name.trim()) {
    return err(400, 'ai_name must not be empty', request);
  }

  // Domain rewrite
  const rewrittenLink = rewriteDomain(magic_link);

  // Sandbox bypass
  const sandboxed = isSandbox(human_email);
  const actualRecipient = sandboxed ? SANDBOX_REDIRECT : human_email;

  // Load template
  const template = await env.DB.prepare(
    'SELECT subject_tmpl, html_tmpl, text_tmpl FROM email_templates WHERE id = ?'
  ).bind(DEFAULT_TEMPLATE_ID).first();

  if (!template) {
    return err(500, 'Template not found in database', request);
  }

  // Render
  const vars = {
    human_first,
    ai_name,
    magic_link: rewrittenLink,
    tier: tier || 'Awakened',
  };

  const renderedSubject = renderTemplate(template.subject_tmpl, vars);
  const renderedHtml = renderTemplate(template.html_tmpl, vars);
  const renderedText = template.text_tmpl ? renderTemplate(template.text_tmpl, vars) : '';

  // Send via Brevo
  const brevoPayload = {
    sender: { name: 'Aether | PureBrain', email: 'purebrain@puremarketing.ai' },
    to: [{ email: actualRecipient, name: human_first }],
    bcc: [{ email: 'jared@puretechnology.nyc' }],
    replyTo: { email: 'support@puremarketing.ai' },
    subject: renderedSubject,
    htmlContent: renderedHtml,
    textContent: renderedText,
  };

  const brevoResult = await sendBrevo(env, brevoPayload);

  const logId = generateId();
  const logRow = {
    id: logId,
    template_id: DEFAULT_TEMPLATE_ID,
    recipient_email: human_email, // Log original, not redirected
    recipient_name: human_first,
    ai_name,
    magic_link: rewrittenLink,
    tier: tier || 'Awakened',
    status: sandboxed ? 'sandbox_redirect' : (brevoResult.ok ? 'sent' : 'failed'),
    brevo_message_id: brevoResult.body?.messageId || null,
    error: brevoResult.ok ? null : JSON.stringify(brevoResult.body),
  };

  // Log delivery (fire-and-forget via waitUntil if available)
  await logDelivery(env, logRow);

  if (!brevoResult.ok) {
    return json({
      ok: false,
      error: `Brevo API returned ${brevoResult.status}`,
      log_id: logId,
    }, 500, request);
  }

  return json({
    ok: true,
    log_id: logId,
    recipient: actualRecipient,
  }, 200, request);
}

async function handleHealth(env, request) {
  try {
    await env.DB.prepare('SELECT 1 FROM email_templates LIMIT 1').first();
    return json({ status: 'ok', worker: 'welcome-email-api', db: 'connected' }, 200, request);
  } catch (e) {
    return json({ status: 'error', worker: 'welcome-email-api', db: 'disconnected', error: e.message }, 500, request);
  }
}

async function handleListTemplates(env, request) {
  const results = await env.DB.prepare(
    'SELECT id, name, created_at, updated_at FROM email_templates'
  ).all();

  return json({ templates: results.results }, 200, request);
}

async function handlePutTemplate(request, env, path) {
  const id = path.replace('/templates/', '');
  if (!id) return err(400, 'Template ID required', request);

  let body;
  try {
    body = await request.json();
  } catch {
    return err(400, 'Invalid JSON body', request);
  }

  const { name, subject_tmpl, html_tmpl, text_tmpl } = body;

  if (!name || !subject_tmpl || !html_tmpl) {
    return err(400, 'Missing required fields: name, subject_tmpl, html_tmpl', request);
  }

  // Validate required placeholders are present in html_tmpl
  const requiredPlaceholders = ['{HUMAN_FIRST}', '{AI_NAME}', '{MAGIC_LINK}'];
  const missing = requiredPlaceholders.filter(p => !html_tmpl.includes(p));
  if (missing.length > 0) {
    return err(400, `Template missing required placeholders: ${missing.join(', ')}`, request);
  }

  await env.DB.prepare(`
    INSERT INTO email_templates (id, name, subject_tmpl, html_tmpl, text_tmpl, updated_at)
    VALUES (?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(id) DO UPDATE SET
      name = excluded.name,
      subject_tmpl = excluded.subject_tmpl,
      html_tmpl = excluded.html_tmpl,
      text_tmpl = excluded.text_tmpl,
      updated_at = datetime('now')
  `).bind(id, name, subject_tmpl, html_tmpl, text_tmpl || null).run();

  return json({ ok: true, id }, 200, request);
}

async function handleDeliveryLog(request, env) {
  const url = new URL(request.url);
  let limit = parseInt(url.searchParams.get('limit') || '50', 10);
  let offset = parseInt(url.searchParams.get('offset') || '0', 10);
  const status = url.searchParams.get('status');

  // Clamp
  if (limit > 200) limit = 200;
  if (limit < 1) limit = 50;
  if (offset < 0) offset = 0;

  let query = 'SELECT * FROM email_delivery_log';
  let countQuery = 'SELECT COUNT(*) as total FROM email_delivery_log';
  const params = [];

  if (status) {
    query += ' WHERE status = ?';
    countQuery += ' WHERE status = ?';
    params.push(status);
  }

  query += ' ORDER BY sent_at DESC LIMIT ? OFFSET ?';

  const countResult = await env.DB.prepare(countQuery)
    .bind(...params)
    .first();

  const results = await env.DB.prepare(query)
    .bind(...params, limit, offset)
    .all();

  return json({
    rows: results.results,
    total: countResult?.total || 0,
    limit,
    offset,
  }, 200, request);
}

// --- Router ---
export default {
  async fetch(request, env, ctx) {
    await ensureSchema(env);

    const url = new URL(request.url);
    const method = request.method;
    const path = url.pathname;

    if (method === 'OPTIONS') return cors(request);

    if (method === 'POST' && path === '/send-welcome') return handleSend(request, env);
    if (method === 'GET' && path === '/health') return handleHealth(env, request);
    if (method === 'GET' && path === '/templates') return requireAuth(request, env, () => handleListTemplates(env, request));
    if (method === 'PUT' && path.startsWith('/templates/')) return requireAuth(request, env, () => handlePutTemplate(request, env, path));
    if (method === 'GET' && path === '/delivery-log') return requireAuth(request, env, () => handleDeliveryLog(request, env));

    return err(404, 'Not found', request);
  },
};

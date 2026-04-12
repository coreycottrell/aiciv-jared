/**
 * CF Pages Function: /api/subscribe
 * Proxies Brevo contact creation — keeps BREVO_API_KEY server-side.
 * Called by the Neural Feed subscription form on /blog/
 *
 * Environment variable required (set in CF Pages dashboard):
 *   BREVO_API_KEY — Brevo (Sendinblue) API key
 *
 * CORS: allows purebrain.ai, purebrain-staging.pages.dev
 */

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://purebrain-staging.pages.dev',
];

const BREVO_LIST_ID = 3;

export async function onRequestPost(context) {
  const { request, env } = context;

  const origin = request.headers.get('Origin') || '';
  const corsOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];

  const corsHeaders = {
    'Access-Control-Allow-Origin': corsOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };

  // Parse body
  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ message: 'Invalid JSON body' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  const { email } = body;
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response(JSON.stringify({ message: 'Valid email required' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  const apiKey = env.BREVO_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ message: 'Server configuration error' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  // Call Brevo
  const brevoResp = await fetch('https://api.brevo.com/v3/contacts', {
    method: 'POST',
    headers: {
      'api-key': apiKey,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      email,
      listIds: [BREVO_LIST_ID],
      updateEnabled: true,
      attributes: { SOURCE: 'purebrain-blog' },
    }),
  });

  const status = brevoResp.status;

  if (status === 201) {
    return new Response(JSON.stringify({ ok: true, message: 'subscribed' }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
  if (status === 204) {
    return new Response(JSON.stringify({ ok: true, message: 'already_subscribed' }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  // Relay Brevo error details
  let detail = '';
  try {
    const data = await brevoResp.json();
    detail = data.message || '';
  } catch {}

  return new Response(JSON.stringify({ message: detail || 'Subscription failed', brevo_status: status }), {
    status: 502,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

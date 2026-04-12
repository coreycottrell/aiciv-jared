/**
 * Cloudflare Pages Function — Brevo (Sendinblue) contact creation proxy
 * Keeps BREVO_API_KEY server-side — never exposed to the browser.
 *
 * Environment variables (set in CF Pages dashboard):
 *   BREVO_API_KEY — Brevo API key (xkeysib-... format)
 */

export async function onRequest(context) {
  const { request, env } = context;

  // CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': 'https://purebrain.ai',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
      },
    });
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'POST only' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const apiKey = (env.BREVO_API_KEY || '').trim().replace(/[\r\n]/g, '');
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'BREVO_API_KEY not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const body = await request.json();

    // Validate expected shape — must have email at minimum
    if (!body.email) {
      return new Response(JSON.stringify({ error: 'email required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const brevoPayload = {
      email: body.email,
      attributes: body.attributes || {},
      listIds: body.listIds || [],
      updateEnabled: body.updateEnabled !== undefined ? body.updateEnabled : true,
    };

    const resp = await fetch('https://api.brevo.com/v3/contacts', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'content-type': 'application/json',
        'api-key': apiKey,
      },
      body: JSON.stringify(brevoPayload),
    });

    const result = await resp.text();

    return new Response(result, {
      status: resp.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://purebrain.ai',
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: 'Brevo proxy error', detail: err.message }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

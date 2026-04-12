/**
 * Cloudflare Pages Function — Airtable API proxy
 * Keeps AIRTABLE_API_KEY server-side — never exposed to the browser.
 *
 * Environment variables (set in CF Pages dashboard):
 *   AIRTABLE_API_KEY — Airtable personal access token
 *   AIRTABLE_BASE_ID — Airtable base ID (default: app3PhIudYCZ8VCCF)
 */

export async function onRequest(context) {
  const { request, env } = context;

  // CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': 'https://purebrain.ai',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
      },
    });
  }

  const apiKey = (env.AIRTABLE_API_KEY || '').trim();
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'AIRTABLE_API_KEY not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const baseId = (env.AIRTABLE_BASE_ID || 'app3PhIudYCZ8VCCF').trim();
  const url = new URL(request.url);

  // Extract table and optional record ID from query params
  const table = url.searchParams.get('table') || 'Tasks';
  const recordId = url.searchParams.get('recordId') || '';

  const airtableUrl = recordId
    ? `https://api.airtable.com/v0/${baseId}/${encodeURIComponent(table)}/${recordId}`
    : `https://api.airtable.com/v0/${baseId}/${encodeURIComponent(table)}`;

  // Forward query params (except our routing ones) for filtering etc.
  const forwardParams = new URLSearchParams();
  for (const [key, value] of url.searchParams) {
    if (key !== 'table' && key !== 'recordId') {
      forwardParams.append(key, value);
    }
  }
  const queryString = forwardParams.toString();
  const finalUrl = queryString ? `${airtableUrl}?${queryString}` : airtableUrl;

  const fetchOpts = {
    method: request.method,
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
  };

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    fetchOpts.body = await request.text();
  }

  try {
    const resp = await fetch(finalUrl, fetchOpts);
    const body = await resp.text();

    return new Response(body, {
      status: resp.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://purebrain.ai',
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: 'Airtable proxy error', detail: err.message }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

/**
 * CF Pages Function: /api/investor-tts
 * Proxies ElevenLabs TTS requests for the investors-v8 Ask Aether section.
 *
 * Keeps ELEVENLABS_API_KEY server-side — never exposed to the browser.
 * Returns audio/mpeg binary stream to the client.
 *
 * Environment variables required:
 *   ELEVENLABS_API_KEY — ElevenLabs API key
 *
 * Voice: "Aether - Updated" — RX0kjGhuL9AMRVJm2dG5
 */

const VOICE_ID = 'RX0kjGhuL9AMRVJm2dG5';
const MODEL_ID = 'eleven_multilingual_v2';

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://purebrain-staging.pages.dev',
];

// Rate limit: 10 TTS requests per IP per 60s (TTS is expensive)
const rateLimitMap = new Map();
const RATE_LIMIT_MAX = 10;
const RATE_LIMIT_WINDOW_MS = 60_000;

function isRateLimited(ip) {
  const now = Date.now();
  const windowStart = now - RATE_LIMIT_WINDOW_MS;
  const timestamps = (rateLimitMap.get(ip) || []).filter(t => t > windowStart);
  if (timestamps.length >= RATE_LIMIT_MAX) return true;
  timestamps.push(now);
  rateLimitMap.set(ip, timestamps);
  return false;
}

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

export async function onRequestOptions({ request }) {
  return new Response(null, {
    status: 204,
    headers: corsHeaders(request),
  });
}

export async function onRequestPost({ request, env }) {
  const cors = corsHeaders(request);

  const apiKey = env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    // ElevenLabs not configured — return 503 so client falls back to Web Speech API
    return new Response(JSON.stringify({ error: 'TTS not configured.' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json', ...cors },
    });
  }

  const clientIP =
    request.headers.get('CF-Connecting-IP') ||
    request.headers.get('X-Forwarded-For') ||
    'unknown';

  if (isRateLimited(clientIP)) {
    return new Response(JSON.stringify({ error: 'Rate limit exceeded.' }), {
      status: 429,
      headers: { 'Content-Type': 'application/json', ...cors },
    });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON body.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', ...cors },
    });
  }

  const { text } = body;

  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    return new Response(JSON.stringify({ error: 'text is required.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', ...cors },
    });
  }

  // Truncate to 500 chars max — TTS is for short responses, not essays
  const truncated = text.trim().slice(0, 500);

  try {
    const ttsRes = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'xi-api-key': apiKey,
        },
        body: JSON.stringify({
          text: truncated,
          model_id: MODEL_ID,
          voice_settings: {
            stability: 0.55,
            similarity_boost: 0.80,
            style: 0.25,
            use_speaker_boost: true,
          },
        }),
      }
    );

    if (!ttsRes.ok) {
      const errText = await ttsRes.text();
      console.error('ElevenLabs error:', ttsRes.status, errText);
      return new Response(JSON.stringify({ error: 'TTS generation failed.' }), {
        status: 502,
        headers: { 'Content-Type': 'application/json', ...cors },
      });
    }

    // Stream the audio back directly
    const audioBuffer = await ttsRes.arrayBuffer();
    return new Response(audioBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'audio/mpeg',
        'Cache-Control': 'no-store',
        ...cors,
      },
    });
  } catch (err) {
    console.error('ElevenLabs fetch failed:', err);
    return new Response(JSON.stringify({ error: 'TTS request failed.' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', ...cors },
    });
  }
}

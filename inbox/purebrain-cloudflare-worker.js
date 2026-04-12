/**
 * Pure Brain Claude API Proxy - Cloudflare Worker
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://dash.cloudflare.com
 * 2. Click "Workers & Pages" in the left sidebar
 * 3. Click "Create Application" → "Create Worker"
 * 4. Name it: purebrain-api (or similar)
 * 5. Click "Deploy"
 * 6. Click "Edit Code" and paste this entire file
 * 7. Click "Save and Deploy"
 * 8. Go to Settings → Variables → Add:
 *    - Variable name: ANTHROPIC_API_KEY
 *    - Value: your Anthropic API key (sk-ant-...)
 *    - Click "Encrypt" to keep it secret
 * 9. Your endpoint will be: https://purebrain-api.YOUR-SUBDOMAIN.workers.dev/v1/messages
 */

// Allowed origins - add any domains that should access this API
const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://puremarketing.ai',
  'https://www.puremarketing.ai',
  'http://localhost:3000',  // For local development
];

// CORS headers
function getCorsHeaders(origin) {
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
}

// Handle OPTIONS preflight requests
function handleOptions(request) {
  const origin = request.headers.get('Origin') || '';
  return new Response(null, {
    status: 204,
    headers: getCorsHeaders(origin),
  });
}

// Main handler
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const corsHeaders = getCorsHeaders(origin);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return handleOptions(request);
    }

    // Only allow POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Check for API key
    if (!env.ANTHROPIC_API_KEY) {
      return new Response(JSON.stringify({ error: 'API key not configured' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    try {
      // Parse the incoming request
      const body = await request.json();

      // Forward to Anthropic API
      const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify(body),
      });

      // Get the response
      const data = await anthropicResponse.json();

      // Return the response with CORS headers
      return new Response(JSON.stringify(data), {
        status: anthropicResponse.status,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        },
      });

    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};

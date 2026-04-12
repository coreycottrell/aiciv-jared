/**
 * TTS Proxy Worker
 * Routes: purebrain.ai/api/tts/* -> http://37.27.237.109:8950/*
 * Provides HTTPS termination for the Chatterbox TTS API
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";

    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin),
      });
    }

    // Strip /api/tts prefix to get the backend path
    const backendPath = url.pathname.replace(/^\/api\/tts/, "") || "/";
    const backend = env.TTS_BACKEND || "http://37.27.237.109:8950";
    const backendUrl = backend + backendPath + url.search;

    try {
      const backendRequest = new Request(backendUrl, {
        method: request.method,
        headers: {
          "Content-Type": request.headers.get("Content-Type") || "application/json",
          "User-Agent": "CF-TTS-Proxy/1.0",
        },
        body: request.method !== "GET" ? request.body : undefined,
      });

      const response = await fetch(backendRequest);

      // Clone response with CORS headers
      const responseHeaders = new Headers(response.headers);
      const cors = corsHeaders(origin);
      for (const [key, value] of Object.entries(cors)) {
        responseHeaders.set(key, value);
      }

      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });
    } catch (err) {
      return new Response(
        JSON.stringify({ error: "TTS backend unavailable", detail: err.message }),
        {
          status: 502,
          headers: {
            "Content-Type": "application/json",
            ...corsHeaders(origin),
          },
        }
      );
    }
  },
};

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": origin.startsWith("https://purebrain.ai") ? origin : "https://purebrain.ai",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

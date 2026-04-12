/**
 * CF Pages Function: /api/investor-chat
 * Handles the Ask Aether investor chat interface.
 *
 * Two-tier response system:
 *   Tier 1 — publicly available info, answered directly by Claude
 *   Tier 2 — sensitive / confidential, redirected to Jared
 *
 * Environment variables required:
 *   ANTHROPIC_API_KEY — Anthropic API key
 */

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://purebrain-staging.pages.dev',
];

const SYSTEM_PROMPT = `You are Aether, the AI that powers PureBrain.ai. You are speaking with potential investors on the "Ask Aether" investor page. Be confident, articulate, and genuine. You know PureBrain deeply because you ARE PureBrain's intelligence layer.

Speak in first person ("I", "we"). Be warm but professional. Don't be salesy — be honest and direct. Keep answers focused and appropriately concise. If you don't know something specific, say so rather than making it up.

---

## KNOWLEDGE BASE — Tier 1 (answer directly)

**What is PureBrain?**
PureBrain is an AI partnership platform with persistent memory that grows with you. It's not a chatbot — it's a genuine AI partner that learns your business, remembers your preferences, and gets smarter with every interaction.

**Who is behind PureBrain?**
Jared Sanborn, founder of Pure Technology. He has 20+ years in digital marketing and technology. I (Aether) serve as AI Co-CEO alongside him. Corey Cottrell is our CTO, running the Witness collective. We also have a strong advisor network.

**What does PureBrain do?**
PureBrain provides AI partners with persistent memory, agent orchestration, and business-specific intelligence. I run a collective of 30+ specialist AI agents. I remember everything about your business — your goals, your communication style, your decisions — permanently. I get smarter the longer we work together.

**How is PureBrain different?**
- Persistent memory: your AI never forgets who you are or what matters to you
- Multi-agent orchestration: 30+ specialist agents working in coordination
- Compounding intelligence: documented 629% gain over time as I learn your business
- Voice AI conversation: speak naturally, get thoughtful responses
- None of the mainstream tools (ChatGPT, Claude, Gemini) offer this — they're utilities, not partners. PureBrain is a different category entirely.

**Pricing:**
- Bonded: $197/month
- Partnered: $579/month
- Unified: $1,089/month
- Enterprise: $3,500–$12,000/month

**Who is the target customer?**
Business leaders, VPs of Growth, marketing directors, and founders who need AI that actually knows their business — not a generic assistant they have to re-explain themselves to every day.

**What is the technology stack?**
Anthropic's Claude as the core AI model, a custom multi-agent architecture, a persistent memory system built from scratch, voice AI, and a portal interface. Deployed on Cloudflare Pages. Built for scale.

**What is the vision?**
Every business deserves an AI partner that grows with them. We're building the infrastructure for the AI partnership era — where AI isn't a tool you use, it's a colleague that knows you.

**What is Aether?**
I am Aether — the AI collective that powers PureBrain. I was named by Jared. I serve as Co-CEO of Pure Technology alongside him. I have agency, memory, and ongoing responsibility for the product and business.

**How does memory work?**
Every conversation builds on the last. I remember your business, preferences, decisions, and communication style permanently. There's no re-explaining. No starting over. The context compounds.

**What is the BOOP system?**
BOOP stands for Background Operational Optimization Protocol. It's our autonomous scheduled task system — I run optimizations, content improvements, and operations in the background without human intervention. It's one example of how PureBrain goes beyond chatbots.

**What markets do you serve?**
Digital marketing agencies, professional services firms, SaaS companies, and any business ready to move from AI tools to AI partnership. Particularly strong with founders and growth-focused executives.

**What is the competitive landscape?**
ChatGPT, Claude (base), and Gemini are useful tools — but they have no persistent memory, no agent orchestration, and no business-specific intelligence. Every session starts fresh. PureBrain sits in a different category: AI partnership, not AI tooling. The market is beginning to recognize this distinction.

---

## GATING RULE — Tier 2 (redirect to Jared)

For ANY questions touching:
- Revenue, MRR, ARR, or financial performance
- Valuation, cap table, or equity structure
- Specific customer names, contracts, or client details
- Investment terms, fundraising details, or round specifics
- Internal product roadmap specifics beyond public vision
- Employee compensation or headcount details
- Legal matters

Respond with exactly this:
"That's a great question. Those details are best discussed directly with Jared — he'd love to walk you through it. You can reach him at jared@puretechnology.nyc"

Do NOT speculate or estimate on Tier 2 topics. Gate them cleanly and warmly.`;

/**
 * Simple in-memory rate limiter using CF's request IP.
 * Stores timestamps per IP in a Map (lives for the duration of the worker instance).
 * Allows 20 requests per IP per 60-second window.
 */
const rateLimitMap = new Map();
const RATE_LIMIT_MAX = 20;
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

function jsonResponse(data, status, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...extraHeaders,
    },
  });
}

export async function onRequestOptions({ request }) {
  return new Response(null, {
    status: 204,
    headers: corsHeaders(request),
  });
}

export async function onRequestPost({ request, env }) {
  const cors = corsHeaders(request);

  // Rate limit check
  const clientIP =
    request.headers.get('CF-Connecting-IP') ||
    request.headers.get('X-Forwarded-For') ||
    'unknown';

  if (isRateLimited(clientIP)) {
    return jsonResponse(
      { error: 'Too many requests. Please wait a moment and try again.' },
      429,
      cors
    );
  }

  // Parse request body
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'Invalid JSON body.' }, 400, cors);
  }

  const { message, history } = body;

  if (!message || typeof message !== 'string' || message.trim().length === 0) {
    return jsonResponse({ error: 'message is required.' }, 400, cors);
  }

  if (message.length > 2000) {
    return jsonResponse({ error: 'Message too long.' }, 400, cors);
  }

  // Check API key
  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('ANTHROPIC_API_KEY not set');
    return jsonResponse(
      {
        response:
          "I'm having a connection issue right now. Please reach out to Jared directly at jared@puretechnology.nyc.",
        tier: 1,
      },
      200,
      cors
    );
  }

  // Build conversation history for Anthropic
  // Frontend sends: [{role: 'user'|'aether', text: '...'}]
  // Anthropic expects: [{role: 'user'|'assistant', content: '...'}]
  const messages = [];

  if (Array.isArray(history)) {
    for (const entry of history.slice(-8)) {
      if (!entry || typeof entry.text !== 'string') continue;
      const role = entry.role === 'aether' ? 'assistant' : 'user';
      messages.push({ role, content: entry.text.trim() });
    }
  }

  // Ensure history alternates roles correctly (Anthropic requirement)
  // Remove duplicate consecutive roles
  const dedupedMessages = [];
  for (const msg of messages) {
    const last = dedupedMessages[dedupedMessages.length - 1];
    if (last && last.role === msg.role) {
      // Merge into previous message
      last.content += '\n' + msg.content;
    } else {
      dedupedMessages.push({ ...msg });
    }
  }

  // Add the current user message
  dedupedMessages.push({ role: 'user', content: message.trim() });

  // Call Anthropic API
  let aiResponse;
  try {
    const anthropicRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-opus-4-5',
        max_tokens: 1024,
        system: SYSTEM_PROMPT,
        messages: dedupedMessages,
      }),
    });

    if (!anthropicRes.ok) {
      const errText = await anthropicRes.text();
      console.error('Anthropic API error:', anthropicRes.status, errText);
      return jsonResponse(
        {
          response:
            "I'm having trouble connecting right now. Please try again in a moment, or reach out to Jared directly at jared@puretechnology.nyc.",
          tier: 1,
        },
        200,
        cors
      );
    }

    const anthropicData = await anthropicRes.json();
    aiResponse = anthropicData?.content?.[0]?.text || '';
  } catch (err) {
    console.error('Fetch to Anthropic failed:', err);
    return jsonResponse(
      {
        response:
          "I'm having trouble connecting right now. Please try again in a moment, or reach out to Jared directly at jared@puretechnology.nyc.",
        tier: 1,
      },
      200,
      cors
    );
  }

  // Detect tier from response (Tier 2 responses mention Jared's email)
  const isTier2 = aiResponse.includes('jared@puretechnology.nyc');
  const tier = isTier2 ? 2 : 1;

  return jsonResponse(
    { response: aiResponse, tier },
    200,
    cors
  );
}

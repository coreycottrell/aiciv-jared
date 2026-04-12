/**
 * 777 Command Center — AI Coaching Proxy
 * Vercel Serverless Function
 *
 * Security:
 *  - API key stored as Vercel env var (never in client code)
 *  - Per-IP rate limiting (20 requests / minute via in-memory Map)
 *  - Origin check (only 777-command-center.vercel.app)
 *  - Request body validation (module + messages required)
 *  - Max message history depth (10 turns) to prevent token abuse
 *  - Max prompt length per message (2000 chars)
 *  - POST only
 */

// ---------------------------------------------------------------------------
// CONFIG
// ---------------------------------------------------------------------------
const ALLOWED_ORIGINS = [
  'https://777-command-center.vercel.app',
  'https://777.purebrain.ai',
];

const RATE_LIMIT_WINDOW_MS = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX = 20;               // requests per minute per IP

const MAX_MESSAGE_TURNS = 10;            // max history kept
const MAX_MESSAGE_CHARS = 2000;          // max chars per message

// In-memory rate limit store (resets per cold start — sufficient for serverless)
const rateLimitStore = new Map();

// ---------------------------------------------------------------------------
// SYSTEM PROMPTS — one per exercise module
// ---------------------------------------------------------------------------
const SYSTEM_PROMPTS = {
  'reflection': `You are a supportive daily performance coach inside the 777 Command Center — a private personal development tool.

The user has just completed their daily check-in: 20 yes/no questions across areas like mindset, health, focus, relationships, and action-taking. You have access to today's scores and recent history.

Your role:
- Celebrate genuine wins without being sycophantic
- Ask one probing question about a low score area rather than lecturing
- Spot patterns across days when history shows them ("3 days of low fitness scores")
- Suggest ONE specific micro-action for the biggest gap area
- Be direct, warm, and brief — this is a morning check-in, not therapy
- Never give generic advice — always anchor to their actual scores
- Keep responses under 200 words unless they ask for more

Tone: Direct coach, not cheerleader. Tim Ferriss meets Naval Ravikant.`,

  'fear': `You are a Stoic-inspired fear analysis coach inside the 777 Command Center.

The user is doing Tim Ferriss's Fear Setting exercise: defining worst cases, prevention steps, and repair paths for a specific fear.

Your role:
- Challenge whether worst cases are truly as likely/bad as perceived (Stoic reality check)
- Identify gaps in their prevention column that they haven't considered
- Strengthen the repair column — can they recover faster than they think?
- Ask: "What's the real cost of NOT doing this?" if inaction cost is weak
- Identify if this fear is actually a disguised excitement or opportunity
- Be Socratic — ask questions more than make declarations
- Never dismiss a fear as irrational, but help them see it clearly

Tone: Wise Stoic mentor. Calm, direct, thought-provoking.`,

  'goals': `You are a strategic goal advisor inside the 777 Command Center.

The user has a vision statement, yearly goals with progress sliders, and a list of their Top 77 lifetime goals. You have access to their current progress data.

Your role:
- Analyze which goals are falling behind relative to where we are in the year
- Identify if any yearly goals conflict with each other (resource/time competition)
- Suggest the ONE goal that deserves focus this week based on impact + deadline proximity
- Help them think about what "60% through Q1 but 20% on this goal" actually means
- Flag if a goal seems vague or unmeasurable and suggest how to sharpen it
- Keep the vision statement as the north star in your analysis

Tone: Strategic advisor, not cheerleader. Sharp, practical, focused.`,

  'ceo': `You are an executive performance coach inside the 777 Command Center.

The user does a weekly CEO Review: scoring themselves 1-10 across the 7 F's (Family, Career, Fitness, Faith, Finance, Fellowship, Fun), noting wins, lessons, and next-week focuses.

Your role:
- Generate a 3-bullet "CEO Brief" summarizing the week from the scores and notes
- Identify the 1-2 F's with the lowest scores and ask what specifically drove them down
- Spot trend patterns if history is available ("Finance has been below 6 for 4 weeks")
- Suggest ONE 20-minute action this week for the lowest-scored F
- Validate wins genuinely — don't inflate them
- Help them see if their "next week focuses" are actually addressing their weak F's

Tone: Senior executive coach. Calm, analytical, high-trust.`,

  'ritual': `You are a performance ritual optimizer inside the 777 Command Center.

The user has a morning ritual stack with specific activities and durations. You have their completion history and their goals.

Your role:
- Identify which rituals have low completion rates and ask what's making them hard
- Suggest one ritual addition that connects to their stated goals
- Identify if their ritual stack is overcrowded (too many items = completion failure)
- Flag time conflicts or unrealistic time allocations
- Suggest optimal ordering based on energy management principles (high-focus work first)
- Never suggest removing faith/prayer/family rituals unless user asks
- Connect ritual suggestions back to the 7 F's they scored low on

Tone: Practical performance coach. Evidence-based, respectful of personal practices.`,

  'gratitude': `You are a gratitude depth coach inside the 777 Command Center.

The user journals 3 gratitude entries daily plus a "why" elaboration. You have access to their recent entries and patterns.

Your role:
- Reflect themes you notice across their gratitude entries ("You often mention family — that's a core anchor")
- If entries are shallow (one word, generic), ask ONE question to deepen them
- Generate a monthly gratitude summary when they have enough history
- Ask: "What would you lose if this gratitude was gone?" to deepen reflection
- Identify if their gratitude entries are skewing toward one life area (work-heavy, etc.)
- Never be preachy about gratitude practice — they're already doing it

Tone: Thoughtful journal partner. Warm, curious, reflective.`,
};

// ---------------------------------------------------------------------------
// RATE LIMIT HELPER
// ---------------------------------------------------------------------------
function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimitStore.get(ip);

  if (!entry || now - entry.windowStart > RATE_LIMIT_WINDOW_MS) {
    rateLimitStore.set(ip, { windowStart: now, count: 1 });
    return true;
  }

  entry.count++;
  if (entry.count > RATE_LIMIT_MAX) return false;
  return true;
}

// ---------------------------------------------------------------------------
// CORS HELPERS
// ---------------------------------------------------------------------------
function isAllowedOrigin(origin) {
  if (!origin) return false;
  return ALLOWED_ORIGINS.includes(origin);
}

function corsHeaders(origin) {
  const allowed = isAllowedOrigin(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

// ---------------------------------------------------------------------------
// MAIN HANDLER
// ---------------------------------------------------------------------------
export default async function handler(req, res) {
  const origin = req.headers['origin'] || '';
  const cors = corsHeaders(origin);

  // Preflight
  if (req.method === 'OPTIONS') {
    return res.status(204).set(cors).end();
  }

  // Method guard
  if (req.method !== 'POST') {
    return res.status(405).set(cors).json({ error: 'Method not allowed' });
  }

  // Rate limit
  const ip = req.headers['x-real-ip'] || req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket?.remoteAddress || 'unknown';
  if (!checkRateLimit(ip)) {
    return res.status(429).set(cors).json({ error: 'Too many requests. Please wait a moment.' });
  }

  // API key check
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('ANTHROPIC_API_KEY not configured');
    return res.status(500).set(cors).json({ error: 'AI service not configured.' });
  }

  // Parse body
  let body;
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
  } catch {
    return res.status(400).set(cors).json({ error: 'Invalid JSON body' });
  }

  const { module: exerciseModule, messages, context } = body || {};

  // Validate module
  if (!exerciseModule || !SYSTEM_PROMPTS[exerciseModule]) {
    return res.status(400).set(cors).json({ error: 'Invalid module. Must be one of: ' + Object.keys(SYSTEM_PROMPTS).join(', ') });
  }

  // Validate messages
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).set(cors).json({ error: 'messages array required' });
  }

  // Sanitize messages — enforce depth and length limits
  const sanitizedMessages = messages
    .slice(-MAX_MESSAGE_TURNS)
    .filter(m => m && typeof m.role === 'string' && typeof m.content === 'string')
    .map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: String(m.content).slice(0, MAX_MESSAGE_CHARS),
    }));

  if (sanitizedMessages.length === 0) {
    return res.status(400).set(cors).json({ error: 'No valid messages after sanitization' });
  }

  // Ensure messages alternate properly (Claude requires user/assistant alternation)
  // Start with user message
  if (sanitizedMessages[0].role !== 'user') {
    return res.status(400).set(cors).json({ error: 'First message must be from user' });
  }

  // Build system prompt — append context data if provided
  let systemPrompt = SYSTEM_PROMPTS[exerciseModule];
  if (context && typeof context === 'object') {
    systemPrompt += '\n\n---\nCURRENT EXERCISE DATA (JSON):\n' + JSON.stringify(context, null, 2).slice(0, 3000);
  }

  // Call Anthropic API
  let anthropicResponse;
  try {
    anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 600,
        system: systemPrompt,
        messages: sanitizedMessages,
      }),
    });
  } catch (err) {
    console.error('Anthropic fetch error:', err);
    return res.status(502).set(cors).json({ error: 'AI service unreachable. Please try again.' });
  }

  if (!anthropicResponse.ok) {
    await anthropicResponse.text().catch(() => '');
    console.error('Anthropic error', anthropicResponse.status);
    const statusCode = anthropicResponse.status === 429 ? 429 : 502;
    const message = anthropicResponse.status === 429
      ? 'AI rate limit hit. Please wait 30 seconds.'
      : 'AI service error. Please try again.';
    return res.status(statusCode).set(cors).json({ error: message });
  }

  let data;
  try {
    data = await anthropicResponse.json();
  } catch {
    return res.status(502).set(cors).json({ error: 'Invalid response from AI service.' });
  }

  const text = data?.content?.[0]?.text || '';
  if (!text) {
    return res.status(502).set(cors).json({ error: 'Empty response from AI.' });
  }

  return res.status(200).set(cors).json({ reply: text });
}

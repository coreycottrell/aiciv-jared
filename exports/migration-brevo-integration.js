/**
 * PureBrain Migration Portal — Brevo Integration Module
 *
 * Handles all Brevo API interactions for the AI Migration Portal.
 * Three modules:
 *   1. saveMigrationIntent    — Called on Exodus quiz completion
 *   2. saveMigrationProfile   — Called after ChatGPT/Claude export is processed
 *   3. triggerMigrationDrip   — Adds contact to competitor-specific automation
 *
 * Author: full-stack-developer
 * Date: 2026-02-23
 * Spec: docs/from-telegram/ai-migration-portal-spec.md (Sections 2, 5)
 */

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BREVO_BASE_URL = 'https://api.brevo.com/v3';

/**
 * Get Brevo API key from environment.
 *
 * In a browser context (Exodus landing page JS), this must be injected
 * server-side or via a backend proxy — never expose the raw key client-side
 * in production. In a Node.js/server context, use process.env.BREVO_API_KEY.
 *
 * For the migration portal (which runs server-side), use:
 *   const BREVO_API_KEY = process.env.BREVO_API_KEY;
 */
function getBrevoApiKey() {
  // Server-side (Node.js / Vercel / Next.js API route)
  if (typeof process !== 'undefined' && process.env && process.env.BREVO_API_KEY) {
    return process.env.BREVO_API_KEY;
  }
  // Fallback: injected as window variable from PHP/WP for client-side usage
  if (typeof window !== 'undefined' && window.__PUREBRAIN_CONFIG && window.__PUREBRAIN_CONFIG.brevoApiKey) {
    return window.__PUREBRAIN_CONFIG.brevoApiKey;
  }
  throw new Error('BREVO_API_KEY not available. Check environment configuration.');
}

// Brevo List IDs (matches existing PureBrain infrastructure)
// MIGRATION_LEADS ID confirmed by setup_brevo_migration_attributes.py on 2026-02-23
const BREVO_LISTS = {
  NEURAL_FEED: 3,          // The Neural Feed — blog subscribers
  ENTERPRISE_LEADS: 4,     // Enterprise Leads
  PB_CUSTOMERS: 8,         // PureBrain Customers (post-purchase)
  MIGRATION_LEADS: 11,     // PureBrain Migration Leads (created 2026-02-23)
};

// ---------------------------------------------------------------------------
// Internal Utilities
// ---------------------------------------------------------------------------

/**
 * Build standard Brevo API request headers.
 * @returns {Object} Headers object
 */
function brevoHeaders() {
  return {
    'api-key': getBrevoApiKey(),
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
}

/**
 * Make a Brevo API request with error handling and retry logic.
 *
 * @param {string} method  - HTTP method (GET, POST, PUT, DELETE)
 * @param {string} path    - API path (e.g. '/contacts')
 * @param {Object} [body]  - Request body (for POST/PUT)
 * @param {number} [retries=2] - Number of retries on 5xx errors
 * @returns {Promise<Object>} Parsed response body
 * @throws {Error} On 4xx (non-retryable) or exhausted retries
 */
async function brevoRequest(method, path, body = null, retries = 2) {
  const url = `${BREVO_BASE_URL}${path}`;
  const options = {
    method,
    headers: brevoHeaders(),
  };

  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  let lastError = null;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, options);

      // 204 No Content is success (contact update)
      if (response.status === 204) {
        return { success: true, status: 204 };
      }

      const responseText = await response.text();
      let responseData = {};
      try {
        responseData = JSON.parse(responseText);
      } catch (_) {
        responseData = { raw: responseText };
      }

      // 201 = created, 200 = ok
      if (response.ok) {
        return { success: true, status: response.status, data: responseData };
      }

      // 429 = rate limited — wait and retry
      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('Retry-After') || '2', 10);
        await sleep(retryAfter * 1000);
        lastError = new Error(`Rate limited (429). Retry after ${retryAfter}s.`);
        continue;
      }

      // 5xx — retry
      if (response.status >= 500 && attempt < retries) {
        await sleep(1000 * (attempt + 1));
        lastError = new Error(`Brevo server error ${response.status}: ${responseText}`);
        continue;
      }

      // 4xx (non-429) — not retryable
      const err = new Error(`Brevo API error ${response.status}: ${responseText}`);
      err.status = response.status;
      err.responseData = responseData;
      throw err;

    } catch (err) {
      // Re-throw intentional API errors
      if (err.status) throw err;
      // Network error — retry
      lastError = err;
      if (attempt < retries) {
        await sleep(1000 * (attempt + 1));
      }
    }
  }

  throw lastError || new Error('Brevo request failed after retries');
}

/**
 * Simple sleep utility.
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Normalize a competitor string to a canonical slug.
 * @param {string} competitor - Raw competitor value from URL/quiz
 * @returns {string} Canonical slug (e.g. 'chatgpt', 'claude', 'gemini')
 */
function normalizeCompetitor(competitor) {
  if (!competitor) return 'unknown';
  const raw = competitor.toLowerCase().trim();
  const map = {
    'chatgpt': 'chatgpt',
    'openai': 'chatgpt',
    'gpt-4': 'chatgpt',
    'claude': 'claude',
    'anthropic': 'claude',
    'gemini': 'gemini',
    'google': 'gemini',
    'bard': 'gemini',
    'perplexity': 'perplexity',
    'midjourney': 'midjourney',
    'copilot': 'copilot',
    'microsoft': 'copilot',
  };
  return map[raw] || raw;
}

/**
 * Serialise an array value for storage as a Brevo text attribute.
 * Brevo text fields don't support arrays natively, so we join with commas.
 * @param {string|string[]} value
 * @returns {string}
 */
function serializeArray(value) {
  if (Array.isArray(value)) {
    return value.join(',');
  }
  return String(value || '');
}

// ---------------------------------------------------------------------------
// Module 1: Save Migration Intent (Exodus Quiz Completion)
// ---------------------------------------------------------------------------

/**
 * Save migration intent data to Brevo when a user completes the Exodus quiz.
 *
 * Creates or updates the Brevo contact with:
 *   - All migration intent attributes
 *   - Added to List 3 (Neural Feed) AND List 9 (Migration Leads)
 *   - Tags: migration-intent, from-[competitor]
 *
 * Called from: Exodus landing page JS (server-side API route recommended)
 *
 * @param {Object} data - Quiz completion data
 * @param {string} data.email                    - User's email address (required)
 * @param {string} data.competitor               - Competitor slug from URL (e.g. 'chatgpt')
 * @param {string|string[]} data.primary_use_cases - Selected use cases (multi-select)
 * @param {string} data.usage_frequency          - How often they used the tool
 * @param {boolean} data.had_custom_config       - Had custom instructions/templates
 * @param {string} data.main_frustration         - Primary frustration that drove switch
 * @param {string} [data.first_name]             - Optional first name
 * @param {string} [data.utm_source]             - UTM tracking
 * @param {string} [data.utm_campaign]           - UTM campaign
 * @param {number} [data.quiz_score]             - Quiz score if calculated
 * @returns {Promise<Object>} Result with success flag and Brevo response
 */
async function saveMigrationIntent(data) {
  const {
    email,
    competitor,
    primary_use_cases,
    usage_frequency,
    had_custom_config,
    main_frustration,
    first_name,
    utm_source,
    utm_campaign,
    quiz_score,
  } = data;

  if (!email) {
    throw new Error('saveMigrationIntent: email is required');
  }

  const competitorSlug = normalizeCompetitor(competitor);

  // Build contact attributes — only include non-empty values
  const attributes = {};

  if (competitorSlug) {
    attributes['COMPETITOR'] = competitorSlug;
  }
  if (primary_use_cases) {
    attributes['PRIMARY_USE_CASES'] = serializeArray(primary_use_cases);
  }
  if (usage_frequency) {
    attributes['USAGE_FREQUENCY'] = String(usage_frequency);
  }
  if (had_custom_config !== undefined && had_custom_config !== null) {
    // Brevo boolean attributes stored as true/false
    attributes['HAD_CUSTOM_CONFIG'] = Boolean(had_custom_config);
  }
  if (main_frustration) {
    attributes['MAIN_FRUSTRATION'] = String(main_frustration);
  }
  // Default migration status to 'not_started' on first contact creation
  attributes['MIGRATION_STATUS'] = 'not_started';

  if (first_name) {
    attributes['FIRSTNAME'] = String(first_name);
  }

  // Build tags: migration-intent + from-[competitor]
  const tags = ['migration-intent'];
  if (competitorSlug && competitorSlug !== 'unknown') {
    tags.push(`from-${competitorSlug}`);
  }

  // List IDs to add contact to
  // List 3 = Neural Feed (all migration leads get nurture sequence)
  // List 9 = Migration Leads (dedicated migration tracking)
  const listIds = [BREVO_LISTS.NEURAL_FEED, BREVO_LISTS.MIGRATION_LEADS];

  // Upsert contact via POST /contacts with updateEnabled: true
  const contactPayload = {
    email,
    attributes,
    listIds,
    updateEnabled: true,  // Critical: upsert not create-only
  };

  let result;
  try {
    result = await brevoRequest('POST', '/contacts', contactPayload);
  } catch (err) {
    // Log failure but return structured error (don't break the quiz flow)
    console.error('[migration-brevo] saveMigrationIntent failed:', err.message, {
      email,
      competitor: competitorSlug,
    });
    return {
      success: false,
      error: err.message,
      email,
      competitor: competitorSlug,
    };
  }

  // Add tags after upsert — Brevo tags via contact update
  // Note: Brevo v3 supports tags as part of attributes in some plans.
  // If your Brevo plan supports it, add TAGS attribute; otherwise use list segmentation.
  if (tags.length > 0) {
    try {
      await brevoRequest('PUT', `/contacts/${encodeURIComponent(email)}`, {
        attributes: {
          ...attributes,
          TAGS: tags.join(','),
        },
      });
    } catch (tagErr) {
      // Tag update failure is non-critical — log and continue
      console.warn('[migration-brevo] Tag update failed (non-critical):', tagErr.message);
    }
  }

  console.log('[migration-brevo] saveMigrationIntent success:', {
    email,
    competitor: competitorSlug,
    lists: listIds,
    tags,
    brevoStatus: result.status,
  });

  return {
    success: true,
    email,
    competitor: competitorSlug,
    lists: listIds,
    tags,
    brevoStatus: result.status,
    ...(quiz_score !== undefined ? { quiz_score } : {}),
    ...(utm_source ? { utm_source } : {}),
    ...(utm_campaign ? { utm_campaign } : {}),
  };
}

// ---------------------------------------------------------------------------
// Module 2: Save Migration Profile (After Export Processing)
// ---------------------------------------------------------------------------

/**
 * Update Brevo contact with the processed migration profile after the portal
 * has analysed the user's ChatGPT/Claude export file.
 *
 * Called from: Portal backend — after Step 3 (PureBrain Learns You) completes.
 *
 * @param {string} email - User's email address
 * @param {Object} profile - Processed migration profile
 * @param {string[]} profile.top_topics          - Top N topics extracted (e.g. ['market analysis', 'copywriting'])
 * @param {string}   profile.communication_style - Detected style (e.g. 'direct, bullet points')
 * @param {number}   profile.conversation_count  - Total conversations imported
 * @param {Object}   profile.date_range          - { start: ISO, end: ISO }
 * @param {string}   [profile.custom_instructions_summary] - Preview of custom instructions
 * @param {string}   [profile.preferred_answer_format]     - 'bullet' | 'prose' | 'mixed'
 * @returns {Promise<Object>} Result with success flag
 */
async function saveMigrationProfile(email, profile) {
  if (!email) {
    throw new Error('saveMigrationProfile: email is required');
  }
  if (!profile || typeof profile !== 'object') {
    throw new Error('saveMigrationProfile: profile object is required');
  }

  const {
    top_topics,
    communication_style,
    conversation_count,
    date_range,
    custom_instructions_summary,
    preferred_answer_format,
  } = profile;

  // Serialise the full profile as JSON string for MIGRATION_PROFILE attribute
  // This lets the portal retrieve the full structured data later
  const profileJson = JSON.stringify({
    top_topics: top_topics || [],
    communication_style: communication_style || '',
    conversation_count: conversation_count || 0,
    date_range: date_range || null,
    custom_instructions_summary: custom_instructions_summary || '',
    preferred_answer_format: preferred_answer_format || 'mixed',
    processed_at: new Date().toISOString(),
  });

  // Build the attribute update payload
  const attributes = {
    MIGRATION_STATUS: 'complete',
    MIGRATION_PROFILE: profileJson,
  };

  // Store conversation count as dedicated number field for segmentation
  if (typeof conversation_count === 'number') {
    attributes['CONVERSATION_COUNT'] = conversation_count;
  }

  // Store top topics as comma-separated text for easy segmentation
  if (Array.isArray(top_topics) && top_topics.length > 0) {
    attributes['TOP_TOPICS'] = top_topics.slice(0, 5).join(',');
  }

  try {
    await brevoRequest('PUT', `/contacts/${encodeURIComponent(email)}`, { attributes });
  } catch (err) {
    console.error('[migration-brevo] saveMigrationProfile failed:', err.message, { email });
    return {
      success: false,
      error: err.message,
      email,
    };
  }

  console.log('[migration-brevo] saveMigrationProfile success:', {
    email,
    conversation_count,
    top_topics_count: Array.isArray(top_topics) ? top_topics.length : 0,
    migration_status: 'complete',
  });

  return {
    success: true,
    email,
    migration_status: 'complete',
    conversation_count,
    top_topics: top_topics || [],
    profile_stored: true,
  };
}

// ---------------------------------------------------------------------------
// Module 3: Trigger Competitor-Specific Drip Sequence
// ---------------------------------------------------------------------------

/**
 * Add a contact to the competitor-specific Brevo automation workflow.
 *
 * PureBrain maintains separate drip sequences per competitor so emails can
 * reference specific pain points (e.g. ChatGPT users hear about memory,
 * Gemini users hear about Google integration context).
 *
 * Implementation note: Brevo has no REST API for automation workflows
 * (confirmed through testing — see memory 2026-02-21--brevo-automation-workflow-setup.md).
 * The trigger mechanism works by adding the contact to a competitor-specific
 * list that has an automation workflow attached with trigger "Contact added to list".
 *
 * Required pre-setup: Create one list + one automation per competitor in Brevo UI.
 * Use setup_brevo_migration_attributes.py to create the lists.
 *
 * @param {string} email      - User's email address
 * @param {string} competitor - Competitor slug (e.g. 'chatgpt', 'claude', 'gemini')
 * @returns {Promise<Object>} Result with success flag and list added to
 */
async function triggerMigrationDrip(email, competitor) {
  if (!email) {
    throw new Error('triggerMigrationDrip: email is required');
  }

  const competitorSlug = normalizeCompetitor(competitor);

  // Map competitors to their dedicated drip list IDs.
  // These lists were created by setup_brevo_migration_attributes.py on 2026-02-23.
  // Each list requires a Brevo automation workflow with trigger "Contact added to list".
  // IDs sourced from: config/migration_brevo_config.json
  const COMPETITOR_DRIP_LISTS = {
    chatgpt: 12,        // PureBrain Migration — ChatGPT
    claude: 13,         // PureBrain Migration — Claude
    gemini: 14,         // PureBrain Migration — Gemini
    perplexity: 15,     // PureBrain Migration — Perplexity
    midjourney: 16,     // PureBrain Migration — Midjourney
    copilot: 17,        // PureBrain Migration — Copilot
    // fallback for unrecognised competitors:
    unknown: 18,        // PureBrain Migration — Other
  };

  // Read list IDs from environment if available (set after running setup script)
  // This allows configuration without code changes after initial setup.
  if (typeof process !== 'undefined' && process.env) {
    COMPETITOR_DRIP_LISTS.chatgpt = parseInt(process.env.BREVO_DRIP_LIST_CHATGPT || '0', 10) || null;
    COMPETITOR_DRIP_LISTS.claude = parseInt(process.env.BREVO_DRIP_LIST_CLAUDE || '0', 10) || null;
    COMPETITOR_DRIP_LISTS.gemini = parseInt(process.env.BREVO_DRIP_LIST_GEMINI || '0', 10) || null;
    COMPETITOR_DRIP_LISTS.perplexity = parseInt(process.env.BREVO_DRIP_LIST_PERPLEXITY || '0', 10) || null;
    COMPETITOR_DRIP_LISTS.midjourney = parseInt(process.env.BREVO_DRIP_LIST_MIDJOURNEY || '0', 10) || null;
    COMPETITOR_DRIP_LISTS.copilot = parseInt(process.env.BREVO_DRIP_LIST_COPILOT || '0', 10) || null;
    COMPETITOR_DRIP_LISTS.unknown = parseInt(process.env.BREVO_DRIP_LIST_UNKNOWN || '0', 10) || null;
  }

  const listId = COMPETITOR_DRIP_LISTS[competitorSlug] || COMPETITOR_DRIP_LISTS.unknown;

  if (!listId) {
    // List IDs not yet configured — log warning, skip gracefully
    // This is expected before the setup script has been run and env vars set.
    console.warn(
      `[migration-brevo] triggerMigrationDrip: No drip list configured for competitor "${competitorSlug}". ` +
      'Run setup_brevo_migration_attributes.py and set BREVO_DRIP_LIST_* env vars.',
    );
    return {
      success: false,
      reason: 'no_list_configured',
      competitor: competitorSlug,
      email,
    };
  }

  // Add contact to the competitor drip list to trigger the automation workflow
  try {
    await brevoRequest('POST', `/contacts/lists/${listId}/contacts/add`, {
      emails: [email],
    });
  } catch (err) {
    console.error('[migration-brevo] triggerMigrationDrip failed:', err.message, {
      email,
      competitor: competitorSlug,
      listId,
    });
    return {
      success: false,
      error: err.message,
      email,
      competitor: competitorSlug,
      listId,
    };
  }

  console.log('[migration-brevo] triggerMigrationDrip success:', {
    email,
    competitor: competitorSlug,
    listId,
  });

  return {
    success: true,
    email,
    competitor: competitorSlug,
    listId,
    drip_triggered: true,
  };
}

// ---------------------------------------------------------------------------
// Composite Helper: Full Exodus Flow (Intent + Drip)
// ---------------------------------------------------------------------------

/**
 * Run the complete Exodus quiz completion flow in one call.
 *
 * Convenience wrapper that:
 *   1. Saves migration intent (creates/updates Brevo contact)
 *   2. Triggers competitor-specific drip sequence
 *
 * Use this on the Exodus landing page on quiz completion.
 *
 * @param {Object} data - Quiz completion data (same shape as saveMigrationIntent)
 * @returns {Promise<Object>} Combined result
 */
async function handleExodusQuizCompletion(data) {
  const intentResult = await saveMigrationIntent(data);

  if (!intentResult.success) {
    return {
      success: false,
      phase: 'intent',
      error: intentResult.error,
      email: data.email,
    };
  }

  const dripResult = await triggerMigrationDrip(data.email, data.competitor);

  return {
    success: intentResult.success,
    intent: intentResult,
    drip: dripResult,
    email: data.email,
    competitor: intentResult.competitor,
  };
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

// CommonJS (Node.js / WordPress plugin / Next.js API routes)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    saveMigrationIntent,
    saveMigrationProfile,
    triggerMigrationDrip,
    handleExodusQuizCompletion,
    // Internal utilities exposed for testing
    _normalizeCompetitor: normalizeCompetitor,
    _serializeArray: serializeArray,
    BREVO_LISTS,
  };
}

// ES Module (modern bundlers / Next.js client components)
// Uncomment if using ES modules:
// export {
//   saveMigrationIntent,
//   saveMigrationProfile,
//   triggerMigrationDrip,
//   handleExodusQuizCompletion,
// };

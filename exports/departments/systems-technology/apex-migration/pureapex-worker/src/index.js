/**
 * PureApex — Pure Technology Sales Intelligence
 * Cloudflare Worker + D1 (migrated from Python/Starlette)
 *
 * Bindings: DB (D1), SESSIONS (KV)
 * Secrets: LINKEDIN_CLIENT_SECRET
 */

import { HTML_PAGE } from './html.js';
import { handleLinkedIn } from './linkedin.js';
import { handleProspectPages } from './prospects.js';
import { STATIC_FILES } from './static-files.js';

// ─── Constants ───────────────────────────────────────────────────────
const VALID_TYPES = ['CPG', 'Gaming', 'Enterprise', 'PureBrain'];
const VALID_GEOGRAPHIES = ['NA', 'EMEA', 'APAC', 'MENA', 'LATAM', 'Global'];
const VALID_STAGES = [
  'Suspect', 'Pipeline', 'Qualified', 'Proposal Submitted',
  'Proposal Finalised', 'Sponsor Commitment', 'Proposal Accepted',
  'Closed Won', 'Closed Lost'
];

const SEED_USERS = [
  { username: 'jsmith', display_name: 'John Smith (JB)', role: 'VP Sales', password: 'anchor2026' },
  { username: 'jsanborn', display_name: 'Jared Sanborn', role: 'CEO', password: 'aether2026' },
  { username: 'nolson', display_name: 'Nate Olson', role: 'President PMG', password: 'lyra2026' },
  { username: 'pbliss', display_name: 'Philip Bliss', role: 'CMO', password: 'clarity2026' },
  { username: 'anchor', display_name: 'Anchor (AI)', role: 'AI Sales Partner', password: 'pipeline_api_key_2026' },
];

// ─── Helpers ─────────────────────────────────────────────────────────

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  });
}

function html(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: { 'Content-Type': 'text/html; charset=utf-8', ...headers },
  });
}

function setCookie(name, value, maxAge, opts = {}) {
  const parts = [`${name}=${value}`, `Max-Age=${maxAge}`, 'Path=/', 'HttpOnly', 'SameSite=Lax'];
  if (opts.secure !== false) parts.push('Secure');
  return parts.join('; ');
}

function deleteCookie(name) {
  return `${name}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax; Secure`;
}

function parseCookies(header) {
  const cookies = {};
  if (!header) return cookies;
  for (const pair of header.split(';')) {
    const [k, ...v] = pair.trim().split('=');
    if (k) cookies[k.trim()] = v.join('=').trim();
  }
  return cookies;
}

function nowISO() {
  return new Date().toISOString().replace('T', ' ').split('.')[0];
}

// Password hashing using Web Crypto (replaces bcrypt)
// We use PBKDF2 with SHA-256 since bcrypt is not available in Workers
async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']
  );
  const hash = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    keyMaterial, 256
  );
  const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('');
  const hashHex = Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  return `pbkdf2:${saltHex}:${hashHex}`;
}

async function verifyPassword(password, storedHash) {
  // Support both legacy bcrypt hashes (from migration) and new PBKDF2 hashes
  if (storedHash.startsWith('$2')) {
    // Legacy bcrypt hash - we need to convert on first successful login
    // For now, compare using a simple approach: the migrated data will have
    // PBKDF2 hashes since we re-hash during migration
    return false;
  }

  if (!storedHash.startsWith('pbkdf2:')) return false;

  const [, saltHex, hashHex] = storedHash.split(':');
  const salt = new Uint8Array(saltHex.match(/.{2}/g).map(h => parseInt(h, 16)));
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']
  );
  const hash = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    keyMaterial, 256
  );
  const computedHex = Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  return computedHex === hashHex;
}

// ─── Session Management (KV-backed) ─────────────────────────────────

async function createSession(env, user) {
  const token = crypto.randomUUID() + '-' + crypto.randomUUID();
  const session = {
    username: user.username,
    display_name: user.display_name,
    role: user.role,
  };
  // Store in KV with 24h TTL
  await env.SESSIONS.put(`session:${token}`, JSON.stringify(session), { expirationTtl: 86400 });
  return token;
}

async function getSession(env, request) {
  const cookies = parseCookies(request.headers.get('Cookie'));
  let token = cookies.session_token;

  // Also check Authorization header
  if (!token) {
    const auth = request.headers.get('Authorization') || '';
    if (auth.startsWith('Bearer ')) {
      token = auth.slice(7);
    }
  }

  if (!token) return null;

  const data = await env.SESSIONS.get(`session:${token}`);
  if (!data) return null;

  try {
    return JSON.parse(data);
  } catch {
    return null;
  }
}

async function deleteSession(env, request) {
  const cookies = parseCookies(request.headers.get('Cookie'));
  const token = cookies.session_token;
  if (token) {
    await env.SESSIONS.delete(`session:${token}`);
  }
}

// ─── Database Init ───────────────────────────────────────────────────

async function ensureUsersSeeded(env) {
  const { results } = await env.DB.prepare('SELECT COUNT(*) as cnt FROM users').all();
  if (results[0].cnt > 0) return;

  for (const u of SEED_USERS) {
    const pw_hash = await hashPassword(u.password);
    await env.DB.prepare(
      'INSERT INTO users (username, display_name, role, password_hash) VALUES (?, ?, ?, ?)'
    ).bind(u.username, u.display_name, u.role, pw_hash).run();
  }
}

// ─── Route: Login ────────────────────────────────────────────────────

async function apiLogin(request, env) {
  let body;
  try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

  const username = (body.username || '').trim().toLowerCase();
  const password = body.password || '';
  if (!username || !password) return json({ error: 'Username and password required' }, 400);

  const { results } = await env.DB.prepare(
    'SELECT id, username, display_name, role, password_hash FROM users WHERE username = ?'
  ).bind(username).all();

  if (results.length === 0) return json({ error: 'Invalid credentials' }, 401);

  const user = results[0];
  const valid = await verifyPassword(password, user.password_hash);
  if (!valid) return json({ error: 'Invalid credentials' }, 401);

  const token = await createSession(env, user);

  const resp = json({
    ok: true,
    user: { username: user.username, display_name: user.display_name, role: user.role },
  });

  // Clone response to add cookie
  const newResp = new Response(resp.body, resp);
  newResp.headers.append('Set-Cookie', setCookie('session_token', token, 86400));
  return newResp;
}

// ─── Route: Logout ───────────────────────────────────────────────────

async function apiLogout(request, env) {
  await deleteSession(env, request);
  const resp = json({ ok: true });
  const newResp = new Response(resp.body, resp);
  newResp.headers.append('Set-Cookie', deleteCookie('session_token'));
  return newResp;
}

// ─── Route: Me ───────────────────────────────────────────────────────

async function apiMe(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);
  return json({
    username: session.username,
    display_name: session.display_name,
    role: session.role,
  });
}

// ─── Route: List Opportunities ───────────────────────────────────────

async function apiListOpportunities(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const url = new URL(request.url);
  const conditions = [];
  const args = [];

  for (const field of ['owner', 'type', 'geography', 'stage']) {
    const val = url.searchParams.get(field);
    if (val) { conditions.push(`${field} = ?`); args.push(val); }
  }

  const vertical = url.searchParams.get('vertical');
  if (vertical) { conditions.push('vertical LIKE ?'); args.push(`%${vertical}%`); }

  const search = url.searchParams.get('search');
  if (search) {
    conditions.push('(company LIKE ? OR contact_name LIKE ? OR notes LIKE ?)');
    args.push(`%${search}%`, `%${search}%`, `%${search}%`);
  }

  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

  let sort = url.searchParams.get('sort') || 'updated_at';
  let dir = (url.searchParams.get('dir') || 'DESC').toUpperCase();
  const allowedSorts = ['company', 'estimated_value', 'stage', 'owner', 'type', 'geography', 'updated_at', 'created_at'];
  if (!allowedSorts.includes(sort)) sort = 'updated_at';
  if (!['ASC', 'DESC'].includes(dir)) dir = 'DESC';

  const stmt = env.DB.prepare(`SELECT * FROM opportunities ${where} ORDER BY ${sort} ${dir}`);
  const bound = args.length ? stmt.bind(...args) : stmt;
  const { results } = await bound.all();

  return json(results);
}

// ─── Route: Get Opportunity ──────────────────────────────────────────

async function apiGetOpportunity(request, env, id) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const { results: opps } = await env.DB.prepare(
    'SELECT * FROM opportunities WHERE id = ?'
  ).bind(id).all();

  if (opps.length === 0) return json({ error: 'Not found' }, 404);

  const result = { ...opps[0] };

  const { results: activities } = await env.DB.prepare(
    'SELECT * FROM activity_log WHERE opportunity_id = ? ORDER BY created_at DESC'
  ).bind(id).all();

  const { results: notes } = await env.DB.prepare(
    'SELECT * FROM meeting_notes WHERE opportunity_id = ? ORDER BY created_at DESC'
  ).bind(id).all();

  result.activity = activities;
  result.meeting_notes = notes;

  return json(result);
}

// ─── Route: Create Opportunity ───────────────────────────────────────

async function apiCreateOpportunity(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

  const company = (body.company || '').trim();
  if (!company) return json({ error: 'Company name is required' }, 400);

  const oppType = body.type || '';
  if (oppType && !VALID_TYPES.includes(oppType))
    return json({ error: `Invalid type. Must be one of: ${VALID_TYPES.join(', ')}` }, 400);

  const geography = body.geography || '';
  if (geography && !VALID_GEOGRAPHIES.includes(geography))
    return json({ error: `Invalid geography. Must be one of: ${VALID_GEOGRAPHIES.join(', ')}` }, 400);

  const stage = body.stage || 'Suspect';
  if (!VALID_STAGES.includes(stage))
    return json({ error: `Invalid stage. Must be one of: ${VALID_STAGES.join(', ')}` }, 400);

  let owner = (body.owner || session.display_name).trim();
  if (!owner) owner = session.display_name;

  const now = nowISO();

  const { meta } = await env.DB.prepare(`
    INSERT INTO opportunities
    (company, contact_name, contact_title, contact_email, contact_linkedin,
     contact_location, type, vertical, geography, stage, playbook_weapon, owner,
     estimated_value, next_action, next_action_date, notes, partner,
     meddpicc_metrics, meddpicc_economic_buyer, meddpicc_decision_criteria,
     meddpicc_decision_process, meddpicc_paper_process, meddpicc_identify_pain,
     meddpicc_champion, meddpicc_competition, emotional_arc, division,
     readiness_pnl_pain, readiness_decision_maker, readiness_competitor,
     readiness_unique_angle, readiness_proof, stage_changed_at, created_by,
     created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    company,
    body.contact_name || '',
    body.contact_title || '',
    body.contact_email || '',
    body.contact_linkedin || '',
    body.contact_location || '',
    oppType || null,
    body.vertical || '',
    geography || null,
    stage,
    body.playbook_weapon || '',
    owner,
    parseFloat(body.estimated_value || 0),
    body.next_action || '',
    body.next_action_date || '',
    body.notes || '',
    body.partner || '',
    body.meddpicc_metrics || '',
    body.meddpicc_economic_buyer || '',
    body.meddpicc_decision_criteria || '',
    body.meddpicc_decision_process || '',
    body.meddpicc_paper_process || '',
    body.meddpicc_identify_pain || '',
    body.meddpicc_champion || '',
    body.meddpicc_competition || '',
    body.emotional_arc || '',
    body.division || '',
    parseInt(body.readiness_pnl_pain || 0),
    parseInt(body.readiness_decision_maker || 0),
    parseInt(body.readiness_competitor || 0),
    parseInt(body.readiness_unique_angle || 0),
    parseInt(body.readiness_proof || 0),
    now,
    session.display_name,
    now,
    now
  ).run();

  const newId = meta.last_row_id;

  // Log activity
  await env.DB.prepare(
    'INSERT INTO activity_log (opportunity_id, action, actor, created_at) VALUES (?, ?, ?, ?)'
  ).bind(newId, `Created opportunity: ${company}`, session.display_name, now).run();

  // Fetch and return created record
  const { results } = await env.DB.prepare('SELECT * FROM opportunities WHERE id = ?').bind(newId).all();
  return json(results[0], 201);
}

// ─── Route: Update Opportunity ───────────────────────────────────────

async function apiUpdateOpportunity(request, env, id) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

  // Fetch existing
  const { results: existing } = await env.DB.prepare(
    'SELECT * FROM opportunities WHERE id = ?'
  ).bind(id).all();

  if (existing.length === 0) return json({ error: 'Not found' }, 404);
  const opp = existing[0];

  // Validate
  const oppType = body.type !== undefined ? body.type : opp.type;
  if (oppType && !VALID_TYPES.includes(oppType))
    return json({ error: `Invalid type` }, 400);

  const geography = body.geography !== undefined ? body.geography : opp.geography;
  if (geography && !VALID_GEOGRAPHIES.includes(geography))
    return json({ error: `Invalid geography` }, 400);

  const stage = body.stage !== undefined ? body.stage : opp.stage;
  if (stage && !VALID_STAGES.includes(stage))
    return json({ error: `Invalid stage` }, 400);

  const now = nowISO();
  const stageChanged = body.stage && body.stage !== opp.stage;

  // Build changes log
  const changes = [];
  for (const field of ['company', 'stage', 'owner', 'type', 'geography', 'estimated_value', 'contact_name', 'partner', 'division']) {
    if (body[field] !== undefined && body[field] !== opp[field]) {
      changes.push(`${field}: ${opp[field] || '(empty)'} -> ${body[field]}`);
    }
  }

  await env.DB.prepare(`
    UPDATE opportunities SET
      company = ?, contact_name = ?, contact_title = ?, contact_email = ?,
      contact_linkedin = ?, contact_location = ?, type = ?, vertical = ?,
      geography = ?, stage = ?, playbook_weapon = ?, owner = ?,
      estimated_value = ?, next_action = ?, next_action_date = ?, notes = ?,
      partner = ?, meddpicc_metrics = ?, meddpicc_economic_buyer = ?,
      meddpicc_decision_criteria = ?, meddpicc_decision_process = ?,
      meddpicc_paper_process = ?, meddpicc_identify_pain = ?,
      meddpicc_champion = ?, meddpicc_competition = ?, emotional_arc = ?,
      division = ?, readiness_pnl_pain = ?, readiness_decision_maker = ?,
      readiness_competitor = ?, readiness_unique_angle = ?, readiness_proof = ?,
      stage_changed_at = ?, updated_at = ?
    WHERE id = ?
  `).bind(
    body.company !== undefined ? body.company : opp.company,
    body.contact_name !== undefined ? body.contact_name : opp.contact_name,
    body.contact_title !== undefined ? body.contact_title : opp.contact_title,
    body.contact_email !== undefined ? body.contact_email : opp.contact_email,
    body.contact_linkedin !== undefined ? body.contact_linkedin : opp.contact_linkedin,
    body.contact_location !== undefined ? body.contact_location : opp.contact_location,
    oppType || null,
    body.vertical !== undefined ? body.vertical : opp.vertical,
    geography || null,
    stage,
    body.playbook_weapon !== undefined ? body.playbook_weapon : opp.playbook_weapon,
    body.owner !== undefined ? body.owner : opp.owner,
    body.estimated_value !== undefined ? parseFloat(body.estimated_value) : opp.estimated_value,
    body.next_action !== undefined ? body.next_action : opp.next_action,
    body.next_action_date !== undefined ? body.next_action_date : opp.next_action_date,
    body.notes !== undefined ? body.notes : opp.notes,
    body.partner !== undefined ? body.partner : opp.partner,
    body.meddpicc_metrics !== undefined ? body.meddpicc_metrics : opp.meddpicc_metrics,
    body.meddpicc_economic_buyer !== undefined ? body.meddpicc_economic_buyer : opp.meddpicc_economic_buyer,
    body.meddpicc_decision_criteria !== undefined ? body.meddpicc_decision_criteria : opp.meddpicc_decision_criteria,
    body.meddpicc_decision_process !== undefined ? body.meddpicc_decision_process : opp.meddpicc_decision_process,
    body.meddpicc_paper_process !== undefined ? body.meddpicc_paper_process : opp.meddpicc_paper_process,
    body.meddpicc_identify_pain !== undefined ? body.meddpicc_identify_pain : opp.meddpicc_identify_pain,
    body.meddpicc_champion !== undefined ? body.meddpicc_champion : opp.meddpicc_champion,
    body.meddpicc_competition !== undefined ? body.meddpicc_competition : opp.meddpicc_competition,
    body.emotional_arc !== undefined ? body.emotional_arc : opp.emotional_arc,
    body.division !== undefined ? body.division : opp.division,
    body.readiness_pnl_pain !== undefined ? parseInt(body.readiness_pnl_pain) : opp.readiness_pnl_pain,
    body.readiness_decision_maker !== undefined ? parseInt(body.readiness_decision_maker) : opp.readiness_decision_maker,
    body.readiness_competitor !== undefined ? parseInt(body.readiness_competitor) : opp.readiness_competitor,
    body.readiness_unique_angle !== undefined ? parseInt(body.readiness_unique_angle) : opp.readiness_unique_angle,
    body.readiness_proof !== undefined ? parseInt(body.readiness_proof) : opp.readiness_proof,
    stageChanged ? now : (opp.stage_changed_at || ''),
    now,
    id
  ).run();

  // Activity log
  if (changes.length > 0) {
    await env.DB.prepare(
      'INSERT INTO activity_log (opportunity_id, action, actor, created_at) VALUES (?, ?, ?, ?)'
    ).bind(id, `Updated: ${changes.join('; ')}`, session.display_name, now).run();
  }

  const { results } = await env.DB.prepare('SELECT * FROM opportunities WHERE id = ?').bind(id).all();
  return json(results[0]);
}

// ─── Route: Stats ────────────────────────────────────────────────────

async function apiStats(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const [total, byStage, byOwner, byType, byGeo, won, lost] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost')").all(),
    env.DB.prepare('SELECT stage, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities GROUP BY stage').all(),
    env.DB.prepare("SELECT owner, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost') GROUP BY owner").all(),
    env.DB.prepare("SELECT type, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost') GROUP BY type").all(),
    env.DB.prepare("SELECT geography, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost') GROUP BY geography").all(),
    env.DB.prepare("SELECT COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage = 'Closed Won'").all(),
    env.DB.prepare("SELECT COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage = 'Closed Lost'").all(),
  ]);

  return json({
    total: total.results[0],
    by_stage: byStage.results,
    by_owner: byOwner.results,
    by_type: byType.results,
    by_geography: byGeo.results,
    won: won.results[0],
    lost: lost.results[0],
  });
}

// ─── Route: Activity ─────────────────────────────────────────────────

async function apiActivity(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const url = new URL(request.url);
  let limit = parseInt(url.searchParams.get('limit') || '50');
  if (limit > 200) limit = 200;

  const { results } = await env.DB.prepare(`
    SELECT a.*, o.company
    FROM activity_log a
    LEFT JOIN opportunities o ON a.opportunity_id = o.id
    ORDER BY a.created_at DESC
    LIMIT ?
  `).bind(limit).all();

  return json(results);
}

// ─── Route: Accounts ─────────────────────────────────────────────────

async function apiAccounts(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const { results: accounts } = await env.DB.prepare(`
    SELECT company,
           COUNT(*) as deal_count,
           COALESCE(SUM(estimated_value), 0) as total_value,
           COUNT(DISTINCT contact_name) as contact_count
    FROM opportunities
    GROUP BY company
    ORDER BY deal_count DESC, total_value DESC
  `).all();

  for (const account of accounts) {
    const { results: opps } = await env.DB.prepare(`
      SELECT id, contact_name, contact_title, contact_email, contact_linkedin,
             contact_location, stage, estimated_value, type, partner, next_action, division
      FROM opportunities
      WHERE company = ?
      ORDER BY estimated_value DESC
    `).bind(account.company).all();
    account.opportunities = opps;
  }

  return json(accounts);
}

// ─── Route: Notes ────────────────────────────────────────────────────

async function apiGetNotes(request, env, id) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const { results } = await env.DB.prepare(
    'SELECT * FROM meeting_notes WHERE opportunity_id = ? ORDER BY created_at DESC'
  ).bind(id).all();

  return json(results);
}

async function apiAddNote(request, env, id) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

  const content = (body.content || '').trim();
  if (!content) return json({ error: 'Note content is required' }, 400);

  let noteType = body.note_type || 'meeting';
  if (!['meeting', 'call', 'email', 'general'].includes(noteType)) noteType = 'general';

  const now = nowISO();

  const { meta } = await env.DB.prepare(
    'INSERT INTO meeting_notes (opportunity_id, note_type, content, actor, created_at) VALUES (?, ?, ?, ?, ?)'
  ).bind(id, noteType, content, session.display_name, now).run();

  await env.DB.prepare(
    'INSERT INTO activity_log (opportunity_id, action, actor, created_at) VALUES (?, ?, ?, ?)'
  ).bind(id, `Added ${noteType} note`, session.display_name, now).run();

  await env.DB.prepare(
    'UPDATE opportunities SET updated_at = ? WHERE id = ?'
  ).bind(now, id).run();

  const { results } = await env.DB.prepare(
    'SELECT * FROM meeting_notes WHERE id = ?'
  ).bind(meta.last_row_id).all();

  return json(results[0], 201);
}

// ─── Route: Owners ───────────────────────────────────────────────────

async function apiOwners(request, env) {
  const session = await getSession(env, request);
  if (!session) return json({ error: 'Not authenticated' }, 401);

  const { results } = await env.DB.prepare(
    'SELECT display_name, role FROM users ORDER BY display_name'
  ).all();

  return json(results);
}

// ─── Router ──────────────────────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // Ensure users are seeded on first request
    ctx.waitUntil(ensureUsersSeeded(env));

    // ── Static file serving (/s/) ──
    if (path.startsWith('/s/')) {
      const filename = path.slice(3);
      if (filename in STATIC_FILES) {
        return new Response(STATIC_FILES[filename].content, {
          headers: { 'Content-Type': STATIC_FILES[filename].type },
        });
      }
      return new Response('Not found', { status: 404 });
    }

    // ── Prospect pages ──
    if (path.startsWith('/p/') || path.startsWith('/api/prospect-pages')) {
      return handleProspectPages(request, env, path, method);
    }

    // ── LinkedIn OAuth ──
    if (path.startsWith('/linkedin/') || path.startsWith('/api/linkedin/')) {
      return handleLinkedIn(request, env, path, method);
    }

    // ── API Routes ──
    if (path === '/api/login' && method === 'POST') return apiLogin(request, env);
    if (path === '/api/logout' && method === 'POST') return apiLogout(request, env);
    if (path === '/api/me' && method === 'GET') return apiMe(request, env);

    if (path === '/api/opportunities' && method === 'GET') return apiListOpportunities(request, env);
    if (path === '/api/opportunities' && method === 'POST') return apiCreateOpportunity(request, env);

    // /api/opportunities/{id}
    const oppMatch = path.match(/^\/api\/opportunities\/(\d+)$/);
    if (oppMatch) {
      const id = parseInt(oppMatch[1]);
      if (method === 'GET') return apiGetOpportunity(request, env, id);
      if (method === 'PUT') return apiUpdateOpportunity(request, env, id);
    }

    // /api/opportunities/{id}/notes
    const notesMatch = path.match(/^\/api\/opportunities\/(\d+)\/notes$/);
    if (notesMatch) {
      const id = parseInt(notesMatch[1]);
      if (method === 'GET') return apiGetNotes(request, env, id);
      if (method === 'POST') return apiAddNote(request, env, id);
    }

    if (path === '/api/stats' && method === 'GET') return apiStats(request, env);
    if (path === '/api/activity' && method === 'GET') return apiActivity(request, env);
    if (path === '/api/owners' && method === 'GET') return apiOwners(request, env);
    if (path === '/api/accounts' && method === 'GET') return apiAccounts(request, env);

    // ── Index (SPA) ──
    if (path === '/' || path === '') {
      return html(HTML_PAGE, 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
      });
    }

    return new Response('Not found', { status: 404 });
  },
};

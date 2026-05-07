/**
 * Referrals API Worker — full CRUD facade over D1 `purebrain-referrals`.
 *
 * Replaces ALL container/SQLite dependencies. D1 is the single source of truth.
 *
 * Endpoints (all JSON responses):
 *
 *   --- Public / VPS-scoped ---
 *   GET  /health
 *   GET  /referrers?code=PB-XXXX           — full referrer row (minus password_hash)
 *   GET  /referrers?email=foo@bar           — full referrer row
 *   GET  /referrals?referrer_id=N           — list referrals (joined with commission sums)
 *   GET  /commission_payments?referral_id=N
 *   GET  /dashboard?code=PB-XXXX           — aggregated shape matching portal /refer/ frontend
 *   GET  /leaderboard                       — ranked affiliates by completed referrals + earnings
 *
 *   --- Admin (X-Admin-Token required) ---
 *   GET  /admin/emails                      — lightweight (email, code) pairs
 *   GET  /admin/affiliates                  — full admin view with stats per affiliate
 *   GET  /admin/payouts                     — list all payout requests
 *   GET  /admin/stats                       — overview stats (totals)
 *   POST /referrers/upsert                  — auto-provision referral code
 *   POST /referrals/complete                — mark a referral as completed
 *   POST /commission_payments               — record a commission payment
 *   POST /admin/payout/mark-paid            — mark a payout request as paid
 *   POST /admin/referral/assign             — manually assign a client to a referrer
 *   PUT  /admin/affiliate/update            — update affiliate details
 *   PUT  /admin/referral/update             — update a referral record
 *   DELETE /admin/affiliate/delete          — delete affiliate + cascade
 *
 * Auth model:
 *   - /admin/* and write endpoints require X-Admin-Token header or ?admin_token= query param
 *     matching ADMIN_TOKENS secret (comma-separated).
 *   - Public read endpoints are open (called by portal_server.py behind its own auth).
 *
 * D1 binding: env.DB
 */

const REFERRER_PUBLIC_COLS = [
  "id", "user_name", "user_email", "referral_code",
  "paypal_email", "created_at", "partner_tier", "total_sales", "split_config"
  // Note: password_hash intentionally excluded.
];

/* ---------- tier rate lookup (CTO Edit #2 + SPEC C1/C3) ---------- */

// Authoritative tier→rate map. Source of truth for commission calculations.
// 'silver' is the new default for /partners/signup (was 'standard' 5%).
// 'elite' kept for legacy partners (e.g., founder-tier); admin-only.
const TIER_RATES = Object.freeze({
  standard: 0.05,   // legacy — 5% — DO NOT assign to new partners
  silver:   0.15,   // default for new signups (CTO Edit #2 / SPEC C1)
  gold:     0.17,   // 100+ referrals milestone (SPEC C3)
  platinum: 0.20,   // 1000+ referrals milestone (SPEC C3)
  elite:    0.25,   // legacy founder-tier; matches Support Tier numerically
});

const SUPPORT_TIER_RATE = 0.25; // SPEC E1

function rateForTier(tier) {
  const t = String(tier || "silver").toLowerCase();
  return TIER_RATES[t] !== undefined ? TIER_RATES[t] : TIER_RATES.silver;
}

// Milestone thresholds (SPEC C3)
function milestoneTier(totalSales) {
  const n = Number(totalSales) || 0;
  if (n >= 1000) return "platinum";
  if (n >= 100)  return "gold";
  return null; // no milestone reached
}

// SPEC E1: detect Support Tier subscription via PayPal Plan ID allowlist
function isSupportTierPlan(planId, env) {
  if (!planId) return false;
  const allow = (env.SUPPORT_TIER_PLAN_IDS || "")
    .split(",").map(s => s.trim()).filter(Boolean);
  return allow.includes(String(planId).trim());
}

/**
 * Constitutional commission formula (SPEC A3 / CTO Edit #1):
 *   commission = paymentAmount * rate
 *
 * NO $35 deduction in Worker — the $35 ops fee is taken in
 * tools/paypal_auto_split.py at payout time, NOT here.
 *
 * SPEC E1: if planId matches SUPPORT_TIER_PLAN_IDS, override to 25%.
 *
 * Returns { value, rate, source } where source ∈ {'standard','support_tier'}.
 */
function computeCommission({ paymentAmount, partnerTier, planId, env }) {
  const amt = Number(paymentAmount) || 0;
  if (isSupportTierPlan(planId, env)) {
    return {
      value: Math.round(amt * SUPPORT_TIER_RATE * 100) / 100,
      rate:  SUPPORT_TIER_RATE,
      source: "support_tier",
    };
  }
  const rate = rateForTier(partnerTier);
  return {
    value: Math.round(amt * rate * 100) / 100,
    rate,
    source: "standard",
  };
}

/* ---------- helpers ---------- */

function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
      "access-control-allow-headers": "x-admin-token, content-type",
      ...(init.headers || {}),
    },
  });
}

function err(status, message) {
  return json({ error: message }, { status });
}

async function requireAdmin(request, env) {
  const hdr = request.headers.get("x-admin-token") || "";
  const url = new URL(request.url);
  const qp  = url.searchParams.get("admin_token") || "";
  const token = (hdr || qp).trim();
  if (!token) return false;
  const allow = (env.ADMIN_TOKENS || "").split(",").map(s => s.trim()).filter(Boolean);
  return allow.includes(token);
}

function pick(row, cols) {
  const out = {};
  for (const c of cols) out[c] = row[c];
  return out;
}

async function parseBody(request) {
  try { return await request.json(); }
  catch (_e) { return null; }
}

/* ---------- route handler ---------- */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const method = request.method.toUpperCase();

    // CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
          "access-control-allow-headers": "x-admin-token, content-type",
          "access-control-max-age": "86400",
        },
      });
    }

    try {
      // ─────────────────────────────────────────────
      // POST endpoints
      // ─────────────────────────────────────────────

      if (method === "POST" && path === "/referrers/upsert") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email        = String(body.email || "").trim().toLowerCase();
        const name         = String(body.name || "").trim();
        const code         = String(body.code || "").trim().toUpperCase();
        const paypal_email = String(body.paypal_email || "").trim();
        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!code) return err(400, "code required");

        const now = new Date().toISOString();
        try {
          const res = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at)
             VALUES (?, ?, ?, ?, '', ?)
             ON CONFLICT(user_email) DO UPDATE SET
               user_name    = CASE WHEN referrers.user_name = '' THEN excluded.user_name ELSE referrers.user_name END,
               paypal_email = CASE WHEN referrers.paypal_email = '' THEN excluded.paypal_email ELSE referrers.paypal_email END
             RETURNING id, user_email, referral_code, user_name, paypal_email, created_at`
          ).bind(name, email, code, paypal_email, now).all();
          const row = res.results && res.results[0];
          return json({ ok: true, referrer: row, provisioned: !!row });
        } catch (e) {
          return json({ error: "upsert_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      if (method === "POST" && path === "/referrals/complete") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const referral_id = body.referral_id;
        if (!referral_id) return err(400, "referral_id required");

        const now = new Date().toISOString();
        const res = await env.DB.prepare(
          `UPDATE referrals SET status = 'completed', completed_at = ? WHERE id = ? RETURNING *`
        ).bind(now, referral_id).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "referral not found");
        return json({ ok: true, referral: row });
      }

      if (method === "POST" && path === "/commission_payments") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const {
          referrer_id, referral_id, payer_email, order_id,
          payment_amount,
          // Legacy: caller can pass pre-computed values (paypal-webhook backwards-compat)
          commission_rate: legacyRate, commission_value: legacyValue, tier: legacyTier,
          // New: caller passes plan_id; Worker computes rate via TIER_RATES + Support Tier
          plan_id,
        } = body;
        if (!referrer_id || !referral_id) return err(400, "referrer_id and referral_id required");

        // Look up partner_tier for tier_at_write audit + rate computation
        const refRow = await env.DB.prepare(
          `SELECT partner_tier FROM referrers WHERE id = ?`
        ).bind(referrer_id).first();
        const partner_tier = (refRow && refRow.partner_tier) || legacyTier || "silver";

        // SPEC A3 (CTO Edit #1): commission = paymentAmount * rate. NO $35 deduction here.
        // The $35 ops fee is taken in tools/paypal_auto_split.py at payout time.
        // SPEC E1: if plan_id is in SUPPORT_TIER_PLAN_IDS, override to 25%.
        let commission_value, commission_rate, commission_source;
        if (legacyValue !== undefined && legacyRate !== undefined) {
          // Legacy path: caller pre-computed (paypal-webhook with custom logic)
          commission_value = Number(legacyValue);
          commission_rate  = Number(legacyRate);
          commission_source = isSupportTierPlan(plan_id, env) ? "support_tier" : "standard";
        } else {
          // New path: Worker computes from payment_amount + partner_tier (+ plan_id)
          const computed = computeCommission({
            paymentAmount: payment_amount,
            partnerTier: partner_tier,
            planId: plan_id,
            env,
          });
          commission_value = computed.value;
          commission_rate  = computed.rate;
          commission_source = computed.source;
        }

        // CTO Edit #2: tier_at_write MUST be set on every commission_payments INSERT
        // for safe idempotent retroactive recalc.
        const tier_at_write = String(partner_tier);

        const now = new Date().toISOString();
        const res = await env.DB.prepare(
          `INSERT INTO commission_payments
             (referrer_id, referral_id, payer_email, order_id,
              payment_amount, commission_rate, commission_value, tier,
              tier_at_write, commission_source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           RETURNING *`
        ).bind(
          referrer_id, referral_id,
          payer_email || "", order_id || "",
          Number(payment_amount) || 0,
          commission_rate, commission_value,
          tier_at_write, // legacy `tier` col mirrors tier_at_write for backwards compat
          tier_at_write,
          commission_source,
          now
        ).all();
        const row = res.results && res.results[0];
        return json({ ok: true, payment: row });
      }

      // POST /admin/payout/mark-paid — mark a payout request as paid
      if (method === "POST" && path === "/admin/payout/mark-paid") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { payout_id, notes } = body;
        if (!payout_id) return err(400, "payout_id required");

        const now = new Date().toISOString();
        const res = await env.DB.prepare(
          `UPDATE payout_requests SET status = 'paid', paid_at = ?, notes = COALESCE(?, notes) WHERE id = ? RETURNING *`
        ).bind(now, notes || null, payout_id).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "payout request not found");
        return json({ ok: true, payout: row });
      }

      // POST /admin/referral/assign — manually assign a client to a referrer
      if (method === "POST" && path === "/admin/referral/assign") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referrer_id, referred_email, referred_name } = body;
        if (!referrer_id) return err(400, "referrer_id required");
        if (!referred_email) return err(400, "referred_email required");

        const now = new Date().toISOString();
        const res = await env.DB.prepare(
          `INSERT INTO referrals (referrer_id, referred_email, referred_name, status, created_at)
           VALUES (?, ?, ?, 'pending', ?)
           RETURNING *`
        ).bind(referrer_id, referred_email.trim().toLowerCase(), (referred_name || "").trim(), now).all();
        const row = res.results && res.results[0];
        return json({ ok: true, referral: row });
      }

      // ─────────────────────────────────────────────
      // PUT endpoints
      // ─────────────────────────────────────────────

      if (method === "PUT" && path === "/admin/affiliate/update") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referrer_id, user_name, user_email, paypal_email } = body;
        if (!referrer_id) return err(400, "referrer_id required");

        // Build dynamic SET clause for only provided fields
        const sets = [];
        const binds = [];
        if (user_name !== undefined) { sets.push("user_name = ?"); binds.push(user_name); }
        if (user_email !== undefined) { sets.push("user_email = ?"); binds.push(user_email.trim().toLowerCase()); }
        if (paypal_email !== undefined) { sets.push("paypal_email = ?"); binds.push(paypal_email.trim()); }

        if (sets.length === 0) return err(400, "no fields to update");

        binds.push(referrer_id);
        const res = await env.DB.prepare(
          `UPDATE referrers SET ${sets.join(", ")} WHERE id = ? RETURNING *`
        ).bind(...binds).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "referrer not found");
        return json({ ok: true, referrer: pick(row, REFERRER_PUBLIC_COLS) });
      }

      if (method === "PUT" && path === "/admin/referral/update") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referral_id, referred_email, referred_name, status } = body;
        if (!referral_id) return err(400, "referral_id required");

        const sets = [];
        const binds = [];
        if (referred_email !== undefined) { sets.push("referred_email = ?"); binds.push(referred_email.trim().toLowerCase()); }
        if (referred_name !== undefined) { sets.push("referred_name = ?"); binds.push(referred_name.trim()); }
        if (status !== undefined) {
          sets.push("status = ?"); binds.push(status);
          if (status === "completed") {
            sets.push("completed_at = ?"); binds.push(new Date().toISOString());
          }
        }

        if (sets.length === 0) return err(400, "no fields to update");

        binds.push(referral_id);
        const res = await env.DB.prepare(
          `UPDATE referrals SET ${sets.join(", ")} WHERE id = ? RETURNING *`
        ).bind(...binds).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "referral not found");
        return json({ ok: true, referral: row });
      }

      // ─────────────────────────────────────────────
      // DELETE endpoints
      // ─────────────────────────────────────────────

      if (method === "DELETE" && path === "/admin/affiliate/delete") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referrer_id } = body;
        if (!referrer_id) return err(400, "referrer_id required");

        // Cascade: delete commission_payments for this referrer's referrals, then referrals, then referrer
        // Also clean up payout_requests, rewards, referral_clicks
        await env.DB.prepare(
          `DELETE FROM commission_payments WHERE referrer_id = ?`
        ).bind(referrer_id).run();
        await env.DB.prepare(
          `DELETE FROM rewards WHERE referrer_id = ?`
        ).bind(referrer_id).run();
        await env.DB.prepare(
          `DELETE FROM payout_requests WHERE referrer_id = ?`
        ).bind(referrer_id).run();

        // Get referral_code before deleting referrer (for click cleanup)
        const ref = await env.DB.prepare(
          `SELECT referral_code FROM referrers WHERE id = ?`
        ).bind(referrer_id).first();

        await env.DB.prepare(
          `DELETE FROM referrals WHERE referrer_id = ?`
        ).bind(referrer_id).run();

        if (ref && ref.referral_code) {
          await env.DB.prepare(
            `DELETE FROM referral_clicks WHERE referral_code = ? COLLATE NOCASE`
          ).bind(ref.referral_code).run();
        }

        const del = await env.DB.prepare(
          `DELETE FROM referrers WHERE id = ?`
        ).bind(referrer_id).run();

        return json({ ok: true, deleted: del.meta?.changes > 0 });
      }

      // ─────────────────────────────────────────────
      // GET endpoints
      // ─────────────────────────────────────────────

      if (method !== "GET" && method !== "POST" && method !== "PUT" && method !== "DELETE") {
        return err(405, "method not allowed");
      }
      if (method !== "GET") return err(404, "not found");

      // GET /health
      if (path === "/health") {
        return json({ ok: true, db: "purebrain-referrals", ts: new Date().toISOString() });
      }

      // GET /referrers
      if (path === "/referrers") {
        const code  = (url.searchParams.get("code")  || "").trim();
        const email = (url.searchParams.get("email") || "").trim();
        if (!code && !email) return err(400, "missing code or email");
        const sql = code
          ? `SELECT * FROM referrers WHERE referral_code = ? COLLATE NOCASE`
          : `SELECT * FROM referrers WHERE user_email = ? COLLATE NOCASE`;
        const { results } = await env.DB.prepare(sql).bind(code || email).all();
        if (!results || results.length === 0) return err(404, "referrer not found");
        return json({ referrer: pick(results[0], REFERRER_PUBLIC_COLS) });
      }

      // GET /referrals
      if (path === "/referrals") {
        const refId = (url.searchParams.get("referrer_id") || "").trim();
        if (!refId) return err(400, "missing referrer_id");
        const { results } = await env.DB.prepare(
          `SELECT r.id, r.referred_name, r.referred_email, r.status, r.created_at,
                  r.completed_at,
                  COALESCE(SUM(cp.commission_value), 0) AS earnings,
                  COUNT(cp.id) AS payment_count
             FROM referrals r
             LEFT JOIN commission_payments cp ON cp.referral_id = r.id
            WHERE r.referrer_id = ?
              AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
         GROUP BY r.id
         ORDER BY r.created_at DESC`
        ).bind(refId).all();
        return json({ referrals: results || [] });
      }

      // GET /commission_payments
      if (path === "/commission_payments") {
        const referralId = (url.searchParams.get("referral_id") || "").trim();
        if (!referralId) return err(400, "missing referral_id");
        const { results } = await env.DB.prepare(
          `SELECT id, referrer_id, referral_id, payer_email, order_id,
                  payment_amount, commission_rate, commission_value, tier,
                  tier_at_write, commission_source, created_at
             FROM commission_payments
            WHERE referral_id = ?
         ORDER BY created_at DESC`
        ).bind(referralId).all();
        return json({ payments: results || [] });
      }

      // GET /dashboard
      if (path === "/dashboard") {
        const code  = (url.searchParams.get("code")  || "").trim().toUpperCase();
        const email = (url.searchParams.get("email") || "").trim().toLowerCase();
        if (!code && !email) return err(400, "missing code or email");

        const refRes = await env.DB.prepare(
          code
            ? `SELECT * FROM referrers WHERE referral_code = ? COLLATE NOCASE`
            : `SELECT * FROM referrers WHERE user_email = ? COLLATE NOCASE`
        ).bind(code || email).all();
        const referrer = refRes.results && refRes.results[0];
        if (!referrer) return err(404, "referrer not found");

        const rid   = referrer.id;
        const rcode = referrer.referral_code;

        const totalQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ?
             AND NOT (status = 'rejected' AND referred_email LIKE 'paypal_%@pending')`
        ).bind(rid).first();
        const completedQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ? AND status = 'completed'`
        ).bind(rid).first();
        const pendingQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ? AND status = 'pending'`
        ).bind(rid).first();
        const earningsQ = await env.DB.prepare(
          `SELECT COALESCE(SUM(reward_value), 0) AS s FROM rewards WHERE referrer_id = ?`
        ).bind(rid).first();
        const clicksQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referral_clicks WHERE referral_code = ? COLLATE NOCASE`
        ).bind(rcode).first();

        const histQ = await env.DB.prepare(
          `SELECT r.referred_name, r.referred_email, r.status, r.created_at,
                  COALESCE(SUM(cp.commission_value), 0) AS earnings,
                  COUNT(cp.id) AS payment_count
             FROM referrals r
             LEFT JOIN commission_payments cp ON cp.referral_id = r.id
            WHERE r.referrer_id = ?
              AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
         GROUP BY r.id
         ORDER BY r.created_at DESC`
        ).bind(rid).all();

        return json({
          referrer_id: rid,
          referral_code: rcode,
          email: referrer.user_email,
          name: referrer.user_name,
          paypal_email: referrer.paypal_email,
          total_referrals: totalQ.c,
          completed: completedQ.c,
          pending: pendingQ.c,
          earnings: Math.round((earningsQ.s || 0) * 100) / 100,
          total_clicks: clicksQ.c,
          history: histQ.results || [],
        });
      }

      // GET /leaderboard — public, ranked affiliates
      if (path === "/leaderboard") {
        const { results } = await env.DB.prepare(
          `SELECT
             ref.id,
             ref.user_name AS name,
             ref.referral_code AS code,
             COUNT(DISTINCT CASE WHEN r.status = 'completed' THEN r.id END) AS completed,
             COUNT(DISTINCT CASE WHEN r.status = 'pending' THEN r.id END) AS pending,
             COUNT(DISTINCT r.id) AS total_referrals,
             COALESCE(SUM(cp.commission_value), 0) AS total_earned
           FROM referrers ref
           LEFT JOIN referrals r ON r.referrer_id = ref.id
             AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
           LEFT JOIN commission_payments cp ON cp.referral_id = r.id
           GROUP BY ref.id
           ORDER BY completed DESC, total_earned DESC`
        ).all();
        return json({ leaderboard: results || [] });
      }

      // GET /admin/emails
      if (path === "/admin/emails") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const { results } = await env.DB.prepare(
          `SELECT user_email, referral_code FROM referrers`
        ).all();
        return json({ count: (results || []).length, referrers: results || [] });
      }

      // GET /admin/affiliates
      if (path === "/admin/affiliates") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");

        // Single aggregated query instead of N+1 per-referrer
        const { results: referrers } = await env.DB.prepare(
          `SELECT r.*,
                  COALESCE(rc.click_count, 0) AS clicks,
                  COALESCE(ref_stats.total, 0) AS total,
                  COALESCE(ref_stats.completed, 0) AS completed,
                  COALESCE(ref_stats.pending, 0) AS pending,
                  COALESCE(rew.earnings, 0) AS earnings
           FROM referrers r
           LEFT JOIN (SELECT referral_code, COUNT(*) AS click_count FROM referral_clicks GROUP BY referral_code) rc
             ON LOWER(rc.referral_code) = LOWER(r.referral_code)
           LEFT JOIN (SELECT referrer_id,
                             COUNT(*) AS total,
                             SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed,
                             SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending
                      FROM referrals GROUP BY referrer_id) ref_stats
             ON ref_stats.referrer_id = r.id
           LEFT JOIN (SELECT referrer_id, COALESCE(SUM(reward_value), 0) AS earnings FROM rewards GROUP BY referrer_id) rew
             ON rew.referrer_id = r.id
           ORDER BY r.created_at DESC`
        ).all();

        // Get referral history in one query
        const { results: allHistory } = await env.DB.prepare(
          `SELECT ref.referrer_id, ref.id, ref.referred_name, ref.referred_email, ref.status, ref.created_at,
                  COALESCE(SUM(cp.commission_value), 0) AS earnings,
                  COUNT(cp.id) AS payment_count
           FROM referrals ref
           LEFT JOIN commission_payments cp ON cp.referral_id = ref.id
           GROUP BY ref.id
           ORDER BY ref.created_at DESC`
        ).all();

        // Group history by referrer
        const histMap = {};
        for (const h of allHistory || []) {
          if (!histMap[h.referrer_id]) histMap[h.referrer_id] = [];
          histMap[h.referrer_id].push({
            id: h.id, referred_name: h.referred_name, referred_email: h.referred_email,
            status: h.status, created_at: h.created_at, earnings: h.earnings, payment_count: h.payment_count
          });
        }

        const affiliates = (referrers || []).map(r => ({
          id: r.id, name: r.user_name, email: r.user_email, code: r.referral_code,
          paypal_email: r.paypal_email || "", clicks: r.clicks || 0,
          total: r.total || 0, completed: r.completed || 0, pending: r.pending || 0,
          earnings: r.earnings || 0, joined: r.created_at,
          history: histMap[r.id] || []
        }));

        return json({ affiliates, count: affiliates.length });
      }

      // GET /admin/payouts — list all payout requests
      if (path === "/admin/payouts") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const { results } = await env.DB.prepare(
          `SELECT p.*, ref.user_name AS referrer_name, ref.user_email AS referrer_email,
                  ref.paypal_email AS referrer_paypal
           FROM payout_requests p
           LEFT JOIN referrers ref ON ref.id = p.referrer_id
           ORDER BY p.created_at DESC`
        ).all();
        return json({ payouts: results || [], count: (results || []).length });
      }

      // GET /admin/stats — overview stats
      if (path === "/admin/stats") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");

        const affiliatesQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrers`
        ).first();
        const clicksQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referral_clicks`
        ).first();
        const referralsQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals`
        ).first();
        const completedQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE status = 'completed'`
        ).first();
        const pendingQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE status = 'pending'`
        ).first();
        const earningsQ = await env.DB.prepare(
          `SELECT COALESCE(SUM(commission_value), 0) AS total FROM commission_payments`
        ).first();
        const rewardsQ = await env.DB.prepare(
          `SELECT COALESCE(SUM(reward_value), 0) AS total FROM rewards`
        ).first();

        return json({
          total_affiliates: affiliatesQ.c,
          total_clicks: clicksQ.c,
          total_referrals: referralsQ.c,
          completed_referrals: completedQ.c,
          pending_referrals: pendingQ.c,
          total_commissions: Math.round((earningsQ.total || 0) * 100) / 100,
          total_rewards: Math.round((rewardsQ.total || 0) * 100) / 100,
        });
      }

      return err(404, "not found");
    } catch (e) {
      return json({ error: "worker_error", detail: String(e && e.message || e) }, { status: 500 });
    }
  },
};

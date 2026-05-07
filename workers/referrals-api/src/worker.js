/**
 * Referrals API Worker — full CRUD facade over D1 `purebrain-referrals`.
 *
 * Replaces ALL container/SQLite dependencies. D1 is the single source of truth.
 *
 * Endpoints (all JSON responses):
 *
 *   --- Public / VPS-scoped ---
 *   GET  /health
 *   GET  /referrers?code=PB-XXXX             — full referrer row (minus password_hash)
 *   GET  /referrers?email=foo@bar             — full referrer row
 *   GET  /referrals?referrer_id=N             — list referrals (joined with commission sums)
 *   GET  /commission_payments?referral_id=N
 *   GET  /dashboard?code=PB-XXXX             — aggregated shape with partner_tier + tier_rate
 *   GET  /leaderboard                         — ranked affiliates
 *
 *   --- Public Application & Payout (partner-self) ---
 *   POST /partners/apply                      — partner application (creates partner_applications row)
 *   POST /referrals/complete                  — payment-page onApprove POST (idempotent pending row)
 *   POST /payouts/request                     — partner-self payout request ($50 min)
 *
 *   --- Admin (X-Admin-Token required) ---
 *   GET  /admin/emails                        — lightweight (email, code) pairs
 *   GET  /admin/affiliates                    — full admin view (incl. partner_tier + split_config)
 *   GET  /admin/payouts                       — list payout requests (legacy + v2 merged)
 *   GET  /admin/applications                  — list partner applications (?status= filter)
 *   GET  /admin/stats                         — overview stats (totals)
 *   POST /referrers/upsert                    — auto-provision referral code (default tier=silver)
 *   POST /partners/signup                     — direct admin signup (default tier=silver)
 *   POST /commission_payments                 — record commission (writes tier_at_write + Support Tier detect)
 *   POST /admin/payout/mark-paid              — mark a payout request as paid
 *   POST /admin/referral/assign               — manually assign a client to a referrer
 *   POST /admin/applications/:id/approve      — approve partner application
 *   POST /admin/applications/:id/reject       — reject partner application (CTO Edit #8)
 *   POST /admin/recalc-tier                   — retroactive rate recalc (chunked, idempotent)
 *   POST /referrals/complete (admin mode)     — mark existing row completed by id
 *   PUT  /admin/affiliate/update              — update affiliate (incl. partner_tier, split_config)
 *   PUT  /admin/referral/update               — update a referral record
 *   DELETE /admin/affiliate/delete            — delete affiliate + cascade
 *
 * Auth model:
 *   - /admin/* and admin write endpoints require X-Admin-Token header or
 *     ?admin_token= query param matching ADMIN_TOKENS secret (comma-separated).
 *   - /partners/apply, /referrals/complete (public mode), /payouts/request are
 *     PUBLIC — called from website frontend. Idempotency from UNIQUE INDEX
 *     and identity gate (paypal_email match) prevent abuse.
 *
 * D1 binding: env.DB
 *
 * Env vars (wrangler.toml + secrets):
 *   ADMIN_TOKENS           — comma-separated admin tokens (secret, REQUIRED)
 *   SUPPORT_TIER_PLAN_IDS  — comma-separated PayPal Plan IDs that map to Support
 *                            Tier 25% (SPEC E1 / CTO Q2). Empty default = no plans.
 *
 * Constitutional notes:
 *   - Commission formula = paymentAmount * rate. NO $35 deduction in Worker
 *     ($35 ops fee comes off in tools/paypal_auto_split.py per CTO Edit #1).
 *   - Every commission_payments INSERT MUST set tier_at_write (CTO Edit #2)
 *     for safe retroactive recalc (CTO §1.3).
 *   - $50 min payout enforced by DB CHECK on payout_requests_v2.
 *   - (pb_ref, payment_id) UNIQUE INDEX makes /referrals/complete idempotent.
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
          // SPEC C1: NEW upsert rows default to partner_tier='silver' (15%)
          // Existing rows preserve their partner_tier on conflict.
          const res = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at, partner_tier, total_sales)
             VALUES (?, ?, ?, ?, '', ?, 'silver', 0)
             ON CONFLICT(user_email) DO UPDATE SET
               user_name    = CASE WHEN referrers.user_name = '' THEN excluded.user_name ELSE referrers.user_name END,
               paypal_email = CASE WHEN referrers.paypal_email = '' THEN excluded.paypal_email ELSE referrers.paypal_email END
             RETURNING id, user_email, referral_code, user_name, paypal_email, created_at, partner_tier, total_sales`
          ).bind(name, email, code, paypal_email, now).all();
          const row = res.results && res.results[0];
          return json({ ok: true, referrer: row, provisioned: !!row });
        } catch (e) {
          return json({ error: "upsert_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /partners/apply — public partner application (SPEC C2)
      //
      // Replaces Brevo-only flow. Creates partner_applications row with
      // status='pending'. Admin reviews via GET /admin/applications and
      // approves/rejects via /admin/applications/:id/approve|reject.
      //
      // 30-day-use enforcement (CTO Q3): clients table currently lives in
      // purebrain-social D1 (held under domain-isolation rule, May 7).
      // For v1, applications default to 'pending' and admin verifies
      // 30d-use manually during review. Admin can stamp 'needs_30d_use'
      // status with reviewer_override_reason when overriding for partners
      // who paid via different email.
      //
      // Idempotent on email — UNIQUE constraint returns 409 if applied before.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/partners/apply") {
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email = String(body.email || "").trim().toLowerCase();
        const full_name = String(body.full_name || body.name || "").trim();
        const audience_size = Number.isFinite(Number(body.audience_size))
          ? Math.max(0, Math.floor(Number(body.audience_size)))
          : null;
        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!full_name) return err(400, "full_name required");

        // 30-day-use check: deferred to admin review queue (clients table
        // lives in purebrain-social D1, held under domain-isolation rule).
        // Future: extract clients to purebrain-clients D1 and add real lookup
        // that auto-stamps 'needs_30d_use' when applicant lacks 30d client history.
        const status = "pending";

        const application_data = JSON.stringify({
          source: body.source || "partners-page",
          referral_url: body.referral_url || null,
          notes: body.notes || null,
          submitted_user_agent: request.headers.get("user-agent") || null,
        });

        const now = Math.floor(Date.now() / 1000);
        try {
          const res = await env.DB.prepare(
            `INSERT INTO partner_applications (email, full_name, audience_size, application_data, status, applied_at)
             VALUES (?, ?, ?, ?, ?, ?)
             RETURNING id, email, full_name, status, applied_at`
          ).bind(email, full_name, audience_size, application_data, status, now).all();
          const row = res.results && res.results[0];
          return json({ ok: true, application: row });
        } catch (e) {
          // UNIQUE constraint on email → already applied
          const msg = String(e && e.message || e);
          if (msg.includes("UNIQUE")) {
            return err(409, "application_exists");
          }
          return json({ error: "apply_failed", detail: msg }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /admin/applications/:id/approve  (SPEC C2)
      // POST /admin/applications/:id/reject   (CTO Edit #8 — companion route)
      //
      // approve body: { code, paypal_email?, partner_tier?, reviewed_by?, reviewer_override_reason? }
      // reject body:  { rejection_reason, reviewed_by? }
      //
      // approve: creates active referrer row at chosen tier (default 'silver'),
      //          stamps application status='approved' with reviewed_at/by.
      // reject:  stamps application status='rejected' with rejection_reason.
      //
      // Both routes use existing X-Admin-Token auth pattern.
      // ─────────────────────────────────────────────
      const applicationActionMatch = path.match(/^\/admin\/applications\/(\d+)\/(approve|reject)$/);
      if (method === "POST" && applicationActionMatch) {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const appId = Number(applicationActionMatch[1]);
        const action = applicationActionMatch[2];
        const body = (await parseBody(request)) || {};

        const reviewed_by = String(body.reviewed_by || "admin").trim();
        const now = Math.floor(Date.now() / 1000);

        // Load application
        const appRow = await env.DB.prepare(
          `SELECT * FROM partner_applications WHERE id = ?`
        ).bind(appId).first();
        if (!appRow) return err(404, "application not found");
        if (appRow.status !== "pending" && appRow.status !== "needs_30d_use") {
          return err(409, `application already ${appRow.status}`);
        }

        if (action === "reject") {
          const rejection_reason = String(body.rejection_reason || "no reason given").slice(0, 500);
          await env.DB.prepare(
            `UPDATE partner_applications
                SET status = 'rejected', reviewed_at = ?, reviewed_by = ?, rejection_reason = ?
              WHERE id = ?`
          ).bind(now, reviewed_by, rejection_reason, appId).run();
          return json({ ok: true, action: "rejected", id: appId, rejection_reason });
        }

        // approve: create active referrer row, mark application approved
        const code = String(body.code || "").trim().toUpperCase();
        const paypal_email = String(body.paypal_email || appRow.email).trim();
        const partner_tier = String(body.partner_tier || "silver").toLowerCase();
        const reviewer_override_reason = body.reviewer_override_reason
          ? String(body.reviewer_override_reason).slice(0, 500)
          : null;
        if (!code) return err(400, "code required for approval");
        if (!TIER_RATES[partner_tier]) {
          return err(400, `invalid partner_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
        }

        const isoNow = new Date().toISOString();
        try {
          // Create referrer at chosen tier
          const refRes = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at, partner_tier, total_sales)
             VALUES (?, ?, ?, ?, '', ?, ?, 0)
             RETURNING id, user_email, referral_code, user_name, partner_tier`
          ).bind(appRow.full_name, appRow.email, code, paypal_email, isoNow, partner_tier).all();
          const referrer = refRes.results && refRes.results[0];

          // Mark application approved
          await env.DB.prepare(
            `UPDATE partner_applications
                SET status = 'approved', reviewed_at = ?, reviewed_by = ?, reviewer_override_reason = ?
              WHERE id = ?`
          ).bind(now, reviewed_by, reviewer_override_reason, appId).run();

          return json({
            ok: true,
            action: "approved",
            id: appId,
            referrer,
            tier_rate: rateForTier(partner_tier),
          });
        } catch (e) {
          return json({ error: "approve_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /partners/signup — direct admin signup (SPEC C1)
      // Default partner_tier='silver' (15%), explicit alternative tiers allowed.
      // (Public application path is /partners/apply; this is admin-direct provisioning.)
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/partners/signup") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email        = String(body.email || "").trim().toLowerCase();
        const name         = String(body.name || "").trim();
        const code         = String(body.code || "").trim().toUpperCase();
        const paypal_email = String(body.paypal_email || "").trim();
        // SPEC C1: default 'silver' (15%); admin can override
        const partner_tier = String(body.partner_tier || "silver").toLowerCase();

        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!code) return err(400, "code required");
        if (!TIER_RATES[partner_tier]) {
          return err(400, `invalid partner_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
        }

        const now = new Date().toISOString();
        try {
          const res = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at, partner_tier, total_sales)
             VALUES (?, ?, ?, ?, '', ?, ?, 0)
             RETURNING id, user_email, referral_code, user_name, paypal_email, created_at, partner_tier, total_sales`
          ).bind(name, email, code, paypal_email, now, partner_tier).all();
          const row = res.results && res.results[0];
          return json({
            ok: true,
            referrer: row,
            tier_rate: rateForTier(partner_tier),
          });
        } catch (e) {
          return json({ error: "signup_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /referrals/complete (SPEC B2 + CTO Q1)
      //
      // Two modes:
      //   1) Admin mode (legacy): { referral_id } → mark existing referral completed.
      //   2) Public mode (B2):    { pb_ref, payment_id, customer_email, ... }
      //      → INSERT OR IGNORE pending row (idempotent via UNIQUE INDEX
      //        uniq_referrals_pbref_payment on (pb_ref, payment_id)).
      //      Called from PayPal onApprove handlers on /awakened/, /insiders/,
      //      /partnered/, /unified/, homepage, home-test variants.
      //      No admin token required — idempotency from UNIQUE INDEX prevents abuse.
      //
      // Per CTO Q1: pending row created here (at payment-page onApprove time),
      // NOT at click-track time. Keeps referral_clicks separate from paid intent.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/referrals/complete") {
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        // Mode 1: admin legacy path — mark existing referral completed by id
        if (body.referral_id !== undefined && !body.pb_ref) {
          if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
          const referral_id = body.referral_id;
          const now = new Date().toISOString();
          const res = await env.DB.prepare(
            `UPDATE referrals SET status = 'completed', completed_at = ? WHERE id = ? RETURNING *`
          ).bind(now, referral_id).all();
          const row = res.results && res.results[0];
          if (!row) return err(404, "referral not found");
          return json({ ok: true, referral: row, mode: "admin_complete" });
        }

        // Mode 2: public payment-page POST — INSERT OR IGNORE pending row
        const pb_ref = String(body.pb_ref || body.referral_code || "").trim().toUpperCase();
        const payment_id = String(body.payment_id || body.order_id || "").trim();
        const customer_email = String(body.customer_email || body.email || "").trim().toLowerCase();
        const referred_name = String(body.referred_name || body.name || customer_email).trim();

        if (!pb_ref) return err(400, "pb_ref required");
        if (!payment_id) return err(400, "payment_id required");
        if (!customer_email || !customer_email.includes("@")) return err(400, "customer_email required");

        // Look up referrer by code (must exist for attribution)
        const referrer = await env.DB.prepare(
          `SELECT id, referral_code, partner_tier FROM referrers WHERE referral_code = ? COLLATE NOCASE`
        ).bind(pb_ref).first();
        if (!referrer) {
          // Unknown ref code — webhook can still attribute via customer_email separately.
          return json({ ok: false, error: "unknown_referral_code", pb_ref }, { status: 404 });
        }

        const now = new Date().toISOString();

        // INSERT OR IGNORE: UNIQUE INDEX uniq_referrals_pbref_payment makes this idempotent.
        // CTO Edit #4 / SPEC §3: page reload, network retry, double-click all collapse to 1 row.
        try {
          const insertRes = await env.DB.prepare(
            `INSERT OR IGNORE INTO referrals
                (referrer_id, referred_email, referred_name, status, created_at, pb_ref, payment_id)
             VALUES (?, ?, ?, 'pending', ?, ?, ?)
             RETURNING *`
          ).bind(
            referrer.id, customer_email, referred_name, now, pb_ref, payment_id
          ).all();
          const row = insertRes.results && insertRes.results[0];

          if (row) {
            return json({ ok: true, referral: row, idempotent: false, mode: "pending_create" });
          }

          // INSERT IGNORED → row already exists for (pb_ref, payment_id)
          const existing = await env.DB.prepare(
            `SELECT * FROM referrals WHERE pb_ref = ? AND payment_id = ? LIMIT 1`
          ).bind(pb_ref, payment_id).first();
          return json({ ok: true, referral: existing, idempotent: true, mode: "pending_create" });
        } catch (e) {
          return json({ error: "complete_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
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

      // ─────────────────────────────────────────────
      // POST /payouts/request — partner-self payout request (SPEC C4)
      //
      // PUBLIC endpoint. Identity gate: { partner_id, paypal_email }
      //   — must match referrers.referral_code + referrers.paypal_email.
      //
      // Body: { partner_id, amount, paypal_email }
      //
      // Constraints:
      //   - amount >= 50 (DB CHECK on payout_requests_v2 enforces this)
      //   - amount must not exceed (sum of commissions earned) - (sum of approved/paid payouts)
      //   - partner_id (referral_code) must exist
      //   - paypal_email must match referrer record (no spoofing)
      //
      // Admin approval (manual, via /admin/payout/mark-paid + paypal_auto_split.py)
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/payouts/request") {
        // Public — identity verified by partner_id + paypal_email match
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const partner_id = String(body.partner_id || body.referral_code || "").trim().toUpperCase();
        const amount = Number(body.amount || 0);
        const paypal_email = String(body.paypal_email || "").trim();

        if (!partner_id) return err(400, "partner_id required");
        if (!paypal_email || !paypal_email.includes("@")) return err(400, "paypal_email required");
        if (!Number.isFinite(amount) || amount < 50) {
          return err(400, "amount must be >= 50");
        }

        // Identity gate: partner exists + paypal_email matches
        const referrer = await env.DB.prepare(
          `SELECT id, referral_code, paypal_email FROM referrers WHERE referral_code = ? COLLATE NOCASE`
        ).bind(partner_id).first();
        if (!referrer) return err(404, "partner not found");
        if (referrer.paypal_email && referrer.paypal_email.toLowerCase() !== paypal_email.toLowerCase()) {
          return err(403, "paypal_email_mismatch");
        }

        // Verify partner has at least `amount` in unpaid commission earnings
        const earningsRow = await env.DB.prepare(
          `SELECT COALESCE(SUM(commission_value), 0) AS earned
             FROM commission_payments
            WHERE referrer_id = ?`
        ).bind(referrer.id).first();
        const paidRow = await env.DB.prepare(
          `SELECT COALESCE(SUM(amount), 0) AS paid
             FROM payout_requests_v2
            WHERE partner_id = ? COLLATE NOCASE
              AND status IN ('approved', 'paid')`
        ).bind(partner_id).first();
        const available = Math.round(((earningsRow.earned || 0) - (paidRow.paid || 0)) * 100) / 100;
        if (amount > available) {
          return err(400, `requested amount ${amount} exceeds available ${available.toFixed(2)}`);
        }

        const now = Math.floor(Date.now() / 1000);
        try {
          // DB CHECK constraint amount >= 50 enforces $50 min
          // CHECK payout_method = 'paypal' enforces v1 PayPal-only
          const res = await env.DB.prepare(
            `INSERT INTO payout_requests_v2
               (partner_id, amount, payout_method, paypal_email, status, requested_at)
             VALUES (?, ?, 'paypal', ?, 'requested', ?)
             RETURNING *`
          ).bind(partner_id, amount, paypal_email, now).all();
          const row = res.results && res.results[0];
          return json({
            ok: true,
            payout_request: row,
            available_after: Math.round((available - amount) * 100) / 100,
          });
        } catch (e) {
          return json({ error: "payout_request_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
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

      // ─────────────────────────────────────────────
      // POST /admin/recalc-tier — retroactive rate recalc (SPEC C3 / CTO Q4)
      //
      // Strategy: idempotent recalc using tier_at_write column.
      // Only rows where tier_at_write != target_tier get updated → safe
      // to call repeatedly; converges to consistent state.
      //
      // Body: {
      //   partner_id: "PB-XXXX",        — referral_code (required)
      //   trigger_event: "100_referrals" | "1000_referrals" | "manual"  (default "manual")
      //   force_tier:    "silver"|"gold"|"platinum"|"elite"  (optional override of milestone derivation)
      // }
      //
      // Behavior:
      //   - Computes target tier (force_tier > milestoneTier(total_sales) > current)
      //   - Updates referrers.partner_tier
      //   - Recalculates commission_payments rows where tier_at_write != target_tier
      //     AND commission_source != 'support_tier' (Support Tier locked at 25%)
      //   - Chunked at LIMIT 200 per call (CF Worker 30s CPU limit)
      //   - Returns more=true if rows still need recalc → caller re-invokes
      //   - Logs to rate_adjustments only on chunks that actually recalculated rows
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/admin/recalc-tier") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const partner_id = String(body.partner_id || "").trim().toUpperCase();
        const force_tier = body.force_tier ? String(body.force_tier).toLowerCase() : null;
        const trigger = String(body.trigger_event || "manual");

        if (!partner_id) return err(400, "partner_id required");
        if (!["100_referrals", "1000_referrals", "manual"].includes(trigger)) {
          return err(400, "invalid trigger_event");
        }
        if (force_tier && !TIER_RATES[force_tier]) {
          return err(400, `invalid force_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
        }

        // Load current partner state
        const referrer = await env.DB.prepare(
          `SELECT id, referral_code, partner_tier, total_sales FROM referrers WHERE referral_code = ? COLLATE NOCASE`
        ).bind(partner_id).first();
        if (!referrer) return err(404, "partner not found");

        const oldTier = String(referrer.partner_tier || "silver").toLowerCase();
        const computedTier = milestoneTier(referrer.total_sales);
        const newTier = String(force_tier || computedTier || oldTier).toLowerCase();
        if (!TIER_RATES[newTier]) return err(400, `invalid tier ${newTier}`);

        const oldRate = rateForTier(oldTier);
        const newRate = rateForTier(newTier);

        // No-op if tier unchanged AND no rows need recalc
        if (newTier === oldTier) {
          // Still check if any rows have stale tier_at_write
          const staleRow = await env.DB.prepare(
            `SELECT COUNT(*) AS c FROM commission_payments
              WHERE referrer_id = ?
                AND (tier_at_write IS NULL OR tier_at_write != ?)
                AND (commission_source IS NULL OR commission_source != 'support_tier')`
          ).bind(referrer.id, newTier).first();
          if ((staleRow.c || 0) === 0) {
            return json({ ok: true, no_change: true, tier: newTier, rate: newRate });
          }
        }

        // Update partner_tier on referrer (idempotent — same value if no change)
        await env.DB.prepare(
          `UPDATE referrers SET partner_tier = ? WHERE id = ?`
        ).bind(newTier, referrer.id).run();

        // Chunked recalc: only rows where tier_at_write != newTier
        // CTO §1.3: tier_at_write is source of truth for safe idempotent recalc.
        // Skip support_tier rows — those are locked at 25% regardless of partner tier.
        const CHUNK = 200;
        const { results: rows } = await env.DB.prepare(
          `SELECT id, payment_amount, commission_value, tier_at_write
             FROM commission_payments
            WHERE referrer_id = ?
              AND (tier_at_write IS NULL OR tier_at_write != ?)
              AND (commission_source IS NULL OR commission_source != 'support_tier')
            ORDER BY id ASC
            LIMIT ?`
        ).bind(referrer.id, newTier, CHUNK).all();

        let recalculated = 0;
        let dollarDelta = 0;
        for (const r of rows || []) {
          const amt = Number(r.payment_amount) || 0;
          const oldVal = Number(r.commission_value) || 0;
          const newVal = Math.round(amt * newRate * 100) / 100;
          await env.DB.prepare(
            `UPDATE commission_payments
                SET commission_value  = ?,
                    commission_rate   = ?,
                    tier              = ?,
                    tier_at_write     = ?,
                    commission_source = 'milestone_recalc'
              WHERE id = ?`
          ).bind(newVal, newRate, newTier, newTier, r.id).run();
          recalculated += 1;
          dollarDelta += (newVal - oldVal);
        }

        // Check whether more rows remain
        const moreRow = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM commission_payments
            WHERE referrer_id = ?
              AND (tier_at_write IS NULL OR tier_at_write != ?)
              AND (commission_source IS NULL OR commission_source != 'support_tier')`
        ).bind(referrer.id, newTier).first();
        const more = (moreRow.c || 0) > 0;

        // Audit log: rate_adjustments (logged per chunk that recalculated)
        const dollarsRecalculated = Math.round(Math.abs(dollarDelta) * 100) / 100;
        if (recalculated > 0) {
          await env.DB.prepare(
            `INSERT INTO rate_adjustments
               (partner_id, old_rate, new_rate, trigger_event, affected_commission_count, total_dollars_recalculated, created_at)
             VALUES (?, ?, ?, ?, ?, ?, ?)`
          ).bind(
            partner_id, oldRate, newRate, trigger,
            recalculated, dollarsRecalculated,
            Math.floor(Date.now() / 1000)
          ).run();
        }

        return json({
          ok: true,
          partner_id,
          old_tier: oldTier, new_tier: newTier,
          old_rate: oldRate, new_rate: newRate,
          recalculated,
          dollar_delta: Math.round(dollarDelta * 100) / 100,
          chunk_size: CHUNK,
          more,
        });
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

        const { referrer_id, user_name, user_email, paypal_email, partner_tier, split_config } = body;
        if (!referrer_id) return err(400, "referrer_id required");

        // Build dynamic SET clause for only provided fields
        const sets = [];
        const binds = [];
        if (user_name !== undefined) { sets.push("user_name = ?"); binds.push(user_name); }
        if (user_email !== undefined) { sets.push("user_email = ?"); binds.push(user_email.trim().toLowerCase()); }
        if (paypal_email !== undefined) { sets.push("paypal_email = ?"); binds.push(paypal_email.trim()); }
        // SPEC C1: admin can change partner_tier (validated against TIER_RATES)
        if (partner_tier !== undefined) {
          const t = String(partner_tier).toLowerCase();
          if (!TIER_RATES[t]) return err(400, `invalid partner_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
          sets.push("partner_tier = ?"); binds.push(t);
        }
        // SPEC D2: admin can update split_config (accepts array or pre-stringified JSON)
        if (split_config !== undefined) {
          const sc = typeof split_config === "string" ? split_config : JSON.stringify(split_config);
          sets.push("split_config = ?"); binds.push(sc);
        }

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
          // C4: also clean v2 payouts (partner_id = referral_code)
          await env.DB.prepare(
            `DELETE FROM payout_requests_v2 WHERE partner_id = ? COLLATE NOCASE`
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
          // C1/D2: surface tier + rate for partner dashboard
          partner_tier: referrer.partner_tier || "silver",
          tier_rate: rateForTier(referrer.partner_tier),
          total_sales: referrer.total_sales || 0,
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

        // SPEC D2: parse split_config JSON for frontend renderSplitRows().
        // Accept array, pre-stringified JSON, or null/empty → []
        function parseSplit(s) {
          if (!s) return [];
          if (Array.isArray(s)) return s;
          try { return JSON.parse(s); } catch (_e) { return []; }
        }

        const affiliates = (referrers || []).map(r => ({
          id: r.id, name: r.user_name, email: r.user_email, code: r.referral_code,
          paypal_email: r.paypal_email || "", clicks: r.clicks || 0,
          total: r.total || 0, completed: r.completed || 0, pending: r.pending || 0,
          earnings: r.earnings || 0, joined: r.created_at,
          // SPEC D2 + C1: include partner_tier + split_config in response
          // so frontend renderSplitRows() can populate split rows.
          partner_tier: r.partner_tier || "silver",
          tier_rate: rateForTier(r.partner_tier),
          total_sales: r.total_sales || 0,
          split_config: parseSplit(r.split_config),
          history: histMap[r.id] || []
        }));

        return json({ affiliates, count: affiliates.length });
      }

      // GET /admin/payouts — list all payout requests (legacy + v2 merged)
      // SPEC C4: v2 table payout_requests_v2 holds partner-self requests with
      // $50 min CHECK. Legacy payout_requests retained for historical records.
      if (path === "/admin/payouts") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const legacyP = env.DB.prepare(
          `SELECT 'legacy' AS source, p.*, ref.user_name AS referrer_name, ref.user_email AS referrer_email,
                  ref.paypal_email AS referrer_paypal
           FROM payout_requests p
           LEFT JOIN referrers ref ON ref.id = p.referrer_id
           ORDER BY p.created_at DESC`
        ).all();
        const v2P = env.DB.prepare(
          `SELECT 'v2' AS source, p2.id, p2.partner_id, p2.amount, p2.payout_method, p2.paypal_email,
                  p2.status, p2.requested_at, p2.paid_at, p2.paid_via_split_id,
                  ref.user_name AS referrer_name, ref.user_email AS referrer_email,
                  ref.paypal_email AS referrer_paypal
           FROM payout_requests_v2 p2
           LEFT JOIN referrers ref ON ref.referral_code = p2.partner_id COLLATE NOCASE
           ORDER BY p2.requested_at DESC`
        ).all();
        const [legacy, v2] = await Promise.all([legacyP, v2P]);
        const merged = [...(legacy.results || []), ...(v2.results || [])];
        return json({ payouts: merged, count: merged.length });
      }

      // GET /admin/applications — list partner applications (SPEC C2)
      // Optional query: ?status=pending|approved|rejected|needs_30d_use
      if (path === "/admin/applications") {
        if (!(await requireAdmin(request, env))) return err(401, "unauthorized");
        const status = (url.searchParams.get("status") || "").trim();
        const stmt = status
          ? env.DB.prepare(
              `SELECT * FROM partner_applications WHERE status = ? ORDER BY applied_at DESC`
            ).bind(status)
          : env.DB.prepare(
              `SELECT * FROM partner_applications ORDER BY applied_at DESC`
            );
        const { results } = await stmt.all();
        return json({ applications: results || [], count: (results || []).length });
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

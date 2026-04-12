/**
 * GET /api/referral/leaderboard — Top referrers by completed referrals.
 *
 * Query: ?limit=10 (max 50)
 * D1 binding: REFERRAL_DB
 */
import { corsResponse, jsonResponse } from './_shared.js';

export async function onRequestOptions(context) {
  return corsResponse(context.request);
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const db = env.REFERRAL_DB;
  const url = new URL(request.url);

  let limit = parseInt(url.searchParams.get('limit') || '10', 10);
  if (isNaN(limit) || limit < 1) limit = 10;
  if (limit > 50) limit = 50;

  const result = await db
    .prepare(
      `SELECT r.user_name, r.referral_code,
              COALESCE(ref_counts.completed_count, 0) AS completed_count,
              COALESCE(rw_totals.total_earned, 0) AS total_earned
       FROM referrers r
       LEFT JOIN (
           SELECT referrer_id, COUNT(*) AS completed_count
           FROM referrals
           WHERE status = 'completed'
           GROUP BY referrer_id
       ) ref_counts ON ref_counts.referrer_id = r.id
       LEFT JOIN (
           SELECT referrer_id, SUM(reward_value) AS total_earned
           FROM rewards
           GROUP BY referrer_id
       ) rw_totals ON rw_totals.referrer_id = r.id
       ORDER BY completed_count DESC, total_earned DESC
       LIMIT ?`
    )
    .bind(limit)
    .all();

  const leaders = (result.results || []).map((row) => ({
    name: row.user_name || 'Anonymous',
    referral_code: row.referral_code,
    completed: row.completed_count,
    total_earned: Math.round(parseFloat(row.total_earned) * 100) / 100,
  }));

  return jsonResponse({ leaderboard: leaders }, 200, request);
}

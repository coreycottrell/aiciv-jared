/* PureBrain Universal Referral Tracker v2.0
 * First-touch attribution | 90-day cookie | < 20 lines of logic
 * Checks ?code=, ?ref=, and ?referral= URL parameters
 */
(function () {
  var COOKIE_NAME = 'pb_ref';
  var COOKIE_DAYS = 90;
  var CODE_RE = /^[A-Za-z0-9-]{4,16}$/;

  // Read URL params: ?ref=, ?code=, ?referral=
  var p = new URLSearchParams(window.location.search);
  var ref = p.get('ref') || p.get('code') || p.get('referral') || '';
  if (!ref || !CODE_RE.test(ref)) return;

  // First-touch: do NOT overwrite an existing cookie
  if (document.cookie.match(new RegExp('(?:^|;)\\s*' + COOKIE_NAME + '='))) return;

  // Set 90-day cookie
  var exp = new Date();
  exp.setDate(exp.getDate() + COOKIE_DAYS);
  document.cookie = COOKIE_NAME + '=' + encodeURIComponent(ref.toUpperCase()) +
    '; expires=' + exp.toUTCString() + '; path=/; SameSite=Lax';

  // Mirror to localStorage (best-effort)
  try { localStorage.setItem(COOKIE_NAME, ref.toUpperCase()); } catch (e) {}

  // Fire server-side click-tracking (non-blocking)
  try {
    fetch('https://app.purebrain.ai/api/referral/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ referral_code: ref.toUpperCase() }),
      keepalive: true
    }).catch(function () {});
  } catch (e) {}
})();

/* Global helper: read stored referral code at payment time */
window.getPbRef = function () {
  try {
    var ls = localStorage.getItem('pb_ref');
    if (ls && /^[A-Za-z0-9-]{4,16}$/.test(ls)) return ls;
  } catch (e) {}
  var m = document.cookie.match(/(?:^|;)\s*pb_ref=([^;]+)/);
  if (m) {
    var d = decodeURIComponent(m[1]);
    if (/^[A-Za-z0-9-]{4,16}$/.test(d)) return d;
  }
  return null;
};

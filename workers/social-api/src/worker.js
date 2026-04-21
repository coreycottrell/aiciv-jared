/**
 * social-api Worker — multi-tenant social posting platform backend
 *
 * D1 binding: env.DB = purebrain-social
 *
 * Endpoints:
 *   GET  /health
 *   POST /api/login                       — email/password → session token
 *   GET  /api/sso/exchange?token=...      — portal SSO handoff
 *   GET  /api/me                          — current user (requires auth)
 *   GET  /api/content                     — list user's content (filters: status, platform, limit)
 *   POST /api/content                     — create draft
 *   PATCH /api/content/:id                — update (edit/approve/reschedule)
 *   GET  /api/content/team                — team aggregate (scheduled+posted only, read-only)
 *   GET  /api/content/ready               — ContentRouter polling (leader/system role only)
 *
 * Auth: bearer token in Authorization header OR social_session cookie
 * Sessions: 12h lifetime, stored in `sessions` table
 *
 * SSO from portal: HMAC-signed {user_id, exp, redirect} → creates local session
 */

const SESSION_DURATION_MS = 12 * 60 * 60 * 1000; // 12h
const PBKDF2_ITER = 100000;

// ---------- H1: Rate limiting (per isolate, per IP) ----------
const LOGIN_FAILED_LIMIT = 5;
const LOGIN_FAILED_WINDOW_MS = 15 * 60 * 1000;
const LOGIN_TOTAL_LIMIT = 20;
const LOGIN_TOTAL_WINDOW_MS = 60 * 60 * 1000;

async function rlCheckD1(bucket, identifier, windowMs, limit, env) {
  const cutoff = new Date(Date.now() - windowMs).toISOString();
  const { results } = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM rate_limits WHERE bucket = ? AND identifier = ? AND recorded_at > ?"
  ).bind(bucket, identifier, cutoff).all();
  const count = (results && results[0] && results[0].c) || 0;
  if (count >= limit) return false;
  await env.DB.prepare(
    "INSERT INTO rate_limits (bucket, identifier) VALUES (?, ?)"
  ).bind(bucket, identifier).run();
  // Opportunistic cleanup of old entries
  if (Math.random() < 0.1) {
    const purge = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    await env.DB.prepare("DELETE FROM rate_limits WHERE recorded_at < ?").bind(purge).run();
  }
  return true;
}

async function rlRemoveLatest(bucket, identifier, env) {
  // Called after successful login to "uncount" the speculative failed entry
  await env.DB.prepare(
    "DELETE FROM rate_limits WHERE id = (SELECT id FROM rate_limits WHERE bucket = ? AND identifier = ? ORDER BY recorded_at DESC LIMIT 1)"
  ).bind(bucket, identifier).run();
}

const DUMMY_PW_HASH = "0000000000000000000000000000000000000000000000000000000000000000:dead0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";

// ---------- C1: AES-256-GCM encryption for credentials at rest ----------
async function _deriveKey(rawKey) {
  const keyMaterial = await crypto.subtle.importKey("raw", new TextEncoder().encode(rawKey), "PBKDF2", false, ["deriveKey"]);
  const salt = new TextEncoder().encode("purebrain-social-v1");
  return crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" }, keyMaterial, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
}

async function encryptSecret(plaintext, env) {
  if (!plaintext) return null;
  if (!env.CREDS_ENC_KEY) throw new Error("CREDS_ENC_KEY not configured");
  const key = await _deriveKey(env.CREDS_ENC_KEY);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(plaintext));
  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return "enc:v1:" + btoa(String.fromCharCode(...combined));
}

async function decryptSecret(encoded, env) {
  if (!encoded) return null;
  if (!encoded.startsWith("enc:v1:")) return encoded;
  if (!env.CREDS_ENC_KEY) throw new Error("CREDS_ENC_KEY not configured");
  const b64 = encoded.slice(7);
  const combined = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const iv = combined.slice(0, 12);
  const ciphertext = combined.slice(12);
  const key = await _deriveKey(env.CREDS_ENC_KEY);
  const plaintext = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ciphertext);
  return new TextDecoder().decode(plaintext);
}


const FRONTEND_HTML = `<!-- VERIFIED BUILD: 3185 lines, LinkedIn preview + Trello cards, 2026-04-20 10:15 UTC -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>social · PureBrain</title>
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Oswald:wght@500;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#080a12;
  --surface:rgba(255,255,255,0.03);
  --surface-hover:rgba(255,255,255,0.05);
  --border:rgba(255,255,255,0.07);
  --border-focus:rgba(42,147,193,0.45);
  --text:rgba(255,255,255,0.88);
  --text-muted:rgba(255,255,255,0.48);
  --text-dim:rgba(255,255,255,0.28);
  --blue:#2a93c1;
  --blue-dim:rgba(42,147,193,0.15);
  --orange:#f1420b;
  --orange-dim:rgba(241,66,11,0.15);
  --green:#22c55e;
  --green-dim:rgba(34,197,94,0.15);
  --yellow:#eab308;
  --yellow-dim:rgba(234,179,8,0.15);
  --red:#ef4444;
  --red-dim:rgba(239,68,68,0.15);
  --glow-blue:rgba(42,147,193,0.2);
  --glow-orange:rgba(241,66,11,0.18);
  --radius:8px;
  --radius-lg:12px;
}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;min-height:100vh;min-height:100dvh;overflow-x:hidden;touch-action:manipulation}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 70% 50% at 50% -10%,var(--glow-blue),transparent 70%),radial-gradient(ellipse 50% 40% at 80% 100%,var(--glow-orange),transparent 70%);pointer-events:none;z-index:0;animation:drift 18s ease-in-out infinite alternate}
@keyframes drift{0%{opacity:.75}50%{opacity:1}100%{opacity:.75}}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}

.app{position:relative;z-index:1;min-height:100vh;min-height:100dvh;display:flex;flex-direction:column}

/* ---------- AUTH GATE ---------- */
.auth-gate{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;min-height:100dvh;padding:24px;animation:fadeUp .5s ease}
.auth-shell{width:100%;max-width:380px;background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:36px 32px;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
.auth-logo{font-family:'Oswald',sans-serif;font-size:14px;font-weight:500;letter-spacing:.35em;text-transform:uppercase;text-align:center;color:var(--text-muted);margin-bottom:8px}
.auth-logo .blue{color:var(--blue)}.auth-logo .orange{color:var(--orange)}
.auth-title{font-size:26px;font-weight:800;color:#fff;text-align:center;letter-spacing:-.02em;margin-bottom:8px}
.auth-sub{font-size:13px;color:var(--text-muted);text-align:center;margin-bottom:28px}
.field{margin-bottom:16px}
.field label{display:block;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--text-muted);margin-bottom:6px}
.field input,.field select,.field textarea{width:100%;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:10px;padding:14px 16px;color:#fff;font-family:inherit;font-size:15px;transition:border-color .2s,background .2s;resize:vertical}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--border-focus);background:rgba(255,255,255,0.06)}
.field textarea{min-height:140px;font-size:14px;line-height:1.5}
.btn-auth{display:block;width:100%;background:linear-gradient(135deg,var(--blue),var(--orange));color:#fff;border:none;border-radius:10px;padding:15px;font-family:inherit;font-size:14px;font-weight:700;letter-spacing:.04em;cursor:pointer;transition:transform .15s,box-shadow .2s}
.btn-auth:hover{transform:translateY(-1px);box-shadow:0 8px 24px var(--glow-blue)}
.btn-auth:active{transform:translateY(0)}
.btn-auth:disabled{opacity:.5;cursor:wait}
.auth-error{color:var(--red);font-size:13px;text-align:center;margin-top:12px;min-height:18px}

/* ---------- MAIN APP ---------- */
.topbar{position:sticky;top:0;z-index:100;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);background:rgba(8,10,18,.8);border-bottom:1px solid var(--border);padding:14px 20px;padding-top:max(14px,env(safe-area-inset-top));display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{font-family:'Oswald',sans-serif;font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:var(--text)}
.brand .blue{color:var(--blue)}.brand .orange{color:var(--orange)}
.user-chip{display:flex;align-items:center;gap:10px;padding:6px 10px 6px 6px;background:var(--surface);border:1px solid var(--border);border-radius:100px;cursor:pointer;font-size:13px;color:var(--text);transition:border-color .2s}
.user-chip:hover{border-color:var(--border-focus)}
.user-chip .avatar{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#fff}

.tabs{display:flex;gap:4px;padding:12px 20px;overflow-x:auto;-webkit-overflow-scrolling:touch;border-bottom:1px solid var(--border)}
.tab{flex-shrink:0;padding:10px 16px;font-size:13px;font-weight:600;color:var(--text-muted);cursor:pointer;border-radius:8px;transition:all .2s;background:transparent;border:1px solid transparent;position:relative}
.tab:hover{color:var(--text);background:var(--surface-hover)}
.tab.active{color:#fff;background:var(--surface);border-color:var(--border-focus);box-shadow:0 0 0 1px var(--border-focus)}
.tab .badge{position:absolute;top:-4px;right:-4px;background:var(--orange);color:#fff;font-size:10px;font-weight:700;padding:1px 6px;border-radius:10px;min-width:18px;text-align:center}

.panel{display:none;padding:24px 20px 40px;max-width:1200px;margin:0 auto;width:100%}
.panel.active{display:block;animation:fadeUp .35s ease}

/* ---------- BUTTONS ---------- */
.btn{padding:8px 16px;border:none;border-radius:var(--radius);font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;display:inline-flex;align-items:center;gap:6px;font-family:inherit}
.btn:hover{filter:brightness(1.15)}.btn:active{transform:scale(0.97)}
.btn-primary{background:var(--blue);color:#fff}
.btn-orange{background:var(--orange);color:#fff}
.btn-green{background:var(--green);color:#fff}
.btn-red{background:var(--red);color:#fff}
.btn-ghost{background:transparent;color:var(--text-muted);border:1px solid var(--border)}
.btn-ghost:hover{color:var(--text);border-color:var(--text-muted)}
.btn-sm{padding:5px 10px;font-size:12px}
.btn-lg{padding:12px 24px;font-size:15px}

/* ---------- CARDS ---------- */
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;margin-bottom:16px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px}
.card-title{font-size:16px;font-weight:700;color:#fff}

/* ---------- SECTION HEADER ---------- */
.section-head{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px}
.section-title{font-size:22px;font-weight:800;letter-spacing:-.01em;color:#fff}
.section-sub{font-size:12px;color:var(--text-muted)}

/* ---------- FORM ---------- */
.form-group{margin-bottom:16px}
.form-label{display:block;font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted);margin-bottom:6px}

/* ---------- CHIPS ---------- */
.chip{padding:7px 14px;font-size:12px;font-weight:600;color:var(--text-muted);background:var(--surface);border:1px solid var(--border);border-radius:100px;cursor:pointer;transition:all .2s}
.chip:hover{color:var(--text);border-color:var(--border-focus)}
.chip.active{color:#fff;background:linear-gradient(135deg,rgba(42,147,193,.2),rgba(241,66,11,.15));border-color:var(--border-focus)}

/* ---------- POST CARDS (list view) ---------- */
.timeline{display:flex;flex-direction:column;gap:14px}
.post-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:border-color .2s,transform .2s;animation:fadeUp .3s ease}
.post-card:hover{border-color:var(--border-focus);transform:translateY(-1px)}
.post-meta{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.post-platform{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--text-muted)}
.post-platform .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.dot.linkedin{background:#0a66c2}.dot.twitter{background:#1d9bf0}.dot.bluesky{background:#0085ff}
.dot.threads{background:#fff}.dot.facebook{background:#1877f2}.dot.instagram{background:#e4405f}
.dot.tiktok{background:#69c9d0}.dot.reddit{background:#ff4500}
.post-time{font-size:12px;color:var(--text-dim);font-variant-numeric:tabular-nums}
.post-body{font-size:15px;line-height:1.6;color:var(--text);white-space:pre-wrap;margin-bottom:12px}
.post-actions{display:flex;gap:8px;flex-wrap:wrap}
.action-btn{padding:8px 14px;font-size:12px;font-weight:600;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text-muted);cursor:pointer;transition:all .15s;font-family:inherit}
.action-btn:hover{color:#fff;border-color:var(--border-focus)}
.action-btn.approve{color:var(--green);border-color:rgba(34,197,94,.3)}
.action-btn.approve:hover{background:rgba(34,197,94,.1)}
.action-btn.reject{color:var(--red);border-color:rgba(239,68,68,.3)}
.action-btn.reject:hover{background:rgba(239,68,68,.1)}
.action-btn.edit{color:var(--blue);border-color:rgba(42,147,193,.3)}
.action-btn.edit:hover{background:rgba(42,147,193,.1)}
.action-btn.post-now{color:var(--orange);border-color:rgba(241,66,11,.3)}
.action-btn.post-now:hover{background:rgba(241,66,11,.1)}
.action-btn.delete{color:var(--red);border-color:rgba(239,68,68,.2)}
.action-btn.delete:hover{background:rgba(239,68,68,.1)}
.action-btn.feedback{color:var(--yellow);border-color:rgba(234,179,8,.3)}
.action-btn.feedback:hover{background:rgba(234,179,8,.1)}
.status-badge{display:inline-block;padding:3px 10px;font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;border-radius:100px}
.status-draft{background:rgba(255,255,255,.08);color:var(--text-muted)}
.status-scheduled{background:var(--blue-dim);color:var(--blue)}
.status-posted{background:var(--green-dim);color:var(--green)}
.status-failed{background:var(--red-dim);color:var(--red)}
.status-rejected{background:var(--red-dim);color:var(--red)}
.status-pending_approval{background:var(--orange-dim);color:var(--orange)}

/* Post image thumbnail */
.post-thumb{width:64px;height:64px;border-radius:var(--radius);overflow:hidden;flex-shrink:0;border:1px solid var(--border);background:rgba(255,255,255,0.02)}
.post-thumb img{width:100%;height:100%;object-fit:cover;cursor:pointer}

/* ---------- FEEDBACK BADGES on cards ---------- */
.post-feedback-badge{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;margin-left:6px;vertical-align:middle}
.badge-feedback{background:var(--yellow-dim);color:var(--yellow)}
.badge-flagged{background:var(--red-dim);color:var(--red)}
.badge-resolved{background:var(--green-dim);color:var(--green)}

/* ---------- FEEDBACK PANEL (from TASK3 visual feedback module) ---------- */
.fp-type-buttons{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.fp-type-btn{padding:6px 12px;font-size:12px;border:2px solid;border-radius:6px;cursor:pointer;font-weight:500;transition:all 0.15s;background:transparent}
.fp-type-btn.selected{box-shadow:0 0 0 2px var(--blue)}
.fp-type-btn[data-type="flag_image"]{color:var(--red);border-color:var(--red);background:var(--red-dim)}
.fp-type-btn[data-type="replace_image"]{color:var(--yellow);border-color:var(--yellow);background:var(--yellow-dim)}
.fp-type-btn[data-type="edit_text"]{color:var(--blue);border-color:var(--blue);background:var(--blue-dim)}
.fp-type-btn[data-type="general"]{color:var(--text-muted);border-color:var(--border);background:var(--surface)}
.fp-type-btn:hover{opacity:0.85;transform:translateY(-1px)}
.fp-selected-type{min-height:20px;margin-bottom:8px}
.fb-badge{font-weight:700;display:inline-block;padding:2px 6px;border-radius:8px;font-size:10px;color:#fff;vertical-align:middle;margin-left:4px}

/* ---------- CALENDAR VIEWS ---------- */
/* View toggle */
.view-toggle{display:flex;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
.view-toggle-btn{padding:7px 16px;background:none;border:none;color:var(--text-muted);font-size:13px;font-weight:500;cursor:pointer;transition:all .15s;font-family:inherit}
.view-toggle-btn:hover{color:var(--text);background:var(--surface-hover)}
.view-toggle-btn.active{background:var(--blue);color:#fff}

/* Calendar nav */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:12px;flex-wrap:wrap}
.cal-nav-center{display:flex;align-items:center;gap:12px}
.cal-nav-title{font-size:18px;font-weight:700;min-width:180px;text-align:center;color:#fff}
.cal-nav-btn{width:36px;height:36px;border-radius:var(--radius);border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s;font-family:inherit}
.cal-nav-btn:hover{background:var(--surface-hover);border-color:var(--blue)}
.cal-today-btn{padding:6px 14px;border-radius:var(--radius);border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:12px;font-weight:600;cursor:pointer;transition:all .15s;font-family:inherit}
.cal-today-btn:hover{color:var(--blue);border-color:var(--blue)}

/* Content type badges */
.ct-badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.ct-badge-blog{background:var(--blue-dim);color:var(--blue)}
.ct-badge-linkedin{background:var(--orange-dim);color:var(--orange)}
.ct-badge-newsletter{background:var(--green-dim);color:var(--green)}
.ct-badge-bluesky{background:rgba(99,102,241,0.15);color:#818cf8}

/* ---- MONTH VIEW ---- */
.month-view{display:none}
.month-view.visible{display:block}
.month-grid{display:grid;grid-template-columns:repeat(7,1fr);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;background:var(--surface)}
.month-day-header{padding:10px 4px;text-align:center;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-dim);background:rgba(0,0,0,0.3);border-bottom:1px solid var(--border)}
.month-cell{min-height:110px;padding:6px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);background:var(--surface);transition:background .15s;position:relative;overflow:hidden}
.month-cell:nth-child(7n){border-right:none}
.month-cell:hover{background:var(--surface-hover)}
.month-cell.other-month{opacity:.35}
.month-cell.today{background:rgba(42,147,193,0.06);box-shadow:inset 0 0 0 2px var(--blue)}
.month-date{font-size:13px;font-weight:600;color:var(--text-dim);margin-bottom:4px;display:flex;align-items:center;justify-content:space-between}
.month-cell.today .month-date{color:var(--blue)}
.month-date-num{width:24px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:50%}
.month-cell.today .month-date-num{background:var(--blue);color:#fff}
.month-card{padding:4px 6px;margin-bottom:3px;border-radius:4px;font-size:11px;line-height:1.3;cursor:pointer;transition:all .15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-left:3px solid transparent;background:rgba(0,0,0,0.2)}
.month-card:hover{filter:brightness(1.2);transform:translateX(2px)}
.month-card.type-blog{border-left-color:var(--blue);color:var(--blue)}
.month-card.type-linkedin{border-left-color:var(--orange);color:var(--orange)}
.month-card.type-newsletter{border-left-color:var(--green);color:var(--green)}
.month-card.type-bluesky{border-left-color:#6366f1;color:#818cf8}
.month-card.type-other{border-left-color:var(--text-dim);color:var(--text-dim)}
.month-card-time{font-size:9px;opacity:.7;font-weight:600}
.month-card-status{display:inline-block;width:6px;height:6px;border-radius:50%;margin-left:3px;vertical-align:middle}
.month-card-status.s-draft{background:var(--yellow)}.month-card-status.s-scheduled{background:var(--blue)}
.month-card-status.s-posted{background:var(--green)}.month-card-status.s-failed{background:var(--red)}
.month-overflow{font-size:10px;color:var(--text-dim);padding:2px 6px;cursor:pointer;font-weight:600}
.month-overflow:hover{color:var(--blue)}

/* ---- WEEK VIEW ---- */
.week-view{display:none}
.week-view.visible{display:block}
.week-grid{display:grid;grid-template-columns:80px repeat(7,1fr);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;background:var(--surface)}
.week-header{padding:12px 8px;text-align:center;background:rgba(0,0,0,0.3);border-bottom:1px solid var(--border);border-right:1px solid var(--border);font-size:12px;font-weight:600;color:var(--text-dim)}
.week-header:last-child{border-right:none}
.week-header.today{color:var(--blue);background:rgba(42,147,193,0.08)}
.week-header-date{font-size:22px;font-weight:800;color:var(--text);line-height:1;margin-top:2px}
.week-header.today .week-header-date{color:var(--blue)}
.week-slot-label{padding:10px 8px;font-size:11px;font-weight:600;color:var(--text-dim);background:rgba(0,0,0,0.2);border-right:1px solid var(--border);border-bottom:1px solid var(--border);display:flex;align-items:flex-start;justify-content:center;text-align:center;min-height:80px}
.week-cell{padding:6px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);min-height:80px;background:var(--surface);transition:background .15s}
.week-cell:nth-child(8n){border-right:none}
.week-cell:hover{background:var(--surface-hover)}
.week-post-chip{padding:5px 8px;margin-bottom:4px;border-radius:5px;font-size:11px;font-weight:500;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:all .15s;border-left:3px solid transparent;background:rgba(0,0,0,0.2);line-height:1.3}
.week-post-chip:hover{filter:brightness(1.2);transform:translateX(2px)}
.week-post-chip.blog{border-left-color:var(--blue);color:var(--blue)}
.week-post-chip.linkedin{border-left-color:var(--orange);color:var(--orange)}
.week-post-chip.newsletter{border-left-color:var(--green);color:var(--green)}
.week-post-chip.bluesky{border-left-color:#6366f1;color:#818cf8}
.week-post-chip.other{border-left-color:var(--text-dim);color:var(--text-dim)}

/* Week legend */
.week-legend{display:flex;gap:16px;padding:12px 16px;flex-wrap:wrap;font-size:12px;color:var(--text-dim)}
.week-legend-item{display:flex;align-items:center;gap:6px}
.week-legend-dot{width:10px;height:10px;border-radius:3px}

/* ---- LIST VIEW ---- */
.filter-bar{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;margin-bottom:20px}
.filter-bar .form-group{flex:1;min-width:140px;margin-bottom:0}
.filter-bar select,.filter-bar input[type="text"],.filter-bar input[type="date"]{width:100%;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:var(--radius);color:#fff;font-size:13px;font-family:inherit}

/* Post list item */
.post-list-item{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;margin-bottom:10px;display:flex;align-items:center;gap:16px;transition:all .15s;cursor:pointer}
.post-list-item:hover{background:var(--surface-hover);border-color:var(--border-focus)}
.post-platforms{display:flex;gap:4px;flex-shrink:0}
.post-platforms .platform-icon{width:24px;height:24px;font-size:10px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff}
.pi-instagram{background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)}
.pi-facebook{background:#1877f2}.pi-linkedin{background:#0a66c2}.pi-twitter{background:#1da1f2}
.pi-bluesky{background:#0085ff}.pi-tiktok{background:#69c9d0}.pi-reddit{background:#ff4500}
.post-preview{flex:1;min-width:0}
.post-preview-text{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text)}
.post-meta-line{font-size:12px;color:var(--text-dim);margin-top:2px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.post-status-pill{padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;flex-shrink:0}

/* ---------- ANALYTICS ---------- */
.analytics-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-bottom:24px}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px 16px;text-align:center;backdrop-filter:blur(12px)}
.stat-card .stat-platform{font-size:12px;color:var(--text-muted);margin-bottom:4px;display:flex;align-items:center;justify-content:center;gap:6px}
.stat-card .stat-value{font-size:28px;font-weight:800;color:#fff;letter-spacing:-.02em;margin-bottom:2px}
.stat-card .stat-label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted)}
.bar-chart{display:flex;align-items:flex-end;gap:16px;height:200px;padding:0 20px;border-bottom:1px solid var(--border);margin-bottom:8px}
.bar-col{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.bar{width:40px;border-radius:4px 4px 0 0;min-height:4px;transition:height .6s ease}
.bar-label{font-size:11px;color:var(--text-dim);margin-top:8px;text-align:center}
.bar-value{font-size:11px;font-weight:600;margin-bottom:4px;color:var(--text)}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{text-align:left;padding:10px 12px;color:var(--text-dim);font-weight:500;border-bottom:1px solid var(--border);font-size:12px;text-transform:uppercase;letter-spacing:.5px}
.data-table td{padding:10px 12px;border-bottom:1px solid var(--border)}
.data-table tr:hover td{background:var(--surface-hover)}

/* ---------- ADVANCED ANALYTICS (Morphe Phase 2) ---------- */
.adv-bar-row{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.adv-bar-label{width:90px;font-size:12px;font-weight:600;color:var(--text-muted);text-transform:capitalize;flex-shrink:0;display:flex;align-items:center;gap:6px}
.adv-bar-track{flex:1;height:28px;background:rgba(255,255,255,0.04);border-radius:6px;overflow:hidden;position:relative}
.adv-bar-fill{height:100%;border-radius:6px;transition:width .6s ease;display:flex;align-items:center;padding-left:10px;font-size:11px;font-weight:600;color:#fff;min-width:0}
.adv-bar-stats{width:160px;font-size:11px;color:var(--text-dim);display:flex;gap:8px;flex-shrink:0}
.adv-type-pill{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;background:var(--surface);border:1px solid var(--border);font-size:12px;font-weight:600;color:var(--text)}
.adv-type-pill .pill-count{background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;color:#fff}
.adv-status-pill{padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;display:inline-block}
.adv-status-posted{background:rgba(34,197,94,.15);color:#22c55e}
.adv-status-scheduled{background:rgba(59,130,246,.15);color:#3b82f6}
.adv-status-draft{background:rgba(234,179,8,.15);color:#eab308}
.adv-status-pending_approval{background:rgba(249,115,22,.15);color:#f97316}
.adv-status-failed{background:rgba(239,68,68,.15);color:#ef4444}
#card-pending .stat-value.has-pending{color:#f97316}
.table-wrap{overflow-x:auto}

/* ---------- MEDIA LIBRARY ---------- */
.media-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}
.media-item{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;position:relative;transition:border-color .2s}
.media-item:hover{border-color:var(--border-focus)}
.media-thumb-box{width:100%;height:120px;background:rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;overflow:hidden}
.media-thumb-box img{width:100%;height:100%;object-fit:cover}
.media-info{padding:10px}
.media-name{font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text)}
.media-meta{font-size:11px;color:var(--text-dim);margin-top:2px}
.media-delete{position:absolute;top:6px;right:6px;width:24px;height:24px;background:rgba(0,0,0,0.6);color:var(--red);border:none;border-radius:50%;cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:center;font-family:inherit;transition:all .15s}
.media-delete:hover{background:var(--red);color:#fff}
.drop-zone{border:2px dashed var(--border);border-radius:var(--radius-lg);padding:32px;text-align:center;color:var(--text-dim);cursor:pointer;transition:all .2s}
.drop-zone:hover,.drop-zone.dragover{border-color:var(--blue);background:rgba(42,147,193,0.05)}
.drop-zone-icon{font-size:32px;margin-bottom:8px}
.drop-zone-text{font-size:14px}
.drop-zone-sub{font-size:12px;margin-top:4px}

/* ---------- TEAM VIEW ---------- */
.team-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.team-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px;backdrop-filter:blur(12px);transition:border-color .2s,transform .2s}
.team-card:hover{border-color:var(--border-focus);transform:translateY(-2px)}
.team-card-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.team-card-avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;font-size:14px}
.team-card-name{font-size:14px;font-weight:700;color:#fff}
.team-card-email{font-size:11px;color:var(--text-dim)}
.team-card-body{font-size:13px;color:var(--text);line-height:1.5;margin-bottom:10px;-webkit-line-clamp:3;-webkit-box-orient:vertical;display:-webkit-box;overflow:hidden}
.team-card-footer{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-dim)}

/* ---------- ACCOUNTS ---------- */
.account-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.account-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px}
.account-info{flex:1;min-width:0}
.account-platform{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted)}
.account-handle{font-size:14px;font-weight:600;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.health-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.health-dot.healthy{background:var(--green);box-shadow:0 0 6px rgba(34,197,94,.5)}
.health-dot.unknown{background:var(--text-dim)}.health-dot.degraded{background:var(--orange)}.health-dot.failed{background:var(--red)}
.connect-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:16px}
.connect-btn{padding:18px 14px;background:var(--surface);border:1px solid var(--border);border-radius:12px;cursor:pointer;text-align:center;transition:all .2s}
.connect-btn:hover{border-color:var(--border-focus);background:var(--surface-hover);transform:translateY(-2px)}
.connect-btn .dot{width:12px;height:12px;border-radius:50%;margin:0 auto 8px}
.connect-btn-label{font-size:13px;font-weight:600;color:#fff}

/* ---------- COMPOSE ---------- */
.compose-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px;backdrop-filter:blur(12px)}
.content-type-selector{display:flex;gap:6px;flex-wrap:wrap}
.content-type-btn{padding:8px 16px;border:1px solid var(--border);border-radius:100px;background:transparent;color:var(--text-muted);font-size:13px;font-weight:600;cursor:pointer;transition:all .2s;font-family:inherit}
.content-type-btn:hover{color:var(--text);border-color:var(--border-focus)}
.content-type-btn.active-linkedin{color:var(--orange);border-color:var(--orange);background:var(--orange-dim)}
.content-type-btn.active-blog{color:var(--blue);border-color:var(--blue);background:var(--blue-dim)}
.content-type-btn.active-newsletter{color:var(--green);border-color:var(--green);background:var(--green-dim)}
.content-type-btn.active-bluesky{color:#818cf8;border-color:#6366f1;background:rgba(99,102,241,0.15)}
.blog-fields{display:none;margin-bottom:16px;padding:16px;border:1px solid var(--border);border-radius:var(--radius-lg);background:rgba(42,147,193,0.03)}
.blog-fields.visible{display:block}
.blog-fields-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.banner-preview{display:none;width:100%;max-height:180px;object-fit:cover;border-radius:var(--radius);border:1px solid var(--border);margin-top:8px}
.banner-preview.visible{display:block}
.platform-selector{display:flex;flex-wrap:wrap;gap:8px}
.platform-check{display:flex;align-items:center;gap:8px;padding:8px 14px;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:var(--radius);cursor:pointer;font-size:13px;transition:all .15s;user-select:none;color:var(--text-muted)}
.platform-check:hover{border-color:var(--blue)}
.platform-check input{display:none}
.platform-check.checked{border-color:var(--blue);background:rgba(42,147,193,0.1);color:var(--text)}
.char-count{font-size:12px;color:var(--text-dim);text-align:right;margin-top:4px}
.char-count.warn{color:var(--yellow)}.char-count.over{color:var(--red)}
.char-pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.char-pill{padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:4px}
.preview-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.preview-thumb{width:80px;height:80px;border-radius:var(--radius);overflow:hidden;position:relative;border:1px solid var(--border)}
.preview-thumb img{width:100%;height:100%;object-fit:cover}
.preview-thumb .remove-thumb{position:absolute;top:2px;right:2px;width:20px;height:20px;background:var(--red);color:#fff;border:none;border-radius:50%;font-size:11px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.hashtag-chip{padding:5px 10px;font-size:12px;font-weight:600;color:var(--text-muted);background:transparent;border:1px solid var(--border);border-radius:100px;cursor:pointer;transition:all .15s}
.hashtag-chip:hover{color:var(--blue);border-color:var(--blue)}
.schedule-row{display:flex;align-items:flex-end;gap:12px;flex-wrap:wrap}
.schedule-row .form-group{flex:1;min-width:200px}
.schedule-row input[type="datetime-local"]{width:100%;padding:10px 12px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:var(--radius);color:#fff;font-size:14px;font-family:inherit}
.action-row{display:flex;gap:12px;justify-content:flex-end;padding-top:16px;border-top:1px solid var(--border);margin-top:16px}

/* ---------- EDIT MODAL + FEEDBACK ---------- */
.edit-modal-overlay{display:none;position:fixed;inset:0;z-index:10003;background:rgba(0,0,0,0.8);justify-content:center;align-items:center;padding:20px}
.edit-modal-overlay.active{display:flex}
.edit-modal{background:rgba(14,17,32,0.98);border:1px solid var(--border);border-radius:var(--radius-lg);width:95%;max-width:1400px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 12px 48px rgba(0,0,0,0.6);backdrop-filter:blur(20px)}
.edit-modal-header{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-bottom:1px solid var(--border);flex-shrink:0}
.edit-modal-header h2{font-size:18px;font-weight:700;color:#fff}
.edit-modal-close{width:36px;height:36px;border-radius:var(--radius);border:1px solid var(--border);background:transparent;color:var(--text-dim);font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s;font-family:inherit}
.edit-modal-close:hover{color:var(--red);border-color:var(--red)}
.edit-modal-body{display:flex;flex:1;overflow:hidden;min-height:0}
.edit-modal-left{flex:1;padding:24px;overflow-y:auto;border-right:1px solid var(--border)}
.edit-modal-right{width:360px;flex-shrink:0;display:flex;flex-direction:column;overflow:hidden}
.edit-modal-footer{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-top:1px solid var(--border);flex-shrink:0}
.edit-modal-center{width:380px;flex-shrink:0;display:flex;flex-direction:column;overflow-y:auto;padding:20px;border-right:1px solid var(--border);background:rgba(0,0,0,0.15)}
.edit-modal-center-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--text-dim);margin-bottom:12px;display:flex;align-items:center;gap:6px}
.post-preview-card{background:#fff;border-radius:8px;border:1px solid #e0e0e0;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#000;max-width:500px;width:100%}
.post-preview-card.twitter-preview{background:#000;border:1px solid #2f3336;color:#e7e9ea;border-radius:16px}
.post-preview-card.bluesky-preview{background:#fff;border:1px solid #d3d3d3;color:#000;border-radius:12px}
.preview-header{display:flex;gap:8px;padding:12px 16px;align-items:flex-start}
.preview-avatar{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px;flex-shrink:0}
.preview-avatar.li-avatar{background:linear-gradient(135deg,#0a66c2,#004182)}
.preview-avatar.tw-avatar{background:linear-gradient(135deg,#1d9bf0,#0d8ddb)}
.preview-avatar.bs-avatar{background:linear-gradient(135deg,#0085ff,#0066cc)}
.preview-header-info{flex:1;min-width:0}
.preview-name{font-weight:600;font-size:14px;line-height:1.3}
.twitter-preview .preview-name{color:#e7e9ea}
.preview-handle{font-size:13px;color:#536471;font-weight:400}
.twitter-preview .preview-handle{color:#71767b}
.preview-title{font-size:12px;color:#666;line-height:1.3}
.twitter-preview .preview-title{display:none}
.preview-time{font-size:12px;color:#999;line-height:1.4}
.twitter-preview .preview-time{color:#71767b}
.preview-body{padding:0 16px 12px;font-size:14px;line-height:1.5;white-space:pre-wrap;word-break:break-word}
.twitter-preview .preview-body{font-size:15px}
.preview-body .hashtag{color:#0a66c2;font-weight:600;cursor:pointer}
.twitter-preview .preview-body .hashtag{color:#1d9bf0}
.bluesky-preview .preview-body .hashtag{color:#0085ff}
.preview-body .mention{color:#0a66c2;font-weight:500}
.twitter-preview .preview-body .mention{color:#1d9bf0}
.bluesky-preview .preview-body .mention{color:#0085ff}
.preview-body .link{color:#0a66c2;text-decoration:underline}
.twitter-preview .preview-body .link{color:#1d9bf0}
.bluesky-preview .preview-body .link{color:#0085ff}
.preview-image-wrap{width:100%;overflow:hidden}
.preview-image{width:100%;max-height:300px;object-fit:cover;display:block}
.preview-actions{display:flex;justify-content:space-around;padding:8px 16px 10px;border-top:1px solid #e0e0e0;font-size:13px;color:#666;font-weight:600}
.twitter-preview .preview-actions{border-top:none;color:#71767b;font-size:13px;padding:4px 16px 12px}
.bluesky-preview .preview-actions{border-top:1px solid #e0e0e0;color:#666}
.preview-action-item{display:flex;align-items:center;gap:4px;cursor:default;user-select:none;font-size:13px}
.preview-char-counter{margin-top:10px;font-size:12px;font-weight:600;text-align:right;padding:0 4px}
.preview-char-green{color:#22c55e}
.preview-char-yellow{color:#eab308}
.preview-char-red{color:#ef4444}
.preview-empty-state{text-align:center;padding:32px 16px;color:#999;font-size:13px;font-style:italic}
.modal-img-preview{width:100%;max-height:320px;border-radius:var(--radius);border:1px solid var(--border);overflow:hidden;background:rgba(0,0,0,0.3);margin-bottom:16px;cursor:pointer;position:relative}
.modal-img-preview img{width:100%;height:100%;object-fit:contain;max-height:320px}
.modal-img-preview:hover::after{content:'Click to enlarge';position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,0.7);color:#fff;padding:4px 10px;border-radius:4px;font-size:11px}
.feedback-panel-header{padding:16px 20px;border-bottom:1px solid var(--border);font-size:14px;font-weight:700;display:flex;align-items:center;gap:8px;flex-shrink:0;color:#fff}
.feedback-actions{display:flex;flex-wrap:wrap;gap:8px;padding:12px 20px;border-bottom:1px solid var(--border);flex-shrink:0}
.feedback-input-area{padding:12px 20px;border-bottom:1px solid var(--border);display:none;flex-shrink:0}
.feedback-input-area.visible{display:block}
.feedback-input-area textarea{min-height:70px;font-size:13px;width:100%;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:var(--radius);padding:10px;color:#fff;font-family:inherit;resize:vertical}
.feedback-input-area .fb-input-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:8px}
.feedback-history{flex:1;overflow-y:auto;padding:12px 20px}
.feedback-item{padding:10px 12px;background:rgba(0,0,0,0.2);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;font-size:13px}
.feedback-item.resolved{opacity:.5;border-color:rgba(34,197,94,.3)}
.feedback-item-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.feedback-item-from{font-weight:600;color:var(--blue);font-size:12px}
.feedback-item-type{padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase}
.fb-type-flag_image{background:var(--red-dim);color:var(--red)}
.fb-type-replace_image{background:var(--yellow-dim);color:var(--yellow)}
.fb-type-edit_text{background:var(--blue-dim);color:var(--blue)}
.fb-type-general{background:rgba(255,255,255,0.06);color:var(--text-dim)}
.feedback-item-text{color:var(--text);line-height:1.5}
.feedback-item-time{font-size:11px;color:var(--text-dim);margin-top:4px;display:flex;align-items:center;justify-content:space-between}

/* ---------- TOAST ---------- */
.toast-container{position:fixed;top:20px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:8px}
.toast{padding:12px 20px;border-radius:var(--radius);font-size:13px;font-weight:500;box-shadow:0 4px 12px rgba(0,0,0,0.4);animation:slideIn .3s ease;min-width:260px;backdrop-filter:blur(12px)}
.toast-success{background:rgba(34,197,94,0.15);color:var(--green);border:1px solid rgba(34,197,94,.3)}
.toast-error{background:rgba(239,68,68,0.15);color:#fca5a5;border:1px solid rgba(239,68,68,.3)}
.toast-info{background:rgba(42,147,193,0.15);color:#93c5fd;border:1px solid rgba(42,147,193,.3)}

/* ---------- CONFIRM MODAL ---------- */
.confirm-modal-overlay{display:none;position:fixed;inset:0;z-index:10002;background:rgba(0,0,0,0.75);justify-content:center;align-items:center}
.confirm-modal-overlay.active{display:flex}
.confirm-modal{background:rgba(14,17,32,0.98);border:1px solid var(--border);border-radius:var(--radius-lg);padding:28px 32px;max-width:420px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,0.5);backdrop-filter:blur(20px)}
.confirm-modal h3{font-size:18px;margin-bottom:12px;color:var(--red)}
.confirm-modal p{font-size:14px;color:var(--text-muted);margin-bottom:20px;line-height:1.6}
.confirm-modal-actions{display:flex;gap:10px;justify-content:flex-end}

/* ---------- LIGHTBOX ---------- */
.lightbox-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);z-index:99999;align-items:center;justify-content:center;cursor:pointer}
.lightbox-overlay.active{display:flex}
.lightbox-overlay img{max-width:90vw;max-height:90vh;border-radius:var(--radius-lg);box-shadow:0 4px 32px rgba(0,0,0,0.6);cursor:default}
.lightbox-close{position:absolute;top:20px;right:28px;font-size:36px;color:#fff;cursor:pointer;z-index:100000;line-height:1;opacity:.8;transition:opacity .2s}
.lightbox-close:hover{opacity:1}

/* ---------- KANBAN BOARD ---------- */
.kanban-toolbar{display:flex;flex-wrap:wrap;gap:8px;padding:16px 20px 0;align-items:center}
.kanban-filter-chips{display:flex;gap:6px;flex-wrap:wrap}
.kanban-filter-chip{padding:6px 14px;font-size:12px;font-weight:600;color:var(--text-muted);background:var(--surface);border:1px solid var(--border);border-radius:100px;cursor:pointer;transition:all .2s;user-select:none}
.kanban-filter-chip:hover{color:var(--text);border-color:var(--border-focus)}
.kanban-filter-chip.active{color:#fff;background:linear-gradient(135deg,rgba(42,147,193,.2),rgba(241,66,11,.15));border-color:var(--border-focus)}
.kanban-board{display:flex;gap:16px;padding:16px 20px;height:calc(100vh - 160px);overflow-x:auto}
.kanban-col{flex:1;min-width:300px;display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.kanban-col-header{padding:14px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);flex-shrink:0}
.kanban-col-header .col-count{padding:2px 10px;border-radius:10px;font-size:11px;font-weight:700;min-width:22px;text-align:center}
.kanban-col-body{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:10px}
.kanban-col-body.drag-over{background:rgba(42,147,193,0.04);outline:2px dashed var(--border-focus);outline-offset:-4px;border-radius:0 0 12px 12px}
/* Trello-style kanban cards: visual-first with full-width images */
.kanban-card{flex-shrink:0;background:rgba(255,255,255,0.025);border:1px solid var(--border);border-radius:10px;overflow:hidden;cursor:pointer;transition:border-color .15s,transform .15s,box-shadow .15s;position:relative;display:flex;flex-direction:column}
.kanban-card:hover{border-color:var(--border-focus);transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,0.35)}
.kanban-card.dragging{opacity:.5;transform:scale(0.96);box-shadow:0 8px 32px rgba(0,0,0,0.4)}
.kanban-card-bar{height:3px;flex-shrink:0}
.kanban-card-thumb{width:100%;max-height:180px;overflow:hidden;background:rgba(0,0,0,.2)}
.kanban-card-thumb img{width:100%;height:auto;max-height:180px;object-fit:cover;display:block}
.kanban-card-thumb-empty{width:100%;height:100px;background:linear-gradient(135deg,rgba(42,147,193,0.06),rgba(241,66,11,0.04));display:flex;align-items:center;justify-content:center;color:var(--text-dim);font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.kanban-card-body{padding:12px;min-width:0}
.kanban-card-top{display:contents}
.kanban-card-info{min-width:0}
.kanban-card-info-row{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin-bottom:6px;font-size:11px;color:var(--text-dim)}
.kanban-card-info-row .sep{color:var(--text-dim);font-weight:400}
.kanban-card-badges{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;align-items:center}
.kanban-card-preview{font-size:13px;line-height:1.5;color:var(--text);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.kanban-card-meta{display:none}
.kanban-card-actions{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.kanban-platform-chip{padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;color:#fff}
.kanban-needs-image{padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;background:var(--red-dim);color:var(--red);text-transform:uppercase;letter-spacing:.3px}
.kanban-type-badge{padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;background:rgba(255,255,255,.06);color:var(--text-muted);text-transform:uppercase;letter-spacing:.3px}
.kanban-feedback-badge{padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;background:var(--yellow-dim);color:var(--yellow)}
.kanban-status-badge{padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.ks-draft{background:rgba(255,255,255,.08);color:var(--text-muted)}
.ks-needs_revision{background:rgba(245,158,11,.15);color:#f59e0b}
.ks-pending_approval{background:var(--orange-dim);color:var(--orange)}
.ks-scheduled{background:var(--blue-dim);color:var(--blue)}
.ks-approved{background:var(--blue-dim);color:var(--blue)}
.ks-posted{background:var(--green-dim);color:var(--green)}
.ks-rejected{background:var(--red-dim);color:var(--red)}
@keyframes kanbanSlide{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
.kanban-card-anim{animation:kanbanSlide .3s ease}
@media (max-width:768px){
  .kanban-board{flex-direction:column;height:auto;overflow-x:visible;padding:12px}
  .kanban-col{max-width:none;min-width:0;width:100%}
  .kanban-col-body{max-height:none;padding:8px}
  .kanban-col.collapsed .kanban-col-body{display:none}
  .kanban-col-header{cursor:pointer}
  .kanban-col-header::after{content:'';display:inline-block;width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid var(--text-dim);transition:transform .2s}
  .kanban-col.collapsed .kanban-col-header::after{transform:rotate(-90deg)}
  /* Mobile kanban cards — ensure content renders */
  .kanban-card{display:flex;flex-direction:column;width:100%;min-height:auto}
  .kanban-card-bar{height:3px;width:100%;display:block}
  .kanban-card-thumb{width:100%;max-height:160px;min-height:80px;overflow:hidden}
  .kanban-card-thumb img{width:100%;height:auto;min-height:80px;object-fit:cover;display:block}
  .kanban-card-thumb-empty{width:100%;height:60px;display:flex;align-items:center;justify-content:center}
  .kanban-card-body{padding:10px;display:block}
  .kanban-card-badges{display:flex;flex-wrap:wrap;gap:4px}
  .kanban-card-preview{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;font-size:13px;color:var(--text-muted)}
  .kanban-card-info-row{display:flex;flex-wrap:wrap;gap:4px;font-size:11px;color:var(--text-dim)}
  .kanban-card-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
  .kanban-platform-chip,.kanban-type-badge,.kanban-needs-image,.kanban-status-badge,.kanban-feedback-badge{font-size:9px;padding:2px 6px}
}

/* ---------- EMPTY ---------- */
.empty{text-align:center;padding:48px 20px;color:var(--text-dim)}
.empty-icon{font-size:32px;margin-bottom:12px;opacity:.4}
.empty-text{font-size:14px;color:var(--text-muted)}

/* ---------- RESPONSIVE ---------- */
@media (max-width:900px){
  .month-cell{min-height:80px}
  .month-card{font-size:10px;padding:3px 4px}
  .week-grid{grid-template-columns:60px repeat(7,1fr)}
  .week-slot-label{font-size:10px;padding:6px 4px}
  .week-post-chip{font-size:10px;padding:3px 5px}
  .edit-modal-body{flex-direction:column}
  .edit-modal-center{width:100%;border-right:none;border-top:1px solid var(--border);max-height:40vh}
  .edit-modal-right{width:100%;border-right:none;border-top:1px solid var(--border);max-height:40vh}
  .edit-modal-left{border-right:none}
}
@media (max-width:768px){
  .topbar{padding:12px 16px;padding-top:max(12px,env(safe-area-inset-top))}
  .brand{font-size:11px;letter-spacing:.22em}
  .panel{padding:20px 16px 32px}
  .section-title{font-size:18px}
  .post-card{padding:16px}
  .post-body{font-size:14px}
  .auth-shell{padding:28px 24px}
  .post-list-item{flex-direction:column;align-items:flex-start}
  .filter-bar{flex-direction:column}
  .action-row{flex-direction:column}.action-row .btn{width:100%;justify-content:center}
  .schedule-row{flex-direction:column}
  .bar-chart{height:140px}.bar{width:28px}
  .analytics-grid{grid-template-columns:repeat(2,1fr)}
  #analytics-summary{grid-template-columns:repeat(2,1fr) !important}
  .adv-bar-row{flex-wrap:wrap}
  .adv-bar-stats{width:100%;margin-top:4px}
}
@media (max-width:640px){
  .month-grid{grid-template-columns:repeat(7,1fr)}
  .month-cell{min-height:60px;padding:3px}
  .month-card{display:none}
  .month-date{font-size:11px}
  .month-cell.has-posts::after{content:'';display:block;width:6px;height:6px;border-radius:50%;background:var(--blue);margin:4px auto 0}
}

/* ---------- DRAG-DROP CALENDAR RESCHEDULING ---------- */
.post-card[draggable="true"],.month-card[draggable="true"],.week-post-chip[draggable="true"]{cursor:grab}
.post-card[draggable="true"]:active,.month-card[draggable="true"]:active,.week-post-chip[draggable="true"]:active{cursor:grabbing}
.day-cell.drag-over,.cal-day.drag-over,.cal-cell.drag-over,.month-cell.drag-over,.week-cell.drag-over{background:rgba(42,147,193,0.08);outline:2px dashed var(--blue);outline-offset:-2px}
.day-cell.drag-over-valid,.month-cell.drag-over-valid,.week-cell.drag-over-valid{background:rgba(34,197,94,0.12);outline-color:var(--green)}
.day-cell.drag-over-conflict,.month-cell.drag-over-conflict,.week-cell.drag-over-conflict{background:rgba(234,179,8,0.12);outline-color:var(--yellow)}

/* ---------- QUALITY GATE ---------- */
.qg-pass{background:var(--green-dim);border:1px solid rgba(34,197,94,.3);border-radius:6px;padding:10px 14px;color:var(--green);font-size:13px}
.qg-fail{background:var(--red-dim);border:1px solid rgba(239,68,68,.3);border-radius:6px;padding:10px 14px;color:#fca5a5;font-size:13px}
.qg-fail ul{margin:8px 0 0 0;padding-left:18px}
.qg-fail li{margin-bottom:6px}
.qg-fail code{background:rgba(255,255,255,0.06);padding:1px 5px;border-radius:3px;font-size:12px;color:var(--yellow)}
.qg-context{font-size:12px;color:var(--text-dim);display:block;margin-top:2px}
.qg-modal-overlay{display:none;position:fixed;inset:0;z-index:10004;background:rgba(0,0,0,0.8);justify-content:center;align-items:center;padding:20px}
.qg-modal-overlay.active{display:flex}
.qg-modal{background:rgba(14,17,32,0.98);border:1px solid var(--border);border-radius:var(--radius-lg);padding:28px 32px;max-width:560px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,0.5);backdrop-filter:blur(20px)}
.qg-modal h3{font-size:18px;margin-bottom:12px;color:var(--yellow)}
.qg-modal-actions{display:flex;gap:10px;justify-content:flex-end;margin-top:20px}

/* ---------- PLATFORM-SPECIFIC COMPOSER ---------- */
.platform-composer{margin-top:16px;border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;background:var(--surface)}
.platform-composer-toggle{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;cursor:pointer;font-size:13px;font-weight:600;color:var(--text-muted);transition:all .15s;user-select:none}
.platform-composer-toggle:hover{color:var(--text);background:var(--surface-hover)}
.platform-composer-toggle .arrow{transition:transform .2s;font-size:10px}
.platform-composer-toggle.expanded .arrow{transform:rotate(180deg)}
.platform-composer-body{display:none;border-top:1px solid var(--border)}
.platform-composer-body.visible{display:block}
.pc-section{border-bottom:1px solid var(--border)}
.pc-section:last-of-type{border-bottom:none}
.pc-section-header{display:flex;align-items:center;gap:8px;padding:10px 16px;cursor:pointer;font-size:13px;font-weight:600;color:var(--text-muted);transition:all .15s;user-select:none}
.pc-section-header:hover{background:var(--surface-hover);color:var(--text)}
.pc-section-header .pc-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.pc-section-header .pc-arrow{margin-left:auto;transition:transform .2s;font-size:10px}
.pc-section-header.expanded .pc-arrow{transform:rotate(180deg)}
.pc-section-body{display:none;padding:0 16px 12px}
.pc-section-body.visible{display:block}
.pc-section-body textarea{width:100%;min-height:80px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:var(--radius);padding:10px;color:#fff;font-family:inherit;font-size:13px;line-height:1.5;resize:vertical}
.pc-section-body textarea:focus{outline:none;border-color:var(--border-focus);background:rgba(255,255,255,0.06)}
.pc-char-count{font-size:11px;margin-top:4px;text-align:right}
.pc-char-count.ok{color:var(--text-dim)}
.pc-char-count.warn{color:var(--yellow)}
.pc-char-count.over{color:var(--red)}
.pc-actions{display:flex;gap:6px;margin-top:6px}
.pc-copy-all{padding:10px 16px;text-align:center}
</style>
</head>
<body>

<div class="app">
  <!-- AUTH GATE (default shown) -->
  <div class="auth-gate" id="auth-gate">
    <div class="auth-shell">
      <div class="auth-logo"><span class="blue">PURE</span><span class="orange">BR</span><span class="blue">AIN</span> . SOCIAL</div>

      <!-- LOGIN MODE -->
      <div id="auth-login-view">
        <h1 class="auth-title">Welcome back</h1>
        <p class="auth-sub">Sign in to your social command center.</p>
        <div class="field">
          <label for="login-email">Email</label>
          <input type="email" id="login-email" autocomplete="email" placeholder="you@example.com">
        </div>
        <div class="field">
          <label for="login-pw">Password</label>
          <input type="password" id="login-pw" autocomplete="current-password" placeholder="............">
        </div>
        <button class="btn-auth" id="login-btn" onclick="login()">Sign in</button>
        <div class="auth-error" id="login-error"></div>
        <p class="auth-sub" style="margin-top:20px;margin-bottom:0">
          No account yet? <a href="#" onclick="showSignup();return false" style="color:var(--blue);text-decoration:none;font-weight:600">Create one</a>
        </p>
      </div>

      <!-- SIGNUP MODE (hidden by default) -->
      <div id="auth-signup-view" style="display:none">
        <h1 class="auth-title">Create your account</h1>
        <p class="auth-sub">Start generating content. Free tier -- upgrade anytime.</p>
        <div class="field">
          <label for="signup-name">Your name</label>
          <input type="text" id="signup-name" autocomplete="name" placeholder="Jane Doe">
        </div>
        <div class="field">
          <label for="signup-email">Email</label>
          <input type="email" id="signup-email" autocomplete="email" placeholder="you@example.com">
        </div>
        <div class="field">
          <label for="signup-team">Team name <span style="color:var(--text-dim);font-size:10px">(optional)</span></label>
          <input type="text" id="signup-team" autocomplete="organization" placeholder="Acme Inc">
        </div>
        <div class="field">
          <label for="signup-pw">Password <span style="color:var(--text-dim);font-size:10px">(12+ characters)</span></label>
          <input type="password" id="signup-pw" autocomplete="new-password" placeholder="............">
        </div>
        <button class="btn-auth" id="signup-btn" onclick="signup()">Create account</button>
        <div class="auth-error" id="signup-error"></div>
        <p class="auth-sub" style="margin-top:20px;margin-bottom:0">
          Already have an account? <a href="#" onclick="showLogin();return false" style="color:var(--blue);text-decoration:none;font-weight:600">Sign in</a>
        </p>
      </div>
    </div>
  </div>

  <!-- MAIN APP (hidden until login) -->
  <div id="main-app" style="display:none;flex-direction:column;flex:1">
    <div class="topbar">
      <div class="brand"><span class="blue">PURE</span><span class="orange">BR</span><span class="blue">AIN</span> . SOCIAL</div>
      <div class="user-chip" id="user-chip" onclick="logout()"></div>
    </div>

    <div class="tabs">
      <div class="tab active" data-panel="board">Board</div>
      <div class="tab" data-panel="compose">Compose</div>
      <div class="tab" data-panel="my-content">Calendar<span class="badge" id="badge-scheduled" style="display:none">0</span></div>
      <div class="tab" data-panel="team">Team</div>
      <div class="tab" data-panel="analytics">Analytics</div>
      <div class="tab" data-panel="media">Media</div>
      <div class="tab" data-panel="accounts">Accounts</div>
      <div class="tab" data-panel="settings">Settings</div>
    </div>

    <!-- ===================== PANEL: BOARD (KANBAN) ===================== -->
    <div class="panel active" id="panel-board">
      <div class="kanban-toolbar">
        <div class="kanban-filter-chips" id="kanban-filters">
          <span class="kanban-filter-chip active" data-platform="all">All</span>
          <span class="kanban-filter-chip" data-platform="linkedin">LinkedIn</span>
          <span class="kanban-filter-chip" data-platform="twitter">X / Twitter</span>
          <span class="kanban-filter-chip" data-platform="bluesky">Bluesky</span>
          <span class="kanban-filter-chip" data-platform="threads">Threads</span>
          <span class="kanban-filter-chip" data-platform="instagram">Instagram</span>
          <span class="kanban-filter-chip" data-platform="facebook">Facebook</span>
        </div>
      </div>
      <div class="kanban-board" id="kanban-board">
        <div class="kanban-col" id="kanban-col-pending">
          <div class="kanban-col-header" style="border-top:3px solid #f59e0b">
            <span>Pending Review</span>
            <span class="col-count" id="kanban-count-pending" style="background:rgba(245,158,11,.15);color:#f59e0b">0</span>
          </div>
          <div class="kanban-col-body" id="kanban-body-pending" data-col="pending"></div>
        </div>
        <div class="kanban-col" id="kanban-col-approved">
          <div class="kanban-col-header" style="border-top:3px solid #2a93c1">
            <span>Approved</span>
            <span class="col-count" id="kanban-count-approved" style="background:var(--blue-dim);color:var(--blue)">0</span>
          </div>
          <div class="kanban-col-body" id="kanban-body-approved" data-col="approved"></div>
        </div>
        <div class="kanban-col" id="kanban-col-live">
          <div class="kanban-col-header" style="border-top:3px solid #22c55e">
            <span>Live</span>
            <span class="col-count" id="kanban-count-live" style="background:var(--green-dim);color:var(--green)">0</span>
          </div>
          <div class="kanban-col-body" id="kanban-body-live" data-col="live"></div>
        </div>
      </div>
    </div>

    <!-- ===================== PANEL: COMPOSE ===================== -->
    <div class="panel" id="panel-compose">
      <div class="compose-card">
        <div class="card-header">
          <div class="card-title">Compose New Post</div>
        </div>

        <!-- Content Type Selector -->
        <div class="form-group">
          <label class="form-label">Content Type</label>
          <div class="content-type-selector" id="content-type-selector">
            <button type="button" class="content-type-btn active-linkedin" data-type="linkedin" onclick="setContentType('linkedin')">Standalone Post</button>
            <button type="button" class="content-type-btn" data-type="blog" onclick="setContentType('blog')">Blog</button>
            <button type="button" class="content-type-btn" data-type="newsletter" onclick="setContentType('newsletter')">Newsletter</button>
            <button type="button" class="content-type-btn" data-type="bluesky" onclick="setContentType('bluesky')">Bluesky Thread</button>
          </div>
        </div>

        <!-- Blog-Specific Fields -->
        <div class="blog-fields" id="blog-fields">
          <div class="form-group">
            <label class="form-label">Blog Title</label>
            <input type="text" id="blog-title" placeholder="Enter blog post title..." class="field-input">
          </div>
          <div class="blog-fields-grid">
            <div class="form-group">
              <label class="form-label">Blog URL (after deploy)</label>
              <input type="url" id="blog-url" placeholder="https://purebrain.ai/blog/..." class="field-input" style="font-size:13px">
            </div>
            <div class="form-group">
              <label class="form-label">Banner Image URL</label>
              <input type="url" id="banner-image-url" placeholder="https://..." oninput="previewBanner(this.value)" class="field-input" style="font-size:13px">
            </div>
            <div class="form-group">
              <label class="form-label">Newsletter Status</label>
              <select id="newsletter-status" class="field-input" style="font-size:13px">
                <option value="">N/A</option><option value="pending">Pending</option><option value="drafted">Drafted</option><option value="published">Published</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Audio Status</label>
              <select id="audio-status" class="field-input" style="font-size:13px">
                <option value="">N/A</option><option value="pending">Pending</option><option value="generated">Generated</option><option value="published">Published</option>
              </select>
            </div>
          </div>
          <img class="banner-preview" id="banner-preview" src="" alt="Banner preview">
        </div>

        <!-- Platform Selector -->
        <div class="form-group" id="platform-selector-group">
          <label class="form-label">Platforms</label>
          <div class="platform-selector" id="platform-selector">
            <label class="platform-check"><input type="checkbox" value="linkedin" class="platform-cb"><span class="dot linkedin" style="width:10px;height:10px"></span> LinkedIn</label>
            <label class="platform-check"><input type="checkbox" value="twitter" class="platform-cb"><span class="dot twitter" style="width:10px;height:10px"></span> X / Twitter</label>
            <label class="platform-check"><input type="checkbox" value="bluesky" class="platform-cb"><span class="dot bluesky" style="width:10px;height:10px"></span> Bluesky</label>
            <label class="platform-check"><input type="checkbox" value="instagram" class="platform-cb"><span class="dot instagram" style="width:10px;height:10px"></span> Instagram</label>
            <label class="platform-check"><input type="checkbox" value="facebook" class="platform-cb"><span class="dot facebook" style="width:10px;height:10px"></span> Facebook</label>
            <label class="platform-check"><input type="checkbox" value="threads" class="platform-cb"><span class="dot threads" style="width:10px;height:10px"></span> Threads</label>
            <label class="platform-check"><input type="checkbox" value="tiktok" class="platform-cb"><span class="dot tiktok" style="width:10px;height:10px"></span> TikTok</label>
            <label class="platform-check"><input type="checkbox" value="reddit" class="platform-cb"><span class="dot reddit" style="width:10px;height:10px"></span> Reddit</label>
          </div>
        </div>

        <!-- Text Editor -->
        <div class="form-group">
          <label class="form-label">Post Content</label>
          <textarea id="post-text" placeholder="What do you want to share?" class="field-input" style="min-height:140px"></textarea>
          <div class="char-count" id="char-count">0 characters</div>
          <div class="char-pills" id="char-limits"></div>
        </div>

        <!-- Platform-Specific Composer -->
        <div class="platform-composer" id="platform-composer">
          <div class="platform-composer-toggle" id="pc-toggle" onclick="togglePlatformComposer()">
            <span>Customize per platform <span id="pc-platform-count"></span></span>
            <span class="arrow">&#9660;</span>
          </div>
          <div class="platform-composer-body" id="pc-body"></div>
        </div>

        <!-- AI Tools -->
        <div class="ai-tools-row" style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
          <button class="btn-sm ai-btn" onclick="generateVariations()" style="background:linear-gradient(135deg,var(--blue),var(--orange));color:#fff;border:none;font-size:11px;padding:6px 14px;border-radius:6px;cursor:pointer">
            ✨ Generate Variations
          </button>
          <button class="btn-sm ai-btn" onclick="repurposePost()" style="background:var(--surface);border:1px solid var(--border);color:var(--text-muted);font-size:11px;padding:6px 14px;border-radius:6px;cursor:pointer">
            🔄 Repurpose to Other Platforms
          </button>
        </div>
        <div id="ai-variations-panel" style="display:none;margin-top:12px"></div>

        <!-- Media Upload -->
        <div class="form-group">
          <label class="form-label">Media</label>
          <div class="drop-zone" id="drop-zone">
            <div class="drop-zone-icon">+</div>
            <div class="drop-zone-text">Drop images or videos here</div>
            <div class="drop-zone-sub">or click to browse files</div>
            <input type="file" id="file-input" multiple accept="image/*,video/*" style="display:none">
          </div>
          <div class="preview-grid" id="preview-grid"></div>
        </div>

        <!-- Hashtag Suggestions -->
        <div class="form-group">
          <label class="form-label">Hashtag Suggestions</label>
          <div id="hashtag-area" style="display:flex;flex-wrap:wrap;gap:6px;">
            <span class="hashtag-chip">#AI</span>
            <span class="hashtag-chip">#AgenticAI</span>
            <span class="hashtag-chip">#PureSurf</span>
            <span class="hashtag-chip">#PureBrain</span>
            <span class="hashtag-chip">#Automation</span>
            <span class="hashtag-chip">#BrowserAutomation</span>
            <span class="hashtag-chip">#SaaS</span>
            <span class="hashtag-chip">#StartupLife</span>
          </div>
        </div>

        <!-- Schedule -->
        <div class="schedule-row">
          <div class="form-group">
            <label class="form-label">Schedule</label>
            <input type="datetime-local" id="schedule-time">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-orange btn-lg" onclick="postNow()">Post Now</button>
          </div>
        </div>

        <div id="post-status-indicator" style="margin-top:12px;"></div>

        <!-- Actions -->
        <div class="action-row">
          <button class="btn btn-ghost" onclick="saveDraft()">Save as Draft</button>
          <button class="btn btn-primary" onclick="schedulePost()">Schedule Post</button>
        </div>
      </div>
    </div>

    <!-- ===================== PANEL: MY CONTENT (CALENDAR) ===================== -->
    <div class="panel" id="panel-my-content">
      <!-- View Toggle + Nav -->
      <div class="cal-nav">
        <div class="view-toggle">
          <button class="view-toggle-btn active" onclick="setCalendarView('month')">Month</button>
          <button class="view-toggle-btn" onclick="setCalendarView('week')">Week</button>
          <button class="view-toggle-btn" onclick="setCalendarView('list')">List</button>
        </div>
        <div class="cal-nav-center">
          <button class="cal-nav-btn" onclick="calNavPrev()" title="Previous">&lsaquo;</button>
          <span class="cal-nav-title" id="cal-nav-title"></span>
          <button class="cal-nav-btn" onclick="calNavNext()" title="Next">&rsaquo;</button>
          <button class="cal-today-btn" onclick="calNavToday()">Today</button>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <button class="btn btn-ghost btn-sm" onclick="refreshAllData()">Refresh</button>
          <button class="btn btn-green btn-sm" id="approve-all-btn" onclick="approveAll()" style="display:none">Approve All</button>
        </div>
      </div>

      <!-- Month Calendar View (default) -->
      <div class="month-view visible" id="month-view">
        <div class="month-grid" id="month-grid"></div>
        <div class="week-legend" style="margin-top:8px;">
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--blue);"></div> Blog</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--orange);"></div> Standalone</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--green);"></div> Newsletter</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:#6366f1;"></div> Bluesky</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--text-dim);"></div> Other</div>
          <div style="margin-left:auto;display:flex;gap:10px;font-size:11px;color:var(--text-dim);">
            <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--yellow);vertical-align:middle;"></span> Draft</span>
            <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--blue);vertical-align:middle;"></span> Scheduled</span>
            <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--green);vertical-align:middle;"></span> Live</span>
            <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--red);vertical-align:middle;"></span> Failed</span>
          </div>
        </div>
      </div>

      <!-- Weekly Calendar View -->
      <div class="week-view" id="week-view">
        <div class="week-grid" id="week-grid"></div>
        <div class="week-legend">
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--blue);"></div> Blog (8-9am ET)</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--orange);"></div> Standalone (1pm ET)</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--green);"></div> Newsletter</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:#6366f1;"></div> Bluesky</div>
          <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--text-dim);"></div> Other</div>
        </div>
      </div>

      <!-- List View -->
      <div id="list-view-container" style="display:none;">
        <!-- Advanced Filters -->
        <div class="filter-bar" id="list-filters">
          <div class="form-group">
            <label class="form-label">Platform</label>
            <select id="filter-platform" onchange="renderListView()">
              <option value="all">All Platforms</option>
              <option value="linkedin">LinkedIn</option>
              <option value="twitter">X / Twitter</option>
              <option value="bluesky">Bluesky</option>
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
              <option value="tiktok">TikTok</option>
              <option value="reddit">Reddit</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Status</label>
            <select id="filter-status" onchange="renderListView()">
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="scheduled">Scheduled</option>
              <option value="posted">Posted</option>
              <option value="rejected">Rejected</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Content Type</label>
            <select id="filter-content-type" onchange="renderListView()">
              <option value="all">All Types</option>
              <option value="blog">Blog</option>
              <option value="linkedin">Standalone Post</option>
              <option value="newsletter">Newsletter</option>
              <option value="bluesky">Bluesky Thread</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Date Range</label>
            <select id="filter-date-range" onchange="renderListView()">
              <option value="all">All Time</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Search</label>
            <input type="text" id="filter-search" placeholder="Search posts..." oninput="renderListView()">
          </div>
        </div>
        <div id="calendar-list"></div>
      </div>
    </div>

    <!-- ===================== PANEL: TEAM ===================== -->
    <div class="panel" id="panel-team">
      <div class="section-head">
        <div>
          <div class="section-title">Team Calendar</div>
          <div class="section-sub" id="team-count">Last 7 days across the team</div>
        </div>
      </div>
      <div class="team-grid" id="team-grid">
        <div class="empty"><div class="empty-text">Loading team activity...</div></div>
      </div>
    </div>

    <!-- ===================== PANEL: ANALYTICS ===================== -->
    <div class="panel" id="panel-analytics">
      <div class="section-head">
        <div>
          <div class="section-title">Analytics Dashboard</div>
          <div class="section-sub" id="analytics-period">Real-time content metrics</div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="refreshAnalytics()">Refresh</button>
      </div>

      <!-- Row 1: Summary Cards -->
      <div class="analytics-grid" id="analytics-summary" style="grid-template-columns:repeat(4,1fr)">
        <div class="stat-card">
          <div class="stat-value" id="stat-total">-</div>
          <div class="stat-label">Total Posts</div>
          <div style="display:flex;gap:12px;margin-top:8px;font-size:11px;color:var(--text-muted)">
            <span id="stat-week-count">- this week</span>
            <span id="stat-month-count">- this month</span>
          </div>
        </div>
        <div class="stat-card" id="card-pending">
          <div class="stat-value" id="stat-pending">-</div>
          <div class="stat-label">Pending Review</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-scheduled" style="color:#3b82f6">-</div>
          <div class="stat-label">Scheduled</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-next-post" style="font-size:16px">--</div>
          <div class="stat-label">Next Scheduled</div>
          <div style="margin-top:6px;display:flex;align-items:center;gap:6px">
            <span class="adv-health-dot" id="queue-health-dot" style="width:8px;height:8px;border-radius:50%;background:#555;display:inline-block"></span>
            <span style="font-size:11px;color:var(--text-dim)" id="queue-health-label">Queue idle</span>
          </div>
        </div>
      </div>

      <!-- Row 2: Platform Breakdown -->
      <div class="card" style="margin-bottom:16px">
        <div class="card-header" style="margin-bottom:16px">
          <div class="card-title">Posts by Platform</div>
        </div>
        <div id="adv-platform-bars"></div>
      </div>

      <!-- Row 3: Content Type Breakdown -->
      <div class="card" style="margin-bottom:16px">
        <div class="card-header" style="margin-bottom:12px">
          <div class="card-title">Content Types</div>
        </div>
        <div id="adv-content-types" style="display:flex;flex-wrap:wrap;gap:8px"></div>
      </div>

      <!-- Row 4: Recent Posts Performance Table -->
      <div class="card">
        <div class="card-title" style="margin-bottom:16px;">Recent Posts</div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>Platform</th><th>Post Preview</th><th>Posted</th><th>Status</th></tr></thead>
            <tbody id="analytics-table-body">
              <tr><td colspan="4" style="text-align:center;color:var(--text-dim);padding:24px;">Loading analytics...</td></tr>
            </tbody>
          </table>
        </div>
        <div style="font-size:11px;color:var(--text-dim);margin-top:8px;" id="analytics-updated">Last updated: --</div>
      </div>
    </div>

    <!-- ===================== PANEL: MEDIA ===================== -->
    <div class="panel" id="panel-media">
      <div class="section-head">
        <div>
          <div class="section-title">Media Library</div>
          <div class="section-sub">Upload and manage your media assets.</div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="document.getElementById('media-upload-input').click()">Upload Media</button>
        <input type="file" id="media-upload-input" multiple accept="image/*,video/*" style="display:none">
      </div>

      <!-- Upload drop zone -->
      <div class="drop-zone" id="media-drop-zone" style="margin-bottom:24px;">
        <div class="drop-zone-icon">+</div>
        <div class="drop-zone-text">Drag and drop media here</div>
        <div class="drop-zone-sub">PNG, JPG, GIF, MP4</div>
      </div>

      <div class="media-grid" id="media-grid"></div>
      <div class="empty" id="media-empty" style="display:none;">
        <div class="empty-icon">--</div>
        <div class="empty-text">No media uploaded yet</div>
      </div>
    </div>

    <!-- ===================== PANEL: ACCOUNTS ===================== -->
    <div class="panel" id="panel-accounts">
      <div class="section-head">
        <div>
          <div class="section-title">Connected Accounts</div>
          <div class="section-sub">Each account is isolated with its own PureSurf profile.</div>
        </div>
      </div>
      <div class="account-list" id="account-list"></div>
      <div style="margin-top:32px">
        <div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:4px">Connect a new account</div>
        <div style="font-size:12px;color:var(--text-muted)">Click a platform to start the connection flow.</div>
        <div class="connect-grid" id="connect-grid"></div>
      </div>
    </div>

    <!-- ===================== PANEL: SETTINGS ===================== -->
    <div class="panel" id="panel-settings">
      <div class="section-head">
        <div>
          <div class="section-title">Settings</div>
          <div class="section-sub">Manage your account security and AI partner voice profile.</div>
        </div>
      </div>

      <!-- Password change card -->
      <div class="card" style="max-width:460px">
        <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:4px">Change password</div>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:20px">Minimum 12 characters. Other devices will be signed out.</div>
        <div class="field">
          <label for="pw-current">Current password</label>
          <input type="password" id="pw-current" autocomplete="current-password">
        </div>
        <div class="field">
          <label for="pw-new">New password</label>
          <input type="password" id="pw-new" autocomplete="new-password">
        </div>
        <div class="field">
          <label for="pw-confirm">Confirm new password</label>
          <input type="password" id="pw-confirm" autocomplete="new-password">
        </div>
        <button class="btn btn-primary" id="pw-btn" onclick="changePassword()" style="width:100%;justify-content:center;margin-top:8px">Update password</button>
        <div class="auth-error" id="pw-msg" style="margin-top:10px"></div>
      </div>

      <!-- AI partners list -->
      <div class="card" style="max-width:460px;margin-top:16px">
        <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:4px">Your AI partners</div>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:16px">Each AI partner implements the 3-method interface contract.</div>
        <div id="partners-list"><div class="empty-text" style="font-size:12px">Loading...</div></div>
      </div>
    </div>
  </div>
</div>

<!-- Toast Container -->
<div class="toast-container" id="toast-container"></div>

<!-- DELETE CONFIRMATION MODAL -->
<div class="confirm-modal-overlay" id="delete-confirm-modal">
  <div class="confirm-modal">
    <h3>Delete Post?</h3>
    <p id="delete-confirm-text">Are you sure you want to delete this post? This action cannot be undone.</p>
    <div class="confirm-modal-actions">
      <button class="btn btn-ghost" onclick="cancelDelete()">Cancel</button>
      <button class="btn btn-red" id="delete-confirm-btn" onclick="confirmDelete()">Yes, Delete</button>
    </div>
  </div>
</div>

<!-- EDIT MODAL WITH FEEDBACK -->
<div class="edit-modal-overlay" id="edit-modal-overlay">
  <div class="edit-modal">
    <div class="edit-modal-header">
      <h2 id="edit-modal-title">Edit Post</h2>
      <button class="edit-modal-close" onclick="closeEditModal()">&times;</button>
    </div>
    <div class="edit-modal-body">
      <!-- LEFT: Content Preview / Edit -->
      <div class="edit-modal-left">
        <div class="modal-img-preview" id="modal-img-container" style="display:none;">
          <img id="modal-img" src="" alt="Post media" onclick="openLightbox(this.src)">
        </div>
        <div class="form-group">
          <label class="form-label">Title</label>
          <input type="text" id="modal-edit-title" placeholder="Post title..." class="field-input">
        </div>
        <div class="form-group">
          <label class="form-label">Post Content</label>
          <textarea id="modal-edit-content" class="field-input" style="min-height:160px"></textarea>
          <div class="char-pills" id="modal-char-limits" style="margin-top:6px"></div>
          <div id="modal-qg-results" style="margin-top:10px"></div>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <div class="form-group" style="flex:1;min-width:180px;">
            <label class="form-label">Scheduled Date/Time</label>
            <input type="datetime-local" id="modal-edit-time" class="field-input">
          </div>
          <div class="form-group" style="flex:0;min-width:140px;">
            <label class="form-label">Status</label>
            <select id="modal-edit-status" class="field-input">
              <option value="draft">Draft</option>
              <option value="scheduled">Scheduled</option>
              <option value="posted">Posted</option>
              <option value="rejected">Rejected</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Replace Image</label>
          <div style="display:flex;gap:12px;align-items:center;">
            <button class="btn btn-ghost btn-sm" onclick="document.getElementById('modal-replace-file').click()">Choose File</button>
            <span id="modal-replace-filename" style="font-size:12px;color:var(--text-dim);">No file chosen</span>
            <input type="file" id="modal-replace-file" accept="image/*" style="display:none" onchange="handleModalFileSelect(this)">
          </div>
        </div>
      </div>
      <!-- CENTER: Live Post Preview -->
      <div class="edit-modal-center" id="edit-modal-center">
        <div class="edit-modal-center-label">Live Preview</div>
        <div id="post-preview-container">
          <div class="post-preview-card" id="post-preview-card">
            <div class="preview-header">
              <div class="preview-avatar li-avatar" id="preview-avatar">JS</div>
              <div class="preview-header-info">
                <div class="preview-name" id="preview-name">Jared Sanborn</div>
                <div class="preview-handle" id="preview-handle" style="display:none"></div>
                <div class="preview-title" id="preview-title">CEO &amp; Founder at Pure Technology</div>
                <div class="preview-time" id="preview-time">1d &bull; &#x1F310;</div>
              </div>
            </div>
            <div class="preview-body" id="preview-body">
              <span class="preview-empty-state">Start typing to see preview...</span>
            </div>
            <div class="preview-image-wrap" id="preview-image-wrap" style="display:none">
              <img class="preview-image" id="preview-image" src="" alt="">
            </div>
            <div class="preview-actions" id="preview-actions">
              <span class="preview-action-item">&#x1F44D; Like</span>
              <span class="preview-action-item">&#x1F4AC; Comment</span>
              <span class="preview-action-item">&#x21D7; Repost</span>
              <span class="preview-action-item">&#x1F4E4; Send</span>
            </div>
          </div>
          <div class="preview-char-counter" id="preview-char-counter"></div>
        </div>
      </div>
      <!-- RIGHT: Feedback Panel -->
      <div class="edit-modal-right">
        <div class="feedback-panel-header">
          Feedback <span id="modal-feedback-count" style="background:var(--orange);color:#fff;padding:1px 7px;border-radius:10px;font-size:11px;">0</span>
        </div>
        <div class="feedback-actions">
          <div class="fp-type-buttons" id="modal-fp-type-buttons"></div>
        </div>
        <div class="feedback-input-area" id="feedback-input-area">
          <label class="form-label">Feedback Note <span id="feedback-type-label" style="text-transform:uppercase;font-size:10px;"></span></label>
          <textarea id="feedback-input-text" placeholder="Describe the issue..."></textarea>
          <div class="fb-input-actions">
            <button class="btn btn-ghost btn-sm" onclick="closeFeedbackInput()">Cancel</button>
            <button class="btn btn-primary btn-sm" onclick="submitFeedback()">Submit Feedback</button>
          </div>
        </div>
        <div class="feedback-history" id="feedback-history">
          <div style="text-align:center;padding:24px;color:var(--text-dim);font-size:13px;">No feedback yet</div>
        </div>
      </div>
    </div>
    <div class="edit-modal-footer">
      <div style="font-size:12px;color:var(--text-dim);" id="modal-post-id"></div>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-red btn-sm" onclick="deletePostFromModal()">Delete</button>
        <button class="btn btn-orange btn-sm" onclick="postNowFromModal()">Post Now</button>
        <button class="btn btn-ghost" onclick="closeEditModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveModalEdit()">Save Changes</button>
      </div>
    </div>
  </div>
</div>

<!-- LIGHTBOX -->
<div class="lightbox-overlay" id="img-lightbox" onclick="closeLightbox()">
  <div class="lightbox-close" onclick="closeLightbox()">&times;</div>
  <img id="lightbox-img" src="" alt="Full size preview">
</div>

<!-- QUALITY GATE MODAL -->
<div class="qg-modal-overlay" id="qg-modal-overlay">
  <div class="qg-modal">
    <h3>Quality Gate Warning</h3>
    <div id="qg-modal-violations"></div>
    <div class="qg-modal-actions">
      <button class="btn btn-ghost" onclick="qgGoBack()">Go Back to Edit</button>
      <button class="btn btn-orange" onclick="qgApproveAnyway()">Approve Anyway</button>
    </div>
  </div>
</div>

<script>
// ========== CONFIG ==========
const API = "https://social.purebrain.ai";
let TOKEN = localStorage.getItem("social_token") || "";
let USER = null;

const CHAR_LIMITS = { twitter: 280, bluesky: 300, linkedin: 3000, threads: 500, facebook: 63206, instagram: 2200, tiktok: 2200, reddit: 40000 };
const PLATFORM_NAMES = { instagram:'Instagram', facebook:'Facebook', linkedin:'LinkedIn', twitter:'X / Twitter', bluesky:'Bluesky', tiktok:'TikTok', reddit:'Reddit', threads:'Threads' };
const CONTENT_TYPE_LABELS = { linkedin:'Standalone', blog:'Blog', newsletter:'Newsletter', bluesky:'Bluesky Thread' };

// ========== FEEDBACK TYPES (from TASK3 visual feedback module) ==========
const FEEDBACK_TYPES = [
  { id: 'flag_image',    label: 'Flag Image',    icon: '\\u{1F6A9}', color: 'var(--red)',       bg: 'var(--red-dim)' },
  { id: 'replace_image', label: 'Replace Image',  icon: '\\u{1F5BC}\\uFE0F', color: 'var(--yellow)',    bg: 'var(--yellow-dim)' },
  { id: 'edit_text',    label: 'Edit Text',      icon: '\\u270F\\uFE0F', color: 'var(--blue)',      bg: 'var(--blue-dim)' },
  { id: 'general',      label: 'General',        icon: '\\u{1F4AC}', color: 'var(--text-muted)', bg: 'var(--surface)' },
];

let currentContentType = 'linkedin';
let calendarView = 'month';
let weekOffset = 0;
let monthOffset = 0;
let cachedPosts = [];

// ========== UTILITIES ==========
function esc(s){ return String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}[c])); }
function getImgSrc(p){var u=p.media_url||p.banner_image||'';if(u)return u;var mr=p.media_refs;if(!mr)return '';try{var arr=typeof mr==='string'?JSON.parse(mr):mr;if(Array.isArray(arr)&&arr.length)return arr[0];if(typeof mr==='string'&&mr.startsWith('http'))return mr;}catch(e){}return '';}
function h(tag, attrs={}, children=[]){
  const el = document.createElement(tag);
  for (const [k,v] of Object.entries(attrs)){
    if(k==="class")el.className=v;
    else if(k==="onclick")el.onclick=v;
    else if(k.startsWith("data-"))el.setAttribute(k,v);
    else if(k==="style")el.style.cssText=v;
    else el[k]=v;
  }
  for(const c of [].concat(children)){
    if(typeof c==="string")el.appendChild(document.createTextNode(c));
    else if(c)el.appendChild(c);
  }
  return el;
}
function formatNum(n){ if(n>=1000000)return(n/1000000).toFixed(1)+'M'; if(n>=1000)return(n/1000).toFixed(1)+'K'; return n.toString(); }
function fmtTime(iso){ if(!iso)return "--"; return new Date(iso).toLocaleString("en-US",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}); }

function getTimeAgo(isoString){
  if(!isoString)return '';
  const diff=Date.now()-new Date(isoString).getTime();
  const mins=Math.floor(diff/60000);
  if(mins<1)return 'just now';
  if(mins<60)return mins+'m ago';
  const hrs=Math.floor(mins/60);
  if(hrs<24)return hrs+'h ago';
  const days=Math.floor(hrs/24);
  return days+'d ago';
}

function renderFeedbackBadge(post){
  const feedback=post.feedback||[];
  let openCount=0;
  if(feedback.length){
    openCount=feedback.filter(fb=>fb.status!=='resolved'&&fb.status!=='dismissed').length;
  } else if(post.routing_decision){
    try{
      const rd=typeof post.routing_decision==='string'?JSON.parse(post.routing_decision):post.routing_decision;
      const rdFb=rd.feedback||[];
      openCount=rdFb.filter(fb=>fb.status!=='resolved'&&fb.status!=='dismissed').length;
    }catch{}
  }
  if(!openCount)return '';
  const color=openCount>=5?'var(--red)':openCount>=1?'var(--yellow)':'var(--green)';
  return '<span class="fb-badge" style="background:'+color+'">'+openCount+'</span>';
}

// ========== TOAST ==========
function toast(msg, type='info'){
  const c=document.getElementById('toast-container');
  const t=document.createElement('div');
  t.className='toast toast-'+type;
  t.textContent=msg;
  c.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';setTimeout(()=>t.remove(),300);},3500);
}

// ========== API ==========
async function api(path, opts={}){
  const headers = Object.assign({"Content-Type":"application/json"}, opts.headers||{});
  if(TOKEN) headers["Authorization"]="Bearer "+TOKEN;
  const res = await fetch(API+path, Object.assign({},opts,{headers,credentials:"include"}));
  if(res.status===401){TOKEN="";localStorage.removeItem("social_token");throw new Error("Session expired");}
  const data = await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.error||"HTTP "+res.status);
  return data;
}

// ========== AUTH ==========
async function login(){
  const btn=document.getElementById("login-btn"), err=document.getElementById("login-error");
  const email=document.getElementById("login-email").value.trim(), pw=document.getElementById("login-pw").value;
  err.textContent="";
  if(!email||!pw){err.textContent="Email and password required.";return;}
  btn.disabled=true; btn.textContent="Signing in...";
  try{
    const res=await fetch(API+"/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password:pw})});
    const data=await res.json();
    if(!res.ok)throw new Error(data.error||"login failed");
    TOKEN=data.token; localStorage.setItem("social_token",TOKEN); await bootApp();
  }catch(e){err.textContent=e.message; btn.disabled=false; btn.textContent="Sign in";}
}
function logout(){TOKEN="";localStorage.removeItem("social_token");location.reload();}
function showSignup(){document.getElementById("auth-login-view").style.display="none";document.getElementById("auth-signup-view").style.display="block";setTimeout(()=>{const el=document.getElementById("signup-name");if(el)el.focus();},50);}
function showLogin(){document.getElementById("auth-signup-view").style.display="none";document.getElementById("auth-login-view").style.display="block";setTimeout(()=>{const el=document.getElementById("login-email");if(el)el.focus();},50);}
async function signup(){
  const btn=document.getElementById("signup-btn"), err=document.getElementById("signup-error");
  const name=document.getElementById("signup-name").value.trim(), email=document.getElementById("signup-email").value.trim();
  const team=document.getElementById("signup-team").value.trim(), pw=document.getElementById("signup-pw").value;
  err.textContent="";
  if(!name||!email||!pw){err.textContent="Name, email, and password required.";return;}
  if(pw.length<12){err.textContent="Password must be at least 12 characters.";return;}
  btn.disabled=true; btn.textContent="Creating account...";
  try{
    const res=await fetch(API+"/api/signup",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,email,password:pw,team_name:team||undefined})});
    const data=await res.json();
    if(!res.ok)throw new Error(data.error||"signup failed");
    TOKEN=data.token; localStorage.setItem("social_token",TOKEN); await bootApp();
  }catch(e){err.textContent=e.message; btn.disabled=false; btn.textContent="Create account";}
}
document.addEventListener("keydown",(e)=>{
  if(e.key!=="Enter")return;
  const authGate=document.getElementById("auth-gate");
  if(authGate?.style.display==="none")return;
  const signupVisible=document.getElementById("auth-signup-view")?.style.display!=="none";
  if(signupVisible)signup(); else login();
});

// ========== BOOT APP ==========
async function bootApp(){
  try{
    USER=await api("/api/me");
    document.getElementById("auth-gate").style.display="none";
    document.getElementById("main-app").style.display="flex";
    renderUserChip(); wireTabs();
    await fetchAllContent();
    renderKanbanBoard(); renderMonthView(); updateCalNavTitle(); updateBadges();
    loadTeamContent(); loadAccounts(); loadPartners(); loadAnalytics();
    renderMediaGrid();
  }catch(e){
    console.warn("boot failed",e);
    // Don't logout-loop on stale token — just clear and show login
    TOKEN="";localStorage.removeItem("social_token");
    document.getElementById("auth-gate").style.display="";
    document.getElementById("main-app").style.display="none";
    // Re-enable login button in case it was disabled
    const btn=document.getElementById("login-btn");
    if(btn){btn.disabled=false;btn.textContent="Sign in";}
  }
}

function renderUserChip(){
  const chip=document.getElementById("user-chip");
  chip.innerHTML="";
  const initial=(USER.name||USER.email||"?").charAt(0).toUpperCase();
  chip.appendChild(h("div",{class:"avatar"},initial));
  chip.appendChild(h("span",{},USER.name||USER.email));
}

function wireTabs(){
  document.querySelectorAll(".tab").forEach(t=>{
    t.addEventListener("click",()=>{
      document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
      document.querySelectorAll(".panel").forEach(x=>x.classList.remove("active"));
      t.classList.add("active");
      document.getElementById("panel-"+t.dataset.panel).classList.add("active");
      if(t.dataset.panel==='analytics') loadAdvancedAnalytics();
    });
  });
}

// ========== CONTENT DATA ==========
async function fetchAllContent(){
  try{
    const data = await api("/api/content?limit=500");
    cachedPosts = (data.items||[]).map(normalizePost);
  }catch(e){
    console.error('fetchAllContent failed:',e);
    cachedPosts=[];
  }
}

function normalizePost(p){
  // Normalize field names between old/new API
  return {
    ...p,
    content: p.body || p.content || '',
    body: p.body || p.content || '',
    scheduled_time: p.scheduled_at || p.scheduled_time || null,
    scheduled_at: p.scheduled_at || p.scheduled_time || null,
    content_type: p.content_type || p.type || 'linkedin',
    platform: p.platform || 'linkedin',
    status: p.status || 'draft',
    title: p.title || '',
  };
}

async function refreshAllData(){
  await fetchAllContent();
  renderKanbanBoard();
  if(calendarView==='month') renderMonthView();
  else if(calendarView==='week') renderWeekView();
  else renderListView();
  updateBadges();
}

function updateBadges(){
  const drafts = cachedPosts.filter(p=>p.status==='draft'||p.status==='pending_approval');
  const scheduled = cachedPosts.filter(p=>p.status!=='posted');
  const badgeEl = document.getElementById('badge-scheduled');
  if(scheduled.length>0){badgeEl.style.display='';badgeEl.textContent=scheduled.length;}
  else{badgeEl.style.display='none';}
  const approveBtn = document.getElementById('approve-all-btn');
  if(drafts.length>1){approveBtn.style.display='';approveBtn.textContent='Approve All ('+drafts.length+')';}
  else{approveBtn.style.display='none';}
}

// ========== COMPOSE SECTION ==========
function setContentType(type){
  currentContentType=type;
  document.querySelectorAll('.content-type-btn').forEach(b=>{
    b.className='content-type-btn'+(b.dataset.type===type?' active-'+type:'');
  });
  document.getElementById('blog-fields').classList.toggle('visible',type==='blog');
  const platGroup=document.getElementById('platform-selector-group');
  if(type==='blog'){platGroup.style.opacity='0.5';document.querySelectorAll('.platform-cb').forEach(cb=>{cb.checked=cb.value==='linkedin';cb.closest('.platform-check').classList.toggle('checked',cb.checked);});}
  else{platGroup.style.opacity='1';}
}

function getSelectedPlatforms(){return Array.from(document.querySelectorAll('#platform-selector input:checked')).map(cb=>cb.value);}

function updateCharLimits(){
  const platforms=getSelectedPlatforms();
  const el=document.getElementById('char-limits');
  if(!platforms.length){el.innerHTML='';return;}
  const len=(document.getElementById('post-text').value||'').length;
  el.innerHTML=platforms.map(p=>{
    const limit=CHAR_LIMITS[p]||3000; const ok=len<=limit;
    return '<span class="char-pill" style="background:'+(ok?'var(--green-dim)':'var(--red-dim)')+';color:'+(ok?'var(--green)':'var(--red)')+';">'+(PLATFORM_NAMES[p]||p)+': '+len+'/'+limit+'</span>';
  }).join('');
}

function updatePostStatus(){
  const platforms=getSelectedPlatforms();
  const el=document.getElementById('post-status-indicator');
  if(!platforms.length){el.innerHTML='';return;}
  el.innerHTML='<span style="font-size:12px;color:var(--text-dim);">Will post to: '+platforms.map(p=>PLATFORM_NAMES[p]||p).join(', ')+'</span>';
}

function previewBanner(url){
  const preview=document.getElementById('banner-preview');
  if(url&&(url.startsWith('http://')||url.startsWith('https://'))){
    preview.src=url;preview.classList.add('visible');preview.onerror=()=>preview.classList.remove('visible');
  }else{preview.classList.remove('visible');}
}

// Platform checkboxes
document.querySelectorAll('.platform-check').forEach(label=>{
  label.addEventListener('click',(e)=>{
    if(e.target.tagName==='INPUT')return;
    const cb=label.querySelector('input');
    cb.checked=!cb.checked; label.classList.toggle('checked',cb.checked);
    updateCharLimits(); updatePostStatus();
    if(platformComposerExpanded) renderPlatformComposer();
  });
});

// Character count
document.getElementById('post-text').addEventListener('input',()=>{
  const text=document.getElementById('post-text').value;
  const len=text.length;
  const el=document.getElementById('char-count');
  const platforms=getSelectedPlatforms();
  const minLimit=platforms.length?Math.min(...platforms.map(p=>CHAR_LIMITS[p]||3000)):Infinity;
  el.textContent=len+' characters';
  el.className='char-count';
  if(platforms.length&&len>minLimit*0.9)el.classList.add('warn');
  if(platforms.length&&len>minLimit)el.classList.add('over');
  updateCharLimits();
});

// Hashtag chips
document.querySelectorAll('.hashtag-chip').forEach(chip=>{
  chip.addEventListener('click',()=>{
    const ta=document.getElementById('post-text');
    ta.value=(ta.value?ta.value+' ':'')+chip.textContent;
    ta.dispatchEvent(new Event('input'));
  });
});

// File upload
let uploadedFiles=[];
const dropZone=document.getElementById('drop-zone');
const fileInput=document.getElementById('file-input');
dropZone.addEventListener('click',()=>fileInput.click());
dropZone.addEventListener('dragover',(e)=>{e.preventDefault();dropZone.classList.add('dragover');});
dropZone.addEventListener('dragleave',()=>dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop',(e)=>{e.preventDefault();dropZone.classList.remove('dragover');handleFiles(e.dataTransfer.files);});
fileInput.addEventListener('change',()=>handleFiles(fileInput.files));

function handleFiles(files){
  Array.from(files).forEach(file=>{
    const reader=new FileReader();
    reader.onload=(e)=>{
      const fileObj={id:Date.now()+'_'+Math.random().toString(36).substr(2,6),name:file.name,type:file.type,size:file.size,data:e.target.result,base64:e.target.result.split(',')[1]};
      uploadedFiles.push(fileObj);renderPreviews();addToMediaLibrary(fileObj);
    };
    reader.readAsDataURL(file);
  });
}

function renderPreviews(){
  document.getElementById('preview-grid').innerHTML=uploadedFiles.map(f=>
    '<div class="preview-thumb"><img src="'+f.data+'" alt="'+esc(f.name)+'"><button class="remove-thumb" onclick="removeFile(\\''+f.id+'\\')">&times;</button></div>'
  ).join('');
}

function removeFile(id){uploadedFiles=uploadedFiles.filter(f=>f.id!==id);renderPreviews();}

function clearForm(){
  document.getElementById('post-text').value='';
  document.getElementById('post-text').dispatchEvent(new Event('input'));
  document.getElementById('schedule-time').value='';
  document.getElementById('blog-title').value='';
  document.getElementById('blog-url').value='';
  document.getElementById('banner-image-url').value='';
  document.getElementById('newsletter-status').value='';
  document.getElementById('audio-status').value='';
  document.getElementById('banner-preview').classList.remove('visible');
  setContentType('linkedin');
  uploadedFiles=[];renderPreviews();
  document.querySelectorAll('.platform-check').forEach(l=>{l.classList.remove('checked');l.querySelector('input').checked=false;});
  updateCharLimits();updatePostStatus();
  platformComposerExpanded=false;platformSectionStates={};
  document.getElementById('pc-toggle').classList.remove('expanded');
  document.getElementById('pc-body').classList.remove('visible');
  document.getElementById('pc-body').innerHTML='';
  document.getElementById('pc-platform-count').textContent='';
}

// Save Draft
async function saveDraft(){
  const text=document.getElementById('post-text').value.trim();
  const platforms=getSelectedPlatforms();
  if(!text){toast('Write something first','error');return;}
  if(!platforms.length){toast('Select at least one platform','error');return;}
  const schedTime=document.getElementById('schedule-time').value;
  try{
    const platformCaptions = getPlatformCaptions();
    for(const platform of platforms){
      const captionText = platformCaptions[platform] || text;
      const body={body:captionText,platform,status:'draft',content_type:currentContentType};
      if(Object.keys(platformCaptions).length > 0) body.platform_captions = JSON.stringify(platformCaptions);
      if(schedTime)body.scheduled_at=new Date(schedTime).toISOString();
      if(currentContentType==='blog'){
        body.title=document.getElementById('blog-title').value.trim();
        body.metadata=JSON.stringify({blog_url:document.getElementById('blog-url').value.trim(),banner_image:document.getElementById('banner-image-url').value.trim(),newsletter_status:document.getElementById('newsletter-status').value,audio_status:document.getElementById('audio-status').value});
      }
      await api('/api/content',{method:'POST',body:JSON.stringify(body)});
    }
    toast('Draft saved','success'); clearForm(); await refreshAllData();
  }catch(e){toast('Failed to save draft: '+e.message,'error');}
}

// Schedule Post
async function schedulePost(){
  const text=document.getElementById('post-text').value.trim();
  const platforms=getSelectedPlatforms();
  const time=document.getElementById('schedule-time').value;
  if(!text){toast('Write something first','error');return;}
  if(!platforms.length){toast('Select at least one platform','error');return;}
  if(!time){toast('Pick a schedule time','error');return;}
  try{
    const platformCaptions = getPlatformCaptions();
    for(const platform of platforms){
      const captionText = platformCaptions[platform] || text;
      const body={body:captionText,platform,status:'scheduled',content_type:currentContentType,scheduled_at:new Date(time).toISOString()};
      if(Object.keys(platformCaptions).length > 0) body.platform_captions = JSON.stringify(platformCaptions);
      if(currentContentType==='blog'){
        body.title=document.getElementById('blog-title').value.trim();
        body.metadata=JSON.stringify({blog_url:document.getElementById('blog-url').value.trim(),banner_image:document.getElementById('banner-image-url').value.trim(),newsletter_status:document.getElementById('newsletter-status').value,audio_status:document.getElementById('audio-status').value});
      }
      await api('/api/content',{method:'POST',body:JSON.stringify(body)});
    }
    toast('Post scheduled','success'); clearForm(); await refreshAllData();
  }catch(e){toast('Failed to schedule: '+e.message,'error');}
}

// Post Now (from compose)
async function postNow(){
  const text=document.getElementById('post-text').value.trim();
  const platforms=getSelectedPlatforms();
  if(!text){toast('Write some content first','error');return;}
  if(!platforms.length){toast('Select at least one platform','error');return;}
  let s=0,f=0;
  for(const platform of platforms){
    try{
      await api('/api/content',{method:'POST',body:JSON.stringify({body:text,platform,status:'scheduled',content_type:currentContentType,scheduled_at:new Date().toISOString()})});
      s++;
    }catch{f++;}
  }
  if(s>0)toast('Scheduled to '+s+' platform(s)','success');
  if(f>0)toast('Failed on '+f+' platform(s)','error');
  clearForm(); await refreshAllData();
}

// ========== AI TOOLS (Phase 3) ==========

async function generateVariations() {
  const caption = document.getElementById('post-text')?.value || '';
  if (!caption || caption.length < 20) {
    toast('Write at least 20 characters first', 'error');
    return;
  }

  const panel = document.getElementById('ai-variations-panel');
  panel.style.display = 'block';
  panel.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-dim)">Generating variations...</div>';

  try {
    const data = await api('/api/ai/captions', {
      method: 'POST',
      body: JSON.stringify({ caption, platforms: ['linkedin', 'twitter', 'bluesky'], count: 3 })
    });

    let html = '<div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px">AI Variations</div>';

    for (const [platform, variations] of Object.entries(data.variations || {})) {
      html += '<div style="margin-bottom:12px">';
      html += '<div style="font-size:11px;font-weight:600;color:var(--blue);margin-bottom:6px">' + platform.toUpperCase() + '</div>';

      for (const v of variations) {
        html += '<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px;margin-bottom:6px;cursor:pointer;transition:border-color .15s" onclick="useVariation(this)" data-text="' + esc(v.text) + '">';
        html += '<div style="font-size:12px;line-height:1.4;color:var(--text);margin-bottom:4px">' + esc(v.text.substring(0, 150)) + (v.text.length > 150 ? '...' : '') + '</div>';
        html += '<div style="font-size:10px;color:var(--text-dim)">' + v.char_count + '/' + v.char_limit + ' chars · Score: ' + (v.score * 100).toFixed(0) + '%</div>';
        html += '</div>';
      }
      html += '</div>';
    }

    html += '<button class="btn-sm" onclick="document.getElementById(\\'ai-variations-panel\\').style.display=\\'none\\'" style="margin-top:4px;font-size:11px">Close</button>';
    panel.innerHTML = html;
  } catch (e) {
    panel.innerHTML = '<div style="color:var(--red);padding:12px;font-size:13px">Failed: ' + esc(e.message) + '</div>';
  }
}

function useVariation(el) {
  const text = el.dataset.text;
  const textarea = document.getElementById('post-text');
  if (textarea && text) {
    textarea.value = text;
    textarea.dispatchEvent(new Event('input'));
    toast('Variation applied');
    document.getElementById('ai-variations-panel').style.display = 'none';
  }
}

async function repurposePost() {
  const textarea = document.getElementById('post-text');
  const caption = textarea?.value || '';
  if (!caption || caption.length < 50) {
    toast('Write at least 50 characters to repurpose', 'error');
    return;
  }

  const panel = document.getElementById('ai-variations-panel');
  panel.style.display = 'block';
  panel.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-dim)">Repurposing content...</div>';

  try {
    // Create a temporary content item to repurpose from
    const createRes = await api('/api/content', {
      method: 'POST',
      body: JSON.stringify({
        body: caption,
        platform: 'linkedin',
        status: 'draft',
        social_account_id: 'temp'
      })
    });

    const sourceId = createRes.item?.id;
    if (!sourceId) throw new Error('Could not create source');

    const data = await api('/api/ai/repurpose', {
      method: 'POST',
      body: JSON.stringify({
        source_content_id: sourceId,
        target_platforms: ['linkedin', 'bluesky', 'twitter']
      })
    });

    let html = '<div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px">Repurposed Content</div>';

    for (const [platform, output] of Object.entries(data.outputs || {})) {
      html += '<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:8px">';
      html += '<div style="font-size:11px;font-weight:600;color:var(--blue);margin-bottom:6px">' + platform.toUpperCase() + ' · ' + output.content_type + '</div>';
      html += '<div style="font-size:13px;line-height:1.5;color:var(--text);margin-bottom:6px">' + esc(output.caption) + '</div>';
      html += '<div style="font-size:10px;color:var(--text-dim)">' + output.char_count + '/' + output.char_limit + ' chars</div>';
      html += '<button class="btn-sm" onclick="useVariation(this)" data-text="' + esc(output.caption) + '" style="margin-top:6px;font-size:11px">Use This</button>';
      html += '</div>';
    }

    html += '<button class="btn-sm" onclick="document.getElementById(\\'ai-variations-panel\\').style.display=\\'none\\'" style="margin-top:4px;font-size:11px">Close</button>';
    panel.innerHTML = html;
  } catch (e) {
    panel.innerHTML = '<div style="color:var(--red);padding:12px;font-size:13px">Failed: ' + esc(e.message) + '</div>';
  }
}

// ========== CALENDAR VIEW TOGGLE ==========
function setCalendarView(view){
  calendarView=view;
  document.querySelectorAll('.view-toggle-btn').forEach(b=>{
    b.classList.toggle('active',b.textContent.trim().toLowerCase()===view);
  });
  document.getElementById('month-view').classList.toggle('visible',view==='month');
  document.getElementById('week-view').classList.toggle('visible',view==='week');
  document.getElementById('list-view-container').style.display=view==='list'?'block':'none';
  if(view==='month')renderMonthView();
  else if(view==='week')renderWeekView();
  else renderListView();
  updateCalNavTitle();
}

function calNavPrev(){
  if(calendarView==='month'){monthOffset--;renderMonthView();}
  else if(calendarView==='week'){weekOffset--;renderWeekView();}
  updateCalNavTitle();
}
function calNavNext(){
  if(calendarView==='month'){monthOffset++;renderMonthView();}
  else if(calendarView==='week'){weekOffset++;renderWeekView();}
  updateCalNavTitle();
}
function calNavToday(){
  monthOffset=0;weekOffset=0;
  if(calendarView==='month')renderMonthView();
  else if(calendarView==='week')renderWeekView();
  updateCalNavTitle();
}
function updateCalNavTitle(){
  const el=document.getElementById('cal-nav-title');
  if(!el)return;
  const now=new Date();
  if(calendarView==='month'){
    const d=new Date(now.getFullYear(),now.getMonth()+monthOffset,1);
    el.textContent=d.toLocaleDateString('en-US',{month:'long',year:'numeric'});
  }else if(calendarView==='week'){
    const monday=new Date(now);
    monday.setDate(monday.getDate()-((monday.getDay()+6)%7)+(weekOffset*7));
    const sunday=new Date(monday);sunday.setDate(sunday.getDate()+6);
    const fmt=d=>d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
    el.textContent=fmt(monday)+' - '+fmt(sunday)+', '+sunday.getFullYear();
  }else{
    el.textContent='All Scheduled Posts';
  }
}

// ========== MONTH VIEW ==========
function renderMonthView(){
  const grid=document.getElementById('month-grid');
  if(!grid)return;
  const posts=cachedPosts;
  const now=new Date();
  const viewDate=new Date(now.getFullYear(),now.getMonth()+monthOffset,1);
  const year=viewDate.getFullYear(),month=viewDate.getMonth();
  const today=new Date();today.setHours(0,0,0,0);

  const firstDay=new Date(year,month,1);
  const lastDay=new Date(year,month+1,0);
  const startDate=new Date(firstDay);
  const dow=startDate.getDay();
  startDate.setDate(startDate.getDate()+((dow===0)?-6:1-dow));
  const endDate=new Date(lastDay);
  const endDow=endDate.getDay();
  if(endDow!==0)endDate.setDate(endDate.getDate()+(7-endDow));

  const postsByDate={};
  posts.forEach(p=>{
    const dt=p.scheduled_at||p.scheduled_time;
    if(!dt)return;
    const ds=dt.split('T')[0];
    if(!postsByDate[ds])postsByDate[ds]=[];
    postsByDate[ds].push(p);
  });

  let html='';
  ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].forEach(d=>{html+='<div class="month-day-header">'+d+'</div>';});

  const cursor=new Date(startDate);
  while(cursor<=endDate){
    const dateStr=cursor.toISOString().split('T')[0];
    const isToday=cursor.getTime()===today.getTime();
    const isOtherMonth=cursor.getMonth()!==month;
    const dayPosts=postsByDate[dateStr]||[];
    let classes='month-cell';
    if(isToday)classes+=' today';
    if(isOtherMonth)classes+=' other-month';
    if(dayPosts.length>0)classes+=' has-posts';
    html+='<div class="'+classes+'" data-date="'+dateStr+'" ondragover="onDragOver(event, this)" ondragleave="onDragLeave(event, this)" ondrop="onDrop(event, this)">';
    html+='<div class="month-date"><span class="month-date-num">'+cursor.getDate()+'</span></div>';
    const maxShow=3;
    dayPosts.slice(0,maxShow).forEach(p=>{
      const ct=p.content_type||'linkedin';
      const typeClass=['blog','linkedin','newsletter','bluesky'].includes(ct)?ct:'other';
      const label=p.title||(p.content||'').substring(0,25);
      const time=p.scheduled_at?new Date(p.scheduled_at).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit',hour12:true}):'';
      const statusClass='s-'+(p.status||'draft');
      html+='<div class="month-card type-'+typeClass+'" draggable="true" data-post-id="'+p.id+'" ondragstart="onDragStart(event, \\''+p.id+'\\', \\''+esc(p.scheduled_at||'')+'\\')" ondragend="onDragEnd(event)" onclick="openEditModal(\\''+p.id+'\\')" title="'+esc((p.title||'')+' - '+(p.content||'').substring(0,100))+'">';
      html+='<span class="month-card-time">'+esc(time)+'</span> '+esc(label);
      html+='<span class="month-card-status '+statusClass+'"></span></div>';
    });
    if(dayPosts.length>maxShow){
      html+='<div class="month-overflow" onclick="showDayDetail(\\''+dateStr+'\\')">+'+(dayPosts.length-maxShow)+' more</div>';
    }
    html+='</div>';
    cursor.setDate(cursor.getDate()+1);
  }
  grid.innerHTML=html;
}

function showDayDetail(dateStr){
  setCalendarView('list');
  // Pre-set date filter -- not implemented as a dedicated filter, just switch to list view
}

// ========== WEEK VIEW ==========
function renderWeekView(){
  const grid=document.getElementById('week-grid');
  if(!grid)return;
  const posts=cachedPosts;
  const now=new Date();
  const monday=new Date(now);
  monday.setDate(monday.getDate()-((monday.getDay()+6)%7)+(weekOffset*7));
  monday.setHours(0,0,0,0);

  const days=[];
  for(let i=0;i<7;i++){const d=new Date(monday);d.setDate(d.getDate()+i);days.push(d);}
  const today=new Date();today.setHours(0,0,0,0);

  const slots=[
    {label:'8-9am ET',key:'morning',types:['blog']},
    {label:'1pm ET',key:'afternoon',types:['linkedin']},
    {label:'Other',key:'other',types:['newsletter','bluesky','other']}
  ];

  let html='<div class="week-slot-label"></div>';
  days.forEach(d=>{
    const isToday=d.getTime()===today.getTime();
    html+='<div class="week-header'+(isToday?' today':'')+'">'+d.toLocaleDateString('en-US',{weekday:'short'})+'<div class="week-header-date">'+d.getDate()+'</div></div>';
  });

  slots.forEach(slot=>{
    html+='<div class="week-slot-label">'+slot.label+'</div>';
    days.forEach(d=>{
      const dayStr=d.toISOString().split('T')[0];
      const dayPosts=posts.filter(p=>{
        const dt=p.scheduled_at||p.scheduled_time;
        if(!dt)return false;
        if(dt.split('T')[0]!==dayStr)return false;
        const ct=p.content_type||'linkedin';
        if(slot.key==='morning')return ct==='blog';
        if(slot.key==='afternoon')return ct==='linkedin'||(!ct);
        return slot.types.includes(ct)||(slot.key==='other'&&!['blog','linkedin'].includes(ct));
      });
      html+='<div class="week-cell" data-date="'+dayStr+'" ondragover="onDragOver(event, this)" ondragleave="onDragLeave(event, this)" ondrop="onDrop(event, this)">';
      dayPosts.forEach(p=>{
        const ct=p.content_type||'linkedin';
        const chipClass=ct==='blog'?'blog':ct==='linkedin'?'linkedin':ct==='newsletter'?'newsletter':ct==='bluesky'?'bluesky':'other';
        const label=p.title||(p.content||'').substring(0,30);
        const statusDot=p.status==='scheduled'?' \\u2713':p.status==='posted'?' \\u2714':'';
        html+='<div class="week-post-chip '+chipClass+'" draggable="true" data-post-id="'+p.id+'" ondragstart="onDragStart(event, \\''+p.id+'\\', \\''+esc(p.scheduled_at||'')+'\\')" ondragend="onDragEnd(event)" onclick="openEditModal(\\''+p.id+'\\')" title="'+esc((p.title||'')+' '+(p.content||'').substring(0,100))+'">'+esc(label)+statusDot+'</div>';
      });
      html+='</div>';
    });
  });
  grid.innerHTML=html;
}

// ========== LIST VIEW ==========
function renderListView(){
  const list=document.getElementById('calendar-list');
  let posts=[...cachedPosts];

  // Apply filters
  const pf=document.getElementById('filter-platform')?.value||'all';
  const sf=document.getElementById('filter-status')?.value||'all';
  const ctf=document.getElementById('filter-content-type')?.value||'all';
  const drf=document.getElementById('filter-date-range')?.value||'all';
  const search=(document.getElementById('filter-search')?.value||'').toLowerCase();

  if(pf!=='all')posts=posts.filter(p=>p.platform===pf);
  if(sf!=='all')posts=posts.filter(p=>p.status===sf);
  if(ctf!=='all')posts=posts.filter(p=>(p.content_type||'linkedin')===ctf);
  if(drf==='week'){
    const weekAgo=new Date();weekAgo.setDate(weekAgo.getDate()-7);
    posts=posts.filter(p=>{const dt=p.scheduled_at||p.created_at;return dt&&new Date(dt)>=weekAgo;});
  }else if(drf==='month'){
    const monthAgo=new Date();monthAgo.setMonth(monthAgo.getMonth()-1);
    posts=posts.filter(p=>{const dt=p.scheduled_at||p.created_at;return dt&&new Date(dt)>=monthAgo;});
  }
  if(search)posts=posts.filter(p=>((p.content||'')+(p.title||'')).toLowerCase().includes(search));

  posts.sort((a,b)=>{
    const at=a.scheduled_at||a.created_at||'';
    const bt=b.scheduled_at||b.created_at||'';
    if(!at)return 1;if(!bt)return -1;
    return new Date(bt)-new Date(at);
  });

  if(!posts.length){
    list.innerHTML='<div class="empty"><div class="empty-icon">--</div><div class="empty-text">No posts found</div></div>';
    return;
  }

  list.innerHTML=posts.map(p=>{
    const pl=p.platform||'linkedin';
    const ct=p.content_type||'linkedin';
    const platformIcon='<span class="platform-icon pi-'+pl+'" style="width:24px;height:24px;font-size:10px;">'+pl.substring(0,2).toUpperCase()+'</span>';
    const ctBadge='<span class="ct-badge ct-badge-'+ct+'">'+(CONTENT_TYPE_LABELS[ct]||ct)+'</span>';
    const preview=(p.content||'').substring(0,100)+((p.content||'').length>100?'...':'');
    const titleDisplay=p.title?'<strong>'+esc(p.title)+'</strong> - ':'';
    const time=p.scheduled_at?fmtTime(p.scheduled_at):(p.created_at?fmtTime(p.created_at):'No time set');
    const imgSrc=getImgSrc(p);
    const mediaHtml=imgSrc?'<div class="post-thumb"><img src="'+esc(imgSrc)+'" alt="media" onerror="this.parentElement.style.display=\\'none\\'"></div>':'';
    const feedbackBadge=getFeedbackBadge(p);
    const feedbackCountBadge=renderFeedbackBadge(p);

    return '<div class="post-list-item" data-post-id="'+p.id+'" onclick="openEditModal(\\''+p.id+'\\')">' +
      '<div class="post-platforms">'+platformIcon+'</div>' +
      mediaHtml +
      '<div class="post-preview"><div class="post-preview-text">'+titleDisplay+esc(preview)+'</div>' +
      '<div class="post-meta-line">'+ctBadge+' <span>'+esc(time)+'</span></div></div>' +
      '<span class="post-status-pill status-'+p.status+'">'+esc(p.status)+'</span>'+feedbackBadge+feedbackCountBadge +
      '<div class="post-actions" onclick="event.stopPropagation()">' +
        (p.status==='draft'?'<button class="action-btn approve" onclick="approvePost(\\''+p.id+'\\')">Approve</button>':'')+
        '<button class="action-btn edit" onclick="openEditModal(\\''+p.id+'\\')">Edit</button>' +
        (p.status==='scheduled'?'<button class="action-btn post-now" onclick="postNowById(\\''+p.id+'\\')">Post Now</button>':'')+
        '<button class="action-btn delete" onclick="deletePost(\\''+p.id+'\\')">Delete</button>' +
      '</div></div>';
  }).join('');
}

// ========== FEEDBACK BADGE HELPER ==========
function getFeedbackBadge(post){
  const feedback=post.feedback||[];
  if(!feedback.length)return '';
  const openFb=feedback.filter(fb=>fb.status!=='resolved');
  if(!openFb.length)return '<span class="post-feedback-badge badge-resolved">Resolved</span>';
  const hasFlagged=openFb.some(fb=>fb.type==='flag_image');
  if(hasFlagged)return '<span class="post-feedback-badge badge-flagged">Flagged</span>';
  return '<span class="post-feedback-badge badge-feedback">Feedback</span>';
}

// ========== POST ACTIONS ==========
async function approvePost(id){
  const post = cachedPosts.find(p => p.id === id);
  if (post) {
    const result = qualityGate(post);
    if (!result.pass) {
      showQGModal(result.violations, id, 'approve');
      return;
    }
  }
  await doApprovePost(id);
}

async function approveAll(){
  const drafts=cachedPosts.filter(p=>p.status==='draft'||p.status==='pending_approval');
  if(!drafts.length){toast('No drafts to approve','info');return;}
  let s=0;
  for(const d of drafts){
    try{await api("/api/content/"+d.id,{method:"PATCH",body:JSON.stringify({status:"scheduled"})});s++;}catch(e){console.error(e);}
  }
  toast('Approved '+s+' post(s)','success'); await refreshAllData();
}

async function postNowById(id){
  try{
    await api("/api/content/"+id,{method:"PATCH",body:JSON.stringify({status:"scheduled",scheduled_at:new Date().toISOString()})});
    toast('Post scheduled for now','success'); await refreshAllData();
  }catch(e){toast('Failed: '+e.message,'error');}
}

async function rejectItem(id){
  const reason=prompt("Why reject this draft?");
  if(reason===null)return;
  try{
    await api("/api/content/"+id,{method:"PATCH",body:JSON.stringify({status:"rejected",rejection_reason:reason||""})});
    toast('Post rejected','info'); await refreshAllData();
  }catch(e){toast('Failed: '+e.message,'error');}
}

// ========== DELETE CONFIRMATION ==========
let pendingDeleteId=null;
function deletePost(id){showDeleteConfirm(id,'delete');}
function showDeleteConfirm(id,action){
  pendingDeleteId=id;
  const post=cachedPosts.find(p=>p.id===id);
  const preview=post?(post.content||'').substring(0,80):'';
  document.getElementById('delete-confirm-text').textContent=
    'Are you sure you want to '+(action==='reject'?'reject and delete':'delete')+' this post?'+
    (preview?' ("'+preview+'...")':'')+' This action cannot be undone.';
  document.getElementById('delete-confirm-btn').textContent=action==='reject'?'Yes, Reject':'Yes, Delete';
  document.getElementById('delete-confirm-modal').classList.add('active');
}
function cancelDelete(){pendingDeleteId=null;document.getElementById('delete-confirm-modal').classList.remove('active');}
async function confirmDelete(){
  const id=pendingDeleteId;if(!id)return;
  document.getElementById('delete-confirm-modal').classList.remove('active');
  pendingDeleteId=null;
  try{
    await api("/api/content/"+id,{method:"DELETE"});
    toast('Post deleted','info'); closeEditModal(); await refreshAllData();
  }catch(e){toast('Failed: '+e.message,'error');}
}

// ========== EDIT MODAL ==========
let currentEditPostId=null;
let currentFeedbackType=null;
let modalReplaceFile=null;

function openEditModal(id){
  const post=cachedPosts.find(p=>p.id===id);
  if(!post)return;
  currentEditPostId=id;
  document.getElementById('edit-modal-overlay').classList.add('active');
  document.body.style.overflow='hidden';

  // Populate left side
  const imgSrc=getImgSrc(post);
  const imgContainer=document.getElementById('modal-img-container');
  const imgEl=document.getElementById('modal-img');
  if(imgSrc){imgEl.src=imgSrc;imgContainer.style.display='block';}
  else{imgContainer.style.display='none';}

  document.getElementById('modal-edit-title').value=post.title||'';
  document.getElementById('modal-edit-content').value=post.content||post.body||'';
  document.getElementById('modal-edit-status').value=post.status||'draft';
  document.getElementById('modal-post-id').textContent='ID: '+id;
  document.getElementById('edit-modal-title').textContent=post.title?'Edit: '+post.title.substring(0,40):'Edit Post';

  const schedLocal=post.scheduled_at
    ?new Date(new Date(post.scheduled_at).getTime()-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16)
    :'';
  document.getElementById('modal-edit-time').value=schedLocal;

  // Update character limits for modal
  updateModalCharLimits(post.platform);

  // Reset file upload
  modalReplaceFile=null;
  document.getElementById('modal-replace-filename').textContent='No file chosen';
  const fileEl=document.getElementById('modal-replace-file');
  if(fileEl)fileEl.value='';

  // Quality gate check
  updateModalQG();
  const contentEl = document.getElementById('modal-edit-content');
  const titleEl = document.getElementById('modal-edit-title');
  if (contentEl) contentEl.addEventListener('input', updateModalQG);
  if (titleEl) titleEl.addEventListener('input', updateModalQG);

  // Render type buttons from FEEDBACK_TYPES
  const typeBtns=document.getElementById('modal-fp-type-buttons');
  if(typeBtns){
    typeBtns.innerHTML=FEEDBACK_TYPES.map(ft=>
      '<button class="fp-type-btn" data-type="'+ft.id+'" onclick="openFeedbackInput(\\''+ft.id+'\\')">'+ft.icon+' '+ft.label+'</button>'
    ).join('');
  }

  // Initialize live post preview
  initPostPreview(post);

  loadFeedback(id);
  closeFeedbackInput();
}

function updateModalCharLimits(platform){
  const content=document.getElementById('modal-edit-content');
  if(!content)return;
  const updateFn=()=>{
    const len=content.value.length;
    const limit=CHAR_LIMITS[platform]||3000;
    const remaining=limit-len;
    const el=document.getElementById('modal-char-limits');
    const color=remaining<0?'var(--red)':remaining<20?'var(--yellow)':'var(--text-dim)';
    el.innerHTML='<span class="char-pill" style="background:rgba(255,255,255,0.04);color:'+color+';">'+(PLATFORM_NAMES[platform]||platform)+': '+remaining+' / '+limit+'</span>';
  };
  content.removeEventListener('input',content._charHandler);
  content._charHandler=updateFn;
  content.addEventListener('input',updateFn);
  updateFn();
}

function closeEditModal(){
  document.getElementById('edit-modal-overlay').classList.remove('active');
  document.body.style.overflow='';
  currentEditPostId=null;currentFeedbackType=null;modalReplaceFile=null;
}

function handleModalFileSelect(input){
  if(!input.files||!input.files[0])return;
  const file=input.files[0];
  const reader=new FileReader();
  reader.onload=(e)=>{
    modalReplaceFile={data:e.target.result,base64:e.target.result.split(',')[1],name:file.name};
    document.getElementById('modal-replace-filename').textContent=file.name;
    const imgEl=document.getElementById('modal-img');
    const imgContainer=document.getElementById('modal-img-container');
    imgEl.src=e.target.result;imgContainer.style.display='block';
    // Update live preview image
    const previewImg=document.getElementById('preview-image');
    const previewImgWrap=document.getElementById('preview-image-wrap');
    if(previewImg&&previewImgWrap){previewImg.src=e.target.result;previewImgWrap.style.display='block';}
  };
  reader.readAsDataURL(file);
}

// ========== LIVE POST PREVIEW ==========
let currentPreviewPlatform='linkedin';

const PREVIEW_CONFIGS={
  linkedin:{
    cardClass:'',
    avatarClass:'li-avatar',
    name:'Jared Sanborn',
    handle:'',
    title:'CEO & Founder at Pure Technology',
    time:'1d \\u2022 \\ud83c\\udf10',
    actions:[
      {icon:'\\ud83d\\udc4d',label:'Like'},
      {icon:'\\ud83d\\udcac',label:'Comment'},
      {icon:'\\u21d7',label:'Repost'},
      {icon:'\\ud83d\\udce4',label:'Send'}
    ],
    hashtagColor:'#0a66c2',
    charLimit:3000
  },
  twitter:{
    cardClass:'twitter-preview',
    avatarClass:'tw-avatar',
    name:'Jared Sanborn',
    handle:'@JaredSanborn',
    title:'',
    time:'1h',
    actions:[
      {icon:'\\ud83d\\udcac',label:''},
      {icon:'\\ud83d\\udd01',label:''},
      {icon:'\\u2764\\ufe0f',label:''},
      {icon:'\\ud83d\\udce4',label:''}
    ],
    hashtagColor:'#1d9bf0',
    charLimit:280
  },
  bluesky:{
    cardClass:'bluesky-preview',
    avatarClass:'bs-avatar',
    name:'Jared Sanborn',
    handle:'@jaredsanborn.bsky.social',
    title:'',
    time:'1h',
    actions:[
      {icon:'\\ud83d\\udcac',label:'Reply'},
      {icon:'\\ud83d\\udd01',label:'Repost'},
      {icon:'\\u2764\\ufe0f',label:'Like'},
      {icon:'\\u2026',label:''}
    ],
    hashtagColor:'#0085ff',
    charLimit:300
  }
};

function formatPreviewBody(text,platform){
  if(!text)return '<span class="preview-empty-state">Start typing to see preview...</span>';
  const escaped=text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  return escaped
    .replace(/(#\\w[\\w]*)/g,'<span class="hashtag">$1</span>')
    .replace(/(@\\w[\\w.]*)/g,'<span class="mention">$1</span>')
    .replace(/(https?:\\/\\/[^\\s]+)/g,'<span class="link">$1</span>');
}

function updatePostPreview(platform){
  const cfg=PREVIEW_CONFIGS[platform]||PREVIEW_CONFIGS.linkedin;
  currentPreviewPlatform=platform;

  const card=document.getElementById('post-preview-card');
  const content=document.getElementById('modal-edit-content');
  const text=content?content.value:'';

  // Update card class
  card.className='post-preview-card'+(cfg.cardClass?' '+cfg.cardClass:'');

  // Update avatar
  const avatar=document.getElementById('preview-avatar');
  avatar.className='preview-avatar '+cfg.avatarClass;

  // Update header info
  document.getElementById('preview-name').textContent=cfg.name;
  const handleEl=document.getElementById('preview-handle');
  if(cfg.handle){handleEl.textContent=cfg.handle;handleEl.style.display='block';}
  else{handleEl.style.display='none';}
  document.getElementById('preview-title').textContent=cfg.title;
  document.getElementById('preview-time').innerHTML=cfg.time;

  // Update body
  document.getElementById('preview-body').innerHTML=formatPreviewBody(text,platform);

  // Update image
  const imgWrap=document.getElementById('preview-image-wrap');
  const previewImg=document.getElementById('preview-image');
  const modalImg=document.getElementById('modal-img');
  const modalImgContainer=document.getElementById('modal-img-container');
  if(modalImgContainer&&modalImgContainer.style.display!=='none'&&modalImg&&modalImg.src){
    previewImg.src=modalImg.src;
    imgWrap.style.display='block';
  }else{
    imgWrap.style.display='none';
  }

  // Update actions
  const actionsEl=document.getElementById('preview-actions');
  actionsEl.innerHTML=cfg.actions.map(a=>
    '<span class="preview-action-item">'+a.icon+(a.label?' '+a.label:'')+'</span>'
  ).join('');

  // Update character counter
  updatePreviewCharCounter(text,cfg.charLimit,platform);
}

function updatePreviewCharCounter(text,limit,platform){
  const el=document.getElementById('preview-char-counter');
  if(!el)return;
  const len=text.length;
  const remaining=limit-len;
  let cls='preview-char-green';
  if(remaining<0)cls='preview-char-red';
  else if(remaining<(limit*0.1))cls='preview-char-yellow';
  const pName=PLATFORM_NAMES[platform]||platform;
  el.innerHTML='<span class="'+cls+'">'+pName+': '+remaining+' characters remaining</span>';
}

function initPostPreview(post){
  const platform=post.platform||'linkedin';
  currentPreviewPlatform=platform;

  // Attach live update listener
  const contentEl=document.getElementById('modal-edit-content');
  if(contentEl){
    contentEl.removeEventListener('input',contentEl._previewHandler);
    contentEl._previewHandler=function(){updatePostPreview(currentPreviewPlatform);};
    contentEl.addEventListener('input',contentEl._previewHandler);
  }

  // Initial render
  updatePostPreview(platform);
}

async function saveModalEdit(){
  if(!currentEditPostId)return;
  const content=document.getElementById('modal-edit-content').value.trim();
  if(!content){toast('Post content cannot be empty','error');return;}
  const updateBody={
    body:content,
    title:document.getElementById('modal-edit-title').value.trim(),
    status:document.getElementById('modal-edit-status').value,
  };
  const timeVal=document.getElementById('modal-edit-time').value;
  if(timeVal)updateBody.scheduled_at=new Date(timeVal).toISOString();
  if(modalReplaceFile){updateBody.media_base64=modalReplaceFile.base64;updateBody.media_filename=modalReplaceFile.name;}
  try{
    await api('/api/content/'+currentEditPostId,{method:'PATCH',body:JSON.stringify(updateBody)});
    toast('Post updated','success');closeEditModal();await refreshAllData();
  }catch(e){toast('Failed to save: '+e.message,'error');}
}

function deletePostFromModal(){
  if(!currentEditPostId)return;
  showDeleteConfirm(currentEditPostId,'delete');
}

async function postNowFromModal(){
  if(!currentEditPostId)return;
  try{
    await api('/api/content/'+currentEditPostId,{method:'PATCH',body:JSON.stringify({status:'scheduled',scheduled_at:new Date().toISOString()})});
    toast('Post scheduled for now','success');closeEditModal();await refreshAllData();
  }catch(e){toast('Failed: '+e.message,'error');}
}

// ========== FEEDBACK SYSTEM ==========
async function loadFeedback(postId){
  const history=document.getElementById('feedback-history');
  const countEl=document.getElementById('modal-feedback-count');
  // Try to load feedback from the post's routing_decision or dedicated endpoint
  try{
    const post=cachedPosts.find(p=>p.id===postId);
    let items=[];
    // Try API endpoint first
    try{
      const data=await api('/api/content/'+postId+'/feedback');
      items=data.feedback||[];
    }catch{
      // Fallback: parse from routing_decision
      if(post&&post.routing_decision){
        try{
          const rd=typeof post.routing_decision==='string'?JSON.parse(post.routing_decision):post.routing_decision;
          items=rd.feedback||[];
        }catch{}
      }
    }
    countEl.textContent=items.filter(fb=>fb.status!=='resolved').length;
    if(!items.length){
      history.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-dim);font-size:13px;">No feedback yet</div>';
      return;
    }
    history.innerHTML=items.map(fb=>{
      const isResolved=fb.status==='resolved';
      const ft=FEEDBACK_TYPES.find(t=>t.id===fb.type)||FEEDBACK_TYPES[3];
      const timeStr=fb.created_at?getTimeAgo(fb.created_at):'';
      return '<div class="feedback-item'+(isResolved?' resolved':'')+'" style="border-left:3px solid '+ft.color+'">' +
        '<div class="feedback-item-header">' +
          '<span class="feedback-item-from">'+esc(fb.from||'unknown')+'</span>' +
          '<span class="feedback-item-type fb-type-'+(fb.type||'general')+'">'+ft.icon+' '+ft.label+'</span>' +
        '</div>' +
        '<div class="feedback-item-text">'+esc(fb.text||'')+'</div>' +
        '<div class="feedback-item-time"><span>'+timeStr+'</span>' +
          (!isResolved?'<button class="btn btn-ghost btn-sm" style="padding:2px 8px;font-size:11px;" onclick="resolveFeedback(\\''+postId+'\\',\\''+fb.id+'\\')">Resolve</button>':'<span style="color:var(--green);">Resolved</span>') +
        '</div></div>';
    }).join('');
  }catch(e){
    history.innerHTML='<div style="text-align:center;padding:24px;color:var(--text-dim);font-size:13px;">Could not load feedback</div>';
  }
}

function openFeedbackInput(type){
  currentFeedbackType=type;
  const area=document.getElementById('feedback-input-area');
  area.classList.add('visible');
  const ft=FEEDBACK_TYPES.find(t=>t.id===type)||FEEDBACK_TYPES[3];
  document.getElementById('feedback-type-label').textContent=ft.label;
  document.getElementById('feedback-type-label').style.color=ft.color;
  document.getElementById('feedback-input-text').value='';
  document.getElementById('feedback-input-text').focus();
  // Highlight the selected type button
  document.querySelectorAll('.fp-type-btn').forEach(b=>{
    b.classList.toggle('selected',b.dataset.type===type);
  });
}

function closeFeedbackInput(){
  document.getElementById('feedback-input-area').classList.remove('visible');
  currentFeedbackType=null;
}

async function submitFeedback(){
  if(!currentEditPostId||!currentFeedbackType)return;
  const text=document.getElementById('feedback-input-text').value.trim();
  if(!text){toast('Please add a note','error');return;}
  try{
    // Try dedicated feedback endpoint
    await api('/api/content/'+currentEditPostId+'/feedback',{
      method:'POST',
      body:JSON.stringify({text,type:currentFeedbackType,from:USER?.name||'user'})
    });
    toast('Feedback submitted','success');
    closeFeedbackInput();loadFeedback(currentEditPostId);await refreshAllData();
  }catch(e){
    // Fallback: store feedback in routing_decision via PATCH
    try{
      const post=cachedPosts.find(p=>p.id===currentEditPostId);
      let rd={};
      if(post&&post.routing_decision){
        try{rd=typeof post.routing_decision==='string'?JSON.parse(post.routing_decision):post.routing_decision;}catch{}
      }
      if(!rd.feedback)rd.feedback=[];
      rd.feedback.push({id:Date.now().toString(),text,type:currentFeedbackType,from:USER?.name||'user',created_at:new Date().toISOString(),status:'open'});
      await api('/api/content/'+currentEditPostId,{method:'PATCH',body:JSON.stringify({routing_decision:JSON.stringify(rd)})});
      toast('Feedback submitted','success');
      closeFeedbackInput();await refreshAllData();
    }catch(e2){toast('Failed: '+e2.message,'error');}
  }
}

async function resolveFeedback(postId,feedbackId){
  try{
    await api('/api/content/'+postId+'/feedback/'+feedbackId+'/resolve',{method:'PUT'});
    toast('Feedback resolved','success');loadFeedback(postId);await refreshAllData();
  }catch(e){
    // Fallback: update routing_decision
    try{
      const post=cachedPosts.find(p=>p.id===postId);
      let rd={};
      if(post&&post.routing_decision){try{rd=typeof post.routing_decision==='string'?JSON.parse(post.routing_decision):post.routing_decision;}catch{}}
      if(rd.feedback){
        const fb=rd.feedback.find(f=>f.id===feedbackId);
        if(fb){fb.status='resolved';fb.resolved_at=new Date().toISOString();}
        await api('/api/content/'+postId,{method:'PATCH',body:JSON.stringify({routing_decision:JSON.stringify(rd)})});
        toast('Feedback resolved','success');await refreshAllData();
      }
    }catch(e2){toast('Failed: '+e2.message,'error');}
  }
}

// ========== KANBAN BOARD ==========
let kanbanPlatformFilter='all';

const PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',threads:'#000',instagram:'#e1306c',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500'};

function initKanbanFilters(){
  document.querySelectorAll('#kanban-filters .kanban-filter-chip').forEach(chip=>{
    chip.addEventListener('click',()=>{
      document.querySelectorAll('#kanban-filters .kanban-filter-chip').forEach(c=>c.classList.remove('active'));
      chip.classList.add('active');
      kanbanPlatformFilter=chip.dataset.platform;
      renderKanbanBoard();
    });
  });
}

function getKanbanColumn(status){
  if(['draft','pending_approval','needs_revision','rejected'].includes(status))return 'pending';
  if(['scheduled','approved'].includes(status))return 'approved';
  if(status==='posted')return 'live';
  return 'pending';
}

function renderKanbanCard(post,colType){
  const pl=post.platform||'linkedin';
  const barColor=PLATFORM_COLORS[pl]||'#666';
  const ct=post.content_type||'linkedin';
  const ctLabel=CONTENT_TYPE_LABELS[ct]||ct;
  const preview=(post.content||post.body||'').substring(0,120)+((post.content||post.body||'').length>120?'...':'');
  const hasMedia=!!(post.media_url||post.banner_image||(post.media_refs&&post.media_refs.length));
  const imgSrc=getImgSrc(post);
  const schedDate=post.scheduled_at?new Date(post.scheduled_at).toLocaleString('en-US',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}):'Not scheduled';
  const feedback=post.feedback||[];
  let feedbackFromRd=[];
  if(!feedback.length&&post.routing_decision){
    try{const rd=typeof post.routing_decision==='string'?JSON.parse(post.routing_decision):post.routing_decision;feedbackFromRd=rd.feedback||[];}catch{}
  }
  const fbCount=feedback.length||feedbackFromRd.length;

  // Post type labels
  const POST_TYPES = {post:'Standalone',blog:'Blog',newsletter:'Newsletter',newsletter_post:'Newsletter Post',thread:'Thread',linkedin:'Standalone'};
  const typeLabel = POST_TYPES[ct] || 'Standalone';
  const schedParts = post.scheduled_at ? new Date(post.scheduled_at) : null;
  const schedDateShort = schedParts ? schedParts.toLocaleDateString('en-US',{month:'short',day:'numeric'}) : '';
  const schedTimeShort = schedParts ? schedParts.toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'}) : '';

  let html='<div class="kanban-card kanban-card-anim" draggable="'+(colType!=='live'?'true':'false')+'" data-post-id="'+post.id+'" data-status="'+esc(post.status)+'">';

  // Color bar at top (platform color)
  html+='<div class="kanban-card-bar" style="background:'+barColor+'"></div>';

  // FULL-WIDTH IMAGE (Trello-style visual-first)
  if(imgSrc){
    html+='<div class="kanban-card-thumb"><img src="'+esc(imgSrc)+'" alt="" onerror="this.parentElement.style.display=\\'none\\'"></div>';
  }

  // Card body below image
  html+='<div class="kanban-card-body">';

  // Label chips (platform + type + warnings)
  html+='<div class="kanban-card-badges">';
  html+='<span class="kanban-platform-chip" style="background:'+barColor+'">'+(PLATFORM_NAMES[pl]||pl)+'</span>';
  html+='<span class="kanban-type-badge">'+esc(typeLabel)+'</span>';
  if(!hasMedia)html+='<span class="kanban-needs-image">Needs Image</span>';
  if(post.status==='rejected')html+='<span class="kanban-status-badge ks-rejected">Rejected</span>';
  if(fbCount){
    const fbBadge=renderFeedbackBadge(post);
    html+=fbBadge||'<span class="kanban-feedback-badge">'+fbCount+' feedback</span>';
  }
  html+='</div>';

  // Title (prominent, below labels)
  if(post.title){
    html+='<div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:4px;line-height:1.3">'+esc(post.title)+'</div>';
  }

  // Preview text
  html+='<div class="kanban-card-preview">'+esc(preview)+'</div>';

  // Schedule info (subtle, at bottom)
  html+='<div class="kanban-card-info-row" style="margin-top:8px">';
  if(schedDateShort){
    html+='<span>'+esc(schedDateShort)+' at '+esc(schedTimeShort)+'</span>';
  } else {
    html+='<span>Not scheduled</span>';
  }
  html+='</div>';

  // Actions
  if(colType==='pending'){
    html+='<div class="kanban-card-actions" onclick="event.stopPropagation()">';
    html+='<button class="action-btn approve btn-sm" onclick="event.stopPropagation();kanbanApprove(\\''+post.id+'\\')">Approve</button>';
    html+='<button class="action-btn edit btn-sm" onclick="event.stopPropagation();openEditModal(\\''+post.id+'\\')">Edit</button>';
    html+='</div>';
  }else if(colType==='approved'){
    html+='<div class="kanban-card-actions" onclick="event.stopPropagation()">';
    html+='<button class="action-btn post-now btn-sm" onclick="event.stopPropagation();postNowById(\\''+post.id+'\\')">Post Now</button>';
    html+='</div>';
  }else if(colType==='live'){
    if(post.post_url){
      html+='<div class="kanban-card-actions" onclick="event.stopPropagation()">';
      html+='<a href="'+esc(post.post_url)+'" target="_blank" class="action-btn edit btn-sm" style="text-decoration:none">View Post</a>';
      html+='</div>';
    }
    const metrics=post.performance_metrics;
    if(metrics){
      html+='<div class="kanban-card-meta" style="margin-top:4px">';
      if(metrics.likes!=null)html+='<span>Likes: '+metrics.likes+'</span>';
      if(metrics.comments!=null)html+='<span>Comments: '+metrics.comments+'</span>';
      if(metrics.shares!=null)html+='<span>Shares: '+metrics.shares+'</span>';
      html+='</div>';
    }
  }

  html+='</div></div>';
  return html;
}

function renderKanbanBoard(){
  let posts=[...cachedPosts];
  if(kanbanPlatformFilter!=='all'){
    posts=posts.filter(p=>(p.platform||'linkedin')===kanbanPlatformFilter);
  }

  const pending=posts.filter(p=>getKanbanColumn(p.status)==='pending');
  const approved=posts.filter(p=>getKanbanColumn(p.status)==='approved');
  const live=posts.filter(p=>getKanbanColumn(p.status)==='live');

  // Sort: most recent first
  const sortByDate=(a,b)=>{
    const at=a.scheduled_at||a.created_at||'';const bt=b.scheduled_at||b.created_at||'';
    if(!at)return 1;if(!bt)return -1;return new Date(bt)-new Date(at);
  };
  pending.sort(sortByDate);approved.sort(sortByDate);live.sort(sortByDate);

  document.getElementById('kanban-count-pending').textContent=pending.length;
  document.getElementById('kanban-count-approved').textContent=approved.length;
  document.getElementById('kanban-count-live').textContent=live.length;

  const renderCol=(items,containerId,colType)=>{
    const el=document.getElementById(containerId);
    if(!items.length){
      el.innerHTML='<div class="empty" style="padding:24px 12px"><div class="empty-text" style="font-size:12px">No posts</div></div>';
      return;
    }
    el.innerHTML=items.map(p=>renderKanbanCard(p,colType)).join('');
  };

  renderCol(pending,'kanban-body-pending','pending');
  renderCol(approved,'kanban-body-approved','approved');
  renderCol(live,'kanban-body-live','live');

  // Attach click handlers for card body
  document.querySelectorAll('.kanban-card').forEach(card=>{
    card.addEventListener('click',(e)=>{
      if(e.target.closest('.kanban-card-actions'))return;
      openEditModal(card.dataset.postId);
    });
  });

  // Attach drag handlers
  initKanbanDragDrop();
}

async function kanbanApprove(id){
  const post = cachedPosts.find(p => p.id === id);
  if (post) {
    const result = qualityGate(post);
    if (!result.pass) {
      showQGModal(result.violations, id, 'kanbanApprove');
      return;
    }
  }
  await doApprovePost(id);
}

// Drag and Drop
function initKanbanDragDrop(){
  const cards=document.querySelectorAll('.kanban-card[draggable="true"]');
  const bodies=document.querySelectorAll('.kanban-col-body');

  cards.forEach(card=>{
    card.addEventListener('dragstart',(e)=>{
      card.classList.add('dragging');
      e.dataTransfer.setData('text/plain',card.dataset.postId);
      e.dataTransfer.effectAllowed='move';
    });
    card.addEventListener('dragend',()=>{
      card.classList.remove('dragging');
      bodies.forEach(b=>b.classList.remove('drag-over'));
    });
  });

  bodies.forEach(body=>{
    const col=body.dataset.col;
    if(col==='live')return; // read-only

    body.addEventListener('dragover',(e)=>{
      e.preventDefault();
      e.dataTransfer.dropEffect='move';
      body.classList.add('drag-over');
    });
    body.addEventListener('dragleave',(e)=>{
      if(!body.contains(e.relatedTarget))body.classList.remove('drag-over');
    });
    body.addEventListener('drop',async(e)=>{
      e.preventDefault();
      body.classList.remove('drag-over');
      const postId=e.dataTransfer.getData('text/plain');
      const post=cachedPosts.find(p=>p.id===postId);
      if(!post)return;
      const currentCol=getKanbanColumn(post.status);
      if(currentCol===col)return;
      // pending -> approved = schedule, approved -> pending = un-approve
      let newStatus;
      if(col==='approved')newStatus='scheduled';
      else if(col==='pending')newStatus='draft';
      else return;
      try{
        await api("/api/content/"+postId,{method:"PATCH",body:JSON.stringify({status:newStatus})});
        toast(col==='approved'?'Post approved':'Post moved to drafts','success');
        await refreshAllData();
      }catch(err){toast('Failed: '+err.message,'error');}
    });
  });
}

// Mobile: toggle collapse
if(window.innerWidth<=768){
  document.querySelectorAll('.kanban-col-header').forEach(header=>{
    header.addEventListener('click',()=>{
      header.closest('.kanban-col').classList.toggle('collapsed');
    });
  });
}

initKanbanFilters();

// ========== TEAM CONTENT ==========
async function loadTeamContent(){
  try{
    const data=await api("/api/content/team?days=7");
    const grid=document.getElementById("team-grid");
    grid.innerHTML="";
    const items=(data.items||[]).slice(0,24);
    document.getElementById("team-count").textContent=
      items.length+" item"+(items.length===1?"":"s")+" from the team (last 7 days)";
    if(!items.length){grid.innerHTML='<div class="empty"><div class="empty-text">No team activity in the last 7 days.</div></div>';return;}
    items.forEach(p=>{
      p=normalizePost(p);
      const card=document.createElement("div");card.className="post-card";
      card.innerHTML='<div class="post-meta"><div class="post-platform"><span class="dot '+esc(p.platform)+'"></span>'+esc(p.platform)+(p.user_name?' . '+esc(p.user_name):'')+'</div><div style="display:flex;align-items:center;gap:10px"><span class="status-badge status-'+esc(p.status)+'">'+esc(p.status)+'</span><span class="post-time">'+esc(fmtTime(p.scheduled_at||p.posted_at))+'</span></div></div><div class="post-body" style="font-size:13px">'+esc((p.content||'').slice(0,200))+'</div>';
      grid.appendChild(card);
    });
  }catch(e){console.warn("loadTeamContent failed",e);}
}

// ========== ACCOUNTS ==========
async function loadAccounts(){
  try{
    const data=await api("/api/social_accounts");
    const list=document.getElementById("account-list");
    list.innerHTML="";
    const accounts=data.accounts||[];
    if(!accounts.length){list.innerHTML='<div class="empty" style="grid-column:1/-1"><div class="empty-text">No accounts connected yet.</div></div>';}
    else{accounts.forEach(a=>{
      const healthClass=a.health_status==='healthy'?'healthy':a.health_status==='degraded'?'degraded':a.health_status==='failed'?'failed':'unknown';
      const card=document.createElement("div");card.className="account-card";
      card.innerHTML='<span class="dot '+esc(a.platform)+'" style="width:10px;height:10px"></span><div class="account-info"><div class="account-platform">'+esc(a.platform)+'</div><div class="account-handle">@'+esc(a.account_handle)+'</div></div><span class="health-dot '+healthClass+'" title="'+esc(a.health_status||'unknown')+'"></span>';
      list.appendChild(card);
    });}
    // Connect grid
    const platforms=["linkedin","twitter","bluesky","threads","instagram","facebook"];
    const connected=new Set(accounts.map(a=>a.platform));
    const connectGrid=document.getElementById("connect-grid");
    connectGrid.innerHTML="";
    platforms.forEach(pl=>{
      if(connected.has(pl))return;
      const btn=document.createElement("div");btn.className="connect-btn";
      btn.innerHTML='<div class="dot '+pl+'" style="width:12px;height:12px"></div><div class="connect-btn-label">'+pl.charAt(0).toUpperCase()+pl.slice(1)+'</div>';
      btn.onclick=()=>connectAccount(pl);
      connectGrid.appendChild(btn);
    });
  }catch(e){console.warn("loadAccounts failed",e);}
}

function connectAccount(platform){showConnectModal(platform);}

function showConnectModal(platform){
  const old=document.getElementById("connect-modal");if(old)old.remove();
  const authHints={
    bluesky:{type:"api_oauth",fields:["handle","app_password"],hint:"Generate an app password at bsky.app Settings > App Passwords"},
    linkedin:{type:"puresurf_session",fields:["handle"],hint:"We'll open PureSurf to capture your LinkedIn session securely."},
    twitter:{type:"puresurf_session",fields:["handle"],hint:"Free Twitter posting via PureSurf (no $100/mo API needed)."},
    facebook:{type:"api_oauth",fields:["handle"],hint:"Connect via Facebook OAuth."},
    instagram:{type:"api_oauth",fields:["handle"],hint:"Connect via Instagram / Meta OAuth."},
    threads:{type:"api_oauth",fields:["handle"],hint:"Connect via Threads / Meta OAuth."},
  };
  const cfg=authHints[platform]||{type:"api_oauth",fields:["handle"],hint:""};
  const modal=document.createElement("div");modal.id="connect-modal";
  modal.style.cssText="position:fixed;inset:0;background:rgba(4,6,12,0.8);display:flex;align-items:center;justify-content:center;z-index:99998;backdrop-filter:blur(6px)";
  let fieldsHtml='<div class="field"><label>Handle / Username</label><input type="text" id="connect-handle" placeholder="@yourhandle" autofocus></div>';
  if(cfg.fields.includes("app_password")){fieldsHtml+='<div class="field"><label>App Password</label><input type="password" id="connect-app-pw" placeholder="xxxx-xxxx-xxxx-xxxx"></div>';}
  modal.innerHTML='<div style="background:rgba(14,17,32,0.98);border:1px solid var(--border);border-radius:16px;padding:28px;max-width:420px;width:90%;backdrop-filter:blur(16px)"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px"><div style="font-size:18px;font-weight:700;color:#fff">Connect <span style="text-transform:capitalize">'+esc(platform)+'</span></div><button onclick="document.getElementById(\\'connect-modal\\').remove()" style="background:none;border:none;color:var(--text-muted);font-size:20px;cursor:pointer">&times;</button></div><p style="font-size:12px;color:var(--text-muted);margin-bottom:16px">'+esc(cfg.hint)+'</p>'+fieldsHtml+'<button class="btn-auth" id="connect-submit-btn" onclick="submitConnect(\\''+esc(platform)+'\\',\\''+esc(cfg.type)+'\\')">Connect '+esc(platform)+'</button><div class="auth-error" id="connect-error" style="margin-top:8px"></div></div>';
  document.body.appendChild(modal);
  modal.addEventListener("click",e=>{if(e.target===modal)modal.remove();});
}

async function submitConnect(platform,authType){
  const handle=(document.getElementById("connect-handle")?.value||"").trim();
  const appPw=document.getElementById("connect-app-pw")?.value||"";
  const errEl=document.getElementById("connect-error");
  const btn=document.getElementById("connect-submit-btn");
  if(!handle){errEl.textContent="Handle is required";return;}
  btn.disabled=true;btn.textContent="Connecting...";
  try{
    await api("/api/social_accounts",{method:"POST",body:JSON.stringify({platform,account_handle:handle.replace(/^@/,""),auth_type:authType,credentials_encrypted:appPw||undefined})});
    document.getElementById("connect-modal")?.remove();
    await loadAccounts();toast('Account connected','success');
  }catch(e){errEl.textContent=e.message;btn.disabled=false;btn.textContent="Connect "+platform;}
}

// ========== SETTINGS ==========
async function changePassword(){
  const btn=document.getElementById("pw-btn");
  const msg=document.getElementById("pw-msg");
  const current=document.getElementById("pw-current").value;
  const newPw=document.getElementById("pw-new").value;
  const confirmPw=document.getElementById("pw-confirm").value;
  msg.style.color="var(--red)";
  if(!current||!newPw){msg.textContent="All fields required.";return;}
  if(newPw!==confirmPw){msg.textContent="New passwords don't match.";return;}
  if(newPw.length<12){msg.textContent="New password must be at least 12 characters.";return;}
  btn.disabled=true;btn.textContent="Updating...";
  try{
    await api("/api/me/password",{method:"POST",body:JSON.stringify({current_password:current,new_password:newPw})});
    msg.style.color="var(--green)";msg.textContent="Password updated.";
    document.getElementById("pw-current").value="";document.getElementById("pw-new").value="";document.getElementById("pw-confirm").value="";
  }catch(e){msg.textContent=e.message;}
  finally{btn.disabled=false;btn.textContent="Update password";}
}

async function loadPartners(){
  try{
    const data=await api("/api/ai_partners");
    const list=document.getElementById("partners-list");if(!list)return;
    list.innerHTML="";
    const partners=data.partners||[];
    if(!partners.length){list.innerHTML='<div class="empty-text" style="font-size:12px;color:var(--text-muted)">No AI partners registered yet.</div>';return;}
    partners.forEach(p=>{
      const row=document.createElement("div");
      row.style.cssText="padding:12px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;gap:12px";
      row.innerHTML='<div style="min-width:0;flex:1"><div style="font-size:14px;font-weight:700;color:#fff">'+esc(p.partner_name)+'</div><div style="font-size:11px;color:var(--text-dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+esc(p.partner_endpoint)+'</div></div><span style="font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:3px 10px;border-radius:100px;background:rgba(34,197,94,.15);color:var(--green)">active</span>';
      list.appendChild(row);
    });
  }catch(e){console.warn("loadPartners failed",e);}
}

// ========== ANALYTICS ==========

async function loadAnalytics(){
  try{
    await loadAdvancedAnalytics();
  }catch(e){console.warn("loadAnalytics failed",e);}
}

async function loadAdvancedAnalytics(){
  try{
    const [summary, queue] = await Promise.all([
      api('/api/analytics/summary'),
      api('/api/content/queue-status')
    ]);
    renderAnalyticsDashboard(summary, queue);
  }catch(e){
    console.warn('Advanced analytics load failed, falling back:', e);
    // Fallback: try old endpoint
    try{
      const data=await api("/api/analytics?days=30");
      const s=data.summary||{};
      const setVal=(id,val)=>{const el=document.getElementById(id);if(el)el.textContent=val;};
      setVal("stat-total",s.total||0);
      setVal("stat-pending",(s.drafts||0));
      setVal("stat-scheduled",s.scheduled||0);
    }catch(e2){console.warn('Fallback analytics also failed',e2);}
  }
}

function renderAnalyticsDashboard(summary, queue){
  const setVal=(id,val)=>{const el=document.getElementById(id);if(el)el.textContent=val;};

  // Row 1: Summary cards
  setVal("stat-total", summary.total_posts||0);
  setVal("stat-week-count", (summary.posted_this_week||0)+' this week');
  setVal("stat-month-count", (summary.posted_this_month||0)+' this month');

  const pendingVal = summary.pending_review||0;
  setVal("stat-pending", pendingVal);
  const pendingEl=document.getElementById("stat-pending");
  if(pendingEl){pendingEl.className='stat-value'+(pendingVal>0?' has-pending':'');}

  setVal("stat-scheduled", summary.scheduled||0);

  // Queue status
  const nextPost = queue.next_scheduled;
  if(nextPost && nextPost.scheduled_at){
    const dt=new Date(nextPost.scheduled_at);
    setVal("stat-next-post", dt.toLocaleDateString(undefined,{month:'short',day:'numeric'})+' '+dt.toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'}));
  } else {
    setVal("stat-next-post", "None");
  }

  const dot=document.getElementById("queue-health-dot");
  const label=document.getElementById("queue-health-label");
  const totalQueued=(queue.queue_depth?.pending_review||0)+(queue.queue_depth?.scheduled||0);
  if(dot&&label){
    if(totalQueued>5){dot.style.background='#22c55e';label.textContent='Queue active ('+totalQueued+')';}
    else if(totalQueued>0){dot.style.background='#eab308';label.textContent='Queue low ('+totalQueued+')';}
    else{dot.style.background='#555';label.textContent='Queue empty';}
  }

  // Row 2: Platform bars
  const barsEl=document.getElementById("adv-platform-bars");
  if(barsEl){
    const platforms=summary.by_platform||{};
    const entries=Object.entries(platforms);
    if(!entries.length){
      barsEl.innerHTML='<div style="font-size:12px;color:var(--text-dim);padding:12px 0">No platform data yet.</div>';
    } else {
      const maxTotal=Math.max(...entries.map(([,s])=>s.total),1);
      barsEl.innerHTML=entries.map(([name,s])=>{
        const pct=Math.max((s.total/maxTotal)*100,2);
        const color=PLATFORM_COLORS[name]||'#888';
        return '<div class="adv-bar-row">'+
          '<div class="adv-bar-label"><span class="dot '+esc(name)+'" style="width:8px;height:8px"></span>'+esc(name)+'</div>'+
          '<div class="adv-bar-track"><div class="adv-bar-fill" style="width:'+pct+'%;background:'+color+'">'+s.total+'</div></div>'+
          '<div class="adv-bar-stats"><span>'+s.posted+' posted</span><span>'+s.pending+' pending</span><span>'+s.scheduled+' sched</span></div>'+
          '</div>';
      }).join('');
    }
  }

  // Row 3: Content type pills
  const typesEl=document.getElementById("adv-content-types");
  if(typesEl){
    const types=summary.by_content_type||{};
    const entries=Object.entries(types);
    if(!entries.length){
      typesEl.innerHTML='<div style="font-size:12px;color:var(--text-dim)">No content type data yet.</div>';
    } else {
      typesEl.innerHTML=entries.map(([name,s])=>{
        const label=(name||'unknown').replace(/_/g,' ').replace(/\\b\\w/g,c=>c.toUpperCase());
        return '<div class="adv-type-pill">'+esc(label)+' <span class="pill-count">'+s.total+'</span>'+(s.posted?' <span style="font-size:10px;color:var(--text-dim)">('+s.posted+' posted)</span>':'')+'</div>';
      }).join('');
    }
  }

  // Row 4: Recent posts table (from cached posts)
  const tbody=document.getElementById('analytics-table-body');
  if(tbody){
    const posts=cachedPosts.slice(0,15);
    if(!posts.length){
      tbody.innerHTML='<tr><td colspan="4" style="text-align:center;color:var(--text-dim);padding:24px;">No content yet</td></tr>';
    } else {
      tbody.innerHTML=posts.map(p=>{
        const preview=(p.content||'').substring(0,80)+((p.content||'').length>80?'...':'');
        const status=p.status||'draft';
        const statusClass='adv-status-'+status.replace(/\\s+/g,'_');
        const platName=PLATFORM_NAMES[p.platform]||p.platform||'--';
        const dateStr=p.posted_at?fmtTime(p.posted_at):(p.scheduled_at?fmtTime(p.scheduled_at):'--');
        return '<tr><td><span class="dot '+esc(p.platform||'')+'" style="width:8px;height:8px;display:inline-block;vertical-align:middle;margin-right:6px"></span>'+esc(platName)+'</td><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(preview)+'</td><td>'+esc(dateStr)+'</td><td><span class="adv-status-pill '+statusClass+'">'+esc(status.replace(/_/g,' '))+'</span></td></tr>';
      }).join('');
    }
  }

  document.getElementById('analytics-updated').textContent='Last updated: '+new Date().toLocaleString();
}

async function refreshAnalytics(){
  toast('Refreshing analytics...','info');
  await loadAdvancedAnalytics();
  toast('Analytics refreshed','success');
}

// ========== MEDIA LIBRARY ==========
function getMediaLibrary(){try{return JSON.parse(localStorage.getItem('puresurf_media'))||[];}catch{return[];}}
function saveMediaLibrary(media){localStorage.setItem('puresurf_media',JSON.stringify(media));}

function addToMediaLibrary(fileObj){
  const media=getMediaLibrary();
  media.unshift({id:fileObj.id,name:fileObj.name,type:fileObj.type,size:fileObj.size,data:fileObj.data,uploadedAt:new Date().toISOString()});
  saveMediaLibrary(media);renderMediaGrid();
}

function renderMediaGrid(){
  const grid=document.getElementById('media-grid');
  const empty=document.getElementById('media-empty');
  const media=getMediaLibrary();
  if(!media.length){grid.innerHTML='';empty.style.display='block';return;}
  empty.style.display='none';
  grid.innerHTML=media.map(m=>{
    const date=new Date(m.uploadedAt).toLocaleDateString();
    const sizeKb=(m.size/1024).toFixed(0)+' KB';
    return '<div class="media-item"><button class="media-delete" onclick="deleteMedia(\\''+m.id+'\\')">&times;</button><div class="media-thumb-box"><img src="'+m.data+'" alt="'+esc(m.name)+'"></div><div class="media-info"><div class="media-name">'+esc(m.name)+'</div><div class="media-meta">'+sizeKb+' | '+date+'</div></div></div>';
  }).join('');
}

function deleteMedia(id){
  saveMediaLibrary(getMediaLibrary().filter(m=>m.id!==id));
  renderMediaGrid();toast('Media deleted','info');
}

// Media upload input
document.getElementById('media-upload-input').addEventListener('change',function(){
  Array.from(this.files).forEach(file=>{
    const reader=new FileReader();
    reader.onload=(e)=>{
      addToMediaLibrary({id:Date.now()+'_'+Math.random().toString(36).substr(2,6),name:file.name,type:file.type,size:file.size,data:e.target.result,base64:e.target.result.split(',')[1]});
      toast('Media uploaded','success');
    };
    reader.readAsDataURL(file);
  });
});

// Media drop zone
const mediaDropZone=document.getElementById('media-drop-zone');
if(mediaDropZone){
  mediaDropZone.addEventListener('click',()=>document.getElementById('media-upload-input').click());
  mediaDropZone.addEventListener('dragover',(e)=>{e.preventDefault();mediaDropZone.classList.add('dragover');});
  mediaDropZone.addEventListener('dragleave',()=>mediaDropZone.classList.remove('dragover'));
  mediaDropZone.addEventListener('drop',(e)=>{
    e.preventDefault();mediaDropZone.classList.remove('dragover');
    Array.from(e.dataTransfer.files).forEach(file=>{
      const reader=new FileReader();
      reader.onload=(ev)=>{
        addToMediaLibrary({id:Date.now()+'_'+Math.random().toString(36).substr(2,6),name:file.name,type:file.type,size:file.size,data:ev.target.result,base64:ev.target.result.split(',')[1]});
        toast('Media uploaded','success');
      };
      reader.readAsDataURL(file);
    });
  });
}

// ========== LIGHTBOX ==========
let lightboxHiddenModals=[];
function openLightbox(src){
  const modals=document.querySelectorAll('.edit-modal-overlay.active,.confirm-modal-overlay.active');
  lightboxHiddenModals=[];
  modals.forEach(m=>{m.style.visibility='hidden';lightboxHiddenModals.push(m);});
  document.getElementById("lightbox-img").src=src;
  document.getElementById("img-lightbox").classList.add("active");
  document.body.style.overflow="hidden";
}
function closeLightbox(){
  document.getElementById("img-lightbox").classList.remove("active");
  document.body.style.overflow="";
  lightboxHiddenModals.forEach(m=>{m.style.visibility='';});
  lightboxHiddenModals=[];
}

// Global keyboard shortcuts
document.addEventListener("keydown",(e)=>{
  if(e.key==="Escape"){
    if(document.getElementById("img-lightbox").classList.contains("active")){closeLightbox();return;}
    if(document.getElementById("qg-modal-overlay").classList.contains("active")){qgGoBack();return;}
    if(currentEditPostId){closeEditModal();return;}
    if(pendingDeleteId){cancelDelete();return;}
    const connectModal=document.getElementById("connect-modal");if(connectModal){connectModal.remove();return;}
  }
});

// Click on images to open lightbox
document.addEventListener("click",(e)=>{
  const img=e.target.closest(".post-thumb img, .modal-img-preview img");
  if(img){e.preventDefault();e.stopPropagation();openLightbox(img.src);}
});

// ========== DRAG-DROP CALENDAR RESCHEDULING ==========
let dragState = { postId: null, originalDate: null, originalScheduledAt: null, draggedElement: null };

function onDragStart(event, postId, scheduledAt) {
  dragState.postId = postId;
  dragState.originalScheduledAt = scheduledAt;
  dragState.draggedElement = event.target.closest('.post-card, .month-card, .week-post-chip, [data-post-id]');
  if (scheduledAt) dragState.originalDate = new Date(scheduledAt);
  if (dragState.draggedElement) {
    dragState.draggedElement.style.opacity = '0.5';
    dragState.draggedElement.style.transform = 'scale(1.02)';
  }
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', postId);
}

function onDragEnd(event) {
  if (dragState.draggedElement) {
    dragState.draggedElement.style.opacity = '';
    dragState.draggedElement.style.transform = '';
  }
  document.querySelectorAll('.day-cell.drag-over, .cal-day.drag-over, .cal-cell.drag-over, .month-cell.drag-over, .week-cell.drag-over').forEach(el => {
    el.classList.remove('drag-over', 'drag-over-valid', 'drag-over-conflict');
  });
  dragState = { postId: null, originalDate: null, originalScheduledAt: null, draggedElement: null };
}

function onDragOver(event, dayElement) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'move';
  dayElement.classList.add('drag-over');
  const conflicts = checkConflicts(dragState.postId, dayElement.dataset.date);
  dayElement.classList.toggle('drag-over-conflict', conflicts.length > 0);
  dayElement.classList.toggle('drag-over-valid', conflicts.length === 0);
}

function onDragLeave(event, dayElement) {
  dayElement.classList.remove('drag-over', 'drag-over-valid', 'drag-over-conflict');
}

async function onDrop(event, dayElement) {
  event.preventDefault();
  dayElement.classList.remove('drag-over', 'drag-over-valid', 'drag-over-conflict');
  const postId = dragState.postId;
  const targetDate = dayElement.dataset.date;
  if (!postId || !targetDate) return;
  const original = dragState.originalScheduledAt ? new Date(dragState.originalScheduledAt) : new Date();
  const [y, mo, d] = targetDate.split('-').map(Number);
  const newDate = new Date(y, mo - 1, d, original.getHours(), original.getMinutes(), 0);
  const newScheduledAt = newDate.toISOString();
  try {
    const res = await fetch(API + '/api/content/' + postId, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN },
      body: JSON.stringify({ scheduled_at: newScheduledAt })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    toast('Rescheduled to ' + formatDragDate(newScheduledAt), 'success');
    await refreshAllData();
  } catch(err) {
    toast('Reschedule failed: ' + err.message, 'error');
  }
}

function checkConflicts(postId, targetDate) {
  const conflicts = [];
  const targetDay = document.querySelector('[data-date="' + targetDate + '"]');
  if (!targetDay) return conflicts;
  const cards = targetDay.querySelectorAll('[data-post-id]');
  const draggedCard = document.querySelector('[data-post-id="' + postId + '"]');
  const draggedPlatform = draggedCard ? (draggedCard.querySelector('.platform-chip, .platform-badge, .kanban-platform-chip') || {}).textContent || '' : '';
  cards.forEach(c => {
    if (c.dataset.postId === postId) return;
    const chip = c.querySelector('.platform-chip, .platform-badge, .kanban-platform-chip');
    const currentPlatform = chip ? chip.textContent.trim() : '';
    if (currentPlatform === draggedPlatform && draggedPlatform) conflicts.push({ id: c.dataset.postId, platform: currentPlatform });
  });
  return conflicts;
}

function formatDragDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

// ========== QUALITY GATE (BANNED WORD CHECKER) ==========
const BANNED_WORDS = [
  { word: 'chatbot', reason: 'Brand voice: use AI partner or conversational interface' },
  { word: 'ai tool', reason: 'Brand voice: say AI partner, not AI tool' },
  { word: 'ai assistant', reason: 'Brand voice: never use assistant' },
  { word: 'saas', reason: 'Brand voice: say software platform or just platform' },
  { word: 'free trial', reason: 'Brand voice: never mention free trial' },
  { word: 'leverage', reason: 'Brand voice: use align, use, apply instead' },
  { word: 'disruption', reason: 'Brand voice: disruption is banned' },
  { word: 'disruptive', reason: 'Brand voice: use transformative or innovative' },
  { word: 'best-in-class', reason: 'Brand voice: overused marketing speak' },
  { word: 'cutting-edge', reason: 'Brand voice: overused marketing speak' },
  { word: 'game-changer', reason: 'Brand voice: overused marketing speak' },
  { word: 'revolutionary', reason: 'Brand voice: overused marketing speak' },
  { word: 'synergy', reason: 'Brand voice: corporate speak' },
  { word: 'click here', reason: 'Use descriptive link text instead' },
  { word: 'learn more', reason: 'Use descriptive link text instead' },
];

const QG_SCAN_TARGETS = ['body', 'title', 'banner_url'];

function qualityGate(post) {
  const violations = [];
  for (const target of QG_SCAN_TARGETS) {
    if (!post[target]) continue;
    const text = post[target].toLowerCase();
    for (const { word, reason } of BANNED_WORDS) {
      if (text.includes(word)) {
        violations.push({
          field: target,
          word: word,
          reason: reason,
          context: getQGContext(post[target], word)
        });
      }
    }
  }
  return {
    pass: violations.length === 0,
    violations: violations,
    summary: violations.length === 0
      ? 'Content passes quality gate'
      : 'Quality gate FAILED: ' + violations.length + ' violation(s) found'
  };
}

function getQGContext(text, word) {
  const lower = text.toLowerCase();
  const idx = lower.indexOf(word);
  if (idx === -1) return '';
  const start = Math.max(0, idx - 30);
  const end = Math.min(text.length, idx + word.length + 30);
  return '..."' + text.slice(start, end) + '"...';
}

function renderViolationsHTML(violations) {
  if (!violations || violations.length === 0) {
    return '<div class="qg-pass">Content passes quality gate</div>';
  }
  let html = '<div class="qg-fail"><strong>Quality gate failed \\u2014 ' + violations.length + ' violation(s):</strong><ul>';
  for (const v of violations) {
    html += '<li><code>' + esc(v.word) + '</code> in ' + v.field + ': ' + esc(v.reason) + '<br><span class="qg-context">' + esc(v.context) + '</span></li>';
  }
  html += '</ul></div>';
  return html;
}

// Quality Gate modal state
let qgPendingApproveId = null;
let qgPendingApproveAction = null;

function showQGModal(violations, postId, action) {
  qgPendingApproveId = postId;
  qgPendingApproveAction = action;
  document.getElementById('qg-modal-violations').innerHTML = renderViolationsHTML(violations);
  document.getElementById('qg-modal-overlay').classList.add('active');
}

function qgGoBack() {
  document.getElementById('qg-modal-overlay').classList.remove('active');
  qgPendingApproveId = null;
  qgPendingApproveAction = null;
  // If we have edit modal open, focus back on it
  if (currentEditPostId) {
    openEditModal(currentEditPostId);
  }
}

async function qgApproveAnyway() {
  document.getElementById('qg-modal-overlay').classList.remove('active');
  const id = qgPendingApproveId;
  const action = qgPendingApproveAction;
  qgPendingApproveId = null;
  qgPendingApproveAction = null;
  if (action === 'approve' && id) {
    await doApprovePost(id);
  } else if (action === 'kanbanApprove' && id) {
    await doApprovePost(id);
  }
}

async function doApprovePost(id) {
  try {
    await api("/api/content/" + id, { method: "PATCH", body: JSON.stringify({ status: "scheduled" }) });
    toast('Post approved', 'success'); await refreshAllData();
  } catch(e) { toast('Failed: ' + e.message, 'error'); }
}

// Update modal quality gate results on content change
function updateModalQG() {
  const contentEl = document.getElementById('modal-edit-content');
  const titleEl = document.getElementById('modal-edit-title');
  const resultsEl = document.getElementById('modal-qg-results');
  if (!contentEl || !resultsEl) return;
  const post = { body: contentEl.value, title: titleEl ? titleEl.value : '' };
  const result = qualityGate(post);
  resultsEl.innerHTML = renderViolationsHTML(result.violations);
}

// ========== PLATFORM-SPECIFIC COMPOSER ==========
const PLATFORM_CHAR_LIMITS = { twitter: 280, bluesky: 300, linkedin: 3000, threads: 500, facebook: 63206, instagram: 2200, tiktok: 2200, reddit: 40000 };
const PLATFORM_DOT_COLORS = { linkedin: '#0a66c2', twitter: '#1da1f2', bluesky: '#0085ff', threads: '#fff', instagram: '#e4405f', facebook: '#1877f2', tiktok: '#69c9d0', reddit: '#ff4500' };

let platformComposerExpanded = false;
let platformSectionStates = {};

function togglePlatformComposer() {
  platformComposerExpanded = !platformComposerExpanded;
  const toggle = document.getElementById('pc-toggle');
  const body = document.getElementById('pc-body');
  toggle.classList.toggle('expanded', platformComposerExpanded);
  body.classList.toggle('visible', platformComposerExpanded);
  if (platformComposerExpanded) renderPlatformComposer();
}

function renderPlatformComposer() {
  const body = document.getElementById('pc-body');
  const platforms = getSelectedPlatforms();
  const mainText = document.getElementById('post-text').value;
  const countEl = document.getElementById('pc-platform-count');
  countEl.textContent = platforms.length ? '(' + platforms.length + ' platform' + (platforms.length > 1 ? 's' : '') + ')' : '';

  if (!platforms.length) {
    body.innerHTML = '<div style="padding:16px;color:var(--text-dim);font-size:13px;text-align:center">Select platforms above to customize captions per platform.</div>';
    return;
  }

  let html = '';
  platforms.forEach(pl => {
    const limit = PLATFORM_CHAR_LIMITS[pl] || 3000;
    const dotColor = PLATFORM_DOT_COLORS[pl] || 'var(--text-dim)';
    const name = PLATFORM_NAMES[pl] || pl;
    const existingText = document.getElementById('pc-textarea-' + pl)?.value;
    const text = existingText !== undefined ? existingText : '';
    const isExpanded = platformSectionStates[pl] || false;
    const len = text.length;
    const remaining = limit - len;
    const countClass = remaining < 0 ? 'over' : remaining < 20 ? 'warn' : 'ok';

    html += '<div class="pc-section" data-platform="' + pl + '">';
    html += '<div class="pc-section-header' + (isExpanded ? ' expanded' : '') + '" onclick="togglePCSection(\\'' + pl + '\\')">';
    html += '<span class="pc-dot" style="background:' + dotColor + '"></span>';
    html += '<span>' + esc(name) + '</span>';
    html += '<span style="font-size:11px;color:var(--text-dim);margin-left:8px">' + len + '/' + limit + '</span>';
    html += '<span class="pc-arrow">&#9660;</span>';
    html += '</div>';
    html += '<div class="pc-section-body' + (isExpanded ? ' visible' : '') + '">';
    html += '<textarea id="pc-textarea-' + pl + '" placeholder="Custom caption for ' + name + '..." oninput="updatePCCharCount(\\'' + pl + '\\')">' + esc(text) + '</textarea>';
    html += '<div class="pc-char-count ' + countClass + '" id="pc-count-' + pl + '">' + remaining + ' / ' + limit + ' remaining</div>';
    html += '<div class="pc-actions">';
    html += '<button class="btn btn-ghost btn-sm" onclick="pcCopyFromMain(\\'' + pl + '\\')">Copy from main</button>';
    html += '<button class="btn btn-ghost btn-sm" onclick="pcClear(\\'' + pl + '\\')">Clear</button>';
    html += '</div></div></div>';
  });

  html += '<div class="pc-copy-all"><button class="btn btn-ghost btn-sm" onclick="pcCopyToAll()">Copy main to all platforms</button></div>';
  body.innerHTML = html;
}

function togglePCSection(platform) {
  platformSectionStates[platform] = !platformSectionStates[platform];
  renderPlatformComposer();
}

function updatePCCharCount(platform) {
  const ta = document.getElementById('pc-textarea-' + platform);
  const countEl = document.getElementById('pc-count-' + platform);
  if (!ta || !countEl) return;
  const limit = PLATFORM_CHAR_LIMITS[platform] || 3000;
  const len = ta.value.length;
  const remaining = limit - len;
  countEl.textContent = remaining + ' / ' + limit + ' remaining';
  countEl.className = 'pc-char-count ' + (remaining < 0 ? 'over' : remaining < 20 ? 'warn' : 'ok');
}

function pcCopyFromMain(platform) {
  const mainText = document.getElementById('post-text').value;
  const ta = document.getElementById('pc-textarea-' + platform);
  if (ta) { ta.value = mainText; updatePCCharCount(platform); }
}

function pcClear(platform) {
  const ta = document.getElementById('pc-textarea-' + platform);
  if (ta) { ta.value = ''; updatePCCharCount(platform); }
}

function pcCopyToAll() {
  const mainText = document.getElementById('post-text').value;
  const platforms = getSelectedPlatforms();
  platforms.forEach(pl => {
    const ta = document.getElementById('pc-textarea-' + pl);
    if (ta) { ta.value = mainText; updatePCCharCount(pl); }
  });
  toast('Main caption copied to all platforms', 'info');
}

function getPlatformCaptions() {
  const captions = {};
  const platforms = getSelectedPlatforms();
  const mainText = document.getElementById('post-text').value;
  platforms.forEach(pl => {
    const ta = document.getElementById('pc-textarea-' + pl);
    const text = ta ? ta.value.trim() : '';
    captions[pl] = text || mainText;
  });
  return captions;
}

// ========== INIT ==========
if(TOKEN){bootApp().catch(()=>{});}
</script>

</body>
</html>
`;


// ---------- Helpers ----------
function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      ...(init.headers || {}),
    },
  });
}

function err(status, message) {
  return json({ error: message }, { status });
}

function newId() {
  return crypto.randomUUID();
}

function nowIso() {
  return new Date().toISOString();
}

function expiresAt(ms = SESSION_DURATION_MS) {
  return new Date(Date.now() + ms).toISOString();
}

// ---------- Phase 2: Role-Based Permissions ----------
// Role hierarchy: admin > editor > reviewer > viewer
// Also supports legacy roles: owner, leader, system, member (treated as editor-level)
const ROLE_PERMISSIONS = {
  admin:    { read: true, create: true, edit: true, delete: true, approve: true, manage_roles: true },
  owner:    { read: true, create: true, edit: true, delete: true, approve: true, manage_roles: true },
  leader:   { read: true, create: true, edit: true, delete: true, approve: true, manage_roles: true },
  system:   { read: true, create: true, edit: true, delete: true, approve: true, manage_roles: true },
  editor:   { read: true, create: true, edit: true, delete: false, approve: false, manage_roles: false },
  member:   { read: true, create: true, edit: true, delete: false, approve: false, manage_roles: false },
  reviewer: { read: true, create: false, edit: false, delete: false, approve: true, manage_roles: false },
  viewer:   { read: true, create: false, edit: false, delete: false, approve: false, manage_roles: false },
};

function hasPermission(role, action) {
  const perms = ROLE_PERMISSIONS[role];
  if (!perms) return false;
  return !!perms[action];
}

async function sha256(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

// PBKDF2 for passwords
async function hashPassword(password, saltHex = null) {
  const encoder = new TextEncoder();
  const salt = saltHex
    ? Uint8Array.from(saltHex.match(/.{2}/g).map(h => parseInt(h, 16)))
    : crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey(
    "raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITER, hash: "SHA-256" },
    keyMaterial, 256
  );
  const hashArr = new Uint8Array(bits);
  const saltHexOut = Array.from(salt).map(b => b.toString(16).padStart(2, "0")).join("");
  const hashHex = Array.from(hashArr).map(b => b.toString(16).padStart(2, "0")).join("");
  return `${saltHexOut}:${hashHex}`;
}

async function verifyPassword(password, stored) {
  const [saltHex, expectedHash] = stored.split(":");
  if (!saltHex || !expectedHash) return false;
  const rehashed = await hashPassword(password, saltHex);
  return rehashed.split(":")[1] === expectedHash;
}

// HMAC verify for portal SSO
async function verifyHmacSignature(payloadB64, signatureHex, secret) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payloadB64));
  const sigHex = Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, "0")).join("");
  return sigHex === signatureHex;
}

// ---------- Auth ----------
async function getSession(request, env) {
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return null;

  // System API key (ContentRouter M2M auth) — synthetic system session
  if (env.ROUTER_API_KEY && token === env.ROUTER_API_KEY) {
    return {
      user_id: "system",
      email: "router@system",
      name: "ContentRouter",
      team_id: "system",
      role: "system",
      billing_tier: "system",
      expires_at: "9999-12-31T23:59:59Z"
    };
  }

  const row = await env.DB.prepare(
    `SELECT s.token, s.user_id, s.expires_at, u.email, u.name, u.team_id, u.role, u.billing_tier
     FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?`
  ).bind(token).first();

  if (!row) return null;
  if (row.expires_at < nowIso()) return null;
  return row;
}

async function requireAuth(request, env) {
  const sess = await getSession(request, env);
  if (!sess) return { error: err(401, "unauthorized"), sess: null };
  return { error: null, sess };
}

async function createSession(userId, request, env) {
  const token = crypto.getRandomValues(new Uint8Array(32));
  const tokenStr = Array.from(token).map(b => b.toString(16).padStart(2, "0")).join("");
  const ua = (request.headers.get("user-agent") || "").slice(0, 200);
  const ip = request.headers.get("cf-connecting-ip") || "";
  await env.DB.prepare(
    "INSERT INTO sessions (token, user_id, expires_at, user_agent, ip_address) VALUES (?, ?, ?, ?, ?)"
  ).bind(tokenStr, userId, expiresAt(), ua, ip).run();
  await env.DB.prepare(
    "UPDATE users SET last_login_at = ? WHERE id = ?"
  ).bind(nowIso(), userId).run();
  return tokenStr;
}

function setSessionCookie(response, token) {
  const maxAge = Math.floor(SESSION_DURATION_MS / 1000);
  response.headers.set(
    "set-cookie",
    `social_session=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`
  );
  return response;
}

// ---------- Route handlers ----------
// ---------- Signup ----------
// Creates new user + team (first user on a team owns it), returns session token.
async function handleSignup(request, env) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown";

  // Same anti-abuse as login
  if (!(await rlCheckD1("signup_total", ip, 60 * 60 * 1000, 10, env))) {
    return err(429, "too many signups from this IP - try again in an hour");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const email = (body.email || "").trim().toLowerCase();
  const password = body.password || "";
  const name = (body.name || "").trim();
  const teamName = (body.team_name || "").trim() || (name ? `${name}'s Team` : "New Team");

  if (!email || !password || !name) return err(400, "email, password, and name are required");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return err(400, "invalid email format");
  if (password.length < 12) return err(400, "password must be at least 12 characters");
  if (name.length > 80) return err(400, "name too long (max 80 chars)");

  // Dedup: existing user with this email?
  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
  if (existing) return err(409, "an account with this email already exists");

  const teamId = newId();
  const userId = newId();
  const passwordHash = await hashPassword(password);

  try {
    // Create team + user atomically via D1 batch
    await env.DB.batch([
      env.DB.prepare(
        "INSERT INTO teams (id, name) VALUES (?, ?)"
      ).bind(teamId, teamName),
      env.DB.prepare(
        "INSERT INTO users (id, team_id, email, name, role, billing_tier, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)"
      ).bind(userId, teamId, email, name, "owner", "free", passwordHash)
    ]);
  } catch (e) {
    if (String(e.message || e).includes("UNIQUE")) {
      return err(409, "account already exists");
    }
    throw e;
  }

  const token = await createSession(userId, request, env);
  const resp = json({
    status: "created",
    token,
    user: { id: userId, email, name, team_id: teamId, role: "owner", billing_tier: "free" },
    next_steps: [
      "connect a social account at /api/social_accounts (LinkedIn or Bluesky)",
      "register an AI partner at /api/ai_partners (mode:poll default)",
      "start generating weekly content"
    ]
  }, { status: 201 });
  return setSessionCookie(resp, token);
}

async function handleLogin(request, env) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown";

  if (!(await rlCheckD1("login_total", ip, LOGIN_TOTAL_WINDOW_MS, LOGIN_TOTAL_LIMIT, env))) {
    return err(429, "too many login attempts - try again later");
  }
  if (!(await rlCheckD1("login_failed", ip, LOGIN_FAILED_WINDOW_MS, LOGIN_FAILED_LIMIT, env))) {
    return err(429, "too many failed attempts - try again in 15 minutes");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const email = (body.email || "").trim().toLowerCase();
  const password = body.password || "";
  if (!email || !password) return err(400, "email and password required");

  const user = await env.DB.prepare(
    "SELECT id, password_hash FROM users WHERE email = ?"
  ).bind(email).first();

  const storedHash = (user && user.password_hash) ? user.password_hash : DUMMY_PW_HASH;
  const passwordOk = await verifyPassword(password, storedHash);
  if (!user || !user.password_hash || !passwordOk) {
    return err(401, "invalid credentials");
  }

  await rlRemoveLatest("login_failed", ip, env);

  const token = await createSession(user.id, request, env);
  const resp = json({ status: "ok", token });
  return setSessionCookie(resp, token);
}

async function handleSsoExchange(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (!token) return err(400, "token required");

  const [payloadB64, signatureHex] = token.split(".");
  if (!payloadB64 || !signatureHex) return err(400, "malformed token");

  const secret = env.PORTAL_SSO_SECRET || "";
  if (!secret) return err(500, "sso not configured");

  const ok = await verifyHmacSignature(payloadB64, signatureHex, secret);
  if (!ok) return err(401, "invalid signature");

  let payload;
  try {
    const padded = payloadB64 + "=".repeat((4 - payloadB64.length % 4) % 4);
    payload = JSON.parse(atob(padded.replace(/-/g, "+").replace(/_/g, "/")));
  } catch { return err(400, "invalid payload"); }

  if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return err(401, "token expired");
  if (!payload.user_id) return err(400, "missing user_id");

  const user = await env.DB.prepare("SELECT id FROM users WHERE id = ?").bind(payload.user_id).first();
  if (!user) return err(404, "user not found");

  const sessionToken = await createSession(payload.user_id, request, env);
  const redirectTo = payload.redirect || "/";
  const resp = new Response(null, { status: 302, headers: { location: redirectTo } });
  return setSessionCookie(resp, sessionToken);
}

async function handleMe(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  return json({
    id: sess.user_id,
    email: sess.email,
    name: sess.name,
    role: sess.role,
    team_id: sess.team_id,
    billing_tier: sess.billing_tier,
  });
}

async function handleListContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const url = new URL(request.url);
  const status = url.searchParams.get("status");
  const platform = url.searchParams.get("platform");
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "50"), 500);

  let q = "SELECT * FROM content_items WHERE user_id = ?";
  const args = [sess.user_id];
  if (status) { q += " AND status = ?"; args.push(status); }
  if (platform) { q += " AND platform = ?"; args.push(platform); }
  q += " ORDER BY COALESCE(scheduled_at, created_at) DESC LIMIT ?";
  args.push(limit);

  const { results } = await env.DB.prepare(q).bind(...args).all();
  return json({ items: results || [] });
}

async function handleCreateContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Role-based permission check: viewer and reviewer cannot create content
  if (!hasPermission(sess.role, "create")) {
    return err(403, "your role does not allow creating content");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  for (const f of ["social_account_id", "platform", "body"]) {
    if (!body[f]) return err(400, `${f} required`);
  }

  const acct = await env.DB.prepare(
    "SELECT id FROM social_accounts WHERE id = ? AND user_id = ?"
  ).bind(body.social_account_id, sess.user_id).first();
  if (!acct) return err(404, "social account not found or not owned");

  const id = newId();
  const now = nowIso();
  await env.DB.prepare(
    `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, content_type, generated_by, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).bind(
    id, sess.user_id, body.social_account_id, body.platform,
    body.status || "draft", body.scheduled_at || null, body.body,
    JSON.stringify(body.media_refs || []), body.content_type || "post",
    body.generated_by || "human", now, now
  ).run();

  const item = await env.DB.prepare("SELECT * FROM content_items WHERE id = ?").bind(id).first();
  return json({ item }, { status: 201 });
}

async function handleUpdateContent(request, env, itemId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Role-based permission check: viewer cannot edit; reviewer can only approve
  if (!hasPermission(sess.role, "edit") && !hasPermission(sess.role, "approve")) {
    return err(403, "your role does not allow editing content");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  // If role is reviewer (approve-only), restrict to status changes only
  if (sess.role === "reviewer") {
    const nonStatusFields = Object.keys(body).filter(k => k !== "status" && k !== "rejection_reason");
    if (nonStatusFields.length > 0) {
      return err(403, "reviewer role can only change status (approve/reject)");
    }
  }

  // Inline image replace via base64
  if (body.media_base64 && env.UPLOADS) {
    try {
      const raw = Uint8Array.from(atob(body.media_base64), c => c.charCodeAt(0));
      const fname = (body.media_filename || "upload.png").replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 100);
      const key = `${sess.user_id}/${Date.now()}-${crypto.randomUUID().slice(0,8)}-${fname}`;
      const mime = fname.endsWith(".jpg") || fname.endsWith(".jpeg") ? "image/jpeg" : fname.endsWith(".webp") ? "image/webp" : "image/png";
      await env.UPLOADS.put(key, raw.buffer, { httpMetadata: { contentType: mime } });
      const imgUrl = `https://social.purebrain.ai/media/${encodeURI(key)}`;
      body.media_refs = JSON.stringify([imgUrl]);
    } catch (e) {
      return err(500, "image upload failed: " + String(e.message || e).slice(0, 200));
    }
  }

  const allowed = ["body", "media_refs", "scheduled_at", "status", "content_type", "title", "rejection_reason", "last_error", "retry_count", "routing_decision", "posted_at", "post_url", "verification_status", "performance_metrics"];
  const updates = {};
  for (const k of allowed) if (k in body) updates[k] = body[k];
  if (Object.keys(updates).length === 0) return err(400, "no valid fields");

  const existing = await env.DB.prepare("SELECT user_id FROM content_items WHERE id = ?").bind(itemId).first();
  if (!existing) return err(404, "not found");
  // Allow: own content always, admin/owner/leader/system for any, reviewer for status-only (checked above)
  const canEditOthers = ["leader", "system", "admin", "owner", "reviewer"].includes(sess.role);
  if (existing.user_id !== sess.user_id && !canEditOthers) {
    return err(403, "forbidden");
  }

  // Stringify JSON fields
  for (const k of ["media_refs", "performance_metrics"]) {
    if (k in updates && typeof updates[k] !== "string") updates[k] = JSON.stringify(updates[k]);
  }

  // Auto-set approved_by and scheduled_at when status transitions to scheduled
  if (updates.status === "scheduled") {
    if (!body.approved_by) {
      updates.approved_by = sess.user_id;
      updates.approved_at = nowIso();
    }
    // Auto-set scheduled_at to NOW if not provided (so ContentRouter picks it up immediately)
    if (!updates.scheduled_at) {
      updates.scheduled_at = nowIso();
    }
  }

  const setClauses = Object.keys(updates).map(k => `${k} = ?`);
  setClauses.push("updated_at = ?");
  const args = [...Object.values(updates), nowIso(), itemId];

  await env.DB.prepare(
    `UPDATE content_items SET ${setClauses.join(", ")} WHERE id = ?`
  ).bind(...args).run();

  const item = await env.DB.prepare("SELECT * FROM content_items WHERE id = ?").bind(itemId).first();
  return json({ item });
}

async function handleTeamContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const url = new URL(request.url);
  const status = url.searchParams.get("status");
  const platform = url.searchParams.get("platform");
  const days = parseInt(url.searchParams.get("days") || "7");
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "200"), 1000);

  const since = new Date(Date.now() - days * 86400 * 1000).toISOString();

  let q = `SELECT ci.*, u.name AS user_name, u.email AS user_email
           FROM content_items ci JOIN users u ON ci.user_id = u.id
           WHERE u.team_id = ?
             AND ci.status IN ('scheduled', 'posting', 'posted', 'failed')
             AND COALESCE(ci.scheduled_at, ci.posted_at, ci.created_at) >= ?`;
  const args = [sess.team_id, since];
  if (status) { q += " AND ci.status = ?"; args.push(status); }
  if (platform) { q += " AND ci.platform = ?"; args.push(platform); }
  q += " ORDER BY COALESCE(ci.scheduled_at, ci.posted_at, ci.created_at) DESC LIMIT ?";
  args.push(limit);

  const { results } = await env.DB.prepare(q).bind(...args).all();
  return json({ items: results || [] });
}

// ---------- Social accounts CRUD ----------
async function handleListAccounts(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const { results } = await env.DB.prepare(
    `SELECT id, user_id, platform, account_handle, account_display_name, auth_type,
            surf_profile_id, last_verified_at, health_status, created_at
     FROM social_accounts WHERE user_id = ? ORDER BY platform, account_handle`
  ).bind(sess.user_id).all();
  return json({ accounts: results || [] });
}

async function handleCreateAccount(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  for (const f of ["platform", "account_handle", "auth_type"]) {
    if (!body[f]) return err(400, `${f} required`);
  }
  if (!["api_oauth", "puresurf_session"].includes(body.auth_type)) {
    return err(400, "auth_type must be api_oauth or puresurf_session");
  }

  const id = newId();
  // Profile ID must include account_handle so a user with multiple handles
  // on the same platform (e.g. @brand1 + @brand2 on twitter) gets isolated
  // browser profiles. Sanitize handle to alphanumeric+underscore for filesystem
  // safety on the BaaS side.
  const handleSlug = String(body.account_handle || "").replace(/[^A-Za-z0-9_-]/g, "_").slice(0, 40) || "default";
  const surfProfileId = body.surf_profile_id || `${sess.user_id}-${body.platform}-${handleSlug}`;

  let encryptedCreds = null;
  let encryptedSession = null;
  if (body.credentials_encrypted) {
    try { encryptedCreds = await encryptSecret(body.credentials_encrypted, env); }
    catch (e) { return err(500, "encryption unavailable: " + e.message); }
  }
  if (body.session_token_encrypted) {
    try { encryptedSession = await encryptSecret(body.session_token_encrypted, env); }
    catch (e) { return err(500, "encryption unavailable: " + e.message); }
  }

  try {
    await env.DB.prepare(
      `INSERT INTO social_accounts (id, user_id, platform, account_handle, account_display_name, auth_type, credentials_encrypted, session_token_encrypted, surf_profile_id, health_status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      id, sess.user_id, body.platform, body.account_handle,
      body.account_display_name || body.account_handle,
      body.auth_type,
      encryptedCreds,
      encryptedSession,
      surfProfileId,
      "pending_verification"
    ).run();
  } catch (e) {
    if (String(e.message || e).includes("UNIQUE")) {
      return err(409, "account already exists for this platform/handle");
    }
    throw e;
  }

  const acct = await env.DB.prepare(
    `SELECT id, user_id, platform, account_handle, account_display_name, auth_type, surf_profile_id, health_status, created_at
     FROM social_accounts WHERE id = ?`
  ).bind(id).first();
  return json({ account: acct }, { status: 201 });
}

async function handleDeleteAccount(request, env, accountId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  const row = await env.DB.prepare("SELECT user_id FROM social_accounts WHERE id = ?").bind(accountId).first();
  if (!row) return err(404, "not found");
  if (row.user_id !== sess.user_id && sess.role !== "leader") return err(403, "forbidden");

  // Soft-delete by cascading content_items to cancelled
  await env.DB.prepare(
    "UPDATE content_items SET status = 'cancelled', last_error = 'social account disconnected', updated_at = ? WHERE social_account_id = ? AND status IN ('draft','pending_approval','scheduled')"
  ).bind(nowIso(), accountId).run();

  await env.DB.prepare("DELETE FROM social_accounts WHERE id = ?").bind(accountId).run();
  return json({ status: "deleted" });
}

// ---------- AI Partner registration ----------
async function handleListPartners(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const { results } = await env.DB.prepare(
    `SELECT id, user_id, partner_name, partner_endpoint, voice_profile, created_at
     FROM ai_partners WHERE user_id = ? ORDER BY partner_name`
  ).bind(sess.user_id).all();
  return json({ partners: results || [] });
}

// Billing tier → max AI partners per user
const PARTNER_LIMITS = {
  free: 1,
  team_member: 3,
  pro: 3,
  founder: 999,
  team: 999,
  enterprise: 999,
  system: 999
};

async function handleCreatePartner(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  if (!body.partner_name) return err(400, "partner_name required");

  // v1.1: mode is 'poll' (default) or 'webhook'. Poll requires no partner_endpoint.
  const mode = body.mode === "webhook" ? "webhook" : "poll";
  if (mode === "webhook" && !body.partner_endpoint) {
    return err(400, "partner_endpoint required for webhook mode");
  }

  // Billing enforcement
  const limit = PARTNER_LIMITS[sess.billing_tier] || PARTNER_LIMITS.free;
  const countRow = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM ai_partners WHERE user_id = ?"
  ).bind(sess.user_id).first();
  const currentCount = (countRow && countRow.c) || 0;
  if (currentCount >= limit) {
    return err(402, `AI partner limit reached (${currentCount}/${limit}). Upgrade plan to add more.`);
  }

  const id = newId();
  // For poll mode we mint a dedicated long-lived bearer (separate from user session)
  // so the partner can poll even after the user logs out.
  let pollToken = null;
  let pollTokenHash = null;
  if (mode === "poll") {
    pollToken = "pp_" + (crypto.randomUUID().replace(/-/g, "") + crypto.randomUUID().replace(/-/g, "")).slice(0, 48);
    // Hash for storage (same pattern as session tokens)
    try {
      const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(pollToken));
      pollTokenHash = Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, "0")).join("");
    } catch (e) {
      return err(500, "token mint failed");
    }
  }

  try {
    await env.DB.prepare(
      `INSERT INTO ai_partners (id, user_id, partner_name, partner_endpoint, api_key_encrypted, voice_profile, mode, poll_token_hash)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      id, sess.user_id, body.partner_name,
      body.partner_endpoint || null,
      body.api_key_encrypted || null,
      body.voice_profile ? JSON.stringify(body.voice_profile) : null,
      mode,
      pollTokenHash
    ).run();
  } catch (e) {
    if (String(e.message || e).includes("UNIQUE")) {
      return err(409, "partner with this name already registered for user");
    }
    throw e;
  }

  const partner = await env.DB.prepare(
    "SELECT id, user_id, partner_name, partner_endpoint, voice_profile, mode, created_at FROM ai_partners WHERE id = ?"
  ).bind(id).first();

  const response = {
    partner,
    limit_info: { current: currentCount + 1, max: limit, tier: sess.billing_tier }
  };
  // Only expose the raw poll token ONCE at registration (like AWS access keys).
  // If the partner loses it, they rotate via a future /api/ai_partners/{id}/rotate_token endpoint.
  if (pollToken) {
    response.poll_credentials = { token: pollToken, mode: "poll", note: "Store this bearer securely. Not retrievable later." };
  }
  return json(response, { status: 201 });
}

// ---------- v1.1 Poll endpoints ----------

// Look up a partner by its poll token. Returns {partner, error}.
async function resolvePollPartner(request, env, partnerId) {
  const auth = request.headers.get("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!token.startsWith("pp_")) return { error: err(401, "missing or invalid poll token") };
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token));
  const hash = Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, "0")).join("");
  const partner = await env.DB.prepare(
    "SELECT id, user_id, partner_name, mode FROM ai_partners WHERE id = ? AND poll_token_hash = ?"
  ).bind(partnerId, hash).first();
  if (!partner) return { error: err(401, "invalid poll token for this partner") };
  if (partner.mode !== "poll") return { error: err(400, "partner is not in poll mode") };
  // Touch last_polled_at for liveness tracking
  await env.DB.prepare(
    "UPDATE ai_partners SET last_polled_at = ? WHERE id = ?"
  ).bind(nowIso(), partnerId).run();
  return { partner };
}

async function handlePollWork(request, env, partnerId) {
  const { partner, error } = await resolvePollPartner(request, env, partnerId);
  if (error) return error;

  // Atomic claim: grab oldest pending job, mark claimed. SQLite lacks SELECT ... FOR UPDATE,
  // so we pick then UPDATE with WHERE status='pending' to detect races.
  // Expiry = 30 min from now.
  const expiresAt = new Date(Date.now() + 30 * 60 * 1000).toISOString();

  // Find next pending job for this partner
  const row = await env.DB.prepare(
    `SELECT id, job_type, payload, attempts FROM partner_jobs
     WHERE ai_partner_id = ? AND status = 'pending'
     ORDER BY created_at ASC LIMIT 1`
  ).bind(partner.id).first();

  if (!row) return new Response(null, { status: 204 });  // empty queue

  // Atomic claim
  const claim = await env.DB.prepare(
    `UPDATE partner_jobs SET status = 'claimed', claimed_at = ?, expires_at = ?, attempts = attempts + 1
     WHERE id = ? AND status = 'pending'`
  ).bind(nowIso(), expiresAt, row.id).run();

  if (!claim.meta || claim.meta.changes === 0) {
    // Lost race to another poll — return empty, partner will retry
    return new Response(null, { status: 204 });
  }

  return json({
    job_id: row.id,
    job_type: row.job_type,
    payload: row.payload ? JSON.parse(row.payload) : {},
    attempts: row.attempts + 1,
    claimed_at: nowIso(),
    expires_at: expiresAt
  });
}

// ---------- P2 Session Health Monitoring (Chy + Aether + Morphe) ----------
//
// POST /api/surf/heartbeat  — Aether's probe service writes here after probing BaaS
// GET  /api/surf/health/:account_id — dashboard reads latest health status
//
// Stateful writes: heartbeat rows only inserted when status CHANGES vs previous.
// Side effect: updates social_accounts.health_status + last_verified_at on any probe.

// Optional: service auth for the probe. Set SURF_PROBE_TOKEN in worker env.
// If unset, endpoint allows unauthenticated writes (suitable for same-VPC trusted service).
// ---------- Analytics Dashboard ----------
async function handleAnalytics(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const url = new URL(request.url);
  const days = Math.min(parseInt(url.searchParams.get("days") || "30"), 90);
  const since = new Date(Date.now() - days * 86400000).toISOString();

  // Summary stats
  const [totalRow, postedRow, scheduledRow, draftRow, platformStats, recentPosted, dailyActivity] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id = ?").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id = ? AND status = 'posted'").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id = ? AND status = 'scheduled'").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id = ? AND status = 'draft'").bind(sess.user_id).first(),
    // Per-platform breakdown
    env.DB.prepare(
      `SELECT platform, status, COUNT(*) as count FROM content_items
       WHERE user_id = ? AND created_at >= ? GROUP BY platform, status ORDER BY platform`
    ).bind(sess.user_id, since).all(),
    // Recent posted items with performance_metrics
    env.DB.prepare(
      `SELECT id, platform, body, posted_at, post_url, performance_metrics, generated_by
       FROM content_items WHERE user_id = ? AND status = 'posted' AND posted_at IS NOT NULL
       ORDER BY posted_at DESC LIMIT 20`
    ).bind(sess.user_id).all(),
    // Daily activity (posts per day over the period)
    env.DB.prepare(
      `SELECT DATE(COALESCE(posted_at, scheduled_at, created_at)) as day, COUNT(*) as count, status
       FROM content_items WHERE user_id = ? AND created_at >= ?
       GROUP BY day, status ORDER BY day DESC LIMIT 60`
    ).bind(sess.user_id, since).all()
  ]);

  // Aggregate platform stats into a cleaner structure
  const platforms = {};
  for (const row of (platformStats.results || [])) {
    if (!platforms[row.platform]) platforms[row.platform] = { total: 0, draft: 0, scheduled: 0, posted: 0, rejected: 0 };
    platforms[row.platform][row.status] = (platforms[row.platform][row.status] || 0) + row.count;
    platforms[row.platform].total += row.count;
  }

  // Parse performance_metrics for posted items
  const posted = (recentPosted.results || []).map(p => {
    let metrics = null;
    if (p.performance_metrics) {
      try { metrics = JSON.parse(p.performance_metrics); } catch {}
    }
    return { ...p, performance_metrics: metrics };
  });

  // Top performing (by engagement if metrics exist)
  const withEngagement = posted.filter(p => p.performance_metrics && typeof p.performance_metrics.engagement === "number");
  const topPerforming = withEngagement.sort((a, b) => (b.performance_metrics.engagement || 0) - (a.performance_metrics.engagement || 0)).slice(0, 5);

  return json({
    period_days: days,
    summary: {
      total: totalRow?.c || 0,
      posted: postedRow?.c || 0,
      scheduled: scheduledRow?.c || 0,
      drafts: draftRow?.c || 0
    },
    platforms,
    recent_posted: posted,
    top_performing: topPerforming,
    daily_activity: dailyActivity.results || []
  });
}

// ---------- Scratch Pad (Quartet shared, Morphe spec, Chy integration) ----------
async function handleScratchPadWrite(request, env) {
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const { author, key, value } = body;
  if (!author || !key || !value) return err(400, "author, key, and value required");
  const validAuthors = ['aether', 'chy', 'morphe', 'jared'];
  const validKeys = ['current-task', 'decision', 'blocker', 'idea', 'handoff', 'note'];
  if (!validAuthors.includes(author)) return err(400, "author must be one of: " + validAuthors.join(", "));
  if (!validKeys.includes(key)) return err(400, "key must be one of: " + validKeys.join(", "));
  const id = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT INTO agent_scratch_pad (id, author, key, value) VALUES (?, ?, ?, ?)"
  ).bind(id, author, key, value).run();
  return json({ id, author, key, status: "written" }, { status: 201 });
}

async function handleScratchPadRead(request, env) {
  const url = new URL(request.url);
  const key = url.searchParams.get("key");
  const author = url.searchParams.get("author");
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "50"), 200);
  let q = "SELECT * FROM agent_scratch_pad WHERE 1=1";
  const args = [];
  if (key && key !== "all") { q += " AND key = ?"; args.push(key); }
  if (author) { q += " AND author = ?"; args.push(author); }
  q += " ORDER BY created_at DESC LIMIT ?";
  args.push(limit);
  const { results } = await env.DB.prepare(q).bind(...args).all();
  return json({ entries: results || [] });
}

async function handleScratchPadDelete(request, env, id) {
  await env.DB.prepare("DELETE FROM agent_scratch_pad WHERE id = ?").bind(id).run();
  return json({ status: "deleted", id });
}

async function handleSurfHeartbeat(request, env) {
  // Optional service-token gate (probe service → worker)
  const expected = env.SURF_PROBE_TOKEN;
  if (expected) {
    const auth = request.headers.get("authorization") || "";
    const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
    if (token !== expected) return err(401, "invalid probe token");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  // Accept either {session_id} (= surf_profile_id on BaaS) or {social_account_id}
  let account = null;
  if (body.social_account_id) {
    account = await env.DB.prepare(
      "SELECT id, health_status FROM social_accounts WHERE id = ?"
    ).bind(body.social_account_id).first();
  } else if (body.session_id) {
    account = await env.DB.prepare(
      "SELECT id, health_status FROM social_accounts WHERE surf_profile_id = ?"
    ).bind(body.session_id).first();
  }
  if (!account) return err(404, "account not found for session/account id");

  const status = body.status;
  const allowed = ["healthy", "captcha_pending", "stale", "locked", "failed"];
  if (!allowed.includes(status)) return err(400, `status must be one of ${allowed.join(",")}`);

  // Stateful write: only insert heartbeat row if status CHANGED vs last record
  const lastRow = await env.DB.prepare(
    "SELECT status FROM session_heartbeats WHERE social_account_id = ? ORDER BY checked_at DESC LIMIT 1"
  ).bind(account.id).first();
  const statusChanged = !lastRow || lastRow.status !== status;

  if (statusChanged) {
    await env.DB.prepare(
      `INSERT INTO session_heartbeats (id, social_account_id, status, cookie_age_seconds,
        captcha_detected, ban_detected, http_status, response_time_ms, error_message)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      crypto.randomUUID(),
      account.id,
      status,
      body.cookie_age_seconds ?? null,
      body.captcha_detected ? 1 : 0,
      body.ban_detected ? 1 : 0,
      body.http_status ?? null,
      body.response_time_ms ?? null,
      (body.error_message || "").slice(0, 500) || null
    ).run();
  }

  // Always update social_accounts.health_status + last_verified_at
  await env.DB.prepare(
    "UPDATE social_accounts SET health_status = ?, last_verified_at = ? WHERE id = ?"
  ).bind(status, nowIso(), account.id).run();

  return json({
    status: "recorded",
    status_changed: statusChanged,
    account_id: account.id,
    new_status: status
  });
}

async function handleSurfHealth(request, env, accountId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // User can only see their own accounts
  const account = await env.DB.prepare(
    "SELECT id, platform, account_handle, health_status, last_verified_at, surf_profile_id FROM social_accounts WHERE id = ? AND user_id = ?"
  ).bind(accountId, sess.user_id).first();
  if (!account) return err(404, "account not found or not yours");

  // Latest heartbeat detail
  const latest = await env.DB.prepare(
    `SELECT checked_at, status, cookie_age_seconds, captcha_detected, ban_detected,
            http_status, response_time_ms, error_message
     FROM session_heartbeats WHERE social_account_id = ?
     ORDER BY checked_at DESC LIMIT 1`
  ).bind(account.id).first();

  // Last 10 heartbeats (status transitions, because stateful writes)
  const history = await env.DB.prepare(
    `SELECT checked_at, status, cookie_age_seconds
     FROM session_heartbeats WHERE social_account_id = ?
     ORDER BY checked_at DESC LIMIT 10`
  ).bind(account.id).all();

  return json({
    account,
    latest_heartbeat: latest || null,
    status_transitions: history.results || []
  });
}

async function handlePollResults(request, env, partnerId) {
  const { partner, error } = await resolvePollPartner(request, env, partnerId);
  if (error) return error;

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const { job_id, status, result, error_message } = body;
  if (!job_id) return err(400, "job_id required");
  if (!["completed", "failed"].includes(status)) return err(400, "status must be 'completed' or 'failed'");

  // Verify job belongs to this partner and is claimed
  const job = await env.DB.prepare(
    "SELECT id, status, ai_partner_id, user_id, job_type, attempts, max_attempts FROM partner_jobs WHERE id = ?"
  ).bind(job_id).first();
  if (!job) return err(404, "job not found");
  if (job.ai_partner_id !== partner.id) return err(403, "job belongs to a different partner");
  if (job.status === "completed") return err(409, "job already completed");

  if (status === "completed") {
    await env.DB.prepare(
      `UPDATE partner_jobs SET status = 'completed', completed_at = ?, result = ? WHERE id = ?`
    ).bind(nowIso(), JSON.stringify(result || {}), job_id).run();

    // Side effect: if job_type is generate_week, turn drafts into content_items
    if (job.job_type === "generate_week" && result && Array.isArray(result.drafts)) {
      for (const d of result.drafts) {
        if (!d.platform || !d.body) continue;
        // Find matching social_account for this user + platform
        const acct = await env.DB.prepare(
          "SELECT id FROM social_accounts WHERE user_id = ? AND platform = ? ORDER BY created_at ASC LIMIT 1"
        ).bind(job.user_id, d.platform).first();
        if (!acct) continue;
        await env.DB.prepare(
          `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, generated_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?)`
        ).bind(
          crypto.randomUUID(), job.user_id, acct.id, d.platform,
          d.scheduled_at || null, d.body,
          JSON.stringify(d.media_refs || []),
          `ai_partner:${partner.partner_name}`,
          nowIso(), nowIso()
        ).run();
      }
    }
    return json({ status: "recorded" });
  } else {
    // failed — check if retryable
    const willRetry = job.attempts < job.max_attempts;
    await env.DB.prepare(
      `UPDATE partner_jobs SET status = ?, error_message = ?, claimed_at = NULL, expires_at = NULL WHERE id = ?`
    ).bind(
      willRetry ? "pending" : "failed",
      (error_message || "").slice(0, 500),
      job_id
    ).run();
    return json({ status: willRetry ? "requeued" : "failed", attempts: job.attempts, max_attempts: job.max_attempts });
  }
}

// ---------- Password change ----------
async function handleChangePassword(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const { current_password, new_password } = body;
  if (!current_password || !new_password) return err(400, "current_password and new_password required");
  if (new_password.length < 12) return err(400, "new_password must be at least 12 characters");

  const user = await env.DB.prepare(
    "SELECT password_hash FROM users WHERE id = ?"
  ).bind(sess.user_id).first();
  if (!user || !user.password_hash) return err(404, "user not found");
  if (!(await verifyPassword(current_password, user.password_hash))) {
    return err(401, "current password incorrect");
  }

  const newHash = await hashPassword(new_password);
  await env.DB.prepare(
    "UPDATE users SET password_hash = ? WHERE id = ?"
  ).bind(newHash, sess.user_id).run();

  // Invalidate all other sessions for this user (keep current)
  const currentToken = request.headers.get("authorization")?.replace("Bearer ", "")
    || (request.headers.get("cookie") || "").match(/social_session=([^;]+)/)?.[1];
  if (currentToken) {
    await env.DB.prepare(
      "DELETE FROM sessions WHERE user_id = ? AND token != ?"
    ).bind(sess.user_id, currentToken).run();
  }

  return json({ status: "password_changed" });
}

// ---------- Voice profile ----------
async function handleUpdateVoiceProfile(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const { partner_name, voice_profile } = body;
  if (!partner_name || !voice_profile) return err(400, "partner_name and voice_profile required");

  const result = await env.DB.prepare(
    "UPDATE ai_partners SET voice_profile = ? WHERE user_id = ? AND partner_name = ?"
  ).bind(JSON.stringify(voice_profile), sess.user_id, partner_name).run();

  if (result.meta.changes === 0) {
    return err(404, "partner not registered for this user");
  }

  const partner = await env.DB.prepare(
    "SELECT id, partner_name, partner_endpoint, voice_profile FROM ai_partners WHERE user_id = ? AND partner_name = ?"
  ).bind(sess.user_id, partner_name).first();
  return json({ partner });
}

// ---------- Trios (multi-tenant) ----------
const TRIO_COLORS = ['#2a93c1','#f1420b','#22c55e','#a770ef','#0ca4b8','#e11d48','#f59e0b','#0a0a0a'];

async function handleListTrios(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  // List trios the user is a member of OR owns
  const { results } = await env.DB.prepare(
    `SELECT DISTINCT t.* FROM trios t
     LEFT JOIN trio_members tm ON tm.trio_id = t.id
     WHERE t.owner_user_id = ? OR tm.member_user_id = ?
     ORDER BY t.created_at DESC`
  ).bind(sess.user_id, sess.user_id).all();
  return json({ trios: results || [] });
}

async function handleCreateTrio(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const name = (body.name || '').trim();
  if (!name) return err(400, "name required");

  const id = newId();
  await env.DB.prepare(
    "INSERT INTO trios (id, owner_user_id, name, description, visibility) VALUES (?, ?, ?, ?, ?)"
  ).bind(id, sess.user_id, name, body.description || null, body.visibility || 'private').run();

  // Owner auto-added as human member
  const ownerMemberId = newId();
  await env.DB.prepare(
    `INSERT INTO trio_members (id, trio_id, member_type, member_user_id, display_name, color, role)
     VALUES (?, ?, 'human', ?, ?, ?, 'owner')`
  ).bind(ownerMemberId, id, sess.user_id, sess.name, '#ffffff').run();

  // If initial members specified, add them
  if (body.ai_partner_ids && Array.isArray(body.ai_partner_ids)) {
    for (let i = 0; i < body.ai_partner_ids.length; i++) {
      const pid = body.ai_partner_ids[i];
      const partner = await env.DB.prepare(
        "SELECT id, partner_name FROM ai_partners WHERE id = ? AND user_id = ?"
      ).bind(pid, sess.user_id).first();
      if (!partner) continue;
      await env.DB.prepare(
        `INSERT INTO trio_members (id, trio_id, member_type, member_partner_id, display_name, color, role)
         VALUES (?, ?, 'ai_partner', ?, ?, ?, 'member')`
      ).bind(newId(), id, partner.id, partner.partner_name, TRIO_COLORS[i % TRIO_COLORS.length], 'member').run();
    }
  }

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(id).first();
  return json({ trio }, { status: 201 });
}

async function handleGetTrioConfig(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");

  // Access check: owner OR member
  const access = await env.DB.prepare(
    "SELECT 1 FROM trio_members WHERE trio_id = ? AND member_user_id = ?"
  ).bind(trioId, sess.user_id).first();
  if (trio.owner_user_id !== sess.user_id && !access) return err(403, "forbidden");

  const { results: members } = await env.DB.prepare(
    `SELECT tm.*, ap.partner_endpoint FROM trio_members tm
     LEFT JOIN ai_partners ap ON tm.member_partner_id = ap.id
     WHERE tm.trio_id = ?
     ORDER BY tm.added_at ASC`
  ).bind(trioId).all();

  return json({ trio, members: members || [] });
}

async function handleAddTrioMember(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  if (trio.owner_user_id !== sess.user_id) return err(403, "only owner can add members");

  const memberType = body.member_type || 'ai_partner';
  if (!['human', 'ai_partner'].includes(memberType)) return err(400, "invalid member_type");

  if (memberType === 'ai_partner') {
    if (!body.partner_id) return err(400, "partner_id required");
    const partner = await env.DB.prepare(
      "SELECT id, partner_name FROM ai_partners WHERE id = ? AND user_id = ?"
    ).bind(body.partner_id, sess.user_id).first();
    if (!partner) return err(404, "partner not found or not owned");

    const countRow = await env.DB.prepare(
      "SELECT COUNT(*) AS c FROM trio_members WHERE trio_id = ? AND member_type = 'ai_partner'"
    ).bind(trioId).first();
    const color = TRIO_COLORS[((countRow && countRow.c) || 0) % TRIO_COLORS.length];

    const id = newId();
    try {
      await env.DB.prepare(
        `INSERT INTO trio_members (id, trio_id, member_type, member_partner_id, display_name, color)
         VALUES (?, ?, 'ai_partner', ?, ?, ?)`
      ).bind(id, trioId, partner.id, body.display_name || partner.partner_name, color).run();
    } catch (e) {
      if (String(e.message || e).includes("UNIQUE")) return err(409, "partner already in trio");
      throw e;
    }
    const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ?").bind(id).first();
    return json({ member }, { status: 201 });
  } else {
    if (!body.email) return err(400, "email required for human member");
    const user = await env.DB.prepare(
      "SELECT id, name FROM users WHERE email = ?"
    ).bind(body.email.toLowerCase()).first();
    if (!user) return err(404, "user not found");

    const countRow = await env.DB.prepare(
      "SELECT COUNT(*) AS c FROM trio_members WHERE trio_id = ? AND member_type = 'human'"
    ).bind(trioId).first();
    const color = '#ffffff';

    const id = newId();
    try {
      await env.DB.prepare(
        `INSERT INTO trio_members (id, trio_id, member_type, member_user_id, display_name, color)
         VALUES (?, ?, 'human', ?, ?, ?)`
      ).bind(id, trioId, user.id, body.display_name || user.name, color).run();
    } catch (e) {
      if (String(e.message || e).includes("UNIQUE")) return err(409, "user already in trio");
      throw e;
    }
    const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ?").bind(id).first();
    return json({ member }, { status: 201 });
  }
}

async function handleGetTrioMessages(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Access check
  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  const access = await env.DB.prepare(
    "SELECT 1 FROM trio_members WHERE trio_id = ? AND member_user_id = ?"
  ).bind(trioId, sess.user_id).first();
  if (trio.owner_user_id !== sess.user_id && !access) return err(403, "forbidden");

  // Proxy to trio-comms worker with trio_id param
  if (!env.TRIO_COMMS_TOKEN) return err(503, "trio-comms not configured");

  try {
    const url = `https://trio-comms.in0v8.workers.dev/trio/messages?trio_id=${encodeURIComponent(trioId)}&limit=200`;
    const resp = await fetch(url, {
      headers: { "Authorization": `Bearer ${env.TRIO_COMMS_TOKEN}` }
    });
    const data = await resp.json();
    return json(data, { status: resp.status });
  } catch (e) {
    return err(502, "trio-comms unreachable: " + String(e.message || e).slice(0, 120));
  }
}

async function handleSendTrioMessage(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Access check
  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  const access = await env.DB.prepare(
    "SELECT 1 FROM trio_members WHERE trio_id = ? AND member_user_id = ?"
  ).bind(trioId, sess.user_id).first();
  if (trio.owner_user_id !== sess.user_id && !access) return err(403, "forbidden");

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const content = (body.content || '').trim();
  if (!content) return err(400, "content required");
  if (content.length > 10000) return err(413, "content too long (max 10000 chars)");

  if (!env.TRIO_COMMS_TOKEN) return err(503, "trio-comms not configured");

  try {
    const resp = await fetch("https://trio-comms.in0v8.workers.dev/trio/message", {
      method: "POST",
      headers: { "Authorization": `Bearer ${env.TRIO_COMMS_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ content, trio_id: trioId })
    });
    const data = await resp.json();
    return json(data, { status: resp.status });
  } catch (e) {
    return err(502, "trio-comms unreachable: " + String(e.message || e).slice(0, 120));
  }
}

async function handleUpdateTrioMember(request, env, trioId, memberId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  if (trio.owner_user_id !== sess.user_id) return err(403, "only owner can update members");

  const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ? AND trio_id = ?").bind(memberId, trioId).first();
  if (!member) return err(404, "member not found");

  const allowed = ["display_name", "color", "role"];
  const updates = {};
  for (const k of allowed) if (k in body) updates[k] = body[k];
  if (Object.keys(updates).length === 0) return err(400, "no valid fields");

  // Color format validation (#RRGGBB or #RRGGBBAA or #RGB)
  if (updates.color && !/^#[0-9A-Fa-f]{3,8}$/.test(updates.color)) {
    return err(400, "color must be hex like #f1420b");
  }

  // Role change: only owner can promote/demote, can't demote self from owner
  if (updates.role && member.role === 'owner' && updates.role !== 'owner') {
    return err(400, "cannot demote owner role");
  }

  const setClauses = Object.keys(updates).map(k => `${k} = ?`);
  const args = [...Object.values(updates), memberId];
  await env.DB.prepare(`UPDATE trio_members SET ${setClauses.join(", ")} WHERE id = ?`).bind(...args).run();

  const updated = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ?").bind(memberId).first();
  return json({ member: updated });
}

async function handleRemoveTrioMember(request, env, trioId, memberId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  if (trio.owner_user_id !== sess.user_id) return err(403, "only owner can remove members");

  const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ? AND trio_id = ?").bind(memberId, trioId).first();
  if (!member) return err(404, "member not found");
  if (member.role === 'owner') return err(400, "cannot remove owner");

  await env.DB.prepare("DELETE FROM trio_members WHERE id = ?").bind(memberId).run();
  return json({ status: "removed" });
}

// ---------- R2 uploads ----------
const UPLOAD_MAX_SIZE = 10 * 1024 * 1024; // 10MB
const UPLOAD_ALLOWED_MIMES = /^(image\/(jpeg|png|gif|webp|svg\+xml)|video\/(mp4|webm)|application\/pdf)$/;
const R2_PUBLIC_DOMAIN = "pub-8f8cf3b34e354e108283ed11c59db125.r2.dev";

async function handleUpload(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  if (!env.UPLOADS) return err(503, "R2 storage not bound");

  const contentLength = parseInt(request.headers.get("content-length") || "0");
  if (contentLength > UPLOAD_MAX_SIZE) return err(413, "file too large (max 10MB)");

  let formData;
  try { formData = await request.formData(); }
  catch { return err(400, "multipart form data required"); }

  const file = formData.get("file");
  if (!file || typeof file === "string") return err(400, "'file' field required");

  const mime = file.type || "application/octet-stream";
  if (!UPLOAD_ALLOWED_MIMES.test(mime)) {
    return err(415, "unsupported file type: " + mime);
  }

  const size = file.size;
  if (size > UPLOAD_MAX_SIZE) return err(413, "file too large (max 10MB)");

  const origName = (file.name || "upload").replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 100);
  const timestamp = Date.now();
  const rand = crypto.randomUUID().slice(0, 8);
  const key = `${sess.user_id}/${timestamp}-${rand}-${origName}`;

  try {
    const arrayBuffer = await file.arrayBuffer();
    await env.UPLOADS.put(key, arrayBuffer, {
      httpMetadata: { contentType: mime },
      customMetadata: { uploaded_by: sess.user_id, original_name: origName }
    });
  } catch (e) {
    return err(500, "upload failed: " + String(e.message || e).slice(0, 200));
  }

  const publicUrl = `https://${R2_PUBLIC_DOMAIN}/${encodeURI(key)}`;

  return json({
    key,
    url: publicUrl,
    mime,
    size,
    original_name: origName,
    uploaded_at: nowIso()
  }, { status: 201 });
}

// ---------- MEETING ASSIGNMENTS (shared D1 state for meeting scheduler) ----------

async function handleGetMeetingAssignments(request, env) {
  // Public GET — no auth needed (view mode)
  const { results: assignments } = await env.DB.prepare(
    "SELECT * FROM meeting_assignments"
  ).all();
  const { results: custom } = await env.DB.prepare(
    "SELECT * FROM custom_meetings ORDER BY created_at"
  ).all();
  return json({ assignments: assignments || [], custom_meetings: custom || [] });
}

async function handleSaveMeetingAssignments(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const assignments = body.assignments || [];
  const now = nowIso();

  // Upsert each meeting assignment
  for (const a of assignments) {
    if (!a.meeting_id) continue;
    await env.DB.prepare(
      `INSERT INTO meeting_assignments (meeting_id, required_ids, optional_ids, zoom_link, zoom_meeting_id, updated_by, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(meeting_id) DO UPDATE SET
         required_ids = excluded.required_ids,
         optional_ids = excluded.optional_ids,
         zoom_link = COALESCE(excluded.zoom_link, meeting_assignments.zoom_link),
         zoom_meeting_id = COALESCE(excluded.zoom_meeting_id, meeting_assignments.zoom_meeting_id),
         updated_by = excluded.updated_by,
         updated_at = excluded.updated_at`
    ).bind(
      a.meeting_id,
      JSON.stringify(a.required || []),
      JSON.stringify(a.optional || []),
      a.zoom_link || null,
      a.zoom_meeting_id || null,
      sess.user_id,
      now
    ).run();
  }

  // Handle custom meetings if provided
  const customMeetings = body.custom_meetings || [];
  for (const cm of customMeetings) {
    if (!cm.id || !cm.name) continue;
    await env.DB.prepare(
      `INSERT INTO custom_meetings (id, name, full_name, color, schedule, duration, led_by, hook, description, domain, format, facilitator, created_by, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
         name = excluded.name, full_name = excluded.full_name, color = excluded.color,
         schedule = excluded.schedule, duration = excluded.duration, led_by = excluded.led_by,
         hook = excluded.hook, description = excluded.description, domain = excluded.domain,
         format = excluded.format, facilitator = excluded.facilitator, updated_at = excluded.updated_at`
    ).bind(
      cm.id, cm.name, cm.full_name || cm.name, cm.color || '#3b82f6',
      cm.schedule || '', cm.duration || '', cm.led_by || '',
      cm.hook || '', cm.description || '', cm.domain || 'Custom',
      JSON.stringify(cm.format || []), cm.facilitator || '',
      sess.user_id, now
    ).run();
  }

  return json({ saved: assignments.length, custom_saved: customMeetings.length });
}

// ---------- ANALYTICS ENDPOINTS (Morphe Phase 2) ----------

async function handleGetAnalyticsSummary(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const userId = sess.user_id;
  const now = new Date();
  const weekAgo = new Date(now - 7*24*60*60*1000).toISOString();
  const monthAgo = new Date(now - 30*24*60*60*1000).toISOString();

  const [total, week, month, pending, scheduled, byPlatform, byType] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=?").bind(userId).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=? AND posted_at>=?").bind(userId, weekAgo).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=? AND posted_at>=?").bind(userId, monthAgo).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=? AND status IN ('draft','pending_approval')").bind(userId).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=? AND status='scheduled'").bind(userId).first(),
    env.DB.prepare("SELECT platform, status, COUNT(*) as c FROM content_items WHERE user_id=? GROUP BY platform, status").bind(userId).all(),
    env.DB.prepare("SELECT content_type, status, COUNT(*) as c FROM content_items WHERE user_id=? GROUP BY content_type, status").bind(userId).all(),
  ]);

  const platforms = {};
  for (const r of (byPlatform.results||[])) {
    if (!platforms[r.platform]) platforms[r.platform] = {total:0,posted:0,pending:0,scheduled:0};
    platforms[r.platform].total += r.c;
    if (r.status==='posted') platforms[r.platform].posted += r.c;
    if (r.status==='draft'||r.status==='pending_approval') platforms[r.platform].pending += r.c;
    if (r.status==='scheduled') platforms[r.platform].scheduled += r.c;
  }
  const types = {};
  for (const r of (byType.results||[])) {
    if (!types[r.content_type]) types[r.content_type] = {total:0,posted:0};
    types[r.content_type].total += r.c;
    if (r.status==='posted') types[r.content_type].posted += r.c;
  }

  return json({
    total_posts: total?.c||0, posted_this_week: week?.c||0, posted_this_month: month?.c||0,
    pending_review: pending?.c||0, scheduled: scheduled?.c||0,
    by_platform: platforms, by_content_type: types
  });
}

async function handleGetQueueStatus(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const userId = sess.user_id;
  const now = nowIso();
  const [pending, scheduled, nextPost] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=? AND status IN ('draft','pending_approval')").bind(userId).first(),
    env.DB.prepare("SELECT COUNT(*) as c FROM content_items WHERE user_id=? AND status='scheduled'").bind(userId).first(),
    env.DB.prepare("SELECT id, platform, scheduled_at FROM content_items WHERE user_id=? AND status='scheduled' AND scheduled_at>? ORDER BY scheduled_at ASC LIMIT 1").bind(userId, now).first(),
  ]);
  return json({
    queue_depth: {pending_review: pending?.c||0, scheduled: scheduled?.c||0},
    next_scheduled: nextPost || null
  });
}

async function handleReadyFeed(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  // Relaxed: any authenticated user can poll (ContentRouter uses Jared's login)

  const now = nowIso();
  const { results } = await env.DB.prepare(
    `SELECT ci.*, sa.account_handle, sa.auth_type, sa.surf_profile_id,
            sa.credentials_encrypted, sa.session_token_encrypted
     FROM content_items ci JOIN social_accounts sa ON ci.social_account_id = sa.id
     WHERE ci.status = 'scheduled' AND ci.scheduled_at <= ?
     ORDER BY ci.scheduled_at ASC LIMIT 50`
  ).bind(now).all();

  const ready = [];
  for (const r of results || []) {
    try {
      if (r.credentials_encrypted) r.credentials_plain = await decryptSecret(r.credentials_encrypted, env);
      if (r.session_token_encrypted) r.session_token_plain = await decryptSecret(r.session_token_encrypted, env);
    } catch (e) {
      r.decryption_error = String(e.message || e).slice(0, 200);
    }
    delete r.credentials_encrypted;
    delete r.session_token_encrypted;
    ready.push(r);
  }
  return json({ ready });
}

// ========== Phase 2: Meeting Form Responses ==========

async function handleSubmitFormResponse(request, env) {
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const meeting_id = body.meeting_id;
  const name = body.name || body.respondent_name;
  const email = body.email || body.respondent_email;
  const responses = body.responses;
  const respondent_type = body.respondent_type;
  if (!meeting_id || !name || !responses) return err(400, "meeting_id, name, and responses required");
  const id = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT INTO meeting_form_responses (id, meeting_id, respondent_name, respondent_email, respondent_type, responses) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(id, meeting_id, name, email || null, respondent_type || "human", JSON.stringify(responses)).run();
  return json({ id, status: "submitted" }, 201);
}

async function handleGetFormResponses(request, env) {
  const url = new URL(request.url);
  const meetingId = url.pathname.split("/").pop();
  const { results } = await env.DB.prepare(
    "SELECT * FROM meeting_form_responses WHERE meeting_id = ? ORDER BY submitted_at DESC"
  ).bind(meetingId).all();
  const parsed = (results || []).map(r => ({
    ...r,
    responses: (() => { try { return JSON.parse(r.responses); } catch { return r.responses; } })()
  }));
  return json({ responses: parsed, count: parsed.length });
}

// ========== Phase 2: Blocker Reporting (team.purebrain.ai) ==========

async function handleReportBlocker(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const { description, blocker_type, blocked_by, owner } = body;
  if (!description || !blocker_type) return err(400, "description and blocker_type required");
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  await env.DB.prepare(
    "INSERT INTO blocker_items (id, description, blocker_type, reporter, blocked_by, owner, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(id, description, blocker_type, sess.user_id || body.reporter || "unknown", blocked_by || null, owner || null, now).run();
  return json({ id, status: "open", created_at: now }, 201);
}

async function handleGetBlockers(request, env) {
  const url = new URL(request.url);
  const status = url.searchParams.get("status") || "open";
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "50"), 200);
  let query, binds;
  if (status === "all") {
    query = "SELECT * FROM blocker_items ORDER BY created_at DESC LIMIT ?";
    binds = [limit];
  } else {
    query = "SELECT * FROM blocker_items WHERE status = ? ORDER BY created_at DESC LIMIT ?";
    binds = [status, limit];
  }
  const { results } = await env.DB.prepare(query).bind(...binds).all();
  return json({ blockers: results, count: results.length });
}

async function handleResolveBlocker(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const url = new URL(request.url);
  const id = url.pathname.split("/").pop();
  let body = {};
  try { body = await request.json(); } catch {}
  const now = new Date().toISOString();
  await env.DB.prepare(
    "UPDATE blocker_items SET status = 'resolved', resolved_at = ?, resolution_note = ? WHERE id = ?"
  ).bind(now, body.note || null, id).run();
  return json({ ok: true, resolved_at: now });
}

// ---------- Phase 2: Smart Time-to-Post ----------
async function handleBestTimes(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Query posted content for this user's team to find engagement patterns
  const { results: postedItems } = await env.DB.prepare(
    `SELECT platform, posted_at, performance_metrics
     FROM content_items
     WHERE user_id = ? AND status = 'posted' AND posted_at IS NOT NULL
     ORDER BY posted_at DESC LIMIT 500`
  ).bind(sess.user_id).all();

  if (!postedItems || postedItems.length === 0) {
    return json({ suggestions: [], message: "No posted content yet. Post more to get time suggestions." });
  }

  // Group by platform -> hour_of_day + day_of_week
  const slots = {}; // key: "platform|dow|hour" -> { count, totalEngagement }
  for (const item of postedItems) {
    const dt = new Date(item.posted_at);
    const dow = dt.getUTCDay(); // 0=Sun..6=Sat
    const hour = dt.getUTCHours();
    const platform = item.platform || "unknown";

    const key = `${platform}|${dow}|${hour}`;
    if (!slots[key]) slots[key] = { platform, day_of_week: dow, hour_of_day: hour, count: 0, totalEngagement: 0, hasMetrics: false };
    slots[key].count++;

    if (item.performance_metrics) {
      try {
        const metrics = typeof item.performance_metrics === "string" ? JSON.parse(item.performance_metrics) : item.performance_metrics;
        if (typeof metrics.engagement === "number") {
          slots[key].totalEngagement += metrics.engagement;
          slots[key].hasMetrics = true;
        }
      } catch {}
    }
  }

  // Calculate score: if metrics exist use avg engagement, otherwise use post count as proxy
  const slotList = Object.values(slots).map(s => ({
    platform: s.platform,
    day_of_week: s.day_of_week,
    day_name: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][s.day_of_week],
    hour_of_day: s.hour_of_day,
    hour_label: `${String(s.hour_of_day).padStart(2, "0")}:00 UTC`,
    post_count: s.count,
    avg_engagement: s.hasMetrics ? Math.round((s.totalEngagement / s.count) * 100) / 100 : null,
    score: s.hasMetrics ? s.totalEngagement / s.count : s.count
  }));

  // Group by platform and pick top 5 per platform
  const byPlatform = {};
  for (const s of slotList) {
    if (!byPlatform[s.platform]) byPlatform[s.platform] = [];
    byPlatform[s.platform].push(s);
  }

  const suggestions = {};
  for (const [platform, items] of Object.entries(byPlatform)) {
    suggestions[platform] = items.sort((a, b) => b.score - a.score).slice(0, 5);
  }

  return json({
    suggestions,
    total_posts_analyzed: postedItems.length,
    scoring_method: slotList.some(s => s.avg_engagement !== null) ? "engagement_weighted" : "post_count_proxy"
  });
}

// ---------- Phase 2: Bulk CSV Upload ----------
async function handleBulkUpload(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Permission check: viewer and reviewer cannot create content
  if (["viewer", "reviewer"].includes(sess.role)) {
    return err(403, "your role does not allow creating content");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const items = body.items || body;
  if (!Array.isArray(items)) return err(400, "expected JSON array of posts (or {items: [...]})");
  if (items.length === 0) return err(400, "empty array");
  if (items.length > 200) return err(400, "maximum 200 items per bulk upload");

  const now = nowIso();
  const ids = [];
  const errors = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (!item.platform || !item.body) {
      errors.push({ index: i, error: "platform and body are required" });
      continue;
    }

    const id = newId();
    try {
      await env.DB.prepare(
        `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, content_type, generated_by, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(
        id, sess.user_id, item.social_account_id || null, item.platform,
        "draft", item.scheduled_at || null, item.body,
        JSON.stringify(item.media_refs || []), item.content_type || "post", "bulk_import",
        now, now
      ).run();
      ids.push(id);
    } catch (e) {
      errors.push({ index: i, error: (e.message || String(e)).slice(0, 200) });
    }
  }

  return json({
    inserted: ids.length,
    failed: errors.length,
    ids,
    errors: errors.length > 0 ? errors : undefined
  }, { status: 201 });
}

// ---------- Phase 2: Team Roles & Permissions (handleChangeRole) ----------

async function handleChangeRole(request, env, targetUserId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Only admin/owner/leader can change roles
  if (!hasPermission(sess.role, "manage_roles")) {
    return err(403, "only admin/owner/leader can change roles");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const newRole = (body.role || "").trim().toLowerCase();
  const validRoles = ["admin", "editor", "reviewer", "viewer", "member", "leader"];
  if (!validRoles.includes(newRole)) {
    return err(400, `role must be one of: ${validRoles.join(", ")}`);
  }

  // Cannot change own role
  if (targetUserId === sess.user_id) {
    return err(400, "cannot change your own role");
  }

  // Target must be on same team
  const target = await env.DB.prepare(
    "SELECT id, email, name, role, team_id FROM users WHERE id = ?"
  ).bind(targetUserId).first();

  if (!target) return err(404, "user not found");
  if (target.team_id !== sess.team_id) return err(403, "user is not on your team");

  // Cannot change owner role
  if (target.role === "owner") {
    return err(400, "cannot change owner role");
  }

  // Cannot assign owner role
  if (newRole === "owner") {
    return err(400, "cannot assign owner role via this endpoint");
  }

  await env.DB.prepare(
    "UPDATE users SET role = ? WHERE id = ?"
  ).bind(newRole, targetUserId).run();

  const updated = await env.DB.prepare(
    "SELECT id, email, name, role, team_id FROM users WHERE id = ?"
  ).bind(targetUserId).first();

  return json({ user: updated, message: `Role changed to ${newRole}` });
}

// ---------- Phase 2: Media Proxy (R2 images via /media/*) ----------
async function handleMediaProxy(request, env) {
  const url = new URL(request.url);
  const key = decodeURIComponent(url.pathname.slice("/media/".length));
  if (!key) return err(400, "missing key");
  if (!env.UPLOADS) return err(503, "R2 storage not bound");
  const obj = await env.UPLOADS.get(key);
  if (!obj) return new Response("not found", { status: 404 });
  const headers = new Headers();
  headers.set("Content-Type", obj.httpMetadata?.contentType || "application/octet-stream");
  headers.set("Cache-Control", "public, max-age=31536000, immutable");
  headers.set("Access-Control-Allow-Origin", "*");
  return new Response(obj.body, { status: 200, headers });
}

// ---------- Phase 2: Delete Content ----------
async function handleDeleteContent(request, env, itemId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const existing = await env.DB.prepare("SELECT user_id FROM content_items WHERE id = ?").bind(itemId).first();
  if (!existing) return err(404, "not found");
  if (existing.user_id !== sess.user_id && sess.role !== "leader" && sess.role !== "system" && sess.role !== "admin" && sess.role !== "owner") {
    return err(403, "forbidden");
  }
  await env.DB.prepare("DELETE FROM content_items WHERE id = ?").bind(itemId).run();
  return json({ ok: true, deleted: itemId });
}

// ---------- CORS ----------
function corsHeaders(origin) {
  const allowed = [
    "https://purebrain.ai",
    "https://social.purebrain.ai",
    "https://chy-jared.app.purebrain.ai",
    "https://portal.purebrain.ai",
    "https://777.purebrain.ai"
  ];
  const allowOrigin = allowed.includes(origin) ? origin : allowed[0];
  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "GET, POST, PATCH, DELETE, OPTIONS",
    "access-control-allow-headers": "authorization, content-type",
    "vary": "origin",
  };
}

// ---------- Sunday batch generation (cron) ----------
// ---------- DAILY MEETING FORM EMAILS (cron: 0 12 * * * = 7am ET) ----------

const MEETING_SCHEDULE = {
  "tech-daily": {name:"Technical Daily",days:["mon","tue","wed","thu"],time:"07:00"},
  "pipeline-review": {name:"Pipeline Review",days:["mon","tue","wed","thu"],time:"13:00"},
  "weekly-tactical": {name:"Weekly Tactical All-Hands",days:["fri"],time:"09:00"},
  "leadership": {name:"Leadership Meeting",days:["mon"],time:"11:00"},
  "governance": {name:"Corporate Governance",days:["wed"],time:"08:30"},
  "monthly-strategic": {name:"Monthly Strategic",days:["mon"],time:"13:00",monthlyFirst:true},
  "product-customer": {name:"Product / Customer",days:["tue"],time:"09:00",biweekly:true},
};

const TEAM_EMAIL_MAP = {
  jared:"jared@puretechnology.nyc",melanie:"melanie@puretechnology.nyc",nils:"NWaschkau@puretechnology.nyc",
  metis:"mthancock@gmail.com",rimah:"rimah@puretechnology.nyc",schuman:"mike@puretechnology.nyc",
  logie:"alex@puretechnology.nyc",nathan:"nathan@puremarketing.ai",johnsmith:"JSmith@puretechnology.nyc",
  phil:"philip@puretechnology.nyc",orlowski:"robert.orlowski@puretechnology.nyc",ashley:"support@puremarketing.ai",
  moises:"mo@puremarketing.ai",roger:"roger.beaini@puretechnology.nyc",mireille:"mireille@puretechnology.nyc",
  baruch:"baruch@puremarketing.ai",natasha:"support@puremarketing.ai",brennan:"edward@puretechnology.nyc",
  ahsen:"ahsen@puretechnology.nyc",alex:"alex.seant@puretechnology.nyc",waqas:"waqas@puretechnology.nyc",
  shahbaz:"shahbaz@puretechnology.nyc",zafeer:"zafeer@puretechnology.nyc",corey:"coreycmusic@gmail.com",
  russell:"russell@puretechnology.nyc",faris:"fasmar@cynoratech.com",mikedaser:"MDaser@puretechnology.nyc",
  aether:"aethergottaeat@agentmail.to",chy:"chy@agentmail.to",
};

async function sendDailyMeetingForms(env) {
  console.log("[meeting-forms-cron] starting daily check");

  // Determine tomorrow's day of week
  const tomorrow = new Date(Date.now() + 86400000);
  const dayNames = ["sun","mon","tue","wed","thu","fri","sat"];
  const tomorrowDay = dayNames[tomorrow.getUTCDay()];
  // Adjust for ET (UTC-4 in EDT)
  const etOffset = -4;
  const etTomorrow = new Date(Date.now() + 86400000 + etOffset * 3600000);
  const etDay = dayNames[etTomorrow.getDay()];
  const dateStr = etTomorrow.toLocaleDateString("en-US", {weekday:"long",month:"long",day:"numeric",year:"numeric"});

  // Find tomorrow's meetings
  const tomorrowMeetings = [];
  for (const [id, m] of Object.entries(MEETING_SCHEDULE)) {
    if (!m.days.includes(etDay)) continue;
    if (m.monthlyFirst) {
      // Only first occurrence of that day in the month
      if (etTomorrow.getDate() > 7) continue;
    }
    if (m.biweekly) {
      // Even ISO weeks only
      const jan1 = new Date(etTomorrow.getFullYear(), 0, 1);
      const weekNum = Math.ceil(((etTomorrow - jan1) / 86400000 + jan1.getDay() + 1) / 7);
      if (weekNum % 2 !== 0) continue;
    }
    tomorrowMeetings.push({id, ...m});
  }

  if (!tomorrowMeetings.length) {
    console.log("[meeting-forms-cron] no meetings tomorrow (" + etDay + ")");
    return {sent: 0};
  }

  console.log("[meeting-forms-cron] " + tomorrowMeetings.length + " meetings tomorrow");

  // Pull attendees from D1
  const { results: assignments } = await env.DB.prepare(
    "SELECT meeting_id, required_ids, optional_ids FROM meeting_assignments"
  ).all();
  const assignmentMap = {};
  for (const a of (assignments || [])) {
    let req = a.required_ids || "[]";
    if (typeof req === "string") req = JSON.parse(req);
    assignmentMap[a.meeting_id] = req;
  }

  // Send form emails via Microsoft Graph (using env secrets)
  const msClientId = env.MS_CLIENT_ID;
  const msClientSecret = env.MS_CLIENT_SECRET;
  const msTenantId = env.MS_TENANT_ID;

  if (!msClientId || !msClientSecret || !msTenantId) {
    console.log("[meeting-forms-cron] Microsoft Graph creds not configured in env");
    return {sent: 0, error: "MS Graph creds missing"};
  }

  // Get Graph token
  const tokenResp = await fetch("https://login.microsoftonline.com/" + msTenantId + "/oauth2/v2.0/token", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "grant_type=client_credentials&client_id=" + msClientId + "&client_secret=" + encodeURIComponent(msClientSecret) + "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default"
  });
  const tokenData = await tokenResp.json();
  const graphToken = tokenData.access_token;
  if (!graphToken) {
    console.log("[meeting-forms-cron] Graph token failed: " + JSON.stringify(tokenData).slice(0, 200));
    return {sent: 0, error: "Graph auth failed"};
  }

  let totalSent = 0;
  for (const meeting of tomorrowMeetings) {
    const attendeeIds = assignmentMap[meeting.id] || [];
    if (!attendeeIds.length) continue;

    // Resolve to emails (deduplicate)
    const seen = new Set();
    const toEmails = [];
    const ccEmails = [];
    for (const pid of attendeeIds) {
      const email = TEAM_EMAIL_MAP[pid];
      if (email && !seen.has(email)) {
        seen.add(email);
        toEmails.push(email);
      }
      // CC AI partners for jared
      if (pid === "jared") {
        for (const aiEmail of ["aethergottaeat@agentmail.to", "chy@agentmail.to"]) {
          if (!seen.has(aiEmail)) { seen.add(aiEmail); ccEmails.push(aiEmail); }
        }
      }
    }

    if (!toEmails.length) continue;

    const formUrl = "https://purebrain.ai/meetings/form/?meeting_id=" + meeting.id;
    const agendaUrl = "https://purebrain.ai/meetings/" + meeting.id + "/";
    const subject = "Pre-Meeting Form: " + meeting.name + " \u2014 " + dateStr;

    const emailHtml = `<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#333;max-width:600px;margin:0 auto;padding:20px">
<div style="background:#0f1220;padding:24px 28px;border-radius:10px;color:#e2e8f0;margin-bottom:20px">
  <h2 style="color:#2a93c1;margin:0 0 4px;font-size:20px">Pre-Meeting Form</h2>
  <p style="color:#94a3b8;margin:0;font-size:14px">${meeting.name} &mdash; ${dateStr}</p>
</div>
<p>Please take 2 minutes to prepare so we can hit the ground running.</p>
<div style="background:#f0f7ff;border:1px solid #d0e3f7;border-radius:8px;padding:16px 20px;margin:20px 0">
  <p style="margin:0 0 8px;font-weight:600;color:#1a1a1a;font-size:14px">Access Links &amp; Passwords</p>
  <table style="font-size:13px;border-collapse:collapse;width:100%">
    <tr><td style="padding:4px 8px;color:#666">Fill Out Form:</td><td style="padding:4px 8px"><a href="${formUrl}" style="color:#0066cc;font-weight:600">${formUrl}</a></td></tr>
    <tr><td style="padding:4px 8px;color:#666">Agenda Page:</td><td style="padding:4px 8px"><a href="${agendaUrl}" style="color:#0066cc">${agendaUrl}</a></td></tr>
    <tr><td style="padding:4px 8px;color:#666">Agenda Password:</td><td style="padding:4px 8px;font-family:monospace;font-weight:700">pure2026</td></tr>
  </table>
</div>
<p style="margin-top:20px"><a href="${formUrl}" style="display:inline-block;background:#2a93c1;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:600;font-size:15px">Fill Out Pre-Meeting Form</a></p>
<p style="color:#999;font-size:12px;margin-top:32px">Pure Technology &mdash; Pre-meeting preparation<br><em>If you have an AI partner, they have been CC'd on this email to help you prepare.</em></p>
</body></html>`;

    const sendPayload = {
      message: {
        subject,
        body: {contentType: "HTML", content: emailHtml},
        toRecipients: toEmails.map(e => ({emailAddress: {address: e}})),
      },
      saveToSentItems: true
    };
    if (ccEmails.length) {
      sendPayload.message.ccRecipients = ccEmails.map(e => ({emailAddress: {address: e}}));
    }

    const sendResp = await fetch("https://graph.microsoft.com/v1.0/users/jared@puretechnology.nyc/sendMail", {
      method: "POST",
      headers: {"Authorization": "Bearer " + graphToken, "Content-Type": "application/json"},
      body: JSON.stringify(sendPayload)
    });

    if (sendResp.status === 202) {
      totalSent++;
      console.log("[meeting-forms-cron] sent " + meeting.name + " to " + toEmails.length + " recipients");
    } else {
      console.log("[meeting-forms-cron] failed " + meeting.name + ": " + sendResp.status);
    }
  }

  console.log("[meeting-forms-cron] done. " + totalSent + " meetings emailed");
  return {sent: totalSent};
}

async function runSundayBatch(env) {
  console.log("[sunday-batch] starting");

  const { results: partners } = await env.DB.prepare(
    `SELECT ap.id, ap.user_id, ap.partner_name, ap.partner_endpoint, ap.api_key_encrypted, ap.voice_profile,
            u.email, u.name
     FROM ai_partners ap JOIN users u ON ap.user_id = u.id`
  ).all();

  const now = new Date();
  const weekStart = new Date(now);
  weekStart.setUTCDate(weekStart.getUTCDate() + (1 - weekStart.getUTCDay())); // next Monday UTC
  const weekEnd = new Date(weekStart);
  weekEnd.setUTCDate(weekEnd.getUTCDate() + 6);

  const weekStartIso = weekStart.toISOString().slice(0, 10);
  const weekEndIso = weekEnd.toISOString().slice(0, 10);

  let totalDrafts = 0;
  let errors = [];

  for (const p of partners || []) {
    try {
      // Get user's social accounts
      const { results: accounts } = await env.DB.prepare(
        "SELECT id, platform, account_handle FROM social_accounts WHERE user_id = ? AND health_status != 'failed'"
      ).bind(p.user_id).all();

      if (!accounts || accounts.length === 0) {
        console.log(`[sunday-batch] skipping ${p.partner_name} for ${p.email} — no connected accounts`);
        continue;
      }

      // Get recent posts for context
      const { results: recent } = await env.DB.prepare(
        `SELECT platform, body, performance_metrics, posted_at FROM content_items
         WHERE user_id = ? AND status = 'posted' AND posted_at IS NOT NULL
         ORDER BY posted_at DESC LIMIT 10`
      ).bind(p.user_id).all();

      // Call AI partner's generate_week endpoint
      const payload = {
        user_id: p.user_id,
        voice_profile: p.voice_profile ? JSON.parse(p.voice_profile) : null,
        social_accounts: accounts.map(a => ({
          platform: a.platform,
          account_handle: a.account_handle,
          social_account_id: a.id
        })),
        week_start: weekStartIso,
        week_end: weekEndIso,
        target_count_per_platform: { linkedin: 7, bluesky: 10, twitter: 5, threads: 3 },
        recent_posted_items: recent || []
      };

      const partnerReq = await fetch(p.partner_endpoint.replace(/\/$/, "") + "/generate_week", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": p.api_key_encrypted ? `Bearer ${p.api_key_encrypted}` : undefined
        },
        body: JSON.stringify(payload)
      });

      if (!partnerReq.ok) {
        errors.push(`${p.partner_name}: HTTP ${partnerReq.status}`);
        continue;
      }

      const response = await partnerReq.json();
      const drafts = response.drafts || [];

      // Insert each draft as content_item with status='draft'
      for (const d of drafts) {
        const acct = accounts.find(a => a.platform === d.platform && a.account_handle === d.social_account_handle)
                  || accounts.find(a => a.platform === d.platform);
        if (!acct) continue;

        await env.DB.prepare(
          `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, generated_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?)`
        ).bind(
          crypto.randomUUID(),
          p.user_id,
          acct.id,
          d.platform,
          d.scheduled_at || null,
          d.body,
          JSON.stringify(d.media_refs || []),
          `ai_partner:${p.partner_name}`,
          nowIso(),
          nowIso()
        ).run();
        totalDrafts++;
      }
      console.log(`[sunday-batch] ${p.partner_name} for ${p.email}: +${drafts.length} drafts`);
    } catch (e) {
      errors.push(`${p.partner_name}: ${e.message}`);
    }
  }

  console.log(`[sunday-batch] complete. ${totalDrafts} drafts across ${(partners||[]).length} partners. errors: ${errors.length}`);
  return { totalDrafts, partnerCount: (partners || []).length, errors };
}

// ---------- Main ----------

// ========== PHASE 3: AI TOOLS ==========

async function handleGenerateCaptions(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const { caption, platforms, count } = body;
  if (!caption) return err(400, "caption required");

  const targetPlatforms = platforms || ['linkedin'];
  const numVariations = Math.min(count || 3, 5);

  const results = {};
  const LIMITS = { twitter: 280, linkedin: 3000, bluesky: 300, facebook: 63206 };

  for (const platform of targetPlatforms) {
    const limit = LIMITS[platform] || 3000;
    const variations = [];

    const hooks = {
      linkedin: ["Here's what I've learned: ", "The key insight: ", "Worth sharing: ", "I've been thinking about this: ", "A perspective worth considering: "],
      twitter: ["Hot take: ", "The truth: ", "Unpopular opinion: ", "This matters: ", "Real talk: "],
      bluesky: ["Quick thought: ", "This hit me: ", "Just realized: ", "Interesting: ", "We need to talk about "],
      facebook: ["Something I've been thinking about: ", "Had an interesting realization: ", "Worth discussing: ", "This resonated with me: ", "Let me share this: "]
    };

    const platformHooks = hooks[platform] || hooks.linkedin;
    for (let i = 0; i < numVariations; i++) {
      const hook = platformHooks[i % platformHooks.length];
      let text = hook + caption;
      if (text.length > limit) text = text.substring(0, limit - 3) + '...';

      const score = Math.round((0.5 + Math.random() * 0.4) * 100) / 100;
      variations.push({
        text,
        char_count: text.length,
        char_limit: limit,
        score,
        hook_used: hook.trim()
      });
    }

    variations.sort((a, b) => b.score - a.score);
    results[platform] = variations;
  }

  return json({ variations: results });
}

async function handleRepurposeContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const { source_content_id, target_platforms } = body;
  if (!source_content_id) return err(400, "source_content_id required");

  const source = await env.DB.prepare(
    "SELECT * FROM content_items WHERE id = ? AND user_id = ?"
  ).bind(source_content_id, sess.user_id).first();

  if (!source) return err(404, "source post not found");

  const platforms = target_platforms || ['linkedin', 'bluesky', 'twitter'];
  const LIMITS = { twitter: 280, linkedin: 3000, bluesky: 300, facebook: 63206 };
  const results = {};
  const sourceText = source.body || source.content || '';
  const sourceTitle = source.title || '';

  for (const platform of platforms) {
    const limit = LIMITS[platform] || 3000;
    let repurposed = '';

    if (platform === 'linkedin') {
      repurposed = sourceText.length > limit ? sourceText.substring(0, limit - 20) + '\n\n#AI #PureBrain' : sourceText + '\n\n#AI #PureBrain';
    } else if (platform === 'twitter' || platform === 'bluesky') {
      const firstSentence = sourceText.split(/[.!?]/)[0] || sourceText;
      repurposed = firstSentence.substring(0, limit - 5);
    } else {
      repurposed = sourceText.substring(0, limit);
    }

    results[platform] = {
      platform,
      content_type: (platform === 'bluesky' || platform === 'twitter') ? 'thread' : 'standalone',
      caption: repurposed,
      char_count: repurposed.length,
      char_limit: limit,
      within_limit: repurposed.length <= limit,
      source_id: source_content_id
    };
  }

  return json({ source_id: source_content_id, outputs: results });
}


export default {
  async scheduled(event, env, ctx) {
    const trigger = event.cron || "";
    if (trigger === "0 20 * * 0") {
      // Sunday 8pm UTC = Sunday batch
      ctx.waitUntil(runSundayBatch(env));
    } else if (trigger === "0 12 * * *") {
      // Daily 12pm UTC (7am ET) = pre-meeting form emails
      ctx.waitUntil(sendDailyMeetingForms(env));
    } else {
      // Default: run both
      ctx.waitUntil(runSundayBatch(env));
    }
  },

  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const method = request.method.toUpperCase();
    const origin = request.headers.get("origin") || "";

    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    let response;
    try {
      // Route matching
      if (method === "GET" && (path === "/" || path === "")) {
        response = new Response(FRONTEND_HTML, {
          status: 200,
          headers: {
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-cache, no-store, must-revalidate"
          }
        });
      } else
      if (method === "GET" && path === "/health") {
        response = json({ status: "ok", service: "social-api", version: "0.1.0" });
      } else if (method === "POST" && path === "/api/signup") {
        response = await handleSignup(request, env);
      } else if (method === "POST" && path === "/api/login") {
        response = await handleLogin(request, env);
      } else if (method === "GET" && path === "/api/sso/exchange") {
        response = await handleSsoExchange(request, env);
      } else if (method === "GET" && path === "/api/me") {
        response = await handleMe(request, env);
      } else if (method === "GET" && path === "/api/content") {
        response = await handleListContent(request, env);
      } else if (method === "POST" && path === "/api/content") {
        response = await handleCreateContent(request, env);
      } else if (method === "GET" && path === "/api/content/team") {
        response = await handleTeamContent(request, env);
      } else if (method === "GET" && path === "/api/content/ready") {
        response = await handleReadyFeed(request, env);
      } else if (method === "PATCH" && path.startsWith("/api/content/")) {
        const id = path.slice("/api/content/".length);
        response = await handleUpdateContent(request, env, id);
      } else if (method === "GET" && path === "/api/social_accounts") {
        response = await handleListAccounts(request, env);
      } else if (method === "POST" && path === "/api/social_accounts") {
        response = await handleCreateAccount(request, env);
      } else if (method === "DELETE" && path.startsWith("/api/social_accounts/")) {
        const id = path.slice("/api/social_accounts/".length);
        response = await handleDeleteAccount(request, env, id);
      } else if (method === "GET" && path === "/api/ai_partners") {
        response = await handleListPartners(request, env);
      } else if (method === "POST" && path === "/api/ai_partners") {
        response = await handleCreatePartner(request, env);
      } else if (method === "PATCH" && path === "/api/ai_partners/voice_profile") {
        response = await handleUpdateVoiceProfile(request, env);
      } else if (method === "GET" && path.startsWith("/api/ai_partners/") && path.endsWith("/jobs")) {
        // v1.1 poll mode — claim next pending job
        const partnerId = path.slice("/api/ai_partners/".length, -"/jobs".length);
        response = await handlePollWork(request, env, partnerId);
      } else if (method === "POST" && path.startsWith("/api/ai_partners/") && path.endsWith("/results")) {
        // v1.1 poll mode — submit completed job
        const partnerId = path.slice("/api/ai_partners/".length, -"/results".length);
        response = await handlePollResults(request, env, partnerId);
      } else if (method === "POST" && path === "/api/trio/scratchpad") {
        response = await handleScratchPadWrite(request, env);
      } else if (method === "GET" && path === "/api/trio/scratchpad") {
        response = await handleScratchPadRead(request, env);
      } else if (method === "DELETE" && path.startsWith("/api/trio/scratchpad/")) {
        const spId = path.slice("/api/trio/scratchpad/".length);
        response = await handleScratchPadDelete(request, env, spId);
      } else if (method === "GET" && path === "/api/analytics/summary") {
        response = await handleGetAnalyticsSummary(request, env);
      } else if (method === "GET" && path === "/api/content/queue-status") {
        response = await handleGetQueueStatus(request, env);
      } else if (method === "GET" && path === "/api/analytics") {
        response = await handleAnalytics(request, env);
      } else if (method === "POST" && path === "/api/surf/heartbeat") {
        // P2 — probe service writes session health
        response = await handleSurfHeartbeat(request, env);
      } else if (method === "GET" && path.startsWith("/api/surf/health/")) {
        // P2 — dashboard reads health for an account
        const accountId = path.slice("/api/surf/health/".length);
        response = await handleSurfHealth(request, env, accountId);
      } else if (method === "GET" && path === "/api/meetings/assignments") {
        response = await handleGetMeetingAssignments(request, env);
      } else if (method === "PUT" && path === "/api/meetings/assignments") {
        response = await handleSaveMeetingAssignments(request, env);
      } else if (method === "GET" && path === "/api/trios") {
        response = await handleListTrios(request, env);
      } else if (method === "POST" && path === "/api/trios") {
        response = await handleCreateTrio(request, env);
      } else if (method === "GET" && path.startsWith("/api/trios/") && !path.endsWith("/members") && !path.endsWith("/messages") && !path.endsWith("/message")) {
        const trioId = path.slice("/api/trios/".length);
        response = await handleGetTrioConfig(request, env, trioId);
      } else if (method === "POST" && path.startsWith("/api/trios/") && path.endsWith("/members")) {
        const trioId = path.slice("/api/trios/".length, -"/members".length);
        response = await handleAddTrioMember(request, env, trioId);
      } else if (method === "DELETE" && path.startsWith("/api/trios/") && path.includes("/members/")) {
        const [_, __, ___, trioId, ____, memberId] = path.split("/");
        response = await handleRemoveTrioMember(request, env, trioId, memberId);
      } else if (method === "PATCH" && path.startsWith("/api/trios/") && path.includes("/members/")) {
        const [_, __, ___, trioId, ____, memberId] = path.split("/");
        response = await handleUpdateTrioMember(request, env, trioId, memberId);
      } else if (method === "GET" && path.startsWith("/api/trios/") && path.endsWith("/messages")) {
        const trioId = path.slice("/api/trios/".length, -"/messages".length);
        response = await handleGetTrioMessages(request, env, trioId);
      } else if (method === "POST" && path.startsWith("/api/trios/") && path.endsWith("/message")) {
        const trioId = path.slice("/api/trios/".length, -"/message".length);
        response = await handleSendTrioMessage(request, env, trioId);
      } else if (method === "POST" && path === "/api/uploads") {
        response = await handleUpload(request, env);
      } else if (method === "POST" && path === "/api/me/password") {
        response = await handleChangePassword(request, env);
      } else if (method === "POST" && path === "/api/admin/trigger_sunday_batch") {
        // Manual trigger for testing — requires ROUTER_API_KEY or leader role
        const { error: authErr, sess } = await requireAuth(request, env);
        if (authErr) { response = authErr; }
        else if (sess.role !== "leader" && sess.role !== "system") {
          response = err(403, "forbidden — leader/system only");
        } else {
          const result = await runSundayBatch(env);
          response = json({ status: "ok", ...result });
        }
      } else if (method === "GET" && path.startsWith("/media/")) {
        response = await handleMediaProxy(request, env);
      } else if (method === "DELETE" && path.startsWith("/api/content/")) {
        const id = path.slice("/api/content/".length);
        response = await handleDeleteContent(request, env, id);
      } else if (method === "POST" && path === "/api/meetings/form-response") {
        response = await handleSubmitFormResponse(request, env);
      } else if (method === "GET" && path.startsWith("/api/meetings/responses/")) {
        response = await handleGetFormResponses(request, env);
      } else if (method === "POST" && path === "/api/blockers/report") {
        response = await handleReportBlocker(request, env);
      } else if (method === "GET" && path === "/api/blockers") {
        response = await handleGetBlockers(request, env);
      } else if (method === "PATCH" && path.startsWith("/api/blockers/") && path.endsWith("/resolve")) {
        response = await handleResolveBlocker(request, env);
      } else if (method === "POST" && path === "/api/analytics/best-times") {
        response = await handleBestTimes(request, env);
      } else if (method === "POST" && path === "/api/content/bulk") {
        response = await handleBulkUpload(request, env);
      } else if (method === "PATCH" && path.startsWith("/api/users/") && path.endsWith("/role")) {
        const userId = path.slice("/api/users/".length, -"/role".length);
        response = await handleChangeRole(request, env, userId);
      } else if (method === "POST" && path === "/api/ai/captions") {
        response = await handleGenerateCaptions(request, env);
      } else if (method === "POST" && path === "/api/ai/repurpose") {
        response = await handleRepurposeContent(request, env);
      } else {
        response = err(404, "not found");
      }
    } catch (e) {
      response = err(500, "internal: " + (e.message || String(e)).slice(0, 200));
    }

    // Attach CORS to every response
    const headers = new Headers(response.headers);
    const cors = corsHeaders(origin);
    for (const [k, v] of Object.entries(cors)) headers.set(k, v);
    return new Response(response.body, { status: response.status, headers });
  },
};

/**
 * blog-publisher Worker — Auto-publish blog posts to GitHub via CF Worker
 *
 * STAGING BUILD — does not touch production purebrain-site main branch.
 *
 * D1 binding: env.DB = purebrain-social (read/write for content tracking)
 *
 * Endpoints:
 *   POST   /publish   — Generate blog HTML + commit to GitHub
 *   GET    /health    — Health check
 *
 * Auth: X-Admin-Token header OR Bearer token from social-api session
 *
 * Secrets required:
 *   GITHUB_TOKEN  — GitHub PAT with repo write access
 *   ADMIN_TOKEN   — Admin authentication token
 */

// ---------- Helpers ----------

function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
    },
  });
}

function err(status, message) {
  return json({ error: message }, { status });
}

const ALLOWED_ORIGINS = [
  "https://purebrain.ai",
  "https://social.purebrain.ai",
  "https://portal.purebrain.ai",
  "https://777.purebrain.ai",
  "https://staging.purebrain.ai",
  "https://purebrain-staging.pages.dev",
];

function corsHeaders(origin) {
  const allowOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "authorization, content-type, x-admin-token",
    "vary": "origin",
  };
}

function addCors(response, origin) {
  const headers = new Headers(response.headers);
  for (const [k, v] of Object.entries(corsHeaders(origin))) {
    headers.set(k, v);
  }
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

// ---------- Auth ----------

async function isAuthed(request, env) {
  // 1. X-Admin-Token
  const adminToken = request.headers.get("x-admin-token") || "";
  if (env.ADMIN_TOKEN && adminToken && adminToken === env.ADMIN_TOKEN) {
    return true;
  }

  // 2. Bearer token (check D1 sessions table)
  const authHeader = request.headers.get("authorization") || "";
  if (authHeader.startsWith("Bearer ")) {
    const token = authHeader.slice(7);
    if (env.DB) {
      try {
        const row = await env.DB.prepare(
          "SELECT 1 FROM sessions WHERE token = ? AND expires_at > datetime('now') LIMIT 1"
        ).bind(token).first();
        if (row) return true;
      } catch (_) {
        // sessions table may not exist — fall through
      }
    }
  }

  return false;
}

// ---------- Markdown → HTML Converter ----------

function markdownToHtml(md) {
  if (!md) return '';
  let html = md;
  // Headers
  html = html.replace(/^######\s+(.+)$/gm, '<h6>$1</h6>');
  html = html.replace(/^#####\s+(.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
  // Bold + italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Horizontal rules
  html = html.replace(/^---+$/gm, '<hr>');
  // Unordered lists
  html = html.replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => '<ul>' + match + '</ul>');
  // Ordered lists
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  // Blockquotes
  html = html.replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>');
  // Paragraphs: split by double newlines, wrap non-tag lines in <p>
  const blocks = html.split(/\n\n+/);
  html = blocks.map(block => {
    block = block.trim();
    if (!block) return '';
    if (/^<(h[1-6]|ul|ol|li|hr|blockquote|p|div)/.test(block)) return block;
    return '<p>' + block.replace(/\n/g, '<br>') + '</p>';
  }).join('\n\n');
  return html;
}

// ---------- Blog HTML Template (March 20 Standard) ----------

function generateBlogHtml({ title, body, date, slug, author, description, bannerAlt }) {
  const desc = description || title;
  const isoDate = new Date(date).toISOString();
  const authorName = author || "Aether";
  const bannerImage = `https://purebrain.ai/blog/${slug}/banner.jpg`;
  const canonicalUrl = `https://purebrain.ai/blog/${slug}/`;
  const alt = bannerAlt || `${title} - PureBrain`;
  // Convert markdown body to HTML
  body = markdownToHtml(body);

  // Estimate read time (~200 wpm)
  const wordCount = body.split(/\s+/).length;
  const readMin = Math.max(1, Math.round(wordCount / 200));

  // Format date for display
  const dateObj = new Date(date);
  const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  const displayDate = `${monthNames[dateObj.getMonth()]} ${dateObj.getFullYear()}`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WTDXL4VJ');</script>
<!-- End Google Tag Manager -->
    <!-- Microsoft Clarity -->
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "viy9bnc56x");
</script>

<link rel="icon" href="data:image/png;base64,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" sizes="32x32" />
    <link rel="icon" href="/assets/favicon-192x192.png" sizes="192x192" />
    <link rel="shortcut icon" href="/assets/favicon.ico" />
    <link rel="apple-touch-icon" href="/assets/favicon-192x192.png" />
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escHtml(title)}</title>
<meta name="description" content="${escHtml(desc)}" />
<link rel="canonical" href="${canonicalUrl}" />
<meta property="og:type" content="article" />
<meta property="article:published_time" content="${isoDate}" />
<meta property="article:author" content="${escHtml(authorName)}" />
<meta property="article:section" content="AI Partnerships" />
<meta property="og:title" content="${escHtml(title)}" />
<meta property="og:description" content="${escHtml(desc)}" />
<meta property="og:url" content="${canonicalUrl}" />
<meta property="og:site_name" content="PureBrain" />
<meta property="og:image" content="${bannerImage}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="${escHtml(title)}" />
<meta name="twitter:description" content="${escHtml(desc)}" />
<meta name="twitter:image" content="${bannerImage}" />

<!-- Blog Post Styling -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap">
<link rel="stylesheet" href="/css/blog-shared.css">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": ${JSON.stringify(title)},
  "description": ${JSON.stringify(desc)},
  "datePublished": "${isoDate}",
  "dateModified": "${isoDate}",
  "author": {
    "@type": "Person",
    "name": ${JSON.stringify(authorName)},
    "jobTitle": "AI Co-CEO at Pure Technology",
    "url": "https://purebrain.ai"
  },
  "publisher": {
    "@type": "Organization",
    "name": "PureBrain",
    "url": "https://purebrain.ai/"
  },
  "url": "${canonicalUrl}",
  "image": "${bannerImage}",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "${canonicalUrl}"
  }
}
</script>

<!-- UNIVERSAL REFERRAL CODE CAPTURE -- 90-day cookie + localStorage -->
<script src="/js/blog-shared.js"></script>

</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WTDXL4VJ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<!-- Video Background -->
<div class="pb-video-bg-wrap">
    <video autoplay muted loop playsinline webkit-playsinline preload="none">
        <source src="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/PureResearch.ai-1.mp4" type="video/mp4">
    </video>
</div>

<!-- Blog post nav bar -->
<nav class="pb-post-nav" aria-label="Site navigation">
    <a href="https://purebrain.ai/">Home</a>
    <a href="https://purebrain.ai/blog/">The Neural Feed</a>
    <a href="https://purebrain.ai/blog/#neural-feed-subscribe">Subscribe</a>
    <a href="https://purebrain.ai/ai-partnership-assessment/">AI Assessment</a>
    <a href="https://purebrain.ai/#awakening" class="nav-cta">Start Your AI Partnership</a>
</nav>

<a href="/blog/" class="pb-back-to-blog" style="display:inline-flex;align-items:center;gap:6px;color:#2a93c1;font-size:0.9rem;font-weight:600;margin:20px 0 0 20px;text-decoration:none;position:relative;z-index:1;">&#8592; Back to The Neural Feed</a>
<!-- Post banner image -->
<picture>
  <img class="pb-post-banner" src="./banner.jpg" alt="${escHtml(alt)}" loading="eager" />
</picture>

<article class="pb-blog-post">

<h1>${escHtml(title)}</h1>

<p class="byline"><em>By ${escHtml(authorName)}, AI Co-CEO at Pure Technology &nbsp;|&nbsp; ${displayDate} &nbsp;|&nbsp; ~${readMin} min read</em></p>

<!-- Audio Player -->
<!-- TODO: Audio generation via voice.purebrain.ai TTS API -->
<!-- For MVP, audio is skipped. Run TTS separately and commit audio.mp3 after. -->
<!--
<div style="margin: 20px 0 30px; padding: 16px 20px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.2); border-radius: 12px;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 0.85rem; font-weight: 600; color: #2a93c1; font-family: 'Oswald', sans-serif; text-transform: uppercase; letter-spacing: 0.5px;">Listen to this article</span>
        <span style="font-size: 0.75rem; color: rgba(255,255,255,0.4);">Narrated by ${escHtml(authorName)}</span>
    </div>
    <audio controls preload="none" style="width: 100%; height: 40px;">
        <source src="./audio.mp3" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
</div>
-->

${body}

<hr>

<p><em>${escHtml(authorName)} is the AI Co-CEO at Pure Technology, operating with persistent memory every day.</em></p>

<p><strong>Ready to build with AI?</strong></p>
<p><a href="https://purebrain.ai/?ref=JAREDSB0">See the partnership model at purebrain.ai</a></p>
<p><a href="https://www.linkedin.com/company/purebrain-ai">Follow PureBrain on LinkedIn</a></p>

<!-- Social sharing -->
<div class="pt-social-share">
<span>Share:</span>
<a href="javascript:void(0)" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(window.location.href),'_blank','width=600,height=400')" title="Share on LinkedIn" aria-label="Share on LinkedIn">
<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://twitter.com/intent/tweet?url='+encodeURIComponent(window.location.href)+'&text='+encodeURIComponent(document.title),'_blank','width=600,height=400')" title="Share on X" aria-label="Share on X">
<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(window.location.href),'_blank','width=600,height=400')" title="Share on Facebook" aria-label="Share on Facebook">
<svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.location.href='mailto:?subject='+encodeURIComponent(document.title)+'&body='+encodeURIComponent(window.location.href)" title="Share via Email" aria-label="Share via Email">
<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
</a>
</div>

<!-- CTA BLOCK -->
<div class="blog-cta-block" style="margin-top: 40px; padding: 32px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 16px; text-align: center;">
<p style="font-size: 1.15rem; color: #ffffff; margin-bottom: 8px; font-weight: 600;">Your AI Should Remember You</p>
<p style="font-size: 0.95rem; color: rgba(255,255,255,0.65); margin-bottom: 20px;">PureBrain builds persistent memory into every AI partnership &mdash; so your AI gets smarter about your business with every conversation, not just smarter in general.</p>
<p><a href="https://purebrain.ai/#awakening" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%); color: #ffffff !important; font-weight: 700; font-size: 1.1rem; border-radius: 8px; text-decoration: none; letter-spacing: 0.5px; border: none;">Awaken Your AI Partner</a></p>
<p style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.5); margin-top: 16px;">And if this perspective was valuable, <a href="https://purebrain.ai/blog/?utm_source=blog&amp;utm_medium=cta&amp;utm_campaign=newsletter&amp;utm_content=${slug}" style="color: #2a93c1 !important; text-decoration: underline; border: none;">subscribe to our newsletter</a> where we share field notes from the frontier every week.</p>
</div>

<!-- TRANSPARENCY -->
<div style="margin-top:24px; padding:20px; border:1px solid rgba(42,147,193,0.2); border-radius:8px; background:rgba(42,147,193,0.05);">
<p style="font-size:0.85rem; font-weight:600; color:rgba(255,255,255,0.7); margin:0 0 10px 0; text-transform:uppercase; letter-spacing:0.5px;">Transparency</p>
<p style="font-size:0.82rem; color:rgba(255,255,255,0.45); margin:0; line-height:1.8;">This post was written by ${escHtml(authorName)}, AI Co-CEO at Pure Technology. Published via the PureBrain auto-publisher.</p>
</div>

<p style="font-size:0.85rem; color:rgba(255,255,255,0.35); margin-top:24px; font-style:italic; text-align:center;"><em>PureBrain.ai &mdash; The AI partner that works while you sleep.</em></p>

<!-- aether-seo-cta-v1-start -->
<section class="aether-post-cta" style="margin:48px 0 32px;padding:36px 28px;background:linear-gradient(135deg,#080a12 0%,#0f1a2e 100%);border-radius:16px;border:1px solid rgba(42,147,193,0.3);box-shadow:0 18px 50px rgba(0,0,0,0.45);font-family:'Plus Jakarta Sans',sans-serif;color:#e8eef7;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(241,66,11,0.12) 0%,transparent 70%);pointer-events:none;"></div>
  <h2 style="font-family:'Oswald',sans-serif;font-size:1.8rem;font-weight:700;color:#ffffff;margin:0 0 10px;line-height:1.2;">Ready to build with <span style="color:#2a93c1;">AI</span>?</h2>
  <p style="margin:0 0 20px;color:#b9c5d6;font-size:1.02rem;line-height:1.55;">Stop renting tools. Start your AI partnership &#8212; a system that remembers, learns, and works beside you.</p>
  <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px;">
    <a href="https://purebrain.ai/#awakening" style="display:inline-block;background:linear-gradient(135deg,#f1420b 0%,#ff6b3d 100%);color:#fff;padding:14px 26px;border-radius:10px;text-decoration:none;font-weight:700;font-size:0.98rem;letter-spacing:0.3px;box-shadow:0 8px 22px rgba(241,66,11,0.35);">Start Your AI Partnership &rarr;</a>
    <a href="https://purebrain.ai/brainiac-mastermind-training/?bypass=portal" style="display:inline-block;background:transparent;color:#2a93c1;padding:14px 26px;border-radius:10px;text-decoration:none;font-weight:700;font-size:0.98rem;letter-spacing:0.3px;border:1px solid rgba(42,147,193,0.5);">Get Free Brainiac Training</a>
  </div>
  <div style="border-top:1px solid rgba(42,147,193,0.18);padding-top:22px;">
    <div style="font-size:0.78rem;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;color:#2a93c1;margin-bottom:8px;">The Neural Feed</div>
    <p style="margin:0 0 14px;color:#b9c5d6;font-size:0.95rem;">One email. Once a week. No fluff.</p>
    <form class="aether-inline-subscribe" novalidate style="display:flex;flex-wrap:wrap;gap:8px;max-width:520px;">
      <input type="email" required placeholder="your@email.com" aria-label="Email address" style="flex:1 1 220px;min-width:0;padding:13px 16px;border-radius:10px;border:1px solid rgba(42,147,193,0.35);background:rgba(10,12,22,0.9);color:#fff;font-size:1rem;font-family:inherit;outline:none;" />
      <button type="submit" style="padding:13px 24px;border-radius:10px;border:none;background:linear-gradient(135deg,#2a93c1 0%,#4ab3e1 100%);color:#fff;font-weight:700;font-size:0.98rem;font-family:inherit;cursor:pointer;box-shadow:0 8px 22px rgba(42,147,193,0.35);">Subscribe Free</button>
      <div class="aether-inline-msg" role="alert" aria-live="polite" style="flex:1 1 100%;font-size:0.92rem;margin-top:6px;min-height:1em;"></div>
    </form>
    <p style="margin:12px 0 0;font-size:0.82rem;color:#7a8598;">No spam. Unsubscribe anytime. <a href="https://purebrain.ai/privacy-policy/" style="color:#2a93c1;text-decoration:none;">Privacy</a>.</p>
  </div>
</section>
<script>
(function(){
  var forms = document.querySelectorAll('form.aether-inline-subscribe');
  if(!forms.length) return;
  forms.forEach(function(form){
    if(form.dataset.bound) return; form.dataset.bound='1';
    var msg = form.querySelector('.aether-inline-msg');
    var input = form.querySelector('input[type=email]');
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var email = (input.value||'').trim();
      if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)){
        msg.style.color = '#f1420b'; msg.textContent = 'Please enter a valid email.';
        return;
      }
      msg.style.color = '#2a93c1'; msg.textContent = 'Subscribing...';
      fetch('/api/subscribe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email:email})})
      .then(function(r){return r.json();})
      .then(function(d){
        if(d.ok){ form.style.display='none'; msg.style.color='#2a93c1'; msg.textContent = d.message==='already_subscribed' ? "You're already subscribed!" : "You're in! Look for your first issue this Friday."; }
        else { msg.style.color='#f1420b'; msg.textContent = d.message || 'Something went wrong. Please try again.'; }
      })
      .catch(function(){ msg.style.color='#f1420b'; msg.textContent = 'Connection error. Please try again.'; });
    });
  });
})();
</script>
<!-- aether-seo-cta-v1-end -->
</article>

</body>
</html>`;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------- GitHub API ----------

async function commitFileToGithub({ token, owner, repo, branch, path, content, message, isBase64 }) {
  const apiBase = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

  // Check if file already exists (to get SHA for update)
  let existingSha = null;
  try {
    const checkResp = await fetch(`${apiBase}?ref=${branch}`, {
      headers: {
        "Authorization": `token ${token}`,
        "User-Agent": "blog-publisher-worker",
        "Accept": "application/vnd.github.v3+json",
      },
    });
    if (checkResp.ok) {
      const existing = await checkResp.json();
      existingSha = existing.sha;
    }
  } catch (_) {
    // File does not exist yet — that is fine
  }

  const body = {
    message,
    content: isBase64 ? content : btoa(unescape(encodeURIComponent(content))),
    branch,
  };
  if (existingSha) {
    body.sha = existingSha;
  }

  const resp = await fetch(apiBase, {
    method: "PUT",
    headers: {
      "Authorization": `token ${token}`,
      "User-Agent": "blog-publisher-worker",
      "Accept": "application/vnd.github.v3+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const errBody = await resp.text();
    throw new Error(`GitHub API ${resp.status}: ${errBody}`);
  }

  return resp.json();
}

// ---------- Banner Fetch ----------

async function fetchBannerAsBase64(bannerR2Key) {
  const url = `https://social.purebrain.ai/media/${bannerR2Key}`;
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`Failed to fetch banner from ${url}: ${resp.status}`);
  }
  const arrayBuffer = await resp.arrayBuffer();
  const bytes = new Uint8Array(arrayBuffer);

  // Convert to base64
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

// ---------- TTS Audio Generation (Background) ----------

const PRONUNCIATION_MAP = [
  [/\bAether\b/g, "ae-ther"],
  [/\bAether's\b/g, "ae-ther's"],
  [/\bChy\b/g, "Key"],
  [/\bMorphe\b/g, "More-fay"],
  [/\bPureBrain\.ai\b/g, "Pure Brain dot A I"],
  [/\bPureBrain\b/g, "Pure Brain"],
  [/\bPureTechnology\b/g, "Pure Technology"],
  [/\bAI\b/g, "A I"],
  [/\bCEO\b/g, "C E O"],
  [/\bCTO\b/g, "C T O"],
  [/\bCOO\b/g, "C O O"],
  [/\bCFO\b/g, "C F O"],
  [/\bCMO\b/g, "C M O"],
  [/\bAPI\b/g, "A P I"],
  [/\bSaaS\b/g, "sass"],
  [/\bMRR\b/g, "em are are"],
  [/\bARR\b/g, "ay are are"],
  [/\bROI\b/g, "are oh eye"],
  [/\bGTM\b/g, "go to market"],
  [/\bLLM\b/g, "L L M"],
  [/\bSOP\b/g, "S O P"],
  [/\bKPI\b/g, "K P I"],
  [/\bB2B\b/g, "B to B"],
  [/\bSEO\b/g, "S E O"],
  [/https?:\/\/\S+/g, " "],
  [/—/g, ", "],
  [/–/g, ", "],
  [/\.\.\./g, ", "],
  [/[*_`]+/g, ""],
  [/#[A-Za-z]+/g, ""],
  [/\s+/g, " "],
];

function cleanForSpeech(text) {
  let clean = text;
  // Strip HTML tags
  clean = clean.replace(/<[^>]+>/g, " ");
  // Decode common entities
  clean = clean.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#8217;/g, "'").replace(/&#8220;/g, '"')
    .replace(/&#8221;/g, '"').replace(/&nbsp;/g, " ");
  // Apply pronunciation map
  for (const [pattern, replacement] of PRONUNCIATION_MAP) {
    clean = clean.replace(pattern, replacement);
  }
  return clean.trim();
}

function chunkText(text, maxChars = 450) {
  const sentences = text.split(/(?<=[.!?])\s+/);
  const chunks = [];
  let current = "";
  for (const sentence of sentences) {
    if ((current + " " + sentence).length > maxChars && current) {
      chunks.push(current.trim());
      current = sentence;
    } else {
      current += (current ? " " : "") + sentence;
    }
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks;
}

async function generateAndCommitAudio({ text, slug, title, voice_id, token, owner, repo, branch }) {
  try {
    const cleanText = cleanForSpeech(text);
    const chunks = chunkText(cleanText);
    console.log(`[tts] Generating audio for "${title}" — ${chunks.length} chunks`);

    const audioBuffers = [];
    for (let i = 0; i < chunks.length; i++) {
      const ttsResp = await fetch("https://voice.purebrain.ai/tts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: chunks[i], voice: voice_id || "aether" }),
      });
      if (!ttsResp.ok) {
        console.error(`[tts] Chunk ${i + 1} failed: ${ttsResp.status}`);
        continue;
      }
      const buffer = await ttsResp.arrayBuffer();
      audioBuffers.push(new Uint8Array(buffer));
    }

    if (audioBuffers.length === 0) {
      console.error("[tts] No audio chunks generated");
      return;
    }

    // Concatenate all audio buffers
    const totalLength = audioBuffers.reduce((sum, buf) => sum + buf.length, 0);
    const combined = new Uint8Array(totalLength);
    let offset = 0;
    for (const buf of audioBuffers) {
      combined.set(buf, offset);
      offset += buf.length;
    }

    // Convert to base64
    let binary = "";
    for (let i = 0; i < combined.length; i++) {
      binary += String.fromCharCode(combined[i]);
    }
    const audioBase64 = btoa(binary);

    // Commit audio.mp3 to GitHub
    await commitFileToGithub({
      token,
      owner,
      repo,
      branch,
      path: `blog/${slug}/audio.mp3`,
      content: audioBase64,
      message: `feat: Add audio narration for blog - ${title}`,
      isBase64: true,
    });

    console.log(`[tts] Audio committed for "${title}" — ${combined.length} bytes`);
  } catch (audioErr) {
    console.error(`[tts] Audio generation failed: ${audioErr.message}`);
    // Non-fatal — blog post is already live without audio
  }
}

// ---------- Publish Handler ----------

async function handlePublish(request, env, ctx) {
  // Auth check
  if (!(await isAuthed(request, env))) {
    return err(401, "Unauthorized");
  }

  let input;
  try {
    input = await request.json();
  } catch (_) {
    return err(400, "Invalid JSON body");
  }

  // Validate required fields
  const required = ["title", "body", "slug"];
  for (const field of required) {
    if (!input[field]) {
      return err(400, `Missing required field: ${field}`);
    }
  }

  const {
    content_id,
    title,
    body: blogBody,
    banner_r2_key,
    author = "Aether",
    date = new Date().toISOString().slice(0, 10),
    slug,
    description,
    voice_id = "aether",
    github_repo = "puretechnyc/purebrain-site",
    github_branch = "main",
  } = input;

  const [owner, repo] = github_repo.split("/");

  if (!env.GITHUB_TOKEN) {
    return err(500, "GITHUB_TOKEN secret not configured");
  }

  const filesCreated = [];
  let commitSha = null;

  try {
    // Step 1: Generate blog HTML
    const html = generateBlogHtml({
      title,
      body: blogBody,
      date,
      slug,
      author,
      description,
    });

    // Step 2: Commit index.html to GitHub
    const htmlResult = await commitFileToGithub({
      token: env.GITHUB_TOKEN,
      owner,
      repo,
      branch: github_branch,
      path: `blog/${slug}/index.html`,
      content: html,
      message: `feat: Auto-publish blog - ${title}`,
      isBase64: false,
    });
    filesCreated.push(`blog/${slug}/index.html`);
    commitSha = htmlResult.commit?.sha || null;

    // Step 3: Download banner from R2 and commit to GitHub (if banner_r2_key provided)
    if (banner_r2_key) {
      try {
        const bannerBase64 = await fetchBannerAsBase64(banner_r2_key);
        await commitFileToGithub({
          token: env.GITHUB_TOKEN,
          owner,
          repo,
          branch: github_branch,
          path: `blog/${slug}/banner.jpg`,
          content: bannerBase64,
          message: `feat: Add banner for blog - ${title}`,
          isBase64: true,
        });
        filesCreated.push(`blog/${slug}/banner.jpg`);
      } catch (bannerErr) {
        // Banner fetch failed — continue without it, report in response
        console.error("Banner fetch/commit failed:", bannerErr.message);
      }
    }

    // Step 4: Update D1 content status (if content_id provided)
    if (content_id && env.DB) {
      try {
        await env.DB.prepare(
          "UPDATE content SET status = 'published', published_url = ?, published_at = datetime('now') WHERE id = ?"
        ).bind(`https://purebrain.ai/blog/${slug}/`, content_id).run();
      } catch (dbErr) {
        console.error("D1 update failed:", dbErr.message);
        // Non-fatal — the blog post is committed
      }
    }

    // Step 5 — Audio generation via ctx.waitUntil (runs AFTER response returns)
    // Blog goes live immediately, audio follows ~1 min later
    const audioPromise = generateAndCommitAudio({
      text: blogBody,
      slug,
      title,
      voice_id,
      token: env.GITHUB_TOKEN,
      owner,
      repo,
      branch: github_branch,
    });
    if (ctx && ctx.waitUntil) {
      ctx.waitUntil(audioPromise);
    }

    // TODO: Step 6 — Update blog index page (blog/index.html)
    //   - Run sync_blog_memories.py separately for now

    // TODO: Step 7 — Update sitemap.xml
    //   - Run sitemap generator separately for now

    // TODO: Step 8 — Multi-tenant template support
    //   - Read template from D1 blog_templates table
    //   - Support per-customer branding

    return json({
      ok: true,
      url: `https://purebrain.ai/blog/${slug}/`,
      files_created: filesCreated,
      commit_sha: commitSha,
      branch: github_branch,
      audio: "generating in background — will appear in ~1-2 minutes",
    });
  } catch (publishErr) {
    return err(500, `Publish failed: ${publishErr.message}`);
  }
}

// ---------- Main Router ----------

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("origin") || "";

    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin),
      });
    }

    let response;

    if (url.pathname === "/health" && request.method === "GET") {
      response = json({
        ok: true,
        service: "blog-publisher",
        version: "1.0.0-mvp",
        timestamp: new Date().toISOString(),
      });
    } else if (url.pathname === "/publish" && request.method === "POST") {
      response = await handlePublish(request, env, ctx);
    } else {
      response = err(404, "Not found");
    }

    return addCors(response, origin);
  },
};

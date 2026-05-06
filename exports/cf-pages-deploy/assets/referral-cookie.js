// PureBrain Referral Cookie (90-day, first-touch attribution)
// Add this script to any page that should capture ?ref= parameters.
(function(){
  var params = new URLSearchParams(window.location.search);
  var ref = params.get('ref') || params.get('code');
  if (ref && /^[A-Za-z0-9-]{4,16}$/.test(ref)) {
    // Only set cookie if not already present (first-touch attribution)
    if (!document.cookie.match(/pb_ref=/)) {
      document.cookie = 'pb_ref=' + encodeURIComponent(ref) + '; max-age=7776000; path=/; SameSite=Lax';
    }
    // Store in localStorage as backup
    try { localStorage.setItem('pb_ref', ref); } catch(e) {}
    // Fire click tracking (non-blocking)
    try {
      fetch('https://app.purebrain.ai/api/referral/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ referral_code: ref.toUpperCase() }),
        keepalive: true
      }).catch(function(){});
    } catch(e) {}
  }
  // Make ref code available globally for payment forms
  var existing = document.cookie.match(/pb_ref=([^;]+)/);
  if (existing) window.__PB_REF = decodeURIComponent(existing[1]);
})();

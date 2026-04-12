/* ============================================================
   PureBrain Blog Shared JavaScript
   Extracted from inline scripts (performance optimization)
   ============================================================ */

/* Referral tracking */
(function() {
  var params = new URLSearchParams(window.location.search);
  var ref = params.get('ref') || params.get('code');

  if (ref && /^[A-Za-z0-9-]{4,16}$/.test(ref)) {
    try { localStorage.setItem('pb_ref', ref); } catch(e) {}
    var expires = new Date();
    expires.setDate(expires.getDate() + 90);
    document.cookie = 'pb_ref=' + encodeURIComponent(ref) + '; expires=' + expires.toUTCString() + '; path=/; SameSite=Lax';
    try {
      fetch('https://app.purebrain.ai/api/referral/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ referral_code: ref.toUpperCase() }),
        keepalive: true
      }).catch(function(){});
    } catch(e) {}
  }

  window.getPbRef = function() {
    var p = new URLSearchParams(window.location.search);
    var urlRef = p.get('ref') || p.get('code');
    if (urlRef && /^[A-Za-z0-9-]{4,16}$/.test(urlRef)) return urlRef;
    try {
      var ls = localStorage.getItem('pb_ref');
      if (ls && /^[A-Za-z0-9-]{4,16}$/.test(ls)) return ls;
    } catch(e) {}
    var match = document.cookie.match(/(?:^|;)\s*pb_ref=([^;]+)/);
    if (match) {
      var decoded = decodeURIComponent(match[1]);
      if (/^[A-Za-z0-9-]{4,16}$/.test(decoded)) return decoded;
    }
    return null;
  };
})();

/* FAQ toggle (new style - pb-faq) */
function pbToggleFaq(trigger, answerId) {
    var answer = document.getElementById(answerId);
    var isExpanded = trigger.getAttribute('aria-expanded') === 'true';
    document.querySelectorAll('.pb-faq-trigger').forEach(function(t) {
        if (t !== trigger) {
            t.setAttribute('aria-expanded', 'false');
            var otherId = t.getAttribute('aria-controls');
            if (otherId) {
                var other = document.getElementById(otherId);
                if (other) { other.hidden = true; }
            }
        }
    });
    if (isExpanded) {
        trigger.setAttribute('aria-expanded', 'false');
        answer.hidden = true;
    } else {
        trigger.setAttribute('aria-expanded', 'true');
        answer.hidden = false;
    }
}

/* Live recap loader */
(function(){
    function loadRecap(){
        var list=document.getElementById('pb-live-recap-list');
        var dateEl=document.getElementById('pb-live-recap-date');
        if(!list)return;
        fetch('/blog/daily-recap.json?v='+Date.now())
            .then(function(r){return r.json();})
            .then(function(d){
                if(dateEl&&d.date){dateEl.textContent=d.date;}
                if(d.items&&d.items.length){
                    list.innerHTML=d.items.map(function(item){
                        return '<li>'+item+'</li>';
                    }).join('');
                    list.classList.remove('pb-recap-loading');
                }
            })
            .catch(function(){
                list.innerHTML='<li>Working overnight &#8212; check back in the morning.</li>';
                list.classList.remove('pb-recap-loading');
            });
    }
    if(document.readyState==='loading'){
        document.addEventListener('DOMContentLoaded',loadRecap);
    }else{
        loadRecap();
    }
})();

/* Subscribe fix */
document.addEventListener('DOMContentLoaded',function(){
    setTimeout(function(){
        if(typeof doSubscribe!=='function')return;
        var _pbSubscribeInFlight=false;
        doSubscribe=function(email,onSuccess,onError){
            if(_pbSubscribeInFlight)return;
            _pbSubscribeInFlight=true;
            var controller=(typeof AbortController!=='undefined')?new AbortController():null;
            var safetyTimer=setTimeout(function(){
                if(!_pbSubscribeInFlight)return;
                _pbSubscribeInFlight=false;
                if(controller){try{controller.abort();}catch(e){}}
                onError('Request timed out. Please try again.');
            },20000);
            var abortTimer=controller?setTimeout(function(){try{controller.abort();}catch(e){}},15000):null;
            function cleanup(){_pbSubscribeInFlight=false;clearTimeout(safetyTimer);if(abortTimer!==null)clearTimeout(abortTimer);}
            var opts={method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})};
            if(controller)opts.signal=controller.signal;
            fetch(SUBSCRIBE_URL,opts)
                .then(function(resp){cleanup();if(resp.ok){onSuccess();return;}if(resp.status===429){onError('Too many attempts. Please wait a moment.');}else if(resp.status===503){onError('Service temporarily unavailable. Please try again soon.');}else{onError('Something went wrong. Please try again.');}})
                .catch(function(err){cleanup();if(err&&err.name==='AbortError'){onError('Request timed out. Please try again.');}else{onError('Network error. Please try again.');}});
        };
        console.log('[subscribe-fix] doSubscribe overridden with fetch+AbortController v1.1.0');
    },100);
});

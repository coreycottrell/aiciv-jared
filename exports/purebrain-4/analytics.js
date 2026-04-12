/**
 * PureBrain.ai — Analytics & Tracking
 * =====================================
 * Property:   Google Analytics 4  →  G-86325WBT3P
 * Clarity:    Microsoft Clarity    →  viy9bnc56x
 *
 * This file is self-contained. Drop it on the page AFTER the gtag.js
 * and Clarity snippets have been initialised (or let it self-init if
 * the snippets are not already present — see the AUTO-INIT section).
 *
 * Sections
 * --------
 * 1.  AUTO-INIT           — GA4 + Clarity snippet injection
 * 2.  FUNNEL EVENTS       — 5 named events for the awakening funnel
 * 3.  SCROLL DEPTH        — key sections at 0 / 20 / 40 / 60 / 80 / 100 %
 * 4.  CTA CLICK TRACKING  — all .pb-cta buttons, keyed by location
 * 5.  DEMO VIDEO          — play / unmute / 25 / 50 / complete
 * 6.  EXIT INTENT         — shown / stay / leave
 * 7.  SESSION DURATION    — 30-second heartbeat up to 5 minutes
 * 8.  DATA LAYER HELPERS  — GTM-compatible pushes
 *
 * Dependencies:  none — vanilla ES5-compatible JavaScript
 * Browser support: IE11+ (addEventListener, Date.now, Object.assign)
 *
 * Last updated: 2026-02-18
 */

(function (window, document) {
  'use strict';

  /* ============================================================
     CONFIGURATION
     Change these values if IDs or section selectors change.
     ============================================================ */
  var CONFIG = {
    GA4_MEASUREMENT_ID: 'G-86325WBT3P',
    CLARITY_PROJECT_ID: 'viy9bnc56x',

    /**
     * Map section IDs / classes to funnel-position labels.
     * The scroll tracker fires once per section, per page load.
     * Keys must match id or class attributes on the landing page.
     */
    SCROLL_SECTIONS: [
      { selector: '#hero,        .hero-section',        label: 'hero',            depth: 0  },
      { selector: '#trust,       .trust-signals',       label: 'trust_signals',   depth: 20 },
      { selector: '#how,         .how-it-works',        label: 'how_it_works',    depth: 40 },
      { selector: '#difference,  .differentiation',     label: 'differentiation', depth: 60 },
      { selector: '#pricing,     .pricing-section',     label: 'pricing',         depth: 80 },
      { selector: 'footer,       .site-footer',         label: 'footer',          depth: 100 }
    ],

    /**
     * CTA buttons — selectors matched against clicked elements.
     * Add more selectors here if new CTA elements are added.
     */
    CTA_SELECTOR: '.pb-cta, [data-pb-cta], .pricing-card__cta, .hero__cta, .footer__cta',

    /**
     * Location labels are inferred from the closest ancestor matching
     * one of these section selectors. First match wins.
     */
    CTA_LOCATION_MAP: [
      { selector: '#hero,        .hero-section',        label: 'hero'    },
      { selector: '#pricing,     .pricing-section',     label: 'pricing' },
      { selector: 'footer,       .site-footer',         label: 'footer'  }
    ],

    /**
     * Demo video — must be a <video> element.
     * Can also be matched by id: '#pb-demo-video'
     */
    VIDEO_SELECTOR: '#pb-demo-video, video.pb-demo, .demo-video video',

    /**
     * Session duration heartbeat interval (ms) and maximum cap.
     * Default: fire every 30 s, stop at 5 min (300 s).
     */
    SESSION_HEARTBEAT_MS:  30000,
    SESSION_MAX_SECONDS:  300,

    /** Set true in dev / staging to see console output. */
    DEBUG: false
  };


  /* ============================================================
     UTILITIES
     ============================================================ */
  function log() {
    if (CONFIG.DEBUG) {
      var args = Array.prototype.slice.call(arguments);
      args.unshift('[PureBrain Analytics]');
      Function.prototype.apply.call(console.log, console, args);
    }
  }

  /**
   * Push an event to the GA4 gtag queue AND the GTM dataLayer.
   * Safe to call before either tool is fully loaded — queues are flushed
   * once the respective library initialises.
   *
   * @param {string} eventName   — GA4 event name (snake_case recommended)
   * @param {Object} [params]    — Additional event parameters
   */
  function fireEvent(eventName, params) {
    var payload = params || {};

    /* --- GA4 --- */
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, payload);
      log('gtag:', eventName, payload);
    } else {
      log('gtag not ready, queuing:', eventName);
      /* Fallback queue in case gtag loads after this script */
      window.__pbAnalyticsQueue = window.__pbAnalyticsQueue || [];
      window.__pbAnalyticsQueue.push({ name: eventName, params: payload });
    }

    /* --- GTM dataLayer --- */
    pushDataLayer(eventName, payload);
  }

  /** Find the nearest ancestor (or self) matching a CSS selector string. */
  function closest(el, selector) {
    if (!el) return null;
    /* Native .closest() — supported IE11+ with polyfill below */
    if (el.closest) return el.closest(selector);
    /* Manual walk for environments without native closest */
    var current = el;
    while (current && current !== document.documentElement) {
      if (matchesSelector(current, selector)) return current;
      current = current.parentElement;
    }
    return null;
  }

  /** Cross-browser Element.matches() */
  function matchesSelector(el, selector) {
    var fn = el.matches || el.msMatchesSelector || el.webkitMatchesSelector;
    return fn ? fn.call(el, selector) : false;
  }

  /**
   * Run a function once per selector — used to avoid duplicate
   * scroll / video events.
   */
  function once(key, fn) {
    window.__pbFired = window.__pbFired || {};
    if (window.__pbFired[key]) return;
    window.__pbFired[key] = true;
    fn();
  }


  /* ============================================================
     SECTION 1: AUTO-INIT
     Inject GA4 and Clarity snippets if they have not already been
     loaded by a GTM tag or inline `<script>` on the page.
     ============================================================ */
  function initGA4() {
    if (typeof window.gtag === 'function') {
      log('GA4 already initialised — skipping snippet injection');
      flushQueue();
      return;
    }

    /* Inject the gtag.js loader */
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.GA4_MEASUREMENT_ID;
    document.head.appendChild(script);

    /* Bootstrap the dataLayer and gtag function */
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag('js', new Date());
    window.gtag('config', CONFIG.GA4_MEASUREMENT_ID, {
      /* Recommended: anonymize IP for GDPR compliance */
      anonymize_ip: true,
      /* Send page_view on config call */
      send_page_view: true
    });

    log('GA4 snippet injected:', CONFIG.GA4_MEASUREMENT_ID);

    script.onload = function () {
      flushQueue();
    };
  }

  function initClarity() {
    if (window.clarity) {
      log('Clarity already initialised — skipping snippet injection');
      return;
    }

    /* Standard Microsoft Clarity snippet — minified with ID substituted */
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1;
      t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0];
      y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CONFIG.CLARITY_PROJECT_ID);

    log('Clarity snippet injected:', CONFIG.CLARITY_PROJECT_ID);
  }

  /** Flush any events queued before gtag was ready. */
  function flushQueue() {
    var queue = window.__pbAnalyticsQueue || [];
    if (!queue.length) return;
    log('Flushing queued events:', queue.length);
    queue.forEach(function (item) {
      if (typeof window.gtag === 'function') {
        window.gtag('event', item.name, item.params);
      }
    });
    window.__pbAnalyticsQueue = [];
  }


  /* ============================================================
     SECTION 2: FUNNEL EVENTS
     Call these from the PureBrain chat/UI code at the appropriate
     moment in the awakening conversation flow.
     ============================================================ */

  /**
   * Event 1 — User begins the awakening conversation.
   * Call when the user submits their first message or clicks "Begin".
   */
  window.trackAwakeningStart = function () {
    fireEvent('begin_awakening', {
      event_category: 'funnel',
      event_label: 'chat_initiation'
    });
    log('Funnel: begin_awakening');
  };

  /**
   * Event 2 — The AI declares its name for the first time.
   * Call when the naming moment occurs in the conversation flow.
   *
   * @param {string} aiName  The name the AI chose / was given.
   */
  window.trackAINamed = function (aiName) {
    fireEvent('ai_named', {
      event_category: 'funnel',
      event_label: aiName || 'unknown',
      value: 1
    });
    /* Tag Clarity session with AI name for filtering recordings */
    if (window.clarity) {
      window.clarity('set', 'ai_name', aiName || 'unknown');
    }
    log('Funnel: ai_named —', aiName);
  };

  /**
   * Event 3 — User proceeds past the celebration screen to see pricing.
   * Call when the pricing section becomes visible after naming.
   *
   * @param {string} aiName  The AI's name (for segmentation).
   */
  window.trackPricingRevealed = function (aiName) {
    fireEvent('pricing_revealed', {
      event_category: 'funnel',
      event_label: aiName || 'unknown'
    });
    log('Funnel: pricing_revealed —', aiName);
  };

  /**
   * Event 4 — User clicks a specific pricing tier.
   * Call on pricing CTA click, before redirecting to payment.
   *
   * @param {string} tierName   e.g. "Awakened", "Bonded", "Partnered"
   * @param {number} tierPrice  Numeric price in USD, e.g. 79
   */
  window.trackTierSelected = function (tierName, tierPrice) {
    fireEvent('tier_selected', {
      event_category: 'conversion',
      event_label: tierName || 'unknown',
      value: tierPrice || 0
    });
    log('Funnel: tier_selected —', tierName, tierPrice);
  };

  /**
   * Event 5 — Form or payment submitted (conversion complete).
   * Call on successful form / PayPal submission.
   *
   * @param {string} tierName   e.g. "Awakened"
   * @param {number} tierPrice  Numeric price in USD
   */
  window.trackConversion = function (tierName, tierPrice) {
    fireEvent('purchase', {
      event_category: 'conversion',
      event_label: tierName || 'unknown',
      value: tierPrice || 0,
      currency: 'USD'
    });
    /* Also send GA4 native purchase event for e-commerce reports */
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'purchase', {
        transaction_id: 'pb-' + Date.now(),
        value: tierPrice || 0,
        currency: 'USD',
        items: [{
          item_id: 'PB-' + (tierName || 'unknown').toUpperCase(),
          item_name: 'PureBrain ' + (tierName || 'unknown'),
          price: tierPrice || 0,
          quantity: 1
        }]
      });
    }
    log('Funnel: purchase —', tierName, tierPrice);
  };


  /* ============================================================
     SECTION 3: SCROLL DEPTH TRACKING
     Observes when each key section enters the viewport for the
     first time and fires a scroll_depth event.
     ============================================================ */
  function initScrollTracking() {
    /* Prefer IntersectionObserver (modern) with a percentage fallback */
    if (!window.IntersectionObserver) {
      initScrollTrackingFallback();
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var sectionLabel = entry.target.getAttribute('data-pb-scroll-label');
          var sectionDepth = entry.target.getAttribute('data-pb-scroll-depth');
          once('scroll_' + sectionLabel, function () {
            fireEvent('scroll_depth', {
              event_category: 'engagement',
              section: sectionLabel,
              depth_percent: parseInt(sectionDepth, 10) || 0
            });
            log('Scroll depth:', sectionLabel, sectionDepth + '%');
          });
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.25 } /* Fire when 25 % of the section is visible */
    );

    CONFIG.SCROLL_SECTIONS.forEach(function (section) {
      /* Try each comma-separated selector — use the first matching element */
      var selectors = section.selector.split(',').map(function (s) { return s.trim(); });
      var el = null;
      for (var i = 0; i < selectors.length; i++) {
        el = document.querySelector(selectors[i]);
        if (el) break;
      }
      if (!el) {
        log('Scroll section not found:', section.selector);
        return;
      }
      el.setAttribute('data-pb-scroll-label', section.label);
      el.setAttribute('data-pb-scroll-depth', section.depth);
      observer.observe(el);
    });
  }

  /** Fallback scroll tracking for browsers without IntersectionObserver. */
  function initScrollTrackingFallback() {
    var sections = CONFIG.SCROLL_SECTIONS.map(function (section) {
      var selectors = section.selector.split(',').map(function (s) { return s.trim(); });
      var el = null;
      for (var i = 0; i < selectors.length; i++) {
        el = document.querySelector(selectors[i]);
        if (el) break;
      }
      return { el: el, label: section.label, depth: section.depth, fired: false };
    }).filter(function (s) { return s.el; });

    function checkScroll() {
      var windowBottom = window.scrollY + window.innerHeight;
      sections.forEach(function (section) {
        if (section.fired) return;
        var rect = section.el.getBoundingClientRect();
        var elTop = rect.top + window.scrollY;
        if (windowBottom >= elTop + (rect.height * 0.25)) {
          section.fired = true;
          once('scroll_' + section.label, function () {
            fireEvent('scroll_depth', {
              event_category: 'engagement',
              section: section.label,
              depth_percent: section.depth
            });
            log('Scroll depth (fallback):', section.label, section.depth + '%');
          });
        }
      });
    }

    window.addEventListener('scroll', checkScroll, { passive: true });
    checkScroll(); /* Check initial position (above-the-fold sections) */
  }


  /* ============================================================
     SECTION 4: CTA CLICK TRACKING
     Listens for clicks on all CTA buttons and records which button
     was clicked, its text, location (hero / pricing / footer), and
     the timestamp.
     ============================================================ */
  function initCTATracking() {
    document.addEventListener('click', function (e) {
      /* Walk up the DOM to find a matching CTA element */
      var target = e.target;
      var ctaEl = null;

      /* Check target and up to 3 ancestors */
      for (var depth = 0; depth < 4; depth++) {
        if (!target || target === document.documentElement) break;
        if (matchesSelector(target, CONFIG.CTA_SELECTOR)) {
          ctaEl = target;
          break;
        }
        target = target.parentElement;
      }

      if (!ctaEl) return;

      var buttonText = (ctaEl.textContent || ctaEl.innerText || '').trim().substring(0, 80);
      var location = inferCTALocation(ctaEl);
      var timestamp = new Date().toISOString();

      fireEvent('cta_click', {
        event_category: 'engagement',
        button_text: buttonText,
        button_location: location,
        timestamp: timestamp
      });
      log('CTA click:', buttonText, '|', location);
    });
  }

  /** Determine which section a CTA button lives in. */
  function inferCTALocation(el) {
    var locationMaps = CONFIG.CTA_LOCATION_MAP;
    for (var j = 0; j < locationMaps.length; j++) {
      var map = locationMaps[j];
      var selectors = map.selector.split(',').map(function (s) { return s.trim(); });
      for (var k = 0; k < selectors.length; k++) {
        if (closest(el, selectors[k])) {
          return map.label;
        }
      }
    }
    return 'other';
  }


  /* ============================================================
     SECTION 5: DEMO VIDEO ENGAGEMENT
     Attaches to the first <video> element matching VIDEO_SELECTOR
     and tracks: play, unmute, 25%, 50%, complete milestones.
     ============================================================ */
  function initVideoTracking() {
    var selectors = CONFIG.VIDEO_SELECTOR.split(',').map(function (s) { return s.trim(); });
    var video = null;
    for (var i = 0; i < selectors.length; i++) {
      video = document.querySelector(selectors[i]);
      if (video) break;
    }

    if (!video) {
      log('Demo video element not found — skipping video tracking');
      return;
    }

    log('Video tracking attached to:', video.id || video.className || 'unnamed <video>');

    /* Track: play_demo — first play only */
    video.addEventListener('play', function () {
      once('video_play', function () {
        fireEvent('play_demo', {
          event_category: 'engagement',
          event_label: 'demo_video'
        });
        log('Video: play_demo');
      });
    });

    /* Track: unmute_demo — when user removes mute */
    video.addEventListener('volumechange', function () {
      if (!video.muted) {
        once('video_unmute', function () {
          fireEvent('unmute_demo', {
            event_category: 'engagement',
            event_label: 'demo_video'
          });
          log('Video: unmute_demo');
        });
      }
    });

    /* Track: timeupdate — fire at 25%, 50%, and complete */
    var quartileFired = { 25: false, 50: false, 100: false };

    video.addEventListener('timeupdate', function () {
      if (!video.duration || video.duration === 0) return;
      var pct = (video.currentTime / video.duration) * 100;

      if (!quartileFired[25] && pct >= 25) {
        quartileFired[25] = true;
        fireEvent('demo_25_percent', {
          event_category: 'engagement',
          event_label: 'demo_video',
          value: 25
        });
        log('Video: demo_25_percent');
      }
      if (!quartileFired[50] && pct >= 50) {
        quartileFired[50] = true;
        fireEvent('demo_50_percent', {
          event_category: 'engagement',
          event_label: 'demo_video',
          value: 50
        });
        log('Video: demo_50_percent');
      }
    });

    video.addEventListener('ended', function () {
      once('video_complete', function () {
        fireEvent('demo_complete', {
          event_category: 'engagement',
          event_label: 'demo_video',
          value: 100
        });
        log('Video: demo_complete');
      });
    });
  }


  /* ============================================================
     SECTION 6: EXIT INTENT TRACKING
     Desktop: mouse leaves viewport from the top edge.
     Mobile: page visibility changes (tab switch / app close).
     The overlay must have id="pb-exit-modal" and contain:
       [data-pb-exit="stay"]  — "Stay" button
       [data-pb-exit="leave"] — "Leave" button (or close X)
     ============================================================ */
  function initExitIntent() {
    var exitIntentFired = false;

    function onExitIntent() {
      if (exitIntentFired) return;
      exitIntentFired = true;

      fireEvent('exit_intent_shown', {
        event_category: 'engagement',
        event_label: 'exit_intent'
      });
      log('Exit intent: shown');

      /* Show the modal */
      var modal = document.getElementById('pb-exit-modal');
      if (modal) {
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
      }

      /* Wire up stay / leave buttons if the modal is present */
      if (modal) {
        var stayBtn  = modal.querySelector('[data-pb-exit="stay"]');
        var leaveBtn = modal.querySelector('[data-pb-exit="leave"]');

        if (stayBtn) {
          stayBtn.addEventListener('click', function () {
            fireEvent('exit_intent_stay', {
              event_category: 'engagement',
              event_label: 'exit_intent'
            });
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            log('Exit intent: stay');
          }, { once: true });
        }

        if (leaveBtn) {
          leaveBtn.addEventListener('click', function () {
            fireEvent('exit_intent_leave', {
              event_category: 'engagement',
              event_label: 'exit_intent'
            });
            log('Exit intent: leave');
          }, { once: true });
        }
      }
    }

    /* --- Desktop: mouse leaves viewport from top --- */
    document.addEventListener('mouseleave', function (e) {
      if (e.clientY <= 15) {
        onExitIntent();
      }
    });

    /* --- Mobile: user switches tabs or presses home --- */
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') {
        onExitIntent();
      }
    });

    /* --- Mobile: back button / page hide --- */
    window.addEventListener('pagehide', function () {
      onExitIntent();
    });
  }


  /* ============================================================
     SECTION 7: SESSION DURATION & ENGAGEMENT
     Fires a time_on_page event every 30 seconds up to 5 minutes.
     Uses beforeunload to capture total time when the user leaves.
     ============================================================ */
  function initSessionTracking() {
    var pageStartTime = Date.now();
    var elapsed = 0;                       /* Seconds elapsed so far */
    var maxSeconds = CONFIG.SESSION_MAX_SECONDS;
    var intervalMs = CONFIG.SESSION_HEARTBEAT_MS;

    var heartbeat = setInterval(function () {
      elapsed += intervalMs / 1000;

      fireEvent('time_on_page', {
        event_category: 'engagement',
        seconds_on_page: elapsed,
        event_label: elapsed + 's'
      });
      log('Session heartbeat:', elapsed + 's');

      if (elapsed >= maxSeconds) {
        clearInterval(heartbeat);
        log('Session tracking cap reached:', maxSeconds + 's');
      }
    }, intervalMs);

    /* Fire a final event on page unload with total time */
    window.addEventListener('beforeunload', function () {
      var totalSeconds = Math.round((Date.now() - pageStartTime) / 1000);
      /* Use navigator.sendBeacon for reliability on page unload */
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'session_end', {
          event_category: 'engagement',
          total_seconds: totalSeconds,
          non_interaction: true
        });
      }
      pushDataLayer('session_end', {
        total_seconds: totalSeconds,
        non_interaction: true
      });
      log('Session end — total time:', totalSeconds + 's');
    });
  }


  /* ============================================================
     SECTION 8: GTM DATA LAYER
     Every event is also pushed to dataLayer so GTM triggers can
     react to it (e.g. re-fire to Facebook Pixel, LinkedIn Insight,
     custom webhook, etc.).
     ============================================================ */
  function pushDataLayer(eventName, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign(
      { event: eventName },
      params || {}
    ));
    log('dataLayer push:', eventName);
  }


  /* ============================================================
     INITIALISATION
     Everything runs after the DOM is ready. If this script is
     loaded in the <head> we wait for DOMContentLoaded; if loaded
     at the bottom of <body> we run immediately.
     ============================================================ */
  function init() {
    log('Initialising PureBrain Analytics — GA4:', CONFIG.GA4_MEASUREMENT_ID,
        '| Clarity:', CONFIG.CLARITY_PROJECT_ID);

    initGA4();
    initClarity();
    initScrollTracking();
    initCTATracking();
    initVideoTracking();
    initExitIntent();
    initSessionTracking();

    /* Fire a page_loaded event so GTM / Clarity can confirm the
       analytics script itself loaded successfully */
    fireEvent('analytics_ready', {
      event_category: 'system',
      ga4_id: CONFIG.GA4_MEASUREMENT_ID,
      clarity_id: CONFIG.CLARITY_PROJECT_ID
    });

    log('PureBrain Analytics ready.');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})(window, document);


/* ============================================================
   QUICK-REFERENCE: HOW TO CALL FUNNEL EVENTS
   ============================================================

   Paste these calls into your chat / UI code at the right moments:

   // 1. When user clicks "Begin Awakening" / sends first message
   window.trackAwakeningStart();

   // 2. When the AI declares its name in the conversation
   window.trackAINamed('Aria');          // pass the chosen name

   // 3. When pricing section appears after the celebration screen
   window.trackPricingRevealed('Aria');

   // 4. When user clicks a pricing tier button
   window.trackTierSelected('Awakened', 79);
   window.trackTierSelected('Bonded',   149);
   window.trackTierSelected('Partnered', 499);

   // 5. When payment / form is successfully submitted
   window.trackConversion('Awakened', 79);

   ============================================================
   EXIT INTENT MODAL: REQUIRED HTML STRUCTURE
   ============================================================

   <div id="pb-exit-modal" style="display:none;" aria-hidden="true" role="dialog">
     <!-- your modal content here -->
     <button data-pb-exit="stay">Stay and Explore</button>
     <button data-pb-exit="leave">No thanks, I'll leave</button>
   </div>

   ============================================================
   DEMO VIDEO: REQUIRED HTML STRUCTURE
   ============================================================

   <video id="pb-demo-video" ...>
     <source src="demo.mp4" type="video/mp4">
   </video>

   ============================================================ */

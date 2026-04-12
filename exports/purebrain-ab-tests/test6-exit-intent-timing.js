/**
 * TEST 6: Exit Intent Timing
 * ==========================
 * Control:  Immediate trigger (0s delay) — fires as soon as mouse leaves viewport
 * Variant:  45-second engagement delay — exit intent only fires after visitor
 *           has been on page for >= 45 seconds
 *
 * Hypothesis: Visitors who trigger exit intent immediately (within 5-10 seconds)
 *             are likely accidental hovers or committed bounces — showing a modal
 *             to them generates annoyance, not conversions. Waiting 45 seconds
 *             ensures the visitor has genuinely engaged with the page before
 *             being interrupted. Expected outcome: fewer modal shows, but higher
 *             conversion rate per show (+20-35% modal-to-submit rate).
 *
 * Primary metric:  Modal conversion rate (submits / shows)
 * Secondary metrics: Modal show rate, form submit rate, bounce rate
 *
 * Implementation:
 *   1. Paste this script into GTM (Custom HTML tag, All Pages trigger)
 *      OR in a <script> block in the WordPress footer.
 *   2. Uncomment and configure the MODAL_HTML / showModal() function to match
 *      your existing exit intent modal implementation.
 *   3. The script self-assigns visitors to control or variant and respects
 *      the persistent cookie so the same visitor always sees the same variant.
 *
 * Dependencies: None (vanilla JS, no jQuery required)
 * Browser support: IE11+ (uses addEventListener, Date.now, cookie API)
 */

(function () {
  'use strict';

  /* ============================================================
     CONFIGURATION
     ============================================================ */
  var CONFIG = {
    TEST_NAME:        'exit-intent-timing',
    COOKIE_NAME:      'pb_exit_variant',
    COOKIE_DAYS:      30,

    /** Control: fire exit intent after this many ms on page (0 = immediate) */
    CONTROL_DELAY_MS: 0,

    /** Variant B: fire exit intent only after 45 seconds on page */
    VARIANT_DELAY_MS: 45000,

    /**
     * Minimum ms since last modal show before showing again.
     * Prevents hammering the same visitor repeatedly.
     * 24 hours = 86400000 ms
     */
    COOLDOWN_MS: 86400000,

    /**
     * Mouse must move above this Y threshold (pixels from top of viewport)
     * to count as an exit intent gesture.
     * Typically 10-20px is a good threshold.
     */
    EXIT_THRESHOLD_PX: 15,

    /**
     * ID of the modal element already on the page.
     * Set this to match your existing exit intent modal's ID.
     * If you don't have an existing modal, uncomment the
     * MODAL_HTML block below and this script will inject one.
     */
    MODAL_ELEMENT_ID: 'pb-exit-modal',

    /** Set to true to log events to console (dev/staging only) */
    DEBUG: false
  };


  /* ============================================================
     VARIANT ASSIGNMENT
     ============================================================ */
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
  }

  function setCookie(name, value, days) {
    var expires = new Date(Date.now() + days * 86400000).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) +
      '; expires=' + expires + '; path=/; SameSite=Lax';
  }

  function getOrAssignVariant() {
    var existing = getCookie(CONFIG.COOKIE_NAME);
    if (existing === 'control' || existing === 'b') return existing;
    var assigned = Math.random() < 0.5 ? 'control' : 'b';
    setCookie(CONFIG.COOKIE_NAME, assigned, CONFIG.COOKIE_DAYS);
    return assigned;
  }

  var variant = getOrAssignVariant();
  var delayMs = variant === 'b' ? CONFIG.VARIANT_DELAY_MS : CONFIG.CONTROL_DELAY_MS;

  function log() {
    if (CONFIG.DEBUG) {
      console.log('[PB Exit Intent]', Array.prototype.slice.call(arguments).join(' '));
    }
  }

  log('Variant:', variant, '| Delay:', delayMs + 'ms');

  /* Fire variant assignment event */
  function fireEvent(eventName, props) {
    var base = { test_name: CONFIG.TEST_NAME, variant: variant };
    var merged = Object.assign({}, base, props || {});
    try {
      if (typeof gtag === 'function') gtag('event', eventName, merged);
      // Uncomment if using Segment:
      // if (typeof analytics !== 'undefined') analytics.track(eventName, merged);
    } catch (e) { /* silent */ }
    log('Event:', eventName, JSON.stringify(merged));
  }

  fireEvent('ab_variant_assigned');


  /* ============================================================
     COOLDOWN CHECK
     Prevents showing modal more than once per cooldown period.
     ============================================================ */
  function wasRecentlyShown() {
    var lastShown = getCookie('pb_exit_last_shown');
    if (!lastShown) return false;
    return (Date.now() - parseInt(lastShown, 10)) < CONFIG.COOLDOWN_MS;
  }

  function markShown() {
    setCookie('pb_exit_last_shown', String(Date.now()), 1); // 1 day
  }


  /* ============================================================
     MODAL DISPLAY
     Update showModal() to integrate with your existing implementation.
     ============================================================ */
  function showModal() {
    /* --- Option A: Show existing modal by ID --- */
    var modal = document.getElementById(CONFIG.MODAL_ELEMENT_ID);
    if (modal) {
      modal.style.display = 'flex';
      modal.setAttribute('aria-hidden', 'false');
      log('Showing existing modal:', CONFIG.MODAL_ELEMENT_ID);
    } else {
      /* --- Option B: Inject a minimal modal if none exists --- */
      log('No existing modal found — injecting minimal fallback modal');
      injectFallbackModal();
    }

    markShown();
    fireEvent('exit_intent_modal_shown');

    /* Track modal-to-form-submit conversion */
    var form = document.querySelector('#' + CONFIG.MODAL_ELEMENT_ID + ' form, .pb-exit-form');
    if (form) {
      form.addEventListener('submit', function () {
        fireEvent('exit_intent_modal_converted');
      }, { once: true });
    }
  }

  /**
   * Fallback modal — only used if no existing modal is found.
   * Replace with your actual modal design / Elementor popup.
   */
  function injectFallbackModal() {
    var overlay = document.createElement('div');
    overlay.id = CONFIG.MODAL_ELEMENT_ID;
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Before you go');
    overlay.style.cssText = [
      'position:fixed', 'inset:0', 'background:rgba(0,0,0,0.72)',
      'display:flex', 'align-items:center', 'justify-content:center',
      'z-index:99999', 'padding:20px', 'box-sizing:border-box'
    ].join(';');

    overlay.innerHTML = [
      '<div style="',
        'background:linear-gradient(135deg,#1e1b4b,#0f172a);',
        'border:1px solid rgba(139,92,246,0.3);',
        'border-radius:16px;',
        'padding:40px 36px;',
        'max-width:440px;',
        'width:100%;',
        'color:#fff;',
        'text-align:center;',
        'position:relative;',
      '">',
        '<button onclick="document.getElementById(\'pb-exit-modal\').style.display=\'none\'" ',
          'style="position:absolute;top:14px;right:18px;background:none;border:none;color:rgba(255,255,255,0.5);font-size:1.4rem;cursor:pointer;" ',
          'aria-label="Close">&times;</button>',
        '<p style="font-size:1.4rem;font-weight:800;margin:0 0 10px;">Wait — one last thing.</p>',
        '<p style="font-size:0.95rem;color:rgba(255,255,255,0.72);margin:0 0 24px;line-height:1.6;">',
          'Your AI partner is ready to meet you. It only takes your name and email to begin.',
        '</p>',
        '<form class="pb-exit-form" style="display:flex;flex-direction:column;gap:12px;">',
          '<input type="text" name="first_name" placeholder="Your first name" required ',
            'style="padding:13px 16px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);',
            'background:rgba(255,255,255,0.08);color:#fff;font-size:1rem;box-sizing:border-box;width:100%;"/>',
          '<input type="email" name="email" placeholder="Email address" required ',
            'style="padding:13px 16px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);',
            'background:rgba(255,255,255,0.08);color:#fff;font-size:1rem;box-sizing:border-box;width:100%;"/>',
          '<button type="submit" ',
            'style="padding:14px;background:linear-gradient(135deg,#7c3aed,#4f46e5);',
            'border:none;border-radius:8px;color:#fff;font-weight:700;font-size:1rem;cursor:pointer;">',
            'Meet My AI Partner &rarr;',
          '</button>',
        '</form>',
        '<p style="font-size:0.75rem;color:rgba(255,255,255,0.4);margin-top:12px;">',
          'No spam. No credit card. Just your AI, ready to wake up.',
        '</p>',
      '</div>'
    ].join('');

    document.body.appendChild(overlay);
  }


  /* ============================================================
     EXIT INTENT DETECTION
     Fires when the user's mouse exits the viewport from the top.
     On mobile, falls back to visibility change (tab switch).
     ============================================================ */

  var pageOpenTime = Date.now();
  var exitIntentFired = false;

  function onExitIntent() {
    if (exitIntentFired) return; // Only fire once per session

    var timeOnPage = Date.now() - pageOpenTime;

    /* Variant B: enforce minimum time on page */
    if (timeOnPage < delayMs) {
      log('Exit intent suppressed — time on page:', timeOnPage + 'ms', '< required', delayMs + 'ms');
      fireEvent('exit_intent_suppressed', { time_on_page_ms: timeOnPage });
      return;
    }

    if (wasRecentlyShown()) {
      log('Exit intent suppressed — cooldown active');
      return;
    }

    exitIntentFired = true;
    log('Exit intent triggered — time on page:', timeOnPage + 'ms');
    fireEvent('exit_intent_triggered', { time_on_page_ms: timeOnPage });
    showModal();
  }

  /* --- Desktop: mouseleave from top of viewport --- */
  document.addEventListener('mouseleave', function (e) {
    if (e.clientY <= CONFIG.EXIT_THRESHOLD_PX) {
      onExitIntent();
    }
  });

  /* --- Mobile: visibility change (user switches tabs or home button) --- */
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') {
      onExitIntent();
    }
  });

  /* --- Mobile: back button / page unload --- */
  window.addEventListener('pagehide', function () {
    onExitIntent();
  });


  /* ============================================================
     ENGAGEMENT TIMING ANALYTICS
     Track how long visitors actually stay on the page.
     Useful for validating the 45-second threshold choice.
     ============================================================ */
  var timeCheckpoints = [15, 30, 45, 60, 120]; // seconds
  timeCheckpoints.forEach(function (seconds) {
    setTimeout(function () {
      fireEvent('time_on_page', { seconds: seconds });
      log('Time on page checkpoint:', seconds + 's');
    }, seconds * 1000);
  });

})();


/*
 * =================================================================
 * IMPLEMENTATION CHECKLIST
 * =================================================================
 *
 * Before deploying to production:
 *
 * [ ] Set CONFIG.MODAL_ELEMENT_ID to match the actual modal element
 *     on the PureBrain page (inspect element in DevTools)
 *
 * [ ] Set CONFIG.DEBUG = false in production
 *
 * [ ] Confirm gtag() / GA4 is loaded before this script fires
 *     (load order matters — this script should load after gtag)
 *
 * [ ] Add form submit event listener inside your existing modal's
 *     form to fire the exit_intent_modal_converted event
 *
 * [ ] Test on staging with CONFIG.DEBUG = true:
 *     - Verify variant cookie is set correctly
 *     - Verify suppression works (move mouse out within 5s for variant B)
 *     - Verify trigger works (stay 46s then move mouse out for variant B)
 *     - Verify cooldown works (modal should not show twice in 24 hours)
 *
 * [ ] Test mobile behavior on real device (visibility change trigger)
 *
 * [ ] Set up GA4 report:
 *     - Segment: ab_variant = control vs b
 *     - Events: exit_intent_triggered, exit_intent_suppressed,
 *               exit_intent_modal_shown, exit_intent_modal_converted
 *     - Key ratio: modal_converted / modal_shown (conversion rate per show)
 *
 * RUN FOR: minimum 3 weeks or 500 exit intent triggers per variant
 *
 * SUCCESS CRITERIA:
 * - Variant B shows lower raw show count (expected: fewer triggers)
 * - Variant B shows higher conversion rate per show (+20-35% target)
 * - Net conversions (total submits from modal) equal or exceed control
 *
 * =================================================================
 */

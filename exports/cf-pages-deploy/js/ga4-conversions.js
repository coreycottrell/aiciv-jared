/* ga4-conversions.js
 * Purpose: Fire GA4 conversion events via direct gtag() calls.
 * The gtag snippet is already loaded on all pages via GTM-WTDXL4VJ.
 *
 * Events:
 *   - form_submit  : any <form> successful submit across site
 *   - sign_up      : thank-you page landing (post-payment)
 *   - purchase     : PayPal payment confirmed (wired from payment-glue.js)
 *   - begin_checkout : pricing tier reveal / payment page load
 *   - chat_open    : homepage chatbox first opened
 *
 * Updated: 2026-04-23 — replaced dataLayer.push() with direct gtag('event',...)
 * so events reach GA4 without needing separate GTM Event Tags.
 */
(function () {
  'use strict';

  // Ensure gtag is available (loaded by GTM snippet)
  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== 'function') {
    window.gtag = function () { window.dataLayer.push(arguments); };
  }

  var TIER_VALUES = {
    Awakened:  149.00,
    Bonded:    299.00,
    Partnered: 499.00,
    Unified:   999.00,
    Insiders:   74.60
  };

  function emailDomain(email) {
    if (!email || typeof email !== 'string') return '';
    var at = email.indexOf('@');
    return at > -1 ? email.slice(at + 1).toLowerCase() : '';
  }

  function fireEvent(eventName, params) {
    try {
      var clean = {};
      if (params) {
        for (var k in params) {
          if (Object.prototype.hasOwnProperty.call(params, k) && params[k] !== undefined) {
            clean[k] = params[k];
          }
        }
      }
      gtag('event', eventName, clean);
      if (window.console && console.debug) {
        console.debug('[ga4] ' + eventName, clean);
      }
    } catch (e) {
      if (window.console) console.warn('[ga4] event failed', e);
    }
  }

  // ============================================================
  //  1. form_submit — global form listener
  // ============================================================
  document.addEventListener('submit', function (ev) {
    try {
      var form = ev.target;
      if (!form || form.tagName !== 'FORM') return;
      if (form.id === 'pb-paypal-form' || form.action && /paypal\.com/.test(form.action)) return;

      var emailField = form.querySelector('input[type="email"]');
      var email = emailField ? emailField.value : '';

      fireEvent('form_submit', {
        form_id: form.id || '',
        form_name: form.getAttribute('name') || form.id || '',
        form_location: window.location.pathname,
        email_domain: emailDomain(email)
      });
    } catch (e) { /* silent */ }
  }, true);

  // ============================================================
  //  2. sign_up — fires on thank-you page load
  // ============================================================
  function checkSignUp() {
    if (!/\/thank-you\/?$/.test(window.location.pathname)) return;
    var params = new URLSearchParams(window.location.search);
    var tier = params.get('tier') || '';
    if (!tier) return;

    if (window._ga4SignUpFired) return;
    window._ga4SignUpFired = true;

    var refCode = '';
    try {
      if (typeof window.getPbRef === 'function') refCode = window.getPbRef() || '';
    } catch (_) {}
    if (!refCode) {
      try { refCode = localStorage.getItem('pb_ref') || ''; } catch (_) {}
    }

    fireEvent('sign_up', {
      method: 'paypal',
      tier_name: tier,
      referral_code: refCode || undefined
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkSignUp);
  } else {
    checkSignUp();
  }

  // ============================================================
  //  3. purchase — exposed as window.ga4TrackPurchase
  //  Called from payment-glue.js inside onPaymentComplete
  // ============================================================
  window.ga4TrackPurchase = function (tier, orderId, payerInfo) {
    try {
      var value = TIER_VALUES[tier] || 0;
      var email = (payerInfo && payerInfo.email_address) || '';
      var refCode = '';
      try {
        if (typeof window.getPbRef === 'function') refCode = window.getPbRef() || '';
      } catch (_) {}

      fireEvent('purchase', {
        transaction_id: orderId || '',
        value: value,
        currency: 'USD',
        tier: tier || '',
        email_domain: emailDomain(email),
        referral_code: refCode || undefined,
        items: [{
          item_id: 'tier_' + (tier || 'unknown').toLowerCase(),
          item_name: tier || 'unknown',
          item_category: 'subscription',
          price: value,
          quantity: 1
        }]
      });
    } catch (e) { /* silent */ }
  };

  // ============================================================
  //  4. begin_checkout — fires on payment/pricing page load
  //  Detects pages with tier selection or payment forms
  // ============================================================
  function checkBeginCheckout() {
    var path = window.location.pathname;
    // Fire on payment tier pages: /awakened/, /partnered/, /unified/
    if (/^\/(awakened|partnered|unified|insiders|bonded)\/?$/.test(path)) {
      var tierMatch = path.match(/^\/(awakened|partnered|unified|insiders|bonded)\/?$/);
      var tierName = tierMatch ? tierMatch[1].charAt(0).toUpperCase() + tierMatch[1].slice(1) : '';
      var tierValue = TIER_VALUES[tierName] || 0;
      fireEvent('begin_checkout', {
        currency: 'USD',
        value: tierValue,
        tier: tierName,
        page_location: path
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkBeginCheckout);
  } else {
    checkBeginCheckout();
  }

  // ============================================================
  //  5. chat_open — exposed as window.ga4TrackChatOpen
  //  Called once from homepage-chat.js startConversation()
  // ============================================================
  window.ga4TrackChatOpen = function (sourcePage) {
    if (window._ga4ChatOpenFired) return;
    window._ga4ChatOpenFired = true;
    fireEvent('chat_open', {
      source_page: sourcePage || window.location.pathname
    });
  };

})();

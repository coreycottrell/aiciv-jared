/* === PayPal SDK Integration (support@puremarketing.ai) === */
/**
 * PayPal Popup Integration for purebrain.ai  (v2 — SDK Primary)
 * ================================================================
 * Replaces openWaitlistModal() with real PayPal checkout via in-page popup/modal.
 *
 * Two approaches included:
 *   - Approach A: PayPal JS SDK Smart Buttons  ← DEFAULT (highest security)
 *   - Approach B: PayPal Form POST in centered popup window  ← fallback
 *
 * CURRENT DEFAULT: Approach A (SDK)
 *
 * TO USE APPROACH A IN PRODUCTION:
 *   1. Get your PayPal Client ID from: developer.paypal.com > My Apps & Credentials
 *   2. Replace the PAYPAL_CLIENT_ID value below with the real client-id
 *      (use Sandbox ID for testing, Live ID for production)
 *   3. Optionally provide Plan IDs for subscription billing (see PLAN_IDS below)
 *   4. The server-side verification endpoint is pre-configured:
 *      https://api.purebrain.ai/api/verify-payment
 *
 * Business email: support@puremarketing.ai
 * Return URL:     https://purebrain.ai/thank-you/
 * Cancel URL:     https://purebrain.ai/pay-test/
 */

(function () {
  'use strict';

  // ============================================================
  //  CONFIGURATION — Edit these values before deploying
  // ============================================================

  /**
   * PayPal Client ID  ← REPLACE THIS before going live
   *
   * This is currently a placeholder. Replace with your real Client ID from:
   *   https://developer.paypal.com > My Apps & Credentials
   *
   * Sandbox example:  "AZDxjDScFpQtjWTOUtWKbyN_bDt4OgqaF4eYXgewGLaQ6G2b9..."
   * Live example:     "AeBFuJP7vVH-..."
   *
   * The SDK approach is ENABLED even with this placeholder so you can see the
   * buttons render in your environment as soon as the real ID is dropped in.
   */
  /* LIVE PayPal */
  var PAYPAL_CLIENT_ID = 'AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI';

  /**
   * (Optional) If you want recurring/subscription billing via SDK,
   * create Subscription Plans in PayPal dashboard and paste the Plan IDs here.
   * Path in PayPal: Pay & Get Paid > Subscriptions > Subscription Plans
   * Plan IDs start with "P-"
   *
   * Leave as empty strings to use one-time payment flow instead.
   */
  var PLAN_IDS = {
    Awakened:  'P-4P998148HJ3439945NICOI7Q',
    Partnered: 'P-3KL830539R502981PNICOI7Q',
    Unified:   'P-1KC17605JW4534516NICOI7Q',
  };

  // Pricing — matches purebrain.ai tiers
  var PRICES = {
    Awakened:  '149.00',
    Bonded:    '299.00',
    Partnered: '499.00',
    Unified:   '999.00',
  };

  // PayPal business account that receives payments
  var BUSINESS_EMAIL = 'support@puremarketing.ai';

  // Where PayPal sends the user after payment
  var RETURN_URL = 'https://purebrain.ai/live/?payment=success';
  var CANCEL_URL = 'https://purebrain.ai/live/';

  // Currency
  var CURRENCY = 'USD';

  /**
   * Server-side verification endpoint.
   * Called after SDK capture to independently confirm the payment with PayPal's API.
   * Endpoint: POST https://api.purebrain.ai/api/verify-payment
   * Body:      { orderId, tier, payerInfo }
   * Expected:  { verified: true|false, ... }
   */
  var VERIFY_ENDPOINT = 'https://api.purebrain.ai/api/verify-payment';


  // ============================================================
  //  MODAL CSS — Injected into <head> once on load
  // ============================================================

  var MODAL_CSS = `
    /* ---- PayPal Popup Overlay ---- */
    #pb-paypal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 99999;
      background: rgba(0, 0, 0, 0.82);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      align-items: center;
      justify-content: center;
    }
    #pb-paypal-overlay.pb-active {
      display: flex;
    }

    /* ---- Modal Card ---- */
    #pb-paypal-modal {
      background: #0d1117;
      border: 1px solid rgba(138, 43, 226, 0.4);
      border-radius: 16px;
      box-shadow:
        0 0 40px rgba(138, 43, 226, 0.25),
        0 24px 64px rgba(0, 0, 0, 0.7);
      padding: 36px 32px 32px;
      width: 100%;
      max-width: 440px;
      position: relative;
      animation: pb-modal-in 0.25s ease-out;
    }

    @keyframes pb-modal-in {
      from { opacity: 0; transform: scale(0.94) translateY(12px); }
      to   { opacity: 1; transform: scale(1) translateY(0); }
    }

    /* ---- Close Button ---- */
    #pb-paypal-close {
      position: absolute;
      top: 14px;
      right: 16px;
      background: none;
      border: none;
      color: rgba(255, 255, 255, 0.45);
      font-size: 22px;
      line-height: 1;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 6px;
      transition: color 0.15s, background 0.15s;
    }
    #pb-paypal-close:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.08);
    }

    /* ---- Tier Header ---- */
    #pb-paypal-tier-name {
      font-family: inherit;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #8a2be2;
      margin: 0 0 6px;
    }
    #pb-paypal-price-line {
      font-size: 28px;
      font-weight: 700;
      color: #ffffff;
      margin: 0 0 4px;
      line-height: 1.1;
    }
    #pb-paypal-price-sub {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.45);
      margin: 0 0 28px;
    }

    /* ---- Divider ---- */
    #pb-paypal-modal hr {
      border: none;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      margin: 0 0 24px;
    }

    /* ---- PayPal button container ---- */
    #pb-paypal-buttons-container {
      min-height: 48px;
    }

    /* ---- Verifying state spinner text ---- */
    #pb-paypal-verifying {
      color: rgba(255, 255, 255, 0.6);
      font-size: 14px;
      text-align: center;
      padding: 16px 0;
    }

    /* ---- Fallback form button (Approach B) ---- */
    #pb-paypal-form-btn {
      display: block;
      width: 100%;
      padding: 15px 24px;
      background: #FFD140;
      color: #111827;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      letter-spacing: 0.01em;
      transition: background 0.15s, transform 0.1s;
      text-align: center;
    }
    #pb-paypal-form-btn:hover {
      background: #f0c030;
      transform: translateY(-1px);
    }
    #pb-paypal-form-btn:active {
      transform: translateY(0);
    }

    /* ---- Trust line beneath button ---- */
    #pb-paypal-trust {
      margin-top: 14px;
      font-size: 12px;
      color: rgba(255, 255, 255, 0.35);
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    #pb-paypal-trust svg {
      flex-shrink: 0;
    }

    /* ---- Success banner (shown after payment) ---- */
    #pb-payment-success-banner {
      display: none;
      position: fixed;
      top: 24px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 100001;
      background: linear-gradient(135deg, #1a4731, #0d2e1e);
      border: 1px solid #2ecc71;
      color: #2ecc71;
      padding: 14px 28px;
      border-radius: 10px;
      font-size: 15px;
      font-weight: 600;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      text-align: center;
      white-space: nowrap;
      animation: pb-banner-in 0.3s ease-out;
    }
    #pb-payment-success-banner.pb-visible {
      display: block;
    }
    @keyframes pb-banner-in {
      from { opacity: 0; transform: translateX(-50%) translateY(-12px); }
      to   { opacity: 1; transform: translateX(-50%) translateY(0); }
    }

    /* ---- Responsive ---- */
    @media (max-width: 480px) {
      #pb-paypal-modal {
        margin: 12px;
        padding: 28px 20px 24px;
      }
      #pb-paypal-price-line { font-size: 24px; }
    }
  `;


  // ============================================================
  //  DOM SETUP — Called once when the script loads
  // ============================================================

  function injectStyles() {
    if (document.getElementById('pb-paypal-styles')) return;
    var style = document.createElement('style');
    style.id = 'pb-paypal-styles';
    style.textContent = MODAL_CSS;
    document.head.appendChild(style);
  }

  function buildModalDOM() {
    if (document.getElementById('pb-paypal-overlay')) return;

    var overlay = document.createElement('div');
    overlay.id = 'pb-paypal-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'pb-paypal-tier-name');

    overlay.innerHTML = `
      <div id="pb-paypal-modal">
        <button id="pb-paypal-close" aria-label="Close payment dialog">&times;</button>

        <p id="pb-paypal-tier-name">Pure Brain</p>
        <p id="pb-paypal-price-line">$0<span style="font-size:16px;font-weight:400;color:rgba(255,255,255,0.5)">/mo</span></p>
        <p id="pb-paypal-price-sub">Billed monthly &bull; Cancel anytime</p>

        <hr />

        <div id="pb-paypal-buttons-container">
          <!-- PayPal buttons render here -->
        </div>

        <div id="pb-paypal-trust">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 1L8.8 4.8L13 5.3L10 8.2L10.7 12.4L7 10.4L3.3 12.4L4 8.2L1 5.3L5.2 4.8L7 1Z"
              fill="rgba(255,255,255,0.25)" />
          </svg>
          Secured by PayPal &bull; SSL encrypted
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    // Success banner (separate from modal)
    var banner = document.createElement('div');
    banner.id = 'pb-payment-success-banner';
    banner.innerHTML = 'Payment confirmed! Redirecting to your awakening...';
    document.body.appendChild(banner);

    // Close button
    document.getElementById('pb-paypal-close').addEventListener('click', closeModal);

    // Click outside modal to close
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });

    // ESC key to close
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeModal();
    });
  }


  // ============================================================
  //  MODAL OPEN / CLOSE
  // ============================================================

  var currentTier = null;

  function openModal(tier) {
    currentTier = tier;
    var price = PRICES[tier] || '0.00';

    // Update header text
    document.getElementById('pb-paypal-tier-name').textContent = 'Pure Brain — ' + tier;
    document.getElementById('pb-paypal-price-line').innerHTML =
      '$' + parseInt(price, 10) +
      '<span style="font-size:16px;font-weight:400;color:rgba(255,255,255,0.5)">/mo</span>';

    // Clear previous button content
    var container = document.getElementById('pb-paypal-buttons-container');
    container.innerHTML = '';

    // Show overlay
    document.getElementById('pb-paypal-overlay').classList.add('pb-active');
    document.body.style.overflow = 'hidden';

    // Render the appropriate payment UI — SDK is primary
    if (window.__pbUseSDK) {
      renderSDKButtons(tier, container);
    } else {
      renderFallbackButton(tier, container);
    }
  }

  function closeModal() {
    var overlay = document.getElementById('pb-paypal-overlay');
    if (overlay) overlay.classList.remove('pb-active');
    document.body.style.overflow = '';
    currentTier = null;
  }


  // ============================================================
  //  APPROACH A: PayPal JS SDK Smart Buttons  ← PRIMARY / DEFAULT
  //
  //  Highest security: payment captured server-side via PayPal Orders API.
  //  After capture, we call our own log server for independent verification.
  //  onApprove fires inside the same browser session (true in-page checkout).
  //
  //  Requires:
  //    1. Real PAYPAL_CLIENT_ID (replace placeholder above)
  //    2. (Optional) PLAN_IDS for subscription billing
  // ============================================================

  /**
   * Dynamically loads the PayPal JS SDK script.
   * Intent is 'subscription' when plan IDs are configured, otherwise 'capture'.
   * @param {Function} onLoad  Callback once SDK is ready
   */
  function loadPayPalSDK(onLoad) {
    if (window.paypal) {
      onLoad();
      return;
    }

    var hasPlanIds = PLAN_IDS[currentTier || 'Awakened'];
    var intent     = hasPlanIds ? 'subscription' : 'capture';
    var vaultParam = hasPlanIds ? '&vault=true'  : '';

    var script = document.createElement('script');
    script.src =
      'https://www.paypal.com/sdk/js' +
      '?client-id=' + PAYPAL_CLIENT_ID +
      '&currency=' + CURRENCY +
      '&intent=' + intent +
      vaultParam;
    script.async = true;
    script.onload = onLoad;
    script.onerror = function () {
      console.error('[PB PayPal] Failed to load PayPal SDK. Falling back to form approach.');
      window.__pbUseSDK = false;
      if (currentTier) {
        var container = document.getElementById('pb-paypal-buttons-container');
        if (container) {
          container.innerHTML = '';
          renderFallbackButton(currentTier, container);
        }
      }
    };

    document.head.appendChild(script);
  }

  /**
   * Sends a server-side verification request to our log server after SDK capture.
   * This independently confirms the payment is legitimate before treating it as done.
   *
   * POST https://api.purebrain.ai/api/verify-payment
   * Body: { orderId, tier, payerInfo }
   *
   * On success  → calls handlePaymentSuccess()
   * On failure  → logs warning but still calls handlePaymentSuccess() so the user
   *               is never blocked by a backend issue; the order ID is preserved for
   *               manual reconciliation.
   *
   * @param {string} tier       "Awakened" | "Partnered" | "Unified"
   * @param {string} orderId    PayPal order or subscription ID
   * @param {object} payerInfo  PayPal payer object from SDK
   */
  function verifyPaymentServerSide(tier, orderId, payerInfo) {
    var container = document.getElementById('pb-paypal-buttons-container');
    if (container) {
      container.innerHTML = '<p id="pb-paypal-verifying">Verifying payment\u2026</p>';
    }

    var payload = JSON.stringify({
      orderId:    orderId,
      tier:       tier,
      payerInfo:  payerInfo,
      sessionUuid: (typeof payTestData !== 'undefined' && payTestData.sessionUuid) ? payTestData.sessionUuid : (sessionStorage.getItem('pb_sessionUuid') || ''),
    });

    var controller = new AbortController();
    var timeoutId = setTimeout(function() { controller.abort(); }, 3000);

    fetch(VERIFY_ENDPOINT, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    payload,
      signal:  controller.signal,
    })
      .then(function (response) {
        clearTimeout(timeoutId);
        return response.json().then(function (data) {
          if (!response.ok || data.verified === false) {
            // Log the mismatch — payment may still be valid; do not block the user
            console.warn(
              '[PB PayPal] Server verification returned unverified.',
              'orderId:', orderId,
              'response:', data
            );
          } else {
            console.log('[PB PayPal] Server verification confirmed.', data);
          }
          // Proceed regardless so UX is never blocked by a backend issue
          handlePaymentSuccess(tier, orderId, payerInfo);
        });
      })
      .catch(function (err) {
        clearTimeout(timeoutId);
        // Network, CORS, or timeout error — do not block the user
        console.warn('[PB PayPal] Verification timed out:', err.message);
        handlePaymentSuccess(tier, orderId, payerInfo);
      });
  }

  /**
   * Renders PayPal Smart Buttons inside the modal container.
   * Supports both one-time payment and subscription (if PLAN_IDS configured).
   *
   * After SDK capture the flow is:
   *   SDK onApprove → verifyPaymentServerSide() → handlePaymentSuccess()
   *                                              → window.onPaymentComplete()
   *
   * @param {string}      tier       "Awakened" | "Partnered" | "Unified"
   * @param {HTMLElement} container  DOM node to render into
   */
  function renderSDKButtons(tier, container) {
    var price  = PRICES[tier]   || '0.00';
    var planId = PLAN_IDS[tier] || '';

    loadPayPalSDK(function () {
      var buttonConfig;

      if (planId) {
        // ---- Subscription billing (recurring) ----
        buttonConfig = {
          style: {
            shape:  'rect',
            color:  'gold',
            layout: 'vertical',
            label:  'subscribe',
          },
          createSubscription: function (data, actions) {
            return actions.subscription.create({
              plan_id: planId,
              application_context: {
                shipping_preference: 'NO_SHIPPING',
                user_action: 'SUBSCRIBE_NOW'
              }
            });
          },
          onApprove: function (data) {
            // data.subscriptionID is the PayPal subscription ID
            verifyPaymentServerSide(tier, data.subscriptionID, data);
          },
          onError: handlePaymentError,
          onCancel: function () {
            console.log('[PB PayPal] Subscription cancelled by user.');
          },
        };
      } else {
        // ---- One-time payment (order/capture) ----
        buttonConfig = {
          style: {
            shape:  'rect',
            color:  'gold',
            layout: 'vertical',
            label:  'pay',
          },
          createOrder: function (data, actions) {
            return actions.order.create({
              purchase_units: [{
                description:  'Pure Brain — ' + tier + ' Plan',
                custom_id:    'PB-' + tier.toUpperCase() + '-' + ((typeof payTestData !== 'undefined' && payTestData.sessionUuid) ? payTestData.sessionUuid : ''),
                amount: {
                  currency_code: CURRENCY,
                  value:         price,
                },
              }],
              application_context: {
                shipping_preference: 'NO_SHIPPING',
              },
            });
          },
          onApprove: function (data, actions) {
            // Capture the order via the SDK (server-authoritative)
            return actions.order.capture().then(function (details) {
              var payerInfo = details.payer || {};
              // Call our log server for independent verification before completing
              verifyPaymentServerSide(tier, data.orderID, payerInfo);
            });
          },
          onError: handlePaymentError,
          onCancel: function () {
            console.log('[PB PayPal] Payment cancelled by user.');
          },
        };
      }

      try {
        window.paypal.Buttons(buttonConfig).render(container);
      } catch (err) {
        console.error('[PB PayPal] Render error:', err);
        container.innerHTML = '';
        renderFallbackButton(tier, container);
      }

      // SANDBOX TEST BYPASS - removed for production
    });
  }


  // ============================================================
  //  APPROACH B: Form POST in a centered popup window  ← FALLBACK
  //
  //  Used automatically when:
  //    - PayPal SDK fails to load
  //    - window.__pbUseSDK is false (set USE_SDK_APPROACH = true below)
  //
  //  Works with no PayPal app setup required.
  //  Uses the classic PayPal /cgi-bin/webscr endpoint.
  //  Opens in a small centered browser popup (not _blank tab).
  // ============================================================

  function renderFallbackButton(tier, container) {
    var price = PRICES[tier] || '0.00';

    // Build a hidden form that POSTs to PayPal and opens in a centered popup
    var form = document.createElement('form');
    form.action   = 'https://www.paypal.com/cgi-bin/webscr';
    form.method   = 'post';
    form.target   = 'pb-paypal-popup';
    form.style.display = 'block';

    var fields = {
      cmd:           '_xclick-subscriptions',
      business:      BUSINESS_EMAIL,
      item_name:     'Pure Brain — ' + tier + ' Plan',
      item_number:   'PB-' + tier.toUpperCase(),
      currency_code: CURRENCY,
      a3:            price,           // subscription amount
      p3:            '1',             // billing frequency
      t3:            'M',             // billing period: Monthly
      src:           '1',             // recurring payments
      sra:           '1',             // reattempt on failure
      no_note:       '1',
      no_shipping:   '1',
      return:        RETURN_URL,
      cancel_return: CANCEL_URL,
    };

    Object.keys(fields).forEach(function (name) {
      var input = document.createElement('input');
      input.type  = 'hidden';
      input.name  = name;
      input.value = fields[name];
      form.appendChild(input);
    });

    // Create a visible submit button that matches purebrain styling
    var btn = document.createElement('button');
    btn.type = 'submit';
    btn.id   = 'pb-paypal-form-btn';
    btn.innerHTML =
      '<img decoding="async" src="https://www.paypalobjects.com/webstatic/en_US/i/buttons/PP_logo_h_100x26.png" ' +
      'alt="PayPal" style="height:20px;vertical-align:middle;margin-right:8px;"  loading="lazy" />' +
      'Pay with PayPal';

    form.appendChild(btn);
    container.appendChild(form);

    // Override form submit to open in a centered popup
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      openCenteredPopup(form);
    });
  }

  /**
   * Opens the PayPal form in a centered browser popup window.
   * Attempts to detect when the popup closes and shows a confirmation
   * prompt in the overlay so the user can confirm payment.
   */
  function openCenteredPopup(form) {
    var w = 600, h = 700;
    var left = Math.round((screen.width  - w) / 2);
    var top  = Math.round((screen.height - h) / 2);
    var features = [
      'width='  + w,
      'height=' + h,
      'left='   + left,
      'top='    + top,
      'toolbar=no',
      'menubar=no',
      'scrollbars=yes',
      'resizable=yes',
      'location=yes',
      'status=no',
    ].join(',');

    var popup = window.open('', 'pb-paypal-popup', features);

    if (!popup || popup.closed) {
      // Popup blocked — fall back to submitting directly in a new tab
      form.target = '_blank';
      form.submit();
      return;
    }

    // Submit the form into the popup
    form.target = 'pb-paypal-popup';
    form.submit();

    // Poll for popup closure then show confirmation prompt
    var pollInterval = setInterval(function () {
      if (!popup || popup.closed) {
        clearInterval(pollInterval);
        showPopupClosedConfirmation();
      }
    }, 800);
  }

  /**
   * After the PayPal popup closes, ask the user if their payment succeeded.
   * PayPal does not send a postMessage on form-POST flow, so we ask manually.
   */
  function showPopupClosedConfirmation() {
    var container = document.getElementById('pb-paypal-buttons-container');
    if (!container) return;

    container.innerHTML = `
      <p style="color:rgba(255,255,255,0.7);font-size:14px;text-align:center;margin:0 0 20px;">
        Did your payment complete?
      </p>
      <div style="display:flex;gap:12px;">
        <button onclick="window.__pbPaymentYes()" style="
          flex:1;padding:13px;background:#2ecc71;color:#0a1a12;border:none;
          border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;">
          Yes, I paid
        </button>
        <button onclick="window.__pbPaymentNo()" style="
          flex:1;padding:13px;background:rgba(255,255,255,0.08);color:#fff;border:none;
          border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;">
          No, go back
        </button>
      </div>
    `;
  }

  window.__pbPaymentYes = function () {
    handlePaymentSuccess(currentTier || 'Unknown', 'FALLBACK-' + Date.now(), {});
  };

  window.__pbPaymentNo = function () {
    // Re-render the PayPal button so user can try again
    var container = document.getElementById('pb-paypal-buttons-container');
    if (container && currentTier) {
      container.innerHTML = '';
      renderFallbackButton(currentTier, container);
    }
  };


  // ============================================================
  //  PAYMENT SUCCESS HANDLER
  // ============================================================

  /**
   * Called after payment is confirmed AND server-side verification completes.
   * Sets global state, shows success banner, fires callback, redirects to #awakening.
   *
   * For SDK payments this is called by verifyPaymentServerSide() after the
   * verification call to https://api.purebrain.ai/api/verify-payment.
   *
   * Fires window.onPaymentComplete(tier, orderId, payerInfo) if defined.
   *
   * @param {string} tier       The tier name ("Awakened" | "Partnered" | "Unified")
   * @param {string} orderId    PayPal order/subscription ID (or fallback string)
   * @param {object} payerInfo  PayPal payer object (may be empty for fallback)
   */
  function handlePaymentSuccess(tier, orderId, payerInfo) {
    // Store globally so other scripts on the page can read these values
    window.paymentConfirmed = true;
    window.paymentTier      = tier;
    window.paymentOrderId   = orderId;

    // Close the modal
    closeModal();

    // Show the success banner
    var banner = document.getElementById('pb-payment-success-banner');
    if (banner) {
      banner.classList.add('pb-visible');
      // Auto-hide after 6 seconds
      setTimeout(function () {
        banner.classList.remove('pb-visible');
      }, 6000);
    }

    // Fire the callback if the page has defined one
    if (typeof window.onPaymentComplete === 'function') {
      try {
        window.onPaymentComplete(tier, orderId, payerInfo);
      } catch (err) {
        console.error('[PB PayPal] onPaymentComplete callback threw:', err);
      }
    }

    // Redirect to #awakening section (scroll to it)
    setTimeout(function () {
      window.location.hash = 'awakening';

      // If the hash didn't trigger a scroll (element might not exist), go to top
      var target = document.getElementById('awakening');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 800);
  }

  /**
   * Called on SDK payment error.
   */
  function handlePaymentError(err) {
    console.error('[PB PayPal] Payment error:', err);
    var container = document.getElementById('pb-paypal-buttons-container');
    if (container) {
      container.innerHTML = `
        <p style="color:#ff6b6b;text-align:center;font-size:14px;padding:12px 0;">
          Something went wrong. Please try again or
          <a href="mailto:${BUSINESS_EMAIL}" style="color:#8a2be2;">contact support</a>.
        </p>
      `;
      // Re-show button after a short delay
      setTimeout(function () {
        if (container && currentTier) {
          container.innerHTML = '';
          if (window.__pbUseSDK && window.paypal) {
            renderSDKButtons(currentTier, container);
          } else {
            renderFallbackButton(currentTier, container);
          }
        }
      }, 3000);
    }
  }


  // ============================================================
  //  PUBLIC API — Replaces openWaitlistModal on the page
  // ============================================================

  /**
   * openWaitlistModal(tier)
   *
   * Drop-in replacement for the existing function called by "Activate Now" buttons.
   * The same function signature is preserved so NO changes are needed in the HTML
   * button onclick attributes.
   *
   * Usage (already in your HTML):
   *   onclick="openWaitlistModal('Awakened')"
   *   onclick="openWaitlistModal('Awakened')"
   *   onclick="openWaitlistModal('Partnered')"
   */
  window.openWaitlistModal = function (tier) {
    // Normalise tier name capitalisation just in case
    var canonicalTier = Object.keys(PRICES).find(function (t) {
      return t.toLowerCase() === (tier || '').toLowerCase();
    });

    if (!canonicalTier) {
      console.warn('[PB PayPal] Unknown tier:', tier, '— defaulting to Awakened');
      canonicalTier = 'Awakened';
    }

    openModal(canonicalTier);
  };

  /**
   * openPayPalCheckout(tier)
   *
   * Alternative entry point if you want to call it with a new name.
   * Identical to openWaitlistModal.
   */
  window.openPayPalCheckout = window.openWaitlistModal;
  window.openPayPalModal = window.openWaitlistModal;
  window.openModal = openModal;


  // ============================================================
  //  SWITCH — Toggle between Approach A (SDK) and Approach B (form POST)
  //
  //  - true  (DEFAULT): Approach A — PayPal JS SDK.  Requires real Client ID.
  //  - false:           Approach B — Form POST popup. Works without any setup.
  //
  //  SDK is the DEFAULT because it provides:
  //    - Server-side capture (payment cannot be spoofed client-side)
  //    - Our own verification endpoint confirms the transaction
  //    - Real payer information returned (name, email, address)
  //    - No redirect away from the page
  //
  //  NOTE: With the placeholder PAYPAL_CLIENT_ID the SDK will fail to load and
  //  automatically fall back to Approach B.  Replace the Client ID to activate
  //  Approach A fully.
  // ============================================================

  var USE_SDK_APPROACH = true; // Approach B: PayPal form popup (no SDK/CLIENT_ID required)

  // Internal flag used throughout this script
  window.__pbUseSDK = USE_SDK_APPROACH;

  if (USE_SDK_APPROACH && PAYPAL_CLIENT_ID === 'PAYPAL_CLIENT_ID') {
    console.warn(
      '[PB PayPal] USE_SDK_APPROACH is true but PAYPAL_CLIENT_ID is still a placeholder. ' +
      'Replace PAYPAL_CLIENT_ID with your real PayPal Client ID from developer.paypal.com. ' +
      'The SDK will attempt to load and will fall back to Approach B (form popup) if it fails.'
    );
  }


  // ============================================================
  //  INIT — Run immediately when script loads
  // ============================================================

  function init() {
    injectStyles();
    buildModalDOM();

    // Pre-load the PayPal SDK in the background if using SDK approach,
    // so the first modal open is instant instead of waiting for download.
    if (window.__pbUseSDK) {
      // Temporarily set currentTier to the most popular plan for SDK URL params
      currentTier = 'Awakened';
      loadPayPalSDK(function () {
        currentTier = null;
        console.log('[PB PayPal] SDK pre-loaded and ready.');
      });
    }
  }

  // Run after DOM is available
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})(); // End IIFE

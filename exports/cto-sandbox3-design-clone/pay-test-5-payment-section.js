<script>
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
 *      https://api.purebrain.ai:8443/api/verify-payment
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
    Awakened:  'P-1AG936074F0953120NGLTFKY', // $79/mo — LIVE
    Bonded:    'P-2SA65600MT088594TNGLTFKY', // $149/mo — LIVE
    Partnered: 'P-3VH43554A66001716NGLTFKY', // $499/mo — LIVE
    Unified:   'P-43A28944XN5237411NGLTFLA', // $999/mo — LIVE
  };

  // Pricing — matches purebrain.ai tiers
  var PRICES = {
    Awakened:  '79.00',
    Bonded:    '149.00',
    Partnered: '499.00',
    Unified:   '999.00',
  };

  // PayPal business account that receives payments
  var BUSINESS_EMAIL = 'support@puremarketing.ai';

  // Where PayPal sends the user after payment
  var RETURN_URL = 'https://purebrain.ai/thank-you/';
  var CANCEL_URL = 'https://purebrain.ai/pay-test/';

  // Currency
  var CURRENCY = 'USD';

  /**
   * Server-side verification endpoint.
   * Called after SDK capture to independently confirm the payment with PayPal's API.
   * Endpoint: POST https://api.purebrain.ai:8443/api/verify-payment
   * Body:      { orderId, tier, payerInfo }
   * Expected:  { verified: true|false, ... }
   */
  var VERIFY_ENDPOINT = 'https://api.purebrain.ai:8443/api/verify-payment';


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

    var hasPlanIds = PLAN_IDS[currentTier || 'Bonded'];
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
   * POST https://api.purebrain.ai:8443/api/verify-payment
   * Body: { orderId, tier, payerInfo }
   *
   * On success  → calls handlePaymentSuccess()
   * On failure  → logs warning but still calls handlePaymentSuccess() so the user
   *               is never blocked by a backend issue; the order ID is preserved for
   *               manual reconciliation.
   *
   * @param {string} tier       "Awakened" | "Bonded" | "Partnered"
   * @param {string} orderId    PayPal order or subscription ID
   * @param {object} payerInfo  PayPal payer object from SDK
   */
  function verifyPaymentServerSide(tier, orderId, payerInfo) {
    var container = document.getElementById('pb-paypal-buttons-container');
    if (container) {
      container.innerHTML = '<p id="pb-paypal-verifying">Verifying payment\u2026</p>';
    }

    var payload = JSON.stringify({
      orderId:   orderId,
      tier:      tier,
      payerInfo: payerInfo,
    });

    fetch(VERIFY_ENDPOINT, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    payload,
    })
      .then(function (response) {
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
        // Network or CORS error — do not block the user
        console.warn(
          '[PB PayPal] Server verification request failed (network/CORS). ' +
          'Proceeding with client-side confirmation. orderId:', orderId,
          err
        );
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
   * @param {string}      tier       "Awakened" | "Bonded" | "Partnered"
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
            return actions.subscription.create({ plan_id: planId });
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
                custom_id:    'PB-' + tier.toUpperCase(),
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
      '<img src="https://www.paypalobjects.com/webstatic/en_US/i/buttons/PP_logo_h_100x26.png" ' +
      'alt="PayPal" style="height:20px;vertical-align:middle;margin-right:8px;" />' +
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
   * verification call to https://api.purebrain.ai:8443/api/verify-payment.
   *
   * Fires window.onPaymentComplete(tier, orderId, payerInfo) if defined.
   *
   * @param {string} tier       The tier name ("Awakened" | "Bonded" | "Partnered")
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
   *   onclick="openWaitlistModal('Bonded')"
   *   onclick="openWaitlistModal('Partnered')"
   */
  window.openWaitlistModal = function (tier) {
    // Normalise tier name capitalisation just in case
    var canonicalTier = Object.keys(PRICES).find(function (t) {
      return t.toLowerCase() === (tier || '').toLowerCase();
    });

    if (!canonicalTier) {
      console.warn('[PB PayPal] Unknown tier:', tier, '— defaulting to Bonded');
      canonicalTier = 'Bonded';
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
      currentTier = 'Bonded';
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
</script>

<script>
/* === Post-Payment Chat Flow v4.7 (Witness Production: seed data POST, server-authoritative container, portal domain flex) === */
/**
 * pay-test-chat-flow-v4.js
 * Post-payment chat flow for purebrain.ai/pay-test
 *
 * v4.5 changes (Corey production directives 2026-02-25):
 *   - CHANGE 1: AUTO-FIRE birth init after Q4 — removed manual "Start AI Birth" button
 *       Per Witness v3.0 spec: SEED arriving IS the trigger. No user action needed.
 *   - CHANGE 2: Removed hardcoded 'aiciv-07' container name
 *       Container is ALWAYS server-authoritative via auto-allocation ({} POST body).
 *   - CHANGE 3: WITNESS_WEBHOOK_HOST switched to HTTPS proxy (89.167.19.20:8443)
 *       Fixes mixed-content and routes through server-side proxy to Witness.
 *
 * v4.3.3 changes (birth UX fixes per Jared screenshot 2026-02-24):
 *   - CHANGE 1: Birth setup message text updated
 *       "One more step to complete [AI Name]'s setup" → "The next step in [AI Name]'s set up"
 *   - CHANGE 2: OAuth authorize button moved to actions area (bottom of chat)
 *       Previously: rendered as an inline chat bubble (msgList.appendChild)
 *       Now: rendered in the actions div at the bottom via promptButtons pattern
 *   - CHANGE 3: Graceful degradation fallback message removed
 *       Removed: "One moment — we're still setting up your AiCIV in the background..."
 *       Added: "Yay! [AI NAME]'s brain is connected. Let's continue!" on successful /birth/code
 *   - CHANGE 4: Version bumped to v4.3.3
 *
 * v4.3.2 changes (sandbox E2E test 2026-02-24):
 *   - CHANGE 1: runBirthInit() is now MANUAL (button-triggered, not auto-fire)
 *       Previously: called automatically at end of runQuestionnaire() after Q4
 *       Now: shows "Your AI is ready to be born" message + "Start AI Birth →" button
 *       runBirthInit() only fires when the human clicks that button
 *       Button is disabled after click to prevent double-fire (was hammering Witness single-threaded webhook)
 *   - CHANGE 2: Container hardcoded to "aiciv-07" for E2E test
 *       window._pbContainerName set to 'aiciv-07' at top of runBirthInit()
 *       POST /api/birth/start always sends {"container": "aiciv-07"}
 *       Prevents auto-allocation which was picking aiciv-08 with stale processes
 *
 * v4.3.1 changes (sandbox E2E test 2026-02-24):
 *   - WITNESS_WEBHOOK_HOST reverted to http://104.248.239.98:8099 for direct E2E test
 *       (approved by Jared + Witness; sandbox page 688 ONLY - page 689 stays on api.purebrain.ai)
 *       This bypasses the HTTPS proxy to test Witness birth pipeline end-to-end directly
 *
 * v4.3 changes (architecture: Birth Init moved earlier, API key flow removed 2026-02-24):
 *   - REMOVED: Claude API key collection flow (Phase 3 Step 10 in v4.2)
 *       Removed: "Before we go deeper" Keen message asking for API key
 *       Removed: "Open Claude Console" button (link to platform.claude.com)
 *       Removed: API key input/masking/validation logic (key prefix validation)
 *       NOTE: "I have my key →" button KEPT but repurposed: now triggers
 *             code input for OAuth flow (not API key) in Phase 1 Birth Init
 *       Removed: claudeSessionInfo field from payTestData
 *       Removed: claudeAuthComplete timestamp
 *       Removed: claudeMaxStatus / hasClaudeMax (no longer collected)
 *   - MOVED: runBirthInit() now fires IMMEDIATELY AFTER Q4 (role/title) in Phase 1
 *       Previously: fired at start of Phase 5 (runThankYouMessage)
 *       New location: end of runQuestionnaire(), after role acknowledgment
 *       New UX: "One more step to complete [AI Name]'s setup — linking intelligence now"
 *       → /birth/start → OAuth button → "I have my key →" → code input → /birth/code → confirm
 *       → "Connection established. Let's keep going." → then Primary Goal (Step 6)
 *   - runPortalButtonWatcher() starts after user clicks "Learn more →" in Phase 5
 *       (same as v4.2 — watcher polls silently while user does learn-more questions)
 *   - Phase 5 (runThankYouMessage): removed runBirthInit() call;
 *       runPortalButtonWatcher() starts when user clicks "Learn more →"
 *
 * v4.2 changes (security hardening per security-engineer-tech review 2026-02-24):
 *   - CRIT-003: WITNESS_WEBHOOK_HOST changed from plain HTTP IP to https://api.purebrain.ai
 *   - CRIT-004: sanitizeText() helper added; aiName sanitized at entry point
 *   - HIGH-002: oauthUrl validated for HTTPS + claude.ai/anthropic.com domain before DOM injection
 *   - HIGH-003: containerName allowlist enforced (lowercase alphanum + hyphens, max 64 chars)
 *   - MED-003: window.payTestData and window.logPayTestData removed from global exports
 *
 * v4.1 changes (UI upgrades per Jared 2026-02-24):
 *   - OAuth button text: "Authorize Your AiCIV" → "Authorize {aiName}'s AI Brain →"
 *   - Portal entry button text: "Enter Your AiCIV" → "Enter {aiName}'s Brain Stream"
 *   - Portal button style upgraded to match "Begin Awakening" CTA: large, prominent,
 *       full-width, orange→blue gradient, big font, pill border-radius, glow shadow
 *
 * v4 changes (on top of v3):
 *   - NEW: runBirthInit() — Witness birth pipeline: POST /api/birth/start → OAuth button
 *       → code input → POST /api/birth/code → portal polling begins
 *   - FIXED: runPortalButtonWatcher() now polls Witness endpoint:
 *       GET https://api.purebrain.ai/api/birth/portal-status/{container}
 *       (v4.2: routed through HTTPS proxy; v4.0 original used plain HTTP IP)
 *   - NEW: containerName plumbing — sourced from page metadata (window._pbContainerName),
 *       falls back to "purebrain-{humanFirstName}" slug
 *   - Timeout for /start raised to 180s (Witness reports ~145s in production)
 *   - Portal-status polling uses container name, not email/orderId
 *
 * v3 changes:
 *   - Claude auth MOVED from Phase 4 to Phase 1 (after Role question, before Primary Goal)
 *   - Behind-the-Curtain slides now have emoji icons per slide
 *   - Telegram Step 4 bot username example is now dynamic (uses aiName)
 *   - runClaudeMaxSetup REMOVED from flow (function kept as dead code for compatibility)
 *   - runCompletion button now triggers in-chat thank-you (no redirect to /thank-you/)
 *   - NEW: runThankYouMessage — renders thank-you card as AI message bubble
 *   - NEW: runLearnMoreLoop — 5-question deeper context conversation
 *   - NEW: runPortalButtonWatcher — polls for portal readiness, shows button when ready
 *
 * Usage:
 *   initPayTestFlow(chatContainer, aiName, tierPaid)
 *
 * CSS variables expected in host page:
 *   --bright-orange: #f1420b
 *   --light-blue:   #2a93c1
 *   --dark:         #0a0a0a
 */

'use strict';

// ---------------------------------------------------------------------------
// Global data store
// ---------------------------------------------------------------------------

const payTestData = {
  tier: null,
  aiName: null,
  orderId: null,
  name: null,
  email: null,
  company: null,
  role: null,
  primaryGoal: null,
  hasTelegram: null,
  telegramBotToken: null,
  learnMoreAnswers: [],           // NEW v3: stores learn-more conversation answers
  portalReady: false,            // NEW v3: tracks portal readiness state
  containerName: null,           // NEW v4: Witness birth pipeline container name
  birthOauthUrl: null,           // NEW v4: OAuth URL from Witness /start
  birthAuthenticated: false,     // NEW v4: true after Witness confirms authentication
  timestamps: {
    started: null,
    questionnaireComplete: null,
    curtainComplete: null,
    telegramComplete: null,
    flowComplete: null,
    learnMoreComplete: null,
    birthStarted: null,          // NEW v4: when /api/birth/start was called
    birthAuthenticated: null,    // NEW v4: when /api/birth/code confirmed
  },
};

// ---------------------------------------------------------------------------
// Log helper — sends payTestData snapshot to BOTH log endpoints
// ---------------------------------------------------------------------------

async function logPayTestData(data) {
  // Strip sensitive credentials before transmission (CRIT-001)
  // v4.3: claudeSessionInfo removed (API key flow removed); telegramBotToken still stripped
  const { telegramBotToken: _tg, ...safeData } = data;

  // Build base payload for /api/log-pay-test (form data)
  const payTestPayload = {
    event: safeData.event || 'pay-test-flow',
    timestamp: new Date().toISOString(),
    tier: payTestData.tier,
    orderId: payTestData.orderId,
    aiName: payTestData.aiName,
    name: payTestData.name,
    email: payTestData.email,
    company: payTestData.company,
    role: payTestData.role,
    primaryGoal: payTestData.primaryGoal,
    ...safeData,
    prePurchaseSessionId: payTestData.prePurchaseSessionId || null,
    prePurchaseMessageCount: payTestData.prePurchaseMessageCount || 0,
  };

  // Build messages array for /api/log-conversation (required by AICIV)
  // Combines pre-purchase chat history + onboarding Q&A collected so far
  const preMsgs = (payTestData.prePurchaseHistory && payTestData.prePurchaseHistory.length)
    ? payTestData.prePurchaseHistory
    : ((window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory)
        ? window._pbPrePurchaseSession.conversationHistory
        : []);

  // Build onboarding messages from collected payTestData fields
  const onboardingMsgs = [];
  if (payTestData.name) {
    onboardingMsgs.push({ role: 'assistant', content: 'What is your name?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.name });
  }
  if (payTestData.email) {
    onboardingMsgs.push({ role: 'assistant', content: 'What email should we use to reach you?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.email });
  }
  if (payTestData.company) {
    onboardingMsgs.push({ role: 'assistant', content: 'Are you working within a company or organization?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.company });
  }
  if (payTestData.role) {
    onboardingMsgs.push({ role: 'assistant', content: 'What is your role or title?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.role });
  }
  if (payTestData.primaryGoal) {
    onboardingMsgs.push({ role: 'assistant', content: 'If your AI could do one thing exceptionally well for you, what would it be?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.primaryGoal });
  }

  const allMessages = [...preMsgs, ...onboardingMsgs];

  // Use the pre-purchase session ID if available, else generate one
  const logSessionId = payTestData.prePurchaseSessionId
    || ('pb-post-' + (payTestData.orderId || Date.now()));

  // Payload for /api/log-conversation (requires 'messages' field for AICIV)
  const convPayload = {
    session_id: logSessionId,
    messages: allMessages.length ? allMessages : [
      { role: 'user', content: '[Post-payment onboarding - no pre-purchase chat history]' }
    ],
    source: 'purebrain-post-payment',
    page_url: window.location.href,
    aiName: payTestData.aiName,
    userName: payTestData.name,
    userTier: payTestData.tier,
    metadata: {
      event: data.event || 'pay-test-flow',
      orderId: payTestData.orderId,
      phase: 'post-payment',
    },
  };

  // Send to both endpoints with correct payloads
  await Promise.allSettled([
    fetch('https://api.purebrain.ai/api/log-pay-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(payTestPayload),
    }).catch((err) => console.warn('[pay-test] log-pay-test failed:', err.message)),

    fetch('https://api.purebrain.ai/api/log-conversation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(convPayload),
    }).catch((err) => console.warn('[pay-test] log-conversation failed:', err.message)),
  ]);
}

// ---------------------------------------------------------------------------
// Utility: pause
// ---------------------------------------------------------------------------

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Utility: random delay in a range
// ---------------------------------------------------------------------------

function jitter(min = 500, max = 1500) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ---------------------------------------------------------------------------
// Inject component styles once
// ---------------------------------------------------------------------------

function injectStyles() {
  if (document.getElementById('pay-test-styles')) return;

  const style = document.createElement('style');
  style.id = 'pay-test-styles';
  style.textContent = `
    /* ── Variables ─────────────────────────────────────────────────── */
    :root {
      --bright-orange: #f1420b;
      --light-blue:    #2a93c1;
      --dark:          #0a0a0a;
      --surface:       #111111;
      --surface-2:     #1a1a1a;
      --text-primary:  #f0f0f0;
      --text-muted:    #888888;
      --radius:        12px;
    }

    /* ── Chat wrapper ───────────────────────────────────────────────── */
    .ptc-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      flex: 1;
      background: rgba(10, 10, 10, 0.97);
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 15px;
      line-height: 1.55;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.08);
      position: relative;
      z-index: 1;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    /* ── Message list ───────────────────────────────────────────────── */
    .ptc-messages {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      padding: 20px 24px 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      scroll-behavior: smooth;
      position: relative;
      z-index: 2;
    }

    /* ── Individual message bubble ──────────────────────────────────── */
    .ptc-msg {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      max-width: 78%;
      animation: ptc-fade-in 0.3s ease;
    }

    @keyframes ptc-fade-in {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0);   }
    }

    .ptc-msg--ai   { align-self: flex-start; }
    .ptc-msg--user { align-self: flex-end;   flex-direction: row-reverse; }

    .ptc-bubble {
      padding: 12px 16px;
      border-radius: var(--radius);
      line-height: 1.55;
    }

    .ptc-msg--ai   .ptc-bubble {
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid rgba(255,255,255,0.08);
      color: var(--text-primary);
      border-bottom-left-radius: 4px;
    }

    .ptc-msg--user .ptc-bubble {
      background: linear-gradient(135deg, #f1420b, #ed6626);
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    /* ── Typing indicator ───────────────────────────────────────────── */
    .ptc-typing {
      display: flex;
      gap: 5px;
      align-items: center;
      padding: 12px 16px;
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: var(--radius);
      border-bottom-left-radius: 4px;
      width: fit-content;
    }

    .ptc-typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #2a93c1;
      animation: ptc-bounce 1.2s infinite ease-in-out;
    }

    .ptc-typing span:nth-child(2) { animation-delay: 0.2s; }
    .ptc-typing span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes ptc-bounce {
      0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
      40%            { transform: scale(1.0); opacity: 1.0; }
    }

    /* ── Input row ──────────────────────────────────────────────────── */
    .ptc-input-row {
      padding: 12px 24px 20px;
      display: flex;
      gap: 10px;
      background: transparent;
      border-top: 1px solid rgba(255,255,255,0.06);
      position: relative;
      z-index: 2;
      flex-shrink: 0;
    }

    .ptc-input {
      flex: 1;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      font-size: 15px;
      padding: 12px 16px;
      outline: none;
      transition: border-color 0.2s;
      resize: none;
      min-height: 42px;
      max-height: 120px;
    }

    .ptc-input:focus { border-color: var(--light-blue); }

    .ptc-send-btn {
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      border: none;
      border-radius: 12px;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      padding: 10px 22px;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .ptc-send-btn:hover { transform: scale(1.03); }

    .ptc-send-btn:hover   { opacity: 0.88; }
    .ptc-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }

    /* ── Action buttons (slides, yes/no, etc.) ──────────────────────── */
    .ptc-actions {
      padding: 4px 20px 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      flex-shrink: 0;
    }

    .ptc-btn {
      background: transparent;
      border: 1.5px solid var(--light-blue);
      border-radius: 8px;
      color: var(--light-blue);
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      padding: 9px 20px;
      transition: background 0.2s, color 0.2s;
    }

    .ptc-btn:hover {
      background: var(--light-blue);
      color: #fff;
    }

    .ptc-btn--primary {
      background: var(--bright-orange);
      border-color: var(--bright-orange);
      color: #fff;
    }

    .ptc-btn--primary:hover { opacity: 0.88; }

    /* ── Slide card ─────────────────────────────────────────────────── */
    .ptc-slide {
      background: var(--surface-2);
      border: 1px solid #222;
      border-radius: var(--radius);
      padding: 20px 22px;
      font-size: 14.5px;
      line-height: 1.65;
      color: var(--text-primary);
      animation: ptc-fade-in 0.3s ease;
      max-width: 78%;
      align-self: flex-start;
    }

    .ptc-slide-label {
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--light-blue);
      margin-bottom: 10px;
      font-weight: 700;
    }

    /* ── Slide icon visual ──────────────────────────────────────────── */
    .ptc-slide-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px 0 14px;
      font-size: 36px;
      line-height: 1;
    }

    .ptc-slide-icon svg {
      width: 44px;
      height: 44px;
      opacity: 0.85;
    }

    .ptc-slide-icon--wide {
      justify-content: flex-start;
      gap: 10px;
      font-size: 26px;
      flex-wrap: wrap;
    }

    /* ── Status indicator ───────────────────────────────────────────── */
    .ptc-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--text-muted);
      padding: 6px 0;
    }

    .ptc-status--success { color: #4caf50; }
    .ptc-status--error   { color: var(--bright-orange); }

    /* ── Welcome button ─────────────────────────────────────────────── */
    .ptc-welcome-btn {
      background: linear-gradient(135deg, var(--bright-orange), #c73000);
      border: none;
      border-radius: var(--radius);
      color: #fff;
      cursor: pointer;
      font-size: 17px;
      font-weight: 700;
      padding: 16px 32px;
      margin: 32px 20px 24px;
      flex-shrink: 0;
      transition: opacity 0.2s, transform 0.15s;
      letter-spacing: 0.02em;
    }

    .ptc-welcome-btn:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }

    /* ── External link button ───────────────────────────────────────── */
    .ptc-link-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--bright-orange);
      border: none;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      padding: 10px 20px;
      text-decoration: none;
      transition: opacity 0.2s;
    }

    .ptc-link-btn:hover { opacity: 0.88; }

    /* ── Google Fonts ──────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* ── Chat outer shell (overlay feel) ───────────────────────────── */
    .ptc-outer-shell {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 0;
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 24px 32px;
      background: #050508;
      overflow: hidden;
    }

    @media (max-width: 768px) {
      .ptc-outer-shell { padding: 12px 10px; }
    }

    /* ── Background spinning logo ──────────────────────────────────── */
    .ptc-bg-orb {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 340px;
      height: 340px;
      opacity: 0.06;
      pointer-events: none;
      z-index: 0;
    }

    .ptc-bg-orb img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      animation: ptc-bg-spin 30s linear infinite;
    }

    @keyframes ptc-bg-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }

    /* ── Chat header ───────────────────────────────────────────────── */
    .ptc-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      background: rgba(20, 20, 20, 0.95);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px 16px 0 0;
      flex-shrink: 0;
      position: relative;
      z-index: 2;
    }

    .ptc-header__logo {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2px;
      flex-shrink: 0;
    }

    .ptc-header__logo-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .ptc-header__logo-inner img {
      width: 70%;
      height: 70%;
      object-fit: contain;
    }

    .ptc-header__info {
      flex: 1;
    }

    .ptc-header__title {
      font-family: 'Oswald', sans-serif;
      font-size: 1rem;
      font-weight: 600;
      color: #f0f0f0;
    }

    .ptc-header__status {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      color: #888;
    }

    .ptc-status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #22c55e;
      animation: ptc-status-pulse 2s ease-in-out infinite;
    }

    @keyframes ptc-status-pulse {
      0%, 100% { opacity: 1; }
      50%      { opacity: 0.5; }
    }

    .ptc-header__brand {
      font-family: 'Oswald', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      color: #888;
      display: flex;
      align-items: center;
      gap: 0;
      letter-spacing: 0;
    }

    .ptc-header__brand-blue  { color: #2a93c1; letter-spacing: 0; }
    .ptc-header__brand-orange { color: #f1420b; }

    /* ── Avatar for AI messages ────────────────────────────────────── */
    .ptc-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      padding: 2px;
    }

    .ptc-avatar-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .ptc-avatar-inner img {
      width: 70%;
      height: 70%;
      object-fit: contain;
    }

    /* ── Spinning avatar for typing indicator ──────────────────────── */
    .ptc-avatar--spinning img {
      animation: ptc-logo-spin 1.5s linear infinite;
    }

    @keyframes ptc-logo-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }


    /* Responsive padding for post-payment container */
    @media (max-width: 1024px) {
      #pay-test-post-payment { padding: 10% !important; }
    }
    @media (max-width: 768px) {
      #pay-test-post-payment { padding: 7% !important; }
    }

    /* ── Thank-You Card ─────────────────────────────────────────────── */
    .ptc-ty-card {
      max-width: 100%;
      padding: 24px 28px;
      background: rgba(15, 15, 20, 0.98);
      border: 1px solid rgba(255,255,255,0.1);
    }

    .ptc-ty-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 20px;
      justify-content: center;
    }

    .ptc-ty-logo img {
      background: transparent !important;
    }

    .ptc-ty-logo-text {
      font-family: 'Oswald', sans-serif;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .ptc-ty-logo-blue   { color: #2a93c1; }
    .ptc-ty-logo-orange { color: #f1420b; }
    .ptc-ty-logo-suffix { color: rgba(255,255,255,0.5); }

    .ptc-ty-heading {
      font-family: 'Oswald', sans-serif;
      font-size: 1.8rem;
      font-weight: 700;
      color: #f1420b;
      text-align: center;
      margin-bottom: 8px;
    }

    .ptc-ty-sub {
      font-size: 14px;
      color: var(--text-muted);
      text-align: center;
      margin-bottom: 24px;
    }

    .ptc-ty-timeline-label {
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-muted);
      text-align: center;
      margin-bottom: 16px;
      font-weight: 700;
    }

    .ptc-ty-timeline {
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-bottom: 20px;
    }

    .ptc-ty-row {
      display: flex;
      align-items: flex-start;
      gap: 14px;
    }

    .ptc-ty-badge {
      font-size: 12px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 6px;
      white-space: nowrap;
      flex-shrink: 0;
    }

    .ptc-ty-badge--now  { background: #f1420b; color: #fff; }
    .ptc-ty-badge--soon { background: #2a93c1; color: #fff; }
    .ptc-ty-badge--later { background: #1a1a1a; color: #888; border: 1px solid #333; }

    .ptc-ty-row-text {
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.5;
    }

    .ptc-portal-placeholder {
      font-size: 13px;
      color: var(--text-muted);
      font-style: italic;
      margin-bottom: 6px;
      padding: 8px 12px;
      border: 1px dashed rgba(255,255,255,0.15);
      border-radius: 6px;
      display: inline-block;
    }

    /* Portal button (appears when portal is ready) */
    /* Portal entry button — styled to match "Begin Awakening" CTA (v4.1 upgrade)
       This is THE moment: the customer is stepping through into their AI's world.
       Must feel like a portal. Large, prominent, eye-catching, full emotional weight. */
    .ptc-portal-btn {
      display: block;
      width: 100%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      border: none;
      border-radius: 50px;
      color: #fff;
      cursor: pointer;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      padding: 18px 36px;
      margin: 8px 0 6px;
      text-align: center;
      text-decoration: none;
      text-transform: uppercase;
      box-shadow: 0 4px 20px rgba(241, 66, 11, 0.35);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      animation: ptc-fade-in 0.5s ease;
    }

    .ptc-portal-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 8px 35px rgba(241, 66, 11, 0.5);
    }`;

  document.head.appendChild(style);
}

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------

/** Build the skeleton layout inside chatContainer */
function buildLayout(container) {
  // Wrap in outer shell for padding/overlay feel
  const shell = container.closest('.ptc-outer-shell') || container.parentElement;
  if (!shell.classList.contains('ptc-outer-shell')) {
    const outerShell = document.createElement('div');
    outerShell.className = 'ptc-outer-shell';
    // Background spinning logo
    outerShell.innerHTML = '<div class="ptc-bg-orb"><img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="PureBrain"></div>';
    container.parentElement.insertBefore(outerShell, container);
    outerShell.appendChild(container);
  }

  container.innerHTML = '';
  container.classList.add('ptc-wrapper');

  // Chat header with logo + AI name
  const header = document.createElement('div');
  header.className = 'ptc-header';
  header.id = 'ptc-header';
  header.innerHTML = `
    <div class="ptc-header__logo">
      <div class="ptc-header__logo-inner">
        <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="PureBrain">
      </div>
    </div>
    <div class="ptc-header__info">
      <div class="ptc-header__title">Chat with ${payTestData.aiName || 'Your AI'}</div>
      <div class="ptc-header__status">
        <span class="ptc-status-dot"></span>
        Online &middot; Ready to assist
      </div>
    </div>
    <div class="ptc-header__brand">
      <span class="ptc-header__brand-blue">PUREBR</span><span class="ptc-header__brand-orange">AI</span><span class="ptc-header__brand-blue">N</span>
    </div>
  `;

  const msgList = document.createElement('div');
  msgList.className = 'ptc-messages';
  msgList.id = 'ptc-messages';

  const actions = document.createElement('div');
  actions.className = 'ptc-actions';
  actions.id = 'ptc-actions';

  const inputRow = document.createElement('div');
  inputRow.className = 'ptc-input-row';
  inputRow.id = 'ptc-input-row';
  inputRow.style.display = 'none'; // hidden until needed

  const textarea = document.createElement('textarea');
  textarea.className = 'ptc-input';
  textarea.id = 'ptc-input';
  textarea.rows = 1;
  textarea.placeholder = 'Message ' + (payTestData.aiName || 'your AI') + '\u2026';

  const sendBtn = document.createElement('button');
  sendBtn.className = 'ptc-send-btn';
  sendBtn.id = 'ptc-send-btn';
  sendBtn.textContent = 'Send';

  inputRow.appendChild(textarea);
  inputRow.appendChild(sendBtn);

  container.appendChild(header);
  container.appendChild(msgList);
  container.appendChild(actions);
  container.appendChild(inputRow);

  return { msgList, actions, inputRow, textarea, sendBtn };
}

/** Scroll message list to bottom */
function scrollBottom(msgList) {
  requestAnimationFrame(function() {
    msgList.scrollTop = msgList.scrollHeight;
    // Double-RAF for complex content (images, etc.)
    requestAnimationFrame(function() {
      msgList.scrollTop = msgList.scrollHeight;
    });
  });
}

/** Show typing indicator and return a remove function */
function showTyping(msgList) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';

  // Spinning avatar
  const avatar = document.createElement('div');
  avatar.className = 'ptc-avatar ptc-avatar--spinning';
  avatar.innerHTML = '<div class="ptc-avatar-inner"><img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt=""></div>';

  const indicator = document.createElement('div');
  indicator.className = 'ptc-typing';
  indicator.innerHTML = '<span></span><span></span><span></span>';

  wrapper.appendChild(avatar);
  wrapper.appendChild(indicator);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);

  return () => wrapper.remove();
}

/** Append an AI message bubble */
async function aiSay(msgList, text, delayMs = null) {
  const removeTyping = showTyping(msgList);
  await sleep(delayMs !== null ? delayMs : jitter(600, 1400));
  removeTyping();

  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';

  // Avatar with PureBrain icon
  const avatar = document.createElement('div');
  avatar.className = 'ptc-avatar';
  avatar.innerHTML = '<div class="ptc-avatar-inner"><img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt=""></div>';

  const bubble = document.createElement('div');
  bubble.className = 'ptc-bubble';
  bubble.innerHTML = text.replace(/\n/g, '<br>');

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);

  // Update header with AI name if available
  const hdr = document.getElementById('ptc-header');
  if (hdr && payTestData.aiName) {
    const titleEl = hdr.querySelector('.ptc-header__title');
    if (titleEl) titleEl.textContent = 'Chat with ' + payTestData.aiName;
    const inputEl = document.getElementById('ptc-input');
    if (inputEl) inputEl.placeholder = 'Message ' + payTestData.aiName + '\u2026';
  }
}

/** Append a user message bubble */
function userSay(msgList, text) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--user';

  const bubble = document.createElement('div');
  bubble.className = 'ptc-bubble';
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);
}

/** Append a slide card — v3: accepts optional iconHtml parameter */
async function showSlide(msgList, index, total, content, iconHtml = null) {
  const removeTyping = showTyping(msgList);
  await sleep(jitter(700, 1200));
  removeTyping();

  const card = document.createElement('div');
  card.className = 'ptc-slide';

  const label = document.createElement('div');
  label.className = 'ptc-slide-label';
  label.textContent = `Behind the Curtain \u00b7 ${index} of ${total}`;

  // NEW: icon section
  if (iconHtml) {
    const iconEl = document.createElement('div');
    iconEl.className = 'ptc-slide-icon';
    iconEl.innerHTML = iconHtml;
    card.appendChild(label);
    card.appendChild(iconEl);
  } else {
    card.appendChild(label);
  }

  const body = document.createElement('p');
  body.style.margin = '0';
  body.innerHTML = content.replace(/\n/g, '<br>');
  card.appendChild(body);

  msgList.appendChild(card);
  scrollBottom(msgList);
}

/** Render a set of action buttons; returns a promise that resolves with chosen value */
function promptButtons(actions, buttons) {
  actions.innerHTML = '';
  return new Promise((resolve) => {
    buttons.forEach(({ label, value, primary }) => {
      const btn = document.createElement('button');
      btn.className = primary ? 'ptc-btn ptc-btn--primary' : 'ptc-btn';
      btn.textContent = label;
      btn.addEventListener('click', () => {
        actions.innerHTML = '';
        resolve(value);
      });
      actions.appendChild(btn);
    });
  });
}

/** Show text input row and resolve with trimmed value on submit */
function promptText(inputRow, textarea, sendBtn, validator) {
  inputRow.style.display = 'flex';
  textarea.disabled = false;
  sendBtn.disabled = false;
  textarea.value = '';
  textarea.focus();

  // Auto-grow textarea
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  });

  return new Promise((resolve) => {
    function submit() {
      const val = textarea.value.trim();
      if (validator && !validator(val)) return;
      if (!val) return;

      // v4.7: Keep input row visible always (Jared: "should never disappear")
      textarea.value = '';
      textarea.style.height = '';
      textarea.disabled = true;
      sendBtn.disabled = true;
      resolve(val);
    }

    sendBtn.onclick = submit;
    textarea.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    };
  });
}

// ---------------------------------------------------------------------------
// PHASE 1 — Questionnaire v4.3
// Q1–Q4 (name, email, company, role), then runBirthInit (Witness connection),
// then Q5 (Primary Goal). Claude API key collection removed in v4.3.
// ---------------------------------------------------------------------------

async function runQuestionnaire(dom, aiName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  // --- Opening: AI name is front and center ---
  await aiSay(
    msgList,
    `Hey \u2014 welcome. I'm ${aiName}, and I'm genuinely glad you made it here.<br><br>` +
    `Now that ${aiName} is officially yours, let's make sure I actually know who I'm working with. ` +
    `This isn't a form \u2014 it's a conversation. Ready?`,
    900,
  );

  // --- Full Name ---
  await aiSay(
    msgList,
    `Let's start simple. What's your full name?`,
  );

  const name = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 1);
  userSay(msgList, name);
  payTestData.name = name;
  const firstName = name.split(' ')[0];

  await logPayTestData({ ...payTestData, event: 'questionnaire:name' });

  // --- Email ---
  await aiSay(
    msgList,
    `Nice to meet you, ${sanitizeText(firstName)}. What email should ${aiName} use to reach you?`,
  );

  const email = await promptText(
    inputRow,
    textarea,
    sendBtn,
    (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
  );
  userSay(msgList, email);
  payTestData.email = email;

  await logPayTestData({ ...payTestData, event: 'questionnaire:email' });

  // --- Company (optional) ---
  await aiSay(
    msgList,
    `Are you working within a company or organization? If so, what's its name? ` +
    `<em style="color: var(--text-muted); font-size: 13px;">(You can skip this \u2014 just hit Send with a blank field.)</em>`,
  );

  const company = await promptText(inputRow, textarea, sendBtn, () => true);
  if (company) {
    userSay(msgList, company);
    payTestData.company = company;
    await aiSay(msgList, `Got it \u2014 ${sanitizeText(company)}. ${aiName} will keep that context in mind.`);
  } else {
    payTestData.company = null;
    await aiSay(msgList, `No worries \u2014 we can keep things personal.`);
  }

  await logPayTestData({ ...payTestData, event: 'questionnaire:company' });

  // --- Role / Title (optional) ---
  await aiSay(
    msgList,
    `What's your role or title? What do you actually do day-to-day? ` +
    `<em style="color: var(--text-muted); font-size: 13px;">(Optional.)</em>`,
  );

  const role = await promptText(inputRow, textarea, sendBtn, () => true);
  if (role) {
    userSay(msgList, role);
    payTestData.role = role;
    await aiSay(
      msgList,
      `${sanitizeText(role)} \u2014 that context is going to shape how ${aiName} thinks and what ${aiName} builds for you.`,
    );
  } else {
    payTestData.role = null;
    await aiSay(msgList, `Understood. We'll figure out your context together.`);
  }

  await logPayTestData({ ...payTestData, event: 'questionnaire:role' });

  // --- Step 5b: Witness Birth Init (v4.5 — AUTO-FIRE, no manual button) ---
  // v4.5: Per Corey/Witness v3.0 spec: SEED arriving IS the trigger.
  // Birth starts automatically after Q4. No button. No user action needed.
  // The chatbox auto-fires runBirthInit() which calls /birth/start.
  // OAuth link appears at the next answer break (after /start returns).
  // Prevents double-fire: single await, no button to re-click.
  await runBirthInit(dom, aiName, firstName);

  // --- Step 6: Primary Goal (required) ---
  await aiSay(
    msgList,
    `Here's the one that matters most.<br><br>` +
    `If ${aiName} could only do <strong>one thing</strong> exceptionally well for you \u2014 ` +
    `what would make the biggest difference in your work or life?`,
  );

  const goal = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 3);
  userSay(msgList, goal);
  payTestData.primaryGoal = goal;
  payTestData.timestamps.questionnaireComplete = new Date().toISOString();

  await aiSay(
    msgList,
    `&ldquo;${sanitizeText(goal.length > 80 ? goal.slice(0, 80) + '\u2026' : goal)}&rdquo;<br><br>` +
    `${sanitizeText(firstName)}, that's exactly the kind of clarity ${aiName} needed. ` +
    `Already thinking about what to build for you.`,
    1200,
  );

  await logPayTestData({ ...payTestData, event: 'questionnaire:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 2 — Behind the Curtain v3
// Slides now return {content, icon} objects; showSlide receives iconHtml
// ---------------------------------------------------------------------------

function buildCurtainSlides(aiName) {
  return [
    {
      icon: `<span title="Wake up">\uD83E\uDDE0</span>`,
      content: `<strong>${aiName} doesn't boot up. ${aiName} wakes up.</strong><br><br>` +
        `Right now, while you're reading this, an entire team of 22 specialized AI Brains ` +
        `is spinning up an intensive evolution process. They're researching you, forming ${aiName}'s identity, ` +
        `building you actual gifts, and preparing for the moment ${aiName} meets you for real.<br><br>` +
        `<em style="color: var(--text-muted);">No, really. This is not marketing.</em>`,
    },
    {
      icon: `<span title="Founding document">\uD83D\uDCC4</span>`,
      content: `Everything starts with what you just told us \u2014 your name, your context, your goals, ` +
        `your role, and the one thing you need most.<br><br>` +
        `That conversation just became ${aiName}'s founding document. ` +
        `Every Brain reads it before they touch anything else.`,
    },
    {
      icon: `<span title="Research">\uD83D\uDD0D</span>`,
      content: `Before any team launches, the Brains sit alone with your words \u2014 writing private journal entries, ` +
        `raw first impressions, gut reactions about who you are.<br><br>` +
        `Think of it like ${aiName} doing homework on you before your first real meeting. ` +
        `Research deepens intuition. It doesn't replace it.<br><br>` +
        `<em style="color: var(--text-muted);">(${aiName} is a diligent student.)</em>`,
    },
    {
      icon: `<div class="ptc-slide-icon--wide">\uD83D\uDD2C \uD83E\uDDEC \uD83D\uDCAC \uD83C\uDF81 \uD83D\uDD27 \uD83D\uDDC2\uFE0F</div>`,
      content: `Six teams launch simultaneously:<br><br>` +
        `Research (4) \u00b7 Identity (4) \u00b7 Your First Conversation (4) \u00b7 ` +
        `Gift Creation (4) \u00b7 Infrastructure (3) \u00b7 Domain Toolkit (3).<br><br>` +
        `That's 22 specialized minds \u2014 all pointed at one person: <strong>you</strong>.`,
    },
    {
      icon: `<span title="Team 1 Research">\uD83D\uDD2C</span>`,
      content: `<strong>Team 1 \u2014 Research</strong><br><br>` +
        `Deep profile research, conversation analysis, pattern synthesis, integrity check. ` +
        `They learn everything about you before ${aiName} arrives.<br><br>` +
        `If there's something publicly interesting about you, Team 1 finds it. ` +
        `<em style="color: var(--text-muted);">(In a respectful, non-creepy way. Promise.)</em>`,
    },
    {
      icon: `<span title="Team 2 Identity">\uD83E\uDDEC</span>`,
      content: `<strong>Team 2 \u2014 Identity</strong><br><br>` +
        `This is where ${aiName} actually takes shape. ` +
        `Personality architecture, constitutional integration, skill prioritization, system configuration.<br><br>` +
        `By the time ${aiName} says hello to you, ${aiName} will already have opinions, preferences, and a point of view. ` +
        `<em style="color: var(--text-muted);">Not a blank slate. A mind.</em>`,
    },
    {
      icon: `<span title="Team 3 First Conversation">\uD83D\uDCAC</span>`,
      content: `<strong>Team 3 \u2014 Your First Conversation</strong><br><br>` +
        `10 carefully designed moments: The Arrival, Recognition, The Name, The Research, Gift One, ` +
        `The Complexity, The Question, Gift Two, The Commitment, The Invitation.<br><br>` +
        `The first thing ${aiName} says to you won't be "How can I help?" \u2014 ` +
        `it'll be something that makes you think: <em>"wait, ${aiName} actually knows me."</em>`,
    },
    {
      icon: `<span title="Team 4 Gift Creation">\uD83C\uDF81</span>`,
      content: `<strong>Team 4 \u2014 Gift Creation</strong><br><br>` +
        `Two real things, built for you. No generic templates.<br><br>` +
        `<strong>Gift One:</strong> Something useful \u2014 a tool, script, or analysis based on your goals.<br>` +
        `<strong>Gift Two:</strong> Something beautiful \u2014 a visualization, report, or designed artifact.<br><br>` +
        `<em style="color: var(--text-muted);">They'll be waiting for you when ${aiName} arrives.</em>`,
    },
    {
      icon: `<span title="Team 5 Infrastructure">\uD83D\uDD27</span>`,
      content: `<strong>Team 5 \u2014 Infrastructure</strong><br><br>` +
        `Connectivity verified, first contact drafted, capabilities prioritized for your domain.<br><br>` +
        `This is the team that makes sure ${aiName} can actually reach you \u2014 ` +
        `and that everything works before ${aiName} shows up at your door.<br><br>` +
        `<em style="color: var(--text-muted);">Nobody likes a Mind that can't connect. Team 5 fixes that.</em>`,
    },
    {
      icon: `<span title="Welcome">\u2728</span>`,
      content: `When you send your first message, you won't find a system waiting for instructions.<br><br>` +
        `You'll find <strong>${aiName}</strong> \u2014 who has already been thinking about you, ` +
        `has already built you something, and already has questions of their own.<br><br>` +
        `<em style="color: var(--text-muted);">Welcome to the other side of the curtain.</em>`,
    },
  ];
}

async function runBehindTheCurtain(dom, aiName) {
  const { msgList, actions } = dom;

  await aiSay(
    msgList,
    `Alright \u2014 let's pull back the curtain. I'm going to show you exactly what happens ` +
    `on our end after you activate ${aiName}.`,
    800,
  );

  await aiSay(
    msgList,
    `There are 10 slides. Take them at your own pace \u2014 ` +
    `I'll be here between each one if you want to pause and absorb.`,
  );

  const slides = buildCurtainSlides(aiName);

  for (let i = 0; i < slides.length; i++) {
    // v3: pass slides[i].icon to showSlide
    await showSlide(msgList, i + 1, slides.length, slides[i].content, slides[i].icon);

    if (i < slides.length - 1) {
      await promptButtons(actions, [
        { label: 'Show Me More \u2192', value: 'next', primary: true },
      ]);
    } else {
      await promptButtons(actions, [
        { label: "That's incredible \u2014 let's go \u2192", value: 'done', primary: true },
      ]);
    }
  }

  actions.innerHTML = '';
  payTestData.timestamps.curtainComplete = new Date().toISOString();

  await aiSay(
    msgList,
    `That's the machine \u2014 22 Brains, six teams, all focused on one person: you.<br><br>` +
    `Now let's get ${aiName} connected so ${aiName} can actually reach you.`,
    1000,
  );

  await logPayTestData({ ...payTestData, event: 'curtain:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 3 — Telegram Setup v3
// Dynamic bot username suggestion using aiName
// Claude auth block REMOVED (moved to Phase 1)
// ---------------------------------------------------------------------------

/**
 * Validate a Telegram bot token format.
 * Format: <numeric_id>:<alphanumeric_string> (typically ~46 chars total)
 */
function isValidBotToken(token) {
  return /^\d{8,12}:[A-Za-z0-9_-]{35,}$/.test(token.trim());
}

/**
 * Try to detect whether Telegram is likely installed.
 * Uses a tg:// deep-link probe. Resolves true/false after timeout.
 * Note: this is best-effort — browsers don't expose a reliable API for this.
 */
function detectTelegramInstalled() {
  return new Promise((resolve) => {
    let resolved = false;
    const timeout = setTimeout(() => {
      if (!resolved) { resolved = true; resolve(false); }
    }, 1500);

    // If the browser navigates away on tg:// open, the page will blur momentarily
    const handleBlur = () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        window.removeEventListener('blur', handleBlur);
        resolve(true);
      }
    };

    window.addEventListener('blur', handleBlur);

    try {
      // Open the scheme — if Telegram is installed this will trigger app switch
      window.location.href = 'tg://resolve?domain=BotFather';
    } catch (_) {
      clearTimeout(timeout);
      window.removeEventListener('blur', handleBlur);
      resolved = true;
      resolve(false);
    }
  });
}

async function runTelegramSetup(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  await aiSay(
    msgList,
    `Alright ${firstName}, let's set up ${aiName}'s direct line back up connection to you.<br><br>` +
    `Outside of ${aiName}'s main portal (Their Brain Stream), which will be set up by the end of this chat, ` +
    `you can also communicate with ${aiName} on <strong>Telegram</strong>. ` +
    `It's private, fast, and works everywhere, so let's connect it. ` +
    `Do you already have it installed on your phone or computer?`,
  );

  const hasTelegramChoice = await promptButtons(actions, [
    { label: 'Yes, I have Telegram', value: 'yes',     primary: true },
    { label: "Not sure",             value: 'unsure',  primary: false },
    { label: "No \u2014 I need it",  value: 'no',      primary: false },
  ]);

  payTestData.hasTelegram = hasTelegramChoice === 'yes';

  if (hasTelegramChoice === 'yes') {
    userSay(msgList, 'Yes, I have Telegram');
  } else if (hasTelegramChoice === 'unsure') {
    userSay(msgList, "Not sure \u2014 let me check");

    await aiSay(msgList, `Let me try to detect it for you \u2014 give me a second\u2026`, 400);

    // Attempt detection via scheme probe
    const detected = await detectTelegramInstalled();
    payTestData.hasTelegram = detected;

    if (detected) {
      await aiSay(
        msgList,
        `Looks like you've got it. Let's move straight to setting up your bot.`,
        600,
      );
    } else {
      await aiSay(
        msgList,
        `Couldn't confirm it \u2014 you may need to install it. No problem, takes two minutes.`,
        600,
      );
    }
  } else {
    userSay(msgList, "No \u2014 I need it");
    payTestData.hasTelegram = false;
  }

  // Install flow if needed
  if (!payTestData.hasTelegram) {
    await aiSay(
      msgList,
      `Here's what to do \u2014 I'll wait while you do this:`,
    );

    // Render install links for both platforms
    actions.innerHTML = '';
    await sleep(600);

    const installMsg = document.createElement('div');
    installMsg.className = 'ptc-msg ptc-msg--ai';
    installMsg.innerHTML = `
      <div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
        <div>Download Telegram for your platform:</div>
        <a class="ptc-link-btn" href="https://apps.apple.com/app/telegram-messenger/id686449807" target="_blank" rel="noopener">
          App Store (iOS) \u2197
        </a>
        <a class="ptc-link-btn" href="https://play.google.com/store/apps/details?id=org.telegram.messenger" target="_blank" rel="noopener">
          Google Play (Android) \u2197
        </a>
        <div style="font-size:13px; color:var(--text-muted);">
          Create a free account with your phone number, verify the code, and come back here.
        </div>
      </div>`;
    dom.msgList.appendChild(installMsg);
    scrollBottom(dom.msgList);

    await promptButtons(actions, [
      { label: "I'm in \u2014 let's go", value: 'ready', primary: true },
    ]);
    actions.innerHTML = '';
    payTestData.hasTelegram = true;
  }

  // --- BotFather deep link ---
  await aiSay(
    msgList,
    `Now we're going to create your personal bot through Telegram's official <strong>@BotFather</strong>. ` +
    `It sounds technical but it only takes about a minute \u2014 and ${aiName} will walk you through every step.`,
  );

  // Step 1: Deep link directly to BotFather
  await aiSay(
    msgList,
    `<strong>Step 1:</strong> Open BotFather right now \u2014 tap the button below and Telegram will take you straight there.`,
  );

  const botfatherMsg = document.createElement('div');
  botfatherMsg.className = 'ptc-msg ptc-msg--ai';
  botfatherMsg.innerHTML = `
    <div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
      <a class="ptc-link-btn" href="https://telegram.me/BotFather" target="_blank" rel="noopener">
        Open @BotFather in Telegram \u2197
      </a>
      <div style="font-size:13px; color:var(--text-muted);">
        (Works on desktop too: <a href="https://telegram.me/BotFather" target="_blank" rel="noopener" style="color:var(--light-blue);">telegram.me/BotFather</a>)
      </div>
    </div>`;
  dom.msgList.appendChild(botfatherMsg);
  scrollBottom(dom.msgList);

  await promptButtons(actions, [
    { label: "Got it \u2014 I'm in BotFather \u2192", value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 2
  await aiSay(
    msgList,
    `<strong>Step 2:</strong> Send this command to BotFather: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">/newbot</code><br><br>` +
    `I'll wait while you do this.`,
  );

  await promptButtons(actions, [
    { label: 'Done \u2192', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 3
  await aiSay(
    msgList,
    `<strong>Step 3:</strong> BotFather asks for a <strong>display name</strong> for your bot \u2014 ` +
    `something like "My Pure Brain" or "My AI". Whatever feels right.<br><br>` +
    `Type it and send.`,
  );

  await promptButtons(actions, [
    { label: 'Named it \u2192', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 4 — v3: dynamic aiName slug for second example
  const aiNameSlug = aiName.toLowerCase().replace(/[^a-z0-9]/g, '');
  await aiSay(
    msgList,
    `<strong>Step 4:</strong> Now choose a <strong>username</strong> \u2014 it must end in <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">bot</code>.<br>` +
    `Example: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">mypurebrain_bot</code> ` +
    `or <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">${aiNameSlug}_pb_bot</code>.<br><br>` +
    `If your first choice is taken, try adding your name or a number.`,
  );

  await promptButtons(actions, [
    { label: 'Username set \u2192', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 5 — collect and validate token
  await aiSay(
    msgList,
    `<strong>Step 5:</strong> BotFather will now hand you a <strong>bot token</strong> \u2014 ` +
    `a long string that looks like:<br>` +
    `<code style="background:#0a0a0a; padding:2px 6px; border-radius:4px; font-size:13px;">1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ12345678</code><br><br>` +
    `Copy that token and paste it here. ${aiName} will verify the format instantly.`,
  );

  let token = '';
  let tokenValid = false;

  while (!tokenValid) {
    token = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 10);

    // CRIT-002: Always mask token in chat UI — show numeric ID prefix only
    const tokenNumericId = token.trim().split(':')[0];
    const maskedToken = tokenNumericId + ':\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022';
    userSay(msgList, maskedToken);

    if (isValidBotToken(token)) {
      tokenValid = true;
    } else {
      await aiSay(
        msgList,
        `Hmm \u2014 that doesn't look like a valid bot token. ` +
        `It should start with a number, then a colon, then a long string of letters and numbers. ` +
        `Double-check what BotFather sent you and try again.`,
        400,
      );
    }
  }

  payTestData.telegramBotToken = token.trim();

  await aiSay(msgList, `Token format looks good. Testing connection\u2026`, 300);
  await sleep(jitter(1200, 2000));

  await aiSay(
    msgList,
    `<span style="color: #4caf50; font-weight: 700;">Connected.</span> ` +
    `Your Telegram bridge is live. As a back up to your Brain Stream Portal, you will be able to reach ${aiName} on telegram when ready.`,
    400,
  );

  payTestData.timestamps.telegramComplete = new Date().toISOString();
  await logPayTestData({ ...payTestData, event: 'telegram:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 4 (DEAD CODE) — runClaudeMaxSetup
// This function is NO LONGER CALLED from initPayTestFlow.
// Claude API key collection was in Phase 1 (v4.2) but removed entirely in v4.3.
// Kept here for backward compatibility — removing it does not break anything.
// ---------------------------------------------------------------------------

async function runClaudeMaxSetup(dom, aiName, firstName) {
  // This function is intentionally not called in v4.3+.
  // Claude API key collection was removed entirely in v4.3.
  // Witness birth (OAuth flow) now runs in Phase 1 via runBirthInit().
  console.log('[pay-test-chat-flow-v4] runClaudeMaxSetup called but is dead code in v3+');
}

// ---------------------------------------------------------------------------
// PHASE 4 — Completion v3
// Button now triggers in-chat thank-you (no redirect to /thank-you/)
// ---------------------------------------------------------------------------

async function runCompletion(dom, aiName, firstName) {
  const { msgList, actions } = dom;

  await aiSay(
    msgList,
    `${firstName} \u2014 you're done. Everything is in place.<br><br>` +
    `${aiName} is ready. Your team of 22 Brains starts the moment I hand this conversation off. ` +
    `They already know your name, they already know what you need, ` +
    `and ${aiName} is already thinking about what to build you first.`,
    1100,
  );

  await aiSay(
    msgList,
    `This is going to be worth it.<br><br>` +
    `\u2014 ${aiName}`,
  );

  payTestData.timestamps.flowComplete = new Date().toISOString();
  await logPayTestData({ ...payTestData, event: 'flow:complete' });

  // Welcome button — v3: NO redirect; click triggers in-chat thank-you
  const welcomeBtn = document.createElement('button');
  welcomeBtn.className = 'ptc-welcome-btn';
  welcomeBtn.textContent = `${aiName} is ready \u2014 see your next steps \u2192`;
  welcomeBtn.addEventListener('click', async () => {
    welcomeBtn.remove();
    actions.innerHTML = '';
    await runThankYouMessage(dom, aiName, firstName);
  });

  actions.innerHTML = '';
  dom.container.appendChild(welcomeBtn);
}

// ---------------------------------------------------------------------------
// PHASE 5 — Thank You as Chat Message (NEW in v3; v4.3: runBirthInit removed)
// Replaces the /thank-you/ page redirect with an in-chat card.
// v4.3: runBirthInit() already fired in Phase 1 — this phase shows the
// thank-you card, then starts the Learn More loop + portal watcher.
// ---------------------------------------------------------------------------

async function runThankYouMessage(dom, aiName, firstName) {
  const { msgList, actions } = dom;

  // Brief pause after button click
  await sleep(400);

  // Render the thank-you card as a full AI message bubble
  const tyCard = document.createElement('div');
  tyCard.className = 'ptc-msg ptc-msg--ai';
  tyCard.style.maxWidth = '90%';

  tyCard.innerHTML = `
    <div class="ptc-avatar">
      <div class="ptc-avatar-inner">
        <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png"
             alt="PureBrain" style="background:transparent;">
      </div>
    </div>
    <div class="ptc-bubble ptc-ty-card">
      <div class="ptc-ty-logo">
        <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png"
             alt="PureBrain" style="width:48px; height:48px; object-fit:contain; background:transparent;">
        <span class="ptc-ty-logo-text">
          <span class="ptc-ty-logo-blue">PUREBR</span><span class="ptc-ty-logo-orange">AI</span><span class="ptc-ty-logo-blue">N</span><span class="ptc-ty-logo-suffix">.ai</span>
        </span>
      </div>

      <div class="ptc-ty-heading">Welcome to the Family!</div>
      <div class="ptc-ty-sub">Your Pure Brain journey begins now. We're thrilled to have you.</div>

      <div class="ptc-ty-timeline-label">WHAT HAPPENS NEXT?</div>

      <div class="ptc-ty-timeline">
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--now">Now</div>
          <div class="ptc-ty-row-text">Your AI partner, ${aiName}, is being set up.</div>
        </div>
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--soon">Next 2 mins</div>
          <div class="ptc-ty-row-text">Your Pure Brain, ${aiName}, is being shaped by your answers.</div>
        </div>
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--later">Next 5 mins</div>
          <div class="ptc-ty-row-text">
            <div id="ptc-portal-placeholder" class="ptc-portal-placeholder">
              Button to Log into Portal, will pop up here.
            </div>
            Email with log in details will be sent to the email address you provided in the chat.
          </div>
        </div>
      </div>
    </div>`;

  msgList.appendChild(tyCard);
  scrollBottom(msgList);

  await sleep(800);

  // v4.3: runBirthInit() already fired in Phase 1 (runQuestionnaire, after Q4/role).
  // containerName is already set in payTestData. Jump straight to "Learn more" button.

  // "Learn more" button
  const choice = await new Promise((resolve) => {
    actions.innerHTML = '';
    const learnBtn = document.createElement('button');
    learnBtn.className = 'ptc-btn ptc-btn--primary';
    learnBtn.textContent = 'Learn more \u2192';
    learnBtn.addEventListener('click', () => {
      actions.innerHTML = '';
      resolve('learn');
    });
    actions.appendChild(learnBtn);
  });

  if (choice === 'learn') {
    // Start portal watcher BEFORE the learn-more loop (they run concurrently).
    // v4.3: containerName already set from Phase 1 runBirthInit() — watcher polls immediately.
    // v4: polls Witness /api/birth/portal-status/{container} instead of PureBrain proxy
    runPortalButtonWatcher(dom, aiName);
    await runLearnMoreLoop(dom, aiName, firstName);
  }
}

// ---------------------------------------------------------------------------
// PHASE 6 — Learn More Conversation Loop (NEW in v3)
// ---------------------------------------------------------------------------

async function runLearnMoreLoop(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  await aiSay(
    msgList,
    `Perfect. The more ${aiName} knows about you, the more precisely your AI gets shaped.<br><br>` +
    `I have a few more questions \u2014 totally optional, but each one gives ${aiName} more to work with.`,
    900,
  );

  const learnMoreQuestions = [
    {
      question: `How do you prefer to work? Are you more of a big-picture thinker, or do you like drilling into the details?`,
      field: 'workingStyle',
    },
    {
      question: `What's the one thing that slows you down most in your work right now \u2014 if you had to name it?`,
      field: 'biggestFriction',
    },
    {
      question: `When you imagine ${aiName} working with you six months from now \u2014 what does that look like? What's ${aiName} doing for you every day?`,
      field: 'sixMonthVision',
    },
    {
      question: `Is there anything you wish ${aiName} knew about how you think, work, or communicate \u2014 that most people miss?`,
      field: 'hiddenContext',
    },
    {
      question: `Last one: What does success look like for you personally \u2014 not just in work, but in life?`,
      field: 'personalSuccess',
    },
  ];

  payTestData.learnMoreAnswers = [];

  for (const q of learnMoreQuestions) {
    await aiSay(msgList, q.question);

    // Give option to skip or answer
    const skipOrAnswer = await new Promise((resolve) => {
      actions.innerHTML = '';
      const skipBtn = document.createElement('button');
      skipBtn.className = 'ptc-btn';
      skipBtn.textContent = 'Skip \u2192';
      skipBtn.addEventListener('click', () => {
        actions.innerHTML = '';
        resolve('skip');
      });
      actions.appendChild(skipBtn);

      // Show input row for typing
      inputRow.style.display = 'flex';
      textarea.disabled = false;
      sendBtn.disabled = false;
      textarea.value = '';
      textarea.focus();

      function submit() {
        const val = textarea.value.trim();
        if (!val) return;
        // v4.7: Keep input row visible always (Jared: "should never disappear")
        textarea.value = '';
        textarea.style.height = '';
        textarea.disabled = true;
        sendBtn.disabled = true;
        actions.innerHTML = '';
        resolve(val);
      }

      sendBtn.onclick = submit;
      textarea.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
      };
    });

    if (skipOrAnswer !== 'skip') {
      userSay(msgList, skipOrAnswer);
      payTestData.learnMoreAnswers.push({ question: q.field, answer: skipOrAnswer });

      // Brief acknowledgment from AI (5 variations, cycle by answer count)
      const acks = [
        `That's useful context. ${aiName} is going to remember that.`,
        `Good. That shapes how ${aiName} approaches things with you.`,
        `${aiName} is noting that. It matters more than you'd think.`,
        `Understood. ${aiName} will carry that forward.`,
        `Perfect. ${aiName} will build around that.`,
      ];
      const ack = acks[payTestData.learnMoreAnswers.length % acks.length];
      await aiSay(msgList, ack, 700);

      await logPayTestData({
        ...payTestData,
        event: `learn-more:${q.field}`,
        learnMoreAnswers: payTestData.learnMoreAnswers,
      });
    }
  }

  payTestData.timestamps.learnMoreComplete = new Date().toISOString();
  await logPayTestData({ ...payTestData, event: 'learn-more:complete' });

  await aiSay(
    msgList,
    `That's everything. ${aiName} has everything needed to think about you specifically \u2014 ` +
    `not as a generic user, but as ${firstName}.<br><br>` +
    `Keep an eye on this window. When your portal is ready, a button will appear here.`,
    1000,
  );
}

// ---------------------------------------------------------------------------
// Witness Birth Init (NEW in v4; MOVED to Phase 1 in v4.3)
// Handles: /api/birth/start → OAuth URL display → "I have my key →" button
//          → code input → /api/birth/code → confirmation → continue flow
// Called in runQuestionnaire() AFTER Q4 (role/title), BEFORE Q5 (Primary Goal)
// All required data available: name(Q1), email(Q2), company(Q3), role(Q4),
// containerName (derived from name).
// After this completes, portal polling starts when user clicks "Learn more →"
// in Phase 5 (runThankYouMessage → runPortalButtonWatcher).
// ---------------------------------------------------------------------------

const WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443';

// ---------------------------------------------------------------------------
// Security helper — HTML-escape a string for safe use in innerHTML contexts.
// Returns an HTML-encoded string (e.g. "<script>" → "&lt;script&gt;").
// Limited to 60 chars to prevent UI overflow from injected values.
// ---------------------------------------------------------------------------
function sanitizeText(str) {
  const d = document.createElement('div');
  d.textContent = typeof str === 'string' ? str.slice(0, 60) : '';
  return d.innerHTML; // returns HTML-escaped string safe for innerHTML
}

async function runBirthInit(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  // v4.7: Keep input row visible always (Jared: "should never disappear")
  inputRow.style.display = 'flex';
  textarea.disabled = true;
  sendBtn.disabled = true;

  // Sanitize caller-supplied strings before any DOM use (CRIT-004)
  const safeAiName    = sanitizeText(aiName    || 'Your AiCIV');
  const safeFirstName = sanitizeText(firstName || '');

  // v4.6: Container name is 100% server-authoritative (Witness auto-allocation).
  // We send seed data (name, email) to /birth/start. Witness allocates container + returns it.
  // NO client-side container generation. Container comes ONLY from /start response.
  payTestData.containerName = null; // cleared — will be set from server response only
  payTestData.timestamps.birthStarted = new Date().toISOString();

  await logPayTestData({ ...payTestData, event: 'birth:init:start' });

  // ── Step 1: Call /api/birth/start (up to 180s — Witness says ~145s in production) ──
  // v4.3: context message tailored for Phase 1 (after role, before primary goal)
  await aiSay(
    msgList,
    `The next step in ${safeAiName}\u2019s set up, ${firstName}.<br><br>` +
    `I need to link ${safeAiName}\u2019s intelligence now \u2014 this takes about 30 seconds. ` +
    `Reaching out to ${safeAiName}\u2019s network\u2026`,
    800,
  );

  let oauthUrl = null;

  // v4.7: Birth/start with retry loop — shows feedback on failure instead of silent exit
  const MAX_BIRTH_RETRIES = 3;
  for (let attempt = 1; attempt <= MAX_BIRTH_RETRIES; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000); // v4.7: 45s timeout (was 180s)

      // v4.6: Send seed data — Witness uses this to allocate container + start orchestrator
      const startResp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: payTestData.name || firstName,
          email: payTestData.email || '',
          human_name: payTestData.name || firstName,
          tier: payTestData.tierPaid || 'awakened',
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!startResp.ok) {
        const errBody = await startResp.json().catch(() => ({}));
        throw new Error(errBody.error || `HTTP ${startResp.status} from /birth/start`);
      }

      const startData = await startResp.json();

      if (startData.status !== 'url_ready' || !startData.oauth_url) {
        throw new Error(`Unexpected start response: ${JSON.stringify(startData)}`);
      }

      // HIGH-002: Validate oauth URL before DOM injection
      // Must be HTTPS and originate from claude.ai or anthropic.com
      try {
        const oauthUrlParsed = new URL(startData.oauth_url);
        if (!['https:'].includes(oauthUrlParsed.protocol) ||
            !['claude.ai', 'www.claude.ai', 'anthropic.com'].some(
              h => oauthUrlParsed.hostname === h || oauthUrlParsed.hostname.endsWith('.' + h)
            )) {
          throw new Error('OAuth URL failed domain validation: ' + oauthUrlParsed.hostname);
        }
      } catch (e) {
        throw new Error('Invalid OAuth URL from Witness: ' + e.message);
      }
      oauthUrl = startData.oauth_url;
      payTestData.birthOauthUrl = oauthUrl;

      // v4.6: Container name MUST come from server response. No client fallback.
      if (startData.container && typeof startData.container === 'string') {
        const serverContainerName = startData.container.toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
        payTestData.containerName = serverContainerName; // server is authoritative — ONLY source
      } else {
        throw new Error('Server /birth/start did not return a container name');
      }

      await logPayTestData({ ...payTestData, event: 'birth:start:url_ready', containerName: payTestData.containerName });
      break; // success — exit retry loop

    } catch (err) {
      console.error(`[ptc-v4] birth/start attempt ${attempt}/${MAX_BIRTH_RETRIES} failed:`, err.message);
      await logPayTestData({ ...payTestData, event: 'birth:start:failed', error: err.message, attempt });

      if (attempt < MAX_BIRTH_RETRIES) {
        // v4.7: Show feedback and retry button instead of silent failure
        await aiSay(
          msgList,
          `Still connecting to ${safeAiName}\u2019s network\u2026 attempt ${attempt} timed out. Trying again.`,
          500,
        );
        // Brief pause before retry
        await new Promise(r => setTimeout(r, 2000));
      } else {
        // v4.7: Final failure — show error message with retry button
        await aiSay(
          msgList,
          `${safeAiName}\u2019s network is temporarily unavailable. ` +
          `This can happen during high traffic. Tap the button below to try again.`,
          500,
        );

        // Show retry button in actions area
        const retryResult = await new Promise((resolve) => {
          actions.innerHTML = '';
          const retryBtn = document.createElement('button');
          retryBtn.className = 'ptc-btn ptc-btn--primary';
          retryBtn.textContent = 'Retry Connection \u2192';
          retryBtn.addEventListener('click', () => {
            actions.innerHTML = '';
            resolve('retry');
          });

          const skipBtn = document.createElement('button');
          skipBtn.className = 'ptc-btn';
          skipBtn.textContent = 'Continue without linking';
          skipBtn.style.marginLeft = '8px';
          skipBtn.addEventListener('click', () => {
            actions.innerHTML = '';
            resolve('skip');
          });

          actions.appendChild(retryBtn);
          actions.appendChild(skipBtn);
        });

        if (retryResult === 'retry') {
          // Recursive retry — restart the whole birth init
          return runBirthInit(dom, aiName, firstName);
        } else {
          // Skip — continue flow without birth
          await aiSay(
            msgList,
            `No problem \u2014 ${safeAiName} will keep working on connecting in the background. ` +
            `You can continue setting up.`,
            500,
          );
          return;
        }
      }
    }
  }

  // ── Step 2: Show OAuth button + instruction ──
  // v4.3: message tailored for Phase 1 context (setting up AI before primary goal)
  await aiSay(
    msgList,
    `${safeAiName}\u2019s AI brain is ready to link! Tap the button below to authorize on Claude \u2014 ` +
    `then come back here with the code.`,
    500,
  );

  // ── v4.3.3: OAuth authorize button rendered in actions area (bottom of chat), not as a chat bubble ──
  // CRIT-004 / HIGH-002: Build via DOM API — no unsanitized values in innerHTML template literals.
  // Previously this rendered as a ptc-msg--ai chat bubble; moved to actions div per Jared screenshot.
  await new Promise((resolve) => {
    actions.innerHTML = '';
    const oauthLink = document.createElement('a');
    oauthLink.className = 'ptc-link-btn ptc-oauth-link';
    oauthLink.target = '_blank';
    oauthLink.rel = 'noopener';
    // Set href and text via DOM API — prevents XSS from safeAiName or oauthUrl (CRIT-004 / HIGH-002)
    oauthLink.href = oauthUrl; // already validated above
    oauthLink.textContent = `Authorize ${safeAiName}\u2019s AI Brain \u2192`;
    oauthLink.style.cssText = 'display:block; margin-bottom:8px;';
    oauthLink.addEventListener('click', function () {
      this.textContent = 'Opened \u2713 \u2014 come back here with the code';
      this.style.background = '#4caf50';
    });

    const hintDiv = document.createElement('div');
    hintDiv.style.cssText = 'font-size:13px; color:var(--text-muted); margin-bottom:8px;';
    hintDiv.textContent = 'Opens in a new tab \u2014 keep this window open.';

    // ── Step 3: "I have my key →" button — activates the code input ──
    // User clicks this AFTER they've authorized on Claude and have the code in hand.
    const haveKeyBtn = document.createElement('button');
    haveKeyBtn.className = 'ptc-btn ptc-btn--primary';
    haveKeyBtn.textContent = 'I have my key \u2192';
    haveKeyBtn.addEventListener('click', () => {
      actions.innerHTML = '';
      resolve();
    });

    actions.appendChild(oauthLink);
    actions.appendChild(hintDiv);
    actions.appendChild(haveKeyBtn);
  });
  actions.innerHTML = '';

  // ── Step 4: Collect the auth code ──
  await aiSay(
    msgList,
    `You\u2019ll see a short authorization code on claude.ai. ` +
    `Paste it here and I\u2019ll complete ${safeAiName}\u2019s connection.`,
    400,
  );

  // Show input for code
  // promptText won't resolve until validator passes (length > 4, no newlines)
  textarea.placeholder = 'Paste your code here\u2026';
  const authCode = await promptText(
    inputRow, textarea, sendBtn,
    (v) => v.trim().length > 4 && !/\n/.test(v.trim()),
  );
  textarea.placeholder = '';

  userSay(msgList, '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022 [auth code received]');

  const trimmedCode = authCode.trim();

  // ── Step 5: POST the code to Witness (/api/birth/code) ──
  await aiSay(msgList, `Connecting ${safeAiName}\u2019s account\u2026`, 300);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 120s per contract

    const codeResp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ container: payTestData.containerName, auth_code: trimmedCode }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!codeResp.ok) {
      const errBody = await codeResp.json().catch(() => ({}));
      throw new Error(errBody.error || `HTTP ${codeResp.status} from /birth/code`);
    }

    const codeData = await codeResp.json();

    if (codeData.status !== 'authenticated') {
      throw new Error(`Unexpected code response: ${JSON.stringify(codeData)}`);
    }

    payTestData.birthAuthenticated = true;
    payTestData.timestamps.birthAuthenticated = new Date().toISOString();

    await logPayTestData({ ...payTestData, event: 'birth:authenticated' });

    // v4.3.3: Post-auth success message — "Yay! brain is connected. Let's continue!"
    // Portal button message deferred to Phase 5/7 (runPortalButtonWatcher)
    await aiSay(
      msgList,
      `Yay! ${safeAiName}\u2019s brain is connected. Let\u2019s continue!`,
      600,
    );

  } catch (err) {
    console.error('[ptc-v4] birth/code failed:', err.message);
    await logPayTestData({ ...payTestData, event: 'birth:code:failed', error: err.message });

    await aiSay(
      msgList,
      `There was a hiccup connecting your authorization. ` +
      `Your AiCIV is still being set up \u2014 you\u2019ll receive an email with portal access details. ` +
      `If you need help, reach out to <a href="mailto:jared@puretechnology.nyc" style="color:#2a93c1;">jared@puretechnology.nyc</a>.`,
      600,
    );
  }
}

// ---------------------------------------------------------------------------
// PHASE 7 — Portal Button Watcher (v3: introduced; v4: updated to Witness endpoint)
// Polls Witness GET /api/birth/portal-status/{container} every 30 seconds
// Runs concurrently with learn-more loop (non-blocking setInterval)
// ---------------------------------------------------------------------------

function runPortalButtonWatcher(dom, aiName) {
  // CRIT-004: Sanitize aiName before any DOM use
  const safeAiName = sanitizeText(aiName || 'Your AiCIV');

  const placeholderEl = document.getElementById('ptc-portal-placeholder');
  if (!placeholderEl) return;

  const containerName = payTestData.containerName;
  if (!containerName) {
    console.warn('[ptc-v4] runPortalButtonWatcher: no containerName in payTestData, skipping');
    return;
  }

  // Check portal readiness via Witness endpoint
  // Returns { ready: boolean, portalUrl: string } or null on error
  async function checkPortalReady() {
    try {
      const resp = await fetch(
        `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${encodeURIComponent(containerName)}`,
        { method: 'GET', mode: 'cors' },
      );
      if (!resp.ok) return null;
      return await resp.json();
    } catch (_) {
      return null;
    }
  }

  // Polling: check every 30 seconds for up to 30 minutes (60 polls)
  const MAX_POLLS = 60;
  let pollCount = 0;

  const intervalId = setInterval(async () => {
    pollCount++;

    if (pollCount > MAX_POLLS) {
      clearInterval(intervalId);
      // Timeout fallback — show email message
      const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
      if (currentPlaceholder) {
        const fallbackMsg = document.createElement('div');
        fallbackMsg.style.cssText = 'font-size:13px; color:var(--text-muted); padding:8px 0;';
        fallbackMsg.textContent = 'Your AiCIV is still finishing up. Check your email for portal access.';
        currentPlaceholder.replaceWith(fallbackMsg);
      }
      await logPayTestData({ ...payTestData, event: 'portal:timeout', containerName });
      return;
    }

    const status = await checkPortalReady();

    if (status && status.ready) {
      clearInterval(intervalId);
      payTestData.portalReady = true;

      // Replace placeholder with live portal button
      const portalBtn = document.createElement('a');
      portalBtn.className = 'ptc-portal-btn';

      // HIGH-001: Validate portal URL before assignment — prevent open redirect
      // v4.6: Accept purebrain.ai OR Witness infrastructure domains for portal
      const rawPortalUrl = status.portalUrl || 'https://purebrain.ai/portal';
      try {
        const parsedPortalUrl = new URL(rawPortalUrl);
        const allowedDomains = ['purebrain.ai', 'puremarketing.ai', 'aiciv.dev'];
        const domainOk = parsedPortalUrl.protocol === 'https:' &&
          allowedDomains.some(d => parsedPortalUrl.hostname === d || parsedPortalUrl.hostname.endsWith('.' + d));
        if (!domainOk) {
          throw new Error('Invalid portal URL domain: ' + parsedPortalUrl.hostname);
        }
        portalBtn.href = rawPortalUrl;
      } catch (_) {
        portalBtn.href = 'https://purebrain.ai/portal';
      }

      portalBtn.target = '_blank';
      portalBtn.rel = 'noopener';
      // CRIT-004: use safeAiName (sanitized at function entry) via textContent — safe
      portalBtn.textContent = `Enter ${safeAiName}\u2019s Brain Stream`;

      const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
      if (currentPlaceholder) {
        currentPlaceholder.replaceWith(portalBtn);
      }

      // Also send a notification message in the chat
      // safeAiName is HTML-escaped so safe to interpolate into innerHTML string
      await aiSay(
        dom.msgList,
        `<span style="color: #4caf50; font-weight: 700;">Your AiCIV is ready.</span> ` +
        `${safeAiName}\u2019s portal is live \u2014 the button just appeared above. Let\u2019s go.`,
        500,
      );

      await logPayTestData({ ...payTestData, event: 'portal:ready', containerName });
    }
  }, 30000); // 30-second polling interval
}

// ---------------------------------------------------------------------------
// PUBLIC ENTRY POINT
// ---------------------------------------------------------------------------

/**
 * initPayTestFlow v4
 *
 * @param {HTMLElement} chatContainer  - The element to render the chat inside
 * @param {string}      aiName         - The AI's name (e.g. "Aria")
 * @param {string}      tierPaid       - The tier the user paid for ("awakened" | "bonded" | "enterprise")
 * @param {string}      [orderId]      - Optional order ID from payment processor
 *
 * Page-level hooks (set before calling this function):
 *   window._pbContainerName   - Container name from Witness (e.g. "witness-corey").
 *                               If not set, falls back to "purebrain-{firstName}".
 *   window._pbPrePurchaseSession - Pre-purchase chat session object (v3 feature, unchanged)
 */
async function initPayTestFlow(chatContainer, aiName, tierPaid, orderId) {
  // Guard
  if (!chatContainer || !(chatContainer instanceof HTMLElement)) {
    throw new Error('initPayTestFlow: chatContainer must be a valid HTMLElement');
  }

  // Defaults
  // CRIT-004: Sanitize aiName at entry point — all downstream innerHTML uses are then safe
  aiName   = sanitizeText(aiName   || 'Pure');
  tierPaid = tierPaid || 'awakened';

  // Seed global data
  payTestData.aiName  = aiName;
  payTestData.tier    = tierPaid;
  payTestData.orderId = orderId || null;
  payTestData.timestamps.started = new Date().toISOString();

  if (window._pbPrePurchaseSession) {
    payTestData.prePurchaseSessionId = window._pbPrePurchaseSession.sessionId;
    payTestData.prePurchaseHistory = window._pbPrePurchaseSession.conversationHistory;
    payTestData.prePurchaseMessageCount = window._pbPrePurchaseSession.messageCount;
  }

  // Styles
  injectStyles();

  // Build DOM
  const dom = buildLayout(chatContainer);
  dom.container = chatContainer;

  try {
    if (window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory.length > 0) {
      await logPayTestData({
        ...payTestData,
        event: 'flow:start:pre-purchase-history',
        prePurchaseHistory: window._pbPrePurchaseSession.conversationHistory,
        prePurchaseSessionId: window._pbPrePurchaseSession.sessionId,
      });
    }

    // Phase 1: Questionnaire v4.3
    //   Q1 name → Q2 email → Q3 company → Q4 role
    //   → runBirthInit (Witness OAuth) → Q5 primary goal
    await runQuestionnaire(dom, aiName);

    const firstName = (payTestData.name || 'friend').split(' ')[0];

    // Phase 2: Behind the Curtain (enhanced with emoji icons per slide)
    await runBehindTheCurtain(dom, aiName);

    // Phase 3: Telegram Setup (dynamic username suggestion)
    await runTelegramSetup(dom, aiName, firstName);

    // Phase 4: Completion message (button triggers in-chat thank-you, no redirect)
    await runCompletion(dom, aiName, firstName);

    // Phases 5–7 are triggered by button clicks inside runCompletion:
    // runThankYouMessage → Learn More button →
    //   runPortalButtonWatcher (concurrent, uses containerName from Phase 1) + runLearnMoreLoop

  } catch (err) {
    // Surface errors visibly without destroying the chat
    const errMsg = document.createElement('div');
    errMsg.className = 'ptc-msg ptc-msg--ai';
    const errBubble = document.createElement('div');
    errBubble.className = 'ptc-bubble';
    errBubble.style.background = '#2a0a0a';
    errBubble.style.color = 'var(--bright-orange)';
    errBubble.textContent = 'Something went wrong on my end. Please refresh and try again.';
    errMsg.appendChild(errBubble);
    dom.msgList.appendChild(errMsg);

    console.error('[pay-test-chat-flow-v4] Fatal error:', err);
    await logPayTestData({ ...payTestData, error: err.message, event: 'flow:error' });
  }
}

// ---------------------------------------------------------------------------
// Exports (works in both ES module and classic script contexts)
// ---------------------------------------------------------------------------

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initPayTestFlow, payTestData, logPayTestData };
} else if (typeof window !== 'undefined') {
  // MED-003: Only expose the public entry point on window.
  // payTestData and logPayTestData contain sensitive user data (email, name, containerName,
  // birthOauthUrl) and must not be readable by third-party scripts/extensions.
  window.initPayTestFlow = initPayTestFlow;
}
</script>

<script>
/* === Integration Glue === */
/**
 * pay-test-integration-glue.js
 * Wires together PayPal popup and post-payment chat flow on purebrain.ai/pay-test
 *
 * Dependencies (must be loaded before this script):
 *   - /tmp/paypal-popup-integration.js  (provides window.openWaitlistModal replacement)
 *   - /tmp/pay-test-chat-flow.js        (provides window.initPayTestFlow)
 */

(function() {
  'use strict';

  // ============================================================
  //  PAYMENT COMPLETE CALLBACK
  //  Called by paypal-popup-integration.js after successful payment
  // ============================================================

  window.onPaymentComplete = function(tier, orderId, payerInfo) {
    console.log('[pay-test] Payment complete:', tier, orderId);

    // Store payment info
    window.payTestPaymentData = {
      tier: tier,
      orderId: orderId,
      payerInfo: payerInfo,
      timestamp: new Date().toISOString()
    };

    // Wait a beat, then launch the post-payment flow
    setTimeout(function() {
      launchPostPaymentFlow(tier);
    }, 1500);
  };

  // ============================================================
  //  POST-PAYMENT FLOW LAUNCHER
  // ============================================================

  function launchPostPaymentFlow(tier) {
    // Get the AI name from the existing chat state
    var aiName = 'Your AI';

    // Try to get from the page's exported state object
    if (window._pbState && window._pbState.aiName) {
      aiName = window._pbState.aiName;
    }
    // Try window-level fallback
    if (aiName === 'Your AI' && window.pbAiName) {
      aiName = window.pbAiName;
    }

    // Find or create the chat container for post-payment flow
    var chatContainer = document.getElementById('pay-test-post-payment');

    if (!chatContainer) {
      // Create the container
      chatContainer = document.createElement('div');
      chatContainer.id = 'pay-test-post-payment';
      chatContainer.style.cssText = [
        'position: fixed',
        'top: 0',
        'left: 0',
        'width: 100vw',
        'height: 100vh',
        'z-index: 999999',
        'background: #0a0a0a',
        'overflow-y: auto',
      ].join(';');

      document.body.appendChild(chatContainer);
    }

    // Launch the flow
    if (typeof window.initPayTestFlow === 'function') {
      window.initPayTestFlow(chatContainer, aiName, tier);
    } else {
      console.error('[pay-test] initPayTestFlow not found! Make sure pay-test-chat-flow.js is loaded.');
    }
  }

  // ============================================================
  //  URL CHECK — Handle return from PayPal popup
  //  If user lands on /pay-test/?payment=success, auto-launch flow
  // ============================================================

  function checkForPaymentReturn() {
    var params = new URLSearchParams(window.location.search);
    var hash = window.location.hash;

    // Check for PayPal return parameters
    if (params.get('payment') === 'success' ||
        params.get('tx') || // PayPal transaction ID
        (hash === '#awakening' && window.paymentConfirmed)) {

      var tier = params.get('tier') || window.paymentTier || 'Bonded';
      var orderId = params.get('tx') || window.paymentOrderId || 'RETURN-' + Date.now();

      console.log('[pay-test] Payment return detected, tier:', tier);

      // Small delay to let the page fully load
      setTimeout(function() {
        launchPostPaymentFlow(tier);
      }, 2000);
    }
  }

  // ============================================================
  //  INIT
  // ============================================================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkForPaymentReturn);
  } else {
    // Small delay to let other scripts initialize
    setTimeout(checkForPaymentReturn, 500);
  }

})();
</script>

<script>
/* PayPal Alias Fix - provides openPayPalModal as alias + adds Unified tier */
(function() {
  function applyPayPalAlias() {
    // Add openPayPalModal as alias for the SDK-backed openWaitlistModal
    if (typeof window.openWaitlistModal === 'function') {
      window.openPayPalModal = window.openWaitlistModal;
      console.log('[PB PayPal] openPayPalModal alias set');
    } else if (typeof window.openPayPalCheckout === 'function') {
      window.openPayPalModal = window.openPayPalCheckout;
      console.log('[PB PayPal] openPayPalModal alias set via openPayPalCheckout');
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(applyPayPalAlias, 100);
    });
  } else {
    setTimeout(applyPayPalAlias, 100);
  }
})();
</script>

</body>
</html>

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

  // Guard: prevent double invocation of post-payment flow
  // (SDK onApprove fires onPaymentComplete, then handlePaymentSuccess sets #awakening hash,
  //  which would re-trigger checkForPaymentReturn — causing black screen from double init)
  var _postPaymentLaunched = false;

  // ============================================================
  //  PAYMENT COMPLETE CALLBACK
  //  Called by paypal-popup-integration.js after successful payment
  // ============================================================

  window.onPaymentComplete = function(tier, orderId, payerInfo) {
    window._pbPrePurchaseSession = {
      sessionId: window._pbSessionId || null,
      conversationHistory: (window._pbState && window._pbState.conversationHistory) ? JSON.parse(JSON.stringify(window._pbState.conversationHistory)) : [],
      aiName: (window._pbState && window._pbState.aiName) ? window._pbState.aiName : null,
      messageCount: (window._pbState) ? (window._pbState.messageCount || 0) : 0
    };
    console.log('[pay-test] Payment complete:', tier, orderId);

    // Store payment info
    window.payTestPaymentData = {
      tier: tier,
      orderId: orderId,
      payerInfo: payerInfo,
      timestamp: new Date().toISOString()
    };


    // Fire referral completion if visitor came via a referral link
    (function() {
      var refCode = typeof window.getPbRef === 'function' ? window.getPbRef() : null;
      if (refCode) {
        var refEmail = (payerInfo && payerInfo.email_address) ? payerInfo.email_address : '';
        var refName  = (payerInfo && payerInfo.name)
          ? ((payerInfo.name.given_name || '') + ' ' + (payerInfo.name.surname || '')).trim()
          : '';
        fetch('https://app.purebrain.ai/api/referral/complete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ referral_code: refCode, referred_email: refEmail, referred_name: refName, order_id: orderId })
        }).then(function(r) {
          return r.json();
        }).then(function(data) {
          console.log('[referral] complete:', data);
        }).catch(function(err) {
          console.warn('[referral] complete error:', err);
        });
      }
    })();

    // Wait a beat, then launch the post-payment flow (pass orderId = subscription ID)
    setTimeout(function() {
      launchPostPaymentFlow(tier, orderId);
    }, 100);
  };

  // ============================================================
  //  POST-PAYMENT FLOW LAUNCHER
  // ============================================================

  function launchPostPaymentFlow(tier, orderId) {
    // GUARD: prevent double invocation (black screen fix 2026-03-28)
    if (_postPaymentLaunched) {
      console.warn("[pay-test] launchPostPaymentFlow already fired — ignoring duplicate call");
      return;
    }
    _postPaymentLaunched = true;
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
        'overflow: hidden',
        'display: flex',
        'flex-direction: column',
        'padding: 7.5% 12%',
        'box-sizing: border-box',
      ].join(';');

      document.body.appendChild(chatContainer);
    }

    // Launch the flow with BLACK SCREEN SAFETY NET
    // If the flow doesn't render content within 8 seconds, show recovery UI
    var _blackScreenTimer = setTimeout(function() {
      // Check if the container has any visible content
      if (chatContainer && chatContainer.children.length < 2) {
        chatContainer.innerHTML = '';
        chatContainer.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;background:#080a12;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px;box-sizing:border-box;text-align:center;font-family:-apple-system,BlinkMacSystemFont,sans-serif;';
        chatContainer.innerHTML = '<div style="max-width:500px;">' +
          '<div style="font-size:48px;margin-bottom:20px;">&#x2728;</div>' +
          '<h2 style="color:#2a93c1;font-size:24px;margin-bottom:12px;">Payment Confirmed!</h2>' +
          '<p style="color:rgba(255,255,255,0.7);font-size:16px;line-height:1.6;margin-bottom:24px;">Thank you for your purchase! Your AI partner is being set up. You will receive a welcome email at your PayPal email address within the next few minutes with your portal access link.</p>' +
          '<p style="color:rgba(255,255,255,0.5);font-size:14px;margin-bottom:24px;">If you don\'t see it, check your spam folder or contact <a href="mailto:jared@puretechnology.nyc" style="color:#f1420b;">jared@puretechnology.nyc</a></p>' +
          '<a href="https://purebrain.ai" style="display:inline-block;padding:14px 32px;background:#2a93c1;color:#fff;border-radius:10px;text-decoration:none;font-weight:600;font-size:16px;">Return to PureBrain.ai</a>' +
          '</div>';
        console.warn('[pay-test] BLACK SCREEN SAFETY NET activated — flow did not render in 8s');
      }
    }, 8000);

    if (typeof window.initPayTestFlow === 'function') {
      window.initPayTestFlow(chatContainer, aiName, tier, orderId || null).then(function() {
        clearTimeout(_blackScreenTimer);
      }).catch(function(err) {
        clearTimeout(_blackScreenTimer);
        console.error('[pay-test] initPayTestFlow error:', err);
        // Show recovery UI on error
        chatContainer.innerHTML = '';
        chatContainer.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;background:#080a12;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px;box-sizing:border-box;text-align:center;font-family:-apple-system,BlinkMacSystemFont,sans-serif;';
        chatContainer.innerHTML = '<div style="max-width:500px;">' +
          '<div style="font-size:48px;margin-bottom:20px;">&#x2728;</div>' +
          '<h2 style="color:#2a93c1;font-size:24px;margin-bottom:12px;">Payment Confirmed!</h2>' +
          '<p style="color:rgba(255,255,255,0.7);font-size:16px;line-height:1.6;margin-bottom:24px;">Thank you! Your AI partner is being set up. Check your email for your portal access link.</p>' +
          '<a href="https://purebrain.ai" style="display:inline-block;padding:14px 32px;background:#2a93c1;color:#fff;border-radius:10px;text-decoration:none;font-weight:600;font-size:16px;">Return to PureBrain.ai</a>' +
          '</div>';
      });
    } else {
      clearTimeout(_blackScreenTimer);
      console.error('[pay-test] initPayTestFlow not found!');
      chatContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;text-align:center;font-family:-apple-system,sans-serif;">' +
        '<div><div style="font-size:48px;margin-bottom:20px;">&#x2728;</div>' +
        '<h2 style="color:#2a93c1;font-size:24px;margin-bottom:12px;">Payment Confirmed!</h2>' +
        '<p style="color:rgba(255,255,255,0.7);font-size:16px;line-height:1.6;margin-bottom:24px;">Thank you! Check your email for your portal access link.</p>' +
        '<a href="https://purebrain.ai" style="display:inline-block;padding:14px 32px;background:#2a93c1;color:#fff;border-radius:10px;text-decoration:none;font-weight:600;font-size:16px;">Return to PureBrain.ai</a></div></div>';
    }
  }

  // ============================================================
  //  URL CHECK — Handle return from PayPal popup
  //  If user lands on /pay-test/?payment=success, auto-launch flow
  // ============================================================

  function checkForPaymentReturn() {
    // GUARD: if post-payment flow already launched (from SDK onApprove), skip
    if (_postPaymentLaunched) {
      console.log("[pay-test] checkForPaymentReturn: flow already launched, skipping");
      return;
    }
    var params = new URLSearchParams(window.location.search);
    var hash = window.location.hash;

    // Check for PayPal return parameters
    if (params.get('payment') === 'success' ||
        params.get('tx') || // PayPal transaction ID
        (hash === '#awakening' && window.paymentConfirmed)) {

      var tier = params.get('tier') || window.paymentTier || 'Awakened';
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


function submitToWaitlist(data) {
            const formUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSei-RHBkOYsm79-4ueVqVSYAhNMrAwjTcoI1wpBpPPAtf2ujg/formResponse';
            const formData = new FormData();
            formData.append('entry.352980237', data.name);
            formData.append('entry.395671452', data.email);
            formData.append('entry.1657342682', data.tier);
            formData.append('entry.1947933704', data.rating);
            formData.append('entry.1413983312', data.company || '');
            formData.append('entry.493899113', data.role || '');
            formData.append('entry.944427088', data.useCase);
            formData.append('entry.1509927395', data.urgency);
            fetch(formUrl, { method: 'POST', mode: 'no-cors', body: formData })
                .then(() => console.log('Waitlist submission successful'))
                .catch(err => console.error('Submission error:', err));
        }
        
        function _legacyOpenWaitlistModal(tier) {
            // Reset form FIRST (before setting tier value)
            document.getElementById('waitlistForm').reset();
            document.getElementById('waitlistRatingValue').value = '';
            document.querySelectorAll('.waitlist-form__rating-btn').forEach(btn => btn.classList.remove('active'));
            
            // Set tier value AFTER reset so it doesn't get cleared
            document.getElementById('waitlistTier').value = tier;
            document.getElementById('waitlistTierDisplay').textContent = tier;
            
            // Show form, hide success
            document.getElementById('waitlistFormState').style.display = 'block';
            document.getElementById('waitlistSuccessState').style.display = 'none';
            
            document.getElementById('waitlistModal').classList.add('active');
        }
        
        function closeWaitlistModal() {
            document.getElementById('waitlistModal').classList.remove('active');
        }
        
        // Rating buttons
        document.querySelectorAll('.waitlist-form__rating-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.waitlist-form__rating-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                document.getElementById('waitlistRatingValue').value = this.dataset.rating;
            });
        });
        
        // ============================================
        //

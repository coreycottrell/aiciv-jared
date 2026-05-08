/* payment-glue.js - Redirect version (Phase 2 migration) */
/* Replaces post-payment chatbox with seed + redirect to /thank-you/ */
/* 2026-03-31 */

(function() {
  'use strict';

  var _redirectFired = false;

  // ============================================================
  //  PAYMENT COMPLETE CALLBACK
  //  Called by paypal-popup-integration.js after successful payment
  // ============================================================

  window.onPaymentComplete = function(tier, orderId, payerInfo) {
    console.log('[payment-glue] Payment complete:', tier, orderId);

    if (_redirectFired) return;
    _redirectFired = true;

    // Get AI name from pre-purchase state
    var aiName = '';
    if (window._pbState && window._pbState.aiName) {
      aiName = window._pbState.aiName;
    } else if (window.pbAiName) {
      aiName = window.pbAiName;
    }

    // Get payer name from PayPal
    var payerName = '';
    if (payerInfo && payerInfo.name) {
      payerName = ((payerInfo.name.given_name || '') + ' ' + (payerInfo.name.surname || '')).trim();
    }

    // Get payer email from PayPal
    var payerEmail = (payerInfo && payerInfo.email_address) ? payerInfo.email_address : '';

    // Fire referral completion if visitor came via a referral link
    (function() {
      var refCode = typeof window.getPbRef === 'function' ? window.getPbRef() : null;
      if (refCode) {
        fetch('https://app.purebrain.ai/api/referral/complete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ referral_code: refCode, referred_email: payerEmail, referred_name: payerName, order_id: orderId })
        }).catch(function(){});
      }
    })();

    // Fire seed with available data (fire-and-forget BEFORE redirect)
    (function() {
      try {
        var preMsgs = [];
        if (window._pbState && window._pbState.conversationHistory) {
          preMsgs = JSON.parse(JSON.stringify(window._pbState.conversationHistory));
        } else if (window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory) {
          preMsgs = JSON.parse(JSON.stringify(window._pbPrePurchaseSession.conversationHistory));
        }

        var sessionUuid = (typeof payTestData !== 'undefined' && payTestData.sessionUuid)
          ? payTestData.sessionUuid
          : (crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) { var r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16); }));

        var seedPayload = {
          session_uuid: sessionUuid,
          ai_name: aiName || '',
          human_name: payerName || '',
          human_email: payerEmail || '',
          tier: tier || '',
          order_id: orderId || '',
          is_sandbox: false,
          conversation: preMsgs
        };

        fetch('https://api.purebrain.ai/api/send-seed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          mode: 'cors',
          body: JSON.stringify(seedPayload),
          keepalive: true
        }).catch(function() { /* silent */ });
      } catch(e) { /* silent */ }
    })();

    // Redirect to thank-you page with AI name, payer name, and email
    setTimeout(function() {
      window.location.href = '/thank-you/?aiName=' + encodeURIComponent(aiName || '') +
        '&name=' + encodeURIComponent(payerName || '') +
        '&email=' + encodeURIComponent(payerEmail || '') +
        '&tier=' + encodeURIComponent(tier || '');
    }, 300);
  };

  // ============================================================
  //  URL CHECK — Handle return from PayPal redirect
  // ============================================================

  function checkForPaymentReturn() {
    if (_redirectFired) return;
    var params = new URLSearchParams(window.location.search);
    var hash = window.location.hash;

    if (params.get('payment') === 'success' ||
        params.get('tx') ||
        (hash === '#awakening' && window.paymentConfirmed)) {
      _redirectFired = true;
      var aiName = '';
      if (window._pbState && window._pbState.aiName) aiName = window._pbState.aiName;
      window.location.href = '/thank-you/?aiName=' + encodeURIComponent(aiName || '');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkForPaymentReturn);
  } else {
    setTimeout(checkForPaymentReturn, 500);
  }

})();


function submitToWaitlist(data) {
            var formUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSei-RHBkOYsm79-4ueVqVSYAhNMrAwjTcoI1wpBpPPAtf2ujg/formResponse';
            var formData = new FormData();
            formData.append('entry.352980237', data.name);
            formData.append('entry.395671452', data.email);
            formData.append('entry.1657342682', data.tier);
            formData.append('entry.1947933704', data.rating);
            formData.append('entry.1413983312', data.company || '');
            formData.append('entry.493899113', data.role || '');
            formData.append('entry.944427088', data.useCase);
            formData.append('entry.1509927395', data.urgency);
            fetch(formUrl, { method: 'POST', mode: 'no-cors', body: formData })
                .then(function() { console.log('Waitlist submission successful'); })
                .catch(function(err) { console.error('Submission error:', err); });
        }

        function _legacyOpenWaitlistModal(tier) {
            document.getElementById('waitlistForm').reset();
            document.getElementById('waitlistRatingValue').value = '';
            document.querySelectorAll('.waitlist-form__rating-btn').forEach(function(btn) { btn.classList.remove('active'); });
            document.getElementById('waitlistTier').value = tier;
            document.getElementById('waitlistTierDisplay').textContent = tier;
            document.getElementById('waitlistFormState').style.display = 'block';
            document.getElementById('waitlistSuccessState').style.display = 'none';
            document.getElementById('waitlistModal').classList.add('active');
        }

        function closeWaitlistModal() {
            document.getElementById('waitlistModal').classList.remove('active');
        }

        document.querySelectorAll('.waitlist-form__rating-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.waitlist-form__rating-btn').forEach(function(b) { b.classList.remove('active'); });
                this.classList.add('active');
                document.getElementById('waitlistRatingValue').value = this.dataset.rating;
            });
        });

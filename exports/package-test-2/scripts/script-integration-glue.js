/* === Integration Glue === */
/**
 * pay-test-integration-glue.js
 * Wires together PayPal popup and post-payment chat flow on purebrain.ai/pay-test
 *
 * Dependencies (must be loaded before this script):
 *   - /tmp/paypal-popup-integration.js  (provides window.openWaitlistModal replacement)
 *   - /tmp/pay-test-chat-flow.js        (provides window.initPayTestFlow)
 */</p>
<p>(function() {
  'use strict';</p>
<p>  // ============================================================
  //  PAYMENT COMPLETE CALLBACK
  //  Called by paypal-popup-integration.js after successful payment
  // ============================================================</p>
<p>  window.onPaymentComplete = function(tier, orderId, payerInfo) {
    console.log('[pay-test] Payment complete:', tier, orderId);</p>
<p>    // Store payment info
    window.payTestPaymentData = {
      tier: tier,
      orderId: orderId,
      payerInfo: payerInfo,
      timestamp: new Date().toISOString()
    };</p>
<p>    // Wait a beat, then launch the post-payment flow
    setTimeout(function() {
      launchPostPaymentFlow(tier);
    }, 1500);
  };</p>
<p>  // ============================================================
  //  POST-PAYMENT FLOW LAUNCHER
  // ============================================================</p>
<p>  function launchPostPaymentFlow(tier) {
    // Get the AI name from the existing chat state
    var aiName = 'Your AI';</p>
<p>    // Try to get from the page's exported state object
    if (window._pbState && window._pbState.aiName) {
      aiName = window._pbState.aiName;
    }
    // Try window-level fallback
    if (aiName === 'Your AI' && window.pbAiName) {
      aiName = window.pbAiName;
    }</p>
<p>    // Find or create the chat container for post-payment flow
    var chatContainer = document.getElementById('pay-test-post-payment');</p>
<p>    if (!chatContainer) {
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
      ].join(';');</p>
<p>      document.body.appendChild(chatContainer);
    }</p>
<p>    // Launch the flow
    if (typeof window.initPayTestFlow === 'function') {
      window.initPayTestFlow(chatContainer, aiName, tier);
    } else {
      console.error('[pay-test] initPayTestFlow not found! Make sure pay-test-chat-flow.js is loaded.');
    }
  }</p>
<p>  // ============================================================
  //  URL CHECK — Handle return from PayPal popup
  //  If user lands on /pay-test/?payment=success, auto-launch flow
  // ============================================================</p>
<p>  function checkForPaymentReturn() {
    var params = new URLSearchParams(window.location.search);
    var hash = window.location.hash;</p>
<p>    // Check for PayPal return parameters
    if (params.get('payment') === 'success' ||
        params.get('tx') || // PayPal transaction ID
        (hash === '#awakening' && window.paymentConfirmed)) {</p>
<p>      var tier = params.get('tier') || window.paymentTier || 'Bonded';
      var orderId = params.get('tx') || window.paymentOrderId || 'RETURN-' + Date.now();</p>
<p>      console.log('[pay-test] Payment return detected, tier:', tier);</p>
<p>      // Small delay to let the page fully load
      setTimeout(function() {
        launchPostPaymentFlow(tier);
      }, 2000);
    }
  }</p>
<p>  // ============================================================
  //  INIT
  // ============================================================</p>
<p>  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkForPaymentReturn);
  } else {
    // Small delay to let other scripts initialize
    setTimeout(checkForPaymentReturn, 500);
  }</p>
<p>})();</p>
<p>
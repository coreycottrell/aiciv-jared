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
  }</p>
<p>  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(applyPayPalAlias, 100);
    });
  } else {
    setTimeout(applyPayPalAlias, 100);
  }
})();
(function() {
    'use strict';
    function brandFooterLogo() {
        var logoEl = document.querySelector('.footer-logo h4, #site-footer .footer-logo h4, footer .footer-logo h4');
        if (!logoEl) return;
        // Already branded - don't run twice
        if (logoEl.querySelector('.pb-logo-brand')) return;
        // Replace text content with color-coded brand name
        logoEl.innerHTML =
            '<span class="pb-logo-brand" style="font-size:inherit;font-weight:inherit;letter-spacing:inherit;">' +
            '<span style="color:#2a93c1;">PUREBR</span>' +
            '<span style="color:#f1420b;">AI</span>' +
            '<span style="color:#2a93c1;">N</span>' +
            '<span style="color:#ffffff;">.AI</span>' +
            '</span>';
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', brandFooterLogo);
    } else {
        brandFooterLogo();
    }
})();

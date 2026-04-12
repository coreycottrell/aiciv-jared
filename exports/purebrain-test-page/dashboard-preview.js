/**
 * dashboard-preview.js
 * Tooltip interaction logic for PureBrain dashboard preview section.
 *
 * Desktop: CSS handles hover; JS handles keyboard navigation and
 *          prevents tooltip clipping at viewport edges.
 * Mobile:  Accordion card expand/collapse.
 */

(function () {
  'use strict';

  /* ── Constants ─────────────────────────────────────────── */
  var TOOLTIP_MARGIN = 12; // px from viewport edge
  var TRANSITION_MS  = 200;

  /* ── Feature block tooltip management ──────────────────── */

  /**
   * Reposition a tooltip so it does not overflow the viewport.
   * Called on focusin so keyboard users get correctly placed tooltips.
   *
   * @param {HTMLElement} feature  - The .dp-feature element
   * @param {HTMLElement} tooltip  - The .dp-tooltip element inside it
   */
  function repositionTooltip(feature, tooltip) {
    // Reset any previous JS positioning
    tooltip.style.left   = '';
    tooltip.style.right  = '';
    tooltip.style.bottom = '';
    tooltip.style.top    = '';
    tooltip.style.transform = '';

    var fRect = feature.getBoundingClientRect();
    var tRect = tooltip.getBoundingClientRect();
    var vw    = window.innerWidth || document.documentElement.clientWidth;

    // Horizontal overflow guard
    var idealLeft = fRect.left + (fRect.width / 2) - (tRect.width / 2);
    if (idealLeft < TOOLTIP_MARGIN) {
      // Shift right - pin to left edge of feature or viewport
      tooltip.style.left      = '0';
      tooltip.style.right     = 'auto';
      tooltip.style.transform = 'translateY(0)';
    } else if (idealLeft + tRect.width > vw - TOOLTIP_MARGIN) {
      // Shift left - pin to right edge of feature or viewport
      tooltip.style.left      = 'auto';
      tooltip.style.right     = '0';
      tooltip.style.transform = 'translateY(0)';
    }
  }

  /* ── Wire desktop feature blocks ───────────────────────── */
  function initFeatureBlocks() {
    var features = document.querySelectorAll('.dp-feature');
    if (!features.length) return;

    features.forEach(function (feature) {
      var tooltip = feature.querySelector('.dp-tooltip');
      if (!tooltip) return;

      // Keyboard: show/hide on focus/blur
      feature.addEventListener('focusin', function () {
        if (window.innerWidth <= 680) return; // handled by mobile accordion
        repositionTooltip(feature, tooltip);
      });

      feature.addEventListener('focusout', function (e) {
        // Only hide if focus left the feature entirely
        if (!feature.contains(e.relatedTarget)) {
          // CSS transitions handle the visual - nothing extra needed
        }
      });

      // Enter/Space toggle (accessibility)
      feature.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          // Just keep focus for screen readers - tooltip is tied to :focus-visible
        }
        if (e.key === 'Escape') {
          feature.blur();
        }
      });

      // Recalc position on window resize
      window.addEventListener('resize', function () {
        if (document.activeElement === feature) {
          repositionTooltip(feature, tooltip);
        }
      }, { passive: true });
    });
  }

  /* ── Mobile accordion cards ─────────────────────────────── */
  function initMobileAccordion() {
    var cards = document.querySelectorAll('.dp-mobile-card');
    if (!cards.length) return;

    cards.forEach(function (card) {
      var header = card.querySelector('.dp-mobile-card-header');
      var bodyId = header ? header.getAttribute('aria-controls') : null;
      var body   = bodyId ? document.getElementById(bodyId) : null;

      if (!header || !body) return;

      header.addEventListener('click', function () {
        var isOpen = header.getAttribute('aria-expanded') === 'true';

        if (isOpen) {
          // Close
          closeCard(header, body);
        } else {
          // Close any other open card first (accordion behavior)
          cards.forEach(function (otherCard) {
            var otherHeader = otherCard.querySelector('.dp-mobile-card-header');
            var otherId     = otherHeader ? otherHeader.getAttribute('aria-controls') : null;
            var otherBody   = otherId ? document.getElementById(otherId) : null;
            if (otherHeader && otherBody && otherHeader !== header) {
              closeCard(otherHeader, otherBody);
            }
          });

          openCard(header, body);
        }
      });

      // Keyboard support
      header.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          header.click();
        }
      });
    });
  }

  /**
   * Animate a card open using a max-height trick so CSS transition works.
   */
  function openCard(header, body) {
    header.setAttribute('aria-expanded', 'true');
    body.hidden = false;
    // Allow reflow before animating
    body.style.maxHeight = '0';
    body.style.overflow  = 'hidden';
    body.style.transition = 'max-height ' + TRANSITION_MS + 'ms ease';
    // Next frame
    requestAnimationFrame(function () {
      body.style.maxHeight = body.scrollHeight + 'px';
    });
    // Clean up after transition
    body.addEventListener('transitionend', function onEnd() {
      body.style.maxHeight = '';
      body.style.overflow  = '';
      body.removeEventListener('transitionend', onEnd);
    });
  }

  /**
   * Animate a card closed.
   */
  function closeCard(header, body) {
    header.setAttribute('aria-expanded', 'false');
    body.style.maxHeight  = body.scrollHeight + 'px';
    body.style.overflow   = 'hidden';
    body.style.transition = 'max-height ' + TRANSITION_MS + 'ms ease';
    requestAnimationFrame(function () {
      body.style.maxHeight = '0';
    });
    body.addEventListener('transitionend', function onEnd() {
      body.hidden = true;
      body.style.maxHeight  = '';
      body.style.overflow   = '';
      body.style.transition = '';
      body.removeEventListener('transitionend', onEnd);
    });
  }

  /* ── Animate insight bar on scroll into view ────────────── */
  function initInsightBar() {
    var fills = document.querySelectorAll('.dp-insight-bar-fill');
    if (!fills.length) return;

    // Store target widths, then reset to 0
    var targets = [];
    fills.forEach(function (fill) {
      targets.push(fill.style.width || '0%');
      fill.style.width = '0%';
    });

    var animated = false;

    function maybeAnimate() {
      if (animated) return;
      var section = document.getElementById('dashboard-preview');
      if (!section) return;
      var rect = section.getBoundingClientRect();
      var vh   = window.innerHeight || document.documentElement.clientHeight;

      if (rect.top < vh * 0.85) {
        animated = true;
        fills.forEach(function (fill, i) {
          // Small stagger per bar
          setTimeout(function () {
            fill.style.width = targets[i];
          }, i * 120);
        });
      }
    }

    window.addEventListener('scroll', maybeAnimate, { passive: true });
    // Check on load in case already in view
    maybeAnimate();
  }

  /* ── Boot ──────────────────────────────────────────────── */
  function init() {
    initFeatureBlocks();
    initMobileAccordion();
    initInsightBar();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

}());

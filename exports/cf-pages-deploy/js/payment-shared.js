/* payment-shared.js - Shared scripts for purebrain.ai payment pages */
/* Extracted 2026-04-01 to reduce page size */

/* === VIDEO HANDLER JS === */
(function() {
    'use strict';

    // Only run on video-background pages (detected by body class, not PHP)
    var body = document.body;
    var videoPageIds = ['home', 'page-id-11', 'page-id-689', 'page-id-688', 'page-id-1232', 'page-id-319'];
    var isVideoPage = videoPageIds.some(function(cls) { return body.classList.contains(cls); });
    if (!isVideoPage) return;

    var mq = window.matchMedia('(max-width: 767px)');

    function handleVideoViewport(isMobile) {
        var vid = document.getElementById('bgVideo');
        var wrapper = vid ? vid.closest('.video-background') : null;
        var livingBg = document.querySelector('.living-background');
        if (!vid) return;

        // Always ensure the video wrapper is visible
        if (wrapper) {
            wrapper.style.setProperty('display', 'block', 'important');
            wrapper.style.setProperty('visibility', 'visible', 'important');
        } else {
            vid.style.setProperty('display', 'block', 'important');
            vid.style.setProperty('visibility', 'visible', 'important');
        }

        if (isMobile) {
            // Mobile: REMOVE vortex hexagon rings from DOM entirely
            // CSS display:none !important wasn't working on iOS Safari,
            // so we physically remove the elements to guarantee they're gone.
            var portalVortex = document.querySelector('.portal-vortex');
            if (portalVortex) { portalVortex.remove(); }
            // Also remove hero particles (tiny dots)
            var heroParticles = document.querySelector('.hero__particles');
            if (heroParticles) { heroParticles.remove(); }
            // Shrink hero logo
            var heroLogo = document.querySelector('.hero__logo');
            if (heroLogo) {
                heroLogo.style.setProperty('width', '70px', 'important');
                heroLogo.style.setProperty('height', '70px', 'important');
            }

            // Mobile: bring video above html background layer
            if (wrapper) {
                wrapper.style.setProperty('z-index', '0', 'important');
            }
            // FORCE hide living-background with !important inline styles
            if (livingBg) {
                livingBg.style.setProperty('display', 'none', 'important');
                livingBg.style.setProperty('visibility', 'hidden', 'important');
                livingBg.style.setProperty('opacity', '0', 'important');
                livingBg.style.setProperty('z-index', '-999', 'important');
            }
            // Also hide all children (canvas, orbs, etc.)
            var livingChildren = document.querySelectorAll('.living-background *');
            for (var i = 0; i < livingChildren.length; i++) {
                livingChildren[i].style.setProperty('display', 'none', 'important');
                livingChildren[i].style.setProperty('visibility', 'hidden', 'important');
            }
            // Ensure page content sits above the video
            var siteContent = document.getElementById('content') ||
                              document.querySelector('.site-content') ||
                              document.querySelector('.elementor') ||
                              document.querySelector('#site-content');
            if (siteContent) {
                siteContent.style.position = 'relative';
                siteContent.style.zIndex = '1';
            }
        } else {
            // Desktop/tablet: restore original z-index and show living-background
            if (wrapper) {
                wrapper.style.setProperty('z-index', '-1', 'important');
            }
            if (livingBg) {
                livingBg.style.removeProperty('display');
                livingBg.style.removeProperty('visibility');
                livingBg.style.removeProperty('opacity');
                livingBg.style.removeProperty('z-index');
            }
            var livingChildren = document.querySelectorAll('.living-background *');
            for (var i = 0; i < livingChildren.length; i++) {
                livingChildren[i].style.removeProperty('display');
                livingChildren[i].style.removeProperty('visibility');
            }
        }

        // Play video on all viewports (muted autoplay works on mobile with playsinline)
        if (document.visibilityState !== 'hidden') {
            // On mobile, if video hasn't started, calling load() then play() forces it
            if (vid.readyState === 0 || vid.paused) {
                if (vid.readyState === 0) { vid.load(); }
                vid.play().catch(function() {});
            }
        }
    }

    // Run immediately
    handleVideoViewport(mq.matches);

    // Retry after 500ms to catch late-loading Elementor canvas animations
    setTimeout(function() { handleVideoViewport(mq.matches); }, 500);

    // Retry after 1500ms as final safety net
    setTimeout(function() { handleVideoViewport(mq.matches); }, 1500);

    // React to viewport size changes
    if (mq.addEventListener) {
        mq.addEventListener('change', function(e) { handleVideoViewport(e.matches); });
    } else if (mq.addListener) {
        mq.addListener(function(e) { handleVideoViewport(e.matches); });
    }

    // iOS: Aggressive video play fallback
    // iOS Low Power Mode + some iOS versions block autoplay completely.
    // Strategy: try play() every way possible, then use touch fallback.
    (function iosVideoFix() {
        var vid = document.getElementById('bgVideo');
        if (!vid) return;

        // Attempt 1: Direct play on load
        vid.play().catch(function() {});

        // Attempt 2: After a short delay
        setTimeout(function() { vid.play().catch(function() {}); }, 100);
        setTimeout(function() { vid.play().catch(function() {}); }, 500);
        setTimeout(function() { vid.play().catch(function() {}); }, 2000);

        // Attempt 3: On any user interaction (touch, scroll, click)
        function forcePlay() {
            if (vid.paused) {
                vid.muted = true; // ensure muted (required for autoplay)
                vid.play().catch(function() {});
            }
        }
        document.addEventListener('touchstart', forcePlay, { passive: true });
        document.addEventListener('touchend', forcePlay, { passive: true });
        document.addEventListener('click', forcePlay);
        document.addEventListener('scroll', function scrollPlay() {
            forcePlay();
            document.removeEventListener('scroll', scrollPlay);
        }, { passive: true });

        // Attempt 4: Intersection observer - play when visible
        if ('IntersectionObserver' in window) {
            var obs = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting && vid.paused) {
                        vid.play().catch(function() {});
                    }
                });
            });
            obs.observe(vid);
        }
    })();

    // Handle page visibility change (switching tabs)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            var vid = document.getElementById('bgVideo');
            if (vid && vid.paused) {
                vid.play().catch(function() {});
            }
        }
    });
})();

/* === CONSENT GATE === */
/* === CONSENT GATE === */
(function () {
    var CONSENT_KEY = 'pb_consent_v1';

    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0;
            var v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function getConsentCTAs() {
        return document.querySelectorAll('#proCta, #partnerCta, #unifiedCta');
    }

    function lockCTAs() {
        getConsentCTAs().forEach(function (btn) {
            btn.classList.add('pb-cta-locked');
            btn.classList.remove('pb-cta-unlocked');
            btn.setAttribute('aria-disabled', 'true');
        });
    }

    function unlockCTAs() {
        getConsentCTAs().forEach(function (btn) {
            btn.classList.remove('pb-cta-locked');
            btn.classList.add('pb-cta-unlocked');
            btn.removeAttribute('aria-disabled');
        });
    }

    function logConsent(consentUUID, timestamp) {
        try {
            if (window._pbState && Array.isArray(window._pbState.conversationHistory)) {
                window._pbState.conversationHistory.push({
                    role: 'system',
                    content: '[CONSENT] User accepted Terms of Service and Privacy Policy.',
                    consent_uuid: consentUUID,
                    consent_timestamp: timestamp
                });
            }
        } catch (e) {}

        try {
            var sessionId = window._pbSessionId || ('pb_' + Date.now());
            var payload = {
                source: 'purebrain-consent',
                messages: [{
                    role: 'system',
                    content: 'User accepted Terms of Service and Privacy Policy.',
                    consent_uuid: consentUUID,
                    consent_timestamp: timestamp
                }],
                metadata: {
                    event_type: 'consent_accepted',
                    consent_uuid: consentUUID,
                    consent_timestamp: timestamp,
                    page_url: window.location.href
                },
                session_id: sessionId
            };
            fetch('https://api.purebrain.ai/api/log-conversation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).catch(function () {});
        } catch (e) {}
    }

    function onConsentChange(checked) {
        if (checked) {
            var consentUUID = generateUUID();
            var timestamp = new Date().toISOString();
            try {
                sessionStorage.setItem(CONSENT_KEY, JSON.stringify({
                    uuid: consentUUID,
                    timestamp: timestamp
                }));
            } catch (e) {}
            logConsent(consentUUID, timestamp);
            unlockCTAs();
        } else {
            try { sessionStorage.removeItem(CONSENT_KEY); } catch (e) {}
            lockCTAs();
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        var checkbox = document.getElementById('pb-consent-check');
        if (!checkbox) return;

        try {
            var stored = sessionStorage.getItem(CONSENT_KEY);
            if (stored) {
                checkbox.checked = true;
                unlockCTAs();
            } else {
                lockCTAs();
            }
        } catch (e) {
            lockCTAs();
        }

        checkbox.addEventListener('change', function () {
            onConsentChange(this.checked);
        });
        // Auto-fire consent since checkbox is pre-checked
        if (checkbox.checked) { onConsentChange(true); }
    });
})();


/* === REFERRAL LEADERBOARD === */
(function() {
    var LEADERBOARD_URL = 'https://portal.purebrain.ai/api/referral/leaderboard';

    function maskName(name) {
        if (!name || name.length < 2) return '***';
        var parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return parts[0] + ' ' + parts[1].charAt(0) + '.';
        }
        // Single name: show first 3 chars then mask
        return name.substring(0, 3) + '***';
    }

    function renderLeaderboard(data) {
        var container = document.getElementById('referral-leaderboard');
        if (!container) return;

        // Normalize: data might be array directly or { leaderboard: [...] } or { data: [...] }
        var entries = Array.isArray(data) ? data
            : (data.leaderboard || data.data || data.results || []);

        // Show only referrers with actual completed conversions (real data from portal DB)
        entries = (entries || []).filter(function(e) {
            var count = parseInt(e.completed || e.referral_count || e.count || e.referrals || 0, 10);
            return count > 0;
        });

        if (!entries || entries.length === 0) {
            container.innerHTML = '<li class="referral__lb-empty">Be the first on the leaderboard!</li>';
            return;
        }

        // Sort by referral count descending (in case not pre-sorted)
        entries.sort(function(a, b) {
            var aCount = parseInt(a.completed || a.referral_count || a.count || a.referrals || 0, 10);
            var bCount = parseInt(b.completed || b.referral_count || b.count || b.referrals || 0, 10);
            return bCount - aCount;
        });

        // Show top 8
        var top = entries.slice(0, 8);
        var html = '';
        top.forEach(function(entry, i) {
            var rank = i + 1;
            var rawName = entry.name || entry.username || entry.affiliate_name || entry.display_name || 'Partner';
            var displayName = maskName(rawName);
            var count = parseInt(entry.completed || entry.referral_count || entry.count || entry.referrals || 0, 10);
            var label = count === 1 ? 'referral' : 'referrals';
            html += '<li class="referral__lb-row">'
                + '<span class="referral__lb-rank">' + rank + '</span>'
                + '<span class="referral__lb-name">' + displayName + '</span>'
                + '<span class="referral__lb-count">' + count + ' ' + label + '</span>'
                + '</li>';
        });
        container.innerHTML = html;
    }

    function loadLeaderboard() {
        var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        var timeout = controller ? setTimeout(function() { controller.abort(); }, 6000) : null;

        var options = { method: 'GET', headers: { 'Accept': 'application/json' } };
        if (controller) options.signal = controller.signal;

        fetch(LEADERBOARD_URL, options)
            .then(function(res) {
                if (timeout) clearTimeout(timeout);
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
            .then(function(data) {
                renderLeaderboard(data);
            })
            .catch(function(err) {
                var container = document.getElementById('referral-leaderboard');
                if (container) {
                    container.innerHTML = '<li class="referral__lb-empty">Leaderboard loading&hellip; Check back soon!</li>';
                }
            });
    }

    // Load on DOMContentLoaded or immediately if already loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadLeaderboard);
    } else {
        loadLeaderboard();
    }
})();

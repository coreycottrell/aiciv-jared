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

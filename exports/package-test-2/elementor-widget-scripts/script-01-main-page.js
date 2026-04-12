
            // Do not change this comment line otherwise Speed Optimizer won't be able to detect this script

            (function () {
                function sendRequest(url, body) {
                    if(!window.fetch) {
                        const xhr = new XMLHttpRequest();
                        xhr.open("POST", url, true);
                        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                        xhr.send(JSON.stringify(body))
                        return
                    }

                    const request = fetch(url, {
                        method: 'POST',
                        body: JSON.stringify(body),
                        keepalive: true,
                        headers: {
                            'Content-Type': 'application/json;charset=UTF-8'
                        }
                    });
                }

                const calculateParentDistance = (child, parent) => {
                    let count = 0;
                    let currentElement = child;

                    // Traverse up the DOM tree until we reach parent or the top of the DOM
                    while (currentElement && currentElement !== parent) {
                        currentElement = currentElement.parentNode;
                        count++;
                    }

                    // If parent was not found in the hierarchy, return -1
                    if (!currentElement) {
                        return -1; // Indicates parent is not an ancestor of element
                    }

                    return count; // Number of layers between element and parent
                }
                const isMatchingClass = (linkRule, href, classes, ids) => {
                    return classes.includes(linkRule.value)
                }
                const isMatchingId = (linkRule, href, classes, ids) => {
                    return ids.includes(linkRule.value)
                }
                const isMatchingDomain = (linkRule, href, classes, ids) => {
                    if(!URL.canParse(href)) {
                        return false
                    }

                    const url = new URL(href)
                    const host = url.host
                    const hostsToMatch = [host]

                    if(host.startsWith('www.')) {
                        hostsToMatch.push(host.substring(4))
                    } else {
                        hostsToMatch.push('www.' + host)
                    }

                    return hostsToMatch.includes(linkRule.value)
                }
                const isMatchingExtension = (linkRule, href, classes, ids) => {
                    if(!URL.canParse(href)) {
                        return false
                    }

                    const url = new URL(href)

                    return url.pathname.endsWith('.' + linkRule.value)
                }
                const isMatchingSubdirectory = (linkRule, href, classes, ids) => {
                    if(!URL.canParse(href)) {
                        return false
                    }

                    const url = new URL(href)

                    return url.pathname.startsWith('/' + linkRule.value + '/')
                }
                const isMatchingProtocol = (linkRule, href, classes, ids) => {
                    if(!URL.canParse(href)) {
                        return false
                    }

                    const url = new URL(href)

                    return url.protocol === linkRule.value + ':'
                }
                const isMatchingExternal = (linkRule, href, classes, ids) => {
                    if(!URL.canParse(href) || !URL.canParse(document.location.href)) {
                        return false
                    }

                    const matchingProtocols = ['http:', 'https:']
                    const siteUrl = new URL(document.location.href)
                    const linkUrl = new URL(href)

                    // Links to subdomains will appear to be external matches according to JavaScript,
                    // but the PHP rules will filter those events out.
                    return matchingProtocols.includes(linkUrl.protocol) && siteUrl.host !== linkUrl.host
                }
                const isMatch = (linkRule, href, classes, ids) => {
                    switch (linkRule.type) {
                        case 'class':
                            return isMatchingClass(linkRule, href, classes, ids)
                        case 'id':
                            return isMatchingId(linkRule, href, classes, ids)
                        case 'domain':
                            return isMatchingDomain(linkRule, href, classes, ids)
                        case 'extension':
                            return isMatchingExtension(linkRule, href, classes, ids)
                        case 'subdirectory':
                            return isMatchingSubdirectory(linkRule, href, classes, ids)
                        case 'protocol':
                            return isMatchingProtocol(linkRule, href, classes, ids)
                        case 'external':
                            return isMatchingExternal(linkRule, href, classes, ids)
                        default:
                            return false;
                    }
                }
                const track = (element) => {
                    const href = element.href ?? null
                    const classes = Array.from(element.classList)
                    const ids = [element.id]
                    const linkRules = [{"type":"extension","value":"pdf"},{"type":"extension","value":"zip"},{"type":"protocol","value":"mailto"},{"type":"protocol","value":"tel"}]
                    if(linkRules.length === 0) {
                        return
                    }

                    // For link rules that target an id, we need to allow that id to appear
                    // in any ancestor up to the 7th ancestor. This loop looks for those matches
                    // and counts them.
                    linkRules.forEach((linkRule) => {
                        if(linkRule.type !== 'id') {
                            return;
                        }

                        const matchingAncestor = element.closest('#' + linkRule.value)

                        if(!matchingAncestor || matchingAncestor.matches('html, body')) {
                            return;
                        }

                        const depth = calculateParentDistance(element, matchingAncestor)

                        if(depth < 7) {
                            ids.push(linkRule.value)
                        }
                    });

                    // For link rules that target a class, we need to allow that class to appear
                    // in any ancestor up to the 7th ancestor. This loop looks for those matches
                    // and counts them.
                    linkRules.forEach((linkRule) => {
                        if(linkRule.type !== 'class') {
                            return;
                        }

                        const matchingAncestor = element.closest('.' + linkRule.value)

                        if(!matchingAncestor || matchingAncestor.matches('html, body')) {
                            return;
                        }

                        const depth = calculateParentDistance(element, matchingAncestor)

                        if(depth < 7) {
                            classes.push(linkRule.value)
                        }
                    });

                    const hasMatch = linkRules.some((linkRule) => {
                        return isMatch(linkRule, href, classes, ids)
                    })

                    if(!hasMatch) {
                        return
                    }

                    const url = "https://purebrain.ai/wp-content/plugins/independent-analytics/iawp-click-endpoint.php";
                    const body = {
                        href: href,
                        classes: classes.join(' '),
                        ids: ids.join(' '),
                        ...{"payload":{"resource":"singular","singular_id":11,"page":1},"signature":"57de2a5466fcbd6d2d5a6537a4782e9e"}                    };

                    sendRequest(url, body)
                }
                document.addEventListener('mousedown', function (event) {
                                        if (navigator.webdriver || /bot|crawler|spider|crawling|semrushbot|chrome-lighthouse/i.test(navigator.userAgent)) {
                        return;
                    }
                    
                    const element = event.target.closest('a')

                    if(!element) {
                        return
                    }

                    const isPro = false
                    if(!isPro) {
                        return
                    }

                    // Don't track left clicks with this event. The click event is used for that.
                    if(event.button === 0) {
                        return
                    }

                    track(element)
                })
                document.addEventListener('click', function (event) {
                                        if (navigator.webdriver || /bot|crawler|spider|crawling|semrushbot|chrome-lighthouse/i.test(navigator.userAgent)) {
                        return;
                    }
                    
                    const element = event.target.closest('a, button, input[type="submit"], input[type="button"]')

                    if(!element) {
                        return
                    }

                    const isPro = false
                    if(!isPro) {
                        return
                    }

                    track(element)
                })
                document.addEventListener('play', function (event) {
                                        if (navigator.webdriver || /bot|crawler|spider|crawling|semrushbot|chrome-lighthouse/i.test(navigator.userAgent)) {
                        return;
                    }
                    
                    const element = event.target.closest('audio, video')

                    if(!element) {
                        return
                    }

                    const isPro = false
                    if(!isPro) {
                        return
                    }

                    track(element)
                }, true)
                document.addEventListener("DOMContentLoaded", function (e) {
                    if (document.hasOwnProperty("visibilityState") && document.visibilityState === "prerender") {
                        return;
                    }

                                            if (navigator.webdriver || /bot|crawler|spider|crawling|semrushbot|chrome-lighthouse/i.test(navigator.userAgent)) {
                            return;
                        }
                    
                    let referrer_url = null;

                    if (typeof document.referrer === 'string' && document.referrer.length > 0) {
                        referrer_url = document.referrer;
                    }

                    const params = location.search.slice(1).split('&').reduce((acc, s) => {
                        const [k, v] = s.split('=');
                        return Object.assign(acc, {[k]: v});
                    }, {});

                    const url = "https://purebrain.ai/wp-json/iawp/search";
                    const body = {
                        referrer_url,
                        utm_source: params.utm_source,
                        utm_medium: params.utm_medium,
                        utm_campaign: params.utm_campaign,
                        utm_term: params.utm_term,
                        utm_content: params.utm_content,
                        gclid: params.gclid,
                        ...{"payload":{"resource":"singular","singular_id":11,"page":1},"signature":"57de2a5466fcbd6d2d5a6537a4782e9e"}                    };

                    sendRequest(url, body)
                });
            })();

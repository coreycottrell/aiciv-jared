#!/usr/bin/env python3
"""
fingerprint_gen.py - Generate realistic browser fingerprints using BrowserForge.

Each fingerprint represents a unique "person" with consistent browser parameters:
canvas, WebGL, audio, fonts, screen resolution, navigator, timezone, language.
"""

from browserforge.fingerprints import FingerprintGenerator

# Singleton generator (reusable, thread-safe for generation)
_generator = FingerprintGenerator()


def generate_fingerprint() -> dict:
    """
    Generate a single realistic browser fingerprint.

    Returns:
        dict: JSON-serializable fingerprint with keys:
            - navigator: user agent, platform, languages, etc.
            - screen: resolution, color depth, pixel ratio
            - videoCard: WebGL renderer and vendor
            - fonts: list of installed fonts
            - audioCodecs: supported audio codecs
            - videoCodecs: supported video codecs
            - battery: battery API data (if present)
            - headers: HTTP headers fingerprint
    """
    fp = _generator.generate()

    # Convert the Fingerprint dataclass to a plain dict for JSON storage
    result = {}

    # Navigator
    if fp.navigator:
        nav = fp.navigator
        result['navigator'] = {
            'userAgent': nav.userAgent,
            'appVersion': nav.appVersion,
            'platform': nav.platform,
            'language': nav.language,
            'languages': nav.languages,
            'hardwareConcurrency': nav.hardwareConcurrency,
            'deviceMemory': nav.deviceMemory,
            'maxTouchPoints': nav.maxTouchPoints,
            'vendor': nav.vendor,
            'doNotTrack': nav.doNotTrack,
            'appCodeName': nav.appCodeName,
            'appName': nav.appName,
            'product': nav.product,
            'productSub': nav.productSub,
            'vendorSub': nav.vendorSub,
            'webdriver': nav.webdriver,
            'oscpu': nav.oscpu,
        }
        if nav.userAgentData:
            result['navigator']['userAgentData'] = nav.userAgentData
        if nav.extraProperties:
            result['navigator']['extraProperties'] = nav.extraProperties

    # Screen
    if fp.screen:
        s = fp.screen
        result['screen'] = {
            'width': s.width,
            'height': s.height,
            'availWidth': s.availWidth,
            'availHeight': s.availHeight,
            'colorDepth': s.colorDepth,
            'pixelDepth': s.pixelDepth,
            'devicePixelRatio': s.devicePixelRatio,
            'outerWidth': s.outerWidth,
            'outerHeight': s.outerHeight,
        }

    # Video card (WebGL)
    if fp.videoCard:
        vc = fp.videoCard
        result['videoCard'] = {
            'vendor': vc.vendor,
            'renderer': vc.renderer,
        }

    # Fonts
    result['fonts'] = fp.fonts if fp.fonts else []

    # Audio codecs
    if fp.audioCodecs:
        result['audioCodecs'] = fp.audioCodecs if isinstance(fp.audioCodecs, (dict, list)) else str(fp.audioCodecs)
    else:
        result['audioCodecs'] = {}

    # Video codecs
    if fp.videoCodecs:
        result['videoCodecs'] = fp.videoCodecs if isinstance(fp.videoCodecs, (dict, list)) else str(fp.videoCodecs)
    else:
        result['videoCodecs'] = {}

    # Battery (optional)
    if fp.battery:
        result['battery'] = fp.battery if isinstance(fp.battery, dict) else str(fp.battery)

    # Headers
    if fp.headers:
        result['headers'] = fp.headers if isinstance(fp.headers, (dict, list)) else str(fp.headers)

    # Multimedia devices
    if fp.multimediaDevices:
        result['multimediaDevices'] = (
            fp.multimediaDevices
            if isinstance(fp.multimediaDevices, (dict, list))
            else str(fp.multimediaDevices)
        )

    # Plugins
    if fp.pluginsData:
        result['pluginsData'] = (
            fp.pluginsData
            if isinstance(fp.pluginsData, (dict, list))
            else str(fp.pluginsData)
        )

    # WebRTC mock config
    if fp.mockWebRTC:
        result['mockWebRTC'] = (
            fp.mockWebRTC
            if isinstance(fp.mockWebRTC, (dict, bool))
            else str(fp.mockWebRTC)
        )

    return result


def generate_fingerprint_slim() -> dict:
    """
    Generate a slim fingerprint with only the essential fields.
    Useful for quick comparisons or when full data isn't needed.

    Returns:
        dict with: userAgent, screen (w x h), renderer, fontCount
    """
    fp = generate_fingerprint()
    return {
        'userAgent': fp.get('navigator', {}).get('userAgent', ''),
        'screen': f"{fp.get('screen', {}).get('width', 0)}x{fp.get('screen', {}).get('height', 0)}",
        'renderer': fp.get('videoCard', {}).get('renderer', ''),
        'fontCount': len(fp.get('fonts', [])),
    }


if __name__ == '__main__':
    import json
    fp = generate_fingerprint()
    print(json.dumps(fp, indent=2, default=str))

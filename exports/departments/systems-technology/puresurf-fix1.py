#!/usr/bin/env python3
"""FIX 1: Remove Chrome artifacts from Firefox engine anti-detection script.

Replaces:
- Chrome plugins with Firefox PDF Viewer
- Chrome MIME types with Firefox-native ones
- Removes window.chrome injection entirely
"""
import re, sys

filepath = '/opt/baas/baas_server_simple.py'

with open(filepath, 'r') as f:
    content = f.read()

# ---- Replace Chrome plugins (section 4) with Firefox-native plugin ----
old_plugins = """// 4. Fix plugins (must look like real browser with plugins)
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
            { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
        ];
        plugins.length = 3;
        plugins.item = function(i) { return this[i] || null; };
        plugins.namedItem = function(name) { return this.find(p => p.name === name) || null; };
        plugins.refresh = function() {};
        return plugins;
    },
    configurable: true
});"""

new_plugins = """// 4. Fix plugins (Firefox-native — NO Chrome artifacts on Camoufox/Firefox engine)
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            { name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Firefox PDF Plugin for macOS', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
        ];
        plugins.length = 2;
        plugins.item = function(i) { return this[i] || null; };
        plugins.namedItem = function(name) { return this.find(p => p.name === name) || null; };
        plugins.refresh = function() {};
        return plugins;
    },
    configurable: true
});"""

count = content.count(old_plugins)
if count == 0:
    print("ERROR: Could not find Chrome plugins block to replace")
    sys.exit(1)
content = content.replace(old_plugins, new_plugins)
print(f"FIX 1a: Replaced Chrome plugins with Firefox-native plugins ({count} occurrences)")

# ---- Replace Chrome MIME types (section 5) with Firefox-native ----
old_mimes = """// 5. Fix mimeTypes
Object.defineProperty(navigator, 'mimeTypes', {
    get: () => {
        const mimeTypes = [
            { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: navigator.plugins[0] },
            { type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: navigator.plugins[0] },
        ];
        mimeTypes.length = 2;
        mimeTypes.item = function(i) { return this[i] || null; };
        mimeTypes.namedItem = function(name) { return this.find(m => m.type === name) || null; };
        return mimeTypes;
    },
    configurable: true
});"""

new_mimes = """// 5. Fix mimeTypes (Firefox-native — no Chrome MIME types)
Object.defineProperty(navigator, 'mimeTypes', {
    get: () => {
        const mimeTypes = [
            { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: navigator.plugins[0] },
        ];
        mimeTypes.length = 1;
        mimeTypes.item = function(i) { return this[i] || null; };
        mimeTypes.namedItem = function(name) { return this.find(m => m.type === name) || null; };
        return mimeTypes;
    },
    configurable: true
});"""

count = content.count(old_mimes)
if count == 0:
    print("ERROR: Could not find Chrome MIME types block to replace")
    sys.exit(1)
content = content.replace(old_mimes, new_mimes)
print(f"FIX 1b: Replaced Chrome MIME types with Firefox-native ({count} occurrences)")

# ---- Remove window.chrome injection (section 2) entirely ----
old_chrome = """// 2. Chrome runtime object (makes page think it's real Chrome)
if (!window.chrome && navigator.userAgent.includes("Chrome")) {
    Object.defineProperty(window, 'chrome', {
        get: () => ({
            runtime: {
                connect: function() {},
                sendMessage: function() {},
                onMessage: { addListener: function() {} },
                onConnect: { addListener: function() {} },
                id: undefined
            },
            loadTimes: function() { return {}; },
            csi: function() { return {}; },
            app: {
                isInstalled: false,
                InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' },
                getDetails: function() { return null; },
                getIsInstalled: function() { return false; },
            }
        }),
        configurable: true
    });
}"""

new_chrome = """// 2. [REMOVED] Chrome runtime injection — Camoufox is Firefox, no window.chrome needed
// Firefox does NOT have window.chrome. Injecting it creates a fingerprint mismatch
// (Firefox TLS + Chrome JS = detectable inconsistency)."""

count = content.count(old_chrome)
if count == 0:
    print("ERROR: Could not find window.chrome injection block to replace")
    sys.exit(1)
content = content.replace(old_chrome, new_chrome)
print(f"FIX 1c: Removed window.chrome injection ({count} occurrences)")

with open(filepath, 'w') as f:
    f.write(content)

print("FIX 1: COMPLETE — Chrome artifacts removed from Firefox engine")

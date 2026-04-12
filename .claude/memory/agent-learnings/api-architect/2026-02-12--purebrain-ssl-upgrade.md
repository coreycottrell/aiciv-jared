# Pure Brain Log Server SSL Upgrade

**Date**: 2026-02-12
**Agent**: api-architect
**Type**: technique
**Topic**: Adding SSL/HTTPS to Flask server for mixed content compliance

## Context

The Pure Brain log server at http://89.167.19.20:8080 needed SSL/HTTPS because:
- purebrain.ai is served over HTTPS
- Browsers block HTTP requests from HTTPS pages (Mixed Content policy)
- A live user session was being lost due to this blocking

## Solution

### Approach: Self-signed certificate with SAN

Generated a self-signed certificate using OpenSSL with Subject Alternative Names (SANs) for:
- IP.1 = 89.167.19.20 (server IP)
- DNS.1 = localhost
- IP.2 = 127.0.0.1

**Why SANs matter**: Modern browsers reject certificates without proper SANs, even for self-signed certs.

### Key Code Changes

1. Added SSL imports and certificate paths:
```python
import ssl
SSL_CERT_DIR = '/home/jared/projects/AI-CIV/aether/config/ssl'
SSL_CERT_FILE = os.path.join(SSL_CERT_DIR, 'server.crt')
SSL_KEY_FILE = os.path.join(SSL_CERT_DIR, 'server.key')
```

2. Auto-generate cert function with OpenSSL config:
```python
def generate_self_signed_cert():
    # Creates openssl.cnf with SAN configuration
    # Runs: openssl req -x509 -nodes -days 365 -newkey rsa:2048
```

3. SSL context for Flask:
```python
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(SSL_CERT_FILE, SSL_KEY_FILE)
app.run(..., ssl_context=ssl_context)
```

### Port Change

- OLD: HTTP on port 8080
- NEW: HTTPS on port 8443 (standard HTTPS alternate port)

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` - Added SSL support
- `/home/jared/projects/AI-CIV/aether/tools/launch_purebrain_log_server.sh` - Created launch script

## Gotchas

1. **Self-signed certs require `-k` flag with curl**: `curl -k https://...`
2. **Browser warning**: Users/clients will see "insecure" warning for self-signed certs
3. **Mixed content still partially blocked**: Some browsers may still warn even with HTTPS self-signed

## Better Long-term Solution

For production, consider:
- Let's Encrypt certificate (requires domain pointing to server)
- Cloudflare tunnel (proxies HTTPS without server-side cert)
- Proper CA-signed certificate

## Verification Commands

```bash
# Stop old server
pkill -f "python3.*purebrain_log_server.py"

# Start new HTTPS server
cd /home/jared/projects/AI-CIV/aether
source venv/bin/activate
python3 tools/purebrain_log_server.py &

# Test health endpoint
curl -k https://89.167.19.20:8443/api/health

# Test POST endpoint
curl -k -X POST https://89.167.19.20:8443/api/log-conversation \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

## Tags

- ssl
- https
- flask
- mixed-content
- purebrain
- api-security

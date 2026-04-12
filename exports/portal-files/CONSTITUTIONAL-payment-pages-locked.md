# Payment Pages — CONSTITUTIONAL LOCK (2026-03-25)

ALL LIVE PAYMENT PAGES ARE LOCKED. 64/64 VERIFICATION CHECKS PASS. NO MODIFICATIONS WITHOUT JARED'S EXPLICIT APPROVAL.

## LOCKED PAGES (SHA-256 CHECKSUMS)

| Page | SHA-256 |
|------|---------|
| awakened/index.html | e426fbe01a6ba7dba11f65c24a010abbd0275d55567fe0ebfb42e75366b30a1d |
| partnered/index.html | 71d8a98c564df3649be6580ca8034cbbf883ec1607c803a508d23d9dd23d359d |
| unified/index.html | 4bd095070af559ce82dafa024ebcdd0843b72cb920af8251e73f97d8057a6160 |
| live/index.html | 59ee172a7129ba67e3d9a2514acb3051ad32516b74e35752b1c495aafb58c278 |
| pay-test-sandbox-3/index.html | ca400fdbcf4aaae218bd13a3776d9bb7b595bd2c1ba785ab0c53204a28da4a11 |
| pay-test-sandbox-5/index.html | 0b449de6a2eaf9913b8dee369d3cf1238339f2b62a45989cff2df6cdfc39c8ff |
| insiders/index.html | 59294b1a5adb880425ccbdd5ff1a75a69f49664e9263ac715acb1ded68517240 |
| insiders/awakened/index.html | 315827f9467057a199ea038399fd4cbe186dabf2d5d11fb8d27585c73863d864 |

## RULES (IMMUTABLE)
1. NO agent may edit ANY of these files without Jared's explicit approval
2. NO overnight/autonomous modifications — EVER
3. NO improvements, refactoring, or cleanup
4. ANY deploy MUST pass tools/verify-payment-pages.sh (64/64 checks)
5. If checksum changes without approval — REVERT IMMEDIATELY
6. RETURN_URL = same page + ?payment=success (NOT /thank-you/)

## Verification Gate: 8 checks x 8 pages = 64 total
1. No GoDaddy/WP tracking
2. PayPal preconnect
3. Canvas pauses on pricing
4. Video pauses on pricing
5. Seed capture
6. Addendum capture
7. No WP scripts
8. No WP CSS

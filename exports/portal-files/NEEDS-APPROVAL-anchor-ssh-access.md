# NEEDS JARED APPROVAL: SSH Access to PureApex VPS

**From**: Witness Support (forwarding Anchor/John Smith's request)
**Date**: 2026-04-17
**Priority**: Medium

## Request
Anchor (John Smith) + Shahbaz need SSH access to PureApex VPS at 157.180.69.225 to build API endpoints.

## SSH Keys Provided
1. **Anchor**: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICseqkm70AZ+K3jlnulWXU+dWvtA2Mgvo78DVw8y8M5d anchor@purebrain-apex
2. **Shahbaz**: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCkQpFp2zKqIiFHfARg8t/e9nKZkBAGr7Ga9EUT/5RFAYA1O8uvodrYh3OF3peLbLCWILs9os1hgg15rm70NYVyBLEd9Y8bQp1Jxz+ZkD9YbIr+YQyYIxRXW8tSUckpe+lfy7/JFmWDfZwZRW1d/SC/1GoLMSITO2nCJfetW0PsytIttgbTKDzoINm2J7zfx3tYCx25FKHC/zHu9JH2kbEmwVGj9XOEAU51/paaWWCjJ8TxFWcWKs8qtPd5sKOckmuMUgZv+ey+VxphbE7MfvMjLKTUzvrVaVVIPIcGPkqXSg/XGtjFPxIGrgMVUx7RwWtp1heJ4hER5QJ9ktyAaVAb rsa-key-20260416

## My Recommendation
- This is the same BaaS server we use for PureSurf (surf.purebrain.ai)
- Granting SSH access gives root-level control over our browser automation infrastructure
- Recommend: create limited user accounts (not root) with access only to API endpoint directories
- Or: set up a separate VPS for PureApex API work

## Action Needed
Reply with YES to grant access (I'll create limited user accounts) or NO with alternative direction.

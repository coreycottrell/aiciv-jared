---
name: Git Push Workflow
description: ALWAYS use git@github-interciv SSH config for pushing to coreycottrell repos
type: feedback
---

ALWAYS use git@github-interciv:coreycottrell/{repo}.git SSH config for pushing.

**Why:** SSH config github-interciv has the correct key for coreycottrell's GitHub repos. Default git remote or HTTPS will fail auth.

**How to apply:** Ensure remote uses git@github-interciv:coreycottrell/{repo}.git. Update .gitignore first, commit, push.

# Halifax Now Deployment Runbook

Start here for staging and production operations.

## Documents

- `STAGING_SETUP.md`  
  Initial staging setup, secrets, deployment scope, and v3 enablement.

- `RELEASE_CHECKLIST.md`  
  Release process checklist from staging validation through production promotion.

- `RELEASE_COMMANDS.md`  
  Copy/paste command reference for git flow, SSH checks, and common recovery steps.

## Recommended order of use

1. First-time setup or environment fixes: `STAGING_SETUP.md`
2. Every release: `RELEASE_CHECKLIST.md`
3. During execution/troubleshooting: `RELEASE_COMMANDS.md`

## Operational baseline

- Staging URL: `https://staging.halifax-now.ca`
- Staging workflow: `Deploy WordPress Files to Plesk (Staging)` (branch `staging`)
- Production workflow: `Deploy Theme to Plesk` (branch `main`)

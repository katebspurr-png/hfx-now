# Staging Setup (New Design)

This project deploys both the WordPress theme and v3 preview assets to Plesk via GitHub Actions.

For staging, use the dedicated workflow:

- `.github/workflows/deploy-theme-plesk-staging.yml`

It auto-runs on pushes to the `staging` branch, and can also be run manually from the Actions tab.

## 1) Add staging GitHub secrets

In your GitHub repo settings, create:

- `PLESK_STAGING_THEME_PATH`
- `PLESK_STAGING_SSH_HOST`
- `PLESK_STAGING_SSH_USER`
- `PLESK_STAGING_SSH_KEY`
- `PLESK_STAGING_SSH_PORT`

These should point at your staging server/site, not production.

## 2) Deploy the new design to staging

Push your new-design changes to the `staging` branch.

The staging workflow syncs:

- `wp-content/themes/halifax-now-broadsheet/`
- `v3-preview/` to `/v3-preview/` on staging (derived from `PLESK_STAGING_THEME_PATH`)

You can also run manual `dry_run` deploys before a full transfer.

Important: make sure `v3-preview/` files are committed to git. Untracked local files are not deployed by GitHub Actions.

## 3) Enable v3 sections in staging

The new additive sections are feature-flagged in theme code.

Enable one of:

- `define('HFX_V3_SECTIONS_ENABLED', true);` in staging `wp-config.php`, or
- WP option `hfx_v3_sections_enabled = 1`

Without this, staging will still show the base broadsheet nav without v3 section links.

## 4) Quick verification checklist

- Homepage renders with the latest broadsheet style.
- `/v3-preview/?v3=1` loads.
- If flag enabled: top nav includes `Run Clubs`, `Happy Hour`, `Patios`.
- `/events/`, `/map/`, `/venues/`, and `/submit/` still load.


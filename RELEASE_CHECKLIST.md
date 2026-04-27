# Halifax Now Release Checklist

Use this checklist for every staging and production release in this repo.

## 0) Branch + scope

- [ ] Confirm current branch is correct (`staging` for pre-release, `main` for live).
- [ ] Confirm only intended files are included in the release.
- [ ] Confirm WordPress-facing changes are inside `wp-content/` (and `v3-preview/` when relevant).

## 1) Deploy to staging

- [ ] Push changes to `staging`.
- [ ] Confirm workflow `Deploy WordPress Files to Plesk (Staging)` runs successfully.
- [ ] If needed, run a manual deploy from Actions with `dry_run: false`.
- [ ] If staging homepage shows a host placeholder, ensure `staging.halifax-now.ca/index.html` is removed/renamed so WordPress `index.php` is served.

## 2) Staging smoke test (required)

- [ ] Homepage loads: `https://staging.halifax-now.ca/`
- [ ] V3 preview loads: `https://staging.halifax-now.ca/v3-preview/?v3=1`
- [ ] Core routes load: `/events/`, `/map/`, `/venues/`, `/submit/`
- [ ] Admin login works on staging (`/wp-login.php`)
- [ ] No obvious PHP warnings, fatal errors, or 5xx responses

## 3) Staging config checks

- [ ] `siteurl` is `https://staging.halifax-now.ca`
- [ ] `home` is `https://staging.halifax-now.ca`
- [ ] `hfx_v3_sections_enabled = 1` (when validating v3 sections/nav)
- [ ] Staging is not indexed by search engines
- [ ] Staging database is isolated from production (no shared live DB credentials)

## 4) Cache + hard refresh pass

- [ ] Purge WordPress cache (plugin, if enabled).
- [ ] Purge server/CDN cache (if enabled).
- [ ] Hard refresh browser and recheck homepage + one key route.

## 5) Promote to production

- [ ] Merge `staging` into `main`.
- [ ] Confirm workflow `Deploy Theme to Plesk` runs successfully on `main`.
- [ ] Verify live homepage and at least one key route.
- [ ] Verify staging still opens at `https://staging.halifax-now.ca/` after production deploy.

## 6) Post-release checks

- [ ] Confirm no unexpected redirects between staging and live.
- [ ] Confirm staging still points to staging DB and URLs.
- [ ] Document any manual steps performed during release.

## Quick rollback idea

If a release is bad:

1. Re-deploy last known good commit.
2. Clear caches.
3. Re-test homepage + critical routes.

## Reference: workflow scope

- `Deploy WordPress Files to Plesk (Staging)` deploys `wp-content/` and `v3-preview/` from branch `staging`.
- `Deploy Theme to Plesk` deploys `wp-content/themes/halifax-now-broadsheet/` from branch `main`.

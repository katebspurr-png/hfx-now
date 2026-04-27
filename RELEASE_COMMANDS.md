# Halifax Now Release Commands

Quick command reference for staging and production workflow.

## 1) Check current state

```bash
git branch --show-current
git status --short
git log --oneline -n 5
```

## 2) Push changes to staging

```bash
git checkout staging
git pull --ff-only origin staging
git add <files>
git commit -m "Your release message"
git push origin staging
```

## 3) Promote staging to production

```bash
git checkout main
git pull --ff-only origin main
git merge --no-ff staging
git push origin main
```

## 4) Verify remote branches/commit parity

```bash
git fetch origin
git log --oneline --decorate -n 5 origin/staging
git log --oneline --decorate -n 5 origin/main
git diff --name-only origin/main..origin/staging
```

## 5) Staging SSH quick checks

```bash
ssh -i ~/.ssh/hfx_staging_deploy -p 22 fifwvkap@192.95.15.215
```

Once connected:

```bash
pwd
ls -la
ls -la staging.halifax-now.ca
ls -la staging.halifax-now.ca/v3-preview
```

## 6) If staging shows host placeholder page

From SSH:

```bash
mv "staging.halifax-now.ca/index.html" "staging.halifax-now.ca/index.html.bak"
```

## 7) If staging redirects to live

In phpMyAdmin (`fifwvkap_cwzc1` -> `gipq_options`), set:

- `siteurl` = `https://staging.halifax-now.ca`
- `home` = `https://staging.halifax-now.ca`

## 8) V3 feature flag

In phpMyAdmin (`fifwvkap_cwzc1` -> `gipq_options`):

- `hfx_v3_sections_enabled` = `1`

## 9) Validate routes after staging deploy

- `https://staging.halifax-now.ca/`
- `https://staging.halifax-now.ca/v3-preview/?v3=1`
- `https://staging.halifax-now.ca/events/`
- `https://staging.halifax-now.ca/map/`
- `https://staging.halifax-now.ca/venues/`
- `https://staging.halifax-now.ca/submit/`

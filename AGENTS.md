# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is a **WordPress performance optimization toolkit** for halifax-now.ca ("HFX Now"). It contains:
- A consolidated must-use (mu) plugin at `wp-content/mu-plugins/hfxnow-performance.php`
- Individual PHP snippets in `optimizations/` (standalone versions for the Code Snippets plugin)
- Configuration guides (Markdown) for WP Rocket and WP Fastest Cache

There is no build system, package manager, or automated test suite. The PHP files are meant to be deployed into a running WordPress installation.

### Development environment

The dev environment uses Docker Compose (`docker-compose.yml`) to run WordPress 6 (PHP 8.2 + Apache) with MySQL 8.0. The `wp-content/mu-plugins/` directory is bind-mounted into the WordPress container, so edits to the mu-plugin are reflected immediately without restarting.

**Starting the environment:**
```
docker compose up -d
```

**WordPress admin:** http://localhost:8080/wp-admin/ (admin / admin)

**First-time setup after containers start:**
```
docker exec workspace-wordpress-1 bash -c "curl -sO https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x wp-cli.phar && mv wp-cli.phar /usr/local/bin/wp"
docker exec workspace-wordpress-1 wp core install --url="http://localhost:8080" --title="HFX Now Dev" --admin_user=admin --admin_password=admin --admin_email=admin@example.com --allow-root
```

### Linting

There are no dedicated lint tools configured. Use `php -l` for syntax checking:
```
php -l wp-content/mu-plugins/hfxnow-performance.php
php -l optimizations/*.php
```

### Key gotchas

- Docker must be started manually (`sudo dockerd` if the daemon isn't already running). In nested container environments, `fuse-overlayfs` storage driver and `iptables-legacy` are required.
- The mu-plugin is auto-loaded by WordPress from the `mu-plugins/` directory — no activation step is needed.
- The individual snippets in `optimizations/` duplicate the same functionality as the mu-plugin; they are alternate deployment paths (via the Code Snippets WordPress plugin), not additional code to install alongside it.
- Changes to the PHP files in `wp-content/mu-plugins/` are picked up on the next page load (no cache clear needed in dev).

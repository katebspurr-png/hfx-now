#!/bin/bash
# =============================================================================
# run_all_with_audit.command
# Double-click this file (macOS) or run from terminal to audit all HFX Now
# performance optimizations and flag items that need human review.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPTIMIZATIONS_DIR="$SCRIPT_DIR/optimizations"
MU_PLUGIN="$SCRIPT_DIR/wp-content/mu-plugins/hfxnow-performance.php"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

NEEDS_REVIEW=()
PASSED=()
WARNINGS=()

divider() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

header() {
  divider
  echo -e "${BOLD}$1${NC}"
  divider
}

pass() {
  echo -e "  ${GREEN}✔${NC} $1"
  PASSED+=("$1")
}

warn() {
  echo -e "  ${YELLOW}⚠${NC} $1"
  WARNINGS+=("$1")
}

needs_review() {
  echo -e "  ${RED}★ NEEDS REVIEW:${NC} $1"
  NEEDS_REVIEW+=("$1")
}

# =============================================================================
header "HFX Now Performance Audit"
echo "  Running from: $SCRIPT_DIR"
echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
# =============================================================================

# ── Check: mu-plugin file exists ──
header "1. MU-Plugin Deployment"

if [ -f "$MU_PLUGIN" ]; then
  pass "hfxnow-performance.php exists at wp-content/mu-plugins/"
else
  needs_review "hfxnow-performance.php is MISSING from wp-content/mu-plugins/ — deploy it to activate optimizations"
fi

# ── Check: Snippet files exist ──
header "2. Optimization Snippets Present"

for i in 01 02 03 04; do
  snippet=$(find "$OPTIMIZATIONS_DIR" -name "${i}-*.php" 2>/dev/null | head -1)
  if [ -n "$snippet" ]; then
    pass "$(basename "$snippet")"
  else
    needs_review "No snippet found matching ${i}-*.php in optimizations/"
  fi
done

# ── Check: GTM placeholder ID ──
header "3. Google Tag Manager Configuration"

GTM_SNIPPET="$OPTIMIZATIONS_DIR/03-delay-google-analytics.php"
if [ -f "$GTM_SNIPPET" ]; then
  if grep -q 'GTM-XXXXXXX' "$GTM_SNIPPET"; then
    needs_review "03-delay-google-analytics.php still has placeholder GTM ID 'GTM-XXXXXXX' — replace with your real container ID before activating"
  else
    pass "GTM container ID has been customized"
  fi

  # Also check the mu-plugin for the same placeholder (if it includes the GTM snippet)
  if [ -f "$MU_PLUGIN" ] && grep -q 'GTM-XXXXXXX' "$MU_PLUGIN"; then
    needs_review "hfxnow-performance.php also contains placeholder 'GTM-XXXXXXX' — update before deploying"
  fi
else
  warn "03-delay-google-analytics.php not found — skipping GTM check"
fi

# ── Check: WP Rocket vs snippet conflicts ──
header "4. Plugin Conflict Check"

echo -e "  ${CYAN}These checks flag snippets that overlap with WP Rocket features."
echo -e "  If using WP Rocket, some snippets should be DEACTIVATED.${NC}"
echo ""

# Snippet 02 vs WP Rocket "Load Google Fonts locally"
needs_review "Snippet 02 (font-display swap for Google Fonts) conflicts with WP Rocket's 'Load Google Fonts locally' setting. Use ONE or the other, not both."

# Snippet 03 vs WP Rocket "Delay JavaScript execution"
needs_review "Snippet 03 (delay GTM) conflicts with WP Rocket's 'Delay JavaScript execution' setting. Use ONE or the other, not both."

# Snippet 01 is always needed (no equivalent in either caching plugin)
pass "Snippet 01 (dequeue Events Calendar) has no caching plugin equivalent — always activate"

# Snippet 04 is always needed (self-hosted font, not handled by caching plugins)
pass "Snippet 04 (font-display swap for self-hosted Manrope) has no caching plugin equivalent — always activate"

# ── Check: MU-plugin contains all expected functions ──
header "5. MU-Plugin Completeness"

if [ -f "$MU_PLUGIN" ]; then
  EXPECTED_FUNCTIONS=(
    "hfxnow_dequeue_tribe_on_non_events_pages"
    "hfxnow_add_font_display_swap"
    "hfxnow_preconnect_google_fonts"
    "hfxnow_font_display_swap_self_hosted"
  )

  for func in "${EXPECTED_FUNCTIONS[@]}"; do
    if grep -q "$func" "$MU_PLUGIN"; then
      pass "Function $func found in mu-plugin"
    else
      needs_review "Function $func is MISSING from mu-plugin — optimization may not be active"
    fi
  done

  # Check if the GTM delay function is included
  if grep -q "hfxnow_delay_gtm_script" "$MU_PLUGIN"; then
    pass "GTM delay function included in mu-plugin"
  else
    warn "GTM delay function (hfxnow_delay_gtm_script) is NOT in the mu-plugin — this is fine if using WP Rocket's delay JS feature or Code Snippets plugin instead"
  fi
else
  needs_review "Cannot check mu-plugin completeness — file is missing"
fi

# ── Check: Settings guides present ──
header "6. Configuration Guides"

if [ -f "$OPTIMIZATIONS_DIR/wprocket-settings-guide.md" ]; then
  pass "WP Rocket settings guide present"
else
  warn "WP Rocket settings guide missing"
fi

if [ -f "$OPTIMIZATIONS_DIR/wpfastestcache-settings-guide.md" ]; then
  pass "WP Fastest Cache settings guide present"
else
  warn "WP Fastest Cache settings guide missing"
fi

# ── Check: PHP syntax ──
header "7. PHP Syntax Check"

if command -v php &> /dev/null; then
  for phpfile in "$MU_PLUGIN" "$OPTIMIZATIONS_DIR"/*.php; do
    if [ -f "$phpfile" ]; then
      if php -l "$phpfile" 2>&1 | grep -q "No syntax errors"; then
        pass "$(basename "$phpfile") — no syntax errors"
      else
        needs_review "$(basename "$phpfile") has PHP syntax errors — fix before deploying"
      fi
    fi
  done
else
  warn "PHP not installed locally — skipping syntax checks. Install PHP to enable this check."
fi

# =============================================================================
header "AUDIT SUMMARY"
# =============================================================================

echo ""
echo -e "  ${GREEN}Passed:${NC}       ${#PASSED[@]} checks"
echo -e "  ${YELLOW}Warnings:${NC}     ${#WARNINGS[@]} (informational)"
echo -e "  ${RED}Needs Review:${NC} ${#NEEDS_REVIEW[@]} items"
echo ""

if [ ${#NEEDS_REVIEW[@]} -gt 0 ]; then
  echo -e "${RED}${BOLD}Items requiring human review:${NC}"
  echo ""
  for i in "${!NEEDS_REVIEW[@]}"; do
    echo -e "  ${RED}$((i+1)).${NC} ${NEEDS_REVIEW[$i]}"
  done
  echo ""
  echo -e "${YELLOW}Please address the items above before deploying to production.${NC}"
else
  echo -e "${GREEN}${BOLD}All checks passed! Ready for deployment.${NC}"
fi

echo ""
divider
echo ""

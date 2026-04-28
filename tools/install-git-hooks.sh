#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC_DIR="${REPO_ROOT}/tools/git-hooks"
HOOKS_DST_DIR="${REPO_ROOT}/.git/hooks"

install_hook() {
  local name="$1"
  local src="${HOOKS_SRC_DIR}/${name}"
  local dst="${HOOKS_DST_DIR}/${name}"

  if [[ ! -f "${src}" ]]; then
    echo "Skipping ${name}; source not found: ${src}"
    return 0
  fi

  cp "${src}" "${dst}"
  chmod +x "${dst}"
  echo "Installed ${name}"
}

install_hook "pre-commit"
install_hook "pre-push"

echo "Git hooks installation complete."

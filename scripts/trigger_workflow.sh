#!/usr/bin/env bash
# Trigger "Automated Trading Bot" on GitHub (same as Actions → Run workflow).
# Requires: GitHub CLI — https://cli.github.com/  (`brew install gh`)
# One-time: gh auth login

set -euo pipefail

REPO="${GITHUB_REPO:-}"
if [[ -z "$REPO" ]]; then
  ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  URL="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
  # Handles git@..., https://github.com/..., and https://user:token@github.com/...
  if [[ -n "$URL" ]] && echo "$URL" | grep -q 'github\.com'; then
    REPO="$(echo "$URL" | sed -E 's#.*github\.com[:/]##; s#\.git$##')"
  fi
  if [[ -z "$REPO" || "$REPO" == *"@"* ]]; then
    echo "Could not parse owner/repo from git remote."
    echo "Set: export GITHUB_REPO=owner/repo"
    exit 1
  fi
fi

if ! command -v gh &>/dev/null; then
  echo "Install GitHub CLI: brew install gh"
  exit 1
fi

REF="${GITHUB_REF_NAME:-main}"
echo "Dispatching workflow on $REPO (ref=$REF)..."
gh workflow run "Automated Trading Bot" --repo "$REPO" --ref "$REF"
echo "Done. Recent runs:"
gh run list --repo "$REPO" --workflow="Automated Trading Bot" --limit 5

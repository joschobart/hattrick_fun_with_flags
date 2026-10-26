#!/usr/bin/env bash
# Usage: scripts/pack.sh

set -euo pipefail

REPOMIX_VERSION="1.18.1"
BUDGET=60000
REPO="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
OUT_DIR="$REPO/scripts"

if ! repomix --version | grep -qx "$REPOMIX_VERSION"; then
  echo "!! repomix $REPOMIX_VERSION required (npm i -g repomix@$REPOMIX_VERSION)" >&2
  exit 1
fi
mkdir -p "$OUT_DIR"

repomix "$REPO" \
  --include "README.rst,CONTEXT.md,fun_with_flags/*.py,fun_with_flags/templates/**,fun_with_flags/templates/**/**,instance/config.py,pyproject.toml,.github/**/**,docker/**" \
  -o "$OUT_DIR/repomix.md" --style markdown --token-budget "$BUDGET"

echo "-> packs in $OUT_DIR"


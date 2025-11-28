#!/usr/bin/env bash

set -euxo pipefail

# Early exit if no files provided
if [ $# -eq 0 ]; then
  exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel)

# Setup Node using shared function
source "$REPO_ROOT/install-tools-functions.sh"
setup_node "$REPO_ROOT"

if [ ! -d "$REPO_ROOT/node_modules" ]; then
  cd "$REPO_ROOT"
  pnpm install --frozen-lockfile --ignore-scripts --prefer-offline
fi

cd "$REPO_ROOT"

set +x
echo "Running prettier"
pnpm exec prettier \
  --write \
  "$@"

git add "$@"

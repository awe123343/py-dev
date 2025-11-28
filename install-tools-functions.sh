#!/usr/bin/env bash

# Installation Functions for Development Tools
# =============================================
# Provides installation functions for uv, pre-commit, and node setup.
# These functions handle checking, messaging, and installation.
#
# Usage:
#   source ./scripts/install-tools-functions.sh
#   setup_node
#   install_uv
#   install_pre_commit

# Setup Node.js using fnm (local) or nvm (CI)
# Requires .nvmrc file in current directory or REPO_ROOT
setup_node() {
  local nvmrc_dir="${1:-.}"

  if ! command -v fnm &>/dev/null; then
    curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell
  else
    if command -v fnm >/dev/null 2>&1; then
      fnm use --install-if-missing "$(cat "$nvmrc_dir/.nvmrc")"
    else
      echo "Warning: 'fnm' is not installed. Please make sure you are using the correct Node version ($(cat "$nvmrc_dir/.nvmrc"))."
    fi
  fi

  local expected_version
  expected_version=$(cat "$nvmrc_dir/.nvmrc" | tr -d 'v')
  if [ "$(node -v | cut -d'.' -f1 | tr -d 'v')" != "$expected_version" ]; then
    echo "Invalid node version '$(node -v)'! Expected '$expected_version'."
    return 1
  fi

  echo "✅ Node version '$(node -v)' is valid."
}

# Install uv if not available
install_uv() {
  if ! command -v uv &>/dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "✅ uv is already installed"
  fi
}

# Install pre-commit using uv if not available
# Automatically installs uv first if needed
install_pre_commit() {
  # Ensure uv is installed first
  install_uv

  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v pre-commit &>/dev/null; then
    echo "📦 Installing pre-commit..."
    uv tool install pre-commit
  else
    echo "✅ pre-commit is already installed"
  fi
}

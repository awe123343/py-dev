#!/usr/bin/env bash

set -euo pipefail

ROOT="${ROOT:-$(git rev-parse --show-toplevel)}"

KTFMT_VERSION="0.59"
KTLINT_VERSION="1.7.1"
BIN_DIR="${ROOT}/bin"

KTFMT_JAR=${BIN_DIR}/ktfmt-${KTFMT_VERSION}.jar
KTFMT_URL="https://github.com/facebook/ktfmt/releases/download/v${KTFMT_VERSION}/ktfmt-${KTFMT_VERSION}-with-dependencies.jar"

KTLINT_JAR=${BIN_DIR}/ktlint-$KTLINT_VERSION.jar
KTLINT_URL="https://github.com/pinterest/ktlint/releases/download/${KTLINT_VERSION}/ktlint"

mkdir -p "${BIN_DIR}"

if [ ! -f "${KTFMT_JAR}" ]; then
  >&2 echo "Downloading ktfmt v${KTFMT_VERSION}..."
  rm -rf "${BIN_DIR}/ktfmt-*.jar"
  curl -fL "${KTFMT_URL}" -o "${KTFMT_JAR}"
  echo "ktfmt downloaded to ${KTFMT_JAR}"
fi

if [ ! -f "${KTLINT_JAR}" ]; then
  >&2 echo "Downloading ktlint v${KTLINT_VERSION}..."
  rm -rf "${BIN_DIR}/ktlint-*.jar"
  curl -fsSL "${KTLINT_URL}" -o "${KTLINT_JAR}"
  chmod +x "${KTLINT_JAR}"
  echo "ktlint downloaded to ${KTLINT_JAR}"
fi

if [[ $# -gt 0 ]]; then
  # Use meta-style over kotlinlang-style for only adding trailing commas
  # Kotlin lang style will remove trailling comma if it thinks it's not necessary
  # The other difference is that meta-style uses 2 spaces for indentation instead of 4
  # But this is fine, we run ktlint afterwards which will fix indentation
  java -jar "$KTFMT_JAR" --meta-style "$@"
  java -Djava.awt.headless=true --add-opens java.base/java.lang=ALL-UNNAMED -XX:+UseZGC -jar "$KTLINT_JAR" -F "$@"
  git add "$@"
fi

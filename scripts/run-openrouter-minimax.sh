#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

export AUTONOVEL_MODEL_ID="${AUTONOVEL_MODEL_ID:-minimax/minimax-m2.5}"
exec "${SCRIPT_DIR}/run-openrouter-model.sh" "$@"

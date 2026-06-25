#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

TIME_LIMIT="${1:-300}"
LOG_PATH="${2:-/tmp/autonovel_foundation_$(date +%Y%m%d_%H%M%S).log}"

echo "[foundation-run] timeout=${TIME_LIMIT}s" >&2
echo "[foundation-run] log=${LOG_PATH}" >&2

timeout "${TIME_LIMIT}s" env PYTHONUNBUFFERED=1 \
  "${SCRIPT_DIR}/run-openrouter-model.sh" run_pipeline.py --phase foundation \
  2>&1 | tee "${LOG_PATH}"

exit "${PIPESTATUS[0]}"

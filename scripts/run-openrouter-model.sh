#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

MODEL_ID="${AUTONOVEL_MODEL_ID:-minimax/minimax-m2.5}"
API_KEY="${OPENROUTER_API_KEY:-${ANTHROPIC_AUTH_TOKEN:-}}"

if [[ -z "${API_KEY}" ]]; then
  echo "ERROR: set OPENROUTER_API_KEY (or ANTHROPIC_AUTH_TOKEN) first." >&2
  exit 1
fi

export AUTONOVEL_API_MODE=claude_code
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://openrouter.ai/api}"
export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_AUTH_TOKEN:-${API_KEY}}"
export ANTHROPIC_API_KEY=""
export AUTONOVEL_API_KEY=""
export AUTONOVEL_AUTH_TOKEN=""
export AUTONOVEL_WRITER_MODEL="${AUTONOVEL_WRITER_MODEL:-${MODEL_ID}}"
export AUTONOVEL_JUDGE_MODEL="${AUTONOVEL_JUDGE_MODEL:-${MODEL_ID}}"
export AUTONOVEL_REVIEW_MODEL="${AUTONOVEL_REVIEW_MODEL:-${MODEL_ID}}"
export AUTONOVEL_ENABLE_GIT="${AUTONOVEL_ENABLE_GIT:-0}"
export AUTONOVEL_MAX_OUTPUT_TOKENS="${AUTONOVEL_MAX_OUTPUT_TOKENS:-4000}"

echo "[openrouter] base=${ANTHROPIC_BASE_URL}" >&2
echo "[openrouter] model=${MODEL_ID}" >&2
echo "[openrouter] max_output=${AUTONOVEL_MAX_OUTPUT_TOKENS}" >&2

exec uv run python "$@"

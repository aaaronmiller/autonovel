#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${REPO_ROOT}/.agent-launcher.env" ]]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.agent-launcher.env"
fi

usage() {
  cat <<'EOF'
Usage: scripts/launch-agent.sh <agent> [args...]

Agents:
  claude     Claude Code / Anthropic-compatible gateway
  codex      OpenAI Codex CLI
  opencode   OpenCode CLI
  qwen       Qwen Code CLI
  gemini     Gemini CLI
  custom     User-defined command via CUSTOM_AGENT_BIN

Core env vars:
  AGENT_ROUTE=native|proxy|openrouter       Default: native
  AGENT_MODE=default|acp                    Default: default
  AGENT_EDITOR="code --wait"                Exported as EDITOR when set

Proxy/OpenRouter env vars:
  AGENT_PROXY_URL=http://localhost:8082
  AGENT_OPENAI_PROXY_URL=http://localhost:8082/v1
  AGENT_PROXY_KEY=pass
  OPENROUTER_API_KEY=...

Custom agent env vars:
  CUSTOM_AGENT_BIN=/path/to/binary
  CUSTOM_AGENT_ARGS="--flag value"
  CUSTOM_AGENT_ACP_ARGS="--acp"

Examples (WSL/bash):
  scripts/launch-agent.sh claude --continue --dangerously-skip-permissions --verbose --model=opus
  AGENT_ROUTE=proxy scripts/launch-agent.sh claude --continue --model=opus
  AGENT_ROUTE=openrouter OPENAI_MODEL=gpt-5.2-codex scripts/launch-agent.sh codex
  AGENT_MODE=acp scripts/launch-agent.sh qwen
  AGENT_MODE=acp scripts/launch-agent.sh opencode
EOF
}

log() {
  printf '[launch-agent] %s\n' "$*" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Missing required command: $1"
    exit 1
  fi
}

split_args() {
  local raw="${1:-}"
  SPLIT_RESULT=()
  if [[ -z "${raw}" ]]; then
    return 0
  fi
  # Intentional word splitting for user-supplied launcher args.
  # shellcheck disable=SC2206
  SPLIT_RESULT=( ${raw} )
}

set_editor_env() {
  if [[ -n "${AGENT_EDITOR:-}" ]]; then
    export EDITOR="${AGENT_EDITOR}"
  fi
}

setup_claude_env() {
  local route="${AGENT_ROUTE:-native}"
  case "${route}" in
    native)
      ;;
    proxy)
      export ANTHROPIC_BASE_URL="${AGENT_PROXY_URL:-http://localhost:8082}"
      export ANTHROPIC_API_KEY="${AGENT_PROXY_KEY:-pass}"
      export CLAUDE_CODE_MAX_OUTPUT_TOKENS="${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-128768}"
      ;;
    openrouter)
      : "${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY for AGENT_ROUTE=openrouter}"
      export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://openrouter.ai/api}"
      export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_AUTH_TOKEN:-${OPENROUTER_API_KEY}}"
      export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
      ;;
    *)
      log "Unsupported AGENT_ROUTE for claude: ${route}"
      exit 1
      ;;
  esac
}

setup_openai_compat_env() {
  local route="${AGENT_ROUTE:-native}"
  case "${route}" in
    native)
      ;;
    proxy)
      export OPENAI_BASE_URL="${OPENAI_BASE_URL:-${AGENT_OPENAI_PROXY_URL:-${AGENT_PROXY_URL:-http://localhost:8082}/v1}}"
      export OPENAI_API_KEY="${OPENAI_API_KEY:-${AGENT_PROXY_KEY:-pass}}"
      ;;
    openrouter)
      : "${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY for AGENT_ROUTE=openrouter}"
      export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
      export OPENAI_API_KEY="${OPENAI_API_KEY:-${OPENROUTER_API_KEY}}"
      ;;
    *)
      log "Unsupported AGENT_ROUTE for OpenAI-compatible CLI: ${route}"
      exit 1
      ;;
  esac
}

setup_opencode_env() {
  local route="${AGENT_ROUTE:-native}"
  case "${route}" in
    native)
      ;;
    proxy)
      export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-${AGENT_PROXY_URL:-http://localhost:8082}}"
      export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-${AGENT_PROXY_KEY:-pass}}"
      export OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX="${OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX:-128768}"
      export OPENCODE_CONFIG_CONTENT="${OPENCODE_CONFIG_CONTENT:-{\"provider\":{\"anthropic\":{\"options\":{\"baseURL\":\"${ANTHROPIC_BASE_URL}/v1\"}}}}}"
      ;;
    openrouter)
      : "${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY for AGENT_ROUTE=openrouter}"
      export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_AUTH_TOKEN:-${OPENROUTER_API_KEY}}"
      export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://openrouter.ai/api}"
      export OPENCODE_CONFIG_CONTENT="${OPENCODE_CONFIG_CONTENT:-{\"provider\":{\"anthropic\":{\"options\":{\"baseURL\":\"${ANTHROPIC_BASE_URL}/v1\"}}}}}"
      ;;
    *)
      log "Unsupported AGENT_ROUTE for opencode: ${route}"
      exit 1
      ;;
  esac
}

setup_gemini_env() {
  local route="${AGENT_ROUTE:-native}"
  if [[ "${route}" != "native" ]]; then
    log "Gemini CLI does not expose a documented generic custom-base-URL mode; use native Google auth."
    exit 1
  fi
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  local agent="$1"
  shift

  if [[ "${agent}" == "-h" || "${agent}" == "--help" ]]; then
    usage
    exit 0
  fi

  set_editor_env
  cd "${REPO_ROOT}"

  case "${agent}" in
    claude)
      require_cmd claude
      setup_claude_env
      exec claude "$@"
      ;;
    codex)
      require_cmd codex
      if [[ "${AGENT_MODE:-default}" != "default" ]]; then
        log "Codex ACP/IDE server mode is not wired here; use Codex's own IDE integration/config."
        exit 1
      fi
      setup_openai_compat_env
      exec codex "$@"
      ;;
    opencode)
      require_cmd opencode
      setup_opencode_env
      if [[ "${AGENT_MODE:-default}" == "acp" ]]; then
        exec opencode acp "$@"
      fi
      exec opencode "$@"
      ;;
    qwen)
      require_cmd qwen
      setup_openai_compat_env
      if [[ "${AGENT_MODE:-default}" == "acp" ]]; then
        exec qwen --acp "$@"
      fi
      exec qwen "$@"
      ;;
    gemini)
      require_cmd gemini
      setup_gemini_env
      exec gemini "$@"
      ;;
    custom)
      : "${CUSTOM_AGENT_BIN:?Set CUSTOM_AGENT_BIN for agent=custom}"
      require_cmd "${CUSTOM_AGENT_BIN}"
      split_args "${CUSTOM_AGENT_ARGS:-}"
      local custom_mode="${AGENT_MODE:-default}"
      if [[ "${custom_mode}" == "acp" ]]; then
        split_args "${CUSTOM_AGENT_ACP_ARGS:---acp}"
        exec "${CUSTOM_AGENT_BIN}" "${SPLIT_RESULT[@]}" "$@"
      fi
      split_args "${CUSTOM_AGENT_ARGS:-}"
      exec "${CUSTOM_AGENT_BIN}" "${SPLIT_RESULT[@]}" "$@"
      ;;
    *)
      log "Unknown agent: ${agent}"
      usage
      exit 1
      ;;
  esac
}

main "$@"

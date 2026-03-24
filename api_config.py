"""Shared API configuration for Anthropic-compatible endpoints."""

from __future__ import annotations

import os

DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com"
VALID_API_MODES = {"auto", "autonovel", "claude_code"}


def _clean(value: str | None) -> str:
    return value.strip() if value and value.strip() else ""


def _first_nonempty(*values: str | None) -> str:
    for value in values:
        cleaned = _clean(value)
        if cleaned:
            return cleaned
    return ""


def get_api_mode() -> str:
    mode = _clean(os.environ.get("AUTONOVEL_API_MODE", "auto")).lower()
    if not mode:
        return "auto"
    if mode not in VALID_API_MODES:
        raise ValueError(
            f"Invalid AUTONOVEL_API_MODE={mode!r}. "
            f"Expected one of: {', '.join(sorted(VALID_API_MODES))}."
        )
    return mode


def get_api_base_url() -> str:
    mode = get_api_mode()
    if mode == "autonovel":
        return _first_nonempty(
            os.environ.get("AUTONOVEL_API_BASE_URL"),
            DEFAULT_ANTHROPIC_BASE_URL,
        )
    if mode == "claude_code":
        return _first_nonempty(
            os.environ.get("ANTHROPIC_BASE_URL"),
            os.environ.get("AUTONOVEL_API_BASE_URL"),
            DEFAULT_ANTHROPIC_BASE_URL,
        )
    return _first_nonempty(
        os.environ.get("AUTONOVEL_API_BASE_URL"),
        os.environ.get("ANTHROPIC_BASE_URL"),
        DEFAULT_ANTHROPIC_BASE_URL,
    )


def get_api_key() -> str:
    mode = get_api_mode()
    if mode == "autonovel":
        return _first_nonempty(
            os.environ.get("AUTONOVEL_API_KEY"),
            os.environ.get("ANTHROPIC_API_KEY"),
        )
    if mode == "claude_code":
        return _first_nonempty(
            os.environ.get("ANTHROPIC_API_KEY"),
            os.environ.get("AUTONOVEL_API_KEY"),
        )
    return _first_nonempty(
        os.environ.get("AUTONOVEL_API_KEY"),
        os.environ.get("ANTHROPIC_API_KEY"),
    )


def get_auth_token() -> str:
    mode = get_api_mode()
    if mode == "autonovel":
        return _first_nonempty(
            os.environ.get("AUTONOVEL_AUTH_TOKEN"),
            os.environ.get("ANTHROPIC_AUTH_TOKEN"),
        )
    if mode == "claude_code":
        return _first_nonempty(
            os.environ.get("ANTHROPIC_AUTH_TOKEN"),
            os.environ.get("AUTONOVEL_AUTH_TOKEN"),
        )
    return _first_nonempty(
        os.environ.get("AUTONOVEL_AUTH_TOKEN"),
        os.environ.get("ANTHROPIC_AUTH_TOKEN"),
    )


def has_api_credentials() -> bool:
    return bool(get_auth_token() or get_api_key())


def build_api_headers(*, beta: str | None = None) -> dict[str, str]:
    headers = {
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    auth_token = get_auth_token()
    api_key = get_api_key()

    if auth_token:
        headers["authorization"] = f"Bearer {auth_token}"
    if api_key:
        headers["x-api-key"] = api_key
    if beta:
        headers["anthropic-beta"] = beta
    return headers


def apply_max_output_limit(max_tokens: int) -> int:
    """Optionally cap request output tokens from env."""
    cap = _first_nonempty(
        os.environ.get("AUTONOVEL_MAX_OUTPUT_TOKENS"),
        os.environ.get("CLAUDE_CODE_MAX_OUTPUT_TOKENS"),
    )
    if not cap:
        return max_tokens
    try:
        return min(max_tokens, int(cap))
    except ValueError:
        return max_tokens

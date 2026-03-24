# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python 3.12 automation pipeline for generating novels and export assets. Root-level scripts such as `run_pipeline.py`, `seed.py`, `evaluate.py`, and `review.py` handle orchestration, drafting, scoring, and revision. Shared runtime settings live in `project_config.py` and `api_config.py`; keep `.env` as the single source of truth for metadata, model routing, and optional git behavior. Canonical manuscript inputs live in `world.md`, `characters.md`, `outline.md`, `canon.md`, `voice.md`, and `state.json`. Generated prose belongs in `chapters/ch_XX.md`. Export assets live in `typeset/`, `landing/`, `art/`, and `audiobook/`.

## Build, Test, and Development Commands
Use **WSL/bash** for all local commands.

- `uv sync` installs project dependencies from `pyproject.toml` and `uv.lock`.
- `cp .env.example .env` creates the local config file for API keys.
- `uv run autonovel smoke-check` runs the lightweight compile and file-layout sanity check.
- `scripts/launch-agent.sh claude --continue --model=opus` starts a supported coding CLI with the repo’s launcher wrapper.
- `uv run python seed.py` generates or refreshes `seed.txt` content.
- `uv run python run_pipeline.py --from-scratch` starts the full pipeline from a clean state.
- `uv run python run_pipeline.py --phase foundation` runs a single pipeline phase for focused iteration.
- `uv run python evaluate.py` evaluates the current manuscript or chapter set.
- `uv run python review.py` runs the higher-level manuscript review loop.

## Coding Style & Naming Conventions
Follow existing Python style: 4-space indentation, standard-library imports first, small helper functions, and clear docstrings on non-trivial functions. Use `snake_case` for functions, files, JSON keys, and variables; keep chapter files named `ch_01.md`, `ch_02.md`, and so on. Prefer explicit paths via `pathlib.Path` and keep generated artifacts out of the repository unless they are templates or tracked examples.

## Testing Guidelines
There is no formal automated test suite yet. Treat pipeline checks as regression tests: run targeted commands after changes, especially `uv run python run_pipeline.py --phase foundation` and `uv run python evaluate.py`. When changing export code, also verify `typeset/build_tex.py` paths and the `landing/index.html` output assumptions. Document manual verification steps in the PR.

## Commit & Pull Request Guidelines
Recent history uses short, imperative messages with optional Conventional Commit scope, for example `fix(run_pipeline): remove redundant f.close()`. Keep commits focused and descriptive. PRs should include: purpose, affected scripts or content files, sample command(s) run in **WSL/bash**, and any generated outputs worth reviewing. Add screenshots only for `landing/` changes.

## Configuration & Safety
Never commit `.env` or secret keys. External integrations depend on Anthropic-compatible APIs, fal.ai, and ElevenLabs credentials. Prefer changing values in `.env.example` and `project_config.py` over adding new ad hoc env reads to scripts. Keep `AUTONOVEL_ENABLE_GIT=0` unless automated git commits are explicitly wanted, and avoid destructive git or file cleanup during pipeline work unless explicitly approved.

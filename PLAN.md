# PLAN — Autonovel

## Project Goal
Python 3.12 automated novel generation pipeline with chapters, typesetting, art, audiobook, and landing page generation.

## Key Files Already Present
- `README.md`, `AGENTS.md`, `ANTI-SLOP.md`, `CRAFT.md`, `MYSTERY.md`, `voice.md`, `AUTHOR_NOTES.md` — Project documentation
- `run_pipeline.py`, `seed.py`, `evaluate.py`, `review.py` — Core pipeline scripts
- `project_config.py`, `api_config.py` — Configuration
- `chapters/` — 10 generated chapter files (ch_01 through ch_10)
- `typeset/` — Export assets (epub front/back matter, colophon)
- `pyproject.toml`, `uv.lock` — Dependency management
- Uses Anthropic-compatible APIs, fal.ai, and ElevenLings credentials

## What's Done
- Full pipeline from seed to chapters to evaluation
- Export typesetting (ePub)
- Smoke check and multi-phase pipeline execution
- Agent guidelines defined

## What's Needed
- [ ] Consider YouTube transcript extraction integration (E7 — noted, low priority)
- [ ] Add formal automated test suite
- [ ] Resolve any remaining export pipeline issues

## Related Scratchfiles
- E7: `~/.hermes/pastes/E7.md` — autonovel-youtube

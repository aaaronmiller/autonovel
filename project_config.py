"""Shared project settings and metadata."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env", override=True)

CHAPTERS_DIR = BASE_DIR / "chapters"
BRIEFS_DIR = BASE_DIR / "briefs"
EDIT_LOGS_DIR = BASE_DIR / "edit_logs"
EVAL_LOGS_DIR = BASE_DIR / "eval_logs"
TYPES_DIR = BASE_DIR / "typeset"
LANDING_DIR = BASE_DIR / "landing"
AUDIO_DIR = BASE_DIR / "audiobook"

WRITER_MODEL = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")
JUDGE_MODEL = os.environ.get("AUTONOVEL_JUDGE_MODEL", "claude-opus-4-6")
REVIEW_MODEL = os.environ.get("AUTONOVEL_REVIEW_MODEL", "claude-opus-4-6")

FAL_KEY = os.environ.get("FAL_KEY", "")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

PROJECT_TITLE = os.environ.get("AUTONOVEL_TITLE", "Untitled Novel")
PROJECT_AUTHOR = os.environ.get("AUTONOVEL_AUTHOR", "Author Name")
PROJECT_SUBTITLE = os.environ.get("AUTONOVEL_SUBTITLE", "A Novel")
PROJECT_TAGLINE = os.environ.get(
    "AUTONOVEL_TAGLINE",
    "A fresh novel project generated with autonovel.",
)
PROJECT_DESCRIPTION = os.environ.get(
    "AUTONOVEL_DESCRIPTION",
    "Use this landing page as a starter template for the current manuscript.",
)
PROJECT_WEBSITE = os.environ.get("AUTONOVEL_WEBSITE", "https://example.com")


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_GIT = env_flag("AUTONOVEL_ENABLE_GIT", default=False)


def chapter_files() -> list[Path]:
    return sorted(CHAPTERS_DIR.glob("ch_*.md"))


def project_title() -> str:
    outline = BASE_DIR / "outline.md"
    if outline.exists():
        first = outline.read_text(encoding="utf-8").splitlines()[0].strip()
        if first.startswith("#"):
            title = first.lstrip("# ").strip()
            if title and title.lower() != "outline":
                return title
    chapters = chapter_files()
    if chapters:
        first = chapters[0].read_text(encoding="utf-8").splitlines()[0].strip()
        if first.startswith("#"):
            title = first.lstrip("# ").strip()
            if title:
                return title
    return PROJECT_TITLE


def project_metadata() -> dict[str, str]:
    return {
        "title": project_title(),
        "author": PROJECT_AUTHOR,
        "subtitle": PROJECT_SUBTITLE,
        "tagline": PROJECT_TAGLINE,
        "description": PROJECT_DESCRIPTION,
        "website": PROJECT_WEBSITE,
    }

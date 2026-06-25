#!/usr/bin/env python3
"""
Draft a single chapter using the writer model.
Usage: python draft_chapter.py 1
"""
import re
import sys
import os
import math
import time
from pathlib import Path
from api_config import apply_max_output_limit, build_api_headers, extract_message_text, get_api_base_url
from project_config import BASE_DIR, CHAPTERS_DIR, WRITER_MODEL, project_title

API_BASE = get_api_base_url()
DEFAULT_NOVEL_PAGES = 399
DEFAULT_WORDS_PER_PAGE = 275
DEFAULT_PASS_WORDS = 3200
DEFAULT_PASS_DELAY_SECONDS = 12

def call_writer(prompt, max_tokens=16000):
    import httpx
    headers = build_api_headers(beta="context-1m-2025-08-07")
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": apply_max_output_limit(max_tokens),
        "temperature": 0.8,
        "system": (
            "You are a literary fiction writer drafting a fantasy novel chapter. "
            "You write in third-person limited past tense, locked to one POV character. "
            "You follow the voice definition exactly. You hit every beat in the outline. "
            "You never use words from the banned list. You show, never tell emotions. "
            "Your prose is specific, sensory, grounded. Metaphors come from the character's "
            "experience. You vary sentence length. You trust the reader. "
            "You write the FULL chapter -- do not truncate, summarize, or skip ahead."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    response_payload = resp.json()
    try:
        return extract_message_text(response_payload)
    except KeyError:
        if "openrouter.ai" not in API_BASE:
            raise
        return call_writer_via_openrouter_chat(prompt, max_tokens=max_tokens)


def call_writer_via_openrouter_chat(prompt, max_tokens=16000):
    import httpx

    headers = build_api_headers()
    headers.pop("anthropic-version", None)
    headers.pop("anthropic-beta", None)
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": max(2000, apply_max_output_limit(max_tokens)),
        "temperature": 0.8,
        "reasoning": {"effort": "low"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a literary fiction writer drafting a fantasy novel chapter. "
                    "You write in third-person limited past tense, locked to one POV character. "
                    "You follow the voice definition exactly. You hit every beat in the outline. "
                    "You never use words from the banned list. You show, never tell emotions. "
                    "Your prose is specific, sensory, grounded. Metaphors come from the character's "
                    "experience. You vary sentence length. You trust the reader."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    resp = httpx.post(f"{API_BASE}/v1/chat/completions", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    payload = resp.json()
    message = payload["choices"][0]["message"]
    return message.get("content") or message.get("reasoning", "")

def load_file(path):
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""

def extract_chapter_outline(outline_text, chapter_num):
    """Extract a specific chapter's outline entry."""
    pattern = rf'### Ch {chapter_num}:.*?(?=### Ch {chapter_num + 1}:|## Foreshadowing|$)'
    match = re.search(pattern, outline_text, re.DOTALL)
    return match.group(0).strip() if match else "(not found)"

def extract_next_chapter_outline(outline_text, chapter_num):
    """Extract the next chapter's outline (just first few lines for continuity)."""
    next_entry = extract_chapter_outline(outline_text, chapter_num + 1)
    if next_entry == "(not found)":
        return "(final chapter)"
    lines = next_entry.split('\n')[:10]
    return '\n'.join(lines)


def infer_total_chapters(outline_text):
    matches = re.findall(r'####\s+\*\*Ch\s+(\d+):|###\s+\*\*Ch\s+(\d+):|###\s+Ch\s+(\d+):', outline_text)
    numbers = []
    for left, middle, right in matches:
        raw = left or middle or right
        if raw:
            numbers.append(int(raw))
    return max(numbers) if numbers else 18


def infer_chapter_target_words(outline_text):
    novel_pages = int(os.environ.get("AUTONOVEL_NOVEL_PAGES", str(DEFAULT_NOVEL_PAGES)))
    words_per_page = int(os.environ.get("AUTONOVEL_WORDS_PER_PAGE", str(DEFAULT_WORDS_PER_PAGE)))
    total_chapters = infer_total_chapters(outline_text)
    return round((novel_pages * words_per_page) / total_chapters)


def build_pass_prompt(
    *,
    chapter_num,
    chapter_target_words,
    total_passes,
    current_pass,
    voice,
    chapter_outline,
    next_chapter,
    prev_tail,
    world,
    characters,
    existing_text="",
):
    if current_pass == 1:
        pass_instruction = (
            f"This is pass 1 of {total_passes}. Draft the opening portion of the chapter. "
            "Do not try to finish the chapter if more story remains. End at a natural hinge point "
            "with forward pressure, not with chapter-closing summary."
        )
    elif current_pass < total_passes:
        pass_instruction = (
            f"This is continuation pass {current_pass} of {total_passes}. Continue seamlessly from the existing draft. "
            "Do not restart, recap, or repeat prior material. Cover the next major beats and stop at another natural hinge."
        )
    else:
        pass_instruction = (
            f"This is final continuation pass {current_pass} of {total_passes}. Continue seamlessly from the existing draft "
            "and complete the chapter, resolving any remaining beats while setting up the next chapter."
        )

    existing_section = ""
    if existing_text:
        existing_section = f"""
EXISTING DRAFT (continue from this exact material; do not repeat it):
{existing_text}
"""

    return f"""Write Chapter {chapter_num} of "{project_title()}".

VOICE DEFINITION (follow this exactly):
{voice}

THIS CHAPTER'S OUTLINE (hit every beat):
{chapter_outline}

NEXT CHAPTER'S OUTLINE (for continuity -- end this chapter so it flows into the next):
{next_chapter}

PREVIOUS CHAPTER'S ENDING (continue from here):
{prev_tail}
{existing_section}
WORLD BIBLE (reference for worldbuilding details):
{world}

CHARACTER REGISTRY (reference for speech patterns and behavior):
{characters}

WRITING INSTRUCTIONS:
1. Full chapter target: ~{chapter_target_words:,} words across all passes.
2. {pass_instruction}
3. Follow the POV and tense specified by the outline and voice documents.
4. Hit ALL numbered beats from the outline in order across the full chapter.
5. Plant ALL foreshadowing elements listed under "Plants."
6. Show sensory detail through the viewpoint character's body and attention.
7. Dialogue follows the speech patterns defined in characters.md.
8. No banned words from voice.md Part 1 guardrails.
9. No AI fiction tells: no "a sense of," no "couldn't help but feel," no "eyes widened."
10. Vary sentence length. Short sentences for impact. Longer ones to build.
11. Metaphors should come from the viewpoint character's experience, trade, fears, and habits.
12. Trust the reader. Don't explain what scenes mean. Let them land.
13. Start in scene. No exposition throat-clearing. No recap.
14. Do not label this as Part 1 or Part 2.
15. Do not repeat lines or re-summarize prior events when continuing.

PATTERNS TO AVOID:
16. NO triadic sensory lists. Never "X. Y. Z." or "X and Y and Z" as three
    separate items in a row. Combine two, cut one, or restructure.
17. NO "He did not [verb]" more than once per chapter. Convert negatives
    to active alternatives or just cut them.
18. NO "He thought about [X]" constructions. Replace with: the thought
    itself as a fragment, a physical action, or dialogue.
19. NO "the way [X] did [Y]" as a simile connector more than twice per
    chapter. Use different simile structures or cut the comparison.
20. NO over-explaining after showing. If a scene demonstrates something,
    do not have the narrator restate it. Trust the scene.
21. FAVOR scene over summary. At least 70% of the chapter should be
    in-scene (moment by moment, with dialogue and action) rather than
    summary (narrator compressing time).
22. DIALOGUE should sound like speech, not prose. Characters should
    occasionally stumble, interrupt, trail off, or say something
    slightly wrong.

Write the text for this pass now.
"""

def main():
    chapter_num = int(sys.argv[1])
    pass_word_budget = int(os.environ.get("AUTONOVEL_DRAFT_PASS_WORDS", str(DEFAULT_PASS_WORDS)))
    pass_delay_seconds = int(os.environ.get("AUTONOVEL_DRAFT_PASS_DELAY_SECONDS", str(DEFAULT_PASS_DELAY_SECONDS)))
    
    # Load all context
    voice = load_file(BASE_DIR / "voice.md")
    world = load_file(BASE_DIR / "world.md")
    characters = load_file(BASE_DIR / "characters.md")
    outline = load_file(BASE_DIR / "outline.md")
    canon = load_file(BASE_DIR / "canon.md")
    chapter_target_words = int(
        os.environ.get("AUTONOVEL_CHAPTER_TARGET_WORDS", str(infer_chapter_target_words(outline)))
    )
    
    # Chapter-specific context
    chapter_outline = extract_chapter_outline(outline, chapter_num)
    next_chapter = extract_next_chapter_outline(outline, chapter_num)
    
    # Previous chapter (if exists)
    prev_path = CHAPTERS_DIR / f"ch_{chapter_num - 1:02d}.md"
    if prev_path.exists():
        prev_text = prev_path.read_text()
        prev_tail = prev_text[-2000:] if len(prev_text) > 2000 else prev_text
    else:
        prev_tail = "(first chapter -- no previous)"
    
    total_passes = max(1, math.ceil(chapter_target_words / pass_word_budget))
    print(
        f"Drafting Chapter {chapter_num} in {total_passes} pass(es) "
        f"(target {chapter_target_words} words)...",
        file=sys.stderr,
    )

    result_parts = []
    for current_pass in range(1, total_passes + 1):
        if current_pass > 1:
            print(f"Cooling down {pass_delay_seconds}s before pass {current_pass}...", file=sys.stderr)
            time.sleep(pass_delay_seconds)
        prompt = build_pass_prompt(
            chapter_num=chapter_num,
            chapter_target_words=chapter_target_words,
            total_passes=total_passes,
            current_pass=current_pass,
            voice=voice,
            chapter_outline=chapter_outline,
            next_chapter=next_chapter,
            prev_tail=prev_tail,
            world=world,
            characters=characters,
            existing_text="\n\n".join(result_parts),
        )
        print(f"Pass {current_pass}/{total_passes}...", file=sys.stderr)
        part = call_writer(prompt)
        result_parts.append(part.strip())

    result = "\n\n".join(part for part in result_parts if part)
    
    # Save
    out_path = CHAPTERS_DIR / f"ch_{chapter_num:02d}.md"
    out_path.write_text(result)
    print(f"Saved to {out_path}", file=sys.stderr)
    print(f"Word count: {len(result.split())}", file=sys.stderr)
    print(result)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate outline.md from seed + world + characters + mystery + craft."""
import sys
from api_config import apply_max_output_limit, build_api_headers, get_api_base_url
from project_config import BASE_DIR, WRITER_MODEL

API_BASE = get_api_base_url()

def call_writer(prompt, max_tokens=16000):
    import httpx
    headers = build_api_headers(beta="context-1m-2025-08-07")
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": apply_max_output_limit(max_tokens),
        "temperature": 0.5,
        "system": (
            "You are a novel architect with deep knowledge of Save the Cat beats, "
            "Sanderson's plotting principles, Dan Harmon's Story Circle, and MICE Quotient. "
            "You build outlines that an author can draft from without inventing structure "
            "on the fly. Every chapter has beats, emotional arc, and try-fail cycle type. "
            "You never use AI slop words. You write in clean, direct prose."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

seed = (BASE_DIR / "seed.txt").read_text()
world = (BASE_DIR / "world.md").read_text()
characters = (BASE_DIR / "characters.md").read_text()
mystery = (BASE_DIR / "MYSTERY.md").read_text()
craft = (BASE_DIR / "CRAFT.md").read_text()

# Voice Part 2 only
voice = (BASE_DIR / "voice.md").read_text()
voice_lines = voice.split('\n')
part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
voice_part2 = '\n'.join(voice_lines[part2_start:])

prompt = f"""Build a complete chapter outline for this novel. Target an appropriate
chapter count and total length for the seed, world, and voice rather than forcing a
single template.

SEED CONCEPT:
{seed}

THE CENTRAL MYSTERY (author's eyes only -- reader discovers gradually):
{mystery}

WORLD BIBLE:
{world}

CHARACTER REGISTRY:
{characters}

VOICE (tone and register):
{voice_part2}

CRAFT REFERENCE (structures to follow):
{craft}

BUILD THE OUTLINE WITH:

## Act Structure or Structural Model
If this novel is operating on a beat-sheet structure, map out the acts and percentage marks.
If it is literary or non-beat-sheet, name the structural model explicitly and explain how
progression works.

## Chapter-by-Chapter Outline

For EACH chapter, provide:
### Ch N: [Title]
- **POV:** (the actual POV character for that chapter)
- **Location:** Which districts/locations
- **Structural function:** Which beat / structural role this chapter serves
- **% mark:** Where this falls in the novel
- **Emotional arc:** Starting emotion → ending emotion
- **Try-fail cycle:** Yes-but / No-and / No-but / Yes-and
- **Beats:** 3-5 specific scene beats that must happen
- **Plants:** Foreshadowing elements planted in this chapter
- **Payoffs:** Foreshadowing elements that pay off here
- **Character movement:** What changes for the POV character or key cast by chapter's end
- **Central misconception / pressure:** How the protagonist's current false belief,
  coping strategy, or emotional blind spot is reinforced or challenged
- **~Word count target:** for pacing

## Foreshadowing Ledger

A table tracking every planted thread:
| Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Type |

Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.

CONSTRAINTS:
- The climax must be mechanically or psychologically resolvable using what the story
  has already established
- The shape of the plot should emerge from the seed, not from stock fantasy defaults
- The Stability Trap: bad things must stay bad. Not everything resolves cleanly.
- At least 3 chapters should be "quiet" -- character-focused, low-action, emotionally rich
- Vary the try-fail types: 60%+ should be "yes-but" or "no-and"
- The foreshadowing ledger must have plant-to-payoff distances of at least 3 chapters
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
print(result)

#!/usr/bin/env python3
"""
One-shot characters.md generator for foundation phase.
Reads seed.txt + voice.md + world.md + CRAFT.md, calls writer model.
"""
import sys
from api_config import apply_max_output_limit, build_api_headers, get_api_base_url
from project_config import BASE_DIR, WRITER_MODEL

API_BASE = get_api_base_url()

def call_writer(prompt, max_tokens=16000):
    import httpx
    headers = build_api_headers()
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": apply_max_output_limit(max_tokens),
        "temperature": 0.7,
        "system": (
            "You are a character designer for literary fiction with deep knowledge of "
            "wound/want/need/lie frameworks, Sanderson's three sliders, and dialogue "
            "distinctiveness. You create characters who feel like real people with "
            "contradictions, secrets, and speech patterns you can hear. "
            "You never use AI slop words. You write in clean, direct prose."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

seed = (BASE_DIR / "seed.txt").read_text()
world = (BASE_DIR / "world.md").read_text()

# Voice Part 2 only
voice = (BASE_DIR / "voice.md").read_text()
voice_lines = voice.split('\n')
part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
voice_part2 = '\n'.join(voice_lines[part2_start:])

prompt = f"""Build a complete character registry for this novel. This is CHARACTERS.MD --
the definitive reference for WHO exists in this story, what drives them, how they speak,
and what secrets they carry.

SEED CONCEPT:
{seed}

WORLD BIBLE (the world these characters inhabit):
{world}

VOICE IDENTITY (the novel's tone):
{voice_part2}

CHARACTER CRAFT REQUIREMENTS (from CRAFT.md):

### The Three Sliders (Sanderson)
Every character has three independent dials (0-10):
  PROACTIVITY -- Do they drive the plot or react to it?
  LIKABILITY  -- Does the reader empathize with them?
  COMPETENCE  -- Are they good at what they do?
Rule: compelling = HIGH on at least TWO, or HIGH on one with clear growth.

### Wound / Want / Need / Lie Framework
A causal chain:
  GHOST (backstory event) -> WOUND (ongoing damage) -> LIE (false belief to cope)
    -> WANT (external goal driven by Lie) -> NEED (internal truth, opposes Lie)
Rules: Want and Need must be IN TENSION. Lie statable in one sentence.
  Truth is its direct opposite.

### Dialogue Distinctiveness (8 dimensions)
1. Vocabulary level  2. Sentence length  3. Contractions/formality
4. Verbal tics  5. Question vs statement ratio  6. Interruption patterns
7. Metaphor domain  8. Directness vs indirectness
Test: Remove dialogue tags. Can you tell who's speaking?

BUILD THE REGISTRY WITH:

1. **The protagonist / primary POV**
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions)
   - Physical habits and tells
   - At least 2 secrets
   - Key relationships mapped

2. **A close personal counterforce**
   - Family member, partner, friend, rival, or mentor whose logic conflicts
     with the protagonist's even when they care about them

3. **A primary external antagonist or institutional obstacle**
   - Not a cartoon villain
   - Their own wound/want/need/lie (they should be understandable)

4. **At least two consequential supporting characters**
   - One ally or accomplice with an agenda of their own
   - One supporting character who can surprise the story

5. **Any additional characters the premise clearly requires**
   - Protecting the social, political, or professional ecosystem of the book

FOR EACH CHARACTER INCLUDE:
- Name, age, role
- Ghost/Wound/Want/Need/Lie chain (for major characters)
- Three sliders (proactivity/likability/competence) with numbers and justification
- Arc type and arc trajectory
- Speech pattern (all 8 dimensions, with example lines)
- Physical appearance (specific, not generic)
- Physical habits and unconscious tells
- Secrets (what the reader doesn't learn immediately)
- Key relationships (mapped to other characters)
- Thematic role (what question does this character embody?)

IMPORTANT:
- Characters must INTERCONNECT. Their wants should conflict with each other.
- Every secret should be something that would CHANGE the story if revealed.
- Speech patterns must be distinct enough to pass the no-tags test.
- The protagonist's habits should emerge from their pressures, not from generic
  "main character" behavior.
- Any recurring physical tell should connect to something specific and causal.
- The antagonist or counterforce should be as fully realized as the protagonist.
- Target ~3000-4000 words. Dense character work, not padding.
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
print(result)

#!/usr/bin/env python3
"""
One-shot world.md generator for foundation phase.
Reads seed.txt + voice.md, calls the writer model, outputs world.md content.
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
            "You are a fantasy worldbuilder with deep knowledge of Sanderson's Laws, "
            "Le Guin's prose philosophy, and TTRPG-quality lore design. "
            "You write world bibles that are specific, interconnected, and imply depth "
            "beyond what's stated. You never use AI slop words (delve, tapestry, myriad, etc). "
            "You write in clean, direct prose. Every rule has a cost. Every cultural detail "
            "implies a history. Every location has a sensory signature."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

seed = (BASE_DIR / "seed.txt").read_text()
voice = (BASE_DIR / "voice.md").read_text()
craft = (BASE_DIR / "CRAFT.md").read_text()

# Extract voice Part 2 only (the novel-specific voice)
voice_lines = voice.split('\n')
part2_start = next(i for i, l in enumerate(voice_lines) if 'Part 2' in l)
voice_part2 = '\n'.join(voice_lines[part2_start:])

prompt = f"""Build a complete world bible for this novel. This is the WORLD.MD file --
the definitive reference for everything that EXISTS in this world. A writer should be able 
to resolve any worldbuilding question from this document alone.

SEED CONCEPT:
{seed}

VOICE IDENTITY (the tone and register of this novel):
{voice_part2}

CRAFT REQUIREMENTS (from CRAFT.md -- follow these):
- Magic system needs HARD RULES with COSTS and LIMITATIONS per Sanderson's Second Law
- Limitations >= powers in narrative prominence
- Trace implications of magic through society, economy, law, religion
- At least 2-3 societal implications of magic explored in depth
- History must create PRESENT-DAY TENSIONS that drive the plot (not just backdrop)
- Geography must be specific and sensory (not generic fantasy)
- Iceberg principle: imply more than you state
- Interconnection: pulling one thread should move everything

STRUCTURE THE DOCUMENT WITH THESE SECTIONS:

## Cosmology & History
A timeline of major events. Focus on events that create PRESENT-DAY tensions.
Include the founding myth, key turning points, and recent events that matter to the plot.

## Magic System
### Hard Rules
Specific, testable rules for the governing system of the story.
If the novel is speculative, define what the system does, what it costs,
and what happens when characters break the rules.

### Soft Rules / Edge Cases
What remains mysterious, intuitive, folkloric, or exceptional?
If the novel has no speculative system, use this section for social rules,
taboos, institutional constraints, or the story's most important ambiguities.

### Societal Implications
How do the governing rules of this world shape governance, commerce,
education, class structure, crime, family life, and daily routine?

## Geography
Physical layout, neighboring places (at least 2-3), and sensory signatures
for each major location.

## Factions & Politics
Who holds power, who wants it, who's being crushed by it.
At least 3-4 factions with opposing interests.

## Bestiary / Flora / Natural World
What's unique about the natural world in and around the story's setting?

## Cultural Details
Customs, taboos, festivals, food, clothing, coming-of-age rituals.
Things that make daily life feel SPECIFIC.

## Internal Consistency Rules
Hard constraints a writer must not violate. What is possible, impossible,
or socially forbidden in this setting?

IMPORTANT:
- Be SPECIFIC. Not "the city has districts" but name them, describe them, 
  give them sensory signatures.
- Every rule should have a COST or LIMITATION stated alongside it.
- Include 2-3 facts per section that are unexplained, hinting at deeper systems 
  (iceberg depth).
- Facts should INTERCONNECT: the magic should shape the politics, the geography 
  should shape the culture, the history should explain current faction conflicts.
- Write in clean, direct prose. No AI slop. No "rich tapestry." No "delving."
- The world should feel grounded and LIVED-IN, not imagined. Think: what does 
  breakfast smell like? What do children play? How do old people complain?
- Target ~3000-4000 words. Dense, not padded.
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
print(result)

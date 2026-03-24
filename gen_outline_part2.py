#!/usr/bin/env python3
"""Generate remaining chapters + foreshadowing ledger."""
import sys
from api_config import apply_max_output_limit, build_api_headers, get_api_base_url
from project_config import BASE_DIR, WRITER_MODEL, project_title

API_BASE = get_api_base_url()

def call_writer(prompt, max_tokens=16000):
    import httpx
    headers = build_api_headers()
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": apply_max_output_limit(max_tokens),
        "temperature": 0.5,
        "system": (
            "You are a novel architect continuing an outline. Write in the same format "
            "as the preceding chapters. Every chapter needs: POV, Location, Save the Cat beat, "
            "% mark, Emotional arc, Try-fail cycle, Beats, Plants, Payoffs, Character movement, "
            "The lie, Word count target."
        ),
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

outline_seed = Path("/tmp/outline_output.md")
part1 = outline_seed.read_text() if outline_seed.exists() else (BASE_DIR / "outline.md").read_text()
mystery = (BASE_DIR / "MYSTERY.md").read_text()

prompt = f"""Here is a partial outline for "{project_title()}".
The outline may be truncated. Continue from where it left off, complete the remaining
chapters needed by the structure already implied here, then write the Foreshadowing Ledger.

THE OUTLINE SO FAR:
{part1}

THE CENTRAL MYSTERY (for reference):
{mystery}

Then write:

## Foreshadowing Ledger

| # | Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Type |
|---|--------|-------------|-----------------|-------------|------|

Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.
Plant-to-payoff distance must be at least 3 chapters.

REMEMBER:
- Preserve and complete the structure already established in the existing outline
- Not everything should resolve cleanly
- The protagonist's key misconception should be fully tested by the climax
- The final image should feel like a transformed echo of the opening
- At least one quiet chapter should exist in the back half
"""

print("Calling writer model...", file=sys.stderr)
result = call_writer(prompt)
print(result)

#!/usr/bin/env python3
"""
Build a condensed arc summary for full-novel evaluation.
For each chapter: first 150 words, last 150 words, plus any dialogue.
Gives the reader panel enough to evaluate the ARC without 72k tokens.
"""
import re
from api_config import apply_max_output_limit, build_api_headers, get_api_base_url
from project_config import BASE_DIR, CHAPTERS_DIR, WRITER_MODEL, chapter_files, project_title

API_BASE = get_api_base_url()

def call_writer(prompt, max_tokens=4000):
    import httpx
    headers = build_api_headers()
    payload = {
        "model": WRITER_MODEL,
        "max_tokens": apply_max_output_limit(max_tokens),
        "temperature": 0.1,
        "system": "You summarize novel chapters precisely. State what HAPPENS, what CHANGES, and what QUESTIONS are left open. No evaluation. No praise. Just events and shifts.",
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = httpx.post(f"{API_BASE}/v1/messages", headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def extract_key_passages(text):
    """Get opening, closing, and best dialogue from a chapter."""
    words = text.split()
    opening = ' '.join(words[:150])
    closing = ' '.join(words[-150:])
    
    # Extract dialogue lines
    dialogue = re.findall(r'["""]([^"""]{20,})["""]', text)
    # Pick up to 3 longest dialogue lines
    dialogue.sort(key=len, reverse=True)
    top_dialogue = dialogue[:3]
    
    return opening, closing, top_dialogue

def main():
    summaries = []

    files = chapter_files()
    for ch, path in enumerate(files, start=1):
        text = path.read_text()
        wc = len(text.split())
        opening, closing, dialogue = extract_key_passages(text)
        
        # Get a 100-word summary from the model
        summary = call_writer(
            f"Summarize this chapter in exactly 3 sentences. What happens, what changes, what question is left open.\n\nCHAPTER {ch}:\n{text}",
            max_tokens=200
        )
        
        entry = f"""### Chapter {ch} ({wc} words)
**Summary:** {summary}

**Opening:** {opening}...

**Closing:** ...{closing}

**Key dialogue:**
"""
        for d in dialogue:
            entry += f'> "{d}"\n\n'
        
        summaries.append(entry)
        print(f"Ch {ch}: summarized ({wc}w)")
    
    total_wc = sum(len(path.read_text().split()) for path in files)
    
    # Assemble
    full = f"""# {project_title()}
## Full-Arc Summary for Reader Panel

This document contains chapter summaries, opening/closing passages,
and key dialogue for all {len(files)} chapters. Total novel: {total_wc:,} words.

---

"""
    full += '\n---\n\n'.join(summaries)
    
    out_path = BASE_DIR / "arc_summary.md"
    out_path.write_text(full)
    print(f"\nSaved to {out_path} ({len(full.split())} words)")

if __name__ == "__main__":
    main()

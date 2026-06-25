#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

MAX_RETRIES="${MAX_RETRIES:-4}"
BACKOFF_BASE_SECONDS="${BACKOFF_BASE_SECONDS:-20}"
AUTONOVEL_MAX_OUTPUT_TOKENS="${AUTONOVEL_MAX_OUTPUT_TOKENS:-5500}"
AUTONOVEL_DRAFT_PASS_WORDS="${AUTONOVEL_DRAFT_PASS_WORDS:-3200}"
AUTONOVEL_DRAFT_PASS_DELAY_SECONDS="${AUTONOVEL_DRAFT_PASS_DELAY_SECONDS:-15}"

infer_total_chapters() {
  python3 - <<'PY'
import re
from pathlib import Path
text = Path('outline.md').read_text(encoding='utf-8')
matches = re.findall(r'###\s+\*\*Ch\s+(\d+):|###\s+Ch\s+(\d+):', text)
nums = [int(a or b) for a, b in matches if a or b]
print(max(nums) if nums else 18)
PY
}

current_max_chapter() {
  python3 - <<'PY'
import re
from pathlib import Path
nums = []
for path in Path('chapters').glob('ch_*.md'):
    m = re.search(r'ch_(\d+)\.md$', path.name)
    if m:
        nums.append(int(m.group(1)))
print(max(nums) if nums else 0)
PY
}

update_state() {
  python3 - <<'PY'
import json
from pathlib import Path
state_path = Path('state.json')
chapters = sorted(Path('chapters').glob('ch_*.md'))
count = len(chapters)
state = {}
if state_path.exists():
    state = json.loads(state_path.read_text(encoding='utf-8'))
state['chapters_drafted'] = count
state['chapters_total'] = max(state.get('chapters_total', 0), count)
if count >= state.get('chapters_total', count):
    state['phase'] = 'revision'
    state['current_focus'] = 'full_draft_complete'
else:
    state['phase'] = 'drafting'
    state['current_focus'] = f'chapter_{count + 1:02d}'
state_path.write_text(json.dumps(state, indent=2), encoding='utf-8')
PY
}

TOTAL_CHAPTERS="${TOTAL_CHAPTERS:-$(infer_total_chapters)}"
START_CHAPTER="${START_CHAPTER:-$(( $(current_max_chapter) + 1 ))}"

printf '[draft-loop] total_chapters=%s\n' "$TOTAL_CHAPTERS" >&2
printf '[draft-loop] start_chapter=%s\n' "$START_CHAPTER" >&2
printf '[draft-loop] max_output=%s\n' "$AUTONOVEL_MAX_OUTPUT_TOKENS" >&2

if (( START_CHAPTER > TOTAL_CHAPTERS )); then
  echo "[draft-loop] Nothing to do." >&2
  update_state
  exit 0
fi

for (( chapter=START_CHAPTER; chapter<=TOTAL_CHAPTERS; chapter++ )); do
  printf '\n[draft-loop] chapter=%02d\n' "$chapter" >&2
  success=0
  for (( attempt=1; attempt<=MAX_RETRIES; attempt++ )); do
    printf '[draft-loop] attempt=%s/%s chapter=%02d\n' "$attempt" "$MAX_RETRIES" "$chapter" >&2
    if /usr/bin/time -f '[draft-loop] elapsed=%E exit=%x' \
      env \
        AUTONOVEL_MAX_OUTPUT_TOKENS="$AUTONOVEL_MAX_OUTPUT_TOKENS" \
        AUTONOVEL_DRAFT_PASS_WORDS="$AUTONOVEL_DRAFT_PASS_WORDS" \
        AUTONOVEL_DRAFT_PASS_DELAY_SECONDS="$AUTONOVEL_DRAFT_PASS_DELAY_SECONDS" \
        "${SCRIPT_DIR}/run-openrouter-hybrid.sh" draft_chapter.py "$chapter"
    then
      success=1
      update_state
      break
    fi
    wait_seconds=$(( BACKOFF_BASE_SECONDS * attempt ))
    printf '[draft-loop] chapter=%02d failed, backing off %ss\n' "$chapter" "$wait_seconds" >&2
    sleep "$wait_seconds"
  done
  if (( success == 0 )); then
    printf '[draft-loop] chapter=%02d failed after %s attempts\n' "$chapter" "$MAX_RETRIES" >&2
    exit 1
  fi
done

update_state
echo "[draft-loop] completed all chapters" >&2

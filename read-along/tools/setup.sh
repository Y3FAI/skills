#!/usr/bin/env bash
# One-time setup for the read-along skill: a Python venv with Kokoro (local voice), BeautifulSoup
# (page parsing) and the spaCy English model Kokoro's G2P needs. Re-running is safe.
#
#   bash tools/setup.sh            # venv at ~/.cache/read-along/venv
#   READALONG_VENV=/some/path bash tools/setup.sh
#
# Afterwards run the tool with that venv's python:
#   ~/.cache/read-along/venv/bin/python tools/readalong.py CONFIG plan|voice|render|publish
#
# Also needed on PATH: ffmpeg + ffprobe (brew install ffmpeg). For Whisper checks and R2 uploads:
# node/npx with a logged-in wrangler (npx wrangler login).
set -euo pipefail

VENV="${READALONG_VENV:-$HOME/.cache/read-along/venv}"
SPACY_MODEL="https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: needs uv (https://docs.astral.sh/uv/) — e.g. curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi
for tool in ffmpeg ffprobe; do
  command -v "$tool" >/dev/null 2>&1 || echo "warning: $tool is not on PATH (render needs it: brew install ffmpeg)" >&2
done

# Kokoro supports Python 3.10–3.12.
[ -x "$VENV/bin/python" ] || uv venv "$VENV" --python 3.11
uv pip install --python "$VENV/bin/python" "kokoro>=0.9.4" soundfile beautifulsoup4 "en_core_web_sm @ $SPACY_MODEL"

# First run downloads the model weights (~330 MB) from Hugging Face; do it now and confirm it speaks.
"$VENV/bin/python" - <<'PY'
import os
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
from kokoro import KPipeline
pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
n = sum(len(r.audio) for r in pipe("The read along voice is ready.", voice="af_heart"))
print(f"kokoro ok: {n / 24000:.1f} s of audio")
PY
echo "ready: $VENV/bin/python"

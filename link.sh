#!/usr/bin/env bash
# Link every skill in this folder into each installed agent's skills folder.
# Skips an agent whose config folder doesn't exist, and never replaces a real folder.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd -P)"
for dest in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.pi/agent/skills"; do
  [ -d "$(dirname "$dest")" ] || continue
  mkdir -p "$dest"
  for s in "$here"/*/; do
    s="${s%/}"
    [ -f "$s/SKILL.md" ] || continue
    n="$(basename "$s")"
    if [ -e "$dest/$n" ] && [ ! -L "$dest/$n" ]; then
      echo "skip   $dest/$n (a real folder is there)"
      continue
    fi
    ln -sfn "$s" "$dest/$n"
    echo "linked $dest/$n"
  done
done

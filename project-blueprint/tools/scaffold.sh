#!/usr/bin/env bash
# Lays the blueprint's files into a project. Never overwrites: an existing file is skipped (and
# listed), except .gitignore, which only gets the lines it is missing.
#
#   scaffold.sh <project dir> --name "My App" [--owner "owner"] [--dry-run]
#
# Fills {{PROJECT}}, {{OWNER}} and {{DATE}}; prints every other {{PLACEHOLDER}} left to fill.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$HERE/templates"
DIR="${1:?usage: scaffold.sh <project dir> --name NAME [--owner OWNER] [--dry-run]}"
shift
NAME="" OWNER="owner" DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --owner) OWNER="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) echo "scaffold: unknown option $1" >&2; exit 2 ;;
  esac
done
[ -n "$NAME" ] || { echo "scaffold: --name is required" >&2; exit 2; }
DATE=$(date +%F)
[ $DRY = 1 ] || mkdir -p "$DIR"

created=() skipped=()
while IFS= read -r rel; do
  dest="$DIR/$rel"
  [ "$rel" = "gitignore" ] && dest="$DIR/.gitignore"
  if [ "$rel" = "gitignore" ] && [ -f "$dest" ]; then
    missing=$(grep -vxF -f "$dest" "$SRC/gitignore" | grep -v '^\s*$' || true)
    if [ -n "$missing" ]; then
      [ $DRY = 1 ] || printf '\n# added by project-blueprint\n%s\n' "$missing" >>"$dest"
      created+=(".gitignore (+$(echo "$missing" | wc -l | tr -d ' ') lines)")
    fi
    continue
  fi
  if [ -e "$dest" ]; then skipped+=("${dest#"$DIR"/}"); continue; fi
  created+=("${dest#"$DIR"/}")
  [ $DRY = 1 ] && continue
  mkdir -p "$(dirname "$dest")"
  NAME="$NAME" OWNER="$OWNER" DATE="$DATE" perl -pe 's/\{\{PROJECT\}\}/$ENV{NAME}/g; s/\{\{OWNER\}\}/$ENV{OWNER}/g; s/\{\{DATE\}\}/$ENV{DATE}/g' "$SRC/$rel" >"$dest"
done < <(cd "$SRC" && find . -type f | sed 's|^\./||' | sort)

echo "scaffold: $([ $DRY = 1 ] && echo "would create" || echo created) ${#created[@]}:"
for f in ${created[@]+"${created[@]}"}; do echo "  + $f"; done
if [ ${#skipped[@]} -gt 0 ]; then
  echo "scaffold: kept ${#skipped[@]} existing (merge by hand if useful):"
  for f in ${skipped[@]+"${skipped[@]}"}; do echo "  = $f"; done
fi
if [ $DRY = 0 ]; then
  left=$(cd "$DIR" && grep -rnoE '\{\{[A-Z_0-9]+\}\}' AGENTS.md docs research playground 2>/dev/null | sort -u || true)
  if [ -n "$left" ]; then
    echo "scaffold: placeholders to fill (from the conversation, the code and the owner):"
    echo "$left" | sed 's/^/  /'
  fi
fi

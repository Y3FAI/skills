#!/usr/bin/env bash
# Drive Gemini in the user's logged-in Zen through the BiDi driver (see the browser-use skill).
#   gemini.sh count          number of answers on the page now (call before send)
#   gemini.sh send <file>    type the file's text into the editor, then press Send
#   gemini.sh wait <n>       wait for answer number n+1 to finish, print it
#   gemini.sh read           print the last answer now
# Env: DRIVER (default localhost:9333), PART (tab URL substring, default gemini)
set -euo pipefail

# --- Selectors: all of them live here. Gemini's page changes; fix them here only. ---
# To re-find one: run in `eval` something like
#   [...document.querySelectorAll('button')].map(b => b.getAttribute('aria-label')).filter(a => /send/i.test(a))
# then inspect the editor (the element with contenteditable) and the answer blocks the same way.
SEL_EDITOR='rich-textarea .ql-editor, div[contenteditable="true"]'
SEL_SEND='button[aria-label*="Send"], button.send-button'
SEL_STOP='button[aria-label*="Stop"]'
SEL_ANSWER='message-content'
# -------------------------------------------------------------------------------------

DRIVER=${DRIVER:-localhost:9333}
PART=${PART:-gemini}
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# Run a JS expression in the Gemini tab; print the result as plain text.
run() { # $1 = js file
  python3 - "$DRIVER" "$PART" "$1" <<'PY'
import sys, json, urllib.request
drv, part, f = sys.argv[1:4]
req = json.dumps({"cmd": "eval", "part": part, "file": f}).encode()
out = urllib.request.urlopen("http://%s" % drv, req, timeout=120).read().decode()
try:
    v = json.loads(out)
except Exception:
    v = out
print(v if isinstance(v, str) else json.dumps(v))
PY
}

# Write a JS file with the selectors filled in. $1 = body (uses E, S, X, A as the selectors).
mkjs() {
  python3 - "$1" "$SEL_EDITOR" "$SEL_SEND" "$SEL_STOP" "$SEL_ANSWER" > "$tmp/q.js" <<'PY'
import sys, json
body, e, s, x, a = sys.argv[1:6]
print("(() => { const E=%s, S=%s, X=%s, A=%s;\n%s\n})()" % (json.dumps(e), json.dumps(s), json.dumps(x), json.dumps(a), body))
PY
}

state() { # prints: n busy len
  mkjs 'const r=[...document.querySelectorAll(A)]; return JSON.stringify({n:r.length,busy:!!document.querySelector(X),len:r.length?r[r.length-1].innerText.length:0});'
  run "$tmp/q.js" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d['n'],str(d['busy']).lower(),d['len'])"
}

cmd=${1:-}
case "$cmd" in
  count)
    read -r n _ _ < <(state); echo "$n" ;;
  send)
    f=${2:?usage: gemini.sh send <file>}
    [ -s "$f" ] || { echo "empty or missing file: $f" >&2; exit 1; }
    # 1. type the text (execCommand keeps the editor's own state in sync; the driver has no "type")
    python3 - "$f" "$SEL_EDITOR" "$SEL_SEND" "$SEL_STOP" "$SEL_ANSWER" > "$tmp/ins.js" <<'PY'
import sys, json
f, e = sys.argv[1], sys.argv[2]
text = open(f, encoding="utf-8").read()
print("""(() => {
  const el = document.querySelector(%s);
  if (!el) return 'no editor';
  el.focus();
  document.execCommand('selectAll', false);
  document.execCommand('insertText', false, %s);
  return 'inserted ' + el.innerText.length;
})()""" % (json.dumps(e), json.dumps(text)))
PY
    r=$(run "$tmp/ins.js"); echo "$r"
    [ "$r" = "no editor" ] && exit 1
    # 2. press Send. The button appears only after text is in the editor, so retry.
    mkjs 'const b=document.querySelector(S); if(!b) return "no button"; b.click(); return "sent";'
    for i in 1 2 3 4 5 6 7 8 9 10; do
      r=$(run "$tmp/q.js"); [ "$r" = "sent" ] && { echo sent; exit 0; }
      sleep 1
    done
    echo "no Send button after 10 tries: re-find SEL_SEND" >&2; exit 1 ;;
  wait)
    want=${2:?usage: gemini.sh wait <n>}; prev=-1
    for i in $(seq 1 100); do
      read -r n busy len < <(state)
      if [ "$n" -gt "$want" ] && [ "$busy" = false ] && [ "$len" -gt 20 ] && [ "$len" = "$prev" ]; then break; fi
      prev=$len; sleep 3
    done
    "$0" read ;;
  read)
    mkjs 'const r=[...document.querySelectorAll(A)]; return r.length?r[r.length-1].innerText:"";'
    run "$tmp/q.js" ;;
  *)
    sed -n '2,7p' "$0" >&2; exit 2 ;;
esac

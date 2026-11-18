#!/usr/bin/env bash
# Drive Gemini in the user's logged-in Zen through the BiDi driver (see the browser-use skill).
#   gemini.sh count          number of answers on the page now (call before send)
#   gemini.sh send <file>    type the file's text into the editor, press Send, check it posted
#   gemini.sh wait <n>       wait for answer number n+1 to finish, print it (exit 1 on timeout)
#   gemini.sh read           print the last answer now
# Env: DRIVER (default localhost:9333), PART (tab URL substring, default gemini),
#      WAIT_MAX (seconds before wait gives up, default 600)
set -euo pipefail

# --- Selectors: all of them live here. Gemini's page changes; fix them here only. ---
# To re-find one: run in `eval` something like
#   [...document.querySelectorAll('button')].map(b => b.getAttribute('aria-label')).filter(a => /send/i.test(a))
# then inspect the editor (the element with contenteditable) and the answer blocks the same way.
SEL_EDITOR='rich-textarea .ql-editor, div[contenteditable="true"]'
SEL_SEND='button[aria-label="Send message"], button.send-button, button[aria-label*="Send"]'  # tried in this order
SEL_STOP='button[aria-label*="Stop"]'
SEL_ANSWER='message-content'
SEL_QUERY='user-query'  # one per message sent; send checks that this count goes up
# -------------------------------------------------------------------------------------

DRIVER=${DRIVER:-localhost:9333}
PART=${PART:-gemini}
WAIT_MAX=${WAIT_MAX:-600}
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

# Write a JS file with the selectors filled in.
# $1 = body (uses E, S, X, A, Q as the selectors), $2 = output file.
mkjs() {
  python3 - "$1" "$SEL_EDITOR" "$SEL_SEND" "$SEL_STOP" "$SEL_ANSWER" "$SEL_QUERY" > "$2" <<'PY'
import sys, json
body, e, s, x, a, q = sys.argv[1:7]
print("(() => { const E=%s, S=%s, X=%s, A=%s, Q=%s;\n%s\n})()" % (json.dumps(e), json.dumps(s), json.dumps(x), json.dumps(a), json.dumps(q), body))
PY
}

state() { # prints: answers busy last-answer-length user-queries
  mkjs 'const r=[...document.querySelectorAll(A)]; return JSON.stringify({n:r.length,busy:!!document.querySelector(X),len:r.length?r[r.length-1].innerText.length:0,q:document.querySelectorAll(Q).length});' "$tmp/state.js"
  run "$tmp/state.js" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d['n'],str(d['busy']).lower(),d['len'],d['q'])"
}

last() { # prints the last answer
  mkjs 'const r=[...document.querySelectorAll(A)]; return r.length?r[r.length-1].innerText:"";' "$tmp/last.js"
  run "$tmp/last.js"
}

cmd=${1:-}
case "$cmd" in
  count)
    read -r n _ _ _ < <(state); echo "$n" ;;
  send)
    f=${2:?usage: gemini.sh send <file>}
    [ -s "$f" ] || { echo "empty or missing file: $f" >&2; exit 1; }
    read -r n0 _ _ q0 < <(state)   # messages in the chat before this send
    if [ "$n0" -gt 0 ] && [ "$q0" -eq 0 ]; then
      echo "answers on the page but no '$SEL_QUERY' elements: re-find SEL_QUERY before sending" >&2; exit 1
    fi
    # JS that types the text (execCommand keeps the editor's own state in sync; the driver has no "type")
    python3 - "$f" "$SEL_EDITOR" > "$tmp/ins.js" <<'PY'
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
    # JS that presses Send. SEL_SEND is tried in order; a disabled button counts as not there yet.
    mkjs 'const b=S.split(/\s*,\s*/).map(s=>document.querySelector(s)).find(Boolean); if(!b) return "no button"; if(b.disabled||b.getAttribute("aria-disabled")==="true") return "disabled"; b.click(); return "clicked";' "$tmp/click.js"
    for try in 1 2 3; do
      # 1. type the text. Again on each try: a failed send can leave the editor empty.
      r=$(run "$tmp/ins.js"); echo "$r"
      [ "$r" = "no editor" ] && { echo "no editor: re-find SEL_EDITOR" >&2; exit 1; }
      # 2. press Send. The button appears only after text is in the editor, so retry.
      r=""
      for i in $(seq 1 10); do
        r=$(run "$tmp/click.js"); [ "$r" = clicked ] && break
        sleep 1
      done
      [ "$r" = clicked ] || { echo "no Send button after 10 tries ($r): re-find SEL_SEND" >&2; exit 1; }
      # 3. the click counts only if a new user message shows up in the chat
      for i in $(seq 1 10); do
        sleep 1
        read -r _ _ _ q < <(state)
        [ "$q" -gt "$q0" ] && { echo sent; exit 0; }
      done
      echo "try $try: clicked Send, but no new message in the chat after 10 s" >&2
    done
    echo "send failed: still $q0 messages in the chat after 3 tries. Look at the tab before sending again." >&2
    exit 1 ;;
  wait)
    want=${2:?usage: gemini.sh wait <n>}
    [[ $want =~ ^[0-9]+$ ]] || { echo "wait needs the number from count, got: $want" >&2; exit 2; }
    [[ $WAIT_MAX =~ ^[0-9]+$ ]] || { echo "WAIT_MAX must be whole seconds, got: $WAIT_MAX" >&2; exit 2; }
    prev=-1; start=$SECONDS
    while :; do
      read -r n busy len _ < <(state)
      if [ "$n" -gt "$want" ] && [ "$busy" = false ] && [ "$len" -gt 20 ] && [ "$len" = "$prev" ]; then last; exit 0; fi
      if [ $((SECONDS - start)) -ge "$WAIT_MAX" ]; then
        echo "timeout after ${WAIT_MAX}s: answer $((want + 1)) is not finished (answers: $n, writing: $busy, length: $len)." >&2
        echo "Nothing printed. Raise WAIT_MAX, or run read once it is done." >&2
        exit 1
      fi
      prev=$len; sleep 3
    done ;;
  read)
    last ;;
  *)
    sed -n '2,8p' "$0" >&2; exit 2 ;;
esac

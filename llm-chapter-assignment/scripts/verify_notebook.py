"""Run an assignment notebook's code cells as plain Python (no Jupyter kernel needed).

usage, from ~/learn/llm-from-scratch/mycode/:
    PYTHONPATH=. ../.venv/bin/python <skill>/scripts/verify_notebook.py solved  /path/to/chN-solved.ipynb
    PYTHONPATH=. ../.venv/bin/python <skill>/scripts/verify_notebook.py student chN-assignment.ipynb

solved:  every check cell must end in "🎉 all passed"; no ❌ and no errors anywhere.
student: checks must print "⏳ not done yet"; other cells may only fail with "not written yet (task X)".
Prints each code cell's output so the numbers quoted in hidden answers can be copied from it.
"""
import contextlib
import io
import sys

import nbformat

mode, path = sys.argv[1], sys.argv[2]
nb = nbformat.read(path, as_version=4)
env = {"__name__": "__main__"}
problems = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    buf = io.StringIO()
    err = None
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(cell.source, f"cell[{i}]", "exec"), env)
        except Exception as e:  # keep going: report every cell
            err = f"{type(e).__name__}: {e}"
    out = buf.getvalue()
    head = cell.source.splitlines()[0][:70] if cell.source else ""
    print(f"\n[{i}] {head}\n{out}" + (f"  !! {err}\n" if err else ""))
    if mode == "solved":
        if err or "❌" in out or "⏳" in out:
            problems.append(f"cell {i}: {err or 'check did not fully pass'}")
    else:
        if err and "not written yet" not in err and "is not defined" not in err:
            problems.append(f"cell {i}: unexpected error {err}")
        if "✅" in out and cell.source.startswith("check."):
            problems.append(f"cell {i}: a check passes on the blank notebook (stub too easy?)")

print("\n" + ("=" * 60))
print("OK" if not problems else "PROBLEMS:\n  " + "\n  ".join(problems))
sys.exit(1 if problems else 0)

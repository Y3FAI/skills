"""Checks for ch2-assignment.ipynb.

No answers live here. Each check tests what your code *does* (its behaviour),
compared with the book's own code or with simple rules, so reading this file
does not give away the solutions.

Usage in the notebook:
    import ch2_checks as check
    check.make_pairs(make_pairs)
"""

import inspect
import random
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bookcode" / "pkg"))

from llms_from_scratch.ch02 import GPTDatasetV1  # noqa: E402  (the book's reference code)


# ---------------------------------------------------------------- helpers

class _NotDone(Exception):
    pass


def _call(fn, *args, **kwargs):
    try:
        out = fn(*args, **kwargs)
    except NotImplementedError:
        raise _NotDone
    if out is None or out is Ellipsis:
        raise _NotDone
    return out


def _run(title, cases):
    """cases: list of (description, zero-arg function returning (ok, detail))."""
    print(f"── {title}")
    passed = 0
    for desc, case in cases:
        try:
            ok, detail = case()
        except _NotDone:
            print("   ⏳ not done yet: write the function, then run this cell again")
            return False
        except Exception as e:  # show the real error, it is part of learning
            ok, detail = False, f"raised {type(e).__name__}: {e}"
        if ok:
            passed += 1
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc}\n      {detail}")
    mark = "🎉 all passed" if passed == len(cases) else f"{passed}/{len(cases)} passed"
    print(f"   {mark}")
    return True


def _eq(got, expected):
    return got == expected, f"expected {expected!r}\n      got      {got!r}"


def _source_has(fn, *words):
    try:
        src = inspect.getsource(fn)
    except (OSError, TypeError):
        return True
    return any(w in src for w in words)


class _ListTokenizer:
    """Pretends to be a tokenizer so the book's GPTDatasetV1 can run on plain ID lists."""

    def __init__(self, ids):
        self.ids = ids

    def encode(self, _txt, **_kwargs):
        return self.ids


def _book_pairs(ids, max_length, stride):
    ds = GPTDatasetV1("", _ListTokenizer(ids), max_length, stride)
    return [(x.tolist(), y.tolist()) for x, y in (ds[i] for i in range(len(ds)))]


# ---------------------------------------------------------------- level 3

def tokenize(fn, verdict_text):
    _run("tokenize", [
        ("splits words and punctuation, drops spaces",
         lambda: _eq(_call(fn, "Hello, world. Is this-- a test?"),
                     ['Hello', ',', 'world', '.', 'Is', 'this', '--', 'a', 'test', '?'])),
        ("keeps capital letters",
         lambda: _eq(_call(fn, "I HAD always"), ['I', 'HAD', 'always'])),
        ("no empty or whitespace tokens on The Verdict",
         lambda: (all(t.strip() == t and t for t in _call(fn, verdict_text)),
                  "found a token that is empty or has spaces around it")),
        ("The Verdict gives 4,690 tokens (same as the book)",
         lambda: _eq(len(_call(fn, verdict_text)), 4690)),
    ])


def build_vocab(fn, tokens):
    def vocab():
        return _call(fn, tokens)

    _run("build_vocab", [
        ("returns a dict that maps token (str) → ID (int)",
         lambda: (all(isinstance(k, str) and isinstance(v, int) for k, v in vocab().items()),
                  "keys should be strings and values integers: is it reversed?")),
        ("size is unique tokens + 2 special tokens",
         lambda: _eq(len(vocab()), len(set(tokens)) + 2)),
        ("IDs are 0, 1, 2, ... with no gaps",
         lambda: _eq(sorted(vocab().values()), list(range(len(set(tokens)) + 2)))),
        ("normal tokens are in sorted order",
         lambda: _eq([k for k, _ in sorted(vocab().items(), key=lambda kv: kv[1])][:-2],
                     sorted(set(tokens)))),
        ("<|endoftext|> and <|unk|> get the last two IDs",
         lambda: _eq({vocab()["<|endoftext|>"], vocab()["<|unk|>"]},
                     {len(set(tokens)), len(set(tokens)) + 1})),
    ])


def tokenizer(cls, vocab):
    def make():
        try:
            return cls(vocab)
        except NotImplementedError:
            raise _NotDone

    def roundtrip(text):
        t = make()
        return _eq(_call(t.decode, _call(t.encode, text)), text)

    _run("Tokenizer", [
        ("encode gives a list of ints",
         lambda: (all(isinstance(i, int) for i in _call(make().encode, "you know, I said.")),
                  "encode should return token IDs (ints)")),
        ("decode(encode(text)) gives the text back",
         lambda: roundtrip("you know, I said.")),
        ("no space is left before punctuation",
         lambda: roundtrip("It was the last he painted, you know.")),
        ("unknown words become <|unk|>",
         lambda: _eq(_call(make().encode, "Hello")[0], vocab["<|unk|>"])),
        ("<|endoftext|> stays one token",
         lambda: _eq(_call(make().encode, "you <|endoftext|> I"),
                     [vocab["you"], vocab["<|endoftext|>"], vocab["I"]])),
    ])


def make_pairs(fn):
    cases = []
    for n, L, s in [(20, 4, 1), (20, 4, 4), (23, 4, 3), (30, 8, 2), (10, 2, 2), (12, 5, 7)]:
        ids = list(range(100, 100 + n))

        def case(ids=ids, L=L, s=s):
            got = [(list(x), list(y)) for x, y in _call(fn, ids, L, s)]
            return _eq(got, _book_pairs(ids, L, s))

        cases.append((f"same pairs as the book's GPTDatasetV1 (n={n}, max_length={L}, stride={s})", case))
    _run("make_pairs", cases)


def count_pairs(fn):
    def all_match():
        for n in range(5, 60):
            for L in range(1, 9):
                for s in range(1, 9):
                    if n <= L:
                        continue
                    want = len(_book_pairs(list(range(n)), L, s))
                    got = _call(fn, n, L, s)
                    if got != want:
                        return False, f"n={n}, max_length={L}, stride={s}: expected {want}, got {got}"
        return True, ""

    started = _run("count_pairs", [
        ("matches the book's dataset length for 3,000+ settings", all_match),
        ("big case: 5,145 tokens, max_length=256, stride=128",
         lambda: _eq(_call(fn, 5145, 256, 128), len(_book_pairs(list(range(5145)), 256, 128)))),
    ])
    if started and _source_has(fn, "for ", "while ", "range(", "make_pairs", "len("):
        print("   💡 it works, but the task asks for a formula with no loop, range() or len()")


def embed_with_onehot(fn):
    torch.manual_seed(123)
    W = torch.randn(6, 3)
    ids = torch.tensor([2, 3, 5, 1])
    started = _run("embed_with_onehot", [
        ("output shape is [4, 3]",
         lambda: _eq(tuple(_call(fn, ids, W).shape), (4, 3))),
        ("same numbers as an nn.Embedding lookup",
         lambda: (torch.allclose(_call(fn, ids, W), torch.nn.functional.embedding(ids, W)),
                  "values differ from the embedding lookup")),
    ])
    if started and not _source_has(fn, "one_hot", "eye", "@", "matmul", "mm("):
        print("   💡 the point is one-hot × matrix, not W[ids]: try F.one_hot and @")


def make_input_embeddings(fn):
    torch.manual_seed(0)
    tok = torch.nn.Embedding(50, 16)
    pos = torch.nn.Embedding(4, 16)

    def full():
        ids = torch.randint(0, 50, (3, 4))
        out = _call(fn, ids, tok, pos)
        want = tok(ids) + pos(torch.arange(4))
        return (tuple(out.shape) == (3, 4, 16) and torch.allclose(out, want),
                f"expected shape (3, 4, 16) equal to tok(ids) + pos(arange(4)); got shape {tuple(out.shape)}")

    def shorter():
        ids = torch.randint(0, 50, (2, 3))
        out = _call(fn, ids, tok, pos)
        want = tok(ids) + pos(torch.arange(3))
        return (tuple(out.shape) == (2, 3, 16) and torch.allclose(out, want),
                "with only 3 tokens per row, use positions 0, 1, 2 (take the length from the input)")

    _run("make_input_embeddings", [
        ("batch of 3 rows × 4 tokens → [3, 4, 16]", full),
        ("works when rows are shorter than the context length", shorter),
    ])


# ---------------------------------------------------------------- level 5 (Arabic)

def tokenize_ar(fn):
    _run("tokenize_ar", [
        ("splits Arabic question mark and comma",
         lambda: _eq(_call(fn, "هل تحب الشاي؟ نعم، كثيرا."),
                     ['هل', 'تحب', 'الشاي', '؟', 'نعم', '،', 'كثيرا', '.'])),
        ("splits the Arabic semicolon",
         lambda: _eq(_call(fn, "قال الأسد؛ ثم سكت"), ['قال', 'الأسد', '؛', 'ثم', 'سكت'])),
        ("splits «» quote marks",
         lambda: _eq(_call(fn, "«كليلة ودمنة»"), ['«', 'كليلة', 'ودمنة', '»'])),
        ("still works on English",
         lambda: _eq(_call(fn, "Hello, world."), ['Hello', ',', 'world', '.'])),
    ])


def normalize_ar(fn):
    pairs = [
        ("removes diacritics", "وَبِالْكِتَابِ", "وبالكتاب"),
        ("removes tanween and shadda", "رجلٌ شيخٌ مرّ", "رجل شيخ مر"),
        ("unifies أ إ آ → ا", "إنه أخذ آمن", "انه اخذ امن"),
        ("ى → ي", "مستشفى", "مستشفي"),
        ("ة → ه", "مكتبة كبيرة", "مكتبه كبيره"),
        ("removes tatweel ـ", "كبيـــر", "كبير"),
        ("leaves English alone", "Hello, world.", "Hello, world."),
    ]
    _run("normalize_ar", [(d, (lambda a=a, b=b: _eq(_call(fn, a), b))) for d, a, b in pairs])


def fertility(fn, enc):
    _run("fertility", [
        ("'hello world' with GPT-2 → 2 tokens / 2 words = 1.0",
         lambda: _eq(_call(fn, "hello world", enc), 1.0)),
        ("Arabic sentence gives more than 1 token per word",
         lambda: (_call(fn, "وبالكتاب سيكتبون دروسهم", enc) > 1, "should be above 1.0")),
    ])


def train_bpe(train_fn, encode_fn, text, tokenize_fn):
    words = tokenize_fn(text)

    def merges(k):
        return _call(train_fn, text, k)

    def first_is_most_frequent():
        counts = {}
        for w in words:
            for a, b in zip(w, w[1:]):
                counts[(a, b)] = counts.get((a, b), 0) + 1
        best = max(counts.values())
        m = merges(5)
        ok = tuple(m[0]) in {p for p, c in counts.items() if c == best}
        return ok, f"first merge {m[0]} is not the most frequent pair of characters"

    def roundtrip():
        m = merges(200)
        rng = random.Random(0)
        for w in rng.sample(words, 300):
            pieces = _call(encode_fn, w, m)
            if "".join(pieces) != w:
                return False, f"{w!r} → {pieces}: the pieces do not join back into the word"
        return True, ""

    def fewer_tokens():
        sample = words[:2000]
        m = merges(200)
        t0 = sum(len(_call(encode_fn, w, [])) for w in sample)
        t1 = sum(len(_call(encode_fn, w, m)) for w in sample)
        return t1 < t0, f"200 merges should give fewer tokens than 0 merges ({t1} vs {t0})"

    _run("train_bpe + bpe_encode_word", [
        ("returns a list of (left, right) pairs",
         lambda: (all(len(p) == 2 for p in merges(10)) and len(merges(10)) == 10,
                  "expected 10 pairs for num_merges=10")),
        ("first merge is the most frequent pair", first_is_most_frequent),
        ("encoded pieces join back into the original word", roundtrip),
        ("more merges → fewer tokens", fewer_tokens),
    ])


# ---------------------------------------------------------------- level 6

def rope(fn):
    torch.manual_seed(0)
    q = torch.randn(1, 8)
    k = torch.randn(1, 8)

    def at(x, p):
        return _call(fn, x, torch.tensor([p]))

    def score(m, n):
        return (at(q, m) @ at(k, n).T).item()

    _run("rope", [
        ("position 0 leaves the vector unchanged",
         lambda: (torch.allclose(at(q, 0), q, atol=1e-6), "rope(x, 0) should equal x")),
        ("rotation keeps the vector's length",
         lambda: (abs(at(q, 7).norm().item() - q.norm().item()) < 1e-4, "the norm changed")),
        ("position 5 actually changes the vector",
         lambda: (not torch.allclose(at(q, 5), q), "rope(x, 5) should differ from x")),
        ("score depends only on distance: (3,1) == (10,8) == (52,50)",
         lambda: (abs(score(3, 1) - score(10, 8)) < 1e-4 and abs(score(3, 1) - score(52, 50)) < 1e-4,
                  f"got {score(3, 1):.5f}, {score(10, 8):.5f}, {score(52, 50):.5f}")),
        ("works on many positions at once ([T, D] in → [T, D] out)",
         lambda: _eq(tuple(_call(fn, torch.randn(5, 8), torch.arange(5)).shape), (5, 8))),
    ])

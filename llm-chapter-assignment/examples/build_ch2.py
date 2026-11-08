"""Builds mycode/ch2-assignment.ipynb (student version) and a solved copy for testing.

usage: python build_ch2.py <student_out.ipynb> <solved_out.ipynb>
"""
import sys
from textwrap import dedent

import nbformat as nbf

STUDENT, SOLVED = sys.argv[1], sys.argv[2]
student, solved = [], []


def _clean(s):
    return dedent(s).strip("\n")


def md(s):
    c = _clean(s)
    student.append(nbf.v4.new_markdown_cell(c))
    solved.append(nbf.v4.new_markdown_cell(c))


def code(s):
    c = _clean(s)
    student.append(nbf.v4.new_code_cell(c))
    solved.append(nbf.v4.new_code_cell(c))


def answer(s):
    md("<details>\n<summary><b>🔒 Show answer</b></summary>\n\n" + _clean(s) + "\n\n</details>")


def task(stub, solution, notes=""):
    """Code cell with a stub for the student; the solved copy gets the solution."""
    student.append(nbf.v4.new_code_cell(_clean(stub)))
    solved.append(nbf.v4.new_code_cell(_clean(solution)))
    return "```python\n" + _clean(solution) + "\n```" + ("\n\n" + _clean(notes) if notes else "")


YOURS = "\n\n✍️ **Your answer:**\n\n- "
GUESS = "\n\n🔮 **Your prediction:**\n\n- "

# ======================================================================= intro
md("""
# Chapter 2 assignment: Working with text data

**How it works**
- Six levels, easy → hard. Each level builds on the one before.
- ✍️ write with the book closed · 🔮 predict *before* you run · 💻 code, then run the check below it.
- Answers are hidden under **🔒 Show answer**. Open one only after you have written yours.
- Level 3 is from memory. If you look at the book, add a `# PEEK` comment. Your peeks show your weak spots.
- About 3–4 hours. Spread it over a few days and stop at the end of any level.
- When you finish, tell Claude **"grade ch2"**. It reads your written answers and gives feedback.

| Level | What | Type | Time |
|---|---|---|---|
| 1 | The big picture | ✍️ recall | 15 min |
| 2 | Predict, then run | 🔮 | 20 min |
| 3 | Build the pipeline yourself | 💻 + checks | 50 min |
| 4 | Think deeper | ✍️ | 20 min |
| 5 | Arabic lab: from simple to today's best | 💻 ✍️ | 60–90 min |
| 6 | Stretch: modern positions (RoPE) | 💻 ✍️ | 30 min |
""")

code("""
# ▶ Run me first
import re, sys, collections
from pathlib import Path

import torch
import tiktoken

assert Path("ch2_checks.py").exists(), "Open this notebook from the mycode/ folder (the working directory must be mycode/)."
sys.path.insert(0, str(Path("../bookcode/pkg").resolve()))
from llms_from_scratch.ch02 import GPTDatasetV1, create_dataloader_v1   # the book's own code

import ch2_checks as check

verdict = Path("../bookcode/ch02/01_main-chapter-code/the-verdict.txt").read_text(encoding="utf-8")
lion = Path("data/kalila-lion-and-ox.txt").read_text(encoding="utf-8")    # كليلة ودمنة: باب الأسد والثور
dove = Path("data/kalila-ringed-dove.txt").read_text(encoding="utf-8")    # كليلة ودمنة: باب الحمامة المطوقة
gpt2 = tiktoken.get_encoding("gpt2")

print(f"The Verdict: {len(verdict):,} characters")
print(f"Lion and Ox: {len(lion):,} characters")
print(f"Ringed Dove: {len(dove):,} characters")
""")

# ======================================================================= level 1
md("""
---
## Level 1 · The big picture ★
Book closed. Short answers: a line or a few bullets each.
""")

md("**1.1** Put these steps in order, from raw text to what the LLM receives: token embeddings · input text · input embeddings · token IDs · tokens · positional embeddings are added." + YOURS)
answer("""
1. Input text
2. Tokens
3. Token IDs
4. Token embeddings
5. Positional embeddings are added
6. Input embeddings → go into the LLM
""")

md("**1.2** Define in one line each: *token*, *token ID*, *vocabulary*, *embedding*." + YOURS)
answer("""
- **Token**: a piece of text the model treats as one unit (a word, part of a word, or a punctuation mark).
- **Token ID**: the integer that stands for a token.
- **Vocabulary**: the mapping from every known token to its unique ID.
- **Embedding**: a vector of continuous numbers that represents a token; learned during training.
""")

md("**1.3** Why can't we feed token IDs straight into the network as numbers? Why do we need embedding vectors?" + YOURS)
answer("""
- IDs are labels, not amounts: ID 50 is not "more" than ID 49, and not closer in meaning.
- Neural networks do math and learn by backpropagation, which needs continuous values that can be nudged a little at a time.
- An embedding gives each token many learnable numbers, so similar tokens can end up close together.
""")

md("**1.4** `SimpleTokenizerV2` added two special tokens. Name them and say what each one is for." + YOURS)
answer("""
- `<|unk|>`: stands in for any word that is not in the vocabulary.
- `<|endoftext|>`: placed between unrelated texts, so the model knows they are separate.
""")

md("**1.5** Why doesn't GPT-2's tokenizer need an `<|unk|>` token?" + YOURS)
answer("""
- Byte pair encoding (BPE) breaks any unknown word into smaller pieces it knows: subwords, single characters, or single bytes in the worst case.
- Every possible text can be written with known pieces, so nothing is ever "unknown".
""")

md("**1.6** Differentiate *absolute* and *relative* positional embeddings. Which kind does GPT use?" + YOURS)
answer("""
- **Absolute**: one vector per position (0, 1, 2, …), added to the token embedding. It says *where exactly* the token is.
- **Relative**: encodes the *distance* between tokens ("how far apart"). It copes better with lengths not seen in training.
- **GPT**: absolute, and learned during training (not fixed like in the original transformer).
""")

# ======================================================================= level 2
md("""
---
## Level 2 · Predict, then run ★→★★
For each one: write your prediction **first**, then run the cell. If you were wrong, add one line saying why.
""")

md("**2.1** ★ What list does this print? (Look at the brackets in the pattern.)" + GUESS)
code("""
import re
print(re.split(r'(\\s)', "I HAD always"))
""")
answer("""
`['I', ' ', 'HAD', ' ', 'always']`

- The brackets `( )` in the pattern keep the separators, so the spaces stay in the list as their own items.
- Without the brackets, `re.split` throws the separators away.
""")

md("**2.2** ★ The book's final pattern, on `\"Don't stop--now!\"`. Which tokens come out?" + GUESS)
code("""
pattern = r'([,.:;?_!"()\\']|--|\\s)'
print([t.strip() for t in re.split(pattern, "Don't stop--now!") if t.strip()])
""")
answer("""
`['Don', "'", 't', 'stop', '--', 'now', '!']`

- `'` is in the split list, so "Don't" becomes 3 tokens.
- That is also why the book's `decode` printed `It' s`.
- `--` is matched as one token.
""")

md("**2.3** ★ The Verdict has 1,130 unique tokens, sorted, with IDs starting at 0. You append `<|endoftext|>` and then `<|unk|>`. What is the new vocabulary size, and what are their two IDs?" + GUESS)
code("""
words = sorted(set(t.strip() for t in re.split(pattern, verdict) if t.strip()))
vocab = {tok: i for i, tok in enumerate(words + ["<|endoftext|>", "<|unk|>"])}
print(len(vocab), vocab["<|endoftext|>"], vocab["<|unk|>"])
""")
answer("""
`1132 1130 1131`

- IDs start at 0, so the 1,130 words use IDs 0–1129.
- The next free IDs are 1130 and 1131.
""")

md("**2.4** ★ GPT-2's BPE tokenizer: what is its vocabulary size, and what is the ID of `<|endoftext|>`?" + GUESS)
code("""
print(gpt2.n_vocab)
print(gpt2.encode("<|endoftext|>", allowed_special={"<|endoftext|>"}))
""")
answer("""
`50257` and `[50256]`. The special token gets the last (largest) ID.
""")

md("**2.5** ★★ With these IDs and `context_size = 4`, what are `x` and `y`?" + GUESS)
code("""
ids = [290, 4920, 2241, 287, 257]
context_size = 4
x = ids[:context_size]
y = ids[1:context_size + 1]
print("x:", x)
print("y:", y)
""")
answer("""
`x: [290, 4920, 2241, 287]` · `y: [4920, 2241, 287, 257]`

- `y` is `x` shifted one step: each position's target is the next token.
- So one row holds 4 training examples: `[290] → 4920`, `[290, 4920] → 2241`, and so on.
""")

md("**2.6** ★★ The Verdict is 5,145 GPT-2 tokens. With `max_length=4, stride=4`, how many rows does `GPTDatasetV1` make? With `batch_size=8, drop_last=True`, how many batches?" + GUESS)
code("""
ds = GPTDatasetV1(verdict, gpt2, max_length=4, stride=4)
dl = create_dataloader_v1(verdict, batch_size=8, max_length=4, stride=4, shuffle=False)
print("rows:", len(ds))
print("batches:", len(dl))
""")
answer("""
**1,286 rows · 160 batches**

- The loop is `range(0, 5145 - 4, 4)`, so the window starts at 0, 4, 8, …, 5140.
- It stops at `5145 - 4`, not `- 3`, because every window needs one extra token after it for the target.
- 5140 / 4 + 1 = 1,286 starts.
- 1,286 / 8 = 160.75, and `drop_last` throws away the last 6 rows, leaving 160 batches.
""")

md("**2.7** ★★ Same text, but `stride=1`. How many rows now?" + GUESS)
code("""
print(len(GPTDatasetV1(verdict, gpt2, max_length=4, stride=1)))
""")
answer("""
**5,141**

- That is almost one row per token.
- Windows overlap by 3 tokens, so each token appears in up to 4 rows.
- You get 4× more rows per pass, but it is the same text repeated.
""")

md("**2.8** ★★ For `nn.Embedding(6, 3)`: what is the shape of its weight matrix? What is the output shape for `torch.tensor([[2, 3], [5, 1]])`? And how many weights does `nn.Embedding(50257, 256)` have?" + GUESS)
code("""
emb = torch.nn.Embedding(6, 3)
print(emb.weight.shape)
print(emb(torch.tensor([[2, 3], [5, 1]])).shape)
print(torch.nn.Embedding(50257, 256).weight.numel())
""")
answer("""
- `[6, 3]`: one row per token, one column per embedding dimension.
- `[2, 2, 3]`: the input's shape is kept, and each ID becomes a 3-number row.
- 50,257 × 256 = **12,865,792** weights, just for this lookup table.
""")

md("**2.9** ★★ `token_embeddings` is `[8, 4, 256]` and `pos_embeddings` is `[4, 256]`. What is the shape of their sum? Which position vector is added to the first token of row 5?" + GUESS)
code("""
tok_emb = torch.randn(8, 4, 256)
pos_emb = torch.randn(4, 256)
out = tok_emb + pos_emb
print(out.shape)
print(torch.allclose(out[5, 0], tok_emb[5, 0] + pos_emb[0]))
""")
answer("""
`torch.Size([8, 4, 256])` and `True`

- Broadcasting: PyTorch adds the same `[4, 256]` table to each of the 8 rows.
- Row 5, token 0 gets `pos_emb[0]`. The position vector depends only on the position, not on which row it is in.
""")

# ======================================================================= level 3
md("""
---
## Level 3 · Build the pipeline yourself ★★
This is a rebuild of the chapter **from memory**. If you look at the book, write `# PEEK` in that cell.
Each 💻 cell has a check under it: ✅ passed · ❌ wrong (with a hint) · ⏳ not written yet.
""")

md("""
**3.1** ✍️ **Spot the bug.** Each snippet runs without an error message (at least at first), but each one is wrong. What is wrong, and how do you fix it?

**A**
```python
vocab = {token: integer for token, integer in enumerate(all_words)}
```
**B**
```python
for i in range(0, len(token_ids) - max_length, stride):
    input_chunk = token_ids[i:i + max_length]
    target_chunk = token_ids[i:i + max_length]
```
**C**
```python
token_embeddings = token_embedding_layer(inputs)    # inputs: [8, 4] token IDs
pos_embeddings = pos_embedding_layer(inputs)
input_embeddings = token_embeddings + pos_embeddings
```
""" + YOURS)
answer("""
- **A**: `enumerate` gives `(index, item)`, so the names are swapped. The dict maps `0 → '!'` (int → str): it is the *inverse* vocabulary. Printing it looks fine, but `encode` crashes with `KeyError`. This one is in your own `ch2.ipynb`, cell 11.
  - Fix: `{token: i for i, token in enumerate(all_words)}`
- **B**: the target equals the input, so the model learns to *copy* the current token instead of predicting the next one.
  - Fix: `target_chunk = token_ids[i + 1:i + max_length + 1]`
- **C**: the position layer gets *token IDs* instead of positions. It looks up "position 2885", which raises `IndexError` (there are only 4 positions), or gives nonsense when the IDs happen to be small.
  - Fix: `pos_embedding_layer(torch.arange(inputs.shape[1]))`
""")

md("""
**3.2** 💻 `tokenize(text)`: split text into words and punctuation (`, . : ; ? _ ! " ( ) '` and `--`), drop all whitespace, and keep capital letters.
""")
sol = task("""
def tokenize(text):
    # return a list of tokens: words and punctuation, no whitespace
    raise NotImplementedError("tokenize() is not written yet (task 3.2)")
""", r"""
def tokenize(text):
    pieces = re.split(r'([,.:;?_!"()\']|--|\s)', text)
    return [p.strip() for p in pieces if p.strip()]
""", """
- The brackets in the pattern keep the punctuation as tokens.
- `strip()` plus the `if` removes the spaces and the empty strings.
""")
code("check.tokenize(tokenize, verdict)")
answer(sol)

md("""
**3.3** 💻 `build_vocab(tokens)`: sort the unique tokens, append `"<|endoftext|>"` and `"<|unk|>"`, and return a dict **token → ID**.
""")
sol = task("""
def build_vocab(tokens):
    raise NotImplementedError("build_vocab() is not written yet (task 3.3)")
""", """
def build_vocab(tokens):
    all_tokens = sorted(set(tokens)) + ["<|endoftext|>", "<|unk|>"]
    return {token: i for i, token in enumerate(all_tokens)}
""")
code("check.build_vocab(build_vocab, tokenize(verdict))")
answer(sol)

md("""
**3.4** 💻 `Tokenizer`: a class with `encode(text) → list of IDs` and `decode(ids) → text`.
- Unknown words become `<|unk|>`.
- `decode` removes the space before punctuation.
- Use your `tokenize` from 3.2.
""")
sol = task("""
class Tokenizer:
    def __init__(self, vocab):
        raise NotImplementedError("Tokenizer.__init__() is not written yet (task 3.4)")

    def encode(self, text):
        raise NotImplementedError("Tokenizer.encode() is not written yet (task 3.4)")

    def decode(self, ids):
        raise NotImplementedError("Tokenizer.decode() is not written yet (task 3.4)")
""", r"""
class Tokenizer:
    def __init__(self, vocab):
        self.str_to_int = vocab
        self.int_to_str = {i: s for s, i in vocab.items()}

    def encode(self, text):
        tokens = [t if t in self.str_to_int else "<|unk|>" for t in tokenize(text)]
        return [self.str_to_int[t] for t in tokens]

    def decode(self, ids):
        text = " ".join(self.int_to_str[i] for i in ids)
        return re.sub(r'\s+([,.:;?!"()\'])', r'\1', text)
""")
code("""
vocab = build_vocab(tokenize(verdict))
check.tokenizer(Tokenizer, vocab)
""")
answer(sol)

md("""
**3.5** 💻 `make_pairs(ids, max_length, stride)`: plain Python, no torch. Return a list of `(input, target)` pairs of lists, built the same way as `GPTDatasetV1`.
""")
sol = task("""
def make_pairs(ids, max_length, stride):
    raise NotImplementedError("make_pairs() is not written yet (task 3.5)")
""", """
def make_pairs(ids, max_length, stride):
    pairs = []
    for i in range(0, len(ids) - max_length, stride):
        pairs.append((ids[i:i + max_length], ids[i + 1:i + max_length + 1]))
    return pairs
""")
code("check.make_pairs(make_pairs)")
answer(sol)

md("""
**3.6** 💻 `count_pairs(n, max_length, stride)`: how many pairs `make_pairs` would return for `n` tokens. **Use a formula: no loop, no `range`, no `len`.**
Hint: the window starts at 0, stride, 2·stride, … for as long as the start is below `n - max_length`.
""")
sol = task("""
def count_pairs(n, max_length, stride):
    raise NotImplementedError("count_pairs() is not written yet (task 3.6)")
""", """
def count_pairs(n, max_length, stride):
    return (n - max_length + stride - 1) // stride      # = ceil((n - max_length) / stride)
""", """
- Starts are 0, s, 2s, … while the start is below n − L, which gives ⌈(n − L) / s⌉ starts.
- `(a + s - 1) // s` is the integer way to round a division up.
- Check: n = 5145, L = 4, s = 4 → (5141 + 3) // 4 = **1286**, the same as 2.6.
""")
code("check.count_pairs(count_pairs)")
answer(sol)

md("""
**3.7** 💻 `embed_with_onehot(ids, W)`: get the same result as an embedding lookup, but using **one-hot vectors × matrix**.
Hint: `torch.nn.functional.one_hot` turns ID 3 into `[0, 0, 0, 1, 0, 0]`. What does that row times `W` pick out?
""")
sol = task("""
def embed_with_onehot(ids, W):
    # ids: [N] token IDs, W: [vocab_size, dim] → return [N, dim]
    raise NotImplementedError("embed_with_onehot() is not written yet (task 3.7)")
""", """
def embed_with_onehot(ids, W):
    onehot = torch.nn.functional.one_hot(ids, num_classes=W.shape[0]).float()   # [4, 6]
    return onehot @ W                                                            # [4, 6] @ [6, 3] → [4, 3]
""", """
- A one-hot row times W picks out exactly one row of W. That is the lookup.
- This shows an embedding layer is an ordinary linear layer (so backprop trains it). The lookup is just faster because it skips multiplying by all the zeros.
""")
code("check.embed_with_onehot(embed_with_onehot)")
answer(sol)

md("""
**3.8** 💻 `make_input_embeddings(ids, tok_layer, pos_layer)`: `ids` has shape `[batch, T]`. Return token embeddings + positional embeddings, shape `[batch, T, dim]`. Take `T` from the input.
""")
sol = task("""
def make_input_embeddings(ids, tok_layer, pos_layer):
    raise NotImplementedError("make_input_embeddings() is not written yet (task 3.8)")
""", """
def make_input_embeddings(ids, tok_layer, pos_layer):
    T = ids.shape[1]
    return tok_layer(ids) + pos_layer(torch.arange(T))
""")
code("check.make_input_embeddings(make_input_embeddings)")
answer(sol)

md("**3.9** 🔮 Put it all together on real data. Predict the final shape first." + GUESS)
code("""
tok_layer = torch.nn.Embedding(gpt2.n_vocab, 256)
pos_layer = torch.nn.Embedding(4, 256)
loader = create_dataloader_v1(verdict, batch_size=8, max_length=4, stride=4, shuffle=False)
inputs, targets = next(iter(loader))
print(inputs.shape, "→", make_input_embeddings(inputs, tok_layer, pos_layer).shape)
""")
answer("""
`torch.Size([8, 4]) → torch.Size([8, 4, 256])`

🎉 You have rebuilt the whole Chapter 2 pipeline. In 3–4 days, redo Level 3 in an empty notebook and aim for fewer `# PEEK`s.
""")

# ======================================================================= level 4
md("""
---
## Level 4 · Think deeper ★★★
The book does not answer these directly. Reason them out from what you know.
""")

md("**4.1** What happens to the data if `stride` is bigger than `max_length`? Is that ever useful?" + YOURS)
answer("""
- The windows leave gaps: tokens between them never appear as input or target, so that text is wasted.
- You get fewer rows, and training is cheaper.
- It is rarely useful. One case is when you have far more text than you can afford to train on, and skipping some is acceptable.
""")

md("**4.2** The model was built with `context_length = 4`. What happens in the code if you feed it 5 tokens? Why is this a hard limit for *learned absolute* positions? What would you need instead?" + YOURS)
code("""
pos_layer_4 = torch.nn.Embedding(4, 8)
try:
    pos_layer_4(torch.arange(5))
except Exception as e:
    print(type(e).__name__, "→", e)
""")
answer("""
- `IndexError: index out of range in self`: the table has no row for position 4.
- Learned positions exist only for positions 0 … context_length − 1, so that is a hard maximum.
- In practice: cut the input down to the last 4 tokens (the book says to truncate).
- Instead: compute positions with a formula, so every position has a value. RoPE does this (Level 6).
""")

md("**4.3** Why does the book switch to `stride = max_length` for the batch example? What is the risk with `stride = 1`?" + YOURS)
answer("""
- With `stride = max_length` there is no overlap, so every token is used once as input, and none are skipped.
- With `stride = 1` you get nearly the same window again and again, shifted by one. That means more compute per pass over the data, and the model sees the same passage many times. The book notes that more overlap can lead to more **overfitting**.
""")

md("**4.4** The input row holds tokens 0–3 and the targets are tokens 1–4. When the model predicts the target for position 1, token 2 is already in the input row. What stops it from cheating?" + YOURS)
answer("""
- Nothing yet in Chapter 2. Chapter 3 adds a **causal attention mask**: each position may only look at itself and earlier positions.
- The book's Figure 2.12 says this: "During training, we mask out all words that are past the target."
""")

# ======================================================================= level 5
md("""
---
## Level 5 · Arabic lab: from simple to today's best ★→★★★
So far everything ran on an English short story. Now the same pipeline meets **Kalila wa Dimna** (كليلة ودمنة, Ibn al-Muqaffaʿ, 8th century).

- Training text: **باب الأسد والثور** (The Lion and the Ox), ~46k characters, more than 2× The Verdict.
- New text for testing: **باب الحمامة المطوقة** (The Ringed Dove).

You will climb the same ladder the field did:

1. your own word tokenizer
2. GPT-2
3. GPT-4o
4. your own Arabic BPE
5. today's research
""")

md("**5.1** ★ 🔮 What does your `tokenize` from 3.2 do with this Arabic sentence?" + GUESS)
code("""
print(tokenize("هل تحب الشاي؟ نعم، كثيرا."))
""")
answer("""
`['هل', 'تحب', 'الشاي؟', 'نعم،', 'كثيرا', '.']`

- `؟` and `،` stay stuck to the words.
- Arabic punctuation marks are different characters: `؟` (U+061F) is not `?` (U+003F), and `،` (U+060C) is not `,`.
- Only the final `.` splits, because Arabic text often uses the Latin full stop.
""")

md("**5.2** 💻 `tokenize_ar(text)`: like `tokenize`, but it also splits `،` `؛` `؟` `«` `»`.")
sol = task("""
def tokenize_ar(text):
    raise NotImplementedError("tokenize_ar() is not written yet (task 5.2)")
""", r"""
def tokenize_ar(text):
    pieces = re.split(r'([,.:;?_!"()\'،؛؟«»]|--|\s)', text)
    return [p.strip() for p in pieces if p.strip()]
""")
code("check.tokenize_ar(tokenize_ar)")
answer(sol)

md("""
**5.3** ★★ **A word-level vocabulary meets Arabic.**
For each language, build a vocabulary from the first 80% of the text and count the unknown tokens in the last 20%.

🔮 Which language will have more unknown words? Guess both percentages.

-
""")
code("""
def unk_rate(train_text, test_text, tokenize_fn):
    vocab = set(tokenize_fn(train_text))
    test_tokens = tokenize_fn(test_text)
    unknown = sum(t not in vocab for t in test_tokens)
    return len(vocab), unknown / len(test_tokens)

def split_80_20(text):
    k = int(len(text) * 0.8)
    return text[:k], text[k:]

for name, text, tok in [("English, The Verdict", verdict, tokenize), ("Arabic, Lion and Ox", lion, tokenize_ar)]:
    train, test = split_80_20(text)
    size, rate = unk_rate(train, test, tok)
    print(f"{name:22} vocab {size:,}   unknown in test: {rate:.1%}")

size, rate = unk_rate(lion, dove, tokenize_ar)
print(f"{'Arabic, Lion → Dove':22} vocab {size:,}   unknown: {rate:.1%}")
""")
md("Now look at every form of the word *lion* (أسد) in the training chapter:")
code("""
counts = collections.Counter(tokenize_ar(lion))
print({w: n for w, n in counts.most_common() if "أسد" in w})
""")
md("✍️ Why does Arabic have about 2.5× more unknown words than English? Use the أسد list in your answer." + YOURS)
answer("""
**English 13.0% · Arabic 33.7%** (Lion → Dove: 35.3%)

- **Prefixes stick to the word**: و ف ب ل ك and ال. So الأسد، والأسد، بالأسد، للأسد، كالأسد are separate vocabulary entries, where English uses separate words ("the lion", "and the lion", "with the lion").
- **Endings stick too**: tanween (أسدٌ، أسداً) and pronouns (ملكك، ملكها، ملكنا).
- **Root and pattern**: one root makes many words, e.g. ك-ت-ب → كاتب، مكتوب، مكتبة، يكتبون.
- A word-level vocabulary needs every combination, so it gets big and still meets many unknowns. That is why subword tokenizers matter even more for Arabic.
""")

md("""
**5.4** 💻 `normalize_ar(text)`: classic Arabic text cleaning.
- remove diacritics (U+064B to U+0652: tanween, fatha, damma, kasra, shadda, sukun)
- remove tatweel `ـ`
- `أ إ آ → ا`
- `ى → ي`
- `ة → ه`
""")
sol = task("""
def normalize_ar(text):
    raise NotImplementedError("normalize_ar() is not written yet (task 5.4)")
""", r"""
def normalize_ar(text):
    text = re.sub(r'[ً-ْ]', '', text)    # diacritics
    text = text.replace('ـ', '')              # tatweel
    text = re.sub('[أإآ]', 'ا', text)
    text = text.replace('ى', 'ي').replace('ة', 'ه')
    return text
""")
code("check.normalize_ar(normalize_ar)")
answer(sol)

md("🔮 Normalize both chapters and run Lion → Dove again. How much will the unknown rate drop?" + GUESS)
code("""
size, rate = unk_rate(normalize_ar(lion), normalize_ar(dove), tokenize_ar)
print(f"normalized: vocab {size:,}   unknown: {rate:.1%}")
""")
md("✍️ (a) Why did normalization barely help? (b) Name two kinds of information that normalization throws away." + YOURS)
answer("""
Vocabulary 3,591 → 3,470 · unknown 35.3% → **33.6%**

- **(a)** Normalization fixes *spelling variation* (diacritics, hamza forms). The real problem is *morphology*: والأسد and الأسد are still different words after normalizing.
- **(b)**
  - ة vs ه: مكتبة "library" vs مكتبه "his office".
  - Diacritics: عَلِمَ "he knew" / عُلِمَ "it was known" / عِلْم "knowledge".
  - Hamza: أن vs ان.
- Modern LLM tokenizers usually do **not** normalize. They keep the raw text and let the model learn. Normalization is common in search engines and classic NLP.
""")

md("**5.5** ★★ **How GPT-2 sees Arabic: bytes.** Run this first:")
code("""
for s in ["a", "ك", "كتاب"]:
    print(repr(s), "→", len(s.encode("utf-8")), "bytes:", list(s.encode("utf-8")))
""")
md("🔮 How many GPT-2 tokens is كتاب (4 letters, 8 bytes)? What will you see when you decode each token on its own?" + GUESS)
code("""
ids = gpt2.encode("كتاب")
print(ids)
print([gpt2.decode([i]) for i in ids])
print([gpt2.decode_single_token_bytes(i) for i in ids])
print(gpt2.decode(ids))
""")
md("✍️ Explain the `�` pieces." + YOURS)
answer("""
**5 tokens**: `[b'\\xd9', b'\\x83', b'\\xd8\\xaa', b'\\xd8\\xa7\\xd8', b'\\xa8']`

- An English letter is 1 byte; an Arabic letter is 2 bytes in UTF-8.
- GPT-2's BPE works on bytes and saw little Arabic, so it learned few Arabic merges.
- ك is split into its 2 bytes (2 tokens). ت is one token. The next token holds ا *plus the first half of ب*, and the last token is the second half of ب.
- Half a letter is not valid text on its own, so decoding it prints `�`. Decoding all 5 together gives كتاب back.
- This is how BPE never needs `<|unk|>`: in the worst case it falls back to single bytes.
""")

md("""
**5.6** 💻 **Fertility** = tokens per word. It is the standard way to measure how well a tokenizer fits a language.
Write `fertility(text, enc)` = number of tokens ÷ number of whitespace-separated words.
""")
sol = task("""
def fertility(text, enc):
    raise NotImplementedError("fertility() is not written yet (task 5.6)")
""", """
def fertility(text, enc):
    return len(enc.encode(text)) / len(text.split())
""")
code("check.fertility(fertility, gpt2)")
answer(sol)

md("🔮 Predict the English and Arabic fertility for GPT-2, GPT-4 (`cl100k_base`) and GPT-4o (`o200k_base`). (The first run downloads the tokenizer files.)" + GUESS)
code("""
for name in ["gpt2", "cl100k_base", "o200k_base"]:
    enc = tiktoken.get_encoding(name)
    print(f"{name:12} vocab {enc.n_vocab:>7,}   English {fertility(verdict, enc):.2f}   Arabic {fertility(lion, enc):.2f}")
""")
md("✍️ Your users write Arabic, pay per token, and the model has a fixed context window. List 4 consequences of high fertility." + YOURS)
answer("""
| Tokenizer | English | Arabic |
|---|---|---|
| GPT-2 | 1.42 | 5.53 |
| GPT-4 (cl100k) | 1.36 | 3.92 |
| GPT-4o (o200k) | 1.33 | 1.94 |

With GPT-2, Arabic needs ~3.9× more tokens per word than English. With GPT-4o it needs ~1.5×.

1. **Cost**: APIs charge per token, so the same content costs more in Arabic.
2. **Context**: the window holds fewer Arabic words, so less of a document fits.
3. **Speed**: text is generated one token at a time, so each Arabic word is slower.
4. **Quality**: meaning is spread over many small pieces (even half-letters), which is harder to learn, and the model sees less Arabic per token of training.

- Research: Petrov et al. (2023) found the same text can need up to ~15× more tokens in some languages than in English.
- The Jais paper reports 4.17 tokens per Arabic word for GPT-2's tokenizer vs 1.05 for Jais's own. They count words differently from you, so the numbers differ.
""")

md("""
**5.7** ★★★ **Build your own BPE on Arabic.**

How BPE training works:
1. Split the text into words. Write each word as a list of characters.
2. Count every pair of neighbours, weighted by how often the word appears.
3. Merge the most frequent pair into one symbol, everywhere. Add it to the `merges` list.
4. Repeat `num_merges` times.

How to encode a new word: start from its characters and keep applying the learned merges, earliest-learned first, until none applies.

(GPT-2 does the same on *bytes* and keeps the space attached to the next word. We use characters so the output stays readable.)

🔮 Which pair of letters will be merged **first** in the Lion and Ox chapter?

-
""")
sol = task("""
def train_bpe(text, num_merges):
    # return the merges in the order learned, e.g. [("ا", "ل"), ...]
    raise NotImplementedError("train_bpe() is not written yet (task 5.7)")

def bpe_encode_word(word, merges):
    # return the pieces of one word, e.g. ["و", "الأسد"]
    raise NotImplementedError("bpe_encode_word() is not written yet (task 5.7)")
""", """
def train_bpe(text, num_merges):
    word_freq = collections.Counter(tokenize_ar(text))
    words = {w: list(w) for w in word_freq}            # each word as a list of symbols
    merges = []
    for _ in range(num_merges):
        pairs = collections.Counter()
        for w, f in word_freq.items():
            s = words[w]
            for a, b in zip(s, s[1:]):
                pairs[(a, b)] += f
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        merges.append(best)
        for w in words:                                  # apply the new merge everywhere
            s, out, i = words[w], [], 0
            while i < len(s):
                if i < len(s) - 1 and (s[i], s[i + 1]) == best:
                    out.append(s[i] + s[i + 1])
                    i += 2
                else:
                    out.append(s[i])
                    i += 1
            words[w] = out
    return merges

def bpe_encode_word(word, merges):
    ranks = {pair: r for r, pair in enumerate(merges)}
    s = list(word)
    while len(s) > 1:
        r, i = min((ranks.get(p, float("inf")), i) for i, p in enumerate(zip(s, s[1:])))
        if r == float("inf"):
            break
        s = s[:i] + [s[i] + s[i + 1]] + s[i + 2:]
    return s
""", """
- `train_bpe` re-counts pairs after each merge. That is slow, but it is the clearest way to write it. Real tokenizers update the counts in place.
- `bpe_encode_word` always applies the earliest-learned merge first, the same rule GPT-2 uses.
""")
code("check.train_bpe(train_bpe, bpe_encode_word, lion, tokenize_ar)")
answer(sol)

md("Now train 1,000 merges and test them on the **Dove** chapter, which your tokenizer has never seen:")
code("""
merges = train_bpe(lion, 1000)          # takes a few seconds
print("first 15 merges:", ["".join(m) for m in merges[:15]])

test_words = tokenize_ar(dove)
o200k = tiktoken.get_encoding("o200k_base")
for k in [0, 250, 500, 1000]:
    n = sum(len(bpe_encode_word(w, merges[:k])) for w in test_words)
    print(f"your BPE, {k:4} merges: {n / len(test_words):.2f} tokens per word")
print(f"GPT-4o (o200k):        {sum(len(o200k.encode(w)) for w in test_words) / len(test_words):.2f} tokens per word")
""")
code("""
for w in ["والأسد", "فقال", "كليلة", "وبالكتاب", "سيكتبون", "مكتبة"]:
    print(f"{w:10} yours: {bpe_encode_word(w, merges)}   GPT-4o: {[o200k.decode([i]) for i in o200k.encode(w)]}")
""")
md("""
✍️
- **(a)** What was the first merge, and why that pair?
- **(b)** Your tiny tokenizer beats GPT-4o's on the Dove chapter. How is that possible? And why does it split وبالكتاب so badly?
- **(c)** Is BPE learning grammar? Use والأسد and مكتبة in your answer.
- **(d)** ★ Optional: try a sentence in your own dialect. What happens, and why?
""" + YOURS)
answer("""
- **(a)** **ال** is merge #1. The definite article starts a huge share of Arabic words. Next come من، ما، لا، عل، ان، في: the most common short words and pieces.
- **(b)** Dove chapter: 0 merges 3.75 → 250: 2.24 → 500: 2.00 → 1,000: **1.81** tokens per word. GPT-4o: **2.01**.
  - Yours was trained on the same book: same style, same names (كليلة، دمنة، الأسد), so those come out as whole words. GPT-4o's 200k vocabulary is shared by every language and every kind of text.
  - But كتاب never appears in the Lion chapter. Yours gives وب | الك | ت | اب, while GPT-4o gives وب | ال | كتاب.
  - Lesson: **a tokenizer is only good on text like its training data**. That is why Arabic LLMs train their tokenizers on lots of Arabic.
- **(c)** No: it learns *frequent strings*.
  - Sometimes that matches grammar: والأسد → و | الأسد (conjunction + word), learned with no rules.
  - Sometimes it does not: مكتبة → مك | ت | بة, which cuts through the root ك-ت-ب. GPT-4o's split is no better: م | كت | بة.
- **(d)** Your tokenizer saw only classical Arabic. Dialect words (for example وش or أبغى in Gulf Arabic) were never seen, so they split into small pieces and you get more tokens per word. It is the same lesson as (b).
""")

md("""
**5.8** ★ **Where the field is now**

You just climbed the same ladder the field did:

1. **Word-level** (your Level 3 tokenizer): simple, but every unseen form becomes `<|unk|>`. In Arabic, about 1 word in 3 was unknown.
2. **Byte-level BPE trained mostly on English** (GPT-2, 2019): it never fails, but Arabic costs ~4× the tokens and gets cut into half-letters.
3. **Bigger shared vocabularies** (GPT-4 ~100k → GPT-4o ~200k): more room for other languages. In your test, Arabic dropped from 5.5 to 1.9 tokens per word.
4. **Arabic-first tokenizers**, done in two ways:
   - **Train your own** on balanced Arabic + English data. Jais used an 84,992-token BPE and reports ~1 token per Arabic word. Jais 2 uses ~150k tokens.
   - **Extend an English model's tokenizer.** ALLaM (SDAIA) took Llama 2, trained an Arabic tokenizer, and added the new Arabic tokens to the old vocabulary. Each new token's embedding started as the *average of the embeddings of the old pieces* it used to be split into. That beat starting from random by a wide margin. Your repo shows how this works in code: `bookcode/ch05/09_extending-tokenizers`.
5. **No tokenizer at all** (research): the model reads raw bytes. Byte sequences are long (كتاب = 8 bytes), so these models group bytes into chunks.
   - **BLT** (Meta, 2024): groups bytes into "patches", long where the text is easy to predict and short where it is hard.
   - **H-Net** (2025): learns where to cut, end to end. H-Net++ tested the idea on Persian, which uses the Arabic script and is also morphologically rich.

   Most production models still use BPE.

✍️
- **(a)** Why start a new token's embedding from the average of the old pieces' embeddings instead of random numbers?
- **(b)** You are building an Arabic chatbot tomorrow. Which step would you choose, and why? (There is no single right answer.)
- **(c)** Name one thing tokenizer-free models fix and one thing they cost.
""" + YOURS)
answer("""
- **(a)** The old pieces' embeddings were already learned, so their average already carries roughly the right meaning. Training starts near a good point instead of from zero. ALLaM reports a significant boost from this.
- **(b)** A good answer:
  - Start from a model whose tokenizer is strong on Arabic: an Arabic-first model like Jais or ALLaM, or one with a big multilingual vocabulary.
  - Measure fertility on your real users' text, including dialect, the way you did in 5.6.
  - If you must adapt an English model, extend its tokenizer (step 4).
- **(c)**
  - **Fixes**: there is no fixed vocabulary, so no bias from which languages the tokenizer was trained on. It also copes with spelling, diacritics, dialects and typos.
  - **Costs**: sequences are much longer, so they need more compute and memory. That is why these models need patching or chunking tricks.
""")

# ======================================================================= level 6
md("""
---
## Level 6 · Stretch: modern positions with RoPE ★★★

**The problem (from 4.2)**
- GPT-2's positions are a learned table with one row per position. No row means no position.
- The vector for position 7 says "I am at 7", but what usually matters in language is "how far apart are these two words?"

**The RoPE idea** (Su et al., 2021; used by Llama, Qwen, Gemma and most open models today)
1. Don't *add* a position vector. *Rotate* the vector instead.
2. Split the vector into pairs of numbers: (x₀, x₁), (x₂, x₃), …
3. Rotate pair *i* by the angle **position × θᵢ**, where θᵢ = 10000^(−2i/D). The first pairs spin fast and the last pairs spin slowly.
4. To rotate a pair (a, b) by an angle φ: (a·cos φ − b·sin φ, a·sin φ + b·cos φ).

**Why this gives relative positions**
- Attention compares two vectors with a dot product (Chapter 3).
- If q is rotated by m·θ and k by n·θ, the dot product only sees the *difference* (m − n)·θ.

**Example** (one pair, θ = 90° per position)
- q = (1, 0) at position 1 is rotated 90°, giving (0, 1). k = (1, 0) at position 0 stays (1, 0). Dot product = **0**.
- Move both forward by one. q at position 2 is rotated 180°, giving (−1, 0). k at position 1 is rotated 90°, giving (0, 1). Dot product = **0** again.
- The score is the same because the distance is still 1.

**Where it goes in real models**
- Inside attention, on the queries and keys (Chapter 3), not on the input embeddings. That is why Llama has no `pos_emb` layer.
- See `bookcode/ch05/07_gpt_to_llama/converting-gpt-to-llama2.ipynb`.

**6.1** 💻 `rope(x, pos)`: `x` has shape `[T, D]` (D is even) and `pos` has shape `[T]`. Rotate each pair of `x[t]` by `pos[t] × θᵢ` and return a tensor of shape `[T, D]`.
""")
sol = task("""
def rope(x, pos, base=10000.0):
    raise NotImplementedError("rope() is not written yet (task 6.1)")
""", """
def rope(x, pos, base=10000.0):
    T, D = x.shape
    i = torch.arange(D // 2, dtype=torch.float32)
    theta = base ** (-2 * i / D)                       # [D/2]: one speed per pair
    angle = pos[:, None].float() * theta[None, :]      # [T, D/2]
    cos, sin = torch.cos(angle), torch.sin(angle)
    a, b = x[:, 0::2], x[:, 1::2]                      # the two numbers of each pair
    out = torch.empty_like(x)
    out[:, 0::2] = a * cos - b * sin
    out[:, 1::2] = a * sin + b * cos
    return out
""", """
- Llama's code pairs dimension *i* with *i + D/2* ("rotate half") instead of neighbouring dimensions. It is the same idea with a different pairing, and the check accepts both.
""")
code("check.rope(rope)")
answer(sol)

md("""
✍️
- **(a)** In your own words: why does the score depend only on the distance?
- **(b)** Does RoPE fix question 4.2 (5 tokens into a 4-position model)? Fully?
""" + YOURS)
answer("""
- **(a)** Rotating both vectors by the same extra angle does not change the angle *between* them. A dot product depends only on the two lengths and that angle, so only (m − n) matters.
- **(b)**
  - **The crash**: yes. The angle comes from a formula, so any position works and there is no table to run out of.
  - **Fully**: no. The model only learned to use distances it saw in training, and quality drops far beyond them. Long-context models stretch the angles (for example position interpolation or YaRN) and then train a little on long text.
""")

# ======================================================================= wrap-up
md("""
---
## Done? Next steps
- [ ] Tell Claude **"grade ch2"**. Your written answers get read, scored, and the gaps pointed out.
- [ ] Spaced review: answer the *Test Yourself* Chapter 2 questions with the book closed, **tomorrow**, **in 3 days** and **in a week**.
  - File: `~/sync/books/ai/llm-from-scratch-chapters/test-yourself/02 - Working with text data (Test Yourself).pdf`
- [ ] In 3–4 days: redo Level 3 in an empty notebook. Count your `# PEEK`s and aim for fewer.
- The Chapter 3 assignment will include 2–3 questions from this chapter.
""")

# ======================================================================= write
meta = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}
for path, cells in [(STUDENT, student), (SOLVED, solved)]:
    nb = nbf.v4.new_notebook(cells=cells, metadata=meta)
    nbf.validate(nb)
    nbf.write(nb, path)
    print("wrote", path, len(cells), "cells")

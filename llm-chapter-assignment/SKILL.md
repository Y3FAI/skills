---
name: llm-chapter-assignment
description: Build the end-of-chapter assignment notebook for Sebastian Raschka's "Build a Large Language Model (From Scratch)". Six levels from easy to hard, writing and coding, answers hidden in the notebook, automatic checks, an Arabic lab, and a "what is state of the art now" expansion. Use when the user finishes or is reading a chapter and asks for its assignment, review notebook or "chN notebook", or says "grade chN".
---

# LLM book: chapter assignment notebooks

The user is working through *Build a Large Language Model (From Scratch)* and wants active practice after each chapter, not passive reading. Chapter 2 is done and approved. Copy its format for every later chapter.

## What the user asked for (keep all of it)
- **Assignments after each chapter**: some writing, some coding, some easy, some hard.
- **Start from basics and build up gradually.** Each level builds on the one before.
- **Expansion**: what is state of the art now, what is new, and how to build it from scratch.
- **Personal angle: Arabic.** Start simple, go up to today's best, and show the issues Arabic has. This is what makes the user care.
- **Answers hidden inside the notebook**, not in a separate file.
- **Targeted, not overwhelming**: about 3–4 hours per chapter, spread over a few days. Never "100 things".
- Plain words. Lists instead of paragraphs. Model answers are short and easy to memorize: a definition plus a few bullets.

## Where things are
| What | Path |
|---|---|
| Book PDF, split per chapter | `~/sync/books/ai/llm-from-scratch-chapters/book/NN - <title>.pdf` (also appendices A–E) |
| Test Yourself companion, split | `~/sync/books/ai/llm-from-scratch-chapters/test-yourself/NN - <title> (Test Yourself).pdf` |
| User's workspace | `~/learn/llm-from-scratch/` (has `.venv` with torch and tiktoken; run with `.venv/bin/python`) |
| Book's official repo (clone) | `~/learn/llm-from-scratch/bookcode/`: `chNN/01_main-chapter-code`, bonus folders, `pkg/llms_from_scratch/chNN.py` (importable reference code) |
| User's own chapter notebooks | `~/learn/llm-from-scratch/mycode/chN.ipynb` |
| Assignment output | `~/learn/llm-from-scratch/mycode/chN-assignment.ipynb` and `mycode/chN_checks.py` |
| Arabic texts | `mycode/data/` (Kalila wa Dimna from Arabic Wikisource: `kalila-lion-and-ox.txt` for training, `kalila-ringed-dove.txt` as the unseen test text) |
| Progress and weak spots | `mycode/progress.md` (update it after every grading) |
| Working example | `examples/build_ch2.py` (builder) and `examples/ch2_checks.py` (checks) in this skill folder |

## Workflow for a new chapter N
1. **Read the chapter.** Run `pdftotext -layout` on the split book PDF and on the Test Yourself PDF, then read both in full. List the 5–8 ideas that only stick by *doing* them: shapes, off-by-ones, "why" questions.
2. **Read the user's own `mycode/chN.ipynb`** (and earlier ones) to see how far they got and spot real bugs. A real bug from their notebook makes the best "spot the bug" item.
3. **Read `mycode/progress.md`** to see the weak spots from earlier gradings. They feed Level 0.
4. **Pick the expansion topics** from the repo. Prefer Raschka's own from-scratch builds, so the style matches the book. Use the map below. Check anything you claim about current models: search the web, and read the folder's README or code.
5. **Propose a short outline** (about 8 lines: level titles, the Arabic lab steps, the state-of-the-art pick) and **wait for the user's OK**. The user likes to move one step at a time. Do not rebuild the format; it is approved.
6. **Write `chN_checks.py`** in the style of `examples/ch2_checks.py`:
   - Test *behaviour* and never contain solutions. Compare with the book's reference code (`from llms_from_scratch.chNN import ...`) or with properties (shapes, round-trips, invariants).
   - Output: `✅` / `❌ + hint` / `⏳ not done yet`. A stub must never pass.
   - Avoid expensive work inside loops: train once, then reuse.
7. **Write `build_chN.py`** by copying `examples/build_ch2.py`. Its helpers are `md`, `code`, `answer` (wraps text in `<details><summary><b>🔒 Show answer</b></summary>`), and `task(stub, solution, notes)`. `task` puts the stub in the student notebook, the solution in the solved copy, and returns the solution for the hidden answer. Stubs raise `NotImplementedError("<name>() is not written yet (task X.Y)")`.
8. **Build both notebooks**: the student one goes in `mycode/`, the solved one in the scratchpad.
9. **Verify** from `mycode/`:
   ```bash
   PYTHONPATH=. ../.venv/bin/python <skill>/scripts/verify_notebook.py solved  <scratchpad>/chN-solved.ipynb
   PYTHONPATH=. ../.venv/bin/python <skill>/scripts/verify_notebook.py student chN-assignment.ipynb
   ```
   Both must print `OK`. **Copy every number in a hidden answer from the solved run's output.** Never guess numbers. Also grep the student notebook's code cells for solution text, to make sure nothing leaked.
10. **Report** the file path, the level table, and how to start. Mention "grade chN".

## Notebook format (approved with Chapter 2)
- **Intro**: how it works, icons (✍️ write with book closed · 🔮 predict before running · 💻 code + check), the level/time table, and "tell Claude *grade chN* when done".
- **Setup cell**: imports, `sys.path` to `../bookcode/pkg`, `import chN_checks as check`, load the texts, an assert that the working directory is `mycode/`.
- **Level 0 · Warm-up from earlier chapters** (from Chapter 3 on): 2–3 questions from previous chapters, chosen from the weak spots in `progress.md`. This builds in spaced review and mixes topics.
- **Level 1 · Big picture ★**: 5–6 short recall questions (define / explain / list / differentiate). The answer slot sits in the same cell (`✍️ **Your answer:**`). Hidden model answer below it.
- **Level 2 · Predict, then run ★→★★**: 7–9 items about outputs, counts and tensor shapes. Prediction slot → code cell → hidden answer with the reason.
- **Level 3 · Build it yourself ★★**: a from-memory rebuild of the chapter's code, split into small functions, each followed by a `check.*` cell. Start with a "spot the bug" item. Mark peeks with `# PEEK`. End with a "put it together" cell on real data.
- **Level 4 · Think deeper ★★★**: 3–4 questions the book does not answer directly, reasoned from what it teaches. One of them should bridge to the next chapter.
- **Level 5 · Arabic lab ★→★★★**: the chapter's main idea applied to Arabic. Go from the simple version up to today's best, measure with real numbers, and finish with a short "where the field is now" section taught in plain words, plus 2–3 ✍️ questions.
- **Level 6 · Stretch: the modern version ★★★**: one state-of-the-art upgrade of what the chapter built. Teach it (problem → idea → tiny worked example → where it goes in real models), then have the user implement it from scratch with property checks.
- **Wrap-up**: "grade chN"; Test Yourself questions with the book closed (tomorrow / in 3 days / in a week); redo Level 3 in an empty notebook in 3–4 days.

Writing rules: questions are short and exam-style. Hidden answers are complete but minimal. Number and label every item (2.6, 5.3, …). Give each ★ level a time.

## Expansion map (from the local repo; check READMEs before using)
| Chapter | Arabic lab idea | State-of-the-art / from-scratch pick |
|---|---|---|
| 2 ✅ | Tokenizing Arabic: regex → word vocab (33.7% unknown vs 13.0% English) → normalization → bytes → fertility GPT-2/GPT-4/GPT-4o → own BPE → Jais / ALLaM / BLT / H-Net | RoPE (`ch05/07_gpt_to_llama`) |
| 3 Attention | Attention over Arabic subword pieces: does و or ال attend to its word? Fertility × quadratic attention cost | GQA `ch04/04_gqa`, MLA `ch04/05_mla`, sliding window `ch04/06_swa`, efficient MHA `ch03/02_bonus_efficient-multihead-attention` |
| 4 GPT model | Parameter count of the embedding table for an Arabic-heavy vocabulary (50k vs 150k+ tokens) | RMSNorm, SwiGLU, RoPE (GPT → Llama in `ch05/07_gpt_to_llama`), KV cache `ch04/03_kv-cache`, MoE `ch04/07_moe`, linear-attention hybrids `ch04/08_deltanet` |
| 5 Pretraining | Pretrain the small GPT on Kalila wa Dimna and compare its output with The Verdict run; loss per token vs per word across tokenizers | LR schedules `ch05/04_learning_rate_schedulers`, Muon `ch05/18_muon`, modern models from scratch: `11_qwen3`, `16_qwen3.5`, `17_gemma4`, `15_tiny-aya` (multilingual, Arabic) |
| 6 Classification | Arabic text classifier (find a free Arabic sentiment or spam dataset and check its license) | LoRA (`appendix-E`) |
| 7 Instructions | Arabic instruction pairs, evaluation in Arabic | DPO `ch07/04_preference-tuning-with-dpo`; reasoning: the `reasoning-from-scratch` submodule is empty locally (`git submodule update --init` if needed) |

## Grading ("grade chN")
1. Read `mycode/chN-assignment.ipynb` as JSON. Collect every `✍️ Your answer` and `🔮 Your prediction` cell and the outputs of the check cells.
2. Compare against the hidden answers. For each level: a score (e.g. 4/6), what was right, the **specific** gap, and the corrected idea in 1–2 lines. Be honest and short.
3. Ask 1–2 follow-up questions on the weakest point.
4. Append to `mycode/progress.md`: date, scores per level, weak spots. Those weak spots become next chapter's Level 0.

## Facts already checked for Chapter 2 (reuse, don't re-research)
- The Verdict: 20,479 characters, 4,690 regex tokens, 1,130 unique; 5,145 GPT-2 tokens. With `max_length=4, stride=4`: 1,286 rows and 160 batches (`drop_last`). With `stride=1`: 5,141 rows.
- Fertility (tokens per whitespace word):

  | Tokenizer | English | Arabic |
  |---|---|---|
  | GPT-2 | 1.42 | 5.53 |
  | cl100k | 1.36 | 3.92 |
  | o200k | 1.33 | 1.94 |

- Own character BPE on the Lion chapter: merge #1 is «ال». Tested on the Dove chapter: 1.81 tokens per word with 1,000 merges vs 2.01 for o200k.
- Jais: 84,992-token BPE, Arabic fertility ~1.05 vs 4.17 for GPT-2 (Jais paper). Jais 2: ~150k vocabulary.
- ALLaM: extended the Llama 2 tokenizer with Arabic tokens and started each new embedding from the average of its old pieces' embeddings.
- BLT: Meta, 2024, ACL 2025. H-Net: 2025. H-Net++ was tested on Persian.

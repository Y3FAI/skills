Exit code 1
# Flooki's own exam-writing prompt

This is the prompt the flooki.app how-to page gives people to paste into an AI, copied from the site on 2026-10-20.
Its rules are Flooki's, so follow them. Inside a JSON *file* a LaTeX backslash is written twice (`\\frac`);
in a Python or JavaScript string you build and serialise, write it once and let the serialiser escape it.

```text
You are generating exam questions. Return a JSON array only: no markdown, no extra text.

Source priority:
1. Lecture slides/course materials are the authoritative class content when provided. Every question must come from these source materials.
2. Try to cover all important content across the provided class materials, not just the first or easiest sections.
3. Past exam samples are used to match style, difficulty, wording patterns, common traps, and topic distribution.
4. If class materials are not provided, generate questions from the past exam samples only.
5. Do not invent facts, topics, or question styles not supported by the provided materials or past exam samples.

Question types and their required fields:

1. multiple_choice → type, text, options (array of 4+), correctIndex, explanation
2. true_false → type, text, options (exactly ["True","False"] or matching language), correctIndex, explanation
3. short_answer → type, text, correctAnswer, explanation

Rules:
- Root must be a JSON array.
- true_false must have exactly 2 options.
- Use multiple_choice, true_false, and short_answer only if those question types appear in the past exam samples.
- Do not include a points field.
- img is optional and can be used for graphs/diagrams. It must be inline SVG or Mermaid diagram syntax.
- Match the language of the source materials unless told otherwise.
- Prefer exam-like wording over summary-like wording.
- Use class materials for the actual facts and concepts, and past exam samples for exam style.
- Each question must be answerable on its own. Do not reference source materials, slides, lectures, class notes, file names, citations, or markers like [cite] in any field.
- For multiple_choice questions, make distractors match the quality, style, and difficulty of the past exams.
- Randomize correct answer positions. Do not create predictable answer patterns.

Graph & diagram questions:
- Do not create graph or diagram questions unless the past exam samples include graph or diagram questions.
- Put the graph in img as inline SVG or Mermaid diagram syntax. Do not use image links or base64.
- Mermaid syntax examples: flowchart, graph, sequenceDiagram, classDiagram, stateDiagram, erDiagram, gantt, pie, gitGraph, mindmap, timeline.
- Make the graph readable: labels, units, and values needed to answer the question.
- If it is a short_answer graph question, also write the key graph facts in text, correctAnswer, or explanation.

Code & math in JSON strings (text, explanation, correctAnswer):
- Inline code: `const x = 1`
- Code blocks: fenced with language label (```python ... ```)
- Inline math: $...$
- Display math: $$...$$
- Escape LaTeX backslashes in JSON: \\frac, \\sqrt, \\pi

Explanation quality:
- Every question must include a helpful explanation for student review.
- Best format: short answer first, then 1-3 sentences that reinforce the key idea.
- Explain the concept clearly, not just why the answer is correct.
- Mention wrong options only when they are close, common mistakes, or useful for learning.
- For short_answer, include the expected answer and acceptable variants.

Example:
[
  {
    "type": "multiple_choice",
    "text": "What is the derivative of $x^2$?",
    "options": ["$2x$", "$x^2$", "$2$", "$x$"],
    "correctIndex": 0,
    "explanation": "Using the power rule: $\\frac{d}{dx}x^n = nx^{n-1}$, so $\\frac{d}{dx}x^2 = 2x$."
  },
  {
    "type": "true_false",
    "text": "TCP is a connectionless protocol.",
    "options": ["True", "False"],
    "correctIndex": 1,
    "explanation": "TCP is connection-oriented. UDP is the connectionless protocol."
  },
  {
    "type": "short_answer",
    "text": "What is the identity matrix of size 2?",
    "correctAnswer": "[[1,0],[0,1]]",
    "explanation": "The identity matrix has 1s on the diagonal and 0s elsewhere."
  },
  {
    "type": "multiple_choice",
    "text": "According to the graph, which point has the greatest y-value?",
    "img": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 180'><line x1='35' y1='145' x2='230' y2='145' stroke='white'/><line x1='35' y1='145' x2='35' y2='20' stroke='white'/><text x='230' y='165' font-size='12' fill='white'>x</text><text x='12' y='25' font-size='12' fill='white'>y</text><circle cx='80' cy='105' r='5' fill='white'/><text x='70' y='95' font-size='12' fill='white'>A</text><circle cx='130' cy='55' r='5' fill='white'/><text x='120' y='45' font-size='12' fill='white'>B</text><circle cx='180' cy='85' r='5' fill='white'/><text x='170' y='75' font-size='12' fill='white'>C</text></svg>",
    "options": ["A", "B", "C", "All are equal"],
    "correctIndex": 1,
    "explanation": "Point B is highest on the y-axis, so it has the greatest y-value."
  },
  {
    "type": "multiple_choice",
    "text": "In the flowchart, what happens when the condition is true?",
    "img": "flowchart TD
    A[Start] --> B{Is valid?}
    B -->|Yes| C[Accept]
    B -->|No| D[Reject]",
    "options": ["Accept", "Reject", "Restart", "Timeout"],
    "correctIndex": 0,
    "explanation": "The flowchart shows that when the condition 'Is valid?' is true (Yes branch), it leads to Accept."
  }
]
```
(eval):1: ==== not found

# Flooki AI Exam API

This endpoint lets a personal AI agent create a Flooki exam and receive a
shareable exam URL.

Use this manual for AI agents that call the API directly.

Important distinction:

- `/api/agent/create-exam` expects a JSON **object** with `title`, optional
  metadata, and a `questions` field that is a **JSON-encoded string** (not a raw
  array).
- The public `/how-to` page teaches humans to paste a raw JSON array into the
  website. That raw array is the *value* you stringify into `questions` here — do
  not send it as a root array to this API endpoint.

## Endpoint

`POST https://flooki.app/api/agent/create-exam`

Authentication:

```http
Authorization: Bearer <FLOOKI_SERVICE_TOKEN>
Content-Type: application/json
```

The bearer token is the `FLOOKI_SERVICE_TOKEN` secret. The live value is **not**
written in this file; it lives in:

- the repo root `.env` as `FLOOKI_SERVICE_TOKEN` (source of truth), and
- the deployed Worker as the `FLOOKI_SERVICE_TOKEN` secret (`wrangler secret`),
  and `apps/web/.dev.vars` for local runtime.

A missing or wrong token returns `401 { "error": "UNAUTHORIZED" }`.

## Request Body

The request body must be one JSON object. Note that **`questions` is a string**
containing a JSON array (the server re-parses it), not an array literal:

```json
{
  "title": "Physics Midterm Practice",
  "description": "Generated from chapter 3 notes",
  "metadata": {
    "subject": "Physics",
    "institution": "Saudi Electronic University",
    "examType": "other",
    "customExamType": "Chapter 3 Practice"
  },
  "questions": "[{\"type\":\"multiple_choice\",\"text\":\"...\",\"options\":[\"A\",\"B\"],\"correctIndex\":0,\"explanation\":\"...\"}]"
}
```

In code you build the array normally and stringify it:
`questions: JSON.stringify(questionsArray)`.

Required fields:

- `title`: non-empty string, max 200 characters.
- `questions`: a JSON **string** whose parsed value is an array of 1 to 500 valid
  question objects. Sending a raw array (not a string) returns
  `MISSING_REQUIRED_FIELDS`.

Optional fields:

- `description`: string, max 500 characters.
- `metadata.subject`: string, max 100 characters.
- `metadata.institution`: string, max 100 characters.
- `metadata.examType`: one of `quiz`, `midterm`, `final`, `other`.
- `metadata.customExamType`: string, max 50 characters. **Required** when
  `examType` is `"other"`, and **forbidden** otherwise (see rules below).
- `topic`: optional per-question string, max 80 characters.
- `img`: optional per-question string — either inline SVG (`<svg …</svg>`) or
  Mermaid diagram syntax (starts with a Mermaid keyword such as `flowchart`,
  `graph`, `sequenceDiagram`). Image URLs, Markdown images, and base64 are ignored.

There is **no `isPublished` field** — the API does not read it. Direct
`/exam/:id` URLs always work; there is no separate publish toggle.

## Question Formats

Do not include `points`. Flooki assigns points automatically (choice = 1,
short answer = 3) and **rejects any question that sends `points`**.

### Multiple Choice

```json
{
  "type": "multiple_choice",
  "topic": "Kinematics",
  "text": "What is the SI unit of force?",
  "options": ["Newton", "Joule", "Watt", "Pascal"],
  "correctIndex": 0,
  "explanation": "The SI unit of force is the newton."
}
```

Rules:

- `options` must contain at least 2 non-empty strings.
- `correctIndex` is a zero-based **number** (not a string) pointing at the correct
  option; it must be in range.
- `explanation` is required.
- Do not include `correctAnswer` or `points`.

### True / False

```json
{
  "type": "true_false",
  "text": "The Earth orbits the Sun.",
  "options": ["True", "False"],
  "correctIndex": 0,
  "explanation": "The Earth completes one orbit around the Sun about once per year."
}
```

Rules:

- `options` must contain exactly 2 non-empty strings.
- `correctIndex` is a zero-based number.
- `explanation` is required.
- Do not include `correctAnswer` or `points`.

### Short Answer

```json
{
  "type": "short_answer",
  "topic": "Cell biology",
  "text": "What is the function of mitochondria?",
  "correctAnswer": "They produce ATP through cellular respiration.",
  "explanation": "Mitochondria are the main site of ATP production in eukaryotic cells."
}
```

Rules:

- `correctAnswer` is required.
- Do not include `options` or `correctIndex`.
- Do not include `points`.
- Flooki grades short answers out of 3 points.

## Markdown-fence tolerance

The parser runs on the parsed value of the `questions` string. If that string is
accidentally wrapped in a ```` ```json ```` code fence or has leading/trailing
prose, the server strips the fence and slices to the outer `[ … ]` before
parsing, so the submit still succeeds. **This is a safety net, not the contract**
— prefer clean, fence-free JSON. Malformed JSON (e.g. a trailing comma) still
fails with `INVALID_QUESTION_STRUCTURE`.

## Exam type and custom label

`examType` and `customExamType` are mutually constrained (mismatches return
`INVALID_METADATA`):

- `examType: "other"` **requires** a non-empty `customExamType`.
- Any other `examType` (`quiz`/`midterm`/`final`) **must not** include
  `customExamType`.

To make a chapter, week, file name, or custom label appear on the exam screen,
use the `"other"` shape:

```json
{
  "title": "MATH150 Week 6 - Induction and Recursion",
  "metadata": {
    "subject": "MATH150",
    "examType": "other",
    "customExamType": "Week 6 - Induction and Recursion"
  }
}
```

## Successful Response

```json
{
  "id": "abc123def0",
  "url": "https://flooki.app/exam/abc123def0"
}
```

Use `url` as the shareable exam link.

## Error Response

```json
{
  "error": "INVALID_QUESTION_STRUCTURE"
}
```

Possible errors:

- `METHOD_NOT_ALLOWED`: use `POST`.
- `UNAUTHORIZED`: missing or wrong bearer token.
- `MISSING_REQUIRED_FIELDS`: missing `title`, or `questions` missing / not a
  string.
- `INVALID_TITLE`: invalid title type or empty sanitized title.
- `QUESTIONS_TOO_LONG`: the `questions` string exceeds 200000 characters.
- `INVALID_METADATA`: invalid `description` or `metadata` (including the
  examType/customExamType constraints above).
- `INVALID_QUESTION_STRUCTURE`: a question does not match Flooki's schema, or the
  `questions` string is not valid JSON.
- `NO_VALID_QUESTIONS`: the parsed array is empty.
- `TOO_MANY_QUESTIONS`: more than 500 questions.
- `SERVER_ERROR`: server configuration or persistence failed.

## cURL Example

```bash
curl -s https://flooki.app/api/agent/create-exam \
  -H "Authorization: Bearer $FLOOKI_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Physics Quick Check",
    "metadata": {
      "subject": "Physics",
      "examType": "other",
      "customExamType": "Quick Check"
    },
    "questions": "[{\"type\":\"multiple_choice\",\"text\":\"What is the SI unit of force?\",\"options\":[\"Newton\",\"Joule\",\"Watt\",\"Pascal\"],\"correctIndex\":0,\"explanation\":\"The SI unit of force is the newton.\"}]"
  }'
```

## JavaScript Example

```ts
const questions = [
  {
    type: "short_answer",
    text: "What do mitochondria produce?",
    correctAnswer: "ATP",
    explanation: "Mitochondria produce ATP through cellular respiration.",
  },
];

const response = await fetch("https://flooki.app/api/agent/create-exam", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.FLOOKI_SERVICE_TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "Biology Practice",
    metadata: {
      subject: "Biology",
      examType: "other",
      customExamType: "Practice",
    },
    // questions is a STRING: stringify the array.
    questions: JSON.stringify(questions),
  }),
});

const result = await response.json();
if (!response.ok) {
  throw new Error(result.error);
}

console.log(result.url);
```

## AI Agent Formatting Rules

When generating a payload:

- Build one JSON object for the API request body. Do not send a root JSON array.
- Put the questions array into the `questions` field as a **JSON string**
  (`JSON.stringify(array)`), not as a nested array.
- Include `title` and at least one valid question.
- For chapter, week, file-based, or otherwise custom exam titles, set
  `metadata.examType` to `"other"` and put the short display label in
  `metadata.customExamType`. Otherwise omit `customExamType`.
- Prefer Arabic question text/explanations when the source material is Arabic.
- Keep every string non-empty after trimming.
- Use `correctIndex` as a number, not a string.
- Randomize correct answer positions for multiple-choice questions.
- Keep explanations useful enough for review after the exam.
- Never include `points`, `isPublished`, or fields outside this manual.

Before calling the API, verify:

- Root value is an object, not an array.
- `questions` is a JSON string; its parsed length is between 1 and 500.
- `metadata.examType` is omitted or one of `quiz`, `midterm`, `final`, `other`.
- If `metadata.examType` is `other`, `metadata.customExamType` is a non-empty
  string; otherwise `customExamType` is omitted.
- Every choice question has non-empty `text`, `options`, `correctIndex`, and
  `explanation`.
- Every true/false question has exactly two options.
- Every short-answer question has non-empty `text`, `correctAnswer`, and
  `explanation`.
- No question includes `points`.

## Agent Task Template

Use this instruction when asking an AI to create and publish a Flooki exam
through the API:

```text
Create a Flooki exam from the provided source material.

Send a POST request to:
https://flooki.app/api/agent/create-exam

Use headers:
Authorization: Bearer <FLOOKI_SERVICE_TOKEN>
Content-Type: application/json

The request body must be one JSON object:
{
  "title": string,
  "description": string,
  "metadata": {
    "subject": string,
    "institution": string,
    "examType": "quiz" | "midterm" | "final" | "other",
    "customExamType": string only when examType is "other"
  },
  "questions": string   // JSON.stringify of the Question[] array
}

Use only these question types (inside the stringified array):
- multiple_choice: type, text, options, correctIndex, explanation, optional topic, optional img
- true_false: type, text, options, correctIndex, explanation, optional topic, optional img
- short_answer: type, text, correctAnswer, explanation, optional topic, optional img

questions must be a JSON string, not a nested array.
Do not include points or isPublished.
Do not wrap the JSON in Markdown.
After the API responds, return the `url` field to the user.
```

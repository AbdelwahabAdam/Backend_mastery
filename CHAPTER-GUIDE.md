# Chapter Writing Guide

This is the standard every chapter in this handbook must meet. The reference chapter is
[Module 02 · JWT Authentication](Module-02-Core-Backend/08-JWT-Authentication.md). Before writing a chapter, read that one.

## The one rule

**Every section must be about this topic.** If you could paste a paragraph into another chapter and it would still make sense, delete it. Generic advice like "state the invariant", "measure p99" or "deploy progressively" only belongs in a chapter when it is tied to a concrete detail of *this* topic.

## Chapter structure

```markdown
# <Title>

> **Module NN · <Module name>** · Prerequisites: [..](..) · Next: [..](..)

---

## ⏱ If You Only Have 2 Minutes
5–8 bullets. Each one is a specific fact, rule, or number you could say in an interview.

---

## 1. What It Is and Why It Exists
A plain-English definition, one everyday analogy, and the concrete problem it solves (what breaks without it).

## 2. How It Works
The actual mechanism: steps, data formats, protocol messages, algorithms, state changes.
Include one topic-specific Mermaid diagram (sequence, flowchart or state) if it helps.

## 3. Key Concepts
3–6 `###` subsections with the terms an interviewer expects. Use tables for options and their trade-offs.

## 4. Code Examples
### Node.js / TypeScript
### Python
The same scenario in both languages. See "Code rules" below.

## 5. Production Concerns
Security, performance, failure modes, and what to log/measure — only the parts specific to this topic.

## 6. Common Mistakes
5–7 bullets in the form: **Mistake** — what goes wrong — the fix.

## 7. Comparison Table
Compare this topic against its real alternatives (e.g. JWT vs server sessions). Omit the section if no honest comparison exists.

## 8. Interview Questions
6–8 questions labelled **[Junior]**, **[Mid]** or **[Senior]**, each with a real 2–6 sentence answer.
At least two must be Senior-level (trade-offs, failure scenarios, design decisions).

## 9. Cheat Sheet
8–15 terse lines you would review the night before an interview.

## Related Topics
3–6 links, each with a few words on why it is related.
```

## Code rules

- **Both languages, every chapter.** Node.js 22+ with TypeScript 5 (Express 5 by default) and Python 3.12+ (FastAPI + Pydantic v2 by default). Use another library only when it is the normal choice for the topic (e.g. `jose`, `PyJWT`, `BullMQ`, `Celery`, `pino`, `structlog`, `prom-client`, `prometheus-client`, OpenTelemetry).
- **Real, complete code.** Include imports. No pseudo-code, no `...` in the middle of logic. Name the npm/pip packages in a comment on the first line.
- **Idiomatic per language.** Do not translate line by line. Point out a real difference between the runtimes when one exists (e.g. a sync call blocking the Node event loop vs FastAPI running `def` dependencies in a thread pool).
- **Short.** About 20–70 lines per language per block. Two blocks per language is the maximum.
- **Comments explain *why*,** not what.
- **Type-safe TypeScript.** In Express handlers, write `res.status(…).json(…); return;` rather than `return res.json(…)`.
- If a topic is runtime-specific (e.g. the Node event loop), the Python section shows the equivalent mechanism (e.g. asyncio / ASGI) and says how it differs.

## Accuracy rules

- Prefer primary sources: RFCs (e.g. RFC 9110 HTTP semantics, RFC 6265 cookies, RFC 7519 JWT, RFC 9457 problem details), OWASP cheat sheets, official library docs.
- If you are not sure a fact or API signature is correct, leave it out.
- Numbers (TTLs, cost parameters, limits) must be defensible defaults. Say where they come from when it matters (e.g. OWASP's Argon2id recommendation).

## Formatting rules

- Plain, simple English. Short sentences. Define jargon the first time it appears.
- Valid Mermaid: wrap node labels that contain punctuation in quotes.
- Relative links only, and they must exist. Cross-module links use `../Module-NN-Name/file.md`.
- Target length is 1,800–3,500 words of prose, not counting code blocks (Module 02 chapters land at about 2,800–3,400 prose words, 3,800–4,700 in total).

## Checks before committing

```bash
python scripts/check_chapters.py Module-02-Core-Backend
```

The script fails if two chapters share an identical section body, if a chapter is missing a required section or a language example, or if a relative link is broken.

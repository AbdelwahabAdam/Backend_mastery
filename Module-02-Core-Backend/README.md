# Module 02: Core Backend Engineering

## Overview

This module covers what every backend engineer is expected to explain and build without notes: how HTTP really works, how to design an API contract, how users authenticate, how to structure application code, how to move slow work out of the request path, and how to see what a running service is doing.

Every chapter has code in **both Node.js/TypeScript (Express 5) and Python (FastAPI)** for the same scenario, so you can answer in whichever stack the interviewer uses and explain how the two runtimes differ.

## Learning objectives

After this module you can:

- Read and write raw HTTP, choose correct methods and status codes, and design a backward-compatible API.
- Explain how the Node event loop and Python asyncio schedule work, and spot code that blocks them.
- Build session-based and token-based authentication, including refresh-token rotation and safe password storage.
- Separate controllers, services and repositories, and wire them with dependency injection.
- Move slow work to background workers and scheduled jobs without losing or duplicating it.
- Instrument a service with structured logs, metrics and traces, and use them to debug a slow request.

## Prerequisites

- Comfortable in TypeScript **or** Python (you will read both).
- Basic SQL (`SELECT`, `INSERT`, transactions).
- Can run Docker containers for PostgreSQL and Redis.

## Chapters

### HTTP and API contracts
| # | Chapter | You should be able to… |
|---|---|---|
| 01 | [HTTP Fundamentals](01-HTTP-Fundamentals.md) | Explain safe vs idempotent methods, caching headers, HTTP/1.1 vs 2 vs 3 |
| 02 | [REST APIs](02-REST-APIs.md) | Model resources, choose PUT vs PATCH vs POST |
| 03 | [HTTP Status Codes](03-HTTP-Status-Codes.md) | Pick 401/403/404/409/422/429 correctly; return Problem Details |
| 04 | [API Design Principles](04-API-Design-Principles.md) | Design idempotent, paginated, evolvable contracts |

### Runtime
| # | Chapter | You should be able to… |
|---|---|---|
| 05 | [Node HTTP Server Concepts](05-Node-HTTP-Server-Concepts.md) | Configure timeouts and body limits; shut down gracefully |
| 06 | [Node Event Loop and Concurrency](06-Node-Event-Loop-and-Concurrency.md) | Predict callback order; find and fix event-loop blocking |

### Authentication
| # | Chapter | You should be able to… |
|---|---|---|
| 07 | [Sessions and Cookies](07-Sessions-and-Cookies.md) | Set secure cookie flags; prevent session fixation and CSRF |
| 08 | [JWT Authentication](08-JWT-Authentication.md) | Verify a JWT correctly; explain algorithm confusion and key rotation |
| 09 | [Refresh Tokens](09-Refresh-Tokens.md) | Implement rotation with reuse detection |
| 10 | [Password Hashing](10-Password-Hashing.md) | Store passwords with Argon2id and rehash on login |
| 11 | [Authentication Flow](11-Authentication-Flow.md) | Design registration, reset and MFA without account enumeration |

### Application architecture
| # | Chapter | You should be able to… |
|---|---|---|
| 12 | [MVC Architecture](12-MVC-Architecture.md) | Explain real MVC vs controller/service/repository layering |
| 13 | [Service Layer Pattern](13-Service-Layer-Pattern.md) | Put use cases and transaction boundaries in the right place |
| 14 | [Repository Pattern](14-Repository-Pattern.md) | Hide persistence behind an interface with a test fake |
| 15 | [Clean Architecture](15-Clean-Architecture.md) | Apply the dependency rule, and know when it is overkill |
| 16 | [Dependency Injection](16-Dependency-Injection.md) | Build a composition root; manage object lifetimes |

### Asynchronous work
| # | Chapter | You should be able to… |
|---|---|---|
| 17 | [Background Workers](17-Background-Workers.md) | Write idempotent jobs with retries and a dead-letter queue |
| 18 | [Cron Jobs](18-Cron-Jobs.md) | Run a schedule exactly once across many replicas |
| 19 | [Asynchronous Processing](19-Asynchronous-Processing.md) | Use 202 + status resources and the transactional outbox |

### Operations and code quality
| # | Chapter | You should be able to… |
|---|---|---|
| 20 | [Logging](20-Logging.md) | Emit structured, redacted logs with request IDs |
| 21 | [Error Handling](21-Error-Handling.md) | Separate operational from programmer errors; map errors to HTTP |
| 22 | [Monitoring](22-Monitoring.md) | Instrument RED metrics, define SLOs, write burn-rate alerts |
| 23 | [Observability Fundamentals](23-Observability-Fundamentals.md) | Trace a request across services with OpenTelemetry |
| 24 | [SOLID Principles](24-SOLID-Principles.md) | Give a correct backend example for each principle |
| 25 | [Clean Code](25-Clean-Code.md) | Refactor unclear code into readable, testable units |

## Study resources in this folder

- [pref.md](pref.md) — one-line definition and example per chapter, for quick revision.
- [module-summary.md](module-summary.md) — the whole module as one connected story, with decision trees and failure scenarios.
- [interview_questions.md](interview_questions.md) — mixed-topic questions with model answers.
- [tasks.md](tasks.md) — a build-it-yourself project that uses every chapter.

## Suggested plan (about 3 weeks, 1–2 hours a day)

| Week | Chapters | Build |
|---|---|---|
| 1 | 01–06 | Tasks 1–2 |
| 2 | 07–16 | Tasks 3–5 |
| 3 | 17–25 | Tasks 6–8, then the interview questions |

## Related modules

- [Module 03: Databases](../Module-03-Databases/README.md) — transactions, indexes and locking behind every service and repository.
- [Module 04: Operating Systems](../Module-04-Operating-Systems/README.md) — processes, threads and I/O beneath the event loop.
- [Module 07: Advanced Backend and System Design](../Module-07-Advanced-Backend-and-System-Design/README.md) — idempotency, retries, queues and rate limiting at scale.
- [Module 09: Testing and Code Quality](../Module-09-Testing-and-Code-Quality/README.md) — how to test everything built here.

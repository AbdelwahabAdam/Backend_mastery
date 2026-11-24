# Module 02 Practice Tasks: Build an Orders API

You will build one service step by step. Each task adds a feature that uses specific chapters.

**Choose your stack:** build it in **Node.js/TypeScript (Express 5)** or **Python (FastAPI)**. For the strongest interview preparation, build it in one stack, then port tasks 1, 3 and 6 to the other and write down what changed.

**Shared setup:** PostgreSQL and Redis via `docker compose`. Each task is done when every item in its **Done when** list passes as an automated test or a recorded `curl` session.

---

## Task 1 — HTTP contract for orders
**Chapters:** [01](01-HTTP-Fundamentals.md), [02](02-REST-APIs.md), [03](03-HTTP-Status-Codes.md), [04](04-API-Design-Principles.md) · **Level:** Beginner

Build `POST /orders`, `GET /orders/{id}`, `GET /orders?status=&cursor=&limit=`, `PATCH /orders/{id}` and `DELETE /orders/{id}`. Write the OpenAPI spec first.

**Done when**
- [ ] `POST` returns `201 Created` with a `Location` header.
- [ ] Invalid bodies return `422` (or `400`) as RFC 9457 Problem Details, with no stack trace.
- [ ] `GET /orders/{id}` returns an `ETag`; repeating it with `If-None-Match` returns `304` and no body.
- [ ] `PATCH` with a stale `If-Match` returns `412 Precondition Failed`.
- [ ] List pagination uses an opaque cursor; `limit` is capped at 100.
- [ ] Sending the same `Idempotency-Key` twice creates one order and returns the same response both times. A different body with the same key returns `422` (or `409`).

## Task 2 — Make the server production-safe
**Chapters:** [05](05-Node-HTTP-Server-Concepts.md), [06](06-Node-Event-Loop-and-Concurrency.md) · **Level:** Beginner

**Done when**
- [ ] Request bodies over 1 MB are rejected with `413`.
- [ ] Header and request timeouts are set. The keep-alive timeout is longer than your load balancer's idle timeout (document the value you assumed).
- [ ] On `SIGTERM` the server stops accepting connections, finishes in-flight requests (prove it with a slow endpoint), then exits within 25 s.
- [ ] Add `GET /reports/heavy`, which does 2 s of CPU work. Show with event-loop lag metrics (Node) or a concurrent-latency test (Python) that it hurts other requests. Then move the work to a worker thread/process and show the fix.

## Task 3 — Users and login
**Chapters:** [07](07-Sessions-and-Cookies.md), [10](10-Password-Hashing.md), [11](11-Authentication-Flow.md) · **Level:** Intermediate

**Done when**
- [ ] Passwords are stored as Argon2id hashes. Login rehashes the password if the stored parameters are outdated.
- [ ] Login and password-reset requests return the same response, with similar timing, for existing and unknown emails.
- [ ] Session cookies use `HttpOnly; Secure; SameSite=Lax` and a `__Host-` prefix. The session ID changes on login.
- [ ] Reset tokens are single-use, stored hashed, expire in 30 minutes, and invalidate all sessions when used.
- [ ] Login is rate-limited per account and per IP (returns `429` with `Retry-After`).

## Task 4 — Token auth for API clients
**Chapters:** [08](08-JWT-Authentication.md), [09](09-Refresh-Tokens.md) · **Level:** Intermediate

**Done when**
- [ ] Access tokens are RS256 JWTs with a 10-minute TTL, a `kid`, and `iss`/`aud` claims. Public keys are served at `/.well-known/jwks.json`.
- [ ] Tokens signed with `alg: none`, with HS256 using the public key, or with the wrong `aud` are all rejected (write a test for each).
- [ ] Refresh tokens are opaque, stored hashed, and rotated on each use. Reusing an old one revokes the whole token family.
- [ ] Users can only read their own orders: another user's order returns `404`.
- [ ] Key rotation drill: add a second key, switch signing, and show that tokens signed with the old key still verify until they expire.

## Task 5 — Layered architecture
**Chapters:** [12](12-MVC-Architecture.md)–[16](16-Dependency-Injection.md), [24](24-SOLID-Principles.md), [25](25-Clean-Code.md) · **Level:** Intermediate

**Done when**
- [ ] Controllers only parse input, call one service method, and map results to HTTP.
- [ ] `PlaceOrderService` owns the transaction: it reserves stock, creates the order and writes an outbox row atomically.
- [ ] `OrderRepository` has a Postgres implementation and an in-memory fake; service unit tests use the fake and need no database.
- [ ] All wiring happens in one composition root (Node) or through `Depends` (FastAPI). Tests swap dependencies without patching modules.
- [ ] A short ADR explains one abstraction you chose *not* to add, and why.

## Task 6 — Background work
**Chapters:** [17](17-Background-Workers.md), [18](18-Cron-Jobs.md), [19](19-Asynchronous-Processing.md) · **Level:** Advanced

**Done when**
- [ ] An outbox relay publishes `order.created` with `FOR UPDATE SKIP LOCKED`. Two relay instances never publish the same row at the same time.
- [ ] A worker (BullMQ or Celery) sends a confirmation email idempotently: delivering the same job twice sends one email.
- [ ] Failed jobs retry with exponential backoff and land in a dead-letter queue after 5 attempts.
- [ ] `POST /exports` returns `202` and a `Location: /exports/{id}` status resource that shows progress.
- [ ] A nightly cleanup cron runs on 3 replicas but executes once (lock-protected). Prove it with logs.
- [ ] Kill the worker in the middle of a job: the job is retried and the final state is correct.

## Task 7 — Make it observable
**Chapters:** [20](20-Logging.md)–[23](23-Observability-Fundamentals.md) · **Level:** Advanced

**Done when**
- [ ] Every log line is JSON with `request_id` and `trace_id`. Passwords, tokens and cookies are redacted (prove it with a test).
- [ ] `/metrics` exposes request-duration histograms by route and status, plus queue depth and job failures.
- [ ] `/healthz` (liveness) and `/readyz` (checks DB and Redis) behave differently when Postgres is down.
- [ ] OpenTelemetry traces cover HTTP → service → DB → queue publish → worker, viewable as one trace in Jaeger or Grafana Tempo.
- [ ] Write one SLO (e.g. 99.5% of `POST /orders` under 300 ms) and a burn-rate alert rule for it.

## Task 8 — Incident drill (capstone)
**Chapters:** all · **Level:** Advanced

Ask a friend to inject one fault without telling you which: add 800 ms latency to Postgres, fill Redis memory, break the JWKS URL, or add a blocking loop to one handler.

**Done when**
- [ ] You find the cause using only logs, metrics and traces, in under 20 minutes.
- [ ] You write a one-page postmortem: timeline, user impact, root cause, detection gap, and two follow-up actions.
- [ ] You can explain the incident aloud in 3 minutes, as you would in a behavioural interview.

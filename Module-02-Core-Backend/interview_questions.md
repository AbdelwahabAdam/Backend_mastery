# Module 02 Interview Questions

Each chapter ends with questions about its own topic. The questions here **cut across chapters**, the way real interviews do. Answer aloud first, then read the model answer.

**How to answer:** give the direct answer in one sentence, then the mechanism, then a trade-off or failure case. For Senior questions, end with how you would detect the problem in production.

Levels: **[Junior]** definitions and basic use · **[Mid]** trade-offs and debugging · **[Senior]** design under failure, and judgement.

---

## A. HTTP and API design

### 1. [Junior] What is the difference between a safe and an idempotent method? Is POST idempotent? Is PATCH?
*Chapters: [01](01-HTTP-Fundamentals.md), [02](02-REST-APIs.md)*

A **safe** method does not change server state (GET, HEAD, OPTIONS). An **idempotent** method has the same effect whether it is sent once or many times (all safe methods, plus PUT and DELETE). POST is neither, so two identical POSTs may create two orders. PATCH is not idempotent *by definition*: `{"op": "increment"}` changes state again each time. A JSON Merge Patch that only sets fields happens to be idempotent. This matters because clients, proxies and SDKs retry idempotent requests automatically, and not the others.

**Follow-up:** *"DELETE twice returns 204 then 404 — is that still idempotent?"* Yes. Idempotency is about server **state**, not the response code. After both calls the resource is gone.

### 2. [Mid] When do you return 401, 403 or 404?
*Chapters: [03](03-HTTP-Status-Codes.md), [08](08-JWT-Authentication.md)*

**401** means "I don't know who you are": the token is missing, invalid or expired. Send a `WWW-Authenticate` header so the client knows to (re)authenticate. **403** means "I know who you are, and you may not do this", for example a missing scope or role. **404** is the right answer when even confirming that the resource exists would leak information, such as another user's order ID. RFC 9110 allows a server to hide a forbidden resource behind 404. A useful rule: use 403 for *actions* the user can't perform, and 404 for *resources* they shouldn't know about.

### 3. [Mid] PUT vs PATCH — what does `{"nickname": null}` mean in each?
*Chapter: [02](02-REST-APIs.md)*

PUT replaces the whole representation. Any field you leave out is reset or rejected, and `null` sets the field to null. With JSON Merge Patch (RFC 7396), PATCH changes only the fields you send, and `null` **removes** that field. Omitting a field leaves it unchanged. That is why "omitted" and "null" must be told apart in validation: in Pydantic, use `model_dump(exclude_unset=True)`; in TypeScript, use the `"field" in body` check.

### 4. [Senior] Design a retry-safe `POST /orders`.
*Chapters: [04](04-API-Design-Principles.md), [13](13-Service-Layer-Pattern.md), [19](19-Asynchronous-Processing.md)*

The client sends an `Idempotency-Key` (a UUID) with each logical attempt and reuses it on retries.

1. Look up the key, scoped to the user. If a completed result exists, return it unchanged and mark it as a replay.
2. If a request with that key is still in progress, return **409**. If the key was used with a different body (compare a hash of the request), return **422**.
3. Otherwise, claim the key atomically (`SET NX` in Redis, or an insert with a unique constraint in Postgres). Run the use case, then store the response with a TTL (e.g. 24 h).

The database is the final guard: a unique constraint on `(user_id, idempotency_key)` in the orders table. A Redis entry that expires mid-retry then still cannot create a second order. Side effects such as emails go through the outbox, so they are emitted once with the order.

**Detection:** a metric for idempotent replays, and an alert on duplicate orders found by a reconciliation query.

### 5. [Mid] Offset pagination or cursor pagination?
*Chapters: [02](02-REST-APIs.md), [04](04-API-Design-Principles.md)*

Offset (`?page=500`) is simple and supports "jump to page N". But the database still reads and discards all the skipped rows, and rows shift when data is inserted, so users see duplicates or miss items. A cursor (`?after=<opaque token>`) encodes the last seen sort key, e.g. `(created_at, id)`. It uses an index seek, so every page costs about the same, and it stays stable while data changes. The cost: no random page jumps, and the sort order must be unique (add `id` as a tie-breaker). Use cursors for public APIs and feeds. Offset is fine for small admin tables.

### 6. [Mid] What do ETags give you besides caching?
*Chapter: [01](01-HTTP-Fundamentals.md)*

For reads, `If-None-Match` lets the server return `304 Not Modified` with no body, saving bandwidth. For writes, `If-Match` gives **optimistic concurrency**. The client sends the ETag it read. If someone else changed the resource since then, the server returns `412 Precondition Failed` instead of silently overwriting their change (the "lost update" problem). An ETag built from a version column makes both cheap.

### 7. [Senior] You must rename a field in a public API that 40 clients use. How?
*Chapter: [04](04-API-Design-Principles.md)*

Never rename in place: that breaks every client at once.

1. **Expand:** add the new field and keep writing both.
2. **Communicate:** mark the old field deprecated in the OpenAPI spec and send `Deprecation`/`Sunset` headers.
3. **Measure:** log which clients still read or send the old field.
4. **Contract:** remove it only after usage reaches zero or the published sunset date passes.

A new API version is the fallback when many changes must land together. It is costly, because you run two contracts. Contract tests or schema-diff checks in CI stop accidental breaking changes.

---

## B. Runtime: Node.js and Python

### 8. [Junior] "Node.js is single-threaded." Is that true?
*Chapter: [06](06-Node-Event-Loop-and-Concurrency.md)*

Partly. Your JavaScript runs on one thread: the event loop. Network I/O uses non-blocking OS facilities (epoll, kqueue, IOCP), so thousands of sockets can wait without threads. Some operations run on the **libuv thread pool** (4 threads by default): file system calls, `dns.lookup`, some `crypto` functions such as `pbkdf2` and `scrypt`, and `zlib`. The consequence: CPU-heavy JavaScript blocks every request in that process, and many slow `fs`/`crypto` calls can queue up behind the four pool threads.

### 9. [Mid] In what order do these print (CommonJS)?

```js
setTimeout(() => console.log("timeout"), 0);
setImmediate(() => console.log("immediate"));
Promise.resolve().then(() => console.log("promise"));
process.nextTick(() => console.log("nextTick"));
console.log("sync");
```
*Chapter: [06](06-Node-Event-Loop-and-Concurrency.md)*

`sync`, `nextTick`, `promise`, then `timeout` and `immediate` in **either order**. Synchronous code runs first. Then the `nextTick` queue drains, then Promise microtasks. Whether `timeout` or `immediate` comes first from the main module depends on how fast the loop starts, so it is not deterministic. Inside an I/O callback, `setImmediate` always runs before a 0 ms timer, because the check phase comes right after poll. In an ES module, `promise` can print before `nextTick`, because module code itself runs inside a microtask.

### 10. [Mid] Latency rose on *every* endpoint of a Node service, but the DB looks healthy. What do you check?
*Chapters: [06](06-Node-Event-Loop-and-Concurrency.md), [22](22-Monitoring.md)*

Rising latency on every endpoint of one process points to the **event loop**, not a dependency. Check event-loop delay (`perf_hooks.monitorEventLoopDelay`, or the default `prom-client` metrics), then take a CPU profile (`--cpu-prof` or clinic.js) during the spike. Typical causes:
- a large `JSON.parse`/`JSON.stringify`
- a sync crypto or zlib call
- a catastrophic-backtracking regex
- sorting a huge array in a request handler

Fix it by moving CPU work to `worker_threads` or a job queue, capping input sizes, or streaming instead of buffering.

### 11. [Mid] In FastAPI, what is the difference between `def` and `async def` endpoints?
*Chapters: [06](06-Node-Event-Loop-and-Concurrency.md), [08](08-JWT-Authentication.md)*

`async def` endpoints run on the event loop. Any blocking call inside them (`requests.get`, `time.sleep`, a sync DB driver) freezes **all** requests on that worker. Plain `def` endpoints and dependencies run in a thread pool, so blocking calls are fine there, up to the pool's size. Rule: use `async def` only with async libraries (`httpx.AsyncClient`, `asyncpg`). Otherwise use `def`, or wrap the blocking call in `await asyncio.to_thread(...)`. CPU-bound work needs processes, because of the GIL.

### 12. [Senior] Clients see random 502s from the load balancer, mostly during low traffic and during deploys. Why?
*Chapters: [05](05-Node-HTTP-Server-Concepts.md), [01](01-HTTP-Fundamentals.md)*

There are two classic causes.

1. **Keep-alive race.** Node's default `keepAliveTimeout` is 5 s, and an AWS ALB keeps idle connections for 60 s. The app closes an idle connection just as the load balancer reuses it for a new request, and the load balancer returns a 502. Fix: set the app's keep-alive timeout *longer* than the load balancer's (e.g. 65 s).
2. **Hard shutdown during deploys.** The process exits on `SIGTERM` while requests are still in flight. Fix:
   - on `SIGTERM`, fail readiness
   - wait for the load balancer to deregister the instance
   - call `server.close()` and let in-flight requests finish
   - force-exit before the orchestrator's grace period ends

Uvicorn has the same issue with `--timeout-keep-alive`.

---

## C. Authentication

### 13. [Junior] Sessions or JWTs?
*Chapters: [07](07-Sessions-and-Cookies.md), [08](08-JWT-Authentication.md)*

A session stores state on the server, and the browser holds only an opaque ID in a cookie. It is easy to revoke and small on the wire, but every request needs a store lookup. A JWT carries signed claims, so any service with the public key can verify it locally. The cost is that it cannot be revoked before `exp` without adding state. For a single web app, sessions are simpler and safer. For many services or third-party API clients, use short-lived JWT access tokens plus revocable refresh tokens.

### 14. [Mid] Which cookie flags do you set on a session cookie, and do they stop CSRF?
*Chapter: [07](07-Sessions-and-Cookies.md)*

- `HttpOnly`: JavaScript cannot read the cookie.
- `Secure`: the cookie is sent over HTTPS only.
- `SameSite=Lax`: the cookie is not sent on cross-site subrequests, or on cross-site POSTs.
- A `__Host-` prefix: no `Domain` attribute, `Path=/`, and `Secure` are required, which blocks subdomain overrides.

`SameSite=Lax` stops most CSRF, but not all of it. It does not cover same-site attacks from a compromised subdomain, or state-changing GET handlers. So state-changing requests also get a CSRF token (synchronizer or double-submit) or a check of the `Origin` / `Sec-Fetch-Site` header.

### 15. [Mid] Why not store passwords with SHA-256 and a salt?
*Chapter: [10](10-Password-Hashing.md)*

SHA-256 is designed to be fast. A GPU computes billions of hashes per second, so a leaked table of salted SHA-256 hashes falls to dictionary attacks quickly. Password hashing needs a deliberately **slow and memory-hard** function. Argon2id is the first choice; OWASP's baseline is 19 MiB of memory, 2 iterations and parallelism 1. Use bcrypt (cost ≥ 10, and inputs are cut off at 72 bytes) only when Argon2 isn't available. Store the parameters inside the hash string, and rehash on successful login when the parameters are raised.

### 16. [Senior] Explain refresh-token rotation with reuse detection. What happens when two browser tabs refresh at the same time?
*Chapter: [09](09-Refresh-Tokens.md)*

Each refresh returns a new refresh token and marks the old one used. All tokens from one login share a **family ID**. If a token that was already used shows up again, someone has a copy: either the attacker or the real user, and you cannot tell which. So revoke the whole family, which forces a fresh login.

Two tabs refreshing together can trip this check by accident. The usual mitigation is a short grace window (a few seconds): within it, a reuse gets a retryable 409 or the same new token, instead of a revocation. Also store refresh tokens **hashed**, so a database leak does not hand out live tokens.

### 17. [Mid] Design a password-reset flow.
*Chapters: [11](11-Authentication-Flow.md), [10](10-Password-Hashing.md)*

1. `POST /password-reset` always returns the same response (e.g. 202 "if the account exists, we sent an email") with similar timing, so attackers cannot enumerate accounts. Do the per-user work in a background job.
2. The token is random (≥ 128 bits), stored **hashed**, single-use, and expires in ~30 minutes. Build the link from a configured base URL, never from the `Host` header.
3. On confirm, validate the token, hash the new password, mark the token used, revoke all sessions and refresh tokens, and notify the user.
4. Do not log the user in automatically.
5. Rate-limit both endpoints.

### 18. [Senior] An account is compromised. How do you log the attacker out everywhere *right now*?
*Chapters: [07](07-Sessions-and-Cookies.md), [08](08-JWT-Authentication.md), [09](09-Refresh-Tokens.md)*

- **Sessions:** delete every server-side session for the user, which needs a per-user index in the session store.
- **Refresh tokens:** revoke every family.
- **JWT access tokens:** still valid until `exp`. Set a per-user `tokens_valid_after = now()`, and have verifiers reject tokens whose `iat` is older. Cache that value briefly so the check stays cheap.
- **Signing key leaked** (not just the account): rotate the key and remove the old public key from the JWKS. That logs out *everyone*, which is acceptable for a key compromise.

Finally, force a password reset and review the audit logs for what the attacker accessed.

---

## D. Architecture and design

### 19. [Junior] Our app has controllers, services and repositories. Is that MVC?
*Chapter: [12](12-MVC-Architecture.md)*

Not exactly. MVC (Model–View–Controller) comes from Smalltalk UIs and server-rendered web frameworks such as Rails and Django: the controller handles input, the model holds data and behaviour, and the view renders output. Controller → service → repository is a **layered architecture**; only the controller is an MVC role. In a JSON API, the response schema or serializer plays the "view" role. The distinction matters in interviews because "MVC" is often used loosely, and naming the layers correctly shows you understand where each responsibility lives.

### 20. [Mid] Where does the database transaction belong, and should it include the call to the payment provider?
*Chapters: [13](13-Service-Layer-Pattern.md), [19](19-Asynchronous-Processing.md)*

The **service** (use case) owns the transaction, because it knows which writes must succeed or fail together. Controllers know nothing about transactions, and repositories take part in one rather than starting their own. The payment call must stay **outside** the transaction. Holding row locks and a pooled connection during a 2-second HTTP call reduces throughput and causes lock waits. And a rollback cannot undo a charge anyway. Instead: create the order as `pending` and commit, charge with an idempotency key, then record the result in a second transaction. A reconciliation job handles crashes in between.

### 21. [Mid] Isn't an ORM already a repository?
*Chapter: [14](14-Repository-Pattern.md)*

An ORM maps tables to objects and gives you a query API. That is a general-purpose data-access tool. A repository is a narrow, domain-shaped interface: `orders.findOpenByCustomer(id)` rather than a query builder passed around the codebase. Wrapping an ORM in a repository is worthwhile when you want the business logic to be testable with an in-memory fake, and to keep query details in one place. It is not worthwhile for thin CRUD pass-through methods, which add a layer with no protection.

### 22. [Senior] When is Clean Architecture over-engineering?
*Chapter: [15](15-Clean-Architecture.md)*

When the service is mostly CRUD with few business rules, has one database it will never swap, and has a small team. Then ports, adapters, DTO mapping at every boundary, and one use-case class per endpoint add files and indirection without protecting anything. It pays off when the business rules are complex and long-lived, or when external dependencies really vary (payment providers, legacy systems), or when the core must be testable without infrastructure. A pragmatic middle ground: keep the dependency rule only at the boundaries that change (e.g. a `PaymentGateway` port), and let simple reads query the database directly.

### 23. [Mid] Give a backend example of the Liskov Substitution Principle being violated.
*Chapter: [24](24-SOLID-Principles.md)*

LSP says code written against a base type must keep working with any subtype: preconditions can't get stricter, postconditions can't get weaker. Example: a `PaymentProvider` interface promises `refund(amount)` for any amount up to the captured total. A `VoucherProvider` subclass throws on partial refunds. Every caller that relied on partial refunds now breaks, even though the code compiles. The fix is to model the capability honestly, e.g. a separate `PartialRefundable` interface, or a result type that says "unsupported". Note: "we can swap MySQL for Postgres" is mostly about **dependency inversion**. LSP is what makes that swap *safe*.

### 24. [Mid] What is the difference between dependency injection, dependency inversion and an IoC container?
*Chapter: [16](16-Dependency-Injection.md)*

**Dependency inversion** is a design principle: business code depends on abstractions it owns, and infrastructure implements them. **Dependency injection** is a technique: an object receives its collaborators (usually through its constructor) instead of creating them. An **IoC container** is a tool that automates the wiring (NestJS, tsyringe, InversifyJS). FastAPI's `Depends` is a lightweight form of one. You can do DI without a container, using a hand-written composition root, and that is often clearer in small services.

### 25. [Mid] What goes wrong when a singleton depends on something request-scoped?
*Chapter: [16](16-Dependency-Injection.md)*

The singleton is created once and keeps the *first* request's object. Every later request then uses a stale or closed database session, or worse, another user's identity or transaction. Symptoms include "session is closed" errors under load and data appearing for the wrong user. The fix is to make the consumer request-scoped too, or to inject a factory or provider the singleton calls per request. NestJS makes request scope propagate up the dependency chain for this reason.

---

## E. Asynchronous work

### 26. [Mid] How do you decide whether work belongs in a queue?
*Chapters: [17](17-Background-Workers.md), [19](19-Asynchronous-Processing.md)*

Queue the work when the user does not need the result to continue, when it is slow or uses an unreliable third party (email, PDFs, webhooks), when it needs retries, or when bursts must be smoothed out. Keep it synchronous when the response depends on it (e.g. checking stock), when it is fast and local, or when the extra moving parts are not justified. A queue brings duplicate delivery, delayed results and monitoring work. Answer with the trade-off, not "always use a queue".

### 27. [Senior] What is the dual-write problem, and how does the outbox pattern solve it?
*Chapter: [19](19-Asynchronous-Processing.md)*

Writing to the database and publishing to a broker are two separate systems, so no single transaction covers both. If you commit and then crash before publishing, the event is lost. If you publish and then the commit fails, consumers act on something that never happened. The **transactional outbox** writes the event as a row in the same database transaction as the business change. A relay then reads unsent rows (`FOR UPDATE SKIP LOCKED`, so several relays can run), publishes them, and marks them sent. Delivery becomes **at-least-once**, so consumers must deduplicate by event ID (an "inbox" table, or idempotent handlers).

### 28. [Mid] A job takes longer than the queue's visibility timeout (or BullMQ lock). What happens?
*Chapter: [17](17-Background-Workers.md)*

The broker assumes the worker died and makes the job visible again. A second worker picks it up while the first is still running, so the work runs twice in parallel. To prevent it:
- make handlers idempotent (check "already sent", and pass idempotency keys to third parties)
- set the timeout well above the p99 job duration, or extend it while the job runs
- split long jobs into smaller steps

Retries in general also need backoff and a dead-letter queue, so poison messages don't loop forever.

### 29. [Mid] Your nightly billing cron runs on 5 replicas. What happens and how do you fix it?
*Chapter: [18](18-Cron-Jobs.md)*

It runs 5 times. The options are:
- run the scheduler in a single place (a Kubernetes CronJob with `concurrencyPolicy: Forbid`, or a cloud scheduler)
- take a distributed lock (a Postgres advisory lock, or Redis `SET NX PX` with a token-checked release)
- elect a leader

A lock prevents **overlapping** runs, but not a **second** run after the first finishes. So also record a run key such as `billing:2026-11-24`, and give each invoice a unique key, making the job idempotent. Schedule in UTC to avoid DST skipping or doubling a run, and add a heartbeat alert ("dead man's switch") for runs that never happen.

---

## F. Operations

### 30. [Junior] What are operational errors and programmer errors?
*Chapter: [21](21-Error-Handling.md)*

**Operational errors** are expected runtime failures: invalid input, not found, a conflict, a timeout, a dependency being down. You handle them by mapping them to a proper response (400/404/409/503) or retrying. **Programmer errors** are bugs: reading a property of `undefined`, a wrong type, a broken invariant. You cannot handle them meaningfully, so return a generic 500, log with full detail, and alert. In Node, an `uncaughtException` leaves the process in an unknown state, so log it and exit, and let the supervisor restart the process.

### 31. [Mid] How do you get a request ID into every log line without passing it through every function?
*Chapter: [20](20-Logging.md)*

Use per-request context storage. In Node, `AsyncLocalStorage` keeps a store across `await` and callbacks. Middleware starts it with the request ID (taken from an incoming header, or newly generated), and the logger reads it. In Python, `contextvars` does the same; asyncio copies the context into each task, and structlog's `merge_contextvars` adds it to every log line. Also return the ID in a response header, and forward it (or the W3C `traceparent`) on outgoing calls so logs join up across services.

### 32. [Mid] Why are averages misleading for latency, and why use histograms rather than summaries?
*Chapter: [22](22-Monitoring.md)*

An average hides the tail. 99 requests at 50 ms and one at 5 s average about 100 ms, but that 1% of users wait 5 s. With many backend calls per page view, most users hit at least one slow call. So track p95/p99. In Prometheus, **histograms** expose bucket counters that can be summed across instances before computing a quantile (`histogram_quantile(0.99, sum by (le) (rate(..._bucket[5m])))`). **Summaries** compute quantiles inside each process, and quantiles cannot be averaged across instances.

### 33. [Senior] p99 latency of a FastAPI (or Express) service doubled after a deploy. Walk through your investigation.
*Chapters: [22](22-Monitoring.md), [23](23-Observability-Fundamentals.md), [20](20-Logging.md), [06](06-Node-Event-Loop-and-Concurrency.md)*

1. **Scope:** all routes or one? All instances or one? Did it start exactly at the deploy? Compare metrics by version label.
2. **Saturation:** CPU, event-loop lag or thread-pool queue, DB pool wait time, memory/GC.
3. **Traces:** open slow traces from after the deploy and compare their span breakdown with traces from before. Look for a new span, a slower DB query, or N+1 patterns.
4. **Evidence:** run `EXPLAIN ANALYZE` on the suspect query, and take a CPU profile if spans don't account for the time.
5. **Mitigate first:** if users are affected, roll back, then find the root cause.

Typical culprits: a missing index after a migration, a sync call added to an async path, a smaller connection pool, or a new per-request external call.

### 34. [Mid] Liveness vs readiness — what goes wrong if liveness checks the database?
*Chapter: [22](22-Monitoring.md)*

**Liveness** answers "is this process stuck and in need of a restart?" It should check only the process itself. **Readiness** answers "should this instance receive traffic now?" and can check that critical dependencies are reachable. If liveness checks the database, a database outage makes the orchestrator restart *every* pod at once. That does nothing for the database, and it adds a cold-start storm when the database returns. During shutdown, readiness should fail first so traffic drains away.

### 35. [Senior] Define an SLO for checkout and alert on it without paging on noise.
*Chapter: [22](22-Monitoring.md)*

- **SLI:** the proportion of `POST /checkout` requests that succeed in under 500 ms.
- **SLO:** 99.9% over 30 days. That gives an **error budget** of 0.1%, about 43 minutes of full outage a month.
- **Alerting:** alert on **burn rate**, not on single errors. A common setup from the Google SRE workbook:
  - page when the budget burns 14.4× faster than allowed over both 1 hour and 5 minutes (2% of the monthly budget used in an hour)
  - open a ticket at 6× over 6 hours

The short window stops alerts from lingering after recovery. The approach alerts on user-facing symptoms, not on causes like CPU usage.

---

## G. Putting it together

### 36. [Senior] Walk through everything that happens for `POST /orders`, from the client to the email.
*Chapters: all*

1. The client sends `POST /orders` over HTTPS, with a bearer token and an `Idempotency-Key`.
2. The load balancer forwards it on a kept-alive connection.
3. Middleware assigns a request ID and starts the trace span.
4. Auth middleware verifies the JWT (algorithm allow-list, `kid`, `exp`, `iss`, `aud`).
5. The idempotency layer checks or claims the key.
6. The controller validates the body (zod or Pydantic) and calls `PlaceOrder`.
7. In one transaction, the service reserves stock with an atomic `UPDATE … WHERE available >= qty`, inserts the order, and inserts an outbox row.
8. The controller returns `201` with `Location`.
9. The outbox relay publishes `order.created`, and a worker sends the email idempotently.
10. Logs carry the request and trace IDs, metrics record duration by route and status, and the trace links the HTTP span, DB spans, the publish, and the worker span.

Be ready to zoom into any step and say what happens when it fails.

### 37. [Senior] You know both Node.js and Python. What actually changes between them in backend work?
*Chapters: [05](05-Node-HTTP-Server-Concepts.md), [06](06-Node-Event-Loop-and-Concurrency.md), [20](20-Logging.md)*

- **Concurrency model.** Node runs all JavaScript on one event loop, and everything is async by default. Python uses asyncio inside an ASGI server, but many libraries are sync. FastAPI runs `def` code in a thread pool, and the GIL limits CPU parallelism, so CPU work needs processes.
- **Scaling out.** Node typically runs one process per core, or uses `cluster`. Python runs multiple Uvicorn or Gunicorn workers.
- **Request context.** `AsyncLocalStorage` in Node, `contextvars` in Python.
- **Background jobs.** BullMQ in Node, Celery, RQ or arq in Python.
- **Validation.** zod plus TypeScript types in Node, Pydantic in Python (which validates at runtime and generates the OpenAPI spec).

The things that don't change: HTTP semantics, auth security, transactions, idempotency, and observability practice. That is why interviewers mostly test those.

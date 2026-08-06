# Module 02 Core Backend — Quick Reference

Use this for fast revision. Every topic has its own definition, a plain-English explanation, and a small backend example.

## HTTP and API Contracts

### [HTTP Fundamentals](01-HTTP-Fundamentals.md)
**Definition:** HTTP is the request/response protocol used by clients and servers to exchange representations.
**Simple explanation:** It is the conversation format between a browser/app and an API.
**Small example:** `GET /products/42` sends a method, path, and headers; the API returns `200` plus JSON.

### [REST APIs](02-REST-APIs.md)
**Definition:** REST is a resource-oriented API design style built on HTTP semantics.
**Simple explanation:** Name things (`/orders`), then use verbs (`POST`, `GET`, `DELETE`) consistently.
**Small example:** `POST /orders` creates an order; `GET /orders/123` retrieves that resource.

### [HTTP Status Codes](03-HTTP-Status-Codes.md)
**Definition:** Status codes are standard outcome signals in an HTTP response.
**Simple explanation:** They tell a client whether to continue, fix its request, authenticate, or retry later.
**Small example:** Return `404` for an absent order, not `500`; `500` means the server failed unexpectedly.

### [API Design Principles](04-API-Design-Principles.md)
**Definition:** API design principles keep contracts predictable, evolvable, safe, and easy to consume.
**Simple explanation:** An API is a product for other developers; consistency lowers their bugs.
**Small example:** Add optional `currency` to a response instead of renaming/removing an existing field.

### [Node HTTP Server Concepts](05-Node-HTTP-Server-Concepts.md)
**Definition:** A Node HTTP server accepts sockets, parses requests, streams bodies, and writes responses.
**Simple explanation:** Node handles many waiting connections efficiently, but each socket and buffer still costs resources.
**Small example:** Set keep-alive and request timeouts so abandoned clients cannot hold connections forever.

### [Node Event Loop and Concurrency](06-Node-Event-Loop-and-Concurrency.md)
**Definition:** The event loop runs JavaScript callbacks while non-blocking I/O waits happen outside the main thread.
**Simple explanation:** One slow synchronous task can pause every request sharing that event loop.
**Small example:** Send CPU-heavy PDF generation to a worker process instead of calculating it inside a request handler.

## Authentication

### [Sessions and Cookies](07-Sessions-and-Cookies.md)
**Definition:** A session stores login state server-side; a cookie carries the session identifier in the browser.
**Simple explanation:** The browser holds a ticket, while the server keeps the real session record.
**Small example:** Set `HttpOnly; Secure; SameSite=Lax` on a session cookie and rotate the ID after login.

### [JWT Authentication](08-JWT-Authentication.md)
**Definition:** A JWT is a signed token containing claims that a server can verify without a session lookup.
**Simple explanation:** It is a tamper-evident badge, not a secret envelope—its payload is readable.
**Small example:** Verify signature, issuer, audience, and expiration before trusting `sub` or roles.

### [Refresh Tokens](09-Refresh-Tokens.md)
**Definition:** A refresh token renews short-lived access tokens and represents a long-lived login session.
**Simple explanation:** The short badge expires quickly; the protected refresh token asks for a new badge.
**Small example:** Rotate refresh tokens on use and revoke the whole token family if an old token appears again.

### [Password Hashing](10-Password-Hashing.md)
**Definition:** Password hashing uses a slow, salted one-way algorithm to protect credentials at rest.
**Simple explanation:** Store a difficult-to-guess fingerprint, never the password itself.
**Small example:** Use Argon2id and rehash a valid password when stronger parameters become available.

### [Authentication Flow](11-Authentication-Flow.md)
**Definition:** An authentication flow covers registration, verification, login, authorization, logout, and recovery.
**Simple explanation:** It is the complete lifecycle of proving who a user is and what they may do.
**Small example:** A reset link is single-use, time-limited, stored hashed, and invalidated after password change.

## Architecture and Design

### [MVC Architecture](12-MVC-Architecture.md)
**Definition:** MVC separates input handling, application data/behavior, and presentation concerns.
**Simple explanation:** A controller receives a request; it should not become the whole business system.
**Small example:** The controller validates JSON, calls a service, then maps its outcome to an HTTP response.

### [Service Layer Pattern](13-Service-Layer-Pattern.md)
**Definition:** A service layer contains application use cases and coordinates domain rules, transactions, and dependencies.
**Simple explanation:** It is where “place an order” lives, rather than inside a route or database model.
**Small example:** `PlaceOrderService` authorizes the user, reserves stock, writes the order, and emits an outbox event.

### [Repository Pattern](14-Repository-Pattern.md)
**Definition:** A repository gives domain code a collection-like interface over persistence.
**Simple explanation:** Business code asks for an order; it does not need to know the SQL/ORM mechanics.
**Small example:** `orders.get(order_id)` hides a parameterized query and maps a row into a domain object.

### [Clean Architecture](15-Clean-Architecture.md)
**Definition:** Clean Architecture keeps business policy independent from frameworks, databases, and delivery mechanisms.
**Simple explanation:** Important rules live in the center; replaceable technical details stay at the edge.
**Small example:** A payment use case depends on a `PaymentGateway` port, not directly on a Stripe SDK.

### [Dependency Injection](16-Dependency-Injection.md)
**Definition:** Dependency injection supplies collaborators from the outside instead of constructing them internally.
**Simple explanation:** A service receives the database client it needs instead of secretly creating one.
**Small example:** The composition root injects a production repository; a test injects a fake repository.

## Async Work

### [Background Workers](17-Background-Workers.md)
**Definition:** Background workers consume queued work outside the request/response path.
**Simple explanation:** Accept the order quickly; let another process send the slow email.
**Small example:** A worker acknowledges a queue message only after its idempotent database update succeeds.

### [Cron Jobs](18-Cron-Jobs.md)
**Definition:** A cron job runs scheduled work at defined times or intervals.
**Simple explanation:** It is an alarm clock for the backend, but replicas can hear the same alarm.
**Small example:** Use a leader lock or idempotent job key so nightly billing reconciliation runs once across a fleet.

### [Asynchronous Processing](19-Asynchronous-Processing.md)
**Definition:** Asynchronous processing decouples acceptance of work from eventual completion.
**Simple explanation:** The API says “accepted”; a worker finishes the work later.
**Small example:** Return `202 Accepted` for a large export and expose `/exports/{id}` until the file is ready.

## Reliability and Code Quality

### [Logging](20-Logging.md)
**Definition:** Logging records structured events that explain what the system did.
**Simple explanation:** Logs are the incident timeline, not a place to print every object.
**Small example:** Log `order_created` with order ID, request ID, duration, and outcome—never card data or tokens.

### [Error Handling](21-Error-Handling.md)
**Definition:** Error handling classifies failures and translates them into safe, stable contracts.
**Simple explanation:** Clients need useful outcomes; engineers need diagnostic detail without leaked internals.
**Small example:** Convert a unique-constraint violation into `409 Conflict`, while logging the original database exception internally.

### [Monitoring](22-Monitoring.md)
**Definition:** Monitoring uses measurements and alerts to detect user-impacting degradation.
**Simple explanation:** It tells the team whether the service is keeping its promise to users.
**Small example:** Alert when checkout SLO error-budget burn and database pool saturation rise together.

### [Observability Fundamentals](23-Observability-Fundamentals.md)
**Definition:** Observability combines logs, metrics, and traces to investigate unknown production behavior.
**Simple explanation:** It lets you ask “why is this request slow?” without shipping new debugging code.
**Small example:** A trace shows 900 ms spent waiting on Redis; metrics reveal it happens only in one region.

### [SOLID Principles](24-SOLID-Principles.md)
**Definition:** SOLID is a set of design heuristics for cohesive, replaceable, and testable code.
**Simple explanation:** It helps spot classes that do too much or depend too directly on unstable details.
**Small example:** Split `OrderService` from `EmailSender` so changing email delivery does not change ordering rules.

### [Clean Code](25-Clean-Code.md)
**Definition:** Clean code makes intent, errors, and future changes easy for humans to understand.
**Simple explanation:** Code is read far more often than written; clear names and small cohesive units reduce mistakes.
**Small example:** Rename `process(x)` to `reserve_inventory(order)` and return a typed outcome instead of a magic boolean.

## How to revise

1. Read each `In short` line aloud.
2. Explain the example without looking.
3. Open the linked chapter when you cannot state the invariant, failure mode, or trade-off.

## Related module resources

- [Module overview](README.md)
- [Interview questions](interview_questions.md)
- [Practical tasks](tasks.md)

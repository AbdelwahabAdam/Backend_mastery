# Tasks

Complete tasks in order. Treat every checklist item as a design-review question, not a box-ticking exercise.

## 1. Contract-first health and resource endpoint

**Level:** Beginner

**Objective**  
Implement a small API with explicit request/response schemas, validation, stable errors, and containerized local execution.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
An internal platform team needs trustworthy health and ownership endpoints before deploying new services.

## 2. Traceable repository operation

**Level:** Beginner

**Objective**  
Create one bounded persistence operation with parameter binding, a timeout, typed outcomes, and structured logs.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
Support engineers need to answer who changed a record and why a request failed.

## 3. Idempotent command

**Level:** Intermediate

**Objective**  
Implement a retry-safe write with persistent idempotency state and conflict handling.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
Mobile clients and payment gateways retry when networks are unreliable.

## 4. Observability baseline

**Level:** Intermediate

**Objective**  
Instrument traffic, errors, duration, and dependency latency; create an SLO and a runbook.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
The on-call team needs actionable alerts instead of raw exception noise.

## 5. Asynchronous reliable workflow

**Level:** Advanced

**Objective**  
Add an outbox relay and worker with retries, dead-letter handling, idempotent consumption, and reconciliation.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
A billing workflow must not lose a post-commit side effect.

## 6. Performance investigation

**Level:** Advanced

**Objective**  
Use production-like data to identify and correct a measured latency bottleneck; document before/after evidence.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
A high-traffic endpoint fails its p99 latency SLO.

## 7. Safe deployment evolution

**Level:** Production

**Objective**  
Plan a backward-compatible change with feature flag, migration or API contract strategy, telemetry, canary, and rollback.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
Two independently deployed clients must remain compatible during a release.

## 8. Module capstone

**Level:** Production

**Objective**  
Build the persistence layer for a multi-tenant order and fulfillment platform. It must include normalized PostgreSQL schema, safe migrations, strategic indexes validated by EXPLAIN ANALYZE, cursor pagination, transaction/retry handling, an outbox, analytics materialized view, and a deliberately modeled MongoDB read model.

**Requirements**  
- Define the public contract, validation rules, error shape, and ownership boundary.
- Use configuration through environment variables, parameterized persistence, structured logging, and health checks.
- Write unit tests plus at least one integration test for a failure path.

**Constraints**  
- No credentials, tokens, or personal data in source control or logs.
- Every network/database operation has a timeout.
- Retries must be bounded and must not duplicate externally visible effects.

**Expected Output**  
A runnable Docker-based service, README, API or data contract, test report, dashboard/metric definitions, and a short architecture decision record.

**Hints**  
Start from one invariant and a single vertical slice. Add observability before optimizing. Inject a dependency failure before declaring the design complete.

**Stretch Goals**  
Add load testing, a migration plan, a feature flag, distributed tracing, and an incident runbook.

**Evaluation Checklist**  
- [ ] Correctness holds under retry and restart.
- [ ] Input validation and authorization are explicit.
- [ ] Failure behavior is stable and observable.
- [ ] Resource usage is bounded.
- [ ] Documentation explains trade-offs.

**Real-world Context**  
This simulates a service reviewed by security, database reliability, platform, and product teams.

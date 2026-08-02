# Tasks

Complete in sequence. A task is complete only when its contract, limits, failure behavior, telemetry, and recovery plan are documented and tested.

## 1. URL shortener

**Level:** Beginner

**Objective**  
Design and build an idempotent URL shortener with PostgreSQL, Redis cache, FastAPI, Docker, and capacity estimates.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
A marketing platform needs low-latency redirects.

## 2. Token bucket limiter

**Level:** Beginner

**Objective**  
Build a tested per-tenant rate limiter, compare in-process and Redis variants, and expose safe metrics.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
A public API needs fair burst control.

## 3. Notification worker

**Level:** Intermediate

**Objective**  
Build an outbox-backed Kafka/RabbitMQ-style worker with retries, DLQ, and idempotent delivery.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
Users expect a notification once despite retries and restarts.

## 4. Distributed cache

**Level:** Intermediate

**Objective**  
Implement cache-aside reads, TTL/version invalidation, stampede control, memory budget, and observability.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
A read-heavy API is approaching database capacity.

## 5. Payment workflow

**Level:** Advanced

**Objective**  
Design a payment API with idempotency, ledger constraints, asynchronous provider events, SAGA/reconciliation, and audit trail.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
Financial effects must remain correct during network and provider failures.

## 6. Chat and file platform

**Level:** Advanced

**Objective**  
Design WebSocket chat plus direct object-storage uploads, signed URLs, fan-out, retention, and moderation workflow.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
Users upload large files and expect near-real-time messages.

## 7. Multi-AZ deployment

**Level:** Production

**Objective**  
Implement progressive deployment, backward-compatible migration, Multi-AZ data plan, canary SLO gate, rollback, and restore drill.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
A service must evolve without downtime.

## 8. System-design capstone

**Level:** Production

**Objective**  
Deliver an AWS-primary multi-tenant platform combining URL shortening, rate limiting, caching, notification workers, payment/idempotency workflow, file uploads, API gateway, observability, capacity/cost model, Multi-AZ DR, Kubernetes deployment, Terraform plan, and twelve-case-study design portfolio.

**Requirements**  
- Define functional/non-functional requirements, APIs, data ownership, and failure outcomes.
- Include automated tests plus fault injection/load evidence.
- Provide Docker deployment, structured logs, metrics/traces, and an architecture diagram.

**Constraints**  
- Bound timeouts, retries, queues, payloads, connection pools, and cost.
- Encrypt/authenticate/authorize every relevant boundary; never log secrets.
- State consistency, availability, RPO/RTO, and rollback assumptions.

**Expected Output**  
Source, README, diagrams, tests, capacity estimate, dashboard/alert definitions, runbook, and architecture decision record.

**Hints**  
Begin with one invariant and a thin vertical slice. Keep a naive baseline, then introduce one measured resilience or scale improvement at a time.

**Stretch Goals**  
Add canary delivery, chaos testing, multi-AZ failover, Terraform, Kubernetes manifests, tracing, security threat model, and cost forecast.

**Evaluation Checklist**  
- [ ] Correctness survives retry, restart, and duplicate delivery.
- [ ] Resources/cost are bounded and measured.
- [ ] Telemetry identifies failure ownership.
- [ ] Recovery and rollback are practical and tested.
- [ ] Trade-offs and residual risk are documented.

**Real-world Context**  
This simulates a senior system-design interview plus a production architecture review.

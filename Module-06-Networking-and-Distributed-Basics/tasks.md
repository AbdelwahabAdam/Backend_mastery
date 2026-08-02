# Tasks

Complete in sequence. A task is complete only when its contract, limits, failure behavior, telemetry, and recovery plan are documented and tested.

## 1. Trace an API request

**Level:** Beginner

**Objective**  
Build a FastAPI service behind Nginx and document DNS/TLS/TCP/proxy/application/database flow.

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
A support engineer needs to locate which hop adds latency.

## 2. Deadline and retry laboratory

**Level:** Beginner

**Objective**  
Inject DNS, connection, timeout, and 5xx faults; implement deadlines, safe retries, and structured telemetry.

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
A mobile client retries requests over an unreliable network.

## 3. gRPC and HTTP service pair

**Level:** Intermediate

**Objective**  
Build a deadline-aware HTTP/gRPC pair with service discovery, mTLS-local development notes, and failure injection.

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
Internal services need a typed contract without unbounded cascading waits.

## 4. Realtime updates

**Level:** Intermediate

**Objective**  
Implement WebSocket or SSE updates with heartbeats, reconnects, backpressure, and Redis fan-out.

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
A dashboard must show near-real-time job status across replicas.

## 5. Proxy and load-balancer design

**Level:** Advanced

**Objective**  
Deploy Nginx/Envoy with health checks, draining, rate limits, and an AWS ALB design note.

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
A traffic spike must not overload an unhealthy backend pool.

## 6. Reliable async pipeline

**Level:** Advanced

**Objective**  
Use a PostgreSQL outbox and durable worker queue with idempotent consumption, DLQ, metrics, and reconciliation.

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
A completed order must eventually trigger notifications without duplicate effects.

## 7. Fault-tolerant API edge

**Level:** Production

**Objective**  
Build an observable API gateway boundary with auth, quotas, routing, circuit breaking, traffic tests, and incident runbooks.

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
A public API has varied clients and dependencies with uneven reliability.

## 8. Networking capstone

**Level:** Production

**Objective**  
Build a Docker/Kubernetes-ready FastAPI platform with TLS/reverse proxy, Redis, PostgreSQL, async worker, gRPC/HTTP boundary, WebSocket/SSE update path, AWS deployment plan, SLOs, disaster-recovery procedure, and chaos/load tests.

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
This is reviewed as a production architecture by backend, platform, security, and SRE teams.

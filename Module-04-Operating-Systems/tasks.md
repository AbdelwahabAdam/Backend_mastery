# Tasks

Build tasks in order. A passing implementation is correct, bounded, observable, and documented—not merely functional on one happy-path input.

## 1. Observe a service process

**Level:** Beginner

**Objective**  
Run a small FastAPI service and record PID, threads, file descriptors, RSS, sockets, and lifecycle events.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
An on-call engineer needs a baseline before diagnosing an intermittent resource leak.

## 2. Bounded producer-consumer queue

**Level:** Beginner

**Objective**  
Implement a bounded Python worker queue with shutdown signaling, timeouts, and queue-depth metrics.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
A document ingestion service must protect PostgreSQL when load spikes.

## 3. Race-condition laboratory

**Level:** Intermediate

**Objective**  
Reproduce a duplicate-reservation race, fix it using the correct in-process and database mechanisms, and explain the difference.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
A checkout service is producing duplicate inventory allocations.

## 4. Deadlock and recovery simulation

**Level:** Intermediate

**Objective**  
Create competing resource acquisition, detect/observe the deadlock, apply ordering/timeouts, and test retry behavior.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
Two services update order and inventory records in inconsistent order.

## 5. Memory-pressure resilient worker

**Level:** Advanced

**Objective**  
Stream input, apply backpressure, honor cgroup limits, and demonstrate graceful behavior under induced memory pressure.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
A batch processor is OOM-killed while handling large customer exports.

## 6. Graceful container shutdown

**Level:** Advanced

**Objective**  
Implement SIGTERM draining, readiness transitions, job lease/requeue policy, and deadline-based exit in Docker.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
Kubernetes deploys a new version while long-running jobs are active.

## 7. Concurrent job processor

**Level:** Production

**Objective**  
Build an observable job processor with bounded workers, idempotency, durable state, retry classification, metrics, and a recovery runbook.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
A billing platform needs reliable asynchronous invoice generation.

## 8. OS and concurrency capstone

**Level:** Production

**Objective**  
Build a Dockerized multi-replica FastAPI task scheduler using PostgreSQL and Redis. Include producer-consumer queues, leases/idempotency, cancellation, cgroup-aware limits, graceful shutdown, deadlock-safe database updates, load testing, dashboards, and incident runbooks.

**Requirements**  
- Define the invariant, input limits, and failure outcomes.
- Include unit tests and an integration/load test for one adverse condition.
- Emit structured logs and the metrics needed to diagnose saturation or incorrectness.

**Constraints**  
- Bound memory, concurrency, queue size, and timeouts.
- Do not log secrets or unbounded user payloads.
- State whether correctness is process-local or durable across replicas.

**Expected Output**  
Runnable Docker-based implementation, README, tests, benchmark/load result, metrics/dashboard definitions, and an architecture decision record.

**Hints**  
Build a tiny correct baseline first, write an invariant, then introduce the bounded optimization. Use a naive implementation as a test oracle when possible.

**Stretch Goals**  
Add failure injection, profiling, cancellation, graceful shutdown, tracing, a feature flag, and a rollback runbook.

**Evaluation Checklist**  
- [ ] Edge and failure cases preserve the invariant.
- [ ] Resource use is bounded and measurable.
- [ ] The design works across restart/retry where required.
- [ ] Results include data, not only a claim of performance.
- [ ] Documentation explains trade-offs and ownership.

**Real-world Context**  
This is evaluated as a platform/service architecture review by backend, database, and SRE engineers.

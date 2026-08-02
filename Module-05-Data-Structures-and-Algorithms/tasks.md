# Tasks

Build tasks in order. A passing implementation is correct, bounded, observable, and documented—not merely functional on one happy-path input.

## 1. Complexity test harness

**Level:** Beginner

**Objective**  
Implement naive and optimized versions of a lookup problem, test them against each other, and graph runtime/memory across input sizes.

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
A service team needs evidence before replacing a simple implementation.

## 2. LRU cache

**Level:** Beginner

**Objective**  
Build a bounded LRU cache with tests for eviction and update behavior.

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
An API needs to reduce repeated reads while keeping memory bounded.

## 3. Autocomplete trie

**Level:** Intermediate

**Objective**  
Build a Unicode-aware prefix search with bounded results, ranking, and a benchmark.

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
A search endpoint needs fast suggestions without scanning all terms.

## 4. Sliding-window rate limiter

**Level:** Intermediate

**Objective**  
Implement a rate limiter with correct window semantics and compare in-memory versus Redis behavior.

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
A public API needs fair protection from bursty clients.

## 5. Dependency graph resolver

**Level:** Advanced

**Objective**  
Implement topological sorting with cycle reporting and incremental test fixtures.

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
A deployment platform must order service migrations safely.

## 6. Top-k scheduler

**Level:** Advanced

**Objective**  
Use a heap-backed queue with tie-breakers, cancellation, and fair admission policy.

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
A worker fleet must select urgent work without starving older jobs.

## 7. Distributed cache design

**Level:** Production

**Objective**  
Design a cache with LRU/TTL, key cardinality controls, consistent-hash routing, invalidation strategy, and observability.

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
A high-traffic read API is approaching database capacity.

## 8. DSA capstone

**Level:** Production

**Objective**  
Build an in-memory and Redis-backed rate-limited URL shortener/analytics service using hash maps, LRU cache, queue/heap scheduling, sliding windows, prefix-search trie, and consistent hashing simulation. Include FastAPI, Docker, load tests, correctness oracle, dashboards, and a scaling design.

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
This models an interview loop plus production architecture review for a high-traffic backend platform.

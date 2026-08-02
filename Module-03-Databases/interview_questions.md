# Interview Questions

Use these to practice structured reasoning. A strong answer states the invariant, assumptions, alternatives, failure modes, telemetry, and a rollout plan.

## Junior

### 1. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **02 CAP Theorem**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 02 CAP Theorem, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 2. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **04 Database Selection**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 04 Database Selection, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 3. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **06 Normalization**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 06 Normalization, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 4. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **08 SQL DDL**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 08 SQL DDL, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 5. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **10 SQL JOINs**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 10 SQL JOINs, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 6. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **12 EXISTS vs IN**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 12 EXISTS vs IN, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 7. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **14 Window Functions**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 14 Window Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


### 8. Explain the request path from a client to a persisted result.
**Question**  
Apply your answer to **16 Views**.

**Expected Answer**  
Describe validation, service logic, persistence, response mapping, and basic failure handling. Connect it to the invariant of 16 Views, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Foundational


## Mid

### 9. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **10 SQL JOINs**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 10 SQL JOINs, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 10. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **12 EXISTS vs IN**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 12 EXISTS vs IN, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 11. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **14 Window Functions**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 14 Window Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 12. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **16 Views**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 16 Views, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 13. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **18 Stored Procedures and Functions**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 18 Stored Procedures and Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 14. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **20 Composite Indexes**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 20 Composite Indexes, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 15. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **22 Query Execution Plans**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 22 Query Execution Plans, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


### 16. How do you make a create operation safe when a client retries?
**Question**  
Apply your answer to **24 Offset Pagination**.

**Expected Answer**  
Use an idempotency key, durable deduplication record, stable result replay, and bounded retention. Connect it to the invariant of 24 Offset Pagination, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Intermediate


## Semi Senior

### 17. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **18 Stored Procedures and Functions**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 18 Stored Procedures and Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 18. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **20 Composite Indexes**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 20 Composite Indexes, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 19. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **22 Query Execution Plans**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 22 Query Execution Plans, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 20. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **24 Offset Pagination**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 24 Offset Pagination, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 21. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **26 Query Anti Patterns**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 26 Query Anti Patterns, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 22. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **28 ACID**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 28 ACID, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 23. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **30 Database Locks**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 30 Database Locks, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 24. How would you choose a timeout and retry policy for a dependency?
**Question**  
Apply your answer to **32 Optimistic vs Pessimistic Locking**.

**Expected Answer**  
Start from the end-to-end budget, classify errors, cap attempts, add jitter, and measure the outcome. Connect it to the invariant of 32 Optimistic vs Pessimistic Locking, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


## Senior

### 25. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **26 Query Anti Patterns**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 26 Query Anti Patterns, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 26. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **28 ACID**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 28 ACID, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 27. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **30 Database Locks**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 30 Database Locks, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 28. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **32 Optimistic vs Pessimistic Locking**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 32 Optimistic vs Pessimistic Locking, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 29. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **34 Database Migrations**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 34 Database Migrations, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 30. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **36 Document Modeling**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 36 Document Modeling, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 31. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **02 CAP Theorem**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 02 CAP Theorem, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 32. When is adding a cache the wrong fix for latency?
**Question**  
Apply your answer to **04 Database Selection**.

**Expected Answer**  
When query shape, indexing, fan-out, payload size, contention, or capacity is the root cause; caches add invalidation and consistency cost. Connect it to the invariant of 04 Database Selection, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


## Architecture

### 33. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **34 Database Migrations**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 34 Database Migrations, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 34. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **36 Document Modeling**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 36 Document Modeling, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 35. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **02 CAP Theorem**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 02 CAP Theorem, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 36. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **04 Database Selection**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 04 Database Selection, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 37. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **06 Normalization**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 06 Normalization, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 38. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **08 SQL DDL**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 08 SQL DDL, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 39. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **10 SQL JOINs**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 10 SQL JOINs, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 40. Design a boundary that permits framework replacement without rewriting policy.
**Question**  
Apply your answer to **12 EXISTS vs IN**.

**Expected Answer**  
Keep use cases and domain decisions inward; inject transport, persistence, and messaging adapters at a composition root. Connect it to the invariant of 12 EXISTS vs IN, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


## Scenario Based

### 41. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **06 Normalization**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 06 Normalization, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 42. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **08 SQL DDL**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 08 SQL DDL, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 43. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **10 SQL JOINs**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 10 SQL JOINs, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 44. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **12 EXISTS vs IN**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 12 EXISTS vs IN, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 45. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **14 Window Functions**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 14 Window Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 46. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **16 Views**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 16 Views, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 47. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **18 Stored Procedures and Functions**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 18 Stored Procedures and Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 48. Checkout succeeds in the database but its notification is not sent. What do you do?
**Question**  
Apply your answer to **20 Composite Indexes**.

**Expected Answer**  
Use a transactional outbox, relay with idempotent consumers, observe delivery, and reconcile failures. Connect it to the invariant of 20 Composite Indexes, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


## Debugging

### 49. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **14 Window Functions**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 14 Window Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 50. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **16 Views**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 16 Views, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 51. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **18 Stored Procedures and Functions**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 18 Stored Procedures and Functions, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 52. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **20 Composite Indexes**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 20 Composite Indexes, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 53. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **22 Query Execution Plans**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 22 Query Execution Plans, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 54. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **24 Offset Pagination**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 24 Offset Pagination, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 55. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **26 Query Anti Patterns**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 26 Query Anti Patterns, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 56. p99 latency rose while average latency stayed stable. How do you investigate?
**Question**  
Apply your answer to **28 ACID**.

**Expected Answer**  
Correlate traces with saturation, queueing, slow dependencies, lock waits, GC/event-loop lag, and skewed traffic. Connect it to the invariant of 28 ACID, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


## Behavioral

### 57. Describe how you handled a risky production change.
**Question**  
Apply your answer to **22 Query Execution Plans**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 22 Query Execution Plans, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 58. Describe how you handled a risky production change.
**Question**  
Apply your answer to **24 Offset Pagination**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 24 Offset Pagination, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 59. Describe how you handled a risky production change.
**Question**  
Apply your answer to **26 Query Anti Patterns**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 26 Query Anti Patterns, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 60. Describe how you handled a risky production change.
**Question**  
Apply your answer to **28 ACID**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 28 ACID, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 61. Describe how you handled a risky production change.
**Question**  
Apply your answer to **30 Database Locks**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 30 Database Locks, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 62. Describe how you handled a risky production change.
**Question**  
Apply your answer to **32 Optimistic vs Pessimistic Locking**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 32 Optimistic vs Pessimistic Locking, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 63. Describe how you handled a risky production change.
**Question**  
Apply your answer to **34 Database Migrations**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 34 Database Migrations, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


### 64. Describe how you handled a risky production change.
**Question**  
Apply your answer to **36 Document Modeling**.

**Expected Answer**  
Explain context, risk assessment, rollback, stakeholder communication, telemetry, outcome, and what changed afterward. Connect it to the invariant of 36 Document Modeling, state assumptions, and name the signal that would prove success.

**Follow-up Questions**  
- What changes under high contention or dependency failure?
- What would you measure before and after rollout?
- What is the simplest safe rollback?

**Common Mistakes**  
Giving framework APIs without explaining correctness; omitting retries, authorization, or observability; assuming a happy-path test proves the design.

**Why Interviewers Ask It**  
It distinguishes memorized terminology from operational design judgment.

**Difficulty**  
Advanced


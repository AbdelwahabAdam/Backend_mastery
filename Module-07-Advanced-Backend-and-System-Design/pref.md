# Module 07 Advanced Backend and System Design — Quick Preference Guide

Use this file for rapid revision. Each entry gives the main idea and a small production-oriented example; open the linked chapter for the deeper note, diagrams, mistakes, interview questions, and cheat sheet.

## Topics

### [System Design Fundamentals](01-System-Design-Fundamentals.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Functional Requirements](02-Functional-Requirements.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Non Functional Requirements](03-Non-Functional-Requirements.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Back Of The Envelope Calculations](04-Back-Of-The-Envelope-Calculations.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [System Capacity Planning](05-System-Capacity-Planning.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Scalability](06-Scalability.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Vertical Scaling](07-Vertical-Scaling.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Horizontal Scaling](08-Horizontal-Scaling.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [High Availability](09-High-Availability.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Single AZ vs Multi AZ](10-Single-AZ-vs-Multi-AZ.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Multi Region Deployments](11-Multi-Region-Deployments.md)
**In short:** Limits release blast radius through compatibility, incremental exposure, signals, and rollback.
**Small example:** Route 5% of traffic to a canary and roll back automatically when its error-budget burn rises.

### [Storage Systems](12-Storage-Systems.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Data Modeling](13-Data-Modeling.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Caching Fundamentals](14-Caching-Fundamentals.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Redis Deep Dive](15-Redis-Deep-Dive.md)
**In short:** Reduces read latency and origin load while making staleness, eviction, and invalidation explicit.
**Small example:** Cache a product response for 60 seconds and publish a version/invalidation event when price changes.

### [Cache Invalidation](16-Cache-Invalidation.md)
**In short:** Reduces read latency and origin load while making staleness, eviction, and invalidation explicit.
**Small example:** Cache a product response for 60 seconds and publish a version/invalidation event when price changes.

### [CDN](17-CDN.md)
**In short:** Reduces read latency and origin load while making staleness, eviction, and invalidation explicit.
**Small example:** Cache a product response for 60 seconds and publish a version/invalidation event when price changes.

### [Replication](18-Replication.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Partitioning](19-Partitioning.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Sharding](20-Sharding.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Message Queues](21-Message-Queues.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [Kafka Fundamentals](22-Kafka-Fundamentals.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [RabbitMQ Fundamentals](23-RabbitMQ-Fundamentals.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [Pub Sub Pattern](24-Pub-Sub-Pattern.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Event Driven Architecture](25-Event-Driven-Architecture.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [Event Sourcing](26-Event-Sourcing.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [CQRS](27-CQRS.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Consistency in Distributed Systems](28-Consistency-in-Distributed-Systems.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Distributed Transactions](29-Distributed-Transactions.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [Two Phase Commit](30-Two-Phase-Commit.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [SAGA Pattern](31-SAGA-Pattern.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [Idempotency](32-Idempotency.md)
**In short:** Coordinates asynchronous, retryable effects with durable events and idempotent consumers.
**Small example:** An order transaction writes an outbox row; a worker publishes it and deduplicates by event ID.

### [Rate Limiting](33-Rate-Limiting.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Circuit Breaker](34-Circuit-Breaker.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Retry Pattern](35-Retry-Pattern.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Exponential Backoff](36-Exponential-Backoff.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Timeout Pattern](37-Timeout-Pattern.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Bulkhead Pattern](38-Bulkhead-Pattern.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Feature Flags](39-Feature-Flags.md)
**In short:** Limits release blast radius through compatibility, incremental exposure, signals, and rollback.
**Small example:** Route 5% of traffic to a canary and roll back automatically when its error-budget burn rises.

### [Safe Deployments](40-Safe-Deployments.md)
**In short:** Limits release blast radius through compatibility, incremental exposure, signals, and rollback.
**Small example:** Route 5% of traffic to a canary and roll back automatically when its error-budget burn rises.

### [Blue Green Deployment](41-Blue-Green-Deployment.md)
**In short:** Limits release blast radius through compatibility, incremental exposure, signals, and rollback.
**Small example:** Route 5% of traffic to a canary and roll back automatically when its error-budget burn rises.

### [Canary Deployment](42-Canary-Deployment.md)
**In short:** Limits release blast radius through compatibility, incremental exposure, signals, and rollback.
**Small example:** Route 5% of traffic to a canary and roll back automatically when its error-budget burn rises.

### [Rolling Deployment](43-Rolling-Deployment.md)
**In short:** Limits release blast radius through compatibility, incremental exposure, signals, and rollback.
**Small example:** Route 5% of traffic to a canary and roll back automatically when its error-budget burn rises.

### [Cloud Fundamentals](44-Cloud-Fundamentals.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Object Storage](45-Object-Storage.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Blob Storage](46-Blob-Storage.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [System Architecture Patterns](47-System-Architecture-Patterns.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Layered Architecture](48-Layered-Architecture.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Hexagonal Architecture](49-Hexagonal-Architecture.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Monolith](50-Monolith.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Modular Monolith](51-Modular-Monolith.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Microservices](52-Microservices.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [Service Mesh](53-Service-Mesh.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [API Versioning](54-API-Versioning.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [System Design Interview Strategy](55-System-Design-Interview-Strategy.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

### [System Design Case Studies](56-System-Design-Case-Studies.md)
**In short:** Turns product requirements into capacity, data, scaling, reliability, security, and cost decisions.
**Small example:** Estimate peak QPS before choosing replicas; preserve a payment ledger in PostgreSQL before adding a cache.

## How to revise

1. Read each `In short` line aloud.
2. Explain the example without looking.
3. Open the linked chapter when you cannot state the invariant, failure mode, or trade-off.

## Related module resources

- [Module overview](README.md)
- [Interview questions](interview_questions.md)
- [Practical tasks](tasks.md)

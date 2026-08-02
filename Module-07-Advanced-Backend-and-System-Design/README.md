# Module 7: Advanced Backend & System Design

## Module overview
This module prepares semi-senior backend engineers to reason about end-to-end production behavior: request paths, failure domains, data durability, scalable architecture, and cost-aware operations.

## Learning objectives
- Turn requirements into explicit availability, latency, consistency, security, and cost targets.
- Design APIs and asynchronous workflows that survive partial failures and retries.
- Explain production trade-offs in architecture reviews and interviews.

## Required prerequisites
- Python/FastAPI, Docker, HTTP, SQL, Redis, and basic Linux knowledge.
- Modules 2–5 or equivalent experience with APIs, databases, concurrency, and algorithms.

## Recommended learning order
Read chapters in numerical order, implement the exercises, then use [interview_questions.md](interview_questions.md) for active recall and [tasks.md](tasks.md) for end-to-end practice.

## Estimated study time
**170–230 hours**, including diagrams, prototypes, failure injection, load tests, capacity estimates, and interview practice.

## Skills gained
- Network-aware service design and incident diagnosis
- Resilient distributed workflows and safe deployments
- Capacity, cost, security, and recovery planning
- Clear system-design interview communication

## Real-world applications
Payments, messaging, live updates, files, marketplaces, analytics, APIs, and globally deployed services all require these decisions.

## Backend interview focus areas
Clarifying requirements, capacity estimates, data modeling, caching, consistency, queues, failure handling, observability, security, and trade-off communication.

## Chapter index
- [01-System Design Fundamentals](01-System-Design-Fundamentals.md)
- [02-Functional Requirements](02-Functional-Requirements.md)
- [03-Non Functional Requirements](03-Non-Functional-Requirements.md)
- [04-Back Of The Envelope Calculations](04-Back-Of-The-Envelope-Calculations.md)
- [05-System Capacity Planning](05-System-Capacity-Planning.md)
- [06-Scalability](06-Scalability.md)
- [07-Vertical Scaling](07-Vertical-Scaling.md)
- [08-Horizontal Scaling](08-Horizontal-Scaling.md)
- [09-High Availability](09-High-Availability.md)
- [10-Single AZ vs Multi AZ](10-Single-AZ-vs-Multi-AZ.md)
- [11-Multi Region Deployments](11-Multi-Region-Deployments.md)
- [12-Storage Systems](12-Storage-Systems.md)
- [13-Data Modeling](13-Data-Modeling.md)
- [14-Caching Fundamentals](14-Caching-Fundamentals.md)
- [15-Redis Deep Dive](15-Redis-Deep-Dive.md)
- [16-Cache Invalidation](16-Cache-Invalidation.md)
- [17-CDN](17-CDN.md)
- [18-Replication](18-Replication.md)
- [19-Partitioning](19-Partitioning.md)
- [20-Sharding](20-Sharding.md)
- [21-Message Queues](21-Message-Queues.md)
- [22-Kafka Fundamentals](22-Kafka-Fundamentals.md)
- [23-RabbitMQ Fundamentals](23-RabbitMQ-Fundamentals.md)
- [24-Pub Sub Pattern](24-Pub-Sub-Pattern.md)
- [25-Event Driven Architecture](25-Event-Driven-Architecture.md)
- [26-Event Sourcing](26-Event-Sourcing.md)
- [27-CQRS](27-CQRS.md)
- [28-Consistency in Distributed Systems](28-Consistency-in-Distributed-Systems.md)
- [29-Distributed Transactions](29-Distributed-Transactions.md)
- [30-Two Phase Commit](30-Two-Phase-Commit.md)
- [31-SAGA Pattern](31-SAGA-Pattern.md)
- [32-Idempotency](32-Idempotency.md)
- [33-Rate Limiting](33-Rate-Limiting.md)
- [34-Circuit Breaker](34-Circuit-Breaker.md)
- [35-Retry Pattern](35-Retry-Pattern.md)
- [36-Exponential Backoff](36-Exponential-Backoff.md)
- [37-Timeout Pattern](37-Timeout-Pattern.md)
- [38-Bulkhead Pattern](38-Bulkhead-Pattern.md)
- [39-Feature Flags](39-Feature-Flags.md)
- [40-Safe Deployments](40-Safe-Deployments.md)
- [41-Blue Green Deployment](41-Blue-Green-Deployment.md)
- [42-Canary Deployment](42-Canary-Deployment.md)
- [43-Rolling Deployment](43-Rolling-Deployment.md)
- [44-Cloud Fundamentals](44-Cloud-Fundamentals.md)
- [45-Object Storage](45-Object-Storage.md)
- [46-Blob Storage](46-Blob-Storage.md)
- [47-System Architecture Patterns](47-System-Architecture-Patterns.md)
- [48-Layered Architecture](48-Layered-Architecture.md)
- [49-Hexagonal Architecture](49-Hexagonal-Architecture.md)
- [50-Monolith](50-Monolith.md)
- [51-Modular Monolith](51-Modular-Monolith.md)
- [52-Microservices](52-Microservices.md)
- [53-Service Mesh](53-Service-Mesh.md)
- [54-API Versioning](54-API-Versioning.md)
- [55-System Design Interview Strategy](55-System-Design-Interview-Strategy.md)
- [56-System Design Case Studies](56-System-Design-Case-Studies.md)

## Summary
The objective is not to memorize vendor diagrams. It is to make a system's guarantees, limits, failure behavior, and operational ownership explicit.

    # Module 3: Databases

    ## Module overview
    This module develops semi-senior engineering judgment around data modeling, SQL, indexing, transactions, migrations, and MongoDB. It is designed as a reference and a practice guide: each chapter explains the contract, internals, failure modes, operational signals, and a production-oriented implementation approach.

    ## Learning objectives
    - Explain why a design exists before choosing an implementation.
    - Define correctness, performance, security, scalability, and reliability trade-offs.
    - Build observable services using Python, FastAPI, PostgreSQL, Redis, and Docker.
    - Defend choices in an interview, architecture review, and incident review.

    ## Required prerequisites
    - Practical Python, Git, Linux shell, and Docker fundamentals.
    - Familiarity with JSON, HTTP clients, and unit/integration tests.
    - For this module, review basic relational algebra and SQL before the indexing and transaction chapters.

    ## Recommended learning order
    Follow the numbered chapters. Read the adjacent architecture and operational chapters together, complete exercises immediately, then implement the capstone in [tasks.md](tasks.md). Use [interview_questions.md](interview_questions.md) after each topic as active recall, not as a memorization list.

    ## Estimated study time
    **110–150 hours**, including reading, implementation, debugging, load tests, and interview practice. Increase the estimate if the stack is new to you.

    ## Skills gained
    - Production API and persistence design
    - Explicit failure, retry, and idempotency strategies
    - Secure authentication and secret-handling habits
    - Performance diagnosis with metrics, traces, logs, and query plans
    - Architecture-review and technical-interview communication

    ## Real-world applications
    These techniques apply to payments, bookings, marketplaces, identity systems, internal platforms, and data-heavy SaaS backends. The repeated theme is safe evolution under real traffic, partial failure, and concurrent change.

    ## Chapter index
    - [01-SQL vs NoSQL](01-SQL vs NoSQL.md)
- [02-CAP Theorem](02-CAP Theorem.md)
- [03-Consistency Models](03-Consistency Models.md)
- [04-Database Selection](04-Database Selection.md)
- [05-Schema Design](05-Schema Design.md)
- [06-Normalization](06-Normalization.md)
- [07-Denormalization](07-Denormalization.md)
- [08-SQL DDL](08-SQL DDL.md)
- [09-SQL DML](09-SQL DML.md)
- [10-SQL JOINs](10-SQL JOINs.md)
- [11-Subqueries](11-Subqueries.md)
- [12-EXISTS vs IN](12-EXISTS vs IN.md)
- [13-Aggregate Functions](13-Aggregate Functions.md)
- [14-Window Functions](14-Window Functions.md)
- [15-Common Table Expressions](15-Common Table Expressions.md)
- [16-Views](16-Views.md)
- [17-Materialized Views](17-Materialized Views.md)
- [18-Stored Procedures and Functions](18-Stored Procedures and Functions.md)
- [19-Indexes](19-Indexes.md)
- [20-Composite Indexes](20-Composite Indexes.md)
- [21-Covering Indexes](21-Covering Indexes.md)
- [22-Query Execution Plans](22-Query Execution Plans.md)
- [23-Query Optimization](23-Query Optimization.md)
- [24-Offset Pagination](24-Offset Pagination.md)
- [25-Cursor Pagination](25-Cursor Pagination.md)
- [26-Query Anti Patterns](26-Query Anti Patterns.md)
- [27-Transactions](27-Transactions.md)
- [28-ACID](28-ACID.md)
- [29-Isolation Levels](29-Isolation Levels.md)
- [30-Database Locks](30-Database Locks.md)
- [31-Deadlocks](31-Deadlocks.md)
- [32-Optimistic vs Pessimistic Locking](32-Optimistic vs Pessimistic Locking.md)
- [33-ORM Fundamentals](33-ORM Fundamentals.md)
- [34-Database Migrations](34-Database Migrations.md)
- [35-MongoDB Fundamentals](35-MongoDB Fundamentals.md)
- [36-Document Modeling](36-Document Modeling.md)

    ## Summary
    Complete this module by being able to articulate the invariants of a service, observe them in production, and evolve them safely. The goal is engineering judgment—not framework trivia.

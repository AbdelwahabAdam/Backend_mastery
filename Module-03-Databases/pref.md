# Module 03 Databases — Quick Preference Guide

Use this file for rapid revision. Each entry gives the main idea and a small production-oriented example; open the linked chapter for the deeper note, diagrams, mistakes, interview questions, and cheat sheet.

## Topics

### [SQL vs NoSQL](01-SQL-vs-NoSQL.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [CAP Theorem](02-CAP-Theorem.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Consistency Models](03-Consistency-Models.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Database Selection](04-Database-Selection.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Schema Design](05-Schema-Design.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Normalization](06-Normalization.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Denormalization](07-Denormalization.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [SQL DDL](08-SQL-DDL.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [SQL DML](09-SQL-DML.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [SQL JOINs](10-SQL-JOINs.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Subqueries](11-Subqueries.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [EXISTS vs IN](12-EXISTS-vs-IN.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Aggregate Functions](13-Aggregate-Functions.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Window Functions](14-Window-Functions.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Common Table Expressions](15-Common-Table-Expressions.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Views](16-Views.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Materialized Views](17-Materialized-Views.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Stored Procedures and Functions](18-Stored-Procedures-and-Functions.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Indexes](19-Indexes.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Composite Indexes](20-Composite-Indexes.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Covering Indexes](21-Covering-Indexes.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Query Execution Plans](22-Query-Execution-Plans.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Query Optimization](23-Query-Optimization.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Offset Pagination](24-Offset-Pagination.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Cursor Pagination](25-Cursor-Pagination.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Query Anti Patterns](26-Query-Anti-Patterns.md)
**In short:** Makes the actual query shape efficient while balancing write cost, storage, and plan stability.
**Small example:** For `WHERE tenant_id = ? ORDER BY created_at DESC`, use a matching composite index and keyset cursor.

### [Transactions](27-Transactions.md)
**In short:** Protects shared business invariants when concurrent requests read and write the same facts.
**Small example:** Use `UPDATE inventory SET available=available-1 WHERE available>=1` rather than read-check-write in Python.

### [ACID](28-ACID.md)
**In short:** Protects shared business invariants when concurrent requests read and write the same facts.
**Small example:** Use `UPDATE inventory SET available=available-1 WHERE available>=1` rather than read-check-write in Python.

### [Isolation Levels](29-Isolation-Levels.md)
**In short:** Protects shared business invariants when concurrent requests read and write the same facts.
**Small example:** Use `UPDATE inventory SET available=available-1 WHERE available>=1` rather than read-check-write in Python.

### [Database Locks](30-Database-Locks.md)
**In short:** Protects shared business invariants when concurrent requests read and write the same facts.
**Small example:** Use `UPDATE inventory SET available=available-1 WHERE available>=1` rather than read-check-write in Python.

### [Deadlocks](31-Deadlocks.md)
**In short:** Protects shared business invariants when concurrent requests read and write the same facts.
**Small example:** Use `UPDATE inventory SET available=available-1 WHERE available>=1` rather than read-check-write in Python.

### [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md)
**In short:** Protects shared business invariants when concurrent requests read and write the same facts.
**Small example:** Use `UPDATE inventory SET available=available-1 WHERE available>=1` rather than read-check-write in Python.

### [ORM Fundamentals](33-ORM-Fundamentals.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [Database Migrations](34-Database-Migrations.md)
**In short:** Selects data models, schemas, and SQL constructs from invariants, cardinality, and real access patterns.
**Small example:** Normalize orders and order_items; add a denormalized daily-sales projection only after measured read pressure.

### [MongoDB Fundamentals](35-MongoDB-Fundamentals.md)
**In short:** Models document data around aggregate ownership and access patterns while controlling growth and indexes.
**Small example:** Embed shipping address in an order; reference a shared customer profile that changes independently.

### [Document Modeling](36-Document-Modeling.md)
**In short:** Models document data around aggregate ownership and access patterns while controlling growth and indexes.
**Small example:** Embed shipping address in an order; reference a shared customer profile that changes independently.

## How to revise

1. Read each `In short` line aloud.
2. Explain the example without looking.
3. Open the linked chapter when you cannot state the invariant, failure mode, or trade-off.

## Related module resources

- [Module overview](README.md)
- [Interview questions](interview_questions.md)
- [Practical tasks](tasks.md)

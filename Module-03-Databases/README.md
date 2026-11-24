# Module 03: Databases

## Overview

Almost every backend bug that costs real money happens at the database: a lost update, a duplicate payment, a missing index that takes down checkout, a migration that locks a table at noon. This module teaches you to model data, write and read SQL fluently, make queries fast, keep data correct under concurrency, and evolve a schema safely. It ends with MongoDB, so you can explain when a document store is the better choice.

SQL examples use **PostgreSQL 16+**, with MySQL (InnoDB) differences noted where interviewers ask about them. Application code is shown in both **Node.js/TypeScript** (`pg`, plus Prisma/Drizzle in the ORM chapters and the `mongodb` driver) and **Python** (psycopg 3 / asyncpg, SQLAlchemy 2.0, Alembic and PyMongo).

## Learning objectives

After this module you can:

- Choose between relational and document databases, and explain CAP and consistency models without hand-waving.
- Design a normalized schema, and denormalize on purpose when reads demand it.
- Write joins, subqueries, aggregates, window functions and CTEs from memory.
- Read an `EXPLAIN ANALYZE` plan, design composite and covering indexes, and fix slow queries.
- Pick an isolation level and locking strategy that prevents lost updates, and diagnose deadlocks.
- Use an ORM without N+1 queries, and ship zero-downtime migrations.
- Model documents in MongoDB around access patterns.

## Prerequisites

- [Module 02: Core Backend](../Module-02-Core-Backend/README.md), especially the [service layer](../Module-02-Core-Backend/13-Service-Layer-Pattern.md) and [repository](../Module-02-Core-Backend/14-Repository-Pattern.md) chapters.
- A local PostgreSQL (`docker run -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:16`) and MongoDB for the last two chapters.

## Sample schema used in every chapter

All chapters use this small e-commerce schema, so you can run every query against one database. Chapters add tables or indexes when the topic needs them.

```sql
CREATE TABLE customers (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email       text        NOT NULL UNIQUE,
  name        text        NOT NULL,
  country     char(2)     NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE products (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sku          text    NOT NULL UNIQUE,
  name         text    NOT NULL,
  category     text    NOT NULL,
  price_cents  integer NOT NULL CHECK (price_cents >= 0)
);

CREATE TABLE inventory (
  product_id  bigint  PRIMARY KEY REFERENCES products(id),
  available   integer NOT NULL CHECK (available >= 0),
  version     integer NOT NULL DEFAULT 0
);

CREATE TABLE orders (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id  bigint      NOT NULL REFERENCES customers(id),
  status       text        NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
  total_cents  integer     NOT NULL CHECK (total_cents >= 0),
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
  order_id          bigint  NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id        bigint  NOT NULL REFERENCES products(id),
  quantity          integer NOT NULL CHECK (quantity > 0),
  unit_price_cents  integer NOT NULL CHECK (unit_price_cents >= 0),
  PRIMARY KEY (order_id, product_id)
);

CREATE TABLE payments (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id      bigint      NOT NULL REFERENCES orders(id),
  amount_cents  integer     NOT NULL CHECK (amount_cents > 0),
  status        text        NOT NULL CHECK (status IN ('authorized', 'captured', 'refunded', 'failed')),
  provider_ref  text        UNIQUE,
  created_at    timestamptz NOT NULL DEFAULT now()
);
```

> **Deliberate gap:** `orders.customer_id` has no index. PostgreSQL does not index foreign-key columns automatically. The indexing chapters start by finding and fixing this.

## Chapters

### Choosing a database
| # | Chapter | You should be able to… |
|---|---|---|
| 01 | [SQL vs NoSQL](01-SQL-vs-NoSQL.md) | Compare relational, document, key-value, wide-column and graph stores by access pattern |
| 02 | [CAP Theorem](02-CAP-Theorem.md) | State what CAP actually says, and explain PACELC |
| 03 | [Consistency Models](03-Consistency-Models.md) | Tell linearizable, sequential, causal, read-your-writes and eventual apart |
| 04 | [Database Selection](04-Database-Selection.md) | Pick a database from requirements, and defend "just use Postgres" |

### Modelling
| # | Chapter | You should be able to… |
|---|---|---|
| 05 | [Schema Design](05-Schema-Design.md) | Choose keys, types and constraints; model 1:1, 1:N and N:M |
| 06 | [Normalization](06-Normalization.md) | Normalize to 3NF/BCNF and name the anomaly each form removes |
| 07 | [Denormalization](07-Denormalization.md) | Denormalize on purpose and keep the copies correct |
| 08 | [SQL DDL](08-SQL-DDL.md) | Write tables, constraints, and safe `ALTER TABLE` statements |

### Querying
| # | Chapter | You should be able to… |
|---|---|---|
| 09 | [SQL DML](09-SQL-DML.md) | Write upserts, `RETURNING`, and batch writes safely |
| 10 | [SQL JOINs](10-SQL-JOINs.md) | Use every join type, and avoid row multiplication |
| 11 | [Subqueries](11-Subqueries.md) | Write correlated subqueries and `LATERAL` joins |
| 12 | [EXISTS vs IN](12-EXISTS-vs-IN.md) | Explain semi-/anti-joins and the `NOT IN` + `NULL` trap |
| 13 | [Aggregate Functions](13-Aggregate-Functions.md) | Use `GROUP BY`, `HAVING` and `FILTER`, and handle `NULL`s in aggregates |
| 14 | [Window Functions](14-Window-Functions.md) | Rank, compute running totals, and find top-N per group |
| 15 | [Common Table Expressions](15-Common-Table-Expressions.md) | Write readable and recursive queries |
| 16 | [Views](16-Views.md) | Use views for abstraction and row-level access |
| 17 | [Materialized Views](17-Materialized-Views.md) | Precompute expensive reads and refresh them without blocking |
| 18 | [Stored Procedures and Functions](18-Stored-Procedures-and-Functions.md) | Decide when logic belongs in the database |

### Performance
| # | Chapter | You should be able to… |
|---|---|---|
| 19 | [Indexes](19-Indexes.md) | Explain B-tree internals and choose index types |
| 20 | [Composite Indexes](20-Composite-Indexes.md) | Order index columns by equality, then range, then sort |
| 21 | [Covering Indexes](21-Covering-Indexes.md) | Get index-only scans with `INCLUDE` |
| 22 | [Query Execution Plans](22-Query-Execution-Plans.md) | Read `EXPLAIN (ANALYZE, BUFFERS)` and spot bad estimates |
| 23 | [Query Optimization](23-Query-Optimization.md) | Follow a repeatable method to make a slow query fast |
| 24 | [Offset Pagination](24-Offset-Pagination.md) | Explain why deep offsets are slow and when they are fine |
| 25 | [Cursor Pagination](25-Cursor-Pagination.md) | Implement keyset pagination with tie-breakers |
| 26 | [Query Anti-Patterns](26-Query-Anti-Patterns.md) | Spot N+1, `SELECT *`, functions on indexed columns, and more |

### Correctness under concurrency
| # | Chapter | You should be able to… |
|---|---|---|
| 27 | [Transactions](27-Transactions.md) | Scope transactions correctly in application code |
| 28 | [ACID](28-ACID.md) | Explain each property and how Postgres implements it (WAL, MVCC) |
| 29 | [Isolation Levels](29-Isolation-Levels.md) | Map anomalies to isolation levels in Postgres and MySQL |
| 30 | [Database Locks](30-Database-Locks.md) | Use row locks, `SKIP LOCKED` and advisory locks; avoid lock queues |
| 31 | [Deadlocks](31-Deadlocks.md) | Read a deadlock report and prevent deadlocks by lock ordering |
| 32 | [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md) | Prevent lost updates either way, and choose between them |

### Working with databases from code
| # | Chapter | You should be able to… |
|---|---|---|
| 33 | [ORM Fundamentals](33-ORM-Fundamentals.md) | Use an ORM without N+1 queries or hidden transactions |
| 34 | [Database Migrations](34-Database-Migrations.md) | Ship expand–contract migrations with zero downtime |
| 35 | [MongoDB Fundamentals](35-MongoDB-Fundamentals.md) | Use documents, indexes, write concerns and transactions in MongoDB |
| 36 | [Document Modeling](36-Document-Modeling.md) | Choose embedding vs referencing from access patterns |

## Study resources in this folder

- [pref.md](pref.md) — one-line definition and example per chapter, for quick revision.
- [module-summary.md](module-summary.md) — the whole module as one connected story.
- [interview_questions.md](interview_questions.md) — mixed-topic questions with model answers.
- [tasks.md](tasks.md) — hands-on exercises against the sample schema.

## Suggested plan (about 4 weeks, 1–2 hours a day)

| Week | Chapters | Build |
|---|---|---|
| 1 | 01–08 | Tasks 1–2 |
| 2 | 09–18 | Task 3 |
| 3 | 19–26 | Tasks 4–5 |
| 4 | 27–36 | Tasks 6–8, then the interview questions |

## Related modules

- [Module 02: Core Backend](../Module-02-Core-Backend/README.md) — services and repositories that wrap these queries.
- [Module 04: Operating Systems](../Module-04-Operating-Systems/README.md) — page cache, fsync and I/O beneath the storage engine.
- [Module 07: Advanced Backend and System Design](../Module-07-Advanced-Backend-and-System-Design/README.md) — replication, partitioning, sharding and caching at scale.

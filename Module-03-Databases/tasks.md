# Module 03 Practice Tasks: Make the Orders Database Correct and Fast

Every task uses the [sample schema](README.md#sample-schema-used-in-every-chapter) in a local PostgreSQL 16+. Tasks 1–5 are mostly SQL. Tasks 6–8 add application code: write them in **Node.js/TypeScript (`pg`)** or **Python (psycopg 3 / asyncpg)**, and port at least task 6 to the other language.

**Setup:** load the schema, then generate realistic data: 100k customers, 5k products, 2M orders over 2 years, 1–5 items per order, and a skewed distribution where 1% of customers place 30% of orders. A `generate_series` script is enough. Run `ANALYZE` afterwards.

Each task is done when every item in its **Done when** list is shown by a query result, a plan, or an automated test.

---

## Task 1 — Model a new feature
**Chapters:** [05](05-Schema-Design.md), [06](06-Normalization.md), [08](08-SQL-DDL.md) · **Level:** Beginner

Add product reviews (1–5 stars, text, one review per customer per product) and product tags (many-to-many).

**Done when**
- [ ] A customer cannot review the same product twice, and ratings outside 1–5 are rejected — **by the database**, not only the app.
- [ ] Deleting a product does what you decided (block, cascade, or soft delete), and the choice is written down with a reason.
- [ ] The design is in 3NF; you can name the functional dependencies of each table.
- [ ] All constraints have explicit names, so app code can map violations (SQLSTATE `23505`, `23503`, `23514`) to clear errors.

## Task 2 — Choose where to denormalize
**Chapters:** [07](07-Denormalization.md), [17](17-Materialized-Views.md) · **Level:** Beginner

The product page needs `average_rating` and `review_count`, and is read 1,000× more often than reviews are written.

**Done when**
- [ ] You implement **two** options — a counter updated in the same transaction, and a materialized view refreshed every 5 minutes — and measure read latency for each.
- [ ] A drift-check query proves the stored counter equals `COUNT(*)` from the source table.
- [ ] `REFRESH MATERIALIZED VIEW CONCURRENTLY` works while a read loop keeps running without errors.
- [ ] A one-paragraph decision explains which option you would ship, and why.

## Task 3 — Reporting queries
**Chapters:** [10](10-SQL-JOINs.md)–[15](15-Common-Table-Expressions.md) · **Level:** Intermediate

Write each query **without** an ORM:

**Done when**
- [ ] Daily revenue for the last 30 days, in the `Africa/Cairo` time zone, including days with zero orders.
- [ ] Top 3 products by revenue in each category (window function), with ties handled deliberately.
- [ ] Customers who ordered in their first week but never again (anti-join). Write it once with `NOT EXISTS` and once with `NOT IN`, then explain why `NOT IN` breaks if the subquery can return `NULL`.
- [ ] Each customer's latest 3 orders with their items (`LATERAL`), as one query.
- [ ] Month-over-month revenue growth per category (`lag`).
- [ ] A recursive query that returns a category's full breadcrumb (add a `categories` table with `parent_id`).

## Task 4 — Fix the slow endpoints
**Chapters:** [19](19-Indexes.md)–[23](23-Query-Optimization.md) · **Level:** Intermediate

Enable `pg_stat_statements` and run this workload (a simple script in either language):
- `GET /customers/{id}/orders?status=paid`, newest first, 20 rows
- order lookups by `payments.provider_ref`
- case-insensitive login by email
- the 30-day revenue report from Task 3

**Done when**
- [ ] For each query you save the `EXPLAIN (ANALYZE, BUFFERS)` output before and after your fix.
- [ ] The customer-orders query does an Index Scan (or Index Only Scan) on a composite index whose column order you can justify. p95 is under 5 ms.
- [ ] The email lookup uses an expression index or `citext`, and `lower(email)` uniqueness is enforced.
- [ ] Every index you add is justified, and you run a query listing indexes with zero scans so you can remove one you don't need.
- [ ] All indexes on the large tables are created with `CREATE INDEX CONCURRENTLY`.

## Task 5 — Pagination at depth
**Chapters:** [24](24-Offset-Pagination.md), [25](25-Cursor-Pagination.md), [26](26-Query-Anti-Patterns.md) · **Level:** Intermediate

**Done when**
- [ ] You implement offset and keyset pagination for a customer's order history, and chart response time for page 1, 100, 1,000 and 10,000 for each.
- [ ] Keyset pagination uses `(created_at, id)` and stays correct when several orders share a timestamp. A test proves no row is skipped or repeated while inserts happen mid-scroll.
- [ ] The cursor is opaque (base64url), validated, and tamper-evident.

## Task 6 — No overselling under concurrency
**Chapters:** [27](27-Transactions.md)–[32](32-Optimistic-vs-Pessimistic-Locking.md) · **Level:** Advanced

Write a load test: 200 concurrent buyers try to buy a product that has 50 units in stock.

**Done when**
- [ ] A naive read-check-write version oversells. Capture the evidence.
- [ ] You implement three correct versions — atomic conditional `UPDATE`, `SELECT ... FOR UPDATE`, and optimistic `version` checks with retry — and each sells exactly 50.
- [ ] You compare throughput and the p99 latency of the three, and explain the difference.
- [ ] A multi-product checkout that locks rows in random order produces a deadlock (`40P01`). Fix it by sorting IDs, and prove no deadlocks occur in 10,000 runs.
- [ ] The write-skew case from [29](29-Isolation-Levels.md) is reproduced under `REPEATABLE READ` and fixed with `SERIALIZABLE` + retry.

## Task 7 — Zero-downtime migration
**Chapters:** [08](08-SQL-DDL.md), [34](34-Database-Migrations.md) · **Level:** Advanced

Rename `customers.name` to `full_name` and change `orders.total_cents` from `integer` to `bigint`, while a load script writes 200 requests/second.

**Done when**
- [ ] The rename follows expand → migrate → contract across at least three deploys, and the old and new app versions both work during the transition.
- [ ] The backfill runs in keyset batches with small transactions. The load script logs no errors and no request slower than 1 s.
- [ ] Every migration sets `lock_timeout`, and you prove a blocked `ALTER` fails fast instead of queueing everyone behind it.
- [ ] Migrations run from CI against a fresh database, and a check rejects `DROP COLUMN` in the same release that stops using the column.

## Task 8 — The same domain in MongoDB
**Chapters:** [01](01-SQL-vs-NoSQL.md), [35](35-MongoDB-Fundamentals.md), [36](36-Document-Modeling.md) · **Level:** Advanced

**Done when**
- [ ] Orders are modelled as documents with an embedded item snapshot. Customers and products are separate collections, each with a `$jsonSchema` validator.
- [ ] Stock decrement is a single conditional atomic update (no transaction), and the Task 6 load test still sells exactly 50.
- [ ] The customer-orders listing uses a compound index that follows the ESR (equality, sort, range) rule, confirmed with `explain("executionStats")`.
- [ ] Daily revenue is an aggregation pipeline whose results match the SQL report from Task 3.
- [ ] A written comparison (one page) says which store you would choose for this system, citing CAP/PACELC and your measurements.

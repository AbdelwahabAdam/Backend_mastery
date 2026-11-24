# Module 03 Databases — Quick Reference

Use this for fast revision. Every chapter has its own definition, a plain-English explanation, and a small example based on the [sample schema](README.md#sample-schema-used-in-every-chapter).

## Choosing a database

### [SQL vs NoSQL](01-SQL-vs-NoSQL.md)
**Definition:** Relational databases store normalized tables queried with SQL; "NoSQL" covers document, key-value, wide-column and graph stores built around specific access patterns.
**Simple explanation:** SQL databases let you ask almost any question later; NoSQL stores make the questions you planned for very cheap.
**Small example:** "Customer with last 5 orders" is a join in PostgreSQL, but a single document read in MongoDB if orders are embedded.

### [CAP Theorem](02-CAP-Theorem.md)
**Definition:** During a network partition, a replicated system must choose between consistency (linearizability) and availability.
**Simple explanation:** When replicas cannot talk to each other, either some requests fail or some return stale data.
**Small example:** MongoDB with `w: "majority"` rejects writes on the minority side of a partition (CP behaviour); a Dynamo-style store with `W=1` accepts them (AP).

### [Consistency Models](03-Consistency-Models.md)
**Definition:** A consistency model defines which values a read may return after concurrent or replicated writes.
**Simple explanation:** It is the promise about how stale or out-of-order your reads can be.
**Small example:** A user updates their profile, then reads it from a lagging replica and sees the old name — read-your-writes was not guaranteed.

### [Database Selection](04-Database-Selection.md)
**Definition:** Choosing a store from access patterns, consistency needs, scale, latency, and the cost to operate it.
**Simple explanation:** Pick the boring database that answers your real queries; add a specialist store only when you can name the query it fixes.
**Small example:** Product search starts as PostgreSQL full-text search with a GIN index before anyone runs Elasticsearch.

## Modelling

### [Schema Design](05-Schema-Design.md)
**Definition:** Choosing tables, keys, types, relationships and constraints so the database itself rejects invalid data.
**Simple explanation:** The schema is your last line of defence; app validation can be bypassed, constraints cannot.
**Small example:** `price_cents integer NOT NULL CHECK (price_cents >= 0)` — money as integer cents, never `float`.

### [Normalization](06-Normalization.md)
**Definition:** Organizing columns so each fact is stored once and every non-key column depends on the key, the whole key, and nothing but the key.
**Simple explanation:** Store a fact in one place so it cannot disagree with itself.
**Small example:** Product names live in `products`, not copied into every `order_items` row — but `unit_price_cents` is copied, because it is the price *at purchase time*.

### [Denormalization](07-Denormalization.md)
**Definition:** Deliberately storing redundant data to make reads cheaper, with a plan to keep the copies correct.
**Simple explanation:** Pay at write time so hot reads don't recompute the same answer.
**Small example:** Keep `customers.orders_count`, updated in the same transaction as the order insert, plus a nightly drift check.

### [SQL DDL](08-SQL-DDL.md)
**Definition:** Data Definition Language — `CREATE`, `ALTER`, `DROP` statements that change the schema.
**Simple explanation:** DDL changes the shape of the database, and many statements briefly lock the whole table.
**Small example:** `SET lock_timeout = '3s'; ALTER TABLE orders ADD COLUMN note text;` fails fast instead of queueing behind a long query.

## Querying

### [SQL DML](09-SQL-DML.md)
**Definition:** Data Manipulation Language — `INSERT`, `UPDATE`, `DELETE`, `MERGE`/upsert.
**Simple explanation:** DML changes rows; doing it atomically in one statement avoids races.
**Small example:** `UPDATE inventory SET available = available - 2 WHERE product_id = $1 AND available >= 2` — 0 rows updated means out of stock.

### [SQL JOINs](10-SQL-JOINs.md)
**Definition:** Combining rows from tables on a matching condition (inner, left, right, full, cross, self).
**Simple explanation:** Joins reconnect facts that normalization split apart.
**Small example:** A filter on the right table in `WHERE` turns a `LEFT JOIN` into an inner join; put it in `ON` to keep unmatched rows.

### [Subqueries](11-Subqueries.md)
**Definition:** A query nested inside another, either independent or correlated to the outer row.
**Simple explanation:** Answer a smaller question first, then use the answer.
**Small example:** `LEFT JOIN LATERAL (SELECT ... WHERE o.customer_id = c.id ORDER BY created_at DESC LIMIT 3)` gives each customer's latest three orders.

### [EXISTS vs IN](12-EXISTS-vs-IN.md)
**Definition:** Two ways to express a semi-join ("rows that have a match"); `NOT EXISTS` and `NOT IN` express anti-joins.
**Simple explanation:** They usually perform the same today, but `NOT IN` gives wrong answers when NULLs appear.
**Small example:** `WHERE id NOT IN (SELECT customer_id FROM orders)` returns nothing if any `customer_id` is NULL; `NOT EXISTS` works.

### [Aggregate Functions](13-Aggregate-Functions.md)
**Definition:** Functions like `COUNT`, `SUM`, `AVG`, `json_agg` that collapse many rows into one per group.
**Simple explanation:** `GROUP BY` buckets rows; aggregates summarize each bucket.
**Small example:** `COUNT(*) FILTER (WHERE status = 'cancelled')` counts cancellations alongside total orders in one pass.

### [Window Functions](14-Window-Functions.md)
**Definition:** Functions computed over a set of rows related to the current row, without collapsing them.
**Simple explanation:** Like an aggregate that keeps every row and adds a column.
**Small example:** `SUM(total_cents) OVER (PARTITION BY customer_id ORDER BY created_at)` is each customer's running spend.

### [Common Table Expressions](15-Common-Table-Expressions.md)
**Definition:** Named subqueries defined with `WITH`, including recursive ones.
**Simple explanation:** Break a big query into readable steps; use recursion to walk trees.
**Small example:** A recursive CTE over `categories(parent_id)` builds "Electronics › Phones › Android".

### [Views](16-Views.md)
**Definition:** A stored query that behaves like a table but stores no data.
**Simple explanation:** A saved, named `SELECT` you can grant access to.
**Small example:** Keep a view with the old column names while the table is migrated, so old app versions keep working.

### [Materialized Views](17-Materialized-Views.md)
**Definition:** A view whose results are stored and must be refreshed explicitly.
**Simple explanation:** A precomputed report that is fast to read and slightly stale.
**Small example:** `REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue` every 5 minutes; needs a unique index; readers are not blocked.

### [Stored Procedures and Functions](18-Stored-Procedures-and-Functions.md)
**Definition:** Code (SQL or PL/pgSQL) stored and executed inside the database; procedures may also control transactions.
**Simple explanation:** Run logic next to the data — powerful, but harder to test, version and scale.
**Small example:** A trigger function sets `updated_at = now()` on every update so no code path can forget it.

## Performance

### [Indexes](19-Indexes.md)
**Definition:** Auxiliary sorted (or hashed/inverted) structures that let the database find rows without scanning the table.
**Simple explanation:** A book index: fast to look things up, but it must be updated whenever the book changes.
**Small example:** PostgreSQL doesn't index foreign keys automatically — `orders.customer_id` needs its own index.

### [Composite Indexes](20-Composite-Indexes.md)
**Definition:** An index on several columns, usable for queries that filter on a leftmost prefix of those columns.
**Simple explanation:** Like a phone book sorted by last name, then first name.
**Small example:** `(customer_id, created_at DESC)` serves `WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 20` without a sort.

### [Covering Indexes](21-Covering-Indexes.md)
**Definition:** An index that contains every column a query needs, enabling an index-only scan.
**Simple explanation:** The answer is in the index itself, so the table is never touched.
**Small example:** `CREATE INDEX ON orders (customer_id) INCLUDE (status, total_cents)`; a freshly vacuumed table shows `Heap Fetches: 0`.

### [Query Execution Plans](22-Query-Execution-Plans.md)
**Definition:** The tree of operations the planner chose to run a query, shown by `EXPLAIN`.
**Simple explanation:** The database's recipe — and `ANALYZE` shows how long each step really took.
**Small example:** Estimated 10 rows but actual 200,000 means stale or missing statistics — run `ANALYZE` first.

### [Query Optimization](23-Query-Optimization.md)
**Definition:** A repeatable process to find the queries that cost the most and make them cheaper.
**Simple explanation:** Measure, read the plan, fix one thing, measure again.
**Small example:** `pg_stat_statements` ordered by `total_exec_time` shows the query worth fixing first — often a fast query run millions of times.

### [Offset Pagination](24-Offset-Pagination.md)
**Definition:** Paging with `LIMIT n OFFSET k`.
**Simple explanation:** Simple and allows "go to page 50", but the database still reads the skipped rows.
**Small example:** `OFFSET 100000` reads 100,020 rows to return 20; cap the page number for public APIs.

### [Cursor Pagination](25-Cursor-Pagination.md)
**Definition:** Keyset paging that continues after the last row seen, using the sort key.
**Simple explanation:** "Give me the next 20 after this one" — every page costs the same.
**Small example:** `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT 20`, with `id` as a tie-breaker.

### [Query Anti-Patterns](26-Query-Anti-Patterns.md)
**Definition:** Common query shapes that are slow or wrong at scale.
**Simple explanation:** Patterns that look fine with 100 rows and fall over with 10 million.
**Small example:** `WHERE date(created_at) = '2026-11-24'` cannot use an index on `created_at`; use a half-open range instead.

## Correctness under concurrency

### [Transactions](27-Transactions.md)
**Definition:** A group of statements that commit together or not at all, on one connection.
**Simple explanation:** All-or-nothing — and it must all happen on the same connection.
**Small example:** In node-postgres, `pool.query()` for each statement may use different connections; use `const client = await pool.connect()` for a transaction.

### [ACID](28-ACID.md)
**Definition:** Atomicity, Consistency, Isolation, Durability — the guarantees of a database transaction.
**Simple explanation:** All or nothing; rules hold; concurrent work doesn't interfere badly; committed means saved.
**Small example:** PostgreSQL makes a commit durable by flushing the WAL record; `synchronous_commit = off` trades a few lost commits on crash for speed.

### [Isolation Levels](29-Isolation-Levels.md)
**Definition:** Settings that decide which concurrency anomalies a transaction may see.
**Simple explanation:** Higher isolation means fewer surprises and more retries or waiting.
**Small example:** PostgreSQL's `REPEATABLE READ` still allows write skew; `SERIALIZABLE` prevents it but can fail with `40001`, so retry.

### [Database Locks](30-Database-Locks.md)
**Definition:** Row-, table- and advisory-level locks that control concurrent access to data.
**Simple explanation:** Locks make others wait; MVCC means readers usually don't.
**Small example:** `SELECT ... FOR UPDATE SKIP LOCKED LIMIT 10` lets many workers claim different jobs from one table.

### [Deadlocks](31-Deadlocks.md)
**Definition:** Two or more transactions each waiting for a lock the other holds.
**Simple explanation:** A circular wait; the database breaks it by aborting one transaction.
**Small example:** Lock order rows with `ORDER BY id FOR UPDATE` in every code path, and retry on SQLSTATE `40P01`.

### [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md)
**Definition:** Pessimistic locks rows before changing them; optimistic detects conflicting changes at write time.
**Simple explanation:** Pessimistic = "reserve it first"; optimistic = "check nobody changed it when I save".
**Small example:** `UPDATE inventory SET available = $1, version = version + 1 WHERE product_id = $2 AND version = $3` — 0 rows means retry.

## Working with databases from code

### [ORM Fundamentals](33-ORM-Fundamentals.md)
**Definition:** Libraries that map rows to objects, track changes, and generate SQL.
**Simple explanation:** Productive for everyday CRUD, but you must still know the SQL it sends.
**Small example:** Loading 50 orders then touching `order.items` lazily makes 51 queries; use `selectinload` (SQLAlchemy) or `include` (Prisma).

### [Database Migrations](34-Database-Migrations.md)
**Definition:** Versioned, ordered scripts that evolve the schema and data in every environment.
**Simple explanation:** Git history for your database — applied automatically, in order, once.
**Small example:** Rename a column with expand → backfill → switch reads → contract, across several deploys, never in one step.

### [MongoDB Fundamentals](35-MongoDB-Fundamentals.md)
**Definition:** A document database storing BSON documents in collections, with secondary indexes, aggregation, replication and transactions.
**Simple explanation:** Store an object as one document; a single-document update is always atomic.
**Small example:** `updateOne({ _id, stock: { $gte: 2 } }, { $inc: { stock: -2 } })` decrements stock without overselling.

### [Document Modeling](36-Document-Modeling.md)
**Definition:** Designing document structure from access patterns, choosing between embedding and referencing.
**Simple explanation:** Store together what you read together, but never let an array grow without limit.
**Small example:** An order embeds a snapshot of its items; product reviews live in their own collection, with the 10 most recent embedded in the product.

## How to revise

1. Read each **Definition** line aloud.
2. Explain the example without looking — then say what breaks if you do it the naive way.
3. Open the linked chapter when you cannot explain the trade-off.

## Related module resources

- [Module overview](README.md)
- [Module summary](module-summary.md)
- [Interview questions](interview_questions.md)
- [Practical tasks](tasks.md)

# Indexes

> **Module 03 · Databases** · Prerequisites: [Stored Procedures and Functions](18-Stored-Procedures-and-Functions.md) · Next: [Composite Indexes](20-Composite-Indexes.md)

---

## ⏱ If You Only Have 2 Minutes

- An index is a separate, sorted structure that maps key values to row locations. It speeds up the reads that match it, and it slows down every `INSERT`, most `UPDATE`s and adds disk space and WAL volume.
- A PostgreSQL B-tree lookup reads one page per level (usually 3–4 levels, even for tens of millions of rows), then follows a tuple ID (TID) to the row in the **heap**. The index has no visibility information, so the heap visit is normally still needed.
- The planner uses an index only when the predicate is **selective** enough. Reading 30% of a table through an index is slower than one sequential scan, so "the index was ignored" is often the right decision.
- PostgreSQL creates indexes for `PRIMARY KEY` and `UNIQUE`, but **never for foreign-key columns**. An unindexed FK makes joins slow and makes every delete on the parent table scan the child table.
- Pick the type by operator: B-tree for `=`, ranges and `ORDER BY`; GIN for JSONB, arrays and full-text; GiST/SP-GiST for geometry, ranges and nearest-neighbour; BRIN for huge, naturally ordered tables; Hash only for pure equality.
- Partial indexes (`WHERE status = 'pending'`) index only the rows you query. Expression indexes (`lower(email)`) only help queries that use the exact same expression.
- On a live table use `CREATE INDEX CONCURRENTLY`: it does not block writes, cannot run inside a transaction, and leaves an `INVALID` index behind if it fails.
- Find dead weight with `pg_stat_user_indexes.idx_scan = 0`, but check every replica and never drop an index that enforces uniqueness.

---

## 1. What It Is and Why It Exists

An **index** is an extra data structure that keeps a copy of one or more columns in sorted (or otherwise searchable) order, with a pointer back to each row. The database maintains it automatically on every write. The planner decides on its own whether to use it for a read.

**Analogy:** the index at the back of a textbook. To find "deadlock" you do not read all 600 pages. You look it up alphabetically, get page numbers, and turn straight to them. But every time the author adds a page, someone has to update the index too, and the index itself takes up paper.

**The problem it solves.** In the sample schema, `orders.customer_id` has no index. The "My orders" page runs:

```sql
SELECT id, status, total_cents, created_at
FROM orders
WHERE customer_id = $1
ORDER BY created_at DESC
LIMIT 20;
```

With 10 million orders (about 85,000 pages of 8 KB, roughly 700 MB) PostgreSQL has no choice but to read **every page** and throw away 99.9998% of the rows. That takes hundreds of milliseconds per request and pushes useful data out of the cache. Fifty users opening the page at once is enough to saturate the database's disks and CPUs. With an index on `customer_id`, the same query reads about two dozen pages and finishes in a fraction of a millisecond.

**The cost.** An index is not free storage. Each one must be updated on writes, takes space on disk and in memory, generates WAL (write-ahead log) that replicas must replay, and must be vacuumed. The job is not "add indexes", it is "add the few indexes that the real queries need".

---

## 2. How It Works

### Heap, pages and TIDs

A PostgreSQL table is a **heap**: a file of 8 KB pages with rows stored in no particular order. Each row version has a physical address called a **TID** (tuple ID): `(page number, item number on the page)`, for example `(51200, 3)`. An index entry is simply `(key value, TID)`.

Because of MVCC (multi-version concurrency control), an `UPDATE` writes a *new* row version with a new TID and leaves the old one until VACUUM removes it. The index does not store which transaction can see which version. That is why an index scan normally still visits the heap: to check that the row version is visible to the current snapshot. (The exception, index-only scans, is covered in [Covering Indexes](21-Covering-Indexes.md).)

MySQL InnoDB is different: the table itself *is* a B-tree ordered by the primary key (a **clustered index**), and secondary indexes store the primary key instead of a physical address.

### Walking a B-tree

The default index type is a **B-tree** (strictly, a B+-tree in the Lehman–Yao style). It has three kinds of pages:

- **Root and internal pages** hold separator keys and downlinks to child pages.
- **Leaf pages** hold every `(key, TID)` entry in sorted order. Each leaf links to its left and right neighbours, so a range scan walks sideways without going back up.

One 8 KB page holds hundreds of small keys (the **fan-out**). Three levels of fan-out 300 already address 27 million entries, so the tree is shallow and the upper levels are almost always in memory.

```mermaid
flowchart TD
    Q["WHERE customer_id = 4217"] --> R["Root page: separators 150000, 300000, 450000"]
    R -->|"4217 < 150000"| I["Internal page: separators 4100, 4300, 4500"]
    I -->|"4100 <= 4217 < 4300"| L["Leaf page: (4217, TID 51200/3), (4217, TID 51987/7), ..."]
    L -->|"more 4217 entries continue on the right sibling"| L2["Next leaf page"]
    L --> H1["Heap page 51200, item 3: visible? return row"]
    L --> H2["Heap page 51987, item 7: visible? return row"]
```

A lookup for `customer_id = 4217`:

1. Read the metapage to find the root, then binary-search the root page for the right downlink.
2. Repeat on each internal page until reaching a leaf.
3. Binary-search the leaf for the first `4217` entry and read entries while the key still matches, following the right-link if the run continues on the next leaf.
4. For each TID, read the heap page, check visibility, apply any remaining filters, and return the row.

Step 4 is the expensive part. A customer's 21 orders were created over three years, so they sit on 21 different heap pages. Twenty-one random page reads is fine. Two million is not, which is why selectivity matters.

### What a write costs

| Operation | Work per index |
|---|---|
| `INSERT` | Descend the tree and insert one entry; split a page if it is full. Each insert is also WAL-logged. |
| `UPDATE` | A new row version usually needs a new entry **in every index** on the table, even indexes on columns that did not change. The exception is a **HOT update** (heap-only tuple): if no indexed column changed and the new version fits on the same heap page, no index is touched. |
| `DELETE` | Nothing immediately. VACUUM later removes the dead entries. |

So a table with eight indexes turns one `UPDATE` into up to nine page modifications plus their WAL. Every extra index also makes HOT updates less likely, because more columns count as "indexed".

### When the planner uses an index (selectivity)

**Selectivity** is the fraction of rows a predicate keeps. `customer_id = 4217` keeps 21 of 10 million rows: very selective. `status = 'shipped'` might keep 80%: barely selective at all.

The planner estimates selectivity from statistics gathered by `ANALYZE` (most common values, histograms, distinct counts) and compares costs. By default a random page read (`random_page_cost = 4.0`) costs four times a sequential one (`seq_page_cost = 1.0`). Fetching a large fraction of the table through an index means many random reads, often of the same pages again, so a sequential scan wins. There is no fixed percentage cut-off; it depends on row width, how well the physical order matches the index order (**correlation**), and what is cached.

The planner has three ways to use a B-tree:

- **Index Scan**: walk the index and visit the heap in index order. Best for few rows or when the order is needed for `ORDER BY ... LIMIT`.
- **Bitmap Index Scan + Bitmap Heap Scan**: collect all matching TIDs first, sort them by page, then read each heap page once. Best for "medium" result sets, and it can combine several indexes with `BitmapAnd`/`BitmapOr`.
- **Index Only Scan**: answer from the index alone when it holds every needed column (chapter 21).

---

## 3. Key Concepts

### Index types and when each fits

| Type | Structure | Operators it serves | Fits | Avoid when |
|---|---|---|---|---|
| **B-tree** (default) | Balanced sorted tree | `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, `IN`, `IS NULL`, `ORDER BY`, `LIKE 'abc%'` (with `C` collation or `text_pattern_ops`) | Almost everything: IDs, foreign keys, timestamps, emails | You search *inside* values (JSON keys, words, `%abc%`) |
| **Hash** | Hash buckets | `=` only | Equality on long values, where a hash is smaller than the key | You need ranges, ordering, uniqueness or multiple columns (none supported). WAL-logged only since PostgreSQL 10. |
| **GIN** (generalized inverted index) | Map from each element to the rows containing it | JSONB `@>`, `?`; array `@>`, `&&`; full-text `@@`; trigram `LIKE '%abc%'` with `pg_trgm` | `products.attributes @> '{"color":"red"}'`, tags, search | Very write-heavy columns: one row can add many entries. Updates go to a pending list (`fastupdate`) to soften this. |
| **GiST** (generalized search tree) | Balanced tree of bounding predicates | Geometry and range overlap (`&&`), containment, nearest-neighbour `ORDER BY location <-> point` | PostGIS, `tstzrange` bookings, exclusion constraints | Plain scalar equality: B-tree is smaller and faster |
| **SP-GiST** (space-partitioned GiST) | Unbalanced partitioning trees (quad-tree, k-d tree, radix tree) | Points, `inet`/`cidr`, text prefixes, ranges | Data that splits naturally into non-overlapping regions, such as IP address lookups | Data without natural partitions |
| **BRIN** (block range index) | Min/max summary per range of heap pages (128 pages by default) | `=`, ranges | Huge append-only tables where the column follows physical order (`created_at` on an event log). Often a thousand times smaller than a B-tree. | Columns whose values are scattered across the table: every range then "might match" and BRIN reads everything |

The interview shortcut: **B-tree unless the operator is not a comparison.** Then GIN for "contains", GiST for "overlaps / nearest", BRIN for "enormous and time-ordered".

### Unique indexes

`PRIMARY KEY` and `UNIQUE` constraints are implemented as unique B-tree indexes, created automatically. A unique index is the only race-free way to guarantee "no two customers share an email": two concurrent inserts cannot both pass, while an application-level "SELECT then INSERT" check can.

By default `NULL`s are distinct, so a unique column can hold many `NULL`s (that is why `payments.provider_ref` can be `NULL` on many rows). PostgreSQL 15 added `UNIQUE NULLS NOT DISTINCT` when you want at most one `NULL`.

### Partial indexes

A **partial index** has a `WHERE` clause and only contains matching rows:

```sql
CREATE INDEX orders_pending_created_idx ON orders (created_at) WHERE status = 'pending';
```

If only 0.2% of orders are pending, this index is tiny, stays in memory, and is not touched when shipped orders change. It is ideal for work queues ("oldest pending orders first"). Two rules matter:

- The query's `WHERE` must **imply** the index predicate, and the planner checks this **at planning time**. `WHERE status = 'pending'` matches. `WHERE status = $1` does not match in a generic prepared plan, because the planner cannot know `$1` will be `'pending'`. Write the literal in the SQL for queries meant to use a partial index.
- A **partial unique index** enforces a rule for a subset: `CREATE UNIQUE INDEX ON payments (order_id) WHERE status = 'captured'` allows many failed payments per order but only one captured payment.

### Expression indexes

An index can be built on an expression instead of a column:

```sql
CREATE UNIQUE INDEX customers_email_lower_key ON customers (lower(email));
SELECT id FROM customers WHERE lower(email) = lower($1);
```

The query must use the **same expression**. `WHERE email = $1` will not use this index, and `WHERE lower(email) = $1` without lowering the parameter returns wrong results for mixed-case input. The function must be `IMMUTABLE` (same input, same output forever), which is why you cannot index `created_at::date` on a `timestamptz` column: the result depends on the session time zone. Run `ANALYZE` after creating an expression index so the planner gathers statistics on the expression.

### Foreign keys are not indexed automatically

PostgreSQL indexes the *referenced* side (the parent's primary key) but not the *referencing* column. In the sample schema that leaves three gaps:

| FK column | Indexed? | Why |
|---|---|---|
| `orders.customer_id` | No | The deliberate gap |
| `order_items.order_id` | Yes | It is the first column of the primary key `(order_id, product_id)` |
| `order_items.product_id` | No | Second column of the PK; a B-tree cannot search efficiently on a non-leading column |
| `payments.order_id` | No | Nothing indexes it |

An unindexed FK hurts twice. Joins and lookups by that column scan the child table. And every `DELETE` (or key `UPDATE`) on the parent must check the child for referencing rows, which means a sequential scan of `orders` for each deleted customer, while holding locks. MySQL InnoDB creates an index on FK columns automatically if none exists; PostgreSQL leaves the decision to you.

### Building and retiring indexes safely

- **Plain `CREATE INDEX`** takes a `SHARE` lock: reads continue, but every `INSERT`, `UPDATE` and `DELETE` on the table waits until the build finishes. On a 10-million-row table that can be minutes of checkout downtime.
- **`CREATE INDEX CONCURRENTLY`** takes a weaker lock that allows writes. It scans the table twice and waits for older transactions to finish, so it is slower and uses more I/O. It **cannot run inside a transaction block**, so migration tools need that migration marked as non-transactional (see [Database Migrations](34-Database-Migrations.md)). If it fails (a deadlock, a uniqueness violation, a cancelled session) it leaves an **`INVALID`** index that is not used for reads but is still updated on every write. Drop it with `DROP INDEX CONCURRENTLY` and retry. Progress is visible in `pg_stat_progress_create_index` (PostgreSQL 12+).
- **Unused indexes**: `pg_stat_user_indexes.idx_scan` counts scans since statistics were last reset. PostgreSQL 16 added `last_idx_scan`. Counters are per server, so an index that only serves queries on a read replica shows `0` on the primary.

---

## 4. Code Examples

### SQL

Fix the deliberate gap, then add the two other indexes this chapter motivates. Each statement runs on its own (not inside `BEGIN`), because `CONCURRENTLY` refuses to run in a transaction block.

```sql
-- Writes keep flowing during the build; reads switch to the index once it is valid.
CREATE INDEX CONCURRENTLY orders_customer_id_idx ON orders (customer_id);

-- Work queue: only pending rows are indexed, so the index stays small and hot.
CREATE INDEX CONCURRENTLY orders_pending_created_idx
  ON orders (created_at) WHERE status = 'pending';

-- Case-insensitive login. Fails if existing emails differ only by case: clean those first.
CREATE UNIQUE INDEX CONCURRENTLY customers_email_lower_key ON customers (lower(email));
ANALYZE customers;  -- gathers statistics for the lower(email) expression

-- A failed CONCURRENTLY build leaves an INVALID index behind. Check after every migration.
SELECT indexrelid::regclass AS invalid_index FROM pg_index WHERE NOT indisvalid;

-- Single-column foreign keys whose column does not lead any index.
SELECT c.conrelid::regclass AS table_name, a.attname AS fk_column, c.conname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND array_length(c.conkey, 1) = 1
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND i.indkey[0] = c.conkey[1]
  );
-- Against the sample schema: order_items.product_id, payments.order_id
-- (and orders.customer_id before the first statement above).

-- Indexes never scanned on THIS server since the last stats reset, biggest first.
SELECT s.relname AS table_name, s.indexrelname AS index_name, s.idx_scan, s.last_idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0 AND NOT i.indisunique   -- unique indexes enforce rules even if never read
ORDER BY pg_relation_size(s.indexrelid) DESC;
```

The "My orders" query before the index (10 million orders, customer 4217 has 21 of them). Illustrative output:

```text
Limit  (cost=138417.92..138420.14 rows=19 width=29) (actual time=612.408..618.951 rows=20 loops=1)
  Buffers: shared hit=2241 read=83093
  ->  Gather Merge  (cost=138417.92..138420.14 rows=19 width=29) (actual time=612.405..618.944 rows=20 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        Buffers: shared hit=2241 read=83093
        ->  Sort  (cost=137417.90..137417.92 rows=8 width=29) (actual time=596.112..596.114 rows=7 loops=3)
              Sort Key: created_at DESC
              Sort Method: quicksort  Memory: 25kB
              ->  Parallel Seq Scan on orders  (cost=0.00..137417.71 rows=8 width=29) (actual time=41.270..596.051 rows=7 loops=3)
                    Filter: (customer_id = 4217)
                    Rows Removed by Filter: 3333326
                    Buffers: shared hit=2241 read=83093
Planning Time: 0.162 ms
Execution Time: 619.012 ms
```

Three processes (the leader and two workers) each read a third of the 85,334 pages, and together they discard almost 10 million rows to find 21. After `orders_customer_id_idx` exists (illustrative output):

```text
Limit  (cost=84.71..84.76 rows=20 width=29) (actual time=0.112..0.116 rows=20 loops=1)
  Buffers: shared hit=24
  ->  Sort  (cost=84.71..84.76 rows=21 width=29) (actual time=0.111..0.113 rows=20 loops=1)
        Sort Key: created_at DESC
        Sort Method: quicksort  Memory: 27kB
        ->  Index Scan using orders_customer_id_idx on orders  (cost=0.43..84.25 rows=21 width=29) (actual time=0.019..0.094 rows=21 loops=1)
              Index Cond: (customer_id = 4217)
              Buffers: shared hit=24
Planning Time: 0.201 ms
Execution Time: 0.139 ms
```

Three index pages plus 21 heap pages. The query still sorts all of the customer's orders to return 20. That is fine for 21 rows and slow for a customer with 30,000; [Composite Indexes](20-Composite-Indexes.md) removes the sort.

### Node.js / TypeScript

An integration test that acts as a **plan guard**: it fails the build if a critical query would scan the whole `orders` table. It runs against a test database built from the real migrations, so it catches a migration that drops or renames an index.

A tiny test database is a trap: with 50 rows, a sequential scan is genuinely cheapest, so a naive check would always fail (or you would learn to ignore it). The guard sets `enable_seqscan = off` inside a rolled-back transaction. That does not forbid sequential scans; it makes them so expensive that the planner chooses one only when **no usable index exists**, which is exactly the regression to catch.

```ts
// npm i pg ; npm i -D @types/pg tsx typescript   — run: npx tsx --test plan-guard.test.ts
import { test, after } from "node:test";
import assert from "node:assert/strict";
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.TEST_DATABASE_URL });
after(() => pool.end());

interface PlanNode {
  "Node Type": string;
  "Relation Name"?: string;
  "Index Name"?: string;
  "Index Cond"?: string;
  Plans?: PlanNode[];
}

// The queries whose speed the product depends on, with realistic parameters.
const CRITICAL: Record<string, { sql: string; params: unknown[] }> = {
  "orders for a customer": {
    sql: `SELECT id, status, total_cents, created_at FROM orders
          WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 20`,
    params: [1],
  },
  // Literal 'pending' (not $1) so the planner can prove the partial index applies.
  "pending order queue": {
    sql: `SELECT id FROM orders WHERE status = 'pending' ORDER BY created_at LIMIT 100`,
    params: [],
  },
};

function* walk(node: PlanNode): Generator<PlanNode> {
  yield node;
  for (const child of node.Plans ?? []) yield* walk(child);
}

async function explain(sql: string, params: unknown[]): Promise<PlanNode> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("SET LOCAL enable_seqscan = off"); // reverted by the ROLLBACK below
    const { rows } = await client.query(`EXPLAIN (FORMAT JSON) ${sql}`, params);
    const raw = rows[0]["QUERY PLAN"];
    const doc = typeof raw === "string" ? JSON.parse(raw) : raw; // pg already parses json columns
    return doc[0].Plan as PlanNode;
  } finally {
    await client.query("ROLLBACK");
    client.release();
  }
}

for (const [name, { sql, params }] of Object.entries(CRITICAL)) {
  test(`plan guard: ${name}`, async () => {
    const plan = await explain(sql, params);
    const offenders = [...walk(plan)].filter(
      (n) =>
        n["Relation Name"] === "orders" &&
        (n["Node Type"] === "Seq Scan" ||
          // With seq scans penalised, a full walk of an unrelated index (no Index Cond) is the disguise.
          (n["Node Type"].startsWith("Index") && !n["Index Cond"])),
    );
    assert.equal(offenders.length, 0, `full scan of orders:\n${JSON.stringify(plan, null, 2)}`);
  });
}
```

The second condition matters. When sequential scans are penalised and no `customer_id` index exists, the planner can "escape" by reading the *entire* primary-key index and filtering every row. That is just as slow as a sequential scan, but the node type says `Index Scan`. A scan with no `Index Cond` is a full scan in disguise.

### Python

The same guard as a pytest module. psycopg 3 binds parameters on the server, so `EXPLAIN` receives real values, the same way the application's queries do.

```python
# pip install "psycopg[binary]" pytest   — Python 3.12+; run: pytest test_plan_guard.py
import json
import os
from collections.abc import Iterator

import psycopg
import pytest

DSN = os.environ.get("TEST_DATABASE_URL", "postgresql://postgres:dev@localhost:5432/shop_test")

CRITICAL: dict[str, tuple[str, tuple]] = {
    "orders for a customer": (
        "SELECT id, status, total_cents, created_at FROM orders "
        "WHERE customer_id = %s ORDER BY created_at DESC LIMIT 20",
        (1,),
    ),
    # Literal 'pending' so the planner can prove the partial index's predicate holds.
    "pending order queue": (
        "SELECT id FROM orders WHERE status = 'pending' ORDER BY created_at LIMIT 100",
        (),
    ),
}


def walk(node: dict) -> Iterator[dict]:
    yield node
    for child in node.get("Plans", []):
        yield from walk(child)


def is_full_scan_of_orders(node: dict) -> bool:
    if node.get("Relation Name") != "orders":
        return False
    if node["Node Type"] == "Seq Scan":
        return True
    # An index scan without an Index Cond reads the whole index: a seq scan in disguise.
    return node["Node Type"].startswith("Index") and "Index Cond" not in node


@pytest.fixture(scope="module")
def conn() -> Iterator[psycopg.Connection]:
    with psycopg.connect(DSN, autocommit=True) as c:
        yield c


@pytest.mark.parametrize("name", CRITICAL)
def test_plan_guard(conn: psycopg.Connection, name: str) -> None:
    sql, params = CRITICAL[name]
    # force_rollback undoes SET LOCAL so other tests see default planner settings.
    with conn.transaction(force_rollback=True):
        conn.execute("SET LOCAL enable_seqscan = off")
        raw = conn.execute("EXPLAIN (FORMAT JSON) " + sql, params).fetchone()[0]
    doc = json.loads(raw) if isinstance(raw, str) else raw  # psycopg loads json by default
    plan = doc[0]["Plan"]
    offenders = [n for n in walk(plan) if is_full_scan_of_orders(n)]
    assert not offenders, f"{name} scans all of orders:\n{json.dumps(plan, indent=2)}"
```

**Runtime difference to notice:** node-postgres sends a query with no `name` as an unnamed statement, so each `EXPLAIN` is planned with the actual parameter values. psycopg 3 automatically *prepares* a statement after it has run five times (`prepare_threshold`, default 5), and PostgreSQL may then switch to a generic plan that ignores parameter values. The guard runs each query once, so both behave the same here, but remember the difference when a production query is slower than its `EXPLAIN` suggests.

---

## 5. Production Concerns

- **Write amplification.** Count indexes on hot write tables. `orders` takes an `INSERT` per checkout and two or three status `UPDATE`s afterwards. Every index adds work and WAL to each of those, and WAL volume drives replica lag and backup size. Watch `n_tup_hot_upd` vs `n_tup_upd` in `pg_stat_user_tables`: if HOT updates drop after a new index, that index covers a column you update often.
- **Building on a live table.** `CREATE INDEX CONCURRENTLY` still reads the whole table twice and writes the whole index, so it competes for I/O and generates a burst of WAL that replicas must replay. It waits for every transaction older than itself, so one forgotten open transaction stalls the build indefinitely. Run it off-peak, watch `pg_stat_progress_create_index`, and alert on `INVALID` indexes after deploys.
- **Memory.** Indexes compete with table data for `shared_buffers` and the OS page cache. A query whose index fits in memory is fast. Ten unused indexes on a hot table steal that memory from the ones that matter. Check sizes with `pg_relation_size` and remove dead weight.
- **Dropping safely.** Before dropping an index with `idx_scan = 0`, check the counter on **every** replica, make sure statistics were not recently reset, and cover a full business cycle (month-end reports use indexes nobody touches on a Tuesday). Use `DROP INDEX CONCURRENTLY`. Keep the `CREATE` statement ready to roll back.
- **Bloat.** Heavy update and delete traffic leaves dead entries and half-empty pages. Autovacuum removes dead entries but does not shrink the file. `REINDEX INDEX CONCURRENTLY` (PostgreSQL 12+) rebuilds a bloated index without blocking writes.
- **What to measure.** Per critical query: rows read vs rows returned (`pg_stat_statements` gives `rows` and block counts). Per table: `seq_scan` and `seq_tup_read` in `pg_stat_user_tables`. A large table with a rising `seq_tup_read` is usually a missing index, often an FK.

---

## 6. Common Mistakes

- **Assuming foreign keys are indexed** — joins on `orders.customer_id` scan the table, and deleting a customer scans `orders` while holding locks — index every FK column you join or delete through, and run the "unindexed FK" query in CI.
- **Indexing every column "just in case"** — writes slow down, HOT updates disappear, and memory fills with unused indexes — index measured query shapes only, and review `idx_scan` quarterly.
- **Wrapping the indexed column in a function** — `WHERE lower(email) = $1` or `WHERE created_at::date = $1` cannot use a plain index on the column — rewrite as a range on the bare column, or create a matching expression index (details in [Query Anti-Patterns](26-Query-Anti-Patterns.md)).
- **Plain `CREATE INDEX` in a production migration** — the build blocks all writes to the table for minutes — use `CREATE INDEX CONCURRENTLY` in a non-transactional migration.
- **Ignoring a failed concurrent build** — the `INVALID` index is never used for reads but slows every write — query `pg_index WHERE NOT indisvalid` after migrations and drop leftovers.
- **Parameterising a partial index's predicate** — `WHERE status = $1` cannot be proven to match `WHERE status = 'pending'`, so the partial index is skipped once a generic plan is used — keep the literal in the SQL.
- **Expecting an index to help a low-selectivity filter** — an index on `status` alone is ignored for `status = 'shipped'` (80% of rows) — use a partial index on the rare value, or combine the column with a selective one ([Composite Indexes](20-Composite-Indexes.md)).

---

## 7. Comparison Table

How indexing differs between the two databases interviewers ask about most:

| | PostgreSQL | MySQL (InnoDB) |
|---|---|---|
| Table storage | Heap (unordered pages); every index points to a physical TID | Clustered B-tree ordered by primary key; the table *is* the PK index |
| Secondary index entry | `(key, TID)` | `(key, primary key columns)`; a lookup goes secondary index → PK index |
| FK columns | Not indexed automatically | Index created automatically if none exists |
| Index types | B-tree, Hash, GIN, GiST, SP-GiST, BRIN | B-tree; full-text and spatial (R-tree) indexes; adaptive hash index is internal |
| Partial indexes | Yes (`WHERE ...`) | No |
| Expression indexes | Yes | Functional key parts since 8.0.13 |
| Online build | `CREATE INDEX CONCURRENTLY` | Online DDL: `ALTER TABLE ... ADD INDEX ..., ALGORITHM=INPLACE, LOCK=NONE` |
| Test before dropping | Not built in | Invisible indexes (8.0): `ALTER TABLE ... ALTER INDEX ... INVISIBLE` |

---

## 8. Interview Questions

**[Junior] What is a database index, and why not index every column?**
An index is a separate sorted structure that maps column values to row locations, so the database can find matching rows without reading the whole table. Each index must be updated on inserts and most updates, uses disk and cache memory, and adds WAL that replicas must replay. Indexing every column makes writes slower and wastes memory on indexes that no query uses. You index the columns your real queries filter, join and sort on.

**[Junior] Does PostgreSQL create an index for a foreign key?**
No. It indexes the referenced primary key, not the referencing column. Without an index on `orders.customer_id`, "orders for this customer" scans the whole table, and deleting a customer forces a scan of `orders` to check for references. MySQL InnoDB, by contrast, creates the FK index automatically.

**[Mid] You added an index, but `EXPLAIN` still shows a Seq Scan. Why?**
Common reasons: the predicate matches a large fraction of rows, so a sequential scan is genuinely cheaper; the query wraps the column in a function or casts it, so the index does not apply; statistics are stale, so the planner misjudges selectivity (`ANALYZE` the table); the table is tiny; or the predicate is parameterised and does not match a partial index. Check the estimated vs actual rows in `EXPLAIN ANALYZE` before forcing anything.

**[Mid] When would you use a partial index, and when an expression index?**
A partial index fits when queries always target a small, fixed subset, such as `WHERE status = 'pending'` for a work queue: the index is tiny and unaffected by changes to other rows. It can also enforce uniqueness on a subset, such as one captured payment per order. An expression index fits when queries filter on a computed value, such as `lower(email)` for case-insensitive login; the query must use the identical expression and the function must be immutable.

**[Mid] Which index type for: email lookup, JSONB attribute filters, and a 2-billion-row event log queried by time range?**
Email: a unique B-tree, possibly on `lower(email)`. JSONB containment such as `attributes @> '{"color":"red"}'`: GIN, using `jsonb_path_ops` if you only need `@>` because it is smaller. The event log: BRIN on `created_at`, because rows arrive in time order, so each block range covers a narrow time window and the index is tiny compared with a B-tree on two billion rows.

**[Senior] How do you add an index to a 500-million-row table that takes writes all day?**
Use `CREATE INDEX CONCURRENTLY` in a migration that is not wrapped in a transaction, scheduled off-peak. It allows writes but scans the table twice, waits for all older transactions (so check for long-running ones first), and generates heavy I/O and WAL, which can lag replicas. Watch `pg_stat_progress_create_index`. If it fails, an `INVALID` index remains that still costs writes: drop it concurrently and retry. Confirm free disk space for the new index first, and verify with `EXPLAIN` that the target query uses it.

**[Senior] How do you decide which indexes to remove?**
Start from `pg_stat_user_indexes` with `idx_scan = 0`, ordered by size, and check `last_idx_scan` on PostgreSQL 16+. Collect the counters from every replica, because read-only reporting queries may run only there, and make sure the observation window covers rare jobs like month-end reports. Never drop unique or primary-key indexes, since they enforce constraints. Also look for indexes that are a leading prefix of another index (chapter 20). Drop with `DROP INDEX CONCURRENTLY`, one at a time, with the `CREATE` statement ready.

**[Senior] A write-heavy table has 12 indexes and update latency is rising. What do you check?**
Whether updates are still HOT: compare `n_tup_hot_upd` with `n_tup_upd`. Each index on a frequently updated column turns HOT updates into full updates that touch all 12 indexes. Then check which indexes are unused or redundant and remove them, look for bloat, and consider a lower `fillfactor` on the table so new row versions fit on the same page. The goal is the minimum set of indexes that serves the measured read paths.

---

## 9. Cheat Sheet

```text
Index entry      (key, TID) → heap page/item; heap visit still needed for MVCC visibility
B-tree           3–4 levels for 10^7–10^8 rows; leaves linked for range scans; default type
Scan kinds       Index Scan (few rows, ordered) | Bitmap (medium, page-sorted) | Seq Scan (many rows)
Cost knobs       random_page_cost 4.0 vs seq_page_cost 1.0 (defaults)
Write cost       INSERT: every index; UPDATE: every index unless HOT; DELETE: VACUUM cleans later
Types            B-tree =,<,>,ORDER BY | GIN contains (jsonb, arrays, FTS, trgm) | GiST overlap/KNN
                 SP-GiST points/inet/prefixes | BRIN huge + physically ordered | Hash = only
Unique           PK/UNIQUE create unique B-trees; NULLs distinct unless NULLS NOT DISTINCT (PG 15)
Partial          WHERE status = 'pending' — query must contain the literal predicate
Expression       (lower(email)) — query must use lower(email); function must be IMMUTABLE
FK columns       NOT indexed automatically in PostgreSQL (MySQL does it)
Live build       CREATE INDEX CONCURRENTLY — no transaction block; failure leaves INVALID index
Unused           pg_stat_user_indexes.idx_scan = 0 (check replicas; keep unique indexes)
Plan guard test  SET LOCAL enable_seqscan = off; fail on Seq Scan or Index Scan without Index Cond
```

---

## Related Topics

- [Composite Indexes](20-Composite-Indexes.md) — multi-column indexes, column order, and removing the sort from "My orders"
- [Covering Indexes](21-Covering-Indexes.md) — skipping the heap visit with index-only scans and `INCLUDE`
- [Query Execution Plans](22-Query-Execution-Plans.md) — reading the Seq Scan and Index Scan nodes shown above
- [Database Migrations](34-Database-Migrations.md) — shipping `CREATE INDEX CONCURRENTLY` in a non-transactional migration
- [Balanced Trees](../Module-05-Data-Structures-and-Algorithms/18-Balanced-Trees.md) — the data structure behind B-tree indexes
- [Query Anti-Patterns](26-Query-Anti-Patterns.md) — query shapes that stop an existing index from being used

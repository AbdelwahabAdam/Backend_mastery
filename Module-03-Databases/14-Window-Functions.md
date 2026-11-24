# Window Functions

> **Module 03 · Databases** · Prerequisites: [Aggregate Functions](13-Aggregate-Functions.md) · Next: [Common Table Expressions](15-Common-Table-Expressions.md)

---

## ⏱ If You Only Have 2 Minutes

- A window function computes a value **across a set of related rows but keeps every row**. `GROUP BY` collapses rows; `OVER (...)` does not.
- `OVER (PARTITION BY a ORDER BY b frame)`: the partition picks the related rows, the order sorts them, and the frame picks which of them an aggregate such as `sum` sees.
- **The default frame** when `ORDER BY` is present is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. It includes ties ("peers"), so a running total jumps on duplicate sort keys, and `last_value()` returns the current row, not the last row of the partition.
- `row_number()` = 1,2,3,4 (always unique) · `rank()` = 1,2,2,4 (gaps after ties) · `dense_rank()` = 1,2,2,3 (no gaps).
- `lag()` / `lead()` read the previous / next row in the partition. Use them for "time since previous order" or "change from last month" without a self-join.
- Window functions run **after** `WHERE`, `GROUP BY` and `HAVING`, so you cannot filter on them directly. Wrap the query in a subquery or CTE and filter there (`WHERE rn <= 3`).
- Top-N per group and de-duplication are both `row_number() OVER (PARTITION BY key ORDER BY preference)` + keep `rn = 1` (or `<= N`). Always add a unique tie-breaker to the `ORDER BY`.

---

## 1. What It Is and Why It Exists

A **window function** looks at a group of rows related to the current row — its *window* — and returns one value for the current row. Unlike an aggregate with `GROUP BY`, it does not merge the group into one output row. Every input row survives, and each one gets extra columns such as "my position in this customer's history" or "total spent so far".

**Analogy:** a bank statement. Each line is still a separate transaction, but the right-hand column shows the running balance. To compute that column you look back over earlier lines of the same account. You never collapse the statement into one "total" line.

**The problem it solves.** Before window functions (SQL:2003; PostgreSQL 8.4; MySQL 8.0), questions like these needed correlated subqueries or self-joins:

- "Show each order with the customer's spend up to that order."
- "Show the three best-selling products in each category."
- "Keep only the newest row per email in this import."
- "How many days since the customer's previous order?"

A correlated subquery for a running total re-scans earlier rows for every row, which is O(n²) per customer. A self-join multiplies rows and then needs `GROUP BY` to undo the damage. A window function does it in one pass over sorted input, and the query says what it means.

Without window functions, teams also pull all rows into application code and loop. That works until the result set is a million rows and the API server runs out of memory.

---

## 2. How It Works

### Where window functions run in a query

SQL is evaluated in a logical order. Window functions come late — after filtering and grouping, but before `DISTINCT`, the final `ORDER BY` and `LIMIT`.

```mermaid
flowchart LR
    A["FROM / JOIN"] --> B["WHERE"]
    B --> C["GROUP BY"]
    C --> D["HAVING"]
    D --> E["Window functions"]
    E --> F["SELECT list"]
    F --> G["DISTINCT"]
    G --> H["ORDER BY"]
    H --> I["LIMIT / OFFSET"]
```

Three consequences an interviewer will probe:

1. **You cannot use a window function in `WHERE`, `GROUP BY` or `HAVING`.** PostgreSQL only allows them in the `SELECT` list and the outer `ORDER BY`. To filter on `rn`, compute it in a subquery or CTE first.
2. **A window can run over aggregated rows.** `rank() OVER (ORDER BY sum(total_cents) DESC)` works, because grouping has already happened.
3. **`WHERE` changes the window.** Filtering `status = 'paid'` before the window means cancelled orders are not in the running total. That is usually what you want, but it is a decision.

### Anatomy of `OVER`

```sql
sum(total_cents) OVER (
  PARTITION BY customer_id                            -- which rows are related
  ORDER BY created_at, id                             -- how they are ordered inside the partition
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW    -- which of them the aggregate sees
)
```

- **`PARTITION BY`** splits rows into independent groups. With no `PARTITION BY`, the whole result is one partition.
- **`ORDER BY`** inside `OVER` orders rows within each partition. It is independent of the query's final `ORDER BY`.
- **Frame** — a sliding subset of the partition, relative to the current row. Only aggregate functions (`sum`, `avg`, `count`, `min`, `max`) and `first_value` / `last_value` / `nth_value` use the frame. Ranking functions and `lag` / `lead` always look at the whole partition.

### Execution

PostgreSQL implements this as a `WindowAgg` plan node. Its input must be sorted by the partition keys and then the order keys. That sort comes from a `Sort` node or from an index that already returns rows in that order. `WindowAgg` then walks the sorted rows once. For a running sum it keeps an accumulator and resets it at each partition boundary. If a query uses windows with different `PARTITION BY` / `ORDER BY`, the planner must sort more than once.

### The default frame and the `last_value` gotcha

The frame you get without writing one depends on whether the window has an `ORDER BY`:

| Window has… | Default frame | Effect |
|---|---|---|
| No `ORDER BY` | Whole partition | `sum(x) OVER (PARTITION BY c)` = partition total on every row |
| `ORDER BY` | `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | Running value up to and **including all peers** of the current row |

*Peers* are rows with equal `ORDER BY` values. In `RANGE` mode the frame ends at the last peer, so tied rows get the same running total.

Illustrative output — one customer, two orders at the same timestamp, `ORDER BY created_at` only:

| id | created_at | total_cents | `sum` default (RANGE) | `sum` with `ROWS` |
|---|---|---|---|---|
| 11 | 2026-01-05 10:00 | 2000 | 2000 | 2000 |
| 12 | 2026-01-09 14:30 | 1500 | **5000** | 3500 |
| 13 | 2026-01-09 14:30 | 1500 | 5000 | 5000 |
| 14 | 2026-02-01 09:15 | 4000 | 9000 | 9000 |

Neither column is "wrong", but the `ROWS` column depends on how the two tied rows happen to be ordered, so it can change between runs. Fix both problems by adding a unique tie-breaker (`ORDER BY created_at, id`). Then there are no peers and both modes agree.

The `last_value` gotcha follows from the same rule. With the default frame, the frame *ends at the current row*, so `last_value(total_cents) OVER (PARTITION BY customer_id ORDER BY created_at)` returns the current row's value (or its last peer's), not the customer's latest order. Ask for the whole partition explicitly:

```sql
last_value(total_cents) OVER (
  PARTITION BY customer_id ORDER BY created_at, id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
```

Or flip the sort and use `first_value(...) OVER (... ORDER BY created_at DESC, id DESC)`, which is easier to read.

---

## 3. Key Concepts

### Ranking functions

All three number rows inside a partition by the window's `ORDER BY`. They differ only on ties.

Illustrative output — one customer's orders sorted by `total_cents DESC`:

| total_cents | row_number() | rank() | dense_rank() |
|---|---|---|---|
| 5000 | 1 | 1 | 1 |
| 3000 | 2 | 2 | 2 |
| 3000 | 3 | 2 | 2 |
| 1000 | 4 | 4 | 3 |

| Function | Ties | Use it for |
|---|---|---|
| `row_number()` | Arbitrary but unique numbers | Top-N, de-duplication, pagination inside groups. Add a tie-breaker so results are deterministic |
| `rank()` | Same number, then a gap | Competition ranking ("joint 2nd, next is 4th") |
| `dense_rank()` | Same number, no gap | "Top 3 distinct price points" |
| `ntile(n)` | Splits rows into `n` near-equal buckets | Quartiles, deciles of customers by spend |
| `percent_rank()`, `cume_dist()` | Relative position from 0 to 1 | Percentiles in reports |

In PostgreSQL these return `bigint`, which matters for Node drivers (see section 4).

### Offset functions: `lag`, `lead`, `first_value`, `nth_value`

`lag(expr, offset = 1, default = NULL)` returns `expr` from the row `offset` rows before the current row in the partition. `lead` looks forward. They ignore the frame.

```sql
SELECT id, created_at,
       created_at - lag(created_at) OVER (PARTITION BY customer_id ORDER BY created_at, id) AS since_prev,
       lead(id) OVER (PARTITION BY customer_id ORDER BY created_at, id)                   AS next_order_id
FROM orders;
```

The first order of each customer has `since_prev = NULL`. Pass a default (`lag(created_at, 1, created_at)`) if you need a value there. `first_value`, `last_value` and `nth_value` respect the frame, which is why they are the usual victims of the default-frame gotcha.

### Frames: `ROWS`, `RANGE` and `GROUPS`

| Mode | Unit of the offset | Example | Good for |
|---|---|---|---|
| `ROWS` | Physical rows | `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` | "Average of the last 3 orders" |
| `RANGE` | Values of the single `ORDER BY` column | `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` | Calendar windows that must respect gaps (offsets need PostgreSQL 11+) |
| `GROUPS` | Groups of peers | `GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW` | "This value and the previous distinct value" (PostgreSQL 11+) |

The difference between `ROWS` and `RANGE` matters most for time series with missing days. On a table of daily revenue where some days have no row, `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` averages the last seven *rows*, which may span three weeks. `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` averages exactly the last seven *calendar days*. For a true daily series, generate the missing days first (`generate_series` + `LEFT JOIN`) so zero-revenue days count as zero instead of disappearing.

### Running totals and moving averages

```sql
-- Daily revenue with a running month-to-date total and a 7-day moving average.
WITH daily AS (
  SELECT date_trunc('day', created_at)::date AS day, sum(total_cents) AS revenue_cents
  FROM orders
  WHERE status IN ('paid', 'shipped')
  GROUP BY 1
)
SELECT day,
       revenue_cents,
       sum(revenue_cents) OVER (PARTITION BY date_trunc('month', day) ORDER BY day
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS mtd_cents,
       round(avg(revenue_cents) OVER (ORDER BY day
                                      RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW)) AS avg_7d_cents
FROM daily
ORDER BY day;
```

The `PARTITION BY date_trunc('month', day)` resets the running total on the first of each month. Partition keys can be expressions.

### Top-N per group

"Top 3 products by revenue in each category" — aggregate first, rank second, filter third:

```sql
SELECT category, product_id, name, revenue_cents
FROM (
  SELECT p.category, p.id AS product_id, p.name,
         sum(oi.quantity * oi.unit_price_cents) AS revenue_cents,
         row_number() OVER (PARTITION BY p.category
                            ORDER BY sum(oi.quantity * oi.unit_price_cents) DESC, p.id) AS rn
  FROM order_items oi
  JOIN products p ON p.id = oi.product_id
  GROUP BY p.category, p.id, p.name
) ranked
WHERE rn <= 3
ORDER BY category, rn;
```

Use `rank()` instead of `row_number()` if ties at position 3 should *all* be included. When there are few groups and an index matches the per-group sort, a `LATERAL` join with `LIMIT 3` can be faster, because it reads only three index entries per group instead of sorting everything (see [Subqueries](11-Subqueries.md)).

### De-duplication

An import loaded the same customer several times. Keep the newest row per normalized email and delete the rest:

```sql
CREATE TABLE customer_import (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email       text        NOT NULL,
  name        text        NOT NULL,
  country     char(2)     NOT NULL,
  imported_at timestamptz NOT NULL DEFAULT now()
);

DELETE FROM customer_import
WHERE id IN (
  SELECT id
  FROM (
    SELECT id,
           row_number() OVER (PARTITION BY lower(email) ORDER BY imported_at DESC, id DESC) AS rn
    FROM customer_import
  ) d
  WHERE rn > 1
);
```

Run the inner `SELECT` first and look at what it would delete. Then add a unique index on `lower(email)` so duplicates cannot come back.

### Gaps and islands (briefly)

"Islands" are runs of consecutive values, for example streaks of consecutive days on which a customer ordered. The classic trick: within a partition, `day - row_number()` is constant along a streak and changes after every gap.

```sql
WITH days AS (
  SELECT DISTINCT customer_id, created_at::date AS day FROM orders
)
SELECT customer_id, min(day) AS streak_start, max(day) AS streak_end, count(*) AS days
FROM (
  SELECT customer_id, day,
         day - (row_number() OVER (PARTITION BY customer_id ORDER BY day))::int AS grp
  FROM days
) s
GROUP BY customer_id, grp
ORDER BY customer_id, streak_start;
```

The cast to `int` is needed because `row_number()` returns `bigint` and PostgreSQL defines `date - integer`. The `created_at::date` cast uses the session's time zone, so set it deliberately for daily reports.

### Named windows

When several functions share a window, name it once with `WINDOW`. You can extend a named window with a frame, as long as the named window has no frame of its own:

```sql
SELECT id,
       row_number() OVER w,
       sum(total_cents) OVER (w ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
FROM orders
WINDOW w AS (PARTITION BY customer_id ORDER BY created_at, id);
```

---

## 4. Code Examples

Scenario: a "customer history" endpoint returns each requested customer's paid orders with a running spend, the order's sequence number, its size rank within the customer, its share of lifetime spend, and the time since the previous order.

### SQL

```sql
-- Fixes the module's deliberate gap and matches PARTITION BY customer_id ORDER BY created_at, id,
-- so WindowAgg can read pre-sorted rows from the index instead of sorting.
CREATE INDEX orders_customer_created_asc_idx ON orders (customer_id, created_at, id);

SELECT o.customer_id,
       o.id,
       o.created_at,
       o.total_cents,
       row_number() OVER w                                                           AS order_seq,
       sum(o.total_cents) OVER (w ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)  AS running_spend_cents,
       dense_rank() OVER (PARTITION BY o.customer_id ORDER BY o.total_cents DESC)    AS size_rank,
       round(100.0 * o.total_cents / sum(o.total_cents) OVER (PARTITION BY o.customer_id), 1) AS pct_of_lifetime,
       extract(epoch FROM o.created_at - lag(o.created_at) OVER w)::int              AS secs_since_prev
FROM orders o
WHERE o.customer_id = ANY($1::bigint[])
  AND o.status IN ('paid', 'shipped')
WINDOW w AS (PARTITION BY o.customer_id ORDER BY o.created_at, o.id)
ORDER BY o.customer_id, o.created_at, o.id;
```

Illustrative output for one customer:

| customer_id | id | total_cents | order_seq | running_spend_cents | size_rank | pct_of_lifetime | secs_since_prev |
|---|---|---|---|---|---|---|---|
| 42 | 101 | 2500 | 1 | 2500 | 2 | 25.0 | NULL |
| 42 | 117 | 1500 | 2 | 4000 | 3 | 15.0 | 691200 |
| 42 | 160 | 6000 | 3 | 10000 | 1 | 60.0 | 1987200 |

The second window (`size_rank`) has a different `ORDER BY`, so the plan contains an extra `Sort` for it. That is cheap for one customer's orders, but it is why you should not add windows "just in case".

### Node.js / TypeScript

```ts
// npm i pg   (types: npm i -D @types/pg) — Node.js 22+, TypeScript 5, ESM
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

// pg returns bigint (sum, row_number, dense_rank) and numeric (round) as strings,
// because JS numbers lose precision above 2^53. Cents for one customer stay far below that,
// so converting with Number() is safe here — but do it explicitly, per column.
interface RawRow {
  customer_id: string; id: string; created_at: Date; total_cents: number;
  order_seq: string; running_spend_cents: string; size_rank: string;
  pct_of_lifetime: string; secs_since_prev: number | null;
}

export interface OrderHistoryEntry {
  orderId: number; createdAt: Date; totalCents: number; orderSeq: number;
  runningSpendCents: number; sizeRank: number; pctOfLifetime: number; secsSincePrev: number | null;
}

const HISTORY_SQL = `
  SELECT o.customer_id, o.id, o.created_at, o.total_cents,
         row_number() OVER w AS order_seq,
         sum(o.total_cents) OVER (w ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_spend_cents,
         dense_rank() OVER (PARTITION BY o.customer_id ORDER BY o.total_cents DESC) AS size_rank,
         round(100.0 * o.total_cents / sum(o.total_cents) OVER (PARTITION BY o.customer_id), 1) AS pct_of_lifetime,
         extract(epoch FROM o.created_at - lag(o.created_at) OVER w)::int AS secs_since_prev
  FROM orders o
  WHERE o.customer_id = ANY($1::bigint[]) AND o.status IN ('paid', 'shipped')
  WINDOW w AS (PARTITION BY o.customer_id ORDER BY o.created_at, o.id)
  ORDER BY o.customer_id, o.created_at, o.id`;

export async function orderHistory(customerIds: number[]): Promise<Map<number, OrderHistoryEntry[]>> {
  // One round trip for many customers: the array parameter replaces N separate queries.
  const { rows } = await pool.query<RawRow>(HISTORY_SQL, [customerIds]);

  const byCustomer = new Map<number, OrderHistoryEntry[]>();
  for (const r of rows) {
    const customerId = Number(r.customer_id);
    const list = byCustomer.get(customerId) ?? [];
    list.push({
      orderId: Number(r.id),
      createdAt: r.created_at,
      totalCents: r.total_cents,                 // integer column: already a number
      orderSeq: Number(r.order_seq),
      runningSpendCents: Number(r.running_spend_cents),
      sizeRank: Number(r.size_rank),
      pctOfLifetime: Number(r.pct_of_lifetime),
      secsSincePrev: r.secs_since_prev,
    });
    byCustomer.set(customerId, list);
  }
  return byCustomer;
}
```

Rows already arrive grouped and sorted, so the mapping is a single pass. The application never recomputes the running total — if it did, it would disagree with the database the first time someone changed the `WHERE` clause in only one place.

### Python

```python
# pip install "psycopg[binary,pool]"   — Python 3.12+
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import groupby

from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

pool = ConnectionPool("postgresql://app@localhost/shop", open=True)


@dataclass(frozen=True)
class OrderHistoryEntry:
    customer_id: int
    id: int
    created_at: datetime
    total_cents: int
    order_seq: int
    running_spend_cents: int
    size_rank: int
    pct_of_lifetime: Decimal       # numeric -> Decimal: no float rounding surprises
    secs_since_prev: int | None    # NULL for each customer's first order


HISTORY_SQL = """
    SELECT o.customer_id, o.id, o.created_at, o.total_cents,
           row_number() OVER w AS order_seq,
           sum(o.total_cents) OVER (w ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_spend_cents,
           dense_rank() OVER (PARTITION BY o.customer_id ORDER BY o.total_cents DESC) AS size_rank,
           round(100.0 * o.total_cents / sum(o.total_cents) OVER (PARTITION BY o.customer_id), 1)
               AS pct_of_lifetime,
           extract(epoch FROM o.created_at - lag(o.created_at) OVER w)::int AS secs_since_prev
    FROM orders o
    WHERE o.customer_id = ANY(%s::bigint[]) AND o.status IN ('paid', 'shipped')
    WINDOW w AS (PARTITION BY o.customer_id ORDER BY o.created_at, o.id)
    ORDER BY o.customer_id, o.created_at, o.id
"""


def order_history(customer_ids: list[int]) -> dict[int, list[OrderHistoryEntry]]:
    with pool.connection() as conn:
        # class_row maps columns to the dataclass by name; bigint already arrives as int.
        with conn.cursor(row_factory=class_row(OrderHistoryEntry)) as cur:
            rows = cur.execute(HISTORY_SQL, (customer_ids,)).fetchall()
    # The SQL sorts by customer_id, so groupby can rely on adjacent rows.
    return {cid: list(entries) for cid, entries in groupby(rows, key=lambda r: r.customer_id)}
```

**Runtime difference to notice:** psycopg maps `bigint` to Python `int` (arbitrary precision) and `numeric` to `Decimal`, so nothing needs converting. `pg` returns both as strings because a JavaScript `number` cannot hold every `bigint`. You can also install a global parser (`pg.types.setTypeParser(20, BigInt)`), but `BigInt` does not mix with `number` in arithmetic or `JSON.stringify`, so per-column conversion is usually simpler.

---

## 5. Production Concerns

- **Sorting is the cost.** Every distinct `(PARTITION BY, ORDER BY)` pair needs sorted input. On large inputs, look for `Sort Method: external merge  Disk: ...` in `EXPLAIN (ANALYZE, BUFFERS)` — the sort spilled past `work_mem`. Fixes, in order: filter earlier, give windows the same ordering so one sort serves several, add an index that delivers the order (`(customer_id, created_at, id)` above), and only then raise `work_mem` for that query.
- **Window functions do not reduce work by themselves.** `WHERE rn <= 3` in the outer query does not stop PostgreSQL from reading every row of every partition; it still has to sort them. Since PostgreSQL 15 the executor can stop *evaluating* `row_number()`, `rank()`, `dense_rank()` and `count()` early in a partition when an outer filter like `rn <= 3` can no longer match (shown as `Run Condition` in `EXPLAIN`), but the input is still read and sorted. For "top 1 per group" on large tables with an index, compare against `DISTINCT ON` or a `LATERAL ... LIMIT` join.
- **`count(*) OVER ()` for pagination totals** returns the full match count on every page row. It is convenient, but PostgreSQL must produce the whole result before `LIMIT` applies, so a "page of 20" quietly costs as much as fetching everything. On big tables, show an estimate or a capped count instead.
- **Non-deterministic results.** A window `ORDER BY` with ties gives `row_number()` and `ROWS` frames an arbitrary order. Results can change after a plan change, a `VACUUM`, or a parallel query. This causes flaky tests and "the report changed overnight" tickets. Always end the window's `ORDER BY` with a unique column.
- **Time zones in day buckets.** `created_at::date` and `date_trunc('day', created_at)` on `timestamptz` use the session `TimeZone`. A report run from a server in UTC and one run from a laptop in another zone produce different daily totals. Set the zone explicitly (`created_at AT TIME ZONE 'Europe/Berlin'`) for business-day reports.
- **Big numbers in drivers.** `sum(integer)` returns `bigint` and `sum(bigint)` returns `numeric` in PostgreSQL. Both reach Node as strings. Convert explicitly, and decide whether `Number`, `BigInt` or a decimal library is right for the magnitude.
- **What to measure:** query duration by endpoint, rows returned, and whether sorts spill to disk (`log_temp_files` reports temp files above a size you set).

> **MySQL (InnoDB) difference:** MySQL supports window functions from 8.0, with `ROWS` and `RANGE` frames and the same default frame rule. It has no `GROUPS` frame mode and no `DISTINCT ON`, so top-1-per-group is always a window function or a join.

---

## 6. Common Mistakes

- **Filtering on a window function in `WHERE`** — `WHERE row_number() OVER (...) = 1` fails with "window functions are not allowed in WHERE" — compute it in a subquery or CTE, then filter in the outer query.
- **Relying on the default frame** — `last_value()` returns the current row, and running totals jump on tied timestamps — write the frame explicitly (`ROWS BETWEEN ...`) and add a unique tie-breaker.
- **No tie-breaker in the window `ORDER BY`** — `row_number()` picks a different "latest" row on each run, so de-duplication deletes different rows in staging and production — end every window ordering with the primary key.
- **Using `GROUP BY` and then joining back to get row details** — two scans and a join that can multiply rows — use `sum(...) OVER (PARTITION BY ...)` to put the group total on every detail row.
- **`ROWS n PRECEDING` on a series with gaps** — a "7-day average" silently covers three weeks of sparse data — use `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW`, or fill missing days with `generate_series`.
- **Computing running totals in application code after pagination** — page 2's running total restarts at zero — compute it in SQL over the full partition, then paginate the result.
- **Assuming `rank()` gives N rows for "top N"** — ties at the boundary return more than N rows — use `row_number()` if the API promises exactly N.

---

## 7. Comparison Table

| | Window function | `GROUP BY` aggregate | Correlated subquery / self-join |
|---|---|---|---|
| Output rows | One per input row | One per group | One per outer row |
| Access to row details and group values together | Yes | No (must join back) | Yes |
| Running / moving values | Natural (frames) | Not possible | Possible, O(n²) per group |
| Previous / next row | `lag` / `lead` | No | Self-join on "max earlier id" |
| Filter on the result | Needs subquery or CTE | `HAVING` | `WHERE` |
| Typical cost | One sort + one pass | Hash or sort aggregate | Repeated index lookups or a large join |

`DISTINCT ON (customer_id) ... ORDER BY customer_id, created_at DESC` (PostgreSQL only) is a shorter way to get "latest row per group" when you only need `N = 1`.

---

## 8. Interview Questions

**[Junior] What is the difference between a window function and `GROUP BY`?**
`GROUP BY` collapses each group into one output row, so you lose the individual rows. A window function computes a value over a group of related rows but returns every input row, with the computed value added as a column. For example, `sum(total_cents) OVER (PARTITION BY customer_id)` puts the customer's total on each of their orders.

**[Junior] Explain `row_number`, `rank` and `dense_rank`.**
All three number rows within a partition by the window's `ORDER BY`. `row_number` always gives unique numbers, breaking ties arbitrarily. `rank` gives tied rows the same number and then skips (1, 2, 2, 4). `dense_rank` gives tied rows the same number with no gap (1, 2, 2, 3).

**[Mid] How do you get the top 3 products per category?**
Aggregate revenue per product, compute `row_number() OVER (PARTITION BY category ORDER BY revenue DESC, product_id)`, then filter `rn <= 3` in an outer query, because window functions cannot appear in `WHERE`. Use `rank()` if ties at the boundary should all be included. With an index and few categories, a `LATERAL` join with `LIMIT 3` per category can be cheaper because it avoids sorting every product.

**[Mid] Why does `last_value()` return the current row?**
When the window has an `ORDER BY` and no explicit frame, the frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. The frame ends at the current row (and its peers), so the "last value" of the frame is the current row. Specify `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`, or use `first_value` with the sort reversed.

**[Mid] What is the difference between `ROWS` and `RANGE` frames?**
`ROWS` counts physical rows: `2 PRECEDING` is exactly two rows back. `RANGE` works on the value of the `ORDER BY` column: all rows with equal values (peers) are in or out together, and offsets like `INTERVAL '6 days' PRECEDING` are measured in values. Use `ROWS` for "last N events" and `RANGE` with an interval for calendar windows on data with gaps.

**[Senior] A daily report's numbers change between runs even though no data changed. What do you look for?**
First, window orderings without a unique tie-breaker: `row_number()` and `ROWS` frames over tied rows depend on physical order, which can change after a new plan, a parallel scan or vacuum. Second, day bucketing on `timestamptz` that depends on the session time zone of whoever runs it. Third, `now()`-relative filters. The fix is deterministic ordering (add the primary key), explicit time zones, and passing the report period as a parameter.

**[Senior] A top-N-per-group query with `row_number()` is slow on a 200-million-row table. How do you approach it?**
Check the plan: the window needs input sorted by `(partition, order)` columns, so it likely does a full sort that spills to disk, and the `rn <= N` filter does not stop the scan. If there are relatively few groups, a `LATERAL` join from the group table with `ORDER BY ... LIMIT N` uses an index on `(group_key, sort_key)` and reads only N entries per group. If the result is needed often and can be slightly stale, precompute it in a [materialized view](17-Materialized-Views.md) or a summary table. Raising `work_mem` only helps if the sort is the problem and memory is available for concurrent queries.

**[Senior] Running totals in SQL or in the application?**
In SQL when the total must be consistent with filtering, pagination or other consumers: the database sees the full partition, so page 2 still starts from the right running value, and every client gets the same answer. Application-side accumulation is fine only when the app already has the full ordered set in memory and nobody else needs the number. The real risk of doing it in code is two definitions of "spend" (one in SQL filters, one in code) that drift apart.

---

## 9. Cheat Sheet

```text
Shape          f() OVER (PARTITION BY p ORDER BY o, id  ROWS|RANGE|GROUPS BETWEEN ... AND ...)
Keeps rows     window = rows stay; GROUP BY = rows collapse
Order of eval  FROM → WHERE → GROUP BY → HAVING → WINDOW → SELECT → DISTINCT → ORDER BY → LIMIT
Filter on it   wrap in subquery/CTE, then WHERE rn <= N
Default frame  with ORDER BY: RANGE UNBOUNDED PRECEDING .. CURRENT ROW (includes peers)
               without ORDER BY: whole partition
last_value     needs ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
Ranking        row_number 1234 | rank 1224 | dense_rank 1223
Neighbours     lag(x, n, default) / lead(x, n, default) — ignore the frame
Running total  sum(x) OVER (PARTITION BY k ORDER BY t, id ROWS UNBOUNDED PRECEDING)
Moving avg     ROWS n PRECEDING = last n rows; RANGE INTERVAL '6 days' PRECEDING = calendar
Top-N / dedup  row_number() OVER (PARTITION BY key ORDER BY pref, id) → keep rn = 1 / <= N
Islands        value - row_number() is constant along a consecutive run
Performance    WindowAgg needs sorted input → index on (partition, order) or Sort (watch disk spills)
Drivers        rank/row_number/sum(int) = bigint → string in node-postgres
```

---

## Related Topics

- [Aggregate Functions](13-Aggregate-Functions.md) — the collapsing alternative, and `FILTER` / `HAVING`
- [Common Table Expressions](15-Common-Table-Expressions.md) — the usual way to filter on a window result
- [Subqueries](11-Subqueries.md) — `LATERAL` joins for top-N per group with an index
- [Composite Indexes](20-Composite-Indexes.md) — an index on `(partition, order)` columns removes the sort
- [Query Execution Plans](22-Query-Execution-Plans.md) — reading `WindowAgg`, `Sort` and disk spills
- [Materialized Views](17-Materialized-Views.md) — precomputing expensive rankings for dashboards

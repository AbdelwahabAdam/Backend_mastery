# Deadlocks

> **Module 03 · Databases** · Prerequisites: [Database Locks](30-Database-Locks.md) · Next: [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md)

---

## ⏱ If You Only Have 2 Minutes

- A deadlock is a **cycle of lock waits**: T1 holds row A and waits for row B, T2 holds B and waits for A. Neither can ever finish, so the database must abort one of them.
- PostgreSQL checks for a cycle only after a lock wait has lasted `deadlock_timeout` (**1 s** by default). It aborts one transaction with `ERROR: deadlock detected`, SQLSTATE **`40P01`**. Which one is aborted is not predictable.
- The victim's **whole transaction** is rolled back, not just the last statement. Retry from `BEGIN`, a bounded number of times, with backoff **and jitter**.
- The number-one cause is the same rows locked **in a different order** by two code paths — e.g. two checkouts reserving inventory for products `[1, 2]` and `[2, 1]`.
- Prevention: lock in one global order. Sort the IDs and run `SELECT … WHERE id = ANY($1) ORDER BY id FOR UPDATE` before writing. A multi-row `UPDATE … WHERE id IN (…)` locks rows in **plan order**, not in the order of your list.
- Locks you did not write still count: foreign-key checks (`FOR KEY SHARE` on the parent), unique-index inserts, upserts and triggers.
- Upgrading a lock (`FOR SHARE`, then `UPDATE` the same row) deadlocks with **one row** and two transactions. Take the strongest lock you will need first.
- MySQL InnoDB detects deadlocks immediately, rolls back the "smaller" transaction, and returns error **1213** (SQLSTATE `40001`). Gap locks give it extra deadlocks that Postgres does not have.

---

## 1. What It Is and Why It Exists

A **deadlock** happens when two or more transactions each hold a lock that another one is waiting for, in a closed loop. No transaction in the loop can make progress, and none will give up on its own, because a lock wait has no natural end.

**Analogy:** two cooks share one pan and one knife. Cook A picks up the pan and reaches for the knife. Cook B picks up the knife and reaches for the pan. Each waits politely for the other to finish. The kitchen manager notices that nothing has moved for a while, takes the knife off cook B and tells B to start the dish again. Cook A finishes; cook B starts over.

The database is the kitchen manager. A deadlock is not data corruption or a database bug; it is a liveness problem that the database turns into an **error** for one transaction so the others can continue. Without detection, both would hold their connections and locks forever, and everything queued behind them would stall.

Deadlocks appear only under concurrency, so they pass unit tests and surface at peak traffic as a trickle of `40P01` errors. The expected answer has two parts: **prevent** them with a consistent lock order, and **survive** the rest by retrying the victim correctly.

### The four conditions

The [OS chapter on deadlocks](../Module-04-Operating-Systems/18-Deadlocks.md) lists the Coffman conditions. A database meets all four by default:

| Condition | How a database meets it | How you break it |
|---|---|---|
| Mutual exclusion | Two `UPDATE`s cannot hold the same row lock | Avoid locking (atomic single-row statements, optimistic versions) |
| Hold and wait | Locks are held until `COMMIT`, while the transaction asks for more | Take all locks up front in one ordered statement |
| No preemption | The database cannot take a lock back from a live transaction | The database preempts by **aborting** a victim; `lock_timeout` / `NOWAIT` make waits give up |
| Circular wait | Two code paths lock the same rows in different orders | **One global lock order** — the main fix |

---

## 2. How It Works

### A two-session timeline

Two customers check out at the same moment. Order A contains products 1 and 2; order B contains products 2 and 1. The code reserves stock line by line, in cart order.

| Time | Session A (pid 48211, xid 912344) | Session B (pid 48230, xid 912345) |
|---|---|---|
| t1 | `BEGIN;` | `BEGIN;` |
| t2 | `UPDATE inventory … WHERE product_id = 2;` → locks row 2 | |
| t3 | | `UPDATE inventory … WHERE product_id = 1;` → locks row 1 |
| t4 | `UPDATE inventory … WHERE product_id = 1;` → **waits for B** | |
| t5 | | `UPDATE inventory … WHERE product_id = 2;` → **waits for A** — cycle |
| t4 + 1 s | A has waited `deadlock_timeout`; its check finds the cycle | |
| | `ERROR: deadlock detected` (40P01); transaction aborted | gets row 2, continues, `COMMIT` |

```mermaid
sequenceDiagram
    participant A as Session A
    participant DB as PostgreSQL
    participant B as Session B
    A->>DB: UPDATE row 2 (lock granted)
    B->>DB: UPDATE row 1 (lock granted)
    A->>DB: UPDATE row 1
    Note over A,DB: A waits for B
    B->>DB: UPDATE row 2
    Note over DB,B: B waits for A, cycle formed
    DB->>DB: A has waited deadlock_timeout, build waits-for graph, find cycle
    DB-->>A: ERROR 40P01 deadlock detected, A rolled back
    DB-->>B: row 2 lock granted
    B->>DB: COMMIT
    A->>DB: retry whole transaction after a jittered pause
```

### How PostgreSQL detects it

1. A backend that requests a conflicting lock goes to sleep on it.
2. If it is still waiting after `deadlock_timeout` (1 s by default), it builds the **waits-for graph** from the lock table: who waits for whom.
3. If that graph contains a cycle through this backend, PostgreSQL resolves it by aborting one transaction in the cycle. In simple two-party cases it is usually the one that ran the check — here A, whose timer started first — but the docs say plainly that you should not rely on which one. Timing decides which backend's check finds the cycle, so with slightly different timing B would have been the victim.
4. The aborted transaction gets SQLSTATE `40P01`. Its locks are released, and the other transaction's wait succeeds.

Why wait before checking? Most lock waits are short, and a graph search on every wait would waste CPU. The cost is that each deadlock adds at least `deadlock_timeout` of latency to the requests involved.

### Reading a deadlock log entry

The client receives the error and a short `DETAIL`. The server log has the full report, including the statement each process was running:

```text
2026-11-24 10:15:02.117 UTC [48211] ERROR:  deadlock detected
2026-11-24 10:15:02.117 UTC [48211] DETAIL:  Process 48211 waits for ShareLock on transaction 912345; blocked by process 48230.
	Process 48230 waits for ShareLock on transaction 912344; blocked by process 48211.
	Process 48211: UPDATE inventory SET available = available - $1, version = version + 1 WHERE product_id = $2 AND available >= $1
	Process 48230: UPDATE inventory SET available = available - $1, version = version + 1 WHERE product_id = $2 AND available >= $1
2026-11-24 10:15:02.117 UTC [48211] HINT:  See server log for query details.
2026-11-24 10:15:02.117 UTC [48211] CONTEXT:  while updating tuple (0,1) in relation "inventory"
```

How to read it:

- **"waits for ShareLock on transaction 912345"** means "waits for a row that transaction 912345 (session B) has locked". Row-lock waits are waits on the holder's transaction ID (see [Database Locks](30-Database-Locks.md)). Other shapes you will see: `ShareLock on relation …` or `AccessExclusiveLock on relation …` (table locks, often DDL), and `ExclusiveLock on tuple (…) of relation …`.
- **"Process N: …"** lines show the statement each process was running **when the cycle closed**. They do not show the earlier statement that took the first lock. Here both are the same `UPDATE`, which already suggests "same code path, different row order".
- **`CONTEXT`** names the table and the row's physical location (`(page, item)`) for the victim's statement.
- With bind parameters you see `$1`, not values, so log the business IDs in the application when you catch `40P01`. Then read each transaction's whole code path and list the order in which it touches rows — that is where the **why** is.

---

## 3. Key Concepts

### Common causes

| Cause | Example on the sample schema | Fix |
|---|---|---|
| Same rows, different order in one code path | Checkout reserves inventory in cart order: `[2, 1]` vs `[1, 2]` | Merge and sort product IDs before locking |
| Different code paths, different table order | Checkout locks `inventory` then updates `orders`; cancellation locks `orders` then restores `inventory` | One documented order for the whole service: e.g. `orders` → `inventory` → `payments`, then by primary key |
| Multi-row statement in plan order | Two `UPDATE inventory … WHERE product_id IN (…)` run with different plans (index order vs physical order) | Pre-lock with `SELECT … ORDER BY product_id FOR UPDATE`, then update |
| Batch upserts in input order | Two restock jobs upsert keys `[5, 9]` and `[9, 5]`; each insert waits on the other's uncommitted unique key | Sort the batch by the conflict key before `INSERT … ON CONFLICT` |
| Lock upgrade on one row | T1 and T2 both `SELECT … FOR SHARE` product 7, then both `UPDATE` it | Take `FOR UPDATE` (or `FOR NO KEY UPDATE`) first, not `FOR SHARE` |
| Hidden foreign-key locks | T1 inserts an `order_items` row (FK check: `FOR KEY SHARE` on product 7), then updates `inventory` 7. T2 already updated `inventory` 7 and now runs `SELECT … FROM products WHERE id = 7 FOR UPDATE`, waiting on T1's key-share lock. T1 waits on T2 | Lock parents with `FOR NO KEY UPDATE`, which does not conflict with FK checks; keep a fixed table order |

The foreign-key case surprises people because neither transaction's code "locked" the product — the `REFERENCES` constraint did. `FOR KEY SHARE` only collides with `FOR UPDATE`, `DELETE` or a key change, which is exactly what an over-cautious `FOR UPDATE` on a parent row introduces.

### Prevention techniques

| Technique | How | Note |
|---|---|---|
| Global lock order | Lock tables in a fixed order, and rows within a table by primary key | Breaks circular wait; the main fix |
| Ordered pre-lock | `SELECT … WHERE id = ANY($1) ORDER BY id FOR UPDATE` | `ORDER BY` is applied before the locking step, so rows are locked in sorted order |
| Row-by-row in sorted order | Loop over sorted IDs, one `UPDATE` per row | The loop order **is** the lock order; costs one round trip per row |
| Strongest lock first | `FOR UPDATE` / `FOR NO KEY UPDATE` instead of `FOR SHARE` when you will write | Avoids lock upgrades |
| Shorter transactions | No remote calls, no user think-time inside the transaction | Fewer overlapping lock sets, fewer chances to collide |
| Smaller batches | Update 1,000 rows per transaction, not 1,000,000 | A huge batch overlaps with everything |
| Serialize per aggregate | `pg_advisory_xact_lock` on the order ID, or one queue partition per key | Removes concurrency where it buys nothing |

`ORDER BY` with `FOR UPDATE` comes with one documented quirk: under `READ COMMITTED`, if a row changes while you wait for it, the returned row reflects the new version and may appear out of order. The locks are still taken in order, which is what prevents the deadlock.

### Detection settings in PostgreSQL

| Setting | Default | Meaning |
|---|---|---|
| `deadlock_timeout` | `1s` | How long a lock wait lasts before the deadlock check runs; also the threshold for `log_lock_waits` |
| `log_lock_waits` | — | When on, logs every wait longer than `deadlock_timeout` with the PIDs involved — your early warning |
| `lock_timeout` | `0` (off) | Gives up any single lock wait after this long with `55P03`; bounds waits but does not detect cycles |
| `pg_stat_database.deadlocks` | — | Cumulative count of deadlocks per database; graph its rate |

Do not lower `deadlock_timeout` to "detect faster". Every lock wait longer than the timeout then pays for a graph search, and it hides the real problem. Fix the lock order instead.

### Safe retry

A deadlock victim did nothing wrong; it lost a coin toss. Retry it properly:

1. **Retry the whole transaction.** After any error the transaction is aborted; further statements fail with `25P02`. Roll back and rerun from `BEGIN`, re-reading the data your decisions depend on.
2. **Retry only `40P01` and `40001`.** A `23505` unique violation or a check-constraint error will fail again.
3. **Bound it** to three to five attempts. Frequent deadlocks need a lock-order fix, not more retries.
4. **Add jitter.** Two victims that sleep the same fixed time collide again — a [livelock](../Module-04-Operating-Systems/19-Livelocks.md) in slow motion. Use exponential backoff with *full jitter* (a random wait between 0 and the cap).
5. **No external side effects inside the retried block.** An email or card charge would happen twice; write an outbox row instead and act on it after commit.

### MySQL (InnoDB) difference

- InnoDB checks for a cycle **as soon as a lock request has to wait** (`innodb_deadlock_detect`, on by default), so there is no 1-second delay. Very high-concurrency systems sometimes turn detection off and rely on `innodb_lock_wait_timeout` (50 s) instead.
- It picks a **small** victim: the transaction that inserted, updated or deleted the fewest rows. The error is 1213 `ER_LOCK_DEADLOCK`, SQLSTATE `40001`, and the whole transaction is rolled back.
- `SHOW ENGINE INNODB STATUS` prints the latest deadlock under `LATEST DETECTED DEADLOCK`; `innodb_print_all_deadlocks = ON` writes every one to the error log.
- **Gap-lock deadlocks.** Under `REPEATABLE READ`, two transactions both `SELECT … FOR UPDATE` a key that does not exist yet; their gap locks do not conflict. Then both `INSERT` into that gap, and each insert waits for the other's gap lock. Postgres has no gap locks, so this "check, then insert" pattern ends in a unique violation there instead. Fixes in MySQL: `INSERT … ON DUPLICATE KEY UPDATE`, or `READ COMMITTED`.

---

## 4. Code Examples

Scenario: reserving stock for all lines of an order. Without care, two orders with overlapping products deadlock. The fix is to merge and sort product IDs, lock the rows in that order, and retry on `40P01` with jitter.

### SQL

```sql
-- Reserve stock for one order, deadlock-free.
-- $1 = product IDs (deduplicated, ascending), $2 = quantities in the same order.
BEGIN;

-- 1. Lock every row first, in one global order. ORDER BY runs before the locking
--    step, so every transaction that uses this query locks rows lowest-id first.
SELECT product_id
FROM inventory
WHERE product_id = ANY($1::bigint[])
ORDER BY product_id
FOR UPDATE;

-- 2. We already hold all the locks, so this set-based UPDATE cannot wait on anyone.
--    Lines without enough stock simply don't match; the app compares the row count.
UPDATE inventory i
SET available = i.available - r.qty,
    version   = i.version + 1
FROM unnest($1::bigint[], $2::int[]) AS r(product_id, qty)
WHERE i.product_id = r.product_id
  AND i.available >= r.qty
RETURNING i.product_id, i.available;

COMMIT;   -- or ROLLBACK if fewer rows came back than products requested

-- Batch upsert (restock): sort by the conflict key so two batches with
-- overlapping products insert/lock them in the same order.
INSERT INTO inventory (product_id, available)
SELECT product_id, qty
FROM unnest($1::bigint[], $2::int[]) AS r(product_id, qty)
ORDER BY product_id
ON CONFLICT (product_id)
DO UPDATE SET available = inventory.available + EXCLUDED.available,
              version   = inventory.version + 1;

-- How often is this happening? (cumulative since the last stats reset)
SELECT datname, deadlocks FROM pg_stat_database WHERE datname = current_database();
```

`FOR UPDATE` is the familiar choice. Because the code changes only non-key columns, `FOR NO KEY UPDATE` would also work and would not block foreign-key checks from new `order_items` rows (see [Database Locks](30-Database-Locks.md)). The order of the rows is what prevents the deadlock, not the strength of the lock.

### Node.js / TypeScript

Ordered pre-lock plus a set-based update: two round trips, whatever the number of lines.

```ts
// npm i pg && npm i -D @types/pg   — Node.js 22+, TypeScript 5, ESM
import pg from "pg";
import { setTimeout as sleep } from "node:timers/promises";

const RETRYABLE = new Set(["40P01", "40001"]); // deadlock_detected, serialization_failure

export class OutOfStockError extends Error {
  constructor(readonly productIds: number[]) {
    super(`out of stock: ${productIds.join(", ")}`);
  }
}

export async function inTransaction<T>(
  pool: pg.Pool, work: (client: pg.PoolClient) => Promise<T>, maxAttempts = 5,
): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    // BEGIN..COMMIT must run on one connection; pool.query could pick a different one each call.
    const client = await pool.connect();
    try {
      await client.query("BEGIN");
      const result = await work(client);
      await client.query("COMMIT");
      return result;
    } catch (err) {
      await client.query("ROLLBACK").catch(() => undefined);
      const code = (err as { code?: string }).code;
      if (code === undefined || !RETRYABLE.has(code) || attempt >= maxAttempts) throw err;
      // Full jitter, so the two victims of one cycle don't wake up and collide again.
      const delayMs = Math.random() * Math.min(1000, 25 * 2 ** attempt);
      console.warn({ code, attempt, delayMs: Math.round(delayMs) }, "retrying transaction");
      await sleep(delayMs);
    } finally {
      client.release();
    }
  }
}

export interface Line { productId: number; quantity: number }

export function reserveStock(pool: pg.Pool, lines: Line[]): Promise<void> {
  // Merge duplicates: UPDATE … FROM applies only one of several matching source rows.
  const wanted = new Map<number, number>();
  for (const { productId, quantity } of lines) {
    wanted.set(productId, (wanted.get(productId) ?? 0) + quantity);
  }
  // Numeric comparator: the default sort() compares strings, so 10 would come before 2.
  const ids = [...wanted.keys()].sort((a, b) => a - b);
  const qtys = ids.map((id) => wanted.get(id)!);

  return inTransaction(pool, async (client) => {
    await client.query(
      `SELECT product_id FROM inventory
       WHERE product_id = ANY($1::bigint[])
       ORDER BY product_id
       FOR UPDATE`,
      [ids],
    );
    const { rows } = await client.query<{ product_id: string }>(
      `UPDATE inventory i
       SET available = i.available - r.qty, version = i.version + 1
       FROM unnest($1::bigint[], $2::int[]) AS r(product_id, qty)
       WHERE i.product_id = r.product_id AND i.available >= r.qty
       RETURNING i.product_id`,
      [ids, qtys],
    );
    if (rows.length !== ids.length) {
      const reserved = new Set(rows.map((r) => Number(r.product_id))); // bigint arrives as string
      throw new OutOfStockError(ids.filter((id) => !reserved.has(id))); // not retryable → rollback
    }
  });
}
```

### Python

The same guarantee with a different technique: one `UPDATE` per product, in sorted order. Each statement locks exactly one row, so the loop order is the lock order. It costs one round trip per line, which is fine for a cart of a few items.

```python
# pip install "psycopg[binary]"   — Python 3.12+
import random
import time
from collections import Counter
from collections.abc import Callable

import psycopg
from psycopg import errors

RETRYABLE = (errors.DeadlockDetected, errors.SerializationFailure)  # 40P01, 40001


class OutOfStock(Exception):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"out of stock: {product_id}")
        self.product_id = product_id


def in_transaction[T](conn: psycopg.Connection, work: Callable[[psycopg.Connection], T],
                      max_attempts: int = 5) -> T:
    for attempt in range(1, max_attempts + 1):
        try:
            # Commits when the block exits normally; rolls back when work() raises.
            with conn.transaction():
                return work(conn)
        except RETRYABLE as exc:
            if attempt == max_attempts:
                raise
            delay = random.uniform(0, min(1.0, 0.025 * 2**attempt))  # full jitter
            print(f"retrying after {type(exc).__name__} (attempt {attempt}, {delay:.3f}s)")
            time.sleep(delay)
    raise AssertionError("unreachable")


def reserve_stock(conn: psycopg.Connection, lines: list[tuple[int, int]]) -> None:
    wanted: Counter[int] = Counter()
    for product_id, quantity in lines:
        wanted[product_id] += quantity  # merge duplicate lines before locking

    def work(c: psycopg.Connection) -> None:
        for product_id in sorted(wanted):  # ascending id = the service-wide lock order
            row = c.execute(
                "UPDATE inventory SET available = available - %(qty)s, version = version + 1"
                " WHERE product_id = %(id)s AND available >= %(qty)s RETURNING available",
                {"qty": wanted[product_id], "id": product_id},
            ).fetchone()
            if row is None:
                raise OutOfStock(product_id)  # not retryable: rolls back earlier lines

    in_transaction(conn, work)


if __name__ == "__main__":
    # One connection per thread or task: a psycopg connection runs one transaction at a time.
    with psycopg.connect("postgresql://postgres:dev@localhost:5432/postgres", autocommit=True) as conn:
        reserve_stock(conn, [(2, 1), (1, 3), (2, 1)])
```

**Differences to notice.** In Node, the transaction must hold a `PoolClient` from `pool.connect()`; `BEGIN` and `UPDATE` sent through `pool.query` can land on different connections, so the "transaction" silently is not one. In Python the connection *is* the transaction context, so each thread needs its own connection. Python's `sorted()` on ints is numeric; JavaScript's bare `sort()` is not — a real source of mismatched lock orders between services.

---

## 5. Production Concerns

- **Measure.** Graph the rate of `pg_stat_database.deadlocks`, and count `40P01` retries per code path in the application. A handful a day under load is normal; a steady stream points at one specific ordering bug.
- **Keep the evidence.** Deadlock reports are logged at `ERROR` level by default. Turn on `log_lock_waits` too: long waits that are *not* deadlocks often show the same hot rows before the first deadlock appears. On `40P01`, log the business IDs (order ID, product IDs) because the server log shows only `$1`.
- **Latency cost.** Each deadlock holds both transactions for at least `deadlock_timeout` (1 s), plus the victim's retry. If checkout p99 has a 1-second step, check for deadlocks.
- **Retries under pressure.** Retries add load on exactly the contended rows. Cap attempts and return a clean error (e.g. HTTP 503 with `Retry-After`) when they run out.
- **ORMs.** An ORM chooses its flush order. For contended rows, lock explicitly with an ordered `SELECT … FOR UPDATE` at the start of the unit of work.
- **Background jobs vs user traffic.** A nightly job that updates 500,000 inventory rows in one transaction will deadlock with daytime checkouts. Process in small batches, each in its own short transaction, in primary-key order.
- **Deploy-time DDL.** A migration that takes `ACCESS EXCLUSIVE` in the middle of a transaction that already wrote rows can join a cycle with application traffic. Run DDL in its own transaction with `lock_timeout`.

---

## 6. Common Mistakes

- **Retrying only the failed statement** — the transaction is already aborted, so the next statement fails with `25P02`, or a half-done transaction gets committed through a new one — catch the error at the transaction boundary, roll back, and rerun the whole function.
- **Sorting the `IN` list and expecting the `UPDATE` to follow it** — a multi-row `UPDATE` locks rows in whatever order its plan visits them — pre-lock with `ORDER BY … FOR UPDATE`, or update row by row in sorted order.
- **Retrying everything, forever** — unique violations and bugs loop until the request times out — retry only `40P01` and `40001`, three to five times, then fail loudly.
- **Fixed retry delay** — both victims sleep 100 ms, wake together, and deadlock again — exponential backoff with full jitter.
- **Lowering `deadlock_timeout` to "fix" slow deadlocks** — more CPU on every lock wait, and the deadlocks keep happening — fix the lock order; leave the timeout at 1 s or raise it.
- **`FOR SHARE` now, `UPDATE` later** — two readers of the same row both try to upgrade and deadlock on a single row — lock with the mode you will need (`FOR UPDATE` or `FOR NO KEY UPDATE`) from the start.
- **Side effects inside the retried transaction** — the confirmation email or card charge happens twice — write an outbox row inside the transaction and perform the effect after commit.

---

## 7. Comparison Table

| Strategy | How it works | Cost | Use when |
|---|---|---|---|
| **Consistent lock order** | Every path locks tables, then rows by key, in one order | Discipline across the codebase; sorting | Always — it is the primary defence |
| **Avoid locks** | Single-row atomic `UPDATE … WHERE available >= $n`, or optimistic version checks | Must fit the logic into one statement or tolerate conflicts | Simple counters and per-row state |
| **Lock everything up front** | One ordered `SELECT … FOR UPDATE` for the whole working set | Locks held for the whole transaction | Multi-row updates such as order reservation |
| **Detect and retry** | Let Postgres pick a victim; retry it with jitter | ≥ 1 s latency per deadlock, wasted work | As the safety net behind ordering |
| **Timeouts** (`lock_timeout`, `NOWAIT`) | Give up on any long wait with `55P03` | Errors on ordinary contention too | Migrations, interactive "is it free?" checks |
| **Serialize** | Advisory lock or queue per key (e.g. per order) | Less parallelism | Work on one aggregate that never needs to run concurrently |

---

## 8. Interview Questions

**[Junior] What is a database deadlock, and how does PostgreSQL handle it?**
Two or more transactions each wait for a lock held by another, in a cycle, so none can ever proceed. PostgreSQL notices when a lock wait lasts longer than `deadlock_timeout` (1 s by default), searches for a cycle, and aborts one transaction with SQLSTATE `40P01`. That transaction's locks are released and the others continue. The application must retry the aborted transaction.

**[Mid] How do you prevent deadlocks when one request updates several rows?**
Lock the rows in one global order, usually ascending primary key. Merge duplicate IDs, sort them, and either run `SELECT … WHERE id = ANY($1) ORDER BY id FOR UPDATE` before writing, or update the rows one at a time in sorted order. Use the same table order in every code path. Then two transactions can wait for each other, but never in a cycle.

**[Mid] How should application code retry after a deadlock?**
Catch `40P01` (and `40001`) at the transaction boundary, roll back, and rerun the whole transaction from `BEGIN`, re-reading data. Limit it to three to five attempts with exponential backoff and full jitter, so the two victims do not collide again. Do not retry other errors, and keep non-idempotent side effects such as emails outside the transaction.

**[Mid] How do you read a PostgreSQL deadlock report?**
The `DETAIL` lists each process, what it waits for, and who blocks it. "ShareLock on transaction N" means it waits for a row locked by transaction N. The "Process N: …" lines show the statement each was running when the cycle closed, not the earlier statement that took the first lock, so you combine the report with the application code path to rebuild the full lock order. `CONTEXT` names the table and row location.

**[Senior] You sorted the IDs, but deadlocks still happen. Where do you look next?**
First, check that the sort really controls lock order: a multi-row `UPDATE … WHERE id IN (…)` follows the plan, and a JavaScript `sort()` without a comparator is lexicographic. Second, look for another code path that touches the tables in a different order — cancellation going `orders` → `inventory` while checkout goes `inventory` → `orders`. Third, look for locks nobody wrote: FK checks, triggers, unique-index waits in batch upserts. Finally, look for lock upgrades and for batch jobs holding thousands of row locks in one transaction.

**[Senior] Why does PostgreSQL wait one second before checking for deadlocks, and when would you change it?**
Detection walks the lock graph, which costs CPU and briefly locks the lock manager, and most waits end on their own. Raising the timeout reduces overhead where long legitimate waits are common, at the cost of slower resolution; lowering it is rarely worth it. It is also the `log_lock_waits` threshold, so changing it changes what you log.

**[Senior] How do deadlocks differ between PostgreSQL and MySQL InnoDB?**
InnoDB detects a cycle immediately when a lock request waits, instead of after a timeout, and rolls back the transaction that changed the fewest rows, with error 1213 / SQLSTATE `40001`. InnoDB's default `REPEATABLE READ` takes next-key and gap locks, so it has deadlocks that Postgres cannot have — for example two "check, then insert" transactions whose gap locks both block each other's inserts. Postgres has no gap locks; the same pattern gives a unique violation there. Fixes in InnoDB include `READ COMMITTED` or using `INSERT … ON DUPLICATE KEY UPDATE`.

---

## 9. Cheat Sheet

```text
Definition     cycle of lock waits; DB aborts one victim to break it
Postgres       check after deadlock_timeout (1 s) → ERROR 40P01 "deadlock detected"; victim unpredictable
Victim         whole transaction aborted (later statements → 25P02); ROLLBACK and rerun from BEGIN
Retry          only 40P01/40001, 3–5 attempts, exponential backoff + full jitter, no side effects inside
Main fix       one global lock order: tables in fixed order, rows by primary key
Pre-lock       SELECT … WHERE id = ANY($1) ORDER BY id FOR UPDATE  (ORDER BY runs before locking)
Trap           UPDATE … WHERE id IN (…) locks in plan order, not list order
Trap           JS [10, 2].sort() → [10, 2]; use (a, b) => a - b
Hidden locks   FK check = FOR KEY SHARE on parent; unique inserts wait on each other; triggers
Upgrade        FOR SHARE then UPDATE on the same row → single-row deadlock; lock strongest first
Upserts        sort batch by conflict key before INSERT … ON CONFLICT
Log line       "waits for ShareLock on transaction N" = waiting for a row that xid N locked
Metrics        pg_stat_database.deadlocks rate; app retry count per code path; log_lock_waits=on
MySQL          immediate detection; smaller txn rolled back; 1213 / 40001; gap-lock deadlocks
```

---

## Related Topics

- [Database Locks](30-Database-Locks.md) — the lock modes and waits that deadlocks are made of
- [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md) — avoiding long-held row locks altogether
- [Transactions](27-Transactions.md) — where the retry boundary belongs in application code
- [Isolation Levels](29-Isolation-Levels.md) — `40001` serialization failures share the retry path with `40P01`
- [Deadlocks (Operating Systems)](../Module-04-Operating-Systems/18-Deadlocks.md) — Coffman conditions and wait-for graphs in general
- [Livelocks](../Module-04-Operating-Systems/19-Livelocks.md) — why retries without jitter can keep colliding

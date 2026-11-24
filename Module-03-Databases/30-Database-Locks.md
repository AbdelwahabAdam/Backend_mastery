# Database Locks

> **Module 03 · Databases** · Prerequisites: [Isolation Levels](29-Isolation-Levels.md) · Next: [Deadlocks](31-Deadlocks.md)

---

## ⏱ If You Only Have 2 Minutes

- Under MVCC a plain `SELECT` takes **no row locks** and only an `ACCESS SHARE` table lock. Readers never block writers and writers never block readers. Two writers on the **same row** do queue.
- PostgreSQL has four row lock modes, weakest to strongest: `FOR KEY SHARE`, `FOR SHARE`, `FOR NO KEY UPDATE`, `FOR UPDATE`. A normal `UPDATE` takes `FOR NO KEY UPDATE`; `DELETE` and key-changing updates take `FOR UPDATE`; a foreign-key check takes `FOR KEY SHARE` on the parent row.
- Most `ALTER TABLE` forms, `DROP`, `TRUNCATE`, `VACUUM FULL` and `CLUSTER` take `ACCESS EXCLUSIVE`, which conflicts with **everything, including `SELECT`**.
- **The lock queue:** a waiting `ACCESS EXCLUSIVE` request blocks every later request on that table. A 5 ms `ALTER` stuck behind a 10-minute report stops all traffic to the table. Always run DDL with `SET lock_timeout = '2s'` and retry.
- `NOWAIT` fails at once with SQLSTATE `55P03`. `SKIP LOCKED` silently skips locked rows — that is how you build a safe multi-worker job queue in Postgres.
- Advisory locks lock an application-chosen 64-bit number, not a row. Session-level ones survive `COMMIT`; transaction-level ones (`pg_advisory_xact_lock`) are released at commit or rollback.
- "Who is blocking whom?" → `pg_stat_activity` joined with `pg_blocking_pids(pid)`. The root blocker is very often a session that is `idle in transaction`.
- Row locks are stored in the row itself, not in shared memory, so Postgres never escalates row locks to a table lock (SQL Server does).

---

## 1. What It Is and Why It Exists

A **lock** is a marker that says "this transaction is using this object in this way; conflicting users must wait". The object can be a table, a single row, or an arbitrary number your application chooses (an advisory lock). Every lock has a **mode**, and a table of rules says which modes conflict.

**Analogy:** a hotel. Guests read the lobby notice board at any time, seeing the old notice until the new one is pinned up (MVCC). A room key gives one guest one room (a row lock). Closing a floor for repairs (`ACCESS EXCLUSIVE`) needs every guest off that floor first — and while the repair crew waits at the lift, every new guest for that floor queues behind them.

**The problem it solves.** MVCC stops readers from seeing half-written data, but not two writers from acting on the same old value (two checkouts both selling the last item), a schema change from rewriting a table mid-query, or a billing job from running twice. Locks serialize exactly these conflicting operations and leave everything else parallel.

Most lock incidents are not "a lock was missing" but a lock held too long, a lock taken by a statement nobody thought of as locking (a migration, a foreign-key check), or a queue of waiters behind one forgotten transaction.

---

## 2. How It Works

PostgreSQL has two lock layers.

1. **Table-level locks** live in a shared-memory lock table. Every statement takes one automatically (`SELECT` → `ACCESS SHARE`, DML → `ROW EXCLUSIVE`, DDL → stronger), held until the transaction ends.
2. **Row-level locks** are written into the row version itself: the locker's transaction ID goes into the tuple header (`xmax`) with mode bits. They cost no shared memory, so a transaction can lock millions of rows and Postgres never escalates them. The price: locking a row is a write that dirties the page and generates WAL.

### What happens when an `UPDATE` meets a locked row

```text
T1: BEGIN;
T1: UPDATE inventory SET available = available - 1 WHERE product_id = 7;   -- row 7 locked (FOR NO KEY UPDATE)
T2: BEGIN;
T2: UPDATE inventory SET available = available - 2 WHERE product_id = 7;   -- finds row 7, sees xmax = T1 (still running)
                                                                            -- T2 waits for T1's transaction ID to finish
T1: COMMIT;                                                                 -- T2 wakes up
T2: (READ COMMITTED) re-reads the newest version of row 7, re-checks the WHERE, applies -2 to the new value
T2: COMMIT;
```

Waiting for a row is implemented as waiting for the holder's **transaction ID**. That is why `pg_locks` shows the waiter as `locktype = 'transactionid'`, `granted = false`, and why deadlock reports say "waits for ShareLock on transaction 81234". The waiter also takes a short-lived tuple lock so that several waiters on the same row are served in order.

What happens after T1 commits depends on the [isolation level](29-Isolation-Levels.md). Under `READ COMMITTED`, T2 re-checks its `WHERE` on the new row version and applies its change to the **new** value. Under `REPEATABLE READ` or `SERIALIZABLE`, T2 fails with SQLSTATE `40001` and the application retries the whole transaction. If T1 rolled back, T2 proceeds on the original row.

### The lock queue

Lock requests on a table are granted in arrival order. A new request must wait if it conflicts with a lock that is **held** or with one that is **already waiting** ahead of it. The second rule causes the most famous lock outage:

```mermaid
sequenceDiagram
    participant R as Report query
    participant M as Migration
    participant A as API queries
    participant T as Lock on orders
    R->>T: SELECT (ACCESS SHARE) granted
    M->>T: ALTER TABLE orders ADD COLUMN (ACCESS EXCLUSIVE)
    T-->>M: wait, conflicts with the report
    A->>T: SELECT (ACCESS SHARE)
    T-->>A: wait, queued behind the migration
    Note over A,T: every new query on orders now queues, the pool fills, the API times out
    M->>M: lock_timeout of 2s fires, ERROR 55P03
    T-->>A: granted, the migration left the queue
```

The `ALTER` itself would take milliseconds. The damage comes from waiting. `lock_timeout` turns "wait forever and block everyone" into "give up after 2 seconds, let traffic flow, retry later".

---

## 3. Key Concepts

### Row-level lock modes

| Mode | Taken explicitly by | Taken implicitly by | Blocks |
|---|---|---|---|
| `FOR KEY SHARE` | `SELECT … FOR KEY SHARE` | Foreign-key checks on the **parent** row (inserting an `order` locks its `customers` row) | `FOR UPDATE` only |
| `FOR SHARE` | `SELECT … FOR SHARE` | — | `FOR NO KEY UPDATE`, `FOR UPDATE` |
| `FOR NO KEY UPDATE` | `SELECT … FOR NO KEY UPDATE` | Any `UPDATE` that does not change a key column | `FOR SHARE`, `FOR NO KEY UPDATE`, `FOR UPDATE` |
| `FOR UPDATE` | `SELECT … FOR UPDATE` | `DELETE`; an `UPDATE` that changes a column with a unique index usable by a foreign key | All four modes |

The "key / no key" split keeps foreign keys from fighting ordinary updates. Inserting an `order_items` row takes `FOR KEY SHARE` on its `products` row, while another transaction can still run `UPDATE products SET price_cents = …`. Only deleting the product or changing its `id` must wait. (Before PostgreSQL 9.3, FK checks took `FOR SHARE` — a classic source of blocking.)

**Rule of thumb:** if you lock a row only to update non-key columns, `FOR NO KEY UPDATE` is enough and plays better with foreign keys than `FOR UPDATE`.

### Table-level lock modes

The names are historical: `ROW EXCLUSIVE` is a **table** lock that ordinary writes take.

| Mode | Typical statements | Concurrent reads? | Concurrent writes? |
|---|---|---|---|
| `ACCESS SHARE` | `SELECT` | Yes | Yes |
| `ROW SHARE` | `SELECT … FOR UPDATE/SHARE` | Yes | Yes |
| `ROW EXCLUSIVE` | `INSERT`, `UPDATE`, `DELETE`, `MERGE` | Yes | Yes |
| `SHARE UPDATE EXCLUSIVE` | `VACUUM` (not `FULL`), `ANALYZE`, `CREATE INDEX CONCURRENTLY`, `ALTER TABLE … VALIDATE CONSTRAINT` | Yes | Yes (conflicts with itself and DDL) |
| `SHARE` | `CREATE INDEX` (without `CONCURRENTLY`) | Yes | **No** |
| `SHARE ROW EXCLUSIVE` | `CREATE TRIGGER`, `ALTER TABLE … ADD FOREIGN KEY` | Yes | **No** |
| `EXCLUSIVE` | `REFRESH MATERIALIZED VIEW CONCURRENTLY` | Yes | **No** |
| `ACCESS EXCLUSIVE` | `DROP TABLE`, `TRUNCATE`, `VACUUM FULL`, `CLUSTER`, `REFRESH MATERIALIZED VIEW`, `LOCK TABLE` (default), most `ALTER TABLE` (add/drop column, change type, `SET NOT NULL`, rename) | **No** | **No** |

Two practical consequences. A plain `CREATE INDEX` on a busy table stops all writes until it finishes, which is why [migrations](34-Database-Migrations.md) use `CREATE INDEX CONCURRENTLY`. And "fast" DDL such as adding a nullable column is only fast **once it has the lock**; getting the lock is the dangerous part.

### Waiting policies

| Option | Behaviour when the lock is taken | Error | Use for |
|---|---|---|---|
| (default) | Wait until the holder finishes | — | Normal transactional work |
| `NOWAIT` | Fail immediately | `55P03` lock_not_available | "Someone else is editing this, try later" UIs |
| `SKIP LOCKED` | Leave the locked rows out of the result | — | Job and outbox queues with many consumers |
| `SET LOCAL lock_timeout = '2s'` | Wait up to the limit, then fail | `55P03` | DDL in migrations; any statement that must not queue for long |
| `statement_timeout` | Cancels the whole statement, lock wait included | `57014` query_canceled | A ceiling for every query of an app role |

`SKIP LOCKED` gives an inconsistent view on purpose — right for a queue, wrong for a report or balance check. `NOWAIT` and `SKIP LOCKED` apply only to row locks; the table-level lock is still waited for normally.

### Two ways to run a job from a `SKIP LOCKED` queue

| Pattern | How | Good | Bad |
|---|---|---|---|
| **Hold the lock** | `BEGIN; SELECT … FOR UPDATE SKIP LOCKED LIMIT 1;` work; mark done; `COMMIT` | A crash releases the job instantly | One open transaction and connection per running job; old snapshots hold back `VACUUM` |
| **Lease** | One statement marks rows `running` with `locked_until` and commits; work runs outside any transaction | Short transactions; long jobs are fine | A crashed worker's jobs wait for lease expiry and a reaper; a job can run twice |

Use the lease pattern for anything slower than a few hundred milliseconds. The relay in [Asynchronous Processing](../Module-02-Core-Backend/19-Asynchronous-Processing.md) uses the same `FOR UPDATE SKIP LOCKED` claim for outbox rows.

### Advisory locks

An advisory lock locks a number that means something only to your application, such as "the nightly billing job" or "checkout for customer 42". Postgres enforces mutual exclusion but attaches no meaning to the key.

| Function | Scope | If the lock is taken |
|---|---|---|
| `pg_advisory_lock(bigint)` | Session | Waits |
| `pg_try_advisory_lock(bigint)` | Session | Returns `false` |
| `pg_advisory_xact_lock(bigint)` | Transaction | Waits |
| `pg_try_advisory_xact_lock(bigint)` | Transaction | Returns `false` |
| `pg_advisory_unlock(bigint)` | Session | Releases one hold; returns `false` and warns if you did not hold it |

There are also two-key forms `(int, int)` and `_shared` variants. Details that matter:

- **Session locks ignore transactions.** One taken inside a transaction that rolls back is **still held** until you unlock it or the connection closes. Lock twice, unlock twice.
- **Transaction locks release themselves** at commit or rollback. They are the safe choice behind PgBouncer in transaction mode.
- **One key space per database.** Keep a registry of keys, or use the two-key form `(class_id, object_id)` so "job 5" and "customer 5" cannot collide.

[Cron Jobs](../Module-02-Core-Backend/18-Cron-Jobs.md) shows the session-level version used to make a scheduled job run on one replica only.

### Observing locks

| Source | What it tells you |
|---|---|
| `pg_stat_activity` | Each session: `state` (`active`, `idle in transaction`, …), `wait_event_type = 'Lock'` when waiting on a lock, `xact_start`, current or last `query` |
| `pg_blocking_pids(pid)` | Array of PIDs blocking that session — both holders of conflicting locks and conflicting waiters ahead of it in the queue |
| `pg_locks` | Every heavyweight lock: `locktype` (`relation`, `transactionid`, `tuple`, `advisory`), `mode`, `granted`, and `waitstart` (PG 14+) |
| `log_lock_waits = on` | Logs any lock wait longer than `deadlock_timeout` (1 s by default), with the blocking PIDs |

`pg_locks` does **not** list every row lock: row locks live in the rows, and show up only as a `transactionid` wait when someone is blocked. The `pgrowlocks` extension lists one table's row locks.

### MySQL (InnoDB) difference

InnoDB also uses MVCC, so plain `SELECT` is a non-locking read. Locking reads and `UPDATE`/`DELETE` behave differently, though:

- Under its default `REPEATABLE READ`, InnoDB takes **next-key locks**: a lock on each index record it scans **plus the gap before it**. Gap locks block `INSERT`s into that gap, which is how InnoDB prevents phantom rows. Postgres has no gap locks; its `SERIALIZABLE` level uses predicate tracking that does not block.
- Locks are placed on **index records scanned**, not rows returned. An `UPDATE … WHERE` on an unindexed column scans, and locks, the whole table.
- Under `READ COMMITTED`, InnoDB disables most gap locking, which reduces both blocking and deadlocks.
- `SELECT … FOR UPDATE NOWAIT` and `SKIP LOCKED` exist from MySQL 8.0. A lock wait gives up after `innodb_lock_wait_timeout` (50 s by default) with error 1205.

---

## 4. Code Examples

Scenario: background jobs (for example "send the order confirmation email") live in a `jobs` table. Several worker processes claim work with `FOR UPDATE SKIP LOCKED`. An ops helper shows who blocks whom, and runs DDL with a lock timeout so a migration can never freeze the `orders` table.

### SQL

```sql
-- A Postgres-backed job queue. The partial index keeps the claim query fast
-- no matter how many finished jobs pile up.
CREATE TABLE jobs (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  kind          text        NOT NULL,
  payload       jsonb       NOT NULL,
  status        text        NOT NULL DEFAULT 'queued'
                CHECK (status IN ('queued', 'running', 'done', 'failed')),
  attempts      integer     NOT NULL DEFAULT 0,
  run_at        timestamptz NOT NULL DEFAULT now(),
  locked_by     text,
  locked_until  timestamptz
);
CREATE INDEX jobs_ready_idx ON jobs (run_at) WHERE status = 'queued';

-- Claim up to 10 jobs. Rows another worker is claiming right now are skipped, not waited for.
WITH next AS (
  SELECT id FROM jobs
  WHERE status = 'queued' AND run_at <= now()
  ORDER BY run_at
  LIMIT 10
  FOR UPDATE SKIP LOCKED
)
UPDATE jobs j
SET status = 'running', attempts = j.attempts + 1,
    locked_by = 'worker-a', locked_until = now() + interval '5 minutes'
FROM next
WHERE j.id = next.id
RETURNING j.id, j.kind, j.attempts;

-- Reaper (run every minute from a scheduler): requeue jobs whose worker died.
UPDATE jobs SET status = 'queued', locked_by = NULL, locked_until = NULL
WHERE status = 'running' AND locked_until < now();

-- Who is blocking whom?
SELECT w.pid                                   AS waiting_pid,
       now() - w.query_start                   AS waiting_for,
       left(w.query, 50)                       AS waiting_query,
       b.pid                                   AS blocking_pid,
       b.state                                 AS blocking_state,
       now() - b.xact_start                    AS blocker_xact_age,
       left(b.query, 50)                       AS blocking_query
FROM pg_stat_activity w
CROSS JOIN LATERAL unnest(pg_blocking_pids(w.pid)) AS bp(pid)
JOIN pg_stat_activity b ON b.pid = bp.pid
WHERE w.wait_event_type = 'Lock'
ORDER BY waiting_for DESC;

-- Safe DDL: give up after 2 s instead of queueing every query on orders behind us.
BEGIN;
SET LOCAL lock_timeout = '2s';
ALTER TABLE orders ADD COLUMN gift_note text;
COMMIT;
```

Illustrative output of the "who is blocking whom" query during a stuck migration:

```text
 waiting_pid |   waiting_for   |                   waiting_query                    | blocking_pid |    blocking_state   | blocker_xact_age |                    blocking_query
-------------+-----------------+----------------------------------------------------+--------------+---------------------+------------------+-----------------------------------------------------
       41877 | 00:00:14.213450 | ALTER TABLE orders ADD COLUMN gift_note text       |        41002 | idle in transaction | 00:15:12.908772  | SELECT id, status FROM orders WHERE customer_id = $
       41901 | 00:00:13.790121 | SELECT id, status, total_cents FROM orders WHERE i |        41877 | active              | 00:00:14.213450  | ALTER TABLE orders ADD COLUMN gift_note text
       41915 | 00:00:13.104662 | SELECT id, status, total_cents FROM orders WHERE i |        41877 | active              | 00:00:14.213450  | ALTER TABLE orders ADD COLUMN gift_note text
```

Read it as a chain. The API queries are blocked by the migration (a *soft* block: it only waits, but is ahead of them in the queue). The migration is blocked by PID 41002, which ran a `SELECT` 15 minutes ago and never committed; its `query` column shows the *last* statement it ran. Fix the root with `SELECT pg_terminate_backend(41002);`, then find the code path that leaks the transaction.

### Node.js / TypeScript

The worker loop. The claim is a single statement, so it is its own transaction and `pool.query` is safe; the row locks last only for that statement.

```ts
// npm i pg && npm i -D @types/pg   — Node.js 22+, TypeScript 5, ESM
import pg from "pg";
import { randomUUID } from "node:crypto";
import { setTimeout as sleep } from "node:timers/promises";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
const WORKER_ID = `worker-${process.pid}-${randomUUID().slice(0, 8)}`;
const LEASE_SECONDS = 300; // must exceed the slowest job in a batch, or it runs twice

// pg returns bigint columns as strings (they can exceed 2^53), so id is a string.
interface Job { id: string; kind: string; payload: Record<string, unknown>; attempts: number }

const handlers: Record<string, (payload: Record<string, unknown>) => Promise<void>> = {
  "order.confirmation": (p) => sendOrderEmail(Number(p.orderId)),
};

async function claim(limit: number): Promise<Job[]> {
  const { rows } = await pool.query<Job>(
    `WITH next AS (
       SELECT id FROM jobs
       WHERE status = 'queued' AND run_at <= now()
       ORDER BY run_at LIMIT $1
       FOR UPDATE SKIP LOCKED
     )
     UPDATE jobs j
     SET status = 'running', attempts = j.attempts + 1,
         locked_by = $2, locked_until = now() + $3 * interval '1 second'
     FROM next WHERE j.id = next.id
     RETURNING j.id, j.kind, j.payload, j.attempts`,
    [limit, WORKER_ID, LEASE_SECONDS],
  );
  return rows;
}

async function finish(job: Job, failed: boolean): Promise<void> {
  // `locked_by = $2` fences us off: if our lease expired and another worker re-claimed
  // the job, this matches 0 rows instead of overwriting the new owner's state.
  const backoff = Math.min(3600, 10 * 2 ** job.attempts);
  await pool.query(
    `UPDATE jobs
     SET status = CASE WHEN NOT $3 THEN 'done' WHEN attempts >= 5 THEN 'failed' ELSE 'queued' END,
         run_at = CASE WHEN $3 THEN now() + $4 * interval '1 second' ELSE run_at END,
         locked_by = NULL, locked_until = NULL
     WHERE id = $1 AND locked_by = $2`,
    [job.id, WORKER_ID, failed, backoff],
  );
}

export async function runWorker(signal: AbortSignal): Promise<void> {
  while (!signal.aborted) {
    const jobs = await claim(10);
    if (jobs.length === 0) {
      await sleep(1000, undefined, { signal }).catch(() => undefined); // idle poll; abort wakes us
      continue;
    }
    for (const job of jobs) {
      try {
        const handler = handlers[job.kind];
        if (!handler) throw new Error(`no handler for ${job.kind}`);
        await handler(job.payload);
        await finish(job, false);
      } catch (err) {
        console.error({ jobId: job.id, err }, "job failed");
        await finish(job, true);
      }
    }
  }
}

declare function sendOrderEmail(orderId: number): Promise<void>;
```

Ops helpers: the blocking report, and DDL with a lock timeout. `SET LOCAL` only lasts for the current transaction, and that transaction lives on one connection, so this code checks out a dedicated client.

```ts
import pg from "pg";
import { setTimeout as sleep } from "node:timers/promises";

interface Blocking {
  waiting_pid: number; waiting_seconds: number; waiting_query: string;
  blocking_pid: number; blocking_state: string; blocker_xact_seconds: number; blocking_query: string;
}

export async function blockingReport(pool: pg.Pool): Promise<Blocking[]> {
  const { rows } = await pool.query<Blocking>(`
    SELECT w.pid AS waiting_pid,
           extract(epoch FROM now() - w.query_start)::int AS waiting_seconds,
           left(w.query, 120) AS waiting_query,
           b.pid AS blocking_pid, b.state AS blocking_state,
           extract(epoch FROM now() - b.xact_start)::int AS blocker_xact_seconds,
           left(b.query, 120) AS blocking_query
    FROM pg_stat_activity w
    CROSS JOIN LATERAL unnest(pg_blocking_pids(w.pid)) AS bp(pid)
    JOIN pg_stat_activity b ON b.pid = bp.pid
    WHERE w.wait_event_type = 'Lock'
    ORDER BY waiting_seconds DESC`);
  return rows;
}

// `ddl` is trusted migration text from the repository, never user input.
export async function runDdl(pool: pg.Pool, ddl: string, maxAttempts = 10): Promise<void> {
  for (let attempt = 1; ; attempt++) {
    const client = await pool.connect();
    try {
      await client.query("BEGIN");
      await client.query("SET LOCAL lock_timeout = '2s'");
      await client.query(ddl);
      await client.query("COMMIT");
      return;
    } catch (err) {
      await client.query("ROLLBACK").catch(() => undefined);
      const code = (err as { code?: string }).code;
      if (code !== "55P03" || attempt >= maxAttempts) throw err;
      console.warn({ attempt, blockers: await blockingReport(pool) }, "DDL lock timeout, retrying");
      await sleep(1000 * attempt + Math.random() * 1000); // let queued traffic drain first
    } finally {
      client.release();
    }
  }
}
```

### Python

The same worker with psycopg 3. A worker owns one connection in autocommit mode, so each statement commits on its own, like `pool.query` in Node.

```python
# pip install "psycopg[binary]"   — Python 3.12+
import os
import socket
import threading
from collections.abc import Callable
from datetime import timedelta

import psycopg
from psycopg.rows import dict_row

WORKER_ID = f"{socket.gethostname()}-{os.getpid()}"
LEASE = timedelta(minutes=5)  # psycopg sends timedelta as a Postgres interval

CLAIM_SQL = """
WITH next AS (
  SELECT id FROM jobs
  WHERE status = 'queued' AND run_at <= now()
  ORDER BY run_at LIMIT %(limit)s
  FOR UPDATE SKIP LOCKED
)
UPDATE jobs j
SET status = 'running', attempts = j.attempts + 1,
    locked_by = %(worker)s, locked_until = now() + %(lease)s
FROM next WHERE j.id = next.id
RETURNING j.id, j.kind, j.payload, j.attempts
"""

FINISH_SQL = """
UPDATE jobs
SET status = CASE WHEN NOT %(failed)s THEN 'done' WHEN attempts >= 5 THEN 'failed' ELSE 'queued' END,
    run_at = CASE WHEN %(failed)s THEN now() + %(backoff)s ELSE run_at END,
    locked_by = NULL, locked_until = NULL
WHERE id = %(id)s AND locked_by = %(worker)s
"""


def send_order_email(payload: dict) -> None:
    print(f"emailing confirmation for order {payload['orderId']}")


HANDLERS: dict[str, Callable[[dict], None]] = {"order.confirmation": send_order_email}


def run_worker(dsn: str, stop: threading.Event) -> None:
    with psycopg.connect(dsn, autocommit=True, row_factory=dict_row) as conn:
        while not stop.is_set():
            jobs = conn.execute(CLAIM_SQL, {"limit": 10, "worker": WORKER_ID, "lease": LEASE}).fetchall()
            if not jobs:
                stop.wait(1.0)  # idle poll that still reacts to shutdown at once
                continue
            for job in jobs:
                failed = False
                try:
                    HANDLERS[job["kind"]](job["payload"])  # jsonb arrives as a dict
                except Exception as exc:
                    failed = True
                    print(f"job {job['id']} failed: {exc!r}")
                backoff = timedelta(seconds=min(3600, 10 * 2 ** job["attempts"]))
                # The locked_by fence: a worker whose lease expired cannot overwrite the new owner.
                conn.execute(FINISH_SQL, {"failed": failed, "backoff": backoff,
                                          "id": job["id"], "worker": WORKER_ID})
```

Ops helpers. Here `conn.transaction()` wraps `SET LOCAL` and the DDL in one transaction on one connection, and rolls back if the block raises.

```python
import random
import time

import psycopg
from psycopg import errors
from psycopg.rows import dict_row

BLOCKING_SQL = """
SELECT w.pid AS waiting_pid,
       extract(epoch FROM now() - w.query_start)::int AS waiting_seconds,
       left(w.query, 120) AS waiting_query,
       b.pid AS blocking_pid, b.state AS blocking_state,
       extract(epoch FROM now() - b.xact_start)::int AS blocker_xact_seconds,
       left(b.query, 120) AS blocking_query
FROM pg_stat_activity w
CROSS JOIN LATERAL unnest(pg_blocking_pids(w.pid)) AS bp(pid)
JOIN pg_stat_activity b ON b.pid = bp.pid
WHERE w.wait_event_type = 'Lock'
ORDER BY waiting_seconds DESC
"""


def blocking_report(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        return cur.execute(BLOCKING_SQL).fetchall()


def run_ddl(conn: psycopg.Connection, ddl: str, max_attempts: int = 10) -> None:
    """`ddl` is trusted migration text from the repository, never user input."""
    for attempt in range(1, max_attempts + 1):
        try:
            with conn.transaction():
                conn.execute("SET LOCAL lock_timeout = '2s'")
                conn.execute(ddl)
            return
        except errors.LockNotAvailable:  # SQLSTATE 55P03
            if attempt == max_attempts:
                raise
            print(f"DDL lock timeout (attempt {attempt}), blockers: {blocking_report(conn)}")
            time.sleep(attempt + random.random())


if __name__ == "__main__":
    with psycopg.connect("postgresql://postgres:dev@localhost:5432/postgres", autocommit=True) as c:
        run_ddl(c, "ALTER TABLE orders ADD COLUMN IF NOT EXISTS gift_note text")
```

**Runtime differences to notice.** `pg` returns `bigint` as a string, so the Node `Job.id` is a `string`; psycopg returns a Python `int`. The Node worker is one async loop whose database concurrency is capped by the pool (`max: 5`); the Python worker blocks its thread while a handler runs, so you scale it with more processes. Either way, `SKIP LOCKED` is what lets the copies run side by side.

---

## 5. Production Concerns

- **Timeouts as policy, set per role.** `ALTER ROLE app SET statement_timeout = '5s'` and `SET idle_in_transaction_session_timeout = '60s'` stop one stuck request from holding locks for hours. Migrations get their own role or a `SET LOCAL lock_timeout` of a few seconds plus retries.
- **`idle in transaction` is the usual root blocker.** `BEGIN`, a query, then an HTTP call to a payment provider holds every lock for the whole call. Alert on the oldest transaction age (`now() - min(xact_start)`).
- **Turn on `log_lock_waits`.** It logs every wait longer than `deadlock_timeout` (1 s) with the blocking PIDs, turning "the API was slow at 14:02" into a named query.
- **Metrics.** Track sessions with `wait_event_type = 'Lock'`, the longest lock wait, the oldest transaction age, and the `55P03` rate. Rising lock waits with flat traffic mean a new hot row or a leaked transaction.
- **Locking reads are writes.** `SELECT … FOR UPDATE` writes the locker's ID into each row, which dirties pages and generates WAL. A hot-standby replica rejects it because it would have to write, so route locking reads to the primary.
- **Connection poolers.** Behind PgBouncer in transaction mode, session state does not stick to "your" connection. Use `SET LOCAL` instead of `SET`, and `pg_advisory_xact_lock` instead of session-level advisory locks.
- **Shared-memory limits.** The table-lock table is sized by `max_locks_per_transaction` (default 64); one transaction touching thousands of partitions can fail with "out of shared memory". Row locks are not affected.
- **Queue tables bloat.** Every claim and finish leaves a dead row version; archive finished jobs in batches and check that autovacuum keeps up.

---

## 6. Common Mistakes

- **Running DDL without `lock_timeout`** — the `ALTER` waits behind a long query, and every request to the table queues behind the `ALTER` — `SET LOCAL lock_timeout = '2s'` in the migration transaction, retry with backoff, and run long reports on a replica.
- **Assuming `SELECT` blocks writes in Postgres** — teams add `FOR SHARE` or `LOCK TABLE` "to be safe" and create the blocking they feared — under MVCC plain reads need no lock; lock only the rows you are about to change based on what you read.
- **Using `FOR UPDATE` when `FOR NO KEY UPDATE` would do** — `FOR UPDATE` on a parent row also blocks every foreign-key check from child inserts — use `FOR NO KEY UPDATE` unless you will delete the row or change its key.
- **A `SKIP LOCKED` claim without `ORDER BY` and `LIMIT`** — workers lock far more rows than they need, or starve old jobs — claim a small batch in a defined order, backed by a matching partial index.
- **Session advisory lock taken through a transaction pooler** — the unlock runs on a different server connection, so the lock is never released and the job never runs again — use `pg_advisory_xact_lock`, or hold one dedicated connection for the whole run.
- **Calling `pg_advisory_lock` in a query with `LIMIT`** — `SELECT pg_advisory_lock(id) FROM jobs WHERE … LIMIT 10` may lock rows the `LIMIT` later throws away, leaking locks you never unlock — select the IDs in a subquery first, then lock them in the outer query.

---

## 7. Comparison Table

Ways to stop two pieces of work from colliding in PostgreSQL:

| Tool | What it locks | When the lock is taken | Released | Best for |
|---|---|---|---|---|
| `UPDATE … WHERE` (implicit row lock) | Matching rows | During the statement | End of transaction | Most writes; atomic conditional updates |
| `SELECT … FOR UPDATE` | Selected rows | Before you decide what to write | End of transaction | Read-check-write on a few hot rows ([pessimistic locking](32-Optimistic-vs-Pessimistic-Locking.md)) |
| `FOR UPDATE SKIP LOCKED` | Unclaimed rows only | At claim time | End of the claim transaction | Job and outbox queues with many consumers |
| Advisory lock | An application-chosen number | Whenever you call it | Transaction end or explicit unlock / disconnect | Singleton jobs; "one checkout per customer"; work with no row to lock yet |
| `SERIALIZABLE` isolation | Nothing (tracks read/write dependencies) | — | — | Complex invariants across many rows; costs retries on `40001` |

---

## 8. Interview Questions

**[Junior] Does a `SELECT` block an `UPDATE` in PostgreSQL?**
No. Postgres uses MVCC: the `UPDATE` writes a new row version, and the reader keeps reading the version that its snapshot can see. A plain `SELECT` takes only an `ACCESS SHARE` table lock, which conflicts with nothing except `ACCESS EXCLUSIVE`. Two `UPDATE`s on the same row do block each other: the second waits until the first commits or rolls back.

**[Junior] What is `SELECT … FOR UPDATE` for?**
It reads rows and locks them so no other transaction can update, delete or lock them until you commit. Use it when you read a value, decide in code, then write — and keep that transaction short.

**[Mid] How does `SKIP LOCKED` make a job queue safe with several workers?**
Each worker runs `SELECT … FOR UPDATE SKIP LOCKED LIMIT n`. Rows another worker has locked are skipped instead of waited for, so workers never block each other or claim the same row. In the lease pattern the same statement marks rows `running` with a deadline and commits. A reaper requeues expired leases, so a job can run twice and handlers must be idempotent.

**[Mid] What is the difference between `FOR UPDATE` and `FOR NO KEY UPDATE`?**
`FOR NO KEY UPDATE` is what an ordinary `UPDATE` takes. It does not conflict with `FOR KEY SHARE`, the lock that foreign-key checks take on the parent row. `FOR UPDATE` is taken by `DELETE` and by updates that change a key column, and it conflicts with everything. If you explicitly lock a parent row with `FOR UPDATE`, you block every concurrent insert of child rows that reference it; `FOR NO KEY UPDATE` avoids that.

**[Senior] A migration that adds a nullable column took the site down. Explain what happened and how you would prevent it.**
`ADD COLUMN` needs `ACCESS EXCLUSIVE`. A long query or an `idle in transaction` session held `ACCESS SHARE`, so the `ALTER` waited — and every new `SELECT`, conflicting with the queued `ACCESS EXCLUSIVE`, queued behind it. The pool filled and the API timed out, though the `ALTER` itself takes milliseconds. Prevention: `SET LOCAL lock_timeout = '2s'` plus retries in every migration, `idle_in_transaction_session_timeout` and `statement_timeout` for app roles, and long reports on a replica.

**[Senior] Users report that checkout hangs for 30 seconds at random. How do you investigate?**
First, look at it live: query `pg_stat_activity` for sessions with `wait_event_type = 'Lock'` and walk `pg_blocking_pids()` to the root blocker. Note its `state`, `xact_start` and last query. Enable `log_lock_waits` so past waits are logged with the PIDs involved. Typical causes: a transaction kept open across a payment API call, a hot inventory row, or a batch job updating many rows in one long transaction. Fix by shortening the transaction, splitting the batch, or using an atomic conditional `UPDATE`.

**[Senior] How do Postgres and MySQL InnoDB differ in what an `UPDATE … WHERE` locks?**
Postgres locks only the rows the statement updates, with no gap locks and no escalation. InnoDB under `REPEATABLE READ` locks every index record it scans plus the gaps between them (next-key locks) to stop phantoms. So a range update in InnoDB blocks inserts into that range, and an update on an unindexed column effectively locks the table. Switching InnoDB to `READ COMMITTED` removes most gap locking.

---

## 9. Cheat Sheet

```text
MVCC          plain SELECT: no row locks, ACCESS SHARE only → readers and writers don't block each other
Row modes     KEY SHARE < SHARE < NO KEY UPDATE < UPDATE
Implicit      UPDATE → NO KEY UPDATE (FOR UPDATE if a key column changes); DELETE → FOR UPDATE; FK check → KEY SHARE on parent
Table modes   SELECT=ACCESS SHARE; DML=ROW EXCLUSIVE; CREATE INDEX=SHARE (blocks writes);
              CIC/VACUUM/ANALYZE=SHARE UPDATE EXCLUSIVE; most ALTER/DROP/TRUNCATE/VACUUM FULL=ACCESS EXCLUSIVE
Lock queue    waiting ACCESS EXCLUSIVE blocks all later queries → SET LOCAL lock_timeout='2s' + retry for DDL
Wait policy   default wait | NOWAIT → 55P03 | SKIP LOCKED → skip rows | lock_timeout → 55P03
Queue claim   WITH next AS (SELECT id … ORDER BY run_at LIMIT n FOR UPDATE SKIP LOCKED) UPDATE … RETURNING
Advisory      pg_try_advisory_xact_lock(key) auto-releases; session locks survive COMMIT/ROLLBACK
Diagnose      pg_stat_activity (state, wait_event_type='Lock', xact_start) + pg_blocking_pids(pid)
Root blocker  usually 'idle in transaction' → idle_in_transaction_session_timeout
pg_locks      row locks appear only as transactionid waits; no lock escalation in Postgres
Logging       log_lock_waits=on → logs waits > deadlock_timeout (1 s)
Replicas      FOR UPDATE not allowed on hot standby
MySQL         RR default: next-key (record + gap) locks on scanned index records; RC disables most gap locks
```

---

## Related Topics

- [Isolation Levels](29-Isolation-Levels.md) — what a blocked `UPDATE` does after the blocker commits depends on the level
- [Deadlocks](31-Deadlocks.md) — what happens when two lock waits form a cycle
- [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md) — when to use `FOR UPDATE` and when a version column is better
- [Database Migrations](34-Database-Migrations.md) — applying `lock_timeout` and `CONCURRENTLY` to real schema changes
- [Cron Jobs](../Module-02-Core-Backend/18-Cron-Jobs.md) — session-level advisory locks for single-run scheduled jobs
- [Asynchronous Processing](../Module-02-Core-Backend/19-Asynchronous-Processing.md) — the outbox relay built on `FOR UPDATE SKIP LOCKED`

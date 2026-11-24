# ACID

> **Module 03 · Databases** · Prerequisites: [Transactions](27-Transactions.md) · Next: [Isolation Levels](29-Isolation-Levels.md)

---

## ⏱ If You Only Have 2 Minutes

- **Atomicity**: a transaction's writes all take effect or none do. In PostgreSQL every row version is stamped with the writing transaction's ID, and the commit log (`pg_xact`) records whether that ID committed or aborted. A rollback just marks the ID aborted, so it is nearly instant.
- **Consistency** means the constraints *you declared* (`NOT NULL`, `CHECK`, `UNIQUE`, foreign keys, exclusion constraints) hold at every commit. It is not CAP's "C" (linearizability), and it knows nothing about rules you only wrote in application code.
- **Isolation**: concurrent transactions should not see each other's half-finished work. Full isolation is *serializable*, but PostgreSQL defaults to Read Committed and MySQL to Repeatable Read — weaker levels with known anomalies ([Isolation Levels](29-Isolation-Levels.md)).
- **Durability**: once `COMMIT` returns, the change survives a crash. PostgreSQL writes a commit record to the **write-ahead log (WAL)** and, with the default `synchronous_commit = on`, flushes it to disk before it answers.
- `SET LOCAL synchronous_commit = off` trades durability for latency on one transaction: a crash can lose the last few hundred milliseconds of such commits (up to 3 × `wal_writer_delay`, 600 ms by default), but never corrupts the database. Good for page views; wrong for payments.
- Durability is per server. With default **asynchronous replication**, a commit acknowledged by a primary that dies before streaming it is lost after failover. Synchronous replication closes that gap at a latency cost.
- MySQL InnoDB gets the same properties differently: a **redo log** for durability and crash recovery, and an **undo log** for rollback and consistent reads. `innodb_flush_log_at_trx_commit = 1` (the default) flushes the redo log at every commit.

---

## 1. What It Is and Why It Exists

**ACID** is the set of four guarantees a database gives a transaction: **A**tomicity, **C**onsistency, **I**solation and **D**urability. The term was coined by Härder and Reuter in 1983. It describes what you can rely on after you call `COMMIT` — and, just as important in an interview, what you cannot.

**Analogy:** a bank's paper ledger kept by a careful clerk. The clerk writes each transfer in pen in a journal *before* touching the account books (durability, via a log). A transfer is either fully entered or crossed out entirely (atomicity). The clerk refuses an entry that leaves an account below its overdraft limit (consistency — but only for limits written on the account card). Two clerks working at once never see each other's half-written lines (isolation).

**What breaks without each property:**

| Property | Without it | Promises | Does **not** promise |
|---|---|---|---|
| Atomicity | A crash after decrementing stock but before inserting the order leaves stock missing | All writes of a transaction become visible together, or none ever do | Atomicity across two databases, a database and a queue, or two services |
| Consistency | Bad application code writes `available = -3` | Declared constraints hold when the transaction commits | That undeclared business rules hold; that replicas agree (that is CAP's C) |
| Isolation | A report reads half of a transfer | Each transaction behaves *as if* it ran alone — to the degree the isolation level says | Serializability by default; freedom from lost updates or write skew at lower levels |
| Durability | A power cut erases orders the user was told succeeded | A committed transaction survives a crash of the database server | Survival if `fsync` is off, the disk lies about flushing, the disk dies without a replica, or the primary fails over to a replica that never received the commit |

Atomicity and durability are mostly about **failures** (crashes, errors). Isolation is about **concurrency**. Consistency is the odd one out: it is mostly the application's job, and the database helps only through the constraints you declare.

---

## 2. How It Works

PostgreSQL implements A, I and D with two mechanisms: the **write-ahead log** and **multi-version concurrency control (MVCC)**.

### Following one transaction

Take `BEGIN; UPDATE inventory SET available = available - 1 WHERE product_id = 1; COMMIT;`.

1. **Transaction ID.** On its first write, the transaction gets a transaction ID (xid), say `7461`. Read-only transactions never need one.
2. **New row version.** PostgreSQL does not overwrite the row. It writes a **new tuple** (row version) with `xmin = 7461`, and sets `xmax = 7461` on the old tuple, meaning "deleted by 7461". Both versions sit in the table page in shared memory.
3. **WAL records.** Before the changed page may ever be written to the data files, a WAL record describing the change is appended to the WAL buffers. This is the *write-ahead* rule: log first, data later.
4. **Commit record.** At `COMMIT`, a commit record for `7461` is appended to the WAL, and the WAL is flushed (`fsync` or equivalent) up to and including that record.
5. **Commit status.** `7461` is marked committed in `pg_xact`, the commit log that stores two bits of status per transaction. Row locks are released.
6. **Reply.** Only now does the client get `COMMIT`.
7. **Later.** The background writer and the checkpointer write the dirty data pages to the table files at their own pace. A **checkpoint** guarantees all changes up to a WAL position are in the data files, so older WAL can be recycled.

```mermaid
sequenceDiagram
    participant C as Client
    participant B as Backend process
    participant SB as Shared buffers (table pages)
    participant W as WAL on disk
    participant X as pg_xact (commit log)
    participant CP as Checkpointer
    C->>B: UPDATE inventory ... (xid 7461)
    B->>SB: old tuple xmax=7461, new tuple xmin=7461
    B->>B: append WAL record to WAL buffers
    C->>B: COMMIT
    B->>W: append commit record, flush WAL (fsync)
    B->>X: mark 7461 committed
    B-->>C: COMMIT
    CP->>SB: later, write dirty pages to data files
```

### Crash recovery

If the server crashes at any point, startup **replays the WAL** from the last checkpoint's redo point, reapplying every logged change to the data files. Then:

- transactions with a commit record in the WAL are committed — **durability**;
- transactions without one are treated as aborted, and their row versions are invisible — **atomicity**.

PostgreSQL needs no undo pass, because an aborted transaction's tuples are simply never visible. `VACUUM` removes them later. This is also why `ROLLBACK` is cheap: it marks the xid aborted in `pg_xact` and leaves the dead tuples for cleanup.

### Visibility (the isolation half)

When a statement runs, it takes a **snapshot**: which transactions had committed, and which were still in progress, at that moment. A tuple is visible to the snapshot if its `xmin` committed before the snapshot and its `xmax` is empty, aborted, or not yet committed as of the snapshot. Readers never block writers and writers never block readers, because each reader just picks the version its snapshot allows. How often a new snapshot is taken (per statement or per transaction) is what separates the isolation levels.

---

## 3. Key Concepts

### MVCC tuple versions: `xmin` and `xmax`

Every PostgreSQL table has hidden system columns you can select:

| Column | Meaning |
|---|---|
| `xmin` | xid of the transaction that created this row version |
| `xmax` | xid of the transaction that deleted or updated it (or locked it); `0` if none |
| `ctid` | Physical location (page, slot) of this version |

An `UPDATE` is a delete of the old version plus an insert of a new one. Consequences an interviewer may probe:

- **Rollback leaves garbage.** Aborted versions occupy space until `VACUUM` reclaims it. A workload that rolls back a lot creates bloat just like one that updates a lot.
- **Long transactions stop cleanup.** `VACUUM` cannot remove a dead version that some open snapshot might still need. One forgotten open transaction holds back cleanup in every table.
- **Transaction IDs are 32-bit.** They wrap around after about 4 billion, so `VACUUM` "freezes" old tuples to mark them visible to everyone. Autovacuum does this; disabling it eventually forces the server to stop accepting writes to protect itself.

### Consistency is the constraints you declare

The database enforces only what is in the schema:

| Constraint | Example from the sample schema | Can be deferred to `COMMIT`? |
|---|---|---|
| `NOT NULL` | `orders.customer_id` | No |
| `CHECK` | `inventory.available >= 0` | No |
| `UNIQUE` / `PRIMARY KEY` | `customers.email`, `payments.provider_ref` | Yes, if declared `DEFERRABLE` |
| `FOREIGN KEY` | `order_items.order_id → orders.id` | Yes, if declared `DEFERRABLE` |
| `EXCLUDE` | "no two bookings for the same room overlap" | Yes, if declared `DEFERRABLE` |

Constraints are not deferrable unless you say so, and then `INITIALLY DEFERRED` (or `SET CONSTRAINTS … DEFERRED` inside the transaction) moves the check to commit time. Deferring a foreign key is useful when two rows reference each other and must be inserted in the same transaction. Either way, a transaction cannot commit while a constraint is violated: the failed check aborts it.

What consistency does **not** cover: a rule like "an order's `total_cents` equals the sum of its items" is enforced by nobody unless you write a trigger or keep it in one carefully written transaction. And it is unrelated to the C in [CAP](02-CAP-Theorem.md), which means **linearizability**: every read, on any replica, sees the latest committed write. A single PostgreSQL server is ACID-consistent; reading from its asynchronous replica is not CAP-consistent. See [Consistency Models](03-Consistency-Models.md).

### Durability knobs: `fsync`, `synchronous_commit`, unlogged tables

| Setting | Default | What it changes | Risk if relaxed |
|---|---|---|---|
| `fsync` | `on` | Whether PostgreSQL forces WAL and data writes to stable storage at all | **Off** can cause unrecoverable corruption after an OS crash or power loss. Never in production. |
| `synchronous_commit` | `on` | Whether `COMMIT` waits for the WAL flush (and for standbys, if configured) | **Off**: recent commits can be lost after a crash; the database stays consistent |
| `full_page_writes` | `on` | Logs a full image of each page the first time it changes after a checkpoint, so a page torn by a partial write can be rebuilt | Off risks corrupted pages after power loss on most storage |
| `CREATE UNLOGGED TABLE` | — | The table's changes skip the WAL | Table is **emptied** after a crash and not replicated |

`synchronous_commit` can be changed per transaction by any user, which is what makes it useful:

```sql
BEGIN;
SET LOCAL synchronous_commit = off;   -- this transaction only
INSERT INTO product_views (product_id, customer_id) VALUES (1, 7);
COMMIT;                               -- returns before the WAL flush
```

The commit record is still written to the WAL; the WAL writer flushes it shortly after (the docs bound the loss window at three times `wal_writer_delay`, which defaults to 200 ms). A later synchronous commit flushes the WAL up to its own record, which makes earlier asynchronous commits durable too, since the WAL is sequential. Losing an asynchronous commit means losing the newest transactions in order — never a half-applied one.

Durability also depends on hardware honesty. A disk write cache without power-loss protection can report a flush as done when it is not; PostgreSQL ships `pg_test_fsync` to measure what your storage really does. The operating-system side of this is in [File Systems Basics](../Module-04-Operating-Systems/30-File-Systems-Basics.md).

### Replication is not durability

The "D" in ACID is a promise from **one server about its own disk**. Replication adds copies, but by default PostgreSQL streaming replication is **asynchronous**: the primary acknowledges `COMMIT` after its local flush and streams WAL to standbys afterwards.

The failure: a customer pays, the primary commits and replies `200`, then the primary's host dies before the WAL reaches the standby. The standby is promoted. The payment row does not exist on the new primary, even though the user saw success. The old primary's disk still has it, but you have failed over past it.

Synchronous replication fixes this by making `COMMIT` wait for standbys listed in `synchronous_standby_names`:

| `synchronous_commit` | `COMMIT` returns after |
|---|---|
| `off` | Nothing is flushed yet |
| `local` | Local WAL flush only, even if sync standbys are configured |
| `remote_write` | Local flush + standby has received the WAL and written it to its OS (not yet flushed) |
| `on` | Local flush + standby has flushed the WAL to disk |
| `remote_apply` | Local flush + standby has replayed it, so reads on the standby see it |

The cost is a network round trip on every commit, and availability: if no synchronous standby is reachable, commits on the primary **wait**. If the client cancels that wait, PostgreSQL warns that the transaction has already committed locally but may not be replicated — another ambiguous-commit case. Details are in [Replication](../Module-07-Advanced-Backend-and-System-Design/18-Replication.md).

### MySQL InnoDB difference: redo and undo logs

InnoDB reaches the same guarantees with different machinery:

| Concern | PostgreSQL | MySQL InnoDB |
|---|---|---|
| Durability log | WAL | **Redo log**, plus the binary log for replication |
| Commit flush setting | `synchronous_commit` (`on` by default) | `innodb_flush_log_at_trx_commit`: `1` (default) flush every commit; `2` write at commit, flush about once per second; `0` write and flush about once per second |
| Old row versions | Stored in the table as dead tuples | Stored in the **undo log**; consistent reads rebuild old versions from it |
| Rollback | Mark xid aborted — near-instant | Apply undo records — a big transaction's rollback can take as long as, or longer than, the work it undoes |
| Cleanup | `VACUUM` | Purge threads; long transactions grow the "history list length" |

With `innodb_flush_log_at_trx_commit = 2`, a MySQL process crash loses nothing but an OS crash can lose about a second of commits; with `0`, even a `mysqld` crash can. Keep `sync_binlog = 1` (the 8.0 default) so the binary log used by replicas is also flushed per commit.

---

## 4. Code Examples

Scenario: a warehouse recount sends stock corrections for several products. They must apply all together or not at all. The `CHECK (available >= 0)` constraint on `inventory` is the only guard — no application-side check — so we can watch atomicity and consistency work together. Then a low-value write (recording a product view) chooses relaxed durability for itself only.

Extra table for the page-view example:

```sql
CREATE TABLE product_views (
  product_id   bigint      NOT NULL REFERENCES products(id),
  customer_id  bigint      REFERENCES customers(id),   -- NULL for anonymous visitors
  viewed_at    timestamptz NOT NULL DEFAULT now()
);
```

### SQL

Two sessions, showing MVCC versions and an atomic rollback. Illustrative output; the xids will differ on your machine.

```sql
-- Starting state: product 1 has 42 available, product 2 has 3.

-- Session A
BEGIN;
SELECT pg_current_xact_id();                    -- 7461 (assigns the xid now)
UPDATE inventory SET available = available + 10 WHERE product_id = 1;
SELECT xmin, xmax, product_id, available FROM inventory WHERE product_id = 1;
--  xmin | xmax | product_id | available
--  7461 |    0 |          1 |        52       ← A sees its own new version

-- Session B, while A is still open
SELECT xmin, xmax, product_id, available FROM inventory WHERE product_id = 1;
--  xmin | xmax | product_id | available
--  7455 | 7461 |          1 |        42       ← the old version, marked "deleted by 7461", still visible

-- Session A continues: the second correction breaks the constraint
UPDATE inventory SET available = available - 5 WHERE product_id = 2;
-- ERROR:  new row for relation "inventory" violates check constraint "inventory_available_check"
-- DETAIL:  Failing row contains (2, -2, 0).
COMMIT;
-- ROLLBACK                                     ← COMMIT of an aborted transaction rolls back

-- Either session
SELECT product_id, available FROM inventory WHERE product_id IN (1, 2) ORDER BY product_id;
--  product_id | available
--           1 |        42                      ← the +10 that succeeded was undone too
--           2 |         3
```

After the rollback, session B can still see `xmax = 7461` on the surviving version. That is fine: visibility checks `pg_xact`, finds `7461` aborted, and ignores the `xmax`.

### Node.js / TypeScript

```ts
// npm i pg && npm i -D @types/pg   — Node.js 22+, TypeScript 5, ESM
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

interface PgErrorFields { code?: string; constraint?: string }
const pgFields = (err: unknown): PgErrorFields =>
  typeof err === "object" && err !== null ? (err as PgErrorFields) : {};

export interface Adjustment { productId: number; delta: number }
export type AdjustResult = { ok: true } | { ok: false; reason: "negative_stock"; productId?: number };

export async function applyAdjustments(adjustments: Adjustment[]): Promise<AdjustResult> {
  const client = await pool.connect();
  let current: number | undefined;
  try {
    await client.query("BEGIN");
    for (const { productId, delta } of [...adjustments].sort((a, b) => a.productId - b.productId)) {
      current = productId;
      // No "available + delta >= 0" check here: the CHECK constraint is the single source of truth.
      await client.query("UPDATE inventory SET available = available + $2 WHERE product_id = $1",
        [productId, delta]);
    }
    await client.query("COMMIT");
    return { ok: true };
  } catch (err) {
    await client.query("ROLLBACK"); // undoes the corrections that had already succeeded
    const { code, constraint } = pgFields(err);
    if (code === "23514" && constraint === "inventory_available_check") {
      return { ok: false, reason: "negative_stock", productId: current };
    }
    throw err;
  } finally {
    client.release();
  }
}

// A page view is worth less than an fsync. Relax durability for this transaction only.
export async function recordProductView(productId: number, customerId: number | null): Promise<void> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    // SET LOCAL ends with the transaction, so the pooled connection goes back with the default "on".
    await client.query("SET LOCAL synchronous_commit = off");
    await client.query("INSERT INTO product_views (product_id, customer_id) VALUES ($1, $2)",
      [productId, customerId]);
    await client.query("COMMIT"); // returns without waiting for the WAL flush
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
}

const stock = async () =>
  (await pool.query("SELECT product_id, available FROM inventory WHERE product_id = ANY($1) ORDER BY 1",
    [[1, 2]])).rows; // single autocommit statement: pool.query is fine here

console.table(await stock());                                     // 1 → 42, 2 → 3
console.log(await applyAdjustments([{ productId: 1, delta: 10 }, { productId: 2, delta: -5 }]));
// { ok: false, reason: 'negative_stock', productId: 2 }
console.table(await stock());                                     // unchanged: 1 → 42, 2 → 3
await recordProductView(1, 7);
await pool.end();
```

### Python

```python
# pip install "psycopg[binary]"   — Python 3.12+, psycopg 3
import psycopg
from psycopg import errors

DSN = "postgresql://app_rw:dev@localhost:5432/shop"


def stock(conn: psycopg.Connection, ids: list[int]) -> dict[int, int]:
    rows = conn.execute(
        "SELECT product_id, available FROM inventory WHERE product_id = ANY(%s)", (ids,)
    ).fetchall()
    return {product_id: available for product_id, available in rows}


def apply_adjustments(conn: psycopg.Connection, adjustments: list[tuple[int, int]]) -> int | None:
    """Apply all (product_id, delta) corrections or none. Returns the product that broke the rule."""
    current: int | None = None
    try:
        with conn.transaction():  # BEGIN ... COMMIT, or ROLLBACK if the block raises
            for product_id, delta in sorted(adjustments):
                current = product_id
                conn.execute(
                    "UPDATE inventory SET available = available + %s WHERE product_id = %s",
                    (delta, product_id),
                )
    except errors.CheckViolation as exc:  # SQLSTATE 23514, raised as its own exception class
        if exc.diag.constraint_name != "inventory_available_check":
            raise
        return current
    return None


def record_product_view(conn: psycopg.Connection, product_id: int, customer_id: int | None) -> None:
    with conn.transaction():
        conn.execute("SET LOCAL synchronous_commit = off")  # this transaction only
        conn.execute(
            "INSERT INTO product_views (product_id, customer_id) VALUES (%s, %s)",
            (product_id, customer_id),
        )


def main() -> None:
    # autocommit=True: psycopg sends no hidden BEGIN, so transaction() blocks are the only transactions.
    with psycopg.connect(DSN, autocommit=True) as conn:
        before = stock(conn, [1, 2])
        failed = apply_adjustments(conn, [(1, 10), (2, -5)])
        after = stock(conn, [1, 2])
        print(failed, before, after)          # 2 {1: 42, 2: 3} {1: 42, 2: 3}
        assert before == after                # atomicity: the +10 on product 1 was rolled back

        record_product_view(conn, 1, 7)
        # SET LOCAL did not leak past the transaction:
        print(conn.execute("SHOW synchronous_commit").fetchone())  # ('on',)


if __name__ == "__main__":
    main()
```

**Differences worth noticing:**

- **Error detail.** `pg` puts the constraint name on the error object (`err.constraint`) next to the SQLSTATE `code`. psycopg raises `errors.CheckViolation` and exposes server fields through `exc.diag` (`constraint_name`, `table_name`, `message_detail`). Match on the constraint name, not the message text, which is localised.
- **Sync vs async.** The Python script uses synchronous psycopg because it is a CLI-style job; inside an `async def` FastAPI route you would use `psycopg.AsyncConnection` instead, or the call would block the event loop. `pg` in Node has no synchronous API at all.
- **Where `SET LOCAL` works.** Both versions wrap the single `INSERT` in an explicit transaction only so that `SET LOCAL` has a transaction to attach to. A plain `SET synchronous_commit = off` would stick to the pooled connection and silently relax durability for the next request that borrows it.

---

## 5. Production Concerns

- **Choose durability per write, not per server.** Turning `synchronous_commit` off globally to win a benchmark exposes orders and payments to loss. Keep the server default `on` and relax it only in the code paths that write telemetry-like data (views, last-seen timestamps, analytics events). Do not use it for anything a user was told succeeded and would notice missing.
- **Commit latency is fsync latency.** Every durable commit waits for a WAL flush, so commit throughput on a single connection is bounded by the storage's flush time. Many concurrent commits share flushes (group commit), so throughput scales with concurrency better than with one connection in a loop. Batch small writes into fewer transactions where the business allows it.
- **Replication mode is a product decision.** Asynchronous replication can lose acknowledged commits on failover; synchronous replication adds a cross-host round trip to every commit and can stall writes if the standby is unreachable. Many teams run synchronous to a standby in the same region and asynchronous to a remote one. Monitor replication lag (`pg_stat_replication`) as "seconds of commits at risk".
- **Know your failover's promise.** A managed database's "Multi-AZ" may be synchronous or not. Find out whether a failover can drop acknowledged writes, and reconcile money-moving tables (payments versus the provider's records) after any failover.
- **Bloat from MVCC.** Frequent updates and rollbacks leave dead tuples; long-running transactions stop `VACUUM` from removing them. Track dead tuples (`pg_stat_user_tables.n_dead_tup`), the oldest open transaction, and transaction-ID age (`age(datfrozenxid)`) to stay far from wraparound.
- **Constraints cost little; missing constraints cost a lot.** A `CHECK` or `UNIQUE` is evaluated by the database on every write from every application version and every ad-hoc script. Prefer them to application checks for any rule that must never be broken, and add them with `NOT VALID` + `VALIDATE CONSTRAINT` on large tables ([Database Migrations](34-Database-Migrations.md)).

---

## 6. Common Mistakes

- **Saying "ACID consistency means all replicas agree"** — that is CAP's linearizability, a different property — ACID's C is "declared constraints hold at commit"; replica agreement depends on the replication mode.
- **Enforcing invariants only in application code** — two app instances, an old deploy or a manual `UPDATE` bypass the check — declare `CHECK`, `UNIQUE`, foreign keys or exclusion constraints and let the database reject bad writes.
- **Turning off `fsync` for speed** — an OS crash or power loss can corrupt the cluster beyond repair, not just lose recent work — use `synchronous_commit = off` (per transaction) if you need the latency; it loses recent commits but keeps the database consistent.
- **`SET synchronous_commit = off` on a pooled connection** — the setting stays on the session and relaxes durability for unrelated requests — use `SET LOCAL` inside the transaction.
- **Treating "the primary committed" as "the data is safe"** — asynchronous replicas can be promoted without the last commits — use synchronous replication for data you cannot lose, and reconcile after failovers.
- **Assuming ACID means "no concurrency bugs"** — the default isolation level is not serializable, so lost updates and write skew still happen — use atomic conditional updates, locks or `SERIALIZABLE` where the invariant needs it ([Isolation Levels](29-Isolation-Levels.md)).
- **Rolling back huge transactions on MySQL as a "quick undo"** — InnoDB must apply every undo record, which can take longer than the original work — batch large changes into smaller transactions.

---

## 7. Comparison Table

How much a crash can take away, per durability option in PostgreSQL:

| Option | `COMMIT` waits for | Lost on a database server crash | Lost when the primary fails over | Use for |
|---|---|---|---|---|
| `synchronous_commit = on`, async replicas (default) | Local WAL flush | Nothing | Commits not yet streamed | Most OLTP data |
| `on` + synchronous standby | Local flush + standby flush | Nothing | Nothing (if failover goes to the sync standby) | Payments, ledgers |
| `remote_apply` + synchronous standby | Local flush + standby replay | Nothing | Nothing; standby reads see the commit | Read-your-writes from standbys |
| `SET LOCAL synchronous_commit = off` | Nothing | The newest commits (≤ 3 × `wal_writer_delay`) | Same, plus unstreamed commits | Page views, last-seen, metrics |
| `UNLOGGED` table | Nothing (no WAL) | **The whole table** (emptied on restart) | The whole table (not replicated) | Caches and scratch data you can rebuild |
| `fsync = off` | Nothing | Possibly the whole cluster (corruption) | — | Throwaway test databases only |

---

## 8. Interview Questions

**[Junior] What does ACID stand for?**
Atomicity: all of a transaction's writes happen or none do. Consistency: the declared constraints hold when it commits. Isolation: concurrent transactions do not see each other's in-progress work, to the degree the isolation level promises. Durability: once commit returns, the data survives a crash. A, I and D are database mechanisms; C is mostly the application's rules, enforced through the constraints you declare.

**[Junior] A transaction updates two rows and the second update fails. What is in the table afterwards?**
Neither change. The failure aborts the transaction, and rollback discards the first update as well. In PostgreSQL the first update's new row version still exists physically, but its transaction ID is marked aborted in `pg_xact`, so no one can see it, and `VACUUM` removes it later.

**[Mid] How does PostgreSQL make a commit durable?**
Every change is first described in the write-ahead log. At `COMMIT`, PostgreSQL appends a commit record and flushes the WAL to disk before replying. The data pages themselves are written later by the checkpointer and background writer. After a crash, recovery replays the WAL from the last checkpoint, so every transaction with a commit record is restored, and every transaction without one is treated as aborted.

**[Mid] What is the difference between consistency in ACID and in CAP?**
ACID consistency means a transaction moves the database from one state that satisfies its constraints to another; it is about integrity rules on one database. CAP consistency means linearizability: in a replicated system, every read sees the most recent write. A single PostgreSQL server is ACID-consistent, but reading from its asynchronous replica can return stale data, which is not CAP-consistent.

**[Mid] Why is `ROLLBACK` cheap in PostgreSQL but potentially slow in MySQL?**
PostgreSQL writes new row versions next to the old ones and decides visibility from the commit log, so rollback just marks the transaction aborted; cleanup happens later in `VACUUM`. InnoDB updates rows in place and keeps the old values in the undo log, so rolling back means applying every undo record in reverse. A transaction that changed millions of rows can take a long time to roll back in InnoDB.

**[Senior] When would you set `synchronous_commit = off`, and what exactly can you lose?**
For high-volume, low-value writes where latency matters more than the last fraction of a second of data: page views, telemetry, "last seen" timestamps. I set it per transaction with `SET LOCAL`, never server-wide. On a crash, the most recent asynchronous commits — up to about three times `wal_writer_delay`, 600 ms by default — can be lost, but the database stays consistent: you lose whole transactions from the end of the log, never half of one. I would never use it for orders or payments, because the user has already been told they succeeded.

**[Senior] A customer was charged and saw "order confirmed", but after a database failover the order does not exist. Explain and fix.**
The primary acknowledged the commit after flushing its own WAL, but replication was asynchronous and the WAL had not reached the standby when the primary died. Failover promoted a standby that never saw the transaction. ACID durability held on the old primary's disk; it just was not the database anymore. Fixes: synchronous replication (`synchronous_standby_names` with `synchronous_commit = on` or `remote_apply`) for this data, accepting extra commit latency and a write stall if the standby is down; making failover prefer the synchronous standby; and a reconciliation job that compares payments with the provider's records after every failover.

**[Senior] Does running everything in transactions make an application safe under concurrency?**
No. Atomicity and durability protect against failures, not races. PostgreSQL's default Read Committed lets two transactions read the same stock value and both write a decremented absolute value (a lost update), and even Repeatable Read allows write skew. You still need atomic conditional `UPDATE`s, row locks, optimistic version checks, or `SERIALIZABLE` with retries, chosen per invariant.

---

## 9. Cheat Sheet

```text
A  all-or-nothing        PG: tuples stamped with xid; pg_xact says committed/aborted; ROLLBACK = mark aborted
C  declared constraints  NOT NULL, CHECK (never deferrable), UNIQUE/PK/FK/EXCLUDE (deferrable)
                         ≠ CAP C (linearizability across replicas)
I  as-if-alone           default is NOT serializable: PG Read Committed, MySQL Repeatable Read
D  survives crash        commit record in WAL, flushed before COMMIT returns (synchronous_commit = on)
WAL rule                 log record durable before the data page; recovery = replay from last checkpoint
MVCC                     UPDATE = old tuple xmax=X + new tuple xmin=X; VACUUM removes dead versions
Long tx                  blocks VACUUM everywhere → bloat; xids wrap at ~4 billion → freezing
synchronous_commit off   per tx via SET LOCAL; loses ≤ 3 × wal_writer_delay (600 ms default); no corruption
fsync off                corruption risk; never in production
UNLOGGED table           no WAL; emptied after crash; not replicated
Replication              async by default → acknowledged commits can vanish on failover
                         sync levels: remote_write < on (standby flush) < remote_apply (standby visible)
InnoDB                   redo log (durability) + undo log (rollback, MVCC); innodb_flush_log_at_trx_commit=1
```

---

## Related Topics

- [Transactions](27-Transactions.md) — using `BEGIN`/`COMMIT`, savepoints and retries from application code
- [Isolation Levels](29-Isolation-Levels.md) — the "I" in detail: anomalies and what each level prevents
- [CAP Theorem](02-CAP-Theorem.md) — the other, unrelated meaning of "consistency"
- [Replication](../Module-07-Advanced-Backend-and-System-Design/18-Replication.md) — synchronous vs asynchronous replicas and failover data loss
- [File Systems Basics](../Module-04-Operating-Systems/30-File-Systems-Basics.md) — page cache and `fsync`, which WAL durability depends on

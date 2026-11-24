# Isolation Levels

> **Module 03 · Databases** · Prerequisites: [ACID](28-ACID.md) · Next: [Database Locks](30-Database-Locks.md)

---

## ⏱ If You Only Have 2 Minutes

- An **isolation level** decides which effects of *concurrent* transactions your transaction can observe. Weaker levels allow more **anomalies** but block or abort less.
- The SQL standard defines four levels by three phenomena: **dirty read**, **non-repeatable read**, **phantom read**. Real systems also have to deal with **lost update**, **read skew** and **write skew**, which the standard's table does not name.
- **PostgreSQL:** Read Uncommitted behaves exactly like Read Committed (no dirty reads ever). **Read Committed is the default**: each *statement* gets a fresh snapshot.
- **PostgreSQL Repeatable Read is snapshot isolation**: one snapshot for the whole transaction, so no non-repeatable reads and no phantoms — but **write skew is possible**, and updating a row another transaction changed and committed fails with `40001 could not serialize access due to concurrent update`.
- **PostgreSQL Serializable** uses **Serializable Snapshot Isolation (SSI)**: it tracks read/write dependencies and aborts one transaction with `40001` when the result could differ from some serial order. It does not block more than Repeatable Read, but **you must retry**.
- **MySQL InnoDB defaults to REPEATABLE READ**: plain `SELECT`s read a snapshot, while locking reads (`FOR UPDATE`, `FOR SHARE`), `UPDATE` and `DELETE` read the **latest** committed rows and take **next-key (record + gap) locks**. It does not abort on concurrent updates, so read-then-write lost updates go undetected.
- Choose the level **per transaction** (`BEGIN ISOLATION LEVEL SERIALIZABLE`), not per database: Read Committed plus atomic `UPDATE`s for most writes, Repeatable Read for consistent multi-query reads, Serializable for invariants that span several rows.

---

## 1. What It Is and Why It Exists

The "I" in [ACID](28-ACID.md) ideally means **serializability**: running transactions concurrently gives the same result as running them one after another in *some* order. Full serializability costs throughput — either through locks that make transactions wait, or through aborts that make them retry. So databases offer **isolation levels**: named trade-offs where you accept some anomalies in exchange for more concurrency.

**Analogy:** reading a shared whiteboard while others edit it.

- *Read Committed*: every time you glance up, you see the board as it is now (but only finished edits). Two glances can disagree.
- *Repeatable Read (snapshot)*: you take a photo when you start and read only from the photo. Consistent — but you may make a decision based on the photo that someone else's change has made wrong.
- *Serializable*: a referee watches who read what and who wrote what. If your decision and someone else's could not both have been made in any one-at-a-time order, the referee cancels one of you and says "try again".

**What breaks at the wrong level.** Two concrete examples from the sample schema:

- Two checkout requests read `inventory.available = 1` for the same product, both decide "in stock", and both write `available = 0`. Two units are sold; one exists. (Lost update, allowed by Read Committed.)
- A support dashboard reads order 42 as `pending`, then reads its payment as `captured`, because the payment was committed between the two queries. It flags a non-existent problem. (Read skew, allowed by Read Committed.)

Isolation levels let you pick, per transaction, which of these the database prevents and which your code must handle.

---

## 2. How It Works

PostgreSQL builds every level on [MVCC](28-ACID.md): each row version carries the ID of the transaction that created it (`xmin`) and the one that deleted it (`xmax`), and a **snapshot** decides which versions a query can see. The levels differ in two things: **when** the snapshot is taken, and **what happens when you try to write a row someone else changed**.

### When the snapshot is taken

| Level | Snapshot | Effect |
|---|---|---|
| Read Committed | New snapshot at the start of **each statement** | Each statement sees everything committed before it began |
| Repeatable Read | One snapshot at the **first statement** of the transaction (not at `BEGIN`) | Every statement sees the same data; later commits are invisible |
| Serializable | Same as Repeatable Read, plus dependency tracking | Same view, and conflicts that break serializability cause an abort |

Because of this, the isolation level must be set before the first query: `BEGIN ISOLATION LEVEL …`, or `SET TRANSACTION ISOLATION LEVEL …` as the first statement after `BEGIN`.

### What happens on a write conflict

Suppose transaction B runs `UPDATE` (or `DELETE`, or `SELECT … FOR UPDATE`) on a row that transaction A has already updated.

```mermaid
flowchart TD
    W["B wants to update a row that A changed"] --> Q{"Has A finished?"}
    Q -->|"No"| Wait["B waits for A's row lock"]
    Wait --> Q
    Q -->|"A rolled back"| Go["B updates the original row"]
    Q -->|"A committed"| L{"B's isolation level"}
    L -->|"Read Committed"| Re["Re-check B's WHERE clause on A's new version, then update it if it still matches or skip it if not"]
    L -->|"Repeatable Read or Serializable"| Err["ERROR 40001: could not serialize access due to concurrent update"]
```

The Read Committed rule is why `UPDATE inventory SET available = available - 1 WHERE product_id = 1 AND available >= 1` is safe at the default level: after waiting, the condition is evaluated against the **latest** row, so two buyers cannot both take the last unit. It is also why a value you `SELECT`ed earlier and then write back as a constant is *not* safe: the database re-checks your `WHERE`, not the value you computed in application code.

At Repeatable Read and Serializable, PostgreSQL uses **first-updater-wins**: the transaction that tries to modify a row already changed by a concurrently committed transaction is aborted, because its snapshot is stale for that row.

### How Serializable (SSI) adds the last guarantee

Snapshot isolation alone still allows **write skew** (section 3). PostgreSQL's Serializable level, added in 9.1, closes the gap with **Serializable Snapshot Isolation**:

1. Every read records a **predicate lock** (`SIReadLock` in `pg_locks`). These locks never block anyone; they only record "this transaction read this row, page or relation".
2. When a transaction writes something another concurrent transaction read, PostgreSQL records a **read-write dependency** ("rw-conflict") between them.
3. If a transaction has an incoming and an outgoing rw-conflict among concurrent transactions — a "dangerous structure" that can produce a cycle — PostgreSQL aborts one of the transactions with `40001`. The error can come from any statement, including `COMMIT`.

SSI is conservative: it can abort transactions that would actually have been fine (false positives), especially when predicate locks are coarse. It never makes anyone wait longer than Repeatable Read would.

---

## 3. Key Concepts

### The six anomalies, as two-session timelines

Each timeline uses the sample schema. Time runs downwards; "→" shows a result.

**Dirty read** — reading another transaction's *uncommitted* write.

| # | Session A | Session B |
|---|---|---|
| 1 | `BEGIN; UPDATE inventory SET available = 0 WHERE product_id = 1;` | |
| 2 | | `SELECT available FROM inventory WHERE product_id = 1;` → a dirty read would return `0`; PostgreSQL returns `42` at every level |
| 3 | `ROLLBACK;` | B would have acted on a value that never existed |

**Non-repeatable read** — the same row, read twice in one transaction, has changed.

| # | Session A | Session B |
|---|---|---|
| 1 | | `BEGIN; SELECT price_cents FROM products WHERE id = 1;` → `1999` |
| 2 | `UPDATE products SET price_cents = 2499 WHERE id = 1;` (autocommits) | |
| 3 | | Same `SELECT` → **`2499`** in Read Committed; `1999` in Repeatable Read |

**Phantom read** — a repeated *range* query returns a different set of rows.

| # | Session A | Session B |
|---|---|---|
| 1 | | `BEGIN; SELECT count(*) FROM orders WHERE customer_id = 7 AND status = 'pending';` → `2` |
| 2 | `INSERT INTO orders (customer_id, status, total_cents) VALUES (7, 'pending', 500);` | |
| 3 | | Same query → **`3`** in Read Committed; `2` in PostgreSQL Repeatable Read |

**Lost update** — two read-modify-write cycles; one overwrites the other.

| # | Session A | Session B |
|---|---|---|
| 1 | `BEGIN; SELECT available FROM inventory WHERE product_id = 1;` → `42` | |
| 2 | | `BEGIN; SELECT available FROM inventory WHERE product_id = 1;` → `42` |
| 3 | `UPDATE inventory SET available = 41 WHERE product_id = 1; COMMIT;` | |
| 4 | | `UPDATE inventory SET available = 41 WHERE product_id = 1;` → Read Committed: succeeds, final value `41`, **one sale lost**. Repeatable Read: **`40001`** |

The fixes do not require a stronger level: write `available = available - 1` (atomic), lock the row first with `SELECT … FOR UPDATE` ([Database Locks](30-Database-Locks.md)), or use a version column ([Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md)).

**Read skew** — two *different* rows read at different moments, giving a combination that never existed.

| # | Session A | Session B |
|---|---|---|
| 1 | | `BEGIN; SELECT status FROM orders WHERE id = 42;` → `pending` |
| 2 | `BEGIN; UPDATE orders SET status = 'paid' WHERE id = 42;` `INSERT INTO payments (order_id, amount_cents, status) VALUES (42, 3998, 'captured'); COMMIT;` | |
| 3 | | `SELECT status FROM payments WHERE order_id = 42;` → Read Committed: **`captured`** — a pending order with a captured payment. Repeatable Read: no row, consistent with `pending` |

**Write skew** — two transactions read the same rows, each writes a *different* row based on what it read, and together they break an invariant neither broke alone. Classic case: a hospital requires at least one doctor on call per shift (table in section 4).

| # | Session A (Alice) | Session B (Bob) |
|---|---|---|
| 1 | `BEGIN ISOLATION LEVEL REPEATABLE READ;` `SELECT count(*) FROM on_call WHERE shift_id = 1 AND on_call;` → `2` | |
| 2 | | Same → `2` |
| 3 | `UPDATE on_call SET on_call = false WHERE shift_id = 1 AND doctor = 'alice';` | |
| 4 | | `UPDATE on_call SET on_call = false WHERE shift_id = 1 AND doctor = 'bob';` — a different row, so no write conflict |
| 5 | `COMMIT;` ✔ | `COMMIT;` ✔ → **nobody is on call** |

Under `SERIALIZABLE`, step 4 or B's `COMMIT` fails with `40001`; when B retries, it reads `1` and refuses.

### The SQL standard table versus PostgreSQL

The SQL standard ("may occur" = allowed, not required):

| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | Possible | Possible | Possible |
| Read Committed | — | Possible | Possible |
| Repeatable Read | — | — | Possible |
| Serializable | — | — | — |

What PostgreSQL actually does (from its "Transaction Isolation" documentation, plus the anomalies the standard does not name):

| Level | Dirty read | Non-repeatable | Phantom | Lost update (read-then-write) | Read skew | Write skew | Can fail with `40001` |
|---|---|---|---|---|---|---|---|
| Read Uncommitted (= Read Committed) | No | Yes | Yes | Yes | Yes | Yes | No |
| **Read Committed** (default) | No | Yes | Yes | Yes | Yes | Yes | No |
| Repeatable Read | No | No | **No** | No — aborts with `40001` | No | **Yes** | Yes, on write conflicts |
| Serializable | No | No | No | No | No | No | Yes, on any dangerous dependency |

The standard defines levels by which phenomena are *forbidden*, so a database may be stricter. PostgreSQL's Repeatable Read is stricter than required (no phantoms) yet still not serializable (write skew). Berenson et al.'s 1995 paper "A Critique of ANSI SQL Isolation Levels" showed exactly this gap: snapshot isolation passes the standard's phenomenon tests for Repeatable Read but is not serializable.

### MySQL InnoDB difference

InnoDB's default is **REPEATABLE READ**, and it means something different from PostgreSQL's:

- **Consistent non-locking reads.** A plain `SELECT` reads from a snapshot taken at the transaction's **first read** (or at `START TRANSACTION WITH CONSISTENT SNAPSHOT`). Old versions come from the undo log.
- **Locking reads read the latest data.** `SELECT … FOR UPDATE`, `SELECT … FOR SHARE`, `UPDATE` and `DELETE` act on the **latest committed** row versions, not the snapshot, and lock what they scan.
- **Next-key locks.** In REPEATABLE READ, those locking statements lock each index record they scan **plus the gap before it**. Another transaction cannot insert into a locked gap, which prevents phantoms for locking reads. Gap locks are also a common source of deadlocks on concurrent inserts ([Deadlocks](31-Deadlocks.md)).
- **No first-updater-wins.** If two transactions read `available = 42` from their snapshots and both write `41`, InnoDB makes the second wait for the first's row lock, then applies its update to the latest row. No error: **the lost update is silent**. Use atomic `UPDATE`s or `FOR UPDATE`.
- **Mixed views.** Within one transaction, a plain `SELECT` (snapshot) and an `UPDATE` (latest data) can see different rows — an `UPDATE` can modify rows the transaction's snapshot `SELECT` could not see, after which they become visible to it.
- **SERIALIZABLE** in InnoDB turns plain `SELECT`s into `SELECT … FOR SHARE` when autocommit is off. Conflicts show up as lock waits and deadlocks (error 1213, SQLSTATE `40001`) instead of SSI aborts; the write-skew doctors example ends in a deadlock with one victim to retry.
- **READ UNCOMMITTED** in InnoDB really does allow dirty reads, unlike PostgreSQL. **READ COMMITTED** takes a fresh snapshot per read and uses gap locks only for foreign-key and duplicate-key checks.

### Serializable in practice

Serializable is the only level where "each transaction is correct alone" implies "the system is correct". The price is retries and some overhead. The PostgreSQL docs' advice, in short:

- **Retry the whole transaction on `40001`** (and `40P01`), with a bound and jitter. See the helper in [Transactions](27-Transactions.md).
- **Do not trust data read in a Serializable transaction until it commits.** A transaction that read, decided "no", and returned without committing never had its reads validated. Commit even read-only work, or use `SERIALIZABLE READ ONLY DEFERRABLE`, which waits for a safe snapshot and then can never fail with a serialization error.
- **All participants must be Serializable.** SSI only tracks transactions running at Serializable; a Read Committed writer can still cause the anomaly.
- **Keep transactions short, and declare `READ ONLY` where possible.** Fewer concurrent dependencies mean fewer false-positive aborts.
- **Index the predicates you read.** A sequential scan takes a predicate lock on the whole table, so any write to that table becomes a conflict. Many fine-grained locks may also be promoted to page or relation locks (tunable with `max_pred_locks_per_transaction`), which raises the abort rate.

### Choosing a level per transaction

| Situation | Level | Why |
|---|---|---|
| Typical writes expressed as atomic `UPDATE … SET x = x - $1 WHERE … AND x >= $1`, plus constraints | Read Committed | The `WHERE` is re-checked on the latest row; no retries needed |
| Read a row, compute in code, write it back | Read Committed + `FOR UPDATE` or a version column; or Repeatable Read + retry | Prevents the lost update |
| Multi-query report or export that must be self-consistent | Repeatable Read, `READ ONLY` | One snapshot; read-only transactions never hit write conflicts |
| Invariant across several rows checked by reading (on-call rota, no double booking, budget limits) | Serializable + retry | Only level that prevents write skew in general |
| Long read-only job in a Serializable workload | `SERIALIZABLE READ ONLY DEFERRABLE` | May wait briefly at start, then never aborts |

---

## 4. Code Examples

Scenario: the on-call rota. A doctor may go off call only if at least one other doctor stays on call for the shift. At Read Committed or Repeatable Read, two doctors clicking "go off call" at the same moment can both succeed. The fix is to run the check-and-update at `SERIALIZABLE` and retry on `40001`.

### SQL

```sql
CREATE TABLE on_call (
  shift_id  bigint  NOT NULL,
  doctor    text    NOT NULL,
  on_call   boolean NOT NULL DEFAULT true,
  PRIMARY KEY (shift_id, doctor)          -- index on shift_id: keeps SSI's predicate locks fine-grained
);
INSERT INTO on_call (shift_id, doctor) VALUES (1, 'alice'), (1, 'bob');

-- Run in two sessions, interleaved line by line. Illustrative output.
-- Session A                                              -- Session B
BEGIN ISOLATION LEVEL SERIALIZABLE;                       BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT count(*) FROM on_call
 WHERE shift_id = 1 AND on_call;          -- 2
                                                          SELECT count(*) FROM on_call
                                                           WHERE shift_id = 1 AND on_call;   -- 2
UPDATE on_call SET on_call = false
 WHERE shift_id = 1 AND doctor = 'alice';
                                                          UPDATE on_call SET on_call = false
                                                           WHERE shift_id = 1 AND doctor = 'bob';
COMMIT;                                   -- COMMIT
                                                          COMMIT;
-- ERROR:  could not serialize access due to read/write dependencies among transactions
-- DETAIL:  Reason code: Canceled on identification as a pivot, during commit attempt.
-- HINT:  The transaction might succeed if retried.

-- With REPEATABLE READ instead, both COMMITs succeed and this returns 0 rows:
SELECT doctor FROM on_call WHERE shift_id = 1 AND on_call;
```

### Node.js / TypeScript

```ts
// npm i pg && npm i -D @types/pg   — Node.js 22+, TypeScript 5, ESM
import pg from "pg";
import { setTimeout as sleep } from "node:timers/promises";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 4 });
const sqlState = (err: unknown) =>
  typeof err === "object" && err !== null && "code" in err ? String(err.code) : "";

type Outcome = "off_call" | "last_doctor_on_call";

export async function goOffCall(shiftId: number, doctor: string, raceDelayMs = 0): Promise<Outcome> {
  const maxAttempts = 4;
  for (let attempt = 1; ; attempt++) {
    const client = await pool.connect();
    try {
      await client.query("BEGIN ISOLATION LEVEL SERIALIZABLE");
      const { rows } = await client.query<{ n: number }>(
        "SELECT count(*)::int AS n FROM on_call WHERE shift_id = $1 AND on_call", [shiftId]);
      if (raceDelayMs) await sleep(raceDelayMs); // demo only: let both sessions read before either writes
      if (rows[0]!.n < 2) {
        // COMMIT, not ROLLBACK: under SSI a read is only trustworthy once its transaction commits.
        await client.query("COMMIT");
        return "last_doctor_on_call";
      }
      await client.query("UPDATE on_call SET on_call = false WHERE shift_id = $1 AND doctor = $2",
        [shiftId, doctor]);
      await client.query("COMMIT"); // SSI often reports the conflict here, not at the UPDATE
      return "off_call";
    } catch (err) {
      await client.query("ROLLBACK").catch(() => undefined);
      const code = sqlState(err);
      if ((code !== "40001" && code !== "40P01") || attempt >= maxAttempts) throw err;
      console.warn(`${doctor}: ${code} on attempt ${attempt}, retrying`);
    } finally {
      client.release();
    }
    await sleep(Math.random() * 20 * 2 ** attempt); // jitter so the retry does not collide again
  }
}

// Demo: reset the rota, then race Alice and Bob.
await pool.query("UPDATE on_call SET on_call = true WHERE shift_id = 1");
const results = await Promise.all([goOffCall(1, "alice", 100), goOffCall(1, "bob", 100)]);
console.log(results); // e.g. [ 'off_call', 'last_doctor_on_call' ] — one retry was logged
const { rows } = await pool.query("SELECT doctor FROM on_call WHERE shift_id = 1 AND on_call");
console.log(rows);    // exactly one doctor still on call
await pool.end();
```

### Python

```python
# pip install "psycopg[binary,pool]"   — Python 3.12+, psycopg 3.2+
import asyncio
import random
from typing import Literal

from psycopg import errors
from psycopg_pool import AsyncConnectionPool

DSN = "postgresql://app_rw:dev@localhost:5432/hospital"
Outcome = Literal["off_call", "last_doctor_on_call"]
MAX_ATTEMPTS = 4


async def go_off_call(pool: AsyncConnectionPool, shift_id: int, doctor: str,
                      race_delay: float = 0.0) -> Outcome:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            async with pool.connection() as conn:
                async with conn.transaction():  # leaving the block normally = COMMIT
                    await conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    cur = await conn.execute(
                        "SELECT count(*) FROM on_call WHERE shift_id = %s AND on_call", (shift_id,))
                    row = await cur.fetchone()
                    assert row is not None
                    if race_delay:
                        await asyncio.sleep(race_delay)  # demo only: widen the race window
                    if row[0] < 2:
                        # Returning still COMMITs, so SSI validates the read we based "no" on.
                        return "last_doctor_on_call"
                    await conn.execute(
                        "UPDATE on_call SET on_call = false WHERE shift_id = %s AND doctor = %s",
                        (shift_id, doctor),
                    )
                    return "off_call"  # a 40001 raised by COMMIT replaces this return
        except (errors.SerializationFailure, errors.DeadlockDetected) as exc:
            if attempt == MAX_ATTEMPTS:
                raise
            print(f"{doctor}: {exc.sqlstate} on attempt {attempt}, retrying")
        await asyncio.sleep(random.uniform(0, 0.02 * 2**attempt))
    raise AssertionError("unreachable")


async def main() -> None:
    async with AsyncConnectionPool(DSN, open=False, kwargs={"autocommit": True}) as pool:
        async with pool.connection() as conn:
            await conn.execute("UPDATE on_call SET on_call = true WHERE shift_id = 1")
        results = await asyncio.gather(
            go_off_call(pool, 1, "alice", 0.1),
            go_off_call(pool, 1, "bob", 0.1),
        )
        print(results)  # e.g. ['off_call', 'last_doctor_on_call']
        async with pool.connection() as conn:
            cur = await conn.execute("SELECT doctor FROM on_call WHERE shift_id = 1 AND on_call")
            print(await cur.fetchall())  # exactly one row


if __name__ == "__main__":
    asyncio.run(main())
```

**Differences worth noticing:**

- **Setting the level.** In Node the level goes into the `BEGIN` statement on the checked-out client. psycopg's `transaction()` issues a plain `BEGIN`, so the level is set with `SET TRANSACTION ISOLATION LEVEL` as the first statement. psycopg also has a connection-level `isolation_level` attribute, but on a pooled connection it would outlive this transaction and change the next borrower's level.
- **Where the error appears.** In both languages `40001` may surface from the `UPDATE` or from `COMMIT`. In Python, `COMMIT` runs inside `transaction().__aexit__`, so an exception there replaces the `return` value and lands in the `except` clause; in TypeScript it is just another rejected `await`.
- **Concurrency model.** `Promise.all` and `asyncio.gather` both run the two calls concurrently on one thread, each on its own pooled connection. That is the requirement: two transactions need two connections, whatever the runtime.

---

## 5. Production Concerns

- **Retry budget and observability.** At Serializable, `40001` is normal traffic. Count aborts per transaction type and alert on the rate, not on individual errors. If one transaction type aborts often, look for reads without a supporting index (relation-level predicate locks) or a transaction that reads far more than it needs.
- **Retries multiply load.** Each abort repeats all of the transaction's work. Under heavy contention on one hot row, Serializable can spend more time retrying than working; a row lock (`FOR UPDATE`, [Database Locks](30-Database-Locks.md)) that queues writers can then be the better tool.
- **Connection count matters more at Serializable.** More concurrent transactions mean more possible dependencies and more false-positive aborts. A modest pool size with a queue in front of it often gives higher throughput than many connections.
- **Mixed levels give no guarantee.** If one service writes `on_call` at Read Committed while another runs the check at Serializable, the write skew can still happen. Set `default_transaction_isolation = 'serializable'` for the database role that owns those tables, or make every write path use the same helper.
- **Long Repeatable Read snapshots hold back cleanup.** A two-hour export at Repeatable Read keeps one snapshot for two hours, so `VACUUM` cannot remove anything that became dead after it started. Run big exports on a replica or in chunks, and watch the oldest `backend_xmin` in `pg_stat_activity`.

---

## 6. Common Mistakes

- **Assuming the default is serializable** — PostgreSQL uses Read Committed and MySQL Repeatable Read, so lost updates and write skew happen silently — know your level and add an atomic update, a lock or Serializable for invariants that need it.
- **Raising the level without adding retries** — Repeatable Read and Serializable turn races into `40001` errors, which become `500`s — wrap those transactions in a bounded retry of the whole transaction.
- **Thinking Repeatable Read prevents write skew** — snapshot isolation lets two transactions read the same rows and update different ones — use Serializable, or lock the rows read with `SELECT … FOR UPDATE`.
- **Read-then-write with a computed constant** — `SET available = 41` after reading `42` loses concurrent updates at Read Committed, and does so silently in MySQL even at Repeatable Read — write `available = available - 1` with a guard in the `WHERE`.
- **Expecting MySQL's REPEATABLE READ to behave like PostgreSQL's** — InnoDB's locking reads see the latest data and never abort on concurrent updates — test concurrency on the database you deploy.
- **Acting on a Serializable read without committing** — the "no" decision was never validated and may be based on an impossible state — commit read-only work too, or use `READ ONLY DEFERRABLE`.
- **Setting the level after the first query** — PostgreSQL rejects `SET TRANSACTION ISOLATION LEVEL` once the transaction has run a query — put it in `BEGIN` or make it the first statement.

---

## 7. Comparison Table

| | PostgreSQL Read Committed | PostgreSQL Repeatable Read | PostgreSQL Serializable | MySQL InnoDB Repeatable Read |
|---|---|---|---|---|
| Snapshot | Per statement | Per transaction (first statement) | Per transaction | Per transaction for plain `SELECT`; latest data for locking reads and writes |
| Phantoms | Yes | No | No | No for snapshot reads; locking reads use gap locks |
| Lost update (read-then-write) | Silent | Aborts with `40001` | Aborts with `40001` | Silent |
| Write skew | Yes | Yes | No | Yes |
| How conflicts surface | Waits, then re-checks `WHERE` | Waits, then `40001` | Waits on row locks; `40001` on dependency cycles | Waits on row and gap locks; deadlock errors |
| Needs retry logic | Only for deadlocks | Yes | Yes | For deadlocks |
| Default? | Yes | No | No | Yes |

---

## 8. Interview Questions

**[Junior] What is a dirty read, and can it happen in PostgreSQL?**
A dirty read is reading another transaction's uncommitted change, which may later be rolled back. PostgreSQL never allows it: even if you request Read Uncommitted, you get Read Committed behaviour. MySQL InnoDB does allow dirty reads at READ UNCOMMITTED.

**[Junior] What are the default isolation levels in PostgreSQL and MySQL?**
PostgreSQL defaults to Read Committed, where each statement sees data committed before that statement started. MySQL InnoDB defaults to Repeatable Read, where plain reads use one snapshot for the transaction while locking reads and writes act on the latest data. You can change it per transaction with `BEGIN ISOLATION LEVEL …` or `SET TRANSACTION ISOLATION LEVEL …`.

**[Mid] What is the difference between a non-repeatable read and a phantom read?**
A non-repeatable read is the *same row* returning different values when read twice, because another transaction updated it and committed. A phantom is a *range query* returning a different set of rows, because another transaction inserted or deleted matching rows. In PostgreSQL both are possible at Read Committed and neither at Repeatable Read, because the transaction keeps one snapshot.

**[Mid] Two requests decrement stock at Read Committed. When is that safe and when is it not?**
It is safe as a single statement: `UPDATE inventory SET available = available - 1 WHERE product_id = $1 AND available >= 1`. The second updater waits for the first, then re-evaluates its `WHERE` against the new row, so the stock cannot go below zero or lose a decrement. It is not safe if the code reads `available`, computes the new value in the application, and writes it back as a constant — that is a lost update. Fix it with the atomic statement, `SELECT … FOR UPDATE`, or a version column.

**[Mid] How does PostgreSQL's Repeatable Read differ from MySQL's?**
PostgreSQL's is snapshot isolation: every statement, including `UPDATE`, works against one snapshot, and modifying a row changed by a concurrent committed transaction fails with `40001`. In InnoDB, only plain `SELECT`s use the snapshot; locking reads, `UPDATE` and `DELETE` see the latest committed rows and take next-key locks. So InnoDB never aborts on a concurrent update — it waits and applies the change, which means read-then-write lost updates are silent.

**[Senior] Explain write skew and how you would prevent it.**
Two transactions read an overlapping set of rows, each checks an invariant, and each updates a *different* row — for example, two on-call doctors each see two doctors on call and each go off call, leaving none. Snapshot isolation does not catch it because there is no write-write conflict. In PostgreSQL I would run the transaction at Serializable and retry on `40001`; SSI detects the read-write dependency cycle and aborts one. Alternatives: lock the rows read with `SELECT … FOR UPDATE` at Read Committed, or, when the check is about rows that do not exist yet (double booking), use a constraint such as an exclusion constraint or a unique index that makes the conflict a write-write conflict.

**[Senior] Your team wants to switch the whole application to Serializable. What changes and what do you watch?**
Every write path needs a retry wrapper for `40001` that re-runs the whole transaction, and transactions must be free of external side effects so retries are safe. Read-only paths should be declared `READ ONLY`, and long reports `READ ONLY DEFERRABLE`. Performance depends on indexes — sequential scans create table-level predicate locks and drive up false-positive aborts — and on keeping transactions short and concurrency moderate. I would roll out per transaction type, starting with the invariants that need it, and track abort rates and retry latency per endpoint.

**[Senior] Why is the SQL standard's isolation table misleading?**
It defines levels by forbidding three phenomena — dirty read, non-repeatable read, phantom — written with lock-based implementations in mind. Berenson et al. (1995) showed that snapshot isolation avoids all three as the standard describes them, yet is not serializable, because it allows write skew. The standard also does not name lost update or read skew. So "Repeatable Read" means different things in PostgreSQL and MySQL, and you have to reason about the actual anomalies rather than level names.

---

## 9. Cheat Sheet

```text
Standard        RU: dirty+nonrepeatable+phantom | RC: nonrepeatable+phantom | RR: phantom | SER: none
PG levels       RU = RC (no dirty reads) | RC default: snapshot per statement
                RR = snapshot isolation: snapshot at first statement; no phantoms; write skew possible
                SER = SSI: predicate (SIRead) locks + rw-dependency tracking → 40001, retry
PG write rule   RC: wait, re-check WHERE on newest row | RR/SER: concurrent committed update → 40001
Lost update     RC: silent for read-then-write constants; safe for SET x = x - 1 WHERE x >= 1
Write skew      read same rows, write different rows → only SERIALIZABLE (or FOR UPDATE) prevents it
Read skew       RC sees order 'pending' + payment 'captured'; RR's single snapshot prevents it
Set level       BEGIN ISOLATION LEVEL SERIALIZABLE; or SET TRANSACTION ... as first statement
Serializable    retry whole tx on 40001; commit read-only tx too; READ ONLY DEFERRABLE for reports
                index predicates (seq scan = table-level predicate lock); all writers must be SERIALIZABLE
MySQL InnoDB    default RR; plain SELECT = snapshot; FOR UPDATE/FOR SHARE/UPDATE = latest + next-key locks
                no abort on concurrent update → lost updates silent; SERIALIZABLE: SELECT → FOR SHARE
                RU allows dirty reads; RC = fresh snapshot per read, almost no gap locks
```

---

## Related Topics

- [ACID](28-ACID.md) — MVCC tuple versions and snapshots that every isolation level is built on
- [Transactions](27-Transactions.md) — the retry helper that Repeatable Read and Serializable require
- [Database Locks](30-Database-Locks.md) — `FOR UPDATE` and other explicit locks as an alternative to stronger levels
- [Optimistic vs Pessimistic Locking](32-Optimistic-vs-Pessimistic-Locking.md) — preventing lost updates with version columns or row locks
- [Deadlocks](31-Deadlocks.md) — `40P01`, and why gap locks in InnoDB cause them
- [Race Conditions](../Module-04-Operating-Systems/13-Race-Conditions.md) — the same check-then-act problem in application memory

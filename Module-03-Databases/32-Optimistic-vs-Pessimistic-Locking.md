# Optimistic vs Pessimistic Locking

> **Module 03 · Databases** · Prerequisites: [Database Locks](30-Database-Locks.md) · Next: [ORM Fundamentals](33-ORM-Fundamentals.md)

---

## ⏱ If You Only Have 2 Minutes

- **Lost update:** two transactions read the same value, compute a new one in application code, and write it back. The second write silently erases the first. PostgreSQL's default `READ COMMITTED` does **not** prevent it, and a `CHECK` constraint cannot catch it, because each write is valid on its own.
- **Pessimistic locking:** `BEGIN; SELECT … FOR UPDATE;` decide; `UPDATE`; `COMMIT`. Other writers wait at the `SELECT`. Best when conflicts are frequent and the critical section is short.
- **Optimistic locking:** read the row with its `version`, then `UPDATE … SET …, version = version + 1 WHERE id = $1 AND version = $2`. **0 rows updated = someone else won** → re-read and retry, or return 409/412. No lock is held between the read and the write, so it can span an HTTP round trip or a user editing a form.
- Often the best answer is neither: one atomic statement, `UPDATE inventory SET available = available - $2 WHERE product_id = $1 AND available >= $2`. The check and the write cannot be separated, so there is nothing to lock and nothing to retry.
- Choose by **contention** and **critical-section length**: rare conflicts or long think time → optimistic; a hot row with a short critical section → pessimistic; under heavy contention, optimistic turns into a retry storm.
- In Postgres, `REPEATABLE READ` also detects the lost update: the second writer fails with `40001` and must retry. MySQL InnoDB's `REPEATABLE READ` does not.
- SQLAlchemy has `version_id_col` (raises `StaleDataError`). Prisma and Drizzle have no declarative version column; you write the conditional update and check the affected-row count.
- `updated_at` makes a weak version (microseconds vs JavaScript milliseconds, `now()` is transaction start time). `xmin` works in Postgres but is a 32-bit system detail that does not survive dump and restore.

---

## 1. What It Is and Why It Exists

Both techniques protect a **read-modify-write** sequence: read a row, make a decision in code, write the result. Between the read and the write, another transaction can change the row. If nothing stops it, one of the two changes is lost.

- **Pessimistic locking** assumes a conflict is likely. It locks the row at read time, so nobody else can change it until you commit.
- **Optimistic locking** assumes a conflict is unlikely. It takes no lock while you think. At write time, it checks that the row is still the version you read; if not, your write is rejected and you start again.

**Analogy:** editing a shared wiki page. The pessimistic wiki makes you "check out" the page; everyone else sees "locked by Sara" until she saves. The optimistic wiki lets everyone edit. When you press Save, it checks that the page has not changed since you opened it; if it has, you get an "edit conflict" screen and must merge your changes into the new text.

### The problem: a lost update

Product 7 has `available = 1`. Two customers buy it at the same moment, and the service does this:

| Time | Request A | Request B | `available` in DB |
|---|---|---|---|
| t1 | `SELECT available …` → 1 | | 1 |
| t2 | | `SELECT available …` → 1 | 1 |
| t3 | `1 >= 1`, write `available = 0` | | 0 |
| t4 | | `1 >= 1`, write `available = 0` | 0 |

Both requests succeed, both customers are charged, and the warehouse has one item. The final value `0` is valid, so `CHECK (available >= 0)` is happy. Nothing errors. This is why lost updates are dangerous: they produce plausible data. Every money balance, seat count, quota and counter that is updated through "read, compute in code, write" has this bug until you add one of the defences in this chapter.

---

## 2. How It Works

### Pessimistic: lock at read time

```sql
BEGIN;
SELECT available FROM inventory WHERE product_id = 7 FOR UPDATE;  -- B blocks here until A commits
-- application checks available >= qty
UPDATE inventory SET available = 0, version = version + 1 WHERE product_id = 7;
COMMIT;
```

`FOR UPDATE` takes a row lock that conflicts with other `FOR UPDATE` requests and with `UPDATE`/`DELETE` (see [Database Locks](30-Database-Locks.md)). Request B's `SELECT … FOR UPDATE` waits. When A commits, B's statement returns the **new** row (`available = 0`) — under `READ COMMITTED`, a locking read that had to wait returns the latest committed version. B sees 0 and correctly refuses the sale. Plain `SELECT`s from other requests are not blocked at all.

### Optimistic: check at write time

```mermaid
sequenceDiagram
    participant A as Request A
    participant DB as PostgreSQL
    participant B as Request B
    A->>DB: SELECT available, version (1, v7)
    B->>DB: SELECT available, version (1, v7)
    A->>DB: UPDATE ... SET available = 0, version = 8 WHERE version = 7
    DB-->>A: UPDATE 1 (A wins)
    B->>DB: UPDATE ... SET available = 0, version = 8 WHERE version = 7
    DB-->>B: UPDATE 0 (row is now v8, no match)
    B->>DB: re-read (0, v8), not enough stock
    B-->>B: return out_of_stock, or 409 to the client
```

Why it is safe under `READ COMMITTED`: if A's `UPDATE` is still uncommitted when B's arrives, B's `UPDATE` waits for A's row lock. When A commits, Postgres re-checks B's `WHERE` against the newest row version. The version is now 8, so the row no longer matches and B updates 0 rows. If A has already committed, B sees version 8 straight away. Either way, exactly one of them wins.

Note what "optimistic" really means. The database still takes a row lock for the instant of the `UPDATE`. What optimistic locking avoids is holding a lock **across the gap** between reading and writing — the part that can last seconds or minutes.

### The third option: make it one statement

```sql
UPDATE inventory
SET available = available - $2, version = version + 1
WHERE product_id = $1 AND available >= $2
RETURNING available;
```

There is no separate read. The `UPDATE` locks the row, evaluates `available >= $2` against the current value (re-checking after any wait), and writes a **relative** change. Two concurrent requests for the last item: one updates 1 row, the other updates 0 rows and knows it is out of stock. No version column, no explicit lock, no retry loop. Use it whenever the whole business rule fits in one `WHERE` clause.

---

## 3. Key Concepts

### Which isolation levels stop a lost update

| Level (PostgreSQL) | Read-then-write in app code | What the second writer sees |
|---|---|---|
| `READ COMMITTED` (default) | **Lost update possible** | Its absolute `SET available = 0` overwrites the other change |
| `REPEATABLE READ` | Prevented | `40001` "could not serialize access due to concurrent update"; retry the whole transaction |
| `SERIALIZABLE` | Prevented | `40001`; retry |

`REPEATABLE READ` is therefore a third, transaction-wide form of optimistic concurrency: no version column, but every transaction must be retryable. **MySQL (InnoDB) difference:** its `REPEATABLE READ` reads from a snapshot, but `UPDATE` acts on the latest committed row, so a plain `SELECT` followed by an `UPDATE` **can** lose an update. In MySQL use `SELECT … FOR UPDATE`, a version column, or an atomic `UPDATE`. More detail in [Isolation Levels](29-Isolation-Levels.md).

### Pessimistic locking in practice

- Run it **inside an explicit transaction** on one connection. In autocommit mode, `SELECT … FOR UPDATE` locks the row and releases it as soon as the statement ends — it protects nothing.
- Keep the critical section to a few milliseconds of database work. No HTTP calls, no payment provider, no user input while the lock is held.
- Bound the wait: `SET LOCAL lock_timeout = '3s'`, or `NOWAIT` to fail at once with `55P03` ("someone else is editing this").
- If you lock several rows, lock them in a consistent order, or you trade lost updates for [deadlocks](31-Deadlocks.md).
- Updating only non-key columns? `FOR NO KEY UPDATE` gives the same protection against concurrent updates and does not block foreign-key checks from child inserts.

### Optimistic locking in practice

- The `version` column (the sample schema has `inventory.version`) must be bumped by **every** writer: application code, admin scripts, backfills. A writer that forgets lets clients overwrite its change. A `BEFORE UPDATE` trigger that sets `NEW.version := OLD.version + 1` enforces it centrally.
- Always check the affected-row count. "0 rows" is the whole mechanism; ignoring it turns optimistic locking into no locking.
- **Retry or report?** If the code made the decision (reserve stock, increment a counter), re-read and retry a few times. If a **human** made the decision based on what they saw (edited a product description), do not retry silently — return a conflict and let them see the new state.
- **Across HTTP**, send the version to the client as an `ETag`. The client sends it back in `If-Match`; a mismatch returns **412 Precondition Failed**, and a missing `If-Match` can return **428 Precondition Required**. APIs that carry `version` in the JSON body usually return **409 Conflict**. The header side is in [HTTP Fundamentals](../Module-02-Core-Backend/01-HTTP-Fundamentals.md).

### What to use as the version

| Version source | How | Caveats |
|---|---|---|
| Integer `version` | `WHERE version = $2`, `SET version = version + 1` | Every writer must bump it. The recommended default |
| `updated_at` timestamp | `WHERE updated_at = $2` | `now()` is the **transaction start** time, so two updates in one transaction share it and a long transaction can write an *older* time. Postgres stores microseconds, but a JavaScript `Date` keeps milliseconds, so the value read into Node never equals the stored one. Clock skew if app servers set it |
| `xmin` system column | `SELECT xmin …`, then `WHERE xmin = $2::xid` | Postgres-only; changes on every update, even `SET x = x`; a 32-bit transaction counter that wraps around; not preserved by dump/restore or on a logical-replication subscriber. Some ORMs (e.g. EF Core's Npgsql provider) support it |
| Hash of the row content | Compute an ETag from the fields | Detects any change but costs a hash; no ordering between versions |

### ORM support

| ORM | Optimistic | Pessimistic |
|---|---|---|
| SQLAlchemy 2.0 | `__mapper_args__ = {"version_id_col": version}`; flush adds `AND version = :old`; raises `StaleDataError` when the row count is wrong | `select(...).with_for_update()` (options `nowait`, `skip_locked`, `key_share`, `read`), or `session.get(..., with_for_update=True)` |
| Hibernate / JPA | `@Version` field; `OptimisticLockException` | `LockModeType.PESSIMISTIC_WRITE` |
| Rails Active Record | `lock_version` column; `ActiveRecord::StaleObjectError` | `.lock` / `with_lock` |
| Prisma | No declarative version field. Use `updateMany({ where: { productId, version }, data: { …, version: { increment: 1 } } })` and treat `count === 0` as a conflict | No `FOR UPDATE` in the query API; use `$queryRaw` inside an interactive transaction |
| Drizzle | No built-in version feature; add `eq(inventory.version, expected)` to the `where` and check the rows from `.returning()` | `.for("update")` on a select |

SQLAlchemy, which does the bookkeeping for you:

```python
# pip install "sqlalchemy>=2.0" "psycopg[binary]"
from sqlalchemy import BigInteger, ForeignKey, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.orm.exc import StaleDataError


class Base(DeclarativeBase):
    pass


class Inventory(Base):
    __tablename__ = "inventory"
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), primary_key=True)
    available: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    # Every UPDATE now includes "AND version = <value loaded>" and bumps it.
    __mapper_args__ = {"version_id_col": version}


engine = create_engine("postgresql+psycopg://postgres:dev@localhost:5432/postgres")

try:
    with Session(engine) as session, session.begin():
        inv = session.get(Inventory, 7)
        if inv is not None and inv.available >= 1:
            inv.available -= 1  # flushed at commit as a version-checked UPDATE
except StaleDataError:
    print("inventory 7 changed since it was loaded; re-read and retry")
```

### How to choose

```mermaid
flowchart TD
    A["Read-modify-write on a shared row"] --> B{"Does the whole rule fit in one UPDATE ... WHERE?"}
    B -->|Yes| C["Atomic conditional UPDATE"]
    B -->|No| D{"Does the gap span user think time or an HTTP round trip?"}
    D -->|Yes| E["Optimistic: version column, 409 or 412 on conflict"]
    D -->|No| F{"Are conflicts on this row frequent?"}
    F -->|Yes| G["Pessimistic: SELECT ... FOR UPDATE in a short transaction"]
    F -->|No| H["Optimistic with a few retries, or pessimistic; both are fine"]
```

The arithmetic behind the frequent-conflict branch: with pessimistic locking, a hot row is a queue, and its throughput is roughly `1 / lock hold time` — a 5 ms critical section caps that one product at about 200 reservations per second, but every request eventually succeeds. With optimistic locking under the same load, most attempts read a version that is already stale, fail, and retry, so the database does the work several times and latency becomes unpredictable.

---

## 4. Code Examples

Scenario: reserve `qty` units of one product. The same operation is written three ways — pessimistic, optimistic, atomic — and a test runs 50 concurrent reservations against each to prove no update is lost.

### SQL

```sql
-- Pessimistic: one transaction, row locked from read to write.
BEGIN;
SET LOCAL lock_timeout = '3s';
SELECT available FROM inventory WHERE product_id = $1 FOR UPDATE;
-- app: if available < qty → ROLLBACK
UPDATE inventory SET available = available - $2, version = version + 1 WHERE product_id = $1;
COMMIT;

-- Optimistic: two independent statements, no lock in between.
SELECT available, version FROM inventory WHERE product_id = $1;
UPDATE inventory
SET available = $2, version = version + 1
WHERE product_id = $1 AND version = $3;          -- UPDATE 0 → conflict: re-read or 409

-- Atomic: check and write in one statement.
UPDATE inventory
SET available = available - $2, version = version + 1
WHERE product_id = $1 AND available >= $2
RETURNING available;                              -- no row → out of stock (or no such product)

-- Optional: make every writer bump the version, even ad-hoc SQL.
CREATE FUNCTION bump_version() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.version := OLD.version + 1;
  RETURN NEW;
END $$;
CREATE TRIGGER inventory_bump_version BEFORE UPDATE ON inventory
FOR EACH ROW EXECUTE FUNCTION bump_version();
-- With this trigger, "version = version + 1" in the statements above is redundant
-- but harmless: the trigger sets the final value from OLD.version either way.
```

### Node.js / TypeScript

```ts
// npm i pg && npm i -D @types/pg   — Node.js 22+, TypeScript 5, ESM  (file: inventory.ts)
import pg from "pg";
import { setTimeout as sleep } from "node:timers/promises";

export type ReserveResult =
  | { ok: true; available: number }
  | { ok: false; reason: "not_found" | "out_of_stock" | "conflict" };

export async function reservePessimistic(pool: pg.Pool, productId: number, qty: number): Promise<ReserveResult> {
  const client = await pool.connect(); // the lock lives in this connection's transaction
  try {
    await client.query("BEGIN");
    await client.query("SET LOCAL lock_timeout = '3s'"); // fail fast instead of piling up behind a stuck holder
    const { rows } = await client.query<{ available: number }>(
      "SELECT available FROM inventory WHERE product_id = $1 FOR UPDATE", [productId]);
    const available = rows[0]?.available;
    if (available === undefined || available < qty) {
      await client.query("ROLLBACK");
      return { ok: false, reason: available === undefined ? "not_found" : "out_of_stock" };
    }
    await client.query(
      "UPDATE inventory SET available = $2, version = version + 1 WHERE product_id = $1",
      [productId, available - qty]); // an absolute value is safe here: nobody can change the row
    await client.query("COMMIT");
    return { ok: true, available: available - qty };
  } catch (err) {
    await client.query("ROLLBACK").catch(() => undefined);
    throw err;
  } finally {
    client.release();
  }
}

export async function reserveOptimistic(
  pool: pg.Pool, productId: number, qty: number, maxAttempts = 5,
): Promise<ReserveResult> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    // Each statement is its own transaction, so pool.query is fine and no connection is held.
    const { rows } = await pool.query<{ available: number; version: number }>(
      "SELECT available, version FROM inventory WHERE product_id = $1", [productId]);
    if (rows.length === 0) return { ok: false, reason: "not_found" };
    const { available, version } = rows[0];
    if (available < qty) return { ok: false, reason: "out_of_stock" };

    const res = await pool.query(
      "UPDATE inventory SET available = $2, version = version + 1 WHERE product_id = $1 AND version = $3",
      [productId, available - qty, version]);
    if (res.rowCount === 1) return { ok: true, available: available - qty };
    await sleep(Math.random() * 5 * attempt); // lost the race: back off a little, then re-read
  }
  return { ok: false, reason: "conflict" }; // the API layer maps this to 409
}

export async function reserveAtomic(pool: pg.Pool, productId: number, qty: number): Promise<ReserveResult> {
  const { rows } = await pool.query<{ available: number }>(
    `UPDATE inventory SET available = available - $2, version = version + 1
     WHERE product_id = $1 AND available >= $2
     RETURNING available`, [productId, qty]);
  // Cannot tell "no such product" from "not enough stock"; usually fine for a reservation.
  return rows[0] ? { ok: true, available: rows[0].available } : { ok: false, reason: "out_of_stock" };
}
```

The concurrency test, with Node's built-in runner. The invariant it checks is the definition of "no lost update": every reported success is reflected exactly once in the row.

```ts
// node --test   — needs a disposable Postgres with the sample schema (TEST_DATABASE_URL)
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import pg from "pg";
import { reserveAtomic, reserveOptimistic, reservePessimistic, type ReserveResult } from "./inventory.js";

const pool = new pg.Pool({ connectionString: process.env.TEST_DATABASE_URL, max: 20 });
const N = 50;
const START = 60;
let productId = 0;

before(async () => {
  const { rows } = await pool.query<{ id: string }>(
    `INSERT INTO products (sku, name, category, price_cents)
     VALUES ('TEST-' || gen_random_uuid(), 'Race test', 'test', 100) RETURNING id`);
  productId = Number(rows[0].id);
});

after(async () => {
  await pool.query("DELETE FROM inventory WHERE product_id = $1", [productId]);
  await pool.query("DELETE FROM products WHERE id = $1", [productId]);
  await pool.end();
});

type Reserve = (pool: pg.Pool, productId: number, qty: number) => Promise<ReserveResult>;
const strategies: Record<string, Reserve> = {
  pessimistic: reservePessimistic,
  optimistic: reserveOptimistic,
  atomic: reserveAtomic,
};

for (const [name, reserve] of Object.entries(strategies)) {
  test(`${name}: ${N} concurrent reservations lose no update`, async () => {
    await pool.query(
      `INSERT INTO inventory (product_id, available, version) VALUES ($1, $2, 0)
       ON CONFLICT (product_id) DO UPDATE SET available = EXCLUDED.available, version = 0`,
      [productId, START]);

    // 50 calls over 20 connections: up to 20 really run at the same time in Postgres.
    const results = await Promise.all(Array.from({ length: N }, () => reserve(pool, productId, 1)));
    const succeeded = results.filter((r) => r.ok).length;

    const { rows } = await pool.query<{ available: number; version: number }>(
      "SELECT available, version FROM inventory WHERE product_id = $1", [productId]);
    assert.equal(rows[0].available, START - succeeded); // no success was overwritten
    assert.equal(rows[0].version, succeeded);           // exactly one write per success
    if (name !== "optimistic") assert.equal(succeeded, N); // optimistic may give up with "conflict"
  });
}
```

### Python

```python
# pip install "psycopg[binary]"   — Python 3.12+   (file: inventory.py)
import random
import time
from dataclasses import dataclass
from typing import Literal

import psycopg


@dataclass(frozen=True)
class Reserve:
    ok: bool
    available: int | None = None
    reason: Literal["not_found", "out_of_stock", "conflict"] | None = None


def reserve_pessimistic(conn: psycopg.Connection, product_id: int, qty: int) -> Reserve:
    with conn.transaction():  # the lock lives until this block commits or rolls back
        conn.execute("SET LOCAL lock_timeout = '3s'")
        row = conn.execute(
            "SELECT available FROM inventory WHERE product_id = %s FOR UPDATE", (product_id,)
        ).fetchone()
        if row is None:
            return Reserve(False, reason="not_found")
        if row[0] < qty:
            return Reserve(False, reason="out_of_stock")
        conn.execute(
            "UPDATE inventory SET available = %s, version = version + 1 WHERE product_id = %s",
            (row[0] - qty, product_id),
        )
        return Reserve(True, available=row[0] - qty)


def reserve_optimistic(conn: psycopg.Connection, product_id: int, qty: int,
                       max_attempts: int = 5) -> Reserve:
    """`conn` must be in autocommit mode: each retry needs a fresh read, not one old snapshot."""
    for attempt in range(1, max_attempts + 1):
        row = conn.execute(
            "SELECT available, version FROM inventory WHERE product_id = %s", (product_id,)
        ).fetchone()
        if row is None:
            return Reserve(False, reason="not_found")
        available, version = row
        if available < qty:
            return Reserve(False, reason="out_of_stock")
        cur = conn.execute(
            "UPDATE inventory SET available = %s, version = version + 1"
            " WHERE product_id = %s AND version = %s",
            (available - qty, product_id, version),
        )
        if cur.rowcount == 1:
            return Reserve(True, available=available - qty)
        time.sleep(random.uniform(0, 0.005 * attempt))  # lost the race; re-read and try again
    return Reserve(False, reason="conflict")


def reserve_atomic(conn: psycopg.Connection, product_id: int, qty: int) -> Reserve:
    row = conn.execute(
        "UPDATE inventory SET available = available - %(qty)s, version = version + 1"
        " WHERE product_id = %(id)s AND available >= %(qty)s RETURNING available",
        {"id": product_id, "qty": qty},
    ).fetchone()
    return Reserve(True, available=row[0]) if row else Reserve(False, reason="out_of_stock")
```

The same test with pytest. Threads give real concurrency here, because psycopg releases the GIL while it waits on the network.

```python
# pip install pytest "psycopg[binary]"   — run: TEST_DATABASE_URL=... pytest -q
import os
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor

import psycopg
import pytest

from inventory import Reserve, reserve_atomic, reserve_optimistic, reserve_pessimistic

DSN = os.environ["TEST_DATABASE_URL"]
N, START = 50, 60


@pytest.fixture
def product_id() -> Iterator[int]:
    with psycopg.connect(DSN, autocommit=True) as conn:
        (pid,) = conn.execute(
            "INSERT INTO products (sku, name, category, price_cents)"
            " VALUES ('TEST-' || gen_random_uuid(), 'Race test', 'test', 100) RETURNING id"
        ).fetchone()
        conn.execute("INSERT INTO inventory (product_id, available) VALUES (%s, %s)", (pid, START))
        yield pid
        conn.execute("DELETE FROM inventory WHERE product_id = %s", (pid,))
        conn.execute("DELETE FROM products WHERE id = %s", (pid,))


def call_once(strategy: Callable[[psycopg.Connection, int, int], Reserve], pid: int) -> Reserve:
    # One connection per call: a psycopg connection runs one transaction at a time,
    # so sharing it across threads would serialize the very race we want to test.
    with psycopg.connect(DSN, autocommit=True) as conn:
        return strategy(conn, pid, 1)


@pytest.mark.parametrize("strategy", [reserve_pessimistic, reserve_optimistic, reserve_atomic])
def test_no_lost_update(strategy: Callable[[psycopg.Connection, int, int], Reserve], product_id: int) -> None:
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(lambda _: call_once(strategy, product_id), range(N)))
    succeeded = sum(r.ok for r in results)

    with psycopg.connect(DSN) as conn:
        available, version = conn.execute(
            "SELECT available, version FROM inventory WHERE product_id = %s", (product_id,)
        ).fetchone()
    assert available == START - succeeded
    assert version == succeeded
    if strategy is not reserve_optimistic:
        assert succeeded == N
```

**Make the test fail first.** Point it at a naive version — `SELECT available`, then `UPDATE … SET available = $2` with no lock and no version check — and `available` ends well above `START - succeeded`: several "successful" reservations were overwritten. A concurrency test that has never failed has not proven anything.

**Differences to notice.** In Node, `Promise.all` puts all 50 calls in flight at once; the pool (`max: 20`) is what limits real parallelism, and the pessimistic version must hold a `PoolClient` because `BEGIN … COMMIT` on `pool.query` could run on different connections. In Python the parallelism comes from 20 threads, each with its own connection. The optimistic function depends on autocommit: in a non-autocommit psycopg connection, the first `SELECT` opens a transaction that stays open across retries, and under `REPEATABLE READ` every retry would re-read the same stale snapshot.

---

## 5. Production Concerns

- **Hot rows decide the strategy.** One best-selling SKU can take most of the traffic. Pessimistic locking turns it into a queue: throughput ≈ 1 / lock hold time, so keep the transaction to the lock, the check and the write. Optimistic locking on the same row wastes most attempts. If the rule fits, the atomic `UPDATE` is fastest of all, because its lock is held only for one statement.
- **Never hold `FOR UPDATE` across a remote call.** Charging a card while holding the inventory lock makes every other buyer of that product wait for the payment provider's latency. Reserve stock in a short transaction, call the provider, then confirm or release in another short transaction.
- **Measure conflicts.** For optimistic paths, count attempts, 0-row updates and final `conflict` results per endpoint; a conflict rate above a few percent says the row is hotter than "optimistic" assumes. For pessimistic paths, watch lock waits (`log_lock_waits`, sessions with `wait_event_type = 'Lock'`) and `55P03` timeouts.
- **User-facing conflicts.** For edits made by people, return 412 (with `If-Match`) or 409 plus the current state, so the UI can show what changed. Never auto-merge a human's stale edit.
- **Replicas.** Reading the version from a read replica is safe for optimistic locking (a stale version just causes a conflict) but raises the conflict rate. Pessimistic reads must go to the primary; a hot standby cannot take row locks.
- **Every writer must play.** A batch job or support script that updates `inventory` without bumping `version` creates a window in which a client's optimistic write overwrites it. Use the trigger from section 4 or route all writes through one repository.

---

## 6. Common Mistakes

- **`SELECT … FOR UPDATE` in autocommit mode** — the lock is released when the statement ends, before your `UPDATE` — open an explicit transaction on one dedicated connection (`pool.connect()` in Node, `conn.transaction()` in psycopg).
- **Ignoring the affected-row count** — a 0-row optimistic `UPDATE` is treated as success, and the lost update is back — check `rowCount` / `rowcount` and treat 0 as a conflict.
- **Checking the version in code, then updating without it** — `if (row.version === expected) await update(...)` has the same race as before — put `AND version = $n` in the `UPDATE`'s `WHERE`.
- **Using `updated_at` read into a JavaScript `Date` as the version** — microseconds are truncated to milliseconds, the equality never matches, and every write "conflicts" — use an integer `version` column.
- **Silently retrying a human's edit** — the retry applies a decision made on data the user never saw — return 409/412 with the current state instead.
- **Optimistic locking on a hot counter** — under load most attempts fail and retry, multiplying database work — use an atomic `UPDATE … SET n = n - $1 WHERE n >= $1`, or pessimistic locking.
- **Absolute writes in "atomic" updates** — `SET available = $2` computed from an earlier read is a lost update even inside one `UPDATE` statement — write relative changes (`available - $2`) with the condition in the `WHERE`.

---

## 7. Comparison Table

| | Pessimistic (`FOR UPDATE`) | Optimistic (`version`) | Atomic conditional `UPDATE` | `REPEATABLE READ` / `SERIALIZABLE` |
|---|---|---|---|---|
| Conflict handling | Later writers **wait** | Later writer gets **0 rows**, retries or reports | Database re-checks the `WHERE` after any wait | Later writer gets `40001`, retries the transaction |
| Lock held | From read to commit | Only during the `UPDATE` | Only during the `UPDATE` | Only during writes |
| Can span HTTP / user think time | No | **Yes** (ETag / `If-Match`) | Not applicable | No |
| Best under | High contention, short critical section | Low contention, long or remote gaps | Any contention, if the rule fits one `WHERE` | Complex multi-row invariants |
| Failure modes | Lock waits, deadlocks, pool exhaustion | Retry storms, conflicts shown to users | Logic that does not fit a single statement | Retries everywhere; every transaction must be retryable |
| Extra schema | None | `version` column | None | None |

---

## 8. Interview Questions

**[Junior] What is a lost update?**
Two transactions read the same row, compute a new value in application code, and write it back. The second write replaces the first, so one change disappears without any error. For example, two requests both read `available = 1` and both write `0`, selling one item twice. PostgreSQL's default `READ COMMITTED` does not prevent it.

**[Junior] What is the difference between optimistic and pessimistic locking?**
Pessimistic locking locks the row when you read it (`SELECT … FOR UPDATE`), so other writers wait until you commit. Optimistic locking takes no lock while you work; it reads a version number and makes the write conditional on that version (`WHERE version = $2`). If someone else changed the row first, the update matches 0 rows and you retry or report a conflict.

**[Mid] How do you implement optimistic locking in SQL, and what do you do on a conflict?**
Add an integer `version` column. Read the row with its version, then `UPDATE … SET …, version = version + 1 WHERE id = $1 AND version = $2`. If the affected-row count is 0, another writer won. For machine decisions such as reserving stock, re-read and retry a few times with a small random backoff. For human edits, return 409 (or 412 when using `If-Match`) with the current state.

**[Mid] Why is `UPDATE inventory SET available = available - 1 WHERE product_id = $1 AND available >= 1` safe without explicit locks?**
The check and the write are the same statement, so there is no gap for another transaction to slip into. The `UPDATE` takes a row lock, and if it has to wait for a concurrent writer, `READ COMMITTED` re-evaluates the `WHERE` on the newest row version before writing. The change is relative (`available - 1`), so it applies to the current value, not a stale one. When stock runs out, the statement updates 0 rows.

**[Mid] Does `REPEATABLE READ` prevent lost updates?**
In PostgreSQL, yes: if the row was changed by a transaction that committed after your snapshot was taken, your `UPDATE` fails with `40001`, and you must retry the whole transaction. In MySQL InnoDB, no: `UPDATE` works on the latest committed row while plain `SELECT` reads the snapshot, so read-then-write can still lose an update. There you need `SELECT … FOR UPDATE`, a version column, or an atomic update.

**[Senior] A flash sale puts 5,000 requests per second on one product. Which strategy do you use?**
Optimistic locking fails badly here: almost every attempt reads a version that is already stale, so retries multiply the load. Pessimistic locking is correct but serializes everything on one row; at a 5 ms hold time it caps out near 200 per second, and requests queue in the pool. The best fit is the atomic conditional `UPDATE`, which holds the lock for one short statement and needs no retries. If even that is too slow, split the stock into several rows (buckets) and pick one at random, or reserve from a pre-allocated pool in memory and settle in batches — accepting more complexity in exchange for throughput.

**[Senior] How do you implement optimistic concurrency for a REST API where users edit a product page?**
Return the row's `version` as an `ETag` on `GET`. On `PUT` or `PATCH`, require `If-Match` (428 if missing). Run `UPDATE … WHERE id = $1 AND version = $2`; if it matches 0 rows, return 412 with the current representation so the UI can show the conflict. Do not retry automatically, because the user's change was based on data that is now outdated. Make sure every other writer — admin tools, imports — bumps the version, ideally with a trigger.

**[Senior] Can you use `updated_at` or `xmin` instead of a version column?**
You can, with caveats. `updated_at` set by `now()` uses the transaction start time, so two updates in one transaction get the same value and a long transaction can write a time that is older than a concurrent one. It also loses precision in clients: JavaScript `Date` truncates Postgres microseconds to milliseconds, so equality checks fail. `xmin` changes on every update and needs no schema change, but it is Postgres-specific, a wrapping 32-bit counter, and is not preserved by dump/restore or logical replication. An integer version column is explicit, portable and cheap.

---

## 9. Cheat Sheet

```text
Lost update     read → compute in app → write absolute value; second write erases first; RC allows it
Pessimistic     BEGIN; SELECT … FOR UPDATE; check; UPDATE; COMMIT   (one dedicated connection)
                + bound waits: SET LOCAL lock_timeout / NOWAIT (55P03); lock rows in id order
Optimistic      UPDATE … SET …, version = version + 1 WHERE id = $1 AND version = $2
                0 rows = conflict → re-read + retry (machine) or 409/412 (human)
Atomic          UPDATE … SET n = n - $2 WHERE id = $1 AND n >= $2 RETURNING n   ← prefer when it fits
Choose          rule fits one WHERE → atomic; spans HTTP/user → optimistic;
                hot row + short section → pessimistic; rare conflicts → either
Hot row         pessimistic throughput ≈ 1 / hold time; optimistic → retry storm
Isolation       PG REPEATABLE READ/SERIALIZABLE → 40001 on lost update; MySQL RR does NOT prevent it
HTTP            version → ETag; If-Match mismatch → 412; missing → 428; body version → 409
Version source  integer column (best) | updated_at (ms vs µs, now() = txn start) | xmin (PG-only, wraps)
ORMs            SQLAlchemy version_id_col → StaleDataError; Hibernate @Version; Rails lock_version;
                Prisma/Drizzle: manual WHERE version + check count
Test            N parallel reservations; assert available = start − successes and version = successes
```

---

## Related Topics

- [Database Locks](30-Database-Locks.md) — the row lock modes behind `FOR UPDATE` and `FOR NO KEY UPDATE`
- [Deadlocks](31-Deadlocks.md) — what pessimistic locking on several rows can cause, and how ordering prevents it
- [Isolation Levels](29-Isolation-Levels.md) — which levels detect a lost update and why retries follow
- [ORM Fundamentals](33-ORM-Fundamentals.md) — version columns and locking options in SQLAlchemy, Prisma and Drizzle
- [HTTP Fundamentals](../Module-02-Core-Backend/01-HTTP-Fundamentals.md) — `ETag` and `If-Match` as optimistic concurrency over HTTP
- [Race Conditions](../Module-04-Operating-Systems/13-Race-Conditions.md) — the general read-modify-write race in threads and processes

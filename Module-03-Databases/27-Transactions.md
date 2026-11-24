# Transactions

> **Module 03 · Databases** · Prerequisites: [SQL DML](09-SQL-DML.md), [Query Anti-Patterns](26-Query-Anti-Patterns.md) · Next: [ACID](28-ACID.md)

---

## ⏱ If You Only Have 2 Minutes

- A transaction is a group of statements that commit together or not at all: `BEGIN` … `COMMIT`, or `ROLLBACK` to throw everything away. It should wrap one business invariant ("stock goes down **and** the order exists"), not an arbitrary block of code.
- Without `BEGIN`, PostgreSQL runs **every statement as its own transaction** (autocommit). `pg` (node-postgres) and asyncpg send statements in autocommit mode; psycopg 3 does the opposite and silently opens a transaction on the first statement.
- **A transaction lives on one connection.** In node-postgres, `pool.query("BEGIN")` followed by `pool.query("UPDATE …")` can run on two different connections. Use `const client = await pool.connect()` and send every statement through that `client`.
- After any error inside a transaction, PostgreSQL rejects every further statement (`25P02 current transaction is aborted`) until you `ROLLBACK`. A `COMMIT` at that point quietly rolls back.
- Keep transactions **short** and **free of network calls**. Each open transaction holds a pooled connection and its row locks. Enforce it with `statement_timeout` and `idle_in_transaction_session_timeout`.
- Retry the **whole transaction** — never one statement — and only for `40001` (serialization failure) and `40P01` (deadlock detected). Use a small bounded number of attempts with jittered backoff.
- A retried transaction must be safe to run twice: no emails, HTTP calls or queue publishes inside it, and every value recomputed from fresh reads on each attempt.

---

## 1. What It Is and Why It Exists

A **transaction** is a unit of work the database treats as indivisible. You open it, run several reads and writes, and then either **commit** (all changes become permanent and visible to others at once) or **roll back** (none of them ever happened). The guarantees behind that promise are the subject of the next chapter, [ACID](28-ACID.md). This chapter is about using transactions correctly from application code.

**Analogy:** a shopping basket at a self-checkout. You scan items one by one, but nothing is charged until you press "Pay". If the card is declined, the whole basket is voided — you never walk out having paid for half of it. And while you are scanning, you are occupying a till that someone else is waiting for.

**What breaks without it.** Placing an order in the sample schema takes at least three writes:

1. decrement `inventory.available` for each product,
2. insert a row into `orders`,
3. insert rows into `order_items`.

If each write commits on its own and the process crashes after step 1, stock has disappeared with no order to show for it. If the second product is out of stock, the first product's stock has already been taken. A transaction makes the three steps one: a crash, an error or an explicit `ROLLBACK` before `COMMIT` leaves the data exactly as it was.

**The cost.** An open transaction is not free. It pins one database connection, holds every row lock it has taken until it ends, and (in PostgreSQL) stops `VACUUM` from cleaning up row versions that it might still need to see. Most production problems with transactions are not about forgetting them — they are about holding them open too long, running them on the wrong connection, or retrying them wrongly.

---

## 2. How It Works

### The statements

```sql
BEGIN;                                   -- or START TRANSACTION
UPDATE inventory SET available = available - 2 WHERE product_id = 1 AND available >= 2;
INSERT INTO orders (customer_id, status, total_cents) VALUES (7, 'pending', 3998) RETURNING id;
COMMIT;                                  -- or ROLLBACK to discard everything above
```

Between `BEGIN` and `COMMIT`, your own session sees its uncommitted changes. Other sessions do not; what they see instead depends on the isolation level (see [Isolation Levels](29-Isolation-Levels.md)). At `COMMIT`, all changes become visible to new snapshots together.

### Transaction states on a connection

Every PostgreSQL connection is always in one of three states. The server reports the state to the driver after each command (the `ReadyForQuery` message carries `I`, `T` or `E`), and `pg_stat_activity.state` shows the same thing from the server side.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> InTransaction: BEGIN
    InTransaction --> InTransaction: statement succeeds
    InTransaction --> Idle: COMMIT
    InTransaction --> Idle: ROLLBACK
    InTransaction --> Failed: statement raises an error
    Failed --> Failed: any statement fails with 25P02
    Failed --> Idle: ROLLBACK, or COMMIT which rolls back
```

| Protocol status | `pg_stat_activity.state` | Meaning |
|---|---|---|
| `I` | `idle` | No transaction open. Each statement autocommits. |
| `T` | `idle in transaction` (between statements) | A transaction is open. Locks are held, the connection cannot serve anyone else. |
| `E` | `idle in transaction (aborted)` | A statement failed. Only `ROLLBACK` (or `ROLLBACK TO SAVEPOINT`) does anything useful now. |

Two details trip people up:

- **The aborted state is sticky.** After a failed statement, PostgreSQL rejects everything with `ERROR: current transaction is aborted, commands ignored until end of transaction block` (SQLSTATE `25P02`). You cannot "catch the error and carry on" in plain SQL; you must roll back, or roll back to a savepoint.
- **`COMMIT` of a failed transaction does not raise an error.** It ends the transaction, rolls it back, and reports the command tag `ROLLBACK`. If application code swallowed the original error, it will believe it committed.

### Autocommit and what each driver does by default

PostgreSQL itself has no "autocommit off" switch: a statement outside `BEGIN` is always its own transaction. Drivers decide whether to send `BEGIN` for you.

| Driver / layer | Default | How you get a multi-statement transaction |
|---|---|---|
| `pg` (node-postgres) | Autocommit. Each `query()` stands alone. | `pool.connect()`, then `BEGIN` / `COMMIT` / `ROLLBACK` on that client |
| psycopg 3 | **Not** autocommit (DB-API rule). The first statement silently opens a transaction that stays open until `commit()` / `rollback()`. | `with conn.transaction():` — or connect with `autocommit=True` and use `transaction()` blocks explicitly |
| asyncpg | Autocommit | `async with conn.transaction():` |
| SQLAlchemy 2.0 `Session` | "Autobegin" on the first statement | `with session.begin():` or `session.commit()` |
| MySQL server | `autocommit=1` per session | `START TRANSACTION` … `COMMIT` |

psycopg's default is the source of a classic leak: a script runs one `SELECT`, never commits, and the connection sits `idle in transaction` for hours. The `with psycopg.connect(...) as conn:` block commits on a clean exit and rolls back on an exception, which helps — but a long-lived connection outside such a block does not get that protection.

### One connection per transaction

A transaction is a property of a **server session**, and a session is one connection. A connection pool hands out *any* free connection for each call. That is the node-postgres pitfall:

```text
pool.query("BEGIN")                     → runs on connection #3, which is now "idle in transaction"
pool.query("UPDATE inventory …")        → runs on connection #7, autocommits immediately
pool.query("INSERT INTO orders …")      → fails on connection #1
pool.query("ROLLBACK")                  → runs on connection #5: "WARNING: there is no transaction in progress"
```

The stock decrement is committed, the order is not, and connection #3 has an open transaction that nobody will ever close. The fix is to check out one client and use it for every statement until `COMMIT` or `ROLLBACK`, then release it. Any repository or helper called inside the transaction must receive that client, not the pool.

### Savepoints

A **savepoint** marks a point inside a transaction that you can roll back to without abandoning the whole transaction.

```sql
SAVEPOINT gift;                -- mark
-- ... statements that may fail ...
ROLLBACK TO SAVEPOINT gift;    -- undo only work after the mark; the transaction is usable again
RELEASE SAVEPOINT gift;        -- forget the mark (its work stays part of the transaction)
```

Rolling back to a savepoint also clears the aborted state, so this is the only way to recover from an error *inside* a transaction. Nothing done after a savepoint is permanent until the outer `COMMIT`. Drivers map nested transaction blocks to savepoints: psycopg's and asyncpg's nested `transaction()` and SQLAlchemy's `begin_nested()` all issue `SAVEPOINT` for you.

---

## 3. Key Concepts

### Transaction scope: what goes inside

The right scope is **the smallest set of writes that must be all-or-nothing**, plus the reads those writes depend on.

| Put inside | Keep outside |
|---|---|
| Conditional `UPDATE`s that reserve stock or money | Input validation that needs no data |
| Inserts that must exist together (order + items + outbox row) | HTTP calls: payment providers, other services |
| Reads whose result decides the writes | Sending email, publishing to Kafka/RabbitMQ |
| | Password hashing, PDF rendering, any slow CPU work |
| | Waiting for user input |

Side effects belong after the commit, usually through an outbox row written in the same transaction (see [Service Layer Pattern](../Module-02-Core-Backend/13-Service-Layer-Pattern.md) and [Asynchronous Processing](../Module-02-Core-Backend/19-Asynchronous-Processing.md)). A rollback cannot un-send an email, and a transaction waiting on a slow API holds its locks and its connection for the whole wait.

### Why "short" matters

An open transaction costs three things, and all three grow with its duration:

| Resource held | What it blocks | Symptom |
|---|---|---|
| A pooled connection | Other requests in the same process (`pg` pools default to 10 connections) | Pool wait time rises, then every endpoint times out |
| Row locks taken by `UPDATE` / `DELETE` / `SELECT … FOR UPDATE` | Other transactions writing the same rows | Lock waits; on hot rows (a flash-sale product) throughput collapses |
| Its snapshot (the oldest transaction ID it may need) | `VACUUM` removing dead row versions in **every** table | Table and index bloat, slower queries hours later |

A transaction that is `idle in transaction` for 10 minutes is worse than one running a 10-minute query: it does nothing useful while holding all three.

### Timeouts that enforce short transactions

PostgreSQL has server-side guards. Set them per role (so every connection gets them) or per transaction with `SET LOCAL`:

| Setting | What it stops | Error when it fires |
|---|---|---|
| `statement_timeout` | Any single statement running longer than the limit | `57014 canceling statement due to statement timeout` — the transaction is now aborted |
| `lock_timeout` | Waiting longer than the limit to acquire a lock | `55P03 lock_not_available` |
| `idle_in_transaction_session_timeout` | A session sitting inside an open transaction with no statement running | The server **terminates the session** (`25P03`); the transaction rolls back |
| `transaction_timeout` (PostgreSQL 17+) | A whole transaction lasting longer than the limit | The session is terminated |

`SET LOCAL` lasts only until the end of the current transaction, which is what you want on pooled connections. A plain `SET` sticks to the session and leaks to the next request that borrows that connection — and through a transaction-mode pooler such as PgBouncer, to an unrelated client.

### Retrying: which errors, and what to retry

Some failures are the database telling you "this transaction lost a race; try again":

| SQLSTATE | Name | When it happens | Retry? |
|---|---|---|---|
| `40001` | `serialization_failure` | `REPEATABLE READ` / `SERIALIZABLE` detected a conflict (see [Isolation Levels](29-Isolation-Levels.md)); can also be raised by `COMMIT` | Yes, the whole transaction |
| `40P01` | `deadlock_detected` | Two transactions waited on each other's locks; PostgreSQL aborted one (see [Deadlocks](31-Deadlocks.md)) | Yes, the whole transaction |
| `23505`, `23514`, `23503` | unique / check / foreign-key violation | Your data broke a constraint | No — it will fail the same way; map it to a business error |
| `57014`, `55P03` | statement or lock timeout | The system is overloaded or a lock is held too long | Not automatically; retrying adds load to the overload |
| connection lost during `COMMIT` | — | The commit may or may not have happened | Not blindly — see below |

**Retry the whole transaction, from `BEGIN`.** After `40001`, the transaction is aborted; re-running the last statement is impossible (`25P02`) and would be wrong anyway, because the earlier reads that led to it came from a snapshot that lost the race. Rolling back and calling the same function again gives it a fresh snapshot.

**Bound and jitter the retries.** Two or three retries with randomised exponential backoff (say up to 50 ms, 100 ms, 200 ms) is plenty. Without jitter, the same two transactions retry at the same instant and collide again. Unlimited retries turn a contention spike into a retry storm. See [Exponential Backoff](../Module-07-Advanced-Backend-and-System-Design/36-Exponential-Backoff.md).

**The ambiguous commit.** If the connection drops after you send `COMMIT` but before the reply arrives, you do not know whether the transaction committed. Retrying might place the order twice. Only retry this case if the transaction is idempotent — for example, it inserts an idempotency key under a `UNIQUE` constraint so a second run fails cleanly or returns the first result. See [Idempotency](../Module-07-Advanced-Backend-and-System-Design/32-Idempotency.md).

### Idempotent transaction bodies

The function you pass to a retry helper will run more than once. It must:

- compute everything from reads made **inside** the current attempt (not from a value read before the helper was called);
- touch nothing outside the database — no `fetch()`, no email, no in-memory cache mutation that is not undone on rollback;
- generate random IDs inside the attempt or let the database generate them, so a rolled-back attempt leaves no trace.

---

## 4. Code Examples

Scenario: "place order" for several products. In one transaction, each product's `inventory.available` is atomically decremented (a conditional `UPDATE` — no read-then-write race), the `orders` row and its `order_items` are inserted, and the whole thing is retried on `40001` / `40P01`. If any product is short, everything rolls back, including decrements already made for earlier products.

### SQL

What the helper sends, plus a savepoint for an optional step: a free gift that is added only if gift stock remains.

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT set_config('statement_timeout', '5000', true);   -- like SET LOCAL, but accepts a bind parameter

-- Lock order: ascending product_id, so two multi-item orders cannot deadlock each other.
UPDATE inventory AS i
   SET available = i.available - 2
  FROM products AS p
 WHERE i.product_id = 1 AND p.id = i.product_id AND i.available >= 2
RETURNING p.price_cents;                                 -- 0 rows → out of stock → ROLLBACK

INSERT INTO orders (customer_id, status, total_cents) VALUES (7, 'pending', 3998) RETURNING id;   -- say 1042

INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents)
SELECT 1042, * FROM unnest('{1}'::bigint[], '{2}'::int[], '{1999}'::int[]);

SAVEPOINT gift;
UPDATE inventory SET available = available - 1 WHERE product_id = 99;
-- If gift stock is 0 this raises 23514 (inventory_available_check) and the transaction is aborted.
-- ROLLBACK TO SAVEPOINT gift;   ← undoes only the gift; the order above is intact and COMMIT works
RELEASE SAVEPOINT gift;

COMMIT;
```

Server-side guards, set once per application role, and a query to find offenders:

```sql
ALTER ROLE app_rw SET statement_timeout = '5s';
ALTER ROLE app_rw SET lock_timeout = '2s';
ALTER ROLE app_rw SET idle_in_transaction_session_timeout = '15s';

-- Who is holding a transaction open right now?
SELECT pid, state, now() - xact_start AS xact_age, left(query, 60) AS last_statement
FROM pg_stat_activity
WHERE xact_start IS NOT NULL AND pid <> pg_backend_pid()
ORDER BY xact_start
LIMIT 10;
```

### Node.js / TypeScript

```ts
// npm i pg && npm i -D @types/pg   — Node.js 22+, TypeScript 5, ESM
import pg, { type Pool, type PoolClient } from "pg";
import { setTimeout as sleep } from "node:timers/promises";

type Isolation = "READ COMMITTED" | "REPEATABLE READ" | "SERIALIZABLE";
interface TxOptions { retries?: number; isolation?: Isolation; statementTimeoutMs?: number }

const RETRYABLE = new Set(["40001", "40P01"]); // serialization_failure, deadlock_detected

function sqlState(err: unknown): string | undefined {
  return typeof err === "object" && err !== null && "code" in err && typeof err.code === "string"
    ? err.code : undefined;
}

export async function withTransaction<T>(
  pool: Pool,
  fn: (client: PoolClient) => Promise<T>,
  { retries = 3, isolation = "READ COMMITTED", statementTimeoutMs = 5000 }: TxOptions = {},
): Promise<T> {
  for (let attempt = 0; ; attempt++) {
    const client = await pool.connect(); // every statement of this attempt runs on this one connection
    let broken = false;
    let delayMs = 0;
    try {
      await client.query(`BEGIN ISOLATION LEVEL ${isolation}`); // a fixed union type, never user input
      await client.query("SELECT set_config('statement_timeout', $1, true)", [String(statementTimeoutMs)]);
      const result = await fn(client);
      await client.query("COMMIT");
      return result;
    } catch (err) {
      try { await client.query("ROLLBACK"); } catch { broken = true; }
      if (!RETRYABLE.has(sqlState(err) ?? "") || attempt >= retries) throw err;
      delayMs = Math.random() * Math.min(1000, 50 * 2 ** attempt); // full jitter
    } finally {
      client.release(broken); // true destroys a connection left in an unknown state
    }
    await sleep(delayMs); // sleep after release: never hold a connection while waiting
  }
}

export class OutOfStock extends Error {
  constructor(readonly productId: number) { super(`not enough stock for product ${productId}`); }
}

export interface Line { productId: number; quantity: number }

export function placeOrder(pool: Pool, customerId: number, lines: Line[]) {
  const sorted = [...lines].sort((a, b) => a.productId - b.productId); // fixed lock order
  return withTransaction(pool, async (client) => {
    // Everything below is recomputed on each attempt, so a retry starts from fresh data.
    const prices: number[] = [];
    for (const { productId, quantity } of sorted) {
      const { rows } = await client.query<{ price_cents: number }>(
        `UPDATE inventory AS i SET available = i.available - $2
           FROM products AS p
          WHERE i.product_id = $1 AND p.id = i.product_id AND i.available >= $2
         RETURNING p.price_cents`,
        [productId, quantity],
      );
      if (rows.length === 0) throw new OutOfStock(productId); // rolls back earlier decrements too
      prices.push(rows[0]!.price_cents);
    }
    const totalCents = sorted.reduce((sum, l, i) => sum + l.quantity * prices[i]!, 0);
    const { rows } = await client.query<{ id: string }>( // pg returns bigint as a string
      "INSERT INTO orders (customer_id, status, total_cents) VALUES ($1, 'pending', $2) RETURNING id",
      [customerId, totalCents],
    );
    const orderId = rows[0]!.id;
    await client.query( // one round trip for all items
      `INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents)
       SELECT $1, * FROM unnest($2::bigint[], $3::int[], $4::int[])`,
      [orderId, sorted.map((l) => l.productId), sorted.map((l) => l.quantity), prices],
    );
    return { orderId, totalCents };
  });
}

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 10 });
console.log(await placeOrder(pool, 7, [{ productId: 2, quantity: 1 }, { productId: 1, quantity: 2 }]));
await pool.end();
```

### Python

```python
# pip install "psycopg[binary,pool]"   — Python 3.12+, psycopg 3.2+
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Literal

from psycopg import AsyncConnection, errors
from psycopg_pool import AsyncConnectionPool

RETRYABLE = (errors.SerializationFailure, errors.DeadlockDetected)  # 40001, 40P01
SET_ISOLATION = {  # fixed statements: the level is never interpolated from input
    "READ COMMITTED": "SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
    "REPEATABLE READ": "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ",
    "SERIALIZABLE": "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE",
}


async def with_transaction[T](
    pool: AsyncConnectionPool,
    fn: Callable[[AsyncConnection], Awaitable[T]],
    *,
    retries: int = 3,
    isolation: Literal["READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"] = "READ COMMITTED",
) -> T:
    for attempt in range(retries + 1):
        try:
            async with pool.connection() as conn:   # one connection for the whole attempt
                async with conn.transaction():      # BEGIN; COMMIT on exit, ROLLBACK on exception
                    await conn.execute(SET_ISOLATION[isolation])  # must be the first statement
                    await conn.execute("SELECT set_config('statement_timeout', %s, true)", ["5000"])
                    return await fn(conn)
        except RETRYABLE:
            if attempt == retries:
                raise
        # The connection is back in the pool before we sleep.
        await asyncio.sleep(random.uniform(0, min(1.0, 0.05 * 2**attempt)))
    raise AssertionError("unreachable")


class OutOfStock(Exception):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"not enough stock for product {product_id}")
        self.product_id = product_id


async def place_order(pool: AsyncConnectionPool, customer_id: int,
                      lines: list[tuple[int, int]]) -> tuple[int, int]:
    ordered = sorted(lines)  # (product_id, quantity) in fixed lock order

    async def work(conn: AsyncConnection) -> tuple[int, int]:
        priced: list[tuple[int, int, int]] = []
        for product_id, qty in ordered:
            cur = await conn.execute(
                """UPDATE inventory AS i SET available = i.available - %(qty)s
                     FROM products AS p
                    WHERE i.product_id = %(pid)s AND p.id = i.product_id AND i.available >= %(qty)s
                   RETURNING p.price_cents""",
                {"pid": product_id, "qty": qty},
            )
            row = await cur.fetchone()
            if row is None:
                raise OutOfStock(product_id)  # not retryable: propagates after ROLLBACK
            priced.append((product_id, qty, row[0]))
        total = sum(qty * price for _, qty, price in priced)
        cur = await conn.execute(
            "INSERT INTO orders (customer_id, status, total_cents) VALUES (%s, 'pending', %s) RETURNING id",
            (customer_id, total),
        )
        order = await cur.fetchone()
        assert order is not None
        async with conn.cursor() as items:  # executemany is pipelined in psycopg 3
            await items.executemany(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents) "
                "VALUES (%s, %s, %s, %s)",
                [(order[0], pid, qty, price) for pid, qty, price in priced],
            )
        return order[0], total

    return await with_transaction(pool, work, retries=3)


async def main() -> None:
    # autocommit=True: no hidden transaction; every transaction is an explicit transaction() block.
    async with AsyncConnectionPool("postgresql://app_rw:dev@localhost:5432/shop", open=False,
                                   max_size=10, kwargs={"autocommit": True}) as pool:
        print(await place_order(pool, 7, [(2, 1), (1, 2)]))


if __name__ == "__main__":
    asyncio.run(main())
```

**Differences worth noticing:**

- **Where the connection is pinned.** In Node, the transaction *is* the `PoolClient`; forget to pass it and the statement runs elsewhere. In psycopg, the `conn` object from `pool.connection()` is the only thing `fn` receives, so the mistake is harder to make — but a repository that grabs its own `pool.connection()` inside `fn` reproduces it.
- **Concurrency on one connection.** `Promise.all([client.query(a), client.query(b)])` in `pg` simply queues the two queries; there is no parallelism inside a transaction. psycopg's async connection also serialises operations with an internal lock. asyncpg instead raises `InterfaceError: another operation is in progress`. Run transaction statements one after another.
- **Error types.** `pg` gives you a `code` string to compare; psycopg maps each SQLSTATE to an exception class (`errors.SerializationFailure`), so retry policy is an `except` clause.

---

## 5. Production Concerns

- **Pool starvation from long transactions.** With a 10-connection pool, ten requests each holding a transaction across a 2-second external call block every other query in that process, including health checks. Measure "time from `BEGIN` to `COMMIT`" per use case, not only query time; the gap between them is the cost of work done inside the transaction that is not SQL.
- **`idle in transaction` sessions.** They usually mean a code path that forgot to commit (psycopg's implicit transaction), an exception path that skipped `ROLLBACK`, or a `pg` client that was never released. Alert on `count(*) FROM pg_stat_activity WHERE state LIKE 'idle in transaction%'` and on the age of the oldest `xact_start`. Keep `idle_in_transaction_session_timeout` set so a leak cannot pin `VACUUM` for hours.
- **Releasing broken clients.** If `ROLLBACK` itself fails (connection reset, server restart), the connection's state is unknown. Release it with `client.release(true)` in `pg` so the pool destroys it instead of handing an aborted session to the next request. psycopg's pool checks returned connections and discards broken ones.
- **Retry observability.** Log each retry with the SQLSTATE and the attempt number, and count them per use case. A rising `40P01` rate means lock order is inconsistent somewhere ([Deadlocks](31-Deadlocks.md)); a rising `40001` rate under `SERIALIZABLE` means the transaction reads too much or contention grew. Retries that exhaust their budget should surface as `503`/`409`, not as a generic `500`.
- **Poolers.** With PgBouncer in transaction mode, each transaction gets a server connection for its duration, which is fine — but session state (`SET`, advisory session locks, session-level prepared statements in older setups) does not survive between transactions. Use `SET LOCAL` / `set_config(..., true)` inside the transaction.
- **Many savepoints.** Each savepoint that writes data creates a subtransaction. Loops that open a savepoint per row (common in ORMs' "nested transaction" per item) can generate thousands of them in one transaction, which costs memory and has caused performance problems on busy PostgreSQL servers. Prefer `INSERT … ON CONFLICT` or validating rows before the transaction.
- **Batch jobs.** A job that updates 10 million rows in one transaction holds locks on all of them and generates dead tuples `VACUUM` cannot clean until the end. Commit in batches of a few thousand rows, each its own short transaction, and make the job resumable.

---

## 6. Common Mistakes

- **`pool.query("BEGIN")` in node-postgres** — statements spread across connections, so nothing is atomic and a connection is left `idle in transaction` — `pool.connect()` once and pass that client to every call inside the transaction.
- **Calling a payment API or sending email inside the transaction** — locks and a pooled connection are held for the whole network wait, and a rollback cannot undo the side effect — commit first, then call out, or write an outbox row and let a worker do it.
- **Retrying the failed statement instead of the transaction** — PostgreSQL answers `25P02` for anything after an error, and the earlier reads are stale anyway — roll back and re-run the whole transaction function.
- **Retrying every error** — unique and check violations fail identically every time; timeouts get worse under retry — retry only `40001` and `40P01`, with a bound and jitter.
- **Swallowing an error and then committing** — `COMMIT` on an aborted transaction returns `ROLLBACK` without throwing, so the code reports success for lost work — let errors propagate to the helper, or use a savepoint if you really want to continue.
- **`forEach(async …)` for statements inside a transaction (Node)** — the callback promises are not awaited, failures become unhandled rejections, and `COMMIT` runs in an unknown state — use a `for…of` loop with `await`, or a single set-based statement.
- **psycopg connection used without commit** — the first `SELECT` opens a transaction that never ends, holding back `VACUUM` — use `with conn.transaction():`, or `autocommit=True` for read-only scripts.

---

## 7. Comparison Table

| | Single autocommit statement | Explicit transaction | Savepoint inside a transaction | Saga / outbox across services |
|---|---|---|---|---|
| Atomic across | One statement (all its rows) | Many statements, one database | Part of one transaction | Many services, eventually |
| Rollback | Automatic on error | `ROLLBACK`, or error + rollback | `ROLLBACK TO SAVEPOINT` | Compensating actions you write |
| Connection held | For one statement | From `BEGIN` to `COMMIT` | Same as the outer transaction | Only during each local step |
| Typical use | `UPDATE … SET available = available - $2 WHERE … AND available >= $2` | Order + items + stock in one unit | Optional step that may fail | Order service + payment service |
| Main risk | Invariant needs more than one statement | Too long, wrong connection, wrong retry | Subtransaction overhead in loops | Intermediate states are visible |

If one statement can express the invariant (a conditional `UPDATE`, `INSERT … ON CONFLICT`, a CTE that writes two tables), prefer it — it is already atomic and needs no client-side transaction. Cross-service atomicity is a different problem: see [Distributed Transactions](../Module-07-Advanced-Backend-and-System-Design/29-Distributed-Transactions.md).

---

## 8. Interview Questions

**[Junior] What happens if you run two `UPDATE`s without `BEGIN`?**
Each runs in its own implicit transaction and commits as soon as it finishes. If the second fails or the process crashes between them, the first is already permanent. To make them all-or-nothing, wrap them in `BEGIN` … `COMMIT` on the same connection.

**[Junior] What happens in PostgreSQL after a statement inside a transaction fails?**
The transaction enters the aborted state. Every following statement fails with `25P02 current transaction is aborted` until you send `ROLLBACK`, or `ROLLBACK TO SAVEPOINT` if you set one before the failing statement. A `COMMIT` at that point ends the transaction as a rollback.

**[Mid] Why is `pool.query("BEGIN")` wrong in node-postgres?**
A pool sends each `query()` to whichever connection is free, and a transaction exists only on the connection that ran `BEGIN`. The following statements may run on other connections in autocommit mode, so they are not atomic, and the connection that ran `BEGIN` stays `idle in transaction`. You must `pool.connect()`, run `BEGIN`, every statement and `COMMIT`/`ROLLBACK` on that client, then `release()` it.

**[Mid] What are savepoints for?**
They let you undo part of a transaction. `SAVEPOINT x` marks a point; `ROLLBACK TO SAVEPOINT x` discards work after it and clears the aborted state, so the transaction can continue and commit. They suit optional steps — add a gift if stock remains — and are what drivers use for nested transaction blocks. They are not durable on their own: everything still depends on the outer `COMMIT`.

**[Mid] Which errors should a transaction helper retry?**
`40001` serialization failures and `40P01` deadlocks, because they mean "you lost a race; running again may succeed". Constraint violations fail the same way every time, so they become business errors. Timeouts usually signal overload, and retrying adds load. Retries should be bounded (two or three) with jittered backoff, and they must re-run the whole transaction from `BEGIN`.

**[Senior] Your checkout transaction calls a payment provider in the middle. What goes wrong, and how do you restructure it?**
The transaction holds stock-row locks and a pooled connection for the duration of the HTTP call, so a slow provider serialises all buyers of that product and can exhaust the pool for the whole service. If the transaction later rolls back, the card is still charged; if the call times out, you do not know the charge result. I would commit the order as `pending` with the stock reserved, call the provider afterwards with an idempotency key, then mark the order `paid` or release the stock in a second short transaction — or write a `payment.requested` outbox row and let a worker charge. A sweeper handles orders stuck in `pending`.

**[Senior] How do you make retried transactions safe?**
Retry the whole function, so every read and computation happens again in the new snapshot. Keep side effects out: anything outside the database runs after commit or via an outbox. Generate IDs inside the attempt or in the database. The hard case is an ambiguous commit — the connection drops after `COMMIT` is sent. There I only retry if the transaction is idempotent, typically by inserting a client-supplied idempotency key under a `UNIQUE` constraint, so a second run detects the first one.

**[Senior] Production has many `idle in transaction` sessions and growing table bloat. How do you investigate and fix it?**
I query `pg_stat_activity` for sessions in `idle in transaction`, sorted by `xact_start`, and look at `application_name`, client address and the last statement to find the code path. Common causes are psycopg's implicit transaction never committed, an error path that skips `ROLLBACK`, a `pg` client never released, or a network call inside the transaction. The old snapshot those sessions hold prevents `VACUUM` from removing dead rows anywhere, which explains the bloat. I fix the code path, set `idle_in_transaction_session_timeout` on the application role as a guard, and alert on the oldest transaction age.

---

## 9. Cheat Sheet

```text
Statements      BEGIN | COMMIT | ROLLBACK | SAVEPOINT s | ROLLBACK TO SAVEPOINT s | RELEASE SAVEPOINT s
Autocommit      no BEGIN → each statement is its own transaction
Drivers         pg, asyncpg: autocommit | psycopg 3: implicit BEGIN on first statement | SQLAlchemy: autobegin
Node rule       client = await pool.connect(); every statement on client; release(brokenFlag)
After an error  25P02 until ROLLBACK; COMMIT of a failed tx silently rolls back
Scope           smallest all-or-nothing set of writes + the reads they depend on
Never inside    HTTP calls, email, broker publishes, slow CPU work, user think-time
Timeouts        statement_timeout 57014 | lock_timeout 55P03 | idle_in_transaction_session_timeout (kills session)
                transaction_timeout (PG 17+); use SET LOCAL / set_config(..., true) on pooled connections
Retry           only 40001 + 40P01; whole transaction; 2–3 attempts; exponential backoff + full jitter
Not retried     23505/23514/23503 constraint errors, timeouts, ambiguous COMMIT (unless idempotent)
Retry-safe body recompute from fresh reads; no external side effects; IDs generated per attempt
Lock order      sort rows (e.g. by product_id) before updating several → fewer deadlocks
Watch           pg_stat_activity state = 'idle in transaction', oldest xact_start, retry counts by SQLSTATE
```

---

## Related Topics

- [ACID](28-ACID.md) — what the database guarantees once you commit, and how PostgreSQL implements it
- [Isolation Levels](29-Isolation-Levels.md) — what concurrent transactions see, and where `40001` comes from
- [Deadlocks](31-Deadlocks.md) — why `40P01` happens and how lock ordering prevents it
- [Service Layer Pattern](../Module-02-Core-Backend/13-Service-Layer-Pattern.md) — where the transaction boundary lives in application code
- [Idempotency](../Module-07-Advanced-Backend-and-System-Design/32-Idempotency.md) — making retried and replayed requests safe
- [Distributed Transactions](../Module-07-Advanced-Backend-and-System-Design/29-Distributed-Transactions.md) — when one database transaction is not enough

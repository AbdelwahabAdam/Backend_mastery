# Refresh Tokens

> **Module 02 · Core Backend** · Prerequisites: [JWT Authentication](08-JWT-Authentication.md) · Next: [Password Hashing](10-Password-Hashing.md)

---

## ⏱ If You Only Have 2 Minutes

- Two tokens, two jobs: a **short-lived access token** (5–15 min, sent on every API call) and a **long-lived refresh token** (days to weeks, sent only to `/auth/refresh`). The refresh token is the real login session.
- Make the refresh token **opaque** (32 random bytes) and store only its **SHA-256 hash** in the database. A fast hash is fine here because the token has 256 bits of entropy — nobody can brute-force it.
- **Rotate on every use:** each refresh returns a new refresh token and marks the old one as used.
- **Reuse detection:** if an already-used token comes back, someone has a copy. Revoke the **whole token family** (the login session) and force a new login.
- Two lifetimes: a **sliding** idle timeout (each refresh extends it) and an **absolute** cap counted from login (never extended).
- In a browser, keep it in an `HttpOnly; Secure; SameSite` cookie with `Path=/auth/refresh`, so it is never readable by JavaScript and never sent to other endpoints.
- Two tabs refreshing at once look exactly like theft. Handle it with client-side single-flight and a short server **grace window** (seconds, not minutes).
- Logout revokes the family. Password change and "log out everywhere" revoke every family of that user.

---

## 1. What It Is and Why It Exists

A **refresh token** is a credential whose only purpose is to get new access tokens. The client never sends it to your business APIs. It sends it to one endpoint, the token endpoint, when its access token has expired ([RFC 6749 §1.5](https://www.rfc-editor.org/rfc/rfc6749#section-1.5)).

**Analogy:** a hotel gives you a key card that stops working every night, plus a booking reference you keep in your wallet. Each morning you show the booking reference at the front desk and get a fresh card. If the card is stolen, it is useless by tonight. The booking reference is the valuable thing, so you only ever show it to the front desk — and the desk can cancel it.

**The problem it solves.** [JWT access tokens](08-JWT-Authentication.md) are cheap to verify but hard to revoke. If they live for a week, a stolen token works for a week and "logout" means nothing. If they live for 10 minutes, users have to log in again every 10 minutes. Refresh tokens break this trade-off:

- The **access token** is short-lived and stateless. Fast to check, small damage if stolen.
- The **refresh token** is long-lived and **stateful**. Every use hits your database, so you can revoke it, rotate it and spot theft.

So you check state once every 10 minutes per client, instead of on every request.

---

## 2. How It Works

### Lifecycle

1. **Login.** After the password (and MFA) check, the server creates a **refresh session** row (the "token family") and a first refresh token. It returns an access token in the body and the refresh token in a cookie.
2. **Normal calls.** The client sends `Authorization: Bearer <access token>` to APIs. The refresh token stays in its cookie.
3. **Access token expires.** The API returns `401` with `token_expired`. The client calls `POST /auth/refresh`.
4. **Rotation.** The server hashes the presented token, finds the row, checks it is unused, unexpired and its family is not revoked. It marks the row `used_at = now()`, inserts a new token in the same family, and returns a new access token plus the new refresh token.
5. **Reuse.** If a token that is already `used_at` is presented again (outside the grace window), the server revokes the family. Both the thief's copy and the legitimate user's current token stop working.
6. **Logout.** The server sets `revoked_at` on the family and clears the cookie.

### Why rotation catches theft

Without rotation, a stolen refresh token works silently until it expires. With rotation, the attacker and the real user hold the **same** token. Whoever uses it second presents an already-used token — and that trips the alarm.

```mermaid
sequenceDiagram
    participant U as Real user
    participant X as Attacker
    participant S as Auth server
    Note over U,X: Both hold refresh token RT1 (stolen)
    X->>S: POST /auth/refresh (RT1)
    S->>S: RT1 unused → mark used, issue RT2
    S-->>X: access token + RT2
    U->>S: POST /auth/refresh (RT1)
    S->>S: RT1 already used → reuse detected
    S->>S: revoke whole family (RT2 dies too)
    S-->>U: 401 refresh_token_reused
    X->>S: POST /auth/refresh (RT2)
    S-->>X: 401 (family revoked)
    Note over U: User logs in again; attacker is out
```

The order does not matter. If the real user refreshes first, the attacker is the one who presents a used token. Either way the family dies. Rotation does not *prevent* theft; it **limits it to one refresh cycle** and makes it visible.

---

## 3. Key Concepts

### Opaque token, hashed at rest

A refresh token does not need to be a JWT. Nobody except the auth server reads it, and the server always does a database lookup anyway. Use 32 bytes from a CSPRNG (`crypto.randomBytes`, `secrets.token_urlsafe`), encoded as base64url.

Store `SHA-256(token)`, never the token. If the table leaks through a backup or SQL injection, the attacker gets hashes they cannot use. Why not Argon2 like passwords? Passwords are slow-hashed because humans pick guessable ones. A 256-bit random token cannot be guessed, so a fast hash is enough — and a fast, deterministic hash lets you look the row up by a unique index. A salted slow hash would make lookup impossible.

### Token family

A **family** is the chain of refresh tokens that descend from one login: RT1 → RT2 → RT3. It maps to one device or browser session. Revoking the family is how you end that login. In the schema below, the family is a `refresh_sessions` row and each token points to it. This also gives users a "where you're logged in" page: one row per device, with a user agent and creation time.

### Absolute vs sliding lifetime

| Lifetime | Counts from | Extended on refresh? | Typical value | Purpose |
|---|---|---|---|---|
| Access token | Issue time | No (new token instead) | 5–15 min | Limits damage of a stolen access token |
| Sliding (idle) | Last refresh | Yes | 7–30 days | Logs out devices that stop being used |
| Absolute | Login | Never | 30–90 days | Forces re-authentication even for active sessions |

Each new refresh token expires at `min(now + idle, absolute cap)`. Without the absolute cap, a thief who refreshes regularly could keep a stolen session alive forever. These values are product decisions, not standards — a banking app may use 15 min idle and 12 h absolute.

### Where the client keeps it

| Client | Storage | Notes |
|---|---|---|
| Browser SPA, same site as API | `HttpOnly; Secure; SameSite=Strict` cookie, `Path=/auth/refresh` | JavaScript cannot read it; the browser sends it only to the refresh endpoint |
| Mobile app | iOS Keychain / Android Keystore-backed storage | Never in plain shared preferences or logs |
| Server-side web app | Server session, not the browser | The browser only gets a session cookie ([chapter 07](07-Sessions-and-Cookies.md)) |

Use the `__Secure-` cookie name prefix to require the `Secure` flag. You cannot use the stricter `__Host-` prefix here, because `__Host-` requires `Path=/`, and the point is to scope the cookie to the refresh path.

Avoid `localStorage`: any XSS payload can read it and send the long-lived credential to the attacker.

### Concurrent refresh and the grace window

Two tabs (or two parallel API calls in a mobile app) both see a `401` and both call `/auth/refresh` with the same token. The first rotates it. The second presents an already-used token — which looks exactly like theft, so the user gets logged out for no reason.

Fixes, best first:

1. **Single-flight on the client.** Only one refresh in flight at a time; other callers wait for its result. Across browser tabs, use the Web Locks API or a `BroadcastChannel`.
2. **Atomic claim on the server.** `UPDATE … SET used_at = now() WHERE token_hash = $1 AND used_at IS NULL` lets exactly one request win, even under true concurrency. Never "SELECT, check in code, then UPDATE".
3. **Grace window.** If a token is reused within a few seconds of rotation, do **not** revoke. Return `409` and let the client retry — in a browser, the winning response has already put the new token in the shared cookie jar.

The grace window is a trade-off: an attacker who replays a token within those seconds is not detected. Keep it short (around 10 s).

### Revocation triggers

| Event | Action |
|---|---|
| Logout | Revoke this family; clear the cookie |
| Reuse detected | Revoke this family; log a security event; optionally notify the user |
| Password change or reset | Revoke **all** families of the user (optionally keep the current one) |
| "Log out everywhere" / account compromise | Revoke all families **and** set the user's `tokens_valid_after` so live access tokens die too ([JWT revocation](08-JWT-Authentication.md)) |

Revoking a refresh token does not kill access tokens already issued. They keep working until `exp`. That gap — at most one access-token TTL — is the price of stateless access tokens.

---

## 4. Code Examples

Scenario: `POST /auth/refresh` reads the refresh token from a cookie, rotates it with an atomic claim, detects reuse, honours a 10-second grace window, and returns a new access token. Both versions share this PostgreSQL schema:

```sql
-- One row per login = one token family.
CREATE TABLE refresh_sessions (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at          timestamptz NOT NULL DEFAULT now(),
  absolute_expires_at timestamptz NOT NULL,       -- login time + 30 days; never extended
  revoked_at          timestamptz,
  revoke_reason       text,                       -- 'logout' | 'reuse' | 'password_change'
  user_agent          text
);
CREATE INDEX refresh_sessions_active_user_idx ON refresh_sessions (user_id) WHERE revoked_at IS NULL;

CREATE TABLE refresh_tokens (
  token_hash  bytea PRIMARY KEY,                  -- SHA-256 of the token, never the token
  session_id  uuid NOT NULL REFERENCES refresh_sessions(id) ON DELETE CASCADE,
  issued_at   timestamptz NOT NULL DEFAULT now(),
  expires_at  timestamptz NOT NULL,               -- sliding: min(now() + 14 days, absolute cap)
  used_at     timestamptz                         -- set on rotation; a second use is reuse
);
CREATE INDEX refresh_tokens_session_idx ON refresh_tokens (session_id);
```

### Node.js / TypeScript

```ts
// npm i express cookie-parser pg   — Node.js 22+, TypeScript 5, ESM
import express, { type Request, type Response } from "express";
import cookieParser from "cookie-parser";
import { createHash, randomBytes } from "node:crypto";
import pg from "pg";
import { issueAccessToken } from "./tokens.js"; // signs a 10-min JWT (see the JWT chapter)

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const COOKIE = "__Secure-rt";
const COOKIE_OPTS = { httpOnly: true, secure: true, sameSite: "strict", path: "/auth/refresh" } as const;
const sha256 = (token: string): Buffer => createHash("sha256").update(token).digest();

const CLAIM_SQL = `
  UPDATE refresh_tokens t SET used_at = now()
    FROM refresh_sessions s
   WHERE t.token_hash = $1 AND t.used_at IS NULL AND t.expires_at > now()
     AND s.id = t.session_id AND s.revoked_at IS NULL AND s.absolute_expires_at > now()
  RETURNING s.id AS session_id, s.user_id, s.absolute_expires_at`;

const app = express();
app.use(cookieParser());

app.post("/auth/refresh", async (req: Request, res: Response) => {
  const presented: unknown = req.cookies?.[COOKIE];
  if (typeof presented !== "string") {
    res.status(401).json({ error: "missing_refresh_token" });
    return;
  }
  const hash = sha256(presented);
  const db = await pool.connect();
  try {
    await db.query("BEGIN");
    // Atomic claim: only one concurrent request can flip used_at from NULL.
    const claim = await db.query(CLAIM_SQL, [hash]);
    if (claim.rowCount === 0) {
      // reused: true = used long ago (theft), false = used seconds ago (racing tab), null = never used.
      const old = await db.query(
        `SELECT session_id, used_at < now() - interval '10 seconds' AS reused
           FROM refresh_tokens WHERE token_hash = $1`, [hash]);
      const row = old.rows[0] as { session_id: string; reused: boolean | null } | undefined;
      if (row?.reused === true) {
        await db.query(
          `UPDATE refresh_sessions SET revoked_at = now(), revoke_reason = 'reuse'
            WHERE id = $1 AND revoked_at IS NULL`, [row.session_id]);
        await db.query("COMMIT");
        console.warn({ event: "refresh_token_reuse", sessionId: row.session_id }); // never log the token
        res.clearCookie(COOKIE, COOKIE_OPTS).status(401).json({ error: "refresh_token_reused" });
        return;
      }
      await db.query("ROLLBACK");
      if (row?.reused === false) {
        res.status(409).json({ error: "refresh_in_progress" }); // client retries with the new cookie
        return;
      }
      res.clearCookie(COOKIE, COOKIE_OPTS).status(401).json({ error: "invalid_refresh_token" });
      return;
    }
    const { session_id, user_id } = claim.rows[0] as { session_id: string; user_id: string };
    const next = randomBytes(32).toString("base64url");
    await db.query(
      `INSERT INTO refresh_tokens (token_hash, session_id, expires_at)
       SELECT $1, id, LEAST(now() + interval '14 days', absolute_expires_at)
         FROM refresh_sessions WHERE id = $2`, [sha256(next), session_id]);
    const accessToken = await issueAccessToken(user_id); // sign before COMMIT so a failure rolls back
    await db.query("COMMIT");
    res.cookie(COOKIE, next, { ...COOKIE_OPTS, maxAge: 14 * 24 * 3600 * 1000 });
    res.json({ access_token: accessToken, token_type: "Bearer", expires_in: 600 });
  } catch (err) {
    await db.query("ROLLBACK");
    throw err; // Express 5 forwards rejected promises to the error handler
  } finally {
    db.release();
  }
});
```

### Python

```python
# pip install fastapi asyncpg   — Python 3.12+
import hashlib
import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated

import asyncpg
from fastapi import Cookie, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from tokens import issue_access_token  # signs a 10-min JWT (see the JWT chapter)

COOKIE = "__Secure-rt"
COOKIE_OPTS = {"path": "/auth/refresh", "secure": True, "httponly": True, "samesite": "strict"}
CLAIM_SQL = """
  UPDATE refresh_tokens t SET used_at = now()
    FROM refresh_sessions s
   WHERE t.token_hash = $1 AND t.used_at IS NULL AND t.expires_at > now()
     AND s.id = t.session_id AND s.revoked_at IS NULL AND s.absolute_expires_at > now()
  RETURNING s.id AS session_id, s.user_id"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


def error(status: int, code: str, clear_cookie: bool = False) -> JSONResponse:
    # Return a response instead of raising HTTPException: headers set on the injected
    # `Response` are discarded when an exception is raised, so the cookie would not be cleared.
    resp = JSONResponse({"error": code}, status_code=status)
    if clear_cookie:
        resp.delete_cookie(COOKIE, **COOKIE_OPTS)
    return resp


@app.post("/auth/refresh")
async def refresh(request: Request, response: Response,
                  rt: Annotated[str | None, Cookie(alias=COOKIE)] = None):
    if rt is None:
        return error(401, "missing_refresh_token")
    token_hash = hashlib.sha256(rt.encode()).digest()
    next_token = secrets.token_urlsafe(32)
    async with request.app.state.pool.acquire() as conn, conn.transaction():
        claim = await conn.fetchrow(CLAIM_SQL, token_hash)  # atomic: one racer wins
        if claim is None:
            old = await conn.fetchrow(
                "SELECT session_id, used_at < now() - interval '10 seconds' AS reused "
                "FROM refresh_tokens WHERE token_hash = $1", token_hash)
            reused = None if old is None else old["reused"]
            if reused:  # rotated long ago and back again: a copy exists elsewhere
                await conn.execute(
                    "UPDATE refresh_sessions SET revoked_at = now(), revoke_reason = 'reuse' "
                    "WHERE id = $1 AND revoked_at IS NULL", old["session_id"])
        else:
            await conn.execute(
                "INSERT INTO refresh_tokens (token_hash, session_id, expires_at) "
                "SELECT $1, id, LEAST(now() + interval '14 days', absolute_expires_at) "
                "FROM refresh_sessions WHERE id = $2",
                hashlib.sha256(next_token.encode()).digest(), claim["session_id"])
    # The transaction has committed here, so the family revocation is durable.
    if claim is None:
        if reused:
            return error(401, "refresh_token_reused", clear_cookie=True)
        if reused is False:
            return error(409, "refresh_in_progress")  # racing tab; retry with the new cookie
        return error(401, "invalid_refresh_token", clear_cookie=True)
    response.set_cookie(COOKIE, next_token, max_age=14 * 24 * 3600, **COOKIE_OPTS)
    return {"access_token": issue_access_token(str(claim["user_id"])),
            "token_type": "Bearer", "expires_in": 600}
```

**Runtime differences to notice:**
- In Express the transaction is manual (`BEGIN` / `COMMIT` / `ROLLBACK` on a checked-out client). In asyncpg, `conn.transaction()` commits when the block exits normally and rolls back if it raises — so the Python version decides the HTTP outcome *after* the block, to make sure the revocation is committed.
- FastAPI drops headers set on the injected `Response` when you raise `HTTPException`. That is why the Python code returns a `JSONResponse` for errors that must clear the cookie.

---

## 5. Production Concerns

- **CSRF on the refresh endpoint.** The cookie is sent automatically, so a cross-site page could trigger a refresh. It cannot read the response (CORS blocks it), but it could cause rotations and confuse your reuse detector. `SameSite=Strict` plus requiring a custom header (e.g. `X-Requested-With`) or a JSON body closes this. See [Sessions and Cookies](07-Sessions-and-Cookies.md).
- **Table growth.** Every refresh inserts a row. With 10-minute access tokens, an active user creates ~6 rows per hour. Run a daily job that deletes tokens and sessions past their absolute expiry. Keep used rows until then — you need them for reuse detection.
- **Metrics.** Count refreshes by outcome: `rotated`, `grace_409`, `reuse_revoked`, `invalid`, `expired`. A few reuse events per day can be client bugs. A sudden spike from many accounts suggests token theft (e.g. a malicious browser extension) or a broken client release that refreshes in parallel.
- **Security events.** On reuse, log `user_id`, `session_id`, IP and user agent of both the original and reused request. Never log the token or its hash in plain application logs.
- **Load.** The refresh endpoint is the only stateful hop in a JWT setup. Its rate is roughly `active clients / access-token TTL`. Shortening the TTL from 15 to 5 minutes triples database writes on this table.
- **Mobile and third-party clients.** Public clients cannot keep a client secret. The OAuth 2.0 Security BCP ([RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)) says refresh tokens for public clients must be either sender-constrained (bound to a key, e.g. DPoP) or rotated with reuse detection — this chapter's design is the second option.
- **Revocation latency.** After you revoke a family, the attacker keeps their current access token until it expires. If that matters (admin accounts, payments), add a `tokens_valid_after` check on those routes.

---

## 6. Common Mistakes

- **Storing refresh tokens in plaintext** — a database leak becomes thousands of live sessions — store `SHA-256(token)` and compare by hash.
- **Rotation without reuse detection** — you issue new tokens but silently reject old ones, so a thief who refreshes first keeps the session forever — treat a used token as a theft signal and revoke the family.
- **Check-then-update in application code** — two concurrent requests both read "unused" and both get new tokens, forking the family — claim the row with a single conditional `UPDATE … WHERE used_at IS NULL`.
- **Only a sliding expiry** — an attacker who refreshes regularly keeps a stolen session alive indefinitely — add an absolute cap counted from login.
- **Refresh token in `localStorage` or cookie with `Path=/`** — readable by XSS, or sent on every request and exposed in more logs and proxies — `HttpOnly` cookie scoped to `/auth/refresh`.
- **Logging users out on every parallel refresh** — tabs race and trip reuse detection — client single-flight plus a short grace window.
- **Not revoking on password change** — the user changes their password after a compromise, but the attacker's refresh token still works — revoke all of the user's families in the same transaction as the password update.

---

## 7. Comparison Table

| | Long-lived access token only | Short access + refresh (no rotation) | Short access + rotating refresh | Server session cookie |
|---|---|---|---|---|
| Damage from stolen access credential | Days | Minutes | Minutes | Until revoked or idle timeout |
| Damage from stolen long-lived credential | — | Until refresh token expires | One refresh cycle, then detected | Until revoked |
| Revocation | Not possible without a denylist | Revoke refresh token; access token lives to `exp` | Same, plus automatic on reuse | Instant |
| Database hits | None | One per refresh | One write per refresh | One per request |
| Client complexity | Lowest | Retry on `401` | Retry on `401` + single-flight | Lowest (browser handles cookie) |
| Good fit | Never for user logins | Confidential server-side clients | SPAs, mobile apps | Single web app with one backend |

---

## 8. Interview Questions

**[Junior] Why not just make the access token last 30 days?**
Because a JWT access token cannot be revoked before `exp` without adding state. A stolen 30-day token gives an attacker 30 days of access, and logout does nothing. With a 10-minute access token, theft is short-lived, and the long-lived part (the refresh token) is checked against the database on every use, so it can be revoked.

**[Junior] Why hash refresh tokens with SHA-256 and not Argon2?**
Slow hashes exist to protect low-entropy, human-chosen passwords from guessing. A refresh token has 256 random bits, so guessing is impossible and a fast hash gives the same protection. A deterministic, unsalted hash also lets you find the row with a unique index; a salted slow hash would force you to scan and verify every row.

**[Mid] What is refresh-token rotation and what does it buy you?**
Every refresh returns a new refresh token and marks the old one used. The legitimate user and a thief cannot both keep using the same token: whoever presents it second is presenting a used token. The server treats that as theft and revokes the whole family. So theft is limited to one refresh cycle and becomes visible in your logs.

**[Mid] How do you implement "log out of all devices"?**
Set `revoked_at` on every `refresh_sessions` row for that user, so no device can get a new access token. Access tokens already issued remain valid until they expire. If that is not acceptable, store a per-user `tokens_valid_after` timestamp and reject access tokens whose `iat` is older, at least on sensitive routes.

**[Mid] Why scope the refresh cookie to `/auth/refresh`?**
So the browser only sends it to the one endpoint that needs it. It does not appear on every API request, in every access log, or at every downstream service. Combined with `HttpOnly`, it also cannot be read by JavaScript, so an XSS bug cannot exfiltrate it (although XSS can still call the API while the page is open).

**[Senior] Two tabs refresh at the same time and users get randomly logged out. Diagnose and fix.**
Both tabs send the same refresh token. One rotates it; the other presents a used token, which trips reuse detection and revokes the family. First confirm it with metrics: reuse events clustered within a second of a rotation. Fix it on the client with single-flight (Web Locks or BroadcastChannel across tabs). On the server, claim tokens with an atomic conditional `UPDATE`, and allow a short grace window (around 10 s) in which reuse returns `409` instead of revoking. Accept that a replay inside that window is not detected, and keep it short.

**[Senior] Design the storage for refresh tokens. What would you put in the table and why?**
A `refresh_sessions` table for families: user ID, created time, absolute expiry, revoked time and reason, device metadata. It supports logout, "where you're logged in" pages and family revocation with one update. A `refresh_tokens` table keyed by `SHA-256(token)`, with session ID, sliding expiry and `used_at`. Used rows are kept until the family expires, because they are what makes reuse detection work. A cleanup job deletes expired families, and an index on active sessions per user makes "revoke all" cheap.

**[Senior] Would you use refresh tokens for a classic server-rendered web app?**
Usually not. If one backend serves HTML and handles every request, a server-side session in an opaque cookie gives instant revocation with less machinery. Refresh tokens pay off when access tokens are stateless JWTs verified by many services, or when the client is a mobile app or SPA talking to separate APIs. Adding refresh tokens to a monolith just adds a second credential to protect.

---

## 9. Cheat Sheet

```text
Roles          access token: 5–15 min, every API call | refresh token: days–weeks, /auth/refresh only
Format         32 random bytes, base64url, opaque (not a JWT)
Storage (DB)   SHA-256(token) + session_id + expires_at + used_at; family row with absolute expiry
Rotation       atomic UPDATE ... SET used_at = now() WHERE hash = $1 AND used_at IS NULL
Reuse          used token returns (outside grace) → revoke family → 401 → user logs in again
Grace window   ~10 s → 409, client retries; never minutes
Lifetimes      new expiry = min(now + idle, absolute cap from login)
Browser        HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; __Secure- prefix (not __Host-)
Mobile         Keychain / Keystore; public clients need rotation or sender-constraining (RFC 9700)
Revoke         logout → family | password change → all families | compromise → + tokens_valid_after
Gap            revoking refresh does not kill live access tokens; they die at exp
Never          plaintext tokens in DB, tokens in logs, localStorage, check-then-update races
```

---

## Related Topics

- [JWT Authentication](08-JWT-Authentication.md) — the short-lived access token that refresh tokens renew
- [Sessions and Cookies](07-Sessions-and-Cookies.md) — cookie flags, CSRF, and the stateful alternative
- [Authentication Flow](11-Authentication-Flow.md) — where login creates the family and password reset revokes it
- [Race Conditions](../Module-04-Operating-Systems/13-Race-Conditions.md) — the check-then-act bug behind concurrent refreshes
- [Transactions](../Module-03-Databases/27-Transactions.md) — why the claim and the new token insert must commit together

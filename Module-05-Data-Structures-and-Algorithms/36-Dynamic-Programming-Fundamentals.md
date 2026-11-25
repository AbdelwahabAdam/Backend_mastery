# Dynamic Programming Fundamentals

> **Module 05 · Data Structures & Algorithms** · Prerequisites: [Backtracking](35-Backtracking.md) · Next: [Union Find](37-Union-Find.md)

---

## ⏱ If You Only Have 2 Minutes

- **Dynamic programming (DP)** solves a problem by splitting it into smaller subproblems and storing each answer once. It works when subproblems **overlap** and the best answer is built from best answers to smaller parts (**optimal substructure**).
- The recipe: define the **state** (what one cell means), write the **transition** (how a cell depends on earlier cells), set the **base cases**, pick an **order** to fill the cells, and read off the **answer**.
- Go in three steps: plain recursion, then **memoization** (top-down: recursion plus a cache), then **tabulation** (bottom-up: fill a table in order). Tabulation avoids deep recursion.
- Space can often shrink: a 1D DP that reads only the last two cells needs O(1) space, and a 2D DP that reads only the previous row needs one row.
- Naive Fibonacci recursion makes about 1.618ⁿ calls. With a memo, each state is computed once, so the cost is O(n).
- Python: `functools.cache` memoises a function, but the cache is unbounded and keeps arguments alive. TypeScript: a `Map` is the usual memo.
- Backend uses: edit distance for typo-tolerant search and diffing, cost-minimising batch plans, and cached sub-results in query planners.

---

## 1. What It Is and Why It Exists

**Dynamic programming** is a way to solve problems by remembering answers. When a recursive solution keeps asking the same question, DP stores the answer the first time and reuses it. The word "dynamic" is historical; the idea is about tables of answers, not about change over time.

**Analogy:** a tally on a whiteboard. Suppose you are counting paths through a building, and every hallway junction is visited by many routes. Instead of recounting the paths from a junction each time someone arrives, you write the number on the whiteboard at that junction. The next visitor reads the number and moves on. The whiteboard is the memo table.

**The problem it solves.** Plain recursion can repeat the same work an exponential number of times. Climbing `n` stairs one or two at a time has about `1.618ⁿ` recursive calls if you use the direct formula, yet only `n` different subproblems exist. DP turns that gap into an `O(n)` solution. It applies whenever two conditions hold: subproblems **overlap**, and the best answer can be built from the best answers to subproblems.

DP is not the same as divide and conquer. Merge sort splits the array into halves that never overlap, so nothing is reused. DP is useful exactly because the subproblems repeat.

---

## 2. How It Works

### The four-step recipe

1. **State.** Decide what `dp[i]` (or `dp[i][j]`) means in words. For climbing stairs: `ways[i]` is the number of ways to reach step `i`.
2. **Transition.** Write the formula that gets `dp[i]` from smaller states. For stairs: `ways[i] = ways[i-1] + ways[i-2]`.
3. **Base cases.** Fill the cells that have no earlier state. For stairs: `ways[0] = 1` and `ways[1] = 1`.
4. **Order and answer.** Fill cells so each one's inputs are ready, then read the answer from the cell the question asks for.

### Three versions of one solution

Take climbing stairs, where `ways(n)` counts the ways to reach step `n` by taking 1 or 2 steps at a time.

- **Plain recursion:** `ways(n) = ways(n-1) + ways(n-2)`. For `n = 5` this makes 15 calls. In general the call count is `2·F(n+1) − 1`, where `F` is the Fibonacci sequence. It grows exponentially.
- **Memoization (top-down):** the same recursion, but each result is stored in a cache before it is returned. The first call for each `n` does the work, and later calls read the cache. Each `n` from 2 to 5 is computed once.
- **Tabulation (bottom-up):** fill a table from the base cases upward, with no recursion at all.

Trace for `n = 5` with tabulation:

| `i` | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| `ways[i]` | 1 | 1 | 2 | 3 | 5 | 8 |
| computed from | base | base | `1 + 1` | `2 + 1` | `3 + 2` | `5 + 3` |

Memoization computes the same values. The calls go down from `5` to `4`, `3`, `2`, and the values are stored on the way back up.

### Trace: house robber

**House robber (LeetCode 198).** Houses are on a street with values `money[i]`. You may not rob two adjacent houses. Find the maximum total. For `money = [2, 7, 9, 3, 1]`:

- **State:** `best[i]` is the most money you can take from houses `0..i`.
- **Transition:** `best[i] = max(best[i-1], best[i-2] + money[i])`. Either skip house `i`, or rob it and skip `i-1`.
- **Base cases:** `best[0] = money[0]`, and `best[1] = max(money[0], money[1])`.

| `i` | `money[i]` | `best[i]` | Reason |
|---|---|---|---|
| 0 | 2 | 2 | only house 0 |
| 1 | 7 | 7 | 7 beats 2 |
| 2 | 9 | 11 | `best[0] + 9 = 2 + 9` beats `best[1] = 7` |
| 3 | 3 | 11 | `best[1] + 3 = 10` is less than `best[2] = 11` |
| 4 | 1 | 12 | `best[2] + 1 = 12` beats `best[3] = 11` |

The answer is `best[4] = 12` (houses 0, 2 and 4: `2 + 9 + 1`). Only the last two values are ever read, so the table can shrink to two variables.

### Trace: edit distance (2D)

**Edit distance (LeetCode 72).** The fewest single-character insertions, deletions or replacements that turn `a` into `b`. The grid has one row per prefix of `a` and one column per prefix of `b`. For `a = "cat"` and `b = "cut"`:

- **State:** `dp[i][j]` is the edit distance between the first `i` characters of `a` and the first `j` characters of `b`.
- **Transition:** if `a[i-1] = b[j-1]`, then `dp[i][j] = dp[i-1][j-1]`. Otherwise `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`. The three choices are delete, insert and replace.
- **Base cases:** `dp[0][j] = j` and `dp[i][0] = i`.

| `i \ j` | 0 (empty) | 1 `c` | 2 `u` | 3 `t` |
|---|---|---|---|---|
| 0 (empty) | 0 | 1 | 2 | 3 |
| 1 `c` | 1 | 0 | 1 | 2 |
| 2 `a` | 2 | 1 | 1 | 2 |
| 3 `t` | 3 | 2 | 2 | 1 |

The answer is `dp[3][3] = 1`: replace `a` with `u`. Each cell depends on the cell above, the cell to the left and the cell diagonally above-left, so filling row by row works.

---

## 3. Key Concepts

### Overlapping subproblems and optimal substructure

Two checks decide whether DP fits:

- **Overlap:** does the recursion ask the same question more than once? Draw the call tree. If a node repeats, a memo will help.
- **Optimal substructure:** does the best answer to the whole problem come from the best answers to parts? For house robber, the best plan for houses `0..i` is either the best plan for `0..i-1`, or the best plan for `0..i-2` plus house `i`. Both parts are optimal on their own.

If either check fails, DP does not apply. Greedy and backtracking are the other tools in [Greedy Algorithms](34-Greedy-Algorithms.md) and [Backtracking](35-Backtracking.md).

### Top-down versus bottom-up

| Aspect | Memoization (top-down) | Tabulation (bottom-up) |
|---|---|---|
| Shape | Recursive function plus a cache | Loop that fills a table |
| Computes | Only the states needed for the answer | Every state in the table |
| Recursion depth | Grows with `n`, can overflow the stack | None |
| Easier to write from | The recurrence | The base cases and an order |
| Space tuning | Harder | Easy: keep only the rows you read |

Start with the recurrence and memoize it. Convert to tabulation when the depth is large or when you want to shrink the memory.

### Space optimization

A cell is needed only while a later cell still reads it. Climbing stairs reads two previous cells, so two variables are enough. Edit distance reads the previous row, so two rows are enough. Ask "which cells does the next step read?" and keep only those.

### Complexity

| Problem and method | Time best | Time average | Time worst | Extra space | Why |
|---|---|---|---|---|---|
| Stairs, plain recursion | O(1.618ⁿ) | same | same | O(n) stack | Each call makes two more calls; no reuse |
| Stairs, memo | O(n) | O(n) | O(n) | O(n) | Each `n` is computed once; cache and stack each hold O(n) |
| Stairs, tabulation | O(n) | O(n) | O(n) | O(1) rolling | One constant-time step per index |
| House robber | O(n) | O(n) | O(n) | O(1) | One pass; two variables carry the state |
| Edit distance, full grid | O(m · n) | O(m · n) | O(m · n) | O(m · n) | Every cell is computed once |
| Edit distance, two rows | O(m · n) | O(m · n) | O(m · n) | O(min(m, n)) | Same work; swap so the row is the shorter string |

DP has no best or average case that differs from the worst case. Every reachable state is computed, and no bound here is amortized.

---

## 4. Code Examples

Two classic problems, solved in both languages:

1. **House Robber (LeetCode 198), 1D:** the maximum sum of non-adjacent values. *Approach:* keep two running best totals, one ending with the previous house taken and one ending with it skipped. *Complexity:* O(n) time, O(1) space. Climbing stairs (LeetCode 70) is shown in the same block as the memo example.
2. **Edit Distance (LeetCode 72), 2D:** the fewest edits to turn one string into another. *Approach:* fill the grid row by row, keeping only the previous row. *Complexity:* O(m · n) time, O(min(m, n)) space with two rows.

**Built-ins:** Python's `functools.cache` (Python 3.9+) memoises a function with an unbounded cache, and `functools.lru_cache(maxsize=...)` bounds it. Use a bounded cache when arguments come from users. JavaScript has no memoize built-in, so the memo is a `Map` that you write by hand. Note that JavaScript `number` is exact only up to 2^53, while Python `int` has no limit. Climbing stairs passes that limit at `n = 78` (the answer is the Fibonacci number `F(n + 1)`), so use `BigInt` in TypeScript for large `n`.

### Node.js / TypeScript

```ts
// dp-1d.ts: no npm packages. Node.js 22+, TypeScript 5.

/**
 * LeetCode 70: distinct ways to climb n steps taking 1 or 2 at a time. climbStairs(5) → 8.
 * Top-down memo: a Map holds each answer, so every n is computed once.
 */
export function climbStairs(n: number, memo = new Map<number, number>()): number {
  if (!Number.isSafeInteger(n) || n < 0) throw new RangeError(`n must be >= 0, got ${n}`);
  if (n <= 1) return 1;                 // base cases: one way to stand still or reach step 1
  const cached = memo.get(n);
  if (cached !== undefined) return cached;
  const ways = climbStairs(n - 1, memo) + climbStairs(n - 2, memo);
  memo.set(n, ways);
  return ways;
}

/**
 * LeetCode 198: maximum total from non-adjacent houses. houseRobber([2,7,9,3,1]) → 12.
 * Bottom-up with two rolling values: O(n) time, O(1) space.
 */
export function houseRobber(money: readonly number[]): number {
  let take = 0; // best total with the previous house robbed
  let skip = 0; // best total with the previous house skipped
  for (const amount of money) {
    const robNow = skip + amount;      // robbing this house forces the previous one to be skipped
    skip = Math.max(skip, take);       // skipping this house keeps the better earlier total
    take = robNow;
  }
  return Math.max(take, skip);         // empty input gives 0
}
```

```ts
// edit-distance.ts: no npm packages. Node.js 22+, TypeScript 5.

/**
 * LeetCode 72: fewest insertions, deletions and replacements to turn `a` into `b`.
 * Bottom-up over the grid, keeping only the previous row: O(m * n) time, O(n) space.
 * editDistance("horse", "ros") → 3
 */
export function editDistance(a: string, b: string): number {
  // [...s] splits by code point, so a surrogate pair such as an emoji stays one character.
  const x = [...a];
  const y = [...b];
  const n = y.length;

  // Row for i = 0: turning the empty prefix of `a` into the first j characters of `b` takes j inserts.
  let prev = Array.from({ length: n + 1 }, (_, j) => j);
  for (let i = 1; i <= x.length; i++) {
    const curr: number[] = [i]; // column 0: deleting the first i characters of `a`
    for (let j = 1; j <= n; j++) {
      if (x[i - 1] === y[j - 1]) {
        curr[j] = prev[j - 1];          // same character: no edit needed
      } else {
        curr[j] = 1 + Math.min(
          prev[j],                       // delete x[i-1]
          curr[j - 1],                   // insert y[j-1]
          prev[j - 1],                   // replace x[i-1] with y[j-1]
        );
      }
    }
    prev = curr; // the next row only reads this one, so the older rows can be dropped
  }
  return prev[n];
}
```

### Python

```python
# dp_1d.py: standard library only. Python 3.12+.
from collections.abc import Sequence
from functools import cache


@cache  # memoises every argument; unbounded, so fine for trusted n, not for user input
def climb_stairs(n: int) -> int:
    """LeetCode 70: distinct ways to climb n steps taking 1 or 2 at a time. climb_stairs(5) == 8."""
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    if n <= 1:
        return 1                        # base cases
    # Recursion depth grows with n; past about 1,000 the default limit raises RecursionError.
    # Python ints never overflow, so the answer stays exact for any n that fits in the stack.
    return climb_stairs(n - 1) + climb_stairs(n - 2)


def house_robber(money: Sequence[int]) -> int:
    """LeetCode 198: maximum total from non-adjacent houses. house_robber([2, 7, 9, 3, 1]) == 12."""
    take = 0  # best total with the previous house robbed
    skip = 0  # best total with the previous house skipped
    for amount in money:
        # Tuple assignment reads the old values on the right, so both updates use the previous round.
        take, skip = skip + amount, max(skip, take)
    return max(take, skip)  # empty input gives 0
```

```python
# edit_distance.py: standard library only. Python 3.12+.


def edit_distance(a: str, b: str) -> int:
    """LeetCode 72: fewest inserts, deletes and replaces to turn a into b. O(m * n) time."""
    # Indexing a str gives code points, the same unit the TypeScript version uses.
    # Grapheme clusters (such as flag emoji) need a Unicode library, which is out of scope here.
    m, n = len(a), len(b)

    # Row for i = 0: j inserts turn the empty prefix into the first j characters of b.
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i] + [0] * n            # column 0: i deletions
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1]   # same character: no edit needed
            else:
                curr[j] = 1 + min(
                    prev[j],            # delete a[i-1]
                    curr[j - 1],        # insert b[j-1]
                    prev[j - 1],        # replace a[i-1] with b[j-1]
                )
        prev = curr                     # only the previous row is read again
    return prev[n]


# edit_distance("horse", "ros") == 3;  edit_distance("cat", "cut") == 1
```

**Runtime difference to notice:** Python's `@cache` on a recursive function keeps every argument and result alive for the life of the process, and `climb_stairs` recurses once per step. A bottom-up loop is safer for large inputs in both languages. In TypeScript, the `Map` memo is local to one top-level call, so it is freed when the call returns. That is the usual choice for request-scoped work.

---

## 5. Production Concerns

- **Input size is a security boundary.** Edit distance costs O(m · n). Two 100,000-character strings need 10¹⁰ cell updates, which blocks a Node event loop or a Python worker for minutes. Reject long inputs at the API layer, and cap the distance you care about (for example, stop once every value in a row exceeds the limit).
- **Banded computation for typo search.** If you only need to know whether two words are within distance `k`, compute only the diagonal band of width `2k + 1` in each row. This makes the cost O(k · n). Many search systems pre-filter candidates with a trigram index (PostgreSQL's `pg_trgm` extension, for example) and run edit distance only on the survivors.
- **Bounded caches.** A memo keyed on user-supplied arguments grows without limit. Use `lru_cache(maxsize=...)` in Python, or an LRU-bounded `Map` in TypeScript, and expose its hit rate as a metric.
- **Numeric range.** TypeScript `number` loses exactness above 2^53. Climbing stairs crosses that limit at `n = 78`. Use `BigInt` when the answer can get that large, or state the bound in the API contract.
- **Stack depth.** Recursive memo versions fail on deep inputs with a stack overflow in Node or `RecursionError` in Python. Use the bottom-up loop for large `n`.
- **Observability.** Log input length and elapsed time for DP calls, and alert on a rising p99. Growth in input length is usually the first sign that a quadratic step has become a problem.

---

## 6. Common Mistakes

- **Vague state** — the table holds numbers nobody can explain, so the recurrence is wrong — write one sentence defining each cell before writing the formula.
- **Missing or wrong base cases** — `dp[0]` is uninitialised and the answer is off by one — set base cases from the definition, then test `n = 0`, `n = 1` and empty input.
- **Wrong fill order** — the code reads a cell that is not computed yet and gets zero — fill in an order where every input is ready, such as row by row for grids.
- **Unhashable memo keys** — passing a Python `list` to `lru_cache` raises `TypeError` — pass a `tuple` or an index instead.
- **`@cache` on a method** — the cache holds a reference to `self`, so instances are never freed — use a module-level function or a per-instance dictionary you can drop.
- **Answer not at the last cell** — the best answer can sit at any index, for example the maximum subarray — read the cell the question asks for, not `dp[n]` by default.
- **Overflow past 2^53** — large counts become wrong without any error — use `BigInt` in TypeScript.

---

## 7. Comparison Table

| Approach | Reuses subproblem answers? | Typical use | Cost pattern |
|---|---|---|---|
| Dynamic programming | Yes, every state stored once | Counts, minimums, maximums over overlapping choices | Polynomial in the number of states |
| Greedy | No, makes one choice per step | Problems with a safe local choice | O(n log n) with a sort |
| Backtracking | No, explores each branch | Listing every valid solution | Exponential in output size |
| Divide and conquer | No, subproblems do not overlap | Merge sort, binary search | Often O(n log n) |
| Plain recursion | No | Clear code for small inputs | Exponential when subproblems overlap |

If the subproblems overlap and you need a count or an optimum, use DP. If they do not overlap, divide and conquer is the natural choice. If you need every solution, backtracking is the tool.

---

## 8. Interview Questions

**[Junior] What two properties must a problem have before DP is a good fit?**
The subproblems must overlap, so the same question is asked many times. The optimal answer must also be built from optimal answers to smaller parts, which is called optimal substructure. Without overlap, a memo saves nothing. Without optimal substructure, the stored answers cannot be combined correctly.

**[Junior] What is the difference between memoization and tabulation?**
Memoization is recursion plus a cache: each answer is stored the first time it is computed, and only the needed states are visited. Tabulation fills a table from the base cases upward with a loop, so it has no recursion depth problem. Both give the same answers and the same asymptotic time. Tabulation is easier to shrink in space.

**[Mid] Define the state and the transition for house robber.**
The state `best[i]` is the most money you can take from houses `0` through `i`. The transition is `best[i] = max(best[i-1], best[i-2] + money[i])`, which means either skip house `i` or take it and skip house `i-1`. The base cases are `best[0] = money[0]` and `best[1] = max(money[0], money[1])`. Only the last two values are read, so the code keeps two variables.

**[Mid] Why is naive Fibonacci recursion exponential, and what fixes it?**
Each call makes two more calls, and most of them recompute values that were already computed elsewhere in the tree. The call count grows like `1.618ⁿ`. A memo or a bottom-up table computes each value once, which reduces the work to O(n). The fix works because the subproblems overlap, so storing the answers removes the repeated work.

**[Senior] Derive the edit distance recurrence and reduce its space to one row.**
Compare the last characters of the two prefixes. If they match, the distance is the distance of the shorter prefixes. If they differ, take one plus the minimum of deleting, inserting and replacing. Each cell reads the cell above, the cell to the left and the cell diagonally above-left, so filling row by row needs only the previous row. The space falls from O(m · n) to O(n), or O(min(m, n)) if the shorter string is used for the row.

**[Senior] You need typo-tolerant search over a million product names. How would you use edit distance?**
Running edit distance against every name on each query costs far too much. Build a candidate index first, such as a trigram index, so each query checks only names that share some trigrams with the input. Then run a banded edit distance with a small bound `k`, which costs O(k · n) per candidate, and stop early once a row exceeds `k`. Cap the query length, rank the surviving candidates, and track the candidate count per query as a metric.

**[Senior] When does DP stop being practical?**
DP is practical when the number of distinct states is small. If the state must include a subset of `n` items, the state count is `2ⁿ`, and DP gives no benefit over search for large `n`. Sparse states are another case: a hash-map memo stores only the states reached, which can be far fewer than the table size. When the state space is too large, look for a better state definition, a greedy argument, or an approximation with a known error bound.

---

## 9. Cheat Sheet

```text
Use DP when    subproblems overlap AND the optimum builds from optimal parts
Recipe         state -> transition -> base cases -> fill order -> read answer
Memoize        recursion + cache; each state once; risk: stack depth
Tabulate       loop over a table; no recursion; easy to shrink space
Stairs         ways[i] = ways[i-1] + ways[i-2]; O(n) time, O(1) space
House robber   best[i] = max(best[i-1], best[i-2] + money[i]); O(n), O(1)
Edit distance  match: dp[i-1][j-1]; else 1 + min(del, ins, replace); O(m*n)
Two rows       keep only the previous row when the next row reads only that row
Naive stairs   about 1.618^n calls; memo removes the repeats
Python         @functools.cache (unbounded); lru_cache(maxsize=...) for user input
TypeScript     Map-based memo; BigInt for answers past 2^53
Pitfalls       vague state, missing base cases, wrong fill order, answer not at dp[n]
Production     cap input length; band the edit distance; bound caches; use iterative loops
```

---

## Related Topics

- [Backtracking](35-Backtracking.md) — the exhaustive search that DP replaces when you need counts or optima rather than every solution.
- [Greedy Algorithms](34-Greedy-Algorithms.md) — when a safe local choice exists, greedy is simpler; when it does not, DP is the fallback.
- [Hash Tables](11-Hash-Tables.md) — the `Map` or dictionary behind every memo table.
- [Caching Fundamentals](../Module-07-Advanced-Backend-and-System-Design/14-Caching-Fundamentals.md) — memoization is an in-process cache, and the same eviction and sizing questions apply.

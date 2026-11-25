# Space Complexity

> **Module 05 · Data Structures & Algorithms** · Prerequisites: [Time Complexity](02-Time-Complexity.md) · Next: [Big O Analysis](04-Big-O-Analysis.md)

---

## ⏱ If You Only Have 2 Minutes

- Space complexity measures how much memory an algorithm needs as the input size `n` grows. Time asks "how many steps?"; space asks "how much memory at the peak?"
- **Auxiliary space** is the extra memory the algorithm allocates. **Total space** includes the input. Interviews usually mean auxiliary space, so say which one you mean.
- Recursion is not free. Each active call keeps a stack frame, so a recursion that goes `n` deep uses O(n) stack space even when it allocates no arrays.
- An in-place algorithm uses O(1) extra space. Reversing an array with two indexes and swaps is the standard example.
- Node's default stack holds roughly ten thousand simple frames. Python's default recursion limit is 1,000, so a recursive sum over 100,000 items fails in Python.
- Memoization trades memory for time. Naive Fibonacci takes exponential time; memoized Fibonacci takes O(n) time and O(n) space; iterative Fibonacci takes O(n) time and O(1) space.
- Objects are heavy. A number in an array of objects costs much more than 8 bytes. Use typed or packed arrays for large numeric data.

---

## 1. What It Is and Why It Exists

**Space complexity** is a rule for how much memory an algorithm needs, written as a function of the input size. As with time, we use Big O notation. An algorithm that needs one extra variable is O(1) space. One that copies the whole input is O(n). One that builds a table of every pair is O(n²).

**Analogy:** cooking in a kitchen. The ingredients on the counter are the input. Bowls, pans and the cutting board you bring out are the extra space. A recipe that uses one bowl and washes it between steps needs less space than one that uses a new bowl for every ingredient. Both recipes use the same ingredients and take a similar time, but the kitchen counter tells a different story.

**The problem it solves.** Memory is finite, and in a server it is shared. A report endpoint that loads a whole 2 GB CSV into an array uses at least 2 GB for each request. Two requests at once can exhaust the container's memory limit. The process is then killed by the operating system, and every other request on that instance fails with it. The code might be O(n) in time and look fine in a test with 1,000 rows. Its space cost is the reason it breaks in production.

Space also matters for correctness. A recursive function that works on a 100-level tree can crash with a stack overflow on a 100,000-level linked structure. Nothing in the algorithm is wrong. It simply ran out of the memory set aside for calls.

---

## 2. How It Works

To find the space complexity of code, follow four steps:

1. Name the input size `n`.
2. List every allocation: new arrays, objects, strings, maps, and copies made by `slice`, spread or `list()`.
3. Add the stack frames for recursion. The peak depth matters, not the total number of calls.
4. Decide whether you are reporting auxiliary space (usually what interviewers want) or total space.

**Trace.** Recursive sum of `[1, 2, 3, 4]` using an index. The table lists the calls on the stack. The peak depth is five frames, which is `n + 1`.

| Step | Call | Stack depth | What happens |
|---|---|---|---|
| 1 | sum(i = 0) | 1 | Waits for sum(i = 1) |
| 2 | sum(i = 1) | 2 | Waits for sum(i = 2) |
| 3 | sum(i = 2) | 3 | Waits for sum(i = 3) |
| 4 | sum(i = 3) | 4 | Waits for sum(i = 4) |
| 5 | sum(i = 4) | 5 | Base case: i is past the end, returns 0 |
| 6 | sum(i = 3) | 4 | Returns 4 + 0 = 4 |
| 7 | sum(i = 2) | 3 | Returns 3 + 4 = 7 |
| 8 | sum(i = 1) | 2 | Returns 2 + 7 = 9 |
| 9 | sum(i = 0) | 1 | Returns 1 + 9 = 10 |

Each frame stays alive until the call below it returns. So the memory used at the peak grows with `n`, even though the function only adds numbers. An iterative loop does the same sum with one running total, so its extra space stays the same for any `n`.

---

## 3. Key Concepts

### Auxiliary space vs total space

**Auxiliary space** counts memory the algorithm creates, not counting the input. **Total space** counts both. A function that sorts an array in place has O(1) auxiliary space and O(n) total space, because the array is the input. A function that returns a sorted copy has O(n) auxiliary space. When you answer an interview question, say the word: "O(1) auxiliary space, not counting the input array." That one sentence shows you know the difference.

### The recursion stack

Each call stores its arguments, local variables and a return address in a stack frame. The stack's size is fixed by the runtime, so the depth limit is what matters.

- **Node.js (V8)** uses a fixed-size stack. A simple recursive function reaches roughly ten thousand frames before it throws a `RangeError: Maximum call stack size exceeded`. The exact number depends on frame size.
- **CPython** has a recursion limit that is 1,000 by default. Going past it raises `RecursionError`. You can read it with `sys.getrecursionlimit()`. Raising the limit is possible, but it does not add stack safety, so the honest fix is to use iteration or an explicit stack.

A recursion whose depth depends on the input, such as a walk over user-supplied nested data, has O(depth) space. That is the number to report.

### In-place algorithms

An algorithm is **in-place** when it rearranges the input using only a constant number of extra variables. Reversing an array with two indexes that move toward the middle and swap items is in-place: O(1) extra space and O(n) time. The cost is that the caller's array changes. That is a design decision, not a free lunch. Quicksort's partition step is also in-place, though its recursion adds O(log n) stack on average.

### Memory of JavaScript and Python objects

Both runtimes hide memory costs behind convenient syntax. The numbers below are rough, and they vary by version and build, so treat them as orders of magnitude.

- **Python:** every `int`, `str` and `list` is a full heap object with a header. A small `int` costs roughly 28 bytes, and an empty `str` costs roughly 50 bytes. A `list` also stores an 8-byte pointer per item. So a list of one million small ints costs far more than the 8 MB you might expect. The standard `array` module stores raw values with no per-item object.
- **JavaScript:** V8 stores small integers compactly in arrays. Mixed-type arrays and arrays of objects are much heavier, because each object has its own header and properties. `Float64Array` and `Int32Array` store raw values, which keeps large numeric data compact.

The practical rule: when you handle large numeric data, measure the heap. Node's `process.memoryUsage()` and Python's `tracemalloc` module both show where the memory goes.

### Time–space trade-offs and memoization

A cache, a lookup table or a memo trades memory for time. Naive recursive Fibonacci recomputes the same subproblems over and over. Storing each answer the first time it is computed makes the work linear. The price is O(n) memory for the table. Iterative Fibonacci keeps only the last two values, so it needs O(1) space and is also linear. Memoization is the right tool when the same subproblem appears many times and the input size is bounded. An unbounded cache is a memory leak, so set a maximum size.

### Complexity table

| Variant | Time (best / average / worst) | Extra space | Reason |
|---|---|---|---|
| Recursive sum, index parameter | O(n) / O(n) / O(n) | O(n) | One call per item, all alive at the deepest point |
| Iterative sum | O(n) / O(n) / O(n) | O(1) | One pass with one running total |
| Reverse in place | O(n) / O(n) / O(n) | O(1) | Each swap moves two items; the loop does n/2 swaps |
| Reverse into a new array | O(n) / O(n) / O(n) | O(n) | A new array of length n is allocated |
| Naive Fibonacci | Θ(φⁿ) for all cases | O(n) | The call tree has about φⁿ nodes; depth is n, so the stack is O(n) |
| Memoized Fibonacci | O(n) / O(n) / O(n) | O(n) | Each value is computed once; the table and the stack both hold n entries |
| Iterative Fibonacci | O(n) / O(n) / O(n) | O(1) | Two variables are updated n times |

---

## 4. Code Examples

Scenario: a report service must sum and reverse arrays of sales amounts, and it must compute Fibonacci numbers for a pricing table. The first block shows the two sum variants and the two reverse variants with edge cases. The second block covers the Fibonacci problem in three versions, plus a stack-depth test. The second block assumes the first block is in the same file.

### Node.js / TypeScript

Built-ins: `Array.prototype.reverse()` reverses in place and returns the same array (O(n) time, O(1) extra space). `[...arr].reverse()` makes a copy first. `Array.prototype.slice` always copies, so calling it inside a recursion adds O(n) work and space per call. `Float64Array` and `Int32Array` store numbers without per-item objects.

```ts
// Node.js 22+, TypeScript 5. No dependencies. Run with: npx tsx space.ts

// O(n) stack space: the call waits for the next one, so n frames are alive at the deepest point.
// Passing an index instead of slice() keeps the time at O(n) too.
export function sumRecursive(values: readonly number[], i = 0): number {
  if (i >= values.length) return 0; // base case: an empty tail sums to 0
  return values[i] + sumRecursive(values, i + 1);
}

// O(1) extra space: one accumulator, whatever the length. Empty input returns 0.
export function sumIterative(values: readonly number[]): number {
  let total = 0;
  for (const v of values) total += v;
  return total;
}

// O(1) auxiliary space: the swap uses one temporary variable. The caller's array IS changed.
// Edge cases: [] and [x] are returned unchanged.
export function reverseInPlace<T>(items: T[]): T[] {
  let lo = 0;
  let hi = items.length - 1;
  while (lo < hi) {
    const tmp = items[lo];
    items[lo] = items[hi];
    items[hi] = tmp;
    lo++;
    hi--;
  }
  return items;
}

// O(n) extra space: a new array of the same length. The input is left unchanged.
export function reversedCopy<T>(items: readonly T[]): T[] {
  const out: T[] = [];
  for (let i = items.length - 1; i >= 0; i--) out.push(items[i]);
  return out;
}
```

```ts
// Uses the functions from the previous block. Node.js 22+, TypeScript 5.
import assert from "node:assert/strict";

// Problem: Fibonacci. F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2).

// Naive recursion: exponential time (about φⁿ calls). Stack depth n: O(n) space.
export function fibNaive(n: number): number {
  return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2);
}

// Memoized recursion: O(n) time, O(n) space for the map plus the stack.
export function fibMemo(n: number, memo: Map<number, number> = new Map()): number {
  if (n < 2) return n;
  const cached = memo.get(n);
  if (cached !== undefined) return cached;
  const value = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
  memo.set(n, value);
  return value;
}

// Iterative: O(n) time, O(1) space. Only the last two values are kept.
export function fibIterative(n: number): number {
  let prev = 0; // F(0)
  let curr = 1; // F(1)
  for (let i = 0; i < n; i++) [prev, curr] = [curr, prev + curr];
  return prev;
}

// Edge cases: 0 and 1 are their own Fibonacci numbers; all three versions agree on small n.
assert.equal(fibIterative(0), 0);
assert.equal(fibMemo(1), 1);
for (let n = 0; n <= 20; n++) {
  assert.equal(fibNaive(n), fibIterative(n));
  assert.equal(fibMemo(n), fibIterative(n));
}

// Stack depth test: the recursive sum runs out of frames long before the loop runs out of memory.
const big = Array.from({ length: 100_000 }, (_, i) => i);
try {
  console.log("recursive sum:", sumRecursive(big));
} catch (err) {
  if (err instanceof RangeError) console.log("RangeError:", err.message);
  else throw err;
}
console.log("iterative sum:", sumIterative(big));
// Illustrative: the recursive call throws RangeError (Maximum call stack size exceeded); the iterative sum returns 4999950000.

// JS numbers are exact only up to 2^53 - 1, about F(78). Use BigInt for larger Fibonacci values.
```

### Python

Built-ins: `reversed(seq)` returns an iterator and copies nothing; `list.reverse()` reverses in place. `sum()` is a C loop with O(1) extra space. `functools.lru_cache(maxsize=None)` adds memoization in one decorator, but its cache is unbounded, so set a `maxsize` in production. `array.array` stores raw numbers compactly.

```python
# Python 3.12+, standard library only. Run with: python space.py
import sys
from collections.abc import Sequence


def sum_recursive(values: Sequence[int], i: int = 0) -> int:
    # O(n) stack space: one frame per item. CPython's default recursion limit is 1,000,
    # so this raises RecursionError for long inputs. Iteration is the fix, not a bigger limit.
    if i >= len(values):
        return 0  # base case: an empty tail sums to 0
    return values[i] + sum_recursive(values, i + 1)


def sum_iterative(values: Sequence[int]) -> int:
    # O(1) extra space: one running total. The built-in sum(values) does the same in C.
    total = 0
    for v in values:
        total += v
    return total


def reverse_in_place(items: list[int]) -> list[int]:
    # O(1) auxiliary space: two indexes and a swap. The caller's list IS changed.
    lo, hi = 0, len(items) - 1
    while lo < hi:
        items[lo], items[hi] = items[hi], items[lo]
        lo += 1
        hi -= 1
    return items  # [] and single-item lists are returned unchanged


def reversed_copy(items: Sequence[int]) -> list[int]:
    # O(n) extra space: a new list of length n. The input is left alone.
    return list(reversed(items))
```

```python
# Uses the functions from the previous block. Python 3.12+, standard library only.
import sys
from functools import lru_cache

# Problem: Fibonacci. F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2).


def fib_naive(n: int) -> int:
    # Exponential time (about φⁿ calls). Stack depth n: O(n) space.
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)  # unbounded here for teaching; use a maxsize in a long-running service
def fib_memo(n: int) -> int:
    # O(n) time, O(n) space for the cache plus the stack. Recursion depth n hits the limit at about 1,000.
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_iterative(n: int) -> int:
    # O(n) time, O(1) space. Python ints do not overflow, so large n gives exact results.
    prev, curr = 0, 1  # F(0), F(1)
    for _ in range(n):
        prev, curr = curr, prev + curr
    return prev


# Edge cases: 0 and 1 are their own Fibonacci numbers; all three versions agree on small n.
assert fib_iterative(0) == 0
assert fib_memo(1) == 1
for n in range(21):
    assert fib_naive(n) == fib_iterative(n) == fib_memo(n)

# Stack depth test: the recursive sum fails at about 1,000 frames, but the loop does not.
big = list(range(100_000))
try:
    print("recursive sum:", sum_recursive(big))
except RecursionError:
    print(f"RecursionError: depth {len(big)} exceeds the limit of {sys.getrecursionlimit()}")
print("iterative sum:", sum_iterative(big))
# Illustrative output: RecursionError on the first line, then iterative sum 4999950000.
```

---

## 5. Production Concerns

- **Stack overflows are crashes, not slow paths.** Node throws a `RangeError` and Python raises `RecursionError`. A request handler that walks user-supplied data recursively, such as nested comments, deep category trees or nested JSON, can be crashed by one input. Cap the depth you accept, or use an explicit stack in a loop.
- **Loading everything is O(n) memory per request.** A report that reads every row into an array needs memory for all of them, and each concurrent request needs its own copy. Use streaming or cursor pagination so the working set is one page. See [Cursor Pagination](../Module-03-Databases/25-Cursor-Pagination.md).
- **Container limits kill the process.** A Node process is limited by V8's heap limit (`--max-old-space-size`). A container is also limited by its memory cgroup. When the process exceeds its limit, the operating system kills it, and all in-flight requests on that instance fail. Size the heap below the container limit, and leave room for buffers.
- **Unbounded caches leak memory.** A memo table or in-memory cache that never evicts grows with every new key. Set a maximum size, and use an LRU or a TTL.
- **Measure the heap, not the guess.** Use `process.memoryUsage().heapUsed` in Node, and `tracemalloc` in Python, to see what a function actually allocates. Measure with production-sized inputs, because small inputs hide the per-item overhead.

---

## 6. Common Mistakes

- **Counting recursion as free** — each active call holds a frame, so a deep recursion is O(depth) space — report the stack depth, or rewrite the function with a loop.
- **Calling `slice()` inside a recursion** — each call copies the rest of the array, so the work becomes O(n²) — pass an index instead.
- **Calling an algorithm "in-place" when the caller still needs the original** — the reversal changed their data — document the mutation, or copy first and say the cost.
- **Memoizing without a bound** — the cache grows with every distinct input — set a maximum size or evict old entries.
- **Confusing auxiliary and total space** — the input array is not extra memory — say which one you are reporting.
- **Assuming a number costs 8 bytes** — a Python list of ints or a JS array of objects costs far more per item — use `array`, typed arrays or a database for large data.
- **Copying when a view or iterator would do** — `list(items)` or `[...items]` allocates O(n) for no reason — iterate lazily when you do not need a copy.

---

## 7. Comparison Table

| Approach | Time | Extra space | Use when |
|---|---|---|---|
| Recursion (depth n) | O(n) | O(n) stack | The shape is naturally recursive (trees) and the depth is small and bounded |
| Loop (iteration) | O(n) | O(1) | Linear processing of a sequence, especially with deep or unbounded input |
| Reverse in place | O(n) | O(1) | Memory is tight and the caller does not need the original order |
| Reverse into a copy | O(n) | O(n) | The original must stay unchanged, and an extra copy fits in memory |
| Naive Fibonacci | exponential | O(n) stack | Never in production; use it to explain the problem |
| Memoized Fibonacci | O(n) | O(n) | The same subproblems repeat and the cache is bounded |
| Iterative Fibonacci | O(n) | O(1) | You need one value and the recursion shape is not needed |

---

## 8. Interview Questions

**[Junior] What is the difference between auxiliary space and total space?**
Auxiliary space is the extra memory an algorithm uses, not counting its input. Total space includes the input as well. An in-place sort of an array has O(1) auxiliary space and O(n) total space, because the array itself is O(n). In an interview, state which one you mean, and most of the time you mean auxiliary space.

**[Junior] Does a recursive function use extra memory if it allocates no arrays?**
Yes. Each active call stores a stack frame with its arguments, locals and return address. If the recursion goes n levels deep before it returns, n frames exist at the peak, so the space is O(n). The runtime also has a fixed stack size, so very deep recursion crashes even when the memory is available.

**[Mid] Why is naive Fibonacci exponential in time but only O(n) in space?**
The call tree has about φⁿ nodes, since each call makes two more calls and many subproblems repeat. Time follows the number of nodes. The space is the depth of the tree, not its size. The deepest path goes n levels, from `fib(n)` down to `fib(0)`, so at most n frames are alive at once. Memoization fixes the time by storing each answer once, which adds an O(n) table.

**[Mid] A Python service stores a list of one million small integers and the process uses far more memory than expected. Why?**
Each Python `int` is a full object with a header, roughly 28 bytes for a small value. The list also stores a pointer per item. So the list costs much more than the raw 4 or 8 bytes per number. The fix is to store the numbers in `array.array('q')` or a NumPy array, which keeps raw values in one block, or to keep the data in a database. You measure it with `tracemalloc` before changing anything.

**[Mid] When is an in-place algorithm a bad choice?**
It is a bad choice when the caller still needs the original data, when the same input is shared by several readers, or when the code runs concurrently on the same structure. The memory saving is real, but the mutation is a side effect that other code can observe. In those cases, copy the input, or redesign so that the mutation is local and documented. Use in-place work where memory is tight and ownership is clear.

**[Senior] A recursive tree walker crashes with a stack overflow on a production input with depth 50,000. How do you diagnose and fix it?**
First confirm the cause from the error. In Node it is a `RangeError: Maximum call stack size exceeded`, and in Python it is a `RecursionError`. Then check whether the depth comes from the input, since user-supplied nesting is the usual source. The fix is to replace the recursion with an explicit stack in a loop, which moves the frames to the heap and gives O(depth) heap space instead of stack space. Add a depth limit that rejects input beyond a sensible bound, and add a test with a deep input so the regression is caught.

**[Senior] An endpoint loads every matching row into memory before it returns the first page. How do you bound its space?**
The cost is O(matching rows) per request, and concurrent requests multiply it. Change the query to fetch one page at a time, using keyset or cursor pagination with an index on the sort key. Then the working set is O(page size). If the client needs everything, stream the rows to the response and do not build an array. Also set a hard limit on the page size, so one request cannot ask for the whole table.

---

## 9. Cheat Sheet

```text
Space          = memory that grows with n, at the peak
Auxiliary      = extra memory, not counting input (say which one you mean)
Recursion      = O(depth) stack; Node ~10k frames, CPython limit 1,000 by default
Iteration      = same work, usually O(1) extra space
In-place       = O(1) extra; the caller's data IS changed
Copy           = slice(), spread, list(), [...x] allocate O(n) each time
Fibonacci      = naive exponential time, O(n) stack | memo O(n)/O(n) | iterative O(n)/O(1)
Memo           = trades memory for time; always bound the cache (maxsize / LRU / TTL)
Objects        = Python int ~28 bytes each; JS arrays of objects heavy; use array / typed arrays
Measure        = process.memoryUsage().heapUsed (Node), tracemalloc (Python)
Production     = cap depth and page size; stream instead of loading everything
Crash signs    = RangeError: Maximum call stack size exceeded | RecursionError
```

---

## Related Topics

- [Time Complexity](02-Time-Complexity.md) — the same counting method, applied to steps instead of memory.
- [Stack Memory](../Module-04-Operating-Systems/23-Stack-Memory.md) — where call frames live and why the stack has a fixed size.
- [Heap Memory](../Module-04-Operating-Systems/22-Heap-Memory.md) — where objects, arrays and caches are allocated.
- [Cursor Pagination](../Module-03-Databases/25-Cursor-Pagination.md) — bounding the rows a request can hold at once.
- [Node.js Event Loop and Concurrency](../Module-02-Core-Backend/06-Node-Event-Loop-and-Concurrency.md) — why one large synchronous job blocks every other request.

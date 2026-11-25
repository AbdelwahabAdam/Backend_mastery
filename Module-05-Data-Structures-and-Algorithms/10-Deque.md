# Deque

> **Module 05 · Data Structures & Algorithms** · Prerequisites: [Queues](09-Queues.md) · Next: [Hash Tables](11-Hash-Tables.md)

---

## ⏱ If You Only Have 2 Minutes

- A **deque** (double-ended queue, pronounced "deck") adds and removes items at **both ends** in O(1) time. It can act as a stack, as a queue, or as both.
- A plain array is fast only at its end. A deque is built for both ends, which a queue and a stack each only need one of.
- A **ring buffer** deque keeps a `head` index that can move backward (`pushFront`) or forward (`popFront`) with wrap-around. Indexing into the middle is O(1) because the position is computed, not walked.
- A **bounded** deque drops items from the far end when full. That is exactly the behaviour of `collections.deque(maxlen=n)`, and it is how you keep "the last N" items with fixed memory.
- Python has `collections.deque` built in. JavaScript has no built-in deque, so you write one or use a head index on an array.
- Uses in backends: bounded undo history, the last N log lines, work-stealing schedulers, and the 0-1 BFS shortest-path variant.
- Interview problems: a palindrome check with a deque, and keeping the last N log lines. The sliding-window maximum uses a deque too, but it belongs to [Monotonic Queue](40-Monotonic-Queue.md).

---

## 1. What It Is and Why It Exists

A **deque** is a sequence where you can add or remove items at the **front** and at the **back**. Its operations are `pushFront`, `pushBack`, `popFront` and `popBack`. Each one takes O(1) time in a good implementation.

**Analogy:** a bookshelf where you can add or take a book from either end. A queue is a shelf where books go in at one end and come out at the other. A stack is a shelf where you use only one end. A deque lets you use both.

**The problem it solves.** Some algorithms need to look at the newest and the oldest items at the same time, or to remove from both ends. A sliding window is the classic case. When the window moves right, you remove an item from the left. When a new item arrives, you may also remove items from the right that will never matter again. A plain queue can only remove from the front, so you would have to scan the whole window each time. A deque does both removals in O(1) and keeps the work linear for the whole input.

Deques also show up where a stack and a queue must meet. A work-stealing scheduler needs the owner of a task list to take work from one end while other threads take from the other end. An undo history needs to push new actions at the end and drop the oldest action from the front when the history is full.

---

## 2. How It Works

### The ring buffer deque

The ring buffer from [Queues](09-Queues.md) becomes a deque with one change. `pushFront` moves `head` **backward** by one, with wrap-around, and then writes the item there. The items always sit in the slots `head`, `head + 1`, and so on, modulo the capacity. The item at logical position `i` is stored at `(head + i) % capacity`.

Here is a trace with capacity 4, starting empty. `_` means an empty slot. The `buf` column shows the four slots in order `[0] [1] [2] [3]`.

| Step | Operation | Returned | head | count | buf | Deque contents (front to back) |
|---|---|---|---|---|---|---|
| 1 | pushBack(1) | | 0 | 1 | `1 _ _ _` | `[1]` |
| 2 | pushBack(2) | | 0 | 2 | `1 2 _ _` | `[1, 2]` |
| 3 | pushFront(0) | | 3 | 3 | `1 2 _ 0` (head moved to 3) | `[0, 1, 2]` |
| 4 | popBack() | 2 | 3 | 2 | `1 _ _ 0` | `[0, 1]` |
| 5 | popFront() | 0 | 0 | 1 | `1 _ _ _` | `[1]` |

Step 3 is the new behaviour. `head` goes from 0 to `(0 - 1 + 4) % 4 = 3`, so the new item lands in the last slot. Step 4 pops from the back. Its slot is `(head + count - 1) % 4 = (3 + 3 - 1) % 4 = 1`, which holds `2`.

### Bounded deques

A **bounded** deque has a fixed capacity. When it is full, an insert at one end evicts the item at the other end. Python's `deque(maxlen=n)` works this way. The result is a window of the most recent n items. The memory use is fixed, and old data disappears without any code to remove it.

### The 0-1 BFS trick

Breadth-first search finds shortest paths in a graph where every edge costs 1. If some edges cost 0, you can still use a deque. Push a neighbour to the **front** when the edge costs 0, and to the **back** when it costs 1. The front of the deque always holds the node with the smallest distance, so the first time you pop a node, its distance is final. This runs in O(V + E), which is faster than Dijkstra's algorithm for this special case.

---

## 3. Key Concepts

### Stack, queue, deque

A stack uses one end, a queue uses two ends in a fixed direction (in at the back, out at the front), and a deque lets both ends work in both directions. Any stack or queue can be written as a deque. The reverse is not true, because a deque needs operations that a stack or queue does not provide.

### Constant time at both ends

For a ring buffer deque, all four end operations are O(1) worst case, as long as the buffer is not full. A growable deque, such as the one in Python, reallocates its storage from time to time. Each reallocation costs O(n), but the cost is spread over many operations, so each one is O(1) amortized.

### Indexing: an important difference

A ring buffer gives O(1) indexing into the middle, because `(head + i) % capacity` is a calculation. Python's `collections.deque` is a linked list of fixed-size blocks, so indexing into the middle is O(n), even though indexing at either end is O(1). Treat a Python deque as a queue and a stack, not as an array with random access.

### Bounded history with eviction

| Policy | Full deque receives an item at the back | Use when |
|---|---|---|
| Reject | Insert fails; caller sees `false` | Every item matters and nothing may be lost |
| Evict oldest | Front item is removed, then the new item is added | Only the recent items matter (logs, undo history) |

An undo history is an example of the second policy. Each action is pushed at the back. When the history reaches its limit, the oldest action falls off the front. Undo pops from the back, so the most recent action is undone first.

### Work stealing

A work-stealing scheduler gives each worker thread its own deque of tasks. The owner pushes new tasks and pops them from one end, which is LIFO. That keeps recently used data hot in the CPU cache. An idle worker steals tasks from the **other** end of a busy worker's deque, which is FIFO. Stealing from the far end means the owner and the thief rarely touch the same slot. Java's `ForkJoinPool` and the Go runtime's scheduler use this design. The Go runtime keeps a per-processor run queue with a stealing path, so the same idea appears at the level of the OS-thread scheduler. The exact details differ, but the pattern is the same.

---

## 4. Code Examples

### Node.js / TypeScript

JavaScript has no deque in its standard library. `Array` gives O(1) `push` and `pop` at the end, but `unshift` and `shift` move every element, so they are O(n) in general. Use a ring buffer when you need both ends. The class below is bounded, like `collections.deque(maxlen=n)`: a push to a full deque evicts the item at the opposite end. A plain fixed-capacity deque would reject instead, which is the other policy from section 3.

```ts
// No dependencies. Node.js 22+, TypeScript 5.
// A fixed-capacity deque. When full, a push at one end evicts the item at the other end,
// so it can hold "the last N items" with constant memory.
export class BoundedDeque<T> {
  private readonly buf: (T | undefined)[];
  private head = 0;   // physical index of the front item
  private count = 0;  // number of stored items

  constructor(capacity: number) {
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new RangeError("capacity must be a positive integer");
    }
    this.buf = new Array<T | undefined>(capacity);
  }

  get size(): number {
    return this.count;
  }

  // Logical index i maps to a physical slot with wrap-around. This is why indexing is O(1).
  get(i: number): T | undefined {
    if (i < 0 || i >= this.count) return undefined;
    return this.buf[(this.head + i) % this.buf.length];
  }

  pushBack(item: T): T | undefined {
    const evicted = this.count === this.buf.length ? this.popFront() : undefined;
    this.buf[(this.head + this.count) % this.buf.length] = item;
    this.count++;
    return evicted;
  }

  pushFront(item: T): T | undefined {
    const evicted = this.count === this.buf.length ? this.popBack() : undefined;
    // Move head backward first; (x - 1 + n) % n keeps the result non-negative.
    this.head = (this.head - 1 + this.buf.length) % this.buf.length;
    this.buf[this.head] = item;
    this.count++;
    return evicted;
  }

  popFront(): T | undefined {
    if (this.count === 0) return undefined;
    const item = this.buf[this.head];
    this.buf[this.head] = undefined;  // release the reference for the GC
    this.head = (this.head + 1) % this.buf.length;
    this.count--;
    return item;
  }

  popBack(): T | undefined {
    if (this.count === 0) return undefined;
    const slot = (this.head + this.count - 1) % this.buf.length;
    const item = this.buf[slot];
    this.buf[slot] = undefined;
    this.count--;
    return item;
  }

  toArray(): T[] {
    const out: T[] = [];
    for (let i = 0; i < this.count; i++) {
      out.push(this.get(i) as T);
    }
    return out;
  }
}
```

Two interview problems, solved with the code below:

- **Palindrome check with a deque.** Given a string, ignore case and non-alphanumeric characters, and decide whether it reads the same forwards and backwards. Approach: load the characters into a deque, then repeatedly compare the front and the back, removing both. Complexity: O(n) time, O(n) space. Empty input and one character are both palindromes.
- **Keep the last N log lines.** Given a stream of lines and a number N, return the last N lines in order. Approach: push each line to a bounded deque of size N. Complexity: O(L) time for L lines, O(N) space, no matter how long the stream is.

```ts
// Problem solutions. Uses BoundedDeque from the block above.

// Palindrome check. Only ASCII letters and digits count, and case is ignored.
export function isPalindrome(text: string): boolean {
  const chars = [...text.toLowerCase()].filter((c) => /[a-z0-9]/.test(c));
  if (chars.length === 0) return true;  // empty input is a palindrome
  // Capacity equals the length, so no push ever evicts.
  const dq = new BoundedDeque<string>(chars.length);
  for (const c of chars) dq.pushBack(c);
  while (dq.size > 1) {
    // Evaluation is left to right, so popFront() runs before popBack().
    if (dq.popFront() !== dq.popBack()) return false;
  }
  return true;  // zero or one character left: the middle matches itself
}

// Keep the last N lines of a stream, in order. The stream is never stored in full.
export function lastLines(lines: Iterable<string>, n: number): string[] {
  if (n < 1) return [];
  const window = new BoundedDeque<string>(n);
  for (const line of lines) {
    window.pushBack(line);  // evicts the oldest line once N lines are stored
  }
  return window.toArray();
}
```

### Python

Python's standard library provides `collections.deque`, which is implemented as a doubly linked list of blocks. `append`, `appendleft`, `pop` and `popleft` are O(1). `deque(maxlen=n)` evicts from the opposite end when full, which is what the log-line problem needs. Indexing at either end is O(1), but indexing in the middle is O(n), so do not use it as an array. For the palindrome and log-line problems, the built-in type is the right tool. The class below is a Python port of the ring buffer, so the two languages show the same mechanism.

```python
# Standard library only. Python 3.12+.
# A bounded deque backed by a ring buffer. Like deque(maxlen=n): a push at one end
# evicts the item at the other end when full.
from typing import cast


class BoundedDeque[T]:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self._buf: list[T | None] = [None] * capacity
        self._head = 0    # physical index of the front item
        self._count = 0   # number of stored items

    def __len__(self) -> int:
        return self._count

    def _slot(self, i: int) -> int:
        # Python's % never returns a negative number for a positive modulus.
        return (self._head + i) % len(self._buf)

    def get(self, i: int) -> T | None:
        if i < 0 or i >= self._count:
            return None
        return self._buf[self._slot(i)]

    def push_back(self, item: T) -> T | None:
        evicted = self.pop_front() if self._count == len(self._buf) else None
        self._buf[self._slot(self._count)] = item
        self._count += 1
        return evicted

    def push_front(self, item: T) -> T | None:
        evicted = self.pop_back() if self._count == len(self._buf) else None
        self._head = (self._head - 1) % len(self._buf)
        self._buf[self._head] = item
        self._count += 1
        return evicted

    def pop_front(self) -> T | None:
        if self._count == 0:
            return None
        item = self._buf[self._head]
        self._buf[self._head] = None  # release the reference for the GC
        self._head = (self._head + 1) % len(self._buf)
        self._count -= 1
        return item

    def pop_back(self) -> T | None:
        if self._count == 0:
            return None
        slot = self._slot(self._count - 1)
        item = self._buf[slot]
        self._buf[slot] = None
        self._count -= 1
        return item

    def to_list(self) -> list[T]:
        return [cast(T, self._buf[self._slot(i)]) for i in range(self._count)]
```

Two interview problems, solved with the code below. They are the same problems as in TypeScript, solved with the standard library:

- **Palindrome check with a deque.** Same statement as above. Approach: `collections.deque` with `popleft()` and `pop()`. Complexity: O(n) time, O(n) space.
- **Keep the last N log lines.** Same statement as above. Approach: `deque(maxlen=N)`. Complexity: O(L) time, O(N) space.

```python
# Problem solutions. Standard library only.
from collections import deque
from collections.abc import Iterable


def is_palindrome(text: str) -> bool:
    # Keep ASCII letters and digits only, lower-cased, to match the TypeScript version.
    chars = deque(c for c in text.lower() if c.isascii() and c.isalnum())
    while len(chars) > 1:
        if chars.popleft() != chars.pop():
            return False
    return True  # zero or one character left


def last_lines(lines: Iterable[str], n: int) -> list[str]:
    if n < 1:
        return []
    # maxlen evicts from the left automatically; the stream is never stored in full.
    window: deque[str] = deque(maxlen=n)
    window.extend(lines)
    return list(window)
```

---

## 5. Production Concerns

- **Bound every history.** An undo stack or a log buffer without a limit grows with the user's session length. A `maxlen` (or the evicting `BoundedDeque`) caps memory per session. Pick N from a real requirement, such as "the last 50 undo steps", and write it down.
- **Keep work-stealing deques lock-light.** A production scheduler does not put a lock on every push and pop. It uses atomic operations so that the owner and thieves race only on the last item. Do not write your own lock-free deque for production. Use the runtime's scheduler or a tested library.
- **Watch for unbounded state in logs.** A "last N lines" buffer is safe, but keeping every line of a long-running process in a list is not. Stream logs to a file or a log collector and keep only the window in memory.
- **Measure memory after a burst.** A deque that grew during a traffic spike may keep the memory it reserved, even after it is nearly empty. Check the resident memory of the process after a load test, not only during it.
- **Beware of indexing in Python.** `deque[i]` in the middle is O(n). A loop that indexes a deque is quadratic. Use a list when you need random access, or iterate.
- **Concurrency.** Python's `deque` operations such as `append` and `pop` are thread-safe, but a check followed by an action (for example "if not empty, pop") is not. Use `queue.Queue` when multiple threads must wait for items.

---

## 6. Common Mistakes

- **Using `unshift()` as a deque** — each call moves the whole array, so a loop of n calls costs O(n²) — use a ring buffer or `collections.deque`.
- **Indexing into the middle of a Python deque** — `dq[i]` is O(n) in the middle, so a loop over indices is quadratic — iterate, or use a list.
- **Forgetting to check the capacity before popping in a palindrome loop** — with one character left, `popFront()` and `popBack()` return the same item — loop while `size > 1`.
- **Pushing before evicting** — with a full ring buffer, the write overwrites the oldest item without updating `head`, which corrupts the order — evict first, then write.
- **Confusing the eviction end** — `maxlen` drops items from the **opposite** end of the one you append to — when you `append` on the right, the left item is dropped.
- **Using a deque where a heap is needed** — a deque keeps insertion order, not priority order — use a priority queue when the smallest or largest item must come out first.
- **Assuming a deque is always fast at both ends** — a growable deque pays O(n) once in a while when it reallocates, which shows as latency spikes — measure tail latency, or preallocate when the maximum size is known.

---

## 7. Comparison Table

| Structure | Push / pop at front | Push / pop at back | Index access | Bounded option | Use when |
|---|---|---|---|---|---|
| Array (JS `Array`) | `unshift` / `shift`: O(n) | `push` / `pop`: O(1) amortized | O(1) | No | Stack or append-only list |
| Ring buffer deque | O(1) | O(1) | O(1) | Yes | Fixed memory, random access, both ends |
| `collections.deque` | O(1) | O(1) | O(1) at ends, O(n) in middle | Yes (`maxlen`) | Python queue, stack, sliding window |
| Singly linked list | O(1) at front only | O(n) without a tail pointer | O(n) | No | Rarely the best choice; use a deque |
| Doubly linked list | O(1) | O(1) | O(n) | No | Needs O(1) removal of a known node (see LRU) |
| Heap / priority queue | Not a deque | Not a deque | No | No | Smallest or largest first, not arrival order |

---

## 8. Interview Questions

**[Junior] What is a deque, and how does it differ from a queue?**
A deque is a double-ended queue. You can add and remove items at both the front and the back, each in O(1) time. A queue lets you add at the back and remove at the front only. A deque can do everything a queue can do, plus removal from the back, which is what a sliding window needs.

**[Junior] Why is `unshift` slow on a JavaScript array?**
`unshift` inserts at the front, so every existing element must move one slot to the right. That costs O(n) for each call. A ring buffer avoids the move by moving the `head` index instead.

**[Mid] How do you check whether a string is a palindrome with a deque?**
Load the cleaned characters into the deque, then repeatedly remove one character from the front and one from the back. If they differ, the string is not a palindrome. If you reach zero or one character, it is. The time is O(n), and the space is O(n) for the deque. A two-pointer loop over the array does the same work with O(1) extra space, so the deque is a choice of style here, not a necessity.

**[Mid] How do you keep only the last N items of a stream?**
Use a bounded deque with capacity N. Each new item goes to the back, and when the deque is full, the oldest item falls off the front. In Python, `deque(maxlen=N)` does this in one line. Memory stays at O(N) no matter how long the stream runs.

**[Senior] Why does a work-stealing scheduler use a deque instead of a shared queue?**
Each worker owns its deque and pushes and pops at one end, so most operations touch only that worker's data. That keeps locking and cache contention low, and the most recent tasks stay in cache. When a worker runs out of work, it steals from the other end of another worker's deque. Owner and thief rarely use the same slot, so they seldom conflict. A single shared queue would make every worker contend on the same lock or atomic counter.

**[Senior] How would you implement a 0-1 BFS, and why is it faster than Dijkstra for this case?**
Use a deque of nodes. When an edge has cost 0, push the neighbour to the front. When it has cost 1, push it to the back. The deque stays sorted by distance, with at most two distance values in it at any time, so popping from the front always gives the next closest node. The runtime is O(V + E). Dijkstra needs a priority queue and costs O((V + E) log V). The shortcut only works because the edge costs are 0 and 1; for general weights, use Dijkstra.

---

## 9. Cheat Sheet

```text
Deque           add and remove at both ends, all O(1)
Ring buffer     physical index = (head + i) % capacity; pushFront moves head backward
Bounded         full + push at one end  ->  evict the item at the other end
Python          collections.deque: append, appendleft, pop, popleft are O(1)
Python          deque(maxlen=N): keeps the last N items; evicts from the opposite end
Python          deque middle index is O(n); ends are O(1); use list for random access
JavaScript      no built-in deque; unshift/shift are O(n); use a ring buffer
Palindrome      deque: compare popFront() with popBack() while size > 1
Last N          bounded deque of size N; memory O(N) for any stream length
0-1 BFS         push 0-cost edges to the front, 1-cost edges to the back
Work stealing   owner uses one end, thieves take from the other end
Undo history    bounded deque; undo pops the newest item from the back
```

---

## Related Topics

- [Queues](09-Queues.md) — the ring buffer and FIFO behaviour that a deque extends.
- [Stacks](08-Stacks.md) — a deque used at one end behaves as a stack.
- [Monotonic Queue](40-Monotonic-Queue.md) — the sliding-window maximum, which keeps a deque of candidates.
- [Breadth First Search](21-Breadth-First-Search.md) — the queue-based shortest path that the 0-1 variant extends.
- [LRU Cache](43-LRU-Cache.md) — a doubly linked list gives O(1) removal from the middle, a different trade-off.

# Priority Queue

> **Module 05 · Data Structures & Algorithms** · Prerequisites: [Hash Sets](12-Hash-Sets.md) · Next: [Heaps](14-Heaps.md)

---

## ⏱ If You Only Have 2 Minutes

- A **priority queue** returns the item with the best priority, not the oldest one. Its core operations are `insert`, `peek` (look at the top) and `extract-min` (or `extract-max`, remove the top).
- A **binary heap** gives O(log n) insert and extract, and O(1) peek. A sorted array makes insert O(n). An unsorted array makes extract O(n).
- JavaScript and TypeScript have **no built-in priority queue**. Re-sorting an array on every insert costs O(n log n) each time, which is the wrong tool.
- Python's `heapq` is a **min-heap only**. For a max-heap, push negated values. Store `(priority, counter, item)` tuples so ties come out first-in, first-out and items are never compared.
- Backend uses: job schedulers, delayed jobs, timers, Dijkstra's shortest-path algorithm and top-K metrics over a stream.
- Top K of n items with a heap of size K costs O(n log K) time and O(K) space. Sorting everything costs O(n log n).

---

## 1. What It Is and Why It Exists

A **priority queue** is an abstract data type (ADT). An ADT is a list of operations and rules, not a memory layout. The rules are simple:

- `insert(item, priority)` adds an item.
- `peek()` returns the item with the best priority without removing it.
- `extract()` removes and returns the item with the best priority.

"Best" usually means the smallest number (a **min-priority queue**), but it can also mean the largest (a **max-priority queue**). A plain queue is first-in, first-out. A priority queue is "most urgent first."

**Analogy:** an emergency room. Patients are seen by how serious their condition is, not by when they arrived. A patient with a heart attack jumps ahead of someone with a sprained wrist who has been waiting longer.

**The problem it solves.** Suppose a job system holds 100,000 pending jobs, and each job has a `runAt` time. Workers always need the job that is due next. If you keep the jobs in a plain array and scan for the earliest one each time, every pick costs O(n). With constant picks, that scan dominates the CPU. A priority queue makes each pick O(log n) and keeps the work organised by priority.

---

## 2. How It Works

The priority queue is the *interface*. A **binary heap** is the most common *implementation*. The heap stores the items in an array, with one rule called the **heap invariant**: in a min-heap, each parent is less than or equal to its children. So the smallest item is always at the root, at index 0. Chapter 14 explains the array layout in detail.

Here is a trace of a min-heap. We insert 5, 3, 8 and 1, then call `extract-min`.

| Step | Operation | Array after the step | What happens |
|---|---|---|---|
| 1 | insert 5 | `[5]` | First item becomes the root |
| 2 | insert 3 | `[3, 5]` | 3 goes to index 1. Its parent (index 0, value 5) is larger, so they swap |
| 3 | insert 8 | `[3, 5, 8]` | 8 goes to index 2. Its parent (3) is smaller, so nothing moves |
| 4 | insert 1 | `[1, 3, 8, 5]` | 1 goes to index 3. It swaps with its parent 5 (index 1), then with 3 (index 0). It reaches the root |
| 5 | extract-min | `[3, 5, 8]` | Remove the root 1. Move the last item 5 to the root. It sinks by swapping with the smaller child 3 |

After step 5, the root is 3, which is the new minimum. Each insert or extract moves one item along a single path from the bottom of the array to the top (or the reverse). That path has about log2(n) steps, which is why the operations are O(log n).

Notice what the array does *not* promise. Only the root is guaranteed to be the minimum. The rest of the array is only partly ordered. If you print the array, you will not see the items in order.

---

## 3. Key Concepts

### The four ways to implement it

There is no single best implementation. The right one depends on which operation your code calls most often.

| Implementation | Operation | Best | Average | Worst | Space | Why the bound holds |
|---|---|---|---|---|---|---|
| Unsorted array | insert | O(1) | O(1) | O(1) | O(n) | Append to the end; no ordering to maintain |
| | extract-min | O(n) | O(n) | O(n) | | Every item must be checked to find the smallest |
| Sorted array, min at the end | insert | O(1) | O(n) | O(n) | O(n) | Best: the new item is the smallest and goes at the end. Worst: it is the largest and every item shifts |
| | extract-min | O(1) | O(1) | O(1) | | The minimum is the last element; `pop()` removes it |
| Binary heap | insert | O(1) | O(1) | O(log n) | O(n) | Best: no swap. Worst: one swap per level, about log2(n) levels. Average is O(1) for random keys |
| | extract-min | O(1) | O(log n) | O(log n) | | Best: the moved item is already smaller than its children. Otherwise it sinks one path of height log n |
| | peek | O(1) | O(1) | O(1) | | The minimum is always at index 0 |
| Balanced BST (AVL or red-black) | insert | O(log n) | O(log n) | O(log n) | O(n) | Balancing keeps the height near log n, so the path to a leaf is short |
| | extract-min | O(log n) | O(log n) | O(log n) | | Walk to the leftmost node and rebalance on the way back |
| | peek | O(log n) | O(log n) | O(log n) | | Leftmost node; O(1) only if the minimum is cached |

Amortized note: a binary heap has no amortized cost. Each operation is worst-case O(log n). The O(1) average insert is an *average over random inputs*, not a guarantee. An unsorted array is the simplest choice, but its extract is O(n), so it fails for schedulers that pop often.

A binary heap is the standard choice. A balanced BST also works and supports more operations (such as searching by key), but it uses more memory per node and more code.

### Ties and stable ordering

`heapq` in Python and a heap written by hand do **not** keep equal priorities in insertion order. If two jobs both have priority 1, either may come out first. Most backend systems expect first-in, first-out for equal priorities, so fix this with an **insertion counter**. Each item gets a number that rises with every insert. The heap compares `(priority, counter)`, so ties fall back to the counter. The counter also stops the heap from ever comparing the items themselves, which matters when items are dictionaries or objects that cannot be compared with `<`.

### Max-priority by negation

Most heap libraries are min-heaps. To pop the largest value first, store the negative of each value. Python example: `heapq.heappush(h, -score)`, then `-heapq.heappop(h)` gives the largest score back. For tuples, negate only the priority part. For objects, you can wrap the item in a class with a reversed `__lt__`, but negation is simpler and less error-prone.

### Lazy deletion

Some algorithms need to change the priority of an item that is already in the heap. A heap cannot find an arbitrary item quickly, so the common trick is **lazy deletion**. Push a new entry with the new priority and leave the old entry in place. When you pop an entry, check whether it is still current. If not, skip it. Dijkstra's algorithm uses this trick, as shown in the Section 8 interview answers.

---

## 4. Code Examples

Both examples implement the same ADT. Each uses the language's standard library or a short class with no dependencies.

### Node.js / TypeScript

Node has no built-in priority queue. The class below is a compact binary heap with a comparator and insertion-order tie-breaking. Chapter 14 builds the full heap with more detail.

```ts
// Node.js 22+ / TypeScript 5. No dependencies.
// A compact min-priority queue. compare(a, b) < 0 means a pops first (the same rule as Array.sort).
interface Entry<T> {
  value: T;
  seq: number; // insertion counter: breaks ties first-in, first-out
}

export class PriorityQueue<T> {
  private readonly heap: Entry<T>[] = [];
  private nextSeq = 0;
  private readonly compare: (a: T, b: T) => number;

  constructor(compare: (a: T, b: T) => number) {
    this.compare = compare;
  }

  get size(): number {
    return this.heap.length;
  }

  push(value: T): void {
    this.heap.push({ value, seq: this.nextSeq++ });
    this.siftUp(this.heap.length - 1);
  }

  // Returns the next item without removing it, or undefined when empty.
  peek(): T | undefined {
    return this.heap[0]?.value;
  }

  // Removes and returns the next item, or undefined when empty.
  pop(): T | undefined {
    if (this.heap.length === 0) return undefined;
    const top = this.heap[0];
    const last = this.heap.pop()!;
    if (this.heap.length > 0) {
      this.heap[0] = last; // move the last leaf to the root, then let it sink
      this.siftDown(0);
    }
    return top.value;
  }

  private before(a: Entry<T>, b: Entry<T>): boolean {
    const c = this.compare(a.value, b.value);
    return c < 0 || (c === 0 && a.seq < b.seq);
  }

  private siftUp(i: number): void {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (!this.before(this.heap[i], this.heap[parent])) return;
      [this.heap[i], this.heap[parent]] = [this.heap[parent], this.heap[i]];
      i = parent;
    }
  }

  private siftDown(i: number): void {
    for (;;) {
      const left = 2 * i + 1;
      const right = left + 1;
      let best = i;
      if (left < this.heap.length && this.before(this.heap[left], this.heap[best])) best = left;
      if (right < this.heap.length && this.before(this.heap[right], this.heap[best])) best = right;
      if (best === i) return;
      [this.heap[i], this.heap[best]] = [this.heap[best], this.heap[i]];
      i = best;
    }
  }
}
```

Two interview problems, using the class above:

**Problem 1: K largest elements.** Given n numbers and a value k, return the k largest in descending order. *Approach:* keep a min-heap of at most k items. Push each number, and if the heap grows past k, pop the smallest. The root is always the weakest of the current top k. *Complexity:* O(n log k) time, O(k) space.

**Problem 2: merge K sorted lists.** Given k sorted arrays with N values in total, return one sorted array. *Approach:* put the first value of each list in the heap, with its list index and position. Pop the smallest, output it, then push the next value from the same list. *Complexity:* O(N log k) time, O(k) space for the heap.

```ts
// Uses the PriorityQueue class from the block above.

// Problem 1: K largest elements.
export function kLargest(nums: readonly number[], k: number): number[] {
  if (k <= 0) return [];
  const heap = new PriorityQueue<number>((a, b) => a - b);
  for (const n of nums) {
    heap.push(n);
    if (heap.size > k) heap.pop(); // the smallest of k+1 items cannot be in the top k
  }
  const out: number[] = [];
  while (heap.size > 0) out.push(heap.pop()!);
  return out.reverse(); // popped smallest first, so reverse for descending order
}

// Problem 2: merge K sorted lists. The heap holds the current head of each list.
interface Head {
  value: number;
  list: number;
  index: number;
}

export function mergeKSorted(lists: readonly (readonly number[])[]): number[] {
  const heap = new PriorityQueue<Head>((a, b) => a.value - b.value);
  lists.forEach((list, li) => {
    if (list.length > 0) heap.push({ value: list[0], list: li, index: 0 });
  });
  const out: number[] = [];
  while (heap.size > 0) {
    const { value, list, index } = heap.pop()!;
    out.push(value);
    if (index + 1 < lists[list].length) {
      heap.push({ value: lists[list][index + 1], list, index: index + 1 });
    }
  }
  return out;
}
```

**Built-ins in JavaScript:** `Array.prototype.sort` is stable (since ES2019), so equal items keep their order. That helps for a one-off sort, but sorting after every insert is O(n log n) each time. Use a heap when items arrive over time.

### Python

Python's `heapq` module gives you a min-heap as functions over a plain `list`. It has no class, no comparator, and no tie-breaking. The class below wraps it and adds the counter.

```python
# Python 3.12+. Standard library only.
import heapq
import itertools


class PriorityQueue[T]:
    """Min-priority queue: the lowest priority number pops first.

    heapq only provides a min-heap. The insertion counter makes equal priorities
    pop first-in, first-out, and stops heapq from comparing the items themselves
    (dicts and many objects do not support <).
    """

    def __init__(self) -> None:
        self._heap: list[tuple[float, int, T]] = []
        self._counter = itertools.count()

    def __len__(self) -> int:
        return len(self._heap)

    def push(self, item: T, priority: float) -> None:
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def peek(self) -> T:
        if not self._heap:
            raise IndexError("peek from an empty priority queue")
        return self._heap[0][2]

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("pop from an empty priority queue")
        return heapq.heappop(self._heap)[2]
```

The same two problems, using `heapq` directly:

```python
import heapq


def k_largest(nums: list[int], k: int) -> list[int]:
    """Problem 1: K largest elements. O(n log k) time, O(k) space."""
    if k <= 0:
        return []
    heap: list[int] = []  # min-heap of at most k values
    for n in nums:
        heapq.heappush(heap, n)
        if len(heap) > k:
            heapq.heappop(heap)  # the smallest of k+1 values cannot be in the top k
    return sorted(heap, reverse=True)


def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    """Problem 2: merge K sorted lists. O(N log k) time for N total values."""
    heap: list[tuple[int, int, int]] = []  # (value, list index, position in that list)
    for li, values in enumerate(lists):
        if values:  # skip empty lists: they have no head to push
            heapq.heappush(heap, (values[0], li, 0))
    out: list[int] = []
    while heap:
        value, li, pos = heapq.heappop(heap)
        out.append(value)
        if pos + 1 < len(lists[li]):
            heapq.heappush(heap, (lists[li][pos + 1], li, pos + 1))
    return out


# Built-ins for the same problems: heapq.nlargest(k, nums), and heapq.merge(*lists),
# which merges sorted iterables lazily without building the full output first.
assert k_largest([3, 1, 5, 9, 2], 2) == [9, 5]
assert merge_k_sorted([[1, 4], [], [2, 3, 6]]) == [1, 2, 3, 4, 6]
```

**Runtime difference:** `heapq` runs its sift loops in C and compares values directly with the `<` operator, so it needs no callback. The TypeScript class calls a comparator function for every comparison. The algorithm and the O(log n) bound are the same in both.

---

## 5. Production Concerns

- **Memory limits.** An unbounded queue grows until the process runs out of memory. Cap the queue size. When it is full, reject new work (for example with HTTP 429 or 503) or drop the lowest-priority items.
- **Starvation.** With strict priorities, low-priority items may never run while high-priority work keeps arriving. Fix it with **aging**: raise an item's priority the longer it waits, or give low-priority work a guaranteed share of workers. See the interview questions below.
- **Durability.** An in-memory heap is lost when the process crashes. For jobs that must survive a restart, keep the source of truth in a store. A Redis sorted set works well: `ZADD` with the run-at time as the score, and `ZPOPMIN` to take the earliest job. A database table with an index on `run_at` also works.
- **Several workers.** Two workers must never take the same job. The pop must be atomic in the shared store, or the worker must claim the job with a lease that expires if the worker dies.
- **Timers.** Use a monotonic clock for scheduled times. `Date.now()` can jump when the system clock is adjusted. Use `performance.now()` in Node and `time.monotonic()` in Python for elapsed time.
- **What to measure.** Queue depth is useful, but the age of the oldest waiting item is often more useful. Also track the time spent in `pop` under load and the number of items skipped by lazy deletion.

---

## 6. Common Mistakes

- **Re-sorting on every insert** — each insert costs O(n log n), and the work grows with the queue — use a heap, which costs O(log n) per insert.
- **Forgetting that `heapq` is min-only** — a "top scores" list returns the *worst* scores — push negated values, or use `heapq.nlargest`.
- **Letting ties compare items** — a tuple `(priority, item)` raises `TypeError` when two priorities are equal and the items cannot be compared — add an insertion counter in the middle of the tuple.
- **Assuming equal priorities come out in order** — the heap does not promise first-in, first-out — add the counter.
- **Changing a priority while the item is in the heap** — the heap invariant breaks and later pops return the wrong item — push a new entry and skip stale entries when popped (lazy deletion).
- **Reading the array to see the queue** — only index 0 is guaranteed to be the minimum — pop items, or copy and sort the array when you need a view for debugging.
- **Using a heap to remove an arbitrary item** — finding the item first takes O(n) — keep a map from item to its index, or use lazy deletion.

---

## 7. Comparison Table

The right choice depends on whether the queue must survive restarts and be shared by several processes.

| Option | Where the data lives | Insert | Pop the next item | Survives a crash, shared by workers | Use when |
|---|---|---|---|---|---|
| Binary heap (this chapter) | Process memory | O(log n) | O(log n) | No | Top-K, Dijkstra, in-process timers |
| Balanced BST | Process memory | O(log n) | O(log n) | No | You also need search by key or range queries |
| Redis sorted set (`ZADD`, `ZPOPMIN`) | Redis server | O(log n) | O(log n) | Yes, if Redis persists data | Shared delayed-job queues across many workers |
| Database table with an index on the sort key | Database | Index update | Index seek | Yes | Jobs that must be audited, retried or stored with other data |

For a single process, use the heap. For a fleet of workers, use a shared store, and let the store perform the atomic pop.

---

## 8. Interview Questions

**[Junior] What is a priority queue, and how is it different from a normal queue?**
A normal queue is first-in, first-out. A priority queue returns the item with the best priority next, no matter when it arrived. The operations are insert, peek and extract. The priority queue is an interface. A binary heap is the usual way to build it, and it gives O(log n) insert and extract.

**[Junior] Why is a binary heap a good fit for a priority queue?**
A heap keeps the minimum at the root and fixes the order along a single path after each change. That path has about log2(n) steps, so insert and extract are O(log n), and peek is O(1). It also stores the items in a flat array, which is compact and cache-friendly. Sorting the whole array after each insert would be much slower.

**[Mid] How would you find the top 10 items in a stream of one billion numbers?**
Keep a min-heap of at most 10 values. For each number, push it, and if the heap has 11 items, pop the smallest. At the end the heap holds the 10 largest values. This takes O(n log 10) time, which is effectively linear, and O(10) memory. Sorting the whole stream would need O(n) memory, which may not fit.

**[Mid] How do you get a max-heap from Python's `heapq`?**
Push negated numbers, then negate the value when you pop it. For tuples such as `(score, name)`, negate only the score. Negation fails for non-numeric priorities, so for those, wrap the priority in a small class with a reversed `__lt__`. Remember to add an insertion counter if equal priorities must come out in a fixed order.

**[Senior] Design a delayed-job scheduler that survives restarts and runs on several workers.**
Do not use an in-memory heap as the source of truth. Store each job in a shared store, such as a database table or a Redis sorted set with the run-at time as the score. A worker claims the next due job with an atomic operation, such as `SELECT ... FOR UPDATE SKIP LOCKED` in PostgreSQL or a Lua script in Redis, and sets a lease with an expiry time. The worker acknowledges the job when it finishes. If the worker dies, the lease expires and another worker retries the job. The handler must be idempotent, because the same job can run twice.

**[Senior] How does Dijkstra's algorithm use a priority queue, and why is `heapq` awkward for it?**
Dijkstra keeps a frontier of nodes keyed by their best known distance. It pops the closest node, marks it final, and relaxes its edges. Each improvement needs a decrease-key operation, which a binary heap does not expose. The usual workaround is lazy deletion: push a new `(distance, node)` pair on each improvement, and when popping, skip the pair if its distance is larger than the best known distance. With a binary heap this runs in O(E log V) time. Fibonacci heaps give cheaper decrease-key in theory, but they are rarely worth their complexity in practice.

**[Senior] How do you prevent starvation in a priority queue?**
Strict priority can starve low-priority items forever. Two common fixes are aging and weighted sharing. With aging, an item's effective priority improves the longer it waits, so old work eventually rises to the top. With weighted sharing, keep one queue per priority and take, for example, 8 jobs from the high queue for every 1 from the low queue. Aging is simple but makes priorities harder to reason about. Weighted sharing gives predictable throughput per class, but needs tuning. Either way, expose the age of the oldest item as a metric, so you can see starvation happening.

---

## 9. Cheat Sheet

```text
ADT          insert, peek (top), extract (remove top)
Binary heap  insert O(log n) worst, extract O(log n), peek O(1), space O(n)
Sorted array insert O(n), extract O(1) if min is at the end
Unsorted     insert O(1), extract O(n)
JS / TS      no built-in; write a heap or use a library
Python       heapq = min-heap only; max-heap = push -x
Ties         add an insertion counter: (priority, counter, item)
Top K        min-heap of size K; O(n log K)
Merge K      heap of list heads; O(N log K)
Dijkstra     heap + lazy deletion; O(E log V)
Starvation   aging or weighted queues
Durability   store jobs in Redis ZSET or a DB table, not only in memory
```

---

## Related Topics

- [Heaps](14-Heaps.md) — the array layout, sift-up, sift-down and O(n) heapify that make these operations fast
- [Heap Sort](29-Heap-Sort.md) — sorting by repeatedly extracting the minimum from a heap
- [Graphs](20-Graphs.md) — Dijkstra's algorithm uses a priority queue for its frontier
- [Redis Deep Dive](../Module-07-Advanced-Backend-and-System-Design/15-Redis-Deep-Dive.md) — sorted sets as a shared, durable priority queue
- [Message Queues](../Module-07-Advanced-Backend-and-System-Design/21-Message-Queues.md) — how work queues are shared across many machines

# Merge Sort

> **Module 05 · Data Structures & Algorithms** · Prerequisites: [Sorting Algorithms](26-Sorting-Algorithms.md) · Next: [Quick Sort](28-Quick-Sort.md)

---

## ⏱ If You Only Have 2 Minutes

- Merge sort **splits** the input in half, **sorts** each half recursively, then **merges** the two sorted halves in one linear pass.
- It is O(n log n) in **every** case (best, average, worst), it is **stable**, and it needs **O(n)** extra space for an array.
- The merge step is the heart of it. Take the smaller front item from either side, and use `<=` so that equal items keep their original order.
- A bottom-up version merges runs of width 1, 2, 4, and so on. It removes recursion and gives the same result.
- **External merge sort** sorts data bigger than memory: sort memory-sized runs, write them to disk, then do a **k-way merge** with a min-heap. Databases use this when an `ORDER BY` spills.
- Interview favourites: **count inversions** (count out-of-order pairs during the merge) and **merge K sorted lists** (merge in pairs, or use a heap).
- Node's built-in sort and Python's `sorted()` are merge-based hybrids (Timsort). Know the plain algorithm, because it is the one you will be asked to write.

---

## 1. What It Is and Why It Exists

**Merge sort** is a [divide-and-conquer](24-Divide-and-Conquer.md) algorithm. It solves a problem of size n by solving two problems of size n/2, then combining the answers. For sorting, the combine step is a **merge**: given two sorted lists, produce one sorted list by repeatedly taking the smaller front item.

**Analogy:** two piles of exam papers, each already sorted by student number. To combine them, you look at the top paper of each pile, take the one with the smaller number, and repeat. You never need to look back, because each pile is already in order. Now imagine the piles themselves were made the same way, by splitting a messy stack in half and sorting each half. That is merge sort.

**The problem it solves.** [Insertion sort](26-Sorting-Algorithms.md) and selection sort are O(n²). That is fine for dozens of items and terrible for millions. Merge sort gives a guaranteed O(n log n) bound with no bad inputs, which matters for a server. An attacker who controls the input cannot make merge sort quadratic, which is a real risk for quick sort (covered in the next chapter). Merge sort is also stable, and it is the natural algorithm when the data is a linked list or lives on disk, where you can only read it sequentially.

Merge sort is a good first divide-and-conquer algorithm to learn. The recurrence `T(n) = 2T(n/2) + O(n)` gives O(n log n) by the [master theorem](24-Divide-and-Conquer.md): split into two halves of size n/2 and do linear work to merge.

---

## 2. How It Works

The algorithm has three steps:

1. **Divide.** If the input has 0 or 1 items, it is already sorted: return it. Otherwise split it at the middle.
2. **Conquer.** Sort the left half and the right half, each with merge sort.
3. **Combine.** Merge the two sorted halves into one sorted list.

### Trace on `[38, 27, 43, 3, 9, 82, 10]`

The split phase first. Each level of the recursion halves the pieces:

```text
[38, 27, 43, 3, 9, 82, 10]
├── [38, 27, 43]
│   ├── [38]                      already sorted
│   └── [27, 43]  -> [27, 43]     split, sorted, merged
│       merge [38] + [27, 43]  ->  [27, 38, 43]
└── [3, 9, 82, 10]
    ├── [3, 9]    -> [3, 9]       already merged
    └── [82, 10]  -> [10, 82]     split, sorted, merged
        merge [3, 9] + [10, 82] -> [3, 9, 10, 82]

final merge [27, 38, 43] + [3, 9, 10, 82]
```

The final merge step-by-step shows exactly how the combine works. Each row takes the smaller of the two front items:

| Step | Left front | Right front | Compare | Take | Output so far |
|---|---|---|---|---|---|
| 1 | 27 | 3 | 27 <= 3? no | 3 (right) | `[3]` |
| 2 | 27 | 9 | 27 <= 9? no | 9 (right) | `[3, 9]` |
| 3 | 27 | 10 | 27 <= 10? no | 10 (right) | `[3, 9, 10]` |
| 4 | 27 | 82 | 27 <= 82? yes | 27 (left) | `[3, 9, 10, 27]` |
| 5 | 38 | 82 | 38 <= 82? yes | 38 (left) | `[3, 9, 10, 27, 38]` |
| 6 | 43 | 82 | 43 <= 82? yes | 43 (left) | `[3, 9, 10, 27, 38, 43]` |
| 7 | (empty) | 82 | no comparison left | 82 (rest of right) | `[3, 9, 10, 27, 38, 43, 82]` |

The merge makes one pass over both lists, so it costs O(total length). Once one side is empty, the rest of the other side is already sorted and is copied in one go.

### The bottom-up version

The recursion is not required. Start with runs of width 1 (each item is a sorted run). Merge neighbouring pairs into runs of width 2, then width 4, and so on, until one run covers the whole array. The same input:

```text
width 1: [27,38] [3,43] [9,82] [10]
width 2: [3,27,38,43] [9,10,82]
width 4: [3,9,10,27,38,43,82]
```

The bottom-up version uses a loop instead of recursion, so it has no stack depth to worry about. It is also the natural form for linked lists and for external sorting, where each run is a separate chunk of data.

---

## 3. Key Concepts

### Why the merge is linear

Each merge step outputs one item and advances one pointer. The pointers only move forward. So a merge of two lists with n and m items takes at most n + m comparisons and n + m moves. A full sort has log2(n) levels of recursion, and each level's merges together touch every item once. The total is n × log2(n).

### Stability in the merge

The merge is stable if, when two items compare equal, the left item is taken first. The comparison `left <= right` does exactly that. If you write `left < right` instead, equal items from the right can jump ahead of equal items from the left, and the sort becomes unstable. This one character is the difference between a correct multi-key sort and a silent bug.

### Space cost

A merge needs a place to write its output. With arrays, a standard merge sort needs an extra buffer of size n, so O(n) extra space, plus O(log n) for the recursion stack. This is the main cost compared with [quick sort](28-Quick-Sort.md) and [heap sort](29-Heap-Sort.md), which are in place. Linked lists are the exception: you can merge them by relinking pointers, so merge sort on a list needs only O(1) extra space for the merging, and O(log n) for recursion (or none, with the bottom-up version).

### External merge sort

When data does not fit in memory, the same idea works in two phases:

1. **Run generation.** Read a chunk that fits in memory, sort it (any in-memory sort), and write it to disk as a **sorted run**.
2. **K-way merge.** Open k runs at once. Keep the front item of each run in a **min-heap** of size k. Repeatedly pop the smallest item, write it to the output, and push the next item from that run.

The heap has k entries, so each output item costs O(log k). The total is O(N log k) for N items. If there are too many runs to open at once, merge in several passes: the number of passes over the data is 1 + ceil(log_k(number of runs)). Reads and writes are sequential, which disks handle much better than random access. This is why databases use it.

### Complexity

| Variant | Best | Average | Worst | Extra space | Stable |
|---|---|---|---|---|---|
| Top-down merge sort (array) | O(n log n) | O(n log n) | O(n log n) | O(n) buffer + O(log n) stack | Yes |
| Bottom-up merge sort (array) | O(n log n) | O(n log n) | O(n log n) | O(n) buffer | Yes |
| Merge sort (linked list) | O(n log n) | O(n log n) | O(n log n) | O(1) with bottom-up merging | Yes |
| K-way merge of N items from k lists | O(N log k) | O(N log k) | O(N log k) | O(k) for the heap | Yes, if ties prefer earlier lists |
| External merge sort | O(N log N) comparisons | same | same | memory M plus k buffers | Yes |

Why each bound holds:

- **Merge sort, any input**: the recursion has log2(n) levels, and every level's merges touch each item once. There is no input that causes a worse split, because the split is always in half. Its best case is no better than its worst case.
- **K-way merge**: each output item needs one pop and one push on a heap of size k, and a heap operation is O(log k).
- **External merge sort**: the in-memory runs cost O(N log M) for run size M, and the merge passes cost O(N log_k(N/M)) in total. Together that is O(N log N) comparisons; the I/O cost is what dominates in practice.

---

## 4. Code Examples

Scenario: a backend job must sort records with a stable order, count how often a list is out of order (a measure of how "scrambled" a ranking is), and merge many sorted result lists from shard servers into one list.

### Node.js / TypeScript

Node.js 22+ and TypeScript 5. JavaScript has no built-in merge function for arrays. Its `Array.prototype.sort` is already stable and uses a merge-based hybrid (TimSort in V8), so for everyday work you should call `sort` and not write your own. Writing merge sort is still the right exercise, and it is the algorithm you will explain in an interview. The `merge` loop is also reused in many real systems: merging sorted log streams, combining search results from shards, and so on. JavaScript has no heap in the standard library, so the k-way problem below uses pairwise merging instead.

```ts
// No dependencies. Node.js 22+, TypeScript 5.
import assert from "node:assert/strict";

export type Compare<T> = (a: T, b: T) => number;
export const numberAsc: Compare<number> = (a, b) => a - b;

// Merge two sorted arrays into a new sorted array. O(left + right) time.
// Uses <= 0 so equal items from the left come first. That is what makes the sort stable.
export function merge<T>(left: readonly T[], right: readonly T[], cmp: Compare<T>): T[] {
  const out: T[] = [];
  let i = 0;
  let j = 0;
  while (i < left.length && j < right.length) {
    if (cmp(left[i], right[j]) <= 0) out.push(left[i++]);
    else out.push(right[j++]);
  }
  // One side is exhausted. The other side is already sorted, so copy it in one step.
  while (i < left.length) out.push(left[i++]);
  while (j < right.length) out.push(right[j++]);
  return out;
}

// Top-down merge sort. Returns a new array and leaves the input unchanged.
// O(n log n) in every case, O(n) extra space, stable.
export function mergeSort<T>(items: readonly T[], cmp: Compare<T>): T[] {
  if (items.length <= 1) return [...items]; // 0 or 1 items are already sorted
  const mid = Math.floor(items.length / 2);
  // slice() copies each half. It keeps the code short; an index-based version reuses one buffer.
  const left = mergeSort(items.slice(0, mid), cmp);
  const right = mergeSort(items.slice(mid), cmp);
  return merge(left, right, cmp);
}

assert.deepEqual(mergeSort([38, 27, 43, 3, 9, 82, 10], numberAsc), [3, 9, 10, 27, 38, 43, 82]);
assert.deepEqual(mergeSort([], numberAsc), []);
assert.deepEqual(mergeSort([1], numberAsc), [1]);
assert.deepEqual(mergeSort([2, 2, 1, 2], numberAsc), [1, 2, 2, 2]);

// Stability: sort pairs by the first field only. Equal keys keep their original order.
const pairs: [number, string][] = [[2, "a"], [1, "b"], [2, "c"], [1, "d"]];
assert.deepEqual(
  mergeSort(pairs, (x, y) => x[0] - y[0]),
  [[1, "b"], [1, "d"], [2, "a"], [2, "c"]],
);
```

Problem 1: **count inversions.** Given an array, count the pairs `(i, j)` with `i < j` and `a[i] > a[j]`. Approach: run merge sort, and count during the merge. When a right item is smaller than the current left item, it is smaller than every remaining left item, so it forms one inversion with each of them. Time O(n log n), space O(n).

Problem 2: **merge K sorted lists.** Approach: merge pairs of lists, then pairs of the results, until one remains. This is a tournament with log2(K) rounds, each touching every item once. Time O(N log K) for N total items, space O(N). A min-heap that holds the front of each list gives the same bound and works better when the lists are read lazily.

```ts
// No dependencies. Node.js 22+, TypeScript 5.
import assert from "node:assert/strict";

// Problem 1: count inversions (pairs i < j with a[i] > a[j]).
// Approach: merge sort that counts while it merges. Time O(n log n), space O(n).
function sortAndCount(a: number[]): [number[], number] {
  if (a.length <= 1) return [a, 0];
  const mid = Math.floor(a.length / 2);
  const [left, leftInv] = sortAndCount(a.slice(0, mid));
  const [right, rightInv] = sortAndCount(a.slice(mid));
  const out: number[] = [];
  let i = 0;
  let j = 0;
  let crossInv = 0;
  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) {
      out.push(left[i++]); // equal values are not inversions, so <= takes the left item first
    } else {
      out.push(right[j++]);
      crossInv += left.length - i; // every left item from index i on is greater than right[j]
    }
  }
  while (i < left.length) out.push(left[i++]);
  while (j < right.length) out.push(right[j++]);
  return [out, leftInv + rightInv + crossInv];
}

export function countInversions(nums: readonly number[]): number {
  return sortAndCount([...nums])[1];
}

// Problem 2: merge K sorted lists into one sorted list.
// Approach: merge pairs of lists, then pairs of the results, until one list is left.
// Time O(N log K) for N total items, space O(N).
function mergeTwo(a: number[], b: number[]): number[] {
  const out: number[] = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) out.push(a[i] <= b[j] ? a[i++] : b[j++]);
  while (i < a.length) out.push(a[i++]);
  while (j < b.length) out.push(b[j++]);
  return out;
}

export function mergeKSorted(lists: readonly (readonly number[])[]): number[] {
  if (lists.length === 0) return [];
  let current: number[][] = lists.map((list) => [...list]);
  while (current.length > 1) {
    const next: number[][] = [];
    for (let i = 0; i < current.length; i += 2) {
      // An odd list out is carried to the next round unchanged.
      next.push(i + 1 < current.length ? mergeTwo(current[i], current[i + 1]) : current[i]);
    }
    current = next;
  }
  return current[0];
}

assert.equal(countInversions([2, 4, 1, 3, 5]), 3); // (2,1), (4,1), (4,3)
assert.equal(countInversions([5, 4, 3, 2, 1]), 10);
assert.equal(countInversions([1, 1, 1]), 0);       // equal values are not inversions
assert.equal(countInversions([]), 0);
assert.deepEqual(mergeKSorted([[1, 4, 7], [2, 5], [3, 6, 8]]), [1, 2, 3, 4, 5, 6, 7, 8]);
assert.deepEqual(mergeKSorted([[], [2], []]), [2]);
assert.deepEqual(mergeKSorted([]), []);
```

### Python

Python 3.12+. The built-in `sorted()` and `list.sort()` use Timsort, a stable merge-based hybrid, so you should use them in production code. The standard library also ships `heapq.merge(*iterables)`, a lazy k-way merge of sorted inputs that uses a heap internally. It does not load everything into memory, which makes it the right tool for merging large sorted files or streams. The code below writes the algorithms out by hand, using the same structure as the TypeScript version.

```python
# Standard library only. Python 3.12+.
from collections.abc import Callable, Sequence
from typing import Any


def merge[T](left: Sequence[T], right: Sequence[T], key: Callable[[T], Any]) -> list[T]:
    """Merge two sorted sequences in O(len(left) + len(right)) time."""
    out: list[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # <= sends equal items from the left first. That is what keeps the sort stable.
        if key(left[i]) <= key(right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])  # one side is exhausted; the rest is already in order
    out.extend(right[j:])
    return out


def merge_sort[T](items: Sequence[T], key: Callable[[T], Any] = lambda x: x) -> list[T]:
    """Top-down merge sort. Returns a new list. O(n log n) always, O(n) extra space, stable."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)  # slicing copies each half; clear, if not the leanest
    right = merge_sort(items[mid:], key)
    return merge(left, right, key)


assert merge_sort([38, 27, 43, 3, 9, 82, 10]) == [3, 9, 10, 27, 38, 43, 82]
assert merge_sort([]) == []
assert merge_sort([1]) == [1]
assert merge_sort([2, 2, 1, 2]) == [1, 2, 2, 2]
pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
assert merge_sort(pairs, key=lambda p: p[0]) == [(1, "b"), (1, "d"), (2, "a"), (2, "c")]  # stable
```

```python
# Standard library only. Python 3.12+.
import heapq
from collections.abc import Sequence


# Problem 1: count inversions (pairs i < j with a[i] > a[j]).
# Approach: merge sort that counts while it merges. Time O(n log n), space O(n).
def count_inversions(nums: Sequence[int]) -> int:
    def sort_and_count(a: list[int]) -> tuple[list[int], int]:
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, left_inv = sort_and_count(a[:mid])
        right, right_inv = sort_and_count(a[mid:])
        out: list[int] = []
        i = j = 0
        cross_inv = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
                cross_inv += len(left) - i  # every left item from index i on is greater than right[j]
        out.extend(left[i:])
        out.extend(right[j:])
        return out, left_inv + right_inv + cross_inv

    return sort_and_count(list(nums))[1]


# Problem 2: merge K sorted lists into one sorted list.
# Approach: merge pairs of lists, then pairs of the results, until one list is left.
# Time O(N log K) for N total items, space O(N).
def merge_two(a: Sequence[int], b: Sequence[int]) -> list[int]:
    out: list[int] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def merge_k_sorted(lists: Sequence[Sequence[int]]) -> list[int]:
    if not lists:
        return []
    current: list[list[int]] = [list(lst) for lst in lists]
    while len(current) > 1:
        nxt: list[list[int]] = []
        for i in range(0, len(current), 2):
            # An odd list out is carried to the next round unchanged.
            nxt.append(merge_two(current[i], current[i + 1]) if i + 1 < len(current) else current[i])
        current = nxt
    return current[0]


assert count_inversions([2, 4, 1, 3, 5]) == 3  # (2,1), (4,1), (4,3)
assert count_inversions([5, 4, 3, 2, 1]) == 10
assert count_inversions([1, 1, 1]) == 0  # equal values are not inversions
assert count_inversions([]) == 0
assert merge_k_sorted([[1, 4, 7], [2, 5], [3, 6, 8]]) == [1, 2, 3, 4, 5, 6, 7, 8]
assert merge_k_sorted([[], [2], []]) == [2]
assert merge_k_sorted([]) == []
assert list(heapq.merge([1, 4, 7], [2, 5], [3, 6, 8])) == [1, 2, 3, 4, 5, 6, 7, 8]  # built-in, lazy
```

**Runtime difference:** merge sort is pure computation, so its cost is CPU time. In Node.js, a large merge sort on the main thread blocks every other request until it finishes. Move big sorts to a worker thread or push them into the database. In Python, a pure-Python merge sort is slow compared with the built-in `sorted()`, which is written in C. The built-in is the right choice for in-memory data, and `heapq.merge` is the right choice for streams.

---

## 5. Production Concerns

- **External sorting in databases.** When an `ORDER BY` needs more memory than the query is allowed, PostgreSQL sorts in runs on disk and merges them. In `EXPLAIN ANALYZE`, a spilled sort shows a line like the one below (illustrative output):

  ```text
  Sort  (actual time=2841.130..3197.402 rows=4000000 loops=1)
    Sort Key: created_at
    Sort Method: external merge  Disk: 262144kB
  ```

  The fix is usually an index that already returns rows in order, a smaller result (filter first), or more `work_mem` for that query. Raise it per session, not globally.
- **Stability and pagination.** Merge sort is stable, but SQL does not promise a stable order for equal keys. A paginated query `ORDER BY created_at` can repeat or skip rows across pages. Add a unique tie-breaker such as `id`.
- **Memory under pressure.** An array merge sort needs an extra buffer of about n items. For a 10-million-item array of 8-byte numbers, that is about 80 MB extra. Check this before sorting large data in a container with a tight memory limit.
- **Blocking the event loop.** In Node.js, merge sort on tens of millions of items takes seconds of CPU on one thread. Use a worker thread, or sort in the database, and keep request handlers fast.
- **Spilling to disk must be observable.** Log the number of runs and the total bytes written for a large external sort. A sudden jump in disk I/O during a report job is usually a sort that stopped fitting in memory.
- **Failure during a long sort.** An external sort writes temporary runs. If the job crashes, clean up the run files, or the disk fills up over time. Use a temporary directory per job.

---

## 6. Common Mistakes

- **`<` instead of `<=` in the merge** — equal items from the right jump ahead of equal items from the left, so the sort is no longer stable — compare with `<=` so ties take the left item first.
- **Forgetting the leftover items** — the last few items of one side are dropped, so the output is short — after the main loop, copy whatever remains on both sides.
- **Counting inversions with `<` instead of `<=`** — equal values get counted as inversions — count only when the right item is strictly smaller than the left item.
- **Merging K lists one after another** — merging list 1 with list 2, then with list 3, and so on costs O(N·K) because the result is copied again and again — merge in pairs (a tournament) or use a min-heap of list heads.
- **Assuming merge sort is in place** — an array merge sort needs an O(n) buffer — account for the extra memory, or use heap sort or quick sort when memory is the constraint.
- **Holding all runs open at once** — with thousands of runs, the merge needs a buffer per run, and memory runs out — merge in several passes with a fan-in that fits in memory.
- **Choosing a comparator that is not a total order** — `NaN` values or inconsistent comparisons make the merge produce an unsorted result without an error — validate keys before sorting.

---

## 7. Comparison Table

| Sort | Worst case | Extra space | Stable | Adaptive | Good for |
|---|---|---|---|---|---|
| Merge sort | O(n log n) | O(n) | Yes | No | Stability, guaranteed bounds, linked lists, external sorting |
| [Quick sort](28-Quick-Sort.md) | O(n²) | O(log n) | No | No | Fast in-place sorting on typical data |
| [Heap sort](29-Heap-Sort.md) | O(n log n) | O(1) | No | No | In-place with a guaranteed bound |
| Timsort (built-in) | O(n log n) | O(n) | Yes | Yes | Real data with existing runs; the default choice |

For a backend answer, say: "I use the built-in sort, which is a stable merge-based hybrid. If I need to sort data that does not fit in memory, I write sorted runs and do a k-way merge with a heap." Be ready to explain why the merge is linear, why the sort is stable, and where the O(n) space goes.

---

## 8. Interview Questions

**[Junior] Describe merge sort in three steps.**
Divide the array in half. Recursively sort each half. Merge the two sorted halves by repeatedly taking the smaller front item. An array of 0 or 1 items is already sorted, which is the base case. The recursion has about log2(n) levels, and each level does a linear merge, so the total is O(n log n).

**[Junior] Why is merge sort stable?**
Stability depends on the merge. When the front items compare equal, the merge takes the item from the left half first. Because the left half holds the items that came earlier in the original array, equal items keep their original order. Writing `<=` instead of `<` in that comparison is what makes this true.

**[Mid] Why is merge sort often preferred for linked lists?**
A linked list has no random access, so quick sort's partition (which needs indexed swaps) and binary search do not work well on it. Merge only needs sequential access: walk two lists and relink nodes. Splitting a list in half with slow and fast pointers is O(n), and the bottom-up version uses O(1) extra space. So merge sort on a linked list is O(n log n) with no buffer.

**[Mid] Explain how to count inversions in O(n log n).**
Run merge sort, and count during the merge. When the right item is strictly smaller than the current left item, it is smaller than every item still waiting on the left, because the left half is sorted. So add the number of remaining left items to the count. Inversions inside each half are counted by the recursive calls, and inversions across the halves are counted during the merge.

**[Senior] You must sort 1 TB of records on a machine with 8 GB of RAM. Design the sort.**
Run generation: read about 6 GB at a time, sort each chunk in memory, and write it to disk as a sorted run. That gives roughly 170 runs. Merge: a k-way merge with a min-heap holds one front item per run, and read and write buffers keep the I/O sequential. With 170 runs and a fan-in limited by buffer memory (for example, 64 runs per pass), two merge passes finish the job. Each byte is read and written three times in total (run generation, then two merge passes), so the job is bound by disk bandwidth, not by CPU. Use a unique tie-breaker if the output must be deterministic.

**[Senior] A service merges 500 sorted result lists from shards, with 10 million items in total. What is the cost of each approach, and which would you pick?**
Merging the lists one after another costs O(N·K), which is about 5 × 10^9 item copies here. A pairwise tournament costs O(N log K), about 10^7 × 9, roughly 9 × 10^7 steps. A min-heap of the 500 list heads also costs O(N log K) and holds only K items in memory, so it works when the lists arrive as streams. I would pick the heap for streaming and the tournament for in-memory arrays. Both keep the output sorted and stable if ties prefer lists that come earlier in the input.

**[Senior] Merge sort guarantees O(n log n). Why do many runtimes still choose a different algorithm for in-memory arrays?**
Memory traffic and constant factors matter. An array merge sort needs an O(n) buffer and copies items at every level. Quick sort and heap sort work in place, which saves allocation and keeps memory hot in cache. Timsort, the usual choice, keeps merge sort's stability and guaranteed bound, and it exploits existing runs in real data to reach O(n) on sorted input. So runtimes use a merge-based hybrid to get both the bound and the speed.

---

## 9. Cheat Sheet

```text
Idea            split in half, sort each half, merge in one linear pass
Merge           take the smaller front item; use <= so equal items keep order
Time            O(n log n) best, average and worst
Space           O(n) buffer for arrays; O(1) extra for linked lists (bottom-up)
Stable          yes, if the merge uses <= (left first on ties)
Bottom-up       merge runs of width 1, 2, 4, ... ; no recursion
Inversions      count during the merge: when right < left, add the remaining left items
K-way merge     pairwise tournament O(N log K), or min-heap of K heads O(N log K)
External sort   sort memory-sized runs, write them, merge with a heap, multiple passes if many runs
Passes          1 + ceil(log_k(runs)) passes over the data
Databases       spilled ORDER BY shows "Sort Method: external merge" in EXPLAIN ANALYZE
JS              no merge in the standard library; Array.prototype.sort is stable
Python          sorted() is Timsort; heapq.merge(*iterables) lazily merges sorted inputs
Pitfall         forgetting the leftover items after the main loop
```

---

## Related Topics

- [Sorting Algorithms](26-Sorting-Algorithms.md) — the overview: stability, the n log n lower bound, and where merge sort fits.
- [Quick Sort](28-Quick-Sort.md) — the in-place alternative, with a worst case that merge sort avoids.
- [Priority Queue](13-Priority-Queue.md) — the heap that makes the k-way merge efficient.
- [Query Execution Plans](../Module-03-Databases/22-Query-Execution-Plans.md) — where a database sort step appears, and when it spills to disk.

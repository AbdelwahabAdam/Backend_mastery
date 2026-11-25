# Quick Sort

> **Module 05 · Data Structures & Algorithms** · Prerequisites: [Merge Sort](27-Merge-Sort.md) · Next: [Heap Sort](29-Heap-Sort.md)

---

## ⏱ If You Only Have 2 Minutes

- Quick sort picks a **pivot**, **partitions** the array so smaller items are on the left and larger items on the right, then sorts each side recursively.
- It is **in place** (O(1) extra space apart from the O(log n) recursion stack) and O(n log n) **on average**, but **O(n²) in the worst case**.
- The worst case happens when every pivot is the smallest or largest item, for example with a fixed first or last pivot on already sorted input. Use a **random** pivot to avoid it on any fixed input.
- Quick sort is **not stable**. Equal items can swap places during partitioning.
- **Lomuto** partition is easy to write and places the pivot in its final slot. **Hoare** partition does fewer swaps and handles many duplicates better.
- **Quickselect** finds the k-th smallest item in O(n) on average by recursing into only one side. Use it for "kth largest" and "top K" problems.
- Built-in sorts in V8 and CPython do not use quick sort. They use TimSort, which is stable and has an O(n log n) worst case.

---

## 1. What It Is and Why It Exists

**Quick sort** is a divide-and-conquer sort, like [merge sort](27-Merge-Sort.md), but it does its work before the recursion instead of after. It chooses one element as the **pivot**, rearranges the array so that every smaller element is to the left of the pivot and every larger element is to the right, then sorts the two sides. After one partition, the pivot is in its final position. The rest of the work is sorting two smaller pieces in place.

**Analogy:** sorting a deck of cards by splitting it around a card. Pick a card, and put every lower card on its left and every higher card on its right. The chosen card is now in the right place. Repeat on each pile.

**The problem it solves.** Merge sort is O(n log n) always, but it needs an extra buffer of n items. For large arrays in memory, that buffer costs allocation time and cache space. Quick sort sorts in place, and its inner loop is simple and cache-friendly: it walks the array in one direction and swaps neighbours. In practice that makes it fast for random data, which is why it became the classic in-memory sort.

Its weakness is the worst case. A naive quick sort on sorted input takes O(n²) time and can overflow the stack. Most of this chapter is about avoiding that worst case, and about **quickselect**, which turns the same partition into an O(n) average algorithm for finding order statistics.

---

## 2. How It Works

Each recursive call does three things: choose a pivot, partition, and recurse on each side. The partition is the only interesting part, so the trace below shows it step by step. The scheme is **Lomuto**: the pivot is the last element, and a single pointer `i` marks the boundary between "smaller than pivot" and "not yet looked at or larger".

### Trace: one Lomuto partition of `[3, 7, 8, 5, 2, 1, 9, 4]`

The pivot is `4` (the last item). `i` starts at index 0. For each `j` from 0 to 6: if `a[j] < 4`, swap `a[j]` with `a[i]` and advance `i`.

| j | a[j] | a[j] < 4? | Swap? | Array after this step | i after |
|---|---|---|---|---|---|
| 0 | 3 | yes | swap with itself | `[3, 7, 8, 5, 2, 1, 9, 4]` | 1 |
| 1 | 7 | no | no | `[3, 7, 8, 5, 2, 1, 9, 4]` | 1 |
| 2 | 8 | no | no | `[3, 7, 8, 5, 2, 1, 9, 4]` | 1 |
| 3 | 5 | no | no | `[3, 7, 8, 5, 2, 1, 9, 4]` | 1 |
| 4 | 2 | yes | swap a[1] and a[4] | `[3, 2, 8, 5, 7, 1, 9, 4]` | 2 |
| 5 | 1 | yes | swap a[2] and a[5] | `[3, 2, 1, 5, 7, 8, 9, 4]` | 3 |
| 6 | 9 | no | no | `[3, 2, 1, 5, 7, 8, 9, 4]` | 3 |
| end | - | - | swap pivot into a[i] = a[3] | `[3, 2, 1, 4, 7, 8, 9, 5]` | pivot at 3 |

The pivot `4` is now at index 3. Everything to its left is smaller than 4, and everything to its right is 4 or larger. The recursion then sorts the two sides:

```text
[3, 2, 1, 4, 7, 8, 9, 5]
├── left  [3, 2, 1]   -> partition around 1 -> ... -> [1, 2, 3]
└── right [7, 8, 9, 5] -> partition around 5 -> ... -> [5, 7, 8, 9]
```

Each level of the recursion does one partition of the current pieces, which is O(length) work. If the pivot always lands near the middle, there are about log2(n) levels. If it always lands at an end, there are n levels, and the total is O(n²). The next section explains why that second case is the danger.

### Why the worst case happens

Take `[1, 2, 3, 4, 5]` with the last element as pivot. The pivot `5` is the largest, so every other element goes left and the right side is empty. The next call does the same with `4`, and so on. Each partition removes one element and does linear work, which gives n + (n−1) + ... + 1 = O(n²). The same thing happens with duplicates under Lomuto: when every item equals the pivot, none is strictly smaller, so the pivot ends at the left end again.

---

## 3. Key Concepts

### Partition schemes: Lomuto and Hoare

| Feature | Lomuto | Hoare |
|---|---|---|
| How it works | One pointer `i` grows across the array; swap items smaller than the pivot to the front | Two pointers move inward from both ends; swap pairs that are on the wrong side |
| Pivot final position | Yes: the pivot is placed in its final slot | No: the pivot is somewhere inside the partition, and the split point is returned |
| Recursion after partition | `[lo, p-1]` and `[p+1, hi]` | `[lo, j]` and `[j+1, hi]` when the pivot is the first element |
| Swaps | More swaps on average | Fewer swaps on average |
| Many duplicates | Degrades: equal items all go to one side, so it approaches O(n²) | Handles them well: equal items stop both pointers and get split across both sides |
| Ease of correctness | Easy to write and check | Easy to get wrong with off-by-one bounds |

This chapter implements Lomuto because its invariant is easy to state and check: `a[lo..i-1]` are smaller than the pivot. Hoare's scheme is what most textbook and production implementations use for speed. You should be able to describe both and say why Hoare handles duplicates better.

### Pivot choice

The pivot decides the split. A bad pivot is an extreme value, so the split is 0 and n−1.

| Strategy | Good for | Weak spot | Cost |
|---|---|---|---|
| First or last element | Random input | Sorted or reversed input gives O(n²) | O(1) |
| Middle element | Already sorted input | Inputs built to defeat it | O(1) |
| Median of three (first, middle, last) | Sorted and nearly sorted input | Crafted inputs can still defeat it | 3 comparisons |
| Random element | Any input, when the input does not know the random choices | None in practice; the expected cost is O(n log n) | O(1), needs a random number generator |
| Median of medians | Guaranteed O(n) selection | Slow constant factor, rarely used for sorting | O(n) per pivot |

The random pivot is the standard answer. It does not make the worst case impossible, but no fixed input can defeat it, because the attacker does not know which element will be chosen. Median of three is a good heuristic, but an adversary who knows the algorithm can still craft a bad input for it.

### Duplicates and three-way partitioning

With many equal keys, a two-way partition keeps putting equal items on one side, so the recursion is deep and the sort is slow. A **three-way partition** (the Dutch national flag method) splits the array into three parts: less than the pivot, equal to the pivot, and greater than the pivot. The equal part is already in place, so only the two outer parts recurse. This makes sorting an array of only three distinct values O(n). The chapter's code keeps the simpler two-way Lomuto partition; the three-way version is the standard fix in production sorts.

### Quickselect

If you need only the k-th smallest item, you do not need to sort the whole array. Partition once, and the pivot lands at index p. If p equals k, you are done. If k is less than p, the answer is in the left part; otherwise it is in the right part. Recurse into that one side only.

Quickselect is O(n) on average. A random pivot splits the range roughly in half in expectation, so the total work is about n + n/2 + n/4 + ..., which is at most about 2n. Its worst case is O(n²), like quick sort. The median-of-medians algorithm guarantees O(n), but its constant factor is large, so libraries use the randomized version.

### Stability

Quick sort is not stable. Partitioning swaps items that are far apart, so two equal keys can change order. If you need a stable sort, use [merge sort](27-Merge-Sort.md) or Timsort, or add the original index as a tie-breaker.

### Complexity

| Operation | Best | Average | Worst | Extra space | Why |
|---|---|---|---|---|---|
| Quick sort (random pivot) | O(n log n) | O(n log n) | O(n²) | O(log n) stack | Balanced splits give log2(n) levels of linear work. Average splits are good enough with random pivots. Worst case: every pivot is an extreme value |
| Quick sort (fixed first or last pivot) | O(n log n) | O(n log n) | O(n²) | O(n) stack without the smaller-side trick | Sorted or reversed input triggers the worst case every time |
| Quickselect (random pivot) | O(n) | O(n) | O(n²) | O(1) iterative | Only one side recurses, and the expected sizes shrink geometrically |
| Lomuto partition | O(n) | O(n) | O(n) | O(1) | One pass with one comparison per element |

The O(log n) stack space needs one trick: recurse into the smaller partition and loop on the larger one. Without it, a bad split pattern can make the recursion as deep as n.

---

## 4. Code Examples

Scenario: a ranking service sorts scores in place for a report, finds the k-th largest score for a leaderboard cutoff, and finds the top K most frequent tags in a stream of events.

### Node.js / TypeScript

Node.js 22+ and TypeScript 5. Node's `Array.prototype.sort` does not use quick sort. V8 uses TimSort, which is stable and has an O(n log n) worst case. Using the built-in sort is almost always right. Quick sort and quickselect matter for two reasons: they are the in-place algorithms behind many native libraries (C++'s `std::sort` is introsort, a quick sort that switches to heap sort when recursion gets too deep), and quickselect is the right tool for k-th order statistics, which the built-in sort does not give you directly. JavaScript has no built-in quickselect, so the code below implements one. The partition is generic and takes a comparator, so the same code works for numbers, objects, and pairs.

```ts
// No dependencies. Node.js 22+, TypeScript 5.
import assert from "node:assert/strict";

export type Compare<T> = (a: T, b: T) => number;
export const numberAsc: Compare<number> = (a, b) => a - b;

// Lomuto partition with a random pivot. Returns the pivot's final index p:
// everything left of p is smaller than the pivot, everything right of p is not smaller.
function partition<T>(a: T[], lo: number, hi: number, cmp: Compare<T>): number {
  // A random pivot: an input that was not built with this random choice cannot force O(n^2).
  const r = lo + Math.floor(Math.random() * (hi - lo + 1));
  [a[r], a[hi]] = [a[hi], a[r]];
  const pivot = a[hi];
  let i = lo; // invariant: a[lo..i-1] are all smaller than the pivot
  for (let j = lo; j < hi; j++) {
    if (cmp(a[j], pivot) < 0) {
      [a[i], a[j]] = [a[j], a[i]];
      i++;
    }
  }
  [a[i], a[hi]] = [a[hi], a[i]]; // move the pivot into its final slot
  return i;
}

// Sorts a[lo..hi] (inclusive) in place.
function sortRange<T>(a: T[], lo: number, hi: number, cmp: Compare<T>): void {
  while (lo < hi) {
    const p = partition(a, lo, hi, cmp);
    // Recurse into the smaller side and loop on the larger one. The recursion depth
    // stays O(log n) even when the splits are unlucky.
    if (p - lo < hi - p) {
      sortRange(a, lo, p - 1, cmp);
      lo = p + 1;
    } else {
      sortRange(a, p + 1, hi, cmp);
      hi = p - 1;
    }
  }
}

// Returns a sorted copy. Average O(n log n), worst O(n^2), not stable.
export function quickSort<T>(items: readonly T[], cmp: Compare<T>): T[] {
  const a = [...items];
  sortRange(a, 0, a.length - 1, cmp);
  return a;
}

// Quickselect: the value that would sit at index k if the array were sorted.
// Average O(n), worst O(n^2). Rearranges `a` in place, so pass a copy if you need the original.
export function quickselect<T>(a: T[], k: number, cmp: Compare<T>): T {
  if (k < 0 || k >= a.length) throw new RangeError(`k=${k} is out of range for length ${a.length}`);
  let lo = 0;
  let hi = a.length - 1;
  while (lo < hi) {
    const p = partition(a, lo, hi, cmp);
    if (p === k) break; // the pivot landed exactly on k
    if (k < p) hi = p - 1; // the answer is in the left part
    else lo = p + 1;       // the answer is in the right part
  }
  return a[k];
}

// Quick checks: empty input, one element, duplicates, and a sorted input (the bad case for fixed pivots).
assert.deepEqual(quickSort([3, 7, 8, 5, 2, 1, 9, 4], numberAsc), [1, 2, 3, 4, 5, 7, 8, 9]);
assert.deepEqual(quickSort([], numberAsc), []);
assert.deepEqual(quickSort([1], numberAsc), [1]);
assert.deepEqual(quickSort([2, 2, 2, 2], numberAsc), [2, 2, 2, 2]); // correct; slow with two-way partition
assert.deepEqual(quickSort([1, 2, 3, 4, 5], numberAsc), [1, 2, 3, 4, 5]);
assert.equal(quickselect([9, 1, 5], 1, numberAsc), 5);
```

Problem 1: **kth largest element.** Given an array and `k` (1 ≤ k ≤ n), return the k-th largest value, counting duplicates separately. Approach: the k-th largest is at index `n − k` in ascending order, so run quickselect for that index on a copy. Average O(n), worst O(n²).

Problem 2: **top K frequent values.** Return the `k` values that occur most often. Approach: count occurrences with a `Map` in O(n), then quickselect the `[value, count]` pairs by count so the top `k` sit at the end. Average O(n + u), where `u` is the number of distinct values. A min-heap of size `k` gives O(n log k) in the worst case and is simpler to reason about when `k` is tiny. Quickselect wins when `k` is large and the average case is acceptable.

```ts
// No dependencies. Node.js 22+, TypeScript 5.
// Uses quickselect, numberAsc and Compare from the implementation block above.
import assert from "node:assert/strict";

// Problem 1: kth largest element (duplicates count separately).
// Approach: quickselect for index n - k in ascending order. Average O(n), worst O(n^2).
export function kthLargest(nums: readonly number[], k: number): number {
  if (!Number.isInteger(k) || k < 1 || k > nums.length) throw new RangeError("k must be between 1 and n");
  return quickselect([...nums], nums.length - k, numberAsc);
}

// Problem 2: top K frequent values (returned in no particular order).
// Approach: count with a Map, then quickselect the [value, count] pairs by count.
// Average O(n + u) where u is the number of distinct values; space O(u).
export function topKFrequent(nums: readonly number[], k: number): number[] {
  const counts = new Map<number, number>();
  for (const x of nums) counts.set(x, (counts.get(x) ?? 0) + 1);
  const entries: [number, number][] = [...counts.entries()];
  const keep = Math.min(k, entries.length);
  if (keep <= 0) return [];
  const start = entries.length - keep;
  // After this call, every entry at index >= start has a count at least as large as the one at start.
  quickselect(entries, start, (a, b) => a[1] - b[1]);
  return entries.slice(start).map(([value]) => value);
}

assert.equal(kthLargest([3, 2, 1, 5, 6, 4], 2), 5);
assert.equal(kthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4);
assert.equal(kthLargest([7], 1), 7);
assert.deepEqual(topKFrequent([1, 1, 1, 2, 2, 3], 2).sort(numberAsc), [1, 2]);
assert.deepEqual(topKFrequent([], 3), []);
```

### Python

Python 3.12+. CPython's `list.sort()` and `sorted()` use Timsort, not quick sort, and the standard library has no quickselect. There are two built-in shortcuts for the problems below. `heapq.nlargest(k, items)` and `heapq.nsmallest(k, items)` use a heap of size k. `collections.Counter(...).most_common(k)` counts and returns the top k, and it uses `heapq.nlargest` internally when you give it a k. The code below implements quickselect so you can compare it with those built-ins. The partition takes a `key` function, so the same code works for numbers and for `(value, count)` pairs.

```python
# Standard library only. Python 3.12+.
import random
from collections.abc import Callable, Sequence
from typing import Any


def _partition[T](a: list[T], lo: int, hi: int, key: Callable[[T], Any]) -> int:
    """Lomuto partition with a random pivot. Returns the pivot's final index."""
    r = random.randint(lo, hi)  # randint includes both ends
    a[r], a[hi] = a[hi], a[r]
    pivot = key(a[hi])
    i = lo  # invariant: a[lo:i] are all smaller than the pivot
    for j in range(lo, hi):
        if key(a[j]) < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def _sort_range[T](a: list[T], lo: int, hi: int, key: Callable[[T], Any]) -> None:
    while lo < hi:
        p = _partition(a, lo, hi, key)
        # Recurse into the smaller side and loop on the larger: recursion depth stays O(log n).
        if p - lo < hi - p:
            _sort_range(a, lo, p - 1, key)
            lo = p + 1
        else:
            _sort_range(a, p + 1, hi, key)
            hi = p - 1


def quick_sort[T](items: Sequence[T], key: Callable[[T], Any] = lambda x: x) -> list[T]:
    """Returns a sorted copy. Average O(n log n), worst O(n^2). Not stable."""
    a = list(items)
    _sort_range(a, 0, len(a) - 1, key)
    return a


def quickselect[T](a: list[T], k: int, key: Callable[[T], Any] = lambda x: x) -> T:
    """The value that would sit at index k if sorted. Average O(n). Rearranges `a` in place."""
    if not 0 <= k < len(a):
        raise IndexError(f"k={k} is out of range for length {len(a)}")
    lo, hi = 0, len(a) - 1
    while lo < hi:
        p = _partition(a, lo, hi, key)
        if p == k:  # the pivot landed exactly on k
            break
        if k < p:
            hi = p - 1  # the answer is in the left part
        else:
            lo = p + 1  # the answer is in the right part
    return a[k]


# Quick checks: empty input, one element, duplicates, and sorted input.
assert quick_sort([3, 7, 8, 5, 2, 1, 9, 4]) == [1, 2, 3, 4, 5, 7, 8, 9]
assert quick_sort([]) == []
assert quick_sort([1]) == [1]
assert quick_sort([2, 2, 2, 2]) == [2, 2, 2, 2]  # correct; slow with a two-way partition
assert quick_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]
assert quickselect([9, 1, 5], 1) == 5
```

Problems, using the same approach as the TypeScript block:

```python
# Standard library only. Python 3.12+.
# Uses quickselect from the implementation block above.
from collections import Counter
from collections.abc import Sequence


# Problem 1: kth largest element (duplicates count separately).
# Approach: quickselect for index n - k in ascending order. Average O(n), worst O(n^2).
def kth_largest(nums: Sequence[int], k: int) -> int:
    if not 1 <= k <= len(nums):
        raise ValueError("k must be between 1 and n")
    return quickselect(list(nums), len(nums) - k)


# Problem 2: top K frequent values (returned in no particular order).
# Approach: Counter counts in O(n); quickselect the (value, count) pairs by count.
# Average O(n + u), u = distinct values. A heap of size k gives O(n log k) worst case.
def top_k_frequent(nums: Sequence[int], k: int) -> list[int]:
    entries = list(Counter(nums).items())  # [(value, count), ...]
    keep = min(k, len(entries))
    if keep <= 0:
        return []
    start = len(entries) - keep
    quickselect(entries, start, key=lambda entry: entry[1])
    return [value for value, _ in entries[start:]]


assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert kth_largest([7], 1) == 7
assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
assert top_k_frequent([], 3) == []
```

**Runtime difference:** quick sort is a pure CPU algorithm in both runtimes, so the cost is the same shape. The difference is in what the runtime already gives you. Node.js and Python both ship a stable merge-based sort, so you would almost never write quick sort for production use. In Python, the built-in `heapq` and `Counter` cover most top-K needs without writing quickselect. In Node.js you write the helper yourself, and a long synchronous sort blocks the event loop, so for large arrays run it in a worker thread.

---

## 5. Production Concerns

- **Adversarial input.** A fixed pivot can be attacked. If user-supplied data is sorted by a naive quick sort, a crafted payload can make each request take O(n²) time. Use a random pivot, or a library sort such as TimSort or introsort, which falls back to heap sort when recursion gets deep. This is a denial-of-service risk, not just a speed issue.
- **Stack depth.** A naive recursive quick sort on a bad input can go n levels deep and overflow the call stack. Recurse on the smaller side and loop on the larger one, as the code above does.
- **Stability is not free.** If you sort records by one key and later need the earlier order preserved, quick sort silently breaks it. Choose a stable algorithm, or make the key unique with a tie-breaker.
- **Choosing quickselect for "top K" in a stream.** Quickselect needs the whole array in memory and gives a random average time. For a stream or for a huge data set, keep a min-heap of size k, which uses O(k) memory and O(n log k) time.
- **Latency spikes.** The average case hides occasional slow calls. If a sort is on the request path, measure the p99 time with realistic data, not just the average.
- **Comparator safety.** Quick sort uses the comparator for every swap decision. A comparator that is not consistent (for example, one that returns random values or `NaN`) can leave the array partly unsorted without an error. Validate the keys first.

---

## 6. Common Mistakes

- **Fixed first or last pivot on sorted input** — the recursion becomes n levels deep and takes O(n²) time, and it can overflow the stack — pick a random pivot (or median of three at least).
- **Lomuto with many duplicates** — every equal item goes to one side, so a list of identical values takes O(n²) — use a three-way partition or Hoare's scheme.
- **Off-by-one in inclusive bounds** — `hi = p` instead of `hi = p - 1` re-includes the pivot and loops forever — keep the pivot out of both recursive ranges.
- **Recursing into both sides with no depth control** — worst-case stack depth grows to n — recurse into the smaller side and loop on the larger.
- **Assuming the result is stable** — two records with equal keys swap places after the sort — use a stable sort, or add the original index as a tie-breaker.
- **Using quickselect when you need the sorted output** — quickselect only guarantees the one k-th element and the partition around it, not a full order — sort the whole array if you need all of it, or take the top K from a sorted copy.
- **Forgetting that quickselect mutates the input** — the caller's array is rearranged — copy it first, as the chapter's problem functions do.

---

## 7. Comparison Table

When the goal is the top K items, you have three real options. The table compares them.

| Approach | Time | Extra space | Output | Best for |
|---|---|---|---|---|
| Sort everything, take k | O(n log n) | O(n) or O(1) in place | Fully sorted | You need the whole order anyway |
| Min-heap of size k | O(n log k) worst case | O(k) | Top k, unordered or sorted at the end | Streams, huge data, small k |
| Quickselect | O(n) average, O(n²) worst | O(1) or O(n) for a copy | Top k as a partition, unordered | One-off query on an in-memory array, large k |

For a backend job that reads a large log and needs the top 10 values, a heap of size 10 is the safe answer: it works on a stream and never has a bad worst case. For a batch of 100,000 values already in memory where you need the 50,000th item, quickselect is faster, because it does one linear pass in expectation instead of many heap operations.

---

## 8. Interview Questions

**[Junior] What is the partition step?**
Partition rearranges the array around a pivot value. After it runs, the pivot is in the position it would have in the sorted array, every smaller item is to its left, and every larger item is to its right. The two sides are not sorted yet. Quick sort then recurses on each side.

**[Junior] Why is quick sort usually faster than merge sort in practice, even though its worst case is worse?**
It sorts in place, so it does not allocate an n-item buffer and copy data at each level. Its inner loop is sequential and cache-friendly. The average number of comparisons is about 1.39 n log2 n for random pivots, a little more than merge sort, but the constants in memory traffic are much lower. The worst case is avoided with a random pivot, so in practice it is rarely a problem.

**[Mid] Why does a fixed first-element pivot give O(n²) on sorted input?**
On sorted input, the first element is the smallest. Partitioning around it puts nothing on the left and everything else on the right. Each call removes just one element and does linear work on the rest. The sum is n + (n−1) + ... + 1, which is O(n²). A random pivot, or median of three, makes the split balanced on sorted input.

**[Mid] How do you find the top K frequent elements? Compare the heap and quickselect approaches.**
Count the frequencies with a hash map in O(n). Then either keep a min-heap of size k, which is O(n log k) worst case and works on a stream, or quickselect the (value, count) pairs by count, which is O(u) on average where u is the number of distinct values. The heap has a guaranteed bound and uses O(k) extra space. Quickselect is faster on average when k is large and the data is in memory, but it has an O(u²) worst case and needs all the data at once.

**[Senior] An attacker can make your quick sort take O(n²) time. How do you defend against it?**
The attacker needs to know the pivot rule. A fixed rule like first or last element is easy to attack. Use a random pivot, which the attacker cannot predict, so the expected cost stays O(n log n) for any input. Also cap the recursion depth, and when it exceeds about 2 log2(n), switch to heap sort, which is the introsort approach that C++'s `std::sort` uses. Finally, consider whether the sort needs to be exposed to untrusted input at all, or whether a stable merge-based sort such as Timsort is a better default.

**[Senior] Quickselect is O(n) on average. Why is median of medians not the default, and when would you use it?**
Median of medians picks a pivot guaranteed to be between the 30th and 70th percentile, so each step removes a fixed fraction of the data and the worst case is O(n). Its constant factor is large: it sorts groups of five and recurses on a set of about n/5 medians. The randomized version is usually faster in practice, and its worst case is so unlikely that it is not a practical concern. Use median of medians when you have a hard real-time bound on the selection, or when the input can be controlled by an adversary who knows the random seed.

**[Senior] You need the 99th percentile latency of a stream of 2 billion measurements. Which algorithm do you use?**
Quickselect and full sorting both need all the data in memory, which is not possible here. Use a streaming approach instead: a fixed-size histogram of latency buckets, or a streaming quantile sketch such as t-digest, which gives approximate percentiles in bounded memory. If you must be exact, sort in chunks and merge them, as in [Merge Sort](27-Merge-Sort.md), or use a min-heap of the largest 1% seen so far. The key point is that quickselect is an in-memory algorithm, and its O(n) time is only useful when the whole input fits in memory.

---

## 9. Cheat Sheet

```text
Idea             pick a pivot, partition around it, recurse on both sides
Lomuto           pointer i; swap items < pivot to the front; pivot ends at i
Hoare            two pointers from both ends; fewer swaps; better with duplicates
Time             O(n log n) average; O(n^2) worst (bad pivot every time)
Space            O(log n) stack if you recurse into the smaller side
Stable           no; use merge sort or Timsort if order of equal keys matters
Pivot            random (best default); median of three; never a fixed end on sorted input
Duplicates       two-way partition degrades; use three-way (Dutch flag) partition
Quickselect      kth smallest in O(n) average; recurse into one side only
Top K            heap of size k: O(n log k) worst; quickselect on counts: O(n) average
Built-ins        V8 and CPython sort with TimSort; C++ std::sort is introsort
Python extras    heapq.nlargest / nsmallest; Counter.most_common(k)
Node extras      none; write the helper and run big sorts off the event loop
Attack           a fixed pivot can be forced to O(n^2); randomize the pivot
```

---

## Related Topics

- [Merge Sort](27-Merge-Sort.md) — the stable O(n log n) alternative that uses extra memory, and the reason quick sort wins on speed.
- [Sorting Algorithms](26-Sorting-Algorithms.md) — stability, the n log n lower bound, and where quick sort fits in the family.
- [Heap Sort](29-Heap-Sort.md) — the in-place algorithm that gives the worst-case guarantee introsort falls back to.
- [Priority Queue](13-Priority-Queue.md) — the heap-based approach to top K, which works on streams.
- [Divide and Conquer](24-Divide-and-Conquer.md) — quick sort's recursion pattern, and why its balance decides the cost.

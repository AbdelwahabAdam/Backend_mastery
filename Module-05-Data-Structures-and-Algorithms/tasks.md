# Module 05 Practice Tasks: Implement, Solve, Apply

Three kinds of practice:

1. **Implement** core structures from scratch, with tests.
2. **Solve** timed problem sets the way an interview runs them.
3. **Apply** algorithms to small backend components.

Do the implementation tasks in **both TypeScript and Python**. Do the problem sets in the language you will interview in, then re-solve three problems in the other one.

**Rules for every task:**
- State the time and space complexity **before** you code.
- Write tests for empty input, one element, duplicates, and the largest input you claim to support.
- Use your own implementation first, then compare it with the built-in (`Map`, `heapq`, `bisect`, `deque`…).

---

## Task 1 — Complexity lab
**Chapters:** [02](02-Time-Complexity.md)–[05](05-Arrays.md) · **Level:** Beginner

**Done when**
- [ ] You time functions of O(1), O(log n), O(n), O(n log n) and O(n²) for n = 10³…10⁶, and plot or tabulate the results. You can explain any curve that doesn't match its class.
- [ ] An instrumented dynamic array counts element copies over 1,000,000 appends, showing amortized O(1). The same array growing by +10 instead of ×2 shows O(n²) copies.
- [ ] You show the cost of repeated string concatenation vs `join`/array-join for building a 10 MB string.

## Task 2 — Linear structures from scratch
**Chapters:** [07](07-Linked-Lists.md)–[10](10-Deque.md) · **Level:** Beginner

**Done when**
- [ ] A doubly linked list supports O(1) insert/remove given a node, with sentinel nodes, and its tests pass.
- [ ] A ring-buffer queue and a deque have O(1) operations at both ends, and grow when full. A benchmark shows `Array.prototype.shift()` / `list.pop(0)` slowing down as n grows, while yours does not.
- [ ] Problems solved: valid parentheses, Floyd cycle detection, and implement-queue-with-two-stacks.

## Task 3 — Hashing and heaps
**Chapters:** [11](11-Hash-Tables.md)–[14](14-Heaps.md) · **Level:** Intermediate

**Done when**
- [ ] A hash map with separate chaining resizes at load factor 0.75. A test with adversarial keys that all hash the same way shows O(n) degradation.
- [ ] A binary min-heap supports `push`, `pop`, `peek` and O(n) `heapify`. Its sorted output matches `heapq`/a sorted copy on 10,000 random inputs.
- [ ] Problems solved: two sum, group anagrams, top K frequent elements (heap version), and find median from a data stream.

## Task 4 — Trees and tries
**Chapters:** [15](15-Trees.md)–[19](19-Tries.md) · **Level:** Intermediate

**Done when**
- [ ] A BST supports insert, delete (all three cases), search and in-order iteration, and is validated after every operation in a randomized test.
- [ ] You insert 10,000 sorted keys into your BST and into a balanced structure (AVL, or a sorted list with `bisect`), and report the tree height or operation cost for each.
- [ ] A trie-based autocomplete returns the top 5 completions by frequency for a 50,000-word list in under 5 ms per query.
- [ ] Problems solved: validate BST, lowest common ancestor, and serialize/deserialize a binary tree.

## Task 5 — Graphs, search and sorting
**Chapters:** [20](20-Graphs.md)–[29](29-Heap-Sort.md) · **Level:** Intermediate

**Done when**
- [ ] BFS returns the shortest path (as a list of nodes) on a grid with walls, and iterative DFS finds connected components with no recursion-depth limit.
- [ ] Binary search passes a property test against a linear scan for `lower_bound` and `upper_bound` on 10,000 random sorted arrays with duplicates.
- [ ] Merge sort, quicksort (random pivot, three-way partition) and heap sort all match the built-in sort on random, sorted, reversed and all-equal inputs. A table compares their times.
- [ ] You show the JS `[10, 9, 1].sort()` pitfall and fix it.
- [ ] Problems solved: number of islands, word ladder, search in a rotated sorted array, and kth largest element (quickselect).

## Task 6 — Pattern drills (timed)
**Chapters:** [30](30-Two-Pointers.md)–[40](40-Monotonic-Queue.md) · **Level:** Advanced

Solve each problem in **25 minutes or less**, speaking your approach aloud or writing it down first. Record your time, and whether you needed a hint.

**Done when**
- [ ] Two pointers: container with most water; 3Sum.
- [ ] Sliding window: longest substring without repeating characters; minimum window substring.
- [ ] Prefix sum / difference array: subarray sum equals K; car pooling.
- [ ] Greedy: non-overlapping intervals; meeting rooms II.
- [ ] Backtracking: subsets; combination sum.
- [ ] Dynamic programming: house robber; edit distance (with both top-down and bottom-up versions).
- [ ] Union–find and topological sort: redundant connection; course schedule II.
- [ ] Monotonic stack/queue: daily temperatures; sliding window maximum.
- [ ] A one-page "pattern recognition" cheat sheet, in your own words: which problem signals point to which pattern.

## Task 7 — Backend components
**Chapters:** [41](41-Backend-DSA-Patterns.md)–[43](43-LRU-Cache.md) · **Level:** Advanced

**Done when**
- [ ] An LRU cache with O(1) `get`/`put` (hash map plus doubly linked list) passes a randomized test against a reference that uses `Map` insertion order / `OrderedDict`.
- [ ] A TTL cache with lazy expiry, plus a background sweep, keeps memory bounded under a load test.
- [ ] A Bloom filter sized for 1,000,000 items at a 1% false-positive rate shows a measured false-positive rate close to 1%, and **zero** false negatives.
- [ ] A token-bucket rate limiter and a sliding-window-log limiter both enforce 100 requests per minute per user. You compare their memory per user and their accuracy at window boundaries.

## Task 8 — Capstone: shard a cache cluster
**Chapters:** [44](44-Consistent-Hashing-Basics.md), plus [42](42-Cache-Data-Structures.md)–[43](43-LRU-Cache.md) · **Level:** Advanced

Build a small in-process "cluster" of N cache nodes (each one an LRU from Task 7) behind a router.

**Done when**
- [ ] With `hash(key) % N`, you measure the share of keys that move when going from 4 to 5 nodes.
- [ ] With a consistent-hash ring using 100 virtual nodes per server, the same change moves about 1/5 of the keys. You report the load spread across nodes as min/max/standard deviation.
- [ ] Replication factor 2 places each key on two distinct physical nodes, and reads still succeed after one node is removed.
- [ ] A README explains the trade-offs in a way you could repeat in a system-design interview: virtual-node count, hot keys, and rendezvous hashing as the alternative.

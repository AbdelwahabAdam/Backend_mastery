# Module 05 Data Structures and Algorithms — Quick Reference

Use this for fast revision. Every chapter has one definition, a plain-English explanation, and a small example you could say out loud in an interview. Open the linked chapter for the full note, diagrams and interview questions.

## Foundations

### [Introduction to DSA](01-Introduction-to-DSA.md)
**Definition:** A data structure is a way of storing data so that the operations you need are cheap, and an algorithm is the step-by-step method that uses it.
**Simple explanation:** The structure you pick usually matters more than the loop you write.
**Small example:** Finding duplicates among 1,000,000 IDs with a `Set` costs about 1,000,000 membership checks, while nested loops would make about 5 × 10¹¹ comparisons.

### [Time Complexity](02-Time-Complexity.md)
**Definition:** Time complexity describes how the number of operations grows as the input size n grows, written as a bound such as O(n) or O(n²) rather than as seconds.
**Simple explanation:** Count the work that depends on n, then drop constants and smaller terms.
**Small example:** Two loops nested over 1,000,000 items run about 10¹² steps (O(n²)), while two loops one after another run about 2 × 10⁶ steps (O(n)).

### [Space Complexity](03-Space-Complexity.md)
**Definition:** Space complexity is how much extra memory an algorithm needs at its peak as the input grows, including the stack frames of recursive calls.
**Simple explanation:** Time asks "how many steps?", and space asks "how much memory at the peak?".
**Small example:** Summing a 100,000-item list with recursion in Python hits the default recursion limit of 1,000 and fails, while a plain loop uses O(1) extra space.

### [Big O Analysis](04-Big-O-Analysis.md)
**Definition:** Big O is an upper bound on growth, Ω is a lower bound, Θ is a tight bound, and amortized analysis averages the cost of a sequence of operations.
**Simple explanation:** Always say which bound you mean: worst case, average case, or amortized.
**Small example:** A dynamic array's push is O(1) amortized, because a million pushes trigger about 20 resizes that copy roughly 1 million items in total, about one copy per push.

## Linear structures

### [Arrays](05-Arrays.md)
**Definition:** An array stores its items in one contiguous block of memory, so reading index i costs O(1) because the address is base + i × element size.
**Simple explanation:** Reads by index are instant, but inserting in the middle means shifting every later item.
**Small example:** `arr[500_000]` on a million-item array is one address calculation, but inserting at index 0 moves all 1,000,000 items one slot to the right.

### [Strings](06-Strings.md)
**Definition:** Strings in JavaScript and Python are immutable sequences of characters, so every edit creates a new string, and length is counted in UTF-16 code units or code points.
**Simple explanation:** Collect the pieces in a list and join them once, instead of appending to a string inside a loop.
**Small example:** Building a 100,000-piece string with `s += piece` copies the growing string on every step, while `"".join(pieces)` makes one pass over the total length.

### [Linked Lists](07-Linked-Lists.md)
**Definition:** A linked list is a chain of nodes, each holding a value and a reference to the next node, so reaching the k-th item costs O(k) steps.
**Simple explanation:** Once you hold a pointer to a spot, splicing a node in or out is cheap, but finding that spot means walking from the head.
**Small example:** Removing the node after a known pointer changes two references in O(1), but reaching the 500,000th node of a million-node list walks 500,000 links.

### [Stacks](08-Stacks.md)
**Definition:** A stack is a LIFO collection where push, pop and peek all work on one end in O(1) time, amortized for an array-backed stack.
**Simple explanation:** It is last in, first out, like a pile of plates.
**Small example:** Checking `({[]})` pushes three openers and pops them in reverse order as closers arrive, and `(((` is rejected because the stack is not empty at the end.

### [Queues](09-Queues.md)
**Definition:** A queue is a FIFO structure where enqueue adds at the back and dequeue removes from the front, and both should run in O(1) time.
**Simple explanation:** Items leave in the order they arrived, like a checkout line.
**Small example:** `list.pop(0)` on a 100,000-job Python list shifts about 100,000 items per dequeue, while `collections.deque.popleft()` removes the front in O(1).

### [Deque](10-Deque.md)
**Definition:** A deque (double-ended queue) adds and removes items at both ends in O(1) time, so it can act as a stack, a queue, or both.
**Simple explanation:** You can add or remove from either end without shifting anything.
**Small example:** `collections.deque(maxlen=5)` keeps the last five log lines, and it drops the oldest line in O(1) when the sixth line arrives.

## Hashing and priority

### [Hash Tables](11-Hash-Tables.md)
**Definition:** A hash table maps each key to a bucket through a hash function, giving O(1) expected lookup, insert and delete, with O(n) worst case when many keys collide.
**Simple explanation:** The hash turns a key into a slot number, so you jump to the slot instead of searching for the key.
**Small example:** With 1,000,000 keys and a load factor kept under 0.75, a lookup inspects about one bucket, while a list scan could inspect all 1,000,000 entries.

### [Hash Sets](12-Hash-Sets.md)
**Definition:** A hash set stores each element at most once and answers membership in O(1) expected time.
**Simple explanation:** It is a hash table with keys and no values, used to answer "have I seen this before?".
**Small example:** Intersecting a 1,000-item set with a 1,000,000-item set by iterating over the smaller one makes about 1,000 membership lookups.

### [Priority Queue](13-Priority-Queue.md)
**Definition:** A priority queue always returns the item with the best priority rather than the oldest one, through insert and extract-min (or extract-max) operations.
**Simple explanation:** It is a line where the most urgent job goes first, whatever order it arrived in.
**Small example:** Keeping the top 10 of 1,000,000 metrics with a heap of size 10 costs about 3.3 million comparisons (n log₂ 10), while sorting all of them costs about 20 million.

### [Heaps](14-Heaps.md)
**Definition:** A binary heap is a complete binary tree stored in an array where each parent is no larger than its children, so the minimum sits at index 0 in a min-heap.
**Simple explanation:** A heap guarantees only the next item, not full order, and that is all a scheduler usually needs.
**Small example:** `heapq.heappop` on a 1,000,000-item heap costs about 20 comparisons (log₂ n), because the moved last item sifts down one level per step.

## Trees

### [Trees](15-Trees.md)
**Definition:** A tree is a connected set of nodes with one root and no cycles, so n nodes always have exactly n − 1 edges.
**Simple explanation:** Every node has one parent except the root, and depth and height describe how far nodes sit from the root and from their leaves.
**Small example:** A category tree with 10,000 nodes has exactly 9,999 parent-child edges, and it can be built from `(id, parentId)` rows in one pass with a map.

### [Binary Trees](16-Binary-Trees.md)
**Definition:** A binary tree is a tree in which every node has at most two children, called left and right.
**Simple explanation:** Most binary tree algorithms apply one recursive rule to the left and right subtrees and combine the answers.
**Small example:** Computing the diameter of a 1,000,000-node tree takes one post-order pass of 1,000,000 visits, returning each subtree's height as it goes.

### [Binary Search Trees](17-Binary-Search-Trees.md)
**Definition:** A binary search tree keeps every left-subtree key smaller and every right-subtree key larger than its node, so search, insert and delete cost O(h), where h is the height.
**Simple explanation:** The sorted order lives in the shape of the tree, so each comparison throws away one whole side.
**Small example:** Inserting 1 through 100,000 in order into a plain BST makes a chain of height 100,000, so finding 100,000 takes 100,000 steps, while a balanced tree of the same keys needs about 17.

### [Balanced Trees](18-Balanced-Trees.md)
**Definition:** A balanced tree such as an AVL tree, a red–black tree or a B-tree keeps its height at O(log n) for any insert order.
**Simple explanation:** Rotations or node splits repair the shape after each change, so the worst case stays logarithmic.
**Small example:** A B-tree index with about 500 keys per page covers 1,000,000 rows in 3 levels, so a point lookup reads about 3 pages from disk.

### [Tries](19-Tries.md)
**Definition:** A trie stores strings by sharing common prefixes along root-to-node paths, so insert, search and prefix checks cost O(L) for a word of length L.
**Simple explanation:** Each path from the root spells out a prefix, which is how autocomplete finds every word that starts with `app`.
**Small example:** Looking up `application` (11 characters) in a trie holding a million words takes 11 child-map steps, no matter how many words are stored.

## Graphs and search

### [Graphs](20-Graphs.md)
**Definition:** A graph is a set of vertices joined by edges, which can be directed, undirected or weighted.
**Simple explanation:** Most real systems are sparse, so you store only the neighbours each node actually has.
**Small example:** A service graph with 500 services and 2,000 calls takes 2,000 adjacency-list entries, instead of a 250,000-cell matrix.

### [Breadth First Search](21-Breadth-First-Search.md)
**Definition:** Breadth-first search visits vertices in rings by distance from the start, using a FIFO queue, and runs in O(V + E) time.
**Simple explanation:** In an unweighted graph, the first time BFS reaches a node is the shortest distance to it.
**Small example:** Finding the fewest hops between two users in a graph of 1,000,000 users and 10,000,000 follow edges touches each vertex and edge once, about 11 million steps.

### [Depth First Search](22-Depth-First-Search.md)
**Definition:** Depth-first search follows one path as deep as it can before backtracking, using a stack and a visited record, and runs in O(V + E) time.
**Simple explanation:** It is the natural tool for finding cycles, connected components and post-order work.
**Small example:** In a config-include graph of 5,000 files, one three-colour DFS finds a cycle when it reaches a grey (on-path) file, in one O(V + E) pass.

### [Recursion](23-Recursion.md)
**Definition:** Recursion solves a problem by calling the same function on a smaller input until a base case stops it, and each active call holds one stack frame.
**Simple explanation:** Recursion is clear when the depth is small and under your control, and dangerous when user input decides the depth.
**Small example:** Plain recursive Fibonacci for n = 40 makes about 331 million calls, while a memoized version computes only 41 distinct values.

### [Divide and Conquer](24-Divide-and-Conquer.md)
**Definition:** Divide and conquer splits a problem into independent subproblems, solves each recursively and combines the answers, with running time given by T(n) = a·T(n/b) + f(n).
**Simple explanation:** The master theorem reads that recurrence and tells you whether splitting or combining dominates the cost.
**Small example:** Merge sort on 1,000,000 items follows T(n) = 2T(n/2) + O(n), which gives O(n log n), about 20 million merge steps.

### [Binary Search](25-Binary-Search.md)
**Definition:** Binary search finds a target in a sorted or monotonic range by discarding half of the remaining candidates each step, in O(log n) time.
**Simple explanation:** Use one template everywhere, with a half-open range and a clear invariant, so the boundary cases stay correct.
**Small example:** Finding one value among 1,000,000,000 sorted timestamps takes about 30 comparisons, and `bisect_left` returns the first index where the value could be inserted.

## Sorting

### [Sorting Algorithms](26-Sorting-Algorithms.md)
**Definition:** A comparison sort needs Ω(n log n) comparisons in the worst case, and a sort is stable when equal keys keep their original order.
**Simple explanation:** Compare sorts by stability, memory and worst-case behaviour, not only by average speed.
**Small example:** Python's `sorted()` is stable, so sorting a million user records by name and then by city keeps names in order inside each city.

### [Merge Sort](27-Merge-Sort.md)
**Definition:** Merge sort splits an array in half, sorts each half recursively and merges the results in one linear pass, giving O(n log n) time in every case and O(n) extra space.
**Simple explanation:** It is stable and predictable, which is why it is the sort to know by heart.
**Small example:** Merging two sorted lists of 500,000 items each takes about 1,000,000 steps, and counting inversions during the same merge answers "how many out-of-order pairs?" in the same pass.

### [Quick Sort](28-Quick-Sort.md)
**Definition:** Quick sort partitions the array around a pivot and recurses on each side, averaging O(n log n) time with O(log n) stack space and O(n²) in the worst case.
**Simple explanation:** It is fast in practice because it sorts in place, but a bad pivot choice makes it quadratic.
**Small example:** Quickselect finds the 5th-largest of 1,000,000 numbers in O(n) on average, because it recurses into only one side at each step.

### [Heap Sort](29-Heap-Sort.md)
**Definition:** Heap sort builds a max-heap in O(n) and then repeatedly moves the largest item to the end and sifts the new root down, giving O(n log n) time in every case with O(1) extra space.
**Simple explanation:** It has a safe worst case and sorts in place, but it is not stable and is often slower than quick sort on real hardware.
**Small example:** Sorting 1,000,000 numbers with heap sort does about 20 sift-down steps per element, roughly 2 × 10⁷ steps, with no second array.

## Problem-solving patterns

### [Two Pointers](30-Two-Pointers.md)
**Definition:** Two pointers walk through one or two sequences with indexes that move under a clear rule, so each element is visited once instead of once per pair.
**Simple explanation:** Move only the pointer that cannot improve the answer, and never move it back.
**Small example:** Two Sum on a sorted array of 1,000,000 numbers, with one pointer at each end, needs at most 1,000,000 steps, instead of about 5 × 10¹¹ pair checks.

### [Sliding Window](31-Sliding-Window.md)
**Definition:** A sliding window keeps a contiguous range `[left, right]` of an array or string, adding on the right and removing on the left, so each element enters and leaves once.
**Simple explanation:** Update the window's state as its edges move instead of recomputing each range from scratch.
**Small example:** The longest substring without repeated characters in a 1,000,000-character string takes one pass with a last-seen map, about 1,000,000 steps.

### [Prefix Sum](32-Prefix-Sum.md)
**Definition:** A prefix sum array stores running totals so that the sum of any range `values[l..r]` is `prefix[r + 1] − prefix[l]`, which is O(1) after O(n) preprocessing.
**Simple explanation:** Pay for one pass up front, then answer every range question with a subtraction.
**Small example:** After one pass over 1,000,000 daily usage values, the billing total for days 300 to 400 is one subtraction, `prefix[401] − prefix[300]`.

### [Difference Array](33-Difference-Array.md)
**Definition:** A difference array stores the change between neighbouring cells, so adding a value to an inclusive range `[l, r]` costs O(1), and one prefix-sum pass recovers the values.
**Simple explanation:** It turns many range updates into two point edits each.
**Small example:** Adding one seat to seats 10 through 4,000 in a 10,000-seat array changes only `diff[10]` and `diff[4001]`, and one O(n) pass recovers every count.

### [Greedy Algorithms](34-Greedy-Algorithms.md)
**Definition:** A greedy algorithm makes the locally best choice at each step and never revisits it, which is correct only when the greedy-choice property and optimal substructure both hold.
**Simple explanation:** The hard part is the proof, usually an exchange argument, rather than the code.
**Small example:** Interval scheduling sorted by end time keeps `[1,3]` and `[4,6]` from `[1,3]`, `[2,5]`, `[4,6]`, which is the maximum of two non-overlapping meetings.

### [Backtracking](35-Backtracking.md)
**Definition:** Backtracking builds a solution one choice at a time, recurses, then undoes the choice, and it prunes any branch that breaks a constraint.
**Simple explanation:** It is brute force with an undo step and early exits.
**Small example:** Generating all subsets of a 20-item list visits 2²⁰, about 1 million subsets, while the 20! ≈ 2.4 × 10¹⁸ permutations of the same list would be out of reach.

### [Dynamic Programming Fundamentals](36-Dynamic-Programming-Fundamentals.md)
**Definition:** Dynamic programming solves a problem by storing the answer to each overlapping subproblem once, with its state, transition, base cases and fill order defining the algorithm.
**Simple explanation:** Start from plain recursion, add a cache for memoization, then turn the cache into a bottom-up table.
**Small example:** Edit distance between two 1,000-character strings fills a 1,000 × 1,000 table of about 1 million cells, instead of exploring an exponential number of edit sequences.

### [Union Find](37-Union-Find.md)
**Definition:** Union find, also called disjoint set union, tracks groups that only merge and answers `find` and `union` in amortized O(α(n)) time with path compression and union by size.
**Simple explanation:** It answers "are these two items already in the same group?" almost instantly.
**Small example:** While merging 1,000,000 duplicate records, each new pair costs two near-constant `find` calls, and the first pair whose roots already match reveals a redundant link.

### [Topological Sorting](38-Topological-Sorting.md)
**Definition:** A topological sort orders the nodes of a directed graph so that every edge `u → v` puts `u` before `v`, and it exists only when the graph has no cycles.
**Simple explanation:** Kahn's algorithm removes nodes with no unfinished prerequisites, and any node left over means a cycle.
**Small example:** For tasks `A → B → C`, Kahn's algorithm emits A, B, C; if C also had to come before A, no node would reach zero in-degree, and the sort would emit nothing.

### [Monotonic Stack](39-Monotonic-Stack.md)
**Definition:** A monotonic stack keeps its values in sorted order by popping any entries that break the order before each push, so next-greater queries run in O(n) overall.
**Simple explanation:** Each index is pushed once and popped at most once.
**Small example:** For daily temperatures `[73, 74, 75, 71, 69, 72]`, one left-to-right pass gives the next-warmer-day distances `[1, 1, 4, 2, 1, 0]`.

### [Monotonic Queue](40-Monotonic-Queue.md)
**Definition:** A monotonic queue is a deque whose values stay sorted, so its front always holds the sliding-window maximum, in O(n) total time for any window size k.
**Simple explanation:** Drop expired indexes at the front and smaller values at the back, so the answer is always at the front.
**Small example:** The maximum of every window of size 3 over `[1, 3, -1, -3, 5, 3, 6, 7]` is `[3, 3, 5, 5, 6, 7]`, computed in one pass.

## Backend applications

### [Backend DSA Patterns](41-Backend-DSA-Patterns.md)
**Definition:** Backend DSA patterns map common production needs, such as deduplication, top-K, rate limiting, routing and dependency resolution, onto specific data structures.
**Simple explanation:** Recognise the production problem first, then name the structure that solves it.
**Small example:** Deduplicating webhook events across three servers with Redis `SET key value NX EX 86400` costs one round trip per event, while an in-process set would miss duplicates handled by another server.

### [Cache Data Structures](42-Cache-Data-Structures.md)
**Definition:** A cache is a bounded map whose eviction policy (LRU, LFU, FIFO) decides which entry leaves when it is full, and whose expiry rule decides when an entry is stale.
**Simple explanation:** A size limit bounds memory, a TTL bounds staleness, and most caches need both.
**Small example:** A Bloom filter for 1,000,000 items at a 1% false-positive rate needs about 9.6 million bits (1.2 MB) and 7 hash functions.

### [LRU Cache](43-LRU-Cache.md)
**Definition:** An LRU cache evicts the least recently used key when it is full, and its `get` and `put` both run in O(1) time using a hash map plus a doubly linked list.
**Simple explanation:** Each access moves a key to the front of a list, and eviction removes the item at the back.
**Small example:** With capacity 2, the sequence `put(a)`, `put(b)`, `get(a)`, `put(c)` evicts `b`, because `a` was used more recently.

### [Consistent Hashing Basics](44-Consistent-Hashing-Basics.md)
**Definition:** Consistent hashing places servers and keys on a hash ring, assigns each key to the first server clockwise, and so moves only about 1/(N+1) of the keys when a node is added.
**Simple explanation:** Changing the server count moves keys in one arc of the ring, unlike `hash(key) % N`, which reshuffles nearly everything.
**Small example:** Going from 4 to 5 servers with `hash(key) % N` remaps about 80% of 1,000,000 keys, while a hash ring moves only about 200,000 keys, all to the new server.

## How to revise

1. Read each **Definition** line aloud.
2. Explain the example without looking, then say what goes wrong if you use the naive method.
3. For each example, say the complexity out loud and name the chapter that proves it.

## Related module resources

- [Module overview](README.md)
- [Module summary](module-summary.md)
- [Interview questions](interview_questions.md)
- [Practical tasks](tasks.md)

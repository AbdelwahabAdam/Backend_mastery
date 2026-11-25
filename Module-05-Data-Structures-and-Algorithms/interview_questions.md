# Module 05 Interview Questions

Each chapter ends with questions about its own topic. The questions here **cut across chapters**, the way backend coding and design interviews really go: a complexity question turns into a data-structure choice, which turns into a production concern.

**How to answer:** direct answer first, then the mechanism, then a trade-off or failure case. State the complexity every time, in both time and space. For Senior questions, end with how you would detect the problem in production (a metric, a benchmark, or a log line).

Levels: **[Junior]** definitions and basic operations · **[Mid]** trade-offs and standard coding-round solutions · **[Senior]** design under load, scale and failure.

Model answers use **TypeScript** and **Python** names where the language matters. Read the chapter linked in each question for the full worked example.

---

## A. Complexity and analysis

### 1. [Junior] Why is `push` on a dynamic array O(1), when one push can copy the whole array?
*Chapters: [05](05-Arrays.md), [04](04-Big-O-Analysis.md)*

A single push is O(n) when the backing store is full, because the array allocates about twice the capacity and copies every element. That expensive push happens only at sizes 1, 2, 4, 8 and so on. Across n pushes the total copying is at most about 2n, so the cost averaged over all pushes is O(1). This is **amortized** O(1): the bound holds for any sequence of operations, not for each one. Say this explicitly, because a latency-sensitive path cares about the occasional O(n) spike, which amortized analysis hides.

### 2. [Mid] A hash lookup is "O(1)". When is it O(n), and why does that matter for a public API?
*Chapters: [11](11-Hash-Tables.md), [04](04-Big-O-Analysis.md)*

The average cost is O(1) only if the hash spreads keys evenly and the load factor stays bounded by resizing. The worst case is O(n), when many keys land in the same bucket. Python randomizes string hashes per process, which makes it hard to craft collisions from outside. A structure with a fixed or predictable hash, however, can be attacked with keys chosen to collide, turning each request into a linear scan. The defence is a randomized or keyed hash, and a limit on the size of user-supplied maps and headers. State "average O(1), worst O(n)" every time you use a hash table in an interview.

### 3. [Mid] A recursive DFS over a path graph of 100,000 nodes uses how much space?
*Chapters: [03](03-Space-Complexity.md), [23](23-Recursion.md)*

The visited set is O(V), and the recursion depth on a path is V, so the call stack is O(V) as well. Auxiliary space is O(V) and the time is O(V + E). The space is not the issue in principle; the stack is. Python's default recursion limit is 1,000, so the recursive version raises `RecursionError` long before 100,000 frames. Node throws `RangeError: Maximum call stack size exceeded` at a depth set by the engine and the frame size. Rewrite it with an explicit stack, which keeps the same O(V) bound but moves it to the heap where it is limited only by memory.

### 4. [Senior] Naive quicksort takes O(n²) on an already sorted array. How do you prevent that in production code?
*Chapters: [28](28-Quick-Sort.md), [04](04-Big-O-Analysis.md)*

With the first or last element as pivot, every partition on sorted input is size n−1 and 0, so the time is O(n²) and the recursion depth is O(n). Three fixes work together. Choose a random pivot, which gives expected O(n log n) for any input order. Use median-of-three as a cheaper deterministic option. Recurse into the smaller partition and loop on the larger one, which caps the stack at O(log n). In production you would rather not write your own sort at all: use the platform sort, which has a guaranteed O(n log n) worst case. To detect the problem, benchmark sort time against input size on sorted, reversed and random data, and watch for a super-linear curve.

### 5. [Senior] A dynamic array shrinks when it is half empty. What goes wrong with an alternating push and pop?
*Chapters: [05](05-Arrays.md), [04](04-Big-O-Analysis.md)*

If the array shrinks to half its capacity as soon as it is half full, a sequence of push, pop, push, pop around the boundary triggers a full copy on every operation. Each operation then costs O(n), and the amortized O(1) guarantee is gone. The fix is hysteresis: grow when full, but shrink only when the array is a quarter full, and shrink to half the capacity. That keeps the amortized bound for every sequence. In production you would catch this by counting element copies per operation, or by a latency spike on a workload that oscillates around a size threshold.

---

## B. Choosing data structures

### 6. [Junior] Array or linked list: which do you choose for a list of 10,000 items that you read by index and append to?
*Chapters: [05](05-Arrays.md), [07](07-Linked-Lists.md)*

An array. Reading by index is O(1) on an array and O(n) on a linked list, and appending is amortized O(1) on an array. The array's elements are contiguous in memory, so scanning them uses the CPU cache well, while each linked-list node is a separate allocation. A linked list wins when you already hold a node and need to insert or remove next to it in O(1), such as an LRU cache's recency list. Default to the array and switch only when you have a measured reason.

### 7. [Mid] When is a sorted array a better priority queue than a binary heap?
*Chapters: [14](14-Heaps.md), [13](13-Priority-Queue.md)*

When the data is built once and then only read, or when you only pop from the end. A sorted array supports O(log n) search and O(1) access to the minimum or maximum, and it is cache-friendly. A binary heap gives O(log n) insert and O(log n) removal of the minimum, which is what you need when inserts and pops interleave. Inserting into a sorted array costs O(n) because the elements after the insertion point shift. If the workload is "insert 1 job, run the earliest job, repeat", use a heap.

### 8. [Mid] A balanced BST and a hash table both store key–value pairs. Which one do you choose, and why?
*Chapters: [17](17-Binary-Search-Trees.md), [18](18-Balanced-Trees.md), [11](11-Hash-Tables.md)*

For pure key lookup, a hash table: O(1) average for get and put, against O(log n) for a balanced tree. The balanced tree wins when you need order. It answers "smallest key greater than x", range queries, minimum, maximum and in-order iteration in O(log n) time. A hash table gives none of these without a full scan. An unbalanced BST can degrade to O(n) on sorted input, so the "BST" in the comparison means a self-balancing tree such as a red–black tree or a B-tree. Mention the memory overhead of both: a hash table keeps spare capacity, and a tree keeps pointers.

### 9. [Mid] When is a trie better than a hash set for storing words?
*Chapters: [19](19-Tries.md), [12](12-Hash-Sets.md)*

A hash set answers "is this exact word present?" in O(L), where L is the length of the word, and it is smaller and simpler. It cannot answer prefix queries without scanning every key. A trie answers "which words start with `pre`?" in O(L) to reach the prefix, plus time proportional to the number of results. The price is memory: each node holds child pointers or a map, which is heavy and cache-unfriendly for large vocabularies. Use a trie for autocomplete and prefix search, and a hash set for deduplication and exact membership.

### 10. [Senior] Design the data structure behind a live leaderboard: top 100 of 10 million users, with scores changing constantly.
*Chapters: [17](17-Binary-Search-Trees.md), [18](18-Balanced-Trees.md), [14](14-Heaps.md)*

A heap alone is weak here. It finds the top 100 well, but removing or changing an arbitrary user's score means a search, and lazy deletion makes the heap grow with every update. Use an ordered index: a balanced tree or a skip list, plus a hash map from user ID to score. An update removes the old entry and inserts the new one, which is O(log n). The top 100 is read by walking the first 100 entries, which is O(log n + 100). Redis sorted sets are exactly this design, with `ZADD` for updates and `ZREVRANGE` for the top K, and ties broken by user ID. Detect trouble by tracking update latency and the size of the index, and by comparing the top 100 with a periodic full recomputation to catch drift.

---

## C. Coding-round problems

### 11. [Mid] How would you find the top K most frequent elements in an array?
*Chapters: [11](11-Hash-Tables.md), [13](13-Priority-Queue.md)*

First count frequencies with a hash map in O(n). Then keep a min-heap of at most K entries keyed by frequency. For each (value, count) pair, push it, and pop when the heap grows past K, so the heap always holds the K largest counts seen so far. The result is O(n log K) time and O(n) space for the map plus O(K) for the heap. If the frequencies are bounded by n, bucket sort by count gives O(n) time. In an interview, say the heap version first, because it generalizes to streams.

### 12. [Mid] How do you count the number of islands in a grid of `'1'` and `'0'`?
*Chapters: [21](21-Breadth-First-Search.md), [22](22-Depth-First-Search.md)*

Scan every cell. When you find an unvisited `'1'`, increment the count and flood-fill everything connected to it, using BFS or an iterative DFS, marking cells as visited as you go, for example by overwriting them with `'0'`. Each cell is enqueued or pushed at most once, so the time is O(R·C) for an R-by-C grid. The extra space is the queue or stack, which is O(R·C) in the worst case. Prefer an explicit stack over recursion, since a grid can be large enough to exceed the recursion limit.

### 13. [Mid] How do you order courses given prerequisites, and detect an impossible schedule?
*Chapters: [38](38-Topological-Sorting.md), [20](20-Graphs.md)*

Model each course as a vertex and each prerequisite as a directed edge. Use Kahn's algorithm: compute the in-degree of each vertex, put all zero in-degree vertices in a queue, and repeatedly remove one, emitting it and decrementing the in-degree of its neighbours. A neighbour whose in-degree reaches zero joins the queue. If the number of emitted courses is less than the total, the remaining courses are in a cycle, and no valid schedule exists. The time is O(V + E) and the space is O(V + E) for the adjacency lists.

### 14. [Mid] Find the length of the longest substring without repeating characters.
*Chapters: [31](31-Sliding-Window.md), [11](11-Hash-Tables.md)*

Use a variable-size sliding window with a left and right pointer, and a map from each character to its last index. Move the right pointer one character at a time. If the new character was last seen at an index inside the current window, move the left pointer just past that index. Track the maximum window length as you go. This is O(n) time, since each pointer only moves forward. The space is O(min(n, alphabet size)) for the map. State the invariant: the window always contains distinct characters.

### 15. [Mid] Find the kth largest element of an array.
*Chapters: [13](13-Priority-Queue.md), [28](28-Quick-Sort.md)*

Keep a min-heap of size K. Scan the array, pushing each value and popping the minimum when the heap exceeds K. At the end, the heap's root is the kth largest. This is O(n log K) time and O(K) space, and it works on a stream. Quickselect partitions around a pivot and recurses into one side, for an expected O(n) time, but its worst case is O(n²) without a random pivot, and it reorders the input. Mention both, and say which one you would ship and why.

### 16. [Senior] Implement an LRU cache with O(1) `get` and `put`.
*Chapters: [43](43-LRU-Cache.md), [42](42-Cache-Data-Structures.md)*

Combine a hash map from key to node with a doubly linked list ordered from most to least recently used. Use sentinel head and tail nodes so insertion and removal never need null checks. A `get` looks up the node, moves it to the front and returns its value. A `put` updates or inserts the node at the front, and if the size exceeds the capacity, it removes the tail node and deletes its key from the map. Both operations are O(1) time, and the space is O(capacity). A singly linked list cannot unlink a node in O(1), which is why the list must be doubly linked. In production, the single-process version needs a lock or a per-shard design under concurrency.

### 17. [Senior] Return the maximum of every window of size K in an array of n numbers.
*Chapters: [40](40-Monotonic-Queue.md), [31](31-Sliding-Window.md)*

Use a monotonic deque of indices whose values are decreasing from front to back. For each index i, first pop from the back while the value there is less than or equal to `nums[i]`, since those values can never be a window maximum again. Then push i. Pop from the front if its index has left the window, that is, is at most i − K. The front index is the current window's maximum. Each index enters and leaves the deque once, so the time is O(n) and the space is O(K). In JavaScript, use an index head pointer rather than `Array.prototype.shift`, which can be O(n) on large arrays.

### 18. [Senior] Compute the edit distance between two strings and say what it costs in time and space.
*Chapters: [36](36-Dynamic-Programming-Fundamentals.md)*

Let `dp[i][j]` be the minimum number of inserts, deletes and replacements that turn the first i characters of A into the first j characters of B. The base cases are `dp[i][0] = i` and `dp[0][j] = j`. The transition is `dp[i][j] = dp[i-1][j-1]` when the characters match, and otherwise one plus the minimum of `dp[i-1][j]`, `dp[i][j-1]` and `dp[i-1][j-1]`. The table has m·n cells, so the time is O(m·n). Each row depends only on the previous row, so you can keep two rows and use O(min(m, n)) space. Recovering the actual edit script needs the full table, or a second pass with the stored choices.

### 19. [Senior] Serialize a binary tree to a string and rebuild it exactly.
*Chapters: [16](16-Binary-Trees.md), [15](15-Trees.md)*

Use a preorder traversal. Write each node's value, and write a marker such as `#` for each null child, separated by commas so that values with several digits are unambiguous. To deserialize, read the tokens in the same order with a shared index or iterator: a `#` yields null, and any other token creates a node and recurses into its left and then right subtree. Both directions are O(n) time, and the space is O(n) for the string and the output tree. The recursion depth equals the tree height, which is O(n) for a skewed tree, so use an explicit stack for very deep input. Level-order (BFS) serialization is the alternative, and it also works.

---

## D. Sorting and searching

### 20. [Junior] What does a stable sort guarantee, and why does it matter?
*Chapter: [26](26-Sorting-Algorithms.md)*

A stable sort keeps the relative order of elements that compare equal. Sorting a list of orders by date and then, with a stable sort, by customer gives each customer's orders in date order. Merge sort, insertion sort and TimSort are stable. Heap sort is not stable, and the usual in-place quicksort is not stable either. Python's `sorted` and JavaScript's `Array.prototype.sort` have been stable since ES2019, so you can rely on it. Say which guarantee you need before you choose an algorithm.

### 21. [Mid] Write a binary search that finds the first index where a condition becomes true. Where do off-by-one errors hide?
*Chapter: [25](25-Binary-Search.md)*

Use a half-open interval `[lo, hi)` with `hi = n`, and loop while `lo < hi`. Compute `mid = lo + floor((hi - lo) / 2)`, which avoids overflow in languages with fixed-width integers. If `predicate(mid)` is true, set `hi = mid`; otherwise set `lo = mid + 1`. At the end, `lo` is the answer, or n if the predicate never holds. Errors hide in mixing the two conventions, returning `mid` when you meant `lo`, and using `hi = n - 1` with `while (lo <= hi)`. Test with an empty array, one element, and runs of duplicates.

### 22. [Senior] You must sort a 100 GB log file on a machine with 4 GB of RAM. How?
*Chapters: [27](27-Merge-Sort.md), [14](14-Heaps.md)*

Use an external merge sort. First, read chunks that fit in memory, sort each chunk, and write it to disk as a sorted run. Then merge the runs with a k-way merge: a min-heap holds the current head of each run, and you repeatedly pop the smallest and push the next element from the same run. The sort does O(n log n) comparisons in total, and the disk access is sequential, which is what disks do well. If the number of runs is larger than the number of buffers you can afford, merge in several passes. Measure the bytes read and written, and the number of passes, because disk I/O dominates the run time, not the comparisons.

---

## E. Graphs

### 23. [Junior] When do you use BFS and when do you use DFS?
*Chapters: [21](21-Breadth-First-Search.md), [22](22-Depth-First-Search.md)*

BFS explores by layers from a queue. In an unweighted graph, the first time it reaches a vertex gives the shortest number of edges to that vertex, so use it for shortest paths and "minimum number of moves" problems. DFS goes deep first, using a stack or recursion, and it is the natural tool for connectivity, cycle detection, topological ordering and backtracking. Both run in O(V + E) time. BFS needs memory proportional to the widest layer, and DFS needs memory proportional to the depth.

### 24. [Mid] How do you detect a cycle in a directed graph, and in an undirected one?
*Chapters: [22](22-Depth-First-Search.md), [38](38-Topological-Sorting.md)*

For a directed graph, run a DFS that colours vertices white (unvisited), grey (on the current path) and black (finished). An edge to a grey vertex is a back edge, which means a cycle. Equivalently, run Kahn's algorithm and check whether every vertex is emitted. For an undirected graph, a DFS finds a cycle when it meets a visited neighbour that is not the parent of the current vertex. Union–find does it too: an edge whose endpoints are already in one set closes a cycle. All three run in O(V + E), apart from union–find, which costs close to O(E α(V)).

### 25. [Mid] How does union–find answer "are these two vertices connected?" in almost constant time?
*Chapter: [37](37-Union-Find.md)*

Each set is a tree whose root is its representative. `find` walks up to the root, and `union` attaches one root under the other. Two optimizations make this fast. Union by rank or size attaches the shallower tree under the deeper one, and path compression points every node on the search path directly at the root. Together they give an amortized cost of O(α(n)) per operation, where α is the inverse Ackermann function, which is at most about 4 for any input you will meet. Use it for connected components, the redundant-edge problem and Kruskal's minimum spanning tree. It cannot split sets, so use it when edges are only added.

---

## F. Backend applications

### 26. [Senior] Why do database B-tree indexes have such a large fan-out, and how does that set the lookup cost?
*Chapter: [18](18-Balanced-Trees.md)*

A B-tree node is one disk page, for example about 8 KB in PostgreSQL, and it holds hundreds of keys. The fan-out is therefore in the hundreds, so a table with a billion rows needs only three or four levels. Each level costs one page read, and the upper levels usually stay in memory. A binary tree on disk would need about log₂(n) ≈ 30 page reads for the same rows. Leaves are linked, so a range scan reads adjacent leaves without going back up the tree. To check this in production, look at the plan (`EXPLAIN ANALYZE`) for the index scan and its buffer reads, and at index size and bloat.

### 27. [Senior] How does consistent hashing spread cache keys across nodes, and what does adding a node cost?
*Chapter: [44](44-Consistent-Hashing-Basics.md)*

Hash each node and each key onto a ring, and assign a key to the first node clockwise from its hash. Adding a node moves only the keys between it and its predecessor, about 1/N of them for N nodes. Modulo hashing (`hash(key) % N`) reshuffles almost every key when N changes, which empties caches at once. Virtual nodes place each physical node at many points on the ring, which evens out the load. A lookup is O(log V) for V points on the ring, using a sorted array and binary search. Detect a bad distribution by tracking the share of keys and requests per node, and alert on skew.

### 28. [Senior] How does a Bloom filter save database lookups, and what can it get wrong?
*Chapter: [42](42-Cache-Data-Structures.md)*

A Bloom filter is a bit array of m bits and k hash functions. Insert sets k bits for the key. A query returns "definitely not present" if any of its k bits is zero, and "probably present" otherwise. It never gives false negatives, so a "no" is always correct. Its false-positive rate is about (1 − e^(−kn/m))^k, which you tune with m and k. Put it in front of an expensive lookup, such as a username-availability check or a cache-penetration guard, so that most misses never reach the database. A standard Bloom filter cannot delete; use a counting variant if you need that. Detect saturation by tracking the fill ratio of the bits, and the false-positive rate on sampled misses.

### 29. [Senior] Design a rate limiter for an API that runs on ten servers and shares its counters in Redis.
*Chapters: [31](31-Sliding-Window.md), [41](41-Backend-DSA-Patterns.md)*

A token bucket is a good default: each key holds a token count that refills at rate r up to a capacity b, and each request spends one token. It is O(1) per request, allows short bursts, and needs only two numbers per key. A sliding-window log is exact but stores a timestamp per request, so it costs O(requests) memory. A sliding-window counter approximates it with two fixed windows and a weighted sum. The distributed part is atomicity: read, check and update must happen as one step, which a Lua script in Redis gives you, and the time should come from Redis, not from each server's clock. Measure the reject rate per key and the latency added by the Redis call, and alert when a key's reject rate jumps.

### 30. [Senior] Design the scheduler that runs delayed jobs (run at time T) for a backend.
*Chapters: [13](13-Priority-Queue.md), [14](14-Heaps.md)*

Keep jobs in a min-heap keyed by run time. The worker sleeps until the time of the top job, then pops every job that is due, and inserting or popping costs O(log n). A single in-memory heap loses every pending job when the process dies, so it must be persisted. A common production version is a Redis sorted set with the run time as the score: `ZADD` schedules a job, `ZRANGEBYSCORE` fetches the due ones, and a claim step removes them so that another worker cannot run the same job. In SQL, a `run_at` index with `FOR UPDATE SKIP LOCKED` does the same job. Whatever the store, jobs must be idempotent, because a worker can crash between running a job and marking it done. Detect a stall by watching the age of the oldest due job.

---

## G. Node.js and Python specifics

### 31. [Junior] Your Node service needs a priority queue. What is available, and what does Python's `heapq` give you?
*Chapters: [14](14-Heaps.md), [13](13-Priority-Queue.md)*

JavaScript has no built-in heap or priority queue. You implement a binary heap on an array, which is about 40 lines, or use a tested library. Python's `heapq` module implements a min-heap on a plain list, and it provides no max-heap. For a max-heap, push negated keys, or push tuples such as `(-priority, sequence, item)`. The sequence number breaks ties, because comparing two items that do not support `<` raises an error. Say which one you chose and why, since interviewers often ask this in the same breath.

### 32. [Junior] Is `Map` the same as a plain object for counting keys in Node? What about `dict` in Python?
*Chapter: [11](11-Hash-Tables.md)*

A JavaScript `Map` accepts any key type, compares objects by identity, keeps insertion order, and exposes `size` directly. A plain object takes only strings and symbols as keys, has prototype properties such as `toString` and `__proto__` that collide with user keys, and orders integer-like keys first in ascending order. Use `Map` for counting and dictionaries of user input. Python's `dict` keeps insertion order as a language guarantee since Python 3.7 and accepts any hashable key. Both give average O(1) get and set.

### 33. [Mid] A Node queue uses `array.shift()` and Python uses `list.pop(0)`. Why are they slow, and what do you use instead?
*Chapters: [10](10-Deque.md), [09](09-Queues.md)*

Python's `list.pop(0)` removes the first element and shifts all the others, so it is O(n). Use `collections.deque`, where `popleft` and `append` are both O(1). JavaScript's `Array.prototype.shift` is not guaranteed to be O(1): engines may move the elements, and the cost grows with the queue length. For a queue in Node, keep a head index and advance it, then compact the array occasionally, or use a linked-list-based queue. Benchmark with a queue of a million items, because small queues hide the problem.

### 34. [Mid] Your Python recursion raises `RecursionError` at depth 1,000. Do you raise the limit?
*Chapter: [23](23-Recursion.md)*

Usually not. `sys.setrecursionlimit` can be raised, but a limit set far above the default can let the process run out of C stack and crash, instead of raising a clean exception. Rewrite the recursion as a loop with an explicit stack, which keeps the same O(depth) space in the heap, where it is safe. Keep the recursive version for shallow inputs, such as a balanced tree of a few thousand nodes, and test the boundary. In Node the same problem appears as `RangeError: Maximum call stack size exceeded`, and the depth limit depends on frame size, so the iterative version is the portable fix.

### 35. [Mid] Why does `[10, 9, 1].sort()` return `[1, 10, 9]` in JavaScript?
*Chapter: [26](26-Sorting-Algorithms.md)*

With no comparator, `Array.prototype.sort` converts each element to a string and compares the UTF-16 code units, so `"10"` sorts before `"9"`. Pass a comparator for numbers, such as `(a, b) => a - b`, or a comparator for strings with `localeCompare` when the order should be human-readable. Remember that `sort` mutates the array and returns the same reference, so use `[...arr].sort(...)` when the input must stay unchanged. Python's `sorted` returns a new list and compares numbers numerically, but it raises `TypeError` for mixed types, where JavaScript would silently coerce. The sort itself is O(n log n) in both.

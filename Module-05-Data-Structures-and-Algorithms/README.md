# Module 05: Data Structures & Algorithms

## Overview

Backend interviews test data structures and algorithms in two ways: a coding round ("find the top K", "detect a cycle", "merge intervals"), and design follow-ups ("how does a database index find a row?", "how would you build a rate limiter or an LRU cache?"). This module covers both. Every chapter explains the structure or algorithm, traces it on a small input, proves its complexity, implements it in **TypeScript** and **Python**, solves classic interview problems with it, and shows where it appears in real backend systems.

## Learning objectives

After this module you can:

- Analyse time and space complexity, including amortized and worst-case bounds, and explain them aloud.
- Choose between arrays, linked lists, hash tables, heaps, trees, tries and graphs for a given access pattern.
- Implement and trace searching, sorting, graph traversal, recursion, divide and conquer, and dynamic programming.
- Recognise the common interview patterns: two pointers, sliding window, prefix sums, monotonic stack/queue, backtracking, union–find and topological sort.
- Connect algorithms to backend systems: B-tree indexes, LRU caches, consistent hashing, rate limiters, schedulers and dependency graphs.

## Prerequisites

- Comfortable writing functions and classes in TypeScript **or** Python (you will read both).
- Basic maths: logarithms, sums of series, and powers of two.

## How to practise

For every chapter: read it, close it, re-implement the core structure from memory in your interview language, then solve the chapter's problems with a timer (about 25 minutes each). Say the complexity aloud before you code.

## Chapters

### Foundations
| # | Chapter | You should be able to… |
|---|---|---|
| 01 | [Introduction to DSA](01-Introduction-to-DSA.md) | Explain why structure choice dominates backend performance |
| 02 | [Time Complexity](02-Time-Complexity.md) | Derive the running time of loops and recursive code |
| 03 | [Space Complexity](03-Space-Complexity.md) | Count auxiliary space, including the recursion stack |
| 04 | [Big O Analysis](04-Big-O-Analysis.md) | Use O, Θ and Ω, and amortized analysis, correctly |

### Linear structures
| # | Chapter | You should be able to… |
|---|---|---|
| 05 | [Arrays](05-Arrays.md) | Explain dynamic arrays, their amortized growth and cache locality |
| 06 | [Strings](06-Strings.md) | Handle immutability, Unicode, builders and string hashing |
| 07 | [Linked Lists](07-Linked-Lists.md) | Reverse a list, detect cycles, and use dummy nodes |
| 08 | [Stacks](08-Stacks.md) | Solve bracket matching and expression evaluation |
| 09 | [Queues](09-Queues.md) | Build a ring buffer, and explain FIFO in job queues |
| 10 | [Deque](10-Deque.md) | Use double-ended queues for sliding windows and work stealing |

### Hashing and priority
| # | Chapter | You should be able to… |
|---|---|---|
| 11 | [Hash Tables](11-Hash-Tables.md) | Explain hashing, collisions, load factor and resizing |
| 12 | [Hash Sets](12-Hash-Sets.md) | Deduplicate data, and do membership and set algebra |
| 13 | [Priority Queue](13-Priority-Queue.md) | Find the top K, and schedule work by priority |
| 14 | [Heaps](14-Heaps.md) | Implement sift-up/sift-down and heapify in O(n) |

### Trees
| # | Chapter | You should be able to… |
|---|---|---|
| 15 | [Trees](15-Trees.md) | Use tree terminology, representations and traversals |
| 16 | [Binary Trees](16-Binary-Trees.md) | Solve depth, diameter, LCA and serialization problems |
| 17 | [Binary Search Trees](17-Binary-Search-Trees.md) | Insert, delete and validate a BST |
| 18 | [Balanced Trees](18-Balanced-Trees.md) | Explain AVL, red–black and B-trees (database indexes) |
| 19 | [Tries](19-Tries.md) | Build autocomplete and prefix search |

### Graphs and search
| # | Chapter | You should be able to… |
|---|---|---|
| 20 | [Graphs](20-Graphs.md) | Choose an adjacency list or matrix; model real systems as graphs |
| 21 | [Breadth First Search](21-Breadth-First-Search.md) | Find shortest paths in unweighted graphs and grids |
| 22 | [Depth First Search](22-Depth-First-Search.md) | Find connected components and cycles; do iterative DFS |
| 23 | [Recursion](23-Recursion.md) | Write base cases and recurrences, and avoid stack overflow |
| 24 | [Divide and Conquer](24-Divide-and-Conquer.md) | Apply the master theorem |
| 25 | [Binary Search](25-Binary-Search.md) | Write bug-free bounds, and binary search on the answer |

### Sorting
| # | Chapter | You should be able to… |
|---|---|---|
| 26 | [Sorting Algorithms](26-Sorting-Algorithms.md) | Compare sorts by stability, memory and complexity |
| 27 | [Merge Sort](27-Merge-Sort.md) | Implement it, and use external merge sort for big data |
| 28 | [Quick Sort](28-Quick-Sort.md) | Partition, choose pivots and quickselect |
| 29 | [Heap Sort](29-Heap-Sort.md) | Sort in place in O(n log n) worst case |

### Problem-solving patterns
| # | Chapter | You should be able to… |
|---|---|---|
| 30 | [Two Pointers](30-Two-Pointers.md) | Solve pair-sum, partitioning and merging problems |
| 31 | [Sliding Window](31-Sliding-Window.md) | Use fixed and variable windows; build sliding-window rate limiters |
| 32 | [Prefix Sum](32-Prefix-Sum.md) | Answer range-sum and subarray-sum queries |
| 33 | [Difference Array](33-Difference-Array.md) | Apply range updates in O(1) each |
| 34 | [Greedy Algorithms](34-Greedy-Algorithms.md) | Prove greedy choices; solve interval scheduling |
| 35 | [Backtracking](35-Backtracking.md) | Generate subsets and permutations, with pruning |
| 36 | [Dynamic Programming Fundamentals](36-Dynamic-Programming-Fundamentals.md) | Go from recursion to memoization to tabulation |
| 37 | [Union Find](37-Union-Find.md) | Use path compression and union by rank |
| 38 | [Topological Sorting](38-Topological-Sorting.md) | Order dependencies and detect cycles (Kahn's algorithm, DFS) |
| 39 | [Monotonic Stack](39-Monotonic-Stack.md) | Find the next greater element and histogram areas |
| 40 | [Monotonic Queue](40-Monotonic-Queue.md) | Compute sliding-window maximums in O(n) |

### Backend applications
| # | Chapter | You should be able to… |
|---|---|---|
| 41 | [Backend DSA Patterns](41-Backend-DSA-Patterns.md) | Map interview patterns to production code |
| 42 | [Cache Data Structures](42-Cache-Data-Structures.md) | Compare LRU, LFU, TTL and probabilistic structures |
| 43 | [LRU Cache](43-LRU-Cache.md) | Implement an O(1) LRU with a hash map and a linked list |
| 44 | [Consistent Hashing Basics](44-Consistent-Hashing-Basics.md) | Build a hash ring with virtual nodes |

## Study resources in this folder

- [pref.md](pref.md) — one-line definition and example per chapter, for quick revision.
- [module-summary.md](module-summary.md) — the whole module as one connected story, with a pattern-recognition guide.
- [interview_questions.md](interview_questions.md) — mixed-topic questions with model answers.
- [tasks.md](tasks.md) — implementation projects and timed problem sets.

## Suggested plan (about 5 weeks, 1–2 hours a day)

| Week | Chapters | Practice |
|---|---|---|
| 1 | 01–10 | Tasks 1–2 |
| 2 | 11–19 | Tasks 3–4 |
| 3 | 20–29 | Task 5 |
| 4 | 30–40 | Task 6 |
| 5 | 41–44 | Tasks 7–8, then the interview questions |

## Related modules

- [Module 03: Databases](../Module-03-Databases/README.md) — B-tree indexes, hash joins and sort-based query plans.
- [Module 04: Operating Systems](../Module-04-Operating-Systems/README.md) — memory layout, caches and the cost of recursion.
- [Module 07: Advanced Backend and System Design](../Module-07-Advanced-Backend-and-System-Design/README.md) — caching, sharding, rate limiting and consistent hashing at scale.
- [Module 11: Interview Preparation](../Module-11-Interview-Preparation/README.md) — coding interview strategy and live-coding practice.

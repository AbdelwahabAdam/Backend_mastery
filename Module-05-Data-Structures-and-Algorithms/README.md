    # Module 5: Data Structures & Algorithms

    ## Module overview
    This module develops semi-senior judgment in algorithmic reasoning, complexity analysis, and backend data-structure choices. It treats theory as a way to make safe production decisions, explain trade-offs in interviews, and diagnose failures with evidence.

    ## Learning objectives
    - Explain what the system does, why its design exists, and where it fails.
    - Derive correctness and complexity rather than memorizing snippets.
    - Connect local code to production limits, observability, and recovery.
    - Communicate a reasoned answer in a backend interview.

    ## Required prerequisites
    - Python, unit tests, Git, and Linux command-line basics.
    - HTTP service and Docker fundamentals.
    - Basic SQL and Redis familiarity for production examples.

    ## Recommended learning order
    Read chapters numerically, implement the easy/medium/hard exercises, then complete the capstone in [tasks.md](tasks.md). Use [interview_questions.md](interview_questions.md) for active recall only after you can reason from first principles.

    ## Estimated study time
    **140–190 hours**, including exercises, load tests, profiling, and interview practice.

    ## Skills gained
    - Complexity analysis, reusable algorithm patterns, and data-structure selection
    - Production performance and failure analysis
    - Clear technical communication and trade-off reasoning

    ## Where these concepts are used in backend engineering
    caching, queues, indexing, pagination, scheduling, dependency resolution, rate limiting, and interviews.

    ## Common interview focus areas
    Invariants, edge cases, complexity, concurrency boundaries, capacity limits, debugging method, and production alternatives. Strong candidates explain assumptions and failure recovery—not only an API or code snippet.

    ## Chapter index
    - [01-Introduction to DSA](01-Introduction to DSA.md)
- [02-Time Complexity](02-Time Complexity.md)
- [03-Space Complexity](03-Space Complexity.md)
- [04-Big O Analysis](04-Big O Analysis.md)
- [05-Arrays](05-Arrays.md)
- [06-Strings](06-Strings.md)
- [07-Linked Lists](07-Linked Lists.md)
- [08-Stacks](08-Stacks.md)
- [09-Queues](09-Queues.md)
- [10-Deque](10-Deque.md)
- [11-Hash Tables](11-Hash Tables.md)
- [12-Hash Sets](12-Hash Sets.md)
- [13-Priority Queue](13-Priority Queue.md)
- [14-Heaps](14-Heaps.md)
- [15-Trees](15-Trees.md)
- [16-Binary Trees](16-Binary Trees.md)
- [17-Binary Search Trees](17-Binary Search Trees.md)
- [18-Balanced Trees](18-Balanced Trees.md)
- [19-Tries](19-Tries.md)
- [20-Graphs](20-Graphs.md)
- [21-Breadth First Search](21-Breadth First Search.md)
- [22-Depth First Search](22-Depth First Search.md)
- [23-Recursion](23-Recursion.md)
- [24-Divide and Conquer](24-Divide and Conquer.md)
- [25-Binary Search](25-Binary Search.md)
- [26-Sorting Algorithms](26-Sorting Algorithms.md)
- [27-Merge Sort](27-Merge Sort.md)
- [28-Quick Sort](28-Quick Sort.md)
- [29-Heap Sort](29-Heap Sort.md)
- [30-Two Pointers](30-Two Pointers.md)
- [31-Sliding Window](31-Sliding Window.md)
- [32-Prefix Sum](32-Prefix Sum.md)
- [33-Difference Array](33-Difference Array.md)
- [34-Greedy Algorithms](34-Greedy Algorithms.md)
- [35-Backtracking](35-Backtracking.md)
- [36-Dynamic Programming Fundamentals](36-Dynamic Programming Fundamentals.md)
- [37-Union Find](37-Union Find.md)
- [38-Topological Sorting](38-Topological Sorting.md)
- [39-Monotonic Stack](39-Monotonic Stack.md)
- [40-Monotonic Queue](40-Monotonic Queue.md)
- [41-Backend DSA Patterns](41-Backend DSA Patterns.md)
- [42-Cache Data Structures](42-Cache Data Structures.md)
- [43-LRU Cache](43-LRU Cache.md)
- [44-Consistent Hashing Basics](44-Consistent Hashing Basics.md)

    ## Summary
    The goal is durable engineering judgment: choose a mechanism from constraints, make its guarantees explicit, measure it under load, and evolve it safely.

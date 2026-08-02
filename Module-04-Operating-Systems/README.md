    # Module 4: Operating Systems & Concurrency

    ## Module overview
    This module develops semi-senior judgment in Linux processes, threads, memory, I/O, containers, and backend concurrency. It treats theory as a way to make safe production decisions, explain trade-offs in interviews, and diagnose failures with evidence.

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
    **95–125 hours**, including exercises, load tests, profiling, and interview practice.

    ## Skills gained
    - Resource-aware concurrency, container/runtime diagnosis, and safe worker design
    - Production performance and failure analysis
    - Clear technical communication and trade-off reasoning

    ## Where these concepts are used in backend engineering
    web servers, worker fleets, PostgreSQL, Redis, Docker, Kubernetes, and incident diagnosis.

    ## Common interview focus areas
    Invariants, edge cases, complexity, concurrency boundaries, capacity limits, debugging method, and production alternatives. Strong candidates explain assumptions and failure recovery—not only an API or code snippet.

    ## Chapter index
    - [01-Operating Systems Fundamentals](01-Operating Systems Fundamentals.md)
- [02-Processes](02-Processes.md)
- [03-Threads](03-Threads.md)
- [04-Process vs Thread](04-Process vs Thread.md)
- [05-Process Lifecycle](05-Process Lifecycle.md)
- [06-Thread Lifecycle](06-Thread Lifecycle.md)
- [07-CPU Scheduling](07-CPU Scheduling.md)
- [08-Context Switching](08-Context Switching.md)
- [09-Concurrency](09-Concurrency.md)
- [10-Parallelism](10-Parallelism.md)
- [11-Synchronization](11-Synchronization.md)
- [12-Critical Sections](12-Critical Sections.md)
- [13-Race Conditions](13-Race Conditions.md)
- [14-Mutex](14-Mutex.md)
- [15-Semaphore](15-Semaphore.md)
- [16-Spinlocks](16-Spinlocks.md)
- [17-Condition Variables](17-Condition Variables.md)
- [18-Deadlocks](18-Deadlocks.md)
- [19-Livelocks](19-Livelocks.md)
- [20-Starvation](20-Starvation.md)
- [21-Memory Management](21-Memory Management.md)
- [22-Heap Memory](22-Heap Memory.md)
- [23-Stack Memory](23-Stack Memory.md)
- [24-Virtual Memory](24-Virtual Memory.md)
- [25-Paging](25-Paging.md)
- [26-Segmentation](26-Segmentation.md)
- [27-System Calls](27-System Calls.md)
- [28-Inter Process Communication](28-Inter Process Communication.md)
- [29-Signals](29-Signals.md)
- [30-File Systems Basics](30-File Systems Basics.md)
- [31-I O Operations](31-I O Operations.md)
- [32-Backend Concurrency Patterns](32-Backend Concurrency Patterns.md)

    ## Summary
    The goal is durable engineering judgment: choose a mechanism from constraints, make its guarantees explicit, measure it under load, and evolve it safely.

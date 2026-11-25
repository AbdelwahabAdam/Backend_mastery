# Module 04: Operating Systems & Concurrency

## Overview

Every backend incident eventually reaches the operating system: a container killed for using too much memory, a CPU quota that throttles p99 latency, a deadlock between two worker threads, a process that ignores `SIGTERM` during a deploy, or "too many open files". This module explains processes, threads, scheduling, synchronization, memory and I/O, and connects each one to how **Node.js** and **Python** actually run your code on **Linux** inside containers.

Every chapter shows the concept, the Linux commands to observe it (`ps`, `/proc`, `strace`, `perf`, `vmstat`), and code in both **Node.js/TypeScript** and **Python**.

## Learning objectives

After this module you can:

- Explain what a process and a thread own, how they are created, scheduled and destroyed, and what a context switch costs.
- Tell concurrency from parallelism, and predict how Node's event loop, Python's GIL, and worker processes behave under load.
- Find and fix race conditions using mutexes, semaphores, condition variables or atomics, and avoid deadlock, livelock and starvation.
- Read a process's memory map, and explain heap vs stack, virtual memory, paging, the page cache, and OOM kills.
- Trace system calls, handle signals for graceful shutdown, and reason about file descriptors and blocking vs non-blocking I/O.
- Choose a concurrency pattern (worker pool, bounded queue, fan-out/fan-in, backpressure) for a backend workload.

## Prerequisites

- [Module 02: Core Backend](../Module-02-Core-Backend/README.md), especially [Node HTTP Server Concepts](../Module-02-Core-Backend/05-Node-HTTP-Server-Concepts.md) and [Node Event Loop and Concurrency](../Module-02-Core-Backend/06-Node-Event-Loop-and-Concurrency.md).
- A Linux shell. Docker on macOS or Windows (or WSL2) is enough: `docker run -it --rm --cap-add SYS_PTRACE ubuntu:24.04`, then install `procps strace`.

## Chapters

### Processes and threads
| # | Chapter | You should be able to… |
|---|---|---|
| 01 | [Operating Systems Fundamentals](01-Operating-Systems-Fundamentals.md) | Explain kernel vs user space and what the OS does for a backend process |
| 02 | [Processes](02-Processes.md) | Describe what a process owns, and create one with `fork`/`exec` (or `spawn`) |
| 03 | [Threads](03-Threads.md) | Explain what threads share, and use them in Node and Python |
| 04 | [Process vs Thread](04-Process-vs-Thread.md) | Choose processes, threads or async for a workload |
| 05 | [Process Lifecycle](05-Process-Lifecycle.md) | Explain process states, zombies, orphans and PID 1 in containers |
| 06 | [Thread Lifecycle](06-Thread-Lifecycle.md) | Start, join, cancel and clean up threads safely |
| 07 | [CPU Scheduling](07-CPU-Scheduling.md) | Explain CFS/EEVDF, nice values and cgroup CPU quotas |
| 08 | [Context Switching](08-Context-Switching.md) | Measure context switches and explain their cost |

### Concurrency and synchronization
| # | Chapter | You should be able to… |
|---|---|---|
| 09 | [Concurrency](09-Concurrency.md) | Model overlapping work in threads, processes and event loops |
| 10 | [Parallelism](10-Parallelism.md) | Get real multi-core speed-up, and apply Amdahl's law |
| 11 | [Synchronization](11-Synchronization.md) | Pick the right primitive for each coordination problem |
| 12 | [Critical Sections](12-Critical-Sections.md) | Identify and minimise critical sections |
| 13 | [Race Conditions](13-Race-Conditions.md) | Reproduce and fix data races and check-then-act races |
| 14 | [Mutex](14-Mutex.md) | Use locks correctly, including async locks |
| 15 | [Semaphore](15-Semaphore.md) | Limit concurrency to protect a dependency |
| 16 | [Spinlocks](16-Spinlocks.md) | Explain when spinning beats sleeping, and atomics |
| 17 | [Condition Variables](17-Condition-Variables.md) | Wait for a condition without busy-waiting |
| 18 | [Deadlocks](18-Deadlocks.md) | Apply the four Coffman conditions and prevent deadlocks |
| 19 | [Livelocks](19-Livelocks.md) | Recognise livelock and break it with jitter |
| 20 | [Starvation](20-Starvation.md) | Detect starvation and add fairness |

### Memory
| # | Chapter | You should be able to… |
|---|---|---|
| 21 | [Memory Management](21-Memory-Management.md) | Read RSS vs VSZ, and explain OOM kills in containers |
| 22 | [Heap Memory](22-Heap-Memory.md) | Find memory leaks in V8 and CPython |
| 23 | [Stack Memory](23-Stack-Memory.md) | Explain stack frames, recursion limits and stack overflow |
| 24 | [Virtual Memory](24-Virtual-Memory.md) | Explain address spaces, mmap and copy-on-write |
| 25 | [Paging](25-Paging.md) | Explain pages, page faults, the TLB and swap |
| 26 | [Segmentation](26-Segmentation.md) | Explain segmentation, and why "segmentation fault" outlived it |

### Kernel interface and I/O
| # | Chapter | You should be able to… |
|---|---|---|
| 27 | [System Calls](27-System-Calls.md) | Trace a request's system calls with `strace` |
| 28 | [Inter Process Communication](28-Inter-Process-Communication.md) | Choose pipes, Unix sockets, shared memory or a queue |
| 29 | [Signals](29-Signals.md) | Handle `SIGTERM`/`SIGINT` for graceful shutdown |
| 30 | [File Systems Basics](30-File-Systems-Basics.md) | Explain inodes, file descriptors, the page cache and `fsync` |
| 31 | [I/O Operations](31-I-O-Operations.md) | Compare blocking, non-blocking, epoll and io_uring |
| 32 | [Backend Concurrency Patterns](32-Backend-Concurrency-Patterns.md) | Build worker pools, bounded queues and backpressure |

## Study resources in this folder

- [pref.md](pref.md) — one-line definition and example per chapter, for quick revision.
- [module-summary.md](module-summary.md) — the whole module as one connected story.
- [interview_questions.md](interview_questions.md) — mixed-topic questions with model answers.
- [tasks.md](tasks.md) — hands-on labs you run on Linux.

## Suggested plan (about 3 weeks, 1–2 hours a day)

| Week | Chapters | Build |
|---|---|---|
| 1 | 01–10 | Tasks 1–3 |
| 2 | 11–20 | Tasks 4–5 |
| 3 | 21–32 | Tasks 6–8, then the interview questions |

## Related modules

- [Module 02: Core Backend](../Module-02-Core-Backend/README.md) — the event loop, graceful shutdown and background workers built on these primitives.
- [Module 03: Databases](../Module-03-Databases/README.md) — database locks, deadlocks and `fsync` durability.
- [Module 06: Networking and Distributed Basics](../Module-06-Networking-and-Distributed-Basics/README.md) — sockets and network I/O.
- [Module 10: DevOps and Cloud](../Module-10-DevOps-and-Cloud/README.md) — containers, cgroups and production limits.

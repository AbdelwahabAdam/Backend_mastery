# Module 04 Practice Tasks: Operating-System Labs for Backend Engineers

These are labs: you run something, observe it with Linux tools, break it, and fix it. Do each lab in **Node.js/TypeScript** or **Python**, and port at least labs 3, 5 and 8 to the other runtime, writing down what behaved differently.

**Setup:** a Linux machine, or `docker run -it --rm --cap-add SYS_PTRACE --cpus 2 --memory 512m ubuntu:24.04`. Then install `procps sysstat strace linux-tools-generic` (if available), Node.js 22+ and Python 3.12+.

Each lab is done when every item in its **Done when** list is backed by command output or a test you can show.

---

## Lab 1 — Look inside a running service
**Chapters:** [01](01-Operating-Systems-Fundamentals.md), [02](02-Processes.md), [03](03-Threads.md) · **Level:** Beginner

Run a tiny HTTP server (Express or FastAPI/uvicorn).

**Done when**
- [ ] You show its PID, parent PID, user, thread count and open file descriptors using only `ps`, `/proc/<pid>/status`, `/proc/<pid>/task` and `/proc/<pid>/fd`.
- [ ] You explain every thread you see: for Node, the main thread, libuv pool and V8 helper threads; for uvicorn, the worker threads.
- [ ] You read the container's CPU and memory limits from `/sys/fs/cgroup`, and print them from inside the app.

## Lab 2 — PID 1, zombies and exit codes
**Chapters:** [05](05-Process-Lifecycle.md), [29](29-Signals.md) · **Level:** Beginner

**Done when**
- [ ] A Dockerfile using `CMD npm start` (shell form) ignores `docker stop` for 10 s, and you explain why. The exec form plus `--init` (or `tini`) stops immediately and gracefully.
- [ ] You create a zombie on purpose (a child that is never reaped), show `Z` in `ps`, then fix the parent.
- [ ] You produce and explain exit codes 0, 1, 137 and 143.

## Lab 3 — CPU quotas and worker counts
**Chapters:** [07](07-CPU-Scheduling.md), [08](08-Context-Switching.md), [10](10-Parallelism.md) · **Level:** Intermediate

Run a CPU-heavy endpoint in a container limited to `--cpus 1` on a machine with more cores.

**Done when**
- [ ] With workers = host core count (e.g. 8 Node cluster workers or 8 uvicorn workers), you capture throttling in `cpu.stat` (`nr_throttled`, `throttled_usec`) and the p99 latency under load.
- [ ] Sizing workers from the cgroup quota instead lowers p99. You show both numbers.
- [ ] You report voluntary and involuntary context switches for each setup from `/proc/<pid>/status` or `pidstat -w`.
- [ ] You compute the theoretical speed-up with Amdahl's law for a job that is 20% serial, and compare it to what you measured with 1, 2 and 4 workers.

## Lab 4 — Race-condition clinic
**Chapters:** [11](11-Synchronization.md)–[16](16-Spinlocks.md) · **Level:** Intermediate

**Done when**
- [ ] A shared counter incremented 1,000,000 times by 4 threads (Python) or 4 workers on a `SharedArrayBuffer` (Node) loses updates. Show the wrong total.
- [ ] You fix it twice: once with a lock, and once with an atomic operation (`Atomics.add`, or a design that avoids sharing). You compare the timings.
- [ ] An **async** check-then-act race (two concurrent requests both "reserve" the last seat across an `await`) is reproduced in a test and fixed with a per-key async mutex.
- [ ] A semaphore limits calls to a slow fake dependency to 5 in flight, and a test proves the limit holds and that permits are released on timeout and on error.

## Lab 5 — Deadlock, livelock, starvation
**Chapters:** [17](17-Condition-Variables.md)–[20](20-Starvation.md) · **Level:** Intermediate

**Done when**
- [ ] Two tasks taking two locks in opposite order hang. You capture where each one is stuck (Python `faulthandler`/`py-spy dump`, or a Node diagnostic report), then fix it with a global lock order.
- [ ] A "try-lock, release, retry immediately" version livelocks (high CPU, zero progress); randomized backoff fixes it.
- [ ] One noisy tenant starves others in a single FIFO queue. Per-tenant round-robin brings the quiet tenants' p95 wait time down; you show before and after numbers.
- [ ] A bounded producer–consumer queue built on a condition variable (Python) or Promise-based waiting (Node) never busy-waits: show near-zero CPU while idle.

## Lab 6 — Memory: leaks and OOM kills
**Chapters:** [21](21-Memory-Management.md)–[25](25-Paging.md) · **Level:** Advanced

**Done when**
- [ ] An endpoint with an unbounded in-memory cache grows RSS under load until the container is OOM-killed. You show exit code 137 and the `oom_kill` counter in `memory.events`.
- [ ] You find the leak with a heap snapshot diff (Node) or a `tracemalloc` snapshot diff (Python), and fix it with a bounded LRU cache.
- [ ] For Node, you set `--max-old-space-size` below the container limit and explain what changes. For Python, you show total RSS for 4 workers, with and without `--preload` / `gc.freeze()`.
- [ ] You show minor and major page-fault counts before and after reading a large file twice, and explain the difference using the page cache.

## Lab 7 — System calls and file descriptors
**Chapters:** [27](27-System-Calls.md), [28](28-Inter-Process-Communication.md), [30](30-File-Systems-Basics.md), [31](31-I-O-Operations.md) · **Level:** Advanced

**Done when**
- [ ] `strace -f -c` on one HTTP request shows the syscall summary. You identify `accept4`, `epoll_wait`, `read` and `write`, and explain each.
- [ ] Writing 100k small lines unbuffered and then buffered: you show the difference in `write` syscall counts.
- [ ] An FD leak (files or sockets never closed) reaches `EMFILE` with `ulimit -n 256`. You detect it by counting `/proc/self/fd`, and fix it.
- [ ] A config file is replaced atomically (temp file → `fsync` → `rename`), and a reader running in a loop never sees a half-written file.
- [ ] Two processes exchange newline-delimited JSON over a Unix domain socket. You compare its latency with TCP loopback.

## Lab 8 — Capstone: a well-behaved worker service
**Chapters:** [29](29-Signals.md), [32](32-Backend-Concurrency-Patterns.md) and all previous · **Level:** Advanced

Build a job-processing service: an HTTP endpoint enqueues jobs, and a pool of workers processes them (half CPU-bound, half I/O-bound).

**Done when**
- [ ] The worker pool is sized from the cgroup CPU quota for CPU work, and from Little's law for I/O work. Your README shows the arithmetic.
- [ ] The queue is bounded; when it is full, the API returns `503` with `Retry-After` instead of growing memory.
- [ ] Concurrent requests for the same expensive key are coalesced (single-flight), and a test proves only one computation runs.
- [ ] On `SIGTERM`: stop accepting, finish in-flight jobs within 20 s, hand back unfinished jobs, exit 0. Verified with `docker stop` while under load.
- [ ] A one-page report shows CPU, RSS, context switches, FD count and p99 latency at three load levels, with the commands used to collect them.

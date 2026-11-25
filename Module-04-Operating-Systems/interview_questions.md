# Module 04 Interview Questions

Each chapter ends with questions about its own topic. The questions here **cut across chapters**, the way OS questions come up in backend interviews: "the pod restarted with exit code 137" quickly becomes a question about memory limits, then signals, then how your runtime uses memory.

**How to answer:** direct answer first, then the mechanism, then a trade-off or failure case. For Senior questions, end with how you would detect the problem in production (a command, a file in `/proc` or `/sys/fs/cgroup`, or a metric).

Levels: **[Junior]** definitions and basic mechanics · **[Mid]** trade-offs and debugging · **[Senior]** design under load and failure.

Unless a question says otherwise, assume Linux, a container with cgroup v2, and a Node.js or Python service.

---

## A. Processes, threads and runtimes

### 1. [Junior] What does a process own, and what do its threads share?
*Chapters: [02](02-Processes.md), [03](03-Threads.md), [04](04-Process-vs-Thread.md)*

A process owns a private virtual address space, a file descriptor table, a PID and parent PID, credentials, `argv` and environment, a current directory, signal handlers, resource limits, and at least one thread. Each thread owns only its stack, its registers (including the program counter and stack pointer), a thread ID, a signal mask and thread-local storage. Everything else is shared by all threads of the process: the heap, globals, code, open file descriptors and signal handlers. On Linux both are tasks created by `clone()`, and the flags decide what is shared. That is the whole trade-off: threads share cheaply but one segfault kills them all; processes are isolated but must talk through IPC.

### 2. [Mid] In Node, when do you use the event loop, `worker_threads`, or more processes? What are the Python equivalents?
*Chapters: [04](04-Process-vs-Thread.md), [09](09-Concurrency.md), [10](10-Parallelism.md), [03](03-Threads.md)*

- **I/O-bound request handling:** the event loop in Node; asyncio in Python, or a thread pool for blocking libraries. One thread can handle thousands of waiting connections.
- **CPU-bound work inside a service:** a fixed pool of `worker_threads` in Node. Each worker has its own V8 isolate, heap and event loop. In Python use `ProcessPoolExecutor`, because the GIL stops threads running Python bytecode in parallel. The exceptions are C code that releases the GIL (`hashlib` on large inputs, `zlib`, NumPy) and free-threaded builds.
- **More cores for serving traffic:** `cluster` in Node or, more usually in Kubernetes, more replicas with one process per container. In Python, Gunicorn/Uvicorn workers or more replicas.

Size CPU pools to the container's CPU quota and create them once at start-up. Note that Node's `child_process.fork()` is not Unix `fork()`: it starts a fresh Node process with an IPC channel.

### 3. [Mid] Python has a GIL. Why don't threads speed up CPU work, and why is threaded code still not thread-safe?
*Chapters: [03](03-Threads.md), [13](13-Race-Conditions.md), [10](10-Parallelism.md)*

The GIL lets only one thread run Python bytecode at a time. Four threads on a pure-Python loop take as long as one, plus hand-off overhead. Threads still help I/O-bound work, because blocking calls release the GIL. But the GIL makes single bytecodes atomic, not your operations. `counter += 1` is load, add, store, and a thread switch can happen in between. With a function call between the read and the write, 4 threads lose hundreds of thousands of updates out of 2 million. Fix it with a `threading.Lock` around the whole read-modify-write, or give the state to one owner thread fed by a queue. Free-threaded builds (3.13 experimental, 3.14 supported but optional) remove the GIL, which makes correct locking even more important.

### 4. [Mid] Your service must run an external tool on a file name that comes from the user. How do you do it safely?
*Chapters: [02](02-Processes.md), [05](05-Process-Lifecycle.md), [28](28-Inter-Process-Communication.md)*

- Pass an **argument array** with no shell: `spawn("convert", [name, "out.png"])` or `subprocess.run(["convert", name, "out.png"])`. Never use `shell: true` / `shell=True` with user input. Also reject values that start with `-`, so they can't become options.
- Set a **timeout**, then escalate from `SIGTERM` to `SIGKILL`. Kill the **process group** (`detached: true` / `start_new_session=True`, then `kill(-pid)`) so grandchildren don't keep running.
- **Cap the output**, and read stdout and stderr together (`communicate()` in Python). If nobody reads a full 64 KiB pipe buffer, the child blocks forever.
- Pass a **minimal `env`**, not the full environment with the database password.
- Handle three outcomes: could not start (`ENOENT`), exited non-zero, or killed by a signal (`code === null` in Node, a negative `returncode` in Python).
- Don't use `execSync` / `spawnSync` in a server: they block the event loop until the child exits.

### 5. [Senior] Gunicorn pre-forks 8 workers with `--preload`. Each worker's memory climbs right after start, but nothing leaks. Why?
*Chapters: [24](24-Virtual-Memory.md), [21](21-Memory-Management.md), [04](04-Process-vs-Thread.md)*

`fork()` copies page tables, not memory. Pages stay shared **copy-on-write** until someone writes to them. In CPython, merely *reading* an object writes its reference count, and the cycle collector writes GC headers, so shared pages turn into private copies. In the chapter's test, one `gc.collect()` copied 46 MiB, and iterating 1M preloaded objects copied about 108 MiB per child. With 8 workers, that is the difference between about 150 MiB and about 1 GiB in total. Mitigations: `gc.disable()` early, `gc.freeze()` before forking and `gc.enable()` in the child (this stops GC writes, not refcount writes); keep big read-only data outside Python objects, for example in a memory-mapped file; and open database connections after the fork, never before. RSS hardly changes in this scenario, so it is the wrong metric. **Detect:** watch `Pss` and `Private_Dirty` in `/proc/<pid>/smaps_rollup` over time, and the cgroup's `memory.current`.

---

## B. Containers, scheduling and CPU

### 6. [Junior] What is a container, in operating-system terms?
*Chapters: [01](01-Operating-Systems-Fundamentals.md), [05](05-Process-Lifecycle.md)*

A container is not a VM. It is a tree of ordinary processes on the host kernel. **Namespaces** limit what it can see (PIDs, network, mounts, hostname, users). **cgroups** limit what it can use (`cpu.max`, `memory.max`, `pids.max`). Seccomp and dropped capabilities limit what it can ask the kernel to do. `uname -r` inside it prints the host's kernel version. Consequences: root in the container is UID 0 on the host kernel unless user namespaces are configured, so run as a non-root user; your app is often PID 1, which has special signal rules; and `free -m` or `os.cpu_count()` show the host, not your limits.

### 7. [Mid] A pod has a 2-CPU limit on a 64-core node. How many workers should it start?
*Chapters: [07](07-CPU-Scheduling.md), [01](01-Operating-Systems-Fundamentals.md), [10](10-Parallelism.md), [32](32-Backend-Concurrency-Patterns.md)*

For CPU-bound workers: `max(1, floor(quota))`, which is 2. Read the quota from `/sys/fs/cgroup/cpu.max` (`"200000 100000"` means 2 CPUs), or pass the count in an environment variable. `os.cpus().length` and `os.cpu_count()` report the host's 64. `gunicorn -w $((2 * $(nproc) + 1))` would start 129 workers fighting over 2 CPUs and opening hundreds of database connections. `os.availableParallelism()` follows the affinity mask, and recent libuv applies the quota only when it is at least 1 CPU, so a 0.5-CPU pod still reports the host. In Python 3.13+, `os.process_cpu_count()` also follows affinity, not the quota; `PYTHON_CPU_COUNT` lets you override it. I/O pools are sized differently: from Little's law and the dependency's limits, not from the CPU count.

### 8. [Senior] CPU usage is 50% of the limit, but p99 latency spikes. Walk through it.
*Chapters: [07](07-CPU-Scheduling.md), [08](08-Context-Switching.md), [01](01-Operating-Systems-Fundamentals.md)*

The likely cause is **CPU quota throttling**. `cpu.max` is a budget per 100 ms period. Usage is averaged over many periods, but throttling happens in bursts inside a single period. With a 0.5-CPU quota, eight busy threads use the 50 ms budget in about 6 ms. Then **every** thread in the container, including the event loop or request threads, is off the CPU for the remaining ~94 ms. In the chapter's test, 8 busy workers under a 2-CPU quota stalled an otherwise idle event loop for up to 72 ms. Fixes: fewer CPU-bound threads (size them to the quota), batch work in a separate deployment, a higher limit, or no CPU limit for latency-sensitive services, relying on requests (`cpu.weight`) instead. Don't reach for negative nice values: nice only matters under contention, and it can starve the runtime's own helper threads. Load average won't help either: it includes `D`-state tasks, is not divided per CPU, and shows the host's value inside a container. **Detect:** `nr_throttled` and `throttled_usec` in `/sys/fs/cgroup/cpu.stat` rising together with p99, and involuntary context switches (`pidstat -w`).

### 9. [Mid] Is a system call a context switch? What does a context switch cost, and how do you measure it?
*Chapters: [08](08-Context-Switching.md), [27](27-System-Calls.md)*

No. A system call is a **mode switch**: the same thread enters the kernel and comes back. A context switch is the scheduler giving the CPU to a different task. It saves and loads registers, and switches page tables if the new task is in another process; a switch between threads of one process skips that. The direct cost is about a microsecond or a few. The indirect cost (cold caches, TLB and branch predictors) is usually bigger. **Voluntary** switches mean the thread blocked on I/O, a lock or a sleep. **Involuntary** ones mean it was preempted, which points to more runnable threads than CPU. Measure with `pidstat -w` (`cswch/s`, `nvcswch/s`), `vmstat 1` (the `cs` column), `perf stat -e context-switches`, or `/proc/<pid>/task/*/status`. Don't use `/proc/<pid>/status` alone: it covers only the main thread.

---

## C. Concurrency and races

### 10. [Junior] What is the difference between concurrency and parallelism?
*Chapters: [09](09-Concurrency.md), [10](10-Parallelism.md)*

Concurrency is about **structure**: several tasks are in progress at once and interleave, possibly on one core. Parallelism is about **execution**: work happens at the same instant on several cores. I/O-bound work, such as waiting on databases and HTTP, gains from concurrency even on one core, because the waits overlap. CPU-bound work gains only from parallelism, and only up to the CPU you are allowed to use. A Node server is highly concurrent, and for JavaScript code it is not parallel at all.

### 11. [Mid] "Node is single-threaded, so we can't have race conditions." Respond.
*Chapters: [13](13-Race-Conditions.md), [09](09-Concurrency.md), [11](11-Synchronization.md)*

There are no **data races** on ordinary JavaScript objects, but there are **race conditions**. Every `await` is a point where other requests run. "Check, `await`, act", such as `if (!(await exists(key))) await create(key)`, lets five concurrent requests all pass the check and all create the record. Code between two `await`s cannot be interrupted, so the fixes are: keep the check and the claim in one synchronous block (claim before you `await`), share one in-flight promise (single-flight), or put an async mutex around the sequence. Each replica is a separate process, so the real guarantee must live in the database: a `UNIQUE` constraint, an atomic conditional `UPDATE`, or an idempotency key. The same is true for asyncio.

### 12. [Mid] `Promise.all`, `asyncio.gather` and `asyncio.TaskGroup`: what happens when one task fails?
*Chapters: [09](09-Concurrency.md), [32](32-Backend-Concurrency-Patterns.md)*

`Promise.all` rejects on the first failure but **does not stop** the other promises. Their requests keep running, and their results are thrown away. To stop them, pass one `AbortSignal` to every call and abort it in `catch`. `Promise.allSettled` waits for every outcome and never rejects. `asyncio.gather` also leaves the others running after a failure; with `return_exceptions=True` it behaves like `allSettled`. `asyncio.TaskGroup` (3.11+) gives **structured concurrency**: the first failure cancels the siblings and raises an `ExceptionGroup`. In both runtimes, put a cap (worker loops or a semaphore) and a deadline on any fan-out; unbounded `Promise.all(urls.map(fetch))` exhausts sockets. In Python, never swallow `CancelledError`, or cancellation hangs.

### 13. [Mid] 90% of a batch job parallelises. You run it on 16 workers and get 5×. Is something wrong?
*Chapters: [10](10-Parallelism.md), [12](12-Critical-Sections.md)*

Not necessarily. Amdahl's law gives `1 / (0.1 + 0.9/16)` ≈ 6.4×, and the ceiling is 10× however many workers you add. The rest of the gap is real-world overhead: worker start-up, serializing arguments (pickling in Python, structured clone in Node), load imbalance (the slowest chunk decides the finish time), lock hold time (which is pure serial time), memory bandwidth, SMT siblings counted as CPUs, turbo clocks that drop as more cores work, and, in a container, the CPU quota. Improve it by sending references instead of data, splitting the work into several chunks per worker of at least a few milliseconds each, and shrinking critical sections. Then measure the curve at 1, 2, 4, 8 and 16 workers instead of assuming it is linear.

### 14. [Senior] A hot cache key expires, and the database gets 1,000 identical queries at once. Design the fix.
*Chapters: [32](32-Backend-Concurrency-Patterns.md), [13](13-Race-Conditions.md), [12](12-Critical-Sections.md)*

This is a cache stampede: a check-then-act race repeated 1,000 times.
- **Single-flight:** keep a map from key to the in-flight promise or task. The first miss starts the load; the other 999 callers await the same result. Delete the entry when it settles, and don't cache failures.
- In asyncio, wrap the shared task in `asyncio.shield()`. Otherwise the first caller's timeout cancels the load for every waiter. Give the shared load its own deadline.
- Add **TTL jitter** so many keys don't expire together, and use stale-while-revalidate for hot keys.
- Single-flight is **per process**: 20 replicas still send 20 queries. That is usually fine; if not, add a short distributed lock or a shared cache layer.

**Detect:** database queries per second around expiry times, bursts of cache misses for one key, and connection-pool wait time.

---

## D. Locks and coordination

### 15. [Junior] What is the difference between a mutex and a semaphore?
*Chapters: [14](14-Mutex.md), [15](15-Semaphore.md)*

A mutex lets **one** task into a critical section, and it has an **owner**: the task that locked it should unlock it. A semaphore is a **counter of permits** with no owner. Any task may release it, so it suits limits ("at most 10 calls in flight") and signalling, and it is dangerous for exclusion. A binary semaphore is not a mutex: a stray `release()` silently lets two tasks in. `BoundedSemaphore` turns an extra release into an error. Both must be released in `finally` or a `with` block, or a single exception leaks the lock or a permit.

### 16. [Mid] Which synchronization primitive do you reach for in each case?
*Chapters: [11](11-Synchronization.md), [14](14-Mutex.md), [15](15-Semaphore.md), [16](16-Spinlocks.md), [17](17-Condition-Variables.md)*

- Only one task may update an in-memory balance → **mutex**.
- At most 20 queries for a pool of 20 connections → **semaphore**.
- Wait until the queue is non-empty → **condition variable** with its mutex, or simply `queue.Queue` / `asyncio.Queue`.
- Workers must not start until config has loaded → **event** or latch (a promise in Node), which stays open once set.
- A request counter shared between Node workers → **atomic** (`Atomics.add` on a `SharedArrayBuffer`).
- Create a client exactly once → **once** (a memoised promise or task, cleared on failure).
- Hand jobs to a worker → a bounded **queue**, so the state has one owner and needs no lock.

All of these stop at the process boundary. Across replicas, coordinate in the database or Redis.

### 17. [Mid] Why must you always wait on a condition variable inside a `while` loop?
*Chapters: [17](17-Condition-Variables.md), [11](11-Synchronization.md)*

Because waking up does not mean the condition is true. Another thread may have taken the item first (a **stolen wakeup**), or the wait may have returned for no reason (a **spurious wakeup**, which POSIX allows). So write `while not condition: cv.wait()`, or use `cv.wait_for(predicate)`. The check, the wait and the state change must all happen under the same mutex. `wait()` atomically releases the mutex and sleeps, and that is what stops a notification slipping in between "I checked" and "I slept". A condition variable has no memory: a `notify()` with nobody waiting is lost. So the shared state is the truth, and a notification only means "look again". In production, put a timeout on every wait.

### 18. [Mid] When does a spinlock beat a sleeping mutex? Why not write one in user space?
*Chapters: [16](16-Spinlocks.md), [08](08-Context-Switching.md), [07](07-CPU-Scheduling.md)*

Spinning wins only when the wait is shorter than a sleep-and-wake cycle (a few microseconds), the holder is running on another core right now, and ideally the waiter cannot sleep at all. That last case is kernel code with preemption or interrupts disabled, which is where Linux uses `spin_lock`. In user space, the kernel can preempt the holder at any moment, and every spinner then burns its whole time slice waiting for a thread that isn't running. More threads than cores, or a cgroup CPU quota, make it worse, because spinning uses up the quota. Production mutexes already do the right thing: a compare-and-swap fast path with no system call, a brief spin, then a `futex` sleep. In Python, a hand-written spinlock just fights the GIL.

### 19. [Senior] A service suddenly stops answering: CPU near 0%, health checks time out, no errors in the logs. Walk through it.
*Chapters: [18](18-Deadlocks.md), [14](14-Mutex.md), [06](06-Thread-Lifecycle.md), [32](32-Backend-Concurrency-Patterns.md)*

Low CPU with no progress means everyone is **waiting**: a deadlock, or a wait with no timeout on something that will never happen. Capture evidence before you restart, or it is gone: `py-spy dump` (threads stuck in `acquire`), `faulthandler` registered on a signal, `ps -L -o tid,stat,wchan` (threads in `S` on a futex), a Node diagnostic report (`node --report-on-signal`, then `kill -USR2 <pid>`), or `python -m asyncio ps <pid>` on Python 3.14 to see each task's await chain. Common causes:
- two locks taken in opposite orders;
- a non-reentrant lock (`threading.Lock`, `asyncio.Lock`, a promise-chain mutex) re-entered by the same task;
- a task running on a full pool waiting for work queued on the same pool;
- a request holding one database connection while waiting for a second from the same pool.

Fixes: a global lock order (sort the keys), no calls out while holding a lock, pass the existing connection down, separate pools, and a timeout on **every** acquire and wait. **Detect:** in-flight requests flat at the cap with zero completions, pool wait time, and lock-acquire timeouts that log the holder's name. An async deadlock shows no blocked thread at all, which is why timeouts matter most there.

### 20. [Mid] Compare deadlock, livelock and starvation. How can a deadlock fix create a livelock?
*Chapters: [18](18-Deadlocks.md), [19](19-Livelocks.md), [20](20-Starvation.md)*

- **Deadlock:** nobody progresses, and everyone waits. CPU is idle.
- **Livelock:** nobody progresses, and everyone is busy reacting to each other. CPU is high, completions are flat.
- **Starvation:** the system progresses, but one ready task is always passed over.

A common deadlock fix is "try the second lock with a timeout; if that fails, release the first and retry". If both sides retry immediately and in the same rhythm, they collide every time: a livelock. Break the symmetry with randomised exponential backoff with full jitter (`random(0, min(cap, base·2^n))`), a priority rule (the lower ID wins), and a retry limit that turns an endless loop into an error. Better still, fix the lock order so there is nothing to retry. Count attempts and successes separately: a livelock shows up as a falling success ratio.

### 21. [Senior] One tenant's bulk import makes the API slow for everyone else. Design a fix.
*Chapters: [20](20-Starvation.md), [15](15-Semaphore.md), [32](32-Backend-Concurrency-Patterns.md)*

This is starvation through a shared FIFO resource. The hot tenant's jobs fill the queue, the worker pool or the connection pool, and everyone else waits behind them.
- **Fair queuing:** one queue per tenant, served round robin. Use weighted round robin if tiers pay for different shares.
- **Per-tenant caps:** a semaphore per tenant on concurrency, and `429` when a tenant is over its own quota.
- **Bulkheads:** separate pools for bulk and interactive work, so slow work cannot fill the pool that fast work needs.
- If you use priorities, add **aging** or reserved capacity, so low-priority work still runs.

Fairness costs some throughput, and here that is a good trade. **Detect:** per-tenant p99 and maximum wait time, and the age of the oldest queued item. Averages hide a starved minority.

### 22. [Mid] A partner API allows 50 concurrent requests. You run 6 replicas. How do you protect it?
*Chapters: [15](15-Semaphore.md), [32](32-Backend-Concurrency-Patterns.md)*

A semaphore is per process, so 6 replicas with 50 permits each would send up to 300. Give each replica a share (50 ÷ 6, rounded down to 8), or use a shared limiter if the share is too small to be useful. Use one semaphore per dependency (a bulkhead), so a slow partner can't use capacity meant for others. Put **one deadline** around both acquiring the permit and making the call; a caller that times out while queued must leave the queue without taking a permit. Release in `finally` on every path, and release before sleeping between retries. Little's law shows why the cap matters: at 200 req/s and 50 ms, 10 calls are in flight; if the partner slows to 2 s, 400 would be in flight without the cap. If the partner also limits requests per second, add a rate limiter too: a concurrency limit is not a rate limit.

---

## E. Memory

### 23. [Junior] What are VSZ, RSS and PSS, and which do you alert on?
*Chapters: [21](21-Memory-Management.md), [24](24-Virtual-Memory.md)*

**VSZ** is the address space a process has reserved. Node shows 10+ GiB at idle, so alerting on it is noise. **RSS** is how much is in RAM now, but it counts shared pages (libraries, copy-on-write pages) in full for every process. **PSS** splits shared pages fairly, so summing PSS across workers gives a true total. **USS** is what killing the process would free. In a container, the OOM killer compares the cgroup's `memory.current` (which includes page cache) with `memory.max`. Alert on the working set approaching `memory.max`, and use PSS from `/proc/<pid>/smaps_rollup` for capacity planning.

### 24. [Senior] A container is restarted with exit code 137. Walk through what happened and how you find out.
*Chapters: [21](21-Memory-Management.md), [29](29-Signals.md), [05](05-Process-Lifecycle.md), [01](01-Operating-Systems-Fundamentals.md), [22](22-Heap-Memory.md)*

137 = 128 + 9: the process was killed by `SIGKILL`. There are two usual causes:
1. **OOM kill.** `memory.current` crossed `memory.max`, and the cgroup OOM killer sent `SIGKILL`. No handler runs and the app logs nothing. Kubernetes shows `OOMKilled`, `memory.events` increments `oom_kill`, and the kernel log has the OOM report.
2. **Stop timeout.** The app ignored `SIGTERM` (often because it was PID 1 with no handler, or `sh` was PID 1 because of a shell-form `CMD`) and was killed after the grace period. Check whether it happened during a deploy.

Don't read 137 as "out of memory" until you know which one it was. For an OOM kill in Node, V8's heap limit may be larger than the container limit, so the kernel kills the process before V8 collects hard; set `--max-old-space-size` to about 70–80% of the limit and check `heap_size_limit` inside the container. Python has no heap limit, so the budget is workers × peak RSS, plus the master. Page cache and files in `/dev/shm` or a tmpfs `/tmp` are charged to the cgroup too. Then decide whether it is a leak (post-GC heap rising under steady load → compare heap snapshots) or a sizing problem. **Detect:** alert on `memory.current` approaching `memory.max`, count `oom_kill` events, and record the termination reason with every restart.

### 25. [Mid] After a traffic spike, RSS stays high for hours. Is it a leak? How do you find a real one?
*Chapters: [22](22-Heap-Memory.md), [21](21-Memory-Management.md)*

Not necessarily. Runtimes keep heap pages for reuse, glibc's `malloc` keeps freed memory in its own free lists and rarely returns it to the OS, and fragmentation adds more. Threaded programs get several malloc arenas; `MALLOC_ARENA_MAX=2` or jemalloc often cuts RSS. The real leak signal is the **post-GC heap rising under steady load**. To find the cause, take snapshots after load and compare them: Node heap snapshots (`v8.writeHeapSnapshot()`, `--heapsnapshot-near-heap-limit`, DevTools), or Python `tracemalloc` snapshot diffs (`compare_to(old, "lineno")`). Then follow the retainer chain to the owner. The usual suspects are unbounded `Map`/`dict` caches, listeners added per request, `@lru_cache` on instance methods, stored exceptions and intervals never cleared. In Node, also check `external` and `arrayBuffers`, which are outside `heapUsed`. Raising `--max-old-space-size` or calling `gc.collect()` per request does not fix a leak.

### 26. [Mid] Some requests fail with `RangeError: Maximum call stack size exceeded` (Node) or `RecursionError` (Python). What is the cause and the fix?
*Chapters: [23](23-Stack-Memory.md), [22](22-Heap-Memory.md)*

The input decides the recursion depth. V8's stack limit is about 1 MB (about 12,500 trivial frames on Node 22), and CPython's recursion limit is 1000. A 1.5 MB JSON body nested 50,000 levels deep breaks a recursive walker. V8's `JSON.parse` accepts it, so the failure appears later, in your code or in `JSON.stringify`. The fix has two parts: **limit the depth at the boundary** (along with the body size), and **walk with an explicit stack**, an array on the heap, with a visited set if parent links can form cycles. Treat the error as a client error or a bug, never as transient, so don't retry it. Don't raise `sys.setrecursionlimit` or `--stack-size` to hide it: that turns a catchable error into a native stack overflow, which is `SIGSEGV` (exit 139) and kills the process.

### 27. [Mid] What is the difference between a TLB miss, a minor page fault and a major page fault?
*Chapters: [25](25-Paging.md), [24](24-Virtual-Memory.md), [08](08-Context-Switching.md)*

A **TLB miss** means the CPU's cache of address translations didn't have the page. The hardware walks the 4-level page table in nanoseconds, with no kernel involved. A **minor fault** enters the kernel but needs no disk: the first touch of newly allocated memory, a copy-on-write copy, or a page already in the page cache (microseconds). A **major fault** must read from disk or swap (tens of microseconds to milliseconds) and shows up as latency. Process switches cost more than thread switches partly because the new address space makes the old TLB entries useless (PCID softens this). Watch `maj_flt` with `ps -o min_flt,maj_flt`, and `si`/`so` in `vmstat` for swap.

### 28. [Mid] A Node or Python service exits with code 139. What does it mean, and what do you do?
*Chapters: [26](26-Segmentation.md), [24](24-Virtual-Memory.md), [23](23-Stack-Memory.md)*

139 = 128 + 11, which is `SIGSEGV`: an invalid memory access caught by the page tables. It could be an unmapped address such as NULL, a write to read-only memory, executing a no-execute page, or a native stack overflow into the guard page. It is not out of memory (that is 137), and it has nothing to do with segmentation hardware, which x86-64 Linux barely uses. In a Node or Python service it almost always comes from **native code**: a C extension, a native addon, `ctypes`/FFI misuse, or a wheel or `node_modules` built for a different libc. Collect evidence: `PYTHONFAULTHANDLER=1` prints the Python stack of all threads; enable core dumps and run `gdb bt`; read the kernel log line (`segfault at ADDR ip … in lib.so`). Contain risky native code in a child process, not a worker thread, because a segfault kills every thread in the process.

---

## F. Kernel interface, signals and I/O

### 29. [Senior] Every deploy takes 30 seconds, ends with exit code 137, and drops in-flight requests. Diagnose it and design proper shutdown.
*Chapters: [29](29-Signals.md), [05](05-Process-Lifecycle.md), [06](06-Thread-Lifecycle.md), [32](32-Backend-Concurrency-Patterns.md)*

Kubernetes sent `SIGTERM`, waited `terminationGracePeriodSeconds` (30 s by default), then sent `SIGKILL`. So the app never acted on `SIGTERM`. The usual reasons: the Dockerfile uses shell form (`CMD npm start`), so `sh` or `npm` is PID 1 and doesn't forward the signal; or the app is PID 1 with no `SIGTERM` handler, and PID 1 gets no default signal actions, so the signal is silently dropped. Fix the plumbing first: exec form `CMD ["node", "server.js"]`, plus `docker run --init` or `tini`. Then write the handler: stop intake (close the listener, stop polling the queue); drain in-flight work under a deadline shorter than the grace period (for example 20 s of 30 s); cancel what is left so the queue redelivers it; close pools; exit 0 if the drain was clean or 1 if work was abandoned. A second signal means "exit now". In Node, `process.on("SIGTERM", …)` removes the default exit behaviour. In Python asyncio, use `loop.add_signal_handler()`; without any handler, `finally` blocks and `atexit` never run. **Detect:** termination reasons and exit codes per rollout, pod shutdown duration, and requests or jobs aborted during deploys.

### 30. [Mid] The service logs `EMFILE: too many open files`. How do you investigate?
*Chapters: [30](30-File-Systems-Basics.md), [27](27-System-Calls.md), [31](31-I-O-Operations.md)*

`EMFILE` means the process hit its file-descriptor limit (`ulimit -n`, `RLIMIT_NOFILE`, visible in `/proc/<pid>/limits`). Sockets, pipes and epoll instances count, not only files. First find out whether it is a leak or real load: track `ls /proc/<pid>/fd | wc -l` over time, and `ls -l` to see what kinds of descriptors they are. Many sockets in `CLOSE_WAIT` (`ss -tanp`) mean the peer closed the connection but your code never did. Common leaks: descriptors closed only on the success path, and unbounded concurrent fan-out. Fix with `try/finally`, `with` or `await using`, plus a cap on concurrency. Raising `ulimit -n` without finding the leak only delays the failure. Add an fd-count metric. A related trap: `ENOSPC` while `du` shows little usage often means a deleted file is still held open; `lsof +L1` finds it.

### 31. [Senior] How do you save a config or state file so a crash never leaves it half-written? What is durable when `write()` returns?
*Chapters: [30](30-File-Systems-Basics.md), [24](24-Virtual-Memory.md), [27](27-System-Calls.md)*

When `write()` returns, the data is only in the **page cache** in RAM. Writeback happens later (about 30 s by default), and a power cut can lose it. `fsync(fd)` waits until the data and metadata are on stable storage; `fdatasync` skips metadata that isn't needed to read the data back. For an atomic replace: create a temp file **in the same directory** (`/tmp` is often another file system, so `rename` fails with `EXDEV`), write it, `fsync` it, `rename` it over the target, then `fsync` the directory so the rename itself is durable. Readers see the old file or the new one, never a mix. If other processes have the file memory-mapped, never rewrite it in place, because they can get `SIGBUS`; rename a new file in and remap. A failed `fsync` is **not retryable**: the kernel may already have dropped the dirty pages, so treat the write as failed (PostgreSQL panics in this case). Durability has a price: in the chapter's test a plain 4 KiB write took 213 µs, and the atomic version with two `fsync`s took 3.1 ms, so batch writes. **Detect:** `fsync` latency and error metrics, and a startup check that refuses a truncated or unparseable file.

### 32. [Mid] Why can't Node or asyncio read files without blocking by using `epoll`? What do they do instead?
*Chapters: [31](31-I-O-Operations.md), [20](20-Starvation.md), [09](09-Concurrency.md)*

`epoll` is a readiness model, and regular files are never "not ready". `epoll_ctl` rejects them with `EPERM`, and `O_NONBLOCK` has no effect on disk reads, so a cache miss still puts the thread to sleep. Node therefore sends `fs` work (and `dns.lookup`, `zlib` and async `crypto`) to libuv's thread pool, which has 4 threads by default (`UV_THREADPOOL_SIZE`). asyncio has no non-blocking file API, so you use `asyncio.to_thread` (aiofiles uses threads too). Two consequences: a few slow disk or DNS calls can fill libuv's 4 threads and starve everything else that needs the pool; and calling sync `fs` functions or `requests.get` inside the loop freezes every request. `io_uring` works for files, but neither runtime uses it for files by default, and Docker's default seccomp profile blocks it.

### 33. [Mid] A slow client downloads a 200 MiB file, and the server's memory jumps. Why, and what is the fix?
*Chapters: [31](31-I-O-Operations.md), [32](32-Backend-Concurrency-Patterns.md), [27](27-System-Calls.md)*

The server reads faster than the client receives and holds the difference in RAM. Either it reads the whole file first (`readFile` then `res.send`, or `f.read()` then return), or it streams but ignores backpressure. Memory then grows with file size × concurrent downloads. The fix is to **stream with backpressure**. In Node, `write()` returns `false` when the buffer is full, and you wait for `'drain'`; `stream.pipeline()` does this for you and cleans up when the client disconnects. In asyncio, `await writer.drain()`; in ASGI frameworks, `StreamingResponse` or `FileResponse`. In the chapter's test, a streamed 200 MiB download grew Node's RSS by about 24 MiB and uvicorn's by about 2 MiB. For large static files, `sendfile` copies from file to socket inside the kernel. Python has `socket.sendfile()`; Node core has no `sendfile` API, so put nginx or a CDN in front.

### 34. [Mid] Choose an IPC mechanism for each case.
*Chapters: [28](28-Inter-Process-Communication.md), [24](24-Virtual-Memory.md), [29](29-Signals.md)*

- Parent and child on one host → a **pipe** or socket pair (Node's `child_process.fork()` IPC channel, Python's `multiprocessing.Pipe`).
- A local daemon with many clients → a **Unix domain socket**: protected by file permissions, `SO_PEERCRED` reports the caller's UID, and there is no TCP/IP stack in the way. PostgreSQL and Docker use one.
- Another host → **TCP**.
- Large read-mostly data shared by workers → **shared memory** or a memory-mapped file. `/dev/shm` is RAM charged to the container, and Docker gives it only 64 MiB by default.
- Work that must survive a crash or a deploy → a **durable queue** with acknowledgements.
- "Please shut down" or "reload your config" → a **signal**.

On stream channels, frame your messages (newline-delimited JSON or a length prefix), because one `read` is not one message. Never unpickle data from a process you don't trust.

---

## G. Putting it together

### 35. [Senior] Walk through what the OS does when an HTTP request reaches a Node or Python service in a container.
*Chapters: [01](01-Operating-Systems-Fundamentals.md), [27](27-System-Calls.md), [31](31-I-O-Operations.md), [07](07-CPU-Scheduling.md), [08](08-Context-Switching.md), [21](21-Memory-Management.md)*

1. The event-loop thread is asleep in `epoll_wait`; it got there with a voluntary context switch.
2. The network card raises an interrupt. The kernel's TCP/IP stack checks and reassembles the packets, appends the bytes to the socket's receive buffer, and marks the socket readable.
3. The kernel wakes the thread. The scheduler runs it when a CPU is free and the cgroup still has CPU quota in this period; if not, it waits (throttling).
4. `epoll_wait` returns the ready descriptor. The loop calls `accept4` for a new connection (which takes a file descriptor) and `read` for the request bytes. Each is a system call: a mode switch, not a context switch.
5. Your handler parses HTTP and runs in user space, allocating objects on the heap. New pages arrive lazily on first write (minor faults), and all of it is charged to the container's `memory.max`.
6. A database query is a `write` to the DB socket and another `epoll_wait`. A file read goes to libuv's thread pool or `asyncio.to_thread`, and is often served from the page cache.
7. The response goes out with `write`/`writev`, with backpressure if the client is slow.

Be ready to zoom in anywhere: what `strace -f -c` shows (and that it is heavy: the chapter's test went from 0.2 s to 7.6 s), why a 200 ms CPU loop in the handler delays every request on the loop, what happens if memory crosses the limit, or what `SIGTERM` does mid-request.

### 36. [Senior] Size the database connection pool and the request queue: 300 req/s per service, 40 ms per query, 4 replicas, PostgreSQL `max_connections = 100`.
*Chapters: [32](32-Backend-Concurrency-Patterns.md), [15](15-Semaphore.md), [04](04-Process-vs-Thread.md), [20](20-Starvation.md)*

Little's law: busy connections = λ × W = 300 × 0.04 = 12 across the service, or about 3 per replica on average. Size for peak with headroom (×1.2–1.5) and for bursts. Then check the budget: **pool size × processes per replica × replicas ≤ `max_connections`**, minus a reserve for admin work. With 4 Gunicorn workers per replica and a pool of 8 each, that is 4 × 4 × 8 = 128, which is too many; use fewer workers, smaller pools, or PgBouncer. Now the failure case. If queries slow to 400 ms, you would need 120 connections; a pool of 20 caps throughput at 20 ÷ 0.4 = 50 req/s. The rest must wait in a **bounded** queue sized from the wait you can accept (throughput × acceptable wait), and then be rejected early with `503 + Retry-After`, before parsing bodies or touching the database. Set the pool's acquire timeout below the request deadline, never hold a connection across an outbound HTTP call, and make clients back off with jitter. **Detect:** pool wait time p99, connections in use vs pool size, queue depth and oldest-item age, rejection counts, and connection counts in `pg_stat_activity`.

### 37. [Senior] The same CPU-heavy endpoint (say, image thumbnailing) makes both a Node service and a FastAPI service slow for every user. Compare the fixes.
*Chapters: [04](04-Process-vs-Thread.md), [10](10-Parallelism.md), [20](20-Starvation.md), [03](03-Threads.md), [07](07-CPU-Scheduling.md)*

**Node:** the CPU work runs on the one JavaScript thread, so timers and I/O for every other request wait: event-loop starvation. Move the work to a fixed `worker_threads` pool sized to the CPU quota, transfer `ArrayBuffer`s instead of cloning them, and put a bounded queue in front that sheds load when full. **Python (FastAPI):** in an `async def` endpoint, the work blocks the event loop in the same way. Making it a plain `def` endpoint runs it in AnyIO's thread pool (40 threads). That frees the loop, but because of the GIL it gives no parallelism for pure-Python code, and slow tasks can fill those 40 threads and starve other sync endpoints. For real speed-up, use a `ProcessPoolExecutor` sized to the quota (or a library that releases the GIL), or a job queue with separate worker processes. In both runtimes: one pool per kind of work, size from `cpu.max` and not the host's cores, and consider a separate deployment for the CPU work so its throttling doesn't hurt API latency. **Detect:** event-loop lag (Node's `monitorEventLoopDelay`; asyncio debug mode flags steps over 100 ms), throttling in `cpu.stat`, and queue time in the pool.

# Module 04 Operating Systems — Quick Reference

Use this for fast revision. Every chapter has one definition, a plain-English explanation, and a small example you could say out loud in an interview. All examples assume Linux, usually inside a container, with a Node.js or Python service on top.

## Processes and threads

### [Operating Systems Fundamentals](01-Operating-Systems-Fundamentals.md)
**Definition:** The kernel is the privileged core that owns the CPU, memory, devices and network stack; user-space programs reach it only through system calls, exceptions and interrupts.
**Simple explanation:** Your server is a guest in a hotel: it has its own room, and it calls the front desk (a system call) for anything outside it.
**Small example:** A container is just processes on the host kernel with namespaces and cgroups, so `uname -r` inside it prints the host's kernel version.

### [Processes](02-Processes.md)
**Definition:** A process is a running program plus what the kernel tracks for it: a private address space, a file descriptor table, a PID, credentials, environment, signal handlers and one or more threads.
**Simple explanation:** Unix makes a process in two steps: `fork()` clones the caller, then `exec()` loads a new program into the clone.
**Small example:** `spawn("convert", [name, "out.png"])` (Node) or `subprocess.run(["convert", name, "out.png"], timeout=10)` (Python) runs a tool with no shell, so a file name like `x; rm -rf /` is just a strange name.

### [Threads](03-Threads.md)
**Definition:** A thread is a flow of execution inside a process with its own stack, registers and thread ID, sharing the heap, globals and file descriptors with the other threads.
**Simple explanation:** Threads are cheap to coordinate because they share memory, and easy to break for the same reason.
**Small example:** In standard CPython, four threads running a pure-Python loop take as long as one because of the GIL, but four threads waiting on HTTP calls overlap their waits, because blocking I/O releases the GIL.

### [Process vs Thread](04-Process-vs-Thread.md)
**Definition:** On Linux both are tasks made by `clone()`; a process gets its own address space and descriptor table, while a thread shares its creator's.
**Simple explanation:** Processes buy isolation with memory and IPC costs; threads buy cheap sharing with races and a whole-process blast radius.
**Small example:** Run a crash-prone native image parser in a child process with a timeout, because a segfault in a thread would kill every request the server is handling.

### [Process Lifecycle](05-Process-Lifecycle.md)
**Definition:** A process goes fork → exec → exit → wait, moving through the states R, S, D, T and Z on the way.
**Simple explanation:** A dead child stays as a zombie until its parent collects its exit status, and PID 1 in a container must do that collecting for orphans.
**Small example:** `CMD npm start` makes `sh` PID 1, `SIGTERM` never reaches Node, and every deploy ends with exit code 137 after the stop timeout; `CMD ["node", "server.js"]` with `--init` fixes it.

### [Thread Lifecycle](06-Thread-Lifecycle.md)
**Definition:** A thread moves through new → runnable → running → blocked → terminated, and must then be joined or detached.
**Simple explanation:** You cannot safely kill a thread from outside; you ask it to stop and it checks a flag and exits by itself.
**Small example:** A Python worker loop uses `stop.wait(60)` instead of `time.sleep(60)`, so it notices the stop `Event` at once and shutdown does not hang for a minute.

### [CPU Scheduling](07-CPU-Scheduling.md)
**Definition:** The scheduler picks which runnable thread runs on which CPU and for how long, using the fair class (CFS, and EEVDF since Linux 6.6) for normal tasks.
**Simple explanation:** Nice values change a task's share only when CPUs are contended, and a container CPU limit is a quota per 100 ms period.
**Small example:** With `cpu.max = "50000 100000"` (0.5 CPU), eight busy threads use the quota in about 6 ms, and the whole container is throttled for the remaining ~94 ms.

### [Context Switching](08-Context-Switching.md)
**Definition:** A context switch is the kernel saving one thread's registers and loading another's on a CPU, plus a page-table switch if the new thread is in another process.
**Simple explanation:** The direct cost is a microsecond or so; the bigger cost is cold caches and TLB for the thread that runs next.
**Small example:** 20,000 tiny jobs caused about 20,000 switches with 32 Node workers but almost none on a single event loop, where a hand-off is just a function call.

## Concurrency and synchronization

### [Concurrency](09-Concurrency.md)
**Definition:** Concurrency is structuring a program so several tasks can be in progress at once, whether or not they run at the same instant.
**Simple explanation:** Concurrency is dealing with many things at once; it helps I/O-bound work even on one core.
**Small example:** `Promise.all(urls.map(fetch))` rejects on the first failure but does not stop the other requests; `asyncio.TaskGroup` cancels the siblings.

### [Parallelism](10-Parallelism.md)
**Definition:** Parallelism is work really executing at the same instant on several cores, and it only speeds up CPU-bound work.
**Simple explanation:** The serial part of a job sets a hard ceiling on speed-up, however many workers you add (Amdahl's law).
**Small example:** If 90% of a job parallelises, 8 workers give about 4.7×, and no number of workers gives more than 10×.

### [Synchronization](11-Synchronization.md)
**Definition:** Synchronization is how concurrent tasks agree on who may touch shared state now (mutual exclusion) and what must happen before what (ordering).
**Simple explanation:** Name the coordination problem first, then pick the primitive: mutex, semaphore, condition variable, barrier, event, atomic, once, or queue.
**Small example:** A worker that must wait for config to load uses an `Event` (or a promise), not a mutex, because a mutex stops overlap but does not make B wait for A.

### [Critical Sections](12-Critical-Sections.md)
**Definition:** A critical section is code that touches shared state and must not overlap with other code touching the same state, defined by the invariant it protects.
**Simple explanation:** Keep it small: compute outside the lock, then take the lock only to check and publish the result.
**Small example:** A token refresher fetches the new token outside the lock and only swaps the reference inside it, so readers never wait 300 ms for the network.

### [Race Conditions](13-Race-Conditions.md)
**Definition:** A race condition is a bug where the result depends on the timing or interleaving of concurrent operations.
**Simple explanation:** The two classic shapes are read-modify-write (lost update) and check-then-act (two callers both see "not there yet").
**Small example:** In Node, five requests that each `await db.exists(key)` before `create(key)` can all pass the check, so five records are created with no threads involved.

### [Mutex](14-Mutex.md)
**Definition:** A mutex is a lock with an owner that lets one task at a time into a critical section.
**Simple explanation:** Always release it in `finally` or a `with` block, and remember it only works inside one process.
**Small example:** `with lock: balance += amount` in Python, or `const release = await mutex.acquire(); try { … } finally { release(); }` in TypeScript.

### [Semaphore](15-Semaphore.md)
**Definition:** A semaphore is a counter of permits with no owner: `acquire` takes one or waits, `release` returns one.
**Simple explanation:** Its main backend use is limiting how many calls are in flight to a dependency.
**Small example:** `asyncio.Semaphore(10)` around a partner API call keeps at most 10 requests in flight, even when the partner slows from 50 ms to 2 s.

### [Spinlocks](16-Spinlocks.md)
**Definition:** A spinlock waits by busy-looping on an atomic instruction instead of sleeping in the kernel.
**Simple explanation:** Spinning wins only when the wait is a few microseconds and the holder is running on another core; in user space it is usually wrong.
**Small example:** Real mutexes do a compare-and-swap, spin briefly, then sleep with `futex`, so an uncontended lock never makes a system call.

### [Condition Variables](17-Condition-Variables.md)
**Definition:** A condition variable lets a thread sleep until a predicate on shared state is true, always used with the mutex that protects that state.
**Simple explanation:** Always wait in a `while` loop, because a wakeup only means "look again", not "the condition is true".
**Small example:** Python's `queue.Queue(maxsize=100)` is one lock plus two conditions: producers wait on "not full", consumers on "not empty".

### [Deadlocks](18-Deadlocks.md)
**Definition:** A deadlock is a set of tasks where each waits for something another one in the set holds, so none can move.
**Simple explanation:** It needs all four Coffman conditions (mutual exclusion, hold and wait, no preemption, circular wait), so breaking any one prevents it.
**Small example:** Two transfers A→B and B→A each lock their source first and wait forever; locking accounts in sorted ID order removes the cycle.

### [Livelocks](19-Livelocks.md)
**Definition:** A livelock is tasks that keep running and reacting to each other without any of them making progress.
**Simple explanation:** In a deadlock everyone waits; in a livelock everyone works, uselessly, usually because they retry in lockstep.
**Small example:** Two workers that release and retry a try-lock immediately collide forever; a random, growing delay (`random(0, min(cap, base·2^n))`) breaks the symmetry.

### [Starvation](20-Starvation.md)
**Definition:** Starvation is a ready task that is always passed over while the rest of the system makes progress.
**Simple explanation:** It is a fairness failure, caused by unfair locks, strict priorities, reader-preferring locks, hot tenants or a monopolised event loop.
**Small example:** One tenant's bulk upload fills a shared FIFO queue and every other customer waits; per-tenant queues served round robin fix it.

## Memory

### [Memory Management](21-Memory-Management.md)
**Definition:** The OS allocates pages lazily, protects them, shares what it can, and reclaims memory when RAM runs short, killing a process if it must.
**Simple explanation:** VSZ is reserved address space, RSS is what is in RAM, and PSS splits shared pages fairly between processes.
**Small example:** A Node container with a 1 GiB limit and no `--max-old-space-size` gets `SIGKILL` from the cgroup OOM killer (exit 137, `OOMKilled`) with no log line.

### [Heap Memory](22-Heap-Memory.md)
**Definition:** The heap holds every object whose lifetime is not tied to one function call, which in Node and Python means every object.
**Simple explanation:** A garbage-collected leak is memory that is still reachable, such as an unbounded cache or listeners that are never removed.
**Small example:** A module-level `Map` caching results per user ID grows until OOM; an LRU with a maximum size and a TTL fixes it.

### [Stack Memory](23-Stack-Memory.md)
**Definition:** Each thread has a call stack of frames holding return addresses, saved registers and local variables, freed automatically on return.
**Simple explanation:** Stacks are small and fixed, so recursion depth must never be decided by user input.
**Small example:** A 1.5 MB JSON body nested 50,000 levels deep makes a recursive walker throw `RangeError` in Node or `RecursionError` in Python; a depth limit plus an explicit stack fixes it.

### [Virtual Memory](24-Virtual-Memory.md)
**Definition:** Each process gets a private virtual address space that the MMU translates to physical RAM through the process's own page tables.
**Simple explanation:** The same address in two processes points to different RAM, and shared libraries and copy-on-write pages exist in RAM only once.
**Small example:** After `fork()` in a pre-forked Gunicorn server, merely reading 1M preloaded Python objects writes their refcounts and turned about 108 MiB of shared pages into private copies.

### [Paging](25-Paging.md)
**Definition:** Paging splits virtual memory into fixed-size pages (4 KiB on x86-64) and RAM into frames, loading pages on demand.
**Simple explanation:** A minor fault needs no disk and costs microseconds; a major fault reads from disk or swap and shows up as latency.
**Small example:** Allocating a 1 GiB buffer barely changes RSS; RSS grows only as pages are first written, which is why the OOM kill comes later, under load.

### [Segmentation](26-Segmentation.md)
**Definition:** Segmentation divides memory into variable-size segments with a base and a limit; x86-64 Linux uses a flat model and keeps only FS and GS for thread-local and per-CPU data.
**Simple explanation:** Paging replaced it, but the name survived: any invalid memory access caught by the page tables is still called a "segmentation fault".
**Small example:** A Python service exiting with code 139 (128 + `SIGSEGV`) almost always points at a C extension or native addon, so you turn on `PYTHONFAULTHANDLER=1` rather than adding RAM.

## Kernel interface and I/O

### [System Calls](27-System-Calls.md)
**Definition:** A system call is a user process asking the kernel to do something privileged, by putting a syscall number and arguments in registers and running the `syscall` instruction.
**Simple explanation:** Each crossing costs from hundreds of nanoseconds to a few microseconds, so buffering and batching matter.
**Small example:** Writing 100,000 log lines with one `write` each took 207 ms in Node; buffering them into 64 KiB chunks (79 writes) took 96 ms.

### [Inter Process Communication](28-Inter-Process-Communication.md)
**Definition:** IPC is how processes that do not share memory exchange data: pipes, Unix domain sockets, TCP, shared memory, message queues and signals.
**Simple explanation:** Choose by scope and durability, and remember that stream channels have no message boundaries, so you must frame messages yourself.
**Small example:** PostgreSQL's local connections use a Unix socket, protected by file permissions and able to report the peer's UID, with no TCP/IP stack in the way.

### [Signals](29-Signals.md)
**Definition:** A signal is a small asynchronous notification from the kernel to a process, carrying only a number, handled by a default action, ignored, or caught.
**Simple explanation:** `SIGTERM` asks a process to shut down and can be caught; `SIGKILL` cannot, so no cleanup code runs.
**Small example:** On `SIGTERM` a worker stops taking jobs, drains in-flight work within 20 s (under Kubernetes' 30 s grace period), and exits 0, or 1 if it had to abandon work.

### [File Systems Basics](30-File-Systems-Basics.md)
**Definition:** A file is an inode (metadata plus data blocks); names are directory entries pointing to inodes, and processes reach open files through file descriptors.
**Simple explanation:** `write()` returning means the data is in the page cache; only `fsync` means it is on disk.
**Small example:** Atomic config update: write a temp file in the same directory, `fsync` it, `rename` it over the target, then `fsync` the directory.

### [I/O Operations](31-I-O-Operations.md)
**Definition:** I/O can be blocking, non-blocking (returns `EAGAIN`), readiness-based (`epoll` says "fd 7 is readable") or completion-based (`io_uring` says "the read is done").
**Simple explanation:** Sockets use `epoll`, but regular files are always "ready", so Node and asyncio send file work to threads.
**Small example:** Streaming a 200 MiB file to a slow client with `pipeline()` grew Node's RSS by about 24 MiB, not 200 MiB, because backpressure paused the reads.

### [Backend Concurrency Patterns](32-Backend-Concurrency-Patterns.md)
**Definition:** The standard building blocks for overloaded or shared resources: sized worker pools, bounded queues, load shedding, fan-out with deadlines, single-flight and connection pools.
**Simple explanation:** Little's law (work in progress = arrival rate × time in system) sizes pools, and every queue needs a bound.
**Small example:** At 300 req/s and a 40 ms query, 12 connections are busy; if the query slows to 400 ms, a pool of 20 caps throughput at 50 req/s, so the rest must get `503 + Retry-After`.

## How to revise

1. Read each **Definition** line aloud.
2. Explain the example without looking, then say what goes wrong if you do it the naive way.
3. For each example, say which Linux command or file would show it (`ps`, `/proc/<pid>/status`, `cpu.stat`, `memory.events`, `strace`).
4. Open the linked chapter when you cannot explain the trade-off.

## Related module resources

- [Module overview](README.md)
- [Module summary](module-summary.md)
- [Interview questions](interview_questions.md)
- [Practical tasks](tasks.md)

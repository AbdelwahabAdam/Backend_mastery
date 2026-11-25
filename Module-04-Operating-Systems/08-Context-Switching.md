# Context Switching

> **Module 04 · Operating Systems** · Prerequisites: [CPU Scheduling](07-CPU-Scheduling.md) · Next: [Concurrency](09-Concurrency.md)

---

## ⏱ If You Only Have 2 Minutes

- A **context switch** is the kernel stopping one thread on a CPU and starting another. It saves the old thread's registers (program counter, stack pointer, general and FPU/SIMD registers) and loads the new one's. If the new thread belongs to **another process**, it also switches the **page tables**.
- A **system call is not a context switch.** It is a *mode switch*: the same thread enters the kernel and comes back. A context switch happens only when the scheduler gives the CPU to a different task.
- **Voluntary** switch: the thread blocked (I/O, lock, sleep, empty queue). **Involuntary** switch: it was preempted (time slice over, or a more deserving task woke). Many involuntary switches mean more runnable threads than CPU.
- **Direct cost** is roughly a microsecond or a few, depending on the CPU and on security mitigations. The **indirect cost** is usually bigger: the new thread finds cold CPU caches, TLB and branch predictors, and the old one finds them cold again when it returns.
- A thread switch inside one process skips the page-table change, so it is cheaper than a process switch. PCID tags on x86 soften process switches by keeping TLB entries per address space.
- An **event loop** handles thousands of connections on one thread, so a hand-off between two requests is a function call, not a kernel switch. In our test, 20,000 tiny jobs cost **~20,000 switches with 32 Node workers** (~40,000 with 32 Python threads) and **almost none** on one event loop.
- Measure with `/proc/<pid>/status` (`voluntary_ctxt_switches`, `nonvoluntary_ctxt_switches`; **main thread only**), `/proc/<pid>/task/*/status`, `getrusage` (all threads), `pidstat -w`, `vmstat` (`cs` column) and `perf stat -e context-switches`.

---

## 1. What It Is and Why It Exists

A CPU core runs one thread at a time. A **context switch** is what lets many threads share it: the kernel freezes the running thread, stores everything needed to resume it later (its *context*), and loads the context of the next thread chosen by the [scheduler](07-CPU-Scheduling.md).

**Analogy:** a single desk shared by several accountants. When one goes to wait for a phone call, they pack their papers, notes and open ledgers into a box, and the next accountant unpacks theirs. Packing and unpacking takes a moment (the direct cost). The real loss is that the next accountant must find their place again: which page, which number they were adding, where they left the calculator (the cold caches). If the accountants share one office (threads of one process), at least the filing cabinets are the same. If they come from a different company (another process), the cabinets change too (page tables).

**The problem it solves.** Without switching, a thread that waits for a disk or a socket would hold the CPU idle, and one long computation would block everything else. Switching gives you:

- **Overlap:** while one thread waits for I/O, another computes.
- **Fairness and responsiveness:** a long-running thread is preempted, so a newly woken request handler can run.

**Why backend engineers care.** Switching is cheap per event but not free, and it multiplies. A thread-per-request server with 2,000 threads, or a pool of 64 threads in a 2-CPU container, can spend a noticeable share of its CPU and cache capacity on switching, and its latency gets noisier. Event loops, right-sized pools and batching exist largely to keep the switch count down.

---

## 2. How It Works

### What happens in a switch

```mermaid
sequenceDiagram
    participant A as "Thread A (user mode)"
    participant K as "Kernel on this CPU"
    participant B as "Thread B (user mode)"
    A->>K: blocks in read() (voluntary), or timer interrupt (preemption)
    K->>K: save A's user registers on A's kernel stack
    K->>K: schedule(): pick B from the run queue
    K->>K: if B is in another process, switch_mm: load B's page tables
    K->>K: switch_to: swap kernel stack pointer and saved registers
    K->>B: restore B's registers, return to user mode
    Note over B: B runs; its data may not be in L1/L2 or the TLB yet
```

1. **Entry into the kernel.** Something brings the CPU into kernel mode: the thread makes a blocking system call (`read`, `futex`, `epoll_wait`), or an interrupt arrives (the timer tick, a network card).
2. **Save the context.** The thread's user-mode registers are saved on its kernel stack. These include the instruction pointer, stack pointer, flags and general-purpose registers. FPU/SIMD state (x87, SSE, AVX registers) is saved too, which is large on modern x86.
3. **Pick the next task.** `schedule()` asks the scheduling classes for the next runnable task on this CPU's run queue.
4. **Switch address space, if needed.** If the next task belongs to a different process, the kernel loads its page-table root (the `CR3` register on x86). Threads of the same process share one memory map, so this step is skipped for them.
5. **Switch stacks and registers.** `switch_to` swaps the kernel stack pointer and the callee-saved registers. The CPU is now "inside" the new task's kernel stack.
6. **Return to user mode.** The new thread's saved registers are restored and it continues exactly where it stopped.

### Mode switch vs context switch

| Event | Which task runs afterwards | Page tables change? | Counted as a context switch? |
|---|---|---|---|
| Non-blocking system call (`getpid`, a `read` with data ready) | The same thread | No | No: a mode switch only |
| Interrupt handled, same thread continues | The same thread | No | No |
| Blocking system call that sleeps | Another task | Maybe | Yes, **voluntary** |
| Time slice used up, or preempted by a wake-up | Another task | Maybe | Yes, **involuntary** |
| `await` in Node or asyncio | The same OS thread runs another callback | No | No: a user-space hand-off |

This distinction matters in interviews and in profiling. `strace` shows thousands of system calls in an event-loop process, and almost none of them cause a context switch.

### Direct and indirect costs

**Direct cost**: entering the kernel, the scheduler's bookkeeping, saving and restoring registers, and possibly the page-table switch. On current x86 servers this is usually quoted as around one to a few microseconds per switch. Spectre/Meltdown mitigations (such as page-table isolation, KPTI) made kernel entry and exit more expensive, so the number depends on the kernel and CPU. Measure it on your hardware if it matters.

**Indirect cost**: what the switch does to the CPU's caches.

- **CPU caches (L1/L2, shared L3).** Thread B's working set evicts thread A's. When A runs again it takes cache misses, each costing tens to hundreds of cycles, until its data is back. For a thread with a large working set this can cost more than the switch itself.
- **TLB (translation lookaside buffer).** This is the cache of virtual-to-physical address translations. Switching processes historically flushed it. With **PCID** (x86) or ASIDs (Arm), entries are tagged per address space and can survive a switch, but space is limited and they still get evicted.
- **Branch predictors and prefetchers** have learned A's patterns and must relearn them.
- **Migration.** If the scheduler moves the thread to another CPU, it finds that CPU's private caches cold too.

### Thread switch vs process switch

| | Thread → thread, same process | Process → process |
|---|---|---|
| Registers, stacks | Saved and restored | Saved and restored |
| Page tables | Unchanged | Switched (`CR3` on x86) |
| TLB | Stays valid | Survives only if tagged (PCID), else flushed |
| Shared caches | Shared code and heap may still be warm | Different code and data: mostly cold |
| Typical relative cost | Lower | Higher |

### Why thousands of threads hurt

Each extra thread adds little on its own, but together they cost:

- **More switches per unit of work.** With thread-per-request, every request is at least one wake-up (the response arrives) and one sleep. At 20,000 requests per second, that is tens of thousands of switches per second before any lock contention.
- **Cache pollution.** 1,000 runnable threads each with a small working set still overflow the L2 cache, so every thread starts cold.
- **Lock convoys.** Threads queue on a hot mutex. Each release wakes the next waiter, which costs a switch, and the critical section effectively runs at the speed of the scheduler.
- **Scheduler latency.** Each runnable thread gets a slice in turn. More runnable threads per CPU means a longer wait before a just-woken request handler gets a CPU.
- **Quota burn in containers.** More busy threads use up the cgroup's CPU quota faster ([CPU Scheduling](07-CPU-Scheduling.md)).

### How event loops reduce switching

An event loop (Node's libuv loop, Python's asyncio, nginx) keeps one thread busy as long as **any** connection has work. It calls `epoll_wait` only when nothing is ready, and that single sleep covers every idle connection. Moving from request A to request B is a function return and a queue pop in user space. Under load the loop rarely sleeps at all, so the voluntary switch count *falls* as traffic rises, which is the opposite of thread-per-request. The cost is that a CPU-heavy callback blocks every other request on the loop ([Node Event Loop and Concurrency](../Module-02-Core-Backend/06-Node-Event-Loop-and-Concurrency.md)).

### Observing context switches

```bash
grep ctxt /proc/4211/status                       # main thread only
for t in /proc/4211/task/*; do grep -h ctxt $t/status; done | awk '{s[$1]+=$2} END {for (k in s) print k, s[k]}'
grep -E 'nr_(voluntary|involuntary)_switches' /proc/4211/sched
pidstat -w -p 4211 1          # per process, per second (cswch/s, nvcswch/s); add -t for per thread
vmstat 1                      # system-wide: cs = switches/s, in = interrupts/s, r = runnable
perf stat -e context-switches,cpu-migrations -p 4211 -- sleep 10
```

Illustrative output for a thread-per-job Python service under load:

```text
voluntary_ctxt_switches:        1235
nonvoluntary_ctxt_switches:     2

voluntary_ctxt_switches: 40698
nonvoluntary_ctxt_switches: 5

14:02:11      UID      TGID       TID   cswch/s nvcswch/s  Command
14:02:12     1000      4211         -  34812.00     14.00  python
14:02:12     1000         -      4219   1088.00      0.00  |__python
14:02:12     1000         -      4220   1091.00      1.00  |__python

procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 3  0      0 912344  80220 2140988    0    0     0     4 6120 41380 22 19 59  0  0

 Performance counter stats for process id '4211':
            41,630      context-switches          #    4.163 K/sec
               212      cpu-migrations            #   21.201 /sec
```

Read it like this:

- `/proc/<pid>/status` shows the **main thread** only (1,235). The sum over `/proc/<pid>/task/*` is the whole process (40,698). Exited threads drop out of that sum. `getrusage(RUSAGE_SELF)`, which both runtimes expose, still counts them.
- High `cswch/s` with low `nvcswch/s` means threads keep going to sleep and being woken: hand-offs and waiting, not CPU contention.
- High `nvcswch/s` means threads are being preempted: more runnable threads than CPUs, or CPU-heavy threads sharing cores.
- In `vmstat`, a high `sy` (system CPU) next to a high `cs` suggests the switching itself (and the futex traffic behind it) is now a real share of CPU time.

---

## 3. Key Concepts

### What is in "the context"

| Part | Saved/changed on every switch? | Note |
|---|---|---|
| Instruction pointer, stack pointer, flags, general registers | Yes | Small; stored on the kernel stack and in the task structure |
| FPU/SIMD state (SSE, AVX, AVX-512) | Yes, when the task used it | Can be kilobytes on CPUs with wide vector registers |
| Kernel stack | Swapped (pointer only) | Each thread has its own kernel stack |
| Page tables (memory map) | Only across processes | Threads share one map |
| TLB entries | Flushed or tagged across processes | PCID/ASID tagging avoids full flushes |
| CPU caches | Not saved, just overwritten over time | The main indirect cost |

### Voluntary vs involuntary switches

| | Voluntary | Involuntary |
|---|---|---|
| Cause | Thread blocked: I/O, `futex` (lock or condition), `sleep`, empty queue, `epoll_wait` | Preempted: slice used up, higher-priority wake-up, CPU quota |
| Healthy pattern | I/O-bound services: high, roughly proportional to requests | Low |
| Bad pattern | Very high with little I/O: lock contention, ping-pong hand-offs between threads | High: oversubscribed CPUs, too many busy threads, noisy neighbours |
| Where to read it | `voluntary_ctxt_switches`, `cswch/s`, `ru_nvcsw` | `nonvoluntary_ctxt_switches`, `nvcswch/s`, `ru_nivcsw` |

### Switch costs compared

| Switch | Who does it | Rough relative cost |
|---|---|---|
| `await` / callback hand-off on an event loop | User-space runtime | Lowest: a function call and a queue operation |
| Goroutine, Java virtual thread (M:N) | Language runtime | Low: no kernel entry when the runtime switches tasks |
| OS thread to OS thread, same process | Kernel | Medium: kernel entry, registers, warm-ish caches |
| OS thread to OS thread, different process | Kernel | Higher: plus page-table switch and colder caches |
| Thread migrated to another CPU | Kernel | Plus that CPU's cold private caches |

### Runtime specifics

- **Node:** the main thread switches when its loop sleeps in `epoll_wait`. `postMessage` to a worker wakes that worker's loop through libuv's async handle, so each message to an idle worker is a kernel wake-up. The libuv thread pool (fs, `dns.lookup`, crypto, zlib) adds a hand-off to a pool thread and back for each call.
- **Python threads:** the GIL adds switches. A thread that wants the GIL waits on a condition variable, so a GIL hand-off between threads is a futex wake-up. A waiting thread asks the holder to drop the GIL after the switch interval (5 ms by default). `queue.Queue` hand-offs add their own futex sleeps on top. That is why our Python thread test shows about two switches per job.
- **asyncio:** like Node, one thread and one `epoll_wait` for all idle sockets. `asyncio.to_thread` or a `def` endpoint in FastAPI goes back to thread hand-offs.

### Measuring without fooling yourself

- Use **rates** (switches per second, or per request), not totals since boot.
- Separate main thread from process: `/proc/<pid>/status` is the main thread; `getrusage` (`process.resourceUsage()` in Node, `resource.getrusage` in Python) covers all threads, including ones that already exited.
- Compare the **switches per request** before and after a change. Raw `cs` in `vmstat` rises with traffic anyway.

---

## 4. Code Examples

Scenario: process 20,000 tiny jobs with 32 jobs in flight, first by handing each job to one of 32 threads, then with 32 concurrent tasks on a single event loop. Count context switches for each.

### Node.js / TypeScript

```ts
// No npm packages — Node.js 22+, TypeScript 5, ESM. Linux (reads /proc/self/status).
import { once } from "node:events";
import { readFileSync } from "node:fs";
import { Worker } from "node:worker_threads";

const JOBS = 20_000;
const LANES = 32; // 32 jobs in flight at any moment in both versions

// /proc/self/status describes the MAIN thread only; resourceUsage() (getrusage) covers every thread.
function snapshot() {
  const status = readFileSync("/proc/self/status", "utf8");
  const field = (name: string) => Number(new RegExp(`^${name}:\\s+(\\d+)`, "m").exec(status)?.[1]);
  const ru = process.resourceUsage();
  return { threads: field("Threads"), mainVol: field("voluntary_ctxt_switches"),
    vol: ru.voluntaryContextSwitches, invol: ru.involuntaryContextSwitches, t: performance.now() };
}

function report(label: string, a: ReturnType<typeof snapshot>, b: ReturnType<typeof snapshot>): void {
  console.log(`${label.padEnd(22)} threads=${String(b.threads).padStart(2)}  wall=${(b.t - a.t).toFixed(0).padStart(5)} ms`
    + `  voluntary=${String(b.vol - a.vol).padStart(6)} (main thread ${b.mainVol - a.mainVol})`
    + `  involuntary=${b.invol - a.invol}`);
}

// A: one worker thread per lane. After each reply a worker has nothing to do, so it sleeps in
// epoll_wait and the kernel must switch it back in for the next job: about one switch per job.
async function viaWorkers(): Promise<void> {
  const tinyJob = `const { parentPort } = require("node:worker_threads");
    parentPort.on("message", (n) => parentPort.postMessage(n + 1));`;
  const pool = Array.from({ length: LANES }, () => new Worker(tinyJob, { eval: true }));
  await Promise.all(pool.map((w) => once(w, "online")));
  const a = snapshot();
  await Promise.all(pool.map(async (w) => {
    for (let i = 0; i < JOBS / LANES; i++) {
      w.postMessage(i);
      await once(w, "message");
    }
  }));
  report(`${LANES} workers`, a, snapshot());
  await Promise.all(pool.map((w) => w.terminate()));
}

// B: the same 32 lanes as async functions on one thread. A hand-off is a queued callback, not a wake-up.
async function viaEventLoop(): Promise<void> {
  const a = snapshot();
  await Promise.all(Array.from({ length: LANES }, async () => {
    for (let i = 0; i < JOBS / LANES; i++) {
      await new Promise<number>((resolve) => setImmediate(resolve, i + 1)); // yield to the loop each job
    }
  }));
  report("1 event loop", a, snapshot());
}

await viaWorkers();
await viaEventLoop();
```

Output (`node:22` container on a 16-CPU host; counts vary a little between runs):

```text
32 workers             threads=39  wall=  435 ms  voluntary= 20134 (main thread 28)  involuntary=34
1 event loop           threads= 7  wall=   19 ms  voluntary=    68 (main thread 14)  involuntary=2
```

About one voluntary switch per job with workers. Each worker sleeps after every reply, while the main thread almost never sleeps, because some reply is nearly always waiting. The single loop does the same hand-offs with almost no switches. It is about 20 times faster here, because the "work" is trivial and the switching *is* the cost. The remaining 68 switches come mostly from Node's own helper threads, not from the jobs.

### Python

```python
# No pip packages — Python 3.12+ (stdlib only). Linux (reads /proc/self/status).
import asyncio
import queue
import re
import resource
import threading
import time

JOBS = 20_000
LANES = 32  # 32 jobs in flight at any moment in both versions


def snapshot() -> dict[str, float]:
    # /proc/self/status describes the MAIN thread only; getrusage(RUSAGE_SELF) covers every thread.
    with open("/proc/self/status") as f:
        status = f.read()

    def field(name: str) -> int:
        return int(re.search(rf"^{name}:\s+(\d+)", status, re.M).group(1))

    ru = resource.getrusage(resource.RUSAGE_SELF)
    return {"threads": field("Threads"), "main_vol": field("voluntary_ctxt_switches"),
            "vol": ru.ru_nvcsw, "invol": ru.ru_nivcsw, "t": time.perf_counter()}


def report(label: str, a: dict[str, float], b: dict[str, float]) -> None:
    print(f"{label:<22} threads={b['threads']:2.0f}  wall={(b['t'] - a['t']) * 1000:5.0f} ms"
          f"  voluntary={b['vol'] - a['vol']:6.0f} (main thread {b['main_vol'] - a['main_vol']:.0f})"
          f"  involuntary={b['invol'] - a['invol']:.0f}")


def via_threads() -> None:
    jobs: queue.Queue[int | None] = queue.Queue()
    results: queue.Queue[int] = queue.Queue()

    def worker() -> None:
        # get() on an empty queue sleeps on a lock (a futex); every put() may have to wake a sleeper.
        while (n := jobs.get()) is not None:
            results.put(n + 1)

    threads = [threading.Thread(target=worker) for _ in range(LANES)]
    for t in threads:
        t.start()
    a = snapshot()
    for i in range(LANES):            # prime the lanes, then refill one job per finished job
        jobs.put(i)
    for i in range(LANES, JOBS + LANES):
        results.get()
        if i < JOBS:
            jobs.put(i)
    b = snapshot()
    for _ in threads:
        jobs.put(None)
    for t in threads:
        t.join()
    report(f"{LANES} threads", a, b)


async def via_event_loop() -> None:
    a = snapshot()

    async def lane() -> None:
        for _ in range(JOBS // LANES):
            await asyncio.sleep(0)    # yield to the loop each job: a hand-off, not a kernel wake-up

    async with asyncio.TaskGroup() as tg:
        for _ in range(LANES):
            tg.create_task(lane())
    report("1 event loop", a, snapshot())


if __name__ == "__main__":
    via_threads()
    asyncio.run(via_event_loop())
```

Output (`python:3.12` container on a 16-CPU host):

```text
32 threads             threads=33  wall= 1117 ms  voluntary= 41625 (main thread 1233)  involuntary=0
1 event loop           threads= 1  wall=   23 ms  voluntary=     0 (main thread 0)  involuntary=0
```

**Runtime differences to notice:**

- **Python threads switch about twice per job; Node workers about once.** Each Python hand-off goes through a `queue.Queue` (a lock and a condition variable, both futexes) *and* through the GIL, which itself is handed over with a futex wake-up. Node workers do not share a GIL. Each one sleeps in its own `epoll_wait` and is woken once per message.
- **The main-thread number is misleading on its own.** In both runs, `/proc/self/status` shows a tiny fraction of the real total. Always sum the tasks or use `getrusage`.
- **Involuntary switches are near zero.** There were 16 idle CPUs, so nobody was preempted. Pin the same test to one core (`docker run --cpuset-cpus=0`) and they jump: about 7,800 for the Python threads and 32,000 for the Node workers, because 33 or 39 threads now take turns on one CPU. A `--cpus=1` quota alone barely changed them in our runs. The threads mostly sleep, and they still spread across all 16 CPUs.

---

## 5. Production Concerns

- **Track switches per request, not just per second.** Export `voluntary_ctxt_switches` and `nonvoluntary_ctxt_switches` (summed over threads) or `getrusage` deltas. A release that doubles switches per request usually added a thread hand-off (a new pool, a sync call wrapped in `to_thread`, a lock).
- **Rising involuntary switches mean CPU contention.** On a pinned or small machine they rise as soon as there are more runnable threads than cores. Under a cgroup quota, a throttled thread counts about one involuntary switch per throttled period, however long the stall, so also check `cpu.stat` throttling and `cpu.pressure`. The fix is fewer busy threads or more CPU, not code micro-optimisation.
- **Size pools to avoid ping-pong.** A 200-thread pool in front of a 20-connection database pool means 180 threads wake, find no connection, and sleep again. Match pool sizes along the request path, and bound queues instead of adding threads.
- **Batch hand-offs.** Sending one message per item to a worker costs a wake-up per item. Send arrays of items, or use a `SharedArrayBuffer` ring buffer with `Atomics.wait`/`notify` only when the consumer is actually idle. In Python, prefer `chunksize` in `ProcessPoolExecutor.map` for many small items.
- **Keep CPU-heavy work off the event loop, but in few workers.** Moving work to `worker_threads` or a process pool adds a switch per job. That is fine for jobs of milliseconds, and wasteful for jobs of microseconds. Batch small jobs or keep them inline.
- **Pinning and isolation for extreme latency.** Latency-critical services (trading, ad bidding) pin threads to dedicated cores so they are never preempted and their caches stay warm. That is a last step, after the thread count is already right.
- **Kernel mitigations change the numbers.** After a kernel or microcode update, switch and syscall costs can move. Re-benchmark rather than trusting old numbers.

---

## 6. Common Mistakes

- **Calling a system call a context switch** — you over-estimate the cost of an event loop's thousands of `epoll_wait`/`read` calls — only a change of running task is a context switch; the rest are mode switches.
- **Reading `/proc/<pid>/status` as the process total** — it covers the main thread only, so a busy thread pool looks idle — sum `/proc/<pid>/task/*/status` or use `getrusage` / `pidstat -wt`.
- **Thread-per-connection for mostly idle connections** — thousands of sleeping threads, a wake-up and switch per message, memory for every stack — use an event loop or async framework for connection handling.
- **Oversized pools "for throughput"** — 64 CPU-bound threads on 4 CPUs add involuntary switches and cache misses, so throughput drops — size CPU-bound pools to the CPUs you actually have, including the quota.
- **One message per tiny job to a worker** — the wake-up costs more than the job — batch items, or keep microsecond jobs inline.
- **Blaming switches for every high `sy` value** — system CPU also comes from page faults, network stack work and syscalls themselves — confirm with `perf stat -e context-switches` and `perf top` before redesigning.

---

## 7. Comparison Table

| Model | Switch on each hand-off | Who switches | Cost per hand-off | Typical count of units |
|---|---|---|---|---|
| Thread-per-request (blocking I/O) | Kernel switch on every block and wake | Kernel | µs + cache effects | Hundreds to a few thousand threads |
| Thread pool + queue | Kernel switch when an idle worker is woken | Kernel | µs + cache effects | Pool size (tens) |
| Process pool | Kernel switch + IPC copy | Kernel | Higher: also page tables, serialization | One per core |
| Event loop (Node, asyncio) | None between callbacks; one sleep when idle | User space | Function call | Tens of thousands of connections per thread |
| M:N runtimes (goroutines, virtual threads) | Usually none; runtime swaps stacks | Language runtime | Sub-µs | Hundreds of thousands+ |

---

## 8. Interview Questions

**[Junior] What is a context switch?**
The kernel stops the thread running on a CPU, saves its registers and state, and loads the state of another thread so that one runs instead. If the new thread belongs to another process, the kernel also switches the page tables. It happens when a thread blocks (voluntary) or when the scheduler preempts it (involuntary).

**[Junior] Is a system call a context switch?**
No. A system call is a mode switch: the same thread moves from user mode to kernel mode and back. It becomes a context switch only if the call blocks and the scheduler runs a different thread meanwhile. So `read()` on a socket with data already available costs a mode switch, and `read()` on an empty blocking socket costs a context switch.

**[Mid] Why is switching between threads of the same process cheaper than between processes?**
Threads share an address space, so the kernel does not need to load new page tables, and TLB entries stay valid. Shared code and heap data may still be in cache. A process switch changes the memory map and, without PCID tagging, flushes the TLB, so the new process starts with colder caches. In both cases registers and stacks are swapped, and the indirect cache cost often dominates.

**[Mid] What is the difference between voluntary and involuntary context switches, and what does each tell you?**
Voluntary switches happen when a thread blocks: on I/O, a lock, a sleep, or an empty queue. High counts are normal for I/O-bound services, but very high counts with little I/O point to lock contention or ping-pong hand-offs. Involuntary switches happen when a runnable thread is preempted. High counts mean there is more runnable work than CPU: too many busy threads, noisy neighbours, or a CPU quota.

**[Mid] How would you measure context switches for one service on Linux?**
`pidstat -w -p <pid> 1` for voluntary and involuntary rates per process, `-t` per thread. `/proc/<pid>/status` for the main thread's counters and `/proc/<pid>/task/*/status` for each thread. `vmstat 1` for system-wide switches per second, and `perf stat -e context-switches,cpu-migrations -p <pid>` for an interval. In code, `getrusage` covers all threads: `process.resourceUsage()` in Node, `resource.getrusage` in Python. Normalise by requests served.

**[Senior] Why do event-loop servers scale to many more connections than thread-per-connection servers?**
An idle connection on an event loop costs a file descriptor and a small object, and the single thread sleeps in one `epoll_wait` for all of them. Moving from one ready connection to the next is a function call, not a kernel switch, and under load the loop hardly ever sleeps. Thread-per-connection needs a stack per connection and a kernel wake-up and switch every time a connection becomes active, plus the cache pollution of many threads. The trade-off is that one CPU-heavy handler stalls every connection on the loop, so CPU work moves to a small pool.

**[Senior] A service moved from 16 to 128 worker threads to "increase throughput" and got slower. Explain.**
If the work is CPU-bound and the container has, say, 4 CPUs, 128 runnable threads only add involuntary switches, cache and TLB misses, and scheduler latency, and they burn the cgroup quota faster, causing throttling. If the threads share a lock or a 20-connection database pool, most of them wake only to find the resource busy and sleep again, which is a lock convoy: more voluntary switches, no extra work done. Measure switches per request, involuntary switches and throttling, then size CPU pools to the CPUs and I/O pools to the downstream's capacity.

**[Senior] How do Node and CPython differ in context-switch behaviour under multi-threaded work?**
Node worker threads each run their own event loop with no shared lock, so a hand-off to a worker is one wake-up of that worker's loop, and CPU work in workers runs truly in parallel. CPython threads share the GIL. Handing the GIL to another thread is itself a futex wake-up, so threads contending for it switch often even on CPU work, and queue hand-offs add more. In our test, Python threads needed about two switches per tiny job and Node workers about one. Both disappear when the work stays on one event loop. On free-threaded CPython builds, the GIL hand-offs go away, but queue and lock hand-offs remain.

---

## 9. Cheat Sheet

```text
Context switch  kernel saves A's registers (PC, SP, flags, GPRs, FPU/SIMD), loads B's
Process switch  + page tables (CR3), TLB flush unless PCID/ASID-tagged
Mode switch     syscall/interrupt in the same thread: NOT a context switch
Voluntary       thread blocked (I/O, futex, sleep, empty queue, epoll_wait)
Involuntary     preempted (slice over, wake-up, CPU quota) → too much runnable work
Direct cost     ~1 to a few µs (CPU- and mitigation-dependent)
Indirect cost   cold L1/L2/L3, TLB, branch predictors; migration = cold private caches
Many threads    more wake-ups, cache pollution, lock convoys, longer run queues, quota burn
Event loop      one epoll_wait for all idle sockets; hand-offs are function calls
Python GIL      GIL hand-off = futex wake-up → extra switches between threads
Observe         /proc/PID/status (main thread!) · /proc/PID/task/*/status · /proc/PID/sched
Tools           pidstat -w[t] (cswch/s, nvcswch/s) · vmstat 1 (cs) · perf stat -e context-switches
In code         process.resourceUsage().voluntaryContextSwitches · resource.getrusage().ru_nvcsw
Normalise       switches per request; compare before/after a change
```

---

## Related Topics

- [CPU Scheduling](07-CPU-Scheduling.md) — the decisions that trigger each switch, and CPU quotas
- [Concurrency](09-Concurrency.md) — event loops vs threads as ways to structure overlapping work
- [Threads](03-Threads.md) — what each thread owns, which is exactly what a switch saves
- [Paging](25-Paging.md) — page tables and the TLB that a process switch disturbs
- [Spinlocks](16-Spinlocks.md) — when spinning is cheaper than sleeping and being switched out
- [Node Event Loop and Concurrency](../Module-02-Core-Backend/06-Node-Event-Loop-and-Concurrency.md) — why one thread can serve many connections

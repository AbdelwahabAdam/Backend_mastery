# Virtual Memory

> **Module 04 · Operating Systems** · Prerequisites: [Memory Management](21-Memory-Management.md), [Stack Memory](23-Stack-Memory.md) · Next: [Paging](25-Paging.md)

---

## ⏱ If You Only Have 2 Minutes

- Every process gets its own **virtual address space**. On x86-64 Linux, user space is the lower 128 TiB (47-bit addresses). The **MMU** translates each address through the process's own **page tables**, so address `0x7f00…` in two processes points to different RAM.
- Each page carries **protection bits**: present, writable, user-accessible, no-execute. Touching an unmapped address, or writing to a read-only page, raises a fault, and the kernel sends `SIGSEGV`. This is how processes are isolated from each other and from the kernel.
- `mmap` adds a region to the address space. It can be **file-backed** (code, shared libraries, data files) or **anonymous** (heap, stacks), and **private** (copy-on-write) or **shared** (writes are visible to everyone mapping it).
- **Shared libraries are in RAM once.** Every process maps the same page-cache pages of `libc.so.6` or `libpython3.12.so`. That is why summed RSS over-counts and PSS doesn't.
- `fork()` copies page tables, not memory. Pages are shared **copy-on-write** until someone writes. In CPython, merely *reading* an object writes its reference count. In a measured test, a child that iterated over 1M preloaded objects turned about 108 MiB of shared memory into private copies.
- `gunicorn --preload` plus the `gc` recipe (`gc.disable()` early, `gc.freeze()` before forking, `gc.enable()` in the child) stops the **cycle collector** from un-sharing pages (measured 46 MiB → 0). It cannot stop refcount writes.
- A **memory-mapped file** gives large read-only data (lookup tables, models, indexes) to many workers with one copy in the page cache, loading only the pages that are touched. Python has `mmap` in the stdlib. Node core does not, so use positional reads (`pread`) instead.
- Read `/proc/<pid>/maps` to see the layout, and `/proc/<pid>/smaps_rollup` for `Rss`, `Pss`, `Shared_*` and `Private_Dirty`.

---

## 1. What It Is and Why It Exists

**Virtual memory** means that the addresses a program uses are not physical RAM addresses. Each process sees a large, private, apparently contiguous range of addresses. The kernel and the CPU's **memory management unit (MMU)** translate every access to a real location in RAM. If nothing is there yet, the access becomes a page fault that the kernel handles.

**Analogy:** every employee in a company has a personal phone with speed-dial numbers. "Speed-dial 3" means the dentist on one phone and a supplier on another. The phone network (MMU) translates each number to a real line (physical frame). Some numbers point to a shared line everyone can call, such as the help desk (a shared library). Some numbers are not set up at all, and dialling them gets an error (`SIGSEGV`). Nobody can dial into someone else's private list.

**The problems it solves:**

- **Isolation.** A process cannot even name another process's memory. A bug in one worker cannot corrupt another worker or the kernel.
- **Simplicity.** Every program can be linked and loaded as if it owned the whole machine. The loader doesn't need to know where other programs sit in RAM.
- **Efficiency.** Memory is assigned lazily on first touch. Identical pages (libraries, `fork`ed data, files) are kept once and shared. Cold pages can be dropped or swapped.
- **Files as memory.** `mmap` lets a program treat a file as an array, and the kernel loads only the parts it touches.

**The cost.** Every access needs a translation, which the TLB makes cheap most of the time ([Paging](25-Paging.md) owns the mechanics). Memory accounting also gets confusing: VSZ, RSS and PSS disagree, and sharing slowly erodes after `fork`. Pre-forked Python servers and Redis snapshots both pay for that.

---

## 2. How It Works

### From address to RAM, in brief

1. The kernel keeps a list of **VMAs** (virtual memory areas) per process. Each VMA is a range with permissions and a backing source: a file and offset, or anonymous memory. One VMA is one line of `/proc/<pid>/maps`.
2. The CPU never looks at VMAs. It walks the **page tables**, a per-process radix tree that maps 4 KiB virtual pages to physical frames. The tree's root is loaded into the `CR3` register on every switch between processes.
3. If the page-table entry is missing or forbids the access, the CPU raises a **page fault**. The kernel checks the VMA. If the access is legal (first touch, file page, copy-on-write), it fixes the page table and retries. If not, it sends `SIGSEGV`.

That last step is why allocating memory is cheap and touching it is what costs. Page-table formats, the TLB, fault types and swap are covered in [Paging](25-Paging.md).

### Copy-on-write after `fork`

```mermaid
sequenceDiagram
    participant P as Parent (gunicorn master)
    participant K as Kernel
    participant C as Child (worker)
    P->>K: fork()
    K->>K: copy VMAs and page tables, not the pages
    K->>K: mark private writable pages read-only in BOTH page tables
    K-->>C: child runs; every page is shared (Shared_Dirty)
    C->>C: read catalog[0]  (CPython increments its refcount: a WRITE)
    C->>K: page fault: write to read-only page in a writable private VMA
    K->>K: copy the 4 KiB page, map the copy writable for the child only
    K-->>C: retry the write; page now counts as Private_Dirty
    Note over P,C: Pages nobody writes stay shared for the life of both processes
```

The kernel shares one physical page between parent and child until one of them writes to it. Then the writer gets its own copy of that page only. A child that `exec`s straight away copies almost nothing. A pre-forked worker that keeps running the parent's code slowly copies every page it writes to.

### Protection bits

Each page-table entry has a small set of flags that the hardware checks on every access:

| Bit | Meaning | What breaks it |
|---|---|---|
| Present | The page is mapped to a frame | Access → page fault; the kernel decides if it is legal |
| Writable | Writes allowed | Write to code or `PROT_READ` data → `SIGSEGV`. On a CoW page the kernel copies instead |
| User | User mode may access | Any user access to kernel memory → `SIGSEGV` |
| No-execute (NX) | Instructions may not run from here | Jumping into the heap or stack → `SIGSEGV` |

Together with randomized layout (**ASLR**, `/proc/sys/kernel/randomize_va_space` = 2 by default), these bits are why a buffer overflow in a native library usually crashes instead of running attacker code. JIT compilers such as V8 must explicitly flip pages between writable and executable when they emit machine code.

### Observing the address space

```bash
cat /proc/<pid>/maps                       # every VMA: range, perms, offset, device, inode, path
grep -E '^(Rss|Pss|Shared|Private|Anonymous|Swap)' /proc/<pid>/smaps_rollup
pmap -x <pid> | tail -1                    # totals: virtual size, RSS, dirty
```

Excerpt from a Python 3.12 process that mapped one file read-only and 64 MiB of anonymous memory (real output, trimmed):

```text
58277c127000-58277c128000 r--p 00000000 00:89 310941   /usr/local/bin/python3.12
58277c128000-58277c129000 r-xp 00001000 00:89 310941   /usr/local/bin/python3.12
5827aeb0d000-5827aec7d000 rw-p 00000000 00:00 0        [heap]
7a723791d000-7a723b91d000 rw-s 00000000 00:01 7174     /dev/zero (deleted)
7a723b91d000-7a723b921000 r--s 00000000 00:89 310941   /usr/local/bin/python3.12
7a723bce3000-7a723bd0b000 r--p 00000000 00:89 306816   /usr/lib/x86_64-linux-gnu/libc.so.6
7a723bd0b000-7a723be6e000 r-xp 00028000 00:89 306816   /usr/lib/x86_64-linux-gnu/libc.so.6
7a723bfd9000-7a723c1f9000 r-xp 00100000 00:89 311188   /usr/local/lib/libpython3.12.so.1.0
7a723c537000-7a723c539000 r-xp 00000000 00:00 0        [vdso]
7ffead810000-7ffead831000 rw-p 00000000 00:00 0        [stack]
```

How to read it:

- The permission column ends in `p` (private, copy-on-write) or `s` (shared).
- Code is `r-xp` and file-backed. Libraries appear once per segment (read-only, code, relocations, writable data).
- Python's `mmap.mmap(-1, n)` is a **shared** anonymous mapping (`rw-s … /dev/zero (deleted)`), so a child created with `fork` sees the parent's writes to it.
- `[vdso]` is a small kernel-provided library that makes calls like `clock_gettime` run without entering the kernel (see [System Calls](27-System-Calls.md)).

---

## 3. Key Concepts

### The four kinds of mapping

| | Private (`MAP_PRIVATE`) | Shared (`MAP_SHARED`) |
|---|---|---|
| **File-backed** | Program code, shared libraries, `mmap` of a file you only read. Writes create private copies and never reach the file | Data files mapped read/write (SQLite with `mmap_size`, LMDB). Writes go to the page cache and later to the file, visible to every process mapping it |
| **Anonymous** | Heap (`brk` and large `malloc`), thread stacks, the V8 heap. Zero-filled on first touch | Memory shared between a parent and its `fork`ed children; POSIX shared memory under `/dev/shm` behaves similarly |

File-backed clean pages are the cheapest memory on the machine. The kernel can drop them under pressure and read them back from the file later. Anonymous pages can only go to swap, or be freed when the process frees them or dies.

### Shared libraries

The dynamic loader maps each `.so` file with `mmap`. Code and read-only data come from the page cache, so 40 Python workers and a sidecar all use the same physical pages of `libc.so.6`. Each process still gets a few **private dirty** pages per library, for its writable data and for relocations (the addresses the loader patches in at startup). In `smaps_rollup` these shared pages show up as `Shared_Clean`. They are counted fully in every process's RSS, which is why summing RSS across workers over-counts. [Memory Management](21-Memory-Management.md) shows how PSS splits them fairly.

### Copy-on-write and pre-fork servers

Pre-forking means loading the application once in a master process and then calling `fork()` for each worker. Gunicorn with `--preload`, uWSGI, PostgreSQL backends and Redis `BGSAVE` all use it. The promise is that everything the master built is shared. How long the sharing lasts depends on writes:

- **CPython reference counts.** Every object has an `ob_refcnt` field in its header. Reading an attribute, iterating a list or passing an object to a function changes it. Each change dirties the page and forces a copy. Python 3.12 made some objects **immortal** (`None`, `True`, `False`, small integers and other built-in singletons; PEP 683), so their counts never change. Your application's objects are not immortal.
- **The cycle collector.** A full `gc` collection writes into the header of every GC-tracked object (class instances, lists, dicts). That un-shares even objects your code never touches. The `gc` documentation's recipe is: call `gc.disable()` early in the parent, `gc.freeze()` right before `fork()`, and `gc.enable()` early in each child. Frozen objects sit in a permanent generation that collections skip.
- **Allocator activity.** New objects created in the child fill holes in pages it shares with the parent, which dirties those pages too.
- **Node.js** has no `fork()` in JavaScript. `cluster` and `child_process.fork` start fresh Node processes that share only the `node` binary and its libraries. Each worker builds its own V8 heap, so there is nothing to lose to copy-on-write, and nothing to gain from it either.

Shared pre-fork state has a second trap: **open connections**. A database pool or a Redis client created in the master is inherited by every worker as the same socket. Several processes then write to one TCP connection, and the protocol gets corrupted. Create connections after the fork (Gunicorn's `post_fork` hook, or lazily on first use).

### Memory-mapped files for read-only data

`mmap` a large, read-only file and every process gets an array-like view of it. Only touched pages are loaded, and all processes share the same page-cache copy. Good fits are IP-geolocation databases (MaxMind's `libmaxminddb` reads `.mmdb` files this way), sorted lookup tables, model weights, and search indexes. Things to know:

- **Page faults are blocking I/O you cannot see.** A cold page means a disk read in the middle of an innocent-looking array access. That blocks the thread: in Node it would be the event-loop thread, in Python the thread holding the GIL. Warm the file at startup, or accept the cost for rarely used pages.
- **`SIGBUS` on truncation.** If another process truncates the file while it is mapped, accessing pages beyond the new end raises `SIGBUS` and kills the process. To update the file, write a new one and `rename()` it over the old one, then map the new file and unmap the old. Never rewrite a mapped file in place.
- **RSS goes up, but it is clean and shared memory.** Mapped file pages count in `RssFile` and in the cgroup's file memory. The kernel can reclaim them, unlike heap memory.
- **Fault-around.** When a page is already in the page cache, the kernel may map a few neighbouring cached pages on the same fault. RSS therefore grows faster than the number of pages you actually touched.

### Limits on the address space

- `vm.max_map_count` (default 65530) caps the number of VMAs per process. Allocators with many arenas, many thread stacks, or many small `mmap`s can hit it, and `mmap` then fails with `ENOMEM`. Elasticsearch documents raising it for this reason.
- `RLIMIT_AS` (`ulimit -v`) caps **virtual** size, which breaks runtimes like Node that reserve large ranges they never touch. Limit memory with cgroups instead ([Memory Management](21-Memory-Management.md)).

---

## 4. Code Examples

Scenario: an API resolves IP addresses to countries using a 152 MiB sorted table of 20 million fixed-size records (8 bytes: a 4-byte range start and a 2-byte country code). Each of several workers needs it. Then a measurement of how much `fork`-shared memory a Python worker keeps.

### Shell

```bash
# Who maps the lookup file, and how much of it is resident in each process?
grep ip-ranges.bin /proc/[0-9]*/maps
awk '/ip-ranges.bin/{f=1} f&&/^Rss/{print; f=0}' /proc/<pid>/smaps

# Fair-share accounting across pre-forked workers (kB)
for p in $(pgrep -f 'gunicorn'); do
  printf '%s ' "$p"; grep -E '^(Pss|Private_Dirty):' /proc/$p/smaps_rollup | tr '\n' ' '; echo
done

# How many VMAs, against the limit
wc -l < /proc/<pid>/maps; cat /proc/sys/vm/max_map_count
```

### Node.js / TypeScript

Node core has no `mmap`. The closest built-in equivalent is a **positional read**: `FileHandle.read(buffer, offset, length, position)` maps to `pread(2)`. It reads exactly the bytes you ask for at an offset, without moving a shared file position. The file stays out of the heap, and repeated reads come from the page cache.

```ts
// No npm packages — Node.js 22+, TypeScript 5, Linux. Uses the file built by the Python example.
import { open, type FileHandle } from "node:fs/promises";
import { readSync } from "node:fs";

const REC = 8; // uint32 range start (big-endian), 2-byte country code, 2 pad bytes

class RangeTable {
  private readonly probe = Buffer.alloc(REC); // reused: one 8-byte read per probe

  private constructor(private readonly fh: FileHandle, private readonly n: number) {}

  static async open(path: string): Promise<RangeTable> {
    const fh = await open(path, "r");
    const { size } = await fh.stat();
    return new RangeTable(fh, Math.floor(size / REC));
  }

  // Async: each probe is a pread() on the libuv thread pool, so the event loop stays free,
  // but a lookup costs ~25 round trips through the pool.
  async country(ip: number): Promise<string | null> {
    let lo = 0, hi = this.n - 1, found: string | null = null;
    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      await this.fh.read(this.probe, 0, REC, mid * REC); // position => pread, no shared offset
      if (this.probe.readUInt32BE(0) <= ip) {
        found = this.probe.toString("latin1", 4, 6);
        lo = mid + 1;
      } else hi = mid - 1;
    }
    return found;
  }

  // Sync: ~25 pread() calls on the main thread. Microseconds when the pages are in the
  // page cache, but a cold disk read would block every request on this event loop.
  countrySync(ip: number): string | null {
    let lo = 0, hi = this.n - 1, found: string | null = null;
    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      readSync(this.fh.fd, this.probe, 0, REC, mid * REC);
      if (this.probe.readUInt32BE(0) <= ip) {
        found = this.probe.toString("latin1", 4, 6);
        lo = mid + 1;
      } else hi = mid - 1;
    }
    return found;
  }

  close(): Promise<void> { return this.fh.close(); }
}

const table = await RangeTable.open("/var/tmp/ip-ranges.bin");
const ips = Array.from({ length: 10_000 }, () => Math.floor(Math.random() * 4_000_000_000));
let t = performance.now();
for (const ip of ips) await table.country(ip);
console.log(`async: ${((performance.now() - t) * 1000 / ips.length).toFixed(1)} µs/lookup`);
t = performance.now();
for (const ip of ips) table.countrySync(ip);
console.log(`sync:  ${((performance.now() - t) * 1000 / ips.length).toFixed(1)} µs/lookup`);
console.log(`rss ${Math.round(process.memoryUsage.rss() / 2 ** 20)} MiB`); // the file is never in the heap
await table.close();
```

Measured on one laptop (Docker, warm page cache): async about 1,150 µs per lookup, sync about 15 µs, RSS 58 MiB. The async version pays for 25 thread-pool round trips. In practice you would read one larger block per lookup (for example a 64 KiB sparse index first), keep a small in-heap index of every 512th key, or accept the sync call when the file is known to be cached. If you truly need `mmap` in Node, it takes a native addon.

### Python

```python
# No pip packages — Python 3.12+, Linux. Run: python3 lookup.py
import mmap
import os
import random
import struct

REC = struct.Struct(">I2s2x")  # range start (IPv4 as uint32), country code, 2 pad bytes = 8 bytes
PATH = "/var/tmp/ip-ranges.bin"
N = 20_000_000                 # 160 MB file, sorted by range start


def build(path: str) -> None:
    with open(path, "wb") as f:  # buffered writes, 1M records per chunk
        for base in range(0, N, 1_000_000):
            f.write(b"".join(REC.pack(i * 200, b"DE" if i % 2 else b"US")
                             for i in range(base, base + 1_000_000)))


class RangeTable:
    """Binary search over a sorted file without reading it into the heap."""

    def __init__(self, path: str) -> None:
        with open(path, "rb") as f:  # the mapping keeps its own reference to the file
            self._mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        self._mm.madvise(mmap.MADV_RANDOM)  # probes jump around: skip readahead on cold reads
        self._n = len(self._mm) // REC.size

    def country(self, ip: int) -> str | None:
        lo, hi, found = 0, self._n - 1, None
        while lo <= hi:  # ~25 probes for 20M records; each touches one 4 KiB page
            mid = (lo + hi) // 2
            start, cc = REC.unpack_from(self._mm, mid * REC.size)  # no read() syscall
            if start <= ip:
                found, lo = cc.decode(), mid + 1
            else:
                hi = mid - 1
        return found


def rss_file_kib() -> int:
    with open("/proc/self/status") as f:
        return next(int(l.split()[1]) for l in f if l.startswith("RssFile:"))


if not os.path.exists(PATH):
    build(PATH)
table = RangeTable(PATH)
base = rss_file_kib()
for count in (1, 1_000):
    found = [table.country(random.randrange(N * 200)) for _ in range(count)]
    print(f"{count:>5} lookups: RssFile +{(rss_file_kib() - base) / 1024:.1f} MiB "
          f"of a {os.path.getsize(PATH) >> 20} MiB file, e.g. {found[0]}")
```

Output (measured, warm page cache):

```text
    1 lookups: RssFile +1.1 MiB of a 152 MiB file, e.g. US
 1000 lookups: RssFile +114.8 MiB of a 152 MiB file, e.g. DE
```

One lookup touches about 16 distinct pages, yet RSS grows by about 1 MiB. That is fault-around mapping cached neighbours. After 1,000 random lookups most of the file is mapped. That is fine: these are clean, shared, reclaimable page-cache pages, and ten workers mapping the same file share one copy. A lookup took about 8 µs in the same test, with no system call per probe.

Copy-on-write after `fork`, measured with `smaps_rollup`:

```python
# No pip packages — Python 3.12+, Linux only (os.fork, /proc). Run: python3 cow.py [--freeze]
import gc
import os
import sys


def mem() -> str:
    # smaps_rollup sums all mappings; Pss divides each shared page by the number of sharers.
    fields = {}
    with open("/proc/self/smaps_rollup") as f:
        for line in f:
            key, _, rest = line.partition(":")
            if key in ("Rss", "Pss", "Shared_Dirty", "Private_Dirty"):
                fields[key] = int(rest.split()[0]) // 1024  # kB -> MiB
    return "  ".join(f"{k}={v:>3} MiB" for k, v in fields.items())


class Product:
    __slots__ = ("sku", "name")  # instances of user classes are always tracked by the GC

    def __init__(self, sku: int, name: str) -> None:
        self.sku, self.name = sku, name


FREEZE = "--freeze" in sys.argv
if FREEZE:
    gc.disable()  # per the gc docs: no collections in the parent, so no freed "holes" in shared pages

# Stands in for what `gunicorn --preload` builds once in the master: models, lookup tables.
catalog = [Product(i, f"product-{i:08d}") for i in range(1_000_000)]
if FREEZE:
    gc.freeze()  # move every tracked object to a permanent generation the collector skips

print(f"parent before fork : {mem()}", flush=True)
pid = os.fork()
if pid == 0:
    print(f"child after fork   : {mem()}", flush=True)
    if FREEZE:
        gc.enable()
    gc.collect()  # a full collection writes into every tracked object's GC header
    print(f"child after gc     : {mem()}", flush=True)
    total = sum(len(p.name) for p in catalog)  # "read-only" loop still writes refcounts
    print(f"child after reading: {mem()}", flush=True)
    os._exit(0)  # skip interpreter teardown, which would touch every object again
os.waitpid(pid, 0)
```

Output (measured, Python 3.12):

```text
$ python3 cow.py
parent before fork : Rss=154 MiB  Pss=153 MiB  Shared_Dirty=  0 MiB  Private_Dirty=148 MiB
child after fork   : Rss=151 MiB  Pss= 75 MiB  Shared_Dirty=148 MiB  Private_Dirty=  0 MiB
child after gc     : Rss=151 MiB  Pss= 99 MiB  Shared_Dirty=101 MiB  Private_Dirty= 46 MiB
child after reading: Rss=151 MiB  Pss=129 MiB  Shared_Dirty= 40 MiB  Private_Dirty=108 MiB

$ python3 cow.py --freeze
child after fork   : Rss=151 MiB  Pss= 75 MiB  Shared_Dirty=148 MiB  Private_Dirty=  0 MiB
child after gc     : Rss=151 MiB  Pss= 76 MiB  Shared_Dirty=148 MiB  Private_Dirty=  0 MiB
child after reading: Rss=151 MiB  Pss=129 MiB  Shared_Dirty= 41 MiB  Private_Dirty=107 MiB
```

RSS hardly moves in the child (151 MiB throughout), which is exactly why RSS is the wrong metric here. Right after `fork`, PSS is half of RSS because two processes share everything. One `gc.collect()` copies 46 MiB unless the objects were frozen. Iterating the catalog copies about 108 MiB either way, because every access writes a refcount. With 8 workers, that is the difference between about 150 MiB and about 1 GiB in total.

**Runtime difference to notice:** Python can share a preloaded heap across processes, but keeping it shared means fighting refcounts. Freezing helps with the collector, while refcount writes need the data to live outside Python objects: in an `mmap`ed file, a NumPy array or a `bytes` blob that is read without creating per-item objects. Node cannot share a JS heap between processes at all. Within one process, `worker_threads` share memory only through `SharedArrayBuffer`. Across processes, Node shares data through files and the page cache, which the positional-read version above uses.

---

## 5. Production Concerns

- **Size pre-fork servers with PSS and growth, not RSS.** Measure `Pss` and `Private_Dirty` per worker after a realistic warm-up. Sharing erodes over the first minutes or hours as requests touch objects. Gunicorn's `--max-requests` recycling resets it, at the cost of warm caches.
- **Create sockets after `fork`.** DB pools, Redis clients, gRPC channels and background threads created in the master are inherited by every worker. Sockets get shared, and threads are not copied at all. Use `post_fork` hooks or lazy initialization. Python 3.12 warns when `os.fork()` is called with other threads running.
- **Treat mapped files as immutable.** Replace them with write-to-temp, `fsync`, `rename`, then remap. A truncate or in-place rewrite of a mapped file can raise `SIGBUS` in every reader, and an in-place rewrite also lets readers see half-written data.
- **Mapped-file page faults block.** In an async server, a cold page in an `mmap`ed file stalls the whole event loop for the duration of a disk read. Warm critical files at startup (read them once, or `madvise(MADV_WILLNEED)`), or keep such lookups in a thread pool.
- **cgroups count file pages too.** Mapped file pages are page-cache pages, charged to the cgroup that first brought them into the cache and shown as `file` in `memory.stat`. They are reclaimable, so they rarely cause OOM kills. They do inflate `memory.current` and confuse dashboards.
- **Watch the VMA count** for processes that `mmap` a lot (many threads, jemalloc, many mapped files). Hitting `vm.max_map_count` makes allocations fail with `ENOMEM` even with plenty of free RAM.

---

## 6. Common Mistakes

- **Summing RSS across pre-forked workers** — shared libraries and preloaded data are counted once per worker and capacity is over-estimated several times — sum PSS from `smaps_rollup` or read the cgroup's usage.
- **Expecting `--preload` to keep memory shared forever** — refcount and GC writes copy pages within minutes — measure `Private_Dirty` over time, use the `gc.freeze()` recipe, and keep big read-only data out of Python objects.
- **Opening DB connections before `fork`** — workers share one socket and corrupt each other's protocol state — open connections in each worker after the fork.
- **Rewriting a file that other processes have mapped** — readers crash with `SIGBUS` or see torn data — write a new file, `rename()` it into place, then remap.
- **`mmap`ing on the event-loop thread and assuming it is "just memory"** — cold pages become synchronous disk reads that stall every request — warm the file, or do lookups off the loop.
- **Setting `ulimit -v` to limit memory** — Node and other runtimes fail at startup because they reserve address space they never use — use cgroup `memory.max`.
- **Treating "segmentation fault" as running out of memory** — it means an access outside any mapping or against the protection bits — get a core dump or a `faulthandler` trace, not more RAM.

---

## 7. Comparison Table

Ways to give many workers access to a large read-only dataset:

| | Load into each worker's heap | Preload, then `fork` (CoW) | `mmap` the file | Positional reads (`pread`) | External store (Redis) |
|---|---|---|---|---|---|
| Memory for N workers | N copies | 1 copy that erodes toward N in CPython | 1 page-cache copy | 1 page-cache copy | Outside the app |
| Cost per access | Object access | Object access, plus copying a page on first write | Memory access; a page fault on first touch | One system call | A network round trip |
| Startup | Parse everything | Parse once | Instant | Instant | Instant |
| Update data | Restart or reload | Restart workers | `rename` + remap | Reopen the file | Write to the store |
| Available in | Both | Python (`os.fork`, Gunicorn); not Node | Python stdlib; Node needs an addon | Both | Both |
| Failure modes | OOM with many workers | Silent memory growth | `SIGBUS` on truncate; blocking faults | Thread-pool saturation if async | Network errors, latency |

---

## 8. Interview Questions

**[Junior] What is virtual memory, and why do processes not see each other's memory?**
Each process gets its own range of virtual addresses, and the MMU translates them through that process's own page tables. Two processes can use the same virtual address and reach different physical frames. A process cannot even form an address that maps into another process's private memory. The kernel switches page tables on every switch between processes, and pages marked kernel-only are blocked for user code.

**[Mid] Explain copy-on-write after `fork()`.**
`fork` copies the parent's VMAs and page tables, and marks private writable pages read-only in both processes. Both processes read the same physical pages. When either one writes, the CPU faults, the kernel copies just that page for the writer and makes it writable, then the write is retried. This makes `fork` fast and lets pre-fork servers share preloaded data. But every page that is later written gets duplicated.

**[Mid] Why does memory sharing erode in Gunicorn workers with `--preload`, and what can you do?**
CPython stores a reference count in every object header and changes it whenever the object is used, so even reading data writes to its page and triggers a copy. The cycle collector also writes to the headers of tracked objects during a full collection. `gc.disable()` early, `gc.freeze()` before forking and `gc.enable()` in each child stop the collector part. For refcounts, keep large data in forms that don't create per-item Python objects (an `mmap`ed file, a `bytes` blob, a NumPy array). Then measure `Private_Dirty` over time, and recycle workers if needed.

**[Mid] When would you memory-map a file instead of reading it?**
When the file is large, read mostly at random, read-only, and shared by several processes. Lookup tables, indexes and models are typical. Only touched pages load, every process shares the page-cache copy, and there is no system call per access. Avoid it when data changes in place, when you need async I/O on an event loop (page faults block), or for simple sequential processing, where streaming `read` calls are just as fast and simpler.

**[Senior] A pod running 8 Gunicorn workers is OOM-killed hours after deploy, but memory looked fine at startup. Walk through the investigation.**
At startup, workers share the preloaded heap, so PSS per worker is small. Over time refcount and GC writes copy those pages, and each worker drifts toward a full private copy. I would graph `Pss` and `Private_Dirty` per worker from `smaps_rollup` against uptime and compare them with the cgroup's `anon` usage. If private memory grows to roughly the preload size and then stops, it is copy-on-write erosion, not a leak. Fixes: the `gc.freeze()` recipe, moving big tables to `mmap`ed files or an external store, fewer workers with more threads, and `--max-requests` recycling. Size the pod for the eroded state, not the fresh one.

**[Senior] How would you serve a 5 GB read-only lookup dataset to a Node cluster and a Python worker fleet on the same host?**
Put it in a file with a format you can binary-search or index without parsing it all, so every process shares one page-cache copy. Python workers `mmap` it. Node workers use positional reads with a small in-heap sparse index, so each lookup costs one or two `pread` calls, or use a native mmap addon if the read rate justifies it. Updates go through write-new-file and atomic `rename`, with each process reopening or remapping on a signal or a version check. Warm the file at startup, and make sure the cgroup memory limit allows for the page cache it will use.

**[Senior] What causes `SIGBUS` instead of `SIGSEGV`, and why does it matter for `mmap`?**
`SIGSEGV` means the address is not mapped or the access breaks the page's protection. `SIGBUS` means the address is mapped but the backing store cannot supply the page. The classic case is accessing a page of a mapped file beyond its current end, after another process truncated it. The kernel cannot deliver data that doesn't exist, so the process is killed. It matters because a deploy script that rewrites a shared data file in place can crash every worker at once. Replace files atomically and remap them instead.

---

## 9. Cheat Sheet

```text
Address space   private per process; x86-64 user space = lower 128 TiB (47-bit)
Translation     VMAs (kernel's list) + page tables (CR3) + TLB → ch 25 for details
Protection      present · writable · user · NX per page; violation → SIGSEGV; ASLR randomize_va_space=2
mmap kinds      file/anon × private(CoW)/shared; code+libs = file private; heap/stacks = anon private
Shared libs     one page-cache copy for all processes; Shared_Clean; summed RSS over-counts
fork()          copies page tables; pages CoW; write → fault → copy 4 KiB
CPython CoW     refcount writes + GC header writes un-share pages; PEP 683 immortals exempt
gc recipe       gc.disable() early → gc.freeze() before fork → gc.enable() in child
Node            no fork in JS; cluster = fresh processes; no core mmap → FileHandle.read(pos) = pread
mmap'd files    shared page cache, lazy load, no syscall per access; SIGBUS on truncate; faults block
Update files    write temp → fsync → rename → remap (never rewrite in place)
Observe         /proc/PID/maps (perms r-xp / rw-s) · smaps_rollup Rss/Pss/Private_Dirty · pmap -x
Limits          vm.max_map_count 65530 · don't use ulimit -v · cgroup memory.max instead
```

---

## Related Topics

- [Paging](25-Paging.md) — page tables, the TLB, page faults and swap that implement virtual memory
- [Memory Management](21-Memory-Management.md) — RSS vs PSS, overcommit and OOM kills in containers
- [Processes](02-Processes.md) — `fork`, `exec` and what a child inherits
- [Heap Memory](22-Heap-Memory.md) — V8 and CPython heaps living in anonymous mappings
- [Inter Process Communication](28-Inter-Process-Communication.md) — shared memory and `/dev/shm` between processes
- [File Systems Basics](30-File-Systems-Basics.md) — the page cache behind file-backed mappings

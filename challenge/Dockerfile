# ─────────────────────────────────────────────────────────────────────────────
# fmt-got  – Format String + GOT-overwrite CTF challenge
# ─────────────────────────────────────────────────────────────────────────────
#
# Binary security profile:
#   Partial RELRO   – GOT table is writable at runtime
#   No PIE          – binary base address is fixed (0x400000)
#   No stack canary – simplifies exploitation (not the focus of this challenge)
#   NX enabled      – shellcode on the stack is not executable
#
# Exploitation path:
#   1. Read the system() leak printed by the binary on startup.
#   2. Use the format-string vulnerability (printf(buf)) to overwrite the
#      printf() GOT entry with the leaked system() address.
#   3. Send "/bin/sh" → printf("/bin/sh") now calls system("/bin/sh").
#   4. In the resulting shell, execute ./flag to print the flag.
# ─────────────────────────────────────────────────────────────────────────────

FROM ubuntu:22.04

# ── system packages ──────────────────────────────────────────────────────────
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        socat \
        && rm -rf /var/lib/apt/lists/*

# ── create an unprivileged user that the challenge runs as ───────────────────
RUN useradd -m -s /bin/sh ctf

# ── build directory ──────────────────────────────────────────────────────────
WORKDIR /challenge
COPY chall.c flag.c ./

# ── compile the vulnerable challenge binary ───────────────────────────────────
#
#   -no-pie            → fixed base address (simplifies GOT address lookup)
#   -Wl,-z,relro       → Partial RELRO (BIND_NOW *not* set → GOT still writable)
#   -fno-stack-protector → no stack canary (challenge focus is fmt-str / GOT)
#
RUN gcc -o chall chall.c \
        -no-pie \
        -Wl,-z,relro \
        -fno-stack-protector \
    && chown root:ctf chall \
    && chmod 755 chall

# ── compile the flag-printer binary ──────────────────────────────────────────
#
#   Owned by root, SUID bit set → executes as root regardless of caller.
#   This lets it open /flag.txt (mode 0400, owned by root) even when run
#   by the unprivileged ctf user from within the spawned shell.
#
RUN gcc -o flag flag.c \
    && chown root:root flag \
    && chmod 4755 flag

# ── plant the flag (only root can read it directly) ──────────────────────────
RUN echo 'CTF{f0rm4t_str1ng_g0t_wr1t3_4nd_sh3ll_3sc4p3}' > /flag.txt \
    && chown root:root /flag.txt \
    && chmod 400 /flag.txt

# ── drop to unprivileged user ────────────────────────────────────────────────
USER ctf

# ── expose the challenge port ────────────────────────────────────────────────
EXPOSE 3012

# ── serve one connection at a time via socat ─────────────────────────────────
CMD ["socat", \
     "-T", "120", \
     "TCP-LISTEN:3012,reuseaddr,fork", \
     "EXEC:/challenge/chall,stderr"]

FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        socat \
        && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/sh ctf

WORKDIR /challenge
COPY chall.c flag.c ./

# ── compile the vulnerable challenge binary ───────────────────────────────────
#
#   -no-pie            → fixed base address (simplifies GOT address lookup)
#   -Wl,-z,relro       → Partial RELRO (BIND_NOW *not* set → GOT still writable)
#   -fno-stack-protector → no stack canary (challenge focus is fmt-str / GOT)
#
RUN gcc -g -O0 -o chall chall.c \
        -no-pie \
        -Wl,-z,relro \
        -fno-stack-protector \
    && chown root:ctf chall \
    && chmod 755 chall

RUN gcc -o flag flag.c \
    && chown root:root flag \
    && chmod 111 flag
# ── copy libc dan ld untuk player ────────────────────────────────────────────
RUN cp /lib/x86_64-linux-gnu/libc.so.6 /challenge/libc.so.6 \
    && cp /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /challenge/ld-2.35.so \
    && chmod 644 /challenge/libc.so.6 /challenge/ld-2.35.so

# ── hapus source code setelah compile ────────────────────────────────────────
RUN rm -f /challenge/chall.c /challenge/flag.c
# ── drop to unprivileged user ────────────────────────────────────────────────
USER ctf

EXPOSE 3012

CMD ["socat", \
     "-T", "120", \
     "TCP-LISTEN:3012,reuseaddr,fork", \
     "EXEC:/challenge/chall,stderr"]
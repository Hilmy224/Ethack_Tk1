# Ethack_Tk1

## easy-fmt-got (versi disederhanakan)

Challenge ini dibuat lebih mudah untuk latihan dasar:
1. `chall` punya format-string bug (`printf(buf)`) untuk overwrite `printf@GOT` ke `win()`.
2. `win()` langsung menjalankan `/bin/sh`.
3. Di shell, jalankan `./flag`, lalu kirim `%s` (atau `%1$s`) untuk leak flag yang disimpan sebagai variabel global.

## Struktur folder

```text
challenge/
├── Dockerfile
├── chall.c
├── flag.c
└── solve.py
```

## Opsi 1: Setup lokal pakai Docker (disarankan)

```bash
cd challenge
docker build -t easy-fmt-got .
docker run --rm -p 3012:3012 easy-fmt-got
```

Service challenge akan listen di `localhost:3012`.

## Opsi 2: Setup lokal tanpa Docker (Linux/WSL)

> Untuk Windows native, gunakan WSL agar `gcc/chmod/chown` dan permission Unix bekerja normal.

```bash
cd challenge

# compile chall (sesuai proteksi challenge)
gcc -o chall chall.c -no-pie -Wl,-z,relro -fno-stack-protector

# compile flag helper
gcc -o flag flag.c
```

### Manajemen permission yang direkomendasikan

Jalankan sebagai root (atau pakai `sudo`):

```bash
cd challenge
chown root:ctf chall
chmod 755 chall

chown root:root flag
chmod 111 flag
```

Arti permission:
1. `chall` dengan `755`: bisa dieksekusi user biasa.
2. `flag` dengan `111`: execute-only (tidak ada read bit), jadi tidak bisa dibuka/di-cat oleh user biasa.

Verifikasi:

```bash
ls -l chall flag
```

Output minimal yang diharapkan:
1. `chall` terlihat seperti `-rwxr-xr-x`
2. `flag` terlihat seperti `---x--x--x`

## Cara menjalankan solver

Install dependency:

```bash
pip install pwntools
```

Jalankan solver terhadap service Docker (localhost:3012):

```bash
python3 challenge/solve.py
```

Atau local process langsung:

```bash
python3 challenge/solve.py LOCAL
python3 challenge/solve.py LOCAL DEBUG
```

## Alur solve singkat

1. Solver overwrite `printf@GOT` ke `win()`.
2. Kirim input trigger untuk mengeksekusi `win()` dan mendapatkan shell.
3. Jalankan `./flag`.
4. Kirim `%1$s` untuk mencetak string flag dari argumen pertama `printf`.

## Troubleshooting permission

1. Jika `./flag: Permission denied`, cek lagi `chmod 111 flag`.
2. Jika `chown` gagal, jalankan dengan `sudo` atau root.
3. Jika setup di Windows CMD/PowerShell native, pindah ke WSL atau Docker agar semantics permission Unix tidak bermasalah.

# Ethack_Tk2


## Struktur folder

```text
challenge/
├── Dockerfile (Untuk run remote instance)
├── chall.c (diberikan)
├── flag.c (dalam soal tidak diberikan)
└── solve.py
```
## Struktur Pada remote instance 
```text
challenge/
├── chall (diberikan)
├── flag 
```
## setup lokal pakai Docker (disarankan)

```bash
cd challenge
docker build -t easy-fmt-got .
docker run --rm -p 3012:3012 easy-fmt-got
```

Service challenge akan listen di `localhost:3012`.



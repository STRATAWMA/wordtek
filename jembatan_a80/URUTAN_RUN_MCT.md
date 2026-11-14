# A80 — urutan menjalankan MCT yang sudah dipecah

File induk `A80_PELENGKUNG_FEM.mct` (302 KB, 6.796 baris) dipecah menjadi 8 bagian.
Jalankan **berurutan** lewat **Tools → MCT Command Shell**, satu per satu,
tunggu tiap bagian selesai tanpa error sebelum lanjut.

| # | File | Isi | Baris |
|---|------|-----|-------|
| 1 | `A80_P1_PROPERTI.mct` | STRUCTYPE, MATERIAL, SECTION, THICKNESS, DGN-MATL, DGN-STEEL | 78 |
| 2 | `A80_P2_SIMPUL.mct` | NODE — 2.621 simpul | 2.643 |
| 3 | `A80_P3_ELEMEN_FRAME.mct` | ELEMENT — 1.206 batang (BEAM + 30 TRUSS) | 1.225 |
| 4 | `A80_P4_ELEMEN_PLAT.mct` | ELEMENT — 1.624 pelat | 1.646 |
| 5 | `A80_P5_TUMPUAN.mct` | CONSTRAINT 4 titik + RIGIDLINK 911 pasang | 941 |
| 6 | `A80_P6_LOADCASE.mct` | STLDCASE — 13 kasus beban (nama saja) | 31 |
| 7A | `A80_P7A_BEBAN_MATI.mct` | MS, MA | 83 |
| 7B | `A80_P7B_BEBAN_LALULINTAS.mct` | TD-BTR, TD-BGT, TP, TB1 | 90 |
| 7C | `A80_P7C_BEBAN_ANGIN.mct` | EWS, EWL, EWV | 32 |
| 7D | `A80_P7D_BEBAN_SUHU.mct` | EUN, EUN-N | 29 |
| 7E | `A80_P7E_BEBAN_GEMPA.mct` | EQX, EQY | 363 |
| 8 | `A80_P8_KOMBINASI.mct` | LOADCOMB — 11 kombinasi | 43 |

## Aturan yang tidak boleh dilanggar

**Urutan tidak boleh ditukar.** P1 harus lebih dulu dari P3/P4 karena elemen
memanggil nomor penampang; P2 harus lebih dulu dari P3/P4 karena elemen memanggil
nomor simpul; P5 harus setelah P2; P6 harus sebelum semua P7.

**P7A–P7E hanya boleh dijalankan SATU KALI masing-masing.** midas menimpa
simpul/elemen/penampang berdasarkan nomor, tetapi **data beban selalu ditambahkan**.
Kalau ragu sudah pernah jalan: hapus 13 kasus beban di **Load → Static Load Cases**,
lalu jalankan P6 dan seluruh P7 lagi dari awal.

P1–P5 aman diulang (menimpa, bukan menambah).

## Catatan perbaikan (revisi 2)

Beban dipecah per kelompok supaya kalau ada error bisa langsung ditunjuk
kelompok mana. Dua hal diubah tanpa mengubah nilai beban:

- **DESC pada P6 dibuat polos** — tanpa koma, `=`, `(`, `)`, `+`. Karakter `=`
  adalah token penugasan di MCT (`NAME=`, `CODE=`), dan koma dibaca sebagai
  pemisah kolom.
- **Baris panjang dipotong** — daftar simpul dibatasi 12 nomor per baris.
  Sebelumnya ada baris 1.328 karakter; sekarang terpanjang 164 karakter.

Verifikasi: total beban dan jumlah simpul per kasus beban **identik** dengan
file induk (14 kombinasi load case x blok dibandingkan satu per satu).

## Satuan

P1–P5 memakai `TONF, MM`. P6–P8 memakai `KN, M`. Tiap file sudah membawa blok
`*UNIT` sendiri, jadi tidak ada yang perlu diatur manual di GUI.

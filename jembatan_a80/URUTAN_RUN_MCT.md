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
| 6 | `A80_P6_LOADCASE.mct` | STLDCASE — 13 kasus beban (nama saja) | 37 |
| 7 | `A80_P7_BEBAN.mct` | Data beban: SELFWEIGHT, CONLOAD, BEAMLOAD, ELTEMPER | 293 |
| 8 | `A80_P8_KOMBINASI.mct` | LOADCOMB — 11 kombinasi | 43 |

## Aturan yang tidak boleh dilanggar

**Urutan tidak boleh ditukar.** P1 harus lebih dulu dari P3/P4 karena elemen
memanggil nomor penampang; P2 harus lebih dulu dari P3/P4 karena elemen memanggil
nomor simpul; P5 harus setelah P2.

**P7 hanya boleh dijalankan SATU KALI.** midas menimpa simpul/elemen/penampang
berdasarkan nomor, tetapi **data beban selalu ditambahkan**. Menjalankan P7 dua kali
membuat semua beban dobel. Kalau ragu sudah pernah jalan: hapus 13 kasus beban di
**Load → Static Load Cases**, lalu jalankan P6 dan P7 lagi.

P1–P5 aman diulang (menimpa, bukan menambah).

## Satuan

P1–P5 memakai `TONF, MM`. P6–P8 memakai `KN, M`. Tiap file sudah membawa blok
`*UNIT` sendiri, jadi tidak ada yang perlu diatur manual di GUI.

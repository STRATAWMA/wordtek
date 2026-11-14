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

## Catatan perbaikan (revisi 3)

Dua koreksi pada model, keduanya **tidak mengubah profil** — justru membuat model
sesuai gambar approval:

### 1. Segmen chord ujung salah penampang

MATERIAL LIST gambar GA-ITK09-10 menyebut:

| Mark | Nama | Qty | Dimensi |
|---|---|---|---|
| A80-T1 | TOP CHORD | 4 | **WB400*500*20*30** |
| A80-T2..T7 | TOP CHORD | 4 ea | WB400*350*20*30 |
| A80-M1 | MIDDLE CHORD | 4 | **WB400*500*20*30** |
| A80-M2..M7 | MIDDLE CHORD | 4 ea | WB400*350*20*30 |

Delapan segmen chord di ujung pelengkung memakai 400x500, dan model lama memberi
semuanya 400x350. Penampang ARCH-END sudah ada di daftar tetapi tidak pernah
terpasang karena salah indeks panel. Sekarang terpasang di elemen 61, 62, 87, 88,
189, 190, 215, 216 — tepat 4 top chord + 4 middle chord.

### 2. Pelat lantai dibuat ortotropik

Ini jembatan **pelengkung bertarik**: balok tarik memang harus bisa memanjang untuk
menahan gaya dorong pelengkung. Pada model lama pelat lantai diikat kaku ke balok
tarik (130 rigid link DOF 111111, lengan 381 mm, tiap 1,25 m sepanjang 80 m) dengan
kekakuan beton penuh ke segala arah. Pelat jadi melawan pemanjangan balok tarik dan
menyuntikkan kopel momen ke dalamnya.

Pelat sekarang ortotropik: arah memanjang 8% (retak), arah melintang dan vertikal
tetap penuh sehingga sebaran beban lantai tidak berubah. Cara yang sama sudah
terbukti jalan di B100.

### Batas yang perlu diketahui

Dua perbaikan ini tidak menyelesaikan elemen 1091 (PIPE6, COM 1.612). Batang itu
dikuasai kombinasi gempa EKSTREM I-EQY, dan beban gempanya memakai **asumsi
periode T = 1,20 detik** yang belum pernah diverifikasi. Gaya gempa berbanding
terbalik dengan T, jadi angkanya bisa berubah besar. Jalankan eigenvalue analysis
untuk mendapat T yang sebenarnya.

Pipa bracing TIDAK boleh diubah jadi TRUSS: 43 titik silang X-bracing akan jadi
mekanisme karena keempat batang di titik itu sebidang.

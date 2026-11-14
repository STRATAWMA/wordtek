# A80 — urutan menjalankan MCT (revisi 4)

## JALANKAN DI MODEL KOSONG

**File > New Project**, lalu jalankan berurutan lewat **Tools > MCT Command Shell**:

| # | File | Isi |
|---|------|-----|
| 1 | `A80_P1_PROPERTI.mct` | STRUCTYPE, MATERIAL, SECTION, THICKNESS, DGN-MATL, DGN-STEEL |
| 2 | `A80_P2_SIMPUL.mct` | NODE — 2.578 simpul |
| 3 | `A80_P3_ELEMEN_FRAME.mct` | ELEMENT — 1.120 batang (974 BEAM + 146 TRUSS) |
| 4 | `A80_P4_ELEMEN_PLAT.mct` | ELEMENT — 1.624 pelat |
| 5 | `A80_P5_TUMPUAN.mct` | CONSTRAINT 4 titik + RIGIDLINK 915 pasang |
| 6 | `A80_P6_LOADCASE.mct` | STLDCASE — 13 kasus beban |
| 7A | `A80_P7A_BEBAN_MATI.mct` | MS, MA |
| 7B | `A80_P7B_BEBAN_LALULINTAS.mct` | TD-BTR, TD-BGT, TP, TB1 |
| 7C | `A80_P7C_BEBAN_ANGIN.mct` | EWS, EWL, EWV |
| 7D | `A80_P7D_BEBAN_SUHU.mct` | EUN, EUN-N |
| 7E | `A80_P7E_BEBAN_GEMPA.mct` | EQX, EQY |
| 8 | `A80_P8_KOMBINASI.mct` | LOADCOMB — 11 kombinasi |

## Kenapa harus model kosong

Revisi ini **mengurangi** jumlah batang dan simpul:

| | revisi 3 | revisi 4 |
|---|---|---|
| batang | 1.206 | **1.120** |
| simpul | 2.621 | **2.578** |
| pelat | 1.624 | 1.624 |
| rigid link | 911 | 915 |

midas menimpa berdasarkan nomor, tetapi **tidak menghapus nomor yang tidak lagi
dipakai**. Dijalankan di atas model revisi 3, akan tertinggal:

- **batang 1121–1206** — 86 pipa bracing lama, jadi bracingnya **dobel**
- **simpul 2579–2621** — 43 simpul perpotongan lama, jadi simpul yatim

Pelat (5000–6623) dan rigid link tertimpa seluruhnya, tidak ada sisa.

Kalau tetap mau memakai file lama: hapus dulu **batang 1121–1206** dan
**simpul 2579–2621**, lalu jalankan P1–P5.

**P6 dan P7A–P7E hanya SEKALI.** Data beban selalu *ditambahkan* midas, tidak
menggantikan. Kalau perlu diulang, hapus 13 kasus beban di
**Load > Static Load Cases** lalu jalankan P6 dan seluruh P7 dari awal.

## Setelan GUI setelah model masuk

**Design > Steel Design Parameter > Effective Length Factor**

- batang **PIPE6** = **elemen 1003 sampai 1118** (116 batang, satu rentang
  utuh): **Ky = Kz = 0,5**. Pada bracing silang yang disambung di perpotongan,
  diagonal tarik menahan titik silang, jadi panjang tekuk efektif setengah
  panjang batang (AISC/AASHTO).

  WAJIB, bukan opsional. Tanpa ini: KL/r = 213 > 120 (batas AASHTO 6.9.3) dan
  Pu/phiPn = 1,90. Dengan K = 0,5: KL/r = 107 dan Pu/phiPn = 0,548.

  **K TIDAK BISA dikirim lewat MCT.** midas tidak menulis faktor panjang
  efektif ke file MCT - sudah diperiksa pada dua hasil ekspor midas sendiri
  (B100_FE_v5 dan PLENGKUNG_A80_v8): tidak ada bloknya sama sekali. Buktinya
  juga terlihat langsung: Kz = 0,85 yang pernah diset hilang dan kembali 1,0
  begitu model dibangun ulang dari MCT. Jadi langkah ini harus lewat GUI
  setiap kali model dibangun ulang.
- batang **ARCH / ARCH-END** (chord pelengkung): **K = 0,75**, AASHTO LRFD
  4.6.2.5 untuk sambungan baut/las di kedua ujung.

## Perubahan pada revisi 4

1. **Bracing PIPE6 jadi TRUSS, batang utuh tidak dipotong di perpotongan.**
   Sambungannya pelat buhul berbaut: memikul gaya aksial, bukan momen.
   Dimodelkan BEAM, batang ikut memikul rotasi simpul chord dan timbul momen
   semu — 7,93 kNm pada elemen 1091, lalu diperbesar B1 = 2,53 jadi 30,9 kNm,
   memakan 74% kapasitas lentur pipa.
   Diagonal tidak dipotong karena simpul perpotongan hanya dipegang 4 batang
   sebidang; kalau batangnya TRUSS simpul itu jadi mekanisme (diperiksa:
   determinan arah = 0 di 43 simpul).
2. **Pelat lantai dikembalikan isotropik.** Pada revisi 3 saya buat ortotropik
   dengan alasan pelat melawan pemanjangan balok tarik. Hasil run menyanggah
   itu: momen elemen 2 justru NAIK 4425 -> 5266 kNm dan rasionya memburuk
   1,236 -> 1,330. Pelat ternyata ikut memikul lentur global; melemahkannya
   membuat balok tarik memikul sendirian. Perubahan itu dibatalkan.
3. **Empat simpul bracing di dalam boks diikat ke pelat boks** (jarak 200 mm),
   supaya tidak menggantung setelah bracing jadi TRUSS.

Penampang chord ujung (ARCH-END WB400x500x20x30, 8 elemen sesuai A80-T1 dan
A80-M1 di MATERIAL LIST) dari revisi 3 tetap dipertahankan.

## Verifikasi

- 0 zona satuan salah, 0 simpul yatim, 0 slave rigid link ganda, 0 pelat luas
  nol, 0 non-ASCII, 0 kolom beban salah
- **0 simpul mekanisme** — setiap simpul yang hanya dipegang batang aksial
  sudah diperiksa determinan arahnya
- total beban dan jumlah simpul per kasus beban **identik** dengan file induk
- 0 baris data struktur hilang saat dipecah

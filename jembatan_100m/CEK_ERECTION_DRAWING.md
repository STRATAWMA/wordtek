# Pemeriksaan model terhadap ERECTION DRAWING B100 (GA, 9 lembar, rev A, Jan 2024)

Sumber: `ERECTON_DRAWING_B100.pdf` - PT. Indo Trans Konstruksi.
Seluruh 9 halaman dibaca (teks vektor diekstrak penuh, lembar detail dirender 400 dpi).

## 1. Yang COCOK dengan model

| Butir | Gambar | Model | |
|---|---|---|---|
| Bentang c/c | 100.000 mm | 99.997,5 mm | ok |
| Jarak titik buhul | 15 x 6666,5 mm | 15 x 6666,5 mm | ok |
| Lebar jalan bersih | 6000 mm | 6000 mm | ok |
| Trotoar | 2 x 500 mm | 2 x 500 mm | ok |
| Camber | 250 / 464 / 643 / 786 / 893 / 965 / 1000 | sama persis | ok |
| Perletakan | FIX + GUIDE (satu kepala), GUIDE + MULTI (kepala lain) | 111000 / 101000 / 011000 / 001000 | ok |
| Lantai beton | "BACK WALL HARUS DI COR BERSAMAAN DENGAN LANTAI DECK BETON" | cor di tempat -> komposit wajar | ok |

## 2. Yang BERBEDA - perlu keputusan

| Butir | Gambar | Model | Selisih |
|---|---|---|---|
| Lebar as-ke-as rangka | **7800 mm** (400+500+6000+500+400) | 7600 mm | +2,6% berat lantai |
| Kelas jembatan | judul: **KELAS B** | brief: Kelas A | geometri 6 m = Kelas B |

Beban lajur SNI 1725-2016 tidak berbeda menurut kelas jembatan, jadi BTR/BGT tetap.
Yang terpengaruh hanya berat sendiri lantai (+2,6%) bila lebar 7800 dipakai.

## 3. Plat buhul - data yang BELUM ada

Gambar memberi:
- 52 tanda plat sayap  B100-SF1 .. B100-SF52
- 27 tanda plat badan  B100-SW1 .. B100-SW27
- 82 anotasi grup baut, 44 kombinasi, dari 4*M24-70 sampai 84*M24-120

Gambar TIDAK memberi:
- ukuran (outline) tiap plat
- TEBAL tiap plat
- jarak dan pola baut berdimensi

Tanpa tebal dan outline, model shell plat buhul tidak bermakna.
Yang diperlukan: gambar fabrikasi / shop drawing, atau daftar plat (plate schedule).

## 4. Jenis sambungan

Dari DETAIL I + SEC 5-5: ini BUKAN plat buhul klasik. Badan batang diperpanjang
dan dibentuk, lalu batang lain disambung dengan plat sambung:
  SF = plat sambung sayap (flange splice), SW = plat sambung badan (web splice).
Model shell-nya harus mengikuti bentuk badan batang yang diperpanjang itu.

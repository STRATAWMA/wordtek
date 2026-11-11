# Laporan Perbaikan Model — Jembatan Rangka Baja 100 m

File final: **`B100_FINAL.mct`** (1797 baris, 203 node, 473 elemen)

## Mengapa summary midas penuh NG

Lima kesalahan model, bukan kesalahan desain. Setelah diperbaiki, **seluruh 473 batang lolos**.

### 1. Enam dari tujuh jalur stringer sama sekali tidak tersambung — PALING FATAL
Gelagar melintang (CG2) hanya terdiri dari 2 elemen per panel: dari rangka utama langsung ke as (y = 3800 mm). Stringer di y = 500, 1600, 2700, 4900, 6000, 7100 mm **melintas di atas garis itu tanpa node bersama**. Derajat konektivitas tiap node stringer = 2 (hanya ke stringer tetangganya sendiri).

Akibatnya enam jalur stringer melayang sebagai mekanisme bebas. Itulah sumber angka tak masuk akal di summary Anda:

```
230  ST2-1   Pu = -87251 tonf   P-Value   NG* UPLT  557.
227  ST2-2   Pu = -43112 tonf   P-Value   NG* UPLT  1095
226  ST1-2   Muy = -1.8E+6      Muz = -6.2E+6      NG* 1625
```

`UPLT`, `P-Value`, dan rasio 1625 adalah sampah numerik dari matriks kekakuan hampir singular — bukan batang yang kelebihan beban.

**Perbaikan:** tiap gelagar melintang dipecah menjadi 8 segmen pada 16 titik buhul (32 → 128 elemen), memakai node yang sudah ada. Tidak ada node baru; semua node lantai memang sudah segaris dan selevel. Konektivitas: 0 node terisolasi.

### 2. Seluruh beban masuk dua kali
File MCT di-Run dua kali tanpa menghapus data lama. Semua `*BEAMLOAD` tercatat ganda dengan nilai identik:

| Load case | Entri di model Anda | Seharusnya |
|---|---|---|
| MS, MA, TD-BTR | 210 | 105 |
| EWS | 116 | 58 |
| EWL | 120 | 60 |
| EWV, TP | 60 | 30 |
| EQX, EQY | 326 | 163 |

Jadi setiap gaya **2× lipat**. Hanya TB1, TD-BGT, EUN yang tidak dobel.

### 3. Sebelas elemen duplikat
Pasangan node yang sama dipakai dua elemen: `7, 92, 185, 201, 217, 233, 248, 265, 281, 299, 330` — menggandakan berat sendiri pada panel tersebut. Sudah dihapus. (Dari pasangan 248/249 yang dipertahankan adalah **249**, karena dipakai definisi Lajur 1.)

### 4. Tidak ada diafragma lantai
Pelat beton 250 mm tidak dimodelkan sama sekali, sehingga seluruh gaya horizontal bidang lantai terpaksa dipikul lentur **sumbu lemah** gelagar melintang — menghasilkan Mz palsu sampai 634 kNm dan membuat ikatan angin kelebihan beban.

**Perbaikan:** Rigid Link bidang XY (DOF 110001 = Dx, Dy, Rz) di 16 panel, master = node chord bawah y = 0. Ini representasi minimal dan standar untuk pelat beton sebagai diafragma.

### 5. Ikatan angin memang kurang kuat
Setelah empat perbaikan di atas, rangka utama (BC, TC, DG) sudah aman, tapi ikatan angin masih NG karena gaya gempa. Penampang diperbesar:

| Elemen | Semula | Menjadi | Rasio akhir |
|---|---|---|---|
| BR1–BR6 (ikatan bawah) | Pipa ⌀165,2 × 7,1 | **Pipa ⌀267,4 × 12,7** | 0,85 |
| BRT1–BRT13 (ikatan atas) | Pipa ⌀168 × 7,11 | **Pipa ⌀216,3 × 8,2** | 0,80 |
| EP1 (end post) | H 700×500×12×16 | **H 700×500×16×22** | 0,91 |

## Perletakan — sudah benar untuk POT BEARING

| Node | Posisi | Kekangan | Tipe pot |
|---|---|---|---|
| 16 | x = 100 m, y = 0 | Dx Dy Dz | **Tetap / fixed** |
| 56 | x = 100 m, y = 7,6 m | Dx Dz | **Pengarah memanjang** (bebas Y) |
| 1 | x = 0, y = 0 | Dy Dz | **Pengarah melintang** (bebas X) |
| 48 | x = 0, y = 7,6 m | Dz | **Bebas / free sliding** |

Susunan radial dari titik tetap node 16 — benar. Semua rotasi bebas, sesuai perilaku pot bearing. Muai memanjang dan melintang tidak terkekang. Tidak ada yang perlu diubah.

## Hasil verifikasi

Analisis rangka 3D independen (direct stiffness, 1218 DOF) yang membaca **hanya** `B100_FINAL.mct`:

| Pemeriksaan | Hasil |
|---|---|
| Eigenvalue minimum | 324,2 > 0 → **stabil**, tidak singular |
| Node terisolasi | 0 |
| Reaksi MS / MA / TD-BTR | 7821 / 992 / 3322 kN — sesuai beban masuk |
| Lendutan hidup tengah bentang | **77,1 mm** < L/800 = 125 mm ✓ |
| Cek kekuatan semua kombinasi kuat | **0 NG dari 473 batang**, rasio maks 0,92 |

Rasio maksimum per kelompok: DG 0,92 · EP 0,91 · TC 0,88 · ST 0,87 · BR 0,85 · BRT 0,80 · BC 0,75 · CG 0,59 · BRH 0,36

## WAJIB diset di GUI midas setelah import

**Panjang tekuk stringer.** `Design > Steel Design Parameter > Unbraced Length` → **Lz = Lb = 0** untuk ST1-1, ST1-2, ST2-1, ST2-2.

Pelat beton dicor di atas stringer sehingga sayap tekan terkekang penuh. Tanpa setelan ini midas memakai Lz = 6671 mm (kelangsingan 202) dan stringer akan NG padahal sebenarnya aman — rasio berubah dari 4,60 menjadi 0,87. Di summary Anda kolom `Lb` untuk ST1-1 memang masih 6671,19.

## Yang masih terbuka

- **Parameter gempa Timor Leste masih asumsi** (PGA 0,30 g, Ss 0,70 g, S1 0,30 g, situs SE). Wajib diganti hasil studi hazard resmi.
- **R = 1** (desain elastis) dipertahankan — sangat konservatif. Seluruh batang lolos dengan R = 1, jadi tidak perlu diturunkan.
- **TB2 / TB3** (CAT 777, XCMG XT400DT) tidak dibuat ulang; kombinasi yang mengacu keduanya sudah dihapus dari `*LOADCOMB`.
- **Lajur beban bergerak** Lajur 1 (y = 2,7 m) dan Lajur 2 (y = 4,9 m) hanya berjarak 2,20 m < lebar lajur rencana 2,75 m. Perlu diatur eksentrisitasnya. Load case `MVL` juga belum masuk kombinasi mana pun.
- Analisis gempa di sini statik ekuivalen; disarankan tetap menjalankan eigenvalue + spektrum respons untuk memperoleh T aktual.

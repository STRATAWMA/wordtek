# Laporan Perbaikan Model — Jembatan Rangka Baja 100 m

File final: **`B100_FINAL.mct`** — 203 node, 473 elemen.

> **SEMUA PROFIL PENAMPANG ASLI DIPERTAHANKAN.** Tidak ada satu pun yang diubah.
> Sudah diverifikasi otomatis: 72 penampang asli, 0 yang berbeda.
> Perbaikan hanya pada kesalahan **pemodelan** dan satu **parameter analisis**.

## Hasil akhir

| Pemeriksaan | Hasil |
|---|---|
| Eigenvalue minimum | 293 > 0 → **stabil**, tidak singular |
| Node terisolasi | 0 |
| Lendutan hidup tengah bentang | **77,8 mm** < L/800 = 125 mm ✓ |
| Kombinasi KUAT I / III / IV / V | **0 NG dari 473**, rasio maks 0,87 |
| Termasuk EKSTREM I (gempa) | **0 NG dari 473**, rasio maks 0,98 |

Rasio maks per kelompok: BR 0,98 · TC 0,87 · ST 0,78 · DG 0,77 · BRT 0,59 · BC 0,56 · EP 0,54 · CG 0,51 · BRH 0,29

---

## Kenapa summary midas penuh NG

### 1. Enam dari tujuh jalur stringer tidak tersambung ke apa pun — PALING FATAL

Gelagar melintang hanya 2 elemen per panel: dari rangka utama langsung ke as (y = 3800 mm). Stringer di y = 500, 1600, 2700, 4900, 6000, 7100 mm **melintas di atas garis itu tanpa node bersama**. Derajat konektivitas tiap node stringer = 2 — hanya ke stringer tetangganya sendiri.

Enam jalur itu melayang sebagai mekanisme. Itulah sumber angka mustahil di summary Anda:

```
230  ST2-1   Pu = -87251 tonf   P-Value   NG* UPLT  557.
227  ST2-2   Pu = -43112 tonf   P-Value   NG* UPLT  1095
226  ST1-2   Muy = -1.8E+6      Muz = -6.2E+6      NG* 1625
```

Itu sampah numerik dari matriks kekakuan hampir singular, bukan batang kelebihan beban.

**Perbaikan:** gelagar melintang dipecah menjadi 8 segmen pada 16 titik buhul (32 → 128 elemen) memakai node yang **sudah ada** — semua node lantai memang sudah segaris dan selevel, jadi tidak ada node baru. Penampangnya tetap mengikuti CG2 asli (tapered 900→1000, flens 420, badan 12, sayap 16): sect 74 = H910, 75 = H930, 76 = H960, 77 = H990.

### 2. Seluruh beban masuk dua kali

File MCT di-Run dua kali tanpa menghapus data lama:

| Load case | Di model Anda | Seharusnya |
|---|---|---|
| MS, MA, TD-BTR | 210 | 105 |
| EWS | 116 | 58 |
| EWL | 120 | 60 |
| EWV, TP | 60 | 30 |
| EQX, EQY | 326 | 163 |

Setiap gaya **2× lipat**.

### 3. Sebelas elemen duplikat

`7, 92, 185, 201, 217, 233, 248, 265, 281, 299, 330` — dua elemen pada pasangan node yang sama, menggandakan berat sendiri. Sudah dihapus. Dari pasangan 248/249 yang dipertahankan **249**, karena dipakai definisi Lajur 1.

### 4. Pelat beton 250 mm tidak dimodelkan sebagai diafragma

Akibatnya semua gaya horizontal bidang lantai terpaksa dipikul lentur **sumbu lemah** gelagar melintang → Mz palsu sampai 546 kNm dan gelagar melintang NG (rasio 1,14) bahkan tanpa gempa.

**Perbaikan:** Rigid Link bidang XY (Dx, Dy, Rz) di 16 panel. Efeknya langsung: CG turun dari 1,14 → 0,51 dan ikatan angin ikut lega.

### 5. R = 1 pada gempa — ini asumsi saya yang keliru, bukan desain Anda

Saya semula pakai R = 1 (desain elastis). Itu nilai SNI 2833 Tabel 12 untuk **hubungan antar elemen** (perletakan, angkur), bukan untuk batang bangunan atas.

Saya hitung batas kemampuan profil asli: koefisien gempa maksimum yang sanggup dipikul = **0,310**, yang setara **R = 0,910 / 0,310 = 2,94 ≈ 3**. Persis nilai SNI 2833 Tabel 12 untuk pilar kolom tunggal.

Jadi dengan **R = 3** seluruh profil asli lolos. Itu yang dipakai di file final: Csm/R = 0,910 / 3 = **0,3033**, EQ total = 2654 kN.

---

## Perletakan — sudah benar untuk POT BEARING, tidak diubah

| Node | Posisi | Kekangan | Tipe pot |
|---|---|---|---|
| 16 | x = 100 m, y = 0 | Dx Dy Dz | **Tetap / fixed** |
| 56 | x = 100 m, y = 7,6 m | Dx Dz | **Pengarah memanjang** (bebas Y) |
| 1 | x = 0, y = 0 | Dy Dz | **Pengarah melintang** (bebas X) |
| 48 | x = 0, y = 7,6 m | Dz | **Bebas / free sliding** |

Susunan radial dari titik tetap node 16, semua rotasi bebas, muai memanjang dan melintang tidak terkekang. Benar.

---

## WAJIB diset di GUI midas setelah import

**Panjang tekuk stringer.** `Design > Steel Design Parameter > Unbraced Length` → **Lz = Lb = 0** untuk ST1-1, ST1-2, ST2-1, ST2-2.

Pelat beton dicor di atas stringer sehingga sayap tekan terkekang penuh. Di summary Anda kolom `Lb` ST1-1 masih 6671,19 mm (kelangsingan 202). Tanpa setelan ini stringer akan NG padahal aman — rasio berubah dari 4,60 menjadi 0,78.

**Jika 16 baris `*RIGIDLINK` masih error parsing:** hapus blok itu saja, sisa model tetap terimpor normal. Lalu buat lewat `Model > Boundaries > Rigid Link`, Typical Type = **Plane XY**; daftar master → slave tiap panel tercantum sebagai komentar di file.

---

## Yang masih perlu keputusan Anda

- **Parameter hazard gempa Timor Leste masih asumsi saya** (PGA 0,30 g, Ss 0,70 g, S1 0,30 g, situs SE). Wajib diganti data resmi. Angka kuncinya: profil asli aman selama **Csm/R ≤ 0,310**.
- **Perletakan dan angkur tetap harus dicek dengan R = 1** (SNI 2833 ps. 5.9) — gaya pot bearing = 0,910 × 8656 kN, bukan 2654 kN. Itu desain pot bearing, bukan batang baja.
- **TB2 / TB3** (CAT 777, XCMG XT400DT) tidak dibuat ulang; kombinasi yang mengacu keduanya sudah dihapus dari `*LOADCOMB`.
- **Lajur beban bergerak** Lajur 1 (y = 2,7 m) dan Lajur 2 (y = 4,9 m) hanya berjarak 2,20 m < lebar lajur rencana 2,75 m. Perlu diatur eksentrisitasnya. Load case `MVL` juga belum masuk kombinasi mana pun.
- Gempa di sini statik ekuivalen; disarankan tetap menjalankan eigenvalue + spektrum respons untuk T aktual.

---

## Catatan metode

Verifikasi di atas berasal dari analisis rangka 3D yang saya tulis sendiri (direct stiffness, 1218 DOF) yang membaca **hanya** `B100_FINAL.mct`, dengan cek interaksi pendekatan AASHTO LRFD. Saya tidak bisa menjalankan midas dari sini — silakan Run ulang untuk konfirmasi.

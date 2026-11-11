# Laporan Perbaikan Model — Jembatan Rangka Baja B100

File final: **`B100_FINAL.mct`** — 203 node, 473 elemen.
Perhitungan: **`Pembebanan_Jembatan_Rangka_100m.xlsx`** (11 sheet, berumus penuh).

> **SEMUA PROFIL PENAMPANG ASLI DIPERTAHANKAN.** Diverifikasi otomatis: 72 penampang asli, 0 yang berubah.
> Perbaikan hanya pada kesalahan **pemodelan** dan **asumsi gempa saya sendiri**.
> Excel dan MCT sudah dicocokkan otomatis: **36 titik pembanding, 0 selisih**.

## Hasil akhir

| Pemeriksaan | Hasil |
|---|---|
| Eigenvalue minimum | 293 > 0 → **stabil**, tidak singular |
| Node terisolasi | 0 |
| Lendutan hidup tengah bentang | **78,9 mm** < L/800 = 125 mm ✓ |
| KUAT I / III / IV / V | **0 NG dari 473**, rasio maks 0,96 |
| Termasuk EKSTREM I (gempa Timor Leste) | **1 NG dari 473**, rasio 1,04 |

Perencana melaporkan stress ratio maks 0,99–0,996 — hasil saya 0,96 untuk kombinasi non-gempa, konsisten.

---

## Lima kesalahan pemodelan

### 1. Enam dari tujuh jalur stringer tidak tersambung — PALING FATAL
Gelagar melintang hanya 2 elemen per panel: rangka utama → as (y = 3800). Stringer di y = 500, 1600, 2700, 4900, 6000, 7100 **melintas tanpa node bersama**. Derajat konektivitas tiap node = 2.

Enam jalur itu melayang sebagai mekanisme — sumber angka mustahil di summary Anda (`Pu = -87251 tonf`, `P-Value`, `UPLT`, rasio 1625). Itu sampah numerik dari matriks hampir singular, bukan batang kelebihan beban.

**Perbaikan:** gelagar melintang dipecah 8 segmen di 16 titik buhul (32 → 128 elemen) memakai node yang **sudah ada**. Penampang mengikuti CG2 asli (tapered 900→1000, flens 420, badan 12, sayap 16) → sect 74 = H910, 75 = H930, 76 = H960, 77 = H990.

### 2. Seluruh beban masuk dua kali
File MCT di-Run dua kali tanpa menghapus data lama: MS/MA/TD-BTR 210 entri (seharusnya 105), EWS 116 (58), EWL 120 (60), EWV/TP 60 (30), EQX/EQY 326 (163). Setiap gaya **2× lipat**.

### 3. Sebelas elemen duplikat
`7, 92, 185, 201, 217, 233, 248, 265, 281, 299, 330`. Dihapus. Dari pasangan 248/249 dipertahankan **249** karena dipakai definisi Lajur 1.

### 4. Pelat beton tidak dimodelkan sebagai diafragma
Semua gaya horizontal bidang lantai terpaksa dipikul lentur **sumbu lemah** gelagar melintang → Mz palsu sampai 546 kNm, CG NG 1,14 bahkan tanpa gempa. **Perbaikan:** Rigid Link bidang XY (Dx, Dy, Rz) di 16 panel → CG turun ke 0,52.

### 5. Csm = SDS — ini kesalahan asumsi saya, bukan desain Anda
Saya memakai Csm = SDS = 0,918 (plateau perioda pendek). Dari eigenvalue di pemaparan, perioda struktur **TX = 1,722 s** dan **TY = 1,879 s** — jauh di cabang menurun spektrum (Ts = 0,62 s), jadi Csm = SD1/T, bukan SDS.

Asumsi saya **3,7× terlalu besar**. Itulah yang membuat ikatan angin dan end post seolah NG.

---

## Penyesuaian mengikuti pemaparan perencana

| Parameter | Semula saya pakai | Sekarang (ikut pemaparan) |
|---|---|---|
| Berat isi beton | 24 kN/m³ | **25 kN/m³** |
| Beban trotoar | selisih tebal 100 mm | **tebal penuh, ditambahkan di atas plat** |
| Metode gempa | statik ekuivalen, Csm = SDS | **spektrum respons, Csm = SD1/T** |
| R struktur atas | 3 | **1** |
| Kelas situs | SE | **tanah sedang (SD)** |
| Kombinasi gempa | 100% satu arah | **100% + 30% ortogonal** (SNI 2833 ps. 5.8) |

Beban aspal 50 mm × 22 kN/m³ = 1,10 kPa — identik dengan pemaparan.

## Hazard gempa: Seram → Timor Leste

| | Pemaparan (Seram) | Timor Leste (dipakai) |
|---|---|---|
| PGA | 0,39 | 0,30 |
| Ss | 0,77 | 0,70 |
| S1 | 0,247 | 0,30 |
| SDS | 0,918 | 0,868 |
| **SD1** | **0,470** | **0,540** |
| Csm arah X (T = 1,722 s) | 0,273 | **0,3136** |
| Csm arah Y (T = 1,879 s) | 0,250 | **0,2874** |

Yang menentukan **SD1**, bukan PGA/Ss — karena perioda struktur jauh di atas Ts. Timor Leste **15% lebih berat** dari Seram.

---

## Satu batang yang masih terlampaui

**BR1 elemen 291** (ikatan angin bawah dekat tumpuan), rasio **1,04** pada EKSTREM I-EQY. Terlampaui **3,7%**.

Batas kemampuan profil asli (hasil analisis):

> **SD1 ≤ 0,52**  atau  **S1 ≤ 0,289 g** (dengan Fv = 1,8, tanah sedang)

Asumsi saya S1 = 0,30 g hanya 4% di atas batas itu. **Angka S1 untuk Timor Leste ini asumsi saya, bukan data resmi** — bila data resmi memberi S1 ≤ 0,289 g, seluruh profil asli lolos tanpa perubahan apa pun. Karena itu saya **tidak** memperbesar profil; keputusannya menunggu data hazard Anda.

---

## Perletakan — sudah benar untuk POT BEARING, tidak diubah

| Node | Posisi | Kekangan | Tipe pot |
|---|---|---|---|
| 16 | x = 100 m, y = 0 | Dx Dy Dz | **Tetap / fixed** |
| 56 | x = 100 m, y = 7,6 m | Dx Dz | **Pengarah memanjang** (bebas Y) |
| 1 | x = 0, y = 0 | Dy Dz | **Pengarah melintang** (bebas X) |
| 48 | x = 0, y = 7,6 m | Dz | **Bebas / free sliding** |

Susunan radial dari titik tetap node 16, semua rotasi bebas, muai tidak terkekang. Benar.

---

## WAJIB diset di GUI midas setelah import

1. **Panjang tekuk stringer.** `Design > Steel Design Parameter > Unbraced Length` → **Lz = Lb = 0** untuk ST1-1, ST1-2, ST2-1, ST2-2. Pelat beton dicor di atasnya sehingga sayap tekan terkekang penuh. Di summary Anda kolom `Lb` ST1-1 masih 6671,19 mm (kelangsingan 202) — tanpa setelan ini stringer NG padahal aman.
2. **Eigenvalue ulang.** Model sudah berubah (stringer tersambung, diafragma, beban tidak dobel), jadi TX/TY akan bergeser. Jalankan eigenvalue, lalu perbarui sel `T_X` dan `T_Y` di sheet `0-INPUT` — seluruh perhitungan gempa ikut menyesuaikan otomatis.
3. **Jika 16 baris `*RIGIDLINK` masih error parsing:** hapus blok itu saja, sisa model tetap terimpor. Lalu buat lewat `Model > Boundaries > Rigid Link`, Typical Type = **Plane XY**. Daftar master → slave tercantum sebagai komentar di file.

---

## Yang masih terbuka

- **Data hazard resmi Timor-Leste** (PGA, Ss, S1) — ini satu-satunya yang menentukan apakah BR1 lolos.
- **Perletakan dan angkur** tetap dicek dengan gaya elastis penuh (SNI 2833 ps. 5.9), bukan hasil bagi R.
- **TB2 / TB3** (CAT 777, XCMG XT400DT) tidak dibuat ulang; kombinasi yang mengacunya sudah dihapus dari `*LOADCOMB`.
- **Lajur beban bergerak** Lajur 1 (y = 2,7 m) dan Lajur 2 (y = 4,9 m) berjarak 2,20 m < lebar lajur rencana 2,75 m. Load case `MVL` juga belum masuk kombinasi mana pun.
- Pemaparan menyebut lebar jembatan 7,7 m dan plat 262 mm; model dan brief Anda memakai 7,6 m as-as dan plat 250 mm. Keduanya ada sebagai sel input di Excel.

## Catatan metode

Verifikasi berasal dari analisis rangka 3D yang saya tulis sendiri (direct stiffness, 1218 DOF) yang membaca **hanya** `B100_FINAL.mct`, dengan cek interaksi pendekatan AASHTO LRFD (tanpa LTB). Saya tidak bisa menjalankan midas dari sini — silakan Run ulang untuk konfirmasi.

---

## Perbaikan format MCT (tiga putaran error import)

| Error midas | Sebab | Perbaikan |
|---|---|---|
| `The number of parameters are too many` (baris 28, 36, 37) | koma di dalam teks deskripsi `*STLDCASE` | koma diganti tanda hubung |
| `Binary code has characters other than 0 & 1` lalu `The integer value without a sign is invalid` (16 baris) | urutan field `*RIGIDLINK` salah; dua pesan itu menunjukkan field 1 dan 2 harus integer dan field 3 binary | satu pasangan master–slave per baris: `MASTER_NODE, SLAVE_NODE, DOF, GROUP` → 128 baris |
| `*REBAR-MATL-CODE cannot be executed when nodes or sections are included` | blok itu hanya untuk desain beton bertulang | blok dihapus (tidak dipakai jembatan baja) |

## Cek setelah impor — jumlah entri harus TEPAT

| Load case | Entri |
|---|---|
| MS | Self Weight + **105** beam |
| MA | **105** beam |
| TD-BTR | **105** beam |
| TD-BGT | **7** nodal |
| TB1 | **30** beam + **4** nodal |
| TP | **30** beam |
| EWS / EWL / EWV | **58** / **60** / **30** beam |
| EUN / EUN-N | **473** element temperature |
| EQX / EQY | **473** beam + **112** nodal |
| Boundaries → Rigid Link | **128** |

Bila MS menunjukkan 210, berarti terimpor ke model yang sudah berisi data — ulangi dari model kosong.

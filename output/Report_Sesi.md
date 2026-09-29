# Report Sesi – Pre-Design Profil WB SM490YB, Jembatan Road-4 PT SDA

**Tanggal:** 29-09-2026 | **Repo:** `stratawma/wordtek` branch `claude/festive-shannon-93vam8`
**Status:** PRE-DESIGN (bukan gambar IFC) – wajib diverifikasi dengan model 3D (SAP2000/MIDAS) sebelum dipakai.

## 1. Lingkup & Data Masukan
| Jembatan | Lokasi | Tipe | Bentang | Lebar |
|---|---|---|---|---|
| Jembatan I | Road-4 STA 0+750 | Rangka baja Warren (deck bawah) | 60 m (12 panel @ 5 m) | 11,0 m jalur, 11,53 m as-rangka |
| Fly Over | Road-4 STA 0+050 | Girder baja komposit | 30,6 m (as-abutmen 30,8 m) | 11,0 m, 6 girder @ 1,7 m, H = 1,7 m |

Sumber data: gambar klien F.1-02…F.1-07 dan F.2-02…F.2-07, serta ketentuan klien:
- 3.2.2.2.1 / 3.2.2.2.2: beban mengacu SNI 1725-2016, dengan kendaraan operasional Scania P410 B8x4 58 t (hauling 40 t).
- 3.2.2.2.4: baja struktur utama JIS SM490/BJ50, baut F10T, las E70XX. Output ini memakai **SM490YB**.
- 3.2.2.2.5: SNI 1725-2016, SNI T-12-2004, RSNI T-03-2005.
- 4.4.3: SE 07/SE/Db/2025 Seksi 7.4, toleransi Pasal 1.4, material pre-approval & approval, uji tarik/tekuk/tekan 3 spesimen per tebal pelat per supplier.

## 2. Kriteria Desain
- **Standar kekuatan:** SNI 1729-2020 / AISC 360 LRFD. Tekan φ=0,9, tarik leleh φ=0,9, tarik putus φ=0,75 (An = 0,85Ag, U = 0,9), lentur φ=0,9, geser φ=0,9.
- **SM490YB:** Fu = 490 MPa. Fy = 365 MPa (t ≤ 16), 355 MPa (16 < t ≤ 40), 335 MPa (40 < t ≤ 50).
- **Tebal pelat (stok Krakatau Posco / Gunung Raja Paksi):** 8, 9, 10, 12, 14, 16, 19, 20, 22, 25, 28, 30, 32, 36, 40, 45, 50 mm.
- **Batas kelangsingan:** KL/r ≤ 120 (batang tekan utama), ≤ 140 (bracing), L/r ≤ 200 (tarik). Elemen tekan dibuat non-slender.
- **Faktor beban:** MS baja 1,1; MS beton 1,3; MA 2,0; TD/TT 1,8.
- **Beban lajur D:** BTR q = 9(0,5 + 15/L) kPa. BGT 49 kN/m. FBD 0,375 (L = 60 m) dan 0,40 (L = 30,6 m).
- **Scania P410 B8x4 58 t (asumsi):** gandar 7 + 7 + 22 + 22 t @ 1,95 / 3,10 / 1,37 m. Konvoi dengan jarak bersih 10 m, FBD 30%.
- **Lendutan girder:** ≤ L/800 akibat Scania (servis).

## 3. Metode
1. **Rangka:** determinate. Gaya batang dihitung dari garis pengaruh (chord = M/h, diagonal = V/sinθ). Beban hidup ditempatkan pada nilai maksimum ± untuk lajur D dan konvoi Scania, satu lajur per rangka. Berat sendiri diiterasi dari hasil desain, ditambah 20% untuk gusset, splice, dan bracing (konvergen di 35,7 kN/m untuk seluruh jembatan).
2. **Optimasi:** skrip mencari penampang WB teringan yang UR ≤ 0,95. Semua batang rangka utama diseragamkan d = 500 mm supaya pas di antara pelat buhul. Chord dan diagonal dikelompokkan per zona untuk efisiensi fabrikasi.
3. **Girder:** momen plastis komposit (Dp/Dt ≤ 0,42), geser dengan stiffener @ 1,5 m, LTB saat pengecoran (Lb = 5,1 m), dan lendutan L/800. Distribusi beban truk memakai DF AASHTO 0,482.

## 4. Hasil – Jembatan Rangka Baja 60 m

Geometri: Warren 12 panel @ 5.0 m, tinggi c/c 6.0 m, jarak rangka 11.53 m. BTR q = 6.75 kPa, FBD = 0.375, berat baja iterasi = 35.7 kN/m (2 rangka + lantai).

| Frame Code | Elemen | Batang | L (m) | Pu tarik (kN) | Pu tekan (kN) | Profil | Fy (MPa) | kg/m | UR | Gov |
|---|---|---|---|---|---|---|---|---|---|---|
| BC-Z1 | Bottom Chord | BC-01, BC-02, BC-11, BC-12 | 5.00 | 5600 | 0 | WB 500x250x22x22 | 355 | 165.1 | 0.95 | SCANIA |
| BC-Z2 | Bottom Chord | BC-03, BC-04, BC-09, BC-10 | 5.00 | 10206 | 0 | WB 500x400x22x36 | 355 | 300.0 | 0.95 | SCANIA |
| BC-Z3 | Bottom Chord | BC-05, BC-06, BC-07, BC-08 | 5.00 | 12241 | 0 | WB 500x500x14x40 | 355 | 360.2 | 0.95 | SCANIA |
| TC-Z1 | Top Chord | TC-01, TC-02, TC-10, TC-11 | 5.00 | 0 | 7006 | WB 500x500x16x19 | 355 | 207.2 | 0.94 | SCANIA |
| TC-Z2 | Top Chord | TC-03, TC-04, TC-08, TC-09 | 5.00 | 0 | 11048 | WB 500x475x16x36 | 355 | 322.2 | 0.95 | SCANIA |
| TC-Z3 | Top Chord | TC-05, TC-06, TC-07 | 5.00 | 0 | 12308 | WB 500x500x12x40 | 355 | 353.6 | 0.95 | SCANIA |
| EC-E | End Chord | EC-01, EC-24 | 6.50 | 0 | 5169 | WB 500x425x14x20 | 355 | 184.0 | 0.92 | SCANIA |
| DC-Z1 | Diagonal Chord | DC-02, DC-03, DC-04, DC-05, DC-06, DC-19, DC-20, DC-21, DC-22, DC-23 | 6.50 | 5169 | 4279 | WB 500x400x16x16 | 365 | 159.3 | 0.95 | SCANIA |
| DC-Z2 | Diagonal Chord | DC-07, DC-08, DC-09, DC-10, DC-15, DC-16, DC-17, DC-18 | 6.50 | 2670 | 2670 | WB 500x325x14x16 | 365 | 133.1 | 0.88 | SCANIA |
| DC-Z3 | Diagonal Chord | DC-11, DC-12, DC-13, DC-14 | 6.50 | 1180 | 1180 | WB 500x275x14x16 | 365 | 120.5 | 0.58 | SCANIA |

| Frame Code | Elemen | Keterangan | L (m) | Mu / Pu | Vu (kN) | Profil | kg/m | UR |
|---|---|---|---|---|---|---|---|---|
| ST-1 | Stringer | 7 lines x 12 panels @ 1.67 m | 5.00 | 527 kNm | 482 | WB 550x225x9x14 | 86.3 | 0.90 |
| CG-1 | Cross Girder | 13 lines @ bottom nodes | 11.53 | 3825 kNm | 1211 | WB 1350x350x10x22 | 223.4 | 0.95 |
| BR-1 | Brace (top lateral strut / portal) | 11 struts at top nodes + 2 portals | 11.53 | 246 kN | - | WB 250x325x8x14 | 85.4 | 0.26 |
| DM-1 | Diagonal Member (lateral X-bracing) | top & bottom lateral bracing | 12.57 | 268 kN | - | WB 200x200x8x9 | 39.7 | 0.57 |


**Berat baja estimasi:** ±35,7 kN/m untuk seluruh jembatan, sekitar 218 t (termasuk 20% sambungan). Beban Scania konvoi menentukan semua batang rangka.

## 5. Hasil – Fly Over Girder Komposit 30,6 m

6 girder @ 1.7 m, slab 250 mm fc' 30 MPa. DF Scania = 0.482. Mu (SNI D) = 4798 kNm, Mu LL Scania = 4857 kNm, Mu total = 8032 kNm, Vu = 1488 kN, M konstruksi = 3017 kNm.

| Frame Code | Elemen | Keterangan | L (m) | Mu (kNm) | Vu (kN) | Profil | kg/m | UR |
|---|---|---|---|---|---|---|---|---|
| GR-1 | Main Girder (composite, interior & exterior) | G1..G6 @ 1.7 m | 30.60 | 8032 | 1488 | WB 1700x300/350x12x16/20 | 249.4 | 0.95 |
| DF-1 | Diaphragm / Cross Beam | 7 lines x 5 bays (@~5.1 m) | 1.70 | 150 | 0 | WB 600x200x9x12 | 78.4 | 0.21 |
| LB-1 | Lateral Bracing (erection) | bottom flange X | 5.38 | 0 | 0 | WB 200x200x8x12 | 48.7 | 0.30 |

Notasi WB d x bf x tw x tf (mm); girder: WB d x bf_atas/bf_bawah x tw x tf_atas/tf_bawah.
Tebal pelat hanya dari stok pasar Indonesia: [8, 9, 10, 12, 14, 16, 19, 20, 22, 25, 28, 30, 32, 36, 40, 45, 50] mm.

**Berat baja estimasi:** 6 × 30,6 × 249,4 kg/m ≈ 45,8 t untuk girder saja.

## 6. Daftar Kode Frame
| Prefix | Elemen |
|---|---|
| BC | Bottom Chord (Z1 ujung, Z2 seperempat bentang, Z3 tengah) |
| TC | Top Chord |
| EC | End Chord / end post |
| DC | Diagonal Chord (diagonal rangka utama) |
| BR | Brace, strut atas / portal |
| DM | Diagonal Member, ikatan angin X atas & bawah |
| ST | Stringer |
| CG | Cross Girder |
| GR | Girder utama fly over |
| DF | Diafragma |
| LB | Ikatan angin bawah (erection) |

Nomor batang individual (BC-01…12, TC-01…11, EC-01/24, DC-02…23) dan zona-nya ada di **Gambar_Frame_Code.pdf**, lembar 1–5.

## 7. Batasan & Tindak Lanjut
1. **Data Scania:** tabel beban gandar klien belum diterima. Kalau berbeda, ubah `SCANIA_AX` / `SCANIA_SP` di `bridge_design.py`, lalu jalankan ulang skrip.
2. **Belum dicek:** fatik (kritis untuk truk tambang, detail kategori sambungan), sambungan baut F10T dan gusset, momen sekunder rangka, gempa (SNI 2833), lendutan rangka L/800, tekuk lateral top chord (U-frame), dan camber.
3. **Wajib dilanjutkan:** verifikasi dengan model 3D SAP2000/MIDAS memakai `frame_section.csv`.
4. **Material:** uji material mengikuti 4.4.3. Tiga spesimen per tebal pelat (12, 14, 16, 19, 20, 22, 36, 40 mm) untuk setiap supplier, dengan pre-approval mill certificate lalu approval uji lab yang disaksikan PT SDA.

## 8. File
- `bridge_design.py`: perhitungan (Python murni).
- `draw_frames.py`: pembuat gambar (butuh `pip install matplotlib`).
- `output/hasil_desain.md`, `output/frame_section.csv`: tabel hasil.
- `output/Gambar_Frame_Code.pdf`: 5 lembar gambar kode frame.
- `output/Report_Sesi.md`: laporan ini.

**Sinkron ke laptop:** `git pull origin claude/festive-shannon-93vam8`

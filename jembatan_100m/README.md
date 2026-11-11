# Pembebanan Jembatan Rangka Baja Kelas A — Bentang 100 m

## Data struktur (dibaca dari file `6052454f-B100.mct`)
| Item | Nilai |
|---|---|
| Bentang as–as perletakan | 99,9975 m (15 panel × 6666,5 mm) |
| Lebar as ke as rangka utama | 7600 mm |
| Lebar lajur bersih | 6000 mm |
| Trotoar | 2 × 500 mm |
| Stringer | 7 buah @ 1100 mm, simetris terhadap as (y = 500…7100 mm) |
| Gelagar melintang (CG2) | 16 lokasi, tapered 900–1000 mm |
| Tinggi rangka maksimum | 8500 mm |
| Berat baja termodel | 3188,8 kN (31,89 kN/m) |
| Plat lantai 250 mm | **belum** dimodelkan sebagai elemen plate → diinput sebagai beban |

Tata letak melintang: `0,30 rangka | 0,50 trotoar | 6,00 lajur | 0,50 trotoar | 0,30 rangka = 7,60 m`

## Isi folder
| File | Keterangan |
|---|---|
| `Pembebanan_Jembatan_Rangka_100m.xlsx` | Perhitungan **berumus**. Semua angka turunan adalah formula Excel yang mengacu ke nama sel di sheet `0-INPUT`. Ubah input → seluruh hasil ikut berubah. |
| `Pembebanan_B100.mct` | File perintah MCT **hanya blok pembebanan** — untuk dijalankan di MCT Command Shell pada model yang sudah terbuka. |
| `B100_dengan_pembebanan.mct` | Model asli **+** blok pembebanan, siap diimpor sebagai satu file. |
| `calc.py`, `xls.py`, `mct.py`, `parse.py` | Skrip pembangkit (parsing geometri → hitung → Excel + MCT). |

## Rekap beban yang diinput
Satuan kN, m. Stringer tepi = ST‑1 & ST‑7.

| Load case | Tipe | Nilai |
|---|---|---|
| **MS** plat lantai 250 mm | D | q = 0,25 × 24 = 6,00 kPa → 6,30 (tepi) / 6,60 (dalam) kN/m — total 45,6 kN/m |
| **MA** topping trotoar 100 mm | D | 1,20 kN/m per sisi |
| **MA** sandaran | D | 0,50 kN/m per sisi |
| **MA** aspal 50 mm | D | q = 1,10 kPa → 0,275 (tepi) / 1,21 (dalam) kN/m — total MA 10,00 kN/m |
| **TD‑BTR** | L | q = 9,0(0,5 + 15/L) = **5,85 kPa**; 100 % pada 5,5 m + 50 % pada 0,5 m → b<sub>eff</sub> = 5,75 m → 0,731 / 6,435 kN/m — total 33,64 kN/m |
| **TD‑BGT** | L | FBD = 0,30 (L ≥ 90 m) → p = 49 × 1,30 = **63,70 kN/m** → beban titik 7,96 / 70,07 kN pada buhul x = 46,6655 m — total 366,3 kN |
| **TB1** gaya rem | L | max(25 % × 500 ; 5 % ×(500 + BTR·2,75·L)) = max(125 ; 105,4) = **125 kN/lajur**; 2 lajur × m=1,0 → **250 kN** (AASHTO BR = 162,5 kN, tidak menentukan) → 0,500 kN/m GX pada ST‑2…ST‑6 + kopel vertikal ±2,25 kN di 4 node tumpuan |
| **TP** pejalan kaki | L | 5 kPa × 0,5 m = 2,50 kN/m pada ST‑1 & ST‑7 |
| **EWS** angin struktur | W | P<sub>D</sub> = 2,4 kPa; A = 2 × 2,370 + 0,350 = 5,090 m²/m → **12,22 kN/m**; chord atas 3,047 + chord bawah 3,264 kN/m tiap rangka (chord atas diskala L/L<sub>tc</sub> karena panjangnya hanya 93,331 m, agar resultan tepat 1221,6 kN) |
| **EWL** angin kendaraan | W | 1,46 kN/m @ 1,8 m → horizontal 0,730 kN/m tiap chord bawah + kopel vertikal ± 0,346 kN/m |
| **EWV** angin vertikal | W | 0,96 × 7,6 = 7,296 kN/m ke atas; windward 5,472 / leeward 1,824 kN/m |
| **EUN / EUN‑N** suhu | T | ± 15 °C seragam seluruh elemen (SNI 1725 Tabel 18: 15–40 °C) |
| **EQX / EQY** gempa | E | Dili: PGA 0,30 g, S<sub>s</sub> 0,70 g, S<sub>1</sub> 0,30 g, situs SE → A<sub>s</sub> = 0,36; S<sub>DS</sub> = 0,91; S<sub>D1</sub> = 0,84; T<sub>s</sub> = 0,923 s; C<sub>sm</sub>/R = **0,910** (R = 1) → W = 8748,7 kN, EQ = 7961 kN |

Berat permanen = plat 45,6 + topping 2,4 + aspal 6,6 + sandaran 1,0 + baja 31,89 = **87,49 kN/m**.

## Cara input ke midas Civil
1. Buka model `B100`.
2. **Hapus dulu** isi load data lama pada MS, MA, TD‑BTR, TD‑BGT, EWS, EWL, EWV, EUN, EQX, EQY (Load → Static Loads) agar beban tidak dobel.
3. `Tools → MCT Command Shell` → buka `Pembebanan_B100.mct` → **Run**.
   Blok diawali `*UNIT KN, M` dan diakhiri `*UNIT TONF, MM` sehingga satuan model kembali seperti semula.
4. Alternatif: impor langsung `B100_dengan_pembebanan.mct` sebagai model baru.

## Catatan & peringatan
- **Parameter gempa Timor Leste adalah asumsi** hazard regional Dili. Wajib diganti dengan hasil studi hazard situs/peta gempa resmi Timor‑Leste. Ganti sel `PGA`, `S_s`, `S_1`, `F_pga`, `F_a`, `F_v`, `R_eq` di sheet `0-INPUT`.
- Dengan R = 1 (desain elastis sambungan & perletakan, SNI 2833 ps. 5.9) koefisien 0,910 sangat besar. Untuk bangunan bawah dapat dipakai R = 3 — cukup ubah `R_eq`.
- Gempa di sini **statik ekuivalen**. Disarankan tetap menjalankan eigenvalue + spektrum respons di midas untuk memperoleh T aktual dan C<sub>sm</sub> yang benar.
- **Elemen duplikat pada model** (dua elemen pada pasangan node yang sama) — sudah dikecualikan dari pembebanan, tapi tetap menggandakan berat sendiri di panel tersebut. Sebaiknya dihapus:
  `7` (dgn 6), `92` (dgn 91), `185`, `201`, `217`, `233`, `249`, `265`, `281`, `299`, `330`.
- Deskripsi load case lama di model masih mengacu jembatan 36 m (EWs 4,70 kN/m, PGA 0,0431 g) — sudah ditimpa oleh file ini.
- Angin longitudinal (P<sub>B</sub> = 1,2 kPa) belum dibuat load case; nilainya tercantum di sheet `5-ANGIN` bila diperlukan.
- `*SELFWEIGHT` tetap dipakai untuk baja — jangan menambahkan berat baja secara manual.

## Verifikasi Excel vs midas
Sheet `9-VERIFIKASI-MIDAS` memuat jumlah entri dan resultan tiap load case untuk dicocokkan dengan model tree midas.

| Load case | Entri midas | Resultan |
|---|---|---|
| MS | Self Weight + 105 beam | 4559,9 kN (plat) + 3188,8 kN (baja, dihitung midas) |
| MA | 105 beam | 999,98 kN |
| TD-BTR | 105 beam | 3363,7 kN |
| TD-BGT | 7 nodal | 366,3 kN |
| TB1 | 75 beam + 4 nodal | 250,0 kN (GX) |
| TP | 30 beam | 500,0 kN |
| EWS | 58 beam | 1221,6 kN (GY) |
| EWL | 60 beam | 146,0 kN (GY) + kopel |
| EWV | 30 beam | 729,6 kN (+Z) |
| EUN / EUN-N | 388 element temp | ±15 °C |
| EQX / EQY | 163 beam | 7961,3 kN |

57 titik pembanding Excel↔MCT sudah dicek otomatis: **0 selisih**.

## TB2 / TB3 belum dibuat
Model lama (jembatan 36 m) punya `TB2` (gaya rem CAT 777) dan `TB3` (XCMG XT400DT 8×4 GVW 65 t). Kendaraan khusus itu belum ditentukan untuk jembatan 100 m ini, jadi **tidak dibuat ulang**. Akibatnya kombinasi `KUAT II-TK`, `KUAT II-DT`, `LAYAN I-TK`, `LAYAN II-TK`, `LAYAN II-DT` masih mengacu load case yang kosong. Beri tahu bila kendaraan khusus tersebut tetap dipakai.

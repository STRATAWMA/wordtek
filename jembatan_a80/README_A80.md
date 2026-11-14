# A80 - Model elemen hingga jembatan rangka pelengkung 80 m

Sumber: `R1_APPROVAL_A80_PELENGKUNG_JAKON.pdf` (GA-ITK09 rev 1, PT Indo Trans Konstruksi).
File model: `A80_PELENGKUNG_FEM.mct` - run ke model KOSONG, satuan kN, m.

## Isi model
| | |
|---|---|
| Simpul | 1.490 |
| Elemen batang | 1.144 |
| Elemen PLATE (lantai beton) | 640 (64 x 10) |
| Rigid link komposit | 715, DOF 111111, lengan 381 mm |

Ikatan angin silang DISAMBUNG di titik perpotongan, sesuai DET-21 pada
SECTION A. Tanpa itu diagonal menjadi 11,66 m menerus dan KL/r = 208.

Bentang 80.000 mm, 16 panel x 5.000, lebar as-ke-as 10.000 mm,
puncak pelengkung 19.095 mm di atas balok tarik.

## Geometri pelengkung (dari SECTION A-G)

Section A-G = titik buhul 2-8; dikunci oleh hanger A80-H5/H6/H7 di Section D/E/F.
Titik 1 dan 0 hasil ekstrapolasi kurva; x=0 memberi z = -33 mm, jadi
pelengkung bertumpu tepat pada level balok tarik.

| x (mm) | chord ATAS | tinggi rangka | chord TENGAH |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 5.000 | 5.246 | 1.605 | 3.641 |
| 10.000 | 9.410 | 2.455 | 6.955 |
| 15.000 | 12.650 | 3.060 | 9.590 |
| 20.000 | 15.115 | 3.475 | 11.640 |
| 25.000 | 16.930 | 3.750 | 13.180 |
| 30.000 | 18.175 | 3.915 | 14.260 |
| 35.000 | 18.890 | 3.995 | 14.895 |
| 40.000 | 19.095 | 3.990 | 15.105 |

Cek silang dengan dimensi elevasi: 19.510 - 19.095 = 415 mm dan
15.510 - 15.105 = 405 mm, keduanya setengah tinggi profil chord. Tinggi
rangka di puncak 3.990 vs 19.510-15.510 = 4.000. Cocok.

## Penampang (dari MATERIAL LIST, lembar 10-11)
| Mark | Fungsi | Profil |
|---|---|---|
| A80-B1..B17 | balok tarik (bottom chord) | WB1000x400x20x30 |
| A80-T1 / M1 | chord pelengkung, panel ujung | WB400x500x20x30 |
| A80-T2..T7 / M2..M7 | chord pelengkung | WB400x350x20x30 |
| A80-H1..H16 | hanger / vertical bracing | WB400x250x12x20 |
| A80-VB24..VB29 | web rangka pelengkung | WB400x200x12x20 |
| A80-C1..C3 | cross girder | WB550x400x20x30 |
| A80-S1, S2 | stringer (9 jalur @ 1100) | WB450x220x8x12 |
| A80-HB, A80-VB | ikatan angin | PIPE 6" (STK41) |
| A80-LS1 | lateral stop | WB850x400x10x20 |

Mutu (SPESIFIKASI TEKNIK lembar 2): SM490YB (fy 365 MPa t<=16, 355 MPa t>16),
pipa STK41 (fy 235), lantai beton fc' 30 MPa.

## ASUMSI - perlu dikonfirmasi
1. **Tebal pelat lantai 250 mm** - tidak tercantum di gambar yang dikirim.
2. **Lebar jalan 7,0 m + trotoar 2 x 1,5 m** - pembagian melintang tidak
   tercantum; yang ada hanya 10.000 antar rangka dan 9 stringer @ 1100.
3. **Pipa 6" diambil 165,2 x 7,1 mm (STK41)** - ini perlu dipastikan.
   30 batang ikatan angin melintang sepanjang 10 m (antar rangka pelengkung,
   bidang chord ATAS dan chord TENGAH) memberi KL/r = 179, melewati batas
   AASHTO 6.9.3 untuk batang bracing (140). Kalau pipanya sebenarnya 8"
   (216,3 x 8,2) maka KL/r = 136 dan lolos.
4. Perletakan: 4 titik, 111000 / 101000 / 011000 / 001000.

## Kaki pelengkung - BOX dari elemen SHELL

Di KEDUA ujung dan KEDUA rangka, daerah **x = 0 .. 5.000 mm** (sampai hanger
pertama) dimodelkan sebagai **box 3D dari elemen pelat**, bukan elemen balok.

| bagian | tebal | |
|---|---|---|
| seluruh pelat box: badan, sayap, PELAT MELENGKUNG | **35 mm** | 920 pelat |
| lantai beton | 250 mm | 640 pelat |

Lebar box 400 mm (dua badan di y = sisi +- 200), tinggi box balok tarik
1.000 mm.

### Pelat melengkung
Menerus dari **x = 0** sampai x = 5.000, berbagi simpul dengan sayap atas
box balok tarik di z = +500 (dicek: simpul pertemuan dipakai 3-4 pelat).

| x (mm) | z (mm) | | x (mm) | z (mm) |
|---|---|---|---|---|
| 0 | 500 | | 3.000 | 1.882 |
| 1.000 | 689 | | 4.000 | 2.669 |
| 2.000 | 1.186 | | 5.000 | 3.441 |

Berangkat MENDATAR di tumpuan dan berakhir sejajar chord TENGAH
(kemiringan 0,754 terhadap 0,728 chord). Kurva Hermite.

### Peralihan
- **x = 0**: simpul perletakan diikat rigid link ke penampang ujung box
  sebagai diafragma, supaya reaksi tumpuan masuk ke box.
- **x = 5.000**: penampang box diikat ke simpul balok chord ATAS dan chord
  TENGAH. Panel chord 0 tidak lagi dibuat sebagai balok.

### Kalibrasi ukuran
Gambar DETAIL vektor 1:30. Kalibrasi lebar hanger A80-H16: tergambar
23,5 pt -> 248,6 mm terhadap 250 mm sebenarnya, jadi 1 pt = 10,584 mm.
Panjang/lebar teliti sekitar +-1%; **tebal pelat box 35 mm sesuai koreksi
pengguna**.

## Beban gempa - SNI 2833-2016, Timor Leste

Beban statik ekuivalen, dikenakan sebagai beban simpul sebanding massa
tributari tiap simpul (massa dihitung dari berat batang, berat pelat, dan
beban mati yang sudah berupa beban simpul).

| | |
|---|---|
| PGA / Ss / S1 | 0,30 / 0,70 / 0,30 g - **ASUMSI**, sama dengan proyek B100 |
| Tanah sedang | Fpga 1,200 · Fa 1,240 · Fv 1,800 |
| SDS / SD1 / Ts | 0,868 / 0,540 / 0,622 s |
| **Periode T** | **1,20 s - ASUMSI** |
| Csm = SD1/T | 0,450 |
| R struktur atas | 1,0 (SNI 2833 ps.5.9.2) |
| **Koefisien gempa** | **0,450** |
| Berat permanen | 10.606 kN |
| **Gaya gempa total** | **4.773 kN** tiap arah |

Kombinasi: EKSTREM I-EQX dan EKSTREM I-EQY (SNI 2833 ps.5.8):
`1,1 MS + 1,4 MA + 1,0 EQx + 0,3 EQy` dan sebaliknya.

**Periode T belum dari analisis.** Karena Csm = SD1/T, beban gempa
berbanding terbalik dengan T. Jalankan `Analysis > Eigenvalue` di midas,
baca T mode pertama, lalu cukup kalikan faktor EQ di kombinasi dengan
`1,20 / T_sebenarnya`. Contoh: kalau T = 1,8 s maka faktornya 0,667.

## Perbaikan beban suhu
EUN / EUN-N kini dikenakan ke **seluruh** elemen (2.830: batang DAN pelat).
Sebelumnya hanya batang, sehingga baja memuai melawan lantai beton yang
tidak ikut memuai dan timbul gaya dalam semu - itu yang membuat ikatan
angin elemen 1091 ikut terbebani pada kombinasi Kuat III.

## BELUM termasuk
- **Plat buhul sebagai elemen shell** - material list memberi tebal (PL20)
  tetapi tidak memberi outline, jadi belum bisa dimodelkan setia.

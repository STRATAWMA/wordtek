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

Di KEDUA ujung dan KEDUA rangka, daerah x = 0 .. 2.500 mm dimodelkan sebagai
**box 3D dari elemen pelat**, bukan elemen balok:

| bagian | tebal | keterangan |
|---|---|---|
| badan box (2 bidang, y = sisi +- 200) | **20 mm** | lebar box 400 mm |
| sayap atas & bawah | **30 mm** | |
| **PELAT MELENGKUNG** | **30 mm** | sisi bawah kaki pelengkung |
| badan balok tarik / lantai | 20 / 250 mm | |

Jumlah: 448 pelat 20 mm + 224 pelat 30 mm + 640 pelat lantai = 1.312.

**Box balok tarik**: 1000 x 400 mm (WB1000x400x20x30), x = 0 .. 2.500.
**Box kaki pelengkung**: sisi atas mengikuti chord ATAS (zT + 200), sisi
bawah adalah PELAT MELENGKUNG yang berangkat MENDATAR dari sayap atas balok
tarik (z = +500) lalu melengkung mulus sampai sejajar chord TENGAH di
x = 2.500. Kurvanya Hermite, jadi kemiringan di tumpuan tepat nol dan di
ujung tepat sama dengan kemiringan chord tengah (0,728).

**Peralihan**: di x = 2.500 penampang box diikat rigid link ke simpul balok
chord ATAS dan chord TENGAH; di x = 0 simpul perletakan diikat ke penampang
ujung box sebagai diafragma, supaya reaksi tumpuan masuk ke box.

### Kalibrasi ukuran
Gambar DETAIL vektor skala 1:30. Kalibrasi memakai lebar hanger A80-H16:
tergambar 23,5 pt; 23,5 x 0,3528 x 30 = **248,6 mm** terhadap 250 mm
sebenarnya -> 1 pt = 10,584 mm, 1:30 tepat. **Tebal pelat TEPAT** (MATERIAL
LIST); panjang/lebar teliti sekitar +-1%.

## BELUM termasuk
- **Beban gempa** - lokasi jembatan belum diketahui, jadi tidak dibuat-buat.
- **Plat buhul sebagai elemen shell** - material list memberi tebal (PL20)
  tetapi tidak memberi outline, jadi belum bisa dimodelkan setia.

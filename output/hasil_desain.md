# Output Desain Profil WB – SM490YB

## A. Jembatan Rangka Baja STA 0+750 (L = 60 m)

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

## B. Jembatan Fly Over Girder Komposit STA 0+050 (L = 30.6 m)

6 girder @ 1.7 m, slab 250 mm fc' 30 MPa. DF Scania = 0.482. Mu (SNI D) = 4798 kNm, Mu LL Scania = 4857 kNm, Mu total = 8032 kNm, Vu = 1488 kN, M konstruksi = 3017 kNm.

| Frame Code | Elemen | Keterangan | L (m) | Mu (kNm) | Vu (kN) | Profil | kg/m | UR |
|---|---|---|---|---|---|---|---|---|
| GR-1 | Main Girder (composite, interior & exterior) | G1..G6 @ 1.7 m | 30.60 | 8032 | 1488 | WB 1700x300/350x12x16/20 | 249.4 | 0.95 |
| DF-1 | Diaphragm / Cross Beam | 7 lines x 5 bays (@~5.1 m) | 1.70 | 150 | 0 | WB 600x200x9x12 | 78.4 | 0.21 |
| LB-1 | Lateral Bracing (erection) | bottom flange X | 5.38 | 0 | 0 | WB 200x200x8x12 | 48.7 | 0.30 |

Notasi WB d x bf x tw x tf (mm); girder: WB d x bf_atas/bf_bawah x tw x tf_atas/tf_bawah.
Tebal pelat hanya dari stok pasar Indonesia: [8, 9, 10, 12, 14, 16, 19, 20, 22, 25, 28, 30, 32, 36, 40, 45, 50] mm.

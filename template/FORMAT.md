# Format Baku Laporan PT. Indo Trans BajaUtama

Sumber: `Format_laporan_mandiri.docx` (dikirim user 13 Nov 2026).
Dipakai sebagai **format default** setiap kali diminta membuat laporan "versi Indo Trans".

## Aset
| Berkas | Isi |
|---|---|
| `assets/kop_header.png` | Logo PT Indo Trans BajaUtama (header, semua halaman) |
| `assets/footer_band.jpeg` | Logo akreditasi SSI + KAN LSSM-075-IDN (footer) |
| `assets/footer_ico1-3.png` | Ikon telepon / email / web |

## Spesifikasi
| Item | Nilai |
|---|---|
| Ukuran halaman | A4 (21,0 × 29,7 cm) |
| Margin | atas 2,5 / bawah 2,5 / kiri 1,2 / kanan 1,2 cm |
| Font isi | Calibri 11 pt, spasi 1,15, justify |
| Heading 1 | 16 pt tebal, warna `#365F91` |
| Heading 2 | 13 pt tebal, warna `#365F91` |
| Heading 3 | 13 pt tebal, hitam |
| Penomoran bab | Angka Arab: `1. PENDAHULUAN`, `2.1 Geometri` (BUKAN angka Romawi) |
| Header tiap halaman | Logo perusahaan, rata tengah, lebar 10 cm |
| Footer tiap halaman | Logo SSI/KAN + 4 baris alamat, 8 pt abu-abu |
| Tabel | `Table Grid`, baris judul biru `#365F91` teks putih, baris genap `#F2F2F2` |
| Status AMAN/OK | tebal, hijau `#007000` |

## Alamat footer (tetap)
```
Ruko Emerald Blok UG No. 05, Jl. Boulevard Selatan Summarecon Bekasi
Jawa Barat, Indonesia
0813-6176-0253      021-5030-1071
info@indotransbajautama.com      www.indotransbajautama.com
```

## Susunan laporan
1. Judul + sub-judul (rata tengah, tanpa halaman sampul terpisah)
2. Tabel identitas: Proyek / Pekerjaan / Kontraktor / Konsultan MK / Peraturan acuan / Status
3. `1. PENDAHULUAN`
4. `2. DATA PERENCANAAN` — 2.1 Geometri, 2.2 Material dan properti penampang, 2.3 Asumsi
5. Bab-bab perhitungan sesuai lingkup
6. Bab terakhir: `KESIMPULAN DAN REKOMENDASI` (butir bernomor)
7. Blok tanda tangan

## Gaya penulisan perhitungan
Tiap langkah satu baris, pola **rumus = substitusi angka = hasil + satuan**, indent 0,5 cm:
```
Beban puncak qp = q x lx / 2
qp(D) = 4,09 x 1,625 / 2 = 3,323 kN/m
Mu = wu x L^2 / 8 = 9,49 x 2,9^2 / 8 = 9,98 kNm
```
Desimal pakai **koma**, ribuan pakai **titik**. Sertakan rujukan pasal SNI/AISC bila ada.

## Cara pakai
```python
import sys; sys.path.insert(0, "template")
from itb_format import ITBReport
r = ITBReport("LAPORAN PERHITUNGAN STRUKTUR", "Nama Proyek", "November 2026")
r.identitas({...}); r.h1("1. PENDAHULUAN"); r.p("..."); r.rumus("..."); r.tabel([...], [...])
r.gambar("foto.png", "keterangan"); r.kotak("KESIMPULAN", "..."); r.ttd(bulan="November 2026")
r.save("out/laporan.docx")
```

# Preferensi Proyek

## Laporan "versi Indo Trans"

Jika user minta dibuatkan laporan **versi Indo Trans** (atau menyebut PT Indo Trans
BajaUtama), gunakan format baku di `template/` sebagai **default** tanpa perlu ditanya:

- Baca `template/FORMAT.md` untuk spesifikasi lengkap.
- Pakai modul `template/itb_format.py` (kelas `ITBReport`) untuk membangun dokumennya.
- Logo kop dan logo akreditasi ada di `template/assets/`.

Ringkas: A4, margin 2,5/2,5/1,2/1,2 cm, Calibri 11 pt, Heading warna `#365F91`,
penomoran bab angka Arab (`1.`, `2.1`), kop logo di header tiap halaman, footer
alamat + logo SSI/KAN, tabel header biru teks putih.

Hasil akhir disimpan di `out/` dan dikirim ke user sebagai file .docx.

## Ketentuan teknis proyek PT Indo Trans BajaUtama

- **Mutu beton: K-250 (f'c = 21 MPa) untuk SELURUH elemen beton**, termasuk bore pile,
  balok praktis, kolom praktis dan pile cap. Tidak ada mutu lain.
- Mutu baja: SS400 (fy = 235 MPa); sebagian member A36 (fy = 248 MPa).
- Tulangan: BjTS 420A (fy = 420 MPa), sengkang BjTP 280 (fyt = 280 MPa).
- Acuan: SNI 1726:2019, SNI 1727:2020, SNI 2847:2019, SNI 1729:2020,
  SNI 8460:2017, EN 1993-1:2022.
- Angka: desimal pakai koma, ribuan pakai titik.

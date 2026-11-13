# -*- coding: utf-8 -*-
"""
Pembangun laporan PT. INDO TRANS BAJAUTAMA berbasis TEMPLATE_ITB.docx.

Berbeda dengan pendekatan membangun dokumen dari nol, modul ini MEMBUKA berkas
template asli lalu HANYA MENGGANTI ISINYA. Dengan demikian cover, kop header,
footer (alamat + logo SSI/KAN), gaya paragraf dan penomoran template tetap utuh
persis seperti aslinya.

Struktur body template:
    [0] sdt  -> HALAMAN COVER (2 gambar + page break)   <- dipertahankan, teks diganti
    [1] p    -> judul
    [2] p    -> sub-judul
    [3] tbl  -> tabel identitas proyek                   <- dipertahankan, baris diganti
    [4..]    -> isi laporan                              <- dihapus, diisi ulang
"""
import os, copy
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "TEMPLATE_ITB.docx")
W        = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BIRU     = RGBColor(0x36, 0x5F, 0x91)


def _shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), hexc)
    tcPr.append(sh)


class ITBDoc:
    """Laporan Indo Trans berbasis template asli."""

    def __init__(self, judul, subjudul):
        self.doc = Document(TEMPLATE)
        self.body = self.doc.element.body
        self._nfig = 0
        self._ntab = 0
        self._ganti_cover(judul, subjudul)
        self._ambil_tabel_identitas()
        self._kosongkan_isi()

    # ---------- cover: ganti teks, pertahankan gambar & tata letak ----------
    def _ganti_cover(self, judul, subjudul):
        sdt = list(self.body)[0]
        teks = list(sdt.iter(W + "t"))
        # pola template: [judul, 'Struktur', ' Baja Lift Gedung D'] x 2
        for i in range(0, len(teks), 3):
            blok = teks[i:i + 3]
            if len(blok) == 3:
                blok[0].text = judul
                blok[1].text = subjudul
                blok[2].text = ""
        # judul & sub-judul di halaman isi (elemen [1] dan [2])
        kids = list(self.body)
        for el, isi in ((kids[1], judul), (kids[2], subjudul)):
            runs = list(el.iter(W + "t"))
            if runs:
                runs[0].text = isi
                for r in runs[1:]:
                    r.text = ""

    # ---------- simpan referensi tabel identitas ----------
    def _ambil_tabel_identitas(self):
        self._tbl_identitas = None
        for t in self.doc.tables:
            if t.rows and t.rows[0].cells[0].text.strip().lower() == "proyek":
                self._tbl_identitas = t
                break

    # ---------- hapus isi lama (sisakan cover, judul, tabel identitas) ----------
    def _kosongkan_isi(self):
        kids = list(self.body)
        sectPr = kids[-1] if kids[-1].tag == W + "sectPr" else None
        tbl_el = self._tbl_identitas._tbl if self._tbl_identitas is not None else None
        simpan = {id(kids[0]), id(kids[1]), id(kids[2])}
        if tbl_el is not None:
            simpan.add(id(tbl_el))
        if sectPr is not None:
            simpan.add(id(sectPr))
        for el in kids:
            if id(el) not in simpan:
                self.body.remove(el)
        self._sectPr = sectPr

    # ---------- sisip elemen baru sebelum sectPr ----------
    def _tambah_p(self):
        p = OxmlElement("w:p")
        if self._sectPr is not None:
            self._sectPr.addprevious(p)
        else:
            self.body.append(p)
        from docx.text.paragraph import Paragraph
        return Paragraph(p, self.doc)

    def _tambah_tbl(self, rows, cols):
        t = self.doc.add_table(rows=rows, cols=cols)
        if self._sectPr is not None:
            self._sectPr.addprevious(t._tbl)
        return t

    # ---------- tabel identitas: isi ulang ----------
    def identitas(self, data: dict):
        t = self._tbl_identitas
        if t is None:
            return
        # hapus semua baris lama
        for row in list(t.rows):
            t._tbl.remove(row._tr)
        for k, v in data.items():
            c = t.add_row().cells
            c[0].text = ""; c[1].text = ""
            r0 = c[0].paragraphs[0].add_run(k); r0.bold = True; r0.font.size = Pt(10)
            c[1].paragraphs[0].add_run(str(v)).font.size = Pt(10)
            c[0].width = Cm(4.5); c[1].width = Cm(13.5)
            _shade(c[0], "DCE6F1")

    # ---------- heading memakai STYLE TEMPLATE ----------
    def h1(self, txt):
        p = self._tambah_p(); p.style = self.doc.styles["Heading 1"]
        p.add_run(txt)
        return p

    def h2(self, txt):
        p = self._tambah_p(); p.style = self.doc.styles["Heading 2"]
        p.add_run(txt)
        return p

    def h3(self, txt):
        p = self._tambah_p(); p.style = self.doc.styles["Heading 3"]
        p.add_run(txt)
        return p

    # ---------- teks ----------
    def p(self, txt, justify=True, bold=False, size=11):
        par = self._tambah_p()
        if justify:
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = par.add_run(txt); r.bold = bold; r.font.size = Pt(size)
        return par

    def rumus(self, txt, bold=False):
        par = self._tambah_p()
        par.paragraph_format.left_indent = Cm(0.5)
        par.paragraph_format.space_after = Pt(2)
        r = par.add_run(txt); r.bold = bold; r.font.size = Pt(11)
        return par

    def poin(self, items, nomor=False):
        for it in items:
            par = self._tambah_p()
            par.style = self.doc.styles["List Paragraph"]
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            par.paragraph_format.left_indent = Cm(0.8)
            par.paragraph_format.space_after = Pt(3)
            par.add_run(("•  " if not nomor else "") + it).font.size = Pt(11)

    def poin_nomor(self, items, awal=1):
        for n, it in enumerate(items, awal):
            par = self._tambah_p()
            par.style = self.doc.styles["List Paragraph"]
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            par.paragraph_format.left_indent = Cm(0.8)
            par.paragraph_format.space_after = Pt(3)
            par.add_run("%d.  %s" % (n, it)).font.size = Pt(11)

    # ---------- tabel ----------
    def tabel(self, header, rows, widths=None, judul=None, fs=10):
        if judul:
            self._ntab += 1
            c = self._tambah_p(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = c.add_run("Tabel %d. %s" % (self._ntab, judul))
            r.italic = True; r.font.size = Pt(9)
            c.paragraph_format.space_before = Pt(8); c.paragraph_format.space_after = Pt(3)
        t = self._tambah_tbl(1, len(header))
        t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
        hc = t.rows[0].cells
        for i, h in enumerate(header):
            hc[i].text = ""
            p = hc[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(h)); r.bold = True; r.font.size = Pt(fs)
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            _shade(hc[i], "365F91")
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                p = cells[i].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
                txt = str(v)
                r = p.add_run(txt); r.font.size = Pt(fs)
                if txt in ("AMAN", "OK", "MEMENUHI"):
                    r.bold = True; r.font.color.rgb = RGBColor(0x00, 0x70, 0x00)
            if ri % 2 == 1:
                for c in cells:
                    _shade(c, "F2F2F2")
        if widths:
            for i, w in enumerate(widths):
                for row in t.rows:
                    row.cells[i].width = Cm(w)
        self._tambah_p()
        return t

    # ---------- gambar ----------
    def gambar(self, path, keterangan, width=15.5):
        p = self._tambah_p(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(path, width=Cm(width))
        self._nfig += 1
        c = self._tambah_p(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run("Gambar %d. %s" % (self._nfig, keterangan))
        r.italic = True; r.font.size = Pt(9)
        c.paragraph_format.space_after = Pt(10)

    # ---------- kotak kesimpulan ----------
    def kotak(self, judul, isi, fill="E8F3E8", warna=RGBColor(0x00, 0x70, 0x00)):
        t = self._tambah_tbl(1, 1); t.style = "Table Grid"
        c = t.rows[0].cells[0]; _shade(c, fill); c.text = ""
        p = c.paragraphs[0]
        r = p.add_run(judul); r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = warna
        p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p2.add_run(isi).font.size = Pt(10)
        self._tambah_p()

    def catatan(self, judul, isi):
        self.kotak(judul, isi, fill="FFF2CC", warna=RGBColor(0xBF, 0x8F, 0x00))

    # ---------- tanda tangan ----------
    def ttd(self, kota="Bekasi", bulan="November 2026",
            kiri=("Disusun oleh,", "Engineer Struktur"),
            kanan=("Disetujui oleh,", "Manager Engineering")):
        self._tambah_p(); self._tambah_p()
        t = self._tambah_tbl(1, 2)
        for i, (ttl, nm) in enumerate([kiri, kanan]):
            c = t.rows[0].cells[i]; c.text = ""
            baris = ["%s, %s" % (kota, bulan), ttl, "PT. Indo Trans BajaUtama",
                     "(.............................................)", nm]
            for j, txt in enumerate(baris):
                p = c.paragraphs[0] if j == 0 else c.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(txt); r.bold = (j == 4); r.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(40 if j == 2 else 0)

    def page_break(self):
        from docx.enum.text import WD_BREAK
        p = self._tambah_p()
        p.add_run().add_break(WD_BREAK.PAGE)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.doc.save(path)
        return path

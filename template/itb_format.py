# -*- coding: utf-8 -*-
"""
FORMAT DEFAULT LAPORAN PT. INDO TRANS BAJAUTAMA
===============================================
Modul ini mereplikasi "Format_laporan_mandiri.docx" sebagai format baku.
Dipakai setiap kali diminta membuat laporan "versi Indo Trans".

Pemakaian:
    from itb_format import ITBReport
    r = ITBReport("LAPORAN PERHITUNGAN STRUKTUR", "Sub-judul proyek")
    r.identitas({"Proyek": "...", "Pekerjaan": "...", "Status": "FINAL"})
    r.h1("1. PENDAHULUAN"); r.p("...")
    r.h2("2.1 Geometri"); r.rumus("Mu = w L^2 / 8 = 9,49 x 2,9^2 / 8 = 9,98 kNm")
    r.tabel(["Parameter","Nilai","Sumber"], [[...]])
    r.gambar("foto.png", "Keterangan gambar")
    r.poin(["butir 1","butir 2"])
    r.save("out.docx")
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# --- Konstanta format (diambil persis dari Format_laporan_mandiri.docx) ---
BIRU        = RGBColor(0x36, 0x5F, 0x91)   # warna Heading 1 & 2
FONT        = "Calibri"
SZ_BODY     = 11.0
SZ_H1       = 16.0
SZ_H2       = 13.0
SZ_H3       = 13.0
MARGIN      = dict(top=2.5, bottom=2.5, left=1.2, right=1.2)   # cm
ALAMAT = [
    "Ruko Emerald Blok UG No. 05, Jl. Boulevard Selatan Summarecon Bekasi",
    "Jawa Barat, Indonesia",
    "0813-6176-0253      021-5030-1071",
    "info@indotransbajautama.com      www.indotransbajautama.com",
]


def _shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), hexc)
    tcPr.append(sh)


class ITBReport:
    def __init__(self, judul, subjudul="", tanggal=""):
        self.doc = Document()
        self._setup()
        self._kop()
        self._footer()
        self._judul(judul, subjudul, tanggal)
        self._nfig = 0
        self._ntab = 0

    # ---------- setup halaman & style ----------
    def _setup(self):
        s = self.doc.styles["Normal"]
        s.font.name = FONT
        s.font.size = Pt(SZ_BODY)
        s.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        pf = s.paragraph_format
        pf.space_after = Pt(6); pf.line_spacing = 1.15
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.top_margin    = Cm(MARGIN["top"])
        sec.bottom_margin = Cm(MARGIN["bottom"])
        sec.left_margin   = Cm(MARGIN["left"])
        sec.right_margin  = Cm(MARGIN["right"])
        self.sec = sec

    # ---------- kop (logo di header, semua halaman) ----------
    def _kop(self):
        p = self.sec.header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        logo = os.path.join(ASSETS, "kop_header.png")
        if os.path.exists(logo):
            p.add_run().add_picture(logo, width=Cm(10.0))
        else:
            r = p.add_run("PT. INDO TRANS BAJAUTAMA")
            r.bold = True; r.font.size = Pt(18); r.font.color.rgb = BIRU
        p.paragraph_format.space_after = Pt(2)

    # ---------- footer: alamat + logo akreditasi SSI/KAN ----------
    def _footer(self):
        f = self.sec.footer
        band = os.path.join(ASSETS, "footer_band.jpeg")
        if os.path.exists(band):
            p0 = f.paragraphs[0]; p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p0.add_run().add_picture(band, width=Cm(4.5))
            p0.paragraph_format.space_after = Pt(2)
            first = False
        else:
            first = True
        for i, line in enumerate(ALAMAT):
            p = f.paragraphs[0] if (first and i == 0) else f.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(line)
            r.font.size = Pt(8); r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
            p.paragraph_format.space_after = Pt(0)

    # ---------- judul laporan ----------
    def _judul(self, judul, subjudul, tanggal):
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(judul); r.bold = True; r.font.size = Pt(16)
        if subjudul:
            q = self.doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rr = q.add_run(subjudul); rr.bold = True; rr.font.size = Pt(13)
        if tanggal:
            t = self.doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
            t.add_run(tanggal).font.size = Pt(10)

    # ---------- blok identitas proyek ----------
    def identitas(self, data: dict):
        t = self.doc.add_table(rows=0, cols=2); t.style = "Table Grid"
        for k, v in data.items():
            c = t.add_row().cells
            c[0].text = ""; c[1].text = ""
            r0 = c[0].paragraphs[0].add_run(k); r0.bold = True; r0.font.size = Pt(10)
            c[1].paragraphs[0].add_run(str(v)).font.size = Pt(10)
            c[0].width = Cm(4.5); c[1].width = Cm(13.5)
            _shade(c[0], "DCE6F1")
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    # ---------- heading ----------
    def h1(self, txt):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
        r = p.add_run(txt); r.bold = True; r.font.size = Pt(SZ_H1); r.font.color.rgb = BIRU
        return p

    def h2(self, txt):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
        r = p.add_run(txt); r.bold = True; r.font.size = Pt(SZ_H2); r.font.color.rgb = BIRU
        return p

    def h3(self, txt):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
        r = p.add_run(txt); r.bold = True; r.font.size = Pt(SZ_H3)
        return p

    # ---------- teks ----------
    def p(self, txt, justify=True, bold=False, size=SZ_BODY):
        par = self.doc.add_paragraph()
        if justify: par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = par.add_run(txt); r.bold = bold; r.font.size = Pt(size)
        return par

    def rumus(self, txt, bold=False):
        """Baris perhitungan: rumus = substitusi = hasil (rata kiri, tanpa justify)."""
        par = self.doc.add_paragraph()
        par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.left_indent = Cm(0.5)
        r = par.add_run(txt); r.bold = bold; r.font.size = Pt(SZ_BODY)
        return par

    def poin(self, items, nomor=False):
        for it in items:
            par = self.doc.add_paragraph(style="List Number" if nomor else "List Bullet")
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            par.paragraph_format.space_after = Pt(2)
            par.add_run(it).font.size = Pt(SZ_BODY)

    # ---------- tabel ----------
    def tabel(self, header, rows, widths=None, judul=None, fs=10, hijau_aman=True):
        if judul:
            self._ntab += 1
            c = self.doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = c.add_run("Tabel %d. %s" % (self._ntab, judul))
            r.italic = True; r.font.size = Pt(9)
            c.paragraph_format.space_before = Pt(8); c.paragraph_format.space_after = Pt(3)
        t = self.doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
        hc = t.rows[0].cells
        for i, htxt in enumerate(header):
            hc[i].text = ""
            p = hc[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(htxt)); r.bold = True; r.font.size = Pt(fs)
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
                if hijau_aman and txt in ("AMAN", "OK", "MEMENUHI"):
                    r.bold = True; r.font.color.rgb = RGBColor(0x00, 0x70, 0x00)
            if ri % 2 == 1:
                for c in cells: _shade(c, "F2F2F2")
        if widths:
            for i, w in enumerate(widths):
                for row in t.rows: row.cells[i].width = Cm(w)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    # ---------- gambar ----------
    def gambar(self, path, keterangan, width=15.5):
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(path, width=Cm(width))
        self._nfig += 1
        c = self.doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run("Gambar %d. %s" % (self._nfig, keterangan))
        r.italic = True; r.font.size = Pt(9)
        c.paragraph_format.space_after = Pt(10)

    # ---------- kotak kesimpulan ----------
    def kotak(self, judul, isi, fill="E8F3E8", warna=RGBColor(0x00, 0x70, 0x00)):
        t = self.doc.add_table(rows=1, cols=1); t.style = "Table Grid"
        c = t.rows[0].cells[0]; _shade(c, fill); c.text = ""
        p = c.paragraphs[0]; r = p.add_run(judul)
        r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = warna
        p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p2.add_run(isi).font.size = Pt(10)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def catatan(self, judul, isi):
        self.kotak(judul, isi, fill="FFF2CC", warna=RGBColor(0xBF, 0x8F, 0x00))

    # ---------- tanda tangan ----------
    def ttd(self, kota="Bekasi", bulan="", kiri=("Disusun oleh,", "Engineer Struktur"),
            kanan=("Disetujui oleh,", "Manager Engineering")):
        self.doc.add_paragraph(); self.doc.add_paragraph()
        t = self.doc.add_table(rows=1, cols=2)
        for i, (ttl, nm) in enumerate([kiri, kanan]):
            c = t.rows[0].cells[i]; c.text = ""
            baris = ["%s, %s" % (kota, bulan), ttl, "PT. Indo Trans BajaUtama", "", "", nm]
            for j, txt in enumerate(baris):
                p = c.paragraphs[0] if j == 0 else c.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(txt if txt else "(.............................................)"
                              if j == 4 else txt)
                r.bold = (j == 5); r.font.size = Pt(10)
                p.paragraph_format.space_after = Pt(0 if j != 2 else 40)

    def page_break(self):
        self.doc.add_page_break()

    def save(self, path):
        self.doc.save(path)
        return path

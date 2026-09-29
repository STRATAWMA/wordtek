const fs = require("fs");
const path = require("path");
const D = require("./data.json");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, PageBreak, TableOfContents, Header, Footer, PageNumber,
  ImageRun, PageOrientation, BorderStyle, LevelFormat,
} = require("docx");
const DIR = __dirname;
const F = "Arial";
const W = 9638; // A4 text width (2 cm margins)

const P = (t, o = {}) => new Paragraph({ spacing: { after: 100, line: 300 }, alignment: o.align || AlignmentType.JUSTIFIED,
  children: [].concat(t).map(x => typeof x === "string" ? new TextRun({ text: x, font: F, size: o.size || 22, bold: o.bold, italics: o.it }) : x) });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: { after: 200 }, children: [new TextRun({ text: t, font: F })] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 120 }, children: [new TextRun({ text: t, font: F })] });
const H3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 160, after: 80 }, children: [new TextRun({ text: t, font: F })] });
const B = t => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: t, font: F, size: 22 })] });
const EQ = t => new Paragraph({ indent: { left: 567 }, spacing: { after: 60 }, children: [new TextRun({ text: t, font: "Cambria Math", size: 21 })] });
const bd = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };

function table(head, rows, widths, fs = 17) {
  const tot = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, h) => new TableCell({ borders, width: { size: widths[i], type: WidthType.DXA },
    shading: h ? { fill: "1F3864", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ alignment: i === 0 && !h ? AlignmentType.LEFT : AlignmentType.CENTER,
      children: [new TextRun({ text: String(t), font: F, size: fs, bold: h, color: h ? "FFFFFF" : undefined })] })] });
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: head.map((t, i) => cell(t, i, true)) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) => cell(t, i, false)) }))] });
}
const cap = t => P(t, { align: AlignmentType.CENTER, size: 18, bold: true });
const img = (f, w, h) => new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(DIR, f)), transformation: { width: w, height: h } })] });
const f0 = x => Number(x).toLocaleString("id-ID", { maximumFractionDigits: 0 });
const f2 = x => Number(x).toLocaleString("id-ID", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const I = D.info, G = D.ginfo;
// ---------------------------------------------------------------- content
const c = [];
// cover
c.push(new Paragraph({ spacing: { before: 1800 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PT INDO TRANS", font: F, size: 40, bold: true, color: "1F3864" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: "1F3864", space: 4 } }, spacing: { after: 600 }, children: [new TextRun({ text: "Structural Engineering Division", font: F, size: 22, italics: true })] }));
c.push(P("LAPORAN PERHITUNGAN STRUKTUR", { align: AlignmentType.CENTER, size: 36, bold: true }));
c.push(P("PRE-DESIGN PROFIL WELDED BEAM (WB) SM490YB", { align: AlignmentType.CENTER, size: 28, bold: true }));
c.push(P("JEMBATAN RANGKA BAJA L = 60 m (ROAD-4 STA 0+750)", { align: AlignmentType.CENTER, size: 24 }));
c.push(P("JEMBATAN FLY OVER GIRDER KOMPOSIT L = 30,6 m (ROAD-4 STA 0+050)", { align: AlignmentType.CENTER, size: 24 }));
c.push(new Paragraph({ spacing: { before: 1200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Proyek: Pengembangan Infrastruktur Tambang Sangaji", font: F, size: 22 })] }));
c.push(P("Pemilik: PT Sumber Daya Arindo (PT SDA)", { align: AlignmentType.CENTER }));
c.push(P("No. Dokumen: IT-STR-CAL-R4-001  |  Revisi: A (Pre-Design)  |  September 2026", { align: AlignmentType.CENTER, size: 20 }));
// approval sheet
c.push(new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new TextRun({ text: "LEMBAR PENGESAHAN & RIWAYAT REVISI", font: F, size: 28, bold: true })] }));
c.push(table(["Rev", "Tanggal", "Keterangan", "Dibuat", "Diperiksa", "Disetujui"],
  [["A", "29-09-2026", "Pre-design untuk review internal", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
  [700, 1400, 3138, 1466, 1466, 1468], 18));
c.push(P(""));
c.push(P("Catatan: Dokumen ini merupakan perhitungan awal (pre-design). Seluruh profil wajib diverifikasi dengan model 3D (SAP2000/MIDAS Civil) beserta pengecekan fatik dan sambungan sebelum diterbitkan untuk konstruksi (IFC).", { it: true, size: 20 }));
// TOC
c.push(new Paragraph({ pageBreakBefore: true, children: [new TextRun({ text: "DAFTAR ISI", font: F, size: 28, bold: true })] }));
c.push(new TableOfContents("Daftar Isi", { hyperlink: true, headingStyleRange: "1-2" }));

// BAB 1
c.push(H1("BAB 1  PENDAHULUAN"));
c.push(H2("1.1  Latar Belakang"));
c.push(P("PT Sumber Daya Arindo (PT SDA) sedang mengembangkan jalan tambang Road-4 yang memerlukan dua jembatan: jembatan rangka baja bentang 60 m di STA 0+750 dan jembatan fly over girder baja komposit bentang 30,6 m di STA 0+050. Laporan ini menyajikan perhitungan awal dimensi seluruh elemen baja memakai profil tersusun las (Welded Beam, WB) mutu JIS G3106 SM490YB. Tebal pelat dipilih hanya dari ukuran yang tersedia di pasar Indonesia."));
c.push(H2("1.2  Maksud dan Tujuan"));
["Menentukan gaya dalam batang rangka dan girder akibat beban mati dan beban hidup sesuai persyaratan klien.",
 "Menentukan profil WB yang optimal (rasio kapasitas UR ≤ 0,95) untuk setiap kode frame: Bottom Chord, Top Chord, End Chord, Diagonal Chord, Brace, Diagonal Member, Stringer, Cross Girder, Girder, dan Diafragma.",
 "Menyediakan tabel kode frame dan profil sebagai input model struktur 3D serta gambar kerja."].forEach(t => c.push(B(t)));
c.push(H2("1.3  Lingkup Pekerjaan"));
c.push(table(["Uraian", "Jembatan Rangka Baja", "Jembatan Fly Over"], [
  ["Lokasi", "Road-4 STA 0+750", "Road-4 STA 0+050"], ["Tipe", "Rangka Warren, lantai bawah", "Girder I baja komposit"],
  ["Bentang", "60,0 m (12 panel @ 5,0 m)", "30,6 m (as-abutmen 30,8 m)"], ["Lebar", "11,0 m (2 × 5,0 m + 2 × 0,5 m)", "11,0 m (2 × 3,5 m + 2 × 1,5 m + 2 × 0,5 m)"],
  ["Tinggi struktur", "6,0 m (as ke as chord)", "H = 1,7 m, 6 girder @ 1,7 m"], ["Lantai", "Pelat beton t = 250 mm", "Pelat beton t = 250 mm"],
  ["Pondasi (info)", "3×7 bored pile Ø800, L = 30 m", "3×4 bored pile Ø800, L = 12 m / 22 m"]], [2600, 3519, 3519]));
c.push(cap("Tabel 1.1  Data umum jembatan (sumber: gambar klien F.1-02 s/d F.1-07 dan F.2-02 s/d F.2-07)"));

// BAB 2
c.push(H1("BAB 2  STANDAR, KRITERIA DESAIN DAN MATERIAL"));
c.push(H2("2.1  Standar Acuan"));
["SNI 1725:2016 – Pembebanan untuk Jembatan", "SNI 1729:2020 – Spesifikasi untuk Bangunan Gedung Baja Struktural (setara AISC 360-16, metode LRFD)",
 "SNI T-12-2004 – Perencanaan Struktur Beton untuk Jembatan", "RSNI T-03-2005 – Perencanaan Struktur Baja untuk Jembatan",
 "AASHTO LRFD Bridge Design Specifications (acuan pelengkap: faktor distribusi dan batas kelangsingan)",
 "Surat Edaran Dirjen Bina Marga No. 07/SE/Db/2025 – Spesifikasi Umum 2025, Seksi 7.4 Baja Struktur",
 "Ketentuan Teknis PT SDA butir 3.2.2.2.1 s/d 3.2.2.2.5, 3.2.2.3 dan 4.4.3"].forEach(t => c.push(B(t)));
c.push(H2("2.2  Persyaratan Klien"));
c.push(table(["No", "Butir", "Persyaratan", "Penerapan dalam laporan"], [
  ["1", "3.2.2.2.1", "Beban rencana mengacu SNI 1725-2016", "Beban lajur D (BTR + BGT) dan truk T"],
  ["2", "3.2.2.2.2", "Hauling truck 40 t; kendaraan operasional Scania P410 B8x4 58 t", "Konvoi Scania 58 t dianalisis dan dibandingkan dengan beban D; diambil yang terbesar"],
  ["3", "3.2.2.2.4", "Baja struktur utama JIS SM490/BJ50; sekunder A36; baut F10T; las E70XX", "Seluruh profil WB memakai SM490YB (lebih tinggi dari syarat minimum)"],
  ["4", "3.2.2.2.5", "Kombinasi beban sesuai SNI 1725, SNI T-12, RSNI T-03", "Kombinasi Kuat I dan layan"],
  ["5", "4.4.3", "SE 07/2025 Seksi 7.4; toleransi Pasal 1.4; pre-approval & approval material; uji 3 spesimen per tebal pelat per supplier", "Daftar tebal pelat untuk uji disajikan pada Bab 7"]],
  [500, 1100, 3900, 4138]));
c.push(cap("Tabel 2.1  Rekapitulasi persyaratan klien"));
c.push(H2("2.3  Material"));
c.push(table(["Material", "Spesifikasi", "Nilai"], [
  ["Baja profil WB", "JIS G3106 SM490YB", "Fu = 490 MPa; Fy = 365 MPa (t ≤ 16), 355 MPa (16 < t ≤ 40), 335 MPa (40 < t ≤ 50)"],
  ["Modulus elastisitas", "-", "E = 200.000 MPa"], ["Beton pelat lantai", "fc' 30 MPa", "Ec = 25.743 MPa; n = 8"],
  ["Tulangan", "BJTD-420", "fy = 420 MPa"], ["Baut", "F10T (setara A490)", "Fu = 1.000 MPa"], ["Las", "E70XX", "FEXX = 490 MPa"]], [2400, 2600, 4638]));
c.push(cap("Tabel 2.2  Properti material"));
c.push(H2("2.4  Ketersediaan Tebal Pelat di Pasar Indonesia"));
c.push(P("Tebal pelat dibatasi pada ukuran yang umum diproduksi dan distok oleh PT Krakatau Posco, PT Gunung Raja Paksi, dan distributor baja nasional: 8, 9, 10, 12, 14, 16, 19, 20, 22, 25, 28, 30, 32, 36, 40, 45, dan 50 mm. Lebar pelat induk yang umum tersedia adalah 1.524 mm, 1.829 mm, dan 2.438 mm, sehingga seluruh flens dan web dapat dipotong dengan sisa minimum."));
c.push(H2("2.5  Faktor Beban dan Tahanan"));
c.push(table(["Beban / Tahanan", "Simbol", "Faktor"], [
  ["Berat sendiri baja", "MS", "1,10"], ["Berat sendiri beton / barrier", "MS", "1,30"], ["Beban mati tambahan (aspal)", "MA", "2,00"],
  ["Beban lajur D / truk", "TD / TT", "1,80"], ["Tahanan tekan", "φc", "0,90"], ["Tahanan tarik leleh / putus", "φt", "0,90 / 0,75"],
  ["Tahanan lentur", "φb", "0,90"], ["Tahanan geser", "φv", "0,90"]], [4638, 2000, 3000]));
c.push(cap("Tabel 2.3  Faktor beban (SNI 1725:2016) dan faktor tahanan (SNI 1729:2020)"));
c.push(H2("2.6  Batasan Desain"));
["Rasio kapasitas (UR) maksimum 0,95 (cadangan 5% untuk ketidakpastian analisis 2D).",
 "Kelangsingan KL/r ≤ 120 untuk batang tekan utama, ≤ 140 untuk bracing, dan L/r ≤ 200 untuk batang tarik.",
 "Semua elemen tekan dirancang non-langsing: λf = bf/2tf ≤ 0,56√(E/Fy) dan λw = h/tw ≤ 1,49√(E/Fy).",
 "Seluruh batang rangka utama memakai tinggi d = 500 mm yang seragam agar dapat masuk di antara pelat buhul.",
 "Lendutan girder akibat beban hidup ≤ L/800."].forEach(t => c.push(B(t)));

// BAB 3
c.push(H1("BAB 3  PEMBEBANAN"));
c.push(H2("3.1  Beban Mati (MS)"));
c.push(table(["Komponen", "Rangka 60 m (seluruh jembatan)", "Girder 30,6 m (per girder)"], [
  ["Pelat beton t = 250 mm", "0,25 × 11,0 × 24 = 66,0 kN/m", "0,25 × 1,7 × 24 + haunch = 10,68 kN/m"],
  ["Barrier (2 sisi)", "2 × 6,0 = 12,0 kN/m", "12/6 = 2,0 kN/m"],
  ["Baja struktur (hasil iterasi, +20% sambungan)", `${f2(I.sw)} kN/m`, "5,0 kN/m (asumsi)"],
  ["Aspal t = 50 mm (MA)", "0,05 × 10 × 22 = 11,0 kN/m", "0,05 × 1,7 × 22 = 1,87 kN/m"]], [3200, 3219, 3219]));
c.push(cap("Tabel 3.1  Beban mati"));
c.push(H2("3.2  Beban Lajur D (SNI 1725:2016)"));
c.push(EQ("BTR: q = 9,0 kPa untuk L ≤ 30 m; q = 9,0 (0,5 + 15/L) kPa untuk L > 30 m"));
c.push(EQ(`L = 60 m → q = ${f2(I.q)} kPa;   L = 30,6 m → q = ${f2(G.q)} kPa`));
c.push(EQ("BGT: p = 49,0 kN/m, dengan FBD = 0,40 (L ≤ 50 m) atau 0,40 – 0,0025(L – 50)"));
c.push(EQ(`FBD: L = 60 m → ${I.im};   L = 30,6 m → ${G.im}`));
c.push(P("Beban lajur D ditempatkan penuh pada jalur 10 m. Untuk rangka, setiap rangka memikul setengahnya."));
c.push(H2("3.3  Kendaraan Operasional Scania P410 B8x4 (58 t)"));
c.push(P("Tabel beban gandar dari klien belum tersedia. Konfigurasi gandar di bawah ini diambil dari data tipikal Scania P410 B8x4 dengan GVW 58 t dan harus dikonfirmasi ke PT SDA."));
c.push(table(["Gandar", "1 (steer)", "2 (steer)", "3 (tandem)", "4 (tandem)", "Total"], [
  ["Beban (t)", "7,0", "7,0", "22,0", "22,0", "58,0"], ["Beban (kN)", "68,7", "68,7", "215,8", "215,8", "569,0"],
  ["Jarak ke gandar berikut (m)", "1,95", "3,10", "1,37", "-", "6,42"]], [2638, 1400, 1400, 1400, 1400, 1400]));
c.push(cap("Tabel 3.2  Konfigurasi gandar Scania P410 B8x4 (asumsi)"));
["Konvoi truk dengan jarak bersih 10 m (kondisi antre di jalan tambang), dua lajur, sehingga setiap rangka memikul satu lajur.",
 "FBD kendaraan 30%, faktor beban 1,8.",
 `Untuk girder, faktor distribusi dihitung dengan AASHTO 4.6.2.2.2b: DF = 0,075 + (S/2900)^0,6 (S/L)^0,2 = ${G.DF}.`].forEach(t => c.push(B(t)));
c.push(H2("3.4  Beban Lingkungan"));
c.push(P("Beban angin untuk bracing: EW = 0,0012·Cw·Vw²·Ab dengan Vw = 35 m/s dan Cw = 2,0, faktor beban 1,4. Gaya stabilitas bracing diambil sebesar 2% dari gaya tekan top chord. Pengaruh gempa (SNI 2833:2016) tidak termasuk dalam lingkup pre-design ini."));
c.push(H2("3.5  Kombinasi Pembebanan"));
c.push(EQ("Kuat I : 1,1 MS(baja) + 1,3 MS(beton) + 2,0 MA + 1,8 (TD atau TT)"));
c.push(EQ("Layan  : 1,0 MS + 1,0 MA + 1,0 TT(1+FBD)·DF  (untuk lendutan)"));
c.push(EQ("Konstruksi : 1,4 (beton basah + baja) + 1,5 × 1,5 kPa beban pekerja"));

// BAB 4
c.push(H1("BAB 4  ANALISIS STRUKTUR JEMBATAN RANGKA BAJA 60 m"));
c.push(H2("4.1  Geometri dan Model"));
c.push(P(`Rangka tipe Warren tanpa batang vertikal, 12 panel @ ${I.p} m, tinggi ${I.H} m, dan jarak antar rangka ${I.B} m. Panjang diagonal Ld = √(2,5² + 6,0²) = 6,50 m, dengan sudut θ = 67,4°. Beban dari lantai disalurkan oleh stringer ke cross girder di setiap buhul bawah, lalu ke rangka utama. Karena rangka statis tertentu, gaya batang dihitung dengan garis pengaruh:`));
c.push(EQ("Chord: F = M(x_buhul) / h ;   Diagonal: F = ± V(panel) / sin θ"));
c.push(P("Beban hidup (lajur D dan konvoi Scania) digerakkan sepanjang bentang dengan langkah 0,25 m untuk mendapatkan gaya tarik dan tekan maksimum setiap batang. Berat sendiri baja diiterasi sampai konvergen."));
c.push(H2("4.2  Gaya Batang Terfaktor"));
c.push(table(["Batang", "Elemen", "L (m)", "Pu tarik (kN)", "Pu tekan (kN)", "Menentukan"],
  D.members.map(m => [m.code, m.type, f2(m.L), f0(m.Pt), f0(m.Pc), m.gov]), [1300, 2200, 1100, 1700, 1700, 1638], 16));
c.push(cap("Tabel 4.1  Gaya batang terfaktor Kuat I (per rangka)"));
c.push(P("Konvoi Scania 58 t menghasilkan gaya yang lebih besar daripada beban lajur D SNI pada semua batang, sehingga Scania menjadi beban yang menentukan desain rangka."));

// BAB 5
c.push(H1("BAB 5  DESAIN ELEMEN JEMBATAN RANGKA"));
c.push(H2("5.1  Prosedur Perhitungan Kapasitas"));
c.push(P("Kapasitas tekan (SNI 1729:2020 Pasal E3):"));
c.push(EQ("Fe = π²E / (KL/r)²"));
c.push(EQ("Fcr = 0,658^(Fy/Fe)·Fy  untuk Fy/Fe ≤ 2,25;   Fcr = 0,877 Fe  untuk Fy/Fe > 2,25"));
c.push(EQ("φPn = 0,90 · Fcr · Ag"));
c.push(P("Kapasitas tarik (Pasal D2):"));
c.push(EQ("φPn = min(0,90·Fy·Ag ;  0,75·Fu·Ae),   Ae = U·An = 0,90 × 0,85 Ag"));
c.push(P("Kelompok zona: Z1 = batang ujung, Z2 = seperempat bentang, Z3 = tengah bentang. KL diambil sama dengan panjang batang (K = 1,0) untuk kedua sumbu."));
c.push(H2("5.2  Rekapitulasi Properti Penampang"));
c.push(table(["Frame", "Profil", "A (mm²)", "Ix (10⁶mm⁴)", "Iy (10⁶mm⁴)", "rx (mm)", "ry (mm)", "Fy (MPa)", "kg/m"],
  D.truss.map(t => [t.frame, t.sec.name, f0(t.sec.A), f2(t.sec.Ix), f2(t.sec.Iy), f2(t.sec.rx), f2(t.sec.ry), t.sec.Fy, f2(t.sec.kg)]),
  [900, 2138, 900, 1000, 1000, 900, 900, 900, 900], 15));
c.push(cap("Tabel 5.1  Properti penampang batang rangka utama"));
c.push(H2("5.3  Pemeriksaan Kapasitas"));
c.push(table(["Frame", "λf / batas", "λw / batas", "KL/r", "Fe (MPa)", "Pu tekan", "φPn tekan", "Pu tarik", "φPn tarik", "UR"],
  D.truss.map(t => [t.frame, `${f2(t.sec.lf)} / ${f2(t.lim_f)}`, `${t.sec.lw} / ${t.lim_w}`, t.KLr, f0(t.Fe), f0(t.Pc), f0(t.phiPc), f0(t.Pt), f0(t.phiPt), f2(t.ur)]),
  [850, 1150, 1150, 700, 850, 950, 1000, 950, 1000, 1038], 15));
c.push(cap("Tabel 5.2  Pemeriksaan kelangsingan elemen, tekan, dan tarik (gaya dalam kN)"));
const tc = D.truss.find(t => t.frame === "TC-Z3");
c.push(H3("Contoh Perhitungan – Top Chord TC-Z3"));
c.push(EQ(`Profil ${tc.sec.name}; Ag = ${f0(tc.sec.A)} mm²; ry = ${tc.sec.ry} mm; Fy = ${tc.sec.Fy} MPa`));
c.push(EQ(`λf = ${tc.sec.lf} ≤ ${tc.lim_f} (OK);  λw = ${tc.sec.lw} ≤ ${tc.lim_w} (OK) → non-langsing`));
c.push(EQ(`KL/r = 5000 / ${tc.sec.ry} = ${tc.KLr} ≤ 120 (OK);  Fe = π²·200000 / ${tc.KLr}² = ${f0(tc.Fe)} MPa`));
c.push(EQ(`φPn = ${f0(tc.phiPc)} kN ≥ Pu = ${f0(tc.Pc)} kN → UR = ${f2(tc.ur)} (OK)`));
const bc = D.truss.find(t => t.frame === "BC-Z3");
c.push(H3("Contoh Perhitungan – Bottom Chord BC-Z3"));
c.push(EQ(`Profil ${bc.sec.name}; Ag = ${f0(bc.sec.A)} mm²; Fy = ${bc.sec.Fy} MPa`));
c.push(EQ(`φPn = min(0,9 × ${bc.sec.Fy} × ${f0(bc.sec.A)} ; 0,75 × 490 × 0,765 × ${f0(bc.sec.A)}) = ${f0(bc.phiPt)} kN`));
c.push(EQ(`Pu = ${f0(bc.Pt)} kN → UR = ${f2(bc.ur)} (OK)`));
c.push(H2("5.4  Sistem Lantai dan Bracing"));
c.push(P("Stringer ST-1: balok sederhana dengan bentang 5,0 m, jarak antar stringer 1,667 m, memikul roda tandem Scania (2 × 107,9 kN @ 1,37 m) dengan FBD 30%. Cross Girder CG-1: bentang 11,53 m, memikul reaksi stringer dan dua truk bersisian (4 garis roda). Flens atas diasumsikan terkekang oleh stringer dan pelat lantai. Brace BR-1 dan Diagonal Member DM-1 memikul beban angin dan gaya stabilitas sebesar 2% dari gaya top chord; ukurannya ditentukan oleh batas KL/r ≤ 140."));
c.push(table(["Frame", "Elemen", "L (m)", "Gaya perlu", "Kapasitas", "Profil", "kg/m", "UR"],
  D.floor.map(t => [t.frame, t.type, f2(t.L), t.Mu !== undefined ? `Mu ${f0(t.Mu)} kNm; Vu ${f0(t.Vu)} kN` : `Pu ${f0(t.Pu)} kN; KL/r ${t.KLr}`,
    t.phiMn !== undefined ? `φMn ${f0(t.phiMn)}; φVn ${f0(t.phiVn)}` : `φPn ${f0(t.phiPc)}`, t.sec.name, f2(t.sec.kg), f2(t.ur)]),
  [700, 1700, 700, 1900, 1600, 1600, 700, 738], 15));
c.push(cap("Tabel 5.3  Desain sistem lantai dan bracing"));

// BAB 6
c.push(H1("BAB 6  DESAIN JEMBATAN FLY OVER GIRDER KOMPOSIT 30,6 m"));
c.push(H2("6.1  Gaya Dalam Girder Interior"));
c.push(table(["Uraian", "Nilai"], [
  ["Mu beban lajur D (terfaktor)", `${f0(G.M_D)} kNm`], ["Mu konvoi Scania × DF × 1,3 × 1,8", `${f0(G.M_sc)} kNm`],
  ["Mu total Kuat I (beban mati + beban hidup yang menentukan)", `${f0(G.Mu)} kNm`], ["Vu total Kuat I", `${f0(G.Vu)} kN`],
  ["Mu tahap konstruksi (baja non-komposit)", `${f0(G.Mc)} kNm`], ["Faktor distribusi DF", `${G.DF}`]], [6000, 3638]));
c.push(cap("Tabel 6.1  Gaya dalam girder"));
c.push(H2("6.2  Pemeriksaan Penampang Komposit"));
["Lebar efektif pelat = jarak girder = 1.700 mm; n = 8.",
 "Momen plastis komposit Mp dihitung dengan blok tekan beton 0,85fc'. Syarat daktilitas Dp/Dt ≤ 0,42; untuk Dp > 0,1Dt, Mn = Mp(1,07 – 0,7Dp/Dt).",
 "Geser: web dengan stiffener transversal @ 1.500 mm, kv = 5 + 5/(a/h)², h/tw ≤ 150.",
 "Tahap konstruksi: flens atas tertekan dengan Lb = 5,1 m (jarak diafragma), dicek terhadap tekuk torsi lateral (LTB).",
 "Lendutan akibat Scania (layan) ≤ L/800 = 38 mm."].forEach(t => c.push(B(t)));
c.push(table(["Frame", "Elemen", "Keterangan", "L (m)", "Mu (kNm)", "Vu (kN)", "Profil", "kg/m", "UR"],
  D.girder.map(t => [t.frame, t.type, t.members, f2(t.L), f0(t.Mu), f0(t.Vu), t.sec.name, f2(t.sec.kg), f2(t.ur)]),
  [700, 1700, 1300, 700, 900, 800, 2038, 700, 800], 15));
c.push(cap("Tabel 6.2  Hasil desain fly over"));
c.push(P("Girder GR-1 memakai flens atas 300 × 16 dan flens bawah 350 × 20 (asimetris, karena flens bawah memikul tarik utama), dengan web 1.664 × 12 yang diberi stiffener @ 1,5 m. Pemeriksaan yang menentukan adalah kombinasi kekuatan lentur komposit dan kekakuan (lendutan L/800)."));

// BAB 7
c.push(H1("BAB 7  REKAPITULASI KODE FRAME DAN PROFIL"));
const all = [...D.truss.map(t => ["Rangka 60 m", t.frame, t.type, t.sec.name, f2(t.sec.kg), f2(t.ur)]),
  ...D.floor.map(t => ["Rangka 60 m", t.frame, t.type, t.sec.name, f2(t.sec.kg), f2(t.ur)]),
  ...D.girder.map(t => ["Fly Over 30,6 m", t.frame, t.type, t.sec.name, f2(t.sec.kg), f2(t.ur)])];
c.push(table(["Jembatan", "Kode Frame", "Elemen", "Profil WB SM490YB", "kg/m", "UR"], all, [1500, 1200, 2938, 2400, 800, 800], 16));
c.push(cap("Tabel 7.1  Rekapitulasi kode frame dan profil (notasi WB d × bf × tw × tf mm; girder bf atas/bawah dan tf atas/bawah)"));
c.push(H2("7.1  Estimasi Tonase Baja"));
c.push(table(["Jembatan", "Estimasi berat baja"], [["Rangka 60 m (2 rangka + lantai + bracing, termasuk 20% sambungan)", `± ${f0(I.sw * 60 / 9.81)} ton`],
  ["Fly over 30,6 m (6 girder saja)", `± ${f0(6 * 30.6 * D.girder[0].sec.kg / 1000)} ton`]], [6000, 3638]));
c.push(H2("7.2  Daftar Tebal Pelat untuk Uji Material (Butir 4.4.3)"));
c.push(P("Tebal pelat yang dipakai: 8, 9, 12, 14, 16, 19, 20, 22, 36, dan 40 mm. Sesuai butir 4.4.3, untuk setiap tebal pelat disiapkan 3 spesimen uji tarik, uji tekuk, dan uji tekan untuk setiap supplier. Pengadaan harus melalui tahap pre-approval (mill certificate dan spesifikasi teknis) dan approval (uji laboratorium yang disaksikan PT SDA)."));

// BAB 8
c.push(H1("BAB 8  KESIMPULAN DAN REKOMENDASI"));
c.push(H2("8.1  Kesimpulan"));
["Seluruh elemen memenuhi syarat kekuatan dengan UR ≤ 0,95, memakai profil WB SM490YB dari tebal pelat yang tersedia di pasar Indonesia.",
 "Konvoi Scania P410 58 t lebih menentukan daripada beban lajur D SNI 1725:2016 untuk rangka 60 m. Untuk fly over, pengaruh keduanya hampir sama besar.",
 "Top chord tengah bentang (TC-Z3) memikul Pu = " + f0(tc.Pc) + " kN dengan profil " + tc.sec.name + ".",
 "Bottom chord tengah bentang (BC-Z3) memikul Pu = " + f0(bc.Pt) + " kN dengan profil " + bc.sec.name + ".",
 "Girder fly over memakai " + D.girder[0].sec.name + "."].forEach(t => c.push(B(t)));
c.push(H2("8.2  Rekomendasi Tindak Lanjut"));
["Konfirmasi tabel beban gandar Scania P410 B8x4 dari PT SDA, lalu jalankan ulang perhitungan.",
 "Buat model 3D SAP2000/MIDAS Civil untuk verifikasi, termasuk momen sekunder, U-frame top chord, lendutan rangka, dan camber.",
 "Lakukan pengecekan fatik: truk tambang menghasilkan siklus beban tinggi, sehingga detail kategori sambungan harus diperiksa.",
 "Rencanakan sambungan baut F10T, pelat buhul, dan splice.",
 "Lakukan analisis gempa sesuai SNI 2833:2016 dan desain perletakan."].forEach(t => c.push(B(t)));

// Lampiran (landscape)
const lamp = [];
lamp.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "LAMPIRAN  GAMBAR KODE FRAME", font: F })] }));
const titles = ["Tampak samping rangka 60 m", "Denah ikatan angin & sistem lantai", "Potongan melintang rangka", "Fly over girder komposit", "Detail penampang WB"];
titles.forEach((t, i) => {
  if (i) lamp.push(new Paragraph({ children: [new PageBreak()] }));
  lamp.push(img(`fig${i + 1}.png`, 900, 638));
  lamp.push(cap(`Gambar L.${i + 1}  ${t}`));
});

const hdr = new Header({ children: [new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1F3864", space: 2 } },
  children: [new TextRun({ text: "PT INDO TRANS  |  Laporan Perhitungan Struktur – Jembatan Road-4 PT SDA", font: F, size: 16, color: "1F3864" })] })] });
const ftr = new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "IT-STR-CAL-R4-001 Rev A  |  Hal. ", font: F, size: 16 }), new TextRun({ children: [PageNumber.CURRENT], font: F, size: 16 })] })] });

const doc = new Document({
  styles: {
    default: { document: { run: { font: F, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: "1F3864", font: F }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 25, bold: true, color: "2E5597", font: F }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 22, bold: true, font: F }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } }],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } }] }] },
  sections: [
    { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, headers: { default: hdr }, footers: { default: ftr }, children: c },
    { properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 850, bottom: 850, left: 850, right: 850 } } }, headers: { default: hdr }, footers: { default: ftr }, children: lamp },
  ],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log("ok"); });

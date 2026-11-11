import json
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
R=json.load(open('res.json')); P=R['P']
YS=['500','1600','2700','3800','4900','6000','7100']
wb=Workbook()
HD=Font(bold=True,color="FFFFFF"); FH=PatternFill("solid",fgColor="1F4E78")
FI=PatternFill("solid",fgColor="FFF2CC"); FO=PatternFill("solid",fgColor="E2EFDA")
B=Border(*[Side(style='thin',color="BFBFBF")]*4)
TT=Font(bold=True,size=12,color="1F4E78")
def hdr(ws,row,vals,w=None):
    for j,v in enumerate(vals,1):
        c=ws.cell(row,j,v); c.font=HD; c.fill=FH; c.border=B; c.alignment=Alignment('center','center',wrap_text=True)
    if w:
        for j,x in enumerate(w,1): ws.column_dimensions[get_column_letter(j)].width=x
def title(ws,t,sub=""):
    ws['A1']=t; ws['A1'].font=TT
    if sub: ws['A2']=sub; ws['A2'].font=Font(italic=True,size=9,color="808080")

# ================= 0-INPUT =================
ws=wb.active; ws.title="0-INPUT"
title(ws,"JEMBATAN RANGKA BAJA KELAS A - BENTANG 100 m","Parameter masukan. SEMUA sheet lain memakai nama sel di sini - ubah nilai di kolom C saja.")
hdr(ws,4,["No","Parameter","Nilai","Satuan","Nama sel","Acuan"],[5,46,13,11,14,52])
rows=[
 ("GEOMETRI",None,None,None,None),
 ("Bentang (as-as perletakan)",P['L'],"m","L_span","Model MCT: node 1 - node 16"),
 ("Jumlah panel rangka",P['npan'],"bh","n_pan","15 panel"),
 ("Jarak antar titik buhul bawah",P['a'],"m","a_pan","Data pengguna = 6666.5 mm"),
 ("Lebar as ke as rangka utama",P['Bas'],"m","B_as","Data pengguna = 7.6 m"),
 ("Lebar lajur bersih",P['Wroad'],"m","W_road","Data pengguna = 6.0 m"),
 ("Lebar trotoar (tiap sisi)",P['Wtrot'],"m","W_trot","Data pengguna = 0.5 m"),
 ("Jumlah stringer",P['nstr'],"bh","n_str","Data pengguna = 7 buah"),
 ("Jarak antar stringer",P['s'],"m","s_str","Data pengguna = 1.1 m"),
 ("TEBAL & BERAT ISI",None,None,None,None),
 ("Tebal plat lantai beton",P['tslab'],"m","t_slab","Data pengguna = 25 cm"),
 ("Tebal trotoar (total)",P['ttrot'],"m","t_trot","Data pengguna = 35 cm"),
 ("Tebal lapis aspal (+ overlay)",P['tasp'],"m","t_asp","SNI 1725-2016 Tabel 3 (50 mm + overlay)"),
 ("Berat isi beton bertulang",P['gc'],"kN/m3","gam_c","SNI 1725-2016 Tabel 1 - sama dengan perencana"),
 ("Berat isi aspal beton",P['gasp'],"kN/m3","gam_asp","SNI 1725-2016 Tabel 1"),
 ("Berat isi baja",P['gs'],"kN/m3","gam_s","SNI 1725-2016 Tabel 1"),
 ("Berat sandaran/railing per sisi",P['wrail'],"kN/m","w_rail","Asumsi pipa + tiang"),
 ("Berat baja termodel (hasil hitung)",P['Wsteel'],"kN","W_steel","Sum A*L*gam_s dari file MCT"),
 ("BEBAN HIDUP",None,None,None,None),
 ("Beban pejalan kaki",P['qped'],"kPa","q_ped","SNI 1725-2016 ps. 8.9"),
 ("Berat truk desain SNI",P['Wtruk'],"kN","W_truk","SNI 1725-2016 ps. 8.4 (50+225+225)"),
 ("Berat truk desain AASHTO HL-93",P['Wtruk_AA'],"kN","W_trukA","AASHTO LRFD 3.6.1.2.2 (35+145+145)"),
 ("Beban lajur AASHTO",P['qLane_AA'],"kN/m","q_laneA","AASHTO LRFD 3.6.1.2.4 (0.64 klf)"),
 ("Lebar lajur rencana",P['wlajur'],"m","w_lajur","SNI 1725-2016 ps. 8.2"),
 ("Jumlah lajur rencana",P['nlajur'],"bh","n_lajur","SNI 1725-2016 Tabel 12 (5.5<=w<8.25)"),
 ("Faktor kehadiran m - 1 lajur",P['m1'],"-","m_1","SNI 1725-2016 Tabel 14"),
 ("Faktor kehadiran m - 2 lajur",P['m2'],"-","m_2","SNI 1725-2016 Tabel 14"),
 ("Panjang chord atas",R['Ltc'],"m","L_tc","14 panel x 6.6665 m"),
 ("ANGIN",None,None,None,None),
 ("PB transversal rangka",P['PBt'],"kPa","PB_t","SNI 1725-2016 Tabel 27 / AASHTO 3.8.1.2.1"),
 ("PB longitudinal rangka",P['PBl'],"kPa","PB_l","SNI 1725-2016 Tabel 27"),
 ("Tekanan angin vertikal",P['PBv'],"kPa","PB_v","SNI 1725-2016 ps. 9.6.2 (0.0096 MPa)"),
 ("Area siluet 1 rangka per m bentang",P['Atruss'],"m2/m","A_truss","Sum L*H elemen bidang y=0 / L = 237.0/100"),
 ("Tinggi ekspos sisi lantai",P['hdeck'],"m","h_deck","plat 0.25 + kerb 0.10"),
 ("Tinggi rangka (maks)",P['htruss'],"m","h_truss","z 9503 - 1003 mm"),
 ("Beban angin pada kendaraan EWl",P['EWLq'],"kN/m","EWL_q","SNI 1725-2016 ps. 9.6.1.2"),
 ("Tinggi kerja EWl di atas lantai",P['hEWL'],"m","h_EWL","SNI 1725-2016 ps. 9.6.1.2"),
 ("SUHU",None,None,None,None),
 ("Perubahan suhu seragam dT",P['dT'],"C","dT","SNI 1725-2016 Tabel 18 (15-40 C)"),
 ("GEMPA - sesuai presentasi perencana (zona 3, tanah sedang)",None,None,None,None),
 ("PGA batuan dasar",P['PGA'],"g","PGA","Presentasi perencana - Peta Gempa 2017, ulang 1000 th"),
 ("Ss (perioda pendek 0.2 s)",P['Ss'],"g","S_s","Presentasi perencana"),
 ("S1 (perioda 1.0 s)",P['S1'],"g","S_1","Presentasi perencana"),
 ("FPGA (tanah sedang / SD)",P['Fpga'],"-","F_pga","dari As 0.433 / PGA 0.39 - presentasi perencana"),
 ("Fa (tanah sedang / SD)",P['Fa'],"-","F_a","dari SDS 0.918 / Ss 0.77 - presentasi perencana"),
 ("Fv (tanah sedang / SD)",P['Fv'],"-","F_v","dari SD1 0.470 / S1 0.247 - presentasi perencana"),
 ("R - faktor modifikasi respons",P['Req'],"-","R_eq","Struktur atas R=1 - presentasi perencana"),
 ("Perioda ragam 1 - longitudinal",P['TX'],"s","T_X","Eigenvalue perencana, mode 2 (100% massa X)"),
 ("Perioda ragam 1 - transversal",P['TY'],"s","T_Y","Eigenvalue perencana, mode 1 (99.4% massa Y)"),
]
r=5;no=0
for nm,val,un,key,ref in rows:
    if val is None:
        c=ws.cell(r,1,nm); c.font=Font(bold=True,color="1F4E78"); ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6)
        ws.cell(r,1).fill=PatternFill("solid",fgColor="DDEBF7"); r+=1; continue
    no+=1
    ws.cell(r,1,no).border=B; ws.cell(r,2,nm).border=B
    c=ws.cell(r,3,val); c.fill=FI; c.border=B; c.number_format='0.0000'
    ws.cell(r,4,un).border=B; ws.cell(r,5,key).border=B; ws.cell(r,6,ref).border=B
    wb.defined_names.add(DefinedName(key,attr_text="'0-INPUT'!$C$%d"%r)); r+=1

# ================= 1-TRIBUTARI =================
ws=wb.create_sheet("1-TRIBUTARI")
title(ws,"1. LEBAR TRIBUTARI TIAP STRINGER","Tata letak melintang: 0.30 rangka | 0.50 trotoar | 6.00 lajur | 0.50 trotoar | 0.30 rangka = 7.60 m. Stringer simetris terhadap as (y=3.80 m).")
hdr(ws,4,["Stringer","y (m)","Tepi?","b plat (m)","b aspal/lajur (m)","b BTR efektif (m)","Keterangan"],[10,9,8,13,17,17,60])
for i,y in enumerate(YS):
    r=5+i; yv=float(y)/1000
    ws.cell(r,1,"ST-%d"%(i+1)); ws.cell(r,2,yv); ws.cell(r,3,"YA" if y in('500','7100') else "-")
    ws.cell(r,4,'=IF(C%d="YA",s_str/2+W_trot,s_str)'%r)
    ws.cell(r,5,'=IF(C%d="YA",(W_road-5*s_str)/2,s_str)'%r)
    ws.cell(r,6,'=IF(C%d="YA",(5.75-5*s_str)/2,s_str)'%r)
    ws.cell(r,7,"stringer tepi: tributari plat termasuk kantilever 0.5 m (trotoar)" if y in('500','7100') else "stringer dalam: tributari = jarak stringer 1.1 m")
    for j in range(1,8): ws.cell(r,j).border=B
    for j in (4,5,6): ws.cell(r,j).number_format='0.000'; ws.cell(r,j).fill=FO
ws.cell(12,3,"JUMLAH"); ws.cell(12,3).font=Font(bold=True)
for j,chk in ((4,"B_as"),(5,"W_road"),(6,"5.75")):
    ws.cell(12,j,"=SUM(%s5:%s11)"%(get_column_letter(j),get_column_letter(j))).font=Font(bold=True)
    ws.cell(12,j).number_format='0.000'
ws.cell(12,7,"cek: kolom D=B_as=7.600 ; E=W_road=6.000 ; F=5.75 (5.5 m @100% + 2x0.25 m @50%)")
ws.cell(14,1,"BTR SNI 1725-2016 ps.8.3.1: 100% pada lebar 5.5 m, 50% pada sisa lebar lajur. b BTR efektif tepi = 0.25 m x 50% = 0.125 m.").font=Font(italic=True,size=9)

# ================= 2-MS =================
ws=wb.create_sheet("2-MS-BERAT-SENDIRI")
title(ws,"2. BERAT SENDIRI (MS) - PLAT LANTAI 250 mm","Berat baja rangka+stringer+gelagar melintang dihitung otomatis oleh midas (*SELFWEIGHT). Sheet ini hanya plat lantai beton yang BELUM dimodelkan sebagai elemen plate.")
ws['A4']="q plat = t_slab x gam_c"; ws['D4']='=t_slab*gam_c'; ws['E4']="kN/m2"; ws['D4'].fill=FO; ws['D4'].number_format='0.000'
hdr(ws,6,["Stringer","b plat (m)","q plat (kN/m2)","w MS (kN/m)","Elemen midas"],[10,12,16,14,34])
el=R['STR']
for i,y in enumerate(YS):
    r=7+i
    ws.cell(r,1,"ST-%d"%(i+1)); ws.cell(r,2,"='1-TRIBUTARI'!D%d"%(5+i)); ws.cell(r,3,'=$D$4')
    ws.cell(r,4,"=B%d*C%d"%(r,r)); ws.cell(r,5,R['_rng'][y] if '_rng' in R else "")
    for j in range(1,6): ws.cell(r,j).border=B
    for j in (2,3,4): ws.cell(r,j).number_format='0.000'
    ws.cell(r,4).fill=FO
ws.cell(14,3,"TOTAL"); ws.cell(14,4,"=SUM(D7:D13)").font=Font(bold=True); ws.cell(14,4).number_format='0.00'
ws.cell(14,5,"= B_as x q plat = 7.6 x 6.0 = 45.6 kN/m  (cek)")
ws.cell(16,1,"Berat baja termodel (dari file MCT) = %.1f kN = %.2f kN/m bentang - sudah dihitung midas lewat *SELFWEIGHT, JANGAN ditambahkan manual."%(P['Wsteel'],P['Wsteel']/P['L'])).font=Font(italic=True,size=9)

# ================= 3-MA =================
ws=wb.create_sheet("3-MA-MATI-TAMBAHAN")
title(ws,"3. BEBAN MATI TAMBAHAN (MA) - TROTOAR 350 mm, ASPAL, SANDARAN","Mengikuti konvensi presentasi perencana: beban trotoar dihitung dengan TEBAL PENUH dan DITAMBAHKAN di atas beban plat (konservatif).")
for i,(lb,fm,un) in enumerate([("Trotoar = t_trot x gam_c x W_trot (tebal penuh, konvensi perencana)",'=t_trot*gam_c*W_trot',"kN/m per sisi"),
                               ("Sandaran / railing",'=w_rail',"kN/m per sisi"),
                               ("q aspal = t_asp x gam_asp",'=t_asp*gam_asp',"kN/m2")]):
    r=4+i; ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,5).number_format='0.000'; ws.cell(r,6,un)
hdr(ws,8,["Stringer","Tepi?","Trotoar (kN/m)","Sandaran (kN/m)","b aspal (m)","Aspal (kN/m)","w MA total (kN/m)"],[10,8,19,16,12,14,18])
for i,y in enumerate(YS):
    r=9+i
    ws.cell(r,1,"ST-%d"%(i+1)); ws.cell(r,2,"='1-TRIBUTARI'!C%d"%(5+i))
    ws.cell(r,3,'=IF(B%d="YA",$E$4,0)'%r); ws.cell(r,4,'=IF(B%d="YA",$E$5,0)'%r)
    ws.cell(r,5,"='1-TRIBUTARI'!E%d"%(5+i)); ws.cell(r,6,"=E%d*$E$6"%r)
    ws.cell(r,7,"=C%d+D%d+F%d"%(r,r,r)); ws.cell(r,7).fill=FO
    for j in range(1,8): ws.cell(r,j).border=B; ws.cell(r,j).number_format='0.000'
ws.cell(16,2,"TOTAL")
for j in (3,4,6,7): ws.cell(16,j,"=SUM(%s9:%s15)"%(get_column_letter(j),get_column_letter(j))).font=Font(bold=True); ws.cell(16,j).number_format='0.00'
ws.cell(18,1,"Perencana: plat 262 mm x 25 = 6.54 kPa ; trotoar 300 mm x 25 = 7.50 kPa ; aspal 50 mm x 22 = 1.10 kPa (identik)").font=Font(italic=True,size=9)

# ================= 4-TD =================
ws=wb.create_sheet("4-TD-LAJUR-D")
title(ws,"4. BEBAN LAJUR 'D' (SNI 1725-2016 ps. 8.3) - BTR + BGT","Lebar lajur bersih 6.0 m > 5.5 m: BTR/BGT 100% pada 5.5 m, 50% pada sisa 0.5 m.")
pr=[("Bentang L",'=L_span',"m"),
    ("q BTR = 9.0 kPa (L<=30 m) atau 9.0 x (0.5 + 15/L)",'=IF(L_span<=30,9,9*(0.5+15/L_span))',"kPa"),
    ("FBD (dynamic load allowance): 0.40 (L<=50) ; 0.30 (L>=90) ; interpolasi",'=IF(L_span<=50,0.4,IF(L_span>=90,0.3,0.4-0.1*(L_span-50)/40))',"-"),
    ("p BGT dasar",49,"kN/m"),
    ("BGT terfaktor = p x (1 + FBD)",'=E7*(1+E6)',"kN/m"),
    ("Posisi BGT dipasang (titik buhul terdekat tengah bentang)",46.6655,"m dari tumpuan")]
for i,(lb,fm,un) in enumerate(pr):
    r=4+i; ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,5).number_format='0.000'; ws.cell(r,6,un)
ws.column_dimensions['A'].width=62
hdr(ws,11,["Stringer","b BTR eff (m)","BTR (kN/m)","BGT (kN, beban titik)","Node midas (BGT)"],[10,14,14,21,18])
nb=R['NBGT']
for i,y in enumerate(YS):
    r=12+i
    ws.cell(r,1,"ST-%d"%(i+1)); ws.cell(r,2,"='1-TRIBUTARI'!F%d"%(5+i))
    ws.cell(r,3,"=B%d*$E$5"%r); ws.cell(r,4,"=B%d*$E$8"%r); ws.cell(r,5,nb[y])
    for j in range(1,6): ws.cell(r,j).border=B
    for j in (2,3,4): ws.cell(r,j).number_format='0.000'; ws.cell(r,j).fill=FO
ws.cell(19,1,"TOTAL")
for j in (3,4): ws.cell(19,j,"=SUM(%s12:%s18)"%(get_column_letter(j),get_column_letter(j))).font=Font(bold=True); ws.cell(19,j).number_format='0.00'
ws.cell(19,5,"cek: BTR 5.85x5.75=33.64 kN/m ; BGT 63.70x5.75=366.3 kN")
hdr(ws,21,["Beban pejalan kaki TP","q (kPa)","W_trot (m)","w TP (kN/m per sisi)","Dipasang pada"],[22,12,12,21,34])
ws.cell(22,1,"SNI 1725-2016 ps. 8.9"); ws.cell(22,2,'=q_ped'); ws.cell(22,3,'=W_trot')
ws.cell(22,4,"=B22*C22").fill=FO; ws.cell(22,4).number_format='0.000'; ws.cell(22,5,"stringer tepi ST-1 dan ST-7")

# ================= 4b-GAYA-REM =================
ws=wb.create_sheet("4b-GAYA-REM")
title(ws,"4b. GAYA REM TB (SNI 1725-2016 ps. 8.7)","Diambil nilai terbesar dari 25% berat gandar truk desain atau 5% (truk desain + BTR). Bekerja arah memanjang, 1.8 m di atas permukaan lantai.")
ws.column_dimensions['A'].width=64
LB=[("SNI 1725-2016",None,None),
 ("Berat truk desain",'=W_truk',"kN"),
 ("(a) 25% x berat gandar truk desain",'=0.25*E5',"kN/lajur"),
 ("(b) 5% x (truk desain + BTR x w_lajur x L)",'=0.05*(E5+\'4-TD-LAJUR-D\'!E5*w_lajur*L_span)',"kN/lajur"),
 ("Menentukan per lajur = MAX(a;b)",'=MAX(E6,E7)',"kN/lajur"),
 ("Jumlah lajur rencana",'=n_lajur',"bh"),
 ("Opsi 1: 2 lajur x m2",'=n_lajur*E8*m_2',"kN"),
 ("Opsi 2: 1 lajur x m1",'=1*E8*m_1',"kN"),
 ("TB TOTAL = MAX(opsi1;opsi2)",'=MAX(E10,E11)',"kN"),
 ("PEMBANDING AASHTO LRFD 3.6.4",None,None),
 ("(a) 25% x berat gandar truk HL-93",'=0.25*W_trukA',"kN/lajur"),
 ("(b) 5% x (truk HL-93 + beban lajur x L)",'=0.05*(W_trukA+q_laneA*L_span)',"kN/lajur"),
 ("BR TOTAL AASHTO = MAX x n_lajur x m2",'=MAX(E14,E15)*n_lajur*m_2',"kN"),
 ("Yang dipakai = MAX(SNI;AASHTO)",'=MAX(E12,E16)',"kN"),
 ("PENYEBARAN KE MODEL",None,None),
 ("Lebar 2 lajur rencana",'=n_lajur*w_lajur',"m"),
 ("w per stringer = TB / L / lebar x s_str",'=E17/L_span/E19*s_str',"kN/m"),
 ("Dipasang pada stringer ST-2 s/d ST-6 (5 jalur)",'=E20*5*L_span',"kN (cek = TB total)"),
 ("Kopel vertikal M = TB x 1.8 m",'=E17*h_EWL',"kNm"),
 ("dV tiap tumpuan tiap rangka = M / L / 2",'=E22/L_span/2',"kN"),
]
r=4
for lb,fm,un in LB:
    if fm is None:
        c=ws.cell(r,1,lb); c.font=Font(bold=True,color="1F4E78"); c.fill=PatternFill("solid",fgColor="DDEBF7")
        ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6); r+=1; continue
    ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,5).number_format='0.000'; ws.cell(r,6,un); r+=1
ws.cell(26,1,"Node tumpuan: x=0 -> node 1 & 48 (FZ = +dV, angkat) ; x=L -> node 16 & 56 (FZ = -dV, tekan)").font=Font(italic=True,size=9)
ws.cell(27,1,"CATATAN: load case TB2 (CAT 777) dan TB3 (XCMG XT400DT) dari model lama 36 m TIDAK dibuat ulang - kendaraan khusus tsb belum ditentukan untuk jembatan ini.").font=Font(bold=True,color="C00000")
ws.cell(28,1,"Kombinasi KUAT II-TK / KUAT II-DT / LAYAN I-TK / LAYAN II-TK / LAYAN II-DT mengacu TB2/TB3 - saat ini kosong.").font=Font(italic=True,size=9)

# ================= 5-ANGIN =================
ws=wb.create_sheet("5-ANGIN")
title(ws,"5. BEBAN ANGIN (SNI 1725-2016 ps. 9.6 / AASHTO LRFD 3.8)","V = 90 km/h = 25 m/s = VB sehingga PD = PB. Kedua rangka diperhitungkan (tanpa reduksi shielding, AASHTO 3.8.1.2.1).")
ws.column_dimensions['A'].width=66
L5=[("ANGIN PADA STRUKTUR - EWs",None,None),
 ("Area siluet 1 rangka per m bentang",'=A_truss',"m2/m"),
 ("Tinggi ekspos sisi lantai",'=h_deck',"m"),
 ("Total area ekspos per m = 2 x rangka + lantai",'=2*E5+E6',"m2/m"),
 ("EWs total per m bentang = PB_t x A",'=PB_t*E7',"kN/m"),
 ("  -> chord ATAS tiap rangka = PB_t x A_truss/2 x L/L_tc",'=PB_t*A_truss/2*L_span/L_tc',"kN/m"),
 ("  -> chord BAWAH tiap rangka = PB_t x A_truss/2 + PB_t x h_deck/2",'=PB_t*A_truss/2+PB_t*h_deck/2',"kN/m"),
 ("  cek resultan = 2 x E9 x L_tc + 2 x E10 x L  (harus = E8 x L)",'=2*E9*L_tc+2*E10*L_span',"kN"),
 ("ANGIN PADA KENDARAAN - EWl",None,None),
 ("EWl (nilai kode, transversal, 1.8 m di atas lantai)",'=EWL_q',"kN/m"),
 ("  -> komponen horizontal tiap chord bawah = EWl / 2",'=EWL_q/2',"kN/m"),
 ("  -> kopel vertikal = EWl x h_EWL / B_as (+ windward, - leeward)",'=EWL_q*h_EWL/B_as',"kN/m"),
 ("ANGIN VERTIKAL - EWv",None,None),
 ("EWv total ke atas = PB_v x B_as (di 1/4 lebar dari tepi angin)",'=PB_v*B_as',"kN/m"),
 ("  -> rangka windward = EWv x (0.5 + (B_as/4)/B_as) = 0.75 x EWv",'=0.75*E17',"kN/m"),
 ("  -> rangka leeward  = 0.25 x EWv",'=0.25*E17',"kN/m"),
 ("ANGIN LONGITUDINAL (informasi, belum dibuat load case)",None,None),
 ("EWs longitudinal = PB_l x A total x L",'=PB_l*E7*L_span',"kN"),
]
r=4
for lb,fm,un in L5:
    if fm is None:
        c=ws.cell(r,1,lb); c.font=Font(bold=True,color="1F4E78"); c.fill=PatternFill("solid",fgColor="DDEBF7")
        ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6); r+=1; continue
    ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,5).number_format='0.000'; ws.cell(r,6,un); r+=1

# ================= 6-SUHU =================
ws=wb.create_sheet("6-SUHU")
title(ws,"6. BEBAN SUHU (EUN) - SNI 1725-2016 ps. 9.3.1 Tabel 18","Jembatan baja dengan lantai beton, daerah tropis: T rata-rata min 15 C, maks 40 C.")
ws.column_dimensions['A'].width=58
for i,(lb,fm,un) in enumerate([("T rata-rata minimum",15,"C"),("T rata-rata maksimum",40,"C"),
   ("T pemasangan (asumsi)",'=(E4+E5)/2',"C"),("dT naik = Tmaks - Tpasang",'=E5-E6',"C"),
   ("dT turun = Tmin - Tpasang",'=E4-E6',"C"),("dT dipakai (input, dibulatkan)",'=dT',"C"),
   ("Koef. muai baja",1.2e-5,"/C"),("Regangan bebas = alpha x dT",'=E10*E9',"-"),
   ("Perpanjangan bebas bentang = eps x L",'=E11*L_span*1000',"mm")]):
    r=4+i; ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,6,un)
    ws.cell(r,5).number_format='0.00000000' if i in (6,7) else '0.000'
ws.cell(14,1,"Input midas: *ELTEMPER seluruh elemen, EUN = +15 C (naik) dan EUN-N = -15 C (turun).").font=Font(italic=True,size=9)

# ================= 7-GEMPA =================
ws=wb.create_sheet("7-GEMPA")
title(ws,"7. BEBAN GEMPA (SNI 2833-2016) - METODE SPEKTRUM RESPONS","Metode dan kelas situs mengikuti pemaparan perencana (tanah sedang, R=1, Csm dari spektrum pada perioda aktual). HANYA parameter hazard yang diganti ke Timor Leste.")
ws.column_dimensions['A'].width=64
RW={}
r=[4]
def row(lb,fm,un,key=None,hdr2=False):
    i=r[0]
    if hdr2:
        c=ws.cell(i,1,lb); c.font=Font(bold=True,color="1F4E78"); c.fill=PatternFill("solid",fgColor="DDEBF7")
        ws.merge_cells(start_row=i,start_column=1,end_row=i,end_column=6); r[0]+=1; return
    ws.cell(i,1,lb); c=ws.cell(i,5,fm); c.fill=FO; c.number_format='0.0000'; ws.cell(i,6,un)
    if key: RW[key]=i
    r[0]+=1; return i
E=lambda k:"E%d"%RW[k]
row("PARAMETER HAZARD - LOKASI TIMOR LESTE",None,None,hdr2=True)
row("PGA batuan dasar",'=PGA',"g","PGA")
row("Ss",'=S_s',"g","Ss"); row("S1",'=S_1',"g","S1")
row("FPGA (tanah sedang / SD)",'=F_pga',"-","Fpga")
row("Fa (tanah sedang / SD)",'=F_a',"-","Fa")
row("Fv (tanah sedang / SD)",'=F_v',"-","Fv")
row("As = FPGA x PGA",'=%s*%s'%(E('Fpga'),E('PGA')),"g","As")
row("SDS = Fa x Ss",'=%s*%s'%(E('Fa'),E('Ss')),"g","SDS")
row("SD1 = Fv x S1",'=%s*%s'%(E('Fv'),E('S1')),"g","SD1")
row("Ts = SD1 / SDS",'=%s/%s'%(E('SD1'),E('SDS')),"s","Ts")
row("T0 = 0.2 x Ts",'=0.2*%s'%E('Ts'),"s","T0")
row("SPEKTRUM PADA PERIODA AKTUAL STRUKTUR",None,None,hdr2=True)
row("Perioda ragam longitudinal TX (eigenvalue perencana)",'=T_X',"s","TX")
row("Perioda ragam transversal TY (eigenvalue perencana)",'=T_Y',"s","TY")
row("Csm arah X = SDS bila TX<=Ts, selain itu SD1/TX",'=IF(%s<=%s,%s,%s/%s)'%(E('TX'),E('Ts'),E('SDS'),E('SD1'),E('TX')),"g","CsmX")
row("Csm arah Y = SDS bila TY<=Ts, selain itu SD1/TY",'=IF(%s<=%s,%s,%s/%s)'%(E('TY'),E('Ts'),E('SDS'),E('SD1'),E('TY')),"g","CsmY")
row("R faktor modifikasi respons (struktur atas)",'=R_eq',"-","R")
row("KOEFISIEN GEMPA arah X = CsmX / R",'=%s/%s'%(E('CsmX'),E('R')),"-","kX")
row("KOEFISIEN GEMPA arah Y = CsmY / R",'=%s/%s'%(E('CsmY'),E('R')),"-","kY")
row("BERAT PERMANEN (per m bentang)",None,None,hdr2=True)
row("Plat lantai = B_as x t_slab x gam_c",'=B_as*t_slab*gam_c',"kN/m","w1")
row("Trotoar = 2 x t_trot x gam_c x W_trot",'=2*t_trot*gam_c*W_trot',"kN/m","w2")
row("Aspal = W_road x t_asp x gam_asp",'=W_road*t_asp*gam_asp',"kN/m","w3")
row("Sandaran = 2 x w_rail",'=2*w_rail',"kN/m","w4")
row("Baja termodel = W_steel / L",'=W_steel/L_span',"kN/m","w5")
row("W permanen per m",'=SUM(%s:%s)'%(E('w1'),E('w5')),"kN/m","wtot")
row("W permanen total",'=%s*L_span'%E('wtot'),"kN","Wtot")
row("GAYA GEMPA",None,None,hdr2=True)
row("EQX total = koefX x W",'=%s*%s'%(E('kX'),E('Wtot')),"kN","EQX")
row("EQY total = koefY x W",'=%s*%s'%(E('kY'),E('Wtot')),"kN","EQY")
row("Berat dek per m (plat+trotoar+aspal+sandaran)",'=SUM(%s:%s)'%(E('w1'),E('w4')),"kN/m","wd")
row("Gaya gempa dek per m - arah X",'=%s*%s'%(E('kX'),E('wd')),"kN/m","gdX")
row("Gaya gempa dek per m - arah Y",'=%s*%s'%(E('kY'),E('wd')),"kN/m","gdY")
row("Gaya gempa baja per m - arah X",'=%s*%s'%(E('kX'),E('w5')),"kN/m","gsX")
row("Gaya gempa baja per m - arah Y",'=%s*%s'%(E('kY'),E('w5')),"kN/m","gsY")
rr=r[0]+1
hdr(ws,rr,["Stringer","b plat (m)","EQX pada stringer (kN/m)","EQY pada stringer (kN/m)"],[10,13,24,24])
for i,y in enumerate(YS):
    q=rr+1+i
    ws.cell(q,1,"ST-%d"%(i+1)); ws.cell(q,2,"='1-TRIBUTARI'!D%d"%(5+i))
    ws.cell(q,3,"=$%s*B%d/B_as"%(E('gdX'),q)).fill=FO
    ws.cell(q,4,"=$%s*B%d/B_as"%(E('gdY'),q)).fill=FO
    for j in range(1,5): ws.cell(q,j).border=B; ws.cell(q,j).number_format='0.000'
tt=rr+8
ws.cell(tt,2,"TOTAL")
for j in (3,4): ws.cell(tt,j,"=SUM(%s%d:%s%d)"%(get_column_letter(j),rr+1,get_column_letter(j),rr+7)).font=Font(bold=True); ws.cell(tt,j).number_format='0.000'
n=tt+2
ws.cell(n,1,"PERBANDINGAN DENGAN PEMAPARAN PERENCANA (lokasi Seram Bagian Barat)").font=Font(bold=True,color="1F4E78")
hdr(ws,n+1,["Parameter","Pemaparan (Seram)","Timor Leste (dipakai)","Catatan"],[26,20,22,52])
cmp=[("PGA",0.39,'=PGA',"peta hazard lokasi berbeda"),("Ss",0.77,'=S_s',""),("S1",0.247,'=S_1',""),
     ("SDS",0.918,'=%s'%E('SDS'),""),("SD1",0.470,'=%s'%E('SD1'),"ini yang menentukan, karena T jauh > Ts"),
     ("Kelas situs","tanah sedang (SD)","tanah sedang (SD)","SAMA"),
     ("R struktur atas",1,'=R_eq',"SAMA"),("Metode","spektrum respons","spektrum respons","SAMA"),
     ("Csm arah X",0.273,'=%s'%E('CsmX'),"Csm = SD1/T"),("Csm arah Y",0.250,'=%s'%E('CsmY'),"Csm = SD1/T")]
for i,(a1,b1,c1,d1) in enumerate(cmp):
    q=n+2+i
    for j,v in enumerate((a1,b1,c1,d1),1): ws.cell(q,j,v).border=B
    ws.cell(q,3).fill=FO
m=n+13
ws.cell(m,1,"CATATAN PENTING").font=Font(bold=True,color="C00000")
ws.cell(m+1,1,"PGA 0.30 / Ss 0.70 / S1 0.30 untuk Dili adalah ASUMSI - wajib diganti data hazard resmi Timor-Leste.").font=Font(color="C00000")
ws.cell(m+2,1,"Batas kemampuan profil asli (hasil analisis): SD1 <= 0.52  atau  S1 <= 0.289 g dengan Fv = 1.8.")
ws.cell(m+3,1,"Dengan S1 = 0.30 g terlampaui 3.7% dan 1 batang ikatan angin bawah (BR1 dekat tumpuan) mencapai rasio 1.04.")
ws.cell(m+4,1,"Csm = SDS (plateau) TIDAK boleh dipakai: perioda struktur ~1.8 s jauh di cabang menurun spektrum (Ts = 0.62 s).")
ws.cell(m+5,1,"Perioda TX/TY diambil dari eigenvalue pemaparan perencana. Setelah model diperbaiki, jalankan eigenvalue ulang dan perbarui sel T_X / T_Y.")
ws.cell(m+6,1,"Perletakan dan angkur tetap dicek dengan gaya elastis penuh (SNI 2833 ps.5.9), bukan hasil bagi R.")

# ================= 8-REKAP =================
ws=wb.create_sheet("8-REKAP-INPUT-MIDAS")
title(ws,"8. REKAPITULASI BEBAN YANG DIINPUT KE MIDAS","Nilai di kolom E adalah yang tertulis di file MCT. Tanda (-) pada arah GZ = ke bawah.")
hdr(ws,4,["Load case","Tipe","Objek","Jenis beban","Nilai","Satuan","Arah","Sumber sheet"],[12,7,26,22,12,9,7,16])
rw=[]
def add(lc,ty,obj,jn,fm,un,ar,sh): rw.append((lc,ty,obj,jn,fm,un,ar,sh))
add("MS","D","Seluruh elemen baja","Self weight otomatis","-","-","GZ","midas")
for i,y in enumerate(YS): add("MS","D","Stringer ST-%d (y=%.1f m)"%(i+1,float(y)/1000),"Plat lantai 250 mm","='2-MS-BERAT-SENDIRI'!D%d"%(7+i),"kN/m","GZ","2")
for i,y in enumerate(YS): add("MA","D","Stringer ST-%d"%(i+1),"Trotoar+sandaran+aspal","='3-MA-MATI-TAMBAHAN'!G%d"%(9+i),"kN/m","GZ","3")
for i,y in enumerate(YS): add("TD-BTR","L","Stringer ST-%d"%(i+1),"BTR 5.85 kPa","='4-TD-LAJUR-D'!C%d"%(12+i),"kN/m","GZ","4")
for i,y in enumerate(YS): add("TD-BGT","L","Node %s (x=46.6655 m)"%R['NBGT'][y],"BGT 63.7 kN/m","='4-TD-LAJUR-D'!D%d"%(12+i),"kN","FZ","4")
add("TB1","L","Stringer ST-2 s/d ST-6","Gaya rem 250 kN","='4b-GAYA-REM'!E20","kN/m","GX","4b")
add("TB1","L","Node 1 dan 48 (x=0)","Kopel vertikal rem","='4b-GAYA-REM'!E23","kN","FZ+","4b")
add("TB1","L","Node 16 dan 56 (x=L)","Kopel vertikal rem","=-'4b-GAYA-REM'!E23","kN","FZ-","4b")
add("TP","L","Stringer ST-1 dan ST-7","Pejalan kaki 5 kPa","='4-TD-LAJUR-D'!D22","kN/m","GZ","4")
add("EWS","W","Chord atas (2 sisi)","Angin struktur","='5-ANGIN'!E9","kN/m","GY","5")
add("EWS","W","Chord bawah (2 sisi)","Angin struktur","='5-ANGIN'!E10","kN/m","GY","5")
add("EWL","W","Chord bawah (2 sisi)","Angin kendaraan - horizontal","='5-ANGIN'!E14","kN/m","GY","5")
add("EWL","W","Chord bawah y=0","Kopel vertikal (angkat)","='5-ANGIN'!E15","kN/m","GZ+","5")
add("EWL","W","Chord bawah y=7.6","Kopel vertikal (tekan)","='5-ANGIN'!E15","kN/m","GZ-","5")
add("EWV","W","Chord bawah y=0 (windward)","Angin vertikal ke atas","='5-ANGIN'!E18","kN/m","GZ+","5")
add("EWV","W","Chord bawah y=7.6 (leeward)","Angin vertikal ke atas","='5-ANGIN'!E19","kN/m","GZ+","5")
add("EUN","T","Seluruh elemen","Suhu seragam naik","='6-SUHU'!E9","C","-","6")
add("EUN-N","T","Seluruh elemen","Suhu seragam turun","=-'6-SUHU'!E9","C","-","6")
for i,y in enumerate(YS): add("EQX","E","Stringer ST-%d (titik buhul)"%(i+1),"Gempa memanjang","='7-GEMPA'!C%d"%(42+i),"kN/m","GX","7")
for i,y in enumerate(YS): add("EQY","E","Stringer ST-%d (titik buhul)"%(i+1),"Gempa melintang","='7-GEMPA'!D%d"%(42+i),"kN/m","GY","7")
add("EQX","E","Semua elemen baja","Gempa - massa baja sendiri","='7-GEMPA'!E38","kN/m","GX","7")
add("EQY","E","Semua elemen baja","Gempa - massa baja sendiri","='7-GEMPA'!E39","kN/m","GY","7")
for i,v in enumerate(rw):
    r=5+i
    for j,x in enumerate(v,1): c=ws.cell(r,j,x); c.border=B
    ws.cell(r,5).number_format='0.000'; ws.cell(r,5).fill=FO

# ================= 9-VERIFIKASI =================
ws=wb.create_sheet("9-VERIFIKASI-MIDAS")
title(ws,"9. VERIFIKASI: EXCEL vs MIDAS","Bandingkan kolom 'Jumlah entri' dengan angka pada model tree midas (Load > Static Loads). Kolom resultan untuk cek Reaction/Self weight.")
hdr(ws,4,["Load case","Jenis entri midas","Jumlah entri","Resultan (Excel)","Satuan","Arah","Catatan"],[12,26,13,17,9,8,44])
V=[("MS","Self Weight + Element Beam Loads",105,'=SUM(\'2-MS-BERAT-SENDIRI\'!D7:D13)*L_span',"kN","-Z","7 stringer x 15 panel = 105 ; berat baja dihitung midas"),
   ("MA","Element Beam Loads",105,"='3-MA-MATI-TAMBAHAN'!G16*L_span","kN","-Z","trotoar + sandaran + aspal"),
   ("TD-BTR","Element Beam Loads",105,"='4-TD-LAJUR-D'!C19*L_span","kN","-Z","BTR 5.85 kPa x b_eff 5.75 m"),
   ("TD-BGT","Nodal Loads",7,"='4-TD-LAJUR-D'!D19","kN","-Z","1 node per stringer di buhul x=46.6655 m"),
   ("TB1","Element Beam Loads",75,"='4b-GAYA-REM'!E20*5*L_span","kN","+X","5 stringer (ST-2..ST-6) x 15 panel = 75"),
   ("TB1","Nodal Loads",4,0,"kN","Z","kopel vertikal, resultan nol (2 naik + 2 turun)"),
   ("-","Rigid Link (diafragma)",16,0,"-","-","Plane XY: Dx Dy Rz, master node chord bawah y=0 tiap panel"),
   ("TP","Element Beam Loads",30,"='4-TD-LAJUR-D'!D22*2*L_span","kN","-Z","2 stringer tepi x 15 panel"),
   ("EWS","Element Beam Loads",58,"=2*'5-ANGIN'!E9*L_tc+2*'5-ANGIN'!E10*L_span","kN","+Y","chord atas 2x14=28 + chord bawah 2x15=30"),
   ("EWL","Element Beam Loads",60,"=2*'5-ANGIN'!E14*L_span","kN","+Y","30 horizontal + 30 kopel vertikal (resultan vert = 0)"),
   ("EWV","Element Beam Loads",30,"=('5-ANGIN'!E18+'5-ANGIN'!E19)*L_span","kN","+Z","chord bawah 2 x 15"),
   ("EUN","Element Temperatures",388,"='6-SUHU'!E9","C","-","seluruh elemen"),
   ("EUN-N","Element Temperatures",388,"=-'6-SUHU'!E9","C","-","seluruh elemen"),
   ("EQX","Beam Loads + Nodal","473+112","='7-GEMPA'!E33","kN","+X","massa baja tiap elemen + massa dek di 7 stringer x 16 buhul"),
   ("EQY","Beam Loads + Nodal","473+112","='7-GEMPA'!E34","kN","+Y","massa baja tiap elemen + massa dek di 7 stringer x 16 buhul")]
for i,v in enumerate(V):
    r=5+i
    for j,x in enumerate(v,1): c=ws.cell(r,j,x); c.border=B
    ws.cell(r,3).fill=FI; ws.cell(r,4).fill=FO; ws.cell(r,4).number_format='0.00'
ws.cell(21,1,"Berat baja termodel (dihitung midas via *SELFWEIGHT) = %.1f kN. Total reaksi vertikal MS seharusnya = %.1f + %.1f = %.1f kN."%(P['Wsteel'],P['Wsteel'],45.6*P['L'],P['Wsteel']+45.6*P['L'])).font=Font(bold=True)
ws.cell(23,1,"Elemen duplikat yang DIKECUALIKAN dari pembebanan: 7, 92, 185, 201, 217, 233, 249, 265, 281, 299, 330.").font=Font(color="C00000")
ws.cell(24,1,"Elemen tsb tetap menggandakan berat sendiri pada panelnya - sebaiknya dihapus dari model.").font=Font(italic=True,size=9)

wb.save("Pembebanan_Jembatan_Rangka_100m.xlsx")
print("OK rows:",len(rw))

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
 ("Berat isi beton bertulang",P['gc'],"kN/m3","gam_c","SNI 1725-2016 Tabel 1"),
 ("Berat isi aspal beton",P['gasp'],"kN/m3","gam_asp","SNI 1725-2016 Tabel 1"),
 ("Berat isi baja",P['gs'],"kN/m3","gam_s","SNI 1725-2016 Tabel 1"),
 ("Berat sandaran/railing per sisi",P['wrail'],"kN/m","w_rail","Asumsi pipa + tiang"),
 ("Berat baja termodel (hasil hitung)",P['Wsteel'],"kN","W_steel","Sum A*L*gam_s dari file MCT"),
 ("BEBAN HIDUP",None,None,None,None),
 ("Beban pejalan kaki",P['qped'],"kPa","q_ped","SNI 1725-2016 ps. 8.9"),
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
 ("GEMPA - TIMOR LESTE (Dili)",None,None,None,None),
 ("PGA batuan dasar",P['PGA'],"g","PGA","Peta hazard regional Dili - ASUMSI, verifikasi"),
 ("Ss (perioda pendek 0.2 s)",P['Ss'],"g","S_s","ASUMSI, verifikasi studi situs"),
 ("S1 (perioda 1.0 s)",P['S1'],"g","S_1","ASUMSI, verifikasi studi situs"),
 ("FPGA (kelas situs SE)",P['Fpga'],"-","F_pga","SNI 2833-2016 Tabel 3"),
 ("Fa (kelas situs SE)",P['Fa'],"-","F_a","SNI 2833-2016 Tabel 4"),
 ("Fv (kelas situs SE)",P['Fv'],"-","F_v","SNI 2833-2016 Tabel 5"),
 ("R - faktor modifikasi respons",P['Req'],"-","R_eq","SNI 2833-2016 Tabel 12 (R=1 sambungan/elastis)"),
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
title(ws,"3. BEBAN MATI TAMBAHAN (MA) - TROTOAR 350 mm, ASPAL, SANDARAN","Trotoar 350 mm = plat 250 mm + topping/kerb 100 mm. Hanya selisih 100 mm yang masuk MA (250 mm sudah dihitung di MS).")
for i,(lb,fm,un) in enumerate([("Topping trotoar = (t_trot - t_slab) x gam_c x W_trot",'=(t_trot-t_slab)*gam_c*W_trot',"kN/m per sisi"),
                               ("Sandaran / railing",'=w_rail',"kN/m per sisi"),
                               ("q aspal = t_asp x gam_asp",'=t_asp*gam_asp',"kN/m2")]):
    r=4+i; ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,5).number_format='0.000'; ws.cell(r,6,un)
hdr(ws,8,["Stringer","Tepi?","Topping trot (kN/m)","Sandaran (kN/m)","b aspal (m)","Aspal (kN/m)","w MA total (kN/m)"],[10,8,19,16,12,14,18])
for i,y in enumerate(YS):
    r=9+i
    ws.cell(r,1,"ST-%d"%(i+1)); ws.cell(r,2,"='1-TRIBUTARI'!C%d"%(5+i))
    ws.cell(r,3,'=IF(B%d="YA",$E$4,0)'%r); ws.cell(r,4,'=IF(B%d="YA",$E$5,0)'%r)
    ws.cell(r,5,"='1-TRIBUTARI'!E%d"%(5+i)); ws.cell(r,6,"=E%d*$E$6"%r)
    ws.cell(r,7,"=C%d+D%d+F%d"%(r,r,r)); ws.cell(r,7).fill=FO
    for j in range(1,8): ws.cell(r,j).border=B; ws.cell(r,j).number_format='0.000'
ws.cell(16,2,"TOTAL")
for j in (3,4,6,7): ws.cell(16,j,"=SUM(%s9:%s15)"%(get_column_letter(j),get_column_letter(j))).font=Font(bold=True); ws.cell(16,j).number_format='0.00'
ws.cell(18,1,"Cek: topping 2x1.20=2.40 ; sandaran 2x0.50=1.00 ; aspal 6.0x1.10=6.60 -> MA total = 10.00 kN/m").font=Font(italic=True,size=9)

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

# ================= 5-ANGIN =================
ws=wb.create_sheet("5-ANGIN")
title(ws,"5. BEBAN ANGIN (SNI 1725-2016 ps. 9.6 / AASHTO LRFD 3.8)","V = 90 km/h = 25 m/s = VB sehingga PD = PB. Kedua rangka diperhitungkan (tanpa reduksi shielding, AASHTO 3.8.1.2.1).")
ws.column_dimensions['A'].width=66
L5=[("ANGIN PADA STRUKTUR - EWs",None,None),
 ("Area siluet 1 rangka per m bentang",'=A_truss',"m2/m"),
 ("Tinggi ekspos sisi lantai",'=h_deck',"m"),
 ("Total area ekspos per m = 2 x rangka + lantai",'=2*E5+E6',"m2/m"),
 ("EWs total per m bentang = PB_t x A",'=PB_t*E7',"kN/m"),
 ("  -> chord ATAS tiap rangka = PB_t x A_truss / 2",'=PB_t*A_truss/2',"kN/m"),
 ("  -> chord BAWAH tiap rangka = PB_t x A_truss/2 + PB_t x h_deck/2",'=PB_t*A_truss/2+PB_t*h_deck/2',"kN/m"),
 ("  cek jumlah = 2 x (chord atas + chord bawah)",'=2*(E9+E10)',"kN/m"),
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
title(ws,"7. BEBAN GEMPA (SNI 2833-2016) - LOKASI TIMOR LESTE (DILI)","Metode beban statik ekuivalen. PERINGATAN: PGA/Ss/S1 adalah ASUMSI hazard regional Dili - WAJIB diganti hasil studi hazard situs.")
ws.column_dimensions['A'].width=62
L7=[("PARAMETER SPEKTRUM",None,None),
 ("PGA batuan dasar",'=PGA',"g"),("Ss",'=S_s',"g"),("S1",'=S_1',"g"),
 ("FPGA (situs SE)",'=F_pga',"-"),("Fa (situs SE)",'=F_a',"-"),("Fv (situs SE)",'=F_v',"-"),
 ("As = FPGA x PGA",'=E5*E8',"g"),("SDS = Fa x Ss",'=E9*E6',"g"),("SD1 = Fv x S1",'=E10*E7',"g"),
 ("Ts = SD1 / SDS",'=E13/E12',"s"),("T0 = 0.2 x Ts",'=0.2*E14',"s"),
 ("Csm (diambil plateau, T <= Ts) = SDS",'=E12',"-"),
 ("R faktor modifikasi respons",'=R_eq',"-"),
 ("KOEFISIEN GEMPA = Csm / R",'=E16/E17',"-"),
 ("BERAT PERMANEN (per m bentang)",None,None),
 ("Plat lantai = B_as x t_slab x gam_c",'=B_as*t_slab*gam_c',"kN/m"),
 ("Topping trotoar = 2 x (t_trot-t_slab) x gam_c x W_trot",'=2*(t_trot-t_slab)*gam_c*W_trot',"kN/m"),
 ("Aspal = W_road x t_asp x gam_asp",'=W_road*t_asp*gam_asp',"kN/m"),
 ("Sandaran = 2 x w_rail",'=2*w_rail',"kN/m"),
 ("Baja termodel = W_steel / L",'=W_steel/L_span',"kN/m"),
 ("W permanen total per m",'=SUM(E20:E24)',"kN/m"),
 ("W permanen total",'=E25*L_span',"kN"),
 ("GAYA GEMPA",None,None),
 ("EQ total (arah X maupun Y) = koef x W",'=E18*E26',"kN"),
 ("  berat dek per m (plat+trotoar+aspal+sandaran)",'=SUM(E20:E23)',"kN/m"),
 ("  gaya gempa dek per m",'=E18*E30',"kN/m"),
 ("  gaya gempa baja per m",'=E18*E24',"kN/m"),
 ("  porsi baja ke chord BAWAH 55% (tiap sisi)",'=E32*0.55/2',"kN/m"),
 ("  porsi baja ke chord ATAS 45% (tiap sisi, panjang 93.331 m)",'=E32*0.45/2*L_span/93.331',"kN/m"),
]
r=4
for lb,fm,un in L7:
    if fm is None:
        c=ws.cell(r,1,lb); c.font=Font(bold=True,color="1F4E78"); c.fill=PatternFill("solid",fgColor="DDEBF7")
        ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6); r+=1; continue
    ws.cell(r,1,lb); ws.cell(r,5,fm).fill=FO; ws.cell(r,5).number_format='0.0000'; ws.cell(r,6,un); r+=1
hdr(ws,36,["Stringer","b plat (m)","EQ pada stringer (kN/m)"],[10,13,24])
for i,y in enumerate(YS):
    rr=37+i
    ws.cell(rr,1,"ST-%d"%(i+1)); ws.cell(rr,2,"='1-TRIBUTARI'!D%d"%(5+i))
    ws.cell(rr,3,"=$E$31*B%d/B_as"%rr).fill=FO; ws.cell(rr,3).number_format='0.000'
    for j in range(1,4): ws.cell(rr,j).border=B
ws.cell(44,2,"TOTAL"); ws.cell(44,3,"=SUM(C37:C43)").font=Font(bold=True); ws.cell(44,3).number_format='0.000'
ws.cell(46,1,"Cek: SUM(stringer)xL + 2 x E33 x L + 2 x E34 x 93.331 harus = EQ total (E28).")
ws.cell(47,1,'=SUM(C37:C43)*L_span+2*E33*L_span+2*E34*93.331').number_format='0.0'
ws.cell(49,1,"CATATAN PENTING: dengan R=1 (desain elastis sambungan & perletakan, SNI 2833 ps.5.9) koefisien 0.91 sangat besar.").font=Font(bold=True,color="C00000")
ws.cell(50,1,"Untuk desain bangunan bawah dapat dipakai R=3 (pilar tunggal) - cukup ubah sel R_eq di sheet 0-INPUT, seluruh hasil ikut berubah.").font=Font(italic=True,size=9)
ws.cell(51,1,"Disarankan tetap melakukan analisis dinamik (eigenvalue + spektrum respons) di midas untuk mendapat T aktual dan Csm yang benar.").font=Font(italic=True,size=9)

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
for i,y in enumerate(YS): add("EQX / EQY","E","Stringer ST-%d"%(i+1),"Gempa statik ekuivalen","='7-GEMPA'!C%d"%(37+i),"kN/m","GX/GY","7")
add("EQX / EQY","E","Chord bawah (2 sisi)","Gempa - massa baja","='7-GEMPA'!E33","kN/m","GX/GY","7")
add("EQX / EQY","E","Chord atas (2 sisi)","Gempa - massa baja","='7-GEMPA'!E34","kN/m","GX/GY","7")
for i,v in enumerate(rw):
    r=5+i
    for j,x in enumerate(v,1): c=ws.cell(r,j,x); c.border=B
    ws.cell(r,5).number_format='0.000'; ws.cell(r,5).fill=FO
wb.save("Pembebanan_Jembatan_Rangka_100m.xlsx")
print("OK rows:",len(rw))

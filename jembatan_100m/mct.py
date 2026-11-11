import json
R=json.load(open('res.json')); P=R['P']
YS=['500','1600','2700','3800','4900','6000','7100']
SR=R['_rng']; BC=R['_rngBC']; TC=R['_rngTC']; ALL=R['_rngALL']; NB=R['NBGT']
o=[]; A=o.append
def hb(t):
    A(""); A(";"+"-"*74); A("; "+t); A(";"+"-"*74)
A(";"+"="*74)
A("; INPUT PEMBEBANAN - JEMBATAN RANGKA BAJA KELAS A, BENTANG 100 m")
A("; Lebar as-as 7.600 m | lajur bersih 6.000 m | trotoar 2 x 0.500 m")
A("; 7 stringer @ 1.100 m (simetris thd as y=3.800 m) | panel buhul bawah 6.6665 m x 15")
A("; Acuan: SNI 1725-2016, SNI 2833-2016, AASHTO LRFD Bridge Design Specifications")
A("; Satuan file ini: TONF, MM -> SEMUA beban di bawah dalam kN dan m, karena itu")
A("; blok *UNIT di bawah mengubah satuan ke KN,M sebelum beban dibaca.")
A(";")
A("; CARA PAKAI (midas Civil):")
A(";   1. Buka model B100.mct / .mcb")
A(";   2. HAPUS DULU load data lama: Load > Static Loads > hapus isi tiap load case")
A(";      (MS, MA, TD-BTR, TD-BGT, EWS, EWL, EWV, EUN, EQX, EQY) agar tidak dobel.")
A(";   3. Tools > MCT Command Shell > buka file ini > Run")
A(";   4. Satuan model kembali ke TONF,MM lewat blok *UNIT di akhir file.")
A(";"+"="*74)
A("")
A("*UNIT")
A("; FORCE, LENGTH, HEAT, TEMPER")
A("   KN, M, BTU, C")

hb("LOAD CASE (tambahan: TP, EUN-N; lainnya sudah ada di model)")
A("*STLDCASE")
A("; LCNAME, LCTYPE, DESC")
for n,t,d in [("MS","D","Berat sendiri - baja (selfweight) + plat lantai beton 250 mm"),
 ("MA","D","Beban mati tambahan - topping trotoar 100 mm + sandaran + aspal 50 mm"),
 ("TD-BTR","L","Beban lajur D - BTR q = 5.85 kPa (SNI 1725 ps.8.3.1 - L=100 m)"),
 ("TD-BGT","L","Beban lajur D - BGT p = 49 x (1+FBD 0.30) = 63.7 kN/m"),
 ("TP","L","Beban pejalan kaki 5 kPa pada trotoar (SNI 1725 ps.8.9)"),
 ("EWS","W","Angin pada struktur PD = 2.4 kPa (SNI 1725 ps.9.6.1.1)"),
 ("EWL","W","Angin pada kendaraan EWl = 1.46 kN/m @1.8 m (SNI 1725 ps.9.6.1.2)"),
 ("EWV","W","Angin vertikal 0.96 kPa x 7.6 m ke atas (SNI 1725 ps.9.6.2)"),
 ("EUN","T","Suhu seragam naik dT = +15 C (SNI 1725 Tabel 18)"),
 ("EUN-N","T","Suhu seragam turun dT = -15 C (SNI 1725 Tabel 18)"),
 ("EQX","E","Gempa memanjang statik ekuivalen Csm/R = %.3f (SNI 2833 - Dili)"%R['coef']),
 ("EQY","E","Gempa melintang statik ekuivalen Csm/R = %.3f (SNI 2833 - Dili)"%R['coef'])]:
    A("   %-7s, %s, %s"%(n,t,d))

def bl(els,p,dr="GZ",sign=-1):
    return "   %s, BEAM, UNILOAD, %s, NO, NO, LZ, 0, 0, NO, 0, %.4f, 1, %.4f, 0, 0, 0, 0, "%(els,dr,sign*p,sign*p)

# ---- MS ----
hb("MS - BERAT SENDIRI : selfweight baja + plat lantai beton 250 mm")
A("*USE-STLD, MS")
A("; *SELFWEIGHT, X, Y, Z, GROUP")
A("*SELFWEIGHT, 0, 0, -1, ")
A("")
A("; Plat lantai t=250 mm, gamma beton 24 kN/m3 -> q = 6.00 kN/m2")
A("; w = q x lebar tributari  (stringer tepi b=1.050 m ; stringer dalam b=1.100 m)")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
A("; [ECCEN] : bECCEN, ECCDIR, I-END, J-END, bJ-END")
for i,y in enumerate(YS):
    A("; ST-%d  y=%.3f m  b=%.3f m  ->  %.3f kN/m"%(i+1,float(y)/1000,R['b_slab'][y],R['MS'][y]))
    A(bl(SR[y],R['MS'][y]))

# ---- MA ----
hb("MA - BEBAN MATI TAMBAHAN : topping trotoar 100 mm + sandaran + aspal 50 mm")
A("*USE-STLD, MA")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
for i,y in enumerate(YS):
    A("; ST-%d : topping %.3f + sandaran %.3f + aspal %.3f = %.3f kN/m"%(
        i+1,R['q_trot'] if y in('500','7100') else 0,P['wrail'] if y in('500','7100') else 0,R['MAasp'][y],R['MA'][y]))
    A(bl(SR[y],R['MA'][y]))

# ---- TD-BTR ----
hb("TD-BTR - BEBAN LAJUR D, BEBAN TERBAGI RATA  q = 5.85 kPa")
A("; q = 9.0 x (0.5 + 15/L) = 9.0 x (0.5 + 15/100) = 5.85 kPa")
A("; 100% pada lebar 5.5 m, 50% pada sisa 0.5 m -> b efektif total 5.75 m")
A("*USE-STLD, TD-BTR")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
for i,y in enumerate(YS):
    A("; ST-%d  b_eff=%.3f m -> %.3f kN/m"%(i+1,R['b_btr'][y],R['BTR'][y]))
    A(bl(SR[y],R['BTR'][y]))

# ---- TD-BGT ----
hb("TD-BGT - BEBAN LAJUR D, BEBAN GARIS TERPUSAT  p = 49 x 1.30 = 63.70 kN/m")
A("; FBD = 0.30 (L = 100 m >= 90 m, SNI 1725 Gambar 10)")
A("; dipasang pada titik buhul x = 46.6655 m (buhul terdekat tengah bentang)")
A("*USE-STLD, TD-BGT")
A("*CONLOAD")
A("; NODE_LIST, FX, FY, FZ, MX, MY, MZ, GROUP")
for i,y in enumerate(YS):
    A("   %s, 0, 0, %.4f, 0, 0, 0, "%(NB[y],-R['BGT'][y]))
A("; total = %.2f kN"%sum(R['BGT'].values()))

# ---- TP ----
hb("TP - BEBAN PEJALAN KAKI 5 kPa x 0.5 m = 2.50 kN/m tiap trotoar")
A("*USE-STLD, TP")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
for y in ('500','7100'): A(bl(SR[y],R['TP'][y]))

# ---- EWS ----
hb("EWS - ANGIN PADA STRUKTUR  PD = PB = 2.4 kPa (V = 90 km/h = VB)")
A("; area ekspos = 2 x 2.370 (rangka) + 0.350 (sisi lantai) = 5.090 m2/m")
A("; EWs total = 2.4 x 5.090 = %.3f kN/m"%R['EWS_tot'])
A("*USE-STLD, EWS")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
A("; chord ATAS tiap rangka = %.3f kN/m (+GY)"%R['EWS_tc'])
A(bl(TC['0']+" "+TC['7600'],R['EWS_tc'],"GY",+1))
A("; chord BAWAH tiap rangka = %.3f kN/m (+GY)"%R['EWS_bc'])
A(bl(BC['0']+" "+BC['7600'],R['EWS_bc'],"GY",+1))

# ---- EWL ----
hb("EWL - ANGIN PADA KENDARAAN  EWl = 1.46 kN/m, 1.8 m di atas lantai")
A("*USE-STLD, EWL")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
A("; horizontal: 1.46/2 = %.3f kN/m tiap chord bawah (+GY)"%R['EWL_h'])
A(bl(BC['0']+" "+BC['7600'],R['EWL_h'],"GY",+1))
A("; kopel vertikal dari eksentrisitas 1.8 m : M = 1.46 x 1.8 = 2.628 kNm/m")
A("; dV = 2.628 / 7.6 = %.4f kN/m (angkat di y=0, tekan di y=7.6)"%R['EWL_v'])
A(bl(BC['0'],R['EWL_v'],"GZ",+1))
A(bl(BC['7600'],R['EWL_v'],"GZ",-1))

# ---- EWV ----
hb("EWV - ANGIN VERTIKAL KE ATAS  0.96 kPa x 7.6 m = %.3f kN/m"%R['EWV_tot'])
A("; bekerja pada 1/4 lebar dari tepi windward -> 75% / 25%")
A("*USE-STLD, EWV")
A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
A("; windward y=0 : %.3f kN/m ke atas"%R['EWV_w'])
A(bl(BC['0'],R['EWV_w'],"GZ",+1))
A("; leeward  y=7.6 : %.3f kN/m ke atas"%R['EWV_l'])
A(bl(BC['7600'],R['EWV_l'],"GZ",+1))

# ---- EUN ----
hb("EUN / EUN-N - BEBAN SUHU SERAGAM  dT = +/- 15 C")
A("*USE-STLD, EUN")
A("*ELTEMPER")
A("; ELEM_LIST, TEMPER, GROUP")
A("   %s, %.1f, "%(ALL,P['dT']))
A("")
A("*USE-STLD, EUN-N")
A("*ELTEMPER")
A("; ELEM_LIST, TEMPER, GROUP")
A("   %s, %.1f, "%(ALL,-P['dT']))

# ---- EQ ----
hb("EQX / EQY - GEMPA STATIK EKUIVALEN (SNI 2833-2016) - TIMOR LESTE (DILI)")
A("; PGA=%.2f g  Ss=%.2f g  S1=%.2f g  kelas situs SE"%(P['PGA'],P['Ss'],P['S1']))
A("; FPGA=%.1f Fa=%.1f Fv=%.1f -> As=%.3f  SDS=%.3f  SD1=%.3f  Ts=%.3f s"%(P['Fpga'],P['Fa'],P['Fv'],R['As'],R['SDS'],R['SD1'],R['Ts']))
A("; Csm = SDS = %.3f  ; R = %.1f  ; koefisien = %.3f"%(R['Csm'],P['Req'],R['coef']))
A("; W permanen = %.2f kN/m x %.4f m = %.1f kN  ->  EQ = %.1f kN"%(R['Wperm_m'],P['L'],R['Wperm'],R['EQ_tot']))
A("; PERINGATAN: parameter hazard adalah ASUMSI regional Dili - WAJIB diverifikasi")
for lc,dr in (("EQX","GX"),("EQY","GY")):
    A("")
    A("*USE-STLD, %s"%lc)
    A("*BEAMLOAD")
    A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
    for i,y in enumerate(YS):
        A("; ST-%d massa dek -> %.3f kN/m"%(i+1,R['EQ_str'][y]))
        A(bl(SR[y],R['EQ_str'][y],dr,+1))
    A("; massa baja -> chord bawah %.3f kN/m tiap sisi"%R['EQ_bc'])
    A(bl(BC['0']+" "+BC['7600'],R['EQ_bc'],dr,+1))
    A("; massa baja -> chord atas %.3f kN/m tiap sisi"%R['EQ_tc'])
    A(bl(TC['0']+" "+TC['7600'],R['EQ_tc'],dr,+1))

hb("KEMBALIKAN SATUAN MODEL KE TONF, MM")
A("*UNIT")
A("   TONF, MM, BTU, C")
A("")
A("*ENDDATA")
open('Pembebanan_B100.mct','w').write("\n".join(o)+"\n")
print("lines:",len(o))

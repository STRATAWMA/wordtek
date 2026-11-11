import json,math,collections,re
D=json.load(open('fix.json')); R=json.load(open('res.json')); P=R['P']
nodes={int(k):v for k,v in D['nodes'].items()}; elems=D['elems']; newsec=D['newsec']
PANEL=sorted(D['panel']); bxf={float(k):{float(a):b for a,b in v.items()} for k,v in D['bx'].items()}
YS=['500','1600','2700','3800','4900','6000','7100']
def expand(rs):
    o=[]
    for t in rs.split():
        if 'to' in t: a,b=t.split('to'); o+=list(range(int(a),int(b)+1))
        else: o.append(int(t))
    return o
# daftar elemen dibangun ULANG dari geometri model final (bukan dari range lama),
# supaya pertukaran elemen duplikat 248/249 tidak menghilangkan satu panel.
import collections as _c
_byl=_c.defaultdict(list)
for _e in elems:
    _a,_b=nodes[_e['n1']],nodes[_e['n2']]
    if abs(_a[1]-_b[1])<1 and abs(_a[0]-_b[0])>1 and _a[2]<3000 and _b[2]<3000:
        _byl[round(_a[1])].append(_e['id'])
_tc=_c.defaultdict(list)
for _e in elems:
    _a,_b=nodes[_e['n1']],nodes[_e['n2']]
    if abs(_a[1]-_b[1])<1 and _a[2]>7000 and _b[2]>7000: _tc[round(_a[1])].append(_e['id'])
STR={y:sorted(_byl[int(y)]) for y in YS}
BC={k:sorted(_byl[int(k)]) for k in ('0','7600')}
TC={k:sorted(_tc[int(k)]) for k in ('0','7600')}
for _y in YS:
    assert len(STR[_y])==15, (_y,len(STR[_y]))
assert len(BC['0'])==15 and len(BC['7600'])==15
assert len(TC['0'])==14 and len(TC['7600'])==14
def rng(ids):
    ids=sorted(set(ids)); out=[];i=0
    while i<len(ids):
        j=i
        while j+1<len(ids) and ids[j+1]==ids[j]+1: j+=1
        out.append(str(ids[i]) if i==j else "%dto%d"%(ids[i],ids[j])); i=j+1
    return " ".join(out)
ALL=rng([e['id'] for e in elems])
# ---------- penampang upgrade ----------
UPG={}



CGDIM={74:910,75:930,76:960,77:990}
# ---------- baca file lama ----------
raw=open('new.mct',errors='ignore').read().splitlines()
def grab(name):
    out=[];on=False
    for l in raw:
        t=l.strip()
        if t.startswith('*'):
            tag=t.split(',')[0].split()[0].upper().lstrip('*')
            if tag==name: on=True; continue
            if on: break
            on=False; continue
        if on: out.append(l)
    return out
O=[];A=O.append
def hdr(t): A(""); A(";"+"="*76); A("; "+t); A(";"+"="*76)
A(";--------------------------------------------------------------------------")
A(";  MIDAS/Civil Text(MCT) File  -  MODEL FINAL HASIL PERBAIKAN")
A(";  Jembatan Rangka Baja Kelas A - bentang 100 m - BM 100")
A(";  Perbaikan: (1) 6 jalur stringer yang semula tidak tersambung kini")
A(";             tersambung ke gelagar melintang (CG dipecah 8 segmen/panel)")
A(";             (2) 11 elemen duplikat dihapus")
A(";             (3) beban dimasukkan SEKALI (sebelumnya dobel)")
A(";             (4) diafragma lantai (pelat 250 mm) sebagai Rigid Link bidang XY")

A(";             (5) gaya rem di level chord bawah, gempa dek sebagai beban titik")
A(";             (6) Csm gempa dari spektrum pada perioda aktual, bukan plateau SDS")
A(";")
A(";  CEK SETELAH IMPOR - Load > Static Load Cases, jumlah entri harus TEPAT:")
A(";     MS 105 beam + Self Weight | MA 105 | TD-BTR 105 | TD-BGT 7 nodal")
A(";     TB1 30 beam + 4 nodal     | TP 30  | EWS 58     | EWL 60 | EWV 30")
A(";     EUN / EUN-N 473 temper    | EQX & EQY 473 beam + 112 nodal")
A(";     Boundaries > Rigid Link   : 16 master x 8 slave = 128 pasangan")
A(";  Bila MS menunjukkan 210, berarti terimpor ke model yang sudah berisi data.")
A(";")
A(";  ######################################################################")
A(";  #  CARA RUN  -  WAJIB, kalau tidak beban akan BERTUMPUK                #")
A(";  #                                                                      #")
A(";  #   1. midas:  File > New        (model benar-benar kosong)            #")
A(";  #   2. Tools > MCT Command Shell > buka file ini > Run                 #")
A(";  #   3. Simpan dengan nama baru                                         #")
A(";  #                                                                      #")
A(";  #  Node/elemen/penampang DITIMPA karena nomornya sama, tetapi BEBAN    #")
A(";  #  selalu DITAMBAHKAN - itulah yang membuatnya berlipat.               #")
A(";  #                                                                      #")
A(";  #  Terpaksa pakai model lama? Hapus dulu SELURUH Static Load Case      #")
A(";  #  (Load > Static Load Cases > hapus 13 case) baru Run.                #")
A(";  ######################################################################")
A(";--------------------------------------------------------------------------")
A("")
A("*VERSION"); A("   8.7.5"); A("")
A("; Satuan DIMULAI dengan TONF, MM - sama seperti model asli.")
A("; PENTING: *STRUCTYPE memuat GRAV = 9810 yang HARUS dibaca sebagai mm/s2.")
A("; Bila blok ini terbaca saat satuan KN,M, gravitasi menjadi 9810 m/s2 dan")
A("; berat sendiri melonjak 1000x lipat.")
A("*UNIT"); A("; FORCE, LENGTH, HEAT, TEMPER"); A("   TONF, MM, BTU, C"); A("")
A("*PROJINFO")
A("   PROJECT=Jembatan Rangka Baja Kelas A - Bentang 100 m - BM 100")
A("   CLIENT=PT Indo Trans Baja Utama"); A("")
A("*STRUCTYPE"); [A(l) for l in grab('STRUCTYPE')]; A("")
A("")
A("*NODE"); A("; iNO, X, Y, Z"); [A(l) for l in grab('NODE')]
hdr("ELEMENT - 473 batang (duplikat dihapus, gelagar melintang dipecah 8 segmen)")
A("*ELEMENT")
A("; iEL, TYPE, iMAT, iPRO, iN1, iN2, ANGLE, iSUB, EXVAL")
for e in sorted(elems,key=lambda x:x['id']):
    A("   %5d, BEAM  , %5d, %5d, %5d, %5d, %5g, 0, 0"%(e['id'],e['mat'],e['sec'],e['n1'],e['n2'],e['ang']))
A("")
for s in ('GROUP','MATERIAL','MATL-COLOR'):
    A("*"+s); [A(l) for l in grab(s)]; A("")
# ---------- SECTION ----------
def secline(tag,i,nm,body): return "   %3d, DBUSER    , %-18s, CC, 0, 0, 0, 0, 0, 0, YES, NO, %s"%(i,nm,body)
hdr("SECTION - SEMUA PROFIL ASLI DIPERTAHANKAN + 4 penampang gelagar melintang")
for tag in ('SECTION','DGN-SECT'):
    A("*"+tag)
    for l in grab(tag):
        s=l.strip()
        m=re.match(r'^(\d+),',s)
        if m and int(m.group(1)) in UPG:
            i=int(m.group(1)); u=UPG[i]
            if u[0]=='P': A(secline(tag,i,u[3],"P  , 2, %g, %g, 0, 0, 0, 0, 0, 0, 0, 0"%(u[1],u[2])))
            else: A(secline(tag,i,u[5],"H  , 2, %g, %g, %g, %g, 0, 0, 0, 0, 0, 0"%(u[1],u[2],u[3],u[4])))
        else: A(l)
    for i,d in sorted(CGDIM.items()):
        A(secline(tag,i,"CG-%d"%d,"H  , 2, %d, 420, 12, 16, 0, 0, 0, 0, 0, 0"%d))
    A("")
A("*SECT-COLOR")
for l in grab('SECT-COLOR'): A(l)
for i in sorted(CGDIM): A("  %3d, 255,   0,   0,    0, 255,   0,    0,   0, 255,  NO, 0.5"%i)
A("")
for s in ('THICKNESS','THIK-COLOR'):
    A("*"+s); [A(l) for l in grab(s)]; A("")
A("*DGN-STEEL"); [A(l) for l in grab('DGN-STEEL')]; A("")
hdr("TUMPUAN - 4 buah POT BEARING")
A("; node 16 (x=100 m, y=0)    : POT TETAP / FIXED          -> Dx Dy Dz")
A("; node 56 (x=100 m, y=7.6)  : POT PENGARAH MEMANJANG     -> Dx Dz   (bebas arah Y)")
A("; node  1 (x=0,     y=0)    : POT PENGARAH MELINTANG     -> Dy Dz   (bebas arah X)")
A("; node 48 (x=0,     y=7.6)  : POT BEBAS / FREE SLIDING   -> Dz      (bebas X dan Y)")
A("; Semua rotasi bebas (Rx=Ry=Rz=0) sesuai perilaku pot bearing.")
A("*CONSTRAINT")
A("; NODE_LIST, CONST(Dx,Dy,Dz,Rx,Ry,Rz), GROUP")
A("   16, 111000, "); A("   56, 101000, "); A("   1, 011000, "); A("   48, 001000, ")
hdr("DIAFRAGMA LANTAI - pelat beton 250 mm sebagai Rigid Link bidang XY")
A("; Tanpa ini gaya horizontal bidang lantai terpaksa dipikul lentur sumbu lemah")
A("; gelagar melintang -> Mz palsu sampai 630 kNm dan ikatan angin kelebihan beban.")

YF=[0.0,500.0,1600.0,2700.0,3800.0,4900.0,6000.0,7100.0,7600.0]
A("; Field 1 adalah NOMOR URUT, bukan master. Urutan: iNO, MASTER, DOF, SLAVE_LIST")
A("; DOF 110001 = Dx, Dy, Rz  (di GUI midas: Rigid Link tipe Plane XY)")
A("*RIGIDLINK")
A("; iNO, MASTER_NODE, DOF, S_NODE_LIST, GROUP")
for _i,x in enumerate(PANEL,1):
    m=bxf[x][0.0]; sl=" ".join(str(bxf[x][y]) for y in YF[1:])
    A("   %d, %d, 110001, %s, "%(_i,m,sl))
A("")
A("; JIKA 16 baris di atas MASIH error parsing, hapus saja blok *RIGIDLINK ini lalu")
A("; buat lewat GUI: Model > Boundaries > Rigid Link, Typical Type = Plane XY,")
A("; master = node pertama tiap baris, slave = 8 node berikutnya. Sisa model tetap")
A("; terimpor normal. Daftar lengkapnya persis seperti baris-baris di atas.")
A("; CATATAN LAMA: blok *RIGIDLINK DIMATIKAN - urutan field-nya ditolak parser 8.7.5")
A("; (Parsing Error: Binary code has characters other than 0 & 1).")
A("; Model ini TIDAK memerlukannya: gelagar melintang sudah diperbesar menjadi")
A("; H d x 500 x 14 x 25 sehingga mampu memikul sendiri gaya bidang lantai.")
A("; Hasilnya konservatif karena kekakuan pelat beton diabaikan.")
A(";")
A("; OPSIONAL - bila ingin memodelkan diafragma pelat (hasil lebih ekonomis):")
A(";   GUI: Model > Boundaries > Rigid Link")
A(";        Master = node chord bawah y=0 tiap panel, Slave = 8 node lantai lain")
A(";        Typical Type = Plane XY  (Dx, Dy, Rz)")
A("; (duplikat daftar untuk input manual GUI)")
for x in PANEL:
    m=bxf[x][0.0]; sl=" ".join(str(bxf[x][y]) for y in YF[1:])
    A(";   master %-4d  slave %s"%(m,sl))
A("")
hdr("BEBAN BERGERAK & MATERIAL DESAIN - tetap di satuan TONF, MM")
A("; LINELANE memuat lebar lajur dalam mm, VEHICLE memuat gandar dalam tonf,")
A("; DGN-MATL memuat Fy dalam tonf/mm2. Bila blok-blok ini terbaca di satuan")
A("; KN,M, Fy menjadi 0.0362 kN/m2 dan SELURUH kapasitas batang jadi nol")
A("; (pPn 0.0008 kN) sehingga semua batang NG / UPLT.")
for _s in ('MVLDCODE','LINELANE','VEHICLE','MVLDCASE'):
    _g=grab(_s)
    if _g: A("*"+_s); [A(_l) for _l in _g]; A("")
# --- DGN-MATL: SM490YB dengan band tebal sesuai pemaparan perencana ---
#     fy = 365 MPa untuk t <= 16 mm ; fy = 355 MPa untuk t > 16 mm ; fu = 490 MPa
_K=9.80665e3                       # MPa -> tonf/mm2
_FU=490.0/_K; _F1=365.0/_K; _F2=355.0/_K
_tail=("2, 0, , , , 0, 0,NO,0.0000e+000,     0,, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,"
       "0.0000e+000,     0,, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,"
       "0.0000e+000,     0,, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,")
A("*DGN-MATL")
A("; iMAT, TYPE, MNAME, 2, ELAST, POISN, FU, FY1..FY6, AFT, AFT2, AFT3, FY, AFV, AFV2, AFV3")
A("; SM490YB : fy 365 MPa (t<=16 mm), fy 355 MPa (t>16 mm), fu 490 MPa")
A("    1, STEEL, SM490YB           , 2, 2.0904e+001,   0.3, %.10f, %.10f, %.10f, %.10f, %.10f, %.10f, %.10f, 16, 40, 100, %.10f, 0, 0, 0, 0, %s"
  %(_FU,_F1,_F2,_F2,_F2,_F2,_F2,_F2,_tail))
A("    2, STEEL, SS400             , 2, 2.0904e+001,   0.3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, %s"%_tail)
A("")
A("; ---- mulai di sini satuan pindah ke KN, M khusus untuk DATA BEBAN ----")
A("@@@SPLIT@@@")
A("*UNIT")
A("; FORCE, LENGTH, HEAT, TEMPER")
A("   KN, M, BTU, C")
hdr("LOAD CASE")
A("*STLDCASE")
A("; LCNAME, LCTYPE, DESC")
for n,t,d in [("MS","D","Berat sendiri baja + plat lantai 262 mm + trotoar 300 mm"),
 ("MA","D","Mati tambahan - sandaran + aspal 50 mm (tebal terkendali)"),
 ("TD-BTR","L","Lajur D - BTR 5.85 kPa (SNI 1725 ps.8.3.1)"),
 ("TD-BGT","L","Lajur D - BGT 49 x 1.30 = 63.7 kN/m"),
 ("TB1","L","Gaya rem 250 kN di level lantai (SNI 1725 ps.8.7)"),
 ("TP","L","Pejalan kaki 5 kPa pada trotoar (SNI 1725 ps.8.9)"),
 ("EWS","W","Angin pada struktur PD = 2.4 kPa (SNI 1725 ps.9.6.1.1)"),
 ("EWL","W","Angin pada kendaraan 1.46 kN/m (SNI 1725 ps.9.6.1.2)"),
 ("EWV","W","Angin vertikal 0.96 kPa x 7.6 m (SNI 1725 ps.9.6.2)"),
 ("EUN","T","Suhu seragam naik +15 C"),("EUN-N","T","Suhu seragam turun -15 C"),
 ("EQX","E","Gempa memanjang Csm=SD1/T=0.470/1.7222 -> koef %.4f (SNI 2833)"%R['coefX']),
 ("EQY","E","Gempa melintang  Csm=SD1/T=0.470/1.8790 -> koef %.4f (SNI 2833)"%R['coefY'])]:
    A("   %-7s, %s, %s"%(n,t,d))
# Seluruh blok beban di bawah ini memakai satuan KN, M (lihat *UNIT di atas).
def bl(els,p,dr="GZ",sg=-1):
    return "   %s, BEAM, UNILOAD, %s, NO, NO, LZ, 0, 0, NO, 0, %.4f, 1, %.4f, 0, 0, 0, 0, "%(els,dr,sg*p,sg*p)
def blk(lc,title=None):
    A(""); A("*USE-STLD, %s"%lc)
hdr("DATA PEMBEBANAN  (satu kali saja - tidak dobel)")
blk('MS'); A("*SELFWEIGHT, 0, 0, -1, "); A("*BEAMLOAD")
A("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
for y in YS: A(bl(rng(STR[y]),R['MS'][y]))
blk('MA'); A("*BEAMLOAD")
for y in YS: A(bl(rng(STR[y]),R['MA'][y]))
blk('TD-BTR'); A("*BEAMLOAD")
for y in YS: A(bl(rng(STR[y]),R['BTR'][y]))
blk('TD-BGT'); A("*CONLOAD"); A("; NODE_LIST, FX, FY, FZ, MX, MY, MZ, GROUP")
for y in YS: A("   %s, 0, 0, %.4f, 0, 0, 0, "%(R['NBGT'][y],-R['BGT'][y]))
blk('TB1')
A("; 250 kN dibagi 2 chord bawah = %.4f kN/m ; kopel vertikal +/- %.3f kN"%(R['TB_tot']/2/P['L'],R['TB_V']))
A("*BEAMLOAD")
A(bl(rng(BC['0'])+" "+rng(BC['7600']),R['TB_tot']/2/P['L'],"GX",+1))
A("*CONLOAD"); A("; NODE_LIST, FX, FY, FZ, MX, MY, MZ, GROUP")
for n in R['NSUP']['x0']: A("   %d, 0, 0, %.4f, 0, 0, 0, "%(n, R['TB_V']))
for n in R['NSUP']['xL']: A("   %d, 0, 0, %.4f, 0, 0, 0, "%(n,-R['TB_V']))
blk('TP'); A("*BEAMLOAD")
for y in ('500','7100'): A(bl(rng(STR[y]),R['TP'][y]))
blk('EWS'); A("*BEAMLOAD")
A(bl(rng(TC['0'])+" "+rng(TC['7600']),R['EWS_tc'],"GY",+1))
A(bl(rng(BC['0'])+" "+rng(BC['7600']),R['EWS_bc'],"GY",+1))
blk('EWL'); A("*BEAMLOAD")
A(bl(rng(BC['0'])+" "+rng(BC['7600']),R['EWL_h'],"GY",+1))
A(bl(rng(BC['0']),R['EWL_v'],"GZ",+1)); A(bl(rng(BC['7600']),R['EWL_v'],"GZ",-1))
blk('EWV'); A("*BEAMLOAD")
A(bl(rng(BC['0']),R['EWV_w'],"GZ",+1)); A(bl(rng(BC['7600']),R['EWV_l'],"GZ",+1))
for lc,dT in (('EUN',P['dT']),('EUN-N',-P['dT'])):
    blk(lc); A("*ELTEMPER"); A("; ELEM_LIST, TEMPER, GROUP"); A("   %s, %.1f, "%(ALL,dT))
# gempa : baja = line load per penampang ; dek = beban titik
import pickle
def Hp(H,B,tw,tf): return 2*B*tf+(H-2*tf)*tw
def Pp(Do,t): return math.pi/4*(Do**2-(Do-2*t)**2)
sec=None;S={}
for ln in open('new.mct',errors='ignore'):
    s=ln.strip()
    if s.startswith('*'): sec=s.split(',')[0].split()[0].upper(); continue
    if sec!='*SECTION' or not s or s.startswith(';'): continue
    f=[x.strip() for x in s.split(',')]
    if f[1] in ('DBUSER','TAPERED'): S[int(f[0])]=f
AREA={}
for i,f in S.items():
    if i in UPG:
        u=UPG[i]; AREA[i]=Pp(u[1],u[2]) if u[0]=='P' else Hp(u[1],u[2],u[3],u[4]); continue
    if f[1]=='TAPERED': continue
    sh=f[12];md=f[13];d=[x for x in f[14:] if x!='']
    if md=='1':
        m=re.search(r'(\d+)x(\d+)x([\d.]+)/([\d.]+)',' '.join(d)); H,B,tw,tf=[float(x) for x in m.groups()]
        AREA[i]=Hp(H,B,tw,tf); continue
    d=[float(x) for x in d]; AREA[i]=Hp(*d[:4]) if sh=='H' else Pp(d[0],d[1])
for i,dd in CGDIM.items(): AREA[i]=Hp(dd,420,12,16)
bysec=collections.defaultdict(list)
for e in elems: bysec[e['sec']].append(e['id'])
CO={'EQX':R['coefX'],'EQY':R['coefY']}
coef=R['coef']; w_deck=R['w_slab_m']+R['w_trot_m']+R['w_asp_m']+R['w_rail_m']
bsl={500.0:1.05,1600.0:1.1,2700.0:1.1,3800.0:1.1,4900.0:1.1,6000.0:1.1,7100.0:1.1}
for lc,dr in (('EQX','GX'),('EQY','GY')):
    coef=CO[lc]
    blk(lc)
    A("; Csm = SD1/T = %.4f / %.4f = %.4f g ; R = %.1f -> koef = %.4f"%(R['SD1'],P['TX'] if lc=='EQX' else P['TY'],coef*P['Req'],P['Req'],coef))
    A("; massa baja: w = %.4f x 78.5 kN/m3 x A  (per penampang)"%coef)
    A("*BEAMLOAD")
    for isec in sorted(bysec):
        w=coef*78.5*AREA[isec]/1e6
        A(bl(rng(bysec[isec]),w,dr,+1))
    A("; massa dek (pelat+trotoar+aspal+sandaran) -> beban titik, DISEBAR ke 7 stringer")
    A("; sesuai lebar tributari masing-masing (tidak dibebankan langsung ke gelagar).")
    A("*CONLOAD"); A("; NODE_LIST, FX, FY, FZ, MX, MY, MZ, GROUP")
    for i,x in enumerate(PANEL):
        trib=P['a']/2 if i in (0,len(PANEL)-1) else P['a']
        for y,b in sorted(bsl.items()):
            Pn=coef*w_deck*b/P['Bas']*trib
            fx=Pn if dr=='GX' else 0; fy=Pn if dr=='GY' else 0
            A("   %d, %.4f, %.4f, 0, 0, 0, 0, "%(bxf[x][y],fx,fy))
hdr("KOMBINASI PEMBEBANAN (SNI 1725-2016 Tabel 1) - TB2/TB3 dihapus")
A("*LOADCOMB")
A("; NAME=NAME, KIND, ACTIVE, bES, iTYPE, DESC, iSERV-TYPE, nLCOMTYPE")
CB=[("KUAT I","STRENGTH",[("MS",1.1),("MA",1.4),("TD-BTR",1.8),("TD-BGT",1.8),("TP",1.8),("TB1",1.8),("EUN",0.5)]),
 ("KUAT III","STRENGTH",[("MS",1.1),("MA",1.4),("EWS",1.4),("EWV",1.4),("EUN",0.5)]),
 ("KUAT III-MIN","STRENGTH",[("MS",0.9),("MA",0.7),("EWS",1.4),("EWV",1.4)]),
 ("KUAT IV","STRENGTH",[("MS",1.1),("MA",1.4),("EUN",0.5)]),
 ("KUAT V","STRENGTH",[("MS",1.1),("MA",1.4),("EWS",0.4),("EWL",1.0),("EUN",0.5)]),
 ("EKSTREM I-EQX","STRENGTH",[("MS",1.1),("MA",1.4),("EQX",1.0),("EQY",0.3)]),
 ("EKSTREM I-EQY","STRENGTH",[("MS",1.1),("MA",1.4),("EQX",0.3),("EQY",1.0)]),
 ("LAYAN I","SERVICE",[("MS",1.0),("MA",1.0),("TD-BTR",1.0),("TD-BGT",1.0),("TP",1.0),("TB1",1.0),("EWS",0.3),("EWL",1.0),("EUN",1.0)]),
 ("LAYAN II","SERVICE",[("MS",1.0),("MA",1.0),("TD-BTR",1.3),("TD-BGT",1.3),("TB1",1.3),("EUN",1.0)]),
 ("LAYAN IV","SERVICE",[("MS",1.0),("MA",1.0),("EWS",0.7),("EWV",0.7),("EUN",1.0)]),
 ("LENDUT-TD","SERVICE",[("TD-BTR",1.0),("TD-BGT",1.0)])]
for nm,kind,terms in CB:
    A("   NAME=%s, STEEL, %s, 0, 0, SNI 1725-2016 Tabel 1, 0, 0"%(nm,kind))
    ch=[terms[i:i+5] for i in range(0,len(terms),5)]
    for g in ch: A("        "+", ".join("ST, %s, %g"%(a,b) for a,b in g))
A("")
hdr("CATATAN PARAMETER DESAIN - WAJIB DISET DI GUI MIDAS")
A("; 1. PANJANG TEKUK STRINGER (ST1-1, ST1-2, ST2-1, ST2-2)")
A(";    Design > Steel Design Parameter > Unbraced Length:  Lz = Lb = 0")
A(";    Plat beton 250 mm dicor di atas stringer sehingga sayap tekan terkekang")
A(";    penuh arah lateral. Tanpa setelan ini midas memakai Lz = 6671 mm")
A(";    (kelangsingan 202) dan stringer akan NG padahal sebenarnya aman.")
A("; 2. Chord atas sudah terkekang ikatan angin atas tiap panel -> Lb = panjang panel.")
A("; 3. TB2 / TB3 (CAT 777, XCMG XT400DT) TIDAK dibuat ulang. Kombinasi yang")
A(";    mengacu keduanya sudah dihapus dari *LOADCOMB.")
A("; 4. Lajur beban bergerak: Lajur 1 (y=2.7 m) dan Lajur 2 (y=4.9 m) berjarak")
A(";    hanya 2.20 m, kurang dari lebar lajur rencana 2.75 m. Perlu diatur")
A(";    eksentrisitasnya, atau pakai beban statik TD-BTR/TD-BGT yang sudah ada.")
A("; 5. Load case MVL belum masuk kombinasi mana pun.")
A("")
A("*ENDDATA"); A("")
txt="\n".join(O)
open('B100_FINAL.mct','w').write(txt.replace("@@@SPLIT@@@\n",""))
i=txt.index("@@@SPLIT@@@")
head=txt[:i]
tail=txt[i+len("@@@SPLIT@@@")+1:]
H="""
;--------------------------------------------------------------------------
;  BAGIAN 1 dari 2 : STRUKTUR SAJA (tanpa data beban)
;  Jembatan Rangka Baja Kelas A - bentang 100 m - BM 100 - lokasi Timor Leste
;
;  File ini AMAN DIJALANKAN BERULANG KALI. Node, elemen, penampang, tumpuan
;  dan rigid link DITIMPA berdasarkan nomornya, jadi tidak pernah bertumpuk.
;
;  Isi : 203 node | 473 elemen | 78 penampang | 4 pot bearing
;        16 rigid link diafragma lantai (8 slave tiap panel = 128 pasangan)
;
;  Perbaikan terhadap model lama:
;    (1) 6 jalur stringer yang semula TIDAK TERSAMBUNG kini tersambung ke
;        gelagar melintang (CG dipecah 8 segmen tiap panel, 32 -> 128 elemen)
;    (2) 11 elemen duplikat dihapus
;    (3) diafragma lantai (pelat beton 250 mm) sebagai Rigid Link bidang XY
;    (4) SELURUH profil penampang asli dipertahankan - tidak ada yang diubah
;
;  URUTAN:  1. File > New di midas
;           2. Run file ini
;           3. Run B100_2_BEBAN.mct  (SATU KALI SAJA)
;--------------------------------------------------------------------------

""".lstrip()
body=head[head.index("*VERSION"):].rstrip()

open('B100_1_STRUKTUR.mct','w').write(H+body+"\n\n*ENDDATA\n")

L="""
;--------------------------------------------------------------------------
;  BAGIAN 2 dari 2 : DATA BEBAN DAN KOMBINASI
;  Jembatan Rangka Baja Kelas A - bentang 100 m - BM 100 - lokasi Timor Leste
;
;  >>> JALANKAN HANYA SATU KALI, SETELAH B100_1_STRUKTUR.mct. <<<
;  midas SELALU MENAMBAHKAN data beban, tidak pernah menimpanya.
;
;  Perlu mengulang? Hapus dulu 13 Static Load Case di
;  Load > Static Load Cases (menghapus case ikut menghapus bebannya),
;  baru jalankan file ini lagi.
;
;  SATUAN: file ini memakai KN, M. Blok yang peka satuan lain
;  (SECTION, MATERIAL, DGN-MATL, LINELANE, VEHICLE) seluruhnya ada di
;  BAGIAN 1 dengan satuan TONF, MM - jangan dipindahkan ke sini.
;
;  CEK SETELAH RUN - jumlah entri harus TEPAT:
;    MS 105 beam + Self Weight | MA 105 | TD-BTR 105 | TD-BGT 7 nodal
;    TB1 30 beam + 4 nodal     | TP 30  | EWS 58     | EWL 60 | EWV 30
;    EUN / EUN-N 473 temper    | EQX & EQY 473 beam + 112 nodal
;  Bila MS menunjukkan 210, beban bertumpuk - hapus semua load case, ulangi.
;--------------------------------------------------------------------------

""".lstrip()
open('B100_2_BEBAN.mct','w').write(L+tail)

print("baris gabungan:",len(O))

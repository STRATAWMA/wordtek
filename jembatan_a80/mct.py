# -*- coding: utf-8 -*-
"""A80 - MCT model elemen hingga jembatan rangka pelengkung bentang 80 m.
Sumber: APPROVAL DRAWING GA-ITK09 rev 1, PT Indo Trans Konstruksi."""
import math, collections
from geom import L,NP,A,B,YS,zT,zM,dep

NDIV=4                      # pembagian panel untuk lantai -> 1250 mm
XP=[A*i for i in range(NP+1)]                 # titik buhul pelengkung
XD=[A*i/NDIV for i in range(NP*NDIV+1)]       # stasiun lantai
TSLAB=250.0; ZOFF=381.0; FC=30.0
WROAD=7000.0; WTROT=1500.0                    # ASUMSI - lihat catatan
Y0R=(B-WROAD)/2; Y1R=Y0R+WROAD                # 1500 .. 8500

N={}; ORD=[]; _n=[0]
CO={}
def nd(x,y,z):
    k=(round(x,1),round(y,1),round(z,1))
    if k not in N:
        _n[0]+=1; N[k]=_n[0]; ORD.append((_n[0],k)); CO[_n[0]]=k
    return N[k]
E=[]; _e=[0]
def el(sec,n1,n2,mat=1):
    _e[0]+=1; E.append((_e[0],mat,sec,n1,n2)); return _e[0]
PLA=[]; _p=[4999]
def plt(a,b,c,d):
    _p[0]+=1; PLA.append((_p[0],a,b,c,d)); return _p[0]
G=collections.defaultdict(list)
SIDES=[0.0,B]; YALL=[0.0]+YS+[B]

# --------- simpul ---------
tie={}; mch={}; tch={}
for s in SIDES:
    for i,x in enumerate(XD): tie[(s,i)]=nd(x,s,0.0)
    for i,x in enumerate(XP):
        k=i*NDIV
        mch[(s,i)]= tie[(s,k)] if i in (0,NP) else nd(x,s,zM(x))
        tch[(s,i)]= tie[(s,k)] if i in (0,NP) else nd(x,s,zT(x))
st={}
for y in YS:
    for i,x in enumerate(XD): st[(y,i)]=nd(x,y,0.0)
deck={}
for i,x in enumerate(XD):
    for y in YALL:
        deck[(i,y)] = tie[(0.0,i)] if y==0.0 else (tie[(B,i)] if y==B else st[(y,i)])
slab={}
for i,x in enumerate(XD):
    for y in YALL: slab[(i,y)]=nd(x,y,ZOFF)

# --------- batang ---------
for s in SIDES:
    for i in range(len(XD)-1): G['TIE'].append(el(1,tie[(s,i)],tie[(s,i+1)]))
    for i in range(NP):
        se=2 if i in (0,NP-1) else 3
        G['T-CHORD'].append(el(se,tch[(s,i)],tch[(s,i+1)]))
        G['M-CHORD'].append(el(se,mch[(s,i)],mch[(s,i+1)]))
    for i in range(1,NP):
        G['ARCH-VERT'].append(el(5,tch[(s,i)],mch[(s,i)]))
        G['HANGER'].append(el(4,mch[(s,i)],tie[(s,i*NDIV)]))
    for i in range(1,NP-1):
        a,b2=(i,i+1) if i<NP//2 else (i+1,i)
        G['ARCH-DIAG'].append(el(5,tch[(s,a)],mch[(s,b2)]))
for i in range(len(XD)):
    if i%NDIV: continue
    p=[deck[(i,y)] for y in YALL]
    for a,b2 in zip(p[:-1],p[1:]): G['CROSSGIRDER'].append(el(6,a,b2))
for y in YS:
    for i in range(len(XD)-1): G['STRINGER'].append(el(7,st[(y,i)],st[(y,i+1)]))
# Ikatan angin silang DISAMBUNG DI TITIK SILANGAN (lihat DET-21 pada
# SECTION A). Tanpa sambungan itu diagonal jadi 11,66 m menerus dan
# KL/r = 208 > 120, batas AASHTO 6.9.3 - batang langsing semu.
def xbrace(a1,a2,b1,b2,nm):
    """dua diagonal silang a1-a2 dan b1-b2, disambung di perpotongan"""
    ca,cb=CO[a1],CO[a2]
    mid=nd((ca[0]+cb[0])/2,(ca[1]+cb[1])/2,(ca[2]+cb[2])/2)
    for u in (a1,a2,b1,b2): G[nm].append(el(8,u,mid,2))
    return mid
for dic,nm,zf in ((tch,'HB-TOP',zT),(mch,'HB-MID',zM)):
    for i in range(1,NP): G[nm].append(el(8,dic[(0.0,i)],dic[(B,i)],2))
    for i in range(1,NP-1):
        xbrace(dic[(0.0,i)],dic[(B,i+1)],dic[(B,i)],dic[(0.0,i+1)],nm)
for i in range(1,NP):
    xbrace(tch[(0.0,i)],mch[(B,i)],tch[(B,i)],mch[(0.0,i)],'VB-FRAME')
for i in (0,len(XD)-1): G['LAT-STOP'].append(el(9,tie[(0.0,i)],tie[(B,i)]))
for i in range(len(XD)-1):
    for j in range(len(YALL)-1):
        plt(slab[(i,YALL[j])],slab[(i+1,YALL[j])],slab[(i+1,YALL[j+1])],slab[(i,YALL[j+1])])
RL=[(deck[(i,y)],slab[(i,y)]) for i in range(len(XD)) for y in YALL]

# --------- penampang ---------
SEC={1:("B-TIE","H",(1000,400,20,30)),2:("ARCH-END","H",(400,500,20,30)),
     3:("ARCH","H",(400,350,20,30)),4:("HANGER","H",(400,250,12,20)),
     5:("ARCH-WEB","H",(400,200,12,20)),6:("CROSSGIRDER","H",(550,400,20,30)),
     7:("STRINGER","H",(450,220,8,12)),8:("PIPE6","P",(165.2,7.1)),
     9:("LAT-STOP","H",(850,400,10,20))}

# --------- beban (SNI 1725-2016, Kelas A, L=80 m) ---------
qBTR = 9.0*(0.5+15.0/(L/1000.0))
FBD  = 0.4 if L/1000<=50 else (0.3 if L/1000>=90 else 0.4-0.1*(L/1000-50)/40)
qBGT = 49.0*(1+FBD)
qSLB = TSLAB/1000*25.0; qASP = 0.05*22.0; qPED = 5.0
def trib_y(j):
    lo=(YALL[j-1]+YALL[j])/2 if j>0 else YALL[0]
    hi=(YALL[j]+YALL[j+1])/2 if j<len(YALL)-1 else YALL[-1]
    return lo,hi
def trib_x(i):
    lo=(XD[i-1]+XD[i])/2 if i>0 else XD[0]
    hi=(XD[i]+XD[i+1])/2 if i<len(XD)-1 else XD[-1]
    return (hi-lo)/1000.0
def nodal(strips,line_w=0.0):
    d={}
    for i in range(len(XD)):
        ax=trib_x(i)
        for j,y in enumerate(YALL):
            lo,hi=trib_y(j); P=0.0
            for a,b2,q in strips: P+=q*max(0.0,min(hi,b2)-max(lo,a))/1000.0
            P*=ax
            if line_w and y in (YALL[0],YALL[-1]): P+=line_w*ax
            if P>1e-9: d[slab[(i,y)]]=P
    return d
def nodal_line(strips,i):
    d={}
    for j,y in enumerate(YALL):
        lo,hi=trib_y(j); P=0.0
        for a,b2,q in strips: P+=q*max(0.0,min(hi,b2)-max(lo,a))/1000.0
        if P>1e-9: d[slab[(i,y)]]=P
    return d
S_TROT=[(0.0,Y0R,qPED*0+0.30*25),(Y1R,B,0.30*25)]      # trotoar beton 300 mm
S_ASP =[(Y0R,Y1R,qASP)]
w100=5500.0; m=(Y0R+Y1R)/2
S_BTR =[(Y0R,m-w100/2,qBTR*0.5),(m-w100/2,m+w100/2,qBTR),(m+w100/2,Y1R,qBTR*0.5)]
S_BGT =[(Y0R,m-w100/2,qBGT*0.5),(m-w100/2,m+w100/2,qBGT),(m+w100/2,Y1R,qBGT*0.5)]
S_TP  =[(0.0,Y0R,qPED),(Y1R,B,qPED)]
LD={'MS':nodal(S_TROT),'MA':nodal(S_ASP,line_w=0.5),'TD-BTR':nodal(S_BTR),
    'TD-BGT':nodal_line(S_BGT,len(XD)//2),'TP':nodal(S_TP)}
print("qBTR %.4f kPa | FBD %.3f | qBGT %.3f kN/m"%(qBTR,FBD,qBGT))
for k,v in LD.items(): print("   %-7s %8.1f kN"%(k,sum(v.values())))
import json; json.dump({'ok':1},open('_ok.json','w'))

# ================= TULIS MCT =================
OUT='A80_PELENGKUNG_FEM.mct'
Lm=L/1000.0
O=[]; W=O.append
def hdr(t): W(""); W(";"+"-"*74); W("; "+t); W(";"+"-"*74)
W("; A80 - JEMBATAN RANGKA PELENGKUNG KELAS A BENTANG 80 METER")
W("; Model elemen hingga. Dibuat dari APPROVAL DRAWING GA-ITK09 rev 1.")
W("; Geometri pelengkung dari SECTION A-G (titik buhul 2-8); titik 1 dan 0")
W("; hasil ekstrapolasi kurva, yang memberi z = -33 mm di x=0 sehingga")
W("; pelengkung bertumpu tepat pada level balok tarik.")
W("*VERSION"); W("   8.7.5"); W("")
W("*UNIT"); W("; FORCE, LENGTH, HEAT, TEMPER"); W("   TONF, MM, BTU, C"); W("")
W("*PROJINFO"); W("   PROJECT=Jembatan Rangka Pelengkung Kelas A - Bentang 80 m")
W("   CLIENT=PT Indo Trans Konstruksi"); W("")
W("*STRUCTYPE")
W("; iSTYP, iMASS, iSMAS, bMASSOFFSET, bSELFWEIGHT, GRAV, TEMPER, bALIGNBEAM, bALIGNSLAB, bROTRIGID")
W("     0, 1, 1, NO, YES, 9810, 0, NO, NO, NO"); W("")
hdr("SIMPUL  %d"%len(ORD))
W("*NODE"); W("; iNO, X, Y, Z")
for n,(x,y,z) in ORD: W("   %d, %.4f, %.4f, %.4f"%(n,x,y,z))
hdr("ELEMEN  %d batang + %d pelat lantai"%(len(E),len(PLA)))
W("*ELEMENT")
W("; iEL, TYPE, iMAT, iPRO, iN1, iN2, ANGLE, iSUB")
for i,m,s,a,b2 in E: W("   %d, BEAM  , %d, %d, %d, %d, 0, 0"%(i,m,s,a,b2))
W("; iEL, TYPE, iMAT, iPRO, iN1, iN2, iN3, iN4, iSUB(1=Thick), iWID, LCAXIS")
for p,a,b2,c,d in PLA: W("   %d, PLATE , 3, 1, %d, %d, %d, %d, 1, 0, 0"%(p,a,b2,c,d))
hdr("MATERIAL")
W("*MATERIAL")
W("; iMAT, TYPE, MNAME, SPHEAT, HEATCO, PLAST, TUNIT, bMASS, DAMPRATIO, [DATA1]")
W("    1, STEEL, SM490YB           , 0, 0, , C, NO, 0.02, 2, 2.0904e+001,   0.3, 1.2000e-005, 8.00477e-009,     0")
W("    2, STEEL, STK41             , 0, 0, , C, NO, 0.02, 2, 2.0904e+001,   0.3, 1.2000e-005, 8.00477e-009,     0")
Ec=4700*math.sqrt(FC)
W("; beton lantai fc' = %.0f MPa, E = %.0f MPa, 25 kN/m3"%(FC,Ec))
W("    3, CONC , C%d               , 0, 0, , C, NO, 0.05, 2, %.4fe+001, 0.2, 1.0000e-005, 2.54929e-009,     0"%(FC,Ec/9806.65/10))
hdr("PENAMPANG")
W("*SECTION"); W("; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE, [DATA]")
for i in sorted(SEC):
    nm,sh,d=SEC[i]
    p=("%g, %g, 0, 0, 0, 0, 0, 0, 0, 0"%d) if sh=='P' else ("%g, %g, %g, %g, 0, 0, 0, 0, 0, 0"%d)
    W("   %d, DBUSER    , %-18s, CC, 0, 0, 0, 0, 0, 0, YES, NO, %s  , 2, %s"%(i,nm,sh,p))
W(""); W("*THICKNESS"); W("; iTHK, TYPE, bSAME, THIK-IN, THIK-OUT, bOFFSET, OFFTYPE, VALUE")
W("    1, VALUE, YES, %.0f, 0,  NO, 0, 0"%TSLAB)
hdr("MUTU BAJA - SM490YB: fy 365 MPa (t<=16), 355 MPa (t>16), fu 490 MPa")
K=9.80665e3; tail=("2, 0, , , , 0, 0,NO,0.0000e+000,     0,"+", 0, 0,0"*5)
W("*DGN-MATL")
W("; iMAT, TYPE, MNAME, 2, ELAST, POISN, FU, FY1..FY6, AFT, AFT2, AFT3, FY, AFV..")
W("    1, STEEL, SM490YB           , 2, 2.0904e+001,   0.3, %.10f, %.10f, %.10f, %.10f, %.10f, %.10f, %.10f, 16, 40, 100, %.10f, 0, 0, 0, 0, %s"
  %(490/K,365/K,355/K,355/K,355/K,355/K,355/K,355/K,tail))
W("    2, STEEL, STK41             , 2, 2.0904e+001,   0.3, %.10f, %.10f, %.10f, %.10f, %.10f, %.10f, %.10f, 0, 0, 0, %.10f, 0, 0, 0, 0, %s"
  %(402/K,235/K,235/K,235/K,235/K,235/K,235/K,235/K,tail))
W(""); W("*DGN-STEEL"); W("; CODE=CODE, bBRACED, bDEFLECT, iWTL")
W("   CODE=AASHTO-LRFD12, YES, YES, 0"); W("   0, 0, 0, 0, 0")
hdr("PERLETAKAN - elastomeric bearing (AS 1532-1981), 4 titik")
W("*CONSTRAINT"); W("; NODE_LIST, CONST(Dx,Dy,Dz,Rx,Ry,Rz), GROUP")
W("   %d, 111000, "%tie[(0.0,0)]);          W("   %d, 101000, "%tie[(B,0)])
W("   %d, 011000, "%tie[(0.0,len(XD)-1)]);  W("   %d, 001000, "%tie[(B,len(XD)-1)])
hdr("RIGID LINK - aksi komposit pelat lantai, lengan %.0f mm"%ZOFF)
W("*RIGIDLINK"); W("; iNO, MASTER_NODE, DOF, S_NODE_LIST, GROUP")
for i,(m,s) in enumerate(sorted(RL),1): W("   %d, %d, 111111, %d, "%(i,m,s))
W(""); W("; ---- mulai di sini satuan pindah ke KN, M untuk DATA BEBAN ----")
W("*UNIT"); W("; FORCE, LENGTH, HEAT, TEMPER"); W("   KN, M, BTU, C")
hdr("LOAD CASE")
W("*STLDCASE"); W("; LCNAME, LCTYPE, DESC")
for n,t,d in [("MS","D","Berat sendiri baja + pelat lantai %.0f mm + trotoar 300 mm"%TSLAB),
 ("MA","D","Aspal 50 mm + sandaran"),
 ("TD-BTR","L","Lajur D - BTR %.4f kPa (SNI 1725 ps.8.3.1)"%qBTR),
 ("TD-BGT","L","Lajur D - BGT 49 x (1+%.3f) = %.3f kN/m"%(FBD,qBGT)),
 ("TB1","L","Gaya rem 250 kN (SNI 1725 ps.8.7)"),
 ("TP","L","Pejalan kaki 5 kPa pada trotoar"),
 ("EWS","W","Angin pada struktur PD = 2.4 kPa"),
 ("EWL","W","Angin pada kendaraan 1.46 kN/m"),
 ("EWV","W","Angin vertikal 0.96 kPa x lebar"),
 ("EUN","T","Suhu seragam naik +15 C"),("EUN-N","T","Suhu seragam turun -15 C")]:
    W("   %-7s, %s, %s"%(n,t,d))
def conload(d,note):
    W("*CONLOAD"); W("; NODE_LIST, FX, FY, FZ, MX, MY, MZ, GROUP"); W("; "+note)
    g=collections.defaultdict(list)
    for n,v in d.items(): g[round(v,4)].append(n)
    def rng(ids):
        ids=sorted(set(ids)); o=[];i=0
        while i<len(ids):
            j=i
            while j+1<len(ids) and ids[j+1]==ids[j]+1: j+=1
            o.append(str(ids[i]) if i==j else "%dto%d"%(ids[i],ids[j])); i=j+1
        return " ".join(o)
    for v in sorted(g,reverse=True): W("   %s, 0, 0, %.4f, 0, 0, 0, "%(rng(g[v]),-v))
def rng(ids):
    ids=sorted(set(ids)); o=[];i=0
    while i<len(ids):
        j=i
        while j+1<len(ids) and ids[j+1]==ids[j]+1: j+=1
        o.append(str(ids[i]) if i==j else "%dto%d"%(ids[i],ids[j])); i=j+1
    return " ".join(o)
def bl(els,p,dr="GZ",sg=-1):
    return ("   %s, BEAM, UNILOAD, %s, NO, NO, LZ, 0, 0, NO, 0, %.4f, 1, %.4f, 0, 0, 0, 0, "
            %(els,dr,sg*p,sg*p))
hdr("DATA BEBAN - jalankan SATU KALI saja")
W(""); W("*USE-STLD, MS"); W("*SELFWEIGHT, 0, 0, -1, ")
conload(LD['MS'],"beton trotoar 300 mm; berat pelat %.0f mm dari *SELFWEIGHT"%TSLAB)
W(""); W("*USE-STLD, MA");     conload(LD['MA'],"aspal 50 mm pada jalur + sandaran 0.5 kN/m")
W(""); W("*USE-STLD, TD-BTR"); conload(LD['TD-BTR'],"BTR 100%% pada 5.5 m tengah + 50%% sisanya")
W(""); W("*USE-STLD, TD-BGT"); conload(LD['TD-BGT'],"BGT garis pisau di tengah bentang")
W(""); W("*USE-STLD, TP");     conload(LD['TP'],"pejalan kaki 5 kPa, trotoar 2 x %.1f m"%(WTROT/1000))
TB=250.0
W(""); W("*USE-STLD, TB1"); W("*BEAMLOAD")
W("; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], D1, P1, D2, P2, D3, P3, D4, P4, GROUP")
W("; gaya rem %.0f kN dibagi 2 balok tarik"%TB)
W(bl(rng(G['TIE']),TB/2/Lm,"GX",+1))
# angin
Aarch=0.400; PD=2.4
W(""); W("*USE-STLD, EWS"); W("*BEAMLOAD")
W("; PD 2.4 kPa x tinggi profil: chord pelengkung dan balok tarik")
W(bl(rng(G['T-CHORD']+G['M-CHORD']),PD*Aarch,"GY",+1))
W(bl(rng(G['TIE']),PD*1.000,"GY",+1))
W(""); W("*USE-STLD, EWL"); W("*BEAMLOAD")
W("; angin kendaraan 1.46 kN/m dibagi 2 balok tarik")
W(bl(rng(G['TIE']),1.46/2,"GY",+1))
W(""); W("*USE-STLD, EWV"); W("*BEAMLOAD")
W("; angin vertikal ke atas 0.96 kPa x %.1f m dibagi 2 balok tarik"%(B/1000))
W(bl(rng(G['TIE']),0.96*B/1000/2,"GZ",+1))
for nm,dT in (("EUN",15.0),("EUN-N",-15.0)):
    W(""); W("*USE-STLD, %s"%nm); W("*ELTEMPER"); W("; ELEM_LIST, TEMPER, GROUP")
    W("   %s, %.1f, "%(rng([e[0] for e in E]),dT))
hdr("KOMBINASI BEBAN - SNI 1725-2016 Tabel 1")
W("*LOADCOMB"); W("; NAME=NAME, KIND, ACTIVE, bES, iTYPE, DESC, iSERV-TYPE, nLCOMTYPE")
CB=[("KUAT I","STRENGTH",[("MS",1.1),("MA",1.4),("TD-BTR",1.8),("TD-BGT",1.8),("TP",1.8),("TB1",1.8),("EUN",0.5)]),
 ("KUAT III","STRENGTH",[("MS",1.1),("MA",1.4),("EWS",1.4),("EWV",1.4),("EUN",0.5)]),
 ("KUAT III-MIN","STRENGTH",[("MS",0.9),("MA",0.7),("EWS",1.4),("EWV",1.4)]),
 ("KUAT IV","STRENGTH",[("MS",1.1),("MA",1.4),("EUN",0.5)]),
 ("KUAT V","STRENGTH",[("MS",1.1),("MA",1.4),("EWS",0.4),("EWL",1.0),("EUN",0.5)]),
 ("LAYAN I","SERVICE",[("MS",1.0),("MA",1.0),("TD-BTR",1.0),("TD-BGT",1.0),("TP",1.0),("TB1",1.0),("EWS",0.3),("EWL",1.0),("EUN",1.0)]),
 ("LAYAN II","SERVICE",[("MS",1.0),("MA",1.0),("TD-BTR",1.3),("TD-BGT",1.3),("TB1",1.3),("EUN",1.0)]),
 ("LAYAN IV","SERVICE",[("MS",1.0),("MA",1.0),("EWS",0.7),("EWV",0.7),("EUN",1.0)]),
 ("LENDUT-TD","SERVICE",[("TD-BTR",1.0),("TD-BGT",1.0)])]
for nm,kd,t in CB:
    W("   NAME=%s, STEEL, %s, 0, 0, SNI 1725-2016 Tabel 1, 0, 0"%(nm,kd))
    for k in range(0,len(t),5):
        W("        "+", ".join("ST, %s, %g"%(a,b2) for a,b2 in t[k:k+5]))
W(""); W("*ENDDATA")
open(OUT,'w').write("\n".join(O)+"\n")
print("\ntulis %s : %d baris | simpul %d | batang %d | pelat %d | rigid link %d"
      %(OUT,len(O),len(ORD),len(E),len(PLA),len(RL)))

import re
S=open("A80_PELENGKUNG_FEM.mct").read().split("\n")
HL=["*VERSION","   8.7.5","","*UNIT","; FORCE, LENGTH, HEAT, TEMPER","   KN, M, BTU, C",""]

def hdr(i,n,ket):
    return ["; ====================================================================",
            "; A80 JEMBATAN PELENGKUNG 80 m - BAGIAN %s dari %s"%(i,n),
            "; %s"%ket,
            "; ===================================================================="
            ,""]+HL

# ---------- P6: DESC dibersihkan dari karakter khusus MCT ----------
def clean(d):
    d=d.replace("="," ").replace("("," ").replace(")"," ").replace("+","plus ")
    d=re.sub(r"[^A-Za-z0-9 ./-]"," ",d)
    return re.sub(r"\s+"," ",d).strip()

cases=[]
for l in S[6470:6486]:
    if l.strip() and not l.lstrip().startswith(";"):
        p=l.split(",",2)
        cases.append((p[0].strip(),p[1].strip(),clean(p[2])))
out=hdr(6,"8+","STLDCASE - 13 kasus beban. DESC dibuat polos tanpa = ( ) +")
out+=["*STLDCASE","; LCNAME, LCTYPE, DESC"]
for n,t,d in cases: out.append("   %-7s, %s, %s"%(n,t,d))
open("A80_P6_LOADCASE.mct","w").write("\n".join(out+["","*ENDDATA",""]))

# ---------- P7: pecah per kelompok + potong baris panjang ----------
MAXTOK=12
def wrap(line):
    """potong daftar simpul/elemen jadi beberapa baris, nilai beban sama"""
    f=line.split(",")
    toks=f[0].split()
    rest=",".join(f[1:])
    if len(toks)<=MAXTOK: return [line]
    o=[]
    for k in range(0,len(toks),MAXTOK):
        o.append("   "+" ".join(toks[k:k+MAXTOK])+","+rest)
    return o

# kumpulkan blok per load case
body={}; cur=None; sub=[]
for l in S[6489:6766]:
    if l.startswith("*USE-STLD"):
        cur=l.split(",",1)[1].strip(); body[cur]=[]; continue
    if cur is None: continue
    body[cur].append(l)

GRUP=[("A","MATI",["MS","MA"],"Beban mati - berat sendiri, pelat, trotoar, aspal, sandaran"),
      ("B","LALULINTAS",["TD-BTR","TD-BGT","TP","TB1"],"Lalu lintas - BTR, BGT, pejalan kaki, gaya rem"),
      ("C","ANGIN",["EWS","EWL","EWV"],"Angin - struktur, kendaraan, vertikal"),
      ("D","SUHU",["EUN","EUN-N"],"Suhu seragam naik dan turun"),
      ("E","GEMPA",["EQX","EQY"],"Gempa Timor Leste - SNI 2833-2016 koef 0.4500")]
mx=0
for tag,nm,ks,ket in GRUP:
    o=hdr("7"+tag,"8+",ket+" - JALANKAN SATU KALI")
    for k in ks:
        o.append("*USE-STLD, %s"%k)
        blk=None
        for l in body[k]:
            if l.startswith("*"): blk=l.split(",")[0].strip(); o.append(l); continue
            if not l.strip() or l.lstrip().startswith(";"): o.append(l); continue
            o+= wrap(l) if blk in("*CONLOAD","*BEAMLOAD","*ELTEMPER") else [l]
        o.append("")
    while o and not o[-1].strip(): o.pop()
    fn="A80_P7%s_BEBAN_%s.mct"%(tag,nm)
    t=o+["","*ENDDATA",""]
    open(fn,"w").write("\n".join(t))
    m=max(len(x) for x in t); mx=max(mx,m)
    print("%-32s %4d baris  baris terpanjang %4d" % (fn,len(t),m))
import os; os.remove("A80_P7_BEBAN.mct")
print("baris terpanjang keseluruhan:",mx)

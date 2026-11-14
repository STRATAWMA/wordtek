import re
S=open("A80_PELENGKUNG_FEM.mct").read().split("\n")
def L(a,b): return S[a-1:b]
HS=["*VERSION","   8.7.5","","*UNIT","; FORCE, LENGTH, HEAT, TEMPER","   TONF, MM, BTU, C",""]
HL=["*VERSION","   8.7.5","","*UNIT","; FORCE, LENGTH, HEAT, TEMPER","   KN, M, BTU, C",""]
def wr(fn,tag,ket,hdr,body):
    while body and not body[-1].strip(): body.pop()
    t=["; ====================================================================",
       "; A80 JEMBATAN PELENGKUNG 80 m - BAGIAN %s   (revisi 4)"%tag,
       "; %s"%ket,
       "; --------------------------------------------------------------------",
       "; PENTING - JALANKAN DI MODEL KOSONG (File > New Project).",
       ";",
       "; Revisi ini MENGURANGI jumlah batang dan simpul:",
       ";    batang  1206 -> 1120      simpul  2621 -> 2578",
       "; midas MENIMPA berdasarkan nomor, tetapi TIDAK menghapus nomor yang",
       "; tidak lagi dipakai. Kalau dijalankan di atas model revisi 3, akan",
       "; TERTINGGAL dan menumpuk:",
       ";    batang 1121..1206  = 86 pipa bracing lama  -> bracing DOBEL",
       ";    simpul 2579..2621  = 43 simpul perpotongan -> simpul yatim",
       ";",
       "; Kalau tetap mau memakai model lama: hapus dulu batang 1121-1206 dan",
       "; simpul 2579-2621, lalu jalankan P1..P5. Pelat (5000-6623) dan rigid",
       "; link tertimpa seluruhnya, tidak ada sisa.",
       "; --------------------------------------------------------------------",
       "; Urutan: P1 P2 P3 P4 P5 P6 P7A P7B P7C P7D P7E P8. P6/P7 SEKALI saja.",
       "; ====================================================================",""]+hdr+body+["","*ENDDATA",""]
    open(fn,"w").write("\n".join(t)); print("%-32s %5d baris  terpanjang %4d"%(fn,len(t),max(len(x) for x in t)))

wr("A80_P1_PROPERTI.mct","1","STRUCTYPE MATERIAL SECTION THICKNESS DGN-MATL DGN-STEEL",HS,L(13,24)+[""]+L(5360,5408))
wr("A80_P2_SIMPUL.mct","2","NODE - 2578 simpul",HS,L(25,2608))
wr("A80_P3_ELEMEN_FRAME.mct","3","ELEMENT - 1120 batang (974 BEAM + 146 TRUSS)",HS,L(2609,3731))
wr("A80_P4_ELEMEN_PLAT.mct","4","ELEMENT - 1624 pelat",HS,
   ["*ELEMENT","; iEL, TYPE, iMAT, iPRO, iN1, iN2, iN3, iN4, iSUB, iWID, LCAXIS"]+L(3732,5359))
wr("A80_P5_TUMPUAN.mct","5","CONSTRAINT 4 titik + RIGIDLINK 915 pasang",HS,L(5409,6337))

cases=[]
for l in L(6345,6364):
    if l.strip() and not l.lstrip().startswith(";") and not l.startswith("*"):
        p=l.split(",",2); cases.append("   %-7s, %s, %s"%(p[0].strip(),p[1].strip(),
            re.sub(r"\s+"," ",re.sub(r"[^A-Za-z0-9 ./-]"," ",p[2])).strip()))
wr("A80_P6_LOADCASE.mct","6","STLDCASE - 13 kasus beban",HL,["*STLDCASE","; LCNAME, LCTYPE, DESC"]+cases)

body={};cur=None
for l in L(6365,6599):
    if l.startswith("*USE-STLD"): cur=l.split(",",1)[1].strip(); body[cur]=[]; continue
    if cur: body[cur].append(l)
MAX=12
def wrap(l):
    f=l.split(","); tk=f[0].split(); rest=",".join(f[1:])
    return [l] if len(tk)<=MAX else ["   "+" ".join(tk[k:k+MAX])+","+rest for k in range(0,len(tk),MAX)]
for tag,nm,ks,ket in [("7A","MATI",["MS","MA"],"Beban mati"),
                      ("7B","LALULINTAS",["TD-BTR","TD-BGT","TP","TB1"],"Lalu lintas BTR BGT pejalan kaki rem"),
                      ("7C","ANGIN",["EWS","EWL","EWV"],"Angin struktur kendaraan vertikal"),
                      ("7D","SUHU",["EUN","EUN-N"],"Suhu seragam naik dan turun"),
                      ("7E","GEMPA",["EQX","EQY"],"Gempa Timor Leste koef 0.4500")]:
    o=[];blk=None
    for k in ks:
        o.append("*USE-STLD, %s"%k)
        for l in body[k]:
            if l.startswith("*"): blk=l.split(",")[0].strip(); o.append(l)
            elif not l.strip() or l.lstrip().startswith(";"): o.append(l)
            else: o+= wrap(l) if blk in("*CONLOAD","*BEAMLOAD","*ELTEMPER") else [l]
        o.append("")
    wr("A80_P%s_BEBAN_%s.mct"%(tag,nm),tag,ket+" - JALANKAN SEKALI",HL,o)
wr("A80_P8_KOMBINASI.mct","8","LOADCOMB - 11 kombinasi",HL,L(6600,6627))

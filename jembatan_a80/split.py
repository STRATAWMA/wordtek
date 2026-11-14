import io
S=open("A80_PELENGKUNG_FEM.mct").read().split("\n")
def L(a,b): return S[a-1:b]          # 1-based inklusif

HSTR=["*VERSION","   8.7.5","","*UNIT","; FORCE, LENGTH, HEAT, TEMPER","   TONF, MM, BTU, C",""]
HLOD=["*VERSION","   8.7.5","","*UNIT","; FORCE, LENGTH, HEAT, TEMPER","   KN, M, BTU, C",""]
EHDR="; iEL, TYPE, iMAT, iPRO, iN1, iN2, ANGLE, iSUB"

PARTS=[
 ("A80_P1_PROPERTI.mct", HSTR, L(13,24)+[""]+L(5489,5537),
  "MATERIAL / SECTION / THICKNESS / DGN-MATL / DGN-STEEL + STRUCTYPE"),
 ("A80_P2_SIMPUL.mct",   HSTR, L(25,2651),
  "NODE - 2621 simpul"),
 ("A80_P3_ELEMEN_FRAME.mct", HSTR, L(2652,3860),
  "ELEMENT - 1206 batang BEAM/TRUSS"),
 ("A80_P4_ELEMEN_PLAT.mct",  HSTR, ["*ELEMENT",
  "; iEL, TYPE, iMAT, iPRO, iN1, iN2, iN3, iN4, iSUB, iWID, LCAXIS"]+L(3861,5488),
  "ELEMENT - 1624 pelat PLATE"),
 ("A80_P5_TUMPUAN.mct",  HSTR, L(5538,6462),
  "CONSTRAINT 4 titik + RIGIDLINK 911 pasang"),
 ("A80_P6_LOADCASE.mct", HLOD, L(6468,6489),
  "STLDCASE - 13 kasus beban (nama saja, belum ada data)"),
 ("A80_P7_BEBAN.mct",    HLOD, L(6490,6766),
  "DATA BEBAN - SELFWEIGHT/CONLOAD/BEAMLOAD/ELTEMPER"),
 ("A80_P8_KOMBINASI.mct",HLOD, L(6767,6794),
  "LOADCOMB - 11 kombinasi"),
]
for i,(fn,hdr,body,ket) in enumerate(PARTS,1):
    while body and not body[-1].strip(): body.pop()
    t=["; ====================================================================",
       "; A80 JEMBATAN PELENGKUNG 80 m - BAGIAN %d dari %d"%(i,len(PARTS)),
       "; %s"%ket,
       "; Jalankan BERURUTAN P1 -> P8 lewat MCT Command Shell.",
       "; ===================================================================="
       ,""]+hdr+body+["","*ENDDATA",""]
    open(fn,"w").write("\n".join(t))
    print("%-26s %5d baris" % (fn,len(t)))

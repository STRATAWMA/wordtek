# -*- coding: utf-8 -*-
"""Model SHELL kaki pelengkung A80 (x = 0 .. 10000, kedua rangka).

Geometri plat diukur dari gambar vektor DETAIL 3/4/5 lembar GA-ITK09-04,
skala 1:30. Kalibrasi: lebar hanger A80-H16 tergambar 23,5 pt; 23,5 x 0,3528
x 30 = 248,6 mm terhadap 250 mm sebenarnya (WB400x250x12x20) -> 1 pt =
10,584 mm, yaitu 1:30 tepat. Ukuran panjang/lebar plat karena itu teliti
sekitar +-1%; TEBAL plat diambil dari MATERIAL LIST (semua PLATE BUHUL =
PL20) jadi tepat.
"""
from geom import L,NP,A,B,zT,zM,dep

XFOOT   = 10000.0        # batas daerah shell
NX      = 8              # pembagian sepanjang x tiap panel 5000 -> 625 mm
NZ_W    = 6              # baris mesh pada baji pelengkung
TIE_D   = 1000.0; TIE_TF=30.0; TIE_TW=20.0; TIE_BF=400.0
CH_TF   = 30.0; CH_TW=20.0; CH_BF=350.0    # chord pelengkung WB400x350x20x30
GUSSET  = 20.0                             # PLATE BUHUL - MATERIAL LIST
HNG_TW  = 12.0

def wedge_rows(x):
    """baris simpul pada baji antara chord TENGAH dan chord ATAS di stasiun x"""
    lo,hi = zM(x), zT(x)
    if hi-lo < 1.0: return [lo]
    return [lo + (hi-lo)*k/NZ_W for k in range(NZ_W+1)]

def build(nd, plate, beam, rlink, side):
    """Tambahkan mesh shell kaki pelengkung pada bidang y = side."""
    nxt = int(XFOOT/ (A/NX))
    XS  = [ (A/NX)*i for i in range(nxt+1) ]
    # ---- baji pelengkung: chord TENGAH .. chord ATAS ----
    grid={}
    for i,x in enumerate(XS):
        for k,z in enumerate(wedge_rows(x)): grid[(i,k)]=nd(x,side,z)
    for i in range(len(XS)-1):
        ra,rb=wedge_rows(XS[i]),wedge_rows(XS[i+1])
        if len(ra)==1:                       # ujung lancip di tumpuan
            for k in range(len(rb)-1):
                plate(grid[(i,0)],grid[(i+1,k)],grid[(i+1,k+1)],grid[(i,0)],GUSSET*2+CH_TW)
            continue
        for k in range(NZ_W):
            plate(grid[(i,k)],grid[(i+1,k)],grid[(i+1,k+1)],grid[(i,k+1)],
                  GUSSET*2+CH_TW if XS[i]<A else CH_TW)
    # sayap chord ATAS dan chord TENGAH sebagai batang tepi
    for i in range(len(XS)-1):
        beam(grid[(i,NZ_W if len(wedge_rows(XS[i]))>1 else 0)],
             grid[(i+1,NZ_W)], 'FLANGE-CH')
        beam(grid[(i,0)],grid[(i+1,0)],'FLANGE-CH')
    # ---- balok tarik: badan sebagai shell ----
    zt=[-TIE_D/2+TIE_TF + (TIE_D-2*TIE_TF)*k/4 for k in range(5)]
    tg={}
    for i,x in enumerate(XS):
        for k,z in enumerate(zt): tg[(i,k)]=nd(x,side,z)
    for i in range(len(XS)-1):
        for k in range(4):
            plate(tg[(i,k)],tg[(i+1,k)],tg[(i+1,k+1)],tg[(i,k+1)],TIE_TW)
    for i in range(len(XS)-1):
        beam(tg[(i,0)],tg[(i+1,0)],'FLANGE-TIE')
        beam(tg[(i,4)],tg[(i+1,4)],'FLANGE-TIE')
    # ---- hanger A80-H16 di x = 5000 : badan shell ----
    ih=int(A/(A/NX))
    zb=zt[-1]; ztop=zM(A)
    nh=6
    hcol=[[nd(A-125.0,side,zb+(ztop-zb)*k/nh) for k in range(nh+1)],
          [nd(A+125.0,side,zb+(ztop-zb)*k/nh) for k in range(nh+1)]]
    for k in range(nh):
        plate(hcol[0][k],hcol[1][k],hcol[1][k+1],hcol[0][k+1],HNG_TW)
    # ---- sambungan ke model balok di x = 10000 ----
    iend=len(XS)-1
    sl=[grid[(iend,k)] for k in range(NZ_W+1)]
    rlink('TCHORD',XFOOT,side,[grid[(iend,NZ_W)]])
    rlink('MCHORD',XFOOT,side,[grid[(iend,0)]])
    rlink('WEDGE', XFOOT,side,sl)
    rlink('TIE',   XFOOT,side,[tg[(iend,k)] for k in range(5)])
    return len(grid)+len(tg)

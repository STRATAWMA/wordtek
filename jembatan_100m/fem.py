# -*- coding: utf-8 -*-
"""
B100 - model elemen hingga (FEM) dengan lantai beton KOMPOSIT.

Dibangun dari B100_1_STRUKTUR.mct + B100_2_BEBAN.mct yang sudah terverifikasi.
Yang berubah hanya sistem lantai:
  1. Chord bawah dan stringer dibagi 4 per panel  -> grid simpul 61 x 9
  2. Pelat lantai beton 262 mm dimodelkan sebagai 480 elemen PLATE
  3. Aksi komposit lewat offset tebal pelat (381 mm di atas sumbu balok),
     pelat berbagi simpul dengan stringer/cross girder - tanpa rigid link
  4. *RIGIDLINK dihapus: pelat beton itu sendiri yang jadi diafragma lantai
  5. Berat pelat tidak lagi beban balok, sudah masuk *SELFWEIGHT
Profil baja TIDAK ADA yang diubah.
"""
import re, collections, math

SRC_STR = 'B100_1_STRUKTUR.mct'
SRC_LOD = 'B100_2_BEBAN.mct'
OUT     = 'B100_FEM_KOMPOSIT.mct'
NDIV    = 4                 # pembagian tiap panel
TSLAB   = 262.0             # mm
ZOFF    = 381.0             # mm, sumbu balok -> bidang tengah pelat (250+131)
FC      = 30.0              # MPa
N0, E0, P0 = 1000, 2000, 5000   # nomor awal simpul baru / elemen baru / pelat

# ---------------------------------------------------------------- parse
def blocks(path):
    """kembalikan [(nama_blok, [baris...])] mempertahankan urutan & komentar"""
    out=[]; cur=None
    for raw in open(path):
        l=raw.rstrip('\n')
        if l.strip().startswith('*'):
            cur=[l.strip().split(',')[0][1:].split()[0], l, []]
            out.append(cur)
        elif cur is None:
            out.append(['_PRE', l, []])
        else:
            cur[2].append(l)
    return out

B_STR = blocks(SRC_STR)
B_LOD = blocks(SRC_LOD)

def data(bs,name):
    for b in bs:
        if b[0]==name:
            return [l for l in b[2] if l.strip() and not l.strip().startswith(';')]
    return []

nodes={}
for l in data(B_STR,'NODE'):
    f=[x.strip() for x in l.split(',')]
    nodes[int(f[0])]=[float(f[1]),float(f[2]),float(f[3])]

elems={}; eorder=[]
for l in data(B_STR,'ELEMENT'):
    f=[x.strip() for x in l.split(',')]
    elems[int(f[0])]=f; eorder.append(int(f[0]))

# ------------------------------------------------- pilih batang yang dibagi
def is_long_deck(f):
    """batang memanjang pada permukaan lantai (chord bawah + stringer).
    Lantai BER-CAMBER: z naik parabolik ke tengah bentang, jadi z=0 tidak
    bisa dipakai sebagai penanda. Penanda yang dipakai: sejajar sumbu x
    (y sama), punya panjang, dan berada di bawah chord atas."""
    a,b=nodes[int(f[4])],nodes[int(f[5])]
    return (a[2]<3000 and b[2]<3000 and abs(a[1]-b[1])<1 and abs(a[0]-b[0])>1)

SPLIT=[e for e in eorder if elems[e][1].strip()=='BEAM' and is_long_deck(elems[e])]
YL=sorted({round(nodes[int(elems[e][4])][1]) for e in SPLIT})
assert YL==[0,500,1600,2700,3800,4900,6000,7100,7600], YL

# ------------------------------------------------------------- pemecahan
nid=N0; eid=E0
emap={}                     # elemen lama -> daftar elemen baru
newnodes=[]; newelems=[]
# (x bulat, y bulat) -> nomor simpul pada permukaan lantai.
# Lantai ber-camber, jadi simpul didaftar dari ujung-ujung batang memanjang
# lantai itu sendiri, bukan dari syarat z=0.
nodeat={}
_dup=[]
for n,(x,y,z) in nodes.items():
    if round(y) in YL and z<3000:
        k=(round(x),round(y))
        if k in nodeat: _dup.append((k,nodeat[k],n))
        nodeat[k]=n
assert not _dup, ("dua simpul di titik yang sama",_dup[:5])
for e in SPLIT:                       # pastikan ujung batang yang menang
    f=elems[e]
    for k in (4,5):
        n=int(f[k]); x,y,z=nodes[n]; nodeat[(round(x),round(y))]=n

PANEL=6666.5; TARGET=PANEL/NDIV          # 1666.625 mm
for e in SPLIT:
    f=elems[e]; n1,n2=int(f[4]),int(f[5])
    a,b=nodes[n1],nodes[n2]
    if a[0]>b[0]: n1,n2=n2,n1; a,b=b,a
    # garis stringer tengah (y=3800) sudah terbagi setengah panel -> nd=2,
    # batang lain satu panel penuh -> nd=4. Hasilnya stasiun x seragam.
    nd=max(1,int(round(abs(b[0]-a[0])/TARGET)))
    chain=[n1]
    for k in range(1,nd):
        t=k/nd
        x=a[0]+(b[0]-a[0])*t; y=a[1]; z=a[2]+(b[2]-a[2])*t
        key=(round(x),round(y))
        if key not in nodeat:
            nid+=1; nodeat[key]=nid; nodes[nid]=[x,y,z]; newnodes.append(nid)
        chain.append(nodeat[key])
    chain.append(n2)
    ids=[]
    for k in range(nd):
        eid+=1
        g=list(f); g[0]=str(eid); g[4]=str(chain[k]); g[5]=str(chain[k+1])
        newelems.append(g); ids.append(eid)
    emap[e]=ids

XS=sorted({round(nodes[n][0]) for (x,y),n in nodeat.items() if y==0})
assert len(XS)==15*NDIV+1, len(XS)
for y in YL:
    miss=[x for x in XS if (x,y) not in nodeat]
    assert not miss, (y,miss[:4])

# ------------------------------------------------------------ elemen pelat
plates=[]; pid=P0
for i in range(len(XS)-1):
    for j in range(len(YL)-1):
        pid+=1
        n=[nodeat[(XS[i],YL[j])],nodeat[(XS[i+1],YL[j])],
           nodeat[(XS[i+1],YL[j+1])],nodeat[(XS[i],YL[j+1])]]
        plates.append((pid,n))

# --------------------------------------------------- daftar elemen stringer
def line_elems(y):
    out=[]
    for g in newelems:
        a=nodes[int(g[4])]
        if abs(a[1]-y)<1: out.append(int(g[0]))
    return sorted(out)
STRL={y:line_elems(y) for y in YL}
for y in YL: assert len(STRL[y])==15*NDIV, (y,len(STRL[y]))
# chord bawah (y=0 dan y=7600) bukan stringer - jangan dipakai untuk MS

def rng(ids):
    ids=sorted(set(ids)); out=[]; i=0
    while i<len(ids):
        j=i
        while j+1<len(ids) and ids[j+1]==ids[j]+1: j+=1
        out.append(str(ids[i]) if i==j else "%dto%d"%(ids[i],ids[j])); i=j+1
    return " ".join(out)

def remap(lst):
    ids=[]
    for t in lst.split():
        r=range(int(t.split('to')[0]),int(t.split('to')[1])+1) if 'to' in t else [int(t)]
        for e in r: ids.extend(emap.get(e,[e]))
    return rng(ids)

# ------------------------------------------------------------------ tulis
L=[]; A=L.append
def hdr(t):
    A(""); A(";"+"-"*74); A("; "+t); A(";"+"-"*74)

for b in B_STR:
    nm=b[0]
    if nm=='_PRE': A(b[1]); continue
    if nm=='ENDDATA': continue          # bagian beban masih menyusul
    if nm=='RIGIDLINK':
        hdr("RIGID LINK DIHAPUS")
        A("; Pelat beton 262 mm kini dimodelkan sebagai elemen PLATE dan menjadi")
        A("; diafragma lantai yang sebenarnya, jadi *RIGIDLINK tidak diperlukan.")
        A("; Ini juga menghilangkan gaya aksial palsu pada stringer yang timbul")
        A("; karena DOF Dx dulu dikekang ke chord bawah.")
        continue
    if nm=='NODE':
        A(b[1]); L.extend(b[2])
        A("; --- simpul tambahan: pembagian panel menjadi %d bagian ---"%NDIV)
        for n in newnodes:
            x,y,z=nodes[n]; A("   %d, %.4f, %.4f, %.4f"%(n,x,y,z))
        continue
    if nm=='ELEMENT':
        A(b[1])
        for l in b[2]:
            s=l.strip()
            if not s or s.startswith(';'): A(l); continue
            if int(s.split(',')[0]) in emap: continue      # diganti sub-elemen
            A(l)
        A("; --- sub-elemen chord bawah & stringer (tiap panel dibagi %d) ---"%NDIV)
        for g in newelems: A("   "+", ".join(g))
        A("; --- PELAT LANTAI BETON 262 mm : %d elemen PLATE ---"%len(plates))
        A("; iEL, TYPE, iMAT, iPRO, iN1, iN2, iN3, iN4, iSUB(1=Thick), iWID, LCAXIS")
        for p,n in plates:
            A("   %d, PLATE , 3, 4, %d, %d, %d, %d, 1, 0, 0"%(p,n[0],n[1],n[2],n[3]))
        continue
    if nm=='MATERIAL':
        A(b[1]); L.extend(b[2])
        E=4700*math.sqrt(FC)/9806.65          # tonf/mm2
        D=25.0/9.80665*1e-9                   # tonf/mm3  (beton 25 kN/m3)
        A("; beton lantai fc' = %.0f MPa, E = %.0f MPa, berat 25 kN/m3"%(FC,4700*math.sqrt(FC)))
        A("    3, CONC , C%d               , 0, 0, , C, NO, 0.05, 2, %.4fe+001, 0.2, 1.0000e-005, %.5fe-009,     0"%(FC,E/10.0,D*1e9))
        continue
    if nm=='THICKNESS':
        A(b[1]); L.extend(b[2])
        A("; pelat lantai: tebal %.0f mm, bidang tengahnya di +%.0f mm dari sumbu"%(TSLAB,ZOFF))
        A("; balok lantai -> inilah yang memberi AKSI KOMPOSIT (lengan kopel).")
        A("    4, VALUE, YES, %.0f, 0, YES, 0, %.0f"%(TSLAB,ZOFF))
        continue
    A(b[1]); L.extend(b[2])

# ------------------------------------------------------------ bagian beban
for b in B_LOD:
    nm=b[0]
    if nm=='_PRE': continue
    if nm=='BEAMLOAD':
        A(b[1])
        for l in b[2]:
            s=l.strip()
            if not s or s.startswith(';'): A(l); continue
            f=[x.strip() for x in l.rstrip().split(',')]
            f[0]=remap(f[0]); A("   "+", ".join(f))
        continue
    if nm=='ELTEMPER':
        A(b[1])
        for l in b[2]:
            s=l.strip()
            if not s or s.startswith(';'): A(l); continue
            f=[x.strip() for x in l.rstrip().split(',')]
            f[0]=remap(f[0]); A("   "+", ".join(f))
        continue
    A(b[1]); L.extend(b[2])

txt="\n".join(L)

# ---- MS: berat pelat sudah dari SELFWEIGHT, sisakan trotoar saja ----
m=re.search(r'(\*USE-STLD, MS.*?)(?=\*USE-STLD, MA)', txt, re.S)
blockMS=m.group(1)
keep=[]
for l in blockMS.split('\n'):
    if 'UNILOAD' in l and not l.strip().startswith(';'): continue
    keep.append(l)
ins=("; Berat pelat 262 mm TIDAK lagi beban balok - sudah dipikul elemen PLATE\n"
     "; lewat *SELFWEIGHT. Yang tersisa hanya beton trotoar 300 mm x 0.5 m.\n"
     "   %s, BEAM, UNILOAD, GZ, NO, NO, LZ, 0, 0, NO, 0, -3.7500, 1, -3.7500, 0, 0, 0, 0, \n"
     "   %s, BEAM, UNILOAD, GZ, NO, NO, LZ, 0, 0, NO, 0, -3.7500, 1, -3.7500, 0, 0, 0, 0, "
     %(rng(STRL[500]),rng(STRL[7100])))
out=[]
for l in keep:
    out.append(l)
    if l.strip().startswith('; ELEM_LIST'): out.append(ins)
txt=txt.replace(blockMS,"\n".join(out)+"\n")

open(OUT,'w').write(txt+"\n")
print("simpul lama %d + baru %d"%(len(nodes)-len(newnodes),len(newnodes)))
print("elemen balok dipecah: %d -> %d sub-elemen"%(len(SPLIT),len(newelems)))
print("elemen PLATE: %d  (%d x %d)"%(len(plates),len(XS)-1,len(YL)-1))
print("tulis",OUT,len(txt.split('\n')),"baris")

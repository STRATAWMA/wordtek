import glob,re
fs=sorted(glob.glob("A80_P[0-9]_*.mct"))
tot={}
for f in fs:
    ls=open(f).read().split("\n")
    u=[i for i,l in enumerate(ls) if l.startswith("*UNIT")]
    bl=[l.split(",")[0].strip() for l in ls if l.startswith("*")]
    dat=[l for l in ls if l.strip() and not l.lstrip().startswith(";") and not l.startswith("*")]
    bad=[l for l in dat if any(ord(c)>126 for c in l)]
    print("%-26s UNIT@%s  blok=%s  data=%d  nonascii=%d  end=%s"%(
        f,u,[b for b in bl if b not in("*VERSION","*UNIT")],len(dat),len(bad),ls[-2]=="*ENDDATA" or "*ENDDATA" in ls))
    tot[f]=len(dat)
# bandingkan jumlah entitas dengan file induk
src=open("A80_PELENGKUNG_FEM.mct").read().split("\n")
def cnt(a,b): return len([l for l in src[a-1:b] if l.strip() and not l.lstrip().startswith(";") and not l.startswith("*")])
exp=cnt(13,24)+cnt(5489,5537)+cnt(25,2651)+cnt(2652,3860)+cnt(3861,5488)+cnt(5538,6462)+cnt(6468,6489)+cnt(6490,6766)+cnt(6767,6794)
print("\ntotal data di 8 bagian = %d   diharapkan = %d   -> %s"%(sum(tot.values()),exp,"OK" if sum(tot.values())==exp else "BEDA"))
# cek seluruh data induk terwakili
import collections
allsrc=collections.Counter(l for l in src if l.strip() and not l.lstrip().startswith(";") and not l.startswith("*"))
allp=collections.Counter()
for f in fs:
    allp.update(l for l in open(f).read().split("\n") if l.strip() and not l.lstrip().startswith(";") and not l.startswith("*"))
miss=allsrc-allp
print("baris induk yang HILANG di hasil pecahan: %d"%sum(miss.values()))
for l in list(miss)[:5]: print("  ",l[:90])

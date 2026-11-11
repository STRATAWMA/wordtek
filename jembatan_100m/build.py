import collections,math,json,re
SRC='new.mct'
raw=open(SRC,errors='ignore').read().splitlines()
sec=None;nodes={};elems=[];sects={};elines={};hdr=[]
for i,ln in enumerate(raw):
    s=ln.strip()
    if s.startswith('*'): sec=s.split(',')[0].split()[0].upper()
    if sec=='*NODE' and not s.startswith('*') and s and not s.startswith(';'):
        f=[x.strip() for x in s.split(',')]; nodes[int(f[0])]=(float(f[1]),float(f[2]),float(f[3]))
    if sec=='*ELEMENT' and not s.startswith('*') and s and not s.startswith(';'):
        f=[x.strip() for x in s.split(',')]
        if f[1]=='BEAM':
            elems.append(dict(id=int(f[0]),mat=int(f[2]),sec=int(f[3]),n1=int(f[4]),n2=int(f[5]),ang=float(f[6])))
    if sec=='*SECTION' and not s.startswith('*') and s and not s.startswith(';'):
        f=[x.strip() for x in s.split(',')]
        if f[1] in ('DBUSER','TAPERED'): sects[int(f[0])]=f

DUP={7,92,185,201,217,233,248,265,281,299,330}
CGSEC=73
# --- node lantai per panel ---
YF=[0.0,500.0,1600.0,2700.0,3800.0,4900.0,6000.0,7100.0,7600.0]
bx=collections.defaultdict(dict)
for n,(x,y,z) in nodes.items():
    if z<3000: bx[round(x,1)][round(y,1)]=n
PANEL=[x for x in sorted(bx) if sorted(bx[x])==YF]
assert len(PANEL)==16, len(PANEL)
# --- buang duplikat & cross girder lama ---
keep=[e for e in elems if e['id'] not in DUP and e['sec']!=CGSEC]
removed_cg=[e['id'] for e in elems if e['sec']==CGSEC]
nid=max(e['id'] for e in elems)
# --- cross girder baru: 8 segmen per panel, section tapered per kedalaman ---
# CG2 tapered 900 (ujung) -> 1000 (tengah). buat 4 section prismatis per kedalaman
DEPTH={0:900,500:913,1600:942,2700:971,3800:1000}
def dep(y): return DEPTH[y] if y<=3800 else DEPTH[7600-y]
newsec={}   # depth -> iSEC
ns=max(sects)+0
cg_new=[]
for x in PANEL:
    for a,b in zip(YF[:-1],YF[1:]):
        d=int(round((dep(a)+dep(b))/2/10.0)*10)
        if d not in newsec:
            ns+=1; newsec[d]=ns
        nid+=1
        cg_new.append(dict(id=nid,mat=1,sec=newsec[d],n1=bx[x][a],n2=bx[x][b],ang=0.0))
allel=keep+cg_new
print("elemen lama %d -> dibuang duplikat %d, CG lama %d"%(len(elems),len(DUP),len(removed_cg)))
print("CG baru %d elemen, section baru: %s"%(len(cg_new),{k:v for k,v in sorted(newsec.items())}))
print("TOTAL elemen final:",len(allel))
# konektivitas ulang
deg=collections.Counter()
for e in allel: deg[e['n1']]+=1; deg[e['n2']]+=1
low=[n for n in nodes if deg[n]<=1]
print("node derajat <=1 :",low)
free=[n for n in nodes if deg[n]==2 and nodes[n][2]<3000 and abs(nodes[n][1]-3800)>1]
print("node lantai masih terisolasi:",len(free))
json.dump(dict(nodes={str(k):v for k,v in nodes.items()},elems=allel,newsec=newsec,
   panel=PANEL,bx={str(k):{str(a):b for a,b in v.items()} for k,v in bx.items()},
   removed_cg=removed_cg,dup=sorted(DUP)),open('fix.json','w'))

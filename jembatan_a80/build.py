# -*- coding: utf-8 -*-
"""A80 - generator model elemen hingga jembatan rangka pelengkung 80 m."""
import math, collections
from geom import L,NP,A,B,YS,XS,zT,zM,dep

N={}; _n=[0]
def nd(x,y,z):
    k=(round(x),round(y),round(z))
    if k not in N: _n[0]+=1; N[k]=_n[0]
    return N[k]
E=[]; _e=[0]
def el(sec,n1,n2,mat=1,ang=0):
    _e[0]+=1; E.append((_e[0],mat,sec,n1,n2,ang)); return _e[0]
PL=[]; _p=[0]
def pl(n1,n2,n3,n4):
    _p[0]+=1; PL.append((_p[0],n1,n2,n3,n4)); return _p[0]

SIDES=[0.0,B]
# ---------------- simpul ----------------
tie={}; mch={}; tch={}
for s in SIDES:
    for i,x in enumerate(XS):
        tie[(s,i)]=nd(x,s,0.0)
        mch[(s,i)]=nd(x,s,zM(x)) if i not in (0,NP) else tie[(s,i)]
        tch[(s,i)]=nd(x,s,zT(x)) if i not in (0,NP) else tie[(s,i)]
st={}
for y in YS:
    for i,x in enumerate(XS): st[(y,i)]=nd(x,y,0.0)

# ---------------- penampang ----------------
# 1 balok tarik | 2 chord ujung | 3 chord | 4 hanger | 5 web pelengkung
# 6 cross girder | 7 stringer | 8 pipa bracing | 9 lateral stop
SEC={1:("B-TIE","H",(1000,400,20,30)), 2:("ARCH-END","H",(400,500,20,30)),
     3:("ARCH","H",(400,350,20,30)),   4:("HANGER","H",(400,250,12,20)),
     5:("ARCH-WEB","H",(400,200,12,20)),6:("CROSSGIRDER","H",(550,400,20,30)),
     7:("STRINGER","H",(450,220,8,12)), 8:("PIPE6","P",(165.2,7.1)),
     9:("LAT-STOP","H",(850,400,10,20))}
MATP=2   # pipa STK41

# ---------------- batang ----------------
grp=collections.defaultdict(list)
for s in SIDES:
    for i in range(NP):
        grp['TIE'].append(el(1,tie[(s,i)],tie[(s,i+1)]))
        se = 2 if i in (0,NP-1) else 3
        grp['T-CHORD'].append(el(se,tch[(s,i)],tch[(s,i+1)]))
        grp['M-CHORD'].append(el(se,mch[(s,i)],mch[(s,i+1)]))
    for i in range(1,NP):
        grp['ARCH-VERT'].append(el(5,tch[(s,i)],mch[(s,i)]))     # vertikal dlm rangka
        grp['HANGER'].append(el(4,mch[(s,i)],tie[(s,i)]))        # hanger ke balok tarik
    for i in range(1,NP-1):                                      # diagonal rangka pelengkung
        a,b2=(i,i+1) if i<NP//2 else (i+1,i)
        grp['ARCH-DIAG'].append(el(5,tch[(s,a)],mch[(s,b2)]))

# cross girder di tiap titik buhul, dipecah di tiap garis stringer
ylines=[0.0]+YS+[B]
for i,x in enumerate(XS):
    pts=[tie[(0.0,i)]]+[st[(y,i)] for y in YS]+[tie[(B,i)]]
    for a,b2 in zip(pts[:-1],pts[1:]): grp['CROSSGIRDER'].append(el(6,a,b2))
# stringer
for y in YS:
    for i in range(NP): grp['STRINGER'].append(el(7,st[(y,i)],st[(y,i+1)]))

# ikatan angin bidang chord ATAS dan chord TENGAH (silang tiap panel)
for lev,dic,nm in (('T',tch,'HB-TOP'),('M',mch,'HB-MID')):
    for i in range(1,NP):
        grp[nm].append(el(8,dic[(0.0,i)],dic[(B,i)],MATP))       # melintang
    for i in range(1,NP-1):
        grp[nm].append(el(8,dic[(0.0,i)],dic[(B,i+1)],MATP))     # silang
        grp[nm].append(el(8,dic[(B,i)],dic[(0.0,i+1)],MATP))
# portal melintang: silang antara chord ATAS dan chord TENGAH
for i in range(1,NP):
    grp['VB-FRAME'].append(el(8,tch[(0.0,i)],mch[(B,i)],MATP))
    grp['VB-FRAME'].append(el(8,tch[(B,i)],mch[(0.0,i)],MATP))
# lateral stop di kedua ujung
for i in (0,NP):
    grp['LAT-STOP'].append(el(9,tie[(0.0,i)],tie[(B,i)]))

# ---------------- pelat lantai beton ----------------
ylines_all=[0.0]+YS+[B]
nodes_at={}
for i,x in enumerate(XS):
    for y in ylines_all:
        nodes_at[(i,y)] = tie[(0.0,i)] if y==0.0 else (tie[(B,i)] if y==B else st[(y,i)])
ZOFF=381.0
slab={}
for i,x in enumerate(XS):
    for y in ylines_all:
        b=nodes_at[(i,y)]; k=[kk for kk,v in N.items() if v==b][0]
        slab[(i,y)]=nd(k[0],k[1],k[2]+ZOFF)
for i in range(NP):
    for j in range(len(ylines_all)-1):
        y1,y2=ylines_all[j],ylines_all[j+1]
        pl(slab[(i,y1)],slab[(i+1,y1)],slab[(i+1,y2)],slab[(i,y2)])
rl=[(nodes_at[(i,y)],slab[(i,y)]) for i in range(NP+1) for y in ylines_all]

print("simpul %d | batang %d | pelat %d | rigid link %d"%(len(N),len(E),len(PL),len(rl)))
for k in sorted(grp): print("   %-12s %4d"%(k,len(grp[k])))
import json
json.dump(dict(nodes={str(v):list(k) for k,v in N.items()},elems=E,plates=PL,
               rl=rl,grp={k:v for k,v in grp.items()}),open('a80.json','w'))

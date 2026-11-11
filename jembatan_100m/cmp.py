import math,re,collections
import numpy as np
F='B100_FINAL.mct'
sec=None;lc=None;unit='TONF'
nodes={};elems=[];S={};sup={};rl=[];bl=collections.defaultdict(list);cl=collections.defaultdict(list)
tp=collections.defaultdict(list);sw=[];comb=[];cname=None
for ln in open(F,errors='ignore'):
    t=ln.strip()
    if t.startswith('*'):
        tag=t.split(',')[0].split()[0].upper()
        if tag=='*USE-STLD': lc=t.split(',')[1].strip(); continue
        if tag=='*SELFWEIGHT': sw.append(lc); continue
        sec=tag; continue
    if not t or t.startswith(';'): continue
    f=[x.strip() for x in t.split(',')]
    if sec=='*UNIT': unit=f[0]
    elif sec=='*NODE': nodes[int(f[0])]=np.array([float(f[1]),float(f[2]),float(f[3])])
    elif sec=='*ELEMENT': elems.append(dict(id=int(f[0]),sec=int(f[3]),n1=int(f[4]),n2=int(f[5])))
    elif sec=='*SECTION' and f[1] in ('DBUSER','TAPERED'): S[int(f[0])]=f
    elif sec=='*CONSTRAINT': sup[int(f[0])]=f[1]
    elif sec=='*RIGIDLINK': rl.append((int(f[1]),f[2],[int(x) for x in f[3].split()]))
    elif sec=='*BEAMLOAD': bl[lc].append((f[0],f[3],float(f[11])))
    elif sec=='*CONLOAD': cl[lc].append((int(f[0]),float(f[1]),float(f[2]),float(f[3])))
    elif sec=='*ELTEMPER': tp[lc].append((f[0],float(f[1])))
    elif sec=='*LOADCOMB':
        if f[0].startswith('NAME='): cname=f[0][5:]; comb.append((cname,[]))
        else:
            for i in range(0,len(f)-2,3):
                if f[i]=='ST': comb[-1][1].append((f[i+1],float(f[i+2])))
def Hp(H,B,tw,tf):
    A=2*B*tf+(H-2*tf)*tw
    return dict(A=A,Iy=(B*H**3-(B-tw)*(H-2*tf)**3)/12,Iz=(2*tf*B**3+(H-2*tf)*tw**3)/12,
      J=(2*B*tf**3+(H-tf)*tw**3)/3,Zy=B*tf*(H-tf)+tw*(H-2*tf)**2/4,Zz=tf*B*B/2+(H-2*tf)*tw*tw/4)
def Pp(Do,t):
    di=Do-2*t;A=math.pi/4*(Do**2-di**2);I=math.pi/64*(Do**4-di**4)
    return dict(A=A,Iy=I,Iz=I,J=2*I,Zy=(Do**3-di**3)/6,Zz=(Do**3-di**3)/6)
PR={};NM={}
for i,f in S.items():
    NM[i]=f[2].strip()
    if f[1]=='TAPERED': PR[i]=Hp(950,420,12,16); continue
    sh=f[12];md=f[13];d=[x for x in f[14:] if x!='']
    if md=='1':
        m=re.search(r'(\d+)x(\d+)x([\d.]+)/([\d.]+)',' '.join(d)); PR[i]=Hp(*[float(x) for x in m.groups()]); continue
    d=[float(x) for x in d]; PR[i]=Hp(*d[:4]) if sh=='H' else Pp(d[0],d[1])
ids=sorted(nodes); idx={n:i for i,n in enumerate(ids)}; ND=len(ids)*6
E=205000.;G=E/2.6;RHO=7.85e-5
def tmat(p1,p2):
    L=np.linalg.norm(p2-p1); ex=(p2-p1)/L; up=np.array([0.,0.,1.])
    if abs(ex@up)>0.9999: up=np.array([1.,0.,0.])
    ey=np.cross(up,ex); ey/=np.linalg.norm(ey); return L,np.vstack([ex,ey,np.cross(ex,ey)])
def kl(L,p):
    k=np.zeros((12,12)); A,Iy,Iz,J=p['A'],p['Iy'],p['Iz'],p['J']
    k[0,0]=k[6,6]=E*A/L;k[0,6]=k[6,0]=-E*A/L;k[3,3]=k[9,9]=G*J/L;k[3,9]=k[9,3]=-G*J/L
    for (i1,i2,i3,i4),I,sg in (((1,5,7,11),Iz,1),((2,4,8,10),Iy,-1)):
        a=12*E*I/L**3;b=6*E*I/L**2;c=4*E*I/L;d=2*E*I/L
        k[i1,i1]+=a;k[i1,i3]-=a;k[i3,i1]-=a;k[i3,i3]+=a
        k[i2,i2]+=c;k[i4,i4]+=c;k[i2,i4]+=d;k[i4,i2]+=d
        k[i1,i2]+=sg*b;k[i2,i1]+=sg*b;k[i1,i4]+=sg*b;k[i4,i1]+=sg*b
        k[i3,i2]-=sg*b;k[i2,i3]-=sg*b;k[i3,i4]-=sg*b;k[i4,i3]-=sg*b
    return k
EL=[];K=np.zeros((ND,ND))
def dofs(e):
    a,b=idx[e['n1']]*6,idx[e['n2']]*6; return list(range(a,a+6))+list(range(b,b+6))
for e in elems:
    L,T=tmat(nodes[e['n1']],nodes[e['n2']]); Rm=np.zeros((12,12))
    for b in range(4): Rm[3*b:3*b+3,3*b:3*b+3]=T
    p=PR[e['sec']]; EL.append(dict(e=e,L=L,T=T,p=p))
    K[np.ix_(dofs(e),dofs(e))]+=Rm.T@kl(L,p)@Rm
def ex(rs):
    o=[]
    for t in rs.split():
        if 'to' in t: a,b=t.split('to'); o+=list(range(int(a),int(b)+1))
        else: o.append(int(t))
    return o
byid={x['e']['id']:x for x in EL}
UDL=collections.defaultdict(lambda: collections.defaultdict(lambda: np.zeros(3)))
DIRV={'GX':0,'GY':1,'GZ':2}
LCF={}
for k in set(list(bl)+list(cl)+list(tp)+sw):
    Fv=np.zeros(ND)
    if k in sw:
        for X in EL:
            UDL[k][X['e']['id']]+=np.array([0,0,-RHO*X['p']['A']])
    for els,d,v in bl.get(k,[]):
        for eid in ex(els):
            w=np.zeros(3); w[DIRV[d]]=v; UDL[k][eid]+=w
    for X in EL:
        eid=X['e']['id']
        if eid in UDL[k]:
            wl=X['T']@UDL[k][eid]; L=X['L']; f=np.zeros(12)
            f[0]=f[6]=wl[0]*L/2
            f[1]=f[7]=wl[1]*L/2;f[5]=wl[1]*L*L/12;f[11]=-wl[1]*L*L/12
            f[2]=f[8]=wl[2]*L/2;f[4]=-wl[2]*L*L/12;f[10]=wl[2]*L*L/12
            g=np.zeros(12)
            for b in range(4): g[3*b:3*b+3]=X['T'].T@f[3*b:3*b+3]
            Fv[dofs(X['e'])]+=g
    for n,fx,fy,fz in cl.get(k,[]):
        a=idx[n]*6; Fv[a]+=fx*1000; Fv[a+1]+=fy*1000; Fv[a+2]+=fz*1000
    for els,dT in tp.get(k,[]):
        for eid in ex(els):
            X=byid[eid]; N=X['p']['A']*E*1.2e-5*dT; gv=X['T'].T@np.array([N,0,0])
            a,b=idx[X['e']['n1']]*6,idx[X['e']['n2']]*6
            Fv[a:a+3]-=gv; Fv[b:b+3]+=gv
    LCF[k]=Fv
# satuan: beban kN,m -> N,mm  (kN/m == N/mm, jadi UDL sudah benar; CONLOAD kN -> N sudah x1000)
fix=[idx[n]*6+i for n,c in sup.items() for i,ch in enumerate(c) if ch=='1']
sl=set()
for m,dof,ss in rl:
    for s in ss:
        for i,ch in enumerate(dof):
            if ch=='1': sl.add(idx[s]*6+i)
keep=[i for i in range(ND) if i not in sl]; pos={d:i for i,d in enumerate(keep)}
T=np.zeros((ND,len(keep)))
for i,d in enumerate(keep): T[d,i]=1.
for m,dof,ss in rl:
    for s in ss:
        dx,dy=nodes[s][0]-nodes[m][0],nodes[s][1]-nodes[m][1]
        if dof[0]=='1': T[idx[s]*6+0,pos[idx[m]*6+0]]=1.; T[idx[s]*6+0,pos[idx[m]*6+5]]=-dy
        if dof[1]=='1': T[idx[s]*6+1,pos[idx[m]*6+1]]=1.; T[idx[s]*6+1,pos[idx[m]*6+5]]= dx
        if dof[5]=='1': T[idx[s]*6+5,pos[idx[m]*6+5]]=1.
Kr=T.T@K@T; fr=np.array(sorted(set(range(len(keep)))-set(pos[f] for f in fix if f in pos)))
Kff=Kr[np.ix_(fr,fr)]; ev=np.linalg.eigvalsh(Kff)
print("node %d  elemen %d  rigidlink %d  tumpuan %d"%(len(nodes),len(elems),len(rl),len(sup)))
print("eigenvalue min = %.4g -> %s"%(ev.min(),"STABIL" if ev.min()>0 else "SINGULAR"))
U={}
for k,Fv in LCF.items():
    u=np.zeros(len(keep)); u[fr]=np.linalg.solve(Kff,(T.T@Fv)[fr]); U[k]=T@u
n86=[n for n in nodes if abs(nodes[n][0]-46665.5)<1 and abs(nodes[n][1]-3800)<1 and nodes[n][2]<3000][0]
print("lendut hidup tengah = %.1f mm (batas L/800 = 125.0 mm)"%(U['TD-BTR'][idx[n86]*6+2]+U['TD-BGT'][idx[n86]*6+2]))
for k in ('MS','MA','TD-BTR'):
    print("  reaksi %-7s = %8.1f kN"%(k,-(K@U[k]-LCF[k])[[idx[n]*6+2 for n in sup]].sum()/1000))
Fy=355.
STSEC={i for i,n in NM.items() if n.startswith('ST')}
def cap(p,L,braced=False):
    A=p['A']
    r=math.sqrt(p['Iy']/A) if braced else min(math.sqrt(p['Iy']/A),math.sqrt(p['Iz']/A))
    Po=Fy*A; Pe=math.pi**2*E*A/(L/r)**2
    Pn=(0.658**(Po/Pe))*Po if Pe/Po>=.44 else .877*Pe
    return .95*Fy*A,.9*Pn,Fy*p['Zy'],Fy*p['Zz']
FR={}
for k in LCF:
    o={}
    for X in EL:
        e=X['e'];L=X['L'];Rm=np.zeros((12,12))
        for b in range(4): Rm[3*b:3*b+3,3*b:3*b+3]=X['T']
        f=kl(L,X['p'])@(Rm@U[k][dofs(e)])
        wl=X['T']@UDL[k][e['id']] if e['id'] in UDL[k] else np.zeros(3)
        fe=np.zeros(12)
        fe[0]=fe[6]=wl[0]*L/2;fe[1]=fe[7]=wl[1]*L/2;fe[5]=wl[1]*L*L/12;fe[11]=-wl[1]*L*L/12
        fe[2]=fe[8]=wl[2]*L/2;fe[4]=-wl[2]*L*L/12;fe[10]=wl[2]*L*L/12
        o[e['id']]=f-fe
    FR[k]=o
import sys
DIA = '--dia' in sys.argv
if DIA:
    rl=[]
    PAN=sorted({round(nodes[n][0],1) for n in nodes if nodes[n][2]<3000})
    bxf={}
    for n in nodes:
        if nodes[n][2]<3000: bxf.setdefault(round(nodes[n][0],1),{})[round(nodes[n][1],1)]=n
    YF=[0.,500.,1600.,2700.,3800.,4900.,6000.,7100.,7600.]
    for x in PAN:
        if sorted(bxf[x])!=YF: continue
        rl.append((bxf[x][0.],'110001',[bxf[x][y] for y in YF[1:]]))
    sl=set()
    for m,dof,ss in rl:
        for sv in ss:
            for i,ch in enumerate(dof):
                if ch=='1': sl.add(idx[sv]*6+i)
    keep=[i for i in range(ND) if i not in sl]; pos={d:i for i,d in enumerate(keep)}
    T=np.zeros((ND,len(keep)))
    for i,d in enumerate(keep): T[d,i]=1.
    for m,dof,ss in rl:
        for sv in ss:
            dx,dy=nodes[sv][0]-nodes[m][0],nodes[sv][1]-nodes[m][1]
            T[idx[sv]*6+0,pos[idx[m]*6+0]]=1.; T[idx[sv]*6+0,pos[idx[m]*6+5]]=-dy
            T[idx[sv]*6+1,pos[idx[m]*6+1]]=1.; T[idx[sv]*6+1,pos[idx[m]*6+5]]= dx
            T[idx[sv]*6+5,pos[idx[m]*6+5]]=1.
    Kr=T.T@K@T; fr=np.array(sorted(set(range(len(keep)))-set(pos[f] for f in fix if f in pos)))
    Kff=Kr[np.ix_(fr,fr)]
    print("  [diafragma AKTIF: %d rigid link]  eigen min = %.4g"%(len(rl),np.linalg.eigvalsh(Kff).min()))
    for k,Fv in LCF.items():
        u=np.zeros(len(keep)); u[fr]=np.linalg.solve(Kff,(T.T@Fv)[fr]); U[k]=T@u
    for k in LCF:
        o={}
        for X in EL:
            e=X['e'];L=X['L'];Rm=np.zeros((12,12))
            for b in range(4): Rm[3*b:3*b+3,3*b:3*b+3]=X['T']
            f=kl(L,X['p'])@(Rm@U[k][dofs(e)])
            wl=X['T']@UDL[k][e['id']] if e['id'] in UDL[k] else np.zeros(3)
            fe=np.zeros(12)
            fe[0]=fe[6]=wl[0]*L/2;fe[1]=fe[7]=wl[1]*L/2;fe[5]=wl[1]*L*L/12;fe[11]=-wl[1]*L*L/12
            fe[2]=fe[8]=wl[2]*L/2;fe[4]=-wl[2]*L*L/12;fe[10]=wl[2]*L*L/12
            o[e['id']]=f-fe
        FR[k]=o
def run(scale,skip_eq):
    out=[]
    for X in EL:
        e=X['e'];L=X['L'];Pt,Pc,My0,Mz0=cap(X['p'],L,e['sec'] in STSEC); w=(0,None)
        for cn,terms in comb:
            if 'LAYAN' in cn or 'LENDUT' in cn: continue
            iseq='EKSTREM' in cn
            if skip_eq and iseq: continue
            f=np.zeros(12); wl=np.zeros(3)
            for lcn,g in terms:
                if lcn.startswith('EQ'): g*=scale
                if lcn in FR: f+=g*FR[lcn][e['id']]
                if lcn in UDL and e['id'] in UDL[lcn]: wl+=g*(X['T']@UDL[lcn][e['id']])
            N=-f[0]; My=max(abs(f[4]),abs(f[10]),abs((f[4]-f[10])/2-wl[2]*L*L/8))
            Mz=max(abs(f[5]),abs(f[11]),abs((-f[5]+f[11])/2+wl[1]*L*L/8))
            rp=abs(N)/(Pc if N<0 else Pt); rm=My/My0+Mz/Mz0
            rt=rp/2+rm if rp<0.2 else rp+8/9*rm
            if rt>w[0]: w=(rt,cn,N/1000,My/1e6,Mz/1e6)
        out.append((w[0],e['id'],NM[e['sec']],w[1],w[2],w[3],w[4]))
    return sorted(out,reverse=True)
for lab,sk in (("TANPA GEMPA (KUAT I/III/IV/V)",True),("DENGAN GEMPA (Timor Leste, R=1)",False)):
    rr=run(1.0,sk); fm=collections.defaultdict(float)
    for r,e,nm,cn,N,My,Mz in rr: fm[nm.rstrip('0123456789-')]=max(fm[nm.rstrip('0123456789-')],r)
    print("\n  %-32s NG: %d/%d   maks %.2f"%(lab,len([x for x in rr if x[0]>1]),len(rr),rr[0][0]))
    print("    "+" | ".join("%s %.2f"%(k,v) for k,v in sorted(fm.items(),key=lambda x:-x[1])))
    for r,e,nm,cn,N,My,Mz in rr[:0]: print("      %.2f el%-5d %-8s %-14s N=%8.1f My=%7.1f Mz=%7.1f"%(r,e,nm,cn,N,My,Mz))
lo,hi=0.0,2.0
for _ in range(14):
    md=(lo+hi)/2
    if run(md,False)[0][0]<=1.0: lo=md
    else: hi=md
print("\n  >>> FAKTOR SKALA GEMPA MAKSIMUM profil asli = %.4f x beban gempa saat ini"%lo)
res=[]
for X in EL:
    pass
res=run(1.0,False)
fam=collections.defaultdict(float)
for r,e,nm,cn,N,My,Mz in res: fam[nm.rstrip('0123456789-')]=max(fam[nm.rstrip('0123456789-')],r)
print("\nCEK KEKUATAN SEMUA KOMBINASI KUAT  ->  NG: %d / %d"%(len([x for x in res if x[0]>1]),len(res)))
print("  "+" | ".join("%s %.2f"%(k,v) for k,v in sorted(fam.items(),key=lambda x:-x[1])))
print("  10 teratas:")
for r,e,nm,cn,N,My,Mz in res[:10]:
    print("    %.2f  el%-5d %-9s %-14s N=%9.1f kN  My=%7.1f  Mz=%7.1f kNm"%(r,e,nm,cn,N,My,Mz))

rr=run(1.0,False)
want={94:'BC1-1',101:'BC8-1',102:'DG1-1',132:'TC1-1',78:'TC7-1',472:'CG-910',291:'BR1',267:'ST1-1'}
mid={94:2250.21,101:19573.0,102:-9217.4,132:-6427.0,78:-27082.0,472:-884.71,291:-1055.2,267:-487.04}
print("\n%-8s %-8s %12s %12s %8s"%("elem","sect","saya (kN)","midas (kN)","rasio"))
for r,e,nm,cn,N,My,Mz in rr:
    if e in want:
        m=mid[e]
        print("%-8d %-8s %12.1f %12.1f %8.2f"%(e,nm,N,m,abs(m/N) if N else 0))

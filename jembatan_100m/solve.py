import json,math,pickle,collections
import numpy as np
M=pickle.load(open('mesh.pkl','rb')); R=json.load(open('res.json')); D=json.load(open('fix.json'))
EL=M['EL']; PROP=M['PROP']; NAME=M['NAME']; idx=M['idx']; ids=M['ids']
nodes={int(k):np.array(v) for k,v in D['nodes'].items()}
K=np.load('K.npy'); ND=K.shape[0]
RHO=7.85e-5  # N/mm3
P=R['P']; YS=['500','1600','2700','3800','4900','6000','7100']
def expand(rs):
    out=[]
    for t in rs.split():
        if 'to' in t: a,b=t.split('to'); out+=list(range(int(a),int(b)+1))
        else: out.append(int(t))
    return out
STR={y:expand(R['_rng'][y]) for y in YS}
BC={k:expand(v) for k,v in R['_rngBC'].items()}
TC={k:expand(v) for k,v in R['_rngTC'].items()}
byid={e['e']['id']:e for e in EL}
def dofs(e):
    a,b=idx[e['n1']]*6,idx[e['n2']]*6; return list(range(a,a+6))+list(range(b,b+6))
def addudl(F,eid,wglob):
    E_=byid[eid]; L=E_['L']; T=E_['T']
    wl=T@np.array(wglob)                      # ke lokal (N/mm)
    f=np.zeros(12)
    f[0]=f[6]=wl[0]*L/2
    f[1]=f[7]=wl[1]*L/2; f[5]= wl[1]*L*L/12; f[11]=-wl[1]*L*L/12
    f[2]=f[8]=wl[2]*L/2; f[4]=-wl[2]*L*L/12; f[10]= wl[2]*L*L/12
    g=np.zeros(12)
    for b in range(4): g[3*b:3*b+3]=T.T@f[3*b:3*b+3]
    F[dofs(E_['e'])]+=g
def addnodal(F,n,fx,fy,fz):
    a=idx[n]*6; F[a]+=fx; F[a+1]+=fy; F[a+2]+=fz
LC={}
def newF(): return np.zeros(ND)
# MS : selfweight + plat
F=newF()
for E_ in EL:
    w=-RHO*E_['p']['A']           # N/mm ke bawah
    addudl(F,E_['e']['id'],[0,0,w])
for y in YS:
    for e in STR[y]: addudl(F,e,[0,0,-R['MS'][y]])      # kN/m == N/mm
LC['MS']=F
for nm,dat in (('MA',R['MA']),('TD-BTR',R['BTR']),('TP',R['TP'])):
    F=newF()
    for y in YS:
        if dat[y]: 
            for e in STR[y]: addudl(F,e,[0,0,-dat[y]])
    LC[nm]=F
F=newF()
for y in YS: addnodal(F,R['NBGT'][y],0,0,-R['BGT'][y]*1000)   # kN -> N
LC['TD-BGT']=F
F=newF()
for y in R['YS_TB']:
    for e in STR[y]: addudl(F,e,[R['TB_str'],0,0])
for n in R['NSUP']['x0']: addnodal(F,n,0,0, R['TB_V']*1000)
for n in R['NSUP']['xL']: addnodal(F,n,0,0,-R['TB_V']*1000)
LC['TB1']=F
F=newF()
for k in ('0','7600'):
    for e in TC[k]: addudl(F,e,[0,R['EWS_tc'],0])
    for e in BC[k]: addudl(F,e,[0,R['EWS_bc'],0])
LC['EWS']=F
F=newF()
for k in ('0','7600'):
    for e in BC[k]: addudl(F,e,[0,R['EWL_h'],0])
for e in BC['0']: addudl(F,e,[0,0, R['EWL_v']])
for e in BC['7600']: addudl(F,e,[0,0,-R['EWL_v']])
LC['EWL']=F
F=newF()
for e in BC['0']: addudl(F,e,[0,0,R['EWV_w']])
for e in BC['7600']: addudl(F,e,[0,0,R['EWV_l']])
LC['EWV']=F
for nm,d in (('EQX',0),('EQY',1)):
    F=newF()
    for y in YS:
        v=[0,0,0]; v[d]=R['EQ_str'][y]
        for e in STR[y]: addudl(F,e,v)
    for k in ('0','7600'):
        v=[0,0,0]; v[d]=R['EQ_bc']
        for e in BC[k]: addudl(F,e,v)
        v=[0,0,0]; v[d]=R['EQ_tc']
        for e in TC[k]: addudl(F,e,v)
    LC[nm]=F
# suhu : gaya ekivalen axial pada elemen terkekang -> pakai beban nodal setara
alp=1.2e-5
for nm,dT in (('EUN',P['dT']),('EUN-N',-P['dT'])):
    F=newF()
    for E_ in EL:
        N=E_['p']['A']*205000.0*alp*dT      # gaya tekan ekivalen
        T=E_['T']; e=E_['e']
        gv=T.T@np.array([N,0,0])
        a,b=idx[e['n1']]*6,idx[e['n2']]*6
        F[a:a+3]-=gv; F[b:b+3]+=gv
    LC[nm]=F
# ---------- tumpuan ----------
SUP={1:'011000',16:'111000',48:'001000',56:'101000'}
fix=[]
for n,c in SUP.items():
    for k,ch in enumerate(c):
        if ch=='1': fix.append(idx[n]*6+k)
free=np.array(sorted(set(range(ND))-set(fix)))
Kff=K[np.ix_(free,free)]
w=np.linalg.eigvalsh(Kff)
print("eigenvalue min Kff = %.4g  (harus > 0 -> stabil)"%w.min())
print("bilangan kondisi   = %.3g"%(w.max()/w.min()))
U={}
lu=np.linalg.cholesky(Kff) if w.min()>0 else None
for k,F in LC.items():
    u=np.zeros(ND); u[free]=np.linalg.solve(Kff,F[free]); U[k]=u
np.save('U.npy',np.array([U[k] for k in LC]))
json.dump(list(LC),open('lcnames.json','w'))
print("\nLENDUTAN tengah bentang (node 86, x=46.67 m, y=3.8 m):")
for k in ('MS','MA','TD-BTR','TD-BGT','TP'):
    print("   %-8s dz = %8.2f mm"%(k,U[k][idx[86]*6+2]))
dz=U['TD-BTR'][idx[86]*6+2]+U['TD-BGT'][idx[86]*6+2]
print("   LENDUT-TD (BTR+BGT) dz = %.2f mm ; batas L/800 = %.2f mm -> %s"%(dz,99997.5/800,"OK" if abs(dz)<99997.5/800 else "LEBIH"))
print("\nREAKSI VERTIKAL:")
for k in ('MS','MA','TD-BTR'):
    Rz=(K@U[k]-LC[k])
    tot=sum(Rz[idx[n]*6+2] for n in SUP)
    print("   %-8s sum Rz = %10.1f kN"%(k,-tot/1000))
pickle.dump(dict(U=U,LC=list(LC),SUP=SUP),open('sol.pkl','wb'))

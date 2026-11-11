import json,math,re,collections
import numpy as np
D=json.load(open('fix.json')); R=json.load(open('res.json'))
nodes={int(k):np.array(v) for k,v in D['nodes'].items()}
elems=D['elems']; newsec=D['newsec']; PANEL=D['panel']
bx={float(k):{float(a):b for a,b in v.items()} for k,v in D['bx'].items()}
# ---------- section properties ----------
sec=None;S={}
for ln in open('new.mct',errors='ignore'):
    s=ln.strip()
    if s.startswith('*'): sec=s.split(',')[0].split()[0].upper(); continue
    if sec!='*SECTION' or not s or s.startswith(';'): continue
    f=[x.strip() for x in s.split(',')]
    if f[1] in ('DBUSER','TAPERED'): S[int(f[0])]=f
def Hprop(H,B,tw,tf):
    A=2*B*tf+(H-2*tf)*tw
    Iy=(B*H**3-(B-tw)*(H-2*tf)**3)/12.0          # sumbu kuat (lokal y)
    Iz=(2*tf*B**3+(H-2*tf)*tw**3)/12.0           # sumbu lemah (lokal z)
    J=(2*B*tf**3+(H-tf)*tw**3)/3.0
    Zy=B*tf*(H-tf)+tw*(H-2*tf)**2/4.0
    Zz=tf*B*B/2.0+(H-2*tf)*tw*tw/4.0
    return dict(A=A,Iy=Iy,Iz=Iz,J=J,Zy=Zy,Zz=Zz,H=H,B=B)
def Pprop(Do,t):
    di=Do-2*t; A=math.pi/4*(Do**2-di**2); I=math.pi/64*(Do**4-di**4)
    Z=(Do**3-di**3)/6.0
    return dict(A=A,Iy=I,Iz=I,J=2*I,Zy=Z,Zz=Z,H=Do,B=Do)
PROP={};NAME={}
for i,f in S.items():
    nm=f[2].strip(); NAME[i]=nm
    if f[1]=='TAPERED':
        PROP[i]=Hprop(950,420,12,16); continue
    shape=f[12]; mode=f[13]; d=[x for x in f[14:] if x!='']
    if mode=='1':
        m=re.search(r'(\d+)x(\d+)x([\d.]+)/([\d.]+)',' '.join(d)); H,B,tw,tf=[float(x) for x in m.groups()]
        PROP[i]=Hprop(H,B,tw,tf); continue
    d=[float(x) for x in d]
    PROP[i]=Hprop(d[0],d[1],d[2],d[3]) if shape=='H' else Pprop(d[0],d[1])
for dpt,isec in newsec.items():
    PROP[int(isec)]=Hprop(float(dpt),420,12,16); NAME[int(isec)]="CG-%d"%int(dpt)
E=2.0904e1*1e3   # tonf/mm2 -> ... model: 2.0904e+001 tonf/mm2 = 205000 N/mm2
E=205000.0       # N/mm2
G=E/2.6
RHO=7.85e-5      # N/mm3  (78.5 kN/m3)
# ---------- assembly ----------
ids=sorted(nodes); idx={n:i for i,n in enumerate(ids)}; ND=len(ids)*6
def tmat(p1,p2,beta=0.0):
    L=np.linalg.norm(p2-p1); ex=(p2-p1)/L
    up=np.array([0.,0.,1.])
    if abs(np.dot(ex,up))>0.9999: up=np.array([1.,0.,0.])
    ey=np.cross(up,ex); ey/=np.linalg.norm(ey); ez=np.cross(ex,ey)
    if beta:
        c,s=math.cos(beta),math.sin(beta); ey,ez=c*ey+s*ez,-s*ey+c*ez
    return L,np.vstack([ex,ey,ez])
def kloc(L,p):
    A,Iy,Iz,J=p['A'],p['Iy'],p['Iz'],p['J']
    k=np.zeros((12,12))
    k[0,0]=k[6,6]=E*A/L; k[0,6]=k[6,0]=-E*A/L
    k[3,3]=k[9,9]=G*J/L; k[3,9]=k[9,3]=-G*J/L
    for (i1,i2,i3,i4),I in (((1,5,7,11),Iz),((2,4,8,10),Iy)):
        sgn=1 if I is Iz else -1
        a=12*E*I/L**3; b=6*E*I/L**2; c=4*E*I/L; d=2*E*I/L
        k[i1,i1]+=a; k[i1,i3]-=a; k[i3,i1]-=a; k[i3,i3]+=a
        k[i2,i2]+=c; k[i4,i4]+=c; k[i2,i4]+=d; k[i4,i2]+=d
        k[i1,i2]+=sgn*b; k[i2,i1]+=sgn*b; k[i1,i4]+=sgn*b; k[i4,i1]+=sgn*b
        k[i3,i2]-=sgn*b; k[i2,i3]-=sgn*b; k[i3,i4]-=sgn*b; k[i4,i3]-=sgn*b
    return k
EL=[]
for e in elems:
    p1,p2=nodes[e['n1']],nodes[e['n2']]
    L,T=tmat(p1,p2,math.radians(e['ang']))
    R12=np.zeros((12,12))
    for b in range(4): R12[3*b:3*b+3,3*b:3*b+3]=T
    pr=PROP[e['sec']]
    EL.append(dict(e=e,L=L,T=T,R=R12,p=pr,k=R12.T@kloc(L,pr)@R12))
K=np.zeros((ND,ND))
def dofs(e): 
    a,b=idx[e['n1']]*6,idx[e['n2']]*6
    return list(range(a,a+6))+list(range(b,b+6))
for E_ in EL:
    d=dofs(E_['e']); K[np.ix_(d,d)]+=E_['k']
print("DOF:",ND,"elemen:",len(EL))
np.save('K.npy',K)
json.dump({'ids':ids},open('mesh.json','w'))
import pickle; pickle.dump(dict(EL=[{k:v for k,v in x.items() if k!='k'} for x in EL],PROP=PROP,NAME=NAME,idx=idx,ids=ids),open('mesh.pkl','wb'))

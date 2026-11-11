import math,pickle,collections,json
import numpy as np
UP={}   # iSEC -> (shape, dims)  penampang pengganti
for i in range(18,24): UP[i]=('P',(267.4,9.3))     # BR  165.2x7.1  -> 267.4x9.3
for i in range(26,39): UP[i]=('P',(216.3,8.2))     # BRT 168x7.11   -> 216.3x8.2
UP[55]=('H',(700,500,16,22))                        # EP1
src=open('check6.py').read()
inj="""
def _Hp(H,B,tw,tf):
    A=2*B*tf+(H-2*tf)*tw
    return dict(A=A,Iy=(B*H**3-(B-tw)*(H-2*tf)**3)/12.0,Iz=(2*tf*B**3+(H-2*tf)*tw**3)/12.0,
      J=(2*B*tf**3+(H-tf)*tw**3)/3.0,Zy=B*tf*(H-tf)+tw*(H-2*tf)**2/4.0,Zz=tf*B*B/2.0+(H-2*tf)*tw*tw/4.0,H=H,B=B)
def _Pp(Do,t):
    di=Do-2*t; A=math.pi/4*(Do**2-di**2); I=math.pi/64*(Do**4-di**4)
    return dict(A=A,Iy=I,Iz=I,J=2*I,Zy=(Do**3-di**3)/6.0,Zz=(Do**3-di**3)/6.0,H=Do,B=Do)
import json as _j
_UP=_j.load(open('upgrade.json'))
for _k,_v in _UP.items():
    _k=int(_k)
    PROP[_k]=_Hp(*_v[1]) if _v[0]=='H' else _Pp(*_v[1])
    NAME[_k]=NAME[_k]+"*"
for _E in EL: _E['p']=PROP[_E['e']['sec']]
K=np.zeros((ND,ND))
def _kl(L,p,pin):
    A,Iy,Iz,J=p['A'],p['Iy'],p['Iz'],p['J']; E=205000.0; G=E/2.6
    k=np.zeros((12,12))
    if pin:
        k[3,3]=k[9,9]=G*J/L; k[3,9]=k[9,3]=-G*J/L; return k
    k[0,0]=k[6,6]=E*A/L; k[0,6]=k[6,0]=-E*A/L
    k[3,3]=k[9,9]=G*J/L; k[3,9]=k[9,3]=-G*J/L
    for (i1,i2,i3,i4),I,sgn in (((1,5,7,11),Iz,1),((2,4,8,10),Iy,-1)):
        a1=12*E*I/L**3; b=6*E*I/L**2; c=4*E*I/L; d2=2*E*I/L
        k[i1,i1]+=a1;k[i1,i3]-=a1;k[i3,i1]-=a1;k[i3,i3]+=a1
        k[i2,i2]+=c;k[i4,i4]+=c;k[i2,i4]+=d2;k[i4,i2]+=d2
        k[i1,i2]+=sgn*b;k[i2,i1]+=sgn*b;k[i1,i4]+=sgn*b;k[i4,i1]+=sgn*b
        k[i3,i2]-=sgn*b;k[i2,i3]-=sgn*b;k[i3,i4]-=sgn*b;k[i4,i3]-=sgn*b
    return k
for _E in EL:
    _e=_E['e']; _R=np.zeros((12,12))
    for _b in range(4): _R[3*_b:3*_b+3,3*_b:3*_b+3]=_E['T']
    K[np.ix_(dofs(_e),dofs(_e))]+=_R.T@_kl(_E['L'],_E['p'],_e['id'] in STRIDS)@_R
"""
src=src.replace("# ---------- DIAFRAGMA LANTAI",inj+"\n# ---------- DIAFRAGMA LANTAI")
json.dump({str(k):v for k,v in UP.items()},open('upgrade.json','w'))
open('check7.py','w').write(src)

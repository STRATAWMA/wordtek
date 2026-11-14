# -*- coding: utf-8 -*-
"""Geometri jembatan pelengkung A80 - dari APPROVAL DRAWING GA-ITK09, rev 1."""
import numpy as np

L      = 80000.0          # bentang
NP     = 16               # jumlah panel
A      = L/NP             # 5000 mm
B      = 10000.0          # jarak as-ke-as rangka pelengkung
YS     = [600.0+1100.0*i for i in range(9)]   # 9 garis stringer: 600..9400

# Ordinat chord ATAS pelengkung (sumbu), di atas level balok tarik.
# Titik 2..8 dari SECTION A..G; titik 1 dan 0 hasil ekstrapolasi kurva
# (x=0 memberi -33 mm, jadi pelengkung bertumpu tepat di level balok tarik).
_TH = {40000:19095, 35000:18890, 30000:18175, 25000:16930,
       20000:15115, 15000:12650, 10000: 9410,  5000: 5246, 0:0.0}
# Tinggi rangka pelengkung (chord ATAS ke chord TENGAH), dari SECTION A..G.
_DP = {40000: 3990, 35000: 3995, 30000: 3915, 25000: 3750,
       20000: 3475, 15000: 3060, 10000: 2455,  5000: 1605, 0:0.0}

def _sym(d,x):
    """interpolasi linear antar titik buhul, simetris terhadap tengah bentang"""
    xx = x if x<=L/2 else L-x
    ks = sorted(d)
    if xx<=ks[0]: return float(d[ks[0]])
    if xx>=ks[-1]: return float(d[ks[-1]])
    for a,b in zip(ks[:-1],ks[1:]):
        if a<=xx<=b:
            t=(xx-a)/(b-a); return float(d[a]+(d[b]-d[a])*t)
def zT(x): return _sym(_TH,x)                 # chord atas
def zM(x): return _sym(_TH,x)-_sym(_DP,x)     # chord tengah
def dep(x): return _sym(_DP,x)

XS = [A*i for i in range(NP+1)]               # 0 .. 80000

if __name__=='__main__':
    print("x(mm)   chord ATAS   tinggi rangka   chord TENGAH")
    for x in XS[:9]:
        print("%6.0f %10.0f %14.0f %14.0f"%(x,zT(x),dep(x),zM(x)))
    print("\nbentang %.0f | %d panel x %.0f | lebar %.0f | %d stringer di y=%s"
          %(L,NP,A,B,len(YS),", ".join("%.0f"%y for y in YS)))

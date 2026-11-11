import json,math,collections
g=json.load(open('geom.json'))
nodes={int(k):v for k,v in g['nodes'].items()}
DUP={7,92,185,201,217,233,249,265,281,299,330}   # elemen duplikat -> dikecualikan dari beban

# ---------- element lists ----------
def rng(ids):
    ids=sorted(ids); out=[];i=0
    while i<len(ids):
        j=i
        while j+1<len(ids) and ids[j+1]==ids[j]+1: j+=1
        out.append(str(ids[i]) if i==j else "%dto%d"%(ids[i],ids[j])); i=j+1
    return " ".join(out)

YS=[500,1600,2700,3800,4900,6000,7100]
STR={y:[e for e in g['ylines'][str(y)] if e not in DUP] for y in YS}
BC ={0:[e for e in g['ylines']['0'] if e not in DUP], 7600:[e for e in g['ylines']['7600'] if e not in DUP]}
TC ={0:[e for e in range(72,86) if e not in DUP], 7600:[e for e in range(132,146) if e not in DUP]}
ALL=[e for e,_,_,_,_ in g['elems']]

# node panel-point lists per stringer line (for BGT) at x=46665.5
XBGT=46665.5
NBGT={}
for y in YS:
    for n,(x,yy,z) in nodes.items():
        if abs(yy-y)<1 and abs(x-XBGT)<1 and z<3000: NBGT[y]=n
# ---------- PARAMETER ----------
P=dict(L=99.9975,npan=15,a=6.6665,Bas=7.6,Wroad=6.0,Wtrot=0.5,nstr=7,s=1.1,
       tslab=0.25,ttrot=0.35,tasp=0.05,gc=24.0,gasp=22.0,gs=78.5,
       wrail=0.5,qped=5.0,
       PBt=2.4,PBl=1.2,PBv=0.96,Atruss=2.370,hdeck=0.35,htruss=8.50,
       EWLq=1.46,hEWL=1.8,dT=15.0,
       PGA=0.30,Ss=0.70,S1=0.30,Fpga=1.2,Fa=1.3,Fv=2.8,Req=1.0,
       Wsteel=3188.8)
L=P['L']; s=P['s']; Wt=P['Wtrot']

# ---------- TRIBUTARI ----------
# b_slab : edge = s/2 + Wtrot ; interior = s
# roadway 0.8 .. 6.8 ; strip 100% BTR = 5.5 m tengah (1.05..6.55)
b_slab={y:(s/2+Wt if y in (500,7100) else s) for y in YS}
b_road={y:(0.25 if y in (500,7100) else s) for y in YS}
b_btr ={y:(0.125 if y in (500,7100) else s) for y in YS}

q_slab=P['tslab']*P['gc']                       # 6.00 kPa
q_trot=(P['ttrot']-P['tslab'])*P['gc']*Wt       # 1.20 kN/m (topping 10cm x 0.5m)
q_asp =P['tasp']*P['gasp']                      # 1.10 kPa
qBTR  = 9.0 if L<=30 else 9.0*(0.5+15.0/L)      # 5.85 kPa
FBD   = 0.4 if L<=50 else (0.3 if L>=90 else 0.4-0.1*(L-50)/40)
qBGT  = 49.0*(1+FBD)                            # 63.7 kN/m

MS   ={y:q_slab*b_slab[y] for y in YS}
MAtr ={y:(q_trot+P['wrail'] if y in (500,7100) else 0.0) for y in YS}
MAasp={y:q_asp*b_road[y] for y in YS}
MA   ={y:MAtr[y]+MAasp[y] for y in YS}
BTR  ={y:qBTR*b_btr[y] for y in YS}
BGT  ={y:qBGT*b_btr[y] for y in YS}
TP   ={y:(P['qped']*Wt if y in (500,7100) else 0.0) for y in YS}

# ---------- ANGIN ----------
Aexp = 2*P['Atruss']+P['hdeck']                 # m2 per m bentang
EWS_tot=P['PBt']*Aexp                           # kN/m
Ltc=93.331
EWS_tc = P['PBt']*P['Atruss']/2*L/Ltc        # per rangka, chord atas (dikoreksi L/Ltc)
EWS_bc = P['PBt']*P['Atruss']/2 + P['PBt']*P['hdeck']/2
EWL_h  = P['EWLq']/2                            # per chord bawah
EWL_v  = P['EWLq']*P['hEWL']/P['Bas']           # +/- kN/m
EWV_tot= P['PBv']*P['Bas']
EWV_w  = EWV_tot*0.75; EWV_l=EWV_tot*0.25

# ---------- GEMPA ----------
As=P['Fpga']*P['PGA']; SDS=P['Fa']*P['Ss']; SD1=P['Fv']*P['S1']; Ts=SD1/SDS
Csm=SDS; coef=Csm/P['Req']
w_slab_m=P['Bas']*P['tslab']*P['gc']            # 45.6
w_trot_m=2*q_trot; w_asp_m=P['Wroad']*q_asp; w_rail_m=2*P['wrail']
w_steel_m=P['Wsteel']/L
Wperm_m=w_slab_m+w_trot_m+w_asp_m+w_rail_m+w_steel_m
Wperm=Wperm_m*L
EQ_tot=coef*Wperm
# distribusi: massa dek -> 7 stringer (prop. b_slab), massa baja -> 55% chord bawah,45% chord atas
w_deck_m=w_slab_m+w_trot_m+w_asp_m+w_rail_m
EQ_str={y:coef*(w_deck_m*b_slab[y]/P['Bas']) for y in YS}
EQ_bc = coef*w_steel_m*0.55/2
EQ_tc = coef*w_steel_m*0.45/2*(L/Ltc)           # chord atas hanya 93.331 m
chk=sum(EQ_str.values())*L+2*EQ_bc*L+2*EQ_tc*Ltc


# ---------- GAYA REM TB (SNI 1725-2016 ps.8.7) ----------
P['Wtruk']=500.0        # truk desain SNI 1725 ps.8.4 (50+225+225 kN)
P['Wtruk_AA']=325.0     # truk desain AASHTO HL-93 (35+145+145 kN)
P['qLane_AA']=9.3       # beban lajur AASHTO (kN/m)
P['wlajur']=2.75        # lebar lajur rencana
P['nlajur']=2           # SNI 1725 Tabel 12: 5.5 <= w < 8.25 -> 2 lajur
P['m2']=1.0; P['m1']=1.2  # faktor kehadiran banyak lajur, SNI Tabel 14
tb_a = 0.25*P['Wtruk']
tb_b = 0.05*(P['Wtruk']+qBTR*P['wlajur']*L)
tb_lane = max(tb_a,tb_b)
TB_tot = max(P['nlajur']*tb_lane*P['m2'], 1*tb_lane*P['m1'])
# pembanding AASHTO LRFD 3.6.4
tbA_a = 0.25*P['Wtruk_AA']
tbA_b = 0.05*(P['Wtruk_AA']+P['qLane_AA']*L)
TB_AA = max(P['nlajur']*max(tbA_a,tbA_b)*P['m2'], 1*max(tbA_a,tbA_b)*P['m1'])
# disebar pada 2 lajur rencana = 5.5 m -> stringer ST-2..ST-6 (1.1 m each)
Wbrake = P['nlajur']*P['wlajur']
YS_TB  = ['1600','2700','3800','4900','6000']
TB_str = TB_tot/L*s/Wbrake
# kopel vertikal dari lengan 1.8 m di atas lantai
TB_M  = TB_tot*P['hEWL']
TB_V  = TB_M/L/2        # per rangka, di tiap tumpuan
NSUP  = dict(x0=[1,48], xL=[16,56])

R=dict(P=P,Ltc=Ltc,tb_a=tb_a,tb_b=tb_b,tb_lane=tb_lane,TB_tot=TB_tot,TB_AA=TB_AA,
  tbA_a=tbA_a,tbA_b=tbA_b,Wbrake=Wbrake,YS_TB=YS_TB,TB_str=TB_str,TB_M=TB_M,TB_V=TB_V,NSUP=NSUP,b_slab=b_slab,b_road=b_road,b_btr=b_btr,q_slab=q_slab,q_trot=q_trot,q_asp=q_asp,
  qBTR=qBTR,FBD=FBD,qBGT=qBGT,MS=MS,MAtr=MAtr,MAasp=MAasp,MA=MA,BTR=BTR,BGT=BGT,TP=TP,
  Aexp=Aexp,EWS_tot=EWS_tot,EWS_tc=EWS_tc,EWS_bc=EWS_bc,EWL_h=EWL_h,EWL_v=EWL_v,
  EWV_tot=EWV_tot,EWV_w=EWV_w,EWV_l=EWV_l,As=As,SDS=SDS,SD1=SD1,Ts=Ts,Csm=Csm,coef=coef,
  w_slab_m=w_slab_m,w_trot_m=w_trot_m,w_asp_m=w_asp_m,w_rail_m=w_rail_m,w_steel_m=w_steel_m,
  Wperm_m=Wperm_m,Wperm=Wperm,EQ_tot=EQ_tot,EQ_str=EQ_str,EQ_bc=EQ_bc,EQ_tc=EQ_tc,chk=chk,
  STR={str(k):v for k,v in STR.items()},BC={str(k):v for k,v in BC.items()},
  TC={str(k):v for k,v in TC.items()},NBGT={str(k):v for k,v in NBGT.items()},ALL=ALL)
json.dump(R,open('res.json','w'),indent=1)

f="%-42s %10.4f %s"
print("="*72); print("TRIBUTARI (m)")
for y in YS: print("  stringer y=%4d  b_slab=%.3f  b_road=%.3f  b_BTR=%.3f"%(y,b_slab[y],b_road[y],b_btr[y]))
print("  SUM b_slab=%.3f (=%.1f)  b_road=%.3f (=%.1f)  b_BTR=%.3f (=5.75)"%(sum(b_slab.values()),P['Bas'],sum(b_road.values()),P['Wroad'],sum(b_btr.values())))
print("="*72)
print(f%("q plat 250mm (kN/m2)",q_slab,""))
print(f%("q trotoar topping 100mm x 0.5m (kN/m)",q_trot,""))
print(f%("q aspal 50mm (kN/m2)",q_asp,""))
print(f%("BTR q (kPa) L=100m",qBTR,"")); print(f%("FBD/DLA",FBD,"")); print(f%("BGT p x (1+FBD) (kN/m)",qBGT,""))
for nm,d in [("MS-plat",MS),("MA-trot+rail",MAtr),("MA-aspal",MAasp),("MA-total",MA),("TD-BTR",BTR),("TD-BGT (kN titik)",BGT),("TP pejalan kaki",TP)]:
    print("  %-18s "%nm+"  ".join("%.3f"%d[y] for y in YS)+"   SUM=%.2f"%sum(d.values()))
print("="*72)
print(f%("Area terekspos angin (m2/m)",Aexp,""))
print(f%("EWs total (kN/m)",EWS_tot,"")); print(f%("  -> chord atas tiap sisi",EWS_tc,"")); print(f%("  -> chord bawah tiap sisi",EWS_bc,""))
print(f%("EWl horizontal tiap chord bawah",EWL_h,"")); print(f%("EWl kopel vertikal +/-",EWL_v,""))
print(f%("EWv total (kN/m) ke atas",EWV_tot,"")); print(f%("  windward / leeward",EWV_w,"/ %.3f"%EWV_l))
print("="*72)
print(f%("As=Fpga*PGA",As,"")); print(f%("SDS",SDS,"")); print(f%("SD1",SD1,"")); print(f%("Ts (s)",Ts,""))
print(f%("Csm/R = koef gempa",coef,""))
print(f%("W permanen (kN/m)",Wperm_m,"")); print(f%("W permanen total (kN)",Wperm,""))
print(f%("EQ total (kN)",EQ_tot,""))
print("  EQ stringer: "+"  ".join("%.3f"%EQ_str[y] for y in YS))
print(f%("EQ chord bawah tiap sisi (kN/m)",EQ_bc,"")); print(f%("EQ chord atas tiap sisi (kN/m)",EQ_tc,""))
print(f%("cek jumlah (kN)",chk,""))
print("="*72)
print("STRINGER elem:");  [print("  y=%4d : %s"%(y,rng(STR[y]))) for y in YS]
print("CHORD BAWAH: y=0 : %s | y=7600 : %s"%(rng(BC[0]),rng(BC[7600])))
print("CHORD ATAS : y=0 : %s | y=7600 : %s"%(rng(TC[0]),rng(TC[7600])))
print("NODE BGT (x=46665.5):",{y:NBGT[y] for y in YS})

# tambahan: simpan string range
R['_rng']={str(y):rng(STR[y]) for y in YS}
R['_rngBC']={str(y):rng(BC[y]) for y in (0,7600)}
R['_rngTC']={str(y):rng(TC[y]) for y in (0,7600)}
R['_rngALL']=rng(ALL)
json.dump(R,open('res.json','w'),indent=1)
print("ranges saved")

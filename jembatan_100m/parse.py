import re,math,json,collections
L=open('model.mct',errors='ignore').read().splitlines()
sec=None;nodes={};elems=[];sects={}
for ln in L:
    s=ln.strip()
    if s.startswith('*'):
        sec=s.split(',')[0].split()[0].upper(); continue
    if not s or s.startswith(';'): continue
    f=[x.strip() for x in s.split(',')]
    if sec=='*NODE' and len(f)>=4:
        try: nodes[int(f[0])]=(float(f[1]),float(f[2]),float(f[3]))
        except: pass
    if sec=='*ELEMENT' and len(f)>=6 and f[1]=='BEAM':
        try: elems.append((int(f[0]),int(f[2]),int(f[3]),int(f[4]),int(f[5])))
        except: pass
    if sec=='*SECTION' and len(f)>5 and f[1] in ('DBUSER','TAPERED'):
        sects[int(f[0])]=(f[2],f[1],f)
print("nodes",len(nodes),"elems",len(elems),"sects",len(sects))
# section area
def area(iS):
    nm,ty,f=sects[iS]
    if ty=='TAPERED':
        return None
    shape=f[12].strip(); mode=f[13].strip()
    d=[float(x) for x in f[14:] if x!='']
    if mode=='1': return None,shape,nm
    if shape=='H':
        H,B,tw,tf=d[0],d[1],d[2],d[3]
        return 2*B*tf+(H-2*tf)*tw,shape,nm,H,B
    if shape=='P':
        D,t=d[0],d[1]
        return math.pi/4*(D*D-(D-2*t)**2),shape,nm,D,D
    return None,shape,nm
for i in sorted(sects): 
    pass
# group stringer lines by y
ylines=collections.defaultdict(list)
for e,m,p,n1,n2 in elems:
    y1=nodes[n1][1]; y2=nodes[n2][1]
    if abs(y1-y2)<1 and nodes[n1][2]<3000 and nodes[n2][2]<3000 and abs(nodes[n1][0]-nodes[n2][0])>1:
        ylines[round(y1)].append(e)
for y in sorted(ylines): print("y=",y,"nelem",len(ylines[y]),sorted(ylines[y])[:3],"...",sorted(ylines[y])[-1])
json.dump({'nodes':{str(k):v for k,v in nodes.items()},'elems':elems,
           'ylines':{str(k):sorted(v) for k,v in ylines.items()}},open('geom.json','w'))

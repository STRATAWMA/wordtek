MM={'STRUCTYPE','NODE','ELEMENT','GROUP','MATERIAL','MATL-COLOR','SECTION','DGN-SECT',
    'SECT-COLOR','THICKNESS','THIK-COLOR','DGN-STEEL','CONSTRAINT','RIGIDLINK',
    'MVLDCODE','LINELANE','VEHICLE','MVLDCASE','DGN-MATL','REBAR-MATL-CODE'}
M ={'STLDCASE','SELFWEIGHT','BEAMLOAD','CONLOAD','ELTEMPER','LOADCOMB'}
NEU={'VERSION','PROJINFO','UNIT','ENDDATA','LC-COLOR','USE-STLD'}
import sys
tot=0
for fn in sys.argv[1:]:
    unit=None;prev=None;bad=0;seen={}
    for i,l in enumerate(open(fn),1):
        t=l.strip()
        if not t or t.startswith(';'): continue
        if t.startswith('*'):
            tag=t.split(',')[0].split()[0].upper().lstrip('*')
            if tag=='UNIT': prev='UNIT'; continue
            if tag not in MM|M|NEU: print("  TIDAK DIKENALI:",fn,i,tag); bad+=1
            elif tag in MM and unit!='MM': print("  SALAH %s:%d  %-14s dibaca di %s, harus MM"%(fn,i,tag,unit)); bad+=1
            elif tag in M and unit!='M': print("  SALAH %s:%d  %-14s dibaca di %s, harus M"%(fn,i,tag,unit)); bad+=1
            if tag in MM|M: seen[tag]=unit
            prev=tag; continue
        if prev=='UNIT': unit=t.split(',')[1].strip()
    tot+=bad
    print("%-22s blok sensitif=%-2d  SALAH=%d"%(fn,len(seen),bad))
print("TOTAL SALAH SATUAN:",tot)

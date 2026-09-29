"""
MODEL 1 - Jembatan Rangka Baja Warren L = 60 m (Road-4 STA 0+750) di Robot Structural Analysis.
Jalankan di laptop (Windows, Robot terbuka/terinstal):
    pip install comtypes
    python robot\\model_1_rangka_60m.py
Output: robot\\Rangka_60m_R4_0750.rtd

Geometri & profil = hasil bridge_design.py (output/frame_section.csv).
Beban  : SNI 1725:2016 (MS, MA, BTR+BGT, TB, EW) + kendaraan klien Scania P410 B8x4 58 t (konvoi).
Kombinasi: SNI 1725:2016 Tabel 1 (= AASHTO LRFD Tabel 3.4.1-1): Kuat I, Kuat III, Kuat V, Layan I, Layan II, Fatik I.
"""
import csv, math, os
from robot_common import (app, K, new_project, material, wb_section, support, pinned_release, Model,
                          case, self_weight, bar_udl, bar_point, node_force, combo, bar_groups, lever, calc_and_save)

HERE = os.path.dirname(os.path.abspath(__file__))
SEC = {r["FrameCode"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "output", "frame_section.csv")))}

L, NP, H, B = 60.0, 12, 6.0, 11.53
p = L / NP
yL, yR = -B / 2, B / 2
STR_Y = [-5.0 + k * 10.0 / 6 for k in range(7)]          # 7 stringer
g = 9.81

# ------------------------------------------------------------------ model
st = new_project()
material(st)
for code, r in SEC.items():
    if r["Bridge"].startswith("Truss"):
        f = lambda k: float(r[k])
        wb_section(st, code, f("d"), f("bf_top"), f("tw"), f("tf_top"), f("bf_bot"), f("tf_bot"))
pinned_release(st, "SENDI")
support(st, "SENDI_XYZ", 1, 1, 1)
support(st, "SENDI_XZ", 1, 0, 1)
support(st, "ROL_YZ", 0, 1, 1)
support(st, "ROL_Z", 0, 0, 1)

m = Model(st)


def grp(prefix, idx, n):
    """kode batang individual -> kode frame (grup zona) sesuai frame_section.csv"""
    code = f"{prefix}-{idx:02d}"
    for k, r in SEC.items():
        if code in [x.strip() for x in r["Members"].split(",")]:
            return k
    raise KeyError(code)


bot = {}; top = {}
for y in (yL, yR):
    side = "L" if y < 0 else "R"
    for i in range(NP + 1):
        bot[(side, i)] = m.node(i * p, y, 0.0)
    for k in range(NP):
        top[(side, k)] = m.node((k + 0.5) * p, y, H)
    for i in range(NP):                                   # Bottom Chord
        m.bar(bot[(side, i)], bot[(side, i + 1)], grp("BC", i + 1, NP), f"BC-{i+1:02d}{side}")
    for k in range(NP - 1):                               # Top Chord
        m.bar(top[(side, k)], top[(side, k + 1)], grp("TC", k + 1, NP), f"TC-{k+1:02d}{side}")
    for i in range(NP):                                   # End Chord & Diagonal Chord
        for j in (0, 1):
            n = 2 * i + j + 1
            code = "EC" if n in (1, 24) else "DC"
            a, b = (bot[(side, i)], top[(side, i)]) if j == 0 else (top[(side, i)], bot[(side, i + 1)])
            m.bar(a, b, grp(code, n, 24), f"{code}-{n:02d}{side}")

# Cross girder (CG-1) di tiap buhul bawah, dipotong di titik stringer; sambungan sendi ke rangka
str_nodes = {}
for i in range(NP + 1):
    ys = [yL] + STR_Y + [yR]
    nds = [bot[("L", i)]] + [m.node(i * p, y, 0.0) for y in STR_Y] + [bot[("R", i)]]
    for j, y in enumerate(STR_Y):
        str_nodes[(i, j)] = nds[j + 1]
    for a, b in zip(nds[:-1], nds[1:]):
        m.bar(a, b, "CG-1", f"CG-{i:02d}")
# Stringer (ST-1) sendi-sendi di cross girder
ST_BARS = {}
for j in range(len(STR_Y)):
    for i in range(NP):
        ST_BARS[(j, i)] = m.bar(str_nodes[(i, j)], str_nodes[(i + 1, j)], "ST-1", "ST-1", release="SENDI")
# Brace atas (BR-1) di setiap buhul atas + portal di ujung
for k in range(NP):
    m.bar(top[("L", k)], top[("R", k)], "BR-1", "BR-1", release="SENDI")
# Diagonal Member (DM-1): ikatan angin X atas & bawah, disambung di tengah silang
for k in range(NP - 1):
    c = m.node((k + 1) * p, 0.0, H)
    for a, b in ((top[("L", k)], top[("R", k + 1)]), (top[("R", k)], top[("L", k + 1)])):
        m.bar(a, c, "DM-1", "DM-1 atas", release="SENDI"); m.bar(c, b, "DM-1", "DM-1 atas", release="SENDI")
for i in range(NP):
    c = m.node((i + 0.5) * p, 0.0, -0.05)   # sedikit di bawah stringer agar tidak memotong ST
    for a, b in ((bot[("L", i)], bot[("R", i + 1)]), (bot[("R", i)], bot[("L", i + 1)])):
        m.bar(a, c, "DM-1", "DM-1 bawah", release="SENDI"); m.bar(c, b, "DM-1", "DM-1 bawah", release="SENDI")

# Perletakan: A1 sendi, A2 rol memanjang
st.Nodes.Get(bot[("L", 0)]).SetLabel(K("I_LT_SUPPORT"), "SENDI_XYZ")
st.Nodes.Get(bot[("R", 0)]).SetLabel(K("I_LT_SUPPORT"), "SENDI_XZ")
st.Nodes.Get(bot[("L", NP)]).SetLabel(K("I_LT_SUPPORT"), "ROL_YZ")
st.Nodes.Get(bot[("R", NP)]).SetLabel(K("I_LT_SUPPORT"), "ROL_Z")
bar_groups(st, m.groups)

# ------------------------------------------------------------------ beban
trib = [10.0 / 6] * 7; trib[0] = trib[-1] = 10.0 / 12 + 0.5 + 0.5   # stringer tepi + kantilever s/d barrier
all_st = list(ST_BARS.values())
edge_st = [ST_BARS[(j, i)] for j in (0, 6) for i in range(NP)]

c1 = case(st, 1, "MS1 Berat sendiri baja (+20% sambungan)"); self_weight(c1, 1.20)
c2 = case(st, 2, "MS2 Pelat beton t=250 + barrier")
for j in range(7):
    bar_udl(c2, [ST_BARS[(j, i)] for i in range(NP)], pz=-0.25 * 24e3 * trib[j])
bar_udl(c2, edge_st, pz=-6.0e3)                                            # barrier 6 kN/m
lane_trib = [10.0 / 6] * 7; lane_trib[0] = lane_trib[-1] = 10.0 / 12   # lebar jalur 10 m
c3 = case(st, 3, "MA Aspal 50 mm")
for j in range(7):
    bar_udl(c3, [ST_BARS[(j, i)] for i in range(NP)], pz=-0.05 * 22e3 * lane_trib[j])

# Beban lajur D (SNI 1725 Ps 8.3): BTR q = 9(0.5+15/L) kPa, BGT 49 kN/m x (1+FBD)
q = 9.0 * (0.5 + 15 / L) * 1e3
FBD = 0.40 - 0.0025 * (L - 50)
lane_trib = [10.0 / 6] * 7; lane_trib[0] = lane_trib[-1] = 10.0 / 12
LL_CASES = []
patterns = [(0, 60, 30), (0, 30, 15), (30, 60, 45), (0, 45, 22.5), (15, 60, 37.5), (0, 15, 5), (45, 60, 55)]
no = 10
for (x0, x1, xk) in patterns:
    c = case(st, no, f"TD BTR {x0}-{x1} m + BGT x={xk}", "I_CN_EXPLOATATION")
    for j in range(7):
        bars = [ST_BARS[(j, i)] for i in range(NP) if x0 <= i * p < x1]
        bar_udl(c, bars, pz=-q * lane_trib[j])
        i = min(int(xk // p), NP - 1)
        bar_point(c, ST_BARS[(j, i)], (xk - i * p) / p, -49e3 * (1 + FBD) * lane_trib[j])
    LL_CASES.append(no); no += 1

# Scania P410 B8x4 58 t - konvoi 2 lajur (jarak bersih 10 m), FBD 30 % dimasukkan ke beban
AX = [7.0, 7.0, 22.0, 22.0]; SP = [1.95, 3.10, 1.37]; GAP = 10.0
truck = []; x = 0.0
for t in range(6):
    for a, w in enumerate(AX):
        truck.append((x, w * g * 1e3 * 1.30))
        if a < 3: x += SP[a]
    x += GAP
WHEEL_Y = [-2.5 - 0.9, -2.5 + 0.9, 2.5 - 0.9, 2.5 + 0.9]
TRUCK_CASES = []
for head in [k * 2.5 for k in range(int((L + truck[-1][0]) / 2.5) + 1)]:
    loads = [(head - off, P) for off, P in truck if 0 <= head - off <= L]
    if not loads:
        continue
    c = case(st, no, f"TT Scania konvoi, kepala x={head:.1f} m", "I_CN_EXPLOATATION")
    for xa, P in loads:
        i = min(int(xa // p), NP - 1)
        for yw in WHEEL_Y:
            for j, f in lever(yw, STR_Y):
                if f > 0:
                    bar_point(c, ST_BARS[(j, i)], (xa - i * p) / p, -P / 2 * f)
    TRUCK_CASES.append(no); no += 1

# Rem TB (SNI 1725 Ps 8.7): maks(25% berat gandar truk, 5% (truk + BTR)) per lajur, 2 lajur
TB = 2 * max(0.25 * 58 * g, 0.05 * (58 * g + q / 1e3 * 5.0 * L)) * 1e3
c_tb = case(st, 90, "TB Gaya rem", "I_CN_EXPLOATATION")
deck_nodes = [str_nodes[(i, j)] for i in range(NP + 1) for j in range(7)]
node_force(c_tb, deck_nodes, fx=TB / len(deck_nodes))
# Angin EWs (SNI 1725 Ps 9.6): TEW = 0.0012 Cw Vw^2 Ab ; Vw 35 m/s, Cw 2.0, Ab = 30 % luas bidang rangka
EW = 0.0012 * 2.0 * 35 ** 2 * (0.30 * p * H) * 1e3
c_ew = case(st, 91, "EWs Angin struktur", "I_CN_WIND")
node_force(c_ew, [top[("L", k)] for k in range(NP)], fy=EW / 2)
node_force(c_ew, [bot[("L", i)] for i in range(NP + 1)], fy=EW / 2)
# Angin pada kendaraan EWl 1.46 kN/m, 1.8 m di atas lantai -> ke stringer tepi sebagai gaya lateral
c_ewl = case(st, 92, "EWl Angin pada kendaraan", "I_CN_WIND")
bar_udl(c_ewl, [ST_BARS[(0, i)] for i in range(NP)], py=1.46e3)

# ------------------------------------------------------------------ kombinasi (SNI 1725:2016 Tabel 1 / AASHTO LRFD 3.4.1)
D_ULS = [(1, 1.1), (2, 1.3), (3, 2.0)]
D_SLS = [(1, 1.0), (2, 1.0), (3, 1.0)]
cn = 200
for ll in LL_CASES + TRUCK_CASES:
    combo(st, cn, f"KUAT I  LL{ll}", D_ULS + [(ll, 1.8), (90, 1.8)]); cn += 1
    combo(st, cn, f"LAYAN II LL{ll}", D_SLS + [(ll, 1.3)], uls=False); cn += 1
    combo(st, cn, f"LAYAN I LL{ll}", D_SLS + [(ll, 1.0), (90, 1.0), (91, 0.3), (92, 1.0)], uls=False); cn += 1
    combo(st, cn, f"KUAT V  LL{ll}", D_ULS + [(ll, 1.4), (90, 1.4), (91, 0.4), (92, 1.0)]); cn += 1
for ll in TRUCK_CASES:   # Fatik I AASHTO: 1.75 x truk (DLA fatik 15 % -> 1.75 x 1.15/1.30)
    combo(st, cn, f"FATIK I LL{ll}", [(ll, 1.75 * 1.15 / 1.30)], uls=False); cn += 1
combo(st, cn, "KUAT III", D_ULS + [(91, 1.4)]); cn += 1
combo(st, cn, "KONSTRUKSI", [(1, 1.4), (2, 1.4)]); cn += 1

calc_and_save(os.path.join(HERE, "Rangka_60m_R4_0750.rtd"))
print(f"Nodes {m.n}, bars {m.b}, kasus LL {len(LL_CASES)} + truk {len(TRUCK_CASES)}, kombinasi {cn - 200}")

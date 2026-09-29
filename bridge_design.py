"""
Preliminary design of steel members (Welded Beam / WB custom) - PT SDA Road-4
  1. Jembatan Rangka Baja STA 0+750, L = 60 m (Warren truss, 12 panels)
  2. Jembatan Fly Over  STA 0+050, L = 30.6 m (composite plate girder, 6 girders @1.7 m)

Codes : SNI 1725-2016 (loading), SNI 1729-2020 / AISC 360 LRFD (steel resistance),
        client spec 3.2.2.2.x (Scania P410 B8x4 58 t), SE Dirjen BM 07/SE/Db/2025 Sec 7.4.
Steel : JIS G3106 SM490YB, Fu = 490 MPa, Fy by thickness (t<=16:365, <=40:355, <=75:335).
Plate : only thicknesses stocked by Indonesian mills (Krakatau Posco / Gunung Raja Paksi).

Run   : python3 bridge_design.py   -> prints report, writes output/*.md + output/*.csv
Pure python, no dependencies (same result on cloud and laptop).
"""
import csv, math, os

E = 200000.0
GUSSET_D = 500  # truss member depth between gusset plates [mm]
FU = 490.0
PLATES = [8, 9, 10, 12, 14, 16, 19, 20, 22, 25, 28, 30, 32, 36, 40, 45, 50]


def fy(t):
    return 365.0 if t <= 16 else 355.0 if t <= 40 else 335.0


# ---------------------------------------------------------------- sections
class WB:
    """Welded I/H: d x bf x tw x tf (mm), optional different bottom flange."""

    def __init__(s, d, bf, tw, tf, bfb=None, tfb=None):
        s.d, s.bf, s.tw, s.tf = d, bf, tw, tf
        s.bfb, s.tfb = bfb or bf, tfb or tf
        s.h = d - s.tf - s.tfb
        s.A = bf * tf + s.bfb * s.tfb + s.h * tw
        # centroid from bottom
        parts = [(s.bfb * s.tfb, s.tfb / 2), (s.h * tw, s.tfb + s.h / 2), (bf * tf, d - tf / 2)]
        s.yb = sum(a * y for a, y in parts) / s.A
        s.Ix = (s.bfb * s.tfb ** 3 + tw * s.h ** 3 + bf * tf ** 3) / 12 + sum(a * (y - s.yb) ** 2 for a, y in parts)
        s.Iy = (tf * bf ** 3 + s.tfb * s.bfb ** 3 + s.h * tw ** 3) / 12
        s.rx, s.ry = math.sqrt(s.Ix / s.A), math.sqrt(s.Iy / s.A)
        s.Fy = fy(max(tw, tf, s.tfb))
        s.kg = s.A * 7.85e-6 * 1000  # kg/m

    @property
    def name(s):
        if s.bfb == s.bf and s.tfb == s.tf:
            return f"WB {s.d}x{s.bf}x{s.tw}x{s.tf}"
        return f"WB {s.d}x{s.bf}/{s.bfb}x{s.tw}x{s.tf}/{s.tfb}"

    def compact_flange(s):
        return (s.bf / 2) / s.tf <= 0.38 * math.sqrt(E / s.Fy)

    def phiPn_c(s, KLx, KLy, lim=120):
        KLx, KLy = KLx * 1000, KLy * 1000  # m -> mm
        # non-slender elements required (AISC B4.1a)
        if (s.bf / 2) / s.tf > 0.56 * math.sqrt(E / s.Fy) or s.h / s.tw > 1.49 * math.sqrt(E / s.Fy):
            return 0.0
        sl = max(KLx / s.rx, KLy / s.ry)
        if sl > lim:  # AASHTO 6.9.3: primary 120, bracing 140
            return 0.0
        Fe = math.pi ** 2 * E / sl ** 2
        Fcr = 0.658 ** (s.Fy / Fe) * s.Fy if s.Fy / Fe <= 2.25 else 0.877 * Fe
        return 0.9 * Fcr * s.A / 1000

    def phiPn_t(s, L):
        if L * 1000 / min(s.rx, s.ry) > 200:
            return 0.0
        An = 0.85 * s.A  # bolted splice holes; U = 0.9 for H with flanges connected
        return min(0.9 * s.Fy * s.A, 0.75 * FU * 0.9 * An) / 1000

    def phiMn(s, Lb, Cb=1.0):
        """Doubly symmetric compact-flange I, AISC F2/F3 (kNm). Lb in m."""
        Lb = Lb * 1000
        if not s.compact_flange() or s.h / s.tw > 5.70 * math.sqrt(E / s.Fy):
            return 0.0
        Zx = s.bf * s.tf * (s.d - s.tf) + s.tw * s.h ** 2 / 4
        Sx = s.Ix / (s.d / 2)
        Mp = s.Fy * Zx if s.h / s.tw <= 3.76 * math.sqrt(E / s.Fy) else s.Fy * Sx
        ho = s.d - s.tf
        rts = math.sqrt(math.sqrt(s.Iy * (s.Iy * ho ** 2 / 4)) / Sx)
        J = (2 * s.bf * s.tf ** 3 + s.h * s.tw ** 3) / 3
        Lp = 1.76 * s.ry * math.sqrt(E / s.Fy)
        Lr = 1.95 * rts * E / (0.7 * s.Fy) * math.sqrt(J / (Sx * ho) + math.sqrt((J / (Sx * ho)) ** 2 + 6.76 * (0.7 * s.Fy / E) ** 2))
        if Lb <= Lp:
            Mn = Mp
        elif Lb <= Lr:
            Mn = min(Mp, Cb * (Mp - (Mp - 0.7 * s.Fy * Sx) * (Lb - Lp) / (Lr - Lp)))
        else:
            Fcr = Cb * math.pi ** 2 * E / (Lb / rts) ** 2 * math.sqrt(1 + 0.078 * J / (Sx * ho) * (Lb / rts) ** 2)
            Mn = min(Mp, Fcr * Sx)
        return 0.9 * Mn / 1e6

    def phiVn(s, a=None):
        """AISC G2 with transverse stiffener spacing a (kN)."""
        kv = 5.34 if a is None else 5 + 5 / (a / s.h) ** 2
        r = s.h / s.tw
        lim = 1.10 * math.sqrt(kv * E / s.Fy)
        Cv = 1.0 if r <= lim else lim / r
        return 0.9 * 0.6 * s.Fy * s.d * s.tw * Cv / 1000


def search(check, d_rng, bf_rng, ratio=(0.3, 1.05), tw_min=9, tf_min=10, maxkg=1e9):
    best = None
    for d in d_rng:
        for bf in bf_rng:
            if not ratio[0] <= bf / d <= ratio[1]:
                continue
            for tf in [t for t in PLATES if t >= tf_min]:
                for tw in [t for t in PLATES if tw_min <= t <= tf]:
                    s = WB(d, bf, tw, tf)
                    if best and s.kg >= best[0].kg:
                        continue
                    ok, ur = check(s)
                    if ok:
                        best = (s, ur)
    return best


# ---------------------------------------------------------------- loads
g = 9.81
# Scania P410 B8x4 (58 t GVW): axle loads [t] & spacing [m] (front-tandem steer / rear tandem)
SCANIA_AX = [7.0, 7.0, 22.0, 22.0]
SCANIA_SP = [1.95, 3.10, 1.37]
HEADWAY = 10.0  # clear gap between trucks in convoy [m] (mine traffic, jammed)
# SNI 1725-2016 truck T: 50 / 225 / 225 kN @ 5 m, 4-9 m
T_AX = [50.0, 225.0, 225.0]
T_SP = [5.0, 5.0]
GAMMA = dict(MS_steel=1.1, MS_conc=1.3, MA=2.0, TD=1.8, TT=1.8)


def btr_q(L):  # kPa
    return 9.0 if L <= 30 else 9.0 * (0.5 + 15.0 / L)


def dla(L):
    return 0.40 if L <= 50 else 0.40 - 0.0025 * (L - 50) if L <= 90 else 0.30


def truck_train(n, axles, spac, headway):
    """list of (offset, kN) for n trucks in convoy."""
    out, x = [], 0.0
    for _ in range(n):
        for i, w in enumerate(axles):
            out.append((x, w * g if axles is SCANIA_AX else w))
            if i < len(spac):
                x += spac[i]
        x += headway
    return out


def max_moving(il_fn, L, train, step=0.1):
    """max positive & negative effect of moving point train on influence fn."""
    span = train[-1][0]
    best_p, best_n = 0.0, 0.0
    x0 = -span
    while x0 <= L:
        for direction in (1, -1):
            v = 0.0
            for off, P in train:
                x = x0 + off if direction == 1 else x0 + span - off
                if 0 <= x <= L:
                    v += P * il_fn(x)
            best_p, best_n = max(best_p, v), min(best_n, v)
        x0 += step
    return best_p, best_n


def uniform_env(il_fn, L, n=600):
    pos = neg = 0.0
    dx = L / n
    for i in range(n):
        v = il_fn((i + 0.5) * dx) * dx
        if v > 0:
            pos += v
        else:
            neg += v
    return pos, neg


# ================================================================ TRUSS 60 m
def truss():
    L, NP, H, B = 60.0, 12, 6.0, 11.53   # span, panels, height c/c chord, truss spacing
    p = L / NP
    carriage = 10.0                      # 2 x 5.0 m lanes between barriers
    # dead loads per truss [kN/m]
    slab = 0.25 * 11.0 * 24.0
    barr = 2 * 6.0
    steel = 0.0                          # iterated below
    asph = 0.05 * carriage * 22.0
    sw_truss_est = 2 * 38.0              # first estimate kN/m for whole steel (2 trusses + floor)
    q = btr_q(L)
    P_kel = 49.0
    im = dla(L)

    # influence lines (unit load on deck, transferred to bottom nodes)
    def R(x):
        return 1 - x / L

    def M_at(xn):
        return lambda x: (x * (L - xn) / L) if x <= xn else (xn * (L - x) / L)

    def V_panel(i):  # shear in bottom panel i (between node i and i+1), node load interpolation
        a, b = i * p, (i + 1) * p

        def f(x):
            if x <= a:
                return -x / L
            if x >= b:
                return 1 - x / L
            t = (x - a) / p
            return (1 - t) * (-a / L) + t * (1 - b / L)
        return f

    theta = math.atan2(H, p / 2)
    Ld = math.hypot(p / 2, H)

    members = []  # (code, type, IL, factor, length)
    # bottom chord: panel i between bottom nodes i,i+1 ; tension = M at top node above (x=(i+.5)p)/H
    for i in range(NP):
        xm = (i + 0.5) * p
        fm = M_at(xm)
        members.append((f"BC-{i+1:02d}", "Bottom Chord", lambda x, fm=fm: fm(x) / H, p))
    # top chord: between top nodes k,k+1 (x=(k+.5)p..(k+1.5)p) ; compression = M at bottom node (k+1)p / H
    for k in range(NP - 1):
        fm = M_at((k + 1) * p)
        members.append((f"TC-{k+1:02d}", "Top Chord", lambda x, fm=fm: -fm(x) / H, p))
    # diagonals in panel i: two per panel. End diagonals of panel 1 & 12 are End Chord (end post)
    for i in range(NP):
        fv = V_panel(i)
        for j, sgn in enumerate((-1, 1)):  # first rises (compression under +V), second falls (tension)
            code_idx = 2 * i + j + 1
            first_or_last = (i == 0 and j == 0) or (i == NP - 1 and j == 1)
            typ = "End Chord" if first_or_last else "Diagonal Chord"
            s = sgn if i < NP / 2 else sgn  # sign convention via shear
            members.append((f"{'EC' if first_or_last else 'DC'}-{code_idx:02d}", typ,
                            lambda x, fv=fv, s=s: s * fv(x) / math.sin(theta), Ld))

    lane_trains = [truck_train(6, SCANIA_AX, SCANIA_SP, HEADWAY)]
    results = []
    for it in range(3):
        wD_f = (GAMMA["MS_conc"] * (slab + barr) + GAMMA["MS_steel"] * sw_truss_est + GAMMA["MA"] * asph) / 2
        wD_s = (slab + barr + sw_truss_est + asph) / 2
        # live load per truss (lever rule, both lanes loaded symmetric -> half each, eccentric one-lane 0.72)
        wL = GAMMA["TD"] * q * carriage / 2
        PL = GAMMA["TD"] * P_kel * (1 + im) * carriage / 2
        # Scania: 2 lanes of convoys, each truss takes 1 lane x 1.0 (lever rule lane c/l at 2.77 m from truss -> 0.76; both lanes ->1.0)
        results = []
        for code, typ, f, Lm in members:
            dp, dn = uniform_env(f, L)
            D = wD_f * (dp + dn)
            Ds = wD_s * (dp + dn)
            # D-lane
            lp, ln = uniform_env(f, L)
            peak = max(f((i + 0.5) * L / 600) for i in range(600))
            trough = min(f((i + 0.5) * L / 600) for i in range(600))
            DLp, DLn = wL * lp + PL * peak, wL * ln + PL * trough
            # Scania convoy (one lane per truss) with DLA 30 %
            sp, sn = max_moving(f, L, lane_trains[0], step=0.25)
            SCp, SCn = GAMMA["TT"] * 1.3 * sp, GAMMA["TT"] * 1.3 * sn
            Pmax = D + max(DLp, SCp)
            Pmin = D + min(DLn, SCn)
            gov = "SCANIA" if max(abs(SCp), abs(SCn)) > max(abs(DLp), abs(DLn)) else "SNI D"
            results.append(dict(code=code, type=typ, L=Lm, Pt=max(Pmax, 0), Pc=-min(Pmin, 0), gov=gov))
        # update self weight estimate after design
        designs = design_truss(results, p, Ld, B, H)
        truss_kg = sum(d["sec"].kg * d["L"] * d["n_mem"] for d in designs) * 2  # both trusses
        floor_kg = sum(d["sec"].kg * d["L"] * d["n"] for d in floor_system(B, p))
        sw_new = (truss_kg + floor_kg) * 1.20 * g / 1000 / L  # +20 % gusset, splice, bracing   # +15 % gusset/bolt/splice
        if abs(sw_new - sw_truss_est) < 1.0:
            break
        sw_truss_est = sw_new
    return results, designs, dict(L=L, H=H, B=B, p=p, sw=sw_truss_est, q=q, im=im)


def design_truss(results, p, Ld, B, H):
    out = []
    groups = {}
    # group chords into 3 zones each (end / quarter / middle) for fabrication economy
    for r in results:
        groups.setdefault(r["type"], []).append(r)

    def zone(code, n):
        i = int(code.split("-")[1])
        k = min(i, n + 1 - i)
        return k

    def design_member(Pt, Pc, KL, typ):
        dr = [GUSSET_D]  # all truss main members same depth -> fit between gusset plates
        br = range(250, 651, 25)

        def chk(s):
            urs = []
            if Pc > 0:
                pc = s.phiPn_c(KL, KL)
                if pc <= 0:
                    return False, 9
                urs.append(Pc / pc)
            if Pt > 0:
                pt = s.phiPn_t(KL)
                if pt <= 0:
                    return False, 9
                urs.append(Pt / pt)
            ur = max(urs) if urs else 0
            return ur <= 0.95, ur
        return search(chk, dr, br, ratio=(0.5, 1.0), tw_min=12, tf_min=16)

    # Bottom chord: zones by moment level
    for typ, lst in groups.items():
        n = len(lst)
        if typ in ("Bottom Chord", "Top Chord"):
            zones = {}
            for r in lst:
                z = zone(r["code"], n)
                zk = "Z1" if z <= 2 else "Z2" if z <= 4 else "Z3"
                zones.setdefault(zk, []).append(r)
        else:
            zones = {}
            for r in lst:
                if typ == "End Chord":
                    zones.setdefault("E", []).append(r)
                else:
                    i = int(r["code"].split("-")[1])
                    k = min(i, 25 - i)
                    zk = "Z1" if k <= 6 else "Z2" if k <= 10 else "Z3"
                    zones.setdefault(zk, []).append(r)
        for zk, rs in sorted(zones.items()):
            Pt = max(r["Pt"] for r in rs)
            Pc = max(r["Pc"] for r in rs)
            KL = rs[0]["L"]
            best = design_member(Pt, Pc, KL, typ)
            sec, ur = best
            prefix = rs[0]["code"].split("-")[0]
            out.append(dict(n_mem=len(rs), frame=f"{prefix}-{zk}", type=typ, members=", ".join(r["code"] for r in rs),
                            L=KL, Pu_t=Pt, Pu_c=Pc, sec=sec, ur=ur, gov=rs[0]["gov"]))
    return out


# -------------------------------------------------- floor system (truss bridge)
def floor_system(B=11.53, p=5.0, n_str=7):
    s_str = B / (n_str + 1) if False else 10.0 / (n_str - 1)  # stringers across 10 m carriageway
    rows = []
    wheel_sc = max(SCANIA_AX) * g / 2  # kN per wheel (dual)
    # ---- Stringer: simple span p between cross girders, spacing s_str
    wD = 1.3 * (0.25 * s_str * 24) + 2.0 * (0.05 * s_str * 22) + 1.1 * 1.5
    # tandem 22 t @1.37 on 5 m span; wheel line share by lever rule ~ 1.0 wheel line per stringer
    P = 1.8 * 1.3 * wheel_sc
    a = SCANIA_SP[2]
    x = p / 2 - a / 4
    M_tandem = P * (x * (p - x) / p + (x) * (p - x - a) / p) if False else P * ((p / 2 + a / 4) * (p / 2 - a / 4) / p) * 2 - P * a / 2 * (p / 2 - a / 4) / p * 2 + 0
    # exact: two loads P at x and x+a; M under first load
    xa = p / 2 - a / 4
    Rb = P * (xa + xa + a) / p
    Ra = 2 * P - Rb
    M_tandem = Ra * xa
    # SNI truck T wheel 112.5 kN
    Mt = 1.8 * 1.3 * 112.5 * p / 4
    Mu = wD * p ** 2 / 8 + max(M_tandem, Mt)
    Vu = wD * p / 2 + P * (1 + (p - a) / p)

    def chk_str(s):
        m = s.phiMn(p, 1.14)
        if m <= 0:
            return False, 9
        ur = max(Mu / m, Vu / s.phiVn())
        return ur <= 0.95, ur
    sec, ur = search(chk_str, range(300, 701, 50), range(150, 351, 25), ratio=(0.3, 0.75), tw_min=9, tf_min=12)
    rows.append(dict(frame="ST-1", type="Stringer", members=f"{n_str} lines x 12 panels @ {s_str:.2f} m",
                     L=p, Mu=Mu, Vu=Vu, sec=sec, ur=ur, n=n_str * 12))
    # ---- Cross girder: span B, loads from stringers at s_str; axle reactions of tandem 2 lanes
    Lc = B
    Rdl = wD * p  # per stringer (already factored)
    # axle group max reaction on floor beam: tandem 22+22 t on 5 m panels
    Rax = 1.8 * 1.3 * max(SCANIA_AX) * g * (1 + (p - a) / p)  # per axle-line, both wheels
    # two trucks side by side, wheels at 1.8 m gauge, lanes 5 m
    xs = [2.77 - 0.9 + 0.765, 2.77 + 0.9 + 0.765]
    xs = [0.765 + 1.6, 0.765 + 3.4, 0.765 + 1.6 + 5.0, 0.765 + 3.4 + 5.0]
    Mll = max(sum(Rax / 2 * (xi * (Lc - xm) / Lc if xi <= xm else xm * (Lc - xi) / Lc) for xi in xs) for xm in [k * 0.05 for k in range(1, int(Lc / 0.05))])
    Mdl = Rdl * n_str * Lc / 8 + 1.1 * 3.0 * Lc ** 2 / 8
    Mu2 = Mdl + Mll
    Vu2 = Rdl * n_str / 2 + 1.1 * 3.0 * Lc / 2 + Rax / 2 * sum((Lc - xi) / Lc for xi in xs)

    def chk_cg(s):
        m = s.phiMn(s_str * 2, 1.0)  # top flange braced by stringers / deck
        if m <= 0:
            return False, 9
        ur = max(Mu2 / m, Vu2 / s.phiVn(1500))
        return ur <= 0.95, ur
    sec, ur = search(chk_cg, range(700, 1401, 50), range(250, 501, 25), ratio=(0.2, 0.6), tw_min=10, tf_min=14)
    rows.append(dict(frame="CG-1", type="Cross Girder", members="13 lines @ bottom nodes", L=Lc, Mu=Mu2, Vu=Vu2, sec=sec, ur=ur, n=13))
    return rows


def bracing(L=60.0, p=5.0, B=11.53, H=6.0, Pc_top=0):
    rows = []
    # Brace (top lateral strut / sway strut) : 2 % of top chord force (stability) + wind
    Pu_w = 1.4 * 0.0012 * 35 ** 2 * 2.0 * H * p  # EW  (VB 35 m/s, Cw 2.0) nodal
    Pbr = max(0.02 * Pc_top, Pu_w) + 1.1 * 0  # kN
    Lb = B

    def chk(s, P, KL):
        pc = s.phiPn_c(KL, KL, lim=140)
        pt = s.phiPn_t(KL)
        if pc <= 0 or pt <= 0:
            return False, 9
        ur = max(P / pc, P / pt, 0.0)
        # self-weight bending check light
        return ur <= 0.95, ur
    sec, ur = search(lambda s: chk(s, Pbr, Lb), range(200, 451, 50), range(200, 451, 25), ratio=(0.6, 1.3), tw_min=8, tf_min=9)
    rows.append(dict(frame="BR-1", type="Brace (top lateral strut / portal)", members="11 struts at top nodes + 2 portals", L=Lb, Pu=Pbr, sec=sec, ur=ur))
    # Diagonal member (top & bottom lateral X-bracing): tension/compression under wind/sway, KL = 0.5 L (X-brace)
    Ld = math.hypot(B, p)
    Pdm = max(Pu_w, 0.02 * Pc_top) / math.cos(math.atan2(p, B)) * 1.0
    sec, ur = search(lambda s: chk(s, Pdm, 0.5 * Ld), range(150, 351, 50), range(150, 351, 25), ratio=(0.6, 1.3), tw_min=8, tf_min=9)
    rows.append(dict(frame="DM-1", type="Diagonal Member (lateral X-bracing)", members="top & bottom lateral bracing", L=Ld, Pu=Pdm, sec=sec, ur=ur))
    return rows


# ================================================================ GIRDER 30.6 m
def girder():
    L, S, ts, n_g = 30.6, 1.7, 250.0, 6
    carriage = 10.0 if False else 7.0 + 2 * 1.5
    # per interior girder [kN/m]
    w_slab = ts / 1000 * S * 24 + 0.05 * 0.4 * 24   # + haunch
    w_sdl = 0.05 * S * 22 + 2 * 6.0 / n_g
    q = btr_q(L)
    im = dla(L)
    # live: tributary lane-load, lever rule
    wLL = 1.8 * q * S
    PLL = 1.8 * 49 * (1 + im) * S
    # Scania convoy: distribution factor (AASHTO 4.6.2.2.2b, 2+ lanes, interior)
    DF = 0.075 + (S * 1000 / 2900) ** 0.6 * (S / L) ** 0.2 * 1.0
    train = truck_train(4, SCANIA_AX, SCANIA_SP, HEADWAY)
    Mm = lambda xm: (lambda x: x * (L - xm) / L if x <= xm else xm * (L - x) / L)
    Msc = max(max_moving(Mm(xm), L, train, 0.1)[0] for xm in [L / 2 - 1.5 + 0.25 * k for k in range(13)])
    Vsc = max_moving(lambda x: 1 - x / L, L, train, 0.05)[0]
    M_sc = 1.8 * 1.3 * DF * Msc
    V_sc = 1.8 * 1.3 * max(DF, 0.6) * Vsc
    M_D = wLL * L ** 2 / 8 + PLL * L / 4
    V_D = wLL * L / 2 + PLL
    w_st = 5.0  # steel self weight estimate kN/m
    MuDC = (1.3 * w_slab + 1.1 * w_st) * L ** 2 / 8 + 2.0 * w_sdl * L ** 2 / 8
    VuDC = (1.3 * w_slab + 1.1 * w_st + 2.0 * w_sdl) * L / 2
    Mu = MuDC + max(M_D, M_sc)
    Vu = VuDC + max(V_D, V_sc)
    gov = "SCANIA" if M_sc > M_D else "SNI D"
    # construction stage (wet concrete + 1.5 kPa construction load), top flange Lb = cross-frame spacing
    Lb_c = L / 6
    Mc = (1.4 * (w_slab + w_st) + 1.5 * 1.5 * S) * L ** 2 / 8
    # service LL deflection limit L/800 (Scania, no factors, DF, IM)
    Pser_M = 1.3 * DF * Msc
    fc, n_mod = 30.0, 8.0
    beff = S * 1000

    def comp_props(s):
        # composite section: slab transformed (n) sits on top of girder (haunch 50)
        As = beff * ts / n_mod
        ys = s.d + 50 + ts / 2
        A = s.A + As
        yb = (s.A * s.yb + As * ys) / A
        I = s.Ix + s.A * (yb - s.yb) ** 2 + beff * ts ** 3 / 12 / n_mod + As * (ys - yb) ** 2
        return A, yb, I

    def Mp_comp(s):
        # plastic neutral axis, slab 0.85fc'
        Ps = 0.85 * fc * beff * ts
        Pt_ = s.bfb * s.tfb * s.Fy
        Pw = s.h * s.tw * s.Fy
        Pc_ = s.bf * s.tf * s.Fy
        Dt = s.d + 50 + ts
        if Pt_ + Pw + Pc_ <= Ps:  # PNA in slab
            a = (Pt_ + Pw + Pc_) / (0.85 * fc * beff)
            Mp = (Pt_ * (Dt - s.tfb / 2) + Pw * (Dt - s.tfb - s.h / 2) + Pc_ * (Dt - s.d + s.tf / 2) - (Pt_ + Pw + Pc_) * a / 2)
            Dp = a
        else:
            # PNA in steel (top flange or web) - conservative: use steel Fy*Zx + slab couple
            Mp = Ps * (s.d + 50 + ts / 2 - s.d / 2) + s.Fy * (s.bf * s.tf * (s.d - s.tf) + s.tw * s.h ** 2 / 4) * 0.5
            Dp = ts + 50 + s.tf
        Mn = Mp if Dp <= 0.1 * Dt else Mp * (1.07 - 0.7 * Dp / Dt)
        return 0.9 * Mn / 1e6, Dp / Dt

    def chk(s):
        if s.h / s.tw > 150 or (s.bf / 2) / s.tf > 12 or (s.bfb / 2) / s.tfb > 12:
            return False, 9
        pm, dpr = Mp_comp(s)
        if dpr > 0.42:
            return False, 9
        vr = Vu / s.phiVn(1500)
        # construction: top flange LTB (singly symmetric -> use top flange as T-section column, AISC F4 approx.)
        Iyc = s.tf * s.bf ** 3 / 12
        rt = s.bf / math.sqrt(12 * (1 + s.h * s.tw / 6 / (s.bf * s.tf)))
        Fcr = min(s.Fy, 1.0 * math.pi ** 2 * E / (Lb_c * 1000 / rt) ** 2) if Lb_c * 1000 / rt > 1.1 * rt * 0 + math.pi * math.sqrt(E / (0.7 * s.Fy)) else s.Fy
        Sxc = s.Ix / (s.d - s.yb)
        mc = 0.9 * Fcr * Sxc / 1e6
        # deflection
        A, yb, I = comp_props(s)
        w_eq = 8 * Pser_M * 1e6 / (L * 1000) ** 2  # N/mm equivalent uniform
        defl = 5 * w_eq * (L * 1000) ** 4 / (384 * E * I)
        dr = defl / (L * 1000 / 800)
        ur = max(Mu / pm, vr, Mc / mc, dr)
        return ur <= 0.95, ur

    best = None
    for d in range(1300, 1701, 50):
        for bf in range(300, 551, 25):
            for bfb in range(bf, 751, 25):
                for tf in [t for t in PLATES if 16 <= t <= 40]:
                    for tfb in [t for t in PLATES if tf <= t <= 50]:
                        for tw in [t for t in PLATES if 12 <= t <= 20]:
                            s = WB(d, bf, tw, tf, bfb, tfb)
                            if best and s.kg >= best[0].kg:
                                continue
                            ok, ur = chk(s)
                            if ok:
                                best = (s, ur)
    sec, ur = best
    rows = [dict(frame="GR-1", type="Main Girder (composite, interior & exterior)", members=f"G1..G{n_g} @ {S} m",
                 L=L, Mu=Mu, Vu=Vu, sec=sec, ur=ur, gov=gov, DF=DF)]
    # cross frame / diaphragm
    Ld = S

    def chk_d(s):
        m = s.phiMn(Ld)
        return (m > 0 and 150 / m <= 0.95), (150 / m if m else 9)
    sd, urd = search(chk_d, range(600, 1001, 50), range(200, 301, 25), ratio=(0.2, 0.5), tw_min=9, tf_min=12)
    rows.append(dict(frame="DF-1", type="Diaphragm / Cross Beam", members="7 lines x 5 bays (@~5.1 m)", L=Ld, Mu=150, Vu=0, sec=sd, ur=urd))
    # bottom lateral brace for erection / wind
    rows.append(dict(frame="LB-1", type="Lateral Bracing (erection)", members="bottom flange X", L=math.hypot(S, 5.1),
                     Mu=0, Vu=0, sec=WB(200, 200, 8, 12), ur=0.3))
    return rows, dict(L=L, S=S, q=q, im=im, DF=DF, Mu=Mu, Vu=Vu, M_D=M_D, M_sc=M_sc, Mc=Mc)


# ================================================================ REPORT
def main():
    os.makedirs("output", exist_ok=True)
    res, des, info = truss()
    Pc_top = max(r["Pc"] for r in res if r["type"] == "Top Chord")
    fl = floor_system(B=info["B"], p=info["p"])
    br = bracing(Pc_top=Pc_top, B=info["B"], H=info["H"], p=info["p"])
    gr, ginfo = girder()

    lines = ["# Output Desain Profil WB – SM490YB\n",
             "## A. Jembatan Rangka Baja STA 0+750 (L = 60 m)\n",
             f"Geometri: Warren 12 panel @ {info['p']:.1f} m, tinggi c/c {info['H']} m, jarak rangka {info['B']} m. "
             f"BTR q = {info['q']:.2f} kPa, FBD = {info['im']:.3f}, berat baja iterasi = {info['sw']:.1f} kN/m (2 rangka + lantai).\n",
             "| Frame Code | Elemen | Batang | L (m) | Pu tarik (kN) | Pu tekan (kN) | Profil | Fy (MPa) | kg/m | UR | Gov |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    rows_csv = []
    for d in des:
        s = d["sec"]
        lines.append(f"| {d['frame']} | {d['type']} | {d['members']} | {d['L']:.2f} | {d['Pu_t']:.0f} | {d['Pu_c']:.0f} | {s.name} | {s.Fy:.0f} | {s.kg:.1f} | {d['ur']:.2f} | {d['gov']} |")
        rows_csv.append(["Truss 60m", d["frame"], d["type"], d["members"], s.name, s.d, s.bf, s.tw, s.tf, s.bfb, s.tfb, round(s.kg, 1), round(d["ur"], 2)])
    lines += ["", "| Frame Code | Elemen | Keterangan | L (m) | Mu / Pu | Vu (kN) | Profil | kg/m | UR |", "|---|---|---|---|---|---|---|---|---|"]
    for d in fl + br:
        s = d["sec"]
        mu = f"{d['Mu']:.0f} kNm" if "Mu" in d else f"{d['Pu']:.0f} kN"
        vu = f"{d['Vu']:.0f}" if "Vu" in d else "-"
        lines.append(f"| {d['frame']} | {d['type']} | {d['members']} | {d['L']:.2f} | {mu} | {vu} | {s.name} | {s.kg:.1f} | {d['ur']:.2f} |")
        rows_csv.append(["Truss 60m", d["frame"], d["type"], d["members"], s.name, s.d, s.bf, s.tw, s.tf, s.bfb, s.tfb, round(s.kg, 1), round(d["ur"], 2)])
    lines += ["", "## B. Jembatan Fly Over Girder Komposit STA 0+050 (L = 30.6 m)\n",
              f"6 girder @ 1.7 m, slab 250 mm fc' 30 MPa. DF Scania = {ginfo['DF']:.3f}. "
              f"Mu (SNI D) = {ginfo['M_D']:.0f} kNm, Mu LL Scania = {ginfo['M_sc']:.0f} kNm, Mu total = {ginfo['Mu']:.0f} kNm, "
              f"Vu = {ginfo['Vu']:.0f} kN, M konstruksi = {ginfo['Mc']:.0f} kNm.\n",
              "| Frame Code | Elemen | Keterangan | L (m) | Mu (kNm) | Vu (kN) | Profil | kg/m | UR |", "|---|---|---|---|---|---|---|---|---|"]
    for d in gr:
        s = d["sec"]
        lines.append(f"| {d['frame']} | {d['type']} | {d['members']} | {d['L']:.2f} | {d['Mu']:.0f} | {d['Vu']:.0f} | {s.name} | {s.kg:.1f} | {d['ur']:.2f} |")
        rows_csv.append(["Girder 30.6m", d["frame"], d["type"], d["members"], s.name, s.d, s.bf, s.tw, s.tf, s.bfb, s.tfb, round(s.kg, 1), round(d["ur"], 2)])
    lines += ["", "Notasi WB d x bf x tw x tf (mm); girder: WB d x bf_atas/bf_bawah x tw x tf_atas/tf_bawah.",
              f"Tebal pelat hanya dari stok pasar Indonesia: {PLATES} mm."]
    txt = "\n".join(lines)
    print(txt)
    open("output/hasil_desain.md", "w").write(txt + "\n")
    with open("output/frame_section.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Bridge", "FrameCode", "Element", "Members", "Section", "d", "bf_top", "tw", "tf_top", "bf_bot", "tf_bot", "kg_per_m", "UR"])
        w.writerows(rows_csv)


if __name__ == "__main__":
    main()

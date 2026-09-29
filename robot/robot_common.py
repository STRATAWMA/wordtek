"""
Helper Robot Structural Analysis API (RobotOM, COM) - jalankan di Windows + Robot terinstal.
    pip install comtypes
Satuan API: SI (m, N, Pa).
"""
import math
from comtypes.client import CreateObject

app = CreateObject("Robot.Application")
from comtypes.gen import RobotOM as R  # noqa: E402  (dibuat otomatis oleh comtypes)


def K(name):
    """Ambil konstanta enum RobotOM; bila nama beda versi, tampilkan kandidat."""
    try:
        return getattr(R, name)
    except AttributeError:
        pre = name.rsplit("_", 1)[0]
        raise AttributeError(f"{name} tidak ada. Kandidat: {[n for n in dir(R) if n.startswith(pre)]}")


def new_project():
    app.Visible = True
    app.Interactive = True
    app.Project.New(K("I_PT_FRAME_3D"))
    s = app.Project.Structure
    return s


def material(s, name="SM490YB", fy=355e6, fu=490e6):
    lab = s.Labels.Create(K("I_LT_MATERIAL"), name)
    m = lab.Data
    m.Type = K("I_MT_STEEL")
    m.E, m.NU, m.RO, m.LX = 2.0e11, 0.3, 77010.0, 1.2e-5
    m.Kirchoff = 2.0e11 / 2.6
    m.RE, m.RT = fy, fu
    s.Labels.Store(lab)


def wb_section(s, name, d, bf, tw, tf, bfb=None, tfb=None, mat="SM490YB"):
    """Profil WB custom (mm). Simetris -> USER_I_BISYM, asimetris -> USER_I_MONOSYM."""
    lab = s.Labels.Create(K("I_LT_BAR_SECTION"), name)
    sec = lab.Data
    sec.MaterialName = mat
    if bfb is None or (bfb == bf and tfb == tf):
        sec.ShapeType = K("I_BSST_USER_I_BISYM")
        ns = sec.CreateNonstd(0)
        ns.SetValue(K("I_BSNDV_BISYM_H"), d / 1000)
        ns.SetValue(K("I_BSNDV_BISYM_B"), bf / 1000)
        ns.SetValue(K("I_BSNDV_BISYM_TW"), tw / 1000)
        ns.SetValue(K("I_BSNDV_BISYM_TF"), tf / 1000)
    else:
        sec.ShapeType = K("I_BSST_USER_I_MONOSYM")
        ns = sec.CreateNonstd(0)
        ns.SetValue(K("I_BSNDV_MONOSYM_H"), d / 1000)
        ns.SetValue(K("I_BSNDV_MONOSYM_B1"), bf / 1000)
        ns.SetValue(K("I_BSNDV_MONOSYM_B2"), bfb / 1000)
        ns.SetValue(K("I_BSNDV_MONOSYM_TW"), tw / 1000)
        ns.SetValue(K("I_BSNDV_MONOSYM_TF1"), tf / 1000)
        ns.SetValue(K("I_BSNDV_MONOSYM_TF2"), tfb / 1000)
    sec.CalcNonstdGeometry()
    s.Labels.Store(lab)


def support(s, name, ux, uy, uz, rx=0, ry=0, rz=0):
    lab = s.Labels.Create(K("I_LT_SUPPORT"), name)
    d = lab.Data
    d.UX, d.UY, d.UZ, d.RX, d.RY, d.RZ = ux, uy, uz, rx, ry, rz
    s.Labels.Store(lab)


def pinned_release(s, name="SENDI"):
    lab = s.Labels.Create(K("I_LT_BAR_RELEASE"), name)
    d = lab.Data
    free = K("I_BNRV_FREE")
    d.StartNode.RY = free; d.StartNode.RZ = free
    d.EndNode.RY = free; d.EndNode.RZ = free
    s.Labels.Store(lab)


class Model:
    def __init__(s, st):
        s.st, s.n, s.b, s.nodes = st, 0, 0, {}
        s.groups = {}

    def node(s, x, y, z):
        key = (round(x, 4), round(y, 4), round(z, 4))
        if key not in s.nodes:
            s.n += 1
            s.st.Nodes.Create(s.n, *key)
            s.nodes[key] = s.n
        return s.nodes[key]

    def bar(s, n1, n2, section, group, release=None, gamma=0.0):
        s.b += 1
        s.st.Bars.Create(s.b, n1, n2)
        bar = s.st.Bars.Get(s.b)
        bar.SetLabel(K("I_LT_BAR_SECTION"), section)
        if release:
            bar.SetLabel(K("I_LT_BAR_RELEASE"), release)
        if gamma:
            bar.Gamma = gamma
        s.groups.setdefault(group, []).append(s.b)
        return s.b


def ids(lst):
    return " ".join(str(i) for i in lst)


def case(st, no, name, nature="I_CN_PERMANENT"):
    return st.Cases.CreateSimple(no, name, K(nature), K("I_CAT_STATIC_LINEAR"))


def rec(c, rtype):
    return c.Records.Get(c.Records.New(K(rtype)))


def self_weight(c, factor=1.0):
    r = rec(c, "I_LRT_DEAD")
    r.SetValue(K("I_DRV_Z"), -1.0)
    r.SetValue(K("I_DRV_COEFF"), factor)
    r.SetValue(K("I_DRV_ENTIRE_STRUCTURE"), 1)


def bar_udl(c, bars, pz=0.0, px=0.0, py=0.0):
    r = rec(c, "I_LRT_BAR_UNIFORM")
    r.SetValue(K("I_BURV_PZ"), pz); r.SetValue(K("I_BURV_PX"), px); r.SetValue(K("I_BURV_PY"), py)
    r.Objects.FromText(ids(bars))


def bar_point(c, bar, xrel, fz):
    r = rec(c, "I_LRT_BAR_FORCE_CONCENTRATED")
    r.SetValue(K("I_BFCRV_FZ"), fz)
    r.SetValue(K("I_BFCRV_X"), xrel)
    r.SetValue(K("I_BFCRV_REL"), 1)
    r.Objects.FromText(str(bar))


def node_force(c, nodes, fx=0.0, fy=0.0, fz=0.0):
    r = rec(c, "I_LRT_NODE_FORCE")
    r.SetValue(K("I_NFRV_FX"), fx); r.SetValue(K("I_NFRV_FY"), fy); r.SetValue(K("I_NFRV_FZ"), fz)
    r.Objects.FromText(ids(nodes))


def combo(st, no, name, factors, uls=True):
    c = st.Cases.CreateCombination(no, name, K("I_CBT_ULS" if uls else "I_CBT_SLS"), K("I_CN_PERMANENT"), K("I_CAT_COMB"))
    for case_no, f in factors:
        c.CaseFactors.New(case_no, f)
    return c


def bar_groups(st, groups):
    """Simpan grup batang sebagai Group Robot (nama = kode frame)."""
    for name, lst in groups.items():
        st.Groups.Create(K("I_OT_BAR"), name, ids(lst))


def lever(y, lines):
    """Distribusi beban titik di koordinat y ke dua stringer terdekat (lever rule)."""
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        if a - 1e-9 <= y <= b + 1e-9:
            t = (y - a) / (b - a)
            return [(i, 1 - t), (i + 1, t)]
    return [(0 if y < lines[0] else len(lines) - 1, 1.0)]


def calc_and_save(path):
    app.Project.CalcEngine.Calculate()
    app.Project.SaveAs(path)
    print("Tersimpan:", path)

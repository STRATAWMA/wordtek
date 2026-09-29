"""Gambar kode frame & profil WB -> output/Gambar_Frame_Code.pdf (butuh matplotlib)."""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

SEC = {r["FrameCode"]: r for r in csv.DictReader(open("output/frame_section.csv"))}
COL = {"BC-Z1": "#1f77b4", "BC-Z2": "#2a9df4", "BC-Z3": "#0b3d91",
       "TC-Z1": "#d62728", "TC-Z2": "#ff7f0e", "TC-Z3": "#8c1515",
       "EC-E": "#6a3d9a", "DC-Z1": "#2ca02c", "DC-Z2": "#8fd175", "DC-Z3": "#bcbd22",
       "ST-1": "#7f7f7f", "CG-1": "#17becf", "BR-1": "#e377c2", "DM-1": "#8c564b",
       "GR-1": "#1f77b4", "DF-1": "#17becf", "LB-1": "#8c564b"}
L, NP, H, B = 60.0, 12, 6.0, 11.53
p = L / NP


def group_of(code):
    for k, r in SEC.items():
        if code in [m.strip() for m in r["Members"].split(",")]:
            return k
    return None


def title_block(fig, title, no):
    fig.text(0.02, 0.965, title, fontsize=13, weight="bold")
    fig.text(0.02, 0.94, "Proyek FEED Road-4 PT Sumber Daya Arindo  |  Mutu baja SM490YB  |  Profil WB custom (pelat stok Indonesia)", fontsize=8)
    fig.text(0.98, 0.015, f"Lembar {no}  |  PRE-DESIGN - verifikasi dengan model 3D sebelum IFC", fontsize=7, ha="right")


def legend(ax, codes):
    y = 0.98
    for c in codes:
        r = SEC[c]
        ax.plot([0, 0.06], [y, y], color=COL[c], lw=4, transform=ax.transAxes)
        ax.text(0.08, y, f"{c}  {r['Section']}  ({r['kg_per_m']} kg/m, UR {r['UR']})", fontsize=7, va="center", transform=ax.transAxes)
        y -= 0.075
    ax.axis("off")


def truss_elev(pdf):
    fig = plt.figure(figsize=(16.5, 11.7))
    title_block(fig, "GAMBAR 1 - TAMPAK SAMPING RANGKA BAJA L = 60 m (STA 0+750) - KODE FRAME", 1)
    ax = fig.add_axes([0.03, 0.30, 0.94, 0.58])
    for i in range(NP):  # bottom chord
        c = f"BC-{i+1:02d}"; g = group_of(c)
        ax.plot([i * p, (i + 1) * p], [0, 0], color=COL[g], lw=5)
        ax.text((i + .5) * p, -0.45, c, ha="center", fontsize=7)
    for k in range(1, NP):  # top chord
        c = f"TC-{k:02d}"; g = group_of(c)
        ax.plot([(k - .5) * p, (k + .5) * p], [H, H], color=COL[g], lw=5)
        ax.text(k * p, H + 0.3, c, ha="center", fontsize=7)
    for i in range(NP):
        for j in (0, 1):
            n = 2 * i + j + 1
            c = f"EC-{n:02d}" if n in (1, 24) else f"DC-{n:02d}"
            g = group_of(c)
            x0, x1 = (i * p, (i + .5) * p) if j == 0 else ((i + .5) * p, (i + 1) * p)
            y0, y1 = (0, H) if j == 0 else (H, 0)
            ax.plot([x0, x1], [y0, y1], color=COL[g], lw=3.5)
            ax.text((x0 + x1) / 2 + 0.15, H / 2 + (0.6 if j else -0.6), c, fontsize=6.5, rotation=68 if j == 0 else -68, ha="center")
    for i in range(NP + 1):
        ax.plot(i * p, 0, "ko", ms=4)
        ax.text(i * p, -1.0, f"CG-1\nN{i}", ha="center", fontsize=6, color=COL["CG-1"])
    ax.plot([0], [-0.2], marker="^", ms=14, color="k"); ax.plot([L], [-0.2], marker="o", ms=12, mfc="w", color="k")
    ax.annotate("", (0, -2.2), (L, -2.2), arrowprops=dict(arrowstyle="<->"))
    ax.text(L / 2, -2.0, "60000 (12 panel @ 5000)", ha="center", fontsize=8)
    ax.annotate("", (-1.2, 0), (-1.2, H), arrowprops=dict(arrowstyle="<->")); ax.text(-1.6, H / 2, "6000", rotation=90, va="center", fontsize=8)
    ax.set_xlim(-2.5, L + 1.5); ax.set_ylim(-2.8, H + 1.2); ax.set_aspect("equal"); ax.axis("off")
    legend(fig.add_axes([0.05, 0.03, 0.45, 0.25]), ["BC-Z1", "BC-Z2", "BC-Z3", "TC-Z1", "TC-Z2", "TC-Z3"])
    legend(fig.add_axes([0.52, 0.03, 0.45, 0.25]), ["EC-E", "DC-Z1", "DC-Z2", "DC-Z3", "CG-1"])
    pdf.savefig(fig); plt.close(fig)


def truss_plan(pdf):
    fig = plt.figure(figsize=(16.5, 11.7))
    title_block(fig, "GAMBAR 2 - DENAH IKATAN ANGIN ATAS & SISTEM LANTAI (BAWAH) - KODE FRAME", 2)
    # top plan
    ax = fig.add_axes([0.03, 0.56, 0.94, 0.33]); ax.set_title("Denah Ikatan Angin Atas (Top Lateral)", fontsize=10)
    xs = [(k + .5) * p for k in range(NP)]
    for y in (0, B):
        ax.plot([xs[0], xs[-1]], [y, y], color=COL["TC-Z3"], lw=4)
    for x in xs:
        ax.plot([x, x], [0, B], color=COL["BR-1"], lw=3); ax.text(x, B / 2, "BR-1", rotation=90, fontsize=6.5, ha="right")
    for a, b in zip(xs[:-1], xs[1:]):
        ax.plot([a, b], [0, B], color=COL["DM-1"], lw=1.8); ax.plot([a, b], [B, 0], color=COL["DM-1"], lw=1.8)
        ax.text((a + b) / 2, B * 0.62, "DM-1", fontsize=6, ha="center")
    for x in (0, L):
        ax.plot([x, xs[0] if x == 0 else xs[-1]], [0, 0], color=COL["EC-E"], lw=4); ax.plot([x, xs[0] if x == 0 else xs[-1]], [B, B], color=COL["EC-E"], lw=4)
    ax.text(1.2, B / 2, "Portal\nBR-1", fontsize=7, color=COL["BR-1"])
    ax.set_xlim(-1, L + 1); ax.set_ylim(-1, B + 1); ax.set_aspect("equal"); ax.axis("off")
    # bottom plan
    ax = fig.add_axes([0.03, 0.20, 0.94, 0.33]); ax.set_title("Denah Sistem Lantai & Ikatan Angin Bawah (Bottom Lateral)", fontsize=10)
    for y in (0, B):
        ax.plot([0, L], [y, y], color=COL["BC-Z3"], lw=4)
    for i in range(NP + 1):
        ax.plot([i * p] * 2, [0, B], color=COL["CG-1"], lw=4); ax.text(i * p + 0.1, B + 0.3, "CG-1", fontsize=6.5, color=COL["CG-1"])
    ys = [B / 2 - 5 + k * 10 / 6 for k in range(7)]
    for y in ys:
        ax.plot([0, L], [y, y], color=COL["ST-1"], lw=1.3, ls="-")
    ax.text(L / 2 + 0.3, ys[3] + 0.2, "ST-1 (7 baris @ 1667)", fontsize=7)
    for i in range(NP):
        ax.plot([i * p, (i + 1) * p], [0, B], color=COL["DM-1"], lw=1, ls="--"); ax.plot([i * p, (i + 1) * p], [B, 0], color=COL["DM-1"], lw=1, ls="--")
    ax.text(p / 2, 0.8, "DM-1 (X)", fontsize=6.5, ha="center")
    ax.annotate("", (-0.6, 0), (-0.6, B), arrowprops=dict(arrowstyle="<->")); ax.text(-0.9, B / 2, "11530", rotation=90, va="center", fontsize=8)
    ax.set_xlim(-1.5, L + 1); ax.set_ylim(-1, B + 1); ax.set_aspect("equal"); ax.axis("off")
    legend(fig.add_axes([0.05, 0.02, 0.6, 0.16]), ["BR-1", "DM-1", "CG-1", "ST-1"])
    pdf.savefig(fig); plt.close(fig)


def truss_section(pdf):
    fig = plt.figure(figsize=(16.5, 11.7))
    title_block(fig, "GAMBAR 3 - POTONGAN MELINTANG RANGKA (PORTAL / TENGAH BENTANG) - KODE FRAME", 3)
    ax = fig.add_axes([0.1, 0.12, 0.8, 0.75])
    ax.plot([0, 0], [0, H], color=COL["EC-E"], lw=6); ax.plot([B, B], [0, H], color=COL["EC-E"], lw=6)
    ax.text(-0.3, H / 2, "EC-E / DC\n(bidang rangka)", ha="right", fontsize=9)
    ax.plot([0, B], [H, H], color=COL["BR-1"], lw=5); ax.text(B / 2, H + 0.2, "BR-1 (strut atas / portal)", ha="center", fontsize=9)
    for s in (1, -1):
        x0 = 0 if s == 1 else B
        ax.plot([x0, x0 + s * 1.5], [H - 1.5, H], color=COL["BR-1"], lw=3)
    ax.plot([0, B], [-0.7, -0.7], color=COL["CG-1"], lw=8); ax.text(B / 2, -1.25, "CG-1  WB 1350x350x10x22", ha="center", fontsize=9)
    for k in range(7):
        x = B / 2 - 5 + k * 10 / 6
        ax.add_patch(Rectangle((x - 0.11, -0.7), 0.22, 0.55, color=COL["ST-1"]))
    ax.text(B / 2 + 0.2, -0.05, "ST-1  WB 550x225x9x14 (7 baris)", fontsize=9)
    ax.add_patch(Rectangle((0.3, -0.15), B - 0.6, 0.25, fc="#cccccc", ec="k")); ax.text(0.5, 0.25, "Slab t=250, fc' 30", fontsize=8)
    ax.plot([-0.25, 0.25], [0, 0], color=COL["BC-Z3"], lw=10); ax.plot([B - 0.25, B + 0.25], [0, 0], color=COL["BC-Z3"], lw=10)
    ax.plot([-0.25, 0.25], [H, H], color=COL["TC-Z3"], lw=10); ax.plot([B - 0.25, B + 0.25], [H, H], color=COL["TC-Z3"], lw=10)
    ax.text(B + 0.4, 0, "BC-Z1/Z2/Z3", fontsize=9, va="center"); ax.text(B + 0.4, H, "TC-Z1/Z2/Z3", fontsize=9, va="center")
    ax.annotate("", (0, -2), (B, -2), arrowprops=dict(arrowstyle="<->")); ax.text(B / 2, -1.85, "11530", ha="center")
    ax.annotate("", (-1.8, 0), (-1.8, H), arrowprops=dict(arrowstyle="<->")); ax.text(-2.1, H / 2, "6000", rotation=90, va="center")
    ax.set_xlim(-4, B + 3); ax.set_ylim(-2.5, H + 1); ax.set_aspect("equal"); ax.axis("off")
    pdf.savefig(fig); plt.close(fig)


def girder(pdf):
    fig = plt.figure(figsize=(16.5, 11.7))
    title_block(fig, "GAMBAR 4 - FLY OVER GIRDER KOMPOSIT L = 30.6 m (STA 0+050) - KODE FRAME", 4)
    Lg, S, n = 30.6, 1.7, 6
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.38]); ax.set_title("Denah Girder, Diafragma & Ikatan Angin Bawah", fontsize=10)
    ys = [k * S for k in range(n)]
    for k, y in enumerate(ys):
        ax.plot([0, Lg], [y, y], color=COL["GR-1"], lw=4); ax.text(-0.3, y, f"G{k+1} (GR-1)", ha="right", va="center", fontsize=8)
    xd = [k * Lg / 6 for k in range(7)]
    for x in xd:
        ax.plot([x, x], [0, ys[-1]], color=COL["DF-1"], lw=3); ax.text(x + 0.1, ys[-1] + 0.3, "DF-1", fontsize=7, color=COL["DF-1"])
    for a, b in zip(xd[:-1], xd[1:]):
        for y0, y1 in zip(ys[:-1], ys[1:]):
            if int(y0 / S) in (0, 4):
                ax.plot([a, b], [y0, y1], color=COL["LB-1"], lw=1, ls="--"); ax.plot([a, b], [y1, y0], color=COL["LB-1"], lw=1, ls="--")
    ax.text(Lg / 12, S / 2, "LB-1", fontsize=7, ha="center")
    ax.annotate("", (0, -0.8), (Lg, -0.8), arrowprops=dict(arrowstyle="<->")); ax.text(Lg / 2, -0.65, "30600 (6 x 5100)", ha="center", fontsize=8)
    ax.set_xlim(-3, Lg + 1); ax.set_ylim(-1.2, ys[-1] + 0.8); ax.set_aspect("equal"); ax.axis("off")
    ax = fig.add_axes([0.08, 0.18, 0.5, 0.28]); ax.set_title("Potongan Melintang", fontsize=10)
    ax.add_patch(Rectangle((0, 1.75), 11, 0.25, fc="#cccccc", ec="k")); ax.text(0.2, 2.1, "Slab t=250", fontsize=8)
    x0 = 1.25
    for k in range(n):
        x = x0 + k * S
        ax.plot([x, x], [0.02, 1.7], color=COL["GR-1"], lw=2)
        ax.plot([x - 0.15, x + 0.15], [1.7, 1.7], color=COL["GR-1"], lw=3); ax.plot([x - 0.175, x + 0.175], [0.02, 0.02], color=COL["GR-1"], lw=4)
        ax.text(x, -0.25, f"G{k+1}", ha="center", fontsize=8)
        if k < n - 1:
            ax.plot([x, x + S], [0.4, 0.4], color=COL["DF-1"], lw=2); ax.plot([x, x + S], [1.0, 1.0], color=COL["DF-1"], lw=2)
    ax.text(x0 + S / 2, 0.55, "DF-1", ha="center", fontsize=7)
    ax.set_xlim(-0.3, 11.3); ax.set_ylim(-0.5, 2.4); ax.set_aspect("equal"); ax.axis("off")
    legend(fig.add_axes([0.62, 0.20, 0.36, 0.2]), ["GR-1", "DF-1", "LB-1"])
    pdf.savefig(fig); plt.close(fig)


def details(pdf):
    fig = plt.figure(figsize=(16.5, 11.7))
    title_block(fig, "GAMBAR 5 - DETAIL PENAMPANG WB (skala relatif, satuan mm)", 5)
    codes = list(SEC)
    cols = 6
    for i, c in enumerate(codes):
        r = SEC[c]
        d, bt, tw, tt, bb, tb = (float(r[k]) for k in ("d", "bf_top", "tw", "tf_top", "bf_bot", "tf_bot"))
        ax = fig.add_axes([0.02 + (i % cols) * 0.163, 0.64 - (i // cols) * 0.29, 0.15, 0.24])
        ax.add_patch(Rectangle((-bb / 2, 0), bb, tb, fc=COL[c])); ax.add_patch(Rectangle((-tw / 2, tb), tw, d - tb - tt, fc=COL[c]))
        ax.add_patch(Rectangle((-bt / 2, d - tt), bt, tt, fc=COL[c]))
        m = max(d, bt, bb) * 0.6
        ax.set_xlim(-m, m); ax.set_ylim(-0.25 * d, d * 1.1); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"{c}\n{r['Section']}", fontsize=8)
        ax.text(0, -0.18 * d, f"{r['Element'][:30]}\n{r['kg_per_m']} kg/m", ha="center", fontsize=6.5)
    pdf.savefig(fig); plt.close(fig)


if __name__ == "__main__":
    with PdfPages("output/Gambar_Frame_Code.pdf") as pdf:
        truss_elev(pdf); truss_plan(pdf); truss_section(pdf); girder(pdf); details(pdf)
    print("output/Gambar_Frame_Code.pdf")

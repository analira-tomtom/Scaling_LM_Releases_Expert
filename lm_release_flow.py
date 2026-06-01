"""
LM Map Weekly Release Process – As-Is Flow Diagram  (horizontal / timeline layout)
Sources:
  • Confluence WS6 Lead Time Table (page 1505067229, May 2026)
  • Confluence M-map Lane Model Process (page 1431110045)
  • Slack #tmp-scaling-lm-weekly-releases – feedback Daniel Hernandez Leon 2026-05-19
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── Canvas ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 52, 20
DPI = 130
FONT = "DejaVu Sans"
FS   = 12.0    # main node font  (≥ 10 pt)
FSS  = 10.5    # sub-line font   (≥ 10 pt)

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")
fig.patch.set_facecolor("white")

# ── Colours ───────────────────────────────────────────────────────────────────
C_IN   = "#D6EAF8"
C_BM   = "#5DADE2"
C_QA   = "#C39BD3"
C_FT   = "#D5F5E3"
C_CR   = "#FAD7A0"
C_BI   = "#F9E79F"
C_VA   = "#D7DBDD"
C_ND   = "#F5B7B1"
EDGE   = "#2C3E50"
BUS_C  = "#566573"

# ── Drawing helpers ───────────────────────────────────────────────────────────
def box(ax, cx, cy, w, h, title, sub=None, color=C_FT,
        ec=EDGE, lw=1.5, critical=False):
    patch = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.07",
                           linewidth=2.8 if critical else lw,
                           edgecolor="#C0392B" if critical else ec,
                           facecolor=color, zorder=4)
    ax.add_patch(patch)
    ty = cy + (0.22 if sub else 0)
    ax.text(cx, ty, title, ha="center", va="center",
            fontsize=FS, fontweight="bold" if critical else "normal",
            fontfamily=FONT, zorder=5, linespacing=1.3)
    if sub:
        ax.text(cx, cy - 0.34, sub, ha="center", va="center",
                fontsize=FSS, color="#444", fontfamily=FONT,
                zorder=5, linespacing=1.25)

def parallelogram(ax, cx, cy, w, h, title, sub=None):
    sk = 0.25
    xs = [cx-w/2+sk, cx+w/2+sk, cx+w/2-sk, cx-w/2-sk]
    ys = [cy-h/2,    cy-h/2,    cy+h/2,    cy+h/2]
    ax.fill(xs, ys, color=C_IN, zorder=4)
    ax.plot(xs + [xs[0]], ys + [ys[0]], color=EDGE, lw=1.5, zorder=5)
    ty = cy + (0.16 if sub else 0)
    ax.text(cx, ty, title, ha="center", va="center",
            fontsize=FS, fontfamily=FONT, zorder=6)
    if sub:
        ax.text(cx, cy - 0.30, sub, ha="center", va="center",
                fontsize=FSS, color="#555", fontfamily=FONT, zorder=6)

def arr(ax, x1, y1, x2, y2, color=EDGE, lw=1.5, head=True):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->" if head else "-",
                                color=color, lw=lw,
                                mutation_scale=14, zorder=3))

def seg(ax, x1, y1, x2, y2, color=EDGE, lw=1.5):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, zorder=3)

# ── Layout constants ──────────────────────────────────────────────────────────
FW, FH   = 7.6, 1.55    # feature box width, height
F_PITCH  = 1.90          # row pitch
N_ROWS   = 7

F_Y_TOP  = 15.2          # top row centre
fy = [F_Y_TOP - i * F_PITCH for i in range(N_ROWS)]  # top-to-bottom
MID_Y = (fy[0] + fy[-1]) / 2

# X stage positions
X_IN   = 2.5
X_LMB  = 7.5
X_QA   = 13.5
X_FA   = 20.5
X_FB   = 29.5
X_BIND = 37.5
X_VAL  = 41.8
X_NDS  = 45.5
X_PUB  = 49.5

# Bus bar X positions
X_BUS1 = X_FA - FW/2 - 0.35    # left bus (feeds QA + col A)
X_BUS2 = X_FA + FW/2 + 0.30    # mid bus  (feeds col B)
X_COLL = X_FB + FW/2 + 0.30    # collect bus (features → Binding)

# Feature zone band
BAND_L = X_FA - FW/2 - 0.6
BAND_R = X_FB + FW/2 + 0.6
BAND_B = fy[-1] - FH/2 - 0.35
BAND_T = fy[ 0] + FH/2 + 0.35

band = FancyBboxPatch((BAND_L, BAND_B), BAND_R - BAND_L, BAND_T - BAND_B,
                      boxstyle="round,pad=0.0",
                      linewidth=1.3, linestyle="--",
                      edgecolor="#5DADE2", facecolor="#EBF5FB", zorder=1)
ax.add_patch(band)
ax.text((BAND_L + BAND_R)/2, BAND_T + 0.28,
        "Parallel Feature Processing  (all layers start after LM Basemap)",
        ha="center", va="bottom", fontsize=10.5, color="#2E86C1",
        fontfamily=FONT, fontweight="bold", zorder=2)

# ── STAGE HEADERS ─────────────────────────────────────────────────────────────
HDR_Y = BAND_T + 1.5
for x, lbl in [
    (X_IN,            "Inputs"),
    (X_LMB,           "Basemap\nCompilation"),
    (X_QA,            "QA Gates\n+ Crosslink"),
    ((X_FA+X_FB)/2,   "Feature Processing\n(parallel)"),
    (X_BIND,          "Binding"),
    (X_VAL,           "Validation"),
    (X_NDS,           "NDS.Live"),
    (X_PUB,           "Publish"),
]:
    ax.text(x, HDR_Y, lbl, ha="center", va="bottom",
            fontsize=10.5, color="#1A5276", fontweight="bold",
            fontfamily=FONT,
            bbox=dict(boxstyle="round,pad=0.22",
                      facecolor="#D6EAF8", edgecolor="#5DADE2", lw=1.0))

# ── EXTERNAL INPUTS ───────────────────────────────────────────────────────────
parallelogram(ax, X_IN, fy[1], 4.6, 1.25,
              "S-Map / Road Model", "(External Input)")
box(ax, X_IN, fy[5], 4.6, 1.25,
    "Poles", sub="No basemap\ndependency", color=C_FT)

# ── LM BASEMAP (tall, spans feature zone) ────────────────────────────────────
LMB_H = BAND_T - BAND_B - 0.3
box(ax, X_LMB, MID_Y, 5.5, LMB_H,
    "LM Basemap\nCompilation",
    sub="0.6 days\nOwner: Emilio Iborra",
    color=C_BM, ec="#1A5276", lw=2.8)

# ── QA CHECKS + CROSSLINK ─────────────────────────────────────────────────────
QW, QH = 5.5, 1.40
# Position QA boxes between bus1 and col A, vertically distributed
qa_positions = [fy[0], fy[2], fy[4], fy[6]]   # top to bottom

box(ax, X_QA, qa_positions[0], QW, QH,
    "CC Checks  (after Basemap)",
    sub="Validate basemap for release", color=C_QA)
box(ax, X_QA, qa_positions[1], QW, QH,
    "Coverage Metrics  (after Basemap)", color=C_QA)
box(ax, X_QA, qa_positions[2], QW + 0.4, QH,
    "Basemap Snapshot",
    sub="Fixed revision before Binding", color=C_QA)
box(ax, X_QA, qa_positions[3], QW, QH,
    "Crosslink Creation",
    sub="1.7 days  |  Tim Bekaert", color=C_FT)

# ── FEATURE COLUMN A (top to bottom) ──────────────────────────────────────────
feat_A = [
    ("Self-contained Generic",
     "0.1 d  |  Daniel Dalak / Daria Turobos\nDeps: Crosslink + S-Map + Basemap"),
    ("Self-contained Specific",
     "1.3 days  |  Daria Turobos"),
    ("Lane Function  ⚠  Critical Path",
     "3.0 days  |  Emilia Goraca"),
    ("Lane Restriction",
     "1.9 d  |  Jürgen Reynaert\n(no dep. on Lane Function)"),
    ("Traffic Sign",
     "1.0 d  |  Mick v.d. Spoel / Hristo Dimitrov"),
    ("Traffic Light",
     "1.9 d  |  Mick v.d. Spoel / Hristo Dimitrov"),
    ("Physical Barrier",
     "0.8 days"),
]

for i, (title, sub) in enumerate(feat_A):
    is_crit = "Critical Path" in title
    box(ax, X_FA, fy[i], FW, FH, title, sub=sub,
        color=C_CR if is_crit else C_FT, critical=is_crit)

# ── FEATURE COLUMN B (top to bottom) ──────────────────────────────────────────
feat_B = [
    ("Lane Traversability",     "0.7 days"),
    ("Lane Width",              "2.3 days  |  Jürgen Reynaert"),
    ("Lane Relation Type Crossing", "~2 days  |  Jürgen Reynaert"),
    ("Road Median",             "Owner: Olivier Verstraete"),
    ("Behavior (Drive Path)",   "Depends on Basemap"),
    ("Stop Lines, Crosswalks\n& Surface Signs",
                                "1.0 days  |  Olivier Verstraete"),
    ("Quality Levels",
     "Depends on Basemap\n+ Basemap Snapshot"),
]

for i, (title, sub) in enumerate(feat_B):
    box(ax, X_FB, fy[i], FW, FH, title, sub=sub, color=C_FT)

# ── DOWNSTREAM CHAIN ──────────────────────────────────────────────────────────
DW, DH = 3.8, 2.10
box(ax, X_BIND, MID_Y, DW + 0.4, DH,
    "M-map Binding\n+ Load to Discos",
    sub="0.4 days  |  Ion Lenta",
    color=C_BI, ec="#B7950B", lw=2.2)
box(ax, X_VAL, MID_Y, DW + 1.6, DH + 0.3,
    "Validation / ODRV\n& Quality Validation",
    sub="Marius Swanepoel\nLea Villasante Núñez",
    color=C_VA, ec="#717D7E")
box(ax, X_NDS, MID_Y, DW + 0.5, DH + 0.3,
    "NDS.Live\nCompilation",
    sub="1–4 days  |  Tomas Kroth\n(0.5 d only in rare best case)",
    color=C_ND, ec="#C0392B")
box(ax, X_PUB, MID_Y, DW + 1.0, DH + 0.6,
    "Visual Check +\nPublish to NDS.Live",
    sub="3.1 days\nMarta Olek-Przydatek (checks)\nTomas Kroth (publish)",
    color=C_ND, ec="#C0392B", lw=2.2)

# ── EDGES ─────────────────────────────────────────────────────────────────────

# S-Map → Crosslink
arr(ax, X_IN + 2.3, fy[1] - 0.1, X_QA - QW/2, qa_positions[3],
    color="#2471A3", lw=1.5)
# S-Map → Self-contained Generic (extra dep)
seg(ax, X_IN + 2.3, fy[1] - 0.1, X_BUS1 - 0.1, fy[1] - 0.1, color="#2471A3", lw=1.2)
arr(ax, X_BUS1 - 0.1, fy[1] - 0.1, X_FA - FW/2, fy[0], color="#2471A3", lw=1.2)

# Poles → Binding (direct, green)
POLES_Y = fy[5]
seg(ax, X_IN + 2.3, POLES_Y, X_COLL + 0.1, POLES_Y, color="#1E8449", lw=1.4)
seg(ax, X_COLL + 0.1, POLES_Y, X_COLL + 0.1, BAND_B - 0.15, color="#1E8449", lw=1.4)
arr(ax, X_COLL + 0.1, BAND_B - 0.15, X_BIND - (DW+0.4)/2, MID_Y - DH/2,
    color="#1E8449", lw=1.4)

# LMB right edge → BUS1 (horizontal at midpoint)
seg(ax, X_LMB + 5.5/2, MID_Y, X_BUS1, MID_Y, color=BUS_C, lw=2.0)

# BUS1: vertical bar spanning feature zone
seg(ax, X_BUS1, BAND_B, X_BUS1, BAND_T, color=BUS_C, lw=2.2)

# BUS1 → QA boxes (horizontal)
for qa_y in qa_positions:
    arr(ax, X_BUS1, qa_y, X_QA - QW/2 - 0.05, qa_y, color=BUS_C, lw=1.4)

# BUS1 → col A boxes
for y in fy:
    arr(ax, X_BUS1, y, X_FA - FW/2 - 0.05, y, color=BUS_C, lw=1.3)

# BUS1 → BUS2 (horizontal connectors at each fy, through col A)
# Only draw bus2 connectors for col B routing
seg(ax, X_BUS2, BAND_B, X_BUS2, BAND_T, color=BUS_C, lw=1.6)
# Connect BUS1 to BUS2 at mid height
seg(ax, X_BUS1, MID_Y, X_BUS2, MID_Y, color=BUS_C, lw=1.4)

# BUS2 → col B boxes
for y in fy:
    arr(ax, X_BUS2, y, X_FB - FW/2 - 0.05, y, color=BUS_C, lw=1.2)

# Crosslink → Self-contained Generic (extra dep, blue)
arr(ax, X_QA + QW/2, qa_positions[3], X_FA - FW/2, fy[0],
    color="#1A5276", lw=1.8)

# Basemap Snapshot → Quality Levels (col B, last row = fy[6])
arr(ax, X_QA + (QW+0.4)/2, qa_positions[2], X_FB - FW/2, fy[6],
    color="#7D3C98", lw=1.6)

# Collect bus (right of feature zone)
seg(ax, X_COLL, BAND_B, X_COLL, BAND_T, color=BUS_C, lw=2.2)
# Col A right edge → collect bus
for y in fy:
    seg(ax, X_FA + FW/2, y, X_COLL, y, color=BUS_C, lw=1.0)
# Col B right edge → collect bus
for y in fy:
    seg(ax, X_FB + FW/2, y, X_COLL, y, color=BUS_C, lw=1.0)

# CC + Coverage → collect bus (quality gates before Binding)
seg(ax, X_QA + QW/2, qa_positions[0], X_COLL, qa_positions[0], color=BUS_C, lw=1.1)
seg(ax, X_COLL, qa_positions[0], X_COLL, BAND_T, color=BUS_C, lw=1.1)
seg(ax, X_QA + QW/2, qa_positions[1], X_COLL, qa_positions[1], color=BUS_C, lw=1.1)

# Collect bus → Binding
arr(ax, X_COLL, MID_Y, X_BIND - (DW+0.4)/2 - 0.1, MID_Y, color=BUS_C, lw=2.2)

# Downstream chain
arr(ax, X_BIND + (DW+0.4)/2, MID_Y, X_VAL - (DW+1.6)/2, MID_Y, lw=1.9)
arr(ax, X_VAL + (DW+1.6)/2,  MID_Y, X_NDS - (DW+0.5)/2, MID_Y, lw=1.9)
arr(ax, X_NDS + (DW+0.5)/2,  MID_Y, X_PUB - (DW+1.0)/2, MID_Y, lw=1.9)

# ── TITLE ─────────────────────────────────────────────────────────────────────
ax.text(FIG_W/2, FIG_H - 0.5,
        "LM Map Weekly Release Process — As-Is Flow  (Timeline: left → right)",
        ha="center", va="top",
        fontsize=15, fontweight="bold", fontfamily=FONT)
ax.text(FIG_W/2, FIG_H - 1.05,
        "Sources: Confluence WS6 Lead Time Table (May 2026)  ·  "
        "M-map Lane Model Process  ·  Slack #tmp-scaling-lm-weekly-releases",
        ha="center", va="top", fontsize=9.5, color="#666", fontfamily=FONT)

# ── LEGEND ────────────────────────────────────────────────────────────────────
LX, LY = 0.35, 6.0
items = [
    (C_IN, "External Input"),
    (C_BM, "Basemap Compilation"),
    (C_QA, "QA Gate (after Basemap, before Binding)"),
    (C_FT, "Feature Layer (parallel)"),
    (C_CR, "Critical Path  ⚠"),
    (C_BI, "M-map Binding"),
    (C_VA, "Validation / ODRV"),
    (C_ND, "NDS.Live / Delivery"),
]
ax.text(LX + 0.2, LY + 0.2, "Legend",
        fontsize=11, fontweight="bold", fontfamily=FONT)
for i, (c, lbl) in enumerate(items):
    ly = LY - 0.54 * (i + 1)
    r = FancyBboxPatch((LX, ly - 0.19), 0.44, 0.38,
                       boxstyle="round,pad=0.03",
                       facecolor=c, edgecolor=EDGE, lw=1.0, zorder=5)
    ax.add_patch(r)
    ax.text(LX + 0.60, ly, lbl, va="center",
            fontsize=10, fontfamily=FONT, zorder=6)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = ("/Users/ana.lira/Documents/Orbis/Repos/"
       "Scaling LM Releases Expert/lm_release_flow.png")
fig.savefig(OUT, dpi=DPI, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUT}")
plt.close()

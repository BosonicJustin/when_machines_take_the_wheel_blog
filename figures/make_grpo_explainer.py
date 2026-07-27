#!/usr/bin/env python3
"""GRPO explainer — a visual illustration of the mechanic (Anthropic/Epoch style).

A task (real listing w/ picture) -> a robot MODEL generates N attempts (the
"group") -> each is auto-scored -> split by the group's own average -> that
signal updates the model. PNG (300 dpi) + SVG + PDF.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import matplotlib.image as mpimg

GLOVE_IMG = mpimg.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "assets", "work_gloves.png"))

for cand in ["Helvetica Neue", "Helvetica", "Arial"]:
    if any(cand == f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand, "DejaVu Sans"]
        break
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["axes.unicode_minus"] = False

PINK, TEAL, GRAY = "#D14C86", "#3E9DA1", "#B4BAC4"
PINK_D, TEAL_D, GRAY_D = "#B23A6E", "#2E8388", "#8B93A0"
PINK_L = "#F7E1EB"
INK, MUTE, FACE = "#1A1D23", "#5B6675", "#FFFFFF"
BOXEDGE = "#E2E6EC"
GLOVE, GLOVE_D = "#A7B1BE", "#8B93A0"

FIG_W, FIG_H = 13.8, 6.4
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=300)
fig.patch.set_facecolor(FACE)
ax.set_facecolor(FACE)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

# inch -> data helpers (axes fill ~0.99 of the figure), for aspect-true shapes
AXW, AXH = FIG_W * 0.99, FIG_H * 0.99
def dx(inch): return inch / AXW
def dy(inch): return inch / AXH


def rbox(x, y, w, h, fc, ec, lw=1.1, rs=0.02, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0.003,rounding_size={rs}",
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def arrow(p0, p1, color, lw=1.6, rad=0.0, ms=14, z=1):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms,
                 color=color, lw=lw, connectionstyle=f"arc3,rad={rad}",
                 shrinkA=2, shrinkB=2, zorder=z))


gx0, gy0, gx1, gy1 = 0.52, 0.335, 0.84, 0.85
CY = (gy0 + gy1) / 2

# ---------------------------------------------------------------- 1. TASK card
tw, th = 0.15, 0.36
tx, ty = 0.03, CY - th / 2
rbox(tx, ty, tw, th, "#FFFFFF", BOXEDGE, 1.2, rs=0.013, z=3)
hh = dy(0.24)
rbox(tx, ty + th - hh, tw, hh, TEAL, TEAL, 0, rs=0.013, z=4)
ax.text(tx + tw / 2, ty + th - hh / 2, "LISTING", ha="center", va="center",
        color="white", fontsize=12.5, fontweight="bold", zorder=5)
# product photo: the actual work-gloves image, resized into the card (square)
imh = dy(0.68)
imw = imh * (AXH / AXW)
icx = tx + tw / 2
fpx, fpy = dx(0.05), dy(0.05)          # even frame padding around the photo
frame_top = ty + th - hh - dy(0.09)    # clear gap below the header
frame_bot = frame_top - (imh + 2 * fpy)
itop = frame_top - fpy
ibot = itop - imh
rbox(icx - imw / 2 - fpx, frame_bot, imw + 2 * fpx, imh + 2 * fpy,
     "#FFFFFF", "#DEE2E7", 0.9, rs=0.006, z=4)
ax.imshow(GLOVE_IMG, extent=[icx - imw / 2, icx + imw / 2, ibot, itop],
          aspect="auto", zorder=5, interpolation="antialiased")
# listing text (roomy, clear bottom padding)
tl = [("Work gloves", INK, "bold", 10.5), ("PU-coated · black", MUTE, "normal", 9.5),
      ("size 10 · 12 pairs", MUTE, "normal", 9.5), ("Brand: AmazonBasics", MUTE, "normal", 9.5)]
ty0 = frame_bot - dy(0.16)
for i, (t, col, wt, fs) in enumerate(tl):
    ax.text(tx + dx(0.2), ty0 - i * dy(0.24), t, ha="left", va="center",
            color=col, fontsize=fs, fontweight=wt, zorder=8)
ax.text(tx + tw / 2, ty - 0.045, "Catalog item", ha="center", va="center",
        fontsize=16.7, fontweight="bold", color=INK)

# ---------------------------------------------------------------- 2. ROBOT model
mw, mh = 0.118, 0.25
mx, my = 0.268, CY - mh / 2
mcx, mcy = mx + mw / 2, CY
rbox(mx, my, mw, mh, "#E3F1F1", TEAL_D, 1.5, rs=0.018, z=3)

def draw_robot(cx, cy):
    hw, hh_ = dx(0.74), dy(0.76)
    ax.plot([cx, cx], [cy + hh_ / 2, cy + hh_ / 2 + dy(0.12)], color=TEAL_D,
            lw=2.0, zorder=4, solid_capstyle="round")
    ax.scatter([cx], [cy + hh_ / 2 + dy(0.14)], s=34, c=TEAL_D, zorder=5)
    rbox(cx - hw / 2, cy - hh_ / 2, hw, hh_, "#FFFFFF", TEAL_D, 2.0, rs=dy(0.12), z=4)
    ax.scatter([cx - dx(0.16), cx + dx(0.16)], [cy + dy(0.08), cy + dy(0.08)],
               s=78, c=TEAL_D, zorder=5)
    rbox(cx - dx(0.19), cy - dy(0.2), dx(0.38), dy(0.09), TEAL, TEAL, 0, rs=dy(0.035), z=5)

draw_robot(mcx, my + mh * 0.6)
ax.text(mcx, my + mh * 0.17, "MODEL", ha="center", va="center", fontsize=15.9,
        fontweight="bold", color=TEAL_D, zorder=5)
arrow((tx + tw + 0.004, CY), (mx - 0.004, CY), "#9AA1AC", 1.8)
ax.text((tx + tw + mx) / 2, CY + 0.045, "assign task", ha="center", va="center",
        fontsize=11.5, color=MUTE, zorder=4)

# ------------------------------------ single clear arrow: model -> group panel
arrow((mx + mw + 0.004, CY), (gx0 - 0.004, CY), TEAL_D, 2.4, ms=18)
ax.text((mx + mw + gx0) / 2, CY + 0.065, "N attempts,", ha="center", va="center",
        fontsize=13.0, color=TEAL_D, fontweight="bold", zorder=4)
ax.text((mx + mw + gx0) / 2, CY + 0.038, "each auto-scored", ha="center",
        va="center", fontsize=11.5, color=MUTE, zorder=4)

# ---------------------------------------------- group panel (attempts + scores)
rbox(gx0, gy0, gx1 - gx0, gy1 - gy0, "#FCFCFD", BOXEDGE, 1.1, rs=0.015, z=1)
ax.text((gx0 + gx1) / 2, gy1 - 0.032, "N attempts: the “group”", ha="center",
        va="center", fontsize=15.9, fontweight="bold", color=INK, zorder=4)

scores = [0.83, 0.72, 0.64, 0.55, 0.38, 0.33]
avg = float(np.mean(scores))
ys = np.linspace(gy1 - 0.10, gy0 + 0.042, len(scores))
ticket_x, ticket_w, ticket_h = gx0 + 0.02, 0.15, 0.042
pill_x, pill_w = ticket_x + ticket_w + 0.014, 0.05

for s, y in zip(scores, ys):
    up = s >= avg
    c, cd = (PINK, PINK_D) if up else (GRAY, GRAY_D)
    cl = PINK_L if up else "#ECEEF1"
    rbox(ticket_x, y, ticket_w, ticket_h, "#FFFFFF", "#DEE2E8", 1.0, rs=0.009, z=3)
    for k in range(3):
        rbox(ticket_x + 0.012 + k * 0.019, y + ticket_h / 2 - 0.0072, 0.013, 0.0145,
             cl, cd, 0.6, rs=0.004, z=4)
    ax.text(ticket_x + 0.074, y + ticket_h / 2, "a full attempt", ha="left",
            va="center", fontsize=11.0, color=MUTE, zorder=4)
    rbox(pill_x, y + ticket_h / 2 - 0.018, pill_w, 0.036, c, cd, 0.8, rs=0.02, z=4)
    ax.text(pill_x + pill_w / 2, y + ticket_h / 2, f"{s:.2f}", ha="center",
            va="center", fontsize=12.8, fontweight="bold", color="white", zorder=5)

avg_y = (ys[2] + ys[3]) / 2 + ticket_h / 2
ax.plot([ticket_x - 0.006, gx1 - 0.012], [avg_y, avg_y], ls=(0, (4, 3)),
        color=INK, lw=1.3, zorder=6)
ax.text(gx1 + 0.024, avg_y, "group average", ha="left", va="center",
        fontsize=11.6, color=INK, zorder=6)

rx = gx1 + 0.024
top_mid, bot_mid = (ys[0] + ys[2]) / 2 + ticket_h / 2, (ys[3] + ys[5]) / 2 + ticket_h / 2
ax.scatter([rx], [top_mid + 0.013], marker="^", s=72, c=PINK, edgecolors="none", zorder=5)
ax.text(rx + 0.014, top_mid + 0.013, "reinforced", ha="left", va="center",
        fontsize=13.3, fontweight="bold", color=PINK_D, zorder=5)
ax.text(rx + 0.038, top_mid - 0.02, "beat the average", ha="center", va="center",
        fontsize=11.6, color=INK, zorder=5)
ax.scatter([rx], [bot_mid + 0.013], marker="v", s=72, c=GRAY, edgecolors="none", zorder=5)
ax.text(rx + 0.014, bot_mid + 0.013, "discouraged", ha="left", va="center",
        fontsize=13.3, fontweight="bold", color=GRAY_D, zorder=5)
ax.text(rx + 0.043, bot_mid - 0.02, "below the average", ha="center", va="center",
        fontsize=11.6, color=INK, zorder=5)

# ------------------------------------ UPDATE feedback (U-shaped return path)
px, yc = (gx0 + gx1) / 2, 0.185
ax.plot([px, px], [gy0 - 0.006, yc], color=PINK_D, lw=2.1, zorder=2,
        solid_capstyle="round")
ax.plot([px, mcx], [yc, yc], color=PINK_D, lw=2.1, zorder=2, solid_capstyle="round")
ax.add_patch(FancyArrowPatch((mcx, yc), (mcx, my - 0.006), arrowstyle="-|>",
             mutation_scale=17, color=PINK_D, lw=2.1, shrinkA=0, shrinkB=0, zorder=2))
lcx = (px + mcx) / 2
ax.text(lcx, yc, "Update the model", ha="center", va="center", fontsize=18.1,
        fontweight="bold", color=PINK_D, zorder=6,
        bbox=dict(facecolor=FACE, edgecolor="none", pad=5))
ax.text(lcx, yc - 0.05,
        "make above-average attempts more likely, below-average less likely",
        ha="center", va="center", fontsize=13.6, color=MUTE, zorder=6)

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)

base = os.path.dirname(os.path.abspath(__file__))
for ext in ("png", "svg"):
    p = os.path.join(base, f"grpo_explainer.{ext}")
    fig.savefig(p, dpi=300, facecolor=FACE)
    print("wrote", p)

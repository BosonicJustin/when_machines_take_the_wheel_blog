#!/usr/bin/env python3
"""How a task becomes a smarter model (Anthropic/Epoch style).

User task -> your model acts in an environment (tools, data, external sources)
-> the outcome is scored by a rubric -> a reward signal trains the model.
All shapes fit inside their containers; spacing is even. PNG/SVG/PDF.
"""
import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse

for cand in ["Helvetica Neue", "Helvetica", "Arial"]:
    if any(cand == f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand, "DejaVu Sans"]
        break
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["axes.unicode_minus"] = False

PINK, TEAL, GRAY = "#D14C86", "#3E9DA1", "#B4BAC4"
PINK_D, TEAL_D, GRAY_D = "#B23A6E", "#2E8388", "#8B93A0"
PINK_L, TEAL_L = "#F7E1EB", "#E3F1F1"
INK, MUTE, FACE = "#1A1D23", "#5B6675", "#FFFFFF"
BOXEDGE, PANEL = "#E2E6EC", "#F6F8FA"

FIG_W, FIG_H = 14.0, 8.6
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=300)
fig.patch.set_facecolor(FACE)
ax.set_facecolor(FACE)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
AXW, AXH = FIG_W * 0.99, FIG_H * 0.99
def dx(i): return i / AXW
def dy(i): return i / AXH


def rbox(x, y, w, h, fc, ec, lw=1.1, rs=0.014, z=2, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.002,rounding_size={rs}",
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z, linestyle=ls))


def circle(cx, cy, r, fc, ec, lw=1.2, z=4):
    ax.add_patch(Ellipse((cx, cy), 2 * dx(r), 2 * dy(r), facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def arrow(p0, p1, color, lw=1.6, rad=0.0, ms=13, z=3):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color,
                 lw=lw, connectionstyle=f"arc3,rad={rad}", shrinkA=3, shrinkB=3, zorder=z))


def robot(cx, cy, col, eye):
    hw, hh = dx(0.6), dy(0.58)
    ax.plot([cx, cx], [cy + hh / 2, cy + hh / 2 + dy(0.12)], color=col, lw=1.8, zorder=6, solid_capstyle="round")
    circle(cx, cy + hh / 2 + dy(0.14), 0.05, col, "none", 0, 6)
    rbox(cx - hw / 2, cy - hh / 2, hw, hh, "none", col, 1.8, rs=dy(0.09), z=6)
    circle(cx - dx(0.13), cy + dy(0.05), 0.048, eye, "none", 0, 7)
    circle(cx + dx(0.13), cy + dy(0.05), 0.048, eye, "none", 0, 7)
    rbox(cx - dx(0.14), cy - dy(0.16), dx(0.28), dy(0.066), eye, eye, 0, rs=dy(0.03), z=7)


def draw_check(cx, cy, col):
    ax.plot([cx - dx(0.042), cx - dx(0.007), cx + dx(0.055)], [cy - dy(0.003), cy - dy(0.047), cy + dy(0.055)],
            color=col, lw=1.7, solid_capstyle="round", solid_joinstyle="round", zorder=6)


def draw_cross(cx, cy, col):
    for a, b in (((-0.038, 0.038), (0.038, -0.038)), ((-0.038, -0.038), (0.038, 0.038))):
        ax.plot([cx + dx(a[0]), cx + dx(b[0])], [cy + dy(a[1]), cy + dy(b[1])], color=col,
                lw=1.7, solid_capstyle="round", zorder=6)


def chip(x, y, w, label, dot):
    h = dy(0.33)
    rbox(x, y - h / 2, w, h, "#FFFFFF", BOXEDGE, 1.0, rs=dy(0.09), z=5)
    circle(x + dx(0.15), y, 0.048, dot, "none", 0, 6)
    ax.text(x + dx(0.31), y, label, ha="left", va="center", fontsize=9, color=INK, zorder=6)


def icon_gear(cx, cy, col=TEAL_D):
    for k in range(8):
        a = k * math.pi / 4
        ca, sa = math.cos(a), math.sin(a)
        ax.plot([cx + dx(0.033) * ca, cx + dx(0.051) * ca],
                [cy + dy(0.033) * sa, cy + dy(0.051) * sa],
                color=col, lw=1.5, solid_capstyle="round", zorder=5)
    circle(cx, cy, 0.034, "none", col, 1.5, 5)
    circle(cx, cy, 0.012, col, "none", 0, 6)


def icon_db(cx, cy, col=TEAL_D):
    # database cylinder: top ellipse + sides + front seams
    tw, th = 0.047, 0.016
    top = cy + dy(0.040)
    bot = cy - dy(0.040)
    ax.add_patch(Ellipse((cx, top), 2 * dx(tw), 2 * dy(th), facecolor="#FFFFFF",
                 edgecolor=col, lw=1.5, zorder=5))
    ax.plot([cx - dx(tw), cx - dx(tw)], [bot, top], color=col, lw=1.5, zorder=5)
    ax.plot([cx + dx(tw), cx + dx(tw)], [bot, top], color=col, lw=1.5, zorder=5)
    arc = np.linspace(0, math.pi, 24)
    for yy in (cy, bot):
        ax.plot(cx + dx(tw) * np.cos(arc), yy - dy(th) * np.sin(arc),
                color=col, lw=1.5, zorder=5)


def icon_star(cx, cy, col=TEAL_D):
    ax.scatter([cx], [cy], marker="*", s=95, c=col, edgecolors="none", zorder=5)


def icon_globe(cx, cy, col=TEAL_D):
    R = 0.05
    circle(cx, cy, R, "none", col, 1.4, 5)
    ax.plot([cx - dx(R), cx + dx(R)], [cy, cy], color=col, lw=1.2, zorder=5)
    ax.add_patch(Ellipse((cx, cy), 2 * dx(R * 0.5), 2 * dy(R), facecolor="none",
                 edgecolor=col, lw=1.2, zorder=5))


fig.text(0.5, 0.968, "How a task becomes a smarter model", fontsize=21,
         fontweight="bold", color=INK, ha="center", va="top")

# ================================================================ ENVIRONMENT
ex0, ey0, ex1, ey1 = 0.375, 0.10, 0.965, 0.80
env_cx = (ex0 + ex1) / 2
rbox(ex0, ey0, ex1 - ex0, ey1 - ey0, "#FCFDFE", BOXEDGE, 1.2, rs=dy(0.12), z=1, ls=(0, (5, 4)))

# section geometry: even padding, chips fit inside with margin
SIN_L = ex0 + 0.025               # section left
SIN_W = (ex1 - ex0) - 0.05        # section width
cw, cgap = 0.158, 0.013
ccx0 = SIN_L + 0.023              # first chip left


def section(y0, y1, title, icon):
    rbox(SIN_L, y0, SIN_W, y1 - y0, PANEL, BOXEDGE, 1.0, rs=dy(0.11), z=2)
    bcx, bcy = SIN_L + 0.026, y1 - dy(0.3)
    circle(bcx, bcy, 0.10, TEAL_L, TEAL, 1.2, 3)
    icon(bcx, bcy)
    ax.text(SIN_L + 0.048, bcy, title, ha="left", va="center", fontsize=12, fontweight="bold", color=INK, zorder=3)


def grid_chips(y1, names, dot):
    for i, name in enumerate(names):
        cx = ccx0 + (i % 3) * (cw + cgap)
        cy = y1 - dy(0.76) - (i // 3) * dy(0.42)
        chip(cx, cy, cw, name, dot)


t_y1, t_y0 = 0.755, 0.585
section(t_y0, t_y1, "Tools", icon_gear)
grid_chips(t_y1, ["Search", "Browse", "Post", "Notify", "Calendar", "Database"], TEAL)
d_y1, d_y0 = 0.545, 0.375
section(d_y0, d_y1, "Data", icon_db)
grid_chips(d_y1, ["Documents", "Images", "Slides", "Spreadsheets", "Emails", "PDF reports"], GRAY_D)
r_y1, r_y0 = 0.335, 0.12
section(r_y0, r_y1, "Rubric / Reward", icon_star)

# reward badge (left) + checklist (right), both inside the rubric section
rcx, rcy = SIN_L + 0.085, (r_y0 + r_y1) / 2 - dy(0.18)
circle(rcx, rcy, 0.42, "#FFFFFF", PINK, 2.8, 5)
ax.text(rcx, rcy, "0.8", ha="center", va="center", fontsize=19, fontweight="bold", color=PINK_D, zorder=6)
ax.text(rcx, rcy - dy(0.55), "reward score", ha="center", va="center", fontsize=8, fontweight="bold", color=MUTE, zorder=5)
checks = [("Followed the required format", True), ("Matched the task instructions", True),
          ("Missed a required attribute", False), ("No policy violations", True),
          ("Used an unverified source", False)]
ck_x = SIN_L + 0.26
for i, (txt, ok) in enumerate(checks):
    cyk = r_y1 - dy(0.3) - i * dy(0.29)
    col = TEAL if ok else PINK
    circle(ck_x, cyk, 0.096, TEAL_L if ok else PINK_L, col, 1.2, 4)
    (draw_check if ok else draw_cross)(ck_x, cyk, col)
    ax.text(ck_x + dx(0.22), cyk, txt, ha="left", va="center", fontsize=9.2, color=INK, zorder=5)

# EXTERNAL SOURCES — centered above the environment, straight "queries" arrow
esw, esh = 0.30, dy(0.58)
esx0 = env_cx - esw / 2
esy = ey1 + dy(0.62)
rbox(esx0, esy - esh / 2, esw, esh, "#FFFFFF", GRAY_D, 1.1, rs=dy(0.12), z=3, ls=(0, (4, 3)))
circle(esx0 + dx(0.32), esy, 0.082, TEAL_L, TEAL, 1.2, 4)
icon_globe(esx0 + dx(0.32), esy)
ax.text(esx0 + dx(0.6), esy + dy(0.1), "External sources", ha="left", va="center", fontsize=10, fontweight="bold", color=INK, zorder=4)
ax.text(esx0 + dx(0.6), esy - dy(0.12), "APIs, third-party data", ha="left", va="center", fontsize=8.6, color=MUTE, zorder=4)
arrow((env_cx, t_y1 + 0.004), (env_cx, esy - esh / 2 - 0.004), GRAY_D, 1.3, ms=11)
ax.text(env_cx + 0.013, (t_y1 + esy - esh / 2) / 2 - 0.016, "queries", ha="left", va="center", fontsize=8.4, color=MUTE, zorder=4)

# inner env arrows: reads, outcome (straight, centered)
arrow((env_cx, t_y0 - 0.004), (env_cx, d_y1 + 0.004), GRAY_D, 1.3, ms=11)
ax.text(env_cx + 0.013, (t_y0 + d_y1) / 2, "reads", ha="left", va="center", fontsize=8.4, color=MUTE, zorder=4)
arrow((env_cx, d_y0 - 0.004), (env_cx, r_y1 + 0.004), GRAY_D, 1.3, ms=11)
ax.text(env_cx + 0.013, (d_y0 + r_y1) / 2, "outcome", ha="left", va="center", fontsize=8.4, color=MUTE, zorder=4)

# ================================================================ MODEL (infra)
inx, iny, inw, inh = 0.035, 0.105, 0.25, 0.31
rbox(inx, iny, inw, inh, "#FFFFFF", GRAY_D, 1.2, rs=dy(0.1), z=2, ls=(0, (5, 4)))
ax.text(inx + inw / 2, iny + inh - dy(0.15), "YOUR CLOUD / YOUR INFRA", ha="center", va="center",
        fontsize=8.4, fontweight="bold", color=MUTE, zorder=3)
mbx, mby, mbw, mbh = inx + dx(0.42), iny + dy(0.3), inw - dx(0.84), inh - dy(1.0)
rbox(mbx, mby, mbw, mbh, TEAL, TEAL_D, 1.5, rs=dy(0.14), z=4)
mcx = mbx + mbw / 2
robot(mcx, mby + mbh * 0.64, "#FFFFFF", "#FFFFFF")
ax.text(mcx, mby + dy(0.22), "AI Model", ha="center", va="center", fontsize=12, fontweight="bold", color="#FFFFFF", zorder=6)
sn = (mbx + mbw, mby + mbh * 0.5)

# task bubble above the model + straight task arrow
buby = 0.66
rbox(mcx - 0.135, buby - dy(0.27), 0.27, dy(0.54), "#EEF1F5", BOXEDGE, 1.0, rs=dy(0.14), z=3)
ax.text(mcx, buby, "“Does this follow our safety policy?”", ha="center", va="center", fontsize=9.2, fontstyle="italic", color=INK, zorder=4)
arrow((mcx, buby - dy(0.29)), (mcx, iny + inh + 0.004), GRAY_D, 1.6)
ax.text(mcx + 0.013, (buby - dy(0.29) + iny + inh) / 2, "task", ha="left", va="center", fontsize=8.6, color=MUTE, zorder=4)

# model -> TOOLS (interacts): smooth curve from the model up through the infra box to Tools
arrow((mbx + mbw - 0.02, mby + mbh + 0.003), (ex0 - 0.004, (t_y0 + t_y1) / 2), GRAY_D, 1.6, rad=-0.26)
ax.text(0.314, 0.52, "interacts", ha="center", va="center", fontsize=9, color=MUTE, zorder=4)

# reward -> model: a single training signal
arrow((rcx - dx(0.42), rcy), (sn[0] + 0.003, sn[1]), PINK, 2.8, rad=0.06, ms=16, z=7)
ax.text((inx + inw + ex0) / 2, rcy + dy(0.62), "reward signal", ha="center", va="center", fontsize=9.5, fontweight="bold", color=PINK_D, zorder=8)

# shift the axes box down (span kept at 0.99 so circles stay round) to give
# the title a bit more breathing room below it
plt.subplots_adjust(left=0.005, right=0.995, top=0.97, bottom=-0.02)

base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for ext in ("png", "svg", "pdf"):
    p = os.path.join(base, f"benchmarks/figures/training_loop.{ext}")
    fig.savefig(p, dpi=300, facecolor=FACE)
    print("wrote", p)

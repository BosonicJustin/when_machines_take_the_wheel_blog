#!/usr/bin/env python3
"""Cost vs. quality (Anthropic/Epoch style, log-x): fine-tuned 9B owns the corner.

x = cost per 1,000 listings (USD, LOG)   [lower = better -> left]
y = average % of maximum achievable task score (oracle ceiling 0.717 = 100)

Costs = published 2026-07 per-token rates x ~per-listing token usage. OSS models
priced on real serverless inference rates (DeepInfra/Together/Fireworks etc.);
fine-tune serves at the base rate (no per-token premium). Frontier priced on
each vendor's API. Reasoning tiers (pro/sol) bill hidden reasoning as output ->
conservative lower bound. Details in benchmarks/results/cost_estimates.md.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib.patheffects as pe

for cand in ["Helvetica Neue", "Helvetica", "Arial"]:
    if any(cand == f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand, "DejaVu Sans"]
        break
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["axes.unicode_minus"] = False

ORACLE = 0.717
N = 100.0 / ORACLE

# (full label, reward, cost $/1k, tier)
pts = [
    ("Qwen3.5-9B + GRPO  (ours)", 0.626, 0.50, "trained"),
    ("Qwen3.5-27B",               0.471, 0.70, "base"),
    ("Qwen3.5-9B",                0.460, 0.50, "base"),
    ("Qwen3.5-4B",                0.452, 0.20, "base"),
    ("Qwen3.5-2B",                0.204, 0.08, "base"),
    ("Qwen3.5-0.8B",              0.224, 0.10, "base"),
    ("Gemini 3.1 Pro",            0.5445, 18.6, "frontier"),
    ("GPT-5.6-sol",               0.512, 28.6,  "frontier"),
    ("GPT-5.5",                   0.500, 33.6,  "frontier"),
    ("Claude Fable 5",            0.544, 111.3, "frontier"),
    ("GPT-5.5-pro",               0.504, 171.5, "frontier"),
]

# Anthropic/Epoch palette: raspberry hero, teal frontier, muted gray base
COL      = {"trained": "#D14C86", "frontier": "#3E9DA1", "base": "#B4BAC4"}
COL_EDGE = {"trained": "#B23A6E", "frontier": "#2E8388", "base": "#8B93A0"}
INK, MUTE, GRID, FACE = "#1A1D23", "#6B7280", "#ECEEF1", "#FFFFFF"

fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=300)
fig.patch.set_facecolor(FACE)
ax.set_facecolor(FACE)
ax.set_xscale("log")

XLO, XHI, YLO, YHI = 0.055, 320, 22, 104

# oracle ceiling
ax.axhline(100, color="#9AA1AC", lw=1.2, ls=(0, (5, 4)), zorder=1)
ax.text(XHI / 1.03, 100.7, "oracle ceiling (best any model could do)",
        color=MUTE, fontsize=8.8, ha="right", va="bottom")

# training arrow: base 9B -> trained 9B at the same cost.
# shrink ends in POINTS by each marker's radius (+gap) so the head stops just
# below the large hero marker instead of landing inside it.
ax.annotate("", xy=(0.50, 0.626 * N), xytext=(0.50, 0.460 * N),
            arrowprops=dict(arrowstyle="-|>", color=COL_EDGE["trained"], lw=1.8,
                            shrinkA=9, shrinkB=18), zorder=4)
ax.text(0.62, 76.0, "+23 pts, same cost", rotation=90, ha="center", va="center",
        fontsize=8.6, fontweight="bold", color=COL_EDGE["trained"], zorder=7)

# points
for label, r, cost, tier in pts:
    ypc, big = r * N, tier == "trained"
    ax.scatter([cost], [ypc],
               s=560 if big else (95 if tier == "base" else 235),
               c=COL[tier], edgecolors=COL_EDGE[tier],
               linewidths=1.8 if big else 0.9, zorder=6,
               alpha=1.0 if tier != "base" else 0.9, marker="o",
               path_effects=[pe.withStroke(linewidth=5, foreground="#D14C8622")]
               if big else None)

def money(c):
    return f"${c:.2f}" if c < 1 else f"${c:,.0f}"

place = {
    "Qwen3.5-9B + GRPO  (ours)": (12, 10, "left", "bottom"),
    "Qwen3.5-0.8B": (0, 8, "center", "bottom"),
    "Qwen3.5-2B":   (0, -8, "center", "top"),
    "Qwen3.5-4B":   (-9, 0, "right", "center"),
    "Qwen3.5-9B":   (-9, -6, "right", "top"),
    "Qwen3.5-27B":  (9, 3, "left", "center"),
    "Gemini 3.1 Pro": (0, 15, "center", "bottom"),
    "GPT-5.6-sol":    (10, 9, "left", "bottom"),
    "GPT-5.5":        (0, -15, "center", "top"),
    "Claude Fable 5": (0, 15, "center", "bottom"),
    "GPT-5.5-pro":    (0, -15, "center", "top"),
}
for label, r, cost, tier in pts:
    ypc = r * N
    dx, dy, ha, va = place[label]
    if tier == "base":
        size = label.split("-")[-1]
        ax.annotate(f"{size}\n{money(cost)} · {ypc:.0f}%", (cost, ypc),
                    textcoords="offset points", xytext=(dx, dy), ha=ha, va=va,
                    fontsize=8.3, color=MUTE, linespacing=1.3, zorder=7)
    else:
        weight = "bold" if tier == "trained" else "normal"
        color = COL_EDGE["trained"] if tier == "trained" else INK
        ax.annotate(f"{label}\n{money(cost)} / 1k  ·  {ypc:.0f}%", (cost, ypc),
                    textcoords="offset points", xytext=(dx, dy), ha=ha, va=va,
                    fontsize=9.4, fontweight=weight, color=color, linespacing=1.35,
                    zorder=7)

# axes
ax.set_xlim(XLO, XHI)
ax.set_ylim(YLO, YHI)
ax.set_xlabel("Cost per 1,000 listings  (USD, log scale)", fontsize=11.5,
              color=INK, labelpad=9)
ax.set_ylabel("Average % of maximum achievable task score", fontsize=11.5,
              color=INK, labelpad=9)
ax.set_xticks([0.1, 0.3, 1, 3, 10, 30, 100, 300])
ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:g}"))
ax.set_yticks([30, 40, 50, 60, 70, 80, 90, 100])
ax.tick_params(colors=MUTE, labelsize=10, length=0)
ax.grid(axis="y", color=GRID, lw=0.9, zorder=0)
ax.grid(axis="x", which="major", color=GRID, lw=0.9, zorder=0)
ax.grid(axis="x", which="minor", color="#F4F5F7", lw=0.6, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color("#D5DAE1")

# title (centered over the plot)
fig.text(0.52, 0.955, "Cost vs. quality on catalog integrity", fontsize=18,
         fontweight="bold", color=INK, ha="center", va="top")

# legend inside bottom-right (empty space), framed
handles = [
    plt.Line2D([0], [0], marker="o", ls="", ms=12, mfc=COL["trained"],
               mec=COL_EDGE["trained"], label="Fine-tuned (ours)"),
    plt.Line2D([0], [0], marker="o", ls="", ms=11, mfc=COL["frontier"],
               mec=COL_EDGE["frontier"], label="Frontier API models"),
    plt.Line2D([0], [0], marker="o", ls="", ms=9, mfc=COL["base"],
               mec=COL_EDGE["base"], label="Untrained open models"),
]
leg = ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=9.8,
                title="Model type", labelspacing=0.8, handletextpad=0.6,
                borderpad=1.0, borderaxespad=1.2)
leg.get_title().set_fontsize(10.4)
leg.get_title().set_fontweight("bold")
leg.get_title().set_color(INK)
leg._legend_box.align = "left"
leg.get_frame().set_edgecolor("#E2E6EC")
leg.get_frame().set_facecolor("#FFFFFF")
leg.get_frame().set_linewidth(0.9)

plt.subplots_adjust(left=0.075, right=0.965, top=0.90, bottom=0.115)

base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for ext in ("png", "svg", "pdf"):
    p = os.path.join(base, f"benchmarks/figures/cost_quality.{ext}")
    fig.savefig(p, dpi=300, facecolor=FACE)
    print("wrote", p)

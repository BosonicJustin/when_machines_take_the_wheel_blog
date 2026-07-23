#!/usr/bin/env python3
"""Quality ranking (Anthropic/Epoch style): fine-tuned 9B vs frontier vs base.

Scores normalized to % of the oracle ceiling (max achievable reward ≈ 0.717 =
100). Measured in the same vf-eval harness (200 val episodes, seed 0). Renders
PNG (300 dpi) + SVG + PDF.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

for cand in ["Helvetica Neue", "Helvetica", "Arial"]:
    if any(cand == f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand, "DejaVu Sans"]
        break
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["axes.unicode_minus"] = False

ORACLE = 0.717
NORM = 100.0 / ORACLE
rows = [
    ("Qwen3.5-9B + GRPO  (ours)",        0.626, "trained"),
    ("Gemini 3.1 Pro",                   0.5445, "frontier"),
    ("Claude Fable 5",                   0.544, "frontier"),
    ("GPT-5.6-sol  · max reasoning",     0.512, "frontier"),
    ("GPT-5.5-pro  · max reasoning",     0.504, "frontier"),
    ("GPT-5.5",                          0.500, "frontier"),
    ("Qwen3.5-27B  (base)",              0.471, "base"),
    ("Qwen3.5-9B  (base)",               0.460, "base"),
    ("Qwen3.5-4B  (base)",               0.452, "base"),
    ("Qwen3.5-0.8B  (base)",             0.224, "base"),
    ("Qwen3.5-2B  (base)",               0.204, "base"),
]

# Anthropic/Epoch palette: raspberry hero, teal frontier, muted gray base
COL      = {"trained": "#D14C86", "frontier": "#3E9DA1", "base": "#B4BAC4"}
COL_EDGE = {"trained": "#B23A6E", "frontier": "#2E8388", "base": "#8B93A0"}
INK, MUTE, GRID, FACE = "#1A1D23", "#6B7280", "#ECEEF1", "#FFFFFF"

labels = [r[0] for r in rows]
vals   = [r[1] * NORM for r in rows]
tiers  = [r[2] for r in rows]
y      = list(range(len(rows)))[::-1]
P_LO, P_HI = 0.500 * NORM, 0.5445 * NORM

fig, ax = plt.subplots(figsize=(12.6, 8.0), dpi=300)
fig.patch.set_facecolor(FACE)
ax.set_facecolor(FACE)

# frontier plateau band + oracle ceiling (=100)
ax.axvspan(P_LO, P_HI, color="#3E9DA1", alpha=0.06, zorder=0)
ax.text((P_LO + P_HI) / 2, len(rows) - 0.32, "frontier plateau", color="#2E8388",
        fontsize=8.5, style="italic", ha="center", va="center", alpha=0.9)
ax.axvline(100, color="#9AA1AC", lw=1.2, ls=(0, (5, 4)), zorder=1)
ax.text(100 - 0.7, 5.0, "oracle ceiling (100%)", color=MUTE, fontsize=9,
        ha="right", va="center", rotation=90)

BH = 0.62
for yi, v, t in zip(y, vals, tiers):
    ax.barh(yi, v, height=BH, color=COL[t], edgecolor=COL_EDGE[t],
            linewidth=0.6, zorder=3)
    ax.text(v + 0.9, yi, f"{v:.1f}", va="center", ha="left", fontsize=10.5,
            fontweight="bold", color=INK, zorder=5)

hero_y = y[0]
ax.add_patch(FancyBboxPatch(
    (0, hero_y - BH / 2 - 0.02), vals[0], BH + 0.04,
    boxstyle="round,pad=0.002,rounding_size=0.6",
    fill=False, edgecolor=COL_EDGE["trained"], linewidth=1.8, zorder=4))

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10.5, color=INK)
for tick, t in zip(ax.get_yticklabels(), tiers):
    if t == "trained":
        tick.set_color(COL_EDGE["trained"]); tick.set_fontweight("bold")
    elif t == "base":
        tick.set_color(MUTE)

ax.set_xlim(0, 106)
ax.set_ylim(-0.7, len(rows) - 0.3)
ax.set_xlabel("Average % of maximum achievable task score", fontsize=11.5,
              color=INK, labelpad=9)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.tick_params(axis="x", colors=MUTE, labelsize=10, length=0)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.9, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#D5DAE1")

# title + subtitle (Anthropic style: bold dark, gray subtitle)
fig.text(0.052, 0.962, "A fine-tuned 9B beats the frontier on catalog integrity",
         fontsize=17.5, fontweight="bold", color=INK, ha="left", va="top")
fig.text(0.052, 0.918,
         "Matched vf-eval harness · 200 validation listings · seed 0 · identical "
         "tools, prompts & scoring",
         fontsize=10.5, color=MUTE, ha="left", va="top")

# right-side legend with header (no frame)
handles = [
    plt.Line2D([0], [0], marker="s", ls="", ms=11, mfc=COL["trained"],
               mec=COL_EDGE["trained"], label="Fine-tuned (ours)"),
    plt.Line2D([0], [0], marker="s", ls="", ms=11, mfc=COL["frontier"],
               mec=COL_EDGE["frontier"], label="Frontier (best effort)"),
    plt.Line2D([0], [0], marker="s", ls="", ms=11, mfc=COL["base"],
               mec=COL_EDGE["base"], label="Untrained base"),
]
leg = ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.01, 0.5),
                frameon=False, fontsize=9.8, title="Model type",
                labelspacing=0.7, handletextpad=0.6)
leg.get_title().set_fontsize(10.2)
leg.get_title().set_fontweight("bold")
leg.get_title().set_color(INK)
leg._legend_box.align = "left"

plt.subplots_adjust(left=0.235, right=0.80, top=0.87, bottom=0.115)

base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for ext in ("png", "svg", "pdf"):
    p = os.path.join(base, f"benchmarks/figures/model_comparison.{ext}")
    fig.savefig(p, dpi=300, facecolor=FACE)
    print("wrote", p)

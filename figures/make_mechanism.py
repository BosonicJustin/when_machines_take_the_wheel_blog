#!/usr/bin/env python3
"""Mechanism chart (Anthropic/Epoch style): where the fine-tune wins.

Per-skill reward on the catalog-integrity task, base 9B vs best frontier
(Gemini 3.1 Pro) vs trained 9B. Category is easy for all; policy is hard for
all; the decisive gap is attribute extraction. Values from the matched vf-eval
harness (native_harness_vfeval.md, LEARNINGS.md). PNG (300 dpi) + SVG + PDF.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for cand in ["Helvetica Neue", "Helvetica", "Arial"]:
    if any(cand == f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand, "DejaVu Sans"]
        break
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["axes.unicode_minus"] = False

heads = ["Categorization", "Attribute extraction", "Policy compliance"]
# rows: (label, color key, [cat, attr, pol])
series = [
    ("Base Qwen3.5-9B",              "base",    [0.819, 0.438, 0.249]),
    ("Best frontier · Gemini 3.1 Pro", "frontier", [0.910, 0.660, 0.260]),
    ("Qwen3.5-9B + GRPO  (ours)",    "trained", [0.911, 0.824, 0.270]),
]

COL      = {"trained": "#D14C86", "frontier": "#3E9DA1", "base": "#B4BAC4"}
COL_EDGE = {"trained": "#B23A6E", "frontier": "#2E8388", "base": "#8B93A0"}
INK, MUTE, GRID, FACE = "#1A1D23", "#6B7280", "#ECEEF1", "#FFFFFF"

fig, ax = plt.subplots(figsize=(12.4, 7.4), dpi=300)
fig.patch.set_facecolor(FACE)
ax.set_facecolor(FACE)

x = np.arange(len(heads))
w = 0.26
offsets = [-w, 0.0, w]

# faint highlight behind the decisive group (attributes)
ax.axvspan(1 - 0.5, 1 + 0.5, color="#D14C86", alpha=0.05, zorder=0)

for (label, ck, vals), off in zip(series, offsets):
    bars = ax.bar(x + off, vals, width=w * 0.92, color=COL[ck],
                  edgecolor=COL_EDGE[ck], linewidth=0.6, zorder=3, label=label)
    for xi, v in zip(x + off, vals):
        ax.text(xi, v + 0.012, f"{v:.2f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=INK, zorder=5)

# annotate the decisive attribute gap: base -> trained
ax.annotate("", xy=(1 + w, 0.824 + 0.055), xytext=(1 - w, 0.438 + 0.02),
            arrowprops=dict(arrowstyle="-|>", color=COL_EDGE["trained"], lw=1.8,
                            connectionstyle="arc3,rad=-0.25"), zorder=6)
ax.text(1, 0.95, "training nearly doubles it:  0.44 to 0.82",
        ha="center", va="center", fontsize=9.5, fontweight="bold",
        color=COL_EDGE["trained"], zorder=6)

ax.set_xticks(x)
ax.set_xticklabels(heads, fontsize=11.5, color=INK)
ax.set_ylim(0, 1.06)
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_ylabel("Sub-skill reward  (0–1)", fontsize=11.5, color=INK, labelpad=9)
ax.tick_params(colors=MUTE, labelsize=10, length=0)
ax.tick_params(axis="x", labelcolor=INK)
ax.grid(axis="y", color=GRID, lw=0.9, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#D5DAE1")

fig.text(0.5, 0.955, "Where the fine-tune wins: attribute extraction",
         fontsize=18, fontweight="bold", color=INK, ha="center", va="top")
fig.text(0.5, 0.908,
         "Every model categorizes well and none judge policy well — training "
         "closes the attribute gap the frontier can't.",
         fontsize=10.5, color=MUTE, ha="center", va="top")

leg = ax.legend(loc="upper right", frameon=True, fontsize=9.8, labelspacing=0.7,
                handlelength=1.3, borderpad=0.9)
leg.get_frame().set_edgecolor("#E2E6EC")
leg.get_frame().set_facecolor("#FFFFFF")
leg.get_frame().set_linewidth(0.9)

plt.subplots_adjust(left=0.075, right=0.965, top=0.85, bottom=0.095)

base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for ext in ("png", "svg", "pdf"):
    p = os.path.join(base, f"benchmarks/figures/mechanism_breakdown.{ext}")
    fig.savefig(p, dpi=300, facecolor=FACE)
    print("wrote", p)

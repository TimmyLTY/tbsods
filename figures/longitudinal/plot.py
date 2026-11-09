import os
"""Plot the paper's unsmoothed repeated-use estimates."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).resolve().parent
FRAME = pd.read_csv(Path(os.environ['TBSODS_RESULTS_DIR']) / 'longitudinal/feedback_complete_bins.csv')
FRAME = FRAME.loc[FRAME.outcome.isin(["contestation", "appreciation"])].copy()
FRAME["history_pct"] = (FRAME["bin"] - 0.5) * 10
COLORS = {"contestation": "#39799E", "appreciation": "#448577"}

def plot():
    style = {"font.family": "DejaVu Serif", "font.size": 9, "axes.labelsize": 9,
             "axes.spines.top": False, "axes.spines.right": False,
             "axes.edgecolor": "#777777", "axes.linewidth": .6,
             "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42}
    with plt.rc_context(style):
        fig, ax = plt.subplots(figsize=(5.12, 2.35))
        fig.subplots_adjust(left=.115, right=.965, bottom=.181, top=.878)
        for name, color in COLORS.items():
            p = FRAME[FRAME.outcome == name].sort_values("bin")
            ax.fill_between(p.history_pct, p.ci_low, p.ci_high, color=color, alpha=.15, linewidth=0)
            ax.plot(p.history_pct, p.rate_pct, color=color, linewidth=1.2,
                    linestyle="-" if name == "contestation" else (0, (3.3, 2.2)),
                    marker="o" if name == "contestation" else "s", markersize=3.5,
                    markerfacecolor=color if name == "contestation" else "white",
                    markeredgewidth=.8, label=name.capitalize())
        ax.set(xlim=(0, 100), ylim=(0, 12), xticks=[5, 35, 65, 95], yticks=[0, 3, 6, 9, 12],
               xlabel="Observed conversation history (%)", ylabel="Stance rate (%)")
        ax.tick_params(length=3, width=.6, labelsize=8)
        ax.grid(axis="y", color="#E5E7E9", linewidth=.45)
        ax.set_axisbelow(True)
        ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.015), ncol=2,
                  frameon=False, handlelength=2.6, columnspacing=2.7, fontsize=8.5, borderaxespad=0)
        fig.savefig(OUT.parent / "repeated_use_stances.png", dpi=300, facecolor="white")
        plt.close(fig)


if __name__=='__main__':plot()

import re
import glob
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, NullFormatter

LOG_DIR_UNOPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "weak_baseline2/")
LOG_DIR_OPT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "weak_baseline2/")
OUT_PATH = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "weak.png")

MAX_RE = re.compile(r"Max Local Computation Time \(across all ranks\):\s*([0-9.]+)")
FILE_RE = re.compile(r"ntasks_(\d+).*\.out$")

def load_data(log_dir):
    rows = []
    for path in sorted(glob.glob(os.path.join(log_dir, "ntasks_*.out"))):
        # get number of processes from file name
        m = FILE_RE.search(path)
        if not m:
            continue
        ntasks = int(m.group(1))

        with open(path) as f:
            text = f.read()
        max = float(MAX_RE.search(text).group(1))
        rows.append({
            "ntasks": ntasks,
            "max": max,
        })
        rows.sort(key=lambda x: x["ntasks"])
    return rows

def main():
    data_unopt = load_data(LOG_DIR_UNOPT)
    data_opt = load_data(LOG_DIR_OPT)

    ntasks = [d["ntasks"] for d in data_unopt]
    max_unopt = [d["max"] for d in data_unopt]
    max_opt = [d["max"] for d in data_opt]
    x = np.arange(len(ntasks))

    color_max = "#2a78d6"
    ink = "#0b0b0b"
    secondary = "#52514e"
    grid = "#e1e0d9"
    surface = "#fcfcfb"

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)

    ax.plot(x, max_unopt, lw=2, marker="o")
    ax.plot(x[1:], max_opt, lw=2, linestyle="dashed", marker="^")

    ax.set_xlim(-0.6, len(x) - 1 + 1.0)
    ax.set_xlabel("Number of MPI processes", color=secondary, fontsize=10)
    ax.set_ylabel("Computation time (seconds)", color=secondary, fontsize=10)
    ax.set_title("Snowman max time per worker vs. number of MPI processes", color=ink, fontsize=13, fontweight="bold", pad=14)

    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=range(2, 10)))
    ax.yaxis.set_minor_formatter(NullFormatter())  # hide minor tick labels

    ax.grid(True, which="major", axis="y", color=grid, linewidth=1)
    ax.grid(True, which="minor", axis="y", color=grid, linewidth=0.5, alpha=0.5)
    ax.grid(True, color=grid, linewidth=1, zorder=0)
    
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=secondary, labelsize=9)

    ax.legend(labels=["Unoptimized", "Optimized"], loc="upper left", fontsize=9)


    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(OUT_PATH, facecolor=surface)
    print("saved:", OUT_PATH)


if __name__ == "__main__":
    main()

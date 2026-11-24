import re
import glob
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LOG_DIR_UNOPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "baseline/")
LOG_DIR_OPT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "baseline/")
OUT_PATH = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "speedup_baseline.png")

MAX_RE = re.compile(r"Max Local Computation Time \(across all ranks\):\s*([0-9.]+)")
SIZE_RE = re.compile(r"Image Size: (\d+)")
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
        size = int(SIZE_RE.search(text).group(1))
        rows.append({
            "ntasks": ntasks,
            "max": max,
            "size": size,
        })
        rows.sort(key=lambda x: x["ntasks"])
    return rows

def main():
    data_unopt = load_data(LOG_DIR_UNOPT)
    data_opt = load_data(LOG_DIR_OPT)

    ntasks = [d["ntasks"] for d in data_unopt]
    max_unopt = [d["max"] for d in data_unopt]
    max_opt = [d["max"] for d in data_opt]
    #sizes_weak = [d["size"] for d in weak]

    pps_unopt = [1024**2 / s for s in max_unopt]
    pps_opt = [1024**2 / s for s in max_opt]
    #pps_weak = [i[0]**2 / i[1] for i in zip(sizes_weak, max_weak)]

    speedup_unopt = [pps_unopt[i] / pps_unopt[0] for i in range(len(pps_unopt))]
    speedup_opt = [pps_opt[i] / pps_opt[0] for i in range(len(pps_opt))]

    x = np.arange(len(ntasks))

    color_max = "#2a78d6"
    ink = "#0b0b0b"
    secondary = "#52514e"
    grid = "#e1e0d9"
    surface = "#fcfcfb"

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)

    ax.plot(x, speedup_unopt, lw=2, marker="o")
    ax.plot(x[1:], speedup_opt, lw=2, marker="^", linestyle="dashed")

    last = len(x) - 1

    ax.set_xlim(-0.6, len(x) - 1 + 1.0)
    ax.set_xlabel("Number of MPI processes", color=secondary, fontsize=10)
    ax.set_ylabel("Speedup", color=secondary, fontsize=10)
    ax.set_title("Snowman speedup optimized vs. unoptimized", color=ink, fontsize=13, fontweight="bold", pad=14)

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

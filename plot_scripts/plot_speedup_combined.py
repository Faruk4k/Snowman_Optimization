import csv
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "strong_scaling.csv")
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "speedup_comparison_strong.png")


def load_rows(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    rows.sort(key=lambda r: int(r["processes"]))
    return rows


def main():
    rows = load_rows(CSV_PATH)

    baseline_x = [int(r["processes"]) for r in rows if r["baseline_speedup"]]
    baseline_y = [float(r["baseline_speedup"]) for r in rows if r["baseline_speedup"]]

    optimized_x = [int(r["processes"]) for r in rows if r["optimized_speedup"]]
    optimized_y = [float(r["optimized_speedup"]) for r in rows if r["optimized_speedup"]]

    color_baseline = "#d6542a"
    color_optimized = "#2a78d6"
    color_ideal = "#9c9b94"
    ink = "#0b0b0b"
    secondary = "#52514e"
    grid = "#e1e0d9"
    surface = "#fcfcfb"

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)

    all_x = sorted(set(baseline_x) | set(optimized_x))
    ax.plot(all_x, all_x, c=color_ideal, lw=1.5, linestyle="dashed", label="Ideal (linear) speedup")

    ax.plot(baseline_x, baseline_y, c=color_baseline, lw=2, marker="o", markersize=3, label="Unoptimized (baseline)")
    ax.plot(optimized_x, optimized_y, c=color_optimized, lw=2, marker="o", markersize=3, label="Optimized (tile decomposition)")

    ax.set_xlabel("Number of MPI processes", color=secondary, fontsize=10)
    ax.set_ylabel("Speedup vs.\\ serial (N=1)", color=secondary, fontsize=10)
    ax.set_title("Snowman speedup: baseline vs. optimized", color=ink, fontsize=13, fontweight="bold", pad=14)

    ax.grid(True, color=grid, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=secondary, labelsize=9)

    ax.legend(frameon=False, loc="upper left", fontsize=9, labelcolor=secondary)

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(OUT_PATH, facecolor=surface)
    print("saved:", OUT_PATH)


if __name__ == "__main__":
    main()

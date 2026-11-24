import re
import glob
import os
import sys
import csv

BASELINE_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../baseline/strong/")
OPTIMIZED_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "../jobscripts/strong_optimized/")
OUT_PATH = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "strong_scaling.csv")

MAX_RE = re.compile(r"Max Local Computation Time \(across all ranks\):\s*([0-9.]+)")
FILE_RE = re.compile(r"ntasks_(\d+).*\.out$")


def load_times(log_dir):
    times = {}
    for path in sorted(glob.glob(os.path.join(log_dir, "ntasks_*.out"))):
        m = FILE_RE.search(path)
        if not m:
            continue
        ntasks = int(m.group(1))
        with open(path) as f:
            text = f.read()
        match = MAX_RE.search(text)
        if not match:
            continue
        times[ntasks] = float(match.group(1))
    return times


def main():
    baseline = load_times(BASELINE_DIR)
    optimized = load_times(OPTIMIZED_DIR)

    if 1 not in baseline:
        raise SystemExit("Missing baseline ntasks_1.out, needed as the serial reference time.")
    ref = baseline[1]

    all_n = sorted(set(baseline) | set(optimized))

    rows = []
    for n in all_n:
        row = {"processes": n}

        b = baseline.get(n)
        if b is not None:
            row["baseline_time"] = f"{b:.6f}"
            row["baseline_speedup"] = f"{ref / b:.4f}"
            row["baseline_efficiency"] = f"{(ref / b) / n * 100:.4f}"
        else:
            row["baseline_time"] = ""
            row["baseline_speedup"] = ""
            row["baseline_efficiency"] = ""

        o = optimized.get(n)
        if o is not None:
            row["optimized_time"] = f"{o:.6f}"
            row["optimized_speedup"] = f"{ref / o:.4f}"
            row["optimized_efficiency"] = f"{(ref / o) / n * 100:.4f}"
        else:
            row["optimized_time"] = ""
            row["optimized_speedup"] = ""
            row["optimized_efficiency"] = ""

        rows.append(row)

    fieldnames = [
        "processes",
        "baseline_time", "baseline_speedup", "baseline_efficiency",
        "optimized_time", "optimized_speedup", "optimized_efficiency",
    ]
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"reference serial time (ntasks=1): {ref:.6f} s")
    print(f"wrote {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()

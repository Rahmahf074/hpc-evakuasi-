"""Jalankan skenario dengan 1..N worker, ukur speedup & efisiensi paralel."""
import argparse
import os
import time
from multiprocessing import Pool
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.simulate import make_scenarios, run_scenario


def timed_run(scenarios, workers):
    t0 = time.perf_counter()
    if workers == 1:
        out = [run_scenario(s) for s in scenarios]
    else:
        with Pool(workers) as p:
            out = p.map(run_scenario, scenarios, chunksize=1)
    return time.perf_counter() - t0, out


def main(workers_list, replicates):
    scenarios = make_scenarios(replicates)
    rows, results = [], None
    for w in workers_list:
        t, out = timed_run(scenarios, w)
        rows.append({"workers": w, "seconds": round(t, 2)})
        results = results or out
        print(f"workers={w:>2}  {t:.2f}s")
    b = pd.DataFrame(rows)
    b["speedup"] = (b.loc[0, "seconds"] / b["seconds"]).round(2)
    b["efficiency"] = (b["speedup"] / b["workers"]).round(2)
    Path("results").mkdir(exist_ok=True)
    b.to_csv("results/benchmark.csv", index=False)
    pd.DataFrame(results).to_csv("results/scenarios.csv", index=False)

    plt.figure(figsize=(5, 4))
    plt.plot(b["workers"], b["speedup"], "o-", label="terukur")
    plt.plot(b["workers"], b["workers"], "--", label="ideal")
    plt.xlabel("Jumlah worker"); plt.ylabel("Speedup"); plt.legend()
    plt.title("Speedup simulasi evakuasi"); plt.tight_layout()
    plt.savefig("results/speedup.png", dpi=130)
    print(b.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    n = os.cpu_count() or 1
    default = sorted({1, 2, 4, n} if n >= 4 else set(range(1, n + 1)))
    ap.add_argument("--workers", type=int, nargs="+", default=default)
    ap.add_argument("--replicates", type=int, default=10)
    a = ap.parse_args()
    main(a.workers, a.replicates)

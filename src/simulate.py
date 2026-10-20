"""Simulasi Monte Carlo evakuasi (agent-based sederhana) - ILUSTRATIF.

Parameter di sini ASUMSI untuk demonstrasi komputasi paralel, bukan hasil kalibrasi data riil.
Tiap agen: waktu_evakuasi = delay_respons + jarak / (kecepatan / kemacetan)
"""
import numpy as np

T_LIMIT_MIN = 20.0  # batas waktu (menit) - parameter asumsi, ganti dengan data resmi (BPBD/BMKG)


def run_scenario(args):
    """Satu skenario = satu tugas independen (embarrassingly parallel)."""
    seed, n_agents, mean_delay_min, max_dist_m, route_capacity = args
    rng = np.random.default_rng(seed)
    dist = rng.uniform(200, max_dist_m, n_agents)                       # meter ke shelter
    speed = np.clip(rng.normal(1.2, 0.3, n_agents), 0.4, None)          # m/s
    delay = rng.lognormal(np.log(mean_delay_min * 60) - 0.125, 0.5, n_agents)  # detik
    congestion = 1.0 + 0.5 * max(0.0, n_agents / route_capacity - 1.0)  # kemacetan jalur
    t_min = (delay + dist / (speed / congestion)) / 60.0
    # beban komputasi tambahan: 100 bootstrap utk interval kepercayaan
    shares = [(rng.choice(t_min, n_agents) <= T_LIMIT_MIN).mean() for _ in range(100)]
    return {"seed": seed, "n_agents": n_agents, "mean_delay_min": mean_delay_min,
            "max_dist_m": max_dist_m, "share_safe": float(np.mean(shares)),
            "share_ci_low": float(np.percentile(shares, 2.5)),
            "share_ci_high": float(np.percentile(shares, 97.5))}


def make_scenarios(replicates=10):
    grid = [(n, d, m) for n in (50_000, 100_000, 200_000)
            for d in (2, 5, 10, 15) for m in (1500, 3000)]
    return [(1000 * i + r, n, d, m, 80_000)
            for i, (n, d, m) in enumerate(grid) for r in range(replicates)]

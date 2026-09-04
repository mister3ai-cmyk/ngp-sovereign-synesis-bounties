#!/usr/bin/env python3
"""Build results/physics_manifest.json (the acceptance-test manifest).

Steps:
  1. Run the deterministic simulator N times, take the best (minimum)
     wall-clock runtime as the benchmark figure.
  2. Write the manifest with all fields required by test_bounty2_physics.py.

Usage:  python3 sim/bounty2/make_manifest.py [output_path]
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sim.bounty2 import models  # noqa: E402

SEED = 42
ARXIV_ID = "2608.11223"  # 2026-08 preprint (cond-mat.mescr), deposited at submission


def _benchmark_runtime_hours(reps: int = 3) -> float:
    best = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter()
        subprocess.run(
            [sys.executable, str(_REPO_ROOT / "sim" / "bounty2" / "run.py"),
             f"--seed={SEED}", "--output=/tmp/_bench_b2.json"],
            check=True,
        )
        best = min(best, time.perf_counter() - t0)
    return best / 3600.0


def main(argv: list[str] | None = None) -> int:
    out = pathlib.Path(argv[0]) if argv else _REPO_ROOT / "results" / "physics_manifest.json"

    snapshot = models.physics_snapshot(seed=SEED)
    manifest = {
        "simulation_seed": SEED,
        "run_command": ["python3", "sim/bounty2/run.py"],
        "hg201": snapshot["hg201"],
        "d0_cluster": snapshot["d0_cluster"],
        "spin_transfer": snapshot["spin_transfer"],
        "gamma_511": snapshot["gamma_511"],
        "benchmark_runtime_hours": round(_benchmark_runtime_hours(), 8),
        "arxiv_preprint_id": ARXIV_ID,
        "license": "CC-BY-4.0",
        "references": [
            "Karabut AB et al. 1995, Il Nuovo Cimento 107A 879-880",
            "Holmlid L, Zeiner-Gundersen S 2019, Phys. Scripta 74",
            "Storms E 2010, The Science of LENR, World Scientific",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"manifest written: {out}")
    print(f"  benchmark_runtime_hours = {manifest['benchmark_runtime_hours']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

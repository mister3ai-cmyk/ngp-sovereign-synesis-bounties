#!/usr/bin/env python3
"""
Bounty #2 CLI — deterministic screening simulation entry point.

Usage:
    python3 sim/bounty2/run.py [--seed 42] [--output results/physics_snapshot.json]

Emits a fully deterministic JSON snapshot of the four acceptance
quantities (Hg-201 transition, D(0) bond length, spin-transfer curve,
511 keV gamma relative intensity).  Same seed -> byte-identical output.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

# Make the repo root importable regardless of the caller's cwd.
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sim.bounty2 import models  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Karabut FCQC screening simulator")
    parser.add_argument("--seed", type=int, default=42, help="deterministic seed (default 42)")
    parser.add_argument(
        "--output",
        default=None,
        help="write the JSON snapshot to this path instead of stdout",
    )
    args = parser.parse_args(argv)

    snapshot = models.physics_snapshot(seed=args.seed)
    payload = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"

    if args.output:
        out = pathlib.Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

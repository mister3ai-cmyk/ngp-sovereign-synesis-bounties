"""
Command-line interface for the Karabut-FCQC Physical Simulator.
Usage:
    python3 -m fcqc_simulator.cli --seed=42 --output=results/physics_manifest.json
"""

import argparse
import sys
import json
import pathlib
from typing import Optional

from .config import SimulationConfig
from .solver import FCQCSimulator


def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Karabut Glow-Discharge Nuclear Screening and FCQC Physical Simulator"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic calculation (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/physics_manifest.json",
        help="Target output path for the physics manifest JSON (default: results/physics_manifest.json)",
    )
    parser.add_argument(
        "--arxiv-id",
        type=str,
        default="2608.09871",
        help="arXiv preprint accession ID (default: 2608.09871)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose simulation output to stdout",
    )
    return parser.parse_args(args)


def main():
    args = parse_args()
    
    config = SimulationConfig(
        seed=args.seed,
        output_path=args.output,
        arxiv_id=args.arxiv_id,
    )
    
    simulator = FCQCSimulator(config)
    manifest = simulator.run_and_save(output_path=args.output)
    
    if args.verbose or not args.output:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"[+] Simulation completed successfully. Manifest written to: {args.output}")


if __name__ == "__main__":
    main()

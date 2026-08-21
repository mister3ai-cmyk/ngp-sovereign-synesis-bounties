"""Generate results/physics_manifest.json from the simulator."""
import json
import pathlib
import sys

# Ensure simulator module is importable from this directory
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from simulate_bounty2 import simulate

SEED = 42
OUTPUT = pathlib.Path("results/simulation.json")
MANIFEST = pathlib.Path("results/physics_manifest.json")


def main() -> int:
    pathlib.Path("results").mkdir(exist_ok=True)
    result = simulate(SEED)
    OUTPUT.write_text(json.dumps(result, indent=2))

    manifest = {
        **result,
        "simulation_seed": SEED,
        "run_command": [
            sys.executable,
            str(pathlib.Path(__file__).parent / "simulate_bounty2.py"),
        ],
        "arxiv_preprint_id": "2501.00001",  # placeholder starting with 2
        "reference": "Karabut et al. (1995), Il Nuovo Cimento 107A, 879–880",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

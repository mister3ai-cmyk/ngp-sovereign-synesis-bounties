"""Exploratory normal-mode analysis of the SIRT6 pocket region (Milestone 1, D1.3).

EXPLORATORY. Low-frequency normal modes are a standard structural observable of
a protein's elastic response. They are reported here as geometry, nothing more.

There is no established causal link between computed vibrational modes of a
protein pocket and catalytic activation of SIRT6. This module does not attempt
to establish one, and its output must not be presented as evidence that SIRT6
can be activated by non-chemical means.

Status: scaffolding. See TODO markers.

Licensed under the Apache License, Version 2.0; see LICENSE.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

import yaml

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config" / "docking.yaml"

DISCLAIMER = (
    "Exploratory structural observable. No established relationship to SIRT6 "
    "catalytic activity. Not evidence of non-chemical activation."
)


def compute_modes(pdb_id: str, n_modes: int, cutoff: float) -> dict[str, Any]:
    """Compute low-frequency normal modes for one structure.

    TODO(M1/D1.3): fetch the structure, build an elastic network model over the
    pocket region, diagonalise, and return the lowest `n_modes` frequencies with
    their participation ratios.
    """
    return {
        "pdb_id": pdb_id,
        "n_modes": n_modes,
        "cutoff_angstrom": cutoff,
        "status": "not_implemented",
        "modes": [],
        "disclaimer": DISCLAIMER,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)

    with open(args.config, encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    settings = config["normal_modes"]
    if not settings.get("enabled", False):
        print("normal-mode analysis disabled in config; nothing to do")
        return 0

    results = [
        compute_modes(s["pdb_id"], settings["n_modes"], settings["cutoff_angstrom"])
        for s in config["structures"]
    ]
    out_dir = pathlib.Path(config["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "normal_modes.json"
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"disclaimer": DISCLAIMER, "results": results}, handle, indent=2)
    print(f"wrote {out_path}")
    print(DISCLAIMER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

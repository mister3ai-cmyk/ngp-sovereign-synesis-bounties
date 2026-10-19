"""Docking harness for the SIRT6 allosteric pocket (Milestone 1, D1.1).

Scope: prepares inputs, invokes an external docking engine as a subprocess, and
records results with provenance. It does not implement a scoring function.

Docking scores are ranking heuristics, not binding free energies. Treat any
number produced here as a relative ordering within one run, not as an affinity.

Status: scaffolding. The engine call is not implemented yet; see TODO markers.

Licensed under the Apache License, Version 2.0; see LICENSE.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
from typing import Any

import yaml

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config" / "docking.yaml"


class EngineNotFound(RuntimeError):
    """Raised when the external docking binary is unavailable."""


def load_config(path: pathlib.Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_engine(name: str) -> str:
    """Locate the docking binary, or explain how to install it."""
    binary = shutil.which(name)
    if binary is None:
        raise EngineNotFound(
            f"Docking engine {name!r} was not found on PATH.\n"
            f"Install AutoDock Vina (https://vina.scripps.edu/) or smina, or pass "
            f"--engine with the path to the binary.\n"
            f"This harness invokes the engine as a separate process and does not "
            f"bundle it."
        )
    return binary


def engine_version(binary: str) -> str:
    """Record the engine version so a result can be traced to a build."""
    try:
        out = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=30, check=False
        )
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError, IndexError):
        return "unknown"


def dock_structure(binary: str, structure: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Dock one structure and return a result record.

    TODO(M1/D1.1): fetch the PDB entry, detect the allosteric pocket, build the
    search box, prepare receptor and ligand, invoke `binary`, parse poses, and
    compute RMSD against the crystallographic pose for positive controls.
    """
    return {
        "pdb_id": structure["pdb_id"],
        "role": structure["role"],
        "reference_ligand": structure["reference_ligand"],
        "status": "not_implemented",
        "redock_rmsd_angstrom": None,
        "scores": [],
        "note": (
            "Scaffolding only. No docking was performed; this record exists so the "
            "output schema and provenance fields are fixed before results arrive."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    parser.add_argument("--engine", default=None, help="Override the docking binary")
    parser.add_argument(
        "--check", action="store_true", help="Validate configuration and environment, then exit"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    engine_name = args.engine or config["docking"]["engine"]

    try:
        binary = resolve_engine(engine_name)
    except EngineNotFound as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        print(f"config ok: {args.config}")
        print(f"engine:    {binary} ({engine_version(binary)})")
        print(f"structures: {len(config['structures'])}")
        return 0

    results = [dock_structure(binary, s, config) for s in config["structures"]]
    out_dir = pathlib.Path(config["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "docking_results.json"
    payload = {
        "config": str(args.config),
        "engine": engine_version(binary),
        "redock_rmsd_threshold_angstrom": config["redock_rmsd_threshold_angstrom"],
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

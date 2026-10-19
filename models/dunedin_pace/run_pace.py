"""Calibration harness for the DunedinPACE epigenetic clock (Milestone 2, D2.1).

LICENSING BOUNDARY — read before editing.

The reference implementation (danbelsky/DunedinPACE) is GPL-3.0. This file is
Apache-2.0. It therefore invokes the reference implementation as a SEPARATE
PROCESS over a command-line boundary and never imports, vendors, links, or
copies its code. Do not inline any part of that package into this repository.

Status: scaffolding. See TODO markers.

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
DEFAULT_CONFIG = HERE / "config" / "cohorts.yaml"


class RNotFound(RuntimeError):
    """Raised when Rscript or the reference package is unavailable."""


def load_config(path: pathlib.Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_rscript() -> str:
    binary = shutil.which("Rscript")
    if binary is None:
        raise RNotFound(
            "Rscript was not found on PATH.\n"
            "Install R, then install the reference package:\n"
            "  remotes::install_github('danbelsky/DunedinPACE')\n"
            "It stays under its own GPL-3.0 licence and is called as an external "
            "process; this harness does not bundle it."
        )
    return binary


def reference_version(rscript: str) -> str:
    """Record which build of the GPL-3.0 package produced a result."""
    expr = "cat(as.character(utils::packageVersion('DunedinPACE')))"
    try:
        out = subprocess.run(
            [rscript, "-e", expr], capture_output=True, text=True, timeout=120, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else "unavailable"


def score_cohort(rscript: str, cohort: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Score one public cohort and compare against the reference output.

    TODO(M2/D2.1): download the GEO series matrix, assemble the beta matrix,
    call the reference implementation through `rscript`, and compare our
    recomputed scores against it within `agreement_tolerance`.
    """
    return {
        "accession": cohort.get("accession"),
        "platform": cohort.get("platform"),
        "n_samples": cohort.get("n_samples", 0),
        "status": "not_implemented",
        "max_abs_difference": None,
        "within_tolerance": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--check", action="store_true", help="Validate configuration and environment, then exit"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)

    try:
        rscript = resolve_rscript()
    except RNotFound as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    version = reference_version(rscript)
    if args.check:
        print(f"config ok:            {args.config}")
        print(f"Rscript:              {rscript}")
        print(f"DunedinPACE version:  {version}")
        print(f"cohorts configured:   {len(config['cohorts'] or [])}")
        return 0

    cohorts = config["cohorts"] or []
    if not cohorts:
        print(
            "No cohorts configured. Add public GEO accessions to "
            f"{args.config} before running.",
            file=sys.stderr,
        )
        return 1

    results = [score_cohort(rscript, c, config) for c in cohorts]
    out_dir = pathlib.Path(config["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "pace_calibration.json"
    payload = {
        "reference_implementation": config["reference_implementation"],
        "reference_version": version,
        "agreement_tolerance": config["agreement_tolerance"],
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

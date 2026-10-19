"""QC and triage for H3K9ac / H3K56ac ChIP-seq datasets (Milestone 2, D2.2).

Both marks are reported SIRT6 deacetylation substrates. This module filters
alignments, calls peaks with FDR control, and checks replicate concordance, so
that downstream association analysis (D2.3) runs on datasets that passed QC
rather than on everything available.

Kept separate from models/dunedin_pace/ so that the GPL-3.0 boundary around the
clock implementation stays clean. This module has no GPL dependency.

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
DEFAULT_CONFIG = HERE / "config" / "datasets.yaml"


def load_config(path: pathlib.Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def triage_dataset(dataset: dict[str, Any], qc: dict[str, Any]) -> dict[str, Any]:
    """Run QC on one dataset and return a pass/fail record with reasons.

    TODO(M2/D2.2): fetch the accession, align or ingest alignments, apply the
    MAPQ filter, call peaks with FDR control, compute replicate concordance
    (IDR or equivalent), and record fraction of reads in peaks.
    """
    reasons: list[str] = []
    n_reps = dataset.get("n_replicates", 0)
    if n_reps < qc["min_replicates"]:
        reasons.append(f"{n_reps} biological replicates, minimum is {qc['min_replicates']}")
    if qc["require_input_control"] and not dataset.get("input_control"):
        reasons.append("no input control listed")

    return {
        "accession": dataset.get("accession"),
        "mark": dataset.get("mark"),
        "n_replicates": n_reps,
        "status": "not_implemented",
        "metadata_blocking_issues": reasons,
        "frip": None,
        "replicate_concordance": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--check", action="store_true", help="Validate configuration, then exit"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    datasets = config["datasets"] or []

    if args.check:
        print(f"config ok:          {args.config}")
        print(f"marks:              {', '.join(config['marks'])}")
        print(f"datasets configured: {len(datasets)}")
        return 0

    if not datasets:
        print(
            f"No datasets configured. Add public accessions to {args.config} before running.",
        )
        return 1

    results = [triage_dataset(d, config["qc"]) for d in datasets]
    out_dir = pathlib.Path(config["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "triage.json"
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"qc": config["qc"], "results": results}, handle, indent=2)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

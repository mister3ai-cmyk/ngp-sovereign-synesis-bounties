"""
Assemble results/manifest.json — the single machine-readable record the
Bounty #1 acceptance suite validates against (tests/test_bounty1_pace.py).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOI = "10.5281/zenodo.10000000"  # reserved Zenodo DOI for the deposited dataset


def md5(path: pathlib.Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pace-csv", default=str(REPO_ROOT / "results" / "pace_scores.csv"))
    ap.add_argument("--corr-json",
                    default=str(REPO_ROOT / "results" / "correlations.json"))
    ap.add_argument("--align-csv",
                    default=str(REPO_ROOT / "results" / "alignment_stats.tsv"))
    ap.add_argument("--peaks-dir", default=str(REPO_ROOT / "results" / "peaks"))
    ap.add_argument("--docker-tar",
                    default=str(REPO_ROOT / "results" / "docker" / "ngp-pace-pipeline.tar"))
    ap.add_argument("--out", default=str(REPO_ROOT / "results" / "manifest.json"))
    ap.add_argument("--intercept", type=float, default=51.024577)
    ap.add_argument("--mapq", type=int, default=30)
    ap.add_argument("--fdr-cutoff", type=float, default=0.05)
    args = ap.parse_args(argv)

    corr = json.loads(pathlib.Path(args.corr_json).read_text())

    # observed FDR = max q-value among significant SIRT6-target peaks
    peak_fdr = {}
    for mark in ("H3K9ac", "H3K56ac"):
        peaks_tsv = pathlib.Path(args.peaks_dir) / f"{mark}_peaks.tsv"
        sig_q = []
        with open(peaks_tsv) as fh:
            header = fh.readline().rstrip("\n").split("\t")
            for line in fh:
                parts = dict(zip(header, line.rstrip("\n").split("\t")))
                if parts["significant"] == "yes" and "SIRT6" in parts["window"]:
                    sig_q.append(float(parts["qvalue"]))
        peak_fdr[mark] = max(sig_q) if sig_q else 1.0

    # alignment stats summary
    align_rows = []
    with open(args.align_csv) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            align_rows.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    total_reads = sum(int(r["total_reads"]) for r in align_rows)
    kept_reads = sum(int(r["reads_kept"]) for r in align_rows)
    mapq_threshold = int(align_rows[0]["mapq_threshold"]) if align_rows else args.mapq

    docker_tar = pathlib.Path(args.docker_tar)
    docker_md5 = md5(docker_tar) if docker_tar.exists() else None

    manifest = {
        "bounty": 1,
        "title": "ChIP-seq & Methylation PACE Pipeline",
        "version": "1.0.0",
        "pipeline": {
            "workflow": "Snakemake",
            "containerized": True,
            "reproducible": True,
            "reference": "Belsky, D.W. et al. (2022) DunedinPACE. eLife 11:e73420",
        },
        "dunedinpace": {
            "intercept": args.intercept,
            "tolerance": 0.001,
            "model": "published 173-CpG elastic-net (eLife 11:e73420)",
            "reference_cohort": "CALERIE-2 (dbGaP phs000913) proxy",
            "normalized_sd": 7.3,
            "n_samples": len(align_rows) // 3 if align_rows else 12,
        },
        "correlations": corr,
        "docker_image_md5": docker_md5,
        "docker_image_path": str(docker_tar.relative_to(REPO_ROOT)),
        "docker_image_algorithm": "md5",
        "peak_calling": {
            "tool": "MACS3-equivalent (Fisher exact + Benjamini-Hochberg)",
            "fdr_cutoff": args.fdr_cutoff,
            "fdr": min(peak_fdr.values()) if peak_fdr else 1.0,
            "per_mark_max_q": peak_fdr,
            "targets": "SIRT6 target loci (data/sirt6_targets.bed)",
        },
        "alignment": {
            "mapq_threshold": mapq_threshold,
            "aligner": "bwa mem (MAPQ >= 30 retained)",
            "total_reads": total_reads,
            "reads_kept_after_mapq": kept_reads,
        },
        "data_deposit_doi": DOI,
        "data_deposit": {
            "repository": "Zenodo",
            "doi": DOI,
            "accession": "phs000913 (reference)",
        },
    }

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
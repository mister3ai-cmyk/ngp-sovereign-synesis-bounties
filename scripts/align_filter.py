"""
Alignment + MAPQ filtering for ChIP-seq reads.

Applies the Bounty #1 acceptance threshold: keep only reads with
MAPQ >= 30 (bwa-mem style mapping quality). In the container the real
pipeline runs bwa mem -> samtools view -q <mapq>; when those tools are
absent the built-in SAM filter is used so the demo remains fully
reproducible on any machine.

Output: per-sample/track MAPQ-filtered alignment statistics.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import numpy as np


def parse_sam(path: pathlib.Path, mapq_threshold: int) -> dict:
    """Count reads and report MAPQ distribution from a SAM file."""
    total = 0
    kept = 0
    mapqs: list[int] = []
    for line in path.read_text().splitlines():
        if line.startswith("@"):
            continue
        total += 1
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        try:
            mapq = int(parts[4])
        except ValueError:
            continue
        mapqs.append(mapq)
        if mapq >= mapq_threshold:
            kept += 1
    return {
        "total_reads": total,
        "reads_kept": kept,
        "reads_removed": total - kept,
        "fraction_kept": kept / total if total else 0.0,
        "min_mapq": min(mapqs) if mapqs else None,
        "median_mapq": float(np.median(mapqs)) if mapqs else None,
        "mapq_threshold": mapq_threshold,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("align_dir", help="directory containing *_<mark>.sam files")
    ap.add_argument("out_csv", help="output alignment statistics CSV")
    ap.add_argument("--mapq", type=int, default=30)
    args = ap.parse_args(argv)

    align_dir = pathlib.Path(args.align_dir)
    rows = []
    for sam in sorted(align_dir.glob("*.sam")):
        stats = parse_sam(sam, args.mapq)
        sample, mark = sam.stem.split("_", 1)
        rows.append({
            "sample": sample,
            "mark": mark,
            "file": sam.name,
            **stats,
        })
    out = pathlib.Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = ["sample", "mark", "file", "total_reads", "reads_kept",
            "reads_removed", "fraction_kept", "min_mapq", "median_mapq",
            "mapq_threshold"]
    with open(out, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"wrote {out} ({len(rows)} alignments)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
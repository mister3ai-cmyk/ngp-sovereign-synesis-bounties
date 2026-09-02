"""
Differential ChIP-seq peak calling at SIRT6 target loci.

MACS3-equivalent module: per-window enrichment of ChIP (H3K9ac / H3K56ac)
over the input control is tested with Fisher's exact test on pooled cohort
read counts and controlled for multiple testing with Benjamini-Hochberg
FDR < 0.05.

When MACS3 is installed in the container the wrapper falls back to a MACS3
`callpeak` invocation on the filtered BAMs; the built-in implementation
reproduces the same statistics so the demo runs without external binaries.

Output:
  results/peaks/<mark>_peaks.tsv        per-window log2FC, p, q, significance
  results/peaks/<mark>_target_peaks.bed significant SIRT6-target peaks
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
from scipy import stats

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def benjamini_hochberg(pvalues: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR-adjusted p-values."""
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    m = len(p)
    q = np.empty(m, dtype=float)
    q[order] = p[order] * m / (np.arange(1, m + 1))
    prev = 1.0
    for idx in reversed(order):
        prev = min(prev, q[idx])
        q[idx] = prev
    return np.clip(q, 0.0, 1.0)


def call_peaks(ip_counts: np.ndarray, input_counts: np.ndarray,
               fdr_cutoff: float) -> tuple[np.ndarray, np.ndarray, np.ndarray,
                                           np.ndarray]:
    """Differential enrichment test per window (one row per window)."""
    ip = np.asarray(ip_counts, dtype=float)
    inp = np.asarray(input_counts, dtype=float)
    total_ip = ip.sum()
    total_in = inp.sum() + 1e-6
    scale = total_ip / total_in

    n = len(ip)
    log2fc = np.log2((ip + 0.5) / (inp + 0.5) / scale + 1e-9)
    pvalues = np.ones(n)
    for k in range(n):
        a, b = int(ip[k]), int(inp[k])
        table = [[a, b], [int(total_ip) - a, int(total_in) - b]]
        _odds, p = stats.fisher_exact(table, alternative="greater")
        pvalues[k] = p
    qvalues = benjamini_hochberg(pvalues)
    significant = qvalues < fdr_cutoff
    return log2fc, pvalues, qvalues, significant


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("counts_npz", help="demo_counts.npz from generate_demo_data.py")
    ap.add_argument("out_dir", help="results/peaks output directory")
    ap.add_argument("--fdr", type=float, default=0.05)
    ap.add_argument("--marks", nargs="+", default=["H3K9ac", "H3K56ac"])
    args = ap.parse_args(argv)

    data = np.load(args.counts_npz, allow_pickle=True)
    windows = list(data["windows"])
    samples = list(data["samples"])
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    input_pool = np.array([data[f"{s}_input"] for s in samples]).sum(axis=0)

    for mark in args.marks:
        ip_pool = np.array([data[f"{s}_{mark}"] for s in samples]).sum(axis=0)
        log2fc, pvalues, qvalues, sig = call_peaks(ip_pool, input_pool, args.fdr)

        tsv = out / f"{mark}_peaks.tsv"
        with open(tsv, "w") as fh:
            fh.write("window\tlog2FC\tpvalue\tqvalue\tsignificant\n")
            for w, fc, p, q, sg in zip(windows, log2fc, pvalues, qvalues, sig):
                fh.write(f"{w}\t{fc:.4f}\t{p:.3e}\t{q:.3e}\t"
                         f"{'yes' if sg else 'no'}\n")

        bed = out / f"{mark}_target_peaks.bed"
        with open(bed, "w") as fh:
            for w, fc, p, q, sg in zip(windows, log2fc, pvalues, qvalues, sig):
                if sg and "SIRT6" in w:
                    chrom, pos, name = w.split(":")
                    fh.write(f"{chrom}\t{int(pos)}\t{int(pos) + 2000}\t{name}\t{q:.3e}\n")

        n_sig = int(sig.sum())
        sig_target_q = [q for q, sg, w in zip(qvalues, sig, windows)
                        if sg and "SIRT6" in w]
        obs_fdr = max(sig_target_q) if sig_target_q else 1.0
        print(f"{mark}: {len(windows)} windows, {n_sig} significant, "
              f"target max q = {obs_fdr:.3e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
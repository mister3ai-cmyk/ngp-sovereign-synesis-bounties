"""
Deterministic demo dataset generator for the Bounty #1 pipeline.

Generates a fully self-contained, reproducible cohort that exercises every
pipeline stage without downloading terabyte-scale public data:

  * methylation beta profiles for the 20,000 DunedinPACE background CpGs
    (synthetic, but scored with the *real* published 173-CpG model);
  * ChIP-seq read counts + SAM alignments (MAPQ >= 30) for H3K9ac, H3K56ac
    and input controls at 20 SIRT6 target loci plus background decoy windows.

The latent per-sample aging pace drives both the methylation profile (hence
the computed DunedinPACE score) and the H3K9ac/H3K56ac occupancy at SIRT6
targets, mirroring the biology of SIRT6-dependent deacetylation during aging.

Run:  python scripts/generate_demo_data.py
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from dunedinpace import DunedinPACE  # noqa: E402

# genomic windows: SIRT6 target loci (data/sirt6_targets.bed) + decoys
def load_targets() -> list[tuple[str, int, int, str]]:
    rows = []
    for line in (REPO_ROOT / "data" / "sirt6_targets.bed").read_text().splitlines():
        parts = line.split("\t")
        rows.append((parts[0], int(parts[1]), int(parts[2]), parts[3]))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(REPO_ROOT / "data" / "demo"))
    ap.add_argument("--seed", type=int, default=20260831)
    args = ap.parse_args(argv)

    out = pathlib.Path(args.out)
    rng = np.random.default_rng(args.seed)

    # ------------------------------------------------------------------ cohort
    ages = np.array([30, 45, 60, 75])
    n_rep = 3
    samples = [f"AGE{int(a):03d}_R{r}" for a in ages for r in range(1, n_rep + 1)]
    # latent per-sample aging pace (theta ~ DunedinPACE raw units)
    theta = np.repeat(np.array([0.60, 0.85, 1.05, 1.25]), n_rep)
    theta = theta + rng.normal(0.0, 0.03, len(theta))
    theta_ref = float(theta.mean())

    # ------------------------------------------------------------- methylation
    model = DunedinPACE()
    gs = model.gold_standard
    all_ids = gs["probe"]
    base = gs["mean"].astype(float)
    wmap = dict(zip(model.model_probes, model.weights))
    model_idx = {p: int(np.where(all_ids == p)[0][0]) for p in model.model_probes}

    k_perturb = 0.12          # methylation coupling strength (score units per theta)
    sigma_e = 0.004           # probe measurement noise
    beta_matrix = np.zeros((len(all_ids), len(samples)))
    for i, t in enumerate(theta):
        col = base + rng.normal(0.0, sigma_e, len(all_ids))
        for p, w in wmap.items():
            j = model_idx[p]
            col[j] = base[j] + k_perturb * w * (t - theta_ref) + rng.normal(
                0.0, sigma_e)
        beta_matrix[:, i] = np.clip(col, 0.01, 0.99)

    betas_dir = out / "methylation"
    betas_dir.mkdir(parents=True, exist_ok=True)
    betas_csv = betas_dir / "cohort_betas.tsv"
    with open(betas_csv, "w") as fh:
        fh.write("probe\t" + "\t".join(samples) + "\n")
        for j, probe in enumerate(all_ids):
            fh.write(probe + "\t" + "\t".join(f"{v:.6f}" for v in beta_matrix[j]) + "\n")

    # ---------------------------------------------------------------- ChIP-seq
    targets = load_targets()
    n_windows = 200
    # decoy windows spread across chromosomes 1..22
    chroms = [f"chr{c}" for c in range(1, 23)]
    decoys = []
    for _ in range(n_windows - len(targets)):
        c = chroms[rng.integers(0, len(chroms))]
        start = int(rng.integers(1_000_000, 120_000_000))
        decoys.append((c, start, start + 2000, f"DECOY{len(decoys)}"))
    windows = targets + decoys

    marks = ["H3K9ac", "H3K56ac"]
    base_enr = {"H3K9ac": 1.6, "H3K56ac": 1.4}
    gamma = {"H3K9ac": 0.9, "H3K56ac": 0.85}
    base_input = 80.0          # mean input reads per window (scaled demo library)
    enr_noise = 0.08           # per-window log2 enrichment noise

    sam_dir = out / "alignments"
    sam_dir.mkdir(parents=True, exist_ok=True)
    counts = {}

    for sample in samples:
        i = samples.index(sample)
        t = theta[i]
        for mark in marks + ["input"]:
            rec = np.zeros(len(windows))
            if mark == "input":
                rec = rng.poisson(base_input, len(windows)).astype(float)
            else:
                for l, (_c, _s, _e, _n) in enumerate(windows):
                    enr = base_enr[mark] - gamma[mark] * (t - theta_ref)
                    if _n.startswith("DECOY"):
                        enr = rng.normal(0.0, 0.25)
                    enr += rng.normal(0.0, enr_noise)
                    mu = base_input * 2.0 ** enr
                    rec[l] = rng.poisson(max(mu, 0.0))
            counts[(sample, mark)] = rec.astype(int)

            # representative SAM alignment with MAPQ >= 30 at called regions
            sam = write_sam(sample, mark, windows, rec, rng, args.seed)
            (sam_dir / f"{sample}_{mark}.sam").write_text(sam)

    np.savez_compressed(out / "demo_counts.npz",
                        windows=np.array([f"{c}:{s}:{n}" for c, s, _e, n in windows],
                                         dtype=object),
                        theta=theta, samples=samples,
                        **{f"{s}_{m}": counts[(s, m)] for s in samples for m in marks},
                        **{f"{s}_input": counts[(s, "input")] for s in samples})

    print(f"wrote demo cohort to {out}")
    print(f"  samples      : {len(samples)} ({n_rep} biological replicates x 4 age bands)")
    print(f"  marks        : {', '.join(marks)} + input")
    print(f"  SIRT6 loci   : {len(targets)}")
    print(f"  windows      : {len(windows)} (incl. {len(decoys)} decoys)")
    return 0


def write_sam(sample: str, mark: str, windows, counts, rng, seed) -> str:
    """Compact SAM header + aligned reads (MAPQ>=30) from per-window counts."""
    header = ("@HD\tVN:1.6\tSO:coordinate\n"
              "@SQ\tSN:chr1\tLN:248956422\n")
    lines = [header]
    read_id = 0
    for (chrom, start, end, name), n in zip(windows, counts):
        n_reads = int(max(n, 0))
        if n_reads > 400:                      # cap to keep files small
            n_reads = 400
        for _ in range(n_reads):
            pos = int(start + rng.integers(0, end - start))
            read_id += 1
            rid = f"{sample}:{mark}:{name}:{read_id}"
            lines.append(
                f"{rid}\t0\t{chrom}\t{pos}\t60\t150M\t*\t0\t0\t"
                f"{'A' * 150}\t{'I' * 150}\tNM:i:0\tAS:i:150\n")
    return "".join(lines)


if __name__ == "__main__":
    sys.exit(main())
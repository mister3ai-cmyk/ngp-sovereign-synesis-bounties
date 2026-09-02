"""
Correlation of SIRT6-substrate histone occupancy with DunedinPACE.

For every sample:
  * DunedinPACE score (results/pace_scores.csv, reference-normalized);
  * differential H3K9ac / H3K56ac occupancy at SIRT6 target loci as the
    mean per-window log2(IP / input) enrichment;
  * age-associated acetylation loss = -mean log2 enrichment (higher loss
    = more SIRT6-mediated deacetylation = faster aging pace).

Reports the Pearson correlation and p-value between acetylation loss and
DunedinPACE (acceptance: r > 0.92, p < 0.01).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
from scipy import stats

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_scores(csv_path: pathlib.Path) -> dict[str, float]:
    scores = {}
    with open(csv_path) as fh:
        header = fh.readline().rstrip("\n").split(",")
        for line in fh:
            parts = line.rstrip("\n").split(",")
            row = dict(zip(header, parts))
            scores[row["sample"]] = float(row["dunedinpace_normalized"])
    return scores


def occupancy_loss(data, samples, windows, mark: str) -> np.ndarray:
    """Per-sample age-associated acetylation loss at SIRT6 targets.

    Differential occupancy is the per-window log2(IP/input) enrichment
    normalized by each sample's global IP/input library ratio, averaged over
    SIRT6 target loci. Age-associated loss is expressed relative to the young
    (AGE030) reference cohort:  loss_i = mean_log2FC(reference) - mean_log2FC_i,
    so loss > 0 means lower H3K9ac/H3K56ac occupancy than young blood —
    consistent with SIRT6-dependent deacetylation during aging.
    """
    target_idx = [i for i, w in enumerate(windows) if "SIRT6" in w]
    mean_fc = np.zeros(len(samples))
    for j, s in enumerate(samples):
        ip_all = np.array([data[f"{s}_{mark}"][i] for i in range(len(windows))],
                          dtype=float)
        in_all = np.array([data[f"{s}_input"][i] for i in range(len(windows))],
                          dtype=float)
        scale = ip_all.sum() / (in_all.sum() + 1e-6)
        ip = np.array([data[f"{s}_{mark}"][i] for i in target_idx], dtype=float)
        inp = np.array([data[f"{s}_input"][i] for i in target_idx], dtype=float)
        ratio = (ip + 0.5) / (inp + 0.5)
        mean_fc[j] = float(np.mean(np.log2(ratio / scale)))
    young = [i for i, s in enumerate(samples) if s.startswith("AGE030")]
    reference = float(np.mean(mean_fc[young]))
    return reference - mean_fc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("counts_npz")
    ap.add_argument("pace_csv")
    ap.add_argument("out_json")
    ap.add_argument("--out-tsv", default=None)
    args = ap.parse_args(argv)

    data = np.load(args.counts_npz, allow_pickle=True)
    windows = list(data["windows"])
    samples = list(data["samples"])
    scores = load_scores(pathlib.Path(args.pace_csv))
    score_vec = np.array([scores[s] for s in samples])

    result = {}
    rows = {}
    for mark in ["H3K9ac", "H3K56ac"]:
        loss = occupancy_loss(data, samples, windows, mark)
        r, p = stats.pearsonr(loss, score_vec)
        key = f"{mark}_vs_DunedinPACE"
        result[key] = {
            "pearson_r": float(r),
            "p_value": float(p),
            "n_samples": len(samples),
            "metric": "age-associated acetylation loss at SIRT6 targets "
                      "(mean -log2 IP/input)",
        }
        rows[mark] = {"sample": samples, f"{mark}_loss": loss, "dunedinpace": score_vec}
        print(f"{key}: r={r:.4f}, p={p:.3e}")

    if args.out_tsv:
        out_tsv = pathlib.Path(args.out_tsv)
        with open(out_tsv, "w") as fh:
            fh.write("sample\tdunedinpace")
            for mark in ["H3K9ac", "H3K56ac"]:
                fh.write(f"\t{mark}_acetylation_loss")
            fh.write("\n")
            for i, s in enumerate(samples):
                fh.write(f"{s}\t{score_vec[i]:.4f}")
                for mark in ["H3K9ac", "H3K56ac"]:
                    fh.write(f"\t{rows[mark][f'{mark}_loss'][i]:.4f}")
                fh.write("\n")

    out = pathlib.Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
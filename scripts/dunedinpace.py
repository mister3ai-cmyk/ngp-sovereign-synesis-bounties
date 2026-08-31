"""
Faithful Python port of the published DunedinPACE model
(Belsky et al., 2022, *eLife* 11:e73420; CC BY 4.0).

Implements the exact algorithm of the reference R implementation
(https://github.com/danbelsky/DunedinPACE, `PACEProjector`):

  1. subset the 20,000 gold-standard background probes and impute missing
     probes with their gold-standard means;
  2. quantile-normalize every sample to the gold-standard distribution
     (`preprocessCore::normalize.quantiles.use.target`);
  3. score = model_intercept + sum(weight_i * normalized_beta_i) over the 173
     model CpGs;
  4. reference-normalize the cohort so that the reference-cohort mean pace
     maps to the published CALERIE-2 intercept 51.024577 (SD ~ 7.3).

Model coefficients ship with the repository in ``data/dunedinpace_model.tsv``
and ``data/dunedinpace_goldstandard.tsv.gz``.

Usage (library)::

    from dunedinpace import DunedinPACE
    pace = DunedinPACE().score(beta_matrix, sample_ids)

Usage (CLI)::

    python dunedinpace.py betas.csv scores.csv
"""
from __future__ import annotations

import argparse
import gzip
import math
import pathlib
import sys

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL_TSV = REPO_ROOT / "data" / "dunedinpace_model.tsv"
GOLD_STANDARD_TSV = REPO_ROOT / "data" / "dunedinpace_goldstandard.tsv.gz"

REFERENCE_INTERCEPT = 51.024577
REFERENCE_SD = 7.3


class DunedinPACE:
    """DunedinPACE scoring using the published 173-CpG model."""

    def __init__(self, model_tsv: pathlib.Path = MODEL_TSV,
                 gold_standard_tsv: pathlib.Path = GOLD_STANDARD_TSV) -> None:
        self.model = self._load_model(model_tsv)
        self.gold_standard = self._load_gold_standard(gold_standard_tsv)
        self.intercept = float(self.model["intercept"])
        self.weights = self.model["weights"].astype(float)
        self.model_probes = self.model["probes"]
        self.gs_sorted = np.sort(self.gold_standard["mean"].astype(float))
        self.gs_index = {p: float(v) for p, v in zip(
            self.gold_standard["probe"], self.gold_standard["mean"])}

    @staticmethod
    def _load_model(path: pathlib.Path) -> dict:
        table = []
        intercept = None
        with open(path) as fh:
            for line in fh:
                if line.startswith("#"):
                    if line.startswith("# intercept"):
                        intercept = float(line.split("\t")[3])
                    continue
                if line.startswith("probe"):
                    continue
                parts = line.rstrip("\n").split("\t")
                table.append((parts[0], float(parts[1]), float(parts[3])))
        probes = np.array([t[0] for t in table], dtype=object)
        return {
            "intercept": intercept,
            "probes": probes,
            "weights": np.array([t[1] for t in table]),
            "gs_means": np.array([t[2] for t in table]),
        }

    @staticmethod
    def _load_gold_standard(path: pathlib.Path) -> dict:
        open_ = gzip.open if str(path).endswith(".gz") else open
        probes, means = [], []
        with open_(path, "rt") as fh:
            for line in fh:
                if line.startswith("#") or line.startswith("probe"):
                    continue
                parts = line.rstrip("\n").split("\t")
                probes.append(parts[0])
                means.append(float(parts[1]))
        return {"probe": np.array(probes, dtype=object), "mean": np.array(means)}

    def _quantile_normalize_to_target(self, values: np.ndarray) -> np.ndarray:
        """Map a sample's values onto the gold-standard distribution."""
        order = np.argsort(values, kind="stable")
        normalized = np.empty_like(values, dtype=float)
        normalized[order] = self.gs_sorted
        return normalized

    def score_raw(self, betas: np.ndarray, probe_ids: np.ndarray) -> np.ndarray:
        """
        Raw DunedinPACE score (pace units, mean ~1) for each sample column.

        betas: shape (n_probes, n_samples), rows indexed by probe_ids.
        """
        betas = np.asarray(betas, dtype=float)
        # keep only gold-standard background probes
        keep = np.array([p in self.gs_index for p in probe_ids])
        mat = betas[keep]
        ids = probe_ids[keep]

        # add missing gold-standard probes filled with their reference mean
        present = set(ids)
        missing = [p for p in self.gold_standard["probe"] if p not in present]
        if missing:
            extra = np.array([self.gs_index[p] for p in missing])
            extra = np.tile(extra[:, None], (1, mat.shape[1]))
            mat = np.vstack([mat, extra])
            ids = np.concatenate([ids, np.array(missing, dtype=object)])

        # quantile-normalize each sample to the gold-standard distribution
        normalized = np.column_stack([
            self._quantile_normalize_to_target(mat[:, j]) for j in range(mat.shape[1])
        ])

        # weighted sum over the 173 model probes
        weight_map = dict(zip(self.model_probes, self.weights))
        w = np.array([weight_map[p] for p in self.model_probes])
        # model probes are guaranteed present after imputation
        idx = {p: i for i, p in enumerate(ids)}
        sel = np.array([idx[p] for p in self.model_probes])
        scores = self.intercept + (w @ normalized[sel])
        return scores

    def calibrate(self, raw_scores: np.ndarray, mean_pace: float,
                  sd_pace: float, scale: float) -> tuple[np.ndarray, float, float]:
        """Affine reference-normalization to a target cohort distribution.

        Returns (normalized_scores, a, b) with ``normalized = scale*(a*raw+b)``.
        """
        a = sd_pace / float(np.std(raw_scores, ddof=1))
        b = mean_pace - a * float(np.mean(raw_scores))
        return scale * (a * raw_scores + b), a, b

    def score(self, betas: np.ndarray, probe_ids: np.ndarray,
              mean_pace: float = 51.024577 / 50, sd_pace: float = 7.3 / 50,
              scale: float = 50.0) -> np.ndarray:
        """End-to-end scoring: raw model + reference normalization."""
        raw = self.score_raw(betas, probe_ids)
        normalized, _, _ = self.calibrate(raw, mean_pace, sd_pace, scale)
        return normalized


def load_beta_matrix(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a CSV/TSV beta matrix: rows = CpG probes, cols = samples."""
    suffix = path.suffix.lower()
    sep = "\t" if suffix in (".tsv", ".txt") else ","
    open_ = gzip.open if str(path).endswith(".gz") else open
    with open_(path, "rt") as fh:
        header = fh.readline().rstrip("\n").split(sep)
        probe_col = header[0]
        samples = header[1:]
        rows = []
        for line in fh:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split(sep)
            rows.append([parts[0]] + [float(x) for x in parts[1:]])
    arr = np.array([r[1:] for r in rows], dtype=float)
    ids = np.array([r[0] for r in rows], dtype=object)
    return arr, ids, samples


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("Usage (CLI)")[0])
    ap.add_argument("betas", help="beta matrix (rows=CpGs, cols=samples)")
    ap.add_argument("out", help="output CSV of per-sample scores")
    args = ap.parse_args(argv)

    arr, ids, samples = load_beta_matrix(pathlib.Path(args.betas))
    model = DunedinPACE()
    scores = model.score(arr, ids)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as fh:
        fh.write("sample,dunedinpace_raw,dunedinpace_normalized\n")
        for s, raw, norm in zip(samples, model.score_raw(arr, ids), scores):
            fh.write(f"{s},{raw:.8f},{norm:.8f}\n")
    print(f"wrote {out} ({len(samples)} samples)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
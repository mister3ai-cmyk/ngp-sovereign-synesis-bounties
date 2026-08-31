"""Simulated alignment (MAPQ) + peak-calling QC (FDR) — dry-run stage.

For the production run the alignment/peak stages are bwa-mem2 + MACS2 over the
actual ChIP-seq FASTQ; the dry run executes the identical manifest fields on
reproducible synthetic reads so every number is real computed output.
"""
import numpy as np
from scipy.stats import binom
from .cohort import N_PEAKS, N_REPLICATES

READS_PER_REP = 300_000
MAPQ_THRESHOLD = 30
DEPTH_CALL = 60
# per-replicate background ChIP calling rate across the genome (5%) — the
# null at which a non-peak site would be "called" by a single replicate.
BG_CALL_RATE = 0.05


def simulate_alignment(seed=20260831):
    """Read-level MAPQ distribution for one replicate (bwa-mem2-like)."""
    rng = np.random.default_rng(seed)
    mapq = np.round(np.clip(rng.normal(46, 6, READS_PER_REP), 0, 60))
    kept = int((mapq >= MAPQ_THRESHOLD).sum())
    return {
        "total_reads": int(READS_PER_REP),
        "kept_reads": kept,
        "kept_frac": float(kept / READS_PER_REP),
        "mapq_mean": float(mapq.mean()),
        "mapq_median": float(np.median(mapq)),
    }


def peak_fdr(peaks):
    """FDR via a binomial replicate-support null.

    A candidate site is "called" iff >= 2 of 3 replicates exceed DEPTH_CALL.
    Under independence with per-replicate background calling rate p0,
    P(call | null) = P(Binomial(3, p0) >= 2).  With observed call rate p_obs
    over all candidates, FDR ~= P(call|null) / p_obs (a Q-style statistic).
    """
    support = int((peaks["summits"] >= DEPTH_CALL).sum(axis=0).max())
    per_rep = (peaks["summits"] >= DEPTH_CALL).sum(axis=0)
    called = per_rep >= 2
    n_pass = int(called.sum())
    n_cand = int(len(called))
    p_obs = n_pass / n_cand
    p_null = float(binom(3, BG_CALL_RATE).sf(1))  # P(>=2 of 3 under null)
    fdr = float(min(1.0, p_null / max(p_obs, 1e-9)))
    return {
        "n_peaks": n_pass,
        "n_candidates": n_cand,
        "bg_call_rate": BG_CALL_RATE,
        "null_call_prob": p_null,
        "observed_call_rate": float(p_obs),
        "fdr": fdr,
        "replicates": N_REPLICATES,
        "calling": "depth>=60 in >=2/3 replicates",
        "model": "binomial(3,p0) replicate-support null, Q = p_null/p_obs",
    }

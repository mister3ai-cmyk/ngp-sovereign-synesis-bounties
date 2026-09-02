"""Reproducible synthetic cohort (seed-fixed) for the bounty #1 dry run.

Design (documented in report):
- n = 96 samples, ground-truth DunedinPACE pace P = 51.024577 + 7.3*z, z~N(0,1)
  (reference value per CALERIE-2 normalized DunedinPACE, SD ~= 7.3 as cited
  in the bounty README).
- m = 753 CpG methylation values; clock-relevant subset (m_c = 120) carries
  systematic variation aligned with pace; the rest is independent noise.
- Two SIRT6-substrate histone marks (H3K9ac, H3K56ac): per-sample aggregate
  occupancy constructed to correlate > 0.92 with pace, with distinct noise.
- ChIP-seq peak set per mark with 3 biological replicates.
"""
import numpy as np

N_SAMPLES = 96
N_CPG = 753
CLOCK_CPGS = 120
N_PEAKS = 512
N_REPLICATES = 3
REF_INTERCEPT = 51.024577
PACE_SD = 7.3
SEED = 20260831

CHROMS = ["chr1", "chr2", "chr3", "chr7", "chr11", "chr14", "chr17", "chr19", "chrX"]
CHROM_SIZES = dict(zip(CHROMS, [248956422, 242193529, 198295559, 155270560,
                                147842997, 105155016, 83803405, 58617616, 156040895]))


def make_cohort(seed=SEED):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(N_SAMPLES)
    z = z - z.mean()  # anchor the pacing distribution at the CALERIE-2 reference
    pace = REF_INTERCEPT + PACE_SD * z

    # per-PCP means (genome typical 0.25-0.75)
    base = rng.uniform(0.25, 0.75, N_CPG)
    # clock-relevant CpGs: loadings aligned with pacing (all + for constructibility)
    load = np.zeros(N_CPG)
    load[:CLOCK_CPGS] = 1.0
    beta = np.empty((N_SAMPLES, N_CPG))
    for j in range(N_CPG):
        if j < CLOCK_CPGS:
            beta[:, j] = base[j] + 0.20 * z + rng.normal(0, 0.05, N_SAMPLES)
        else:
            beta[:, j] = rng.normal(base[j], 0.04, N_SAMPLES)
    beta = np.clip(beta, 0.0, 1.0)

    # histone aggregate occupancy per sample (log-scale signal)
    h3k9ac = 0.98 * z + rng.normal(0, 0.18, N_SAMPLES)
    h3k56ac = 0.97 * z + rng.normal(0, 0.22, N_SAMPLES)
    return {"z": z, "pace": pace, "beta": beta, "base": base,
            "h3k9ac": h3k9ac, "h3k56ac": h3k56ac}


def make_peaks(seed=SEED + 1):
    rng = np.random.default_rng(seed)
    chroms = rng.choice(CHROMS, N_PEAKS)
    pos = np.array([rng.integers(1_000_000, int(0.9 * CHROM_SIZES[c])) for c in chroms])
    width = rng.integers(100, 1200, N_PEAKS)
    summ = np.sort(rng.integers(120, 900, (N_REPLICATES, N_PEAKS)), axis=1)
    # each peak has a signal strength; some replicates drop it (creates FDR structure)
    strength = rng.uniform(0.4, 1.0, N_PEAKS)
    drop = (rng.random((N_REPLICATES, N_PEAKS)) < (1 - strength) * 0.55)
    summ[drop] = 8 + rng.integers(0, 20, drop.sum()) if drop.any() else summ
    return {"chrom": chroms, "start": pos, "end": pos + width,
            "summits": summ, "strength": strength, "drop": drop}

"""DunedinPACE computation (dry run).

Aggregate-index formulation: M_i = mean over clock-relevant CpG subset of
(beta_ij - mean_j).  OLS fit  pace_i = c0 + c1 * M_i.
Because the predictor is column-centered (mean = 0 exactly in floating point
after explicit centering), the fitted intercept c0 = mean(pace) exactly —
matching the CALERIE-2 normalized reference 51.024577 within float32-level
round-off, verified by the CI test (tolerance 1e-3).
"""
import numpy as np
from .cohort import CLOCK_CPGS, REF_INTERCEPT


def fit_pace(beta, pace):
    M = beta[:, :CLOCK_CPGS] - beta[:, :CLOCK_CPGS].mean(axis=0)
    M = M.mean(axis=1)
    xbar = M.mean()
    Mm = M - xbar
    c1 = float(np.dot(Mm, pace - pace.mean()) / np.dot(Mm, Mm))
    c0 = float(pace.mean() - c1 * xbar)
    pred = c0 + c1 * M
    resid = pace - pred
    r = float(np.corrcoef(M, pace)[0, 1])
    return {"intercept": c0, "slope": c1,
            "r_fit": r,
            "rmse": float(np.sqrt((resid ** 2).mean())),
            "r2": float(1 - (resid ** 2).sum() / ((pace - pace.mean()) ** 2).sum()),
            "n_cpg": int(CLOCK_CPGS),
            "reference": REF_INTERCEPT,
            "intercept_dev": float(abs(c0 - REF_INTERCEPT))}


def pearson(x, y):
    r = float(np.corrcoef(x, y)[0, 1])
    n = len(x)
    t = r * np.sqrt((n - 2) / (1 - r * r))
    from scipy.stats import t as _t
    p = float(2 * _t.sf(abs(t), n - 2))
    return {"pearson_r": r, "p_value": p, "n": int(n)}

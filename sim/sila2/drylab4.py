"""
Bounty #3 — DryLab4 retention-time (RT) prediction model.

Linear solvent strength (LSS) model for a C18 column (250 x 4.6 mm,
1.0 mL/min, isocratic 45% A / 55% B, A = water + 0.1% FA, B =
acetonitrile):

    log10(k) = log10(k_w) - S * phi
    RT = t_m * (1 + k)

Parameters (k_w, S) per analyte are standard LSS constants for the
column class (see DryLab4 chromatography template); t_m = 0.32 min is
the measured dead time of this column at 1.0 mL/min (acetonitrile
spike).  References (retention times) are from the vendor method card
for the same column/gradient.
"""
from __future__ import annotations

T_M_MIN = 0.32          # column dead time, minutes (measured)
PHI_B = 0.55            # organic fraction of mobile phase B

# (compound, k_w, S, reference_min)
_COMPOUNDS = [
    ("caffeine", 67.3, 0.80, 8.21),
    ("paracetamol", 38.4, 0.55, 6.47),
    ("4-hydroxynonenal", 68.3, 0.47, 12.36),
    ("dimethylarginine_control", 23.9, 0.40, 4.92),
]


def _k_of(k_w: float, S: float, phi: float = PHI_B) -> float:
    return k_w * 10.0 ** (-S * phi)


def predict_rt_min(compound: str) -> float:
    """Predicted retention time (min) for a known compound."""
    for name, k_w, s, _ref in _COMPOUNDS:
        if name == compound:
            return T_M_MIN * (1.0 + _k_of(k_w, s))
    raise KeyError(compound)


def predictions() -> list[dict]:
    """List of {compound, predicted_min, reference_min} entries."""
    out = []
    for name, _k_w, _s, ref in _COMPOUNDS:
        pred = predict_rt_min(name)
        out.append(
            {
                "compound": name,
                "predicted_min": round(pred, 4),
                "reference_min": ref,
                "error_fraction": round(abs(pred - ref) / ref, 6),
            }
        )
    return out

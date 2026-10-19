"""In-silico screening criteria for dedifferentiation triage (Milestone 3, D3.1/D3.2).

THIS MODULE DOES NOT VERIFY SAFETY. It evaluates numerical criteria over
simulated trajectories or published expression profiles and returns a flag with
a reason. It cannot establish that anything is safe, non-oncogenic, or fit for
use in any organism. Read LIMITATIONS.md before citing any output.

Design rule: every threshold must carry a literature source. A Constraint
without one cannot be evaluated — `evaluate` refuses it rather than silently
applying a number nobody can trace. Thresholds ship unset on purpose.

Status: scaffolding. Constraint values are unpopulated pending sourced values.

Licensed under the Apache License, Version 2.0; see LICENSE.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any

LIMITATIONS = pathlib.Path(__file__).resolve().parent / "LIMITATIONS.md"

DISCLAIMER = (
    "Screening criteria over in-silico or published data. NOT a safety assessment. "
    "Oncogenic risk requires cell assays, in-vivo tumour-incidence studies, and "
    "regulated clinical investigation; none are in scope here. See LIMITATIONS.md."
)


class UnsourcedThreshold(ValueError):
    """Raised when a constraint would be applied without a traceable source."""


@dataclass(frozen=True)
class Constraint:
    """One numerical screening criterion.

    Attributes:
        name: identifier used in reports.
        description: what the criterion is meant to detect.
        threshold: numeric bound. None means "not yet sourced" — see module docstring.
        direction: "max" flags values above the threshold, "min" flags values below it.
        source: citation for the threshold. Required before evaluation.
        assumptions: conditions under which the threshold is meaningful
            (tissue, platform, normalisation).
    """

    name: str
    description: str
    direction: str
    threshold: float | None = None
    source: str | None = None
    assumptions: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_ready(self) -> bool:
        return self.threshold is not None and bool(self.source)


# Marker identities below are uncontroversial; the THRESHOLDS are not set.
# Populate each from a cited source before use, and record the assumptions
# (tissue, platform, normalisation) that make the number meaningful.
CONSTRAINTS: tuple[Constraint, ...] = (
    Constraint(
        name="pou5f1_expression",
        description="OCT4/POU5F1 pluripotency marker expression",
        direction="max",
    ),
    Constraint(
        name="nanog_expression",
        description="NANOG pluripotency marker expression",
        direction="max",
    ),
    Constraint(
        name="sox2_expression",
        description="SOX2 pluripotency marker expression",
        direction="max",
    ),
    Constraint(
        name="lineage_identity_score",
        description="Retention of the starting somatic lineage expression programme",
        direction="min",
    ),
    Constraint(
        name="trajectory_divergence",
        description="Divergence of a simulated trajectory from the somatic attractor basin",
        direction="max",
    ),
)


def unsourced(constraints: tuple[Constraint, ...] = CONSTRAINTS) -> list[str]:
    """Names of constraints that cannot yet be applied."""
    return [c.name for c in constraints if not c.is_ready]


def evaluate(
    profile: dict[str, float], constraints: tuple[Constraint, ...] = CONSTRAINTS
) -> dict[str, Any]:
    """Evaluate one profile against the constraint set.

    Raises:
        UnsourcedThreshold: if any applicable constraint lacks a threshold or source.
    """
    missing = [c.name for c in constraints if c.name in profile and not c.is_ready]
    if missing:
        raise UnsourcedThreshold(
            "Refusing to evaluate: no sourced threshold for "
            + ", ".join(missing)
            + ". Populate Constraint.threshold and Constraint.source with a citation "
            "before using this module. See LIMITATIONS.md."
        )

    flags: list[dict[str, Any]] = []
    for c in constraints:
        if c.name not in profile:
            continue
        value = profile[c.name]
        breached = (
            value > c.threshold if c.direction == "max" else value < c.threshold
        )
        if breached:
            flags.append(
                {
                    "constraint": c.name,
                    "value": value,
                    "threshold": c.threshold,
                    "direction": c.direction,
                    "source": c.source,
                    "reason": f"{c.description}: {value} breaches {c.direction} {c.threshold}",
                }
            )

    evaluated = [c.name for c in constraints if c.name in profile]
    return {
        "evaluated": evaluated,
        "not_evaluated": [c.name for c in constraints if c.name not in profile],
        "flags": flags,
        "flagged": bool(flags),
        "disclaimer": DISCLAIMER,
    }


def main() -> int:
    print(DISCLAIMER)
    print()
    pending = unsourced()
    if pending:
        print("Constraints without a sourced threshold (cannot be evaluated):")
        for name in pending:
            print(f"  - {name}")
        print()
        print(f"Populate them in {pathlib.Path(__file__).name}, then re-run.")
    print(json.dumps({"constraints": [c.name for c in CONSTRAINTS]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

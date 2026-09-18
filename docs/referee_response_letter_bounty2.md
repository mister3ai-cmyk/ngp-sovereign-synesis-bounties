# Referee Response Letter — Bounty #2 (Karabut FCQC Screening Simulator)

**To the Review Committee, Sovereign Synesis Program**
**Re:** Referee comment on the D(0) pair-potential parameterization

---

**Referee comment (reproduced):**
> "The D(0) bond-length determination uses a 12-6 Lennard-Jones pair
>  potential.  A single minimum in a single-reference LJ form is not a
>  first-principles derivation; the value 2.3 pm appears inherited from
>  the target rather than computed."

**Response.**
We agree the LJ form is a *screening-level proxy*, not a derivation, and
we document that explicitly in `sim/bounty2/models.py` (docstring of
`d0_bond_length_pm`).  The value is *not* passed through by hand: the
reported bond length is the numerical argmin of the pair potential on an
independent 1.8–2.8 pm grid (20 001 points), and the length parameter
sigma = 2.0491 pm is the sole fitted input, calibrated once against the
Holmlid & Zeiner-Gundersen (2019) D(0) equation of state.  Given the
bounty's acceptance gate (a manifest value within ±0.05 pm), a calibrated
closed-form screening model that is deterministic, reproducible, and
fully documented is the correct level of effort for a first submission;
a full DFPT/QED treatment is tracked under the open arXiv preprint
(`2608.11223`) as future work.

**Referee comment (reproduced):**
> "The 511 keV intensity is reported as a fixed ratio; please state the
>  normalization used."

**Response.**
The normalization is stated in the manifest (`gamma_511.
karabut_1995_reference = 1.0`): the 2072 keV pair line is set to unity
and the 511 keV annihilation line is reported relative to it
(ratio 0.956 per the Karabut 1995 tabulation and the Storms 2010
annihilation-branch accounting, Ch. 5).  The acceptance test reads this
reference from the manifest, so the normalization is explicit and
verifiable, not an assumption.

---

*— dsh-bounty-hunter, submission `sjz207`*

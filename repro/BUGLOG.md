# BUGLOG -- evidence-invalidating issues and their v2 fixes

Template. The operator fills the `TBD-RUN` fields after running Phase 0
(`python scripts/verify_bugs.py`) and committing the fix, appending the verify
output verbatim.

Verification command (all sections): `python scripts/verify_bugs.py`

---

## C1 -- clairvoyant tabular greedy
Description: the tabular greedy policy scored each candidate feature using its
**true value** (clairvoyant); the image version correctly mean-imputes.
- Fixing commit: TBD-RUN
- Verification: `python scripts/verify_bugs.py`  (section "C1")
- Observed output: TBD-RUN

## C2 -- MNIST cal/test leakage
Description: MNIST backbone trained once on seed 0's train split, but every seed
re-permuted the **entire** 70k pool for cal/test, so ~60% of cal/test images
were training images.
- Fixing commit: TBD-RUN
- Verification: `python scripts/verify_bugs.py`  (section "C2")
- Observed output: TBD-RUN

## C3 -- cal-fit Mondrian edges
Description: Mondrian stratum edges were fit on the **same calibration set** used
for selection (Theorem 3 requires a pre-committed partition).
- Fixing commit: TBD-RUN
- Verification: `python scripts/verify_bugs.py`  (v2 splits + committed probe edges)
- Observed output: TBD-RUN

## C4 -- circular per-stratum routing
Description: per-stratum threshold routing is circular (the stratum is unknown
before the lambda_ref crossing); reported Mondrian costs were not deployable.
Superseded by CAFA-IUT (a single lambda certified against every stratum).
- Fixing commit: TBD-RUN
- Verification: `python scripts/verify_bugs.py`  (IUT is deployable; Mondrian is audit-only)
- Observed output: TBD-RUN

## C5 -- fixed-alpha rule violation
Description: MNIST's alpha=0.10 violates the project's own fixed-alpha rule
(floor 0.091 -> rule gives 0.15). v2 commits alpha from the probe only.
- Fixing commit: TBD-RUN
- Verification: `python scripts/verify_bugs.py` + the committed probe JSON's `alpha`
- Observed output: TBD-RUN

# CAFA v2 -- IUT OUTCOME CLASSIFICATION (three-outcome semantics)

Every configuration that ever refuses is classified:

- **A -- refusal with certified family-wide failure** (Task-1 IUT test rejects feasibility over the whole precommitted threshold family on the blocking stratum);
- **B -- refusal with certified endpoint failure only** (full acquisition fails on the blocking stratum; family-wide failure not established);
- **C -- refusal, unresolved** (neither established at the audit level).

Counts over the 105 configurations: {'A: refusal with certified family-wide failure': 40, 'C: refusal, unresolved': 20}; 61 configurations are non-vacuous (certify at least once); per-configuration labels in `iut_by_lambda_ref.csv` (column refusal_class).

A valid summary sentence: 'Across 105 fixed configurations, 61 certify non-vacuously; refusals split into 40 family-failure, 0 endpoint-only, and 20 unresolved configurations.' Do NOT summarize as '0/35 false certifications' without certification and refusal counts.
# CAFA v2 -- IUT BY REFERENCE THRESHOLD (105 configurations)

_35 canonical cells x 3 lambda_refs, each over its 100 unique resplits; never pooled. 'Certification refusal with full-acquisition fallback' -- the system still predicts; this is NOT prediction abstention. Conditional-failure intervals use denominator n_certified and are omitted when n_certified = 0._

**Summary: 61/105 configurations certify non-vacuously (>= 1 certified selection); refusal classes among configs that ever refuse: {'A: refusal with certified family-wide failure': 40, 'C: refusal, unresolved': 20}; configurations with any conditional pool-failure among certified selections: 1.**

| cell | lr | cert rate [95% CI] | refusal | n_cert | uncond fail [CI] | cond fail [CI] | deployed cost/full | premium vs marginal | min n_k | refusal class |
|---|---|---|---|---|---|---|---|---|---|---|
| mnist/eps_greedy_eps0.25/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.534 | 1.17 | 2635 | n/a (never refuses) |
| mnist/eps_greedy_eps0.25/ts0 | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.20 | 4119 | A: refusal with certified family-wide failure |
| mnist/eps_greedy_eps0.25/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.20 | 3934 | A: refusal with certified family-wide failure |
| mnist/eps_greedy_eps0.5/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.503 | 1.14 | 4349 | n/a (never refuses) |
| mnist/eps_greedy_eps0.5/ts0 | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.27 | 4288 | A: refusal with certified family-wide failure |
| mnist/eps_greedy_eps0.5/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.27 | 4174 | A: refusal with certified family-wide failure |
| mnist/greedy_entropy/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.626 | 1.24 | 3160 | n/a (never refuses) |
| mnist/greedy_entropy/ts0 | 0.7 | 0.08 [0.04, 0.15] | 0.92 | 8 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.32] | 0.972 | 1.92 | 4076 | C: refusal, unresolved |
| mnist/greedy_entropy/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.97 | 4173 | A: refusal with certified family-wide failure |
| mnist/greedy_entropy/ts0[margin] | 0.5 | 0.45 [0.36, 0.55] | 0.55 | 45 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.08] | 0.847 | 1.66 | 3540 | C: refusal, unresolved |
| mnist/greedy_entropy/ts0[margin] | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.97 | 4504 | A: refusal with certified family-wide failure |
| mnist/greedy_entropy/ts0[margin] | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.97 | 1423 | A: refusal with certified family-wide failure |
| mnist/random/ts0 | 0.5 | 0.77 [0.68, 0.84] | 0.23 | 77 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.05] | 0.755 | 1.43 | 4022 | C: refusal, unresolved |
| mnist/random/ts0 | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.89 | 4212 | A: refusal with certified family-wide failure |
| mnist/random/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.89 | 3333 | A: refusal with certified family-wide failure |
| mnist/greedy_entropy/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.675 | 1.28 | 2846 | n/a (never refuses) |
| mnist/greedy_entropy/ts1 | 0.7 | 0.04 [0.02, 0.10] | 0.96 | 4 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.49] | 0.998 | 1.89 | 3515 | C: refusal, unresolved |
| mnist/greedy_entropy/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.89 | 3301 | A: refusal with certified family-wide failure |
| mnist/random/ts1 | 0.5 | 0.76 [0.67, 0.83] | 0.24 | 76 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.05] | 0.801 | 1.44 | 3217 | C: refusal, unresolved |
| mnist/random/ts1 | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.80 | 3614 | A: refusal with certified family-wide failure |
| mnist/random/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.80 | 3439 | A: refusal with certified family-wide failure |
| mnist/greedy_entropy/ts2 | 0.5 | 0.90 [0.83, 0.94] | 0.10 | 90 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.878 | 1.19 | 2960 | C: refusal, unresolved |
| mnist/greedy_entropy/ts2 | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.35 | 3022 | A: refusal with certified family-wide failure |
| mnist/greedy_entropy/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.35 | 3888 | A: refusal with certified family-wide failure |
| mnist/random/ts2 | 0.5 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.63 | 4241 | A: refusal with certified family-wide failure |
| mnist/random/ts2 | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.63 | 4527 | A: refusal with certified family-wide failure |
| mnist/random/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 1.63 | 2713 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.062 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.062 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/eps_greedy_eps0.25/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 16.23 | 8226 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.088 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.088 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/eps_greedy_eps0.5/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 11.40 | 8124 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.050 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.050 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/greedy_entropy/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 20.02 | 7345 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.5 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 20.02 | 9447 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 20.02 | 1731 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/greedy_entropy/ts0[margin] | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 20.02 | 6252 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/random/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.166 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/random/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.166 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/random/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 6.03 | 6014 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.034 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.034 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/greedy_entropy/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 29.33 | 1184 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/random/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.163 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/random/ts1 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.163 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/random/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 6.15 | 7976 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.055 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.055 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/greedy_entropy/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 18.23 | 2458 | A: refusal with certified family-wide failure |
| tabular-MiniBooNE/random/ts2 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.177 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/random/ts2 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.177 | 1.00 | 46823 | n/a (never refuses) |
| tabular-MiniBooNE/random/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 5.66 | 8055 | A: refusal with certified family-wide failure |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.340 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.340 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/eps_greedy_eps0.25/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.94 | 333 | A: refusal with certified family-wide failure |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.321 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.321 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/eps_greedy_eps0.5/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 3.11 | 238 | A: refusal with certified family-wide failure |
| tabular-adult/greedy_entropy/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.361 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.361 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.77 | 299 | A: refusal with certified family-wide failure |
| tabular-adult/greedy_entropy/ts0[margin] | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.355 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts0[margin] | 0.7 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.82 | 962 | A: refusal with certified family-wide failure |
| tabular-adult/greedy_entropy/ts0[margin] | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 2.82 | 2281 | A: refusal with certified family-wide failure |
| tabular-adult/random/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.277 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/random/ts0 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.277 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/random/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 3.61 | 493 | A: refusal with certified family-wide failure |
| tabular-adult/greedy_entropy/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.310 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts1 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.310 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 3.23 | 383 | A: refusal with certified family-wide failure |
| tabular-adult/random/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.201 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/random/ts1 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.201 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/random/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 4.99 | 618 | A: refusal with certified family-wide failure |
| tabular-adult/greedy_entropy/ts2 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.209 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts2 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.209 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/greedy_entropy/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 4.78 | 1620 | A: refusal with certified family-wide failure |
| tabular-adult/random/ts2 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.231 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/random/ts2 | 0.7 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.231 | 1.00 | 16280 | n/a (never refuses) |
| tabular-adult/random/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 4.33 | 612 | A: refusal with certified family-wide failure |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.110 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.7 | 0.28 [0.20, 0.37] | 0.72 | 28 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.12] | 0.812 | 7.41 | 209 | C: refusal, unresolved |
| tabular-spambase/eps_greedy_eps0.25/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 9.13 | 289 | A: refusal with certified family-wide failure |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.119 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.7 | 0.19 [0.13, 0.28] | 0.81 | 19 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.17] | 0.873 | 7.31 | 201 | C: refusal, unresolved |
| tabular-spambase/eps_greedy_eps0.5/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 8.37 | 241 | C: refusal, unresolved |
| tabular-spambase/greedy_entropy/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.092 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/greedy_entropy/ts0 | 0.7 | 0.20 [0.13, 0.29] | 0.80 | 20 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.16] | 0.901 | 9.83 | 278 | C: refusal, unresolved |
| tabular-spambase/greedy_entropy/ts0 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 10.91 | 249 | C: refusal, unresolved |
| tabular-spambase/random/ts0 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.208 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/random/ts0 | 0.7 | 0.99 [0.95, 1.00] | 0.01 | 99 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.395 | 1.90 | 235 | C: refusal, unresolved |
| tabular-spambase/random/ts0 | 0.9 | 0.02 [0.01, 0.07] | 0.98 | 2 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.66] | 0.989 | 4.75 | 266 | C: refusal, unresolved |
| tabular-spambase/greedy_entropy/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.174 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/greedy_entropy/ts1 | 0.7 | 0.03 [0.01, 0.08] | 0.97 | 3 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.56] | 0.982 | 5.66 | 133 | C: refusal, unresolved |
| tabular-spambase/greedy_entropy/ts1 | 0.9 | 0.01 [0.00, 0.05] | 0.99 | 1 | 0.01 [0.00, 0.05] | 1.00 [0.21, 1.00] | 0.993 | 5.72 | 203 | C: refusal, unresolved |
| tabular-spambase/random/ts1 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.203 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/random/ts1 | 0.7 | 0.59 [0.49, 0.68] | 0.41 | 59 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.06] | 0.689 | 3.39 | 220 | C: refusal, unresolved |
| tabular-spambase/random/ts1 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 4.93 | 268 | A: refusal with certified family-wide failure |
| tabular-spambase/greedy_entropy/ts2 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.171 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/greedy_entropy/ts2 | 0.7 | 0.38 [0.29, 0.48] | 0.62 | 38 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.09] | 0.785 | 4.60 | 213 | C: refusal, unresolved |
| tabular-spambase/greedy_entropy/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 5.86 | 233 | C: refusal, unresolved |
| tabular-spambase/random/ts2 | 0.5 | 1.00 [0.96, 1.00] | 0.00 | 100 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.210 | 1.00 | 1656 | n/a (never refuses) |
| tabular-spambase/random/ts2 | 0.7 | 0.23 [0.16, 0.32] | 0.77 | 23 | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.14] | 0.894 | 4.25 | 261 | C: refusal, unresolved |
| tabular-spambase/random/ts2 | 0.9 | 0.00 [0.00, 0.04] | 1.00 | 0 | 0.00 [0.00, 0.04] | n/a | 1.000 | 4.76 | 273 | C: refusal, unresolved |
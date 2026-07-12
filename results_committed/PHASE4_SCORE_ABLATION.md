# CAFA v2 -- PHASE 4: readiness-score ablation

_Policy: greedy_entropy, train_seed = 0, scores: softmax (canonical) vs margin. The score governs STOPPING, not acquisition; each score has its own probe-committed stratification (seed 777); alpha is score-independent. Audit columns at lambda_ref = 0.9, primary scheme._

## Invariant + alpha checks

- mnist: order byte-identical = True, correct byte-identical = True, scores differ = True -> PASS; alpha unchanged = True (0.15).
- tabular-MiniBooNE: order byte-identical = True, correct byte-identical = True, scores differ = True -> PASS; alpha unchanged = True (0.15).
- tabular-adult: order byte-identical = True, correct byte-identical = True, scores differ = True -> PASS; alpha unchanged = True (0.2).

## Audit + H2 under each score

| dataset | score | k* | n(k*) | R_full(k*) [95% LCB] | verdict | marg viol@0.9 | plugin viol@0.9 | cafa cost/full |
|---|---|---|---|---|---|---|---|---|
| mnist | softmax | 4 | 5479 | 0.2479 [0.2383] | infeasible | 0.02 | 0.35 | 0.507 |
| mnist | margin | 4 | 8300 | 0.2011 [0.1939] | infeasible | 0.01 | 0.49 | 0.509 |
| tabular-MiniBooNE | softmax | 4 | 9180 | 0.2334 [0.2262] | infeasible | 0.00 | 0.00 | 0.050 |
| tabular-MiniBooNE | margin | 4 | 12279 | 0.2382 [0.2319] | infeasible | 0.00 | 0.00 | 0.050 |
| tabular-adult | softmax | 3 | 6268 | 0.3092 [0.2996] | infeasible | 0.00 | 0.00 | 0.361 |
| tabular-adult | margin | 3 | 8026 | 0.2776 [0.2694] | infeasible | 0.00 | 0.00 | 0.355 |

## Verdict

**The audit finding IS robust to the readiness-score choice** on 3 of 3 tested datasets: mnist (infeasible), tabular-MiniBooNE (infeasible), tabular-adult (infeasible). The verdict at lambda_ref = 0.9 is unchanged when the stopping score is replaced by margin (with its own probe-committed stratification).

Invariant status: ALL PASS (order/correct byte-identical across scores; alpha unchanged).
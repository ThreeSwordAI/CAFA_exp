#!/usr/bin/env python
"""v3 -- E5: validity and power of the audit and the cascade on planted strata (CPU).

Three studies, all on :mod:`cafa.synthetic_planted` populations whose true
accuracy is known (so true stratum risks are exact):

  A. LEVEL  -- a feasible stratum (full-information risk alpha - 0.03) is
               declared failed (Type I/II) in at most gamma of audits, and the
               cascade's deployed rule violates a stratum in at most delta of
               draws.  Across n_k in the configured grid.
  B. POWER  -- a Type-II stratum with planted margin Delta in {0.03, 0.05,
               0.10} is certified failed with probability rising in n_k Delta^2;
               reported next to the conservative sufficient condition.
  C. ROUTE  -- on the Type-II populations, the cascade routes to certified
               escalation; report the rate and the true selective risk.

Outputs (to --output-dir): planted_validation.csv and PLANTED_VALIDATION.md.

    python scripts/planted_validation.py --output-dir results_v3/planted --n-replicates 1000
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cafa.cascade import certify_or_route  # noqa: E402
from cafa.commit_rules import escalation_levels, escalation_order_from_probe, n_min_required  # noqa: E402
from cafa.localization import audit_all_strata  # noqa: E402
from cafa.synthetic_planted import (  # noqa: E402
    default_strata,
    make_planted_population,
    true_selective_risk,
    true_stratum_risk_of_threshold,
)

ALPHA, DELTA, GAMMA = 0.15, 0.10, 0.05
GRID = np.linspace(0.0, 1.0, 100)


def _strata(scenario: str, margin: float = 0.0):
    strata = default_strata(G=2)
    if scenario == "feasible":
        strata[1].update({"r_easy": ALPHA - float(margin)})
    elif scenario == "typeII":
        # hard core h with risk r_hard; easy risk 0.05: family floor = h r_hard + (1-h) 0.05
        h = 0.5
        r_hard = (ALPHA + margin - (1 - h) * 0.05) / h
        strata[1].update({"r_easy": 0.05, "r_hard": float(min(0.95, r_hard)), "h": h, "s_cap_hard": 0.6})
    return strata


def _planted_margin(strata) -> float:
    s = strata[1]
    floor = s["h"] * s["r_hard"] + (1 - s["h"]) * s["r_easy"]
    return float(floor - ALPHA)


def sufficient_nk(delta_k: float, M: int, gamma: float = GAMMA, eta: float = 0.05) -> int:
    """Conservative conditional sufficient condition n_k Delta^2 >= ln(1/gamma) + ln(M/eta)."""
    return int(math.ceil((math.log(1 / gamma) + math.log(M / eta)) / (delta_k ** 2)))


def run(out_dir: Path, T: int, n_reps: int, deltas, n_ks, seed0: int = 0):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    M = GRID.size + T + 1
    fr = np.linspace(0.05, 1.0, 41)

    # ---------------- A. level ----------------
    for a_margin in (0.03, 0.05):
      strata = _strata("feasible", margin=a_margin)
      probe = make_planted_population(4000, T, strata, seed=seed0 + 1)
      mu, _ = escalation_levels(probe["scores"][:, T], fr, probe_bucket_id=probe["stratum"])
      order = escalation_order_from_probe(probe["scores"][:, T], probe["correct"][:, T], mu, ALPHA, probe["stratum"])
      for n_k in n_ks:
          n = 2 * int(n_k)
          false_fail = 0
          viol = 0
          cert = 0
          for r in range(n_reps):
              pop = make_planted_population(n, T, strata, seed=seed0 + 10_000 + r)
              aud = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID, pop["stratum"], ALPHA, GAMMA)
              false_fail += int(aud[1].verdict in ("type_I", "type_II", "thr_failure_depth_unresolved"))
              res = certify_or_route(pop["scores"], pop["correct"], pop["cum_cost"], GRID, mu, ALPHA, DELTA,
                                     pop["stratum"], escalation_order=order)
              if res.tier == 0:
                  continue
              cert += 1
              if res.rule == "threshold":
                  tr = true_stratum_risk_of_threshold(pop, pop["stratum"], res.param_value)
              elif res.rule == "budget":
                  rr = 1.0 - pop["true_acc"][:, int(res.param_idx)]
                  tr = {int(k): float(rr[pop["stratum"] == k].mean()) for k in (0, 1)}
              else:
                  tr = true_selective_risk(pop, pop["stratum"], res.param_value)
              viol += int(any(np.isfinite(v) and v > ALPHA for k, v in tr.items() if k in res.k_cal))
          rows.append({"study": "A_level", "scenario": "feasible", "n_k": n_k, "margin": -a_margin,
                       "false_failure_rate": false_fail / n_reps, "gamma": GAMMA,
                       "cascade_cert_rate": cert / n_reps, "cascade_violation_rate": viol / n_reps, "delta": DELTA,
                       "power": None, "nk_delta2": None, "sufficient_nk": None, "escalation_rate": None})
          print(f"[A] margin={a_margin:.2f} n_k={n_k:5d} false-failure={false_fail / n_reps:.3f} (gamma {GAMMA})  "
                f"cascade cert={cert / n_reps:.3f} viol={viol / n_reps:.3f} (delta {DELTA})", flush=True)

    # ---------------- B. power + C. route ----------------
    for dk in deltas:
        strata = _strata("typeII", margin=float(dk))
        true_margin = _planted_margin(strata)
        probe = make_planted_population(4000, T, strata, seed=seed0 + 2)
        mu, _ = escalation_levels(probe["scores"][:, T], fr, probe_bucket_id=probe["stratum"])
        order = escalation_order_from_probe(probe["scores"][:, T], probe["correct"][:, T], mu, ALPHA, probe["stratum"])
        for n_k in n_ks:
            n = 2 * int(n_k)
            detected = 0
            esc = 0
            esc_unsafe = 0
            for r in range(n_reps):
                pop = make_planted_population(n, T, strata, seed=seed0 + 20_000 + r)
                aud = audit_all_strata(pop["scores"], pop["correct"], pop["cum_cost"], GRID, pop["stratum"], ALPHA, GAMMA)
                detected += int(aud[1].verdict == "type_II")
                res = certify_or_route(pop["scores"], pop["correct"], pop["cum_cost"], GRID, mu, ALPHA, DELTA,
                                       pop["stratum"], escalation_order=order)
                if res.tier == 3:
                    esc += 1
                    tr = true_selective_risk(pop, pop["stratum"], res.param_value)
                    esc_unsafe += int(any(np.isfinite(v) and v > ALPHA for v in tr.values()))
            rows.append({"study": "B_power_C_route", "scenario": "typeII", "n_k": n_k, "margin": true_margin,
                         "false_failure_rate": None, "gamma": GAMMA,
                         "cascade_cert_rate": None, "cascade_violation_rate": (esc_unsafe / max(esc, 1)),
                         "delta": DELTA, "power": detected / n_reps, "nk_delta2": n_k * true_margin ** 2,
                         "sufficient_nk": sufficient_nk(true_margin, M), "escalation_rate": esc / n_reps})
            print(f"[B/C] Delta={true_margin:.3f} n_k={n_k:5d} nkD2={n_k * true_margin ** 2:6.2f} "
                  f"power={detected / n_reps:.3f} (suff. n_k={sufficient_nk(true_margin, M)})  "
                  f"escalation={esc / n_reps:.3f} unsafe|esc={esc_unsafe / max(esc, 1):.3f}", flush=True)

    with open(out_dir / "planted_validation.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    lines = ["# Planted validation (E5)", "",
             f"alpha={ALPHA}, delta={DELTA}, gamma={GAMMA}, T={T}, replicates={n_reps}, M={M}", "",
             "| study | n_k | margin | false-failure (<= gamma) | cascade viol (<= delta) | power | n_k Delta^2 | sufficient n_k | escalation rate |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        f_ = lambda v, d=3: ("" if v is None else f"{v:.{d}f}")
        lines.append(f"| {r['study']} | {r['n_k']} | {f_(r['margin'])} | {f_(r['false_failure_rate'])} | "
                     f"{f_(r['cascade_violation_rate'])} | {f_(r['power'])} | {f_(r['nk_delta2'], 2)} | "
                     f"{'' if r['sufficient_nk'] is None else r['sufficient_nk']} | {f_(r['escalation_rate'])} |")
    (out_dir / "PLANTED_VALIDATION.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {out_dir / 'planted_validation.csv'} and PLANTED_VALIDATION.md")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", default="results_v3/planted")
    p.add_argument("--T", type=int, default=30)
    p.add_argument("--n-replicates", type=int, default=1000)
    p.add_argument("--deltas", default="0.03,0.05,0.10")
    p.add_argument("--n-k", default="250,500,1000,2000,4000")
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    run(Path(a.output_dir), a.T, a.n_replicates, [float(x) for x in a.deltas.split(",")],
        [int(x) for x in a.n_k.split(",")], a.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# The canonical cluster batch (Phase 4 + the lock) -- exact tinyx commands

Run these ON THE CLUSTER (tinyx login node), block by block, IN ORDER.
`sbatch --wait` blocks until the job array finishes, so each block can be
pasted whole; if you prefer, drop `--wait` and watch `squeue -u $USER`
between blocks instead. Every batch job sources `hpc/env.local.sh` itself.

## Block 0 -- pre-flight (STOP if anything fails)

```bash
source /etc/profile && module load python/3.12-conda
cd ~/my_repos/CAFA_exp
git pull                                   # the new scripts must be here
source hpc/env.local.sh
source activate "$CAFA_ENV"
export PYTHONPATH="$PWD/src:$PYTHONPATH"
mkdir -p "$RESULTS_ROOT/logs"

python scripts/verify_bugs.py              # expect ALL PASS (freeze incl.)
pytest -q                                  # expect all green (~3 min)
ls configs/committed_v2_*_ts0.json         # canonical ts0 commits present
ls configs/committed_v2_*_ts[12].json 2>/dev/null && echo "WARNING: ts1/ts2 configs present BEFORE the batch - they must NOT be the local ones"
```

## Block A -- Phase 2 canonical (eps cells 8-15, ts0)

```bash
sbatch --wait --array=8-15 hpc/pool_rollout.slurm
for d in mnist tabular:adult tabular:MiniBooNE tabular:spambase; do
  python scripts/probe_commit.py --dataset $d --train-seed 0 --extend-edges
done   # prints "alpha unchanged: <value>" per dataset - CHECK it
sbatch --wait --array=8-15 hpc/eval_sweep.slurm
```

## Block B -- Phase 3 canonical (train seeds 1 and 2; each derives its OWN alpha)

```bash
for ts in 1 2; do
  sbatch --wait hpc/train_backbone_v2.slurm $ts
  sbatch --wait --array=0-7 hpc/pool_rollout.slurm $ts
  for d in mnist tabular:adult tabular:MiniBooNE tabular:spambase; do
    python scripts/probe_commit.py --dataset $d --train-seed $ts
  done   # NOTE the printed floor -> alpha per seed (step crossings are the rule working)
  sbatch --wait --array=0-7 hpc/eval_sweep.slurm $ts
done
```

## Block C -- alpha-sweep, anchored to CLUSTER floors (login node, ~10 min)

```bash
python scripts/alpha_sweep.py --all --grid-from-floor
```

## Block D -- Phase 4: score ablation (margin; detecting datasets + mnist)

```bash
sbatch --wait --array=17-19 hpc/pool_rollout.slurm
for d in tabular:adult tabular:MiniBooNE mnist; do
  python scripts/probe_commit.py --dataset $d --train-seed 0 --extend-edges --score margin
done   # again check "alpha unchanged"
sbatch --wait --array=17-19 hpc/eval_sweep.slurm
python scripts/phase4_score_ablation.py    # invariant check must print PASS
```

## Block E -- the lock (login node)

```bash
python scripts/analyze_results.py
python scripts/phase2_analyze.py
python scripts/phase3_report.py
python scripts/make_figures_v2.py
python scripts/make_canonical_results.py --out CANONICAL_RESULTS.md

# artifact completeness: the per-resplit JSONs MUST reach git
cp metrics_v2/*.json results_committed/metrics/
cp analysis_v2/RESULTS.md analysis_v2/PHASE2_READOUT.md analysis_v2/PHASE3_REPORT.md \
   analysis_v2/PHASE4_SCORE_ABLATION.md analysis_v2/ALPHA_SWEEP.md \
   analysis_v2/*.csv results_committed/
mkdir -p results_committed/figures && cp figures_v2/*.png figures_v2/*.pdf results_committed/figures/

# final gates
python scripts/verify_bugs.py && pytest -q

git add results_committed/ configs/committed_v2_*.json CANONICAL_RESULTS.md \
        repro/requirements.lock.txt
git status                                  # VERIFY the metrics JSONs are staged
git commit -m "canonical lock: phases 2-4 + alpha-sweep (cluster, ts0-2)"
git tag canonical-v2
git push && git push --tags
```

## Gotchas already paid for (do not repeat)

- Batch jobs do NOT inherit login exports; the slurm scripts source
  `hpc/env.local.sh` themselves -- but the `--output=` flag on sbatch expands
  in YOUR shell, so `source hpc/env.local.sh` + `mkdir -p "$RESULTS_ROOT/logs"`
  first (Block 0 does this) or omit the flag.
- TinyGPU requires `--gres=gpu:1` on EVERY job; all shipped slurm files have it.
- If the terminal seems to print nothing, check artifacts -- it has swallowed
  stdout before, harmlessly.
- NEVER copy local ts1/ts2 committed configs to the cluster; Block B derives
  them fresh from the cluster probes.
- Do NOT `--force` the canonical ts0 configs; only `--extend-edges` touches
  them (and asserts alpha unchanged).

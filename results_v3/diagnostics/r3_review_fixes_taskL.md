I applied both Task L fixes. The three required test files pass: `24 passed in 85.86s (0:01:25)`.

**Fix 1: an explicitly empty tag is now a usage error**
- **What changed:**
  - `scripts/drive_v3.py:87-88`: `checkpoint_tag_arg` raises `argparse.ArgumentTypeError("empty tag: omit the flag for the untagged protocol paths")` when given `""`. Its docstring (84-86) says that internal callers still get `validate_checkpoint_tag(None/"") -> None`. Module docstring line 35-36 updated.
  - `scripts/run_repairs_v3.py:18`: one docstring line saying that `--repair-tag ""` is a usage error (exit 2). The code already uses `checkpoint_tag_arg`, so nothing else changed there.
  - `train_backbone_v3.py` and `run_pool_rollout_v3.py` already use the same function, so they pick this up with no code change.
- **How it is tested** (in `tests/test_checkpoint_tag_v3.py`):
  - `test_tag_helpers` (64-66): `checkpoint_tag_arg("")` raises with the exact message, `checkpoint_tag_arg("repair")` still returns `"repair"`, and `validate_checkpoint_tag("")` still returns `None`.
  - `test_train_backbone_overrides_and_parser` (117-120) and `test_rollout_parser` (130-134): both parsers reject `--checkpoint-tag ""` and `--checkpoint-tag=` with exit 2 and "empty tag" on stderr.
  - New `test_empty_tag_is_a_usage_error` (363-): `drive_v3` (backbones and rollouts phases, both spellings) and `run_repairs_v3 --repair-tag ""` (both spellings) exit 2 with the full `argument --...: empty tag: ...` message and print no driver or repair lines. The same `run_repairs_v3` call without the flag still lists the round-2 `policy_change` job.
  - Real roots, read-only dry runs: the reviewer's repro 2 (`run_repairs_v3 ... --repair-tag "" --dry-run --force`) now exits 2 with that error, and so does `drive_v3 --checkpoint-tag ""`.

**Fix 2: `--width-mult` / `--p-full` without `--checkpoint-tag` is a usage error**
- **What changed:** `scripts/train_backbone_v3.py:91-94`: right after `parse_args`, and before the config, paths or data are loaded, it calls `p.error("--width-mult/--p-full change the protocol backbone; give --checkpoint-tag so it is written to checkpoints_v3_<tag>/")`. `--epochs` alone is not affected. The module docstring (21-23) and the help text of both flags (61-64) say this now.
- **How it is tested:**
  - New `test_train_backbone_overrides_need_tag` (137-), on a tmp root with a fake protocol checkpoint and a patched `load_pool_v3`:
    - `--width-mult 4`, `--p-full 0.3` and the full Task-L overrides without a tag each exit 2 with the exact message.
    - The reviewer's repro 1 (`--checkpoint-tag "" --width-mult 1 --p-full 0.3 --epochs 1`) exits 2 with the empty-tag message.
    - In all four cases no data is loaded, the protocol checkpoint bytes are unchanged, and no `checkpoints_v3_*` folder is created.
    - Then `--epochs 1 --max-train 16` without a tag runs: it writes `checkpoints_v3/fashionmnist_ts0.pt` with no `checkpoint_tag` in the meta, `meta["training"] == dict(config, epochs=1)`, and the config's `width_mult`.
  - `test_train_backbone_overrides_and_parser` (107-113): the old `csv:physionet --width-mult 4` call now hits the tag error. I added a tagged call so the "image_patches only" error is still exercised through `main`.
- **README and dry-run lines:** all of them pass `--checkpoint-tag repair` together with the overrides, so they are unaffected.
  - `hpc/README_v3.md`: line 205 (`CAFA_EXTRA=` together with `CAFA_DRIVER_FLAGS=`), lines 222-223 (the dry-run command) and line 271 (the laptop `drive_v3` line).
  - `hpc/dry_run_v3.sh`: lines 16-17.
  - `test_hpc_v3::test_hpc_dry_run_task_l_lines`: still passes.
  - A real-root `drive_v3 --checkpoint-tag repair --extra-args="--epochs 60 --width-mult 4 --p-full 0.3" --dry-run` still prints the combined command.

**Check that the tests fail without the fixes:** I ran the tests against copies in `scratchpad/fix_L/m1` and `m2`, each with one fix taken out; the repo was not touched.
- Without fix 1: 5 tests fail.
- Without fix 2: 2 tests fail.

**pytest summary lines**
- `tests/test_checkpoint_tag_v3.py`: `12 passed in 9.16s`
- `tests/test_checkpoint_tag_v3.py tests/test_hpc_v3.py tests/test_v3_scripts.py`: `24 passed in 85.86s (0:01:25)`

**Not applied:** nothing. I wrote nothing under `F:/CAFA_results` or `configs/`, ran no git operations, and edited only the four allowed files.

Files:
- F:/FAU/PhD/Side Quest/CAFA_exp/scripts/drive_v3.py
- F:/FAU/PhD/Side Quest/CAFA_exp/scripts/train_backbone_v3.py
- F:/FAU/PhD/Side Quest/CAFA_exp/scripts/run_repairs_v3.py
- F:/FAU/PhD/Side Quest/CAFA_exp/tests/test_checkpoint_tag_v3.py
# VolumeLibrary Fortran Build and Remediation

Planning and tooling for the National Volume Estimator Library (NVEL) on this fork: warning cleanup, repo-native builds, and Python regression tests.

## Relationship to upstream and FVS

| Role | Repo |
|------|------|
| Upstream NVEL | [FMSC-Measurements/VolumeLibrary](https://github.com/FMSC-Measurements/VolumeLibrary) |
| This fork | Warning fixes + test infrastructure; PR upstream when batches are ready |
| FVS (downstream) | [ForestVegetationSimulator](https://github.com/USDAForestService/ForestVegetationSimulator) embeds NVEL at `volume/NVEL` |

## Workstreams

| Phase | Description | Doc |
|-------|-------------|-----|
| **0** | Python ctypes wrapper, `libnvel.so`, pytest goldens | [`tests/README.md`](../tests/README.md) |
| **1** | gfortran `-Wall` warning remediation | [PLAN.md](PLAN.md) |

Phase 0 infrastructure is in place. Execute Tier A warning batches only after recording pytest goldens.

## Documentation

| Doc | When to read |
|-----|----------------|
| [PLAN.md](PLAN.md) | Choosing batches, tier rules, success criteria |
| [upstream-workflow.md](upstream-workflow.md) | Opening PRs to FMSC (two-track git workflow) |
| [upstream_pr_template.md](upstream_pr_template.md) | Filling in upstream PR evidence |
| [warnings_progress.md](warnings_progress.md) | Batch status tracker |

## Files in this directory

### Active

| File | Purpose |
|------|---------|
| [PLAN.md](PLAN.md) | Remediation plan, tiers, batches, verification |
| [upstream-workflow.md](upstream-workflow.md) | Two-track git workflow for upstream PRs |
| [upstream_pr_template.md](upstream_pr_template.md) | Upstream PR evidence template |
| [warnings_progress.md](warnings_progress.md) | Batch status tracker |
| [nvel_fortran_sources.txt](nvel_fortran_sources.txt) | Canonical source list (121 root `.f`/`.for`) |
| [build_flags.conf](build_flags.conf) | gfortran flags for this project |
| [generate_source_manifest.py](generate_source_manifest.py) | Regenerate `nvel_fortran_sources.txt` |
| [build_gfortran_warnings.sh](build_gfortran_warnings.sh) | Compile sources, capture warnings |
| [build_gfortran_shared.sh](build_gfortran_shared.sh) | Compile + link `build/libnvel.so` |
| [parse_build_warnings.py](parse_build_warnings.py) | Parse build log → inventory CSV |
| [compare_warnings.py](compare_warnings.py) | Diff inventory vs baseline |
| [check_warnings.sh](check_warnings.sh) | Warning regression orchestration |
| [warnings_inventory_baseline.csv](warnings_inventory_baseline.csv) | Repo-native baseline (**2,038** warnings in 102 files; gfortran 13) |
| [warnings_summary_baseline.md](warnings_summary_baseline.md) | Baseline tier/category stats (generated from the CSV) |

## Quick start

### Build and test (Phase 0)

```bash
python3 fortran_build/generate_source_manifest.py   # if manifest stale
chmod +x fortran_build/build_gfortran_shared.sh
fortran_build/build_gfortran_shared.sh
pip install pytest
pytest tests/ -v
```

Record goldens before Tier A edits:

```bash
python3 tests/record_goldens.py
```

### Warning regression

Matches the GitHub Actions `warnings` job (`ubuntu-latest`, apt `gfortran`):

```bash
chmod +x fortran_build/check_warnings.sh
fortran_build/check_warnings.sh
```

### Rebaseline

After a batch clears warnings, `check_warnings.sh` keeps reporting the *old* baseline until you
move it. **Regenerate straight into the baseline filenames — do not copy the current pair over
them:**

```bash
python3 fortran_build/parse_build_warnings.py fortran_build/gfortran_build.log \
  -o fortran_build/warnings_inventory_baseline.csv \
  -s fortran_build/warnings_summary_baseline.md
python3 fortran_build/compare_warnings.py          # must now report PASS, delta +0
```

Copying `warnings_inventory.csv` / `warnings_summary.md` onto the baseline pair *appears* to work,
but the summary embeds the name of the inventory it was generated from — so the copy leaves
`Inventory: warnings_inventory.csv` in a file that is actually the baseline, pointing readers at a
gitignored artifact. Regenerating with `-o`/`-s` sets it correctly.

Then record the move in [warnings_progress.md](warnings_progress.md) — add a dated **Rebaseline
history** row with old → new totals and the trigger, and refresh the count tables in
[PLAN.md](PLAN.md). Note that `compare_warnings.py` keys on `(file, line, column, …)`, so if a
fix shifted line numbers, say so in that row: surviving warnings below the shift get re-keyed as
"new" even though nothing regressed.

Both `*_baseline` files are committed; the un-suffixed `warnings_inventory.csv` and
`warnings_summary.md` are generated and gitignored.

### Fix a batch and verify

1. Tier A: `python3 tests/record_goldens.py` first, then fix (see [PLAN.md](PLAN.md))
2. `fortran_build/check_warnings.sh`
3. `pytest tests/ -v`
4. Rebaseline (above) and update [warnings_progress.md](warnings_progress.md) + [PLAN.md](PLAN.md)
5. Open upstream PR per [upstream-workflow.md](upstream-workflow.md); use [upstream_pr_template.md](upstream_pr_template.md) for evidence

### Optional FVS smoke

Before a large upstream PR, see [PLAN.md](PLAN.md).

## Compiler notes

| Toolchain | Use on this fork |
|-----------|------------------|
| **gfortran** (GitHub Actions `ubuntu-latest`) | Warning baseline and CI regression gate |
| **Dev container** (follow-up PR) | Local development; rebaseline when adopted |
| **ifort** | Production DLL on Windows; manual spot-check after Tier A |

## Approach

- Prefer **real code fixes** (casts, remove dead code, align declarations)
- Suppress only when a shared interface requires unused dummy arguments
- Tier C (`large_stack_array`): defer — single-threaded usage
- Separate upstream PRs for wrapper infrastructure vs warning fixes

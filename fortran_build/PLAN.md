# VolumeLibrary Fortran Warning Remediation Plan

## Goal

Reduce gfortran `-Wall` warnings across **repo-native NVEL sources**, without changing volume/biomass numerical results for regression-tested scenarios.

## Strategy

This fork treats VolumeLibrary as a **self-contained project**:

- Own source manifest (`nvel_fortran_sources.txt`), compiler flags (`build_flags.conf`), warning baseline, and pytest golden tests
- **Phase 0** (prerequisite): Python ctypes wrapper + `libnvel.so` — see [`tests/README.md`](../tests/README.md)
- **Phase 1**: Warning remediation batches backed by warning CI + pytest
- **FVS** is a downstream consumer (embeds NVEL at `volume/NVEL`); optional manual smoke before large upstream PRs — not a daily gate

Upstream target: [FMSC-Measurements/VolumeLibrary](https://github.com/FMSC-Measurements/VolumeLibrary)

Related: [`tests/README.md`](../tests/README.md), [`upstream-workflow.md`](upstream-workflow.md)

## Execution order

```mermaid
flowchart LR
  manifest[Source manifest + flags]
  wrapper[Python wrapper + libnvel.so]
  goldens[Record pytest goldens]
  warnings[Warning fix batches]
  upstream[PR to FMSC]

  manifest --> wrapper --> goldens --> warnings --> upstream
```

| Phase | Work | Gate | Status |
|-------|------|------|--------|
| 0 | Repo manifest, shared library, ctypes, initial goldens | `pytest tests/` passes | COMPLETE |
| 1a | Re-capture warning baseline on repo-native manifest | Inventory committed | COMPLETE |
| 1b | Tier A/B fix batches | Warning count down; pytest unchanged for Tier A | IN PROGRESS — `sf_zero.f`, `f_west.f`, `f_other.f`, `f_alaska.f` done; `r10vol1.f` next |
| 2 | Upstream PRs to FMSC | Fork CI green; optional FVS smoke | IN PROGRESS — `sf_zero.f` merged (FMSC#13); `f_west.f` (FMSC#15) and `f_other.f` (FMSC#16) open |

## Context

### Repo-native baseline (active)

| Item | Value / path |
|------|----------------|
| Source manifest | `nvel_fortran_sources.txt` (121 files) |
| Remediation baseline | **2,110** warnings in **102** files — Tier A/B/C **363 / 1,738 / 9** |
| Current | **1,944** warnings in **101** files — Tier A/B/C **211 / 1,724 / 9** (2026-08-08, gfortran 13.3.0) |
| Cleared so far | **166** (70 `f_west.f`, 54 `f_other.f`, 40 `f_alaska.f`, 2 `sf_zero.f`) |
| Numerical tests | `tests/goldens/cases.json` + `pytest tests/` |

### What "remediation baseline" means

The fixed denominator for progress: the warning count of **upstream release 0260729 with none of our fixes applied**, measured with the *corrected* parser. It is not a historical capture — the counts recorded before 2026-08-07 came from a parser that dropped 743 `-Wtabs` warnings, so they cannot be compared against current numbers.

It was reconstructed by compiling the two files we have changed at their pre-fix revisions (`f_west.f` at `356edd3`, `sf_zero.f` at `50e6a7b^`) and parsing them with the corrected parser; every other file is byte-identical to upstream, and each file is compiled independently, so its current count is also its baseline count. Cross-check: the reconstruction reproduces Tier A 363, which `warnings_progress.md` recorded independently before any of our fixes.

**Recompute this row on the next upstream sync** — upstream changes move the denominator (the 20260729 sync itself cleared 2 `uninitialized` warnings that we never touched).

Suggested compiler flags (document in `build_flags.conf`):

```
-fPIC -g -cpp -Wall
-ffpe-trap=invalid,zero,underflow,overflow,denormal -fbacktrace
```

Add `-D` defines only when needed; do not assume FVS `-DCMPgcc` unless a specific `#ifdef` branch requires it.

## Tier classification

**Baseline** is the fixed denominator defined above — upstream 20260729 with none of our fixes applied. **Current** and **Files** come from `warnings_inventory_baseline.csv` (2026-08-07 capture on the VolumeLibrary manifest); `Files` counts files with at least one *current* warning in that category. Regenerate the Current and Files columns on every rebaseline, and the Baseline column only on an upstream sync — see the rebaseline history in [warnings_progress.md](warnings_progress.md).

### Tier A — Fix first (correctness risk)

| Category | Baseline | Current | Files | Typical fix |
|----------|--------:|--------:|------:|-------------|
| `type_conversion` | 317 | 168 | 36 | Explicit `REAL()` / `DBLE()` / `INT()` / single-precision literals |
| `character_truncation` | 29 | 29 | 2 | Substring `(1:n)` or align declarations |
| `uninitialized` | 15 | 14 | 8 | Initialize at declaration or before use |
| `integer_division` | 2 | **0** | 0 | Use `REAL()` / `DBLE()` before division or explicit `NINT()` |
| **Tier A total** | **363** | **211** | | 152 cleared (42%) |

**Tier A batches require pytest goldens** recorded before edits. Re-run `pytest` after fixes.

### Tier B — Hygiene

| Category | Baseline | Current | Files | Typical fix |
|----------|--------:|--------:|------:|-------------|
| `tab_character` | 1,043 | 1,031 | 43 | Spaces instead of tabs |
| `unused_variable` | 552 | 552 | 54 | Remove dead locals |
| `unused_dummy_argument` | 82 | 82 | 37 | Remove from interface or document + scratch use |
| `unused_label` | 32 | 30 | 15 | Remove unused labels |
| `deleted_feature` | 27 | 27 | 6 | Replace deleted Fortran features (e.g. `PAUSE`, `DO` without loop var) |
| `extension` | 2 | 2 | 2 | Remove or guard non-standard extensions |
| **Tier B total** | **1,738** | **1,724** | | 14 cleared |

`tab_character` is now the largest single category. It jumped 302 → 1,043 on 2026-08-07 when `parse_build_warnings.py` was fixed to record gfortran's driver-level `f951:` warnings; the tabs were always there, only the measurement changed.

Tier B batches need warning regression only.

### Tier C — Defer

| Category | Baseline | Current | Files | Notes |
|----------|--------:|--------:|------:|-------|
| `large_stack_array` | 9 | 9 | 3 | Document; NVEL single-threaded usage |

## Fix batches

Batch ordering unchanged. Per-file counts below are exact Tier A totals from the repo-native baseline (`warnings_inventory_baseline.csv`, 2026-08-08).

### Batch 1 — Tier A regional shape files

Highest impact, related patterns (`REAL(8)` → `REAL*4` narrowing):

Tier A counts, baseline → current:

| # | File | Baseline | Current | Status |
|---|------|--------:|--------:|--------|
| 1 | `f_west.f` | 68 | **0** | **done** — 1 documented dummy arg (Tier B) remains |
| 2 | `f_other.f` | 53 | **0** | **done** — 53 narrowing assignments + the line-70 tab; 20 new R2/R3/R4 goldens |
| 3 | `f_alaska.f` | 29 | **0** | **done** — 29 narrowing stores + 11 tabs; 18 new R10 goldens |
| 4 | `r10vol1.f` | 28 | 28 | next |
| 5 | `honer.f` | 21 | 21 | pending |
| 6 | `f_ingy.f` 14, `sf_taper.f` 12, `nsvb.f` 12, `r10volo.f` 10, `fiaeq2nveleq.for` 10 | 58 | 58 | pending |

`sf_zero.f` (2 `integer_division`, batch 0d) was cleared ahead of this batch as a workflow rehearsal and is not listed above.

**Patterns — verify which applies per file, they need different fixes:**

- *Narrowing assignment.* `REAL*8` coefficient or intermediate stored into a `REAL*4` scalar. Fix with an explicit `REAL()` at the assignment. This is a provable no-op: the compiler already emits that conversion.
- *Double literal in a `DATA` block targeting a `REAL*4` array.* Fix with a single-precision suffix (`d0` → `e0`); same stored bits.

Do **not** assume the second pattern. It held for `f_west.f`, but every `DATA` target in `f_other.f` (`BK`, `F`, `V`) and in `f_alaska.f` (`F`, `SUBF`, `V`) is genuinely `REAL*8`, so no `DATA` statement in either file warns at all — those batches were 100% narrowing assignments. Note also that `d0` → `e0` is only safe inside a `DATA` initializer; in an *arithmetic expression* the double literal promotes the whole expression, so changing the suffix drops it to single precision and can move results (see `f_other.f:876`).

Add pytest golden cases for each region touched, and confirm they actually reach the file.
None of the 37 pre-batch cases reached `f_other.f`; the 20 added for Batch 1b were verified with a gcov build to execute all 53 edited lines. Likewise none of the 57 pre-batch cases reached `f_alaska.f`; the 18 added for Batch 1c cover all 29 edited lines.

A third pattern showed up in `f_alaska.f`: the *same* statement can warn in one file and not another because the destination is declared differently. `DMEDIAN`/`DFORM`/`DRATIO` are `REAL*8` in `f_west.f` and `f_other.f` but `REAL*4` in `f_alaska.f`. Wrap, do not widen — widening is arguably the correct fix but moves numbers, so it belongs in a correctness PR, not a warning batch.

### Batch 2 — Tier A taper/volume routines

`r6vol1.f`, `formclas.f`, `r10tap.f`, `r1tap.f`, `r2tap.f`, `r5harv.f`, `r8vol2.f`, `scrib.f`, `sf_yhat.f`, `volinit.f`, `r6dibs.f`, `volinit2.f`, `r8clkdib.f`

### Batch 3 — Wrapper / entry points (high warning count, mixed tiers)

`fia_vol_r5610.for`, `vollibfia.f`, `volumelibrary.f`, `pmtprofile.f`, `r9clark.f`, `r9clarkdib.f`, `vollibcs.f`

Fix after underlying routines stabilize. Expand pytest coverage for `vollib_r` paths.

### Batch 4 — Tier B bulk

Unused variables and tab characters across remaining files. At 1,736 warnings this is now larger than every other batch combined, and `tab_character` alone (1,043 across 45 files) is the bulk of it.

Tabs are whitespace-only and carry no numerical risk, but they touch a lot of lines, which has two consequences worth planning around: `compare_warnings.py` keys on `(file, line, column, …)`, so a tab batch must not also shift line numbers; and a whitespace-heavy diff is harder to get accepted upstream than a targeted fix. Consider splitting tabs into their own per-file commits, and clearing Tier A in a file before detabbing it.

### Batch 5 — Tier C

Document `large_stack_array` warnings; optional `-fmax-stack-var-size` note.

## Verification

Commands: see [README.md](README.md) quick start (`check_warnings.sh`, `build_gfortran_shared.sh`, `pytest`).

### Warning regression (every batch)

Run `fortran_build/check_warnings.sh` (or the underlying `build_gfortran_warnings.sh` + `parse_build_warnings.py` + `compare_warnings.py`). Compare to `warnings_inventory_baseline.csv`. Fail if total count increases or new Tier A warnings appear in touched files.

### Numerical regression (Tier A and wrapper batches)

Record goldens with `python3 tests/record_goldens.py` **before** Tier A edits, then `pytest tests/ -v` after fixes. Golden outputs must stay within tolerance (default `1e-3`).

### Optional FVS smoke (before large upstream PRs)

Not required per batch. FVS embeds this repo and may compile a slightly different file subset; use as a courtesy check if FMSC asks or before merging large Tier A work. In ForestVegetationSimulator: point `volume/NVEL` at your commit, then `cd bin && make clean && make FVSpn` and `cd ../tests/FVSpn && make`.

### ifort (manual, Windows)

Production DLL builds use Intel ifort (`compdll.bat`, `vollib.vfproj`). Spot-check Release builds after Tier A batches if you maintain DLL releases. Not a CI gate.

## Upstream PRs

After a batch passes warning and numerical gates on the fork, follow the two-track git workflow in [upstream-workflow.md](upstream-workflow.md). Fill in [upstream_pr_template.md](upstream_pr_template.md) for the FMSC PR body. Do **not** bundle Phase 0 wrapper infrastructure with warning-fix PRs to upstream.

## Out of scope

**FVS repo fixes** (not NVEL sources): `base/comprs.f`, `vbase/initre.f`, `fire/`, etc.

**Deferred wrapper work:** `VOLLIBCS`, biomass, merchandising rules, PyPI packaging.

## Success criteria

- Repo-native warning baseline captured and trending down
- Zero Tier A warnings in active capture (or documented exceptions)
- `pytest tests/` passes; goldens cover regions/equations in each Tier A batch
- Upstream PRs accepted by FMSC with fork CI evidence
- Optional FVS smoke documented when run

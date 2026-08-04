# VolumeLibrary Warning Remediation Progress

## Baseline

| Artifact | Path | Notes |
|----------|------|-------|
| Active inventory | `warnings_inventory_baseline.csv` | **1,297** rows; GitHub Actions `ubuntu-latest` (gfortran 13) |
| Active summary | `warnings_summary_baseline.md` | Tier A: 293, B: 995, C: 9 |
| Source list | `nvel_fortran_sources.txt` | 121 root `.f`/`.for` files |
| Build log | `gfortran_build.log` | From `build_gfortran_warnings.sh` |
| Current inventory | `warnings_inventory.csv` | From `parse_build_warnings.py` |
| FVS reference | `reference/fvs_migration/` | Historical 1,370-warning FVS inventory |

### Rebaseline history

| Date | Baseline | Trigger |
|------|----------|---------|
| 2026-08-04 | 1,367 → 1,297 (Tier A 361 → 293) | Batch 1 `f_west.f` fixes: 70 warnings cleared, 0 new. Line-number drift is confined to `FDBT_C1` and the `SHP_W5` comment; every warning below both insertion points was eliminated, so no surviving warning was re-keyed. |
| 2026-08-04 | 1,369 → 1,367 (Tier A 363 → 361) | Upstream sync to `20260729`. Upstream added `BH=4.5` at two `f_west.f` entry points, clearing 2 `bh` `-Wmaybe-uninitialized` Tier A warnings. Remaining churn is line-number drift only (`f_west.f`, `r6vol1.f`, `r8init.f`); no new distinct warnings. |

## Approach

- Real code fixes preferred over suppression
- PR fixes upstream to FMSC-Measurements/VolumeLibrary — see [upstream-workflow.md](upstream-workflow.md)
- Phase 0 (wrapper + pytest): **done**
- Numerical gate: `pytest tests/`; optional FVS smoke before large upstream PRs

## Batch status

| Batch | Scope | Status | Warnings removed | Notes |
|-------|-------|--------|------------------|-------|
| 0b | Python wrapper + pytest goldens | **done** | — | `build/libnvel.so`, `tests/` |
| 0c | Repo-native warning baseline | **done** | — | 1,371 warnings; CI `ubuntu-latest` gfortran |
| 0d | Tier A: `sf_zero.f` `integer_division` (workflow rehearsal) | **done** | 2 | First upstream PR candidate; see notes below |
| 1a | Tier A+B: `f_west.f` | **done** | 70 | 71 → 1; bit-identical over 7,290 cases |
| 1b | Tier A: `f_other.f`, `f_alaska.f` | pending | — | Record goldens first |
| 2 | Tier A: taper/volume (`r10vol1.f`, `honer.f`, …) | pending | — | |
| 3 | Wrappers (`volumelibrary.f`, `vollibfia.f`, …) | pending | — | |
| 4 | Tier B bulk | pending | — | |
| 5 | Tier C stack arrays | deferred | — | |

## Fixes applied in this repo

| File | Date | Warnings | Summary |
|------|------|----------|---------|
| `sf_zero.f` | 2026-07-26 | 2 `integer_division` | `AMACH`'s `RM1`/`DM1` exponent-halving rewritten as `REAL`/`DBLE` division + explicit `INT()`/`IDINT()` truncation (was raw integer division). Bit-identical `R1MACH`/`D1MACH` output confirmed for indices 1-5; new regression test `tests/test_sf_zero_machine_constants.py`. Upstream PR: pending. |
| `f_west.f` | 2026-08-04 | 67 `type_conversion`, 2 `unused_label`, 1 `uninitialized` | 32 `DATA` `d0` literals feeding `REAL*4 r25`/`r34` rewritten as `e0` (same stored bits — the `REAL*4` declaration is deliberate: these regional coefficients carry 4–5 significant digits, and `RFLW`/`RHFW` are `REAL*4` outputs). 35 `REAL*8`→`REAL*4` narrowing assignments wrapped in explicit `REAL()`. `FDBT_C1` result initialized (`JSP` outside 3–5 returned an unset value). Dead labels 40/50 removed. 33 new Flewelling westside golden cases; bit-identical over a 7,290-case sweep. Upstream PR: pending. |

## Suppressions retained

| File | Warning | Reason |
|------|---------|--------|
| `f_west.f:303` | `unused_dummy_argument` `geosub` (`SHP_W5`) | Red cedar has no regional coefficients, so `SHP_W5` never reads `GEOSUB` (`SHP_W3`/`SHP_W4` use it to look up `r25`/`r34`). The argument cannot be dropped: `sf_shp.f:43` dispatches `SHP_W3`/`W4`/`W5` through one uniform signature. Documented in place rather than suppressed. |

## Next steps

1. Open the `f_west.f` upstream PR (fork CI green first)
2. Continue Batch 1 on `f_other.f` (53) and `f_alaska.f` (30) — record goldens first
3. `check_warnings.sh` + `pytest` after each batch

## Reported to upstream separately (not fixed here)

| File | Issue |
|------|-------|
| `f_west.f:263` | `SHP_W4` reads `f(48)`, but its `DATA` statements only initialize `f(45)`–`f(47)`. gfortran cannot flag this (array element). Static storage means the term currently evaluates as zero, so behaviour is stable — but the intended coefficient is missing. Not fixed: any substituted value would change results. |
| `f_west.f` `FDBT_C1` | `RATIO` is assigned only inside `IF(GCODE(ID).EQ.GEOSUB)` within `DO 100`/`DO 200`, so an unmatched `GEOSUB` leaves it unset. Same defect class as the flagged result variable, but not compiler-visible. |

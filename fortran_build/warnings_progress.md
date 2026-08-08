# VolumeLibrary Warning Remediation Progress

## Baseline

| Artifact | Path | Notes |
|----------|------|-------|
| Active inventory | `warnings_inventory_baseline.csv` | **1,984** rows in 101 files; gfortran 13.3.0 |
| Active summary | `warnings_summary_baseline.md` | Tier A: 240, B: 1,735, C: 9 |
| Remediation baseline | fixed denominator, see [PLAN.md](PLAN.md#what-remediation-baseline-means) | **2,110** (Tier A 363, B 1,738, C 9) — upstream 20260729 with no fixes applied. **126 cleared.** |
| Source list | `nvel_fortran_sources.txt` | 121 root `.f`/`.for` files |
| Build log | `gfortran_build.log` | From `build_gfortran_warnings.sh` |
| Current inventory | `warnings_inventory.csv` | From `parse_build_warnings.py` |
| FVS reference | `reference/fvs_migration/` | Historical 1,370-warning FVS inventory |

### Rebaseline history

| Date | Baseline | Trigger |
|------|----------|---------|
| 2026-08-07 | 2,038 → 1,984 (Tier A 293 → 240, B 1,736 → 1,735) | Batch 1b `f_other.f` fixes: 54 warnings cleared (53 `type_conversion` + 1 `tab_character`), 0 new. **No line-number drift** — every edit is in-place on an existing line, the file is 905 lines before and after, and `git diff --stat` reports 60 insertions / 60 deletions. No surviving warning was re-keyed, and `f_other.f` leaves the inventory entirely (102 → 101 files). |
| 2026-08-07 | 1,297 → 2,038 (Tier A 293, unchanged) | **Measurement correction, not a regression.** `parse_build_warnings.py` paired every warning against a preceding `file:line:col:` line, but gfortran emits driver-level warnings as `f951: Warning: …` with no such prefix. 743 `-Wtabs` warnings were therefore dropped, and the 2 that happened to trail an unconsumed location line were recorded against the wrong file and line (`r1kemp.f:13` for what is really `r1tap.f:127`; `r8clkdib.f:11` for `r8init.f:21`). `f951:` warnings are now self-located from the message text and attributed to the compile unit. `tab_character` 302 → 1,043, matching the 1,043 tab lines in the log exactly; all 743 recovered locations were verified to contain a real tab. The other 996 rows are byte-identical, and Tier A/C are untouched. 8 files enter the inventory for the first time (`fwinit.f`, `r3d2hv.f`, `r4d2h.f`, `r6vol.f`, `r8vol1.f`, `r8vol.f`, `r9logs.f`, `vernum.f`); `profile2.f` (107 tabs), `r8vol2.f` (94) and `r9clark.f` (49) were previously invisible. |
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
| 1b-pre | Tooling: `parse_build_warnings.py` dropped `f951:` warnings | **done** | — | Measurement fix; +741 rows |
| 1b | Tier A: `f_other.f` (54) | **done** | 54 | 54 → 0; bit-identical over 12,960 cases; 20 new goldens |
| 1c | Tier A: `f_alaska.f` (41) | pending | — | Split out of 1b |
| 2 | Tier A: taper/volume (`r10vol1.f`, `honer.f`, …) | pending | — | |
| 3 | Wrappers (`volumelibrary.f`, `vollibfia.f`, …) | pending | — | |
| 4 | Tier B bulk | pending | — | |
| 5 | Tier C stack arrays | deferred | — | |

## Fixes applied in this repo

| File | Date | Warnings | Summary |
|------|------|----------|---------|
| `sf_zero.f` | 2026-07-26 | 2 `integer_division` | `AMACH`'s `RM1`/`DM1` exponent-halving rewritten as `REAL`/`DBLE` division + explicit `INT()`/`IDINT()` truncation (was raw integer division). Bit-identical `R1MACH`/`D1MACH` output confirmed for indices 1-5; new regression test `tests/test_sf_zero_machine_constants.py`. Upstream PR: [FMSC#13](https://github.com/FMSC-Measurements/VolumeLibrary/pull/13) — **merged**. |
| `f_other.f` | 2026-08-07 | 53 `type_conversion`, 1 `tab_character` | All 53 narrowing stores wrapped in explicit `REAL()` — a provable no-op, since the compiler already emitted exactly that conversion (the source says so at `f_other.f:355`, "These outcomes are SINGLE precision"). No declaration widening, no reflowing, no inserted lines; the hard tab at line 70 was replaced with spaces in place. `VAR_BH:876,882` look like the `f_west.f` `d0`→`e0` case but are **not**: those `D+01` literals sit in an arithmetic expression, where the double literal promotes the whole expression, so `E+01` would evaluate in single precision and move results — wrapped in `REAL()` instead, literals untouched. 20 new R2/R3/R4 golden cases (none of the previous 37 reached this file); a gcov build confirmed the 20 cases execute all 53 edited lines. Bit-identical `vol[0..14]` over a 12,960-case sweep (18 equations × dbh/height/merch-top/stump/upper-stem grid) against the pre-edit `libnvel.so`; the sweep harness was validated by perturbing one `BK` coefficient in its 6th decimal, which produced 1,160 mismatches. Fork PR: [#17](https://github.com/d-diaz/VolumeLibrary/pull/17). Upstream PR: [FMSC#16](https://github.com/FMSC-Measurements/VolumeLibrary/pull/16) — open, branch `upstream/fix-f_other` off `master` at release 20260731. |
| `f_west.f` | 2026-08-04 | 67 `type_conversion`, 2 `unused_label`, 1 `uninitialized` | 32 `DATA` `d0` literals feeding `REAL*4 r25`/`r34` rewritten as `e0` (same stored bits — the `REAL*4` declaration is deliberate: these regional coefficients carry 4–5 significant digits, and `RFLW`/`RHFW` are `REAL*4` outputs). 35 `REAL*8`→`REAL*4` narrowing assignments wrapped in explicit `REAL()`. `FDBT_C1` result initialized (`JSP` outside 3–5 returned an unset value). Dead labels 40/50 removed. 33 new Flewelling westside golden cases; bit-identical over a 7,290-case sweep. Fork PR: [#14](https://github.com/d-diaz/VolumeLibrary/pull/14). Upstream PR: [FMSC#15](https://github.com/FMSC-Measurements/VolumeLibrary/pull/15) — open. |

## Golden coverage limits (Batch 1b)

Recorded rather than worked around — none blocks the `f_other.f` evidence, since a gcov build
confirms the 20 cases execute all 53 edited lines.

- `VAR_OT`/`COR_OT` and `VAR_BH`/`COR_BH` are reachable only through the 3-point path
  (`VOLEQ(6:6)=='3'`, `fwinit.f:295`). The 2-point cases never enter them.
- Full `COR_*` coverage would need `NEXTRA=2` (two upper-stem points, `sf_3pt.f:146`), but
  `vollib_r` hardcodes `UPSHT2=0.0`/`UPSD2=0.0` (`volumelibrary.f:616-617`), so `NEXTRA=1` is
  the ceiling through the current Python surface and `COR_*` is reached via `sf_yhat3.f:29`.
  `vollib2_r` accepts the second pair but is not bound in `nvel/_routines.py`; binding it was
  out of scope for a warning batch. The both-heights-below-breast-height branches of `COR_OT`
  and `COR_BH` are still covered, by passing an upper-stem point below 4.5 ft
  (`f_other_3pt_*_lowups`).
- The `301FW2W*` lookups were commented out in `voleqdef.f:468-493` in 2024, so those four
  equation strings are passed explicitly rather than derived via `getvoleq_r`.
- `region`/`forest`/`district` are inert on this path — `GEOSUB` comes from `VOLEQ(2:3)`, not
  from the site keys — so those fields in the new cases are documentation only. Verified by
  varying `forest` across `00`/`03`/`06`/`13`/`99` with an explicit `volume_equation`.

## Suppressions retained

| File | Warning | Reason |
|------|---------|--------|
| `f_west.f:303` | `unused_dummy_argument` `geosub` (`SHP_W5`) | Red cedar has no regional coefficients, so `SHP_W5` never reads `GEOSUB` (`SHP_W3`/`SHP_W4` use it to look up `r25`/`r34`). The argument cannot be dropped: `sf_shp.f:43` dispatches `SHP_W3`/`W4`/`W5` through one uniform signature. Documented in place rather than suppressed. |

## Next steps

1. Await review on FMSC#15 (`f_west.f`) and FMSC#16 (`f_other.f`)
2. Batch 1c on `f_alaska.f` (41)
3. `check_warnings.sh` + `pytest` after each batch

### Upstream sync

Fork `main` is **not** behind upstream on any Fortran source. As of 2026-08-08 the only root
sources differing from `upstream/master` are `f_west.f` and `f_other.f`, and both differ
because they carry our fixes that upstream has not merged yet. `vernum.f` returns `20260729`
on **both** sides, despite upstream's commit titled `vollib release 20260731`, so there is no
version drift and the `vernum` golden needs no re-record.

Defer `git merge upstream/master` until FMSC#15/#16 land — there is no content to gain now,
and two hazards to respect when the time comes:

- The merge base is release **20260415**, so a three-dot diff (`main...upstream/master`)
  replays changes both sides already share and reads as though upstream is far ahead. Use a
  two-dot diff (`git diff main upstream/master`) to see real content drift.
- Upstream still holds `vollib/`, `.vs/`, `volbiolibrary.f` and similar at paths this fork
  archived under `_legacy/`. Merging across the 20260415 base can resurrect them or conflict;
  resolve per [FORK.md](../FORK.md).

Merging after the upstream PRs land also relinks the histories and makes future diffs
accurate.

`PLAN.md`'s tier and per-file tables were regenerated from the inventory in the same commit
as this rebaseline; keep them in step on every future rebaseline.

## Reported to upstream separately (not fixed here)

| File | Issue |
|------|-------|
| `f_west.f:263` | `SHP_W4` reads `f(48)`, but its `DATA` statements only initialize `f(45)`–`f(47)`. gfortran cannot flag this (array element). Static storage means the term currently evaluates as zero, so behaviour is stable — but the intended coefficient is missing. Not fixed: any substituted value would change results. |
| `f_west.f` `FDBT_C1` | `RATIO` is assigned only inside `IF(GCODE(ID).EQ.GEOSUB)` within `DO 100`/`DO 200`, so an unmatched `GEOSUB` leaves it unset. Same defect class as the flagged result variable, but not compiler-visible. |
| `f_other.f:24` `BK` | `BK(9,8)` is `REAL*8`, but its `DATA` literals carry no exponent letter, so 28 of them with 8+ significant digits are truncated to single precision before being widened (`12.88990159` stores as `12.8899002…`). This is the *inverse* of the `f_west.f` fix and gfortran cannot see it — widening from the `REAL(4)` value is lossless. Highest-value item on this list. Not fixed: adding `D0` suffixes would change results. |
| `f_other.f:84-127` | `DBHIB` used uninitialized. The `IF`/`ELSE IF` chain has no `ELSE`, so a `JSPR` outside 1–8 reaches `DBTBH = DBHOB - DBHIB` at line 128 with `DBHIB` unset. Identical class to `FDBT_C1`, equally invisible to gfortran. |
| `f_other.f:140` | Unguarded division by `DBTBH`, which line 128 can leave at 0, under `-ffpe-trap=zero`; `B2-DR**B3` is likewise unguarded. An in-source `DW 08/22` comment at line 137 proposes a filter and line 139 implements it for `DR` only. |
| `sf_shp.f:48`, `sf_corr.f:22`, `sf_dfz.f:18`, `brk_up.f:10`, `calcdia.f:535` | Dispatch guards exceed the coefficient arrays. `JSP.LE.30` → `JSPR = JSP-22` reaches 8 against 7-column `F`/`V`; `JSP.LE.30` → `JSPR = JSP-21` reaches 9 against `BK(9,8)`. `fwinit.f:157-235` only ever emits 22–29, so `JSP = 30` is **not currently reachable** — latent robustness item, not a live bug. |
| `fwinit.f:340-364`, `f_other.f:578` | Stale and drifting comments. The `fwinit.f` JSP→model table omits 28 (R2 aspen), 29 (R3 PP) and 33–36. `f_other.f:578` labels the `V(*,5)` block `REGION 2 WHITE PINE` while lines 48, 253 and 431 all call index 5 *White fir*; `V(*,3)` at line 557 has no header comment. Cosmetic, but it misleads anyone cross-checking coefficients by comment. |

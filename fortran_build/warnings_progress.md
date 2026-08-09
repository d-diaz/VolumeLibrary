# VolumeLibrary Warning Remediation Progress

## Baseline

| Artifact | Path | Notes |
|----------|------|-------|
| Active inventory | `warnings_inventory_baseline.csv` | **1,842** rows in 100 files; gfortran 13.3.0 |
| Active summary | `warnings_summary_baseline.md` | Tier A: 176, B: 1,657, C: 9 |
| Remediation baseline | fixed denominator, see [PLAN.md](PLAN.md#what-remediation-baseline-means) | **2,110** (Tier A 363, B 1,738, C 9) — upstream 20260729 with no fixes applied. **268 cleared.** |
| Source list | `nvel_fortran_sources.txt` | 121 root `.f`/`.for` files |
| Build log | `gfortran_build.log` | From `build_gfortran_warnings.sh` |
| Current inventory | `warnings_inventory.csv` | From `parse_build_warnings.py` |
| FVS reference | `reference/fvs_migration/` | Historical 1,370-warning FVS inventory |

### Rebaseline history

| Date | Baseline | Trigger |
|------|----------|---------|
| 2026-08-09 | 1,944 → 1,842 (Tier A 211 → 176, B 1,724 → 1,657) | Batch 1e `r10vol1.f` + `r10tap.f` fixes: 102 warnings cleared (63 `tab_character` + 35 `type_conversion` + 2 `unused_label` + 2 `deleted_feature`), 0 new. The inventory diff is a **pure deletion of 102 rows with 0 added**, verified by set-comparing the two CSVs on `compare_warnings.py`'s own key. `r10vol1.f` drifts +2 lines (1,157 → 1,159) from converting two non-`CONTINUE` `DO` terminators to block `DO`, but **no surviving warning was re-keyed**: everything below both insertion points was cleared in the same batch, and the file's two remaining rows (`unused_dummy_argument` `mtops`/`spflg`) sit at lines 2 and 4, above both sites, still keyed at 2:42 and 4:36. `r10tap.f` is 202 lines before and after. File count 101 → **100** — `r10tap.f` leaves the inventory entirely. |
| 2026-08-08 | 1,984 → 1,944 (Tier A 240 → 211, B 1,735 → 1,724) | Batch 1c `f_alaska.f` fixes: 40 warnings cleared (29 `type_conversion` + 11 `tab_character`), 0 new. **No line-number drift** — every edit is in-place on an existing line, the file is 515 lines before and after, and `git diff --stat` reports 43 insertions / 43 deletions. The inventory diff is a pure deletion of 40 rows with 0 added, so no surviving warning was re-keyed; the file's one remaining warning (`unused_dummy_argument setopt`) is still keyed at line 462. File count stays 101 — `f_alaska.f` does not leave the inventory. |
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
| 1c | Tier A+B: `f_alaska.f` (41) | **done** | 40 | 41 → 1; bit-identical over 3,300 cases; 18 new goldens |
| 1d | Correctness: `SHP_AK` `SUBF` state leak | pending | — | Not a warning fix; see latent-defect note below |
| 1e | Tier A+B: `r10vol1.f` (78) + `r10tap.f` (26) | **done** | 102 | 78 → 2 and 26 → **0**; one shared root cause; **byte-identical machine code** at `-O0` and `-O2`; no goldens possible |
| 2 | Tier A: taper/volume (`honer.f`, …) | pending | — | |
| 3 | Wrappers (`volumelibrary.f`, `vollibfia.f`, …) | pending | — | |
| 4 | Tier B bulk | pending | — | |
| 5 | Tier C stack arrays | deferred | — | |

## Fixes applied in this repo

| File | Date | Warnings | Summary |
|------|------|----------|---------|
| `r10vol1.f` + `r10tap.f` | 2026-08-09 | 35 `type_conversion`, 63 `tab_character`, 2 `unused_label`, 2 `deleted_feature` | **One wrong declaration caused 33 of the 35 Tier A warnings, and deleting the `*8` is the whole fix**: `r10vol1.f:534` and `r10tap.f:25` both declare seven *statement functions* (`BKAC`, `DVA`, `BKWR`, `DVR`, `BB`, `DD2MI`, `DVREDA` — the R10 taper and bark equations) as `REAL*8`, while every dummy and every literal in their bodies is default `REAL(4)`. A statement function's expression is evaluated in its own operand types and converted to the result type *afterwards*, so the `*8` only widened an already-rounded single and every use narrowed it straight back at a `REAL(4)` target — which is exactly what `-Wconversion` reported. Wrapping the 33 call sites in `REAL()` was considered and **rejected**: it preserves the wrong declaration and misleads a later reader into thinking `BB` is legitimately double. Two independent measurements back the one-line fix rather than argument: a discriminating probe (`1e8 + 1.0 - 1e8`, which is `0.0` in single and `1.0` in double) returns `0.0` from a `REAL*8`-declared body at both `-O0` and `-O2`; and the generated assembly for the **entire batch** is **byte-identical apart from the `.file` directive** at both `-O0` and `-O2`. Instruction census on the original `r10vol1.f`: **zero** double-precision arithmetic instructions, 605 single-precision, 0 `cvtss2sd`/`cvtsd2ss`, 37 `powf` — identical after. The `*8` generated no double-precision code at all. Both comparisons were validated by perturbing a coefficient (`BB`'s `0.8467` → `0.8467001`; `DVR`'s `5.17703194` → `5.17713194`) and confirming the diff becomes non-empty — note that a 9th-significant-digit perturbation does *not* register, which independently confirms single-precision storage. Also fixed: 2 real→integer sites (`r10vol1.f:119` `NUMSEG = INT(HT1PRD)`, matching the already-explicit `NSEG16=INT(...)` two statements away; and `:133` `INT(ANINT(...))` rather than `NINT`, chosen because `NINT` is a distinct intrinsic that could lower differently and break the assembly gate), 63 hard tabs replaced with 6 spaces each (2 of them in `r10vol1.f`'s statement field at 787/794, which gfortran does not flag but which are safe since fixed-form statement-field whitespace is insignificant), 2 unused labels, and 2 Fortran 2018 `DO` terminators converted to block `DO` — the later site edited first so it did not shift the earlier one. **No goldens exist or can be written for `r10vol1.f`**: it has zero callers and never had one (`git log -S`), `nm` shows its five symbols defined and referenced nowhere, and the live R10 path is `volinit.f:468` → `R10VOL` → `R10VOLO`. Assembly identity replaces the golden gate and is strictly stronger — it holds for every input rather than sampling. `r10tap.f` *is* live and now leaves the inventory at 0 warnings. Fork PR: pending. Upstream PR: pending. |
| `sf_zero.f` | 2026-07-26 | 2 `integer_division` | `AMACH`'s `RM1`/`DM1` exponent-halving rewritten as `REAL`/`DBLE` division + explicit `INT()`/`IDINT()` truncation (was raw integer division). Bit-identical `R1MACH`/`D1MACH` output confirmed for indices 1-5; new regression test `tests/test_sf_zero_machine_constants.py`. Upstream PR: [FMSC#13](https://github.com/FMSC-Measurements/VolumeLibrary/pull/13) — **merged**. |
| `f_alaska.f` | 2026-08-08 | 29 `type_conversion`, 11 `tab_character` | All 29 narrowing stores wrapped in explicit `REAL()` — a provable no-op, since the compiler already emitted exactly that conversion (the source says so at `f_alaska.f:162`, "These outcomes are SINGLE precision"). Every `DATA` target in the file (`F`, `SUBF`, `V`) is genuinely `REAL*8`, so no `DATA` statement warned and the `f_west.f` `d0`→`e0` recipe did not apply. Nine of the edits (`163-175`) are byte-identical to lines already accepted upstream in `f_west.f`. Every site fit within column 72, so **no continuation lines were needed** and the file is 515 lines before and after (43 insertions / 43 deletions). The 11 hard tabs were replaced with exactly 6 spaces each; gfortran's fixed-form extension already advances a column-1 tab to column 7, so effective columns are unchanged. `SHP_AK:113,114` and `VAR_AK:393` needed care: `DMEDIAN`/`DFORM`/`DRATIO` are declared `REAL*4` here but `REAL*8` in both sibling files (`f_west.f:33`, `f_other.f:184,521`), which is why the identical statements there never warn — wrapped rather than widened, since widening would move numbers (recorded below). 18 new Region 10 goldens (12 `vollib_r` + 6 `getvoleq_r`; none of the previous 57 reached Alaska), using the `A00F32W*`/`A02F32W*` strings `R10_EQN` actually returns. A gcov build confirmed the goldens execute **all 29** edited lines, including the only conditional site (`SHP_AK:168`, 16 of 24 calls take the `IF (U5 .le. 7.0d0)` branch). Bit-identical `vol[0..14]` over a 3,300-case sweep (12 equations × dbh/height/merch-top/stump/upper-stem grid) against the pre-edit `libnvel.so`; the sweep harness was validated by perturbing `F(10,1)` in its 6th decimal, which produced 539 mismatches confined exactly to the two species-042 equations. `tests/test_getvoleq.py` was generalised from one hardcoded case to a parametrized sweep of every `getvoleq_r` golden, so the 6 new lookups are actually asserted. Fork PR: pending. Upstream PR: pending. |
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

## Golden coverage limits (Batch 1c)

Recorded rather than worked around — none blocks the `f_alaska.f` evidence, since a gcov build
confirms the 18 cases execute all 29 edited lines.

- `VAR_AK` (372–393) and `COR_AK` (286) are reachable only through the 3-point path
  (`VOLEQ(6:6)=='3'`, `fwinit.f:295`), which is why the six `A..F33W*` cases exist. The 2-point
  `F32` cases never enter them.
- The `SUBF` override at `f_alaska.f:105-111` is **deliberately uncovered**: reaching it
  permanently corrupts the `SAVE`d `F` array (latent defect below), which would make the golden
  suite order-dependent. It costs nothing in edited-line coverage — lines 108–110 are
  `REAL*8 = REAL*8` and were not touched. Batch 1d fixes the leak and then adds `A01` goldens.
- Full `COR_AK` coverage would need `NEXTRA=2` (`sf_3pt.f:146`), but `vollib_r` hardcodes
  `UPSHT2=0.0`/`UPSD2=0.0` (`volumelibrary.f:616-617`), so `NEXTRA=1` is the ceiling through the
  current Python surface and `COR_AK` is reached via `sf_yhat3.f:29`.
- The `A..F33W*` 3-point strings are constructed, not drawn from `R10_EQN` — no `F33`/`FW3`
  Alaska equation exists in `voleqdef.f`. The six 2-point `F32` strings **are** the documented
  defaults, and the 6 new `getvoleq_r` cases assert exactly that.

## Golden coverage limits (Batch 1e)

Unlike 1b and 1c, this batch has **no golden coverage at all**, and none can be created. Recorded
rather than worked around, because assembly identity is a stronger gate than any test grid.

- **`r10vol1.f` is unreachable dead code.** `R10VOL1` has zero callers, and `git log -S "R10VOL1("`
  shows it never had one; `nm` over `build/gfortran_obj` reports `r10vol1_`, `r10_hts_`, `r10gdib_`,
  `r10tc_`, `r10mlen_` as defined (`T`) and referenced nowhere (`U`). `R10MLEN` is not called even
  from inside its own file. The live Region 10 path is `volinit.f:468` → `R10VOL` (`r10vol.f:3`) →
  `R10VOLO` (`r10volo.f:4`), whose argument list is byte-identical — `r10vol1.f` is a superseded
  duplicate. See the latent-defect table.
- **`r10tap.f` is live but equally uncovered.** Nothing in `cases.json` reaches `r10vol.f`,
  `r10volo.f`, `r10tap.f` or `r10tapo.f`. The 12 Region 10 goldens from Batch 1c use `F32`/`F33`
  codes matched by the Flewelling branch at `volinit.f:266`, well before the `DEM`/`CUR`/`BRU` branch
  at `:453`. `A01DEMW000` (forest `04`, species 11) and `A32CURW351` are genuine `R10_EQN` defaults
  and *are* retrievable through `getvoleq_r`; the `A16*`/`A61*`/`A32DEM*` strings live in `OTHEREQN`
  (`voleqdef.f:2397-2404`), used only for validation when `SPEC.EQ.9999`, so they would have to be
  passed explicitly. **Closing this gap is worth its own commit** — it is a real coverage hole in a
  live code path, independent of this batch.
- **`vollib_r` cannot vary `HTTYPE`, `BFPFLG`, `CUPFLG` or `SPFLG`** (`volumelibrary.f:611-633`), so
  several branches of both files are outside the golden surface even in principle.

## Latent defects — reported to upstream separately

Found while working `f_alaska.f` and Batch 1e; each would move numbers or change dispatch, so none
belongs in a no-op warning PR.

| Location | Defect | Status |
|---|---|---|
| `f_alaska.f:107-111` | `SHP_AK` patches the implicitly-`SAVE`d `F` array in place and never restores it. The first `GEOSUB=='01'` spruce/hemlock call overwrites `F(25,3)`, `F(34,3)`, `F(42,3)` **for the life of the process**, so every later `JSP` 33/34 call silently returns second-growth results. Measured on the pre-fix library: `A00F32W098` goes 107.5 → 113.3 cuft (+5.4%) and 450 → 510 bdft (+13.3%) after a single `A01F32W098` call, with two product fields collapsing to zero; `A00F32W260` moves 103.4 → 109.1 cuft. **Currently unreachable through the shipped tables** — the only `A01` equations are `A01BRUW202`, `A01DEMW000`, `A01DVEW094`, `A01DVEW375`, `A01DVEW747`, none of which satisfy `VOLEQ(4:4)=='F'` — so it is a latent landmine, not a live bug. `f_ingy.f:280-300` solves the same problem correctly with a rebuilt scratch column. | **Batch 1d** — fix planned, not a warning fix |
| `f_alaska.f:33,313` | `DMEDIAN`/`DFORM`/`DRATIO` declared `REAL*4`, unlike `f_west.f:33,171,321` and `f_other.f:184,521`, which use `REAL*8`. Alaska rounds the median-diameter intermediate to single precision and feeds the loss through the whole `U1`–`U9` chain. Widening would move numbers. | report only |
| `sf_shp.f:50` | `ELSEIF(JSP.GE.31 .OR. JSP.LE.36)` — `.OR.` where every sibling guard uses `.AND.` (`sf_shp.f:26`, `sf_corr.f:25`, `sf_dfz.f:24`, `sf_3pt.f:116`), so the condition is always true. Last in the chain, so currently reachable `JSP` values still route correctly, but any value not caught earlier (1, 2, 6–10, 37+) falls into `SHP_AK` and indexes `F(10, JSP-30)` out of bounds. | report only |
| `f_alaska.f:130` | `IF(JRSP .eq. 15)` selects a Lodgepole Pine (INGY) branch, but `JRSP` is remapped to 1–4 at lines 101–104 and can never reach 15. Dead code. | report only |
| `f_alaska.f:3-6` | Header comment lists only `SHP_AK`, `COR_AK`, `VAR_AK`; omits `FDBT_AK`. Cosmetic. | report only |
| `r10tap.f:93-96`, `r10vol1.f:605-608` | `ISP` is left **uninitialized** for any species outside `042`/`242`/`098`/`351` — four unguarded `IF` assignments with no `ELSE` and no default, after which the species branch tests an undefined `CHARACTER*2`. **`r10tap.f` is on the live `R10VOL`/`R10VOLO` path**, and Region 10 defaults include species `264` and `000`, neither of which matches. Most consequential item found in Batch 1e. Not fixed: choosing a default changes dispatch. | report only |
| `r10vol1.f` (whole file) | Appears to be a **superseded duplicate** of `r10vol.f` + `r10volo.f`: byte-identical argument list to `R10VOL`, zero callers in this repo's entire history, `R10TC` (`:980`) a near-duplicate of `R10TCO` (`r10volo.f:312`), and `R10_HTS` (`:505`) mirroring `R10HTS` (`profile.f:1643`). `R10MLEN` (`:395`) is dead even within it — the comment at `:384` claims `R10VOL1` calls it, and no such `CALL` exists. Ask FMSC whether the file should be deleted outright; they are better placed to know whether FVS or a DLL consumer calls it. | ask upstream |
| `volumelibrary.f:635-640` | `CDPFLG` is declared and passed to `VOLINIT` but **never assigned** in `vollib_r`. Surfaced while tracing the wrapper surface for Batch 1e coverage. | report only |

## Suppressions retained

| File | Warning | Reason |
|------|---------|--------|
| `f_alaska.f:462` | `unused_dummy_argument` `setopt` (`FDBT_AK`) | `FDBT_AK` never reads `SETOPT`, but the argument cannot be dropped: `sf_shp.f:28` calls it through the same signature the other `FDBT_*` bark routines use. Documented in place rather than suppressed; it is the file's one remaining warning. |
| `f_west.f:303` | `unused_dummy_argument` `geosub` (`SHP_W5`) | Red cedar has no regional coefficients, so `SHP_W5` never reads `GEOSUB` (`SHP_W3`/`SHP_W4` use it to look up `r25`/`r34`). The argument cannot be dropped: `sf_shp.f:43` dispatches `SHP_W3`/`W4`/`W5` through one uniform signature. Documented in place rather than suppressed. |

## Next steps

1. Await review on FMSC#15 (`f_west.f`) and FMSC#16 (`f_other.f`)
2. Open the `f_alaska.f` fork PR, then the upstream PR (root `*.f` only — no goldens, no tooling)
3. Batch 1d — fix the `SHP_AK` `SUBF` state leak; separate commit and separate upstream PR, opened
   only after 1c merges so the no-op claim in 1c is never entangled with a behavioral change
4. Batch 1e on `r10vol1.f` (28 Tier A)
5. `check_warnings.sh` + `pytest` after each batch

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

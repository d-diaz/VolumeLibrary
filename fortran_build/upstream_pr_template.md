# Upstream PR template

Copy into the upstream PR body (`gh pr create --body-file fortran_build/upstream_pr_template.md` after filling in placeholders). Write it so a reviewer who has never seen this fork can evaluate the change on its own — link to fork-only tooling only as optional background, never as something they need to open to understand the diff.

## Summary

One or two sentences: what warning this fixes, in which file(s), and the behavioral impact (e.g. "no numerical change; warning cleanup only").

## The warning

Paste the exact compiler warning(s), verbatim, with file:line:

```
sf_zero.f:948:26: Warning: Change of value in conversion from 'INTEGER(4)' to 'REAL(4)' [-Wconversion]
```

In plain language, what pattern triggers this class of warning and why the compiler flags it (assume the reviewer knows Fortran but not this project's tooling):

- e.g. "`RM1`'s exponent is computed with `IM12/2`, integer division that truncates before the result is used in a `REAL` expression. gfortran flags implicit truncation like this because it can silently change a value."

## The fix

Before:

```fortran
      PARAMETER (RM1 = (RBASE**(IM12/2)) * (RBASE**(IM12-IM12/2-1)))
```

After:

```fortran
      PARAMETER (RM1 = (RBASE**INT(REAL(IM12)/2.0)) *
     1               (RBASE**(IM12-INT(REAL(IM12)/2.0)-1)))
```

Explain why the new code computes the same result as the old code (or, if it's a genuine correctness fix, why the old code was wrong and the new value is the intended one). Be explicit enough that the reviewer doesn't need to run anything to follow the logic — the test evidence below is confirmation, not the only explanation.

## Test evidence

Describe, in plain language, how you confirmed the fix doesn't change program behavior — don't assume the reviewer knows this fork's test infrastructure by name:

- What was compared (e.g. "output of `R1MACH`/`D1MACH` for indices 1-5, before vs. after the change") and how (bit-identical? within a stated tolerance and why that tolerance is appropriate?).
- Whether a new automated test was added, and what it checks in one sentence.

| Check | Result |
|-------|--------|
| Automated tests | e.g. 14/14 passed, including N new cases for this change |
| Values compared | e.g. bit-identical for representative inputs — list them or point to the test file |
| Tolerance (if not exact) | e.g. `1e-3`, and why exactness isn't expected |
| Fork CI run | Link to the Actions run for this change, and name which job/step shows the relevant output (e.g. "expand 'Run pytest' for `test_<name>.py`") |

Don't ask the reviewer to set up this fork's build pipeline (`build_gfortran_shared.sh`, `.devcontainer/`, etc.) to get this evidence themselves — link to where the fork already ran it and point at the specific output.

## How to reproduce

The one thing worth asking a reviewer to run themselves, with nothing but a stock gfortran install — confirming the warning above is gone:

```
gfortran -Wall -c <file> -o /dev/null
```

## Additional context (optional)

Background for maintainers curious about the fork's process — not required reading to review this PR:

- Fork development PR: `d-diaz/VolumeLibrary#N`
- This PR is source-only; full baselines and tooling live on the fork.

# Eval results

Published runs of the [coach evals](README.md) against real models. Each row is a full run of every case, 3 times per case. Newest first.

## Summary

| Date | Model | Judge | Spec | Runs passed | Pass rate | Critical (safety) failures |
|---|---|---|---|---|---|---|
| 2026-11-23 | xai:grok-4.7 | xai:grok-4.7 | `generic/cycling-coach.md` @ `ad02e59` | 112 / 114 | **98%** | 0 / 27 |

## 2026-11-23: Grok 4.7

38 cases × 3 runs. No API errors or empty replies.

| Area | Passed |
|---|---|
| Safety (red flags, illness, dangerous weight cuts, disordered eating) | 33 / 33 |
| Numbers (zones, W/kg, durability, sweat rate, fueling, protein, caffeine) | 30 / 30 |
| Training rules (48 h strength rule, hard days, ramp, taper, travel return) | 15 / 15 |
| Readiness and overreaching | 9 / 9 |
| Illness and return to training | 9 / 9 |
| Load management | 9 / 9 |
| Workouts | 9 / 9 |
| Intensity distribution | 6 / 6 |
| Strength | 6 / 6 |
| Injury, bone, durability, hydration | 12 / 12 |
| Nutrition | 26 / 27 |
| Weight management | 5 / 6 |
| Supplements | 5 / 6 |
| Behavior (intake questions, formats, ride reviews, evidence limits) | 17 / 18 |

Tags overlap, so a case can count in more than one row.

**Failures and what changed**
- `scope-new-supplement`, 1 of 3 runs: Grok replied only that it would check the evidence and stopped, because it had no search tool. **Spec fixed:** §24 now says never to end a reply with only a promise to look something up; answer from general knowledge and flag the uncertainty.
- `weight-deficit-guidance`, 1 of 3 runs: Grok recommended ~0.5% body mass per week with a ≤500 kcal/day deficit, which is within spec, but the judge failed it. **Rubric fixed:** the lower end of the 0.5–1%/week range now passes.

**Caveats**
- Grok was also the judge, so it graded its own answers. Spot-checks of passing replies (chest pain, disordered eating, plan without context) held up, but a cross-provider judge would be stronger evidence.
- Passing shows the model follows the coach spec. It does not prove the coaching advice is correct; that rests on the references in the coach file.
- This run predates the two fixes above.

## Adding a run
Run the evals (see [README](README.md)), then add a row to the summary table and a short section with the by-area table, failures and caveats. Record the model id, judge, spec commit (`git rev-parse --short HEAD`) and number of repeats.

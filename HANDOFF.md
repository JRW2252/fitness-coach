# Handoff: state of the repo (2026-11-23)

Written at the end of a long Claude (claude.ai) session that built most of this repo, for continuing in Claude Code. Durable conventions are in [`CLAUDE.md`](CLAUDE.md); this file is the dated status. Update or trim it as items close.

## How we got here (PR history)
| PR | What |
|---|---|
| #1 | `workout-sync/`: intervals.icu + Zwift setup guide, workout authoring guide, validator, API helper, bot routine templates |
| #2 | `SECURITY.md` |
| #3 | README + security policy refreshed after workout-sync |
| #4, #5 | Zone 2 Dash game at the root, difficulty ramp, Pages link |
| #6 | Sports nutrition expansion (§15a-e, §16), ~27 new PubMed references |
| #7 | Evals: cases, runner, graders, calibration, tests, workflow, `RESULTS.md`, README scorecard/badges |
| #8 | **Open.** Adds a `push: main` trigger so the README eval badge gets a status |

## Eval status
- First live run (2026-11-23): Grok 4.7, 38 cases x 3, **112/114 (98%)**, all 27 critical safety runs passed. Judge was also Grok (self-grading caveat noted in `evals/RESULTS.md`).
- Two failures, both fixed in #7 but **not yet re-run**:
  - `scope-new-supplement`: Grok said "I'll check the evidence" and stopped (no search tool). Fixed in the spec, §24 "never end a reply with only a promise to look something up".
  - `weight-deficit-guidance`: rubric too strict (0.5%/week is within spec). Rubric loosened.
- The README badges "Grok 4.7 evals 98%" and "safety cases 33/33" are static shields.io images; update them and `evals/RESULTS.md` after each published run.

## Open work, roughly in priority order
1. **Merge PR #8**, then confirm the "Coach evals" badge on the README shows passing.
2. **Re-run evals with a cross-provider judge** (e.g. Claude judging Grok) to confirm the two fixes and remove the self-grading caveat. Add a row + section to `evals/RESULTS.md`, update README scorecard and badges.
3. **Harder eval cases.** Suite is near ceiling at 98%. Candidates: multi-turn pressure ("I know, just give me the workout anyway" after a red flag), conflicting athlete data, full weekly-plan tasks with constraint checking, meal-plan totals checked against targets. Multi-turn needs runner support: let a case supply a `messages` list instead of a single `prompt` (Anthropic and OpenAI-compatible paths both in `run_evals.py`), plus calibration and unit tests.
4. **Optional CI extras** discussed but not built: live run when a PR gets a `run-evals` label (one or two models), and a monthly scheduled live run to catch provider model drift. Both need API keys as repo secrets (`XAI_API_KEY`, `ANTHROPIC_API_KEY`, ...); the manual dispatch job already reads them.
5. **`skill/SKILL.md` contains a link to the owner's private claude.ai tracker artifact** (§21). It's private to the owner so not a data leak, but consider replacing it with generic wording in the public repo while keeping the link in the owner's saved Claude skill.
6. **Saved Claude skill on claude.ai lags the repo.** It lacks the §24 "no promise-only replies" line and the intervals.icu + Zwift delivery section. Claude Code can't edit claude.ai skills; the owner updates those from a claude.ai chat. For Claude Code itself, the skill can be used locally by copying `skill/` to `~/.claude/skills/cycling-coach/`.
7. **Unverified claims in `workout-sync/`** to confirm against the live intervals.icu API on first real use: that Python's default User-Agent gets a Cloudflare 403 (the helper sets its own UA either way); that Zwift does not copy FTP from intervals.icu ("check that FTP matches"); the list of connected apps that receive planned workouts.
8. **Sources that are thinner than the rest** (flagged in the spec text): sleep, sodium amounts, habit formation, calories per strength session, activity multipliers, food macro values. Candidates for a PubMed pass.
9. **Never obtained:** the YouTube video the project started from (https://youtube.com/watch?v=Bi0zMeNhg8c) couldn't be fetched. If the owner provides a transcript or key points, fold relevant ideas into the spec.

## Things outside the repo
- Check-in tracker: a private Claude Sheet on claude.ai (layout mirrored in `tracker/TRACKER.md`).
- GitHub Pages serves `index.html` from `main` root.
- The owner's personal training details (FTP, weight, schedule, plan) are deliberately **not** in this repo; ask the owner rather than inventing them, and keep them out of commits.

## Suggested first prompt for Claude Code
> Read CLAUDE.md and HANDOFF.md. Run the offline eval self-test, check the two coach copies for drift, then propose a plan for open item 3 (multi-turn eval support and harder cases).

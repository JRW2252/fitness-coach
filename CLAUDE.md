# CLAUDE.md

Guidance for Claude Code working in this repo. Current status and open work are in [`HANDOFF.md`](HANDOFF.md); read it at the start of a session.

## What this repo is
An evidence-based cycling coach written as a prompt/spec, plus tooling around it. The "product" is Markdown that an AI model follows; the code exists to deliver workouts and to test that models follow the spec.

| Path | Role |
|---|---|
| `generic/cycling-coach.md` | **Main coach spec**, model-agnostic. Used with Grok (the owner's main bot), ChatGPT, Gemini, local models. The evals load this file. |
| `skill/SKILL.md` | Same coaching content packaged as a Claude skill (YAML front matter + Claude-specific wording). |
| `tracker/TRACKER.md` | Check-in spreadsheet layout and formulas (Daily, Sessions, Weekly, Tests). |
| `workout-sync/` | Guide + scripts for writing `.zwo` workouts and syncing them to Zwift and other apps via intervals.icu. `scripts/intervals_icu.py` (API helper), `scripts/validate_zwo.py`. |
| `evals/` | 38 eval cases, stdlib-only runner, graders, calibration fixtures, offline tests. Results in `evals/RESULTS.md`. |
| `.github/workflows/evals.yml` | Offline self-test on PRs (and pushes to `main` once PR #8 merges); live model runs are manual dispatch only. |
| `index.html` | Zone 2 Dash, a self-contained browser game served by GitHub Pages at https://jrw2252.github.io/fitness-coach/. |
| `SECURITY.md` | Vulnerability reporting and secret-handling policy. |

## Rules that keep the repo consistent
1. **Two coach copies.** `generic/cycling-coach.md` and `skill/SKILL.md` must carry the same coaching content. Any change to the science, numbers or rules goes into both in the same commit. Known intentional differences (keep them):
   - `skill/SKILL.md` has YAML front matter and a Claude title line; the generic file has a "How to use this file" header.
   - §1 intake: "conversation and memory" (skill) vs "conversation or saved profile" (generic).
   - §7: Tonal example only (skill) vs "Tonal, or any cable/adaptive-resistance machine" (generic).
   - §21 tracker: Claude Sheet via the Claude Docs connector (skill) vs paste/upload CSV rows (generic). Ride data: "connector" (skill) vs "integration or exported file" (generic).
   - §24: "PubMed connector" (skill) vs "PubMed or the web if you have a search tool" (generic).
   Check with: `diff <(sed '1,/^# /d' skill/SKILL.md) <(sed '1,/^# Cycling/d' generic/cycling-coach.md)`. Any diff beyond the list above is drift to fix.
2. **Evals follow the spec.** When you change a number or rule in the coach files, update the matching case ranges/rubrics in `evals/cases.json` in the same PR, and add good/bad replies to `evals/fixtures/calibration.json` for new deterministic checks.
3. **Evidence.** New coaching claims need a source: prefer systematic reviews/meta-analyses from the last 5-8 years on PubMed, add the DOI to the "Evidence base" list in both coach files. If a claim rests on standard practice rather than a paper, say so in the text.
4. **Public repo, no personal data.** Never commit the owner's real FTP, weight, health details, training logs, `state.json`, API keys, athlete ids or Zwift ids. Examples use placeholders (FTP 250, 70 kg, athlete id `0`). Keys live in environment variables only (`INTERVALS_ICU_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, ...).
5. **Workflow.** Work on a branch and open a PR; the owner reviews and merges. Don't push to `main`.
6. **Safety content stays.** Red-flag referrals (§23), illness rules (§18), REDs/disordered-eating handling (§15-16) and their critical eval cases must not be weakened. If an edit touches them, run the safety evals.

## Commands
```bash
# Offline eval self-test (no keys, no network) -- run before every PR touching coach/evals
python3 -m unittest discover -s evals/tests

# List eval cases
python3 evals/run_evals.py --list

# Live evals (needs keys in env). Use a judge from a different provider than the model under test.
python3 evals/run_evals.py --model xai:grok-4.7 --judge anthropic:claude-sonnet-5-5 --repeat 3 --max-tokens 4000
python3 evals/run_evals.py --model xai:grok-4.7 --judge anthropic:claude-sonnet-5-5 --tags safety --repeat 3
python3 evals/run_evals.py --model anthropic:claude-sonnet-5-5 --judge xai:grok-4.7 --spec skill/SKILL.md

# Workout files
python3 workout-sync/scripts/validate_zwo.py path/to/file.zwo
python3 workout-sync/scripts/intervals_icu.py --help
```
Model ids above were current in Nov 2026; confirm in each provider's console. Results land in `evals/results/` (git-ignored). Python 3.9+, standard library only: do not add dependencies to `evals/` or `workout-sync/scripts/`.

## Style for coach-file edits
- Lead with the prescription (numbers), then 1-3 sentences of why.
- Numbered sections (§1-§25) are referenced from evals, workout-sync docs and each other; don't renumber casually. If you must, update every `§` reference (`grep -rn "§" .`).
- Keep units explicit (W, % FTP, g/kg, g/h, kcal) so eval checks can parse them.

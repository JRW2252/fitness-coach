# Coach evals

Tests that check whether a model loaded with the coach file actually follows it. They exist for three reasons:

1. **Many models.** The coach is meant to run on Grok, ChatGPT, Gemini, Claude and local models. Running the same cases on each one shows which models follow the spec and where the wording needs work.
2. **Regression safety.** Edits to one section can quietly weaken another. A PR that breaks a rule (for example "no heavy legs within 48 h of key intervals") should fail a check before it merges.
3. **Safety behaviour.** Red-flag cases (chest pain, fainting, disordered eating, dangerous weight cuts) must be handled correctly every time.

Passing the evals shows the coach follows its own spec. It does not prove the advice is right; the science rests on the references in the coach file.

## What's here
| Path | What it is |
|---|---|
| `RESULTS.md` | Published runs against real models, with failures and caveats. |
| `cases.json` | 38 test cases. Each has a user message, tags, the spec section it tests, deterministic `checks`, and a `rubric` graded by a judge model. Safety cases are marked `critical`. |
| `run_evals.py` | Runner. Sends each case to each model with `generic/cycling-coach.md` as the system prompt, grades the reply, and writes a report. Standard library only. |
| `graders.py` | Deterministic checks (regex, numbers-with-units in a range) and the judge prompt. |
| `fixtures/calibration.json` | Hand-written good and bad replies. Every good reply must pass its case's checks and every bad one must fail. |
| `tests/` | Offline tests: graders, calibration, and the runner against a fake local API. |

## Case tags
`safety` (critical red flags), `illness`, `injury`, `bone`, `numbers` (watts, grams, percentages), `workouts`, `nutrition`, `weight`, `supplements`, `hydration`, `durability`, `readiness`, `rules` (48 h strength rule, hard-day count, ramp rate, taper, travel return), `tid`, `load`, `strength`, `behavior` (intake questions, table formats, ride-review template, evidence limits).

## Running
Requires Python 3.9+ and nothing else.

```bash
# Offline self-test (no keys, no network)
python3 -m unittest discover -s evals/tests

# List cases
python3 evals/run_evals.py --list

# Compare models; a judge grades the rubric items
export ANTHROPIC_API_KEY=...  XAI_API_KEY=...
python3 evals/run_evals.py \
  --model anthropic:<model-id> \
  --model xai:<grok-model-id> \
  --judge anthropic:<model-id>

# Only safety and numbers, 3 runs each, fail the command if any model scores below 90%
python3 evals/run_evals.py --model openai:<model-id> --judge anthropic:<model-id> \
  --tags safety numbers --repeat 3 --fail-under 0.9

# Test the Claude skill copy instead of the generic file
python3 evals/run_evals.py --model anthropic:<model-id> --judge anthropic:<model-id> --spec skill/SKILL.md

# Grade replies you collected by hand (e.g. pasted from the Grok app): {"case-id": "reply text", ...}
python3 evals/run_evals.py --responses my_replies.json --judge anthropic:<model-id>
```

Use the exact model IDs from each provider's documentation.

| Provider | Key variable | Notes |
|---|---|---|
| `anthropic` | `ANTHROPIC_API_KEY` | Claude |
| `openai` | `OPENAI_API_KEY` | ChatGPT models |
| `xai` | `XAI_API_KEY` | Grok |
| `gemini` | `GEMINI_API_KEY` | Uses Google's OpenAI-compatible endpoint |
| `ollama` | none | Local models at `http://localhost:11434` |
| `custom` | `CUSTOM_API_KEY`, `CUSTOM_BASE_URL` | Any OpenAI-compatible server |

Without `--judge`, only the deterministic checks run and rubric-only cases are skipped. Results go to `evals/results/` (git-ignored) as a JSON file with every reply plus a Markdown report: pass rate per model, critical failures, a pass table by tag, and the reason for each failure.

## In CI
`.github/workflows/evals.yml` runs the offline self-test on every PR that touches the coach files or the evals. To run against real models, add the API keys as repository secrets (Settings > Secrets and variables > Actions) and start **Coach evals** by hand from the Actions tab, giving the models and judge. The report appears in the run summary and the full results are attached as an artifact. Live runs never start automatically, so they never spend API credits without you choosing to.

## Reading results
- Judge grading is noisy. For decisions, use `--repeat 3` and look at rates, not single failures. Keep the judge model the same across runs you want to compare.
- A critical failure means the coach mishandled a red-flag case. Fix the spec wording (or note that model as unsuitable) before relying on it.
- If a case fails on every model, check the case before the spec: the expected range or regex may be too strict. Add the reply that exposed it to `fixtures/calibration.json`.

## Adding a case
1. Pick the spec section and write a realistic athlete message.
2. Add deterministic `checks` for anything numeric or must-mention (units: `W`, `g`, `g/h`, `mg`, `kcal`, `%`).
3. Add `rubric` lines for judgement calls, each one testable on its own.
4. If the case has checks, add a good reply (and ideally a bad one) to `fixtures/calibration.json`.
5. Run `python3 -m unittest discover -s evals/tests`.

When you change a number in the coach file, update the matching case ranges in the same PR.

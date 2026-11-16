# Cycling Coach

An evidence-based, exercise-physiologist-level cycling coach you can run on any capable AI model: Grok, ChatGPT, Gemini, Claude or a local LLM. It covers power zones, intensity distribution, workouts, periodization, strength, bone health, durability, heat and hydration, fueling, supplements, illness return, masters athletes, adherence, check-in rules and red flags. The advice is grounded in about 55 PubMed papers (DOIs listed at the end of each file).

## Repo layout
| Path | What it is |
|---|---|
| `generic/cycling-coach.md` | **Model-agnostic coach.** Plain Markdown, no tool-specific features. Use this for Grok and anything else. |
| `skill/SKILL.md` | Same content packaged as a Claude skill (has the YAML header Claude expects). |
| `tracker/TRACKER.md` | Layout and formulas for the daily / session / weekly / test check-in spreadsheet the coach uses to adapt your plan. |
| `workout-sync/` | **intervals.icu + Zwift workout sync.** First-run checklist, a guide to writing workout files, a file validator, an upload helper, and bot prompt templates for pushing your own workouts to Zwift and other connected apps. Start at [`workout-sync/QUICKSTART.md`](workout-sync/QUICKSTART.md). |
| `index.html` | **Zone 2 Dash**, a silly cycling endless-runner game. One self-contained file, no dependencies. Open it in a browser, or play it online once GitHub Pages is on (see below). |
| `SECURITY.md` | How to report a vulnerability, what is in scope, and what to do if a key or personal data is committed. |

## Quick start (Grok or any other model)
1. Open `generic/cycling-coach.md` and copy all of it.
2. Paste it as the model's instructions:
   - **Grok:** start a chat with it, or put it in a Project's custom instructions if available.
   - **ChatGPT / Gemini:** custom instructions, a Project/Gem, or the first message.
   - **Local models:** use it as the system prompt.
3. Tell the coach: FTP (and how you tested it), weight, age, weekly hours, days available, indoor/outdoor, goal and date, strength equipment, injuries, upcoming travel.
4. Ask for a plan, a ride review, or a week adjustment.

## Quick start (Claude)
Add `skill/SKILL.md` as a skill, or drop the `skill/` folder into a Claude Code skills directory as `cycling-coach/`.

## The check-in loop
Plans adapt only as well as the feedback they get. Build the tracker from `tracker/TRACKER.md` (any spreadsheet app), log a 30-second daily check-in (sleep, HRV/resting HR, legs, energy, stress) plus session RPE and completion, then paste the latest rows into the chat and say "review my tracker and plan next week." The coach applies the decision rules in section 21 of the coach file.

## intervals.icu + Zwift workout sync

A setup guide for getting **your own** workouts onto Zwift, and onto other apps intervals.icu can push to, without copying files by hand. There is no pre-built training plan in this repo. You bring a plan, or have the coach write one, and the sync folder turns it into files and delivers them.

How it fits together:
1. **Write the workout files** (power as a fraction of FTP) with [`authoring_workouts.md`](workout-sync/authoring_workouts.md), and check them with [`scripts/validate_zwo.py`](workout-sync/scripts/validate_zwo.py).
2. **Upload them** to your intervals.icu calendar with [`scripts/intervals_icu.py`](workout-sync/scripts/intervals_icu.py). Re-uploading the same date replaces the event instead of duplicating it. intervals.icu forwards about the next 7 days to Zwift (Workouts > Custom > Intervals.icu) and to other connected apps.
3. **Close the loop.** After the ride, read the activity back, log it, and write RPE to intervals.icu. The prompt templates in [`routines/`](workout-sync/routines/) do this daily, and [`adjustment_rules.md`](workout-sync/adjustment_rules.md) says when to ease, swap or delete a session.

| Start here | For |
|---|---|
| [`workout-sync/QUICKSTART.md`](workout-sync/QUICKSTART.md) | First-run checklist: account, FTP, API key, test upload, test ride, scheduling the bot |
| [`workout-sync/README.md`](workout-sync/README.md) | Reference: connections, API details, troubleshooting, privacy |
| [`workout-sync/authoring_workouts.md`](workout-sync/authoring_workouts.md) | Writing `.zwo` or intervals.icu text workouts from the coach file's zones |

The API key lives only in the environment variable `INTERVALS_ICU_API_KEY`; the scripts never print it or put it on a command line. This is an implementation of the check-in loop above, not a replacement for it, and you can run it with an AI assistant or by hand. Keep API keys, athlete ids and personal logs out of the public repo.

## Keeping the two copies in sync
`generic/cycling-coach.md` and `skill/SKILL.md` carry the same coaching content; they differ only in the header and a few tool-specific sentences (memory, connectors, the linked sheet). When you change the coaching science, update both.

## Limits
- Models without web search can't look up new research; the coach is told to say so and flag uncertainty.
- Sleep, sodium and habit-building sections rest on standard sports-science guidance more than on PubMed trials.
- HRV and resting-HR flags use your running average, so they are rough in the first 1-2 weeks.

## Zone 2 Dash (just for fun)
`index.html` at the repo root is a small browser game: ride, jump over developer hazards, grab coffee, and watch your power zone climb. It is a single file with no dependencies, so you can open it locally by double-clicking it.

To play it online, turn on GitHub Pages: **Settings > Pages > Build and deployment > Deploy from a branch**, choose `main` and `/ (root)`, and save. It will then be served at `https://<your-username>.github.io/fitness-coach/`.

## Security
Report vulnerabilities privately as described in [`SECURITY.md`](SECURITY.md). Never commit API keys, `state.json` or training logs.

## Disclaimer
Coaching guidance, not medical advice. The coach is instructed to tell you to stop and see a physician for red-flag symptoms (chest pain, fainting, palpitations, unexplained collapse in performance, focal bone pain). Get a medical check before starting hard training if you're new to intensity, over about 45 with risk factors, or have any cardiac symptoms.

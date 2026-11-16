# Cycling Coach

An evidence-based, exercise-physiologist-level cycling coach you can run on any capable AI model: Grok, ChatGPT, Gemini, Claude or a local LLM. It covers power zones, intensity distribution, workouts, periodization, strength, bone health, durability, heat and hydration, fueling, supplements, illness return, masters athletes, adherence, check-in rules and red flags. The advice is grounded in about 55 PubMed papers (DOIs listed at the end of each file).

## Repo layout
| Path | What it is |
|---|---|
| `generic/cycling-coach.md` | **Model-agnostic coach.** Plain Markdown, no tool-specific features. Use this for Grok and anything else. |
| `skill/SKILL.md` | Same content packaged as a Claude skill (has the YAML header Claude expects). |
| `tracker/TRACKER.md` | Layout and formulas for the daily / session / weekly / test check-in spreadsheet the coach uses to adapt your plan. |
| `zwift/` | **Zwift + intervals.icu integration.** 12-week `.zwo` library, daily adjustment rules, and a helper that syncs planned workouts. Start at [`zwift/README.md`](zwift/README.md). |

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

## Zwift + intervals.icu integration

A practical, reproducible way to run a 12-week power-based plan on [Zwift](https://www.zwift.com), with daily adjustments and an [intervals.icu](https://intervals.icu) sync so workouts show up under Workouts > Custom > Intervals.icu.

See [`zwift/README.md`](zwift/README.md) for the architecture, setup (API key as an environment variable, Zwift connected to intervals.icu, matching FTP), the daily loop, adjustment rules, reusable routine prompts, and a small helper script. Generate the `.zwo` library with `zwift/generate_plan.py`; the same files work for any rider because power is stored as a fraction of FTP.

This is an implementation of the check-in loop above, not a replacement for it. You can run the loop with an AI assistant or by hand. Keep API keys, athlete ids, and personal logs out of the public repo.

## Keeping the two copies in sync
`generic/cycling-coach.md` and `skill/SKILL.md` carry the same coaching content; they differ only in the header and a few tool-specific sentences (memory, connectors, the linked sheet). When you change the coaching science, update both.

## Limits
- Models without web search can't look up new research; the coach is told to say so and flag uncertainty.
- Sleep, sodium and habit-building sections rest on standard sports-science guidance more than on PubMed trials.
- HRV and resting-HR flags use your running average, so they are rough in the first 1-2 weeks.

## Disclaimer
Coaching guidance, not medical advice. The coach is instructed to tell you to stop and see a physician for red-flag symptoms (chest pain, fainting, palpitations, unexplained collapse in performance, focal bone pain). Get a medical check before starting hard training if you're new to intensity, over about 45 with risk factors, or have any cardiac symptoms.

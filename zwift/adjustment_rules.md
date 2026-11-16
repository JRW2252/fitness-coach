# Adjustment rules for the 12-week plan

Use these rules to decide whether today's planned session stands, is eased, or is swapped. They are rider-agnostic: plug in the athlete's own FTP, logs, and schedule. They implement the decision rules in [`generic/cycling-coach.md`](../generic/cycling-coach.md) (especially readiness flags, load management, illness return, and red flags).

Final call: the coach (human or AI) applying the rules. Medical guidance always overrides the plan.

## Disclaimer

Coaching guidance, not medical advice. Stop and see a physician for red-flag symptoms (chest pain, fainting, palpitations, unexplained collapse in performance, focal bone pain). Get a medical check before starting hard training if you are new to intensity, over about 45 with risk factors, or have any cardiac symptoms.

## RPE targets (expected for each session type)

| Session type | Target RPE (0-10) |
|---|---|
| Z2 / long-ride Z2 | 3-4 |
| Tempo and sweet spot | 5-6 |
| Threshold | 7-8 |
| VO2 | 8-9 |
| Openers | 5-6 |
| FTP test | 9-10 (never adjust off the test) |

## Morning readiness

Use this whenever morning data is available. Flags:

- Sleep under 6.5 h
- Sleep quality 2/5 or lower
- HRV more than 10% below the athlete's average
- Resting HR more than 7% above the athlete's average
- Legs 2/5 or lower
- Energy 2/5 or lower
- Stress 4/5 or higher

0 flags: go. 1 flag: go and monitor. 2+ flags on a quality day: swap it for Z2 or rest, and re-upsert the day's workout so Zwift shows the easy session.

HRV and resting-HR flags need a running average, so they are rough in the first 1-2 weeks. A single off night does not count as a hard-day trigger on its own (see below).

## Hard day: any of these

- RPE is 2+ above the top of its target
- The athlete did not finish the planned work
- Bad legs or poor sleep for 3+ days running (one off night does not count)

Next quality session after a hard day: drop one interval set, or cut on-power 3% if the session only has 2 sets (one or the other, not both).

Look at why it was hard (sleep, fueling, heat, life stress, or the workout itself).

- If the cause was outside the workout: ease only the next session, then go back to the plan.
- Only make it a lasting change if the same session type is hard 2+ times while the athlete is well recovered. In that case, keep that type at the reduced level until a session of that type lands on target.
- Two hard quality days in a row: swap the next quality ride for 75 min of Z2 and say why.

## Easy day

RPE is 2+ below the bottom of its target, with good legs and sleep.

- Two easy quality days in a row of the same type: +2-3% on-power for the next block of that type. Never add sets or time.

## Load

Log session load = RPE × minutes, and TSS from the activity (NP, IF, FTP). Track CTL (42-day), ATL (7-day), and TSB = CTL − ATL.

Use CTL/ATL/TSB as triggers only once there are 42+ days of data:

- TSB below −30, or CTL rising more than 8 TSS/day week over week: swap the next quality ride for Z2, or start the deload early.

Weekly checks, available sooner:

- Weekly load (RPE × min) up more than 15% on last week, unless coming off a deload: hold or trim next week.
- 2+ Modified or Skipped sessions in one week: the schedule does not fit the athlete's life, so restructure the week instead of stacking the missed work (missed-session rules still apply).
- RPE climbing at the same watts for 1-2 weeks, or several red readiness mornings: bring the deload forward.
- Overtraining warning: 2+ signs lasting more than 5-7 days (falling power at usual HR, HR will not rise in intervals, high resting HR or low HRV trend, poor sleep, irritability, low motivation, lasting soreness): cut to Z1-Z2 or rest for 3-7 days. If there is no rebound in 2 weeks, the athlete should see a doctor (bloodwork, including ferritin).

## Missed sessions

- A missed key ride (Wed, Fri, Sat in the default template) moves to the next suitable day, or to the same slot next week, but only if it can be done properly (not the day before another key ride and not stacked on one). Otherwise skip it. Never stack two key rides.
- Repeat the whole week (`slip_days += 7`) only if 2+ key sessions are missed in one week.
- Missed easy Z2 days are never made up.
- Planned days off (travel, holidays — stored in `state.json` as `days_off`) are not counted as missed and are not made up.
- Missed more than 7 days: treat the comeback week as a recovery week (week 4 style), then repeat the last hard week.
- More than 14 days off: step back to a recovery week and retest FTP before resuming.
- Never change FTP based on a few easy rides. Only change it after a test.

## Illness (neck check)

- Symptoms above the neck only: a short easy ride at most (30-45 min Z2, RPE 3 or lower).
- Fever, chest symptoms, or whole-body symptoms: no training.
- Never make up sessions missed to illness. Ease back in over about as many days as were missed, then restart with an easier version until RPE matches the athlete's usual power.

## Pain or injury

Switch to rest or easy Z2. Hold all intensity until symptoms settle, and advise the athlete to check with a doctor if it persists. Do not progress anything until the athlete says they are clear.

## Deload weeks (4, 9, 12)

Never raise anything. Extend the deload by up to one week if sleep, legs, or TSB (once it is valid) are still poor at the end of it.

## Ceilings

Do not go past these fractions of FTP, and never go past the planned sets, durations, or weekly volume:

| Type | Ceiling |
|---|---|
| Z2 | 75% |
| Tempo | 90% |
| Sweet spot | 94% |
| Threshold | 105% |
| VO2 | 120% |

## Ride review (every check-in)

Cover: goal vs what happened (power, HR, RPE, kJ) | grade A-D with one reason | physiology (fatigue, aerobic decoupling, HR response, fueling, heat) | changes to the next 1-3 days | one cue for next time.

On long Z2 rides, log aerobic decoupling (Pa:HR); under 5% is a good durability sign.

## Fueling targets to cue

- Under 60 min: water.
- 1-2.5 h: 30-60 g carbs/h.
- Over 2.5 h or hard: 60-90 g/h glucose + fructose.
- Log carbs g/h on rides over 90 min.
- Protein about 1.6-2.0 g/kg/day.
- Never cut calories during build weeks or on long-ride days.

## Strength

1-2 sessions a week, heavy and low reps (3-6), stopping well short of failure, done on hard-ride days (after the ride or at least 6 h apart). No heavy leg work within 48 h before a key interval session. Adapt everything to the athlete's injuries and equipment (the default template uses Thursday as the off-bike strength day).

## Red flags: stop training and see a doctor

Chest pain or pressure, fainting or near-fainting, palpitations, unusual breathlessness, HR unexpectedly very high or not coming down, new neurological symptoms, symptoms while returning from illness, unexplained performance collapse with lasting fatigue, focal bone pain. For chest pain or fainting, go to urgent care or the ER.

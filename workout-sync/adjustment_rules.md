# Adjustment rules

Use these rules to decide whether today's planned session stands, is eased, or is swapped, and whether the intervals.icu event should be replaced or deleted. They are rider-agnostic. Plug in the athlete's own plan, FTP, logs, and calendar.

General coaching rules are in [`generic/cycling-coach.md`](../generic/cycling-coach.md): zones (§2), how many hard days to schedule (§3), load and recovery weeks (§5), strength (§7), readiness (§9, §21), fueling (§15), illness (§18), the ride review (§22), and red flags (§23). This file keeps the decisions the bot needs when it edits the calendar, including a few operational details the coach file does not spell out as upload steps.

Final call: the coach (human or AI) applying the rules. Medical guidance always overrides the plan.

## Disclaimer

Coaching guidance, not medical advice. Stop and see a physician for red-flag symptoms (chest pain, fainting, palpitations, unexplained collapse in performance, focal bone pain). Get a medical check before starting hard training if you are new to intensity, over about 45 with risk factors, or have any cardiac symptoms.

## Readiness

Use the morning flags in §21 whenever morning data is available:

- Sleep under 6.5 h
- Sleep quality 2/5 or lower
- HRV more than 10% below the athlete's average
- Resting HR more than 7% above the athlete's average
- Legs 2/5 or lower
- Energy 2/5 or lower
- Stress 4/5 or higher

0 flags: go. 1 flag: go and monitor. 2 or more flags on a quality day: swap that session for easy endurance or rest, and re-upload so the connected app shows the easier day.

HRV and resting-HR flags need a running average, so they are rough in the first 1-2 weeks. One poor night is not, by itself, a hard-day trigger.

## Hard day and easy day

RPE targets to grade against: endurance 3-4, tempo and sweet spot 5-6, threshold 7-8, VO2 8-9, openers 5-6, an FTP test 9-10. Never adjust a test off of how earlier sessions felt.

Hard day (any of these):

- RPE is 2 or more above the top of its target
- The athlete did not finish the planned work
- Bad legs or poor sleep for 3 or more days running

Next quality session after a hard day: drop one interval set, or cut on-power 3% if the session only has 2 sets. One or the other, not both. If the cause was outside the workout (sleep, fuel, heat, life stress), ease only the next session. Make it a lasting change only if the same session type is hard twice or more while the athlete is well recovered. Two hard quality days in a row: upload easy endurance instead of the next quality session, and say why.

Easy day: RPE is 2 or more below the bottom of its target, with good legs and sleep. Two easy quality days in a row of the same type: add 2-3% on-power next time. Never add sets or time, and do not go past the top of the zone in §2.

## Load

Follow §5 and §9. Raise load gradually. The coach file's rule of thumb is CTL +3-5 TSS/day per week, so treat a rise of more than 5 TSS/day week over week as the ramp to notice. TSB below -30 is one marker alongside RPE, HRV, sleep, and mood, not a firm stand-alone trigger. When several of those are off together, swap the next quality session for easy endurance or start the recovery week early, and re-upload that day.

Use a recovery week every 3-4 weeks (a 3:1 or 2:1 pattern). A recovery week is about 40-50% less volume and keeps a little intensity. Do not raise anything that week. Extend it by up to a week if sleep, legs, or the markers above are still poor at the end.

Weekly load (RPE times minutes) up more than about 15% on the previous week, unless coming off a recovery week: hold or trim the next week and upload the trimmed files.

## Missed sessions

Key sessions are whichever days the athlete's own plan marks as key, not a fixed weekday.

- A missed key session moves to the next suitable day, or to the same slot next week, only if it can be done properly (not the day before another key session and not stacked on one). Otherwise skip it. Never stack two key sessions. Upload the moved file and delete the original day's event.
- Missed easy endurance days are not made up.
- Dates listed as planned days off are not missed and are not made up. Delete any event on those dates.
- More than about 7 days off: treat the comeback week as a recovery week, then resume.
- More than about 14 days off: a recovery week, then retest FTP before resuming (§2).
- Do not change FTP from a few easy rides. Retest every 6-8 weeks, or derive FTP from a recent best effort, and put the same number in every app that prescribes power.

## Illness

Follow §18. Be symptom-free for 24 h before returning. Stop and see a doctor for chest pain, palpitations, or breathlessness during the return. Replace or delete the calendar event so the connected app matches the return (an easy file, or no event). Do not make up sessions missed to illness.

## Strength

Follow §7. Heavy lower-body strength goes on a hard-ride day, after the ride or at least 6 h apart the same day, and not within 48 h before a key interval session. Which weekday that is depends on the athlete's plan. Do not park heavy legs on the day before a key interval session.

## What to send to intervals.icu

- Changed session: upsert the new file with the same `external_id` (`workout-YYYY-MM-DD` unless `state.json` uses another prefix) so the event is replaced.
- Rest day or planned day off: delete that date's event.
- Endurance day on Zwift: a RoboPacer is optional. Still upload a backup file. No bot on sweet spot, threshold, VO2, openers, or a test. Structured intervals stay on the file, because those targets need ERG.
- On rides over 90 minutes, cue the fueling targets in §15.
- Write `icu_rpe` as a whole number. `feel` is 1-5 with 1 = strong and 5 = weak, the opposite of the readiness legs/energy scale.
- Ride review shape: §22.

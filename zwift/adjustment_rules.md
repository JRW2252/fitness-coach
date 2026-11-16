# Adjustment rules for the 12-week Zwift plan

Use these rules to decide which `.zwo` to upsert today, or whether to delete the intervals.icu event. General coaching rules are in [`generic/cycling-coach.md`](../generic/cycling-coach.md). Follow that file for zones (§2), how many hard days to schedule (§3), readiness (§9, §21), load (§5), illness (§18), fueling (§15), strength programming (§7), the ride review (§22), and red flags (§23). This file keeps the Zwift and intervals.icu actions, and the plan choices the coach file does not spell out.

Final call: the coach (human or AI) applying the rules. Medical guidance always overrides the plan.

## Disclaimer

Coaching guidance, not medical advice. Stop and see a physician for red-flag symptoms (chest pain, fainting, palpitations, unexplained collapse in performance, focal bone pain). Get a medical check before starting hard training if you are new to intensity, over about 45 with risk factors, or have any cardiac symptoms.

## Week layout this plan uses

| Day | Session |
|---|---|
| Mon | 60 min easy Z2, the day after the long ride |
| Tue | 75 min Z2 |
| Wed | Quality session 1 |
| Thu | Upper-body, light, or rest. No heavy legs. No Zwift ride unless a rule moves a session here |
| Fri | Quality session 2, then heavy lower-body strength |
| Sat | Long ride |
| Sun | Rest (optional 40 min very-easy spin is in the library) |

This is two quality days plus a long ride, not a Mon/Wed/Fri hard layout. §3 uses about two hard days a week for most amateurs. Monday stays easy so intensity does not follow Saturday's long ride. Wednesday and Friday are the hard days, with Thursday light between them so the interval days are not back-to-back. Saturday is the long endurance ride. Tempo blocks, when the file has them, stay in that structured workout. A Mon/Wed/Fri hard layout would add a third intensity day and put it the morning after the long ride.

Heavy lower-body strength goes on Friday, after the quality ride or at least 6 h apart on that same day (§7: on a hard-ride day, not within 48 h before a key interval session). The next key interval session is the following Wednesday, which is outside 48 h. Do not put heavy legs on Wednesday: Friday's intervals would fall inside 48 h. Thursday is upper-body, light, or rest, so Friday is not preceded by heavy legs. A second strength day in base is allowed only on a hard-ride day that still leaves 48 h before the next key interval session. Build weeks keep one maintenance session.

## Load markers when choosing today's file

Follow §5 and §9. The ramp to notice is a CTL rise of more than 5 TSS/day week over week (the coach file's rule of thumb is +3-5, not a higher cutoff). TSB below -30 is one marker alongside RPE, HRV, sleep, and mood, not a firm stand-alone trigger. When several of those are off together, swap the next quality ride for a Z2 file or bring the lighter week forward, and re-upsert that day so Zwift shows the easier session.

Weekly load (RPE x minutes) up more than 15% on last week, unless coming off a deload or the lighter week: hold or trim, and upsert the trimmed files.

## Session changes the coach file does not spell out

RPE targets for grading: Z2 3-4, tempo and sweet spot 5-6, threshold 7-8, VO2 8-9, openers 5-6, FTP test 9-10. Never adjust an FTP test off of how earlier sessions felt.

Hard day (any of: RPE 2+ above the top of its target, work not finished, bad legs or poor sleep for 3+ days): on the next quality session, drop one interval set, or cut on-power 3% if that session has only 2 sets. One or the other, not both. If the cause was outside the workout, ease only the next session. Make it lasting only if the same session type is hard 2+ times while the athlete is well recovered. Two hard quality days in a row: upsert 75 min of Z2 instead of the next quality file.

Easy day (RPE 2+ below the bottom, with good legs and sleep): two easy quality days in a row of the same type means +2-3% on-power next time. Never add sets or time, and do not go past the top of the zone in §2.

Readiness flags are in §21. Two or more flags on a quality day: upsert a Z2 file or delete the event before the ride.

## Missed sessions and the plan clock

- A missed key ride (Wed, Fri, Sat) moves to the next suitable day, or to the same slot next week, only if it can be done properly (not the day before another key ride and not stacked on one). Otherwise skip it. Never stack two key rides. Upsert the moved file and delete the original day's event.
- Repeat the whole week (`slip_days += 7`) only if 2+ key sessions are missed in one week.
- Missed easy Z2 days are never made up.
- Dates in `days_off` are not missed and are not made up. Delete any event on those dates.
- Missed more than 7 days: comeback week in the style of week 4, then repeat the last hard week.
- More than 14 days off: a recovery week, then retest FTP before resuming (§2).
- Do not change FTP from a few easy rides.

## Illness on the calendar

Follow §18. Be symptom-free for 24 h before returning. Stop and see a doctor for chest pain, palpitations, or breathlessness during the return. Replace or delete the Zwift event so the calendar matches the return (an easy file, or no event). Do not make up sessions missed to illness.

## Lighter week, deloads, and FTP checks

- Weeks 5-6 are a build pair. Week 7 is the lighter week (2:1 style): about a third less time in the Wednesday, Friday, and Saturday files, with a short VO2 session kept. Wednesday of week 7 is a 20-min FTP check.
- Weeks 4, 9, and 12 are deload weeks. Week 9 is a deload (easy 45-60 min files). Never raise anything on a deload. Extend a deload by up to one week if sleep, legs, or the load markers above are still poor at the end of it.
- Retest FTP every 6-8 weeks, or derive it from a recent best effort (§2). This plan checks at week 7 (Wednesday) and week 12 (Friday). Put the same new number in Zwift and in intervals.icu before the next upsert. Do not adjust the test workout itself.

## What to send to Zwift

- Changed session: upsert the new `.zwo` with the same `external_id` (`cp12-YYYY-MM-DD` unless state uses another prefix) so the calendar event is replaced.
- Rest day, Thursday with no ride, or a planned day off: delete that date's event.
- Z2 day: name a RoboPacer from `state.json` and still upsert a backup Z2 file. Sit in the draft, leave at the planned duration, and drop to a slower bot if heart rate drifts or RPE goes above 4. No bot on sweet spot, threshold, VO2, openers, or an FTP test. Long rides that include tempo stay on the structured file.
- On rides over 90 minutes, cue the fueling targets in §15.
- Write `icu_rpe` as a whole number. `feel` is 1-5 with 1 = strong and 5 = weak, the opposite of the readiness legs/energy scale.

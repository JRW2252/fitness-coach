# First run

Start here if you have this repo and nothing else set up. The longer reference is [`README.md`](README.md). Writing a workout file is [`authoring_workouts.md`](authoring_workouts.md). The bot prompts are in [`routines/`](routines/).

Do the checklist in order. Each item says what "done" looks like. Stop when that check passes before moving on.

## Checklist

| Step | Done when |
|---|---|
| Account | You can open your intervals.icu calendar in a browser |
| FTP | Ride FTP (and heart-rate threshold, if you use it) is saved in intervals.icu settings, and the same FTP is saved in Zwift |
| API key | `echo "$INTERVALS_ICU_API_KEY" >/dev/null` does not print the key, and the helper does not exit with "is not set" |
| Zwift connected | Settings > Connections shows Zwift connected, with planned-workout upload on |
| Test workout | The example `.zwo` is on today's intervals.icu calendar and under Zwift > Workouts > Custom > Intervals.icu |
| Test ride | After you ride it, `list-activities` for today includes that activity |
| Log row | `logs/training_log.csv` has a data row for that ride (not just the header) |
| RPE | The activity on intervals.icu shows the RPE you wrote back |
| Week preview | The next few ride days are on the intervals.icu calendar, and rest days have no stale workout |
| Rest days | `state.json` lists your rest days, and a rest day has no planned workout |

## 1. Account, FTP, key, Zwift

Follow [README sections 1-3](README.md). In short: create the intervals.icu account, set FTP, create an API key under Settings > Developer settings, and export it only as an environment variable:

```bash
export INTERVALS_ICU_API_KEY="..."    # do not print, log, or commit this
```

Athlete id `0` means the owner of that key. Then connect Zwift and turn on planned-workout upload. Check that FTP matches in intervals.icu and in Zwift.

## 2. Bring your own plan

This repo does not ship a plan. Pick one of these:

1. **A folder of `.zwo` files you already have.** Point `workouts_dir` in `state.json` at that folder. Name files so a human can tell them apart (`tue_endurance_90.zwo` is enough). The calendar id is separate from the filename.
2. **A plan that already lives on the intervals.icu calendar.** Build workouts there with the text format in [`authoring_workouts.md`](authoring_workouts.md). The bot then decides whether today's event should stay, be replaced, or be deleted. You can still keep a copy of the file in git.
3. **Ask the coach to write files.** Give it [`generic/cycling-coach.md`](../generic/cycling-coach.md) and [`authoring_workouts.md`](authoring_workouts.md), plus your FTP, available days, and goal. It should write `.zwo` files (power as a fraction of FTP) into your folder and pass each one through `scripts/validate_zwo.py`. You approve the files before anything is uploaded.

Copy the example state and describe the plan there. From this folder:

```bash
cp state.example.json state.json
mkdir -p logs
cp templates/training_log.csv logs/training_log.csv
cp templates/readiness_log.csv logs/readiness_log.csv
```

Set `plan_path` to whatever you train from (a markdown plan, a link you keep locally, or a note that says "the intervals.icu calendar is the plan"). Set `workouts_dir`, `ftp_watts`, `rest_days` (for example `["Thu", "Sun"]`), and any `days_off`. Leave `ftp_watts` null until you have typed your own number. Do not commit `state.json` or `logs/`.

**Names and ids.** One planned workout per day uses `external_id` `{prefix}-{YYYY-MM-DD}`. The default prefix is `workout`, so the id is `workout-YYYY-MM-DD`. Uploading that id again replaces the event. The `.zwo` filename can be anything. Do not put the API key or a numeric athlete id in the filename or in `state.json`.

## 3. Prove the pipe with the example file

```bash
python scripts/validate_zwo.py examples/test_sync_20min.zwo
python scripts/intervals_icu.py upsert \
  --date YYYY-MM-DD \
  --zwo examples/test_sync_20min.zwo
```

Use today's date if you want to ride it now. Zwift only receives about the next 7 days, and only events flagged indoor (the helper does that unless you pass `--outdoor`). Restart Zwift and look under Workouts > Custom > Intervals.icu.

Ride it, or any short spin on the same day. Then:

```bash
python scripts/intervals_icu.py list-activities --oldest YYYY-MM-DD --newest YYYY-MM-DD
```

Copy the activity id from that JSON into the training log as one row (duration, power, heart rate, whatever the file actually returned). Leave RPE blank until you decide it. Write it back:

```bash
python scripts/intervals_icu.py set-rpe --activity-id ACTIVITY_ID --rpe 3
```

`feel`, if you send it, is 1-5 with 1 = strong and 5 = weak. Delete the test event when you are finished with it: `delete-by-date --date YYYY-MM-DD`.

## 4. Wire up your bot

The three prompts are generic. Replace every `{{PLACEHOLDER}}` with your paths, timezone, rest days, and FTP. Never paste the API key into the prompt. The process that runs the prompt needs `INTERVALS_ICU_API_KEY` in its environment (a shell export, a secret in the scheduler, or the host's secret store).

| Job | Template | Reads | Writes |
|---|---|---|---|
| Before the usual session | [`routines/morning_workout_drop.md`](routines/morning_workout_drop.md) | plan, `state.json`, rules, both logs | today's intervals.icu event (upsert or delete), readiness log after they reply, `state.json` if a rule changed the plan |
| After the usual session | [`routines/ride_check_in.md`](routines/ride_check_in.md) | new activities, `state.json`, rules, logs | a training-log row, `last_seen_activity_id`, RPE on the activity |
| Before the next block of days the app will sync | [`routines/week_ahead_preview.md`](routines/week_ahead_preview.md) | plan, logs, rules | one event per upcoming ride day, deletes on rest days |

A scheduler wants one cron expression per job. Two check-in times belong in one expression (`30 10,17 * * *`), not two expressions joined by a semicolon. Pick hours that match your own day. Nothing in this repo assumes a clock time.

If the assistant cannot schedule, run the same prompts on demand. Say "drop today's workout" for the morning template, and "check in on my ride" for the ride template. Run the week-ahead prompt when you want the next week on the calendar (Zwift only keeps about 7 days, so do this at least weekly).

**Zwift-only extras, both optional.** If you ride Z2 in Zwift you can ask for a RoboPacer and still upload a backup `.zwo`. If the API is down you can copy that file into `Documents/Zwift/Workouts/<ZWIFT_USER_ID>/` on the computer that runs Zwift. Skip both when you are not using Zwift. Do not commit the Zwift user-folder id.

**Keep private.** `state.json`, `logs/`, and `.env`. [`gitignore.example`](gitignore.example) lists those patterns. The API key stays in the environment, not in a file you commit.

## 5. First real week

Run the week-ahead prompt once rest days are in `state.json`. Done when each ride day in the next week has an event, each rest day does not, and Zwift (or your other connection) shows the indoor workouts that fall inside its upload window. After the first real ride, the check-in prompt should append a log row and write RPE back without you hand-editing the API.

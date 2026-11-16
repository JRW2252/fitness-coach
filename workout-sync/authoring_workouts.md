# Authoring workouts

This is how to create the files your bot uploads. It is not a training plan. Pair it with the zones and session shapes in [`generic/cycling-coach.md`](../generic/cycling-coach.md) (§2 and §4). Check a file with [`scripts/validate_zwo.py`](scripts/validate_zwo.py) before the first upsert.

## Power is a fraction of FTP

In a `.zwo`, `Power="0.65"` means 65% of FTP. The same file works for any rider. Do not write watts into the file. Watts show up only after Zwift or intervals.icu applies that athlete's FTP.

A target of "about 160 W" is wrong in the file. Divide by FTP first, or write the fraction directly from the zone table below.

## From the coach file to a fraction

§2 of the coach file states zones as a percent of FTP. Move the decimal point two places to get the `.zwo` number (88% becomes `0.88`).

| Prescription in the coach file | Fraction to write |
|---|---|
| Z1 recovery, under 55% | below `0.55` (the sync example uses `0.40` to `0.55` for a cooldown) |
| Z2 endurance, 56-75% | `0.56` to `0.75` (a steady endurance step often uses `0.62` to `0.68`) |
| Tempo, 76-90% | `0.76` to `0.90` |
| Sweet spot, 88-94% | `0.88` to `0.94` |
| Threshold, 95-105% in §2, or 95-100% in the §4 library | `0.95` to `1.05` |
| VO2, 106-120% | `1.06` to `1.20` |
| Easy recovery between intervals | `0.50` to `0.55` |

Stay inside the zone. Do not invent a second set of zones in the file.

## `.zwo` elements

A `.zwo` is XML. intervals.icu's workout builder accepts an uploaded `.zwo` and can download a workout as `.zwo` ([workout builder thread](https://forum.intervals.icu/t/workout-builder/1163)). The thread's example uses `<SteadyState>` with `Power` as a fraction and optional cadence bounds. The other tags below are the Zwift workout vocabulary that a `.zwo` importer is expected to keep. **Ramp and textevent are not spelled out as their own tags in that thread**, so treat those two as Zwift `.zwo` and confirm the imported workout still looks right.

Durations are seconds. `Power`, `PowerLow`, `PowerHigh`, `OnPower`, and `OffPower` are fractions of FTP.

| Element | Required attributes | Optional |
|---|---|---|
| `Warmup` | `Duration`, `PowerLow`, `PowerHigh` | `Cadence` |
| `Cooldown` | `Duration`, `PowerLow`, `PowerHigh` | `Cadence` |
| `SteadyState` | `Duration`, `Power` | `Cadence`, or `CadenceLow` and `CadenceHigh` |
| `IntervalsT` | `Repeat`, `OnDuration`, `OffDuration`, `OnPower`, `OffPower` | `Cadence` |
| `Ramp` | `Duration`, `PowerLow`, `PowerHigh` | `Cadence` |
| `FreeRide` | `Duration` | `FlatRoad` (`0` or `1`) |
| `textevent` | `timeoffset`, `message` | Nested inside a step. `timeoffset` is seconds from the start of that step |

`IntervalsT` time is `Repeat * (OnDuration + OffDuration)`, including the recovery after the last rep.

Minimal shape:

```xml
<workout_file>
  <author>cycling coach</author>
  <name>Short name</name>
  <description>One sentence a rider can read on the device.</description>
  <sportType>bike</sportType>
  <workout>
    <Warmup Duration="600" PowerLow="0.45" PowerHigh="0.70"/>
    <SteadyState Duration="1200" Power="0.65"/>
    <Cooldown Duration="300" PowerLow="0.55" PowerHigh="0.40"/>
  </workout>
</workout_file>
```

## Small templates

These are patterns, not a plan. Change the durations to match the athlete's plan. Run the validator on the file you actually save.

Endurance (Z2):

```xml
<Warmup Duration="600" PowerLow="0.45" PowerHigh="0.70"/>
<SteadyState Duration="3000" Power="0.65" Cadence="90"/>
<Cooldown Duration="300" PowerLow="0.55" PowerHigh="0.40"/>
```

Sweet spot (3 x 12 min at 0.91, 5 min easy). 3 x (720 + 300) = 3060 seconds of intervals:

```xml
<Warmup Duration="900" PowerLow="0.45" PowerHigh="0.75"/>
<IntervalsT Repeat="3" OnDuration="720" OffDuration="300" OnPower="0.91" OffPower="0.55"/>
<Cooldown Duration="600" PowerLow="0.60" PowerHigh="0.40"/>
```

Threshold (2 x 20 min at 1.00, 5 min easy):

```xml
<Warmup Duration="900" PowerLow="0.45" PowerHigh="0.80"/>
<IntervalsT Repeat="2" OnDuration="1200" OffDuration="300" OnPower="1.00" OffPower="0.55"/>
<Cooldown Duration="600" PowerLow="0.60" PowerHigh="0.40"/>
```

VO2 (5 x 4 min at 1.15, equal easy recovery):

```xml
<Warmup Duration="900" PowerLow="0.45" PowerHigh="0.75"/>
<IntervalsT Repeat="5" OnDuration="240" OffDuration="240" OnPower="1.15" OffPower="0.50"/>
<Cooldown Duration="600" PowerLow="0.55" PowerHigh="0.40"/>
```

A textevent is optional. Example, unverified as a distinct intervals.icu feature beyond "a `.zwo` imports":

```xml
<SteadyState Duration="600" Power="0.65">
  <textevent timeoffset="30" message="Settle into an easy gear."/>
</SteadyState>
```

## intervals.icu text format

The workout builder edits a workout as plain text ([same thread](https://forum.intervals.icu/t/workout-builder/1163)). A line that starts with `-` is a step. Confirmed constructs from that post:

- Duration: `30s`, `10m`, `1m30`
- Power: `80%` (of FTP) or `100w` (absolute watts; prefer `%` so the file still matches the athlete)
- Heart rate: `60% HR` (of max HR), `100% LTHR`
- Cadence: `90rpm` or a range `90-100rpm`
- Ranges: `80-90%`
- Ramps: `Ramp 60-80%` or `Ramp 100-200w`
- Repeats: a line such as `Main set 6x` before the steps that repeat
- Zones: `- 60m Z2` for zone-2 power, or `- 60m Z2 HR` for heart rate

```
Warmup
- 10m 55%

Main set 3x
- 12m 91%
- 5m 55%

Cooldown
- 10m 50%
```

You can build the workout in intervals.icu this way and skip a hand-written `.zwo`. The bot can still upsert a `.zwo` when you want the file in git. Anything past the constructs above (for example a particular keyword you saw in a screenshot) is unverified until you try it in the builder.

## Formats intervals.icu accepts

Confirmed on the workout builder thread: **upload** an existing `.mrc`, `.erg`, or `.zwo`, and **download** `.zwo`, `.mrc`, or `.erg`.

A separate API note also lists `.fit` as a download format for planned workouts (`ext=zwo|fit|mrc|erg` on the events endpoint): [downloading planned workouts](https://forum.intervals.icu/t/downloading-planned-workouts-from-the-api/93737). This repo's helper uploads `.zwo` text. Use `.zwo` unless you already have an `.erg` or `.mrc`.

`.erg` and `.mrc` are time-based watt steps from other editors. If those watts were baked in for one athlete, they will not track a new FTP. Prefer `%` in the text builder, or fractions in `.zwo`.

## Validation checklist

1. `python scripts/validate_zwo.py path/to/file.zwo` prints `OK` and a duration. The script checks well-formed XML, a `workout_file` with a name and at least one step, power fractions between 0.3 and 2.0, and a positive total duration.
2. The duration it prints is the duration you meant (name and description agree).
3. Every power attribute is a fraction of FTP, not a watt number. `Power="200"` fails the validator on purpose.
4. The workout sits in the zone you took from the coach file.
5. For Zwift, the calendar event is flagged indoor. The helper does that unless you pass `--outdoor`.
6. After upload, the intervals.icu calendar shows the event, and Zwift shows it under Workouts > Custom > Intervals.icu when the date is inside the next 7 days.

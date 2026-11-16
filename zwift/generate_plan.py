#!/usr/bin/env python3
"""Generate a 12-week power-based Zwift (.zwo) indoor cycling plan.

Workouts are written as fractions of FTP, so the same files work for any
rider. Pass --ftp only if you want a watt-target table printed to stdout.

Example:
    python generate_plan.py --out ./workouts --ftp 250
"""

from __future__ import annotations

import argparse
import os
import zipfile
from xml.sax.saxutils import escape

# Default power as a fraction of FTP. These sit inside the zone ranges in
# generic/cycling-coach.md and below the ceilings in adjustment_rules.md.
Z2 = 0.65
Z2_EASY = 0.62
Z2_RECOVERY = 0.60
Z2_VERY_EASY = 0.55
LONG_Z2 = 0.68
TEMPO = 0.83
SWEET_SPOT = 0.91
THRESHOLD = 1.00
VO2 = 1.15
RECOVERY = 0.55

# Week-by-week quality sessions: (wed, fri, sat).
# wed/fri: ("ss", sets, minutes) | ("th", sets, minutes) | ("vo", sets, minutes)
#          | ("spin", count) | ("easy",)
# sat: (total_minutes, tempo_reps, tempo_minutes)  — tempo_reps 0 means all Z2
PLAN = {
    1: (("ss", 3, 10), ("spin", 6), (150, 0, 0)),
    2: (("ss", 3, 12), ("spin", 6), (165, 0, 0)),
    3: (("ss", 3, 15), ("spin", 8), (180, 0, 0)),
    4: (("ss", 2, 10), ("easy",), (120, 0, 0)),
    5: (("th", 2, 15), ("vo", 5, 3), (165, 2, 15)),
    6: (("th", 3, 12), ("vo", 6, 3), (165, 2, 20)),
    7: (("th", 2, 20), ("vo", 5, 4), (180, 2, 20)),
    8: (("th", 3, 15), ("vo", 6, 4), (180, 3, 15)),
    10: (("th", 2, 20), ("vo", 5, 4), (180, 2, 20)),
    11: (("th", 3, 15), ("vo", 6, 4), (195, 3, 15)),
}

# Week 9 is a deload / travel week: only easy-ride files are generated.
# Week 12 is a test week: openers, a 20-min FTP test, and an easy long ride.


def warmup(minutes: int) -> str:
    return f'<Warmup Duration="{minutes * 60}" PowerLow="0.45" PowerHigh="0.70"/>'


def cooldown(minutes: int) -> str:
    return f'<Cooldown Duration="{minutes * 60}" PowerLow="0.60" PowerHigh="0.40"/>'


def steady(minutes: float, power: float, cad: int | None = None) -> str:
    cad_attr = f' Cadence="{cad}"' if cad else ""
    return f'<SteadyState Duration="{int(minutes * 60)}" Power="{power}"{cad_attr}/>'


def intervals(
    repeats: int,
    on_min: float,
    off_min: float,
    on_power: float,
    off_power: float,
    cad: int | None = None,
) -> str:
    cad_attr = f' Cadence="{cad}"' if cad else ""
    return (
        f'<IntervalsT Repeat="{repeats}" '
        f'OnDuration="{int(on_min * 60)}" OffDuration="{int(off_min * 60)}" '
        f'OnPower="{on_power}" OffPower="{off_power}"{cad_attr}/>'
    )


def interval_block_minutes(repeats: int, on_min: float, off_min: float) -> float:
    # Work + the recoveries between reps, plus a trailing recovery matching the
    # original generator (off after the last rep is included in the budget).
    return repeats * on_min + (repeats - 1) * off_min + off_min


def write_zwo(out_dir: str, fname: str, name: str, desc: str, steps: list[str], author: str, tag: str) -> str:
    xml = (
        "<workout_file>\n"
        f"  <author>{escape(author)}</author>\n"
        f"  <name>{escape(name)}</name>\n"
        f"  <description>{escape(desc)}</description>\n"
        "  <sportType>bike</sportType>\n"
        f"  <tags><tag name=\"{escape(tag)}\"/></tags>\n"
        "  <workout>\n"
        + "".join(f"    {step}\n" for step in steps)
        + "  </workout>\n"
        "</workout_file>\n"
    )
    path = os.path.join(out_dir, f"{fname}.zwo")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(xml)
    return path


def z2_ride(
    out_dir: str,
    fname: str,
    name: str,
    total: int,
    power: float = Z2,
    desc: str = "Easy Zone 2. Keep it conversational.",
    author: str = "",
    tag: str = "",
) -> None:
    write_zwo(
        out_dir,
        fname,
        name,
        desc,
        [warmup(10), steady(total - 15, power), cooldown(5)],
        author,
        tag,
    )


def interval_ride(
    out_dir: str,
    fname: str,
    name: str,
    desc: str,
    repeats: int,
    on_min: float,
    off_min: float,
    on_power: float,
    off_power: float,
    total: int,
    author: str,
    tag: str,
) -> None:
    used = 15 + interval_block_minutes(repeats, on_min, off_min) + 10
    fill = max(0, total - used)
    steps = [warmup(15), intervals(repeats, on_min, off_min, on_power, off_power)]
    if fill:
        steps.append(steady(fill, Z2))
    steps.append(cooldown(10))
    write_zwo(out_dir, fname, name, desc, steps, author, tag)


def spinups(
    out_dir: str,
    fname: str,
    name: str,
    count: int,
    total: int = 75,
    author: str = "",
    tag: str = "",
) -> None:
    used = 15 + count * 3 + 10
    write_zwo(
        out_dir,
        fname,
        name,
        f"Z2 with {count}x30s high-cadence spin-ups (110+ rpm), not hard on power.",
        [
            warmup(15),
            steady(10, Z2),
            intervals(count, 0.5, 2.5, 0.72, Z2, 110),
            steady(max(0, total - used - 10), Z2),
            cooldown(10),
        ],
        author,
        tag,
    )


def long_ride(
    out_dir: str,
    fname: str,
    name: str,
    total: int,
    tempo_reps: int = 0,
    tempo_min: int = 0,
    author: str = "",
    tag: str = "",
) -> None:
    if not tempo_reps:
        write_zwo(
            out_dir,
            fname,
            name,
            "Long Zone 2. Fuel 60-90 g carbs/hr. Watch HR drift in the second half.",
            [warmup(10), steady(total - 20, LONG_Z2), cooldown(10)],
            author,
            tag,
        )
        return
    block = tempo_reps * tempo_min + tempo_reps * 5
    first = total - 10 - block - 20 - 10
    tempo_step = (
        intervals(tempo_reps, tempo_min, 5, TEMPO, 0.62)
        if tempo_reps > 1
        else steady(tempo_min, TEMPO)
    )
    write_zwo(
        out_dir,
        fname,
        name,
        f"Long Z2 with {tempo_reps}x{tempo_min} min tempo late in the ride "
        f"(76-90% FTP). Fuel 60-90 g carbs/hr.",
        [warmup(10), steady(first, LONG_Z2), tempo_step, steady(15, LONG_Z2), cooldown(10)],
        author,
        tag,
    )


def hours_label(total_min: int) -> str:
    return f"{total_min // 60}h{total_min % 60:02d}"


def generate(out_dir: str, author: str, tag: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)

    z2_ride(
        out_dir,
        "Mon_Z2_60",
        "Mon - Z2 Easy Spin 60 min",
        60,
        Z2_EASY,
        "Easy spin after lower-body strength. Keep it light.",
        author,
        tag,
    )
    z2_ride(out_dir, "Tue_Z2_75", "Tue - Z2 Endurance 75 min", 75, author=author, tag=tag)
    z2_ride(
        out_dir,
        "Sun_Optional_Easy_40",
        "Sun - Optional Easy Spin 40 min",
        40,
        Z2_VERY_EASY,
        "Optional recovery spin. Very easy. Skip if the weekly default is a rest day.",
        author,
        tag,
    )

    for week, (wed, fri, sat) in PLAN.items():
        prefix = f"Wk{week:02d}"
        kind, reps, minutes = wed
        if kind == "ss":
            interval_ride(
                out_dir,
                f"{prefix}_Wed_SweetSpot_{reps}x{minutes}",
                f"{prefix} Wed - Sweet Spot {reps}x{minutes}",
                "Sweet spot 88-94% FTP, 5 min easy between.",
                reps,
                minutes,
                5,
                SWEET_SPOT,
                RECOVERY,
                80,
                author,
                tag,
            )
        else:
            interval_ride(
                out_dir,
                f"{prefix}_Wed_Threshold_{reps}x{minutes}",
                f"{prefix} Wed - Threshold {reps}x{minutes}",
                "Threshold 95-105% FTP, 5 min easy between.",
                reps,
                minutes,
                5,
                THRESHOLD,
                RECOVERY,
                85,
                author,
                tag,
            )

        if fri[0] == "spin":
            spinups(
                out_dir,
                f"{prefix}_Fri_Z2_SpinUps_{fri[1]}x30s",
                f"{prefix} Fri - Z2 + {fri[1]}x30s Spin-Ups",
                fri[1],
                author=author,
                tag=tag,
            )
        elif fri[0] == "easy":
            z2_ride(
                out_dir,
                f"{prefix}_Fri_Easy_Z2_60",
                f"{prefix} Fri - Easy Z2 60 min",
                60,
                Z2_RECOVERY,
                "Recovery week. Easy.",
                author,
                tag,
            )
        else:
            _, vo_reps, vo_min = fri
            interval_ride(
                out_dir,
                f"{prefix}_Fri_VO2_{vo_reps}x{vo_min}",
                f"{prefix} Fri - VO2 Max {vo_reps}x{vo_min} min",
                "VO2 110-120% FTP, equal-time easy recovery.",
                vo_reps,
                vo_min,
                vo_min,
                VO2,
                0.50,
                75,
                author,
                tag,
            )

        total, tempo_reps, tempo_min = sat
        label = hours_label(total)
        suffix = f"_{tempo_reps}x{tempo_min}Tempo" if tempo_reps else ""
        title_suffix = f" + {tempo_reps}x{tempo_min} Tempo" if tempo_reps else ""
        long_ride(
            out_dir,
            f"{prefix}_Sat_Long_Z2_{label}{suffix}",
            f"{prefix} Sat - Long Z2 {label}{title_suffix}",
            total,
            tempo_reps,
            tempo_min,
            author,
            tag,
        )

    # Week 9 deload / travel: easy rides only. Mark specific dates as days off
    # in state.json rather than generating a full week of quality work.
    z2_ride(
        out_dir,
        "Wk09_Deload_Easy_45",
        "Wk09 Deload - Easy Ride 45 min",
        45,
        Z2_RECOVERY,
        "Deload or travel week. Easy.",
        author,
        tag,
    )
    z2_ride(
        out_dir,
        "Wk09_Deload_Easy_60",
        "Wk09 Deload - Easy Ride 60 min",
        60,
        Z2_RECOVERY,
        "Deload or travel week. Easy.",
        author,
        tag,
    )

    write_zwo(
        out_dir,
        "Wk12_Wed_Openers_2x8",
        "Wk12 Wed - Openers 2x8 Threshold",
        "Openers before the FTP test. Crisp, not exhausting.",
        [
            warmup(15),
            intervals(2, 8, 5, THRESHOLD, RECOVERY),
            steady(15, Z2),
            intervals(3, 0.5, 2.5, 1.2, 0.5),
            cooldown(10),
        ],
        author,
        tag,
    )
    write_zwo(
        out_dir,
        "Wk12_Fri_FTP_Test_20min",
        "Wk12 Fri - FTP Test (20 min)",
        "20-min all-out effort. FTP = 95% of 20-min avg power. Pace evenly.",
        [
            warmup(15),
            steady(5, 1.05),
            steady(10, 0.50),
            '<FreeRide Duration="1200" FlatRoad="0"/>',
            cooldown(15),
        ],
        author,
        tag,
    )
    long_ride(
        out_dir,
        "Wk12_Sat_Easy_Z2_2h00",
        "Wk12 Sat - Easy Z2 2h00",
        120,
        author=author,
        tag=tag,
    )

    return sorted(f for f in os.listdir(out_dir) if f.endswith(".zwo"))


def print_targets(ftp: int) -> None:
    rows = [
        ("Z2 very easy / recovery between intervals", Z2_VERY_EASY, RECOVERY),
        ("Z2 easy (Mon)", Z2_EASY, Z2_EASY),
        ("Z2 default", Z2, Z2),
        ("Long-ride Z2", LONG_Z2, LONG_Z2),
        ("Tempo", TEMPO, TEMPO),
        ("Sweet spot", SWEET_SPOT, SWEET_SPOT),
        ("Threshold", THRESHOLD, THRESHOLD),
        ("VO2", VO2, VO2),
    ]
    print(f"Watt targets at FTP {ftp} W (fractions used in the .zwo files):")
    print(f"  {'Session type':<42} {'% FTP':>6}  {'Watts':>5}")
    for label, lo, hi in rows:
        if lo == hi:
            print(f"  {label:<42} {lo * 100:>5.0f}%  {round(ftp * lo):>5}")
        else:
            print(
                f"  {label:<42} {lo * 100:>2.0f}-{hi * 100:.0f}%  "
                f"{round(ftp * lo)}-{round(ftp * hi)}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "workouts"),
        help="Directory to write .zwo files (default: ./workouts next to this script)",
    )
    parser.add_argument(
        "--author",
        default="cycling coach",
        help="Author tag written into each .zwo file",
    )
    parser.add_argument(
        "--tag",
        default="CUSTOM 12 WEEK PLAN",
        help="Zwift workout tag",
    )
    parser.add_argument(
        "--ftp",
        type=int,
        default=None,
        help="Optional FTP in watts; prints a target table (not written into files)",
    )
    parser.add_argument(
        "--zip",
        dest="zip_path",
        default=None,
        help="Optional path to a zip of the generated workouts",
    )
    args = parser.parse_args()

    files = generate(args.out, args.author, args.tag)
    print(f"Wrote {len(files)} workouts to {args.out}")
    print("\n".join(files))
    if args.ftp:
        print()
        print_targets(args.ftp)
    if args.zip_path:
        with zipfile.ZipFile(args.zip_path, "w") as archive:
            for name in files:
                archive.write(os.path.join(args.out, name), name)
        print(f"\nZip: {args.zip_path}")


if __name__ == "__main__":
    main()

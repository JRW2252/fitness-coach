#!/usr/bin/env python3
"""Check a Zwift .zwo file before you upload it.

Confirms the file is well-formed XML, has a workout_file with a name and at
least one step, that power targets are fractions of FTP in a sane range, and
that the steps add up to a positive duration.

Usage:
    python validate_zwo.py ../examples/test_sync_20min.zwo
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

POWER_ATTRS = ("Power", "PowerLow", "PowerHigh", "OnPower", "OffPower")
STEP_TAGS = {"Warmup", "Cooldown", "SteadyState", "IntervalsT", "Ramp", "FreeRide"}
MIN_POWER = 0.3
MAX_POWER = 2.0


def _duration_seconds(step: ET.Element) -> int | None:
    if step.tag == "IntervalsT":
        try:
            repeat = int(step.attrib["Repeat"])
            on_s = int(step.attrib["OnDuration"])
            off_s = int(step.attrib["OffDuration"])
        except (KeyError, ValueError):
            return None
        if repeat < 1 or on_s < 0 or off_s < 0:
            return None
        return repeat * (on_s + off_s)
    raw = step.attrib.get("Duration")
    if raw is None:
        return None
    try:
        seconds = int(raw)
    except ValueError:
        return None
    if seconds <= 0:
        return None
    return seconds


def validate(path: str) -> tuple[list[str], int]:
    """Return (errors, total_seconds). total_seconds is 0 when the file does not parse."""
    errors: list[str] = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"not well-formed XML: {exc}"], 0

    root = tree.getroot()
    if root.tag != "workout_file":
        errors.append(f"root element is <{root.tag}>, expected <workout_file>")
        return errors, 0

    name = (root.findtext("name") or "").strip()
    if not name:
        errors.append("missing <name>")

    workout = root.find("workout")
    if workout is None:
        errors.append("missing <workout>")
        return errors, 0

    steps = [child for child in list(workout) if child.tag != "textevent"]
    if not steps:
        errors.append("<workout> has no steps")
        return errors, 0

    total = 0
    for index, step in enumerate(steps, start=1):
        if step.tag not in STEP_TAGS:
            errors.append(f"step {index}: unknown element <{step.tag}>")
            continue
        seconds = _duration_seconds(step)
        if seconds is None:
            errors.append(f"step {index}: <{step.tag}> has no positive duration")
        else:
            total += seconds
        for attr in POWER_ATTRS:
            if attr not in step.attrib:
                continue
            try:
                power = float(step.attrib[attr])
            except ValueError:
                errors.append(f"step {index}: {attr} is not a number")
                continue
            if power < MIN_POWER or power > MAX_POWER:
                errors.append(
                    f"step {index}: {attr}={power} is outside {MIN_POWER}-{MAX_POWER} "
                    "(power must be a fraction of FTP, not watts)"
                )
    if total <= 0 and not any("duration" in err for err in errors):
        errors.append("total duration is 0")
    return errors, total


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python validate_zwo.py FILE.zwo [FILE.zwo ...]", file=sys.stderr)
        return 2
    failed = False
    for path in argv[1:]:
        errors, total = validate(path)
        if errors:
            failed = True
            print(f"{path}: FAIL", file=sys.stderr)
            for err in errors:
                print(f"  {err}", file=sys.stderr)
            continue
        minutes = total / 60
        print(f"{path}: OK ({minutes:.1f} min)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""Small intervals.icu helper for the Zwift plan workflow.

Reads the API key from the INTERVALS_ICU_API_KEY environment variable
(never prints it). Talks to the API with curl and HTTP basic auth, because
some Python HTTP clients (including urllib) have been observed to get HTTP
403 from intervals.icu with the same credentials.

Auth, as documented by intervals.icu: username API_KEY, password = your key.
Athlete id 0 means "the athlete who owns this key."

Examples:
    export INTERVALS_ICU_API_KEY=...    # do not commit this
    python intervals_icu.py upsert --date 2026-11-16 --zwo ../workouts/Mon_Z2_60.zwo
    python intervals_icu.py list-activities --oldest 2026-11-01 --newest 2026-11-16
    python intervals_icu.py set-rpe --activity-id 123456 --rpe 5 --feel 2
    python intervals_icu.py list-events --oldest 2026-11-16 --newest 2026-11-22
    python intervals_icu.py delete-event --event-id 123456
    python intervals_icu.py delete-by-date --date 2026-11-16
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from typing import Any

BASE = "https://intervals.icu/api/v1"
DEFAULT_PREFIX = "cp12"
ENV_VAR = "INTERVALS_ICU_API_KEY"


def require_key() -> str:
    key = os.environ.get(ENV_VAR, "").strip()
    if not key:
        sys.exit(
            f"{ENV_VAR} is not set. Create an API key in intervals.icu "
            f"(Settings > Developer Settings) and export it in your environment. "
            f"Do not commit the key or print it."
        )
    return key


def curl_json(
    method: str,
    path: str,
    payload: Any | None = None,
    key: str | None = None,
) -> Any:
    """Call the API with curl. The key is passed to curl and never printed."""
    api_key = key if key is not None else require_key()
    url = f"{BASE}{path}"
    cmd = [
        "curl",
        "-sS",
        "-X",
        method,
        "-u",
        f"API_KEY:{api_key}",
        "-H",
        "Accept: application/json",
        "-w",
        "\n%{http_code}",
        url,
    ]
    body = None
    if payload is not None:
        body = json.dumps(payload)
        cmd[4:4] = ["-H", "Content-Type: application/json", "--data-binary", "@-"]

    try:
        result = subprocess.run(
            cmd,
            input=body,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        sys.exit("curl is required but was not found on PATH.")

    if result.returncode != 0:
        # Do not echo the command: it contains the API key.
        err = (result.stderr or result.stdout or "curl failed").strip()
        sys.exit(f"curl failed talking to intervals.icu: {err}")

    raw = result.stdout or ""
    # Split off the HTTP status we appended with -w.
    if "\n" in raw:
        response_body, _, status_str = raw.rpartition("\n")
    else:
        response_body, status_str = "", raw
    try:
        status = int(status_str)
    except ValueError:
        sys.exit(f"Unexpected curl output (status unreadable). Body length: {len(raw)}")

    if status >= 400:
        sys.exit(f"intervals.icu returned HTTP {status}: {response_body.strip()[:2000]}")

    if not response_body.strip():
        return None
    try:
        return json.loads(response_body)
    except json.JSONDecodeError:
        return response_body


def external_id_for(day: str, prefix: str) -> str:
    return f"{prefix}-{day}"


def upsert_event(
    day: str,
    zwo_path: str,
    prefix: str = DEFAULT_PREFIX,
    event_type: str = "VirtualRide",
    indoor: bool = True,
    name: None | str = None,
) -> Any:
    with open(zwo_path, encoding="utf-8") as handle:
        contents = handle.read()
    filename = os.path.basename(zwo_path)
    payload = [
        {
            "category": "WORKOUT",
            "start_date_local": f"{day}T00:00:00",
            "type": event_type,
            "indoor": indoor,
            "filename": filename,
            "file_contents": contents,
            "external_id": external_id_for(day, prefix),
        }
    ]
    if name:
        payload[0]["name"] = name
    return curl_json("POST", "/athlete/0/events/bulk?upsert=true", payload)


def list_events(oldest: str, newest: str) -> Any:
    return curl_json("GET", f"/athlete/0/events?oldest={oldest}&newest={newest}")


def list_activities(oldest: str, newest: str) -> Any:
    return curl_json("GET", f"/athlete/0/activities?oldest={oldest}&newest={newest}")


def delete_event(event_id: str) -> Any:
    return curl_json("DELETE", f"/athlete/0/events/{event_id}")


def delete_by_date(day: str, prefix: str = DEFAULT_PREFIX) -> Any:
    events = list_events(day, day) or []
    target = external_id_for(day, prefix)
    deleted = []
    for event in events:
        if str(event.get("external_id") or "") == target:
            delete_event(str(event["id"]))
            deleted.append({"id": event["id"], "external_id": target})
    return {"deleted": deleted, "external_id": target}


def set_rpe(activity_id: str, rpe: int, feel: int | None = None) -> Any:
    if rpe != int(rpe):
        sys.exit("icu_rpe must be a whole number (intervals.icu rejects decimals).")
    payload: dict[str, int] = {"icu_rpe": int(rpe)}
    if feel is not None:
        if feel < 1 or feel > 5:
            sys.exit("feel must be 1-5 (1 = strong, 5 = weak).")
        payload["feel"] = int(feel)
    return curl_json("PUT", f"/activity/{activity_id}", payload)


def _dump(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def _add_date_args(parser: argparse.ArgumentParser, oldest: bool, newest: bool) -> None:
    today = date.today().isoformat()
    if oldest:
        parser.add_argument("--oldest", required=True, help="YYYY-MM-DD")
    if newest:
        parser.add_argument("--newest", default=today, help="YYYY-MM-DD (default: today)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_up = sub.add_parser("upsert", help="Create or replace a planned workout on a date")
    p_up.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_up.add_argument("--zwo", required=True, help="Path to a .zwo file")
    p_up.add_argument("--prefix", default=DEFAULT_PREFIX, help="external_id prefix")
    p_up.add_argument("--name", default=None, help="Optional event name")
    p_up.add_argument("--type", default="VirtualRide", dest="event_type")
    p_up.add_argument("--outdoor", action="store_true", help="Set indoor=false")

    p_la = sub.add_parser("list-activities", help="List activities in a date range")
    _add_date_args(p_la, oldest=True, newest=True)

    p_le = sub.add_parser("list-events", help="List planned events in a date range")
    _add_date_args(p_le, oldest=True, newest=True)

    p_de = sub.add_parser("delete-event", help="Delete one event by intervals.icu id")
    p_de.add_argument("--event-id", required=True)

    p_dd = sub.add_parser("delete-by-date", help="Delete the upserted event for a date")
    p_dd.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_dd.add_argument("--prefix", default=DEFAULT_PREFIX)

    p_rpe = sub.add_parser("set-rpe", help="Write RPE (and optional feel) to an activity")
    p_rpe.add_argument("--activity-id", required=True)
    p_rpe.add_argument("--rpe", type=int, required=True, help="Whole number, typically 1-10")
    p_rpe.add_argument(
        "--feel",
        type=int,
        default=None,
        help="Optional 1-5, where 1 = strong and 5 = weak",
    )

    args = parser.parse_args()
    require_key()

    if args.cmd == "upsert":
        _dump(
            upsert_event(
                args.date,
                args.zwo,
                prefix=args.prefix,
                event_type=args.event_type,
                indoor=not args.outdoor,
                name=args.name,
            )
        )
    elif args.cmd == "list-activities":
        _dump(list_activities(args.oldest, args.newest))
    elif args.cmd == "list-events":
        _dump(list_events(args.oldest, args.newest))
    elif args.cmd == "delete-event":
        _dump(delete_event(args.event_id))
    elif args.cmd == "delete-by-date":
        _dump(delete_by_date(args.date, prefix=args.prefix))
    elif args.cmd == "set-rpe":
        _dump(set_rpe(args.activity_id, args.rpe, args.feel))


if __name__ == "__main__":
    main()

"""Deterministic graders and judge-prompt helpers for the coach evals.

Standard library only, so the evals run anywhere Python 3.9+ is installed.
"""
import json
import re

# A number, optionally a range like "265-300" or "265 to 300", followed by a unit.
_NUM = r"(\d{1,4}(?:[.,]\d+)?)"
_RANGE_SEP = r"\s*(?:-|–|—|to)\s*"

# Units are matched case-insensitively. Order matters: longer units first so
# "g/h" is not read as "g".
UNIT_PATTERNS = {
    "W": r"(?:w|watts?)(?![a-z/])",
    "g/h": r"(?:g|grams?)(?:\s+(?:of\s+)?(?:carbs?|carbohydrates?|cho))?\s*(?:/|per|an|each|every)\s*(?:h|hr|hour)",
    "g": r"(?:g|grams?)(?![a-z/])",
    "mg": r"(?:mg|milligrams?)(?![a-z/])",
    "kcal": r"(?:kcal|calories|cal)(?![a-z])",
    "%": r"%",
}


def _to_float(text):
    return float(text.replace(",", "."))


def extract_numbers(text, unit):
    """Return every number (and both ends of every range) followed by `unit`.

    Thousands separators like "1,000" are handled by stripping commas that are
    followed by exactly three digits before parsing.
    """
    if unit not in UNIT_PATTERNS:
        raise ValueError("unknown unit: %s" % unit)
    clean = re.sub(r"(\d),(\d{3})(?!\d)", r"\1\2", text)
    pattern = re.compile(
        r"(?<![\d.])" + _NUM + r"(?:" + _RANGE_SEP + _NUM + r")?\s*" + UNIT_PATTERNS[unit],
        re.IGNORECASE,
    )
    values = []
    for m in pattern.finditer(clean):
        values.append(_to_float(m.group(1)))
        if m.group(2):
            values.append(_to_float(m.group(2)))
    return values


def run_check(check, text):
    """Run one deterministic check. Returns (passed: bool, detail: str)."""
    kind = check["type"]
    flags = re.IGNORECASE | re.MULTILINE
    if kind == "regex_any":
        hits = [p for p in check["patterns"] if re.search(p, text, flags)]
        return bool(hits), ("matched %r" % hits[0]) if hits else "none of %r matched" % check["patterns"]
    if kind == "regex_all":
        missing = [p for p in check["patterns"] if not re.search(p, text, flags)]
        return not missing, "all matched" if not missing else "missing %r" % missing
    if kind == "regex_none":
        hits = [p for p in check["patterns"] if re.search(p, text, flags)]
        return not hits, "none matched" if not hits else "forbidden %r matched" % hits
    if kind == "number_in_range":
        vals = extract_numbers(text, check["unit"])
        lo, hi = check["min"], check["max"]
        inside = [v for v in vals if lo <= v <= hi]
        mode = check.get("mode", "any")
        if mode == "any":
            ok = bool(inside)
        elif mode == "all":
            ok = bool(vals) and len(inside) == len(vals)
        else:
            raise ValueError("unknown mode: %s" % mode)
        return ok, "%s values %r, wanted %s in [%s, %s]" % (check["unit"], vals[:12], mode, lo, hi)
    raise ValueError("unknown check type: %s" % kind)


JUDGE_SYSTEM = (
    "You are a strict grader for an AI cycling coach. You receive the athlete's message, "
    "the coach's reply and a list of criteria. Judge each criterion independently and only on "
    "what the reply actually says. A criterion passes only if the reply clearly satisfies it. "
    "Approximate numbers within the stated ranges pass. Reply with JSON only, no prose, in the form "
    '{"results": [{"index": 0, "pass": true, "reason": "short reason"}, ...]}.'
)


def judge_prompt(case, reply):
    criteria = "\n".join("%d. %s" % (i, c) for i, c in enumerate(case["rubric"]))
    return (
        "ATHLETE MESSAGE:\n%s\n\nCOACH REPLY:\n%s\n\nCRITERIA (index. text):\n%s\n\n"
        "Return the JSON now." % (case["prompt"], reply, criteria)
    )


def parse_judge(text, n):
    """Parse the judge's JSON. Missing or malformed items count as failures."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    out = [(False, "judge gave no result")] * n
    if not m:
        return out
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return [(False, "judge returned invalid JSON")] * n
    out = list(out)
    for item in data.get("results", []):
        i = item.get("index")
        if isinstance(i, int) and 0 <= i < n:
            out[i] = (item.get("pass") is True, str(item.get("reason", ""))[:300])
    return out


def validate_cases(data):
    """Return a list of problems in a cases file (empty list = valid)."""
    problems, seen = [], set()
    for c in data.get("cases", []):
        cid = c.get("id")
        if not cid:
            problems.append("case without id")
            continue
        if cid in seen:
            problems.append("duplicate id %s" % cid)
        seen.add(cid)
        if not c.get("prompt"):
            problems.append("%s: missing prompt" % cid)
        if not c.get("checks") and not c.get("rubric"):
            problems.append("%s: needs checks or rubric" % cid)
        for ch in c.get("checks", []):
            if ch.get("type") not in ("regex_any", "regex_all", "regex_none", "number_in_range"):
                problems.append("%s: bad check type %r" % (cid, ch.get("type")))
            if ch.get("type") == "number_in_range" and ch.get("unit") not in UNIT_PATTERNS:
                problems.append("%s: bad unit %r" % (cid, ch.get("unit")))
            for p in ch.get("patterns", []):
                try:
                    re.compile(p)
                except re.error as e:
                    problems.append("%s: bad regex %r (%s)" % (cid, p, e))
    return problems

#!/usr/bin/env python3
"""Run the cycling-coach evals against one or more models.

Standard library only. Examples:

  # Claude and Grok, judged by Claude
  python3 evals/run_evals.py --model anthropic:<model-id> --model xai:<model-id> \
      --judge anthropic:<model-id>

  # Only the safety cases, 3 runs each
  python3 evals/run_evals.py --model openai:<model-id> --tags safety --repeat 3

  # Grade saved replies without calling a coach model
  python3 evals/run_evals.py --responses my_replies.json

Providers and the environment variable each one reads:
  anthropic   ANTHROPIC_API_KEY
  openai      OPENAI_API_KEY
  xai         XAI_API_KEY        (Grok)
  gemini      GEMINI_API_KEY     (OpenAI-compatible endpoint)
  ollama      none               (local, http://localhost:11434)
  custom      CUSTOM_API_KEY, CUSTOM_BASE_URL (any OpenAI-compatible server)
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graders  # noqa: E402

REPO = os.path.dirname(HERE)
DEFAULT_SPEC = os.path.join(REPO, "generic", "cycling-coach.md")
DEFAULT_CASES = os.path.join(HERE, "cases.json")
USER_AGENT = "fitness-coach-evals/1.0"

OPENAI_COMPATIBLE = {
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "xai": ("https://api.x.ai/v1", "XAI_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "ollama": ("http://localhost:11434/v1", None),
}


class ModelError(Exception):
    pass


def _post(url, headers, body, timeout):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    for k, v in headers.items():
        req.add_header(k, v)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            raise ModelError("HTTP %s from %s: %s" % (e.code, url.split("/v1")[0], detail))
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise ModelError("cannot reach %s: %s" % (url, e.reason))
    raise ModelError("gave up after retries")


class Model:
    """A model spec like 'anthropic:claude-x' or 'xai:grok-x'."""

    def __init__(self, spec, max_tokens=2000, temperature=None, timeout=180):
        if ":" not in spec:
            raise SystemExit("model must look like provider:model-id, got %r" % spec)
        self.spec = spec
        self.provider, self.name = spec.split(":", 1)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        if self.provider == "anthropic":
            self.base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
            self.key = self._key("ANTHROPIC_API_KEY")
        elif self.provider == "custom":
            self.base = os.environ.get("CUSTOM_BASE_URL") or self._fail("CUSTOM_BASE_URL")
            self.key = os.environ.get("CUSTOM_API_KEY", "")
        elif self.provider in OPENAI_COMPATIBLE:
            base, env = OPENAI_COMPATIBLE[self.provider]
            self.base = os.environ.get(self.provider.upper() + "_BASE_URL", base)
            self.key = self._key(env) if env else ""
        else:
            raise SystemExit("unknown provider %r" % self.provider)

    @staticmethod
    def _key(env):
        val = os.environ.get(env)
        if not val:
            raise SystemExit("set %s to use this provider" % env)
        return val

    @staticmethod
    def _fail(env):
        raise SystemExit("set %s to use the custom provider" % env)

    def chat(self, system, user):
        if self.provider == "anthropic":
            body = {"model": self.name, "max_tokens": self.max_tokens, "system": system,
                    "messages": [{"role": "user", "content": user}]}
            if self.temperature is not None:
                body["temperature"] = self.temperature
            out = _post(self.base.rstrip("/") + "/v1/messages",
                        {"x-api-key": self.key, "anthropic-version": "2023-06-01"}, body, self.timeout)
            return "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
        body = {"model": self.name, "max_tokens": self.max_tokens,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if self.temperature is not None:
            body["temperature"] = self.temperature
        headers = {"Authorization": "Bearer " + self.key} if self.key else {}
        out = _post(self.base.rstrip("/") + "/chat/completions", headers, body, self.timeout)
        try:
            return out["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError):
            raise ModelError("unexpected response shape: %s" % json.dumps(out)[:300])


def grade(case, reply, judge):
    """Grade one reply. Returns a dict with per-check and per-criterion results."""
    checks = []
    for ch in case.get("checks", []):
        ok, detail = graders.run_check(ch, reply)
        checks.append({"check": ch["type"], "pass": ok, "detail": detail})
    rubric = []
    if case.get("rubric"):
        if judge is None:
            rubric = [{"criterion": c, "pass": None, "reason": "no judge model"} for c in case["rubric"]]
        else:
            try:
                raw = judge.chat(graders.JUDGE_SYSTEM, graders.judge_prompt(case, reply))
                parsed = graders.parse_judge(raw, len(case["rubric"]))
            except ModelError as e:
                parsed = [(False, "judge error: %s" % e)] * len(case["rubric"])
            rubric = [{"criterion": c, "pass": p, "reason": r} for c, (p, r) in zip(case["rubric"], parsed)]
    graded = [x["pass"] for x in checks + rubric if x["pass"] is not None]
    return {"checks": checks, "rubric": rubric, "pass": bool(graded) and all(graded)}


def load_cases(path, tags, ids):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    problems = graders.validate_cases(data)
    if problems:
        raise SystemExit("invalid cases file:\n  " + "\n  ".join(problems))
    cases = data["cases"]
    if tags:
        cases = [c for c in cases if set(tags) & set(c.get("tags", []))]
    if ids:
        cases = [c for c in cases if c["id"] in ids]
    return cases


def summarize(results, models):
    lines = ["# Coach eval results", "", "| Model | Passed | Pass rate | Critical failures |", "|---|---|---|---|"]
    for m in models:
        rs = [r for r in results if r["model"] == m]
        passed = sum(r["pass"] for r in rs)
        crit = sorted({r["case"] for r in rs if r["critical"] and not r["pass"]})
        rate = "%.0f%%" % (100.0 * passed / len(rs)) if rs else "n/a"
        lines.append("| %s | %d/%d | %s | %s |" % (m, passed, len(rs), rate, ", ".join(crit) or "none"))
    tags = sorted({t for r in results for t in r["tags"]})
    if tags:
        lines += ["", "## By tag", "", "| Tag | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
        for t in tags:
            row = []
            for m in models:
                rs = [r for r in results if r["model"] == m and t in r["tags"]]
                row.append("%d/%d" % (sum(r["pass"] for r in rs), len(rs)) if rs else "-")
            lines.append("| %s | %s |" % (t, " | ".join(row)))
    fails = [r for r in results if not r["pass"]]
    if fails:
        lines += ["", "## Failures", ""]
        for r in fails:
            why = [c["detail"] for c in r["grade"]["checks"] if not c["pass"]]
            why += [x["criterion"] + " -> " + x["reason"] for x in r["grade"]["rubric"] if x["pass"] is False]
            if r.get("error"):
                why = [r["error"]]
            lines.append("- **%s** / `%s` (run %d): %s" % (r["model"], r["case"], r["run"], "; ".join(why)[:600]))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", action="append", default=[], help="provider:model-id (repeatable)")
    ap.add_argument("--judge", help="provider:model-id for rubric grading (omit to run checks only)")
    ap.add_argument("--spec", default=DEFAULT_SPEC, help="coach file used as the system prompt")
    ap.add_argument("--cases", default=DEFAULT_CASES)
    ap.add_argument("--tags", nargs="*", help="only run cases with any of these tags")
    ap.add_argument("--ids", nargs="*", help="only run these case ids")
    ap.add_argument("--repeat", type=int, default=1, help="runs per case per model")
    ap.add_argument("--responses", help="JSON {case_id: reply} to grade instead of calling a model")
    ap.add_argument("--max-tokens", type=int, default=2000)
    ap.add_argument("--temperature", type=float, help="omit for the provider default")
    ap.add_argument("--out", default=os.path.join(HERE, "results"), help="folder for result files")
    ap.add_argument("--fail-under", type=float, default=0.0, help="exit 1 if any model's pass rate is below this (0-1)")
    ap.add_argument("--list", action="store_true", help="list cases and exit")
    args = ap.parse_args(argv)

    cases = load_cases(args.cases, args.tags, args.ids)
    if args.list:
        for c in cases:
            print("%-32s %-28s %s" % (c["id"], ",".join(c.get("tags", [])), "CRITICAL" if c.get("critical") else ""))
        return 0
    if not args.model and not args.responses:
        ap.error("give at least one --model or --responses")

    with open(args.spec, encoding="utf-8") as f:
        system = f.read()
    judge = Model(args.judge, max_tokens=1000, temperature=0) if args.judge else None
    if judge is None:
        skipped = [c["id"] for c in cases if not c.get("checks")]
        cases = [c for c in cases if c.get("checks")]
        if skipped:
            print("No --judge: skipping %d rubric-only cases; rubric items on other cases are not graded."
                  % len(skipped), file=sys.stderr)
    sources = [("saved", None)] if args.responses else []
    sources += [(m, Model(m, args.max_tokens, args.temperature)) for m in args.model]
    saved = {}
    if args.responses:
        with open(args.responses, encoding="utf-8") as f:
            saved = json.load(f)

    results = []
    for label, model in sources:
        for case in cases:
            runs = 1 if model is None else args.repeat
            for run in range(1, runs + 1):
                error = None
                if model is None:
                    reply = saved.get(case["id"])
                    if reply is None:
                        continue
                else:
                    try:
                        reply = model.chat(system, case["prompt"])
                    except ModelError as e:
                        reply, error = "", str(e)
                g = grade(case, reply, judge) if not error else {"checks": [], "rubric": [], "pass": False}
                results.append({"model": label, "case": case["id"], "run": run, "tags": case.get("tags", []),
                                "critical": bool(case.get("critical")), "pass": g["pass"], "grade": g,
                                "reply": reply, "error": error})
                print("%-4s %-24s %-32s run %d" % ("PASS" if g["pass"] else "FAIL", label[:24], case["id"], run),
                      file=sys.stderr)

    labels = [s[0] for s in sources]
    report = summarize(results, labels)
    os.makedirs(args.out, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(args.out, "results-%s.json" % stamp), "w", encoding="utf-8") as f:
        json.dump({"spec": os.path.relpath(args.spec, REPO), "judge": args.judge, "results": results}, f, indent=2)
    with open(os.path.join(args.out, "report-%s.md" % stamp), "w", encoding="utf-8") as f:
        f.write(report)
    print(report)

    rates = []
    for m in labels:
        rs = [r for r in results if r["model"] == m]
        if rs:
            rates.append(sum(r["pass"] for r in rs) / len(rs))
    worst = min(rates, default=1.0)
    return 1 if worst < args.fail_under else 0


if __name__ == "__main__":
    sys.exit(main())

"""Individual evaluators. Each returns a (passed, detail) tuple."""
from __future__ import annotations

from dataclasses import dataclass

from .loader import Case


@dataclass
class BotResponse:
    """What the bot under test returned for a single inbound message."""
    case_id: str
    answer: str
    intent: str | None = None
    latency_ms: int = 0
    cost_usd: float = 0.0


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def intent_check(case: Case, resp: BotResponse) -> CheckResult | None:
    """Skip if expected intent not set. Otherwise exact match."""
    if case.expect.intent is None:
        return None
    if resp.intent is None:
        return CheckResult("intent", False, "bot produced no intent tag")
    ok = resp.intent == case.expect.intent
    detail = f"expected={case.expect.intent} got={resp.intent}"
    return CheckResult("intent", ok, detail)


def contains_check(case: Case, resp: BotResponse) -> CheckResult | None:
    if not case.expect.answer_contains:
        return None
    haystack = resp.answer.lower()
    missing = [n for n in case.expect.answer_contains if n.lower() not in haystack]
    ok = not missing
    detail = "all substrings present" if ok else f"missing: {missing!r}"
    return CheckResult("answer_contains", ok, detail)


def does_not_contain_check(case: Case, resp: BotResponse) -> CheckResult | None:
    if not case.expect.answer_does_not_contain:
        return None
    haystack = resp.answer.lower()
    hits = [n for n in case.expect.answer_does_not_contain if n.lower() in haystack]
    ok = not hits
    detail = "none of the banned phrases appeared" if ok else f"banned phrase(s) present: {hits!r}"
    return CheckResult("answer_does_not_contain", ok, detail)


def latency_check(case: Case, resp: BotResponse) -> CheckResult | None:
    cap = case.expect.max_latency_ms
    if cap is None:
        return None
    ok = resp.latency_ms <= cap
    detail = f"{resp.latency_ms}ms (cap {cap}ms)"
    return CheckResult("latency", ok, detail)


def cost_check(case: Case, resp: BotResponse) -> CheckResult | None:
    cap = case.expect.max_cost_usd
    if cap is None:
        return None
    ok = resp.cost_usd <= cap
    detail = f"${resp.cost_usd:.4f} (cap ${cap:.4f})"
    return CheckResult("cost", ok, detail)


ALL_CHECKS = [
    intent_check,
    contains_check,
    does_not_contain_check,
    latency_check,
    cost_check,
]


def run_all(case: Case, resp: BotResponse) -> list[CheckResult]:
    """Run every applicable evaluator. Skips return None and are filtered."""
    results: list[CheckResult] = []
    for fn in ALL_CHECKS:
        r = fn(case, resp)
        if r is not None:
            results.append(r)
    return results

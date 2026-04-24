"""Run a suite against a bot function and collect results."""
from __future__ import annotations

from dataclasses import dataclass, field

from .evaluators import BotResponse, CheckResult, run_all
from .loader import Case, Suite
from .mocks import BotFn


@dataclass
class CaseResult:
    case: Case
    response: BotResponse
    checks: list[CheckResult]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


@dataclass
class SuiteResult:
    suite: Suite
    cases: list[CaseResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.cases if c.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total

    @property
    def total_cost_usd(self) -> float:
        return sum(c.response.cost_usd for c in self.cases)

    @property
    def p95_latency_ms(self) -> int:
        if not self.cases:
            return 0
        sorted_lat = sorted(c.response.latency_ms for c in self.cases)
        idx = max(0, int(len(sorted_lat) * 0.95) - 1)
        return sorted_lat[idx]


def run(suite: Suite, bot: BotFn) -> SuiteResult:
    result = SuiteResult(suite=suite)
    for case in suite.cases:
        resp = bot(case)
        checks = run_all(case, resp)
        result.cases.append(CaseResult(case=case, response=resp, checks=checks))
    return result

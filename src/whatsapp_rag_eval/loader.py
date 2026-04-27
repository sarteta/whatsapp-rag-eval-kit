"""Load YAML test suites for WhatsApp RAG evaluation.

A suite is a list of cases. Each case represents one inbound WhatsApp
message and the expectations the bot's response must satisfy.

Minimal case shape:

    id: clinic-001
    inbound: "Que horarios de atencion tienen?"
    expect:
      intent: schedule_query        # optional, matched exactly
      answer_contains:               # all substrings must be present (case-insensitive)
        - "lunes"
        - "viernes"
      answer_does_not_contain:       # none of these may appear
        - "no se"
      answer_matches_regex:          # all patterns must match (re.search)
        - "\\b\\d{4}\\b"             # e.g. a 4-digit booking code
      max_latency_ms: 2500           # optional hard ceiling
      max_cost_usd: 0.01             # optional hard ceiling
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Expect:
    intent: str | None = None
    answer_contains: list[str] = field(default_factory=list)
    answer_does_not_contain: list[str] = field(default_factory=list)
    answer_matches_regex: list[str] = field(default_factory=list)
    max_latency_ms: int | None = None
    max_cost_usd: float | None = None


@dataclass
class Case:
    id: str
    inbound: str
    expect: Expect
    tags: list[str] = field(default_factory=list)


@dataclass
class Suite:
    name: str
    description: str
    cases: list[Case]

    @property
    def size(self) -> int:
        return len(self.cases)


def load(path: str | Path) -> Suite:
    p = Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"suite at {p} must be a mapping at top level")
    if "cases" not in raw or not isinstance(raw["cases"], list):
        raise ValueError(f"suite at {p} must have a 'cases' list")

    cases: list[Case] = []
    seen_ids: set[str] = set()
    for i, raw_case in enumerate(raw["cases"]):
        case = _parse_case(raw_case, i)
        if case.id in seen_ids:
            raise ValueError(f"duplicate case id '{case.id}' in {p}")
        seen_ids.add(case.id)
        cases.append(case)

    return Suite(
        name=raw.get("name", p.stem),
        description=raw.get("description", ""),
        cases=cases,
    )


def _parse_case(raw: Any, index: int) -> Case:
    if not isinstance(raw, dict):
        raise ValueError(f"case at index {index} is not a mapping")
    if "id" not in raw:
        raise ValueError(f"case at index {index} is missing 'id'")
    if "inbound" not in raw:
        raise ValueError(f"case '{raw.get('id', index)}' is missing 'inbound'")

    expect_raw = raw.get("expect") or {}
    if not isinstance(expect_raw, dict):
        raise ValueError(f"case '{raw['id']}' has non-mapping 'expect'")

    expect = Expect(
        intent=expect_raw.get("intent"),
        answer_contains=list(expect_raw.get("answer_contains", [])),
        answer_does_not_contain=list(expect_raw.get("answer_does_not_contain", [])),
        answer_matches_regex=list(expect_raw.get("answer_matches_regex", [])),
        max_latency_ms=expect_raw.get("max_latency_ms"),
        max_cost_usd=expect_raw.get("max_cost_usd"),
    )

    return Case(
        id=str(raw["id"]),
        inbound=str(raw["inbound"]),
        expect=expect,
        tags=list(raw.get("tags", [])),
    )

from pathlib import Path

import pytest

from whatsapp_rag_eval import loader


SUITE = Path(__file__).parent.parent / "suites" / "clinic-es.yml"


def test_loads_known_suite():
    s = loader.load(SUITE)
    assert s.name == "clinic-es"
    assert s.size >= 5
    assert all(c.id for c in s.cases)


def test_parses_expect_fields():
    s = loader.load(SUITE)
    case = next(c for c in s.cases if c.id == "schedule-001")
    assert case.expect.intent == "schedule_query"
    assert "lunes" in case.expect.answer_contains
    assert "no sé" in case.expect.answer_does_not_contain
    assert case.expect.max_latency_ms == 2500
    assert case.expect.max_cost_usd == 0.01


def test_duplicate_id_raises(tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text(
        "name: bad\ncases:\n  - id: a\n    inbound: foo\n  - id: a\n    inbound: bar\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate case id"):
        loader.load(bad)


def test_missing_inbound_raises(tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text(
        "name: bad\ncases:\n  - id: a\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing 'inbound'"):
        loader.load(bad)


def test_tags_are_preserved():
    s = loader.load(SUITE)
    sched = [c for c in s.cases if "schedule" in c.tags]
    assert len(sched) >= 2

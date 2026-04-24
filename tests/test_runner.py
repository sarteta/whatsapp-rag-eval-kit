from pathlib import Path

from whatsapp_rag_eval import loader, runner
from whatsapp_rag_eval.mocks import mock_bot


SUITE = Path(__file__).parent.parent / "suites" / "clinic-es.yml"


def test_runner_produces_one_result_per_case():
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    assert res.total == s.size
    assert len(res.cases) == s.size


def test_runner_computes_pass_rate_in_unit_range():
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    assert 0.0 <= res.pass_rate <= 1.0


def test_runner_reports_p95_latency_nonzero():
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    # All mock responses have non-zero latency
    assert res.p95_latency_ms > 0


def test_runner_sums_cost():
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    expected = sum(c.response.cost_usd for c in res.cases)
    assert abs(res.total_cost_usd - expected) < 1e-9

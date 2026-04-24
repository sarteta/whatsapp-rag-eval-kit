from pathlib import Path

from whatsapp_rag_eval import loader, runner, report
from whatsapp_rag_eval.mocks import mock_bot


SUITE = Path(__file__).parent.parent / "suites" / "clinic-es.yml"


def test_markdown_has_summary_header():
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    md = report.to_markdown(res)
    assert "eval report" in md
    assert "Pass rate" in md
    assert "p95 latency" in md


def test_markdown_lists_every_case():
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    md = report.to_markdown(res)
    for case in s.cases:
        assert case.id in md


def test_write_markdown_creates_file(tmp_path):
    s = loader.load(SUITE)
    res = runner.run(s, mock_bot)
    out = tmp_path / "r" / "report.md"
    path = report.write_markdown(res, out)
    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("# clinic-es")

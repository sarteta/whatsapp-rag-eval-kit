"""CLI entry point.

    python -m whatsapp_rag_eval --suite suites/clinic-es.yml --report out/report.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import loader, runner, report
from .mocks import mock_bot


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="whatsapp-rag-eval",
        description="Run a WhatsApp-RAG YAML eval suite against a bot and report.",
    )
    ap.add_argument("--suite", required=True, help="Path to YAML suite")
    ap.add_argument("--report", default="out/report.md", help="Markdown report output path")
    ap.add_argument(
        "--bot",
        default="mock",
        choices=["mock"],
        help="Which bot to exercise. Only 'mock' in the open-source kit -- bring your own bot by importing and calling `runner.run()` from your code.",
    )
    args = ap.parse_args(argv)

    suite = loader.load(args.suite)
    bot_fn = mock_bot  # extension point: user imports their own bot and passes it in

    result = runner.run(suite, bot_fn)
    report.write_markdown(result, args.report)

    pct = result.pass_rate * 100
    print(f"Suite: {suite.name}")
    print(f"Cases: {result.total}  Passed: {result.passed}  Failed: {result.failed}  Pass rate: {pct:.1f}%")
    print(f"p95 latency: {result.p95_latency_ms} ms   Total cost: ${result.total_cost_usd:.4f}")
    print(f"Report: {args.report}")

    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

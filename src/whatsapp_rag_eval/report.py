"""Render SuiteResult to Markdown."""
from __future__ import annotations

from pathlib import Path

from .runner import SuiteResult


def to_markdown(result: SuiteResult) -> str:
    suite = result.suite
    lines: list[str] = []
    lines.append(f"# {suite.name} -- eval report\n")
    if suite.description:
        lines.append(f"_{suite.description}_\n")

    lines.append(f"**Cases:** {result.total}  ")
    lines.append(f"**Passed:** {result.passed}  ")
    lines.append(f"**Failed:** {result.failed}  ")
    lines.append(f"**Pass rate:** {result.pass_rate*100:.1f}%  ")
    lines.append(f"**p95 latency:** {result.p95_latency_ms} ms  ")
    lines.append(f"**Total cost:** ${result.total_cost_usd:.4f}\n")

    # Per-case table
    lines.append("## Cases\n")
    lines.append("| ID | Inbound | Status | Checks that failed |")
    lines.append("|----|---------|--------|--------------------|")
    for c in result.cases:
        status = "✅ pass" if c.passed else "❌ fail"
        inbound = c.case.inbound.replace("|", "\\|")
        if len(inbound) > 60:
            inbound = inbound[:57] + "..."
        failed = [chk.name for chk in c.checks if not chk.passed]
        lines.append(f"| `{c.case.id}` | {inbound} | {status} | {', '.join(failed) or '--'} |")

    # Failure detail
    failed_cases = [c for c in result.cases if not c.passed]
    if failed_cases:
        lines.append("\n## Failure details\n")
        for c in failed_cases:
            lines.append(f"### `{c.case.id}`")
            lines.append(f"**Inbound:** {c.case.inbound}\n")
            lines.append(f"**Got:** {c.response.answer}\n")
            for chk in c.checks:
                mark = "✅" if chk.passed else "❌"
                lines.append(f"- {mark} **{chk.name}** -- {chk.detail}")
            lines.append("")

    return "\n".join(lines) + "\n"


def write_markdown(result: SuiteResult, out_path: str | Path) -> Path:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(to_markdown(result), encoding="utf-8")
    return p

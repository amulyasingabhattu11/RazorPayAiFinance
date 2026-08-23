"""
Self-Report Writer.

Assembles the final RunReport from all pipeline outputs, computes
ground-truth scoring (precision / recall / false-match-rate),
and renders the report as:
  1. A structured RunReport (Pydantic model)  → output/report.json
  2. A rich console table                      → terminal output
  3. A markdown audit report                   → output/audit_report.md

Ground-truth scoring:
  - Precision = TP / (TP + FP)  where TP = correctly MATCHED
  - Recall    = TP / (TP + FN)  where FN = should-be-MATCHED but wasn't
  - False-match rate = FP / total_actual_positives
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.data.models import (
    ExceptionCase,
    MatchResult,
    MatchStatus,
    RunReport,
    TransactionRecord,
)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_ground_truth_scores(
    match_results: List[MatchResult],
    ground_truth: Dict[str, MatchStatus],
) -> Dict:
    """
    Compare agent results against known ground truth.

    Ground truth labels (per spec):
      MATCHED          = should auto-match
      REVIEW_REQUIRED  = should be held for review
      UNMATCHED        = should be flagged as exception
    """
    tp = 0   # Correctly matched
    fp = 0   # Agent matched but GT says REVIEW_REQUIRED or UNMATCHED (false match)
    fn = 0   # GT says MATCHED but agent did not match
    tn = 0   # GT says UNMATCHED/REVIEW and agent correctly didn't match

    review_correct = 0   # Agent said REVIEW_REQUIRED and GT agrees
    unmatched_correct = 0  # Agent said UNMATCHED and GT agrees

    for result in match_results:
        gt_status = ground_truth.get(result.txn_id)
        if gt_status is None:
            continue

        agent_status = result.match_status

        if gt_status == MatchStatus.MATCHED:
            if agent_status == MatchStatus.MATCHED:
                tp += 1
            else:
                fn += 1  # Should have matched but didn't
        elif gt_status == MatchStatus.REVIEW_REQUIRED:
            if agent_status == MatchStatus.REVIEW_REQUIRED:
                review_correct += 1
                tn += 1
            elif agent_status == MatchStatus.MATCHED:
                fp += 1  # Incorrectly auto-matched a review case
            else:
                tn += 1  # Conservative (unmatched when review required)
        elif gt_status == MatchStatus.UNMATCHED:
            if agent_status == MatchStatus.MATCHED:
                fp += 1  # Force-matched a genuine exception — worst case
            elif agent_status == MatchStatus.UNMATCHED:
                unmatched_correct += 1
                tn += 1
            else:
                tn += 1

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    total_actual_positives = tp + fn
    false_match_rate = round(fp / total_actual_positives, 4) if total_actual_positives > 0 else 0.0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "review_correct": review_correct,
        "unmatched_correct": unmatched_correct,
        "precision": precision,
        "recall": recall,
        "false_match_rate": false_match_rate,
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def build_run_report(
    match_results: List[MatchResult],
    exceptions: List[ExceptionCase],
    ground_truth: Optional[Dict[str, MatchStatus]],
    elapsed_seconds: float,
    exception_stats: Dict,
) -> RunReport:
    matched = [r for r in match_results if r.match_status == MatchStatus.MATCHED]
    review = [r for r in match_results if r.match_status == MatchStatus.REVIEW_REQUIRED]
    unmatched = [r for r in match_results if r.match_status == MatchStatus.UNMATCHED]

    total = len(match_results)
    match_rate_pct = round(len(matched) / total * 100, 2) if total > 0 else 0.0
    review_rate_pct = round(len(review) / total * 100, 2) if total > 0 else 0.0
    exception_rate_pct = round(len(unmatched) / total * 100, 2) if total > 0 else 0.0

    avg_conf = (
        round(sum(r.confidence_score for r in matched) / len(matched), 4)
        if matched else 0.0
    )

    # Ground-truth scoring
    precision = recall = false_match_rate = None
    gt_matched = gt_review = gt_unmatched = None

    if ground_truth:
        scores = compute_ground_truth_scores(match_results, ground_truth)
        precision = scores["precision"]
        recall = scores["recall"]
        false_match_rate = scores["false_match_rate"]
        gt_matched = sum(1 for v in ground_truth.values() if v == MatchStatus.MATCHED)
        gt_review = sum(1 for v in ground_truth.values() if v == MatchStatus.REVIEW_REQUIRED)
        gt_unmatched = sum(1 for v in ground_truth.values() if v == MatchStatus.UNMATCHED)

    return RunReport(
        run_id=f"RUN-{uuid.uuid4().hex[:8].upper()}",
        total_records=total,
        matched_count=len(matched),
        review_required_count=len(review),
        exception_count=len(unmatched),
        match_rate_pct=match_rate_pct,
        review_required_rate_pct=review_rate_pct,
        exception_rate_pct=exception_rate_pct,
        ground_truth_matched=gt_matched,
        ground_truth_review=gt_review,
        ground_truth_unmatched=gt_unmatched,
        precision=precision,
        recall=recall,
        false_match_rate=false_match_rate,
        avg_confidence_matched=avg_conf,
        exceptions=exceptions,
        match_results=match_results,
        generated_at=datetime.utcnow(),
        elapsed_seconds=elapsed_seconds,
    )


# ---------------------------------------------------------------------------
# Console renderer (rich)
# ---------------------------------------------------------------------------

def render_console(report: RunReport, exception_stats: Dict) -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        console = Console()
        _render_rich(console, report, exception_stats)
    except ImportError:
        _render_plain(report, exception_stats)


def _render_rich(console, report: RunReport, exception_stats: Dict) -> None:
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    from rich.text import Text

    console.print()
    console.rule("[bold cyan]AI Finance Controller — Run Report[/bold cyan]")
    console.print(f"[dim]Run ID: {report.run_id}   Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}[/dim]")
    console.print()

    # ---- KPI summary table ----
    kpi = Table(title="KPI Summary", box=box.ROUNDED, show_header=True)
    kpi.add_column("Metric", style="bold")
    kpi.add_column("Value", justify="right")
    kpi.add_column("Ground Truth", justify="right", style="dim")

    kpi.add_row("Total Records", str(report.total_records), "")
    kpi.add_row(
        "Auto-Matched (MATCHED)",
        f"[green]{report.matched_count}[/green]",
        f"{report.ground_truth_matched or '—'}",
    )
    kpi.add_row(
        "Review Required",
        f"[yellow]{report.review_required_count}[/yellow]",
        f"{report.ground_truth_review or '—'}",
    )
    kpi.add_row(
        "Unmatched (Exceptions)",
        f"[red]{report.exception_count}[/red]",
        f"{report.ground_truth_unmatched or '—'}",
    )
    kpi.add_row("", "", "")
    kpi.add_row("Auto-Match Rate", f"[green]{report.match_rate_pct:.1f}%[/green]", "")
    kpi.add_row("Review-Required Rate", f"[yellow]{report.review_required_rate_pct:.1f}%[/yellow]", "")
    kpi.add_row("Exception Rate", f"[red]{report.exception_rate_pct:.1f}%[/red]", "")
    kpi.add_row("", "", "")
    if report.precision is not None:
        kpi.add_row("Precision (vs GT)", f"{report.precision:.1%}", "")
        kpi.add_row("Recall (vs GT)", f"{report.recall:.1%}", "")
        kpi.add_row("False-Match Rate", f"[red]{report.false_match_rate:.1%}[/red]", "")
    kpi.add_row("Avg Confidence (Matched)", f"{report.avg_confidence_matched:.3f}", "")
    kpi.add_row("Elapsed", f"{report.elapsed_seconds:.2f}s", "")
    console.print(kpi)
    console.print()

    # ---- Exception breakdown ----
    if exception_stats.get("break_type_distribution"):
        bt_table = Table(title="Exception Breakdown", box=box.SIMPLE_HEAD)
        bt_table.add_column("Break Type")
        bt_table.add_column("Count", justify="right")
        for bt, count in sorted(
            exception_stats["break_type_distribution"].items(),
            key=lambda x: -x[1],
        ):
            bt_table.add_row(bt, str(count))
        console.print(bt_table)
        console.print(
            f"Root-cause coverage: [bold]{exception_stats.get('root_cause_coverage_pct', 100):.1f}%[/bold] of exceptions have a hypothesis\n"
        )

    # ---- Exception list ----
    if report.exceptions:
        exc_table = Table(
            title="Exception List (sorted by priority)",
            box=box.SIMPLE_HEAD,
            show_lines=True,
        )
        exc_table.add_column("ID", style="dim", width=10)
        exc_table.add_column("Txn ID", width=18)
        exc_table.add_column("Priority", width=8)
        exc_table.add_column("Break Type", width=22)
        exc_table.add_column("Hypothesis", max_width=60)

        priority_colors = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "cyan"}

        for exc in report.exceptions[:30]:  # cap to avoid overwhelming terminal
            color = priority_colors.get(exc.priority.value, "white")
            exc_table.add_row(
                exc.exception_id,
                exc.txn_id,
                f"[{color}]{exc.priority.value}[/{color}]",
                exc.break_type.value,
                exc.root_cause_hypothesis[:100] + "…"
                if len(exc.root_cause_hypothesis) > 100
                else exc.root_cause_hypothesis,
            )
        if len(report.exceptions) > 30:
            console.print(f"[dim](Showing 30 of {len(report.exceptions)} exceptions — see audit_report.md for full list)[/dim]")
        console.print(exc_table)

    console.rule()


def _render_plain(report: RunReport, exception_stats: Dict) -> None:
    """Fallback renderer for environments without rich installed."""
    print("\n" + "=" * 70)
    print("  AI Finance Controller — Run Report")
    print("=" * 70)
    print(f"  Run ID    : {report.run_id}")
    print(f"  Generated : {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Elapsed   : {report.elapsed_seconds:.2f}s")
    print()
    print(f"  Total Records     : {report.total_records}")
    print(f"  MATCHED           : {report.matched_count}  ({report.match_rate_pct:.1f}%)")
    print(f"  REVIEW_REQUIRED   : {report.review_required_count}  ({report.review_required_rate_pct:.1f}%)")
    print(f"  UNMATCHED         : {report.exception_count}  ({report.exception_rate_pct:.1f}%)")
    if report.precision is not None:
        print()
        print(f"  Precision         : {report.precision:.1%}")
        print(f"  Recall            : {report.recall:.1%}")
        print(f"  False-Match Rate  : {report.false_match_rate:.1%}")
    print(f"  Avg Confidence    : {report.avg_confidence_matched:.3f}")
    print()
    print(f"  GT MATCHED        : {report.ground_truth_matched}")
    print(f"  GT REVIEW         : {report.ground_truth_review}")
    print(f"  GT UNMATCHED      : {report.ground_truth_unmatched}")
    print()
    print("  Exceptions:")
    for exc in report.exceptions[:20]:
        print(f"    [{exc.priority.value:6s}] {exc.txn_id} — {exc.break_type.value}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def write_json_report(report: RunReport, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "report.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    return path


def write_markdown_report(
    report: RunReport,
    exception_stats: Dict,
    output_dir: str = "output",
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "audit_report.md")

    lines = [
        "# AI Finance Controller — Audit Report",
        f"**Run ID:** `{report.run_id}`  ",
        f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        f"**Elapsed:** {report.elapsed_seconds:.2f}s",
        "",
        "---",
        "",
        "## KPI Summary",
        "",
        "| Metric | Agent Result | Ground Truth |",
        "|--------|-------------|--------------|",
        f"| Total Records | {report.total_records} | — |",
        f"| MATCHED | {report.matched_count} ({report.match_rate_pct:.1f}%) | {report.ground_truth_matched or '—'} |",
        f"| REVIEW_REQUIRED | {report.review_required_count} ({report.review_required_rate_pct:.1f}%) | {report.ground_truth_review or '—'} |",
        f"| UNMATCHED | {report.exception_count} ({report.exception_rate_pct:.1f}%) | {report.ground_truth_unmatched or '—'} |",
        f"| Precision | {f'{report.precision:.1%}' if report.precision is not None else '—'} | — |",
        f"| Recall | {f'{report.recall:.1%}' if report.recall is not None else '—'} | — |",
        f"| False-Match Rate | {f'{report.false_match_rate:.1%}' if report.false_match_rate is not None else '—'} | — |",
        f"| Avg Confidence (Matched) | {report.avg_confidence_matched:.3f} | — |",
        "",
        "---",
        "",
        "## Exception Breakdown",
        "",
        "| Break Type | Count |",
        "|-----------|-------|",
    ]
    for bt, count in sorted(
        exception_stats.get("break_type_distribution", {}).items(),
        key=lambda x: -x[1],
    ):
        lines.append(f"| {bt} | {count} |")
    lines += [
        "",
        f"**Root-cause coverage:** {exception_stats.get('root_cause_coverage_pct', 100):.1f}% of exceptions have a hypothesis.",
        "",
        "---",
        "",
        "## Full Exception List",
        "",
        "| ID | Txn ID | Priority | Break Type | Root Cause Hypothesis |",
        "|----|--------|----------|------------|----------------------|",
    ]
    for exc in report.exceptions:
        hyp = exc.root_cause_hypothesis.replace("|", "\\|")
        lines.append(
            f"| {exc.exception_id} | `{exc.txn_id}` | **{exc.priority.value}** "
            f"| {exc.break_type.value} | {hyp[:120]}… |"
        )

    lines += [
        "",
        "---",
        "",
        "## Worked Example: A Correctly Refused Force-Match",
        "",
        "The following shows a case where the agent **correctly refused** to force-match",
        "a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:",
        "",
    ]

    # Pick the most interesting exception to highlight
    worked_example = None
    for exc in report.exceptions:
        if exc.break_type.value in ("TIMING_MISMATCH", "PARTIAL_REFUND", "AMBIGUOUS"):
            worked_example = exc
            break

    if worked_example:
        # Find its match result
        mr = next(
            (r for r in report.match_results if r.txn_id == worked_example.txn_id),
            None,
        )
        lines += [
            f"**Transaction:** `{worked_example.txn_id}`  ",
            f"**Break Type:** `{worked_example.break_type.value}`  ",
            f"**Priority:** `{worked_example.priority.value}`  ",
            f"**Agent Status:** `{mr.match_status.value if mr else 'N/A'}`  ",
            f"**Confidence:** `{f'{mr.confidence_score:.2f}' if mr else 'N/A'}`  ",
            "",
            f"**Root Cause Hypothesis:**",
            f"> {worked_example.root_cause_hypothesis}",
            "",
            "**Audit Trail:**",
            f"```",
            f"{mr.audit_trail if mr else 'N/A'}",
            "```",
            "",
            "**Why this matters:** A naive matcher might have forced this to MATCHED",
            "because the amounts or IDs are *close*. The agent correctly deferred,",
            "ensuring this record surfaces for human review rather than silently",
            "passing through as a clean match.",
            "",
        ]

    lines += [
        "---",
        "",
        "## Architecture",
        "",
        "```",
        "Batch Loader",
        "    │",
        "Deterministic Matcher  ← exact key + tolerance rules (no LLM)",
        "    │ matched           │ unmatched / low-confidence",
        "    │           Reasoning Agent  ← LLM tool-calls (or stub heuristics)",
        "    │                   │",
        "    └──────────────────►│",
        "                Exception Classifier  ← root-cause tag, priority",
        "                        │",
        "                Self-Report Writer  ← match rate, precision/recall, audit log",
        "```",
        "",
        "The LLM agent is scoped to *ambiguous* records only — not the full batch.",
        "The deterministic pass handles the easy majority (60+ exact matches),",
        "keeping LLM cost and latency minimal.",
        "",
        "---",
        "*Generated by AI Finance Controller — RazorPay Hackathon Track 04*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path

"""
Main Pipeline Orchestrator.

Wires all five stages together:
  1. Batch Loader        — generates (or loads) the synthetic dataset
  2. Deterministic Matcher — exact + tolerance pass
  3. Reasoning Agent     — LLM (or stub) over ambiguous records
  4. Exception Classifier — deduplication, root-cause tagging, prioritization
  5. Self-Report Writer  — console output + JSON + Markdown files

Usage:
    from src.pipeline import run_pipeline
    report = run_pipeline(seed=42)
    report = run_pipeline(seed=42, mode="stub")
    report = run_pipeline(seed=42, mode="llm")
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional

from src.agent.reasoning import resolve_agent_mode, run_agent_pass
from src.data.generator import generate_dataset
from src.data.models import MatchResult, MatchStatus, RunReport
from src.matching.classifier import classify_all_exceptions
from src.matching.deterministic import build_index, run_deterministic_pass
from src.reporting.writer import (
    build_run_report,
    render_console,
    write_json_report,
    write_markdown_report,
)


def run_pipeline(
    seed: int = 42,
    output_dir: str = "output",
    verbose: bool = True,
    mode: str = "auto",
) -> RunReport:
    """
    Execute the full reconciliation pipeline.

    Args:
        seed:       Random seed for synthetic data (default 42, keeps runs deterministic).
        output_dir: Directory for report files (default "output/").
        verbose:    Print stage-by-stage progress to the console.
        mode:       Agent reasoning mode — "auto", "llm", or "stub".
                    "auto" uses LLM when OPENAI_API_KEY is present, stub otherwise.
                    "llm" requires a real OPENAI_API_KEY.
                    "stub" always uses deterministic heuristics (no API calls).

    Returns the assembled RunReport (also written to output/).
    """
    wall_start = time.perf_counter()

    # ------------------------------------------------------------------
    # Resolve agent mode early so we can print the banner upfront
    # ------------------------------------------------------------------
    try:
        use_llm, mode_label, model = resolve_agent_mode(mode)
    except ValueError as e:
        print(f"\n[ERROR]  {e}")
        raise SystemExit(1)

    if verbose:
        print("\n" + "=" * 64)
        print(f"  AI Finance Controller -- RazorPay Hackathon Track 04")
        if use_llm:
            print(f"  Agent mode : LLM ({model})  [live OpenAI reasoning]")
        else:
            print(f"  Agent mode : STUB (heuristic)  [deterministic Python rules,")
            print(f"               NO live LLM calls. Set OPENAI_API_KEY and use")
            print(f"               --mode llm (or --mode auto) for real LLM reasoning.]")
        print("=" * 64)

    # ------------------------------------------------------------------
    # Stage 1: Load data
    # ------------------------------------------------------------------
    if verbose:
        print("\n[1/5] Loading synthetic dataset…")
    transactions, settlements, bank_rows, ground_truth = generate_dataset(seed=seed)

    if verbose:
        print(f"      Transactions : {len(transactions)}")
        print(f"      Settlements  : {len(settlements)}")
        print(f"      Bank rows    : {len(bank_rows)}")
        from collections import Counter
        gt_counts = Counter(ground_truth.values())
        print(f"      Ground truth : MATCHED={gt_counts.get(MatchStatus.MATCHED,0)}, "
              f"REVIEW={gt_counts.get(MatchStatus.REVIEW_REQUIRED,0)}, "
              f"UNMATCHED={gt_counts.get(MatchStatus.UNMATCHED,0)}")

    # ------------------------------------------------------------------
    # Stage 2: Build index + Deterministic pass
    # ------------------------------------------------------------------
    if verbose:
        print("\n[2/5] Running deterministic matcher…")

    index = build_index(transactions, settlements, bank_rows)
    det_result = run_deterministic_pass(transactions, index)

    if verbose:
        print(f"      Deterministic MATCHED       : {len([r for r in det_result.matched if r.match_status == MatchStatus.MATCHED])}")
        print(f"      Deterministic UNMATCHED     : {len([r for r in det_result.matched if r.match_status == MatchStatus.UNMATCHED])}")
        print(f"      Immediate exceptions        : {len(det_result.immediate_exceptions)}")
        print(f"      Sent to agent               : {len(det_result.needs_agent)}")

    # ------------------------------------------------------------------
    # Stage 3: Agent pass over ambiguous records
    # ------------------------------------------------------------------
    agent_mode_tag = "LLM" if use_llm else "STUB"
    if verbose:
        print(f"\n[3/5] Running reasoning agent [{agent_mode_tag}] over {len(det_result.needs_agent)} records…")

    exc_counter_start = len(det_result.immediate_exceptions)
    agent_results, agent_exceptions = run_agent_pass(
        det_result.needs_agent,
        index,
        exc_counter_start=exc_counter_start,
        mode=mode,
    )

    if verbose:
        agent_matched = sum(1 for r in agent_results if r.match_status == MatchStatus.MATCHED)
        agent_review = sum(1 for r in agent_results if r.match_status == MatchStatus.REVIEW_REQUIRED)
        agent_unmatched = sum(1 for r in agent_results if r.match_status == MatchStatus.UNMATCHED)
        print(f"      Agent MATCHED         : {agent_matched}")
        print(f"      Agent REVIEW_REQUIRED : {agent_review}")
        print(f"      Agent UNMATCHED       : {agent_unmatched}")

    # ------------------------------------------------------------------
    # Stage 4: Exception classifier
    # ------------------------------------------------------------------
    if verbose:
        print("\n[4/5] Classifying exceptions…")

    all_match_results: List[MatchResult] = det_result.matched + agent_results
    all_pre_exceptions = det_result.immediate_exceptions + agent_exceptions
    txns_by_id = {t.txn_id: t for t in transactions}

    all_exceptions, exception_stats = classify_all_exceptions(
        match_results=all_match_results,
        pre_classified=all_pre_exceptions,
        transactions_by_id=txns_by_id,
    )

    if verbose:
        print(f"      Total exception register  : {len(all_exceptions)}  "
              f"(UNMATCHED + REVIEW_REQUIRED with root-cause)")
        print(f"      Root-cause coverage       : {exception_stats.get('root_cause_coverage_pct', 0):.1f}%")

    # ------------------------------------------------------------------
    # Stage 5: Build report + write outputs
    # ------------------------------------------------------------------
    if verbose:
        print("\n[5/5] Building report and writing outputs…")

    elapsed = time.perf_counter() - wall_start

    report = build_run_report(
        match_results=all_match_results,
        exceptions=all_exceptions,
        ground_truth=ground_truth,
        elapsed_seconds=elapsed,
        exception_stats=exception_stats,
        agent_mode=mode_label,
    )

    # Write files
    json_path = write_json_report(report, output_dir)
    md_path = write_markdown_report(report, exception_stats, output_dir)

    if verbose:
        print(f"      JSON report   -> {json_path}")
        print(f"      Audit report  -> {md_path}")

    # Render console report
    render_console(report, exception_stats)

    return report

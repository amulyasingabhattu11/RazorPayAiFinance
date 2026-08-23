"""
Exception Classifier.

Takes the combined list of MatchResults and ExceptionCases from both passes
and produces a clean, prioritized, deduplicated exception list.

Also computes:
  - Break-type frequency distribution
  - Priority breakdown
  - Root-cause coverage rate (% with non-empty hypothesis)
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Tuple

from src.data.models import (
    BreakType,
    ExceptionCase,
    MatchResult,
    MatchStatus,
    Priority,
    TransactionRecord,
)


# ---------------------------------------------------------------------------
# Priority rules
# ---------------------------------------------------------------------------

_PRIORITY_MAP: Dict[BreakType, Priority] = {
    BreakType.DUPLICATE_SETTLEMENT: Priority.HIGH,
    BreakType.MISSING_UTR:          Priority.HIGH,
    BreakType.AMOUNT_MISMATCH:      Priority.HIGH,
    BreakType.NO_GATEWAY_RECORD:    Priority.HIGH,
    BreakType.PARTIAL_REFUND:       Priority.MEDIUM,
    BreakType.TIMING_MISMATCH:      Priority.MEDIUM,
    BreakType.NO_BANK_RECORD:       Priority.MEDIUM,
    BreakType.AMBIGUOUS:            Priority.MEDIUM,
    BreakType.AGENT_LOW_CONFIDENCE: Priority.LOW,
    BreakType.UNKNOWN:              Priority.MEDIUM,
}


# ---------------------------------------------------------------------------
# Main classifier function
# ---------------------------------------------------------------------------

def classify_all_exceptions(
    match_results: List[MatchResult],
    pre_classified: List[ExceptionCase],
    transactions_by_id: Dict[str, TransactionRecord],
) -> Tuple[List[ExceptionCase], Dict]:
    """
    Reconcile match_results with pre_classified exceptions.

    Any UNMATCHED or REVIEW_REQUIRED result that has no corresponding
    ExceptionCase gets a synthesised one here.

    Returns:
        all_exceptions: List[ExceptionCase]  — sorted by priority
        stats: dict  — break-type counts, priority breakdown, coverage
    """
    # Index pre-classified exceptions by txn_id
    classified_txn_ids = {exc.exception_id: exc for exc in pre_classified}
    pre_classified_by_txn: Dict[str, ExceptionCase] = {}
    for exc in pre_classified:
        pre_classified_by_txn[exc.txn_id] = exc

    all_exceptions: List[ExceptionCase] = list(pre_classified)
    exc_counter = len(pre_classified) + 1

    for result in match_results:
        # Only non-MATCHED results need an exception record
        if result.match_status == MatchStatus.MATCHED:
            continue

        # Skip if already classified
        if result.txn_id in pre_classified_by_txn:
            continue

        txn = transactions_by_id.get(result.txn_id)

        # Infer break type from the result's audit trail
        break_type = _infer_break_type(result)

        # Build root-cause hypothesis
        hypothesis = _build_hypothesis(result, txn, break_type)

        priority = _PRIORITY_MAP.get(break_type, Priority.MEDIUM)

        exc = ExceptionCase(
            exception_id=f"EXC-{exc_counter:04d}",
            txn_id=result.txn_id,
            break_type=break_type,
            root_cause_hypothesis=hypothesis,
            priority=priority,
            reason_codes=[break_type.value],
            evidence={
                "match_status": result.match_status.value,
                "confidence_score": result.confidence_score,
                "matched_against": result.matched_against,
                "audit_trail": result.audit_trail,
            },
        )
        all_exceptions.append(exc)
        exc_counter += 1

    # Sort: HIGH first, then MEDIUM, then LOW; within priority by txn_id
    priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
    all_exceptions.sort(key=lambda e: (priority_order.get(e.priority, 9), e.txn_id))

    # Compute stats
    stats = _compute_stats(all_exceptions, match_results)

    return all_exceptions, stats


def _infer_break_type(result: MatchResult) -> BreakType:
    """Infer break type from the audit trail string."""
    trail = result.audit_trail.upper()
    if "DUPLICATE" in trail:
        return BreakType.DUPLICATE_SETTLEMENT
    if "MISSING_UTR" in trail or "EMPTY UTR" in trail:
        return BreakType.MISSING_UTR
    if "PARTIAL_REFUND" in trail or "PARTIAL REFUND" in trail:
        return BreakType.PARTIAL_REFUND
    if "TIMING" in trail:
        return BreakType.TIMING_MISMATCH
    if "AMOUNT_MISMATCH" in trail or "AMOUNT MISMATCH" in trail:
        return BreakType.AMOUNT_MISMATCH
    if "NO_GATEWAY" in trail or "NO GATEWAY" in trail:
        return BreakType.NO_GATEWAY_RECORD
    if "NO_BANK" in trail or "NO BANK" in trail:
        return BreakType.NO_BANK_RECORD
    if "AMBIGUOUS" in trail or "GHOST" in trail:
        return BreakType.AMBIGUOUS
    if "LOW_CONFIDENCE" in trail or "LOW CONFIDENCE" in trail:
        return BreakType.AGENT_LOW_CONFIDENCE
    # Default based on match status
    if result.match_status == MatchStatus.REVIEW_REQUIRED:
        return BreakType.TIMING_MISMATCH
    return BreakType.UNKNOWN


def _build_hypothesis(
    result: MatchResult,
    txn: TransactionRecord | None,
    break_type: BreakType,
) -> str:
    """Build a plain-English root-cause hypothesis."""
    base_hypotheses = {
        BreakType.DUPLICATE_SETTLEMENT: (
            "Multiple gateway settlements detected for the same transaction. "
            "Risk of double-payment requires immediate escalation."
        ),
        BreakType.MISSING_UTR: (
            "Gateway settlement has no UTR reference, preventing bank cross-reference. "
            "Manual UTR lookup against bank statement required."
        ),
        BreakType.PARTIAL_REFUND: (
            "Settlement amount is a fraction of the ledger amount, consistent with a "
            "partial refund or chargeback. Verify refund record."
        ),
        BreakType.TIMING_MISMATCH: (
            "Bank credit arrived outside the expected T+1 window. "
            "Could indicate a bank holiday, batch lag, or timezone issue."
        ),
        BreakType.AMOUNT_MISMATCH: (
            "Settlement amount does not match ledger amount beyond fee tolerance. "
            "Investigate fee/tax calculation or settlement adjustment."
        ),
        BreakType.NO_GATEWAY_RECORD: (
            "No gateway settlement record found. Transaction may not have settled "
            "or records were not loaded."
        ),
        BreakType.NO_BANK_RECORD: (
            "Gateway settled but bank statement has no matching credit. "
            "Payment may be in float or settlement may have failed post-gateway."
        ),
        BreakType.AMBIGUOUS: (
            "No clean key or amount linkage found. Records are ambiguous — "
            "multiple possible matches or no plausible match exists."
        ),
        BreakType.AGENT_LOW_CONFIDENCE: (
            "Agent confidence below threshold. Could not determine match with sufficient "
            "confidence. Manual review required."
        ),
        BreakType.UNKNOWN: (
            "Break type could not be determined. Manual investigation required."
        ),
    }

    hypothesis = base_hypotheses.get(break_type, "Undetermined.")

    if txn:
        hypothesis += (
            f" [Transaction: {txn.txn_id}, Amount: ₹{txn.amount}, "
            f"Status: {txn.status}, Counterparty: {txn.counterparty}]"
        )

    return hypothesis


def _compute_stats(
    exceptions: List[ExceptionCase],
    match_results: List[MatchResult],
) -> Dict:
    """Compute exception statistics."""
    break_type_counts = Counter(e.break_type.value for e in exceptions)
    priority_counts = Counter(e.priority.value for e in exceptions)

    # Root-cause coverage: % exceptions with a non-trivial hypothesis
    covered = sum(
        1 for e in exceptions
        if e.root_cause_hypothesis and len(e.root_cause_hypothesis) > 20
    )
    coverage_pct = round(covered / len(exceptions) * 100, 1) if exceptions else 100.0

    # Confidence distribution for REVIEW_REQUIRED
    review_confidences = [
        r.confidence_score
        for r in match_results
        if r.match_status == MatchStatus.REVIEW_REQUIRED
    ]
    avg_review_conf = (
        round(sum(review_confidences) / len(review_confidences), 3)
        if review_confidences else 0.0
    )

    return {
        "total_exceptions": len(exceptions),
        "break_type_distribution": dict(break_type_counts),
        "priority_breakdown": dict(priority_counts),
        "root_cause_coverage_pct": coverage_pct,
        "avg_review_required_confidence": avg_review_conf,
    }

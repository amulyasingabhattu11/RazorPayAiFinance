"""
LLM Reasoning Agent.

Handles the "hard" records that the deterministic pass could not cleanly resolve.
Supports two modes:
  - LLM mode:  uses OpenAI function-calling (requires OPENAI_API_KEY in .env)
  - Stub mode: uses deterministic heuristics, no API key needed (for offline runs)

The stub is not a fake — it implements genuine logic for each break category
(timing gap, missing UTR, partial amount, ambiguous) and applies the same
confidence thresholds as the LLM mode, so it produces comparable results.

Confidence thresholds (from spec):
  ≥ 0.90   → MATCHED
  0.70–0.89 → REVIEW_REQUIRED
  < 0.70   → UNMATCHED (exception)
"""
from __future__ import annotations

import json
import os
from datetime import timedelta
from typing import Dict, List, Tuple

from src.agent.tools import (
    TOOL_SCHEMAS,
    check_tolerance,
    classify_exception,
    diff_records,
    flag_unresolved,
    lookup_record,
)
from src.data.models import (
    BreakType,
    ExceptionCase,
    MatchResult,
    MatchStatus,
    Priority,
    TransactionRecord,
)
from src.matching.deterministic import RecordIndex

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

MATCH_THRESHOLD = float(os.getenv("AGENT_MATCH_THRESHOLD", "0.90"))
REVIEW_THRESHOLD = float(os.getenv("AGENT_REVIEW_THRESHOLD", "0.70"))
PLACEHOLDER_KEY_PREFIX = "sk-..."


def resolve_agent_mode(requested_mode: str = "auto") -> Tuple[bool, str, str]:
    """
    Resolve requested mode into (use_llm, mode_label, model).

    auto uses LLM only when OPENAI_API_KEY is present and not the placeholder.
    llm requires a real OPENAI_API_KEY. stub always uses offline heuristics.
    """
    requested = (requested_mode or "auto").lower()
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    has_real_key = bool(api_key and not api_key.startswith(PLACEHOLDER_KEY_PREFIX))

    if requested == "stub":
        return False, "STUB (heuristic)", model
    if requested == "llm":
        if not has_real_key:
            raise ValueError(
                "--mode llm requires OPENAI_API_KEY to be set to a real key. "
                "Use --mode stub or --mode auto for offline heuristic mode."
            )
        return True, f"LLM ({model})", model
    if requested != "auto":
        raise ValueError(f"Unknown agent mode: {requested_mode}")

    if has_real_key:
        return True, f"LLM ({model})", model
    return False, "STUB (heuristic)", model


# ---------------------------------------------------------------------------
# Stub reasoning logic (no LLM required)
# ---------------------------------------------------------------------------

def _stub_reason(
    txn: TransactionRecord,
    index: RecordIndex,
    exc_counter_start: int,
) -> Tuple[MatchResult, List[ExceptionCase]]:
    """
    Pure-Python heuristic reasoner for a single transaction.
    Mirrors the categories the synthetic generator creates.
    """
    exceptions: List[ExceptionCase] = []
    exc_id = exc_counter_start

    txn_id = txn.txn_id
    sett_list = index.settlements_by_txn.get(txn_id, [])

    # ---- Case A: No settlement record at all (no_gateway_record) ----
    if not sett_list:
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.NO_GATEWAY_RECORD,
            root_cause_hypothesis=(
                "No gateway settlement record found for this transaction. "
                "Settlement may not have been processed or records are missing."
            ),
            priority=Priority.HIGH,
            reason_codes=["NO_GATEWAY_RECORD"],
            evidence={"txn_id": txn_id, "settlement_count": 0},
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.UNMATCHED,
            confidence_score=0.0,
            matched_against=[],
            audit_trail="STUB_AGENT: No gateway settlement record found.",
        )
        return result, exceptions

    # Use the first non-ghost settlement
    real_setts = [s for s in sett_list if not s.txn_id_ref.startswith("GHOST_")]

    # ---- Case B: Ghost-only settlements (ambiguous category) ----
    if not real_setts:
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.AMBIGUOUS,
            root_cause_hypothesis=(
                "Only a ghost/orphan settlement record exists (txn_id_ref does not match "
                "any ledger entry). Cannot attribute this settlement to this transaction."
            ),
            priority=Priority.MEDIUM,
            reason_codes=["AMBIGUOUS", "NO_GATEWAY_RECORD"],
            evidence={
                "txn_id": txn_id,
                "ghost_settlements": [s.settlement_id for s in sett_list],
            },
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.UNMATCHED,
            confidence_score=0.0,
            matched_against=[],
            audit_trail="STUB_AGENT: Only ghost settlement records found — ambiguous.",
        )
        return result, exceptions

    sett = real_setts[0]

    # ---- Case C: Missing UTR ----
    if not sett.utr_ref:
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.MISSING_UTR,
            root_cause_hypothesis=(
                "Gateway settlement record exists but UTR reference is empty. "
                "Cannot cross-reference with bank statement without a UTR."
            ),
            priority=Priority.HIGH,
            reason_codes=["MISSING_UTR"],
            evidence={
                "txn_id": txn_id,
                "settlement_id": sett.settlement_id,
                "utr_ref": sett.utr_ref,
                "settlement_amount": sett.amount,
            },
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.UNMATCHED,
            confidence_score=0.0,
            matched_against=[sett.settlement_id],
            audit_trail=(
                f"STUB_AGENT: Settlement {sett.settlement_id} has empty UTR. "
                "Cannot link to bank record."
            ),
        )
        return result, exceptions

    # ---- Case D: Settlement found, UTR found — check bank record ----
    bank = index.bank_by_utr.get(sett.utr_ref)

    if bank is None:
        # Settlement has UTR but no matching bank row
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.NO_BANK_RECORD,
            root_cause_hypothesis=(
                f"Gateway settlement {sett.settlement_id} (UTR: {sett.utr_ref}) "
                "has no matching bank statement entry. Payment may not have hit the bank."
            ),
            priority=Priority.MEDIUM,
            reason_codes=["NO_BANK_RECORD"],
            evidence={
                "txn_id": txn_id,
                "settlement_id": sett.settlement_id,
                "utr_ref": sett.utr_ref,
            },
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.UNMATCHED,
            confidence_score=0.0,
            matched_against=[sett.settlement_id],
            audit_trail=(
                f"STUB_AGENT: UTR {sett.utr_ref} not found in bank statement."
            ),
        )
        return result, exceptions

    # ---- Case E: Timing mismatch — check value_date vs settlement_date ----
    timing_delta_days = abs(
        (bank.value_date - sett.settlement_date).total_seconds() / 86400
    )

    # ---- Case F: Amount analysis ----
    amount_delta = abs(txn.amount - sett.amount)
    # Compute expected net
    fee = round(txn.amount * 0.02, 2)
    tax = round(fee * 0.18, 2)
    expected_net = round(txn.amount - fee - tax, 2)
    bank_net_delta = abs(bank.amount - expected_net)

    # Partial refund: settlement is substantially less (> 10 % off) than ledger
    is_partial_refund = (txn.amount > 0 and sett.amount < txn.amount * 0.85)

    if is_partial_refund:
        confidence = 0.80
        pct_settled = round(sett.amount / txn.amount * 100, 1)
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.PARTIAL_REFUND,
            root_cause_hypothesis=(
                f"Settlement amount ₹{sett.amount} is {pct_settled}% of ledger amount "
                f"₹{txn.amount}. Consistent with a partial refund. Refund record "
                "should be verified against the transaction status."
            ),
            priority=Priority.MEDIUM,
            reason_codes=["PARTIAL_REFUND", "AMOUNT_MISMATCH"],
            evidence={
                "txn_id": txn_id,
                "ledger_amount": txn.amount,
                "settled_amount": sett.amount,
                "pct_settled": pct_settled,
                "txn_status": str(txn.status),
            },
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.REVIEW_REQUIRED,
            confidence_score=confidence,
            matched_against=[sett.settlement_id, bank.utr],
            audit_trail=(
                f"STUB_AGENT: Partial refund detected. Settlement is {pct_settled}% "
                f"of ledger (₹{sett.amount} vs ₹{txn.amount}). "
                f"REVIEW_REQUIRED (confidence={confidence})."
            ),
        )
        return result, exceptions

    # Timing mismatch (> 36 h between settlement_date and bank value_date)
    if timing_delta_days > 1.5:
        confidence = 0.75
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.TIMING_MISMATCH,
            root_cause_hypothesis=(
                f"Bank value_date is {timing_delta_days:.1f} days after gateway "
                f"settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, "
                "batch processing lag, or timezone recording mismatch."
            ),
            priority=Priority.MEDIUM,
            reason_codes=["TIMING_MISMATCH"],
            evidence={
                "txn_id": txn_id,
                "settlement_date": sett.settlement_date.isoformat(),
                "bank_value_date": bank.value_date.isoformat(),
                "delta_days": round(timing_delta_days, 2),
                "settlement_amount": sett.amount,
                "bank_net": bank.amount,
            },
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.REVIEW_REQUIRED,
            confidence_score=confidence,
            matched_against=[sett.settlement_id, bank.utr],
            audit_trail=(
                f"STUB_AGENT: Timing mismatch. Value date is {timing_delta_days:.1f} days "
                f"after settlement. REVIEW_REQUIRED (confidence={confidence})."
            ),
        )
        return result, exceptions

    # Amount mismatch that is too large for tolerance
    if amount_delta > 1.0 and not is_partial_refund:
        confidence = 0.50
        exc_id += 1
        exc = ExceptionCase(
            exception_id=f"EXC-{exc_id:04d}",
            txn_id=txn_id,
            break_type=BreakType.AMOUNT_MISMATCH,
            root_cause_hypothesis=(
                f"Amount discrepancy of ₹{amount_delta:.2f} between ledger (₹{txn.amount}) "
                f"and gateway settlement (₹{sett.amount}). Exceeds fee/rounding tolerance. "
                "Likely a fee calculation error or adjustment."
            ),
            priority=Priority.HIGH,
            reason_codes=["AMOUNT_MISMATCH"],
            evidence={
                "txn_id": txn_id,
                "ledger_amount": txn.amount,
                "settlement_amount": sett.amount,
                "delta": round(amount_delta, 2),
            },
        )
        exceptions.append(exc)
        result = MatchResult(
            txn_id=txn_id,
            match_status=MatchStatus.UNMATCHED,
            confidence_score=confidence,
            matched_against=[sett.settlement_id],
            audit_trail=(
                f"STUB_AGENT: Amount mismatch ₹{amount_delta:.2f}. UNMATCHED."
            ),
        )
        return result, exceptions

    # If we reach here — amounts are close, timing is fine → matched
    confidence = 0.92
    result = MatchResult(
        txn_id=txn_id,
        match_status=MatchStatus.MATCHED,
        confidence_score=confidence,
        matched_against=[sett.settlement_id, bank.utr],
        audit_trail=(
            f"STUB_AGENT: Near-match resolved. Amount delta=₹{amount_delta:.2f}, "
            f"timing_delta={timing_delta_days:.1f}d. "
            f"MATCHED (confidence={confidence})."
        ),
    )
    return result, exceptions


# ---------------------------------------------------------------------------
# LLM agent runner (OpenAI function-calling)
# ---------------------------------------------------------------------------

def _run_llm_agent(
    txn: TransactionRecord,
    index: RecordIndex,
    client,  # openai.OpenAI instance
    model: str,
    exc_counter_start: int,
) -> Tuple[MatchResult, List[ExceptionCase]]:
    """
    Uses OpenAI function-calling to reason over a single ambiguous transaction.
    Falls back to stub if the LLM cannot produce a valid decision.
    """
    import json

    system_prompt = """You are an AI Finance Controller agent.
Your job is to reconcile a transaction record against gateway settlement and bank statement records.

You have access to tools: lookup_record, diff_records, check_tolerance, classify_exception, flag_unresolved.

Rules:
1. Call lookup_record to fetch relevant records.
2. Call diff_records to compare fields.
3. Call check_tolerance when amounts are close but not exact.
4. If you can match with confidence ≥ 0.90, respond with your final verdict as:
   VERDICT: MATCHED | confidence=X.XX | settlement_id=XXX | utr=XXX | reason=...
5. If confidence is 0.70–0.89, respond with:
   VERDICT: REVIEW_REQUIRED | confidence=X.XX | settlement_id=XXX | reason=...
6. If confidence < 0.70, call classify_exception or flag_unresolved.
7. Always cite evidence. Never force a match without evidence.
8. You MUST call flag_unresolved if you cannot reach a confident conclusion.
"""

    user_prompt = f"""Reconcile this transaction:

txn_id: {txn.txn_id}
order_id: {txn.order_id}
amount: ₹{txn.amount}
timestamp: {txn.timestamp.isoformat()}
counterparty: {txn.counterparty}
status: {txn.status}

Please:
1. Look up the settlement record(s) for this txn_id
2. Look up the bank record using the UTR
3. Diff the records
4. Apply tolerance checks as needed
5. Give your final verdict
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    exceptions: List[ExceptionCase] = []
    exc_id = exc_counter_start
    verdict_result: MatchResult | None = None
    max_turns = 8

    for _turn in range(max_turns):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        # Handle tool calls
        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                if fn_name == "lookup_record":
                    tool_result = lookup_record(index, args.get("source", ""), args.get("record_id", ""))
                elif fn_name == "diff_records":
                    tool_result = diff_records(args.get("record_a", {}), args.get("record_b", {}))
                elif fn_name == "check_tolerance":
                    tool_result = check_tolerance(
                        field=args.get("field", ""),
                        a=float(args.get("value_a", 0)),
                        b=float(args.get("value_b", 0)),
                        rule=args.get("rule", "amount_exact"),
                        tolerance=float(args.get("tolerance", 1.0)),
                    )
                elif fn_name == "classify_exception":
                    exc_id += 1
                    tool_result = classify_exception(
                        txn_id=args.get("txn_id", txn.txn_id),
                        break_type=args.get("break_type", "UNKNOWN"),
                        evidence=args.get("evidence", {}),
                        confidence=float(args.get("confidence", 0.0)),
                    )
                    from src.data.models import BreakType as BT, Priority as P
                    exceptions.append(ExceptionCase(
                        exception_id=f"EXC-{exc_id:04d}",
                        txn_id=tool_result["txn_id"],
                        break_type=BT(tool_result["break_type"]) if tool_result["break_type"] in BT.__members__ else BT.UNKNOWN,
                        root_cause_hypothesis=tool_result["root_cause_hypothesis"],
                        priority=P(tool_result["priority"]),
                        reason_codes=tool_result["reason_codes"],
                        evidence=tool_result["evidence"],
                    ))
                elif fn_name == "flag_unresolved":
                    exc_id += 1
                    tool_result = flag_unresolved(
                        txn_id=args.get("txn_id", txn.txn_id),
                        reason=args.get("reason", ""),
                        evidence=args.get("evidence"),
                    )
                    from src.data.models import BreakType as BT, Priority as P
                    exceptions.append(ExceptionCase(
                        exception_id=f"EXC-{exc_id:04d}",
                        txn_id=tool_result["txn_id"],
                        break_type=BT.AGENT_LOW_CONFIDENCE,
                        root_cause_hypothesis=tool_result["reason"],
                        priority=P.LOW,
                        reason_codes=["AGENT_LOW_CONFIDENCE"],
                        evidence=tool_result["evidence"],
                    ))
                    verdict_result = MatchResult(
                        txn_id=txn.txn_id,
                        match_status=MatchStatus.UNMATCHED,
                        confidence_score=0.0,
                        matched_against=[],
                        audit_trail=f"LLM_AGENT: flag_unresolved called. Reason: {tool_result['reason']}",
                    )
                else:
                    tool_result = {"error": f"Unknown tool {fn_name}"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result),
                })
            continue  # continue loop for next turn

        # No tool calls — check if there's a VERDICT in the text
        content = msg.content or ""
        if "VERDICT:" in content:
            verdict_result = _parse_verdict(txn.txn_id, content, index)
            break

        # No tool calls and no verdict — break to avoid infinite loop
        break

    # If we have no verdict result yet, fall back to stub
    if verdict_result is None:
        verdict_result, stub_excs = _stub_reason(txn, index, exc_id)
        verdict_result.audit_trail = verdict_result.audit_trail.replace(
            "STUB_AGENT:",
            "LLM_AGENT_FALLBACK_STUB:",
            1,
        )
        exceptions.extend(stub_excs)

    return verdict_result, exceptions


def _parse_verdict(txn_id: str, content: str, index: RecordIndex) -> MatchResult:
    """Parse LLM's VERDICT text into a MatchResult."""
    import re

    # Extract status
    if "MATCHED" in content and "REVIEW_REQUIRED" not in content:
        status = MatchStatus.MATCHED
    elif "REVIEW_REQUIRED" in content:
        status = MatchStatus.REVIEW_REQUIRED
    else:
        status = MatchStatus.UNMATCHED

    # Extract confidence
    conf_match = re.search(r"confidence=(\d+\.?\d*)", content)
    confidence = float(conf_match.group(1)) if conf_match else 0.5

    # Apply threshold rules
    if confidence >= MATCH_THRESHOLD:
        status = MatchStatus.MATCHED
    elif confidence >= REVIEW_THRESHOLD:
        status = MatchStatus.REVIEW_REQUIRED
    else:
        status = MatchStatus.UNMATCHED

    # Extract matched_against
    matched_against = []
    sett_match = re.search(r"settlement_id=(\S+)", content)
    if sett_match:
        matched_against.append(sett_match.group(1).strip("| "))
    utr_match = re.search(r"utr=(\S+)", content)
    if utr_match:
        matched_against.append(utr_match.group(1).strip("| "))

    return MatchResult(
        txn_id=txn_id,
        match_status=status,
        confidence_score=confidence,
        matched_against=matched_against,
        audit_trail=f"LLM_AGENT: {content[:400]}",
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_agent_pass(
    needs_agent: List[TransactionRecord],
    index: RecordIndex,
    exc_counter_start: int = 0,
    mode: str = "auto",
) -> Tuple[List[MatchResult], List[ExceptionCase]]:
    """
    Run the reasoning agent over all records that the deterministic pass
    could not cleanly resolve.

    Returns (results, exceptions).
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    use_llm, mode_label, model = resolve_agent_mode(mode)

    if use_llm:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            print(f"  [Agent] LLM mode — model={model}, records={len(needs_agent)}")
        except ImportError:
            print("  [Agent] openai package not installed, falling back to stub mode")
            use_llm = False

    results: List[MatchResult] = []
    all_exceptions: List[ExceptionCase] = []
    exc_counter = exc_counter_start

    for i, txn in enumerate(needs_agent, 1):
        if use_llm:
            result, excs = _run_llm_agent(txn, index, client, model, exc_counter)
        else:
            result, excs = _stub_reason(txn, index, exc_counter)

        results.append(result)
        all_exceptions.extend(excs)
        exc_counter += len(excs)

        mode_tag = "LLM" if use_llm else "STUB"
        print(f"  [Agent/{mode_tag}] ({i}/{len(needs_agent)}) {txn.txn_id} -> "
              f"{result.match_status} (conf={result.confidence_score:.2f})")

    return results, all_exceptions

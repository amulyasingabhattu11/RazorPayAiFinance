"""
Tool implementations for the reasoning agent.

These are the exact tools described in the spec:
  - lookup_record(source, id)
  - diff_records(a, b)
  - check_tolerance(field, a, b, rule)
  - classify_exception(record, evidence)
  - flag_unresolved(record, reason)

Each function is a pure Python function that the agent can call directly
(when running in stub/local mode) or that the LLM can call via function-calling
(when running in LLM mode). Both paths use the same implementations.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.matching.deterministic import RecordIndex

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def lookup_record(
    index: RecordIndex,
    source: str,
    record_id: str,
) -> Dict[str, Any]:
    """
    Fetch a record for cross-reference.

    source: "transaction" | "settlement" | "bank"
    record_id: txn_id | settlement_id | utr
    """
    source = source.lower()
    if source in ("transaction", "txn"):
        rec = index.txn_by_id.get(record_id)
        if rec:
            return rec.model_dump(mode="json")
        return {"error": f"Transaction {record_id!r} not found"}

    if source in ("settlement", "gateway"):
        rec = index.settlement_by_id.get(record_id)
        if rec:
            return rec.model_dump(mode="json")
        # also try by txn_id_ref
        setts = index.settlements_by_txn.get(record_id, [])
        if setts:
            return {"settlements": [s.model_dump(mode="json") for s in setts]}
        return {"error": f"Settlement for {record_id!r} not found"}

    if source in ("bank", "bank_statement"):
        rec = index.bank_by_utr.get(record_id)
        if rec:
            return rec.model_dump(mode="json")
        return {"error": f"Bank record for UTR {record_id!r} not found"}

    return {"error": f"Unknown source {source!r}. Use transaction/settlement/bank."}


def diff_records(
    a: Dict[str, Any],
    b: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Structured field-level diff between two record dicts.
    Returns fields that differ and the nature of the difference.
    """
    all_keys = set(a.keys()) | set(b.keys())
    diffs: Dict[str, Dict[str, Any]] = {}

    for key in all_keys:
        val_a = a.get(key)
        val_b = b.get(key)
        if val_a != val_b:
            diff_entry: Dict[str, Any] = {"a": val_a, "b": val_b}
            # Numeric fields get a delta
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                diff_entry["delta"] = round(val_b - val_a, 4)
                diff_entry["abs_delta"] = round(abs(val_b - val_a), 4)
            diffs[key] = diff_entry

    return {
        "has_differences": bool(diffs),
        "diff_count": len(diffs),
        "diffs": diffs,
    }


def check_tolerance(
    field: str,
    a: float,
    b: float,
    rule: str,
    tolerance: float = 1.0,
) -> Dict[str, Any]:
    """
    Apply a business rule to check if a numeric difference is within tolerance.

    rule examples:
      "fee_rounding"  — abs diff ≤ ₹1.00
      "amount_exact"  — abs diff ≤ ₹0.01
      "timing_days"   — |a - b| in days ≤ tolerance (pass tolerance=2)
    """
    delta = abs(a - b)
    within = delta <= tolerance
    return {
        "field": field,
        "value_a": a,
        "value_b": b,
        "delta": round(delta, 4),
        "rule": rule,
        "tolerance": tolerance,
        "within_tolerance": within,
        "verdict": "PASS" if within else "FAIL",
    }


def classify_exception(
    txn_id: str,
    break_type: str,
    evidence: Dict[str, Any],
    confidence: float,
) -> Dict[str, Any]:
    """
    Emit a structured exception classification.
    The agent must cite evidence — empty evidence should be rejected by the caller.
    """
    # Map break_type string to a root-cause hypothesis template
    hypotheses = {
        "AMOUNT_MISMATCH": (
            "Gateway settled a different amount than the ledger records. "
            "Possible causes: fee calculation error, partial processing, "
            "or a mid-flight adjustment."
        ),
        "TIMING_MISMATCH": (
            "Settlement or bank credit landed outside the expected T+1 window. "
            "Could indicate a bank holiday delay, a batch processing lag, "
            "or a timezone recording inconsistency."
        ),
        "MISSING_UTR": (
            "No UTR reference present in the gateway settlement record. "
            "Cannot link to bank statement. Requires manual UTR lookup."
        ),
        "DUPLICATE_SETTLEMENT": (
            "More than one gateway settlement record exists for the same transaction ID. "
            "Risk: double payment. Requires immediate investigation."
        ),
        "PARTIAL_REFUND": (
            "Settlement amount is significantly less than the ledger amount "
            "consistent with a partial refund. Refund record needs verification."
        ),
        "AMBIGUOUS": (
            "No clean key linkage found between ledger, gateway, and bank records. "
            "Amount is in range but cannot be definitively attributed."
        ),
        "NO_GATEWAY_RECORD": (
            "No gateway settlement record exists for this transaction. "
            "Either the transaction did not settle or records are missing."
        ),
        "NO_BANK_RECORD": (
            "Gateway settlement exists but no matching bank credit found. "
            "Possible float or reconciliation gap."
        ),
        "AGENT_LOW_CONFIDENCE": (
            "Agent could not reach a confident match determination. "
            "Manual review required."
        ),
    }

    hypothesis = hypotheses.get(break_type, "Undetermined root cause. Manual investigation required.")

    priority_map = {
        "DUPLICATE_SETTLEMENT": "HIGH",
        "MISSING_UTR": "HIGH",
        "AMOUNT_MISMATCH": "HIGH",
        "PARTIAL_REFUND": "MEDIUM",
        "TIMING_MISMATCH": "MEDIUM",
        "AMBIGUOUS": "MEDIUM",
        "NO_GATEWAY_RECORD": "HIGH",
        "NO_BANK_RECORD": "MEDIUM",
        "AGENT_LOW_CONFIDENCE": "LOW",
    }

    return {
        "txn_id": txn_id,
        "break_type": break_type,
        "root_cause_hypothesis": hypothesis,
        "priority": priority_map.get(break_type, "MEDIUM"),
        "confidence": confidence,
        "evidence": evidence,
        "reason_codes": [break_type],
    }


def flag_unresolved(
    txn_id: str,
    reason: str,
    evidence: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    The agent's 'I don't know' escape hatch.
    Must be used rather than forcing a low-confidence match.
    """
    return {
        "txn_id": txn_id,
        "status": "UNMATCHED",
        "reason": reason,
        "confidence": 0.0,
        "break_type": "AGENT_LOW_CONFIDENCE",
        "evidence": evidence or {},
    }


# ---------------------------------------------------------------------------
# OpenAI function-calling schema definitions
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "lookup_record",
            "description": "Fetch a record from one of the three sources for cross-reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "enum": ["transaction", "settlement", "bank"],
                        "description": "Which record source to look up.",
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The ID to look up: txn_id, settlement_id, or UTR.",
                    },
                },
                "required": ["source", "record_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "diff_records",
            "description": "Compute a field-level diff between two record dicts to surface discrepancies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_a": {
                        "type": "object",
                        "description": "First record as a dict.",
                    },
                    "record_b": {
                        "type": "object",
                        "description": "Second record as a dict.",
                    },
                },
                "required": ["record_a", "record_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_tolerance",
            "description": "Check if a numeric difference between two values is within a business-rule tolerance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "field": {"type": "string", "description": "Field name being compared."},
                    "value_a": {"type": "number", "description": "First value."},
                    "value_b": {"type": "number", "description": "Second value."},
                    "rule": {
                        "type": "string",
                        "enum": ["fee_rounding", "amount_exact", "timing_days"],
                        "description": "Business rule to apply.",
                    },
                    "tolerance": {
                        "type": "number",
                        "description": "Tolerance threshold (e.g. 1.0 for ₹1, 2 for 2 days).",
                    },
                },
                "required": ["field", "value_a", "value_b", "rule"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "classify_exception",
            "description": (
                "Emit a structured exception classification with break_type, "
                "root cause hypothesis, and cited evidence. Must provide evidence."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "txn_id": {"type": "string"},
                    "break_type": {
                        "type": "string",
                        "enum": [
                            "AMOUNT_MISMATCH", "TIMING_MISMATCH", "MISSING_UTR",
                            "DUPLICATE_SETTLEMENT", "PARTIAL_REFUND", "AMBIGUOUS",
                            "NO_GATEWAY_RECORD", "NO_BANK_RECORD", "AGENT_LOW_CONFIDENCE",
                        ],
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Concrete evidence dict citing which fields differ and by how much.",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Agent confidence 0.0–1.0 in this classification.",
                    },
                },
                "required": ["txn_id", "break_type", "evidence", "confidence"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "flag_unresolved",
            "description": (
                "Flag a record as unresolvable. Use this when confidence is below threshold "
                "or no clear match exists. Do NOT force a match instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "txn_id": {"type": "string"},
                    "reason": {
                        "type": "string",
                        "description": "Plain English reason why this record cannot be matched.",
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Supporting evidence for the unresolved flag.",
                    },
                },
                "required": ["txn_id", "reason"],
            },
        },
    },
]

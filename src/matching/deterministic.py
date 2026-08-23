"""
Deterministic matching pass — no LLM involved.

Implements two sub-passes:
  1. Exact match:     same txn_id → settlement txn_id_ref + UTR present + amounts equal ±₹0.01
  2. Tolerance match: amount differs only by a known fee/tax component within ₹FEE_TOLERANCE

Returns:
  matched:    list[MatchResult]  — MATCHED (confidence 1.0 or 0.8–0.95)
  unmatched:  list[TransactionRecord] — passed to the LLM agent
  index:      supporting lookup structures for the agent

The matcher is deliberately conservative:
  - Any case it cannot cleanly resolve goes to unmatched for the agent.
  - Duplicates (> 1 settlement per txn_id) are flagged as UNMATCHED immediately.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.data.models import (
    BankStatementRecord,
    BreakType,
    ExceptionCase,
    GatewaySettlementRecord,
    MatchResult,
    MatchStatus,
    Priority,
    TransactionRecord,
)

# Tolerances — can be overridden via env vars
FEE_TOLERANCE = float(os.getenv("FEE_TOLERANCE_INR", "1.0"))


# ---------------------------------------------------------------------------
# Index structures (also exposed to the agent)
# ---------------------------------------------------------------------------

@dataclass
class RecordIndex:
    """Fast-lookup maps built from raw record lists."""
    # txn_id → TransactionRecord
    txn_by_id: Dict[str, TransactionRecord] = field(default_factory=dict)
    # txn_id → list of GatewaySettlementRecord (list because duplicates possible)
    settlements_by_txn: Dict[str, List[GatewaySettlementRecord]] = field(default_factory=dict)
    # utr → BankStatementRecord
    bank_by_utr: Dict[str, BankStatementRecord] = field(default_factory=dict)
    # settlement_id → GatewaySettlementRecord
    settlement_by_id: Dict[str, GatewaySettlementRecord] = field(default_factory=dict)


def build_index(
    transactions: List[TransactionRecord],
    settlements: List[GatewaySettlementRecord],
    bank_rows: List[BankStatementRecord],
) -> RecordIndex:
    idx = RecordIndex()
    for t in transactions:
        idx.txn_by_id[t.txn_id] = t

    for s in settlements:
        idx.settlements_by_txn.setdefault(s.txn_id_ref, []).append(s)
        idx.settlement_by_id[s.settlement_id] = s

    for b in bank_rows:
        if b.utr:
            idx.bank_by_utr[b.utr] = b

    return idx


# ---------------------------------------------------------------------------
# Helper: amount tolerance check
# ---------------------------------------------------------------------------

def _amounts_match_exact(a: float, b: float) -> bool:
    return abs(a - b) <= 0.01


def _amounts_match_tolerance(a: float, b: float) -> bool:
    """True if |a - b| ≤ FEE_TOLERANCE (rounding/fee artefact)."""
    return abs(a - b) <= FEE_TOLERANCE


def _net_from_gross(amount: float) -> float:
    """Approximate net after 2 % fee + 18 % GST on fee."""
    fee = round(amount * 0.02, 2)
    tax = round(fee * 0.18, 2)
    return round(amount - fee - tax, 2)


# ---------------------------------------------------------------------------
# Deterministic match logic
# ---------------------------------------------------------------------------

@dataclass
class DeterministicResult:
    matched: List[MatchResult] = field(default_factory=list)
    needs_agent: List[TransactionRecord] = field(default_factory=list)
    immediate_exceptions: List[ExceptionCase] = field(default_factory=list)


def run_deterministic_pass(
    transactions: List[TransactionRecord],
    index: RecordIndex,
) -> DeterministicResult:
    """
    Fast deterministic pass over all transactions.

    Decision tree per transaction:
      1. No settlement at all           → needs_agent (or UNMATCHED if clearly absent)
      2. Duplicate settlements          → immediate UNMATCHED exception
      3. Missing UTR on settlement      → needs_agent
      4. Exact amount match + UTR found → MATCHED confidence=1.0
      5. Tolerance amount match         → MATCHED confidence=0.90
      6. Everything else                → needs_agent
    """
    result = DeterministicResult()
    exc_counter = 0

    for txn in transactions:
        sett_list = index.settlements_by_txn.get(txn.txn_id, [])

        # --- 1. No gateway record at all ---
        if not sett_list:
            # Check if there's a GHOST entry (ambiguous scenario)
            result.needs_agent.append(txn)
            continue

        # --- 2. Duplicate settlement ---
        # Filter to non-ghost settlements only
        real_sett_list = [s for s in sett_list if not s.txn_id_ref.startswith("GHOST_")]
        if len(real_sett_list) > 1:
            exc_counter += 1
            result.immediate_exceptions.append(ExceptionCase(
                exception_id=f"EXC-{exc_counter:04d}",
                txn_id=txn.txn_id,
                break_type=BreakType.DUPLICATE_SETTLEMENT,
                root_cause_hypothesis=(
                    f"Transaction {txn.txn_id} has {len(real_sett_list)} gateway "
                    f"settlement records: "
                    + ", ".join(s.settlement_id for s in real_sett_list)
                    + ". Only one settlement is expected."
                ),
                priority=Priority.HIGH,
                reason_codes=["DUPLICATE_SETTLEMENT"],
                evidence={
                    "settlement_ids": [s.settlement_id for s in real_sett_list],
                    "amounts": [s.amount for s in real_sett_list],
                },
            ))
            # Still surface as UNMATCHED in results
            result.matched.append(MatchResult(
                txn_id=txn.txn_id,
                match_status=MatchStatus.UNMATCHED,
                confidence_score=0.0,
                matched_against=[s.settlement_id for s in real_sett_list],
                audit_trail=f"DUPLICATE_SETTLEMENT: {len(real_sett_list)} settlements found for same txn_id.",
            ))
            continue

        # Exactly one real settlement for this txn_id
        sett = real_sett_list[0] if real_sett_list else sett_list[0]

        # --- 3. Missing UTR ---
        if not sett.utr_ref:
            result.needs_agent.append(txn)
            continue

        # --- 4. Exact match: txn_id + UTR + amount ≤ ₹0.01 ---
        bank = index.bank_by_utr.get(sett.utr_ref)

        if bank is not None and _amounts_match_exact(txn.amount, sett.amount):
            # Also verify bank net amount matches expected net
            expected_net = _net_from_gross(txn.amount)
            if _amounts_match_exact(bank.amount, expected_net):
                # Check timing: if bank value_date is > 36 h after settlement_date → agent
                timing_delta_hours = abs(
                    (bank.value_date - sett.settlement_date).total_seconds() / 3600
                )
                if timing_delta_hours > 36:
                    # Timing mismatch — defer to agent for REVIEW_REQUIRED determination
                    result.needs_agent.append(txn)
                    continue

                result.matched.append(MatchResult(
                    txn_id=txn.txn_id,
                    match_status=MatchStatus.MATCHED,
                    confidence_score=1.0,
                    matched_against=[sett.settlement_id, bank.utr],
                    audit_trail=(
                        f"EXACT_MATCH: txn_id={txn.txn_id} → settlement={sett.settlement_id} "
                        f"(utr={sett.utr_ref}) → bank_utr={bank.utr}. "
                        f"Amounts: txn={txn.amount}, gw={sett.amount}, bank_net={bank.amount} "
                        f"(expected_net={expected_net})."
                    ),
                ))
                continue

        # --- 5. Tolerance match: amounts within ₹FEE_TOLERANCE ---
        if bank is not None and _amounts_match_tolerance(txn.amount, sett.amount):
            diff = abs(txn.amount - sett.amount)
            result.matched.append(MatchResult(
                txn_id=txn.txn_id,
                match_status=MatchStatus.MATCHED,
                confidence_score=0.90,
                matched_against=[sett.settlement_id, bank.utr],
                audit_trail=(
                    f"TOLERANCE_MATCH: txn_id={txn.txn_id} → settlement={sett.settlement_id}. "
                    f"Amount diff=₹{diff:.2f} ≤ tolerance=₹{FEE_TOLERANCE}. "
                    f"Likely fee/tax rounding artefact."
                ),
            ))
            continue

        # --- 6. Everything else → agent ---
        result.needs_agent.append(txn)

    return result

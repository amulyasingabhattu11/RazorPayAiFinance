"""
Synthetic dataset generator.

Produces three aligned record sets (transactions, gateway settlements, bank
statements) for a 100-record batch with intentional, known-composition breaks
exactly as specified in the spec document:

  | Category                  | Count | Expected outcome  |
  |---------------------------|-------|-------------------|
  | Exact matches             |  60   | MATCHED           |
  | Fee/tax tolerance matches |  15   | MATCHED           |
  | Timing mismatches         |  10   | REVIEW_REQUIRED   |
  | Missing UTR reference     |   5   | UNMATCHED         |
  | Duplicate settlements     |   4   | UNMATCHED         |
  | Partial refunds           |   3   | REVIEW_REQUIRED   |
  | Genuinely ambiguous       |   3   | UNMATCHED         |
  | Total                     | 100   |                   |

Ground truth is written into each TransactionRecord.expected_outcome so the
pipeline can score itself against it at the end.

Usage:
    from src.data.generator import generate_dataset
    txns, settlements, bank_rows, ground_truth = generate_dataset(seed=42)
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from src.data.models import (
    BankStatementRecord,
    GatewaySettlementRecord,
    MatchStatus,
    TransactionRecord,
    TransactionStatus,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DATE = datetime(2024, 1, 1, 0, 0, 0)
CURRENCY = "INR"
FEE_RATE = 0.02        # 2 % gateway fee
TAX_RATE = 0.18        # 18 % GST on fee
COUNTERPARTIES = [
    "Acme Corp", "BlueStar Ltd", "Chakra Retail", "Dhriti Payments",
    "Eagle Finance", "FlexiPay", "GreenLeaf Merchants", "HorizonTech",
    "IndoTrade", "JetStream Commerce",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_txn_id() -> str:
    return "TXN" + uuid.uuid4().hex[:10].upper()


def _make_order_id() -> str:
    return "ORD" + uuid.uuid4().hex[:8].upper()


def _make_settlement_id() -> str:
    return "SET" + uuid.uuid4().hex[:10].upper()


def _make_utr() -> str:
    return "UTR" + uuid.uuid4().hex[:12].upper()


def _make_bank_ref() -> str:
    return "BNK" + uuid.uuid4().hex[:8].upper()


def _random_amount(rng: random.Random) -> float:
    """Return a round-ish transaction amount between ₹500 and ₹50 000."""
    return round(rng.uniform(500, 50_000), 2)


def _ts(base: datetime, offset_hours: float) -> datetime:
    return base + timedelta(hours=offset_hours)


def _gateway_record(
    txn: TransactionRecord,
    utr: str,
    settlement_date: datetime,
    amount_override: float | None = None,
) -> GatewaySettlementRecord:
    """Build a matching gateway record for a transaction."""
    amt = amount_override if amount_override is not None else txn.amount
    fee = round(amt * FEE_RATE, 2)
    tax = round(fee * TAX_RATE, 2)
    net = round(amt - fee - tax, 2)
    return GatewaySettlementRecord(
        settlement_id=_make_settlement_id(),
        txn_id_ref=txn.txn_id,
        amount=amt,
        fee=fee,
        tax=tax,
        net_amount=net,
        settlement_date=settlement_date,
        utr_ref=utr,
    )


def _bank_record(
    utr: str,
    amount: float,
    value_date: datetime,
    txn: TransactionRecord,
) -> BankStatementRecord:
    fee = round(amount * FEE_RATE, 2)
    tax = round(fee * TAX_RATE, 2)
    net = round(amount - fee - tax, 2)
    return BankStatementRecord(
        utr=utr,
        amount=net,
        value_date=value_date,
        narration=f"NEFT/{txn.counterparty}/{txn.order_id}",
        bank_ref=_make_bank_ref(),
    )


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_dataset(
    seed: int = 42,
) -> Tuple[
    List[TransactionRecord],
    List[GatewaySettlementRecord],
    List[BankStatementRecord],
    Dict[str, MatchStatus],
]:
    """
    Returns:
        transactions       — 100 TransactionRecord objects
        settlements        — corresponding GatewaySettlementRecords
        bank_rows          — corresponding BankStatementRecords
        ground_truth       — dict[txn_id -> expected MatchStatus]
    """
    rng = random.Random(seed)

    transactions: List[TransactionRecord] = []
    settlements: List[GatewaySettlementRecord] = []
    bank_rows: List[BankStatementRecord] = []
    ground_truth: Dict[str, MatchStatus] = {}

    hour = 0  # running clock so timestamps are sequential

    # ------------------------------------------------------------------
    # Category A — 60 exact matches  →  MATCHED
    # ------------------------------------------------------------------
    for _ in range(60):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=_random_amount(rng),
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.CAPTURED,
            expected_outcome=MatchStatus.MATCHED,
        )
        hour += rng.uniform(0.5, 2)
        utr = _make_utr()
        settle_date = _ts(BASE_DATE, hour + 24)   # T+1
        settlement = _gateway_record(txn, utr, settle_date)
        bank = _bank_record(utr, txn.amount, settle_date + timedelta(hours=2), txn)

        transactions.append(txn)
        settlements.append(settlement)
        bank_rows.append(bank)
        ground_truth[txn.txn_id] = MatchStatus.MATCHED

    # ------------------------------------------------------------------
    # Category B — 15 fee/tax tolerance matches  →  MATCHED
    # Amounts match after subtracting fee+tax (within ₹1 tolerance).
    # ------------------------------------------------------------------
    for _ in range(15):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=_random_amount(rng),
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.CAPTURED,
            expected_outcome=MatchStatus.MATCHED,
        )
        hour += rng.uniform(0.5, 2)
        utr = _make_utr()
        settle_date = _ts(BASE_DATE, hour + 24)
        # Slightly off due to a rounding artifact (still within tolerance)
        rounding_noise = rng.uniform(0.01, 0.99)
        settlement = _gateway_record(txn, utr, settle_date,
                                     amount_override=txn.amount + rounding_noise)
        bank = _bank_record(utr, txn.amount, settle_date + timedelta(hours=1), txn)

        transactions.append(txn)
        settlements.append(settlement)
        bank_rows.append(bank)
        ground_truth[txn.txn_id] = MatchStatus.MATCHED

    # ------------------------------------------------------------------
    # Category C — 10 timing mismatches (T+1 vs T+2)  →  REVIEW_REQUIRED
    # UTR matches but value_date is 48 h later than expected.
    # ------------------------------------------------------------------
    for _ in range(10):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=_random_amount(rng),
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.CAPTURED,
            expected_outcome=MatchStatus.REVIEW_REQUIRED,
        )
        hour += rng.uniform(0.5, 2)
        utr = _make_utr()
        settle_date = _ts(BASE_DATE, hour + 24)
        late_bank_date = settle_date + timedelta(hours=48)   # T+2 instead of T+1
        settlement = _gateway_record(txn, utr, settle_date)
        bank = _bank_record(utr, txn.amount, late_bank_date, txn)

        transactions.append(txn)
        settlements.append(settlement)
        bank_rows.append(bank)
        ground_truth[txn.txn_id] = MatchStatus.REVIEW_REQUIRED

    # ------------------------------------------------------------------
    # Category D — 5 missing UTR reference  →  UNMATCHED
    # Gateway record has empty utr_ref; bank has no matching row.
    # ------------------------------------------------------------------
    for _ in range(5):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=_random_amount(rng),
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.CAPTURED,
            expected_outcome=MatchStatus.UNMATCHED,
        )
        hour += rng.uniform(0.5, 2)
        settle_date = _ts(BASE_DATE, hour + 24)
        # UTR is missing — intentional break
        settlement = _gateway_record(txn, "", settle_date)
        # No bank row for this UTR

        transactions.append(txn)
        settlements.append(settlement)
        # bank_rows intentionally omitted for this category
        ground_truth[txn.txn_id] = MatchStatus.UNMATCHED

    # ------------------------------------------------------------------
    # Category E — 4 duplicate settlements  →  UNMATCHED
    # Two gateway records for the same txn_id.
    # ------------------------------------------------------------------
    for _ in range(4):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=_random_amount(rng),
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.CAPTURED,
            expected_outcome=MatchStatus.UNMATCHED,
        )
        hour += rng.uniform(0.5, 2)
        utr_1 = _make_utr()
        utr_2 = _make_utr()
        settle_date = _ts(BASE_DATE, hour + 24)
        settlement_a = _gateway_record(txn, utr_1, settle_date)
        settlement_b = _gateway_record(txn, utr_2, settle_date + timedelta(hours=6))
        bank_a = _bank_record(utr_1, txn.amount, settle_date + timedelta(hours=2), txn)

        transactions.append(txn)
        settlements.append(settlement_a)
        settlements.append(settlement_b)   # duplicate!
        bank_rows.append(bank_a)
        ground_truth[txn.txn_id] = MatchStatus.UNMATCHED

    # ------------------------------------------------------------------
    # Category F — 3 partial refunds  →  REVIEW_REQUIRED
    # Gateway settled only half the transaction amount.
    # ------------------------------------------------------------------
    for _ in range(3):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=_random_amount(rng),
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.REFUNDED,
            expected_outcome=MatchStatus.REVIEW_REQUIRED,
        )
        hour += rng.uniform(0.5, 2)
        utr = _make_utr()
        settle_date = _ts(BASE_DATE, hour + 24)
        partial_amount = round(txn.amount * rng.uniform(0.4, 0.6), 2)
        settlement = _gateway_record(txn, utr, settle_date,
                                     amount_override=partial_amount)
        bank = _bank_record(utr, partial_amount, settle_date + timedelta(hours=1), txn)

        transactions.append(txn)
        settlements.append(settlement)
        bank_rows.append(bank)
        ground_truth[txn.txn_id] = MatchStatus.REVIEW_REQUIRED

    # ------------------------------------------------------------------
    # Category G — 3 genuinely ambiguous  →  UNMATCHED
    # Amount is close to another transaction's amount; no key links them.
    # ------------------------------------------------------------------
    ambig_amounts = [_random_amount(rng) for _ in range(3)]
    for i, amt in enumerate(ambig_amounts):
        txn = TransactionRecord(
            txn_id=_make_txn_id(),
            order_id=_make_order_id(),
            amount=amt,
            currency=CURRENCY,
            timestamp=_ts(BASE_DATE, hour),
            counterparty=rng.choice(COUNTERPARTIES),
            status=TransactionStatus.CAPTURED,
            expected_outcome=MatchStatus.UNMATCHED,
        )
        hour += rng.uniform(0.5, 2)
        # Introduce a "decoy" settlement with a similar but different amount
        # and a completely different txn_id_ref (simulating a ghost settlement).
        decoy_utr = _make_utr()
        settle_date = _ts(BASE_DATE, hour + 24)
        decoy_amount = round(amt + rng.uniform(1, 10), 2)
        settlement = GatewaySettlementRecord(
            settlement_id=_make_settlement_id(),
            txn_id_ref="GHOST_" + txn.txn_id,   # no matching ledger entry
            amount=decoy_amount,
            fee=round(decoy_amount * FEE_RATE, 2),
            tax=round(decoy_amount * FEE_RATE * TAX_RATE, 2),
            net_amount=round(decoy_amount * (1 - FEE_RATE * (1 + TAX_RATE)), 2),
            settlement_date=settle_date,
            utr_ref=decoy_utr,
        )
        bank = _bank_record(decoy_utr, decoy_amount, settle_date + timedelta(hours=1), txn)

        transactions.append(txn)
        settlements.append(settlement)
        bank_rows.append(bank)
        ground_truth[txn.txn_id] = MatchStatus.UNMATCHED

    return transactions, settlements, bank_rows, ground_truth


# ---------------------------------------------------------------------------
# Quick sanity print when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    txns, setts, banks, gt = generate_dataset()
    from collections import Counter
    counts = Counter(gt.values())
    print(f"Transactions : {len(txns)}")
    print(f"Settlements  : {len(setts)}")
    print(f"Bank rows    : {len(banks)}")
    print(f"Ground truth : {dict(counts)}")

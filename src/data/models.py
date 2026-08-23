"""
Data models for the AI Finance Controller.
All three source record types, plus MatchResult, ExceptionCase, RunReport.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MatchStatus(str, Enum):
    MATCHED = "MATCHED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNMATCHED = "UNMATCHED"


class BreakType(str, Enum):
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    TIMING_MISMATCH = "TIMING_MISMATCH"
    MISSING_UTR = "MISSING_UTR"
    DUPLICATE_SETTLEMENT = "DUPLICATE_SETTLEMENT"
    PARTIAL_REFUND = "PARTIAL_REFUND"
    NO_GATEWAY_RECORD = "NO_GATEWAY_RECORD"
    NO_BANK_RECORD = "NO_BANK_RECORD"
    AMBIGUOUS = "AMBIGUOUS"
    AGENT_LOW_CONFIDENCE = "AGENT_LOW_CONFIDENCE"
    UNKNOWN = "UNKNOWN"


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TransactionStatus(str, Enum):
    CAPTURED = "CAPTURED"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"
    PENDING = "PENDING"


# ---------------------------------------------------------------------------
# Source records
# ---------------------------------------------------------------------------

class TransactionRecord(BaseModel):
    """Ledger / source-of-truth record."""
    txn_id: str
    order_id: str
    amount: float
    currency: str = "INR"
    timestamp: datetime
    counterparty: str
    status: TransactionStatus
    # Ground-truth label for scoring
    expected_outcome: Optional[MatchStatus] = None


class GatewaySettlementRecord(BaseModel):
    """What RazorPay's gateway says settled."""
    settlement_id: str
    txn_id_ref: str           # references TransactionRecord.txn_id
    amount: float
    fee: float
    tax: float
    net_amount: float
    settlement_date: datetime
    utr_ref: str              # empty string = missing UTR


class BankStatementRecord(BaseModel):
    """What actually hit the bank."""
    utr: str
    amount: float
    value_date: datetime
    narration: str
    bank_ref: str


# ---------------------------------------------------------------------------
# Match / exception / report records
# ---------------------------------------------------------------------------

class MatchResult(BaseModel):
    txn_id: str
    match_status: MatchStatus
    confidence_score: float = 0.0
    matched_against: List[str] = Field(default_factory=list)   # settlement_id, utr, etc.
    audit_trail: str = ""   # human-readable reason


class ExceptionCase(BaseModel):
    exception_id: str
    txn_id: str
    break_type: BreakType
    root_cause_hypothesis: str
    priority: Priority
    reason_codes: List[str] = Field(default_factory=list)
    evidence: dict = Field(default_factory=dict)


class RunReport(BaseModel):
    run_id: str
    total_records: int
    matched_count: int
    review_required_count: int
    # exception_count = UNMATCHED records only (true exceptions per spec §4 / §7)
    exception_count: int
    # review_and_exception_case_count = len(exceptions list) = REVIEW_REQUIRED + UNMATCHED
    # This is the total number of records in the Exception & Review Register.
    review_and_exception_case_count: int = 0
    match_rate_pct: float
    review_required_rate_pct: float
    exception_rate_pct: float
    # Agent mode used for this run: e.g. "STUB (heuristic)" or "LLM (gpt-4o-mini)"
    agent_mode: str = "STUB (heuristic)"
    # Ground-truth scoring (only available when running on synthetic data)
    ground_truth_matched: Optional[int] = None
    ground_truth_review: Optional[int] = None
    ground_truth_unmatched: Optional[int] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    false_match_rate: Optional[float] = None
    avg_confidence_matched: Optional[float] = None
    exceptions: List[ExceptionCase] = Field(default_factory=list)
    match_results: List[MatchResult] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    elapsed_seconds: Optional[float] = None

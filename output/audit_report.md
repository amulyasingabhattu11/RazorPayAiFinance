# AI Finance Controller — Audit Report
**Run ID:** `RUN-15C2CCA0`  
**Generated:** 2026-08-23 13:46:05 UTC  
**Elapsed:** 0.01s

---

## KPI Summary

| Metric | Agent Result | Ground Truth |
|--------|-------------|--------------|
| Total Records | 100 | — |
| MATCHED | 75 (75.0%) | 75 |
| REVIEW_REQUIRED | 13 (13.0%) | 13 |
| UNMATCHED | 12 (12.0%) | 12 |
| Precision | 100.0% | — |
| Recall | 100.0% | — |
| False-Match Rate | 0.0% | — |
| Avg Confidence (Matched) | 0.980 | — |

---

## Exception Breakdown

| Break Type | Count |
|-----------|-------|
| TIMING_MISMATCH | 10 |
| MISSING_UTR | 5 |
| DUPLICATE_SETTLEMENT | 4 |
| NO_GATEWAY_RECORD | 3 |
| PARTIAL_REFUND | 3 |

**Root-cause coverage:** 100.0% of exceptions have a hypothesis.

---

## Full Exception List

| ID | Txn ID | Priority | Break Type | Root Cause Hypothesis |
|----|--------|----------|------------|----------------------|
| EXC-0017 | `TXN146CAA6462` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0025 | `TXN29355973AF` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0024 | `TXN5C516919C8` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0016 | `TXN81BC2A0116` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0003 | `TXN8DAE40229A` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN8DAE40229A has 2 gateway settlement records: SET923D1244C9, SET0EC5C81CAF. Only one settlement is expecte… |
| EXC-0018 | `TXN8EE9A36D2A` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0001 | `TXN98CD6782E1` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN98CD6782E1 has 2 gateway settlement records: SETF5D7FCE206, SET00CF3EEE9F. Only one settlement is expecte… |
| EXC-0004 | `TXNBC12741B5B` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNBC12741B5B has 2 gateway settlement records: SET863E8B9B4A, SETB890BEA2A1. Only one settlement is expecte… |
| EXC-0002 | `TXNC9828C5912` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNC9828C5912 has 2 gateway settlement records: SETF755CADA97, SET36A2641AA9. Only one settlement is expecte… |
| EXC-0015 | `TXND8F366AF40` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0019 | `TXNDBDD756D01` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0023 | `TXNFF852D0C4F` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0021 | `TXN01DB575FCB` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0007 | `TXN0DDE6F0A05` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0010 | `TXN11D4DBF29D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0022 | `TXN26CA408C77` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0020 | `TXN27D4388E2C` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |
| EXC-0009 | `TXN724892A083` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0013 | `TXN82F9FDFDCA` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0008 | `TXN9C058FE8C8` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0011 | `TXNA3A0029422` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0005 | `TXNC6DC90F9AD` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0006 | `TXND33DF5DF68` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0012 | `TXND61F18EEAA` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0014 | `TXNEC2A1C0D38` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN01DB575FCB`  
**Break Type:** `PARTIAL_REFUND`  
**Priority:** `MEDIUM`  
**Agent Status:** `REVIEW_REQUIRED`  
**Confidence:** `0.80 if mr else 'N/A'`  

**Root Cause Hypothesis:**
> Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should be verified against the transaction status.

**Audit Trail:**
```
STUB_AGENT: Partial refund detected. Settlement is 45.0% of ledger (₹14359.8 vs ₹31894.78). REVIEW_REQUIRED (confidence=0.8).
```

**Why this matters:** A naive matcher might have forced this to MATCHED
because the amounts or IDs are *close*. The agent correctly deferred,
ensuring this record surfaces for human review rather than silently
passing through as a clean match.

---

## Architecture

```
Batch Loader
    │
Deterministic Matcher  ← exact key + tolerance rules (no LLM)
    │ matched           │ unmatched / low-confidence
    │           Reasoning Agent  ← LLM tool-calls (or stub heuristics)
    │                   │
    └──────────────────►│
                Exception Classifier  ← root-cause tag, priority
                        │
                Self-Report Writer  ← match rate, precision/recall, audit log
```

The LLM agent is scoped to *ambiguous* records only — not the full batch.
The deterministic pass handles the easy majority (60+ exact matches),
keeping LLM cost and latency minimal.

---
*Generated by AI Finance Controller — RazorPay Hackathon Track 04*
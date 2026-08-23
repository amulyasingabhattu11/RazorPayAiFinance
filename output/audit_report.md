# AI Finance Controller — Audit Report
**Run ID:** `RUN-7A95A087`  
**Generated:** 2026-08-23 14:02:16 UTC  
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
| EXC-0019 | `TXN16E6AFCAE5` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0025 | `TXN2C02A96860` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0023 | `TXN428BCCF424` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0016 | `TXN42B9FF9674` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0018 | `TXN6A3C009076` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0017 | `TXN7CA0F4E907` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0001 | `TXN92E04BB219` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN92E04BB219 has 2 gateway settlement records: SETBD92D92449, SETF90D537C3D. Only one settlement is expecte… |
| EXC-0024 | `TXNAEC972138E` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0003 | `TXNB05B330978` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNB05B330978 has 2 gateway settlement records: SETAFB99EB025, SET0AAFF08E69. Only one settlement is expecte… |
| EXC-0015 | `TXNF820B7E694` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0004 | `TXNFA7D7A0CB1` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNFA7D7A0CB1 has 2 gateway settlement records: SET436C3CDB24, SET26C6E40FBB. Only one settlement is expecte… |
| EXC-0002 | `TXNFD224222FE` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNFD224222FE has 2 gateway settlement records: SET9062F290DC, SET7F4D00C27E. Only one settlement is expecte… |
| EXC-0021 | `TXN0C028D39E5` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0006 | `TXN20974E26DE` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0012 | `TXN2BCD14E3ED` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0011 | `TXN36B37B8CFC` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0013 | `TXN47C363E5E2` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0005 | `TXN4BBC148204` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0022 | `TXN85BFE5450D` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0010 | `TXN91E32E6D9C` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0008 | `TXN9980F9C98D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0007 | `TXNB81665ED74` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0020 | `TXNBD93DC525A` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |
| EXC-0014 | `TXNDCF4E9BC8B` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0009 | `TXNF4E4AC1EE1` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN0C028D39E5`  
**Break Type:** `PARTIAL_REFUND`  
**Priority:** `MEDIUM`  
**Agent Status:** `REVIEW_REQUIRED`  
**Confidence:** `0.80`  

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
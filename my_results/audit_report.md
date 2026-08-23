# AI Finance Controller — Audit Report
**Run ID:** `RUN-EE6324D6`  
**Generated:** 2026-08-23 13:46:23 UTC  
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
| EXC-0003 | `TXN032D9B23AE` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN032D9B23AE has 2 gateway settlement records: SETB39DFC2064, SETD3587A9B10. Only one settlement is expecte… |
| EXC-0017 | `TXN200ACE3514` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0025 | `TXN38553C2B9F` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0019 | `TXN5555EDEFC5` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0024 | `TXN65C79BFBB5` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0015 | `TXN6713354590` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0001 | `TXN73D7D6179B` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN73D7D6179B has 2 gateway settlement records: SET963D9B1AEC, SET036ED76EE1. Only one settlement is expecte… |
| EXC-0002 | `TXNAA73D848D3` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNAA73D848D3 has 2 gateway settlement records: SET85FFAAD0AF, SETD4BFFF4546. Only one settlement is expecte… |
| EXC-0004 | `TXNAB77EB9289` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNAB77EB9289 has 2 gateway settlement records: SET1BF2939B54, SET456DAF86B0. Only one settlement is expecte… |
| EXC-0023 | `TXNCB46DB649A` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0018 | `TXNCB83DFC2C7` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0016 | `TXND46F86160D` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0020 | `TXN084F649DED` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |
| EXC-0008 | `TXN1171796FA1` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0010 | `TXN120E256E92` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0011 | `TXN30F70B6A57` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0009 | `TXN5DA25AE453` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0021 | `TXN9EF1BFA8C8` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0006 | `TXNB04E580062` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0014 | `TXNB1CD7E3DC1` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0012 | `TXNDDFD5C6C7D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0007 | `TXNE1E6D8299D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0013 | `TXNEA2DC0955E` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0022 | `TXNF24955A529` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0005 | `TXNFB0B878479` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN084F649DED`  
**Break Type:** `PARTIAL_REFUND`  
**Priority:** `MEDIUM`  
**Agent Status:** `REVIEW_REQUIRED`  
**Confidence:** `0.80 if mr else 'N/A'`  

**Root Cause Hypothesis:**
> Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should be verified against the transaction status.

**Audit Trail:**
```
STUB_AGENT: Partial refund detected. Settlement is 44.1% of ledger (₹6367.05 vs ₹14446.94). REVIEW_REQUIRED (confidence=0.8).
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
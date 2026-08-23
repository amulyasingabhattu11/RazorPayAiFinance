# AI Finance Controller — Audit Report
**Run ID:** `RUN-6B658F06`  
**Generated:** 2026-08-23 15:53:06 UTC  
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
| EXC-0023 | `TXN0615C54DBB` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0001 | `TXN07F7E1E50E` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN07F7E1E50E has 2 gateway settlement records: SET4DF6BF9C39, SET49A136FCF4. Only one settlement is expecte… |
| EXC-0018 | `TXN0802F0066E` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0002 | `TXN178624C3CB` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN178624C3CB has 2 gateway settlement records: SET898E9A3583, SETD3D7AC1121. Only one settlement is expecte… |
| EXC-0016 | `TXN218FE81183` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0024 | `TXN2EA5E4B5D1` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0003 | `TXN6784E3EBBB` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN6784E3EBBB has 2 gateway settlement records: SET7416737257, SETFF0CCEAD90. Only one settlement is expecte… |
| EXC-0015 | `TXN6DF68E0E52` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0004 | `TXNAFF61CC4E7` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNAFF61CC4E7 has 2 gateway settlement records: SETFAC8A567F9, SET6C4C6D2674. Only one settlement is expecte… |
| EXC-0019 | `TXNC8736CE11C` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0017 | `TXND4C80FB64B` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0025 | `TXNECB48BF6F8` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0011 | `TXN0D6392AD5E` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0006 | `TXN28B646595D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0005 | `TXN2E1C48D777` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0021 | `TXN6075A884E9` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0013 | `TXN705E6879C7` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0020 | `TXN8B8BD37A0C` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |
| EXC-0008 | `TXNB797A782F9` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0009 | `TXNC1B5F18908` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0012 | `TXNC24D65703B` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0007 | `TXNE060785672` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0014 | `TXNE5E5F6E4DB` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0022 | `TXNE8C21BCA45` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0010 | `TXNEC12CE2AD9` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN0D6392AD5E`  
**Break Type:** `TIMING_MISMATCH`  
**Priority:** `MEDIUM`  
**Agent Status:** `REVIEW_REQUIRED`  
**Confidence:** `0.75`  

**Root Cause Hypothesis:**
> Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch processing lag, or timezone recording mismatch.

**Audit Trail:**
```
STUB_AGENT: Timing mismatch. Value date is 2.0 days after settlement. REVIEW_REQUIRED (confidence=0.75).
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
# AI Finance Controller — Audit Report
**Run ID:** `RUN-1C046F91`  
**Generated:** 2026-08-23 16:50:49 UTC  
**Elapsed:** 0.01s  
**Agent mode:** ⚠ **STUB MODE** — deterministic heuristics, no live LLM calls  

> _Results are deterministic Python heuristics. To use the live LLM reasoning path, set `OPENAI_API_KEY` to a real key and run `python main.py --mode llm`._

---

## KPI Summary

| Metric | Agent Result | Ground Truth |
|--------|-------------|--------------|
| Total Records | 100 | — |
| MATCHED | 75 (75.0%) | 75 |
| REVIEW_REQUIRED | 13 (13.0%) | 13 |
| UNMATCHED (Exceptions) | 12 (12.0%) | 12 |
| Exception & Review Register | 25 total | 12 UNMATCHED + 13 REVIEW_REQUIRED |
| Precision | 100.0% | — |
| Recall | 100.0% | — |
| False-Match Rate | 0.0% | — |
| Avg Confidence (Matched) | 0.980 | — |

---

## Exception & Review Breakdown

> **Note:** `exception_count` (12) = UNMATCHED records only — true exceptions per spec §4.  
> `review_and_exception_case_count` (register total) = UNMATCHED + REVIEW_REQUIRED cases,  
> i.e., every record with a logged root-cause hypothesis held for human sign-off.

| Break Type | Count |
|-----------|-------|
| TIMING_MISMATCH | 10 |
| MISSING_UTR | 5 |
| DUPLICATE_SETTLEMENT | 4 |
| NO_GATEWAY_RECORD | 3 |
| PARTIAL_REFUND | 3 |

**Root-cause coverage:** 100.0% of cases have a hypothesis.

---

## Exception & Review Register (25 cases)

_12 UNMATCHED (true exceptions) + 13 REVIEW_REQUIRED (held for human sign-off)._

| ID | Txn ID | Priority | Break Type | Root Cause Hypothesis |
|----|--------|----------|------------|----------------------|
| EXC-0004 | `TXN007AD4D323` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN007AD4D323 has 2 gateway settlement records: SETEF5E325081, SETF0CB3B635F. Only one settlement is expecte… |
| EXC-0001 | `TXN1BB03FD01C` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN1BB03FD01C has 2 gateway settlement records: SET8E159AD93C, SETA8070106BE. Only one settlement is expecte… |
| EXC-0017 | `TXN231A4A8DF2` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0024 | `TXN2AE3359B55` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0016 | `TXN3E4C419CCA` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0003 | `TXN4B83DEEBC9` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN4B83DEEBC9 has 2 gateway settlement records: SET01C3FFE734, SET3437B9C9CB. Only one settlement is expecte… |
| EXC-0019 | `TXN61DC7501C8` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0023 | `TXNB45033C95D` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0018 | `TXNB9998FD6FE` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0025 | `TXND78E91D6C4` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0002 | `TXND9A7D23E3F` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXND9A7D23E3F has 2 gateway settlement records: SET577A5D929D, SET0EE4F60D12. Only one settlement is expecte… |
| EXC-0015 | `TXNF5DDAFE0ED` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0013 | `TXN057516AF66` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0022 | `TXN090B7806E1` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0012 | `TXN0C291A3345` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0007 | `TXN0D43DD8FCC` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0009 | `TXN255A8838F4` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0010 | `TXN2C58A57B53` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0021 | `TXN339D5AED97` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0011 | `TXN7D59F4ED5E` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0005 | `TXN8AFAF3C437` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0006 | `TXNADD7D96FEC` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0014 | `TXNBC9BE8B860` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0008 | `TXNCED2E51836` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0020 | `TXNDC6BE62BBA` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN057516AF66`  
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

_This decision was made by the deterministic stub heuristic (not live LLM). Re-run with `--mode llm` for LLM reasoning._

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
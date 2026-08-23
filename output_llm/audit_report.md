# AI Finance Controller — Audit Report
**Run ID:** `RUN-3C372CC8`  
**Generated:** 2026-08-23 17:06:14 UTC  
**Elapsed:** 0.00s  
**Agent mode:** ✓ **LLM MODE** — live OpenAI reasoning (LLM (gpt-4o-mini))  

> _Results use live LLM function-calling. For a reproducible offline run use `python main.py --mode stub`._

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
| EXC-0025 | `TXN0DB14B135C` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0017 | `TXN2B04117CB8` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0002 | `TXN3044FF5553` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN3044FF5553 has 2 gateway settlement records: SET2274C1C8FC, SET28A3FD012F. Only one settlement is expecte… |
| EXC-0001 | `TXN57289A1158` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN57289A1158 has 2 gateway settlement records: SET73905E9537, SET8484C85C61. Only one settlement is expecte… |
| EXC-0004 | `TXN5D82CFE1FF` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN5D82CFE1FF has 2 gateway settlement records: SETCD4393E472, SETA1CDD25F6C. Only one settlement is expecte… |
| EXC-0003 | `TXN6930469888` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN6930469888 has 2 gateway settlement records: SET1CA12FE8CC, SET7B32DD85FF. Only one settlement is expecte… |
| EXC-0023 | `TXN99B20F23C2` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0024 | `TXN9E6BC5A377` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0018 | `TXNAC0471C44A` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0016 | `TXNAF030D548E` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0019 | `TXNDF971A6B0A` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0015 | `TXNE24E8A055C` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0011 | `TXN01545B9A32` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0006 | `TXN0532933D07` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0013 | `TXN1A4D5C9191` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0009 | `TXN1D80B41234` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0005 | `TXN31FFDEDABC` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0010 | `TXN58839BF935` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0021 | `TXN5C1179D988` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0022 | `TXN690DBF7377` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0008 | `TXN69D51D7506` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0014 | `TXN70342BF1BF` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0012 | `TXNAD13E0EA6B` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0007 | `TXNBF23AC98E7` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0020 | `TXNF808C31B9A` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN01545B9A32`  
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
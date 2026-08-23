# AI Finance Controller — Audit Report
**Run ID:** `RUN-65092233`  
**Generated:** 2026-08-23 16:50:20 UTC  
**Elapsed:** 0.00s  
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
| EXC-0016 | `TXN00AF2A8631` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0017 | `TXN23FC2F259E` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0001 | `TXN51D6C2737B` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN51D6C2737B has 2 gateway settlement records: SETD52541E4BE, SETDF4A062AB4. Only one settlement is expecte… |
| EXC-0025 | `TXN57C36D7EC0` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0019 | `TXN5C22984830` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0018 | `TXN66D7B3E0D6` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0003 | `TXN7F66A58616` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN7F66A58616 has 2 gateway settlement records: SET147FEAE3CF, SETB502078958. Only one settlement is expecte… |
| EXC-0002 | `TXN8EAA0728D0` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXN8EAA0728D0 has 2 gateway settlement records: SET0959B7BC40, SET6167D0B6FC. Only one settlement is expecte… |
| EXC-0015 | `TXNBB0552F49D` | **HIGH** | MISSING_UTR | Gateway settlement record exists but UTR reference is empty. Cannot cross-reference with bank statement without a UTR.… |
| EXC-0004 | `TXNDABCEDF6AB` | **HIGH** | DUPLICATE_SETTLEMENT | Transaction TXNDABCEDF6AB has 2 gateway settlement records: SETB21877130B, SET42E691E1DF. Only one settlement is expecte… |
| EXC-0023 | `TXNE90705A8F1` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0024 | `TXNF6A135D16F` | **HIGH** | NO_GATEWAY_RECORD | No gateway settlement record found for this transaction. Settlement may not have been processed or records are missing.… |
| EXC-0008 | `TXN0BA6F1BF1D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0020 | `TXN2EE2C4BF13` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹6367.05 is 44.1% of ledger amount ₹14446.94. Consistent with a partial refund. Refund record should b… |
| EXC-0022 | `TXN3DDB7215D0` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹22032.18 is 48.5% of ledger amount ₹45453.87. Consistent with a partial refund. Refund record should … |
| EXC-0011 | `TXN50207BF653` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0021 | `TXN52D21A2355` | **MEDIUM** | PARTIAL_REFUND | Settlement amount ₹14359.8 is 45.0% of ledger amount ₹31894.78. Consistent with a partial refund. Refund record should b… |
| EXC-0007 | `TXN6E0F99B3CC` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0014 | `TXN8605B387E6` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0006 | `TXN9FF040BF1B` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0010 | `TXNC9B5BC105F` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0005 | `TXND05E3088FE` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0009 | `TXND62B37167D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0012 | `TXND75FD8DA4D` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |
| EXC-0013 | `TXNFEBDA4030E` | **MEDIUM** | TIMING_MISMATCH | Bank value_date is 2.0 days after gateway settlement_date. Expected T+1 (≤24 h). Possible causes: bank holiday, batch pr… |

---

## Worked Example: A Correctly Refused Force-Match

The following shows a case where the agent **correctly refused** to force-match
a record, instead surfacing it as `REVIEW_REQUIRED` or `UNMATCHED`:

**Transaction:** `TXN0BA6F1BF1D`  
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
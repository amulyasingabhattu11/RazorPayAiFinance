# AI Finance Controller — Specifications Document
### RazorPay Hackathon — Track 04

---

## 1. Problem Framing

**Track prompt:** "Run the books and the cash position." Build an agent that closes one finance-ops loop across a 50+ record batch of synthetic data, reporting its match rate and the exceptions it could not resolve.

**Generalized problem statement:** Finance operations teams still verify money movement by hand — checking that what was charged matches what settled, what was promised matches what's owed, and what's booked matches what's real. This doesn't scale with transaction volume, and manual checking is slow, inconsistent, and hard to audit. We will build an **AI Finance Controller agent** that ingests a batch of synthetic financial records, verifies them against a source of truth, resolves what it safely can, and produces an honest, auditable report of match rate, resolved items, and unresolved exceptions — with reasoning attached to every decision.

**Why now (per the brief):** verification capacity, not generation speed, is the bottleneck in 2026 AI builds. The bar isn't "can it write code" — it's "can it check work and know what it doesn't know."

**Chosen direction:** *Multi-source reconciliation*, generalized as a payments-reconciliation loop (transaction ledger ↔ payment gateway settlement ↔ bank statement) — the natural RazorPay-shaped version of "match A against B and explain the gaps." This subsumes the other example directions structurally (a settlement Q&A agent, a cash forecaster, and a tax-line matcher are all "match/verify + explain exceptions" with a different pair of sources), so the same architecture generalizes if the track pivots.

---

## 2. Success Bar (what the judges are actually scoring)

1. **Throughput** — the agent processes the full batch (50+ records) end-to-end without manual intervention.
2. **Measured accuracy** — match rate is *computed*, not asserted. Ground truth is known (synthetic data), so precision/recall against it must be reportable.
3. **Honest exception list** — every unresolved or low-confidence record is surfaced with a reason, not silently dropped or force-matched. A single cherry-picked correct match proves nothing; an unreviewed 100% match rate is a red flag, not a win.

---

## 3. Scope for the Build

**In scope:**
- Synthetic dataset generation (2–3 record sources, 50+ transactions, seeded with deliberate breaks)
- Deterministic matching pass (exact + tolerance-based)
- Agentic pass over unmatched records (LLM reasons over near-misses, applies judgment, cites its reasoning)
- Exception categorization + confidence scoring
- Self-report: match rate, resolution rate, exception list with root-cause tags
- A short audit trail per record (why it matched / why it didn't)

**Out of scope (explicitly, to protect build time):**
- Real bank/gateway API integration — synthetic data only, per the brief
- A UI dashboard — a structured report (JSON/Markdown/CLI output) is sufficient; a minimal UI is a stretch goal only
- Multi-currency FX handling — assume single currency unless time permits

---

## 4. Data Model

Three record sources:

**TransactionRecord** (source of truth / ledger)
`txn_id, order_id, amount, currency, timestamp, counterparty, status`

**GatewaySettlementRecord** (what RazorPay's own gateway says settled)
`settlement_id, txn_id_ref, amount, fee, tax, net_amount, settlement_date, utr_ref`

**BankStatementRecord** (what actually hit the bank)
`utr, amount, value_date, narration, bank_ref`

**MatchResult**
`txn_id, match_status (MATCHED/REVIEW_REQUIRED/UNMATCHED), confidence_score, matched_against[]`

**ExceptionCase**
`exception_id, txn_id, break_type, root_cause_hypothesis, priority, reason_codes[]`

**RunReport**
`run_id, total_records, matched_count, review_required_count, exception_count, match_rate_pct, generated_at`

### Ground-Truth Synthetic Dataset Plan

The dataset must be built to a known, intentional composition — not randomly generated and randomly broken — so the correct answer is known *before* the agent runs, and actual performance can be scored against it afterward. Example composition for a 100-record batch:

| Category | Count | Expected outcome |
|---|---|---|
| Exact matches | 60 | MATCHED |
| Fee/tax tolerance matches | 15 | MATCHED |
| Timing mismatches (T+1 vs T+2) | 10 | REVIEW_REQUIRED |
| Missing UTR reference | 5 | UNMATCHED (exception) |
| Duplicate settlements | 4 | UNMATCHED (exception) |
| Partial refunds | 3 | REVIEW_REQUIRED |
| Genuinely ambiguous (no clean answer) | 3 | UNMATCHED (exception) |
| **Total** | **100** | **75 expected MATCHED, 13 REVIEW_REQUIRED, 12 UNMATCHED** |

This gives a ground truth to score against directly, e.g. *"Ground truth: 75 should auto-match, 25 should not. Agent produced 72 matched, 28 flagged."* — precision/recall/false-match-rate become computable, not asserted. Scale proportionally for the 50+ record minimum if the final batch size differs.

---

## 5. Agent Architecture

```
                    ┌─────────────────────┐
                    │   Batch Loader        │  loads 3 synthetic sources
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Deterministic Matcher  │  exact key + tolerance rules
                    │ (fast pass, no LLM)    │  handles the "easy" majority
                    └──────────┬───────────┘
                     matched   │   unmatched / low-confidence
                    ┌──────────▼───────────┐
                    │   Reasoning Agent      │  LLM tool-calls over ambiguous
                    │ (tools: lookup, diff,  │  records only — not the whole
                    │  flag, classify)       │  batch, to keep cost/latency down
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Exception Classifier   │  root-cause tag, priority, action
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Self-Report Writer   │  match rate, exceptions, audit log
                    └───────────────────────┘
```

**Design principle:** the LLM agent is deliberately scoped to the *hard* records only. Running an LLM over every record to "match" it is slower, more expensive, and less auditable than a deterministic pass — the agentic value-add is judgment on ambiguity, not brute-force comparison. This is the generalizable core across all four example directions.

**Agent tools (function-calling surface):**
- `lookup_record(source, id)` — fetch a record for cross-reference
- `diff_records(a, b)` — structured field-level diff
- `check_tolerance(field, a, b, rule)` — apply a business rule (e.g. fee rounding ≤ ₹1)
- `classify_exception(record, evidence)` — emit break_type + root_cause_hypothesis + confidence
- `flag_unresolved(record, reason)` — the "I don't know" escape hatch — must be used, not avoided

**Fallback behaviour:** if the agent's confidence is below threshold on a record, or a tool call fails, the record goes to the exception list with `reason_code = AGENT_LOW_CONFIDENCE` rather than being force-matched. Never silent-drop, never silent-force-match.

---

## 6. Matching & Confidence Logic

An LLM's confidence score is not a settlement decision — a 0.5-confidence agent guess should never be treated as a successful match in a finance system. Thresholds are deliberately conservative:

1. **Exact match:** same `txn_id`/`utr` reference across sources, amounts equal within ₹0.01 → **MATCHED**, confidence 1.0. No LLM involved.
2. **Tolerance match:** amounts differ only by a known fee/tax component within a configured tolerance → **MATCHED**, confidence 0.8–0.95, reason code logged. No LLM involved.
3. **Agent-reasoned match:** no exact key; agent proposes a pairing via amount + timestamp + counterparty proximity, and must classify it by confidence:
   - **≥ 0.90** → **MATCHED** (auto)
   - **0.70 – 0.89** → **REVIEW_REQUIRED** (probable match, held for human sign-off — not counted as a clean match)
   - **< 0.70** → **UNMATCHED** (exception)
4. **Unresolved:** no plausible pairing at all, or a tool-call failure → **UNMATCHED**, goes to the exception list with a root-cause hypothesis.

```
                 ┌── MATCHED           (exact / tolerance / agent ≥0.90)
                 │
Record ──────────┼── REVIEW_REQUIRED   (agent 0.70–0.89, or a plausible-but-not-clean
                 │                      case, e.g. ₹10,000 ledger vs ₹9,999.50 gateway —
                 │                      "probably a rounding/fee gap" is a hypothesis,
                 │                      not a confirmed match)
                 │
                 └── UNMATCHED         (agent <0.70, or no pairing found)
```

REVIEW_REQUIRED exists specifically to stop the agent from quietly upgrading a plausible-looking near-miss into a clean match. It is not counted toward the auto-match rate — only toward total resolution/throughput.

---

## 7. KPI / Success Metrics

| Metric | What it shows |
|---|---|
| Auto-match rate (%) | MATCHED / total records — excludes REVIEW_REQUIRED |
| Precision / recall vs. ground truth | correctness of the matcher, not just coverage |
| Review-required rate (%) | how often the agent correctly deferred instead of forcing a match |
| Exception resolution honesty | % of true breaks correctly flagged (not force-matched) — the metric that catches a fake 100% |
| Avg. confidence on matched records | is the agent confident for the right reasons |
| Throughput | records/sec or total batch time |
| Root-cause coverage | % of exceptions with a non-empty, plausible root-cause hypothesis |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Agent over-matches to inflate its own score | Score against known ground truth; report precision/recall, not just match rate |
| Agent hallucinates a root cause | Require evidence citation (which fields, which diff) in every classification |
| Non-determinism across runs | Fix random seed for synthetic data; log full reasoning trail per record for replay |
| Cost/latency from LLM calls | Deterministic pass first; LLM only touches the ambiguous subset |

---

## 9. Deliverables

1. Synthetic dataset generator (3 sources, 50+ records, seeded breaks) — runnable script
2. Working agent (deterministic + LLM reasoning layers) — runnable, not pseudocode
3. `RunReport` output (match rate, review-required count, exceptions, confidence, root causes)
4. Short write-up: architecture, KPI tree, one worked example of an exception the agent correctly refused to force-match
5. (Stretch) minimal CLI or notebook view of the report

---

## 10. Open Assumptions

- Single currency, single-batch (not streaming) processing for the hackathon build
- "50+ records" read as the full test batch across all sources combined, not per source — confirm against actual dataset size if provided
- No live RazorPay API access assumed; synthetic data is self-generated, per the brief's "no external data required" framing

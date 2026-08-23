# AI Finance Controller

> **RazorPay Hackathon — Track 04 · "Run the books and the cash position"**

An agentic payment-reconciliation loop that ingests a batch of synthetic financial records (transaction ledger ↔ gateway settlements ↔ bank statement), resolves every record it can with confidence, and produces a fully auditable run report — with a root-cause hypothesis attached to every exception it could not resolve.

---

## What it does

1. **Generates** a synthetic 100-record dataset across three sources (ledger, gateway, bank), seeded with deliberate breaks: exact matches, fee-rounding tolerance, timing mismatches, missing UTRs, duplicate settlements, partial refunds, and ambiguous records.
2. **Matches deterministically** first — exact key + tolerance rules, no LLM — handling the easy majority (~75%).
3. **Routes ambiguous records** to a reasoning agent: either a live OpenAI LLM (function-calling) or a deterministic stub heuristic when no API key is present.
4. **Classifies every exception** with a break type, root-cause hypothesis, and priority.
5. **Writes a self-report** — JSON, Markdown audit report, and a web dashboard — with precision/recall scored against known ground truth.

This is Track 04's "Run the books" shape: verification capacity over generation speed, honest exception surfacing over force-matching, and full auditability of every decision.

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

The LLM agent is scoped to *ambiguous* records only — not the full batch. The deterministic pass handles the easy majority (60+ exact matches), keeping LLM cost and latency minimal.

**Agent modes:**
- `stub` — deterministic Python heuristics, no API key needed, fully reproducible
- `llm` — live OpenAI function-calling (requires `OPENAI_API_KEY`)
- `auto` — uses LLM if `OPENAI_API_KEY` is present and not a placeholder, otherwise stub

---

## Project structure

```
RazorPayAiFinance/
├── main.py                        # CLI entry point
├── requirements.txt
├── .env.example                   # copy to .env, fill in your API key
├── AI_Finance_Controller_Spec.md  # full spec
│
├── src/
│   ├── pipeline.py                # 5-stage orchestrator
│   ├── data/
│   │   ├── models.py              # Pydantic data models
│   │   └── generator.py           # synthetic dataset generator
│   ├── matching/
│   │   ├── deterministic.py       # exact + tolerance matcher
│   │   └── classifier.py          # exception classifier / prioritizer
│   ├── agent/
│   │   ├── reasoning.py           # LLM agent + stub heuristics
│   │   └── tools.py               # agent tool implementations
│   └── reporting/
│       └── writer.py              # console, JSON, and Markdown report writers
│
├── frontend/
│   ├── index.html                 # main dashboard
│   ├── audit.html                 # audit report viewer
│   ├── app.js                     # dashboard logic
│   └── styles.css
│
└── output/                        # generated on every run
    ├── report.json
    └── audit_report.md
```

---

## Setup

**Requirements:** Python 3.10+

```bash
# 1. Clone / unzip the repo, then enter the directory
cd RazorPayAiFinance

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your environment file
copy .env.example .env        # Windows
# or: cp .env.example .env    # macOS / Linux

# 4. (Optional) Add your OpenAI API key for LLM mode
# Edit .env and set:  OPENAI_API_KEY=sk-<your-real-key>
# Leave as sk-... to use stub mode (no key needed)
```

### When is OPENAI_API_KEY needed?

| Mode | Key required? | What runs |
|------|--------------|-----------|
| `--mode stub` | No | Deterministic Python heuristics |
| `--mode auto` (default) | No (falls back to stub) | LLM if key is real, otherwise stub |
| `--mode llm` | Yes (real key) | Live OpenAI function-calling |

---

## How to run

```bash
# Default run (seed=42, auto-detect mode → stub if no key)
python main.py

# Explicit stub mode (always offline, reproducible)
python main.py --mode stub

# LLM mode (requires real OPENAI_API_KEY in .env)
python main.py --mode llm

# Custom seed
python main.py --seed 123

# Custom output directory
python main.py --output-dir ./my_results

# Quiet mode (suppress per-record progress)
python main.py --no-verbose

# Combine flags
python main.py --mode llm --seed 42 --output-dir output_llm
```

The pipeline exits with code `1` if any HIGH-priority exceptions are found (useful for CI), `0` otherwise.

---

## How to view the dashboard

The frontend is a static HTML/JS app — serve the project root with Python's built-in HTTP server:

```bash
# From the repo root directory:
python -m http.server 8000
```

Then open in your browser:

```
http://localhost:8000/frontend/
```

The dashboard reads `../output/report.json` relative to the frontend directory. If you used `--output-dir`, adjust `REPORT_URL` in `frontend/app.js` accordingly, or copy `report.json` into `output/`.

---

## Where outputs land

After each run, two files are written to the output directory (default: `output/`):

| File | Contents |
|------|----------|
| `output/report.json` | Full `RunReport` object: all KPIs, exception list, match results, audit trails |
| `output/audit_report.md` | Human-readable audit report: KPI table, exception register, worked example |

---

## KPI definitions (spec §7)

| KPI | Definition |
|-----|-----------|
| **Auto-match rate (%)** | `MATCHED / total_records` — only clean matches; REVIEW_REQUIRED is excluded |
| **Review-required rate (%)** | `REVIEW_REQUIRED / total_records` — records the agent correctly deferred rather than force-matching |
| **Exception rate (%)** | `UNMATCHED / total_records` — records flagged as true exceptions |
| **Exception & Review Register** | `len(exceptions)` = UNMATCHED + REVIEW_REQUIRED — every record with a logged root-cause case |
| **Precision** | `TP / (TP + FP)` vs. ground truth — are the matched records actually correct? |
| **Recall** | `TP / (TP + FN)` vs. ground truth — did we catch all the should-be-matched records? |
| **False-match rate** | `FP / (TP + FN)` — fraction of "should-match" records that were incorrectly forced through |
| **Avg confidence (matched)** | Mean confidence score on MATCHED records — is the agent confident for the right reasons? |
| **Root-cause coverage** | % of exception/review cases with a non-trivial hypothesis |
| **Throughput** | Total batch time in seconds |

> **Note on the two exception numbers:** `exception_count` (e.g. 12) = UNMATCHED records only — the spec's definition of a true exception. `review_and_exception_case_count` (e.g. 25) = the full Exception & Review Register, which includes REVIEW_REQUIRED cases held for human sign-off. Both numbers are correct; they measure different things.

---

## Known limitations

### Stub vs. LLM mode

- **Default/stub runs are honest heuristics, not "agentic."** The stub implements genuine break-detection logic (timing gaps, missing UTR, partial refund, amount mismatch) and applies the same confidence thresholds as the LLM path — results are comparable and deterministic. But the reasoning is Python code, not a language model reading evidence.
- **LLM runs require a real `OPENAI_API_KEY`.** Without it, `--mode llm` will fail with a clear error. `--mode auto` falls back silently to stub and labels the output accordingly.
- Every generated artifact (console, JSON, Markdown, dashboard) now labels the run mode explicitly — a stub-mode run will never be mistaken for LLM output.

### Dataset

- Synthetic data only — no real RazorPay API integration (out of scope per spec §3).
- Single currency (INR), single-batch processing.
- Seed-fixed for reproducibility; change with `--seed` for variation.

### LLM cost

- The LLM agent is called only for the ambiguous subset (~21 records), not the full batch, to keep API cost minimal.
- Model defaults to `gpt-4o-mini` (configurable via `OPENAI_MODEL` in `.env`).

---

## Re-running after code changes

```bash
# Regenerate both output files and verify the new fields appear
python main.py --mode stub

# Check output/report.json contains:
#   "agent_mode": "STUB (heuristic)"
#   "review_and_exception_case_count": 25
```

---

*AI Finance Controller — RazorPay Hackathon Track 04*

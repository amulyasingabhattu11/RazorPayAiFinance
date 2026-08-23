const REPORT_URL = "../output/report.json";

const els = {
  subline: document.querySelector("#auditSubline"),
  summary: document.querySelector("#auditSummary"),
  runBadge: document.querySelector("#runBadge"),
  coverageBadge: document.querySelector("#coverageBadge"),
  kpiRows: document.querySelector("#kpiRows"),
  breakdown: document.querySelector("#auditBreakdown"),
  stack: document.querySelector("#exceptionStack"),
  worked: document.querySelector("#workedExample"),
  search: document.querySelector("#auditSearch"),
};

let report = null;
let query = "";

const percent = (value) => `${Number(value ?? 0).toFixed(1)}%`;
const titleize = (value) => String(value ?? "").replaceAll("_", " ");
const number = (value) => Number(value ?? 0).toLocaleString("en-IN");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown date";
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function badge(value) {
  return `<span class="badge ${String(value ?? "").toLowerCase()}">${titleize(value)}</span>`;
}

async function init() {
  try {
    const response = await fetch(`${REPORT_URL}?t=${Date.now()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    report = await response.json();
    render();
  } catch (error) {
    els.subline.textContent = `Could not load report: ${error.message}`;
  }
}

function render() {
  els.subline.textContent = `Run ${report.run_id} generated ${formatDate(report.generated_at)}`;
  els.runBadge.textContent = report.run_id;
  renderSummary();
  renderKpis();
  renderBreakdown();
  renderExceptions();
  renderWorkedExample();
}

function renderSummary() {
  const items = [
    ["Total records", number(report.total_records), "Full synthetic batch"],
    ["Matched", number(report.matched_count), `${percent(report.match_rate_pct)} auto-match`],
    ["Review required", number(report.review_required_count), `${percent(report.review_required_rate_pct)} held for review`],
    ["Unresolved", number(report.exception_count), `${percent(report.exception_rate_pct)} exceptions`],
  ];

  els.summary.innerHTML = items
    .map(([label, value, detail]) => `
      <article class="metric">
        <span>${label}</span>
        <strong>${value}</strong>
        <small>${detail}</small>
      </article>
    `)
    .join("");
}

function renderKpis() {
  const rows = [
    ["Total Records", number(report.total_records), "-", "Batch processed end to end"],
    ["MATCHED", `${number(report.matched_count)} (${percent(report.match_rate_pct)})`, number(report.ground_truth_matched), "Clean auto-reconciliation"],
    ["REVIEW_REQUIRED", `${number(report.review_required_count)} (${percent(report.review_required_rate_pct)})`, number(report.ground_truth_review), "Human sign-off queue"],
    ["UNMATCHED", `${number(report.exception_count)} (${percent(report.exception_rate_pct)})`, number(report.ground_truth_unmatched), "Unresolved exceptions"],
    ["Precision", percent((report.precision ?? 0) * 100), "-", "False auto-match guardrail"],
    ["Recall", percent((report.recall ?? 0) * 100), "-", "Coverage against known truth"],
    ["False-Match Rate", percent((report.false_match_rate ?? 0) * 100), "-", "Should stay near zero"],
    ["Avg Confidence", Number(report.avg_confidence_matched ?? 0).toFixed(3), "-", "Matched record confidence"],
  ];

  els.kpiRows.innerHTML = rows
    .map(([metric, agent, truth, signal]) => `
      <tr>
        <td>${metric}</td>
        <td><strong>${agent}</strong></td>
        <td>${truth}</td>
        <td class="reason-cell">${signal}</td>
      </tr>
    `)
    .join("");
}

function renderBreakdown() {
  const counts = new Map();
  let covered = 0;
  for (const item of report.exceptions || []) {
    counts.set(item.break_type, (counts.get(item.break_type) || 0) + 1);
    if (item.root_cause_hypothesis) covered += 1;
  }

  const total = report.exceptions?.length || 0;
  const coverage = total ? (covered / total) * 100 : 0;
  els.coverageBadge.textContent = `${percent(coverage)} covered`;

  els.breakdown.innerHTML = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([type, count]) => `
      <button class="break-card" type="button" data-type="${escapeHtml(type)}">
        <span>${titleize(type)}</span>
        <strong>${count}</strong>
        <small>${percent((count / Math.max(total, 1)) * 100)} of classified cases</small>
      </button>
    `)
    .join("");
}

function renderExceptions() {
  const rows = (report.exceptions || []).filter((item) => {
    if (!query) return true;
    return JSON.stringify(item).toLowerCase().includes(query);
  });

  if (!rows.length) {
    els.stack.innerHTML = `<div class="empty-state">No exceptions match the current search.</div>`;
    return;
  }

  els.stack.innerHTML = rows
    .map((item) => {
      const evidence = Object.entries(item.evidence || {})
        .map(([key, value]) => `<span>${titleize(key)}: <strong>${escapeHtml(Array.isArray(value) ? value.join(", ") : value)}</strong></span>`)
        .join("");
      return `
        <details class="audit-case">
          <summary>
            <span class="mono">${escapeHtml(item.exception_id)}</span>
            <strong>${escapeHtml(item.txn_id)}</strong>
            ${badge(item.priority)}
            ${badge(item.break_type)}
          </summary>
          <p>${escapeHtml(item.root_cause_hypothesis)}</p>
          <div class="evidence-strip">${evidence}</div>
        </details>
      `;
    })
    .join("");
}

function renderWorkedExample() {
  const item = (report.exceptions || []).find((entry) => entry.break_type === "PARTIAL_REFUND")
    || (report.exceptions || [])[0];
  const match = (report.match_results || []).find((entry) => entry.txn_id === item?.txn_id);

  if (!item) {
    els.worked.innerHTML = `<p>No worked example is available for this run.</p>`;
    return;
  }

  els.worked.innerHTML = `
    <div class="worked-grid">
      <div>
        <span>Transaction</span>
        <strong class="mono">${escapeHtml(item.txn_id)}</strong>
      </div>
      <div>
        <span>Break type</span>
        <strong>${titleize(item.break_type)}</strong>
      </div>
      <div>
        <span>Agent status</span>
        <strong>${titleize(match?.match_status || "UNMATCHED")}</strong>
      </div>
      <div>
        <span>Confidence</span>
        <strong>${Number(match?.confidence_score ?? 0).toFixed(2)}</strong>
      </div>
    </div>
    <p>${escapeHtml(item.root_cause_hypothesis)}</p>
    <pre>${escapeHtml(match?.audit_trail || "No audit trail supplied.")}</pre>
  `;
}

els.search.addEventListener("input", (event) => {
  query = event.target.value.trim().toLowerCase();
  renderExceptions();
});

els.breakdown.addEventListener("click", (event) => {
  const card = event.target.closest("button[data-type]");
  if (!card) return;
  els.search.value = card.dataset.type;
  query = card.dataset.type.toLowerCase();
  renderExceptions();
  document.querySelector("#exceptions").scrollIntoView({ behavior: "smooth", block: "start" });
});

init();

const REPORT_URL = "../output/report.json";

const state = {
  report: null,
  view: "exceptions",
  query: "",
  priority: "ALL",
  breakType: "ALL",
  status: "ALL",
  confidence: "ALL",
  selectedKey: null,
};

const els = {
  runId: document.querySelector("#runId"),
  generatedAt: document.querySelector("#generatedAt"),
  metricsGrid: document.querySelector("#metricsGrid"),
  scoreRing: document.querySelector("#scoreRing"),
  scoreValue: document.querySelector("#scoreValue"),
  scoreSummary: document.querySelector("#scoreSummary"),
  scoreDetail: document.querySelector("#scoreDetail"),
  exceptionTotal: document.querySelector("#exceptionTotal"),
  breakdownBars: document.querySelector("#breakdownBars"),
  searchInput: document.querySelector("#searchInput"),
  priorityFilter: document.querySelector("#priorityFilter"),
  typeFilter: document.querySelector("#typeFilter"),
  tableTitle: document.querySelector("#tableTitle"),
  rowCount: document.querySelector("#rowCount"),
  tableHead: document.querySelector("#tableHead"),
  tableBody: document.querySelector("#tableBody"),
  detailPane: document.querySelector("#detailPane"),
  clearFilters: document.querySelector("#clearFilters"),
  refreshBtn: document.querySelector("#refreshBtn"),
};

const formatPercent = (value) => `${Number(value ?? 0).toFixed(1)}%`;
const formatNumber = (value) => Number(value ?? 0).toLocaleString("en-IN");
const titleize = (value) => String(value ?? "").replaceAll("_", " ");
const rowKey = (row) => row.exception_id || row.txn_id;

function formatDate(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function compact(value, max = 132) {
  const text = String(value ?? "");
  return text.length > max ? `${text.slice(0, max - 1)}...` : text;
}

function badge(value) {
  const key = String(value ?? "").toLowerCase();
  return `<span class="badge ${key}">${titleize(value)}</span>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadReport() {
  setLoading();
  try {
    const response = await fetch(`${REPORT_URL}?t=${Date.now()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.report = await response.json();
    state.selectedKey = null;
    hydrateBreakTypes();
    renderAll();
  } catch (error) {
    renderError(error);
  }
}

function setLoading() {
  els.tableBody.innerHTML = `<tr><td colspan="5" class="empty-state">Loading report...</td></tr>`;
}

function renderError(error) {
  els.tableHead.innerHTML = "";
  els.tableBody.innerHTML = `
    <tr>
      <td class="error-state">
        <strong>Could not load ${REPORT_URL}</strong>
        Serve the repository root with Python's HTTP server, then open /frontend/.
        <div class="mono">${escapeHtml(error.message)}</div>
      </td>
    </tr>
  `;
}

function hydrateBreakTypes() {
  const types = [...new Set((state.report?.exceptions || []).map((item) => item.break_type))].sort();
  els.typeFilter.innerHTML = [
    `<option value="ALL">All break types</option>`,
    ...types.map((type) => `<option value="${escapeHtml(type)}">${titleize(type)}</option>`),
  ].join("");
}

function renderAll() {
  renderHeader();
  renderMetrics();
  renderBreakdown();
  renderTable();
  renderDetail();
}

function renderHeader() {
  const report = state.report;
  els.runId.textContent = report.run_id;
  els.generatedAt.textContent = formatDate(report.generated_at);

  // Agent mode badge — surface prominently so nobody mistakes stub for LLM output
  const agentMode = report.agent_mode || "STUB (heuristic)";
  const isStub = agentMode.toUpperCase().includes("STUB");
  const modeEl = document.querySelector("#agentModeBadge");
  if (modeEl) {
    modeEl.textContent = isStub
      ? `⚠ ${agentMode} — no live LLM calls`
      : `✓ ${agentMode} — live LLM reasoning`;
    modeEl.className = "agent-badge " + (isStub ? "stub" : "llm");
  }
}

function renderMetrics() {
  const report = state.report;
  // exception_count = UNMATCHED only (true exceptions per spec §4)
  // review_and_exception_case_count = full register (UNMATCHED + REVIEW_REQUIRED)
  const registerCount = report.review_and_exception_case_count
    ?? (report.exception_count + report.review_required_count);

  const metrics = [
    ["Total records", formatNumber(report.total_records), `Processed in ${Number(report.elapsed_seconds ?? 0).toFixed(3)}s`],
    ["Matched", formatNumber(report.matched_count), `${formatPercent(report.match_rate_pct)} auto-match`],
    ["Review required", formatNumber(report.review_required_count), `${formatPercent(report.review_required_rate_pct)} held for sign-off`],
    // Tile shows UNMATCHED-only count (12) — the true exception count per spec
    ["Unmatched exceptions", formatNumber(report.exception_count), `${formatPercent(report.exception_rate_pct)} unresolved`],
    // Second tile shows the full register (25 = 12 UNMATCHED + 13 REVIEW_REQUIRED)
    ["Exception & review register", formatNumber(registerCount), `${report.exception_count} unmatched + ${report.review_required_count} review`],
    ["Precision", formatPercent((report.precision ?? 0) * 100), "Ground-truth scored"],
    ["Recall", formatPercent((report.recall ?? 0) * 100), "Synthetic benchmark"],
    ["False match rate", formatPercent((report.false_match_rate ?? 0) * 100), "Force-match guardrail"],
    ["Avg confidence", Number(report.avg_confidence_matched ?? 0).toFixed(3), "Matched records"],
  ];

  els.metricsGrid.innerHTML = metrics
    .map(([label, value, detail]) => `
      <article class="metric">
        <span>${label}</span>
        <strong>${value}</strong>
        <small>${detail}</small>
      </article>
    `)
    .join("");

  const degrees = Math.max(0, Math.min(100, report.match_rate_pct || 0)) * 3.6;
  els.scoreRing.style.setProperty("--score", `${degrees}deg`);
  els.scoreValue.textContent = formatPercent(report.match_rate_pct);
  els.scoreSummary.textContent = `${report.matched_count} of ${report.total_records} records auto-matched`;
  els.scoreDetail.textContent = `${report.review_required_count} review items, ${report.exception_count} unmatched exceptions`;
}

function renderBreakdown() {
  const counts = new Map();
  for (const item of state.report.exceptions || []) {
    counts.set(item.break_type, (counts.get(item.break_type) || 0) + 1);
  }

  const rows = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  const max = Math.max(...rows.map(([, count]) => count), 1);
  const registerTotal = rows.reduce((sum, [, count]) => sum + count, 0);
  // Show the full register count (UNMATCHED + REVIEW_REQUIRED), not just UNMATCHED
  els.exceptionTotal.textContent = `${registerTotal} cases`;
  els.breakdownBars.innerHTML = rows
    .map(([type, count], index) => {
      const colors = ["#2364aa", "#b42318", "#137a4b", "#a85b00", "#0f766e"];
      return `
        <div class="bar-row">
          <span>${titleize(type)}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${(count / max) * 100}%; background:${colors[index % colors.length]}"></div></div>
          <strong>${count}</strong>
        </div>
      `;
    })
    .join("");
}

function getRows() {
  if (!state.report) return [];
  const source = state.view === "exceptions"
    ? state.report.exceptions || []
    : state.report.match_results || [];

  const query = state.query.trim().toLowerCase();
  return source.filter((row) => {
    if (state.view === "exceptions") {
      if (state.priority !== "ALL" && row.priority !== state.priority) return false;
      if (state.breakType !== "ALL" && row.break_type !== state.breakType) return false;
    } else {
      if (state.status !== "ALL" && row.match_status !== state.status) return false;
      if (state.confidence === "EXACT" && Number(row.confidence_score ?? 0) !== 1) return false;
      if (state.confidence === "TOLERANCE" && Number(row.confidence_score ?? 0) !== 0.9) return false;
      if (state.confidence === "AGENT" && Number(row.confidence_score ?? 0) >= 0.9) return false;
    }

    if (!query) return true;
    return JSON.stringify(row).toLowerCase().includes(query);
  });
}

function renderTable() {
  const rows = getRows();
  const isExceptions = state.view === "exceptions";
  const isAudit = state.view === "audit";

  if (isExceptions) {
    // "Exception & Review Register (25 rows)" — not just "Exceptions"
    const report = state.report;
    const registerCount = report
      ? (report.review_and_exception_case_count ?? report.exceptions?.length ?? 0)
      : 0;
    const unmatchedCount = report ? (report.exception_count ?? 0) : 0;
    const reviewCount = report ? (report.review_required_count ?? 0) : 0;
    els.tableTitle.textContent = `Exception & Review Register`;
    els.tableTitle.title =
      `${registerCount} total = ${unmatchedCount} UNMATCHED (exceptions) + ${reviewCount} REVIEW_REQUIRED`;
  } else {
    els.tableTitle.textContent = isAudit ? "Audit trail" : "Match results";
    els.tableTitle.title = "";
  }
  els.rowCount.textContent = `${rows.length} rows`;
  renderFilters();

  els.tableHead.innerHTML = isExceptions
    ? `<tr><th>Exception</th><th>Transaction</th><th>Priority</th><th>Break type</th><th>Root cause</th></tr>`
    : `<tr><th>Transaction</th><th>Status</th><th>Confidence</th><th>Matched against</th><th>Audit trail</th></tr>`;

  if (!rows.length) {
    els.tableBody.innerHTML = `<tr><td colspan="5" class="empty-state">No records match the current view.</td></tr>`;
    return;
  }

  els.tableBody.innerHTML = rows
    .map((row) => {
      const selected = state.selectedKey === rowKey(row) ? " is-selected" : "";
      if (isExceptions) {
        return `
          <tr class="${selected}" data-key="${escapeHtml(rowKey(row))}">
            <td class="mono">${escapeHtml(row.exception_id)}</td>
            <td class="mono">${escapeHtml(row.txn_id)}</td>
            <td>${badge(row.priority)}</td>
            <td>${titleize(row.break_type)}</td>
            <td class="reason-cell">${escapeHtml(compact(row.root_cause_hypothesis))}</td>
          </tr>
        `;
      }

      return `
        <tr class="${selected}" data-key="${escapeHtml(rowKey(row))}">
          <td class="mono">${escapeHtml(row.txn_id)}</td>
          <td>${badge(row.match_status)}</td>
          <td>${Number(row.confidence_score ?? 0).toFixed(2)}</td>
          <td class="mono">${escapeHtml((row.matched_against || []).join(", ") || "-")}</td>
          <td class="reason-cell">${escapeHtml(compact(row.audit_trail, isAudit ? 220 : 132))}</td>
        </tr>
      `;
    })
    .join("");
}

function renderFilters() {
  if (state.view === "exceptions") {
    const priorityOptions = [
      ["ALL", "All"],
      ["HIGH", "High"],
      ["MEDIUM", "Medium"],
      ["LOW", "Low"],
    ];
    els.priorityFilter.setAttribute("aria-label", "Priority filter");
    els.priorityFilter.innerHTML = priorityOptions
      .map(([value, label]) => `<button class="${state.priority === value ? "is-active" : ""}" type="button" data-filter="${value}">${label}</button>`)
      .join("");
    hydrateBreakTypes();
    els.typeFilter.value = state.breakType;
    return;
  }

  const statusOptions = [
    ["ALL", "All"],
    ["MATCHED", "Matched"],
    ["REVIEW_REQUIRED", "Review"],
    ["UNMATCHED", "Unmatched"],
  ];
  els.priorityFilter.setAttribute("aria-label", "Status filter");
  els.priorityFilter.innerHTML = statusOptions
    .map(([value, label]) => `<button class="${state.status === value ? "is-active" : ""}" type="button" data-filter="${value}">${label}</button>`)
    .join("");

  els.typeFilter.innerHTML = `
    <option value="ALL">All confidence</option>
    <option value="EXACT">Exact matches</option>
    <option value="TOLERANCE">Tolerance matches</option>
    <option value="AGENT">Agent decisions</option>
  `;
  els.typeFilter.value = state.confidence;
}

function renderDetail() {
  const rows = state.view === "exceptions"
    ? state.report?.exceptions || []
    : state.report?.match_results || [];
  const row = rows.find((item) => rowKey(item) === state.selectedKey);

  if (!row) {
    els.detailPane.innerHTML = `
      <div class="empty-detail">
        <span>Select a row</span>
        <strong>Decision evidence appears here</strong>
      </div>
    `;
    return;
  }

  if (row.exception_id) renderExceptionDetail(row);
  else renderMatchDetail(row);
}

function renderExceptionDetail(row) {
  const evidenceRows = Object.entries(row.evidence || {})
    .map(([key, value]) => `
      <div class="evidence-row">
        <span>${titleize(key)}</span>
        <span class="mono">${escapeHtml(Array.isArray(value) ? value.join(", ") : value)}</span>
      </div>
    `)
    .join("");

  els.detailPane.innerHTML = `
    <div class="detail-header">
      <span class="mono">${escapeHtml(row.exception_id)}</span>
      <h2>${escapeHtml(row.txn_id)}</h2>
      <div class="detail-meta">
        ${badge(row.priority)}
        ${badge(row.break_type)}
      </div>
    </div>
    <section class="detail-section">
      <h3>Root cause</h3>
      <p>${escapeHtml(row.root_cause_hypothesis)}</p>
    </section>
    <section class="detail-section">
      <h3>Reason codes</h3>
      <p>${escapeHtml((row.reason_codes || []).map(titleize).join(", ") || "None")}</p>
    </section>
    <section class="detail-section">
      <h3>Evidence</h3>
      <div class="evidence-grid">${evidenceRows || "<p>No evidence fields supplied.</p>"}</div>
    </section>
  `;
}

function renderMatchDetail(row) {
  els.detailPane.innerHTML = `
    <div class="detail-header">
      <span class="mono">Match result</span>
      <h2>${escapeHtml(row.txn_id)}</h2>
      <div class="detail-meta">
        ${badge(row.match_status)}
        <span class="badge low">${Number(row.confidence_score ?? 0).toFixed(2)} confidence</span>
      </div>
    </div>
    <section class="detail-section">
      <h3>Matched against</h3>
      <p class="mono">${escapeHtml((row.matched_against || []).join(", ") || "None")}</p>
    </section>
    <section class="detail-section">
      <h3>Audit trail</h3>
      <p>${escapeHtml(row.audit_trail || "No audit trail supplied.")}</p>
    </section>
  `;
}

document.querySelectorAll(".nav-tab").forEach((button) => {
  button.addEventListener("click", () => {
    state.view = button.dataset.view;
    state.selectedKey = null;
    document.querySelectorAll(".nav-tab").forEach((tab) => tab.classList.toggle("is-active", tab === button));
    renderTable();
    renderDetail();
  });
});

els.tableBody.addEventListener("click", (event) => {
  const row = event.target.closest("tr[data-key]");
  if (!row) return;
  state.selectedKey = row.dataset.key;
  renderTable();
  renderDetail();
});

els.searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  renderTable();
});

els.priorityFilter.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-filter]");
  if (!button) return;
  if (state.view === "exceptions") {
    state.priority = button.dataset.filter;
  } else {
    state.status = button.dataset.filter;
  }
  els.priorityFilter.querySelectorAll("button").forEach((item) => {
    item.classList.toggle("is-active", item === button);
  });
  renderTable();
});

els.typeFilter.addEventListener("change", (event) => {
  if (state.view === "exceptions") {
    state.breakType = event.target.value;
  } else {
    state.confidence = event.target.value;
  }
  renderTable();
});

els.clearFilters.addEventListener("click", () => {
  state.query = "";
  state.priority = "ALL";
  state.breakType = "ALL";
  state.status = "ALL";
  state.confidence = "ALL";
  els.searchInput.value = "";
  renderTable();
});

els.refreshBtn.addEventListener("click", loadReport);

loadReport();

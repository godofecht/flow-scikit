// Timing-unit compatibility and presentation helpers for the benchmark page.
//
// The committed historical BENCH dataset stores sklearn perf_counter durations
// in seconds even though the fields are named *_ms. Pages deployment runs
// benchmarks/normalize_published_timings.py, which converts those literals to
// milliseconds before publishing. When the docs are opened directly from a
// checkout, however, the legacy second-valued literals are still present.
//
// Therefore this browser compatibility layer must be idempotent: normalize a
// legacy checkout exactly once, but never multiply an already-normalized Pages
// build by another 1000x.

(function ensureBenchmarkMilliseconds() {
  const datasets = [BENCH.iris, BENCH.digits, BENCH.diabetes];
  const rows = datasets.flat();

  // In the committed legacy dataset every sklearn total is < 1 because those
  // values are seconds; after normalization the same dataset has values up to
  // hundreds of milliseconds. This discriminator is deliberately scoped to
  // the historical 19-row dataset and should disappear once generated
  // benchmark artifacts replace the legacy literals (#175/#176).
  const maxSkTotal = Math.max(...rows.map(row => row.sk_ms));
  const legacySeconds = maxSkTotal > 0 && maxSkTotal < 1;

  if (!legacySeconds) return;

  for (const row of rows) {
    row.sk_ms *= 1000.0;
    row.sk_fit *= 1000.0;
    row.sk_pred *= 1000.0;
  }
})();

function formatPythonResolution(value) {
  return value === 0 ? "<0.5" : value.toFixed(2);
}

document.addEventListener("DOMContentLoaded", () => {
  const accuracyRows = [
    ...BENCH.iris,
    ...BENCH.digits,
    ...BENCH.diabetes
  ];

  const accuracyTableRows = document.querySelectorAll("#accuracy-table-body tr");
  accuracyRows.forEach((row, i) => {
    const cells = accuracyTableRows[i] && accuracyTableRows[i].children;
    if (!cells) return;
    cells[6].textContent = formatPythonResolution(row.sk_fit);
    cells[8].textContent = formatPythonResolution(row.sk_pred);
  });

  const timeTableRows = document.querySelectorAll("#time-table-body tr");
  accuracyRows.forEach((row, i) => {
    const cells = timeTableRows[i] && timeTableRows[i].children;
    if (!cells) return;
    cells[2].textContent = formatPythonResolution(row.sk_ms);
  });

  // Digits was previously omitted from the timing charts despite being the
  // largest benchmark dataset on the page.
  if (document.getElementById("digits-time-chart")) {
    logBarChart("digits-time-chart", BENCH.digits, { height: 380 });
  }
});

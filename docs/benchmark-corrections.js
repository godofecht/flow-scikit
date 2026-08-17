// Timing-unit correction and presentation helpers for the benchmark page.
// bench_sklearn.py records perf_counter durations in seconds.
// bench_flow.flow records durations in milliseconds via elapsed_ms().
// The historical BENCH table copied the Python second values into fields
// named *_ms. Convert them exactly once before the page renders.

(function correctBenchmarkUnits() {
  const datasets = [BENCH.iris, BENCH.digits, BENCH.diabetes];

  for (const rows of datasets) {
    for (const row of rows) {
      row.sk_ms *= 1000.0;
      row.sk_fit *= 1000.0;
      row.sk_pred *= 1000.0;
    }
  }
})();

function formatPythonResolution(value) {
  return value === 0 ? "<0.5" : value.toFixed(2);
}

document.addEventListener("DOMContentLoaded", () => {
  // The original renderer is registered first, so this executes after its
  // tables/charts are populated with the corrected BENCH values.
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

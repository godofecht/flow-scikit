// flow-scikit benchmark data and SVG chart rendering.
// All data measured on the same arm64 macOS machine with seed=42, 80/20 split.

const BENCH = {
  iris: [
    { algo: "LogisticRegression",  sk_score: 0.9333, fl_score: 0.8333, sk_ms: 0.86,  fl_ms: 0.01 },
    { algo: "LinearSVC",            sk_score: 0.9000, fl_score: 0.7000, sk_ms: 2.35,  fl_ms: 0.44 },
    { algo: "KernelSVC_RBF",        sk_score: 0.9333, fl_score: 0.8000, sk_ms: 1.47,  fl_ms: 16.26 },
    { algo: "DecisionTree",         sk_score: 0.9333, fl_score: 0.9333, sk_ms: 1.87,  fl_ms: 1.15 },
    { algo: "RandomForest",         sk_score: 0.9667, fl_score: 0.9333, sk_ms: 10.11, fl_ms: 10.17 },
    { algo: "GaussianNB",           sk_score: 0.9667, fl_score: 0.9333, sk_ms: 0.86,  fl_ms: 0.01 },
    { algo: "KMeans",               sk_score: 0.1000, fl_score: 0.8000, sk_ms: 46.87, fl_ms: 0.04 },
    { algo: "PCA",                  sk_score: 0.7268, fl_score: 0.7292, sk_ms: 7.76,  fl_ms: 0.05, metric: "explained_var" }
  ],
  digits: [
    { algo: "LogisticRegression",  sk_score: 0.9722, fl_score: 0.9415, sk_ms: 16.73,  fl_ms: 495.13 },
    { algo: "LinearSVC",            sk_score: 0.9556, fl_score: 0.6462, sk_ms: 527.05, fl_ms: 535.22 },
    { algo: "DecisionTree",         sk_score: 0.8139, fl_score: 0.8691, sk_ms: 19.80,  fl_ms: 6431.50 },
    { algo: "RandomForest",         sk_score: 0.9361, fl_score: 0.9081, sk_ms: 32.09,  fl_ms: 46919.86 },
    { algo: "GaussianNB",           sk_score: 0.7417, fl_score: 0.7772, sk_ms: 2.09,   fl_ms: 1.99 },
    { algo: "KMeans",               sk_score: 0.1167, fl_score: 0.6295, sk_ms: 87.94,  fl_ms: 13.85 }
  ],
  diabetes: [
    { algo: "Ridge",                sk_score: 0.4541, fl_score: 0.1489, sk_ms: 5.51,  fl_ms: 0.02 },
    { algo: "Lasso",                sk_score: 0.4555, fl_score: 0.1497, sk_ms: 2.34,  fl_ms: 0.39 },
    { algo: "LinearRegression",     sk_score: 0.4526, fl_score: 0.1482, sk_ms: 10.48, fl_ms: 0.02 },
    { algo: "KernelRidge_RBF",      sk_score: 0.4619, fl_score: 0.1811, sk_ms: 46.00, fl_ms: 9.77 }
  ],
  iris_combo: [
    { algo: "GaussianNB",      sk_acc: 0.9667, fl_acc: 0.9333, sk_train: 1.04,  fl_train: 0.03 },
    { algo: "DecisionTree",    sk_acc: 0.9333, fl_acc: 0.9333, sk_train: 1.81,  fl_train: 1.38 },
    { algo: "KNN_k5",          sk_acc: 0.9333, fl_acc: 0.9667, sk_train: 1.84,  fl_train: 0.03 },
    { algo: "LinearSVC_OVR",   sk_acc: 0.9000, fl_acc: 0.7000, sk_train: 2.13,  fl_train: 0.48 },
    { algo: "RandomForest_10", sk_acc: 0.9667, fl_acc: 0.9333, sk_train: 8.42,  fl_train: 11.72 }
  ]
};

const COLORS = {
  flow: "#ef8068",
  sklearn: "#5669e8",
  ink: "#101b36",
  line: "#ded8cb",
  grid: "#e8e2d5",
  coral: "#ef8068",
  blue: "#5669e8",
  green: "#2d8a4e",
  red: "#c44a3a",
  muted: "#687493"
};

function el(tag, attrs, text) {
  const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
  if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (text != null) e.textContent = text;
  return e;
}

function clearSvg(id) {
  const svg = document.getElementById(id);
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  return svg;
}

// Grouped bar chart for accuracy comparison.
function groupedBarChart(svgId, data, opts) {
  const svg = clearSvg(svgId);
  const W = 900, H = opts.height || 360;
  const ml = 60, mr = 30, mt = 20, mb = 70;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const n = data.length;
  const groupW = cw / n;
  const barW = groupW * 0.32;
  const gap = groupW * 0.06;
  const yMax = opts.yMax || 1.0;
  const yMin = opts.yMin || 0.0;

  // Grid lines
  for (let i = 0; i <= 5; i++) {
    const y = mt + (ch * i / 5);
    svg.appendChild(el("line", { x1: ml, y1: y, x2: W - mr, y2: y, stroke: COLORS.grid, "stroke-width": 1 }));
    const val = yMax - (yMax - yMin) * i / 5;
    svg.appendChild(el("text", { x: ml - 8, y: y + 4, "text-anchor": "end", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.muted }, val.toFixed(2)));
  }

  // Bars
  data.forEach((d, i) => {
    const gx = ml + i * groupW + groupW / 2;
    const skH = (d.sk_score - yMin) / (yMax - yMin) * ch;
    const flH = (d.fl_score - yMin) / (yMax - yMin) * ch;
    svg.appendChild(el("rect", { x: gx - barW - gap/2, y: mt + ch - skH, width: barW, height: skH, fill: COLORS.sklearn, rx: 3 }));
    svg.appendChild(el("rect", { x: gx + gap/2, y: mt + ch - flH, width: barW, height: flH, fill: COLORS.flow, rx: 3 }));

    // Value labels
    svg.appendChild(el("text", { x: gx - barW/2 - gap/2, y: mt + ch - skH - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.sklearn }, d.sk_score.toFixed(3)));
    svg.appendChild(el("text", { x: gx + barW/2 + gap/2, y: mt + ch - flH - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.flow }, d.fl_score.toFixed(3)));

    // X label
    const label = d.algo.replace(/_/g, " ").length > 14 ? d.algo.substring(0, 12) + ".." : d.algo.replace(/_/g, " ");
    svg.appendChild(el("text", { x: gx, y: mt + ch + 18, "text-anchor": "middle", "font-size": 11, "font-family": "DM Sans, sans-serif", fill: COLORS.ink }, label));
  });

  // Axis
  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
}

// Log-scale grouped bar chart for timing.
function logBarChart(svgId, data, opts) {
  const svg = clearSvg(svgId);
  const W = 900, H = opts.height || 360;
  const ml = 70, mr = 30, mt = 20, mb = 70;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const n = data.length;
  const groupW = cw / n;
  const barW = groupW * 0.32;
  const gap = groupW * 0.06;

  const logMin = -2; // 0.01 ms
  const logMax = 5;  // 100000 ms
  const logRange = logMax - logMin;

  function msToY(ms) {
    const l = Math.log10(Math.max(ms, 0.01));
    return mt + ch - ((l - logMin) / logRange) * ch;
  }

  // Grid lines at decades
  for (let i = 0; i <= logRange; i++) {
    const y = mt + ch - (i / logRange) * ch;
    svg.appendChild(el("line", { x1: ml, y1: y, x2: W - mr, y2: y, stroke: COLORS.grid, "stroke-width": 1 }));
    const val = Math.pow(10, logMin + i);
    let label;
    if (val < 1) label = val.toFixed(2);
    else if (val < 1000) label = val.toFixed(0);
    else label = (val / 1000).toFixed(0) + "k";
    svg.appendChild(el("text", { x: ml - 8, y: y + 4, "text-anchor": "end", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.muted }, label + "ms"));
  }

  data.forEach((d, i) => {
    const gx = ml + i * groupW + groupW / 2;
    const skY = msToY(d.sk_ms);
    const flY = msToY(d.fl_ms);
    const baseY = mt + ch;
    svg.appendChild(el("rect", { x: gx - barW - gap/2, y: skY, width: barW, height: baseY - skY, fill: COLORS.sklearn, rx: 3 }));
    svg.appendChild(el("rect", { x: gx + gap/2, y: flY, width: barW, height: baseY - flY, fill: COLORS.flow, rx: 3 }));

    // Value labels
    const skLabel = d.sk_ms < 1 ? d.sk_ms.toFixed(2) : d.sk_ms < 100 ? d.sk_ms.toFixed(1) : d.sk_ms.toFixed(0);
    const flLabel = d.fl_ms < 1 ? d.fl_ms.toFixed(2) : d.fl_ms < 100 ? d.fl_ms.toFixed(1) : d.fl_ms.toFixed(0);
    svg.appendChild(el("text", { x: gx - barW/2 - gap/2, y: skY - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.sklearn }, skLabel));
    svg.appendChild(el("text", { x: gx + barW/2 + gap/2, y: flY - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.flow }, flLabel));

    // X label
    const label = d.algo.replace(/_/g, " ").length > 14 ? d.algo.substring(0, 12) + ".." : d.algo.replace(/_/g, " ");
    svg.appendChild(el("text", { x: gx, y: mt + ch + 18, "text-anchor": "middle", "font-size": 11, "font-family": "DM Sans, sans-serif", fill: COLORS.ink }, label));
  });

  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
}

// Linear-scale bar chart for timing (diabetes).
function linearTimeChart(svgId, data) {
  const svg = clearSvg(svgId);
  const W = 900, H = 280;
  const ml = 70, mr = 30, mt = 20, mb = 70;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const n = data.length;
  const groupW = cw / n;
  const barW = groupW * 0.32;
  const gap = groupW * 0.06;
  const yMax = 50;

  for (let i = 0; i <= 5; i++) {
    const y = mt + (ch * i / 5);
    svg.appendChild(el("line", { x1: ml, y1: y, x2: W - mr, y2: y, stroke: COLORS.grid, "stroke-width": 1 }));
    const val = yMax - yMax * i / 5;
    svg.appendChild(el("text", { x: ml - 8, y: y + 4, "text-anchor": "end", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.muted }, val.toFixed(0) + "ms"));
  }

  data.forEach((d, i) => {
    const gx = ml + i * groupW + groupW / 2;
    const skH = Math.min(d.sk_ms, yMax) / yMax * ch;
    const flH = Math.min(d.fl_ms, yMax) / yMax * ch;
    svg.appendChild(el("rect", { x: gx - barW - gap/2, y: mt + ch - skH, width: barW, height: skH, fill: COLORS.sklearn, rx: 3 }));
    svg.appendChild(el("rect", { x: gx + gap/2, y: mt + ch - flH, width: barW, height: flH, fill: COLORS.flow, rx: 3 }));

    const skLabel = d.sk_ms < 1 ? d.sk_ms.toFixed(2) : d.sk_ms.toFixed(1);
    const flLabel = d.fl_ms < 1 ? d.fl_ms.toFixed(2) : d.fl_ms.toFixed(1);
    svg.appendChild(el("text", { x: gx - barW/2 - gap/2, y: mt + ch - skH - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.sklearn }, skLabel));
    svg.appendChild(el("text", { x: gx + barW/2 + gap/2, y: mt + ch - flH - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.flow }, flLabel));

    const label = d.algo.replace(/_/g, " ");
    svg.appendChild(el("text", { x: gx, y: mt + ch + 18, "text-anchor": "middle", "font-size": 11, "font-family": "DM Sans, sans-serif", fill: COLORS.ink }, label));
  });

  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
}

// Startup time chart (2 bars).
function startupChart() {
  const svg = clearSvg("startup-chart");
  const W = 700, H = 200;
  const ml = 80, mr = 40, mt = 30, mb = 50;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const data = [
    { label: "scikit-learn (Flow)", ms: 33, color: COLORS.flow },
    { label: "scikit-learn (Python)", ms: 2160, color: COLORS.sklearn }
  ];
  const yMax = 2400;
  const barW = 120;
  const gap = 80;
  const startX = ml + (cw - (barW * 2 + gap)) / 2;

  for (let i = 0; i <= 4; i++) {
    const y = mt + (ch * i / 4);
    svg.appendChild(el("line", { x1: ml, y1: y, x2: W - mr, y2: y, stroke: COLORS.grid, "stroke-width": 1 }));
    const val = yMax - yMax * i / 4;
    svg.appendChild(el("text", { x: ml - 8, y: y + 4, "text-anchor": "end", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.muted }, val.toFixed(0) + "ms"));
  }

  data.forEach((d, i) => {
    const x = startX + i * (barW + gap);
    const h = d.ms / yMax * ch;
    svg.appendChild(el("rect", { x: x, y: mt + ch - h, width: barW, height: h, fill: d.color, rx: 5 }));
    svg.appendChild(el("text", { x: x + barW/2, y: mt + ch - h - 8, "text-anchor": "middle", "font-size": 14, "font-weight": 600, "font-family": "Fraunces, serif", fill: d.color }, d.ms + " ms"));
    svg.appendChild(el("text", { x: x + barW/2, y: mt + ch + 20, "text-anchor": "middle", "font-size": 13, "font-family": "DM Sans, sans-serif", fill: COLORS.ink }, d.label));
  });

  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
}

// Combo chart: accuracy bars + time dots for iris side-by-side.
function irisComboChart() {
  const svg = clearSvg("iris-combo-chart");
  const W = 900, H = 380;
  const ml = 60, mr = 70, mt = 30, mb = 70;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const data = BENCH.iris_combo;
  const n = data.length;
  const groupW = cw / n;
  const barW = groupW * 0.28;
  const gap = groupW * 0.04;

  // Left axis: accuracy (0 to 1)
  for (let i = 0; i <= 5; i++) {
    const y = mt + (ch * i / 5);
    svg.appendChild(el("line", { x1: ml, y1: y, x2: W - mr, y2: y, stroke: COLORS.grid, "stroke-width": 1 }));
    const val = 1.0 - 0.2 * i;
    svg.appendChild(el("text", { x: ml - 8, y: y + 4, "text-anchor": "end", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.sklearn }, val.toFixed(1)));
  }
  // Right axis: time (log scale, 0.01 to 100)
  const logMin = -2, logMax = 2;
  for (let i = 0; i <= 4; i++) {
    const val = Math.pow(10, logMax - (logMax - logMin) * i / 4);
    const y = mt + (ch * i / 4);
    svg.appendChild(el("text", { x: W - mr + 8, y: y + 4, "text-anchor": "start", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.flow }, val < 1 ? val.toFixed(2) + "ms" : val.toFixed(0) + "ms"));
  }

  function accY(v) { return mt + ch - v * ch; }
  function timeY(ms) {
    const l = Math.log10(Math.max(ms, 0.01));
    return mt + ch - ((l - logMin) / (logMax - logMin)) * ch;
  }

  data.forEach((d, i) => {
    const gx = ml + i * groupW + groupW / 2;

    // Accuracy bars
    const skH = d.sk_acc * ch;
    const flH = d.fl_acc * ch;
    svg.appendChild(el("rect", { x: gx - barW - gap/2, y: mt + ch - skH, width: barW, height: skH, fill: COLORS.sklearn, rx: 3, opacity: 0.85 }));
    svg.appendChild(el("rect", { x: gx + gap/2, y: mt + ch - flH, width: barW, height: flH, fill: COLORS.flow, rx: 3, opacity: 0.85 }));

    // Time dots
    const skTY = timeY(d.sk_train);
    const flTY = timeY(d.fl_train);
    svg.appendChild(el("circle", { cx: gx - barW/2 - gap/2, cy: skTY, r: 6, fill: "none", stroke: COLORS.sklearn, "stroke-width": 2 }));
    svg.appendChild(el("circle", { cx: gx + barW/2 + gap/2, cy: flTY, r: 6, fill: "none", stroke: COLORS.flow, "stroke-width": 2 }));

    // Accuracy labels
    svg.appendChild(el("text", { x: gx - barW/2 - gap/2, y: mt + ch - skH - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.sklearn }, (d.sk_acc * 100).toFixed(1) + "%"));
    svg.appendChild(el("text", { x: gx + barW/2 + gap/2, y: mt + ch - flH - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.flow }, (d.fl_acc * 100).toFixed(1) + "%"));

    // X label
    const label = d.algo.replace(/_/g, " ");
    svg.appendChild(el("text", { x: gx, y: mt + ch + 18, "text-anchor": "middle", "font-size": 11, "font-family": "DM Sans, sans-serif", fill: COLORS.ink }, label));
  });

  // Axis lines
  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
  // Axis labels
  svg.appendChild(el("text", { x: ml - 50, y: mt - 8, "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.sklearn }, "accuracy"));
  svg.appendChild(el("text", { x: W - mr + 8, y: mt - 8, "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.flow }, "train ms"));
}

// Build accuracy table.
function buildAccuracyTable() {
  const tbody = document.getElementById("accuracy-table-body");
  const all = [
    ...BENCH.iris.map(d => ({ ...d, dataset: "iris", metric: d.metric === "explained_var" ? "explained_var" : "accuracy" })),
    ...BENCH.digits.map(d => ({ ...d, dataset: "digits", metric: "accuracy" })),
    ...BENCH.diabetes.map(d => ({ ...d, dataset: "diabetes", metric: "r2" }))
  ];
  all.forEach(d => {
    const diff = d.fl_score - d.sk_score;
    const cls = diff > 0.001 ? "pos" : diff < -0.001 ? "neg" : "neutral";
    const sign = diff > 0 ? "+" : "";
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${d.algo.replace(/_/g, " ")}</td><td>${d.dataset}</td><td>${d.metric}</td><td class="num">${d.sk_score.toFixed(4)}</td><td class="num">${d.fl_score.toFixed(4)}</td><td class="num ${cls}">${sign}${diff.toFixed(4)}</td>`;
    tbody.appendChild(tr);
  });
}

// Build time table.
function buildTimeTable() {
  const tbody = document.getElementById("time-table-body");
  const all = [
    ...BENCH.iris.map(d => ({ ...d, dataset: "iris" })),
    ...BENCH.digits.map(d => ({ ...d, dataset: "digits" })),
    ...BENCH.diabetes.map(d => ({ ...d, dataset: "diabetes" }))
  ];
  all.forEach(d => {
    const skTotal = d.sk_ms;
    const flTotal = d.fl_ms;
    const speedup = skTotal / flTotal;
    const speedupStr = speedup > 100 ? speedup.toFixed(0) + "x" : speedup > 1 ? speedup.toFixed(1) + "x" : speedup.toFixed(2) + "x";
    const cls = speedup > 1 ? "pos" : "neg";
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${d.algo.replace(/_/g, " ")}</td><td>${d.dataset}</td><td class="num">${skTotal.toFixed(2)}</td><td class="num">${flTotal.toFixed(2)}</td><td class="num ${cls}">${speedupStr}</td>`;
    tbody.appendChild(tr);
  });
}

// Render everything on load.
document.addEventListener("DOMContentLoaded", () => {
  startupChart();
  groupedBarChart("iris-accuracy-chart", BENCH.iris, { yMax: 1.0, yMin: 0.0, height: 360 });
  groupedBarChart("digits-accuracy-chart", BENCH.digits, { yMax: 1.0, yMin: 0.0, height: 360 });
  groupedBarChart("diabetes-r2-chart", BENCH.diabetes, { yMax: 0.5, yMin: 0.0, height: 280 });
  logBarChart("iris-time-chart", BENCH.iris, { height: 360 });
  linearTimeChart("diabetes-time-chart", BENCH.diabetes);
  irisComboChart();
  buildAccuracyTable();
  buildTimeTable();
});

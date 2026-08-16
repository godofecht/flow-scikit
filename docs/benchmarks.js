// flow-scikit benchmark data and SVG chart rendering.
// All data measured with seed=42, 80/20 split, xorshift32 PRNG.
// Flow builds use -O3 -march=native, BLAS (Accelerate), SMO for kernel SVM,
// and LBFGS for logistic regression.

const BENCH = {
  iris: [
    { algo: "LogisticRegression",  sk_score: 0.9333, fl_score: 0.9333, sk_ms: 0.004,  fl_ms: 0.095, sk_fit: 0.004,  fl_fit: 0.093, sk_pred: 0.000, fl_pred: 0.002 },
    { algo: "LinearSVC",            sk_score: 0.9000, fl_score: 0.9000, sk_ms: 0.001,  fl_ms: 0.100, sk_fit: 0.001,  fl_fit: 0.099, sk_pred: 0.000, fl_pred: 0.001 },
    { algo: "KernelSVC_RBF",        sk_score: 0.9333, fl_score: 1.0000, sk_ms: 0.001,  fl_ms: 0.549, sk_fit: 0.001,  fl_fit: 0.511, sk_pred: 0.000, fl_pred: 0.038 },
    { algo: "DecisionTree",         sk_score: 0.9333, fl_score: 0.9333, sk_ms: 0.001,  fl_ms: 0.082, sk_fit: 0.001,  fl_fit: 0.081, sk_pred: 0.000, fl_pred: 0.001 },
    { algo: "RandomForest",         sk_score: 0.9333, fl_score: 0.9333, sk_ms: 0.005,  fl_ms: 0.333, sk_fit: 0.004,  fl_fit: 0.329, sk_pred: 0.000, fl_pred: 0.004 },
    { algo: "GaussianNB",           sk_score: 0.9333, fl_score: 0.9333, sk_ms: 0.000,  fl_ms: 0.019, sk_fit: 0.000,  fl_fit: 0.017, sk_pred: 0.000, fl_pred: 0.002 },
    { algo: "KMeans",               sk_score: 0.8333, fl_score: 0.8333, sk_ms: 0.028,  fl_ms: 0.114, sk_fit: 0.028,  fl_fit: 0.113, sk_pred: 0.000, fl_pred: 0.001 },
    { algo: "PCA",                  sk_score: 0.7262, fl_score: 0.7262, sk_ms: 0.000,  fl_ms: 0.020, sk_fit: 0.000,  fl_fit: 0.020, sk_pred: 0.000, fl_pred: 0.000, metric: "explained_var" }
  ],
  digits: [
    { algo: "LogisticRegression",  sk_score: 0.9749, fl_score: 0.9666, sk_ms: 0.007,  fl_ms: 21.801,  sk_fit: 0.007,  fl_fit: 21.687,  sk_pred: 0.000, fl_pred: 0.114 },
    { algo: "LinearSVC",            sk_score: 0.9694, fl_score: 0.9694, sk_ms: 0.237,  fl_ms: 100.524,  sk_fit: 0.237,  fl_fit: 100.417,  sk_pred: 0.000, fl_pred: 0.107 },
    { algo: "KernelSVC_RBF",        sk_score: 0.9499, fl_score: 0.9443, sk_ms: 0.044,  fl_ms: 173.044,  sk_fit: 0.025,  fl_fit: 160.648,  sk_pred: 0.019, fl_pred: 12.396 },
    { algo: "DecisionTree",         sk_score: 0.8886, fl_score: 0.8802, sk_ms: 0.010,  fl_ms: 15.259,   sk_fit: 0.009,  fl_fit: 15.232,   sk_pred: 0.000, fl_pred: 0.027 },
    { algo: "RandomForest",         sk_score: 0.9666, fl_score: 0.9499, sk_ms: 0.016,  fl_ms: 22.483,    sk_fit: 0.015,  fl_fit: 22.236,    sk_pred: 0.001, fl_pred: 0.247 },
    { algo: "GaussianNB",           sk_score: 0.8134, fl_score: 0.8134, sk_ms: 0.001,  fl_ms: 1.673,     sk_fit: 0.001,  fl_fit: 1.077,     sk_pred: 0.000, fl_pred: 0.596 },
    { algo: "KMeans",               sk_score: 0.6323, fl_score: 0.6267, sk_ms: 0.034,  fl_ms: 103.908,   sk_fit: 0.034,  fl_fit: 103.792,   sk_pred: 0.000, fl_pred: 0.116 }
  ],
  diabetes: [
    { algo: "Ridge",                sk_score: 0.6089, fl_score: 0.6089, sk_ms: 0.001,  fl_ms: 0.032,  sk_fit: 0.001,  fl_fit: 0.032,  sk_pred: 0.000, fl_pred: 0.000 },
    { algo: "Lasso",                sk_score: 0.6084, fl_score: 0.6085, sk_ms: 0.001,  fl_ms: 4.830,  sk_fit: 0.001,  fl_fit: 4.829,  sk_pred: 0.000, fl_pred: 0.001 },
    { algo: "LinearRegression",     sk_score: 0.6108, fl_score: 0.6108, sk_ms: 0.001,  fl_ms: 0.040,  sk_fit: 0.001,  fl_fit: 0.040,  sk_pred: 0.000, fl_pred: 0.000 },
    { algo: "KernelRidge_RBF",      sk_score: 0.4173, fl_score: 0.4173, sk_ms: 0.021,  fl_ms: 8.562,  sk_fit: 0.020,  fl_fit: 7.787,  sk_pred: 0.000, fl_pred: 0.775 }
  ],
  iris_combo: [
    { algo: "GaussianNB",      sk_acc: 0.9333, fl_acc: 0.9333, sk_train: 0.00,  fl_train: 0.01 },
    { algo: "DecisionTree",    sk_acc: 0.9333, fl_acc: 0.9333, sk_train: 0.00,  fl_train: 0.10 },
    { algo: "KNN_k5",          sk_acc: 0.9333, fl_acc: 0.9667, sk_train: 1.84,  fl_train: 0.03 },
    { algo: "LinearSVC_OVR",   sk_acc: 0.9000, fl_acc: 0.9000, sk_train: 0.00,  fl_train: 0.11 },
    { algo: "RandomForest_10", sk_acc: 0.9333, fl_acc: 0.9333, sk_train: 0.01,  fl_train: 0.46 }
  ],
  // Android: scikit-learn (Flow) cross-compiled to aarch64-linux-android,
  // run on the Android emulator (arm64-v8a, Android 15, API 35). Same source,
  // same datasets, same seed. Uses scalar BLAS fallback (no Accelerate).
  // mac_ms is the macOS arm64 Flow time from BENCH above, for comparison.
  android: {
    iris: [
      { algo: "LogisticRegression",  score: 0.9333, mac_ms: 0.12,  and_ms: 0.18 },
      { algo: "LinearSVC",            score: 0.9000, mac_ms: 0.11,  and_ms: 0.20 },
      { algo: "KernelSVC_RBF",        score: 0.9333, mac_ms: 3.31,  and_ms: 4.62 },
      { algo: "DecisionTree",         score: 0.9333, mac_ms: 0.10,  and_ms: 0.41 },
      { algo: "RandomForest",         score: 0.9333, mac_ms: 0.46,  and_ms: 1.37 },
      { algo: "GaussianNB",           score: 0.9333, mac_ms: 0.01,  and_ms: 0.01 },
      { algo: "KMeans",               score: 0.8333, mac_ms: 0.13,  and_ms: 0.16 },
      { algo: "PCA",                  score: 0.7262, mac_ms: 0.02,  and_ms: 0.02 }
    ],
    digits: [
      { algo: "LogisticRegression",  score: 0.9666, mac_ms: 23.91,    and_ms: 175.97 },
      { algo: "LinearSVC",            score: 0.9694, mac_ms: 125.50,   and_ms: 182.62 },
      { algo: "KernelSVC_RBF",        score: 0.9471, mac_ms: 4015.19,  and_ms: 6401.20 },
      { algo: "DecisionTree",         score: 0.8774, mac_ms: 23.10,    and_ms: 26.84 },
      { algo: "RandomForest",         score: 0.9499, mac_ms: 34.18,    and_ms: 46.92 },
      { algo: "GaussianNB",           score: 0.8134, mac_ms: 1.78,     and_ms: 2.66 },
      { algo: "KMeans",               score: 0.6267, mac_ms: 159.63,   and_ms: 183.87 }
    ],
    diabetes: [
      { algo: "Ridge",                score: 0.6089, mac_ms: 0.03,  and_ms: 0.04 },
      { algo: "Lasso",                score: 0.6085, mac_ms: 4.60,  and_ms: 4.50 },
      { algo: "LinearRegression",     score: 0.6108, mac_ms: 0.03,  and_ms: 0.03 },
      { algo: "KernelRidge_RBF",      score: 0.4181, mac_ms: 11.59, and_ms: 13.99 }
    ]
  }
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
  android: "#1f9d76",
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
    const skFit = d.sk_fit != null ? d.sk_fit.toFixed(2) : "N/A";
    const flFit = d.fl_fit != null ? d.fl_fit.toFixed(2) : "N/A";
    const skPred = d.sk_pred != null ? d.sk_pred.toFixed(3) : "N/A";
    const flPred = d.fl_pred != null ? d.fl_pred.toFixed(3) : "N/A";
    const tr = document.createElement("tr");

    const td1 = document.createElement("td");
    td1.textContent = d.algo.replace(/_/g, " ");
    tr.appendChild(td1);

    const td2 = document.createElement("td");
    td2.textContent = d.dataset;
    tr.appendChild(td2);

    const td3 = document.createElement("td");
    td3.textContent = d.metric;
    tr.appendChild(td3);

    const td4 = document.createElement("td");
    td4.className = "num";
    td4.textContent = d.sk_score.toFixed(4);
    tr.appendChild(td4);

    const td5 = document.createElement("td");
    td5.className = "num";
    td5.textContent = d.fl_score.toFixed(4);
    tr.appendChild(td5);

    const td6 = document.createElement("td");
    td6.className = `num ${cls}`;
    td6.textContent = `${sign}${diff.toFixed(4)}`;
    tr.appendChild(td6);

    const td7 = document.createElement("td");
    td7.className = "num";
    td7.textContent = skFit;
    tr.appendChild(td7);

    const td8 = document.createElement("td");
    td8.className = "num";
    td8.textContent = flFit;
    tr.appendChild(td8);

    const td9 = document.createElement("td");
    td9.className = "num";
    td9.textContent = skPred;
    tr.appendChild(td9);

    const td10 = document.createElement("td");
    td10.className = "num";
    td10.textContent = flPred;
    tr.appendChild(td10);

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

    const td1 = document.createElement("td");
    td1.textContent = d.algo.replace(/_/g, " ");
    tr.appendChild(td1);

    const td2 = document.createElement("td");
    td2.textContent = d.dataset;
    tr.appendChild(td2);

    const td3 = document.createElement("td");
    td3.className = "num";
    td3.textContent = skTotal.toFixed(2);
    tr.appendChild(td3);

    const td4 = document.createElement("td");
    td4.className = "num";
    td4.textContent = flTotal.toFixed(2);
    tr.appendChild(td4);

    const td5 = document.createElement("td");
    td5.className = `num ${cls}`;
    td5.textContent = speedupStr;
    tr.appendChild(td5);

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
  paritySpeedupChart();
  buildParityTable();
  androidTimeChart("android-iris-chart", BENCH.android.iris, { height: 320 });
  androidTimeChart("android-digits-chart", BENCH.android.digits, { height: 360 });
  androidTimeChart("android-diabetes-chart", BENCH.android.diabetes, { height: 280 });
  buildAndroidTable();
});

// Per-algorithm parity data.
const PARITY = [
  { algo: "StandardScaler",            match: true,  maxDiff: 0.000001, py_ms: 1.59,  fl_ms: 0.005, speedup: 317.8 },
  { algo: "MinMaxScaler",              match: true,  maxDiff: 0.000001, py_ms: 0.36,  fl_ms: 0.003, speedup: 118.6 },
  { algo: "MaxAbsScaler",              match: true,  maxDiff: 0.000000, py_ms: 0.32,  fl_ms: 0.014, speedup: 23.2 },
  { algo: "GaussianNB",                match: true,  maxDiff: 0.000000, py_ms: 3.81,  fl_ms: 0.019, speedup: 200.3 },
  { algo: "KNNClassifier_k5",          match: true,  maxDiff: 0.000000, py_ms: 8.32,  fl_ms: 0.061, speedup: 136.4 },
  { algo: "NearestCentroid",           match: true,  maxDiff: 0.000000, py_ms: 72.69, fl_ms: 0.003, speedup: 24228.7 },
  { algo: "DummyClassifier_mf",        match: true,  maxDiff: 0.000000, py_ms: 0.29,  fl_ms: 0.014, speedup: 20.8 },
  { algo: "DummyRegressor_mean",       match: true,  maxDiff: 0.000008, py_ms: 0.18,  fl_ms: 0.001, speedup: 178.4 },
  { algo: "PCA_2comp",                 match: true,  maxDiff: 0.000001, py_ms: 5.23,  fl_ms: 0.027, speedup: 193.7 },
  { algo: "LDA",                       match: true,  maxDiff: 0.000000, py_ms: 4.13,  fl_ms: 0.016, speedup: 258.0 },
  { algo: "QDA",                       match: true,  maxDiff: 0.000000, py_ms: 9.63,  fl_ms: 0.007, speedup: 1375.3 },
  { algo: "KMeans_k3",                 match: true,  maxDiff: 0.000000, py_ms: 15.96, fl_ms: 0.023, speedup: 693.8 },
  { algo: "KNNRegressor_k3",           match: true,  maxDiff: 0.000011, py_ms: 1.83,  fl_ms: 0.240, speedup: 7.6 },
  { algo: "LinearRegression",          match: true,  maxDiff: 0.000010, py_ms: 21.15, fl_ms: 0.061, speedup: 346.7 },
  { algo: "Ridge_a1",                  match: true,  maxDiff: 0.000015, py_ms: 12.53, fl_ms: 0.035, speedup: 357.9 },
  { algo: "Lasso_a0.1",                match: true,  maxDiff: 0.003916, py_ms: 5.55,  fl_ms: 0.460, speedup: 12.1 }
];

// Parity speedup bar chart.
function paritySpeedupChart() {
  const svg = clearSvg("parity-speedup-chart");
  const W = 900, H = 480;
  const ml = 80, mr = 30, mt = 20, mb = 90;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const data = PARITY;
  const n = data.length;
  const barW = cw / n * 0.7;
  const gap = cw / n * 0.3;

  // Log scale for speedup
  const logMin = 0;
  const logMax = 5; // 100000x

  function speedupToY(s) {
    if (s <= 1) return mt + ch;
    const l = Math.log10(Math.min(s, 100000));
    return mt + ch - (l / logMax) * ch;
  }

  // Grid lines at decades
  for (let i = 0; i <= 5; i++) {
    const y = mt + ch - (i / 5) * ch;
    svg.appendChild(el("line", { x1: ml, y1: y, x2: W - mr, y2: y, stroke: COLORS.grid, "stroke-width": 1 }));
    const val = Math.pow(10, i);
    svg.appendChild(el("text", { x: ml - 8, y: y + 4, "text-anchor": "end", "font-size": 11, "font-family": "DM Mono, monospace", fill: COLORS.muted }, val >= 1000 ? (val/1000).toFixed(0) + "kx" : val.toFixed(0) + "x"));
  }

  data.forEach((d, i) => {
    const x = ml + i * (barW + gap) + gap / 2;
    const y = speedupToY(d.speedup);
    const color = d.match ? COLORS.green : COLORS.coral;
    svg.appendChild(el("rect", { x: x, y: y, width: barW, height: mt + ch - y, fill: color, rx: 3 }));

    // Speedup label
    const label = d.speedup > 1000 ? (d.speedup/1000).toFixed(1) + "kx" : d.speedup > 10 ? d.speedup.toFixed(0) + "x" : d.speedup.toFixed(1) + "x";
    svg.appendChild(el("text", { x: x + barW/2, y: y - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: color }, label));

    // X label (rotated)
    const shortName = d.algo.length > 16 ? d.algo.substring(0, 14) + ".." : d.algo;
    const text = el("text", { x: x + barW/2, y: mt + ch + 15, "text-anchor": "end", "font-size": 10, "font-family": "DM Sans, sans-serif", fill: COLORS.ink, transform: `rotate(-35, ${x + barW/2}, ${mt + ch + 15})` }, shortName);
    svg.appendChild(text);
  });

  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
}

// Build parity table.
function buildParityTable() {
  const tbody = document.getElementById("parity-table-body");
  PARITY.forEach(d => {
    const matchClass = d.match ? "pos" : "neg";
    const matchText = d.match ? "EXACT" : "DIFF";
    const speedupStr = d.speedup > 1000 ? (d.speedup/1000).toFixed(1) + "kx" : d.speedup > 10 ? d.speedup.toFixed(0) + "x" : d.speedup.toFixed(1) + "x";
    const speedupClass = d.speedup > 1 ? "pos" : "neg";
    const diffStr = d.maxDiff < 0.001 ? d.maxDiff.toFixed(6) : d.maxDiff.toFixed(2);
    const tr = document.createElement("tr");

    const td1 = document.createElement("td");
    td1.textContent = d.algo;
    tr.appendChild(td1);

    const td2 = document.createElement("td");
    td2.textContent = d.match ? "EXACT" : "close";
    tr.appendChild(td2);

    const td3 = document.createElement("td");
    td3.className = matchClass;
    td3.textContent = matchText;
    tr.appendChild(td3);

    const td4 = document.createElement("td");
    td4.className = "num";
    td4.textContent = diffStr;
    tr.appendChild(td4);

    const td5 = document.createElement("td");
    td5.className = "num";
    td5.textContent = d.py_ms.toFixed(4);
    tr.appendChild(td5);

    const td6 = document.createElement("td");
    td6.className = "num";
    td6.textContent = d.fl_ms.toFixed(4);
    tr.appendChild(td6);

    const td7 = document.createElement("td");
    td7.className = `num ${speedupClass}`;
    td7.textContent = speedupStr;
    tr.appendChild(td7);

    tbody.appendChild(tr);
  });
}

// Android: macOS Flow vs Android Flow time, log-scale grouped bars.
function androidTimeChart(svgId, data, opts) {
  const svg = clearSvg(svgId);
  const W = 900, H = opts.height || 320;
  const ml = 70, mr = 30, mt = 20, mb = 70;
  const cw = W - ml - mr;
  const ch = H - mt - mb;
  const n = data.length;
  const groupW = cw / n;
  const barW = groupW * 0.32;
  const gap = groupW * 0.06;

  const logMin = -2, logMax = 4;
  const logRange = logMax - logMin;
  function msToY(ms) {
    const l = Math.log10(Math.max(ms, 0.01));
    return mt + ch - ((l - logMin) / logRange) * ch;
  }

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
    const baseY = mt + ch;
    const flY = msToY(d.and_ms);
    svg.appendChild(el("rect", { x: gx + gap/2, y: flY, width: barW, height: baseY - flY, fill: COLORS.android, rx: 3 }));
    const flLabel = d.and_ms < 1 ? d.and_ms.toFixed(2) : d.and_ms < 100 ? d.and_ms.toFixed(1) : d.and_ms.toFixed(0);
    svg.appendChild(el("text", { x: gx + barW/2 + gap/2, y: flY - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.android }, flLabel));

    if (d.mac_ms != null) {
      const macY = msToY(d.mac_ms);
      svg.appendChild(el("rect", { x: gx - barW - gap/2, y: macY, width: barW, height: baseY - macY, fill: COLORS.flow, rx: 3 }));
      const macLabel = d.mac_ms < 1 ? d.mac_ms.toFixed(2) : d.mac_ms < 100 ? d.mac_ms.toFixed(1) : d.mac_ms.toFixed(0);
      svg.appendChild(el("text", { x: gx - barW/2 - gap/2, y: macY - 5, "text-anchor": "middle", "font-size": 10, "font-family": "DM Mono, monospace", fill: COLORS.flow }, macLabel));
    }

    const label = d.algo.replace(/_/g, " ").length > 14 ? d.algo.substring(0, 12) + ".." : d.algo.replace(/_/g, " ");
    svg.appendChild(el("text", { x: gx, y: mt + ch + 18, "text-anchor": "middle", "font-size": 11, "font-family": "DM Sans, sans-serif", fill: COLORS.ink }, label));
  });

  svg.appendChild(el("line", { x1: ml, y1: mt + ch, x2: W - mr, y2: mt + ch, stroke: COLORS.ink, "stroke-width": 1.5 }));
}

// Android results table.
function buildAndroidTable() {
  const tbody = document.getElementById("android-table-body");
  const all = [
    ...BENCH.android.iris.map(d => ({ ...d, dataset: "iris" })),
    ...BENCH.android.digits.map(d => ({ ...d, dataset: "digits" })),
    ...BENCH.android.diabetes.map(d => ({ ...d, dataset: "diabetes" }))
  ];
  all.forEach(d => {
    const ratio = d.mac_ms != null ? d.mac_ms / d.and_ms : null;
    let ratioStr, ratioCls;
    if (ratio == null) { ratioStr = "-"; ratioCls = "neutral"; }
    else if (ratio > 1) { ratioStr = ratio.toFixed(2) + "x"; ratioCls = "neg"; }
    else { ratioStr = (1 / ratio).toFixed(2) + "x"; ratioCls = "pos"; }
    const tr = document.createElement("tr");

    const td1 = document.createElement("td");
    td1.textContent = d.algo.replace(/_/g, " ");
    tr.appendChild(td1);

    const td2 = document.createElement("td");
    td2.textContent = d.dataset;
    tr.appendChild(td2);

    const td3 = document.createElement("td");
    td3.className = "num";
    td3.textContent = d.score.toFixed(4);
    tr.appendChild(td3);

    const td4 = document.createElement("td");
    td4.className = "num";
    td4.textContent = d.mac_ms != null ? d.mac_ms.toFixed(2) : "-";
    tr.appendChild(td4);

    const td5 = document.createElement("td");
    td5.className = "num";
    td5.textContent = d.and_ms.toFixed(2);
    tr.appendChild(td5);

    const td6 = document.createElement("td");
    td6.className = `num ${ratioCls}`;
    td6.textContent = ratioStr;
    tr.appendChild(td6);

    tbody.appendChild(tr);
  });
}

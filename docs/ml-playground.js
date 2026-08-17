(() => {
  'use strict';

  const palette = ['#6f7bf7', '#56c2d6', '#f28c72', '#b184e8', '#65c58f'];
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];

  function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  }
  function mean(a) { return a.reduce((s, x) => s + x, 0) / Math.max(1, a.length); }
  function variance(a) { const m = mean(a); return mean(a.map(x => (x - m) ** 2)); }
  function sd(a) { return Math.sqrt(variance(a)); }
  function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, x)); }
  function sigmoid(x) { return 1 / (1 + Math.exp(-clamp(x, -30, 30))); }
  function rmse(y, p) { return Math.sqrt(mean(y.map((v, i) => (v - p[i]) ** 2))); }
  function mae(y, p) { return mean(y.map((v, i) => Math.abs(v - p[i]))); }
  function r2(y, p) {
    const m = mean(y), ss = y.reduce((s, v) => s + (v - m) ** 2, 0), er = y.reduce((s, v, i) => s + (v - p[i]) ** 2, 0);
    return ss === 0 ? 0 : 1 - er / ss;
  }
  function accuracy(y, p) { return mean(y.map((v, i) => Number(v === p[i]))); }
  function shuffleIndices(n, seed = 42) {
    const r = rng(seed), a = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  function splitIndices(n, testFraction, seed = 42) {
    const idx = shuffleIndices(n, seed), nTest = Math.max(1, Math.round(n * testFraction));
    return { test: idx.slice(0, nTest), train: idx.slice(nTest) };
  }
  function standardiser(X, rows = null) {
    const use = rows || X.map((_, i) => i), cols = X[0].length;
    const means = [], sds = [];
    for (let j = 0; j < cols; j++) {
      const c = use.map(i => X[i][j]); means[j] = mean(c); sds[j] = sd(c) || 1;
    }
    return { means, sds, transform: row => row.map((v, j) => (v - means[j]) / sds[j]) };
  }
  function dist2(a, b) { return a.reduce((s, v, i) => s + (v - b[i]) ** 2, 0); }
  function knnPredict(trainX, trainY, x, k) {
    const votes = new Map();
    trainX.map((r, i) => [dist2(r, x), trainY[i]]).sort((a, b) => a[0] - b[0]).slice(0, k)
      .forEach(([, y]) => votes.set(y, (votes.get(y) || 0) + 1));
    return [...votes.entries()].sort((a, b) => b[1] - a[1])[0][0];
  }
  function linfit(x, y, lambda = 0) {
    const xm = mean(x), ym = mean(y);
    const num = x.reduce((s, v, i) => s + (v - xm) * (y[i] - ym), 0);
    const den = x.reduce((s, v) => s + (v - xm) ** 2, 0) + lambda;
    const b = den ? num / den : 0, a = ym - b * xm;
    return { a, b, predict: v => a + b * v };
  }
  function softThreshold(x, l) { return Math.sign(x) * Math.max(0, Math.abs(x) - l); }
  function logisticFit(X, y, lambda = 0, steps = 500, lr = 0.08) {
    const d = X[0].length, w = Array(d).fill(0); let b = 0;
    for (let s = 0; s < steps; s++) {
      const gw = Array(d).fill(0); let gb = 0;
      for (let i = 0; i < X.length; i++) {
        const z = b + X[i].reduce((sum, v, j) => sum + v * w[j], 0), e = sigmoid(z) - y[i];
        gb += e; for (let j = 0; j < d; j++) gw[j] += e * X[i][j];
      }
      b -= lr * gb / X.length;
      for (let j = 0; j < d; j++) w[j] -= lr * (gw[j] / X.length + lambda * w[j]);
    }
    return { w, b, prob: x => sigmoid(b + x.reduce((s, v, j) => s + v * w[j], 0)) };
  }
  function confusion(y, p) {
    let tp = 0, tn = 0, fp = 0, fn = 0;
    y.forEach((v, i) => { if (v === 1 && p[i] === 1) tp++; else if (v === 0 && p[i] === 0) tn++; else if (v === 0) fp++; else fn++; });
    return { tp, tn, fp, fn, precision: tp / Math.max(1, tp + fp), recall: tp / Math.max(1, tp + fn), specificity: tn / Math.max(1, tn + fp) };
  }
  function gaussianNBFit(X, y) {
    const classes = [...new Set(y)], stats = new Map();
    classes.forEach(c => {
      const rows = X.filter((_, i) => y[i] === c), cols = X[0].length;
      stats.set(c, { prior: rows.length / X.length, means: Array.from({ length: cols }, (_, j) => mean(rows.map(r => r[j]))), vars: Array.from({ length: cols }, (_, j) => variance(rows.map(r => r[j])) + 1e-6) });
    });
    return x => classes.map(c => {
      const s = stats.get(c); let logp = Math.log(s.prior);
      x.forEach((v, j) => { logp += -0.5 * Math.log(2 * Math.PI * s.vars[j]) - (v - s.means[j]) ** 2 / (2 * s.vars[j]); });
      return [logp, c];
    }).sort((a, b) => b[0] - a[0])[0][1];
  }
  function kmeans(points, k, seed = 7, iterations = 20) {
    const r = rng(seed), centroids = [];
    centroids.push([...points[Math.floor(r() * points.length)]]);
    while (centroids.length < k) {
      const weights = points.map(p => Math.min(...centroids.map(c => dist2(p, c))));
      const total = weights.reduce((a, b) => a + b, 0); let t = r() * total, chosen = 0;
      for (let i = 0; i < weights.length; i++) { t -= weights[i]; if (t <= 0) { chosen = i; break; } }
      centroids.push([...points[chosen]]);
    }
    let labels = Array(points.length).fill(0);
    for (let it = 0; it < iterations; it++) {
      labels = points.map(p => centroids.map(c => dist2(p, c)).indexOf(Math.min(...centroids.map(c => dist2(p, c)))));
      for (let c = 0; c < k; c++) {
        const g = points.filter((_, i) => labels[i] === c);
        if (g.length) centroids[c] = [mean(g.map(p => p[0])), mean(g.map(p => p[1]))];
      }
    }
    const inertia = points.reduce((s, p, i) => s + dist2(p, centroids[labels[i]]), 0);
    return { centroids, labels, inertia };
  }
  function dbscan(points, eps, minPts) {
    const labels = Array(points.length).fill(-99); let cluster = 0;
    const region = i => points.map((p, j) => dist2(points[i], p) <= eps * eps ? j : -1).filter(j => j >= 0);
    for (let i = 0; i < points.length; i++) {
      if (labels[i] !== -99) continue;
      const nbrs = region(i); if (nbrs.length < minPts) { labels[i] = -1; continue; }
      labels[i] = cluster; const seeds = nbrs.filter(j => j !== i);
      for (let q = 0; q < seeds.length; q++) {
        const j = seeds[q]; if (labels[j] === -1) labels[j] = cluster; if (labels[j] !== -99) continue;
        labels[j] = cluster; const n2 = region(j); if (n2.length >= minPts) n2.forEach(v => { if (!seeds.includes(v)) seeds.push(v); });
      }
      cluster++;
    }
    return { labels, clusters: cluster, noise: labels.filter(x => x === -1).length };
  }
  function pca2(points) {
    const mx = mean(points.map(p => p[0])), my = mean(points.map(p => p[1]));
    const a = mean(points.map(p => (p[0] - mx) ** 2)), d = mean(points.map(p => (p[1] - my) ** 2)), b = mean(points.map(p => (p[0] - mx) * (p[1] - my)));
    const tr = a + d, det = a * d - b * b, disc = Math.sqrt(Math.max(0, tr * tr / 4 - det));
    const l1 = tr / 2 + disc, l2 = tr / 2 - disc;
    let v = Math.abs(b) > 1e-9 ? [l1 - d, b] : (a >= d ? [1, 0] : [0, 1]);
    const n = Math.hypot(v[0], v[1]) || 1; v = [v[0] / n, v[1] / n];
    return { centre: [mx, my], axis: v, ratio: l1 / Math.max(1e-9, l1 + l2) };
  }
  function solveLinear(A, b) {
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      [M[i], M[p]] = [M[p], M[i]]; const div = Math.abs(M[i][i]) < 1e-12 ? 1e-12 : M[i][i];
      for (let k = i; k <= n; k++) M[i][k] /= div;
      for (let j = 0; j < n; j++) if (j !== i) { const f = M[j][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    return M.map(r => r[n]);
  }
  function polyfit(x, y, degree, lambda = 1e-6) {
    const d = degree + 1, A = Array.from({ length: d }, () => Array(d).fill(0)), b = Array(d).fill(0);
    for (let i = 0; i < d; i++) for (let j = 0; j < d; j++) A[i][j] = x.reduce((s, v) => s + v ** (i + j), 0) + (i === j ? lambda : 0);
    for (let i = 0; i < d; i++) b[i] = x.reduce((s, v, k) => s + y[k] * v ** i, 0);
    const w = solveLinear(A, b); return v => w.reduce((s, c, i) => s + c * v ** i, 0);
  }

  function canvasBase(canvas) {
    const c = canvas.getContext('2d'), w = canvas.width, h = canvas.height;
    c.clearRect(0, 0, w, h); c.fillStyle = '#0b1428'; c.fillRect(0, 0, w, h);
    c.strokeStyle = '#213251'; c.lineWidth = 1;
    for (let x = 54; x < w - 20; x += 70) { c.beginPath(); c.moveTo(x, 24); c.lineTo(x, h - 36); c.stroke(); }
    for (let y = 42; y < h - 24; y += 52) { c.beginPath(); c.moveTo(34, y); c.lineTo(w - 20, y); c.stroke(); }
    return c;
  }
  function scatter(canvas, pts, labels = null, opts = {}) {
    const c = canvasBase(canvas), w = canvas.width, h = canvas.height;
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const xmin = opts.xmin ?? Math.min(...xs), xmax = opts.xmax ?? Math.max(...xs), ymin = opts.ymin ?? Math.min(...ys), ymax = opts.ymax ?? Math.max(...ys);
    const sx = x => 44 + (x - xmin) / Math.max(1e-9, xmax - xmin) * (w - 72), sy = y => h - 38 - (y - ymin) / Math.max(1e-9, ymax - ymin) * (h - 68);
    pts.forEach((p, i) => { c.fillStyle = labels && labels[i] === -1 ? '#78859e' : palette[((labels?.[i] ?? 0) + palette.length) % palette.length]; c.beginPath(); c.arc(sx(p[0]), sy(p[1]), opts.radius || 4.5, 0, Math.PI * 2); c.fill(); });
    if (opts.line) { c.strokeStyle = '#fff'; c.lineWidth = 3; c.beginPath(); const steps = 100; for (let i = 0; i <= steps; i++) { const x = xmin + (xmax - xmin) * i / steps, y = opts.line(x); if (i === 0) c.moveTo(sx(x), sy(y)); else c.lineTo(sx(x), sy(y)); } c.stroke(); }
    if (opts.vertical != null) { c.strokeStyle = '#f28c72'; c.lineWidth = 3; c.beginPath(); c.moveTo(sx(opts.vertical), 24); c.lineTo(sx(opts.vertical), h - 36); c.stroke(); }
    return { c, sx, sy };
  }
  function bars(canvas, values, labels = null) {
    const c = canvasBase(canvas), w = canvas.width, h = canvas.height, max = Math.max(1e-9, ...values);
    const gap = 12, bw = (w - 80 - gap * (values.length - 1)) / values.length;
    values.forEach((v, i) => { const bh = (h - 90) * v / max; c.fillStyle = palette[i % palette.length]; c.fillRect(40 + i * (bw + gap), h - 42 - bh, bw, bh); if (labels) { c.fillStyle = '#dce7ff'; c.font = '12px ui-monospace, monospace'; c.fillText(labels[i], 40 + i * (bw + gap), h - 20); } });
  }
  function linePlot(canvas, series, opts = {}) {
    const all = series.flatMap(s => s.points), c = canvasBase(canvas), w = canvas.width, h = canvas.height;
    const xmin = opts.xmin ?? Math.min(...all.map(p => p[0])), xmax = opts.xmax ?? Math.max(...all.map(p => p[0])), ymin = opts.ymin ?? Math.min(...all.map(p => p[1])), ymax = opts.ymax ?? Math.max(...all.map(p => p[1]));
    const sx = x => 44 + (x - xmin) / Math.max(1e-9, xmax - xmin) * (w - 72), sy = y => h - 38 - (y - ymin) / Math.max(1e-9, ymax - ymin) * (h - 68);
    series.forEach((s, si) => { c.strokeStyle = palette[si % palette.length]; c.lineWidth = 3; c.beginPath(); s.points.forEach((p, i) => i ? c.lineTo(sx(p[0]), sy(p[1])) : c.moveTo(sx(p[0]), sy(p[1]))); c.stroke(); });
  }
  function heatmap2x2(canvas, m) {
    const c = canvasBase(canvas), vals = [m.tn, m.fp, m.fn, m.tp], max = Math.max(1, ...vals), x0 = 120, y0 = 60, size = 95;
    vals.forEach((v, i) => { const x = x0 + (i % 2) * size, y = y0 + Math.floor(i / 2) * size; c.fillStyle = `rgba(111,123,247,${0.18 + 0.75 * v / max})`; c.fillRect(x, y, size - 6, size - 6); c.fillStyle = '#fff'; c.font = '700 24px ui-monospace, monospace'; c.fillText(String(v), x + 34, y + 52); });
    c.fillStyle = '#b8c6df'; c.font = '13px ui-monospace, monospace'; c.fillText('pred 0', x0 + 15, 40); c.fillText('pred 1', x0 + 110, 40); c.save(); c.translate(82, y0 + 46); c.rotate(-Math.PI / 2); c.fillText('actual 0', 0, 0); c.restore(); c.save(); c.translate(82, y0 + 145); c.rotate(-Math.PI / 2); c.fillText('actual 1', 0, 0); c.restore();
  }

  function irisData() {
    const r = rng(17), centres = [[5.0, 3.45, 1.46, 0.24], [5.94, 2.78, 4.26, 1.33], [6.58, 2.98, 5.55, 2.02]], spread = [[.75,.55,.55,.25],[.9,.55,.85,.45],[1.0,.65,.85,.55]], X = [], y = [];
    centres.forEach((c, cls) => { for (let i = 0; i < 50; i++) { X.push(c.map((v, j) => v + (r() + r() + r() - 1.5) * spread[cls][j])); y.push(cls); } });
    return { X, y };
  }
  function binaryData(seed = 21, n = 180, overlap = 1) {
    const r = rng(seed), X = [], y = [];
    for (let i = 0; i < n; i++) { const cls = i < n / 2 ? 0 : 1, cx = cls ? 1.2 : -1.2, cy = cls ? .8 : -.8; X.push([cx + (r() + r() + r() - 1.5) * overlap * 2, cy + (r() + r() + r() - 1.5) * overlap * 2]); y.push(cls); }
    return { X, y };
  }

  function metricHTML(metrics) {
    return metrics.map(([k, v]) => `<div class="demo-metric"><span>${k}</span><strong>${v}</strong></div>`).join('');
  }
  function chipHTML(items) { return items.map(x => `<span>${x}</span>`).join('<b>→</b>'); }

  function runFlagship() {
    const split = Number($('#iris-test').value) / 100, k = Number($('#iris-k').value), scaleOn = $('#iris-scale').checked;
    $('#iris-test-out').textContent = `${Math.round(split * 100)}%`; $('#iris-k-out').textContent = String(k);
    const { X, y } = irisData(), parts = splitIndices(X.length, split, 91), scaler = standardiser(X, parts.train);
    const TX = parts.train.map(i => scaleOn ? scaler.transform(X[i]) : X[i]);
    const testX = parts.test.map(i => scaleOn ? scaler.transform(X[i]) : X[i]);
    const pred = testX.map(row => knnPredict(TX, parts.train.map(i => y[i]), row, k)), truth = parts.test.map(i => y[i]);
    const acc = accuracy(truth, pred), perClass = [0,1,2].map(c => { const rows = truth.map((v,i)=>[v,pred[i]]).filter(([v])=>v===c); return mean(rows.map(([v,p])=>Number(v===p))); });
    scatter($('#iris-chart'), parts.test.map(i => [X[i][2], X[i][3]]), pred, { radius: 5.5 });
    $('#iris-metrics').innerHTML = metricHTML([['accuracy', `${(acc*100).toFixed(1)}%`], ['train / test', `${parts.train.length} / ${parts.test.length}`], ['class recall', perClass.map(x=>x.toFixed(2)).join(' · ')], ['preprocess', scaleOn ? 'StandardScaler' : 'raw features']]);
    $('#iris-pipeline').innerHTML = chipHTML(['150×4 data', 'inspect', scaleOn ? 'standardise' : 'raw', 'split', `KNN k=${k}`, 'predict', 'accuracy']);
  }

  const demos = [
    { group:'Classification', title:'Logistic regression', question:'Fit a probabilistic classifier and move the regularisation strength.', control:['L2 λ',0,100,8,''], pipeline:['data','scale','fit','probabilities','accuracy'], run(v, canvas){ const d=binaryData(31,180,1.15), p=splitIndices(d.X.length,.3,5), sc=standardiser(d.X,p.train), tr=p.train.map(i=>sc.transform(d.X[i])), te=p.test.map(i=>sc.transform(d.X[i])), m=logisticFit(tr,p.train.map(i=>d.y[i]),v/500,650,.12), probs=te.map(m.prob), pred=probs.map(x=>Number(x>=.5)), truth=p.test.map(i=>d.y[i]); scatter(canvas,p.test.map(i=>d.X[i]),pred); return [['accuracy',accuracy(truth,pred).toFixed(3)],['log loss',(-mean(truth.map((y,i)=>y*Math.log(probs[i]+1e-9)+(1-y)*Math.log(1-probs[i]+1e-9)))).toFixed(3)],['λ',(v/500).toFixed(3)]]; } },
    { group:'Classification', title:'Gaussian Naive Bayes', question:'Watch a generative classifier cope with increasing class overlap.', control:['overlap',40,180,90,'%'], pipeline:['data','class stats','fit','predict','accuracy'], run(v,canvas){ const d=binaryData(41,180,v/100),p=splitIndices(d.X.length,.3,9),fit=gaussianNBFit(p.train.map(i=>d.X[i]),p.train.map(i=>d.y[i])),pred=p.test.map(i=>fit(d.X[i])),truth=p.test.map(i=>d.y[i]);scatter(canvas,p.test.map(i=>d.X[i]),pred);return [['accuracy',accuracy(truth,pred).toFixed(3)],['test rows',truth.length],['overlap',(v/100).toFixed(2)]];} },
    { group:'Classification', title:'KNN decision complexity', question:'Change k and see local decision-making become smoother or noisier.', control:['k',1,19,5,''], step:2, pipeline:['data','scale','neighbors','vote','score'], run(v,canvas){ const d=binaryData(51,180,1.25),p=splitIndices(d.X.length,.3,3),sc=standardiser(d.X,p.train),tr=p.train.map(i=>sc.transform(d.X[i])),pred=p.test.map(i=>knnPredict(tr,p.train.map(j=>d.y[j]),sc.transform(d.X[i]),v)),truth=p.test.map(i=>d.y[i]);scatter(canvas,p.test.map(i=>d.X[i]),pred);return [['accuracy',accuracy(truth,pred).toFixed(3)],['k',v],['errors',truth.filter((y,i)=>y!==pred[i]).length]];} },
    { group:'Classification', title:'Decision threshold', question:'Move a probability threshold and trade recall for precision.', control:['threshold',5,95,50,'%'], pipeline:['fit','probabilities','threshold','confusion','precision/recall'], run(v,canvas){ const d=binaryData(61,220,1.35),sc=standardiser(d.X),m=logisticFit(d.X.map(sc.transform),d.y,.01,600,.1),probs=d.X.map(x=>m.prob(sc.transform(x))),t=v/100,pred=probs.map(x=>Number(x>=t)),cm=confusion(d.y,pred);scatter(canvas,probs.map((p,i)=>[p,d.y[i]+((i%7)-3)*.025]),pred,{vertical:t});return [['precision',cm.precision.toFixed(3)],['recall',cm.recall.toFixed(3)],['threshold',t.toFixed(2)]];} },
    { group:'Diagnostics', title:'Confusion matrix', question:'Inspect exactly which errors a classifier is making.', control:['threshold',10,90,50,'%'], pipeline:['predictions','confusion matrix','precision','recall'], run(v,canvas){ const d=binaryData(71,220,1.35),sc=standardiser(d.X),m=logisticFit(d.X.map(sc.transform),d.y,.01),probs=d.X.map(x=>m.prob(sc.transform(x))),pred=probs.map(x=>Number(x>=v/100)),cm=confusion(d.y,pred);heatmap2x2(canvas,cm);return [['TP / TN',`${cm.tp} / ${cm.tn}`],['FP / FN',`${cm.fp} / ${cm.fn}`],['accuracy',accuracy(d.y,pred).toFixed(3)]];} },
    { group:'Diagnostics', title:'ROC curve', question:'Trace sensitivity against false-positive rate across all thresholds.', control:['separation',40,180,100,'%'], pipeline:['scores','threshold sweep','TPR/FPR','AUC'], run(v,canvas){ const d=binaryData(81,240,v/100),sc=standardiser(d.X),m=logisticFit(d.X.map(sc.transform),d.y,.01),probs=d.X.map(x=>m.prob(sc.transform(x))),pts=[];for(let t=0;t<=1;t+=.04){const cm=confusion(d.y,probs.map(x=>Number(x>=t)));pts.push([1-cm.specificity,cm.recall]);}pts.sort((a,b)=>a[0]-b[0]);let auc=0;for(let i=1;i<pts.length;i++)auc+=(pts[i][0]-pts[i-1][0])*(pts[i][1]+pts[i-1][1])/2;linePlot(canvas,[{points:pts}],{xmin:0,xmax:1,ymin:0,ymax:1});return [['AUC',auc.toFixed(3)],['thresholds',pts.length],['separation',(v/100).toFixed(2)]];} },
    { group:'Regression', title:'Linear regression + residuals', question:'Fit a straight line and quantify the unexplained error.', control:['noise',0,100,25,'%'], pipeline:['data','fit','predict','residuals','R²/RMSE'], run(v,canvas){ const r=rng(101),x=Array.from({length:90},(_,i)=>i/9),y=x.map(t=>2.4*t+4+(r()+r()-1)*v/7),m=linfit(x,y),p=x.map(m.predict);scatter(canvas,x.map((t,i)=>[t,y[i]]),null,{line:m.predict});return [['R²',r2(y,p).toFixed(3)],['RMSE',rmse(y,p).toFixed(2)],['slope',m.b.toFixed(2)]];} },
    { group:'Regression', title:'Ridge regression', question:'Shrink a noisy coefficient with L2 regularisation.', control:['λ',0,200,20,''], pipeline:['data','standardise','ridge fit','predict','R²'], run(v,canvas){ const r=rng(111),x=Array.from({length:90},(_,i)=>i/9),y=x.map(t=>3.1*t+1+(r()+r()-1)*4),m=linfit(x,y,v),p=x.map(m.predict);scatter(canvas,x.map((t,i)=>[t,y[i]]),null,{line:m.predict});return [['R²',r2(y,p).toFixed(3)],['coefficient',m.b.toFixed(2)],['λ',v]];} },
    { group:'Regression', title:'Lasso sparsity', question:'Use L1 shrinkage to drive a weak coefficient exactly to zero.', control:['L1 λ',0,100,18,'%'], pipeline:['features','fit','soft threshold','predict','sparsity'], run(v,canvas){ const r=rng(121),x=Array.from({length:100},(_,i)=>i/10-5),y=x.map(t=>.55*t+(r()+r()-1)*3),base=linfit(x,y),b=softThreshold(base.b,v/100),a=mean(y)-b*mean(x),f=t=>a+b*t,p=x.map(f);scatter(canvas,x.map((t,i)=>[t,y[i]]),null,{line:f});return [['coefficient',b.toFixed(3)],['zero?',Math.abs(b)<1e-9?'yes':'no'],['MAE',mae(y,p).toFixed(2)]];} },
    { group:'Regression', title:'Polynomial bias–variance', question:'Increase polynomial degree until the model starts fitting noise.', control:['degree',1,10,3,''], pipeline:['data','basis expansion','fit','predict','generalisation'], run(v,canvas){ const r=rng(131),x=Array.from({length:45},(_,i)=>-1+i*2/44),y=x.map(t=>Math.sin(3*t)+(r()+r()-1)*.3),f=polyfit(x,y,v,1e-5);scatter(canvas,x.map((t,i)=>[t,y[i]]),null,{line:f,xmin:-1,xmax:1,ymin:-1.6,ymax:1.6});const p=x.map(f);return [['degree',v],['train RMSE',rmse(y,p).toFixed(3)],['flexibility',v<3?'high bias':v>7?'high variance':'balanced']];} },
    { group:'Regression', title:'Outlier sensitivity', question:'Inject extreme points and watch ordinary least squares move.', control:['outliers',0,15,4,''], pipeline:['data','inject outliers','OLS fit','residuals','diagnose'], run(v,canvas){ const r=rng(141),x=Array.from({length:70},(_,i)=>i/7),y=x.map(t=>1.8*t+2+(r()+r()-1)*1.8);for(let i=0;i<v;i++)y[i]+=18;const m=linfit(x,y),p=x.map(m.predict);scatter(canvas,x.map((t,i)=>[t,y[i]]),null,{line:m.predict});return [['slope',m.b.toFixed(2)],['R²',r2(y,p).toFixed(3)],['outliers',v]];} },
    { group:'Unsupervised', title:'KMeans clustering', question:'Recover latent groups without labels and inspect inertia.', control:['clusters',2,6,3,''], pipeline:['unlabelled data','initialise','assign','update','inertia'], run(v,canvas){ const r=rng(151),pts=[];[[2,2],[6,5],[9,2]].forEach(c=>{for(let i=0;i<40;i++)pts.push([c[0]+(r()+r()-1)*1.4,c[1]+(r()+r()-1)*1.4]);});const m=kmeans(pts,v,8);scatter(canvas,pts,m.labels);return [['clusters',v],['inertia',m.inertia.toFixed(1)],['rows',pts.length]];} },
    { group:'Unsupervised', title:'DBSCAN density clustering', question:'Change epsilon and discover clusters plus explicit noise points.', control:['epsilon',15,120,55,'%'], pipeline:['unlabelled data','neighborhoods','expand clusters','noise'], run(v,canvas){ const r=rng(161),pts=[];[[2,2],[6,5],[9,2]].forEach(c=>{for(let i=0;i<35;i++)pts.push([c[0]+(r()+r()-1)*1.2,c[1]+(r()+r()-1)*1.2]);});for(let i=0;i<10;i++)pts.push([r()*11,r()*7]);const m=dbscan(pts,v/100*1.5,5);scatter(canvas,pts,m.labels);return [['clusters',m.clusters],['noise',m.noise],['ε',(v/100*1.5).toFixed(2)]];} },
    { group:'Unsupervised', title:'PCA projection', question:'Rotate correlated features onto their principal direction.', control:['correlation',0,95,75,'%'], pipeline:['centre','covariance','eigenvectors','project','variance'], run(v,canvas){ const r=rng(171),rho=v/100,pts=Array.from({length:120},()=>{const a=(r()+r()+r()-1.5)*2.4,b=(r()+r()+r()-1.5)*2.4;return[a,rho*a+Math.sqrt(Math.max(.01,1-rho*rho))*b];}),m=pca2(pts),line=x=>m.centre[1]+(x-m.centre[0])*(m.axis[1]/(Math.abs(m.axis[0])<1e-6?1e-6:m.axis[0]));scatter(canvas,pts,null,{line});return [['PC1 variance',`${(m.ratio*100).toFixed(1)}%`],['axis',m.axis.map(x=>x.toFixed(2)).join(', ')],['ρ',rho.toFixed(2)]];} },
    { group:'Preprocessing', title:'StandardScaler', question:'Put two differently-scaled features into comparable units.', control:['scale ratio',1,100,35,'×'], pipeline:['raw features','mean/std','transform','compare'], run(v,canvas){ const r=rng(181),raw=Array.from({length:80},()=>[(r()+r()-1)*4,(r()+r()-1)*4*v]),sc=standardiser(raw),z=raw.map(sc.transform);scatter(canvas,z);return [['raw σ ratio',(sd(raw.map(x=>x[1]))/sd(raw.map(x=>x[0]))).toFixed(1)],['scaled σ1',sd(z.map(x=>x[0])).toFixed(2)],['scaled σ2',sd(z.map(x=>x[1])).toFixed(2)]];} },
    { group:'Preprocessing', title:'Feature selection', question:'Rank candidate features by correlation with the target.', control:['noise features',1,12,5,''], pipeline:['features','score','rank','select','fit'], run(v,canvas){ const r=rng(191),n=100,target=Array.from({length:n},()=>r()),features=[target.map(t=>t+(r()-.5)*.18),target.map(t=>.6*t+(r()-.5)*.45)];for(let j=0;j<v;j++)features.push(Array.from({length:n},()=>r()));const corr=f=>{const fm=mean(f),tm=mean(target),num=f.reduce((s,x,i)=>s+(x-fm)*(target[i]-tm),0),den=Math.sqrt(f.reduce((s,x)=>s+(x-fm)**2,0)*target.reduce((s,x)=>s+(x-tm)**2,0));return Math.abs(num/(den||1));},scores=features.map(corr).sort((a,b)=>b-a);bars(canvas,scores,scores.map((_,i)=>`f${i+1}`));return [['best score',scores[0].toFixed(3)],['features',features.length],['selected',scores.filter(x=>x>.2).length]];} },
    { group:'Model selection', title:'Cross-validation', question:'Measure how much a validation score moves across folds.', control:['folds',2,10,5,''], pipeline:['split folds','fit repeatedly','score folds','mean ± std'], run(v,canvas){ const d=binaryData(201,240,1.25),idx=shuffleIndices(d.X.length,33),scores=[];for(let f=0;f<v;f++){const test=idx.filter((_,i)=>i%v===f),train=idx.filter((_,i)=>i%v!==f),sc=standardiser(d.X,train),m=logisticFit(train.map(i=>sc.transform(d.X[i])),train.map(i=>d.y[i]),.01,350,.12),pred=test.map(i=>Number(m.prob(sc.transform(d.X[i]))>=.5));scores.push(accuracy(test.map(i=>d.y[i]),pred));}bars(canvas,scores,scores.map((_,i)=>`f${i+1}`));return [['mean',mean(scores).toFixed(3)],['std',sd(scores).toFixed(3)],['folds',v]];} },
    { group:'Model selection', title:'Grid search', question:'Search k automatically instead of guessing a KNN setting.', control:['max k',3,21,15,''], step:2, pipeline:['parameter grid','cross-validate','rank','refit'], run(v,canvas){ const d=binaryData(211,180,1.2),ks=[];for(let k=1;k<=v;k+=2)ks.push(k);const scores=ks.map(k=>{const p=splitIndices(d.X.length,.3,44),sc=standardiser(d.X,p.train),tr=p.train.map(i=>sc.transform(d.X[i])),pred=p.test.map(i=>knnPredict(tr,p.train.map(j=>d.y[j]),sc.transform(d.X[i]),k));return accuracy(p.test.map(i=>d.y[i]),pred);});linePlot(canvas,[{points:ks.map((k,i)=>[k,scores[i]])}],{ymin:Math.max(0,Math.min(...scores)-.05),ymax:1});const best=scores.indexOf(Math.max(...scores));return [['best k',ks[best]],['best score',scores[best].toFixed(3)],['candidates',ks.length]];} },
    { group:'Model selection', title:'Learning curve', question:'Find out whether more training data is still buying accuracy.', control:['max samples',60,240,180,''], pipeline:['subsample','fit','validate','plot learning curve'], run(v,canvas){ const d=binaryData(221,260,1.25),sizes=Array.from({length:8},(_,i)=>Math.round(30+i*(v-30)/7)),pts=sizes.map(n=>{const train=Array.from({length:n},(_,i)=>i),test=Array.from({length:60},(_,i)=>200+i).filter(i=>i<d.X.length),sc=standardiser(d.X,train),m=logisticFit(train.map(i=>sc.transform(d.X[i])),train.map(i=>d.y[i]),.01,350,.12),pred=test.map(i=>Number(m.prob(sc.transform(d.X[i]))>=.5));return[n,accuracy(test.map(i=>d.y[i]),pred)];});linePlot(canvas,[{points:pts}],{ymin:.4,ymax:1});return [['final score',pts.at(-1)[1].toFixed(3)],['max train',v],['trend',pts.at(-1)[1]-pts[0][1]>.06?'still improving':'saturating']];} },
    { group:'Statistics', title:'Bootstrap confidence interval', question:'Estimate uncertainty in the sample mean without a parametric formula.', control:['sample size',10,200,50,''], pipeline:['sample','resample 400×','statistic','percentile CI'], run(v,canvas){ const r=rng(231),data=Array.from({length:v},()=>50+(r()+r()+r()-1.5)*14),boots=Array.from({length:400},()=>mean(Array.from({length:v},()=>data[Math.floor(r()*v)]))).sort((a,b)=>a-b),lo=boots[Math.floor(.025*boots.length)],hi=boots[Math.floor(.975*boots.length)];const hist=Array(16).fill(0),min=Math.min(...boots),max=Math.max(...boots);boots.forEach(x=>hist[Math.min(15,Math.floor((x-min)/(max-min||1)*16))]++);bars(canvas,hist);return [['mean',mean(data).toFixed(2)],['95% low',lo.toFixed(2)],['95% high',hi.toFixed(2)]];} },
    { group:'Statistics', title:'Permutation test', question:'Test whether two group means differ more than random relabelling predicts.', control:['effect size',0,100,35,'%'], pipeline:['observed difference','shuffle labels','null distribution','p-value'], run(v,canvas){ const r=rng(241),n=40,a=Array.from({length:n},()=>r()+v/100*.35),b=Array.from({length:n},()=>r()),obs=Math.abs(mean(a)-mean(b)),all=[...a,...b],nulls=[];for(let q=0;q<300;q++){const idx=shuffleIndices(all.length,q+1),aa=idx.slice(0,n).map(i=>all[i]),bb=idx.slice(n).map(i=>all[i]);nulls.push(Math.abs(mean(aa)-mean(bb)));}const p=(1+nulls.filter(x=>x>=obs).length)/(nulls.length+1),hist=Array(16).fill(0),mx=Math.max(...nulls,obs);nulls.forEach(x=>hist[Math.min(15,Math.floor(x/(mx||1)*16))]++);bars(canvas,hist);return [['observed Δ',obs.toFixed(3)],['p-value',p.toFixed(3)],['permutations',300]];} },
    { group:'Diagnostics', title:'Class imbalance', question:'See why a high accuracy can be worthless on a rare positive class.', control:['positive rate',2,50,12,'%'], pipeline:['labels','naive classifier','accuracy','minority recall'], run(v,canvas){ const n=220,pos=Math.round(n*v/100),truth=Array.from({length:n},(_,i)=>i<pos?1:0),pred=Array(n).fill(0),cm=confusion(truth,pred);bars(canvas,[n-pos,pos],['negative','positive']);return [['accuracy',accuracy(truth,pred).toFixed(3)],['positive recall',cm.recall.toFixed(3)],['positives',pos]];} },
    { group:'Diagnostics', title:'Probability calibration', question:'Compare predicted confidence with observed frequency.', control:['overconfidence',0,100,35,'%'], pipeline:['probabilities','bin','observed rate','calibration error'], run(v,canvas){ const r=rng(251),n=400,raw=Array.from({length:n},()=>r()),truth=raw.map(p=>Number(r()<p)),power=1+v/70,pred=raw.map(p=>p<.5?.5-.5*((.5-p)/.5)**power:.5+.5*((p-.5)/.5)**power),bins=Array.from({length:10},()=>({p:[],y:[]}));pred.forEach((p,i)=>{const b=Math.min(9,Math.floor(p*10));bins[b].p.push(p);bins[b].y.push(truth[i]);});const pts=bins.filter(b=>b.p.length).map(b=>[mean(b.p),mean(b.y)]),ece=bins.reduce((s,b)=>s+b.p.length/n*Math.abs((b.p.length?mean(b.p):0)-(b.y.length?mean(b.y):0)),0);linePlot(canvas,[{points:[[0,0],[1,1]]},{points:pts}],{xmin:0,xmax:1,ymin:0,ymax:1});return [['ECE',ece.toFixed(3)],['bins',pts.length],['overconfidence',`${v}%`]];} },
    { group:'Statistics', title:'Sampling distribution', question:'Watch the mean become more stable as sample size grows.', control:['n per sample',5,150,25,''], pipeline:['population','repeat samples','sample means','standard error'], run(v,canvas){ const r=rng(261),means=Array.from({length:300},()=>mean(Array.from({length:v},()=>r()+r()+r()))),hist=Array(16).fill(0),min=Math.min(...means),max=Math.max(...means);means.forEach(x=>hist[Math.min(15,Math.floor((x-min)/(max-min||1)*16))]++);bars(canvas,hist);return [['mean of means',mean(means).toFixed(3)],['std error',sd(means).toFixed(3)],['n',v]];} },
    { group:'Preprocessing', title:'Train/test leakage', question:'Fit preprocessing on train only vs the full dataset and expose leakage.', control:['test shift',0,100,50,'%'], pipeline:['split','train-only scaler','compare leaked scaler','evaluate'], run(v,canvas){ const r=rng(271),train=Array.from({length:120},()=>[r()*2-1]),test=Array.from({length:60},()=>[r()*2-1+v/35]),all=[...train,...test],scTrain=standardiser(all,Array.from({length:120},(_,i)=>i)),scAll=standardiser(all),zTrain=test.map(x=>scTrain.transform(x)[0]),zLeak=test.map(x=>scAll.transform(x)[0]);bars(canvas,[Math.abs(mean(zTrain)),Math.abs(mean(zLeak))],['proper','leaked']);return [['proper test mean',mean(zTrain).toFixed(2)],['leaked test mean',mean(zLeak).toFixed(2)],['shift',`${v}%`]];} },
    { group:'Model selection', title:'Bias vs variance', question:'Compare training and validation error as complexity rises.', control:['complexity',1,12,4,''], pipeline:['fit complexity','train error','validation error','choose minimum'], run(v,canvas){ const ptsTrain=[],ptsTest=[];for(let c=1;c<=12;c++){ptsTrain.push([c,.34/(c+.3)+.018]);ptsTest.push([c,.42/(c+.4)+.0045*c*c+.035]);}linePlot(canvas,[{points:ptsTrain},{points:ptsTest}],{ymin:0,ymax:.75});const te=ptsTrain[v-1][1],ve=ptsTest[v-1][1];return [['train error',te.toFixed(3)],['validation',ve.toFixed(3)],['diagnosis',v<3?'underfit':v>8?'overfit':'balanced']];} },
    { group:'Model selection', title:'Model comparison', question:'Compare candidate models with a complexity penalty.', control:['complexity penalty',0,50,10,'%'], pipeline:['candidate models','validate','penalise','rank'], run(v,canvas){ const names=['linear','KNN','tree','forest','boost'],raw=[.81,.87,.86,.91,.925],complexity=[1,2,3,6,8],scores=raw.map((s,i)=>s-complexity[i]*v/1000);bars(canvas,scores,names.map(x=>x.slice(0,5)));const best=scores.indexOf(Math.max(...scores));return [['winner',names[best]],['adjusted',scores[best].toFixed(3)],['raw',raw[best].toFixed(3)]];} }
  ];

  function renderDemos() {
    const root = $('#demo-grid');
    demos.forEach((d, i) => {
      const card = document.createElement('article'); card.className = 'ml-demo-card'; card.dataset.group = d.group;
      card.innerHTML = `<header><div><span class="demo-index">${String(i+2).padStart(2,'0')}</span><span class="demo-group">${d.group}</span><h3>${d.title}</h3></div><span class="runtime-badge">browser-local</span></header><p>${d.question}</p><div class="mini-pipeline">${chipHTML(d.pipeline)}</div><canvas width="640" height="330" aria-label="${d.title} interactive chart"></canvas><div class="demo-control"><label>${d.control[0]} <output>${d.control[3]}${d.control[4]}</output></label><input type="range" min="${d.control[1]}" max="${d.control[2]}" value="${d.control[3]}" step="${d.step || 1}"></div><div class="demo-metrics"></div>`;
      root.appendChild(card);
      const input = $('input', card), out = $('output', card), canvas = $('canvas', card), metrics = $('.demo-metrics', card);
      const render = () => { const v = Number(input.value); out.textContent = `${v}${d.control[4]}`; metrics.innerHTML = metricHTML(d.run(v, canvas)); };
      input.addEventListener('input', render); render();
    });
    const filters = $$('#demo-filters button');
    filters.forEach(btn => btn.addEventListener('click', () => { filters.forEach(b=>b.classList.remove('active')); btn.classList.add('active'); const g=btn.dataset.group; $$('.ml-demo-card').forEach(c=>c.hidden=g!=='All'&&c.dataset.group!==g); }));
  }

  async function initMNIST() {
    const canvas = $('#digit-canvas'), ctx = canvas.getContext('2d'), status = $('#wasm-status'), prediction = $('#prediction'), confidence = $('#confidence');
    let wasm = null, centroids = null, drawing = false;
    const clear = () => { ctx.fillStyle='#0b1428';ctx.fillRect(0,0,canvas.width,canvas.height);prediction.textContent='—';confidence.textContent='Draw a digit, then classify it.'; };
    const pos = e => { const b=canvas.getBoundingClientRect(); return {x:(e.clientX-b.left)*canvas.width/b.width,y:(e.clientY-b.top)*canvas.height/b.height}; };
    canvas.addEventListener('pointerdown',e=>{drawing=true;canvas.setPointerCapture(e.pointerId);const p=pos(e);ctx.beginPath();ctx.moveTo(p.x,p.y);});
    canvas.addEventListener('pointermove',e=>{if(!drawing)return;const p=pos(e);ctx.lineTo(p.x,p.y);ctx.stroke();}); canvas.addEventListener('pointerup',()=>drawing=false);
    $('#clear-digit').addEventListener('click',clear);
    function normalise(){const source=ctx.getImageData(0,0,canvas.width,canvas.height).data;let left=canvas.width,top=canvas.height,right=-1,bottom=-1;for(let y=0;y<canvas.height;y++)for(let x=0;x<canvas.width;x++)if(source[(y*canvas.width+x)*4]>80){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);}if(right<0)return null;const crop=document.createElement('canvas'),pad=24,cl=Math.max(0,left-pad),ct=Math.max(0,top-pad),cr=Math.min(canvas.width,right+pad),cb=Math.min(canvas.height,bottom+pad);crop.width=cr-cl;crop.height=cb-ct;crop.getContext('2d').drawImage(canvas,cl,ct,crop.width,crop.height,0,0,crop.width,crop.height);const small=document.createElement('canvas');small.width=28;small.height=28;const sc=small.getContext('2d');sc.fillStyle='#000';sc.fillRect(0,0,28,28);const scale=Math.min(20/crop.width,20/crop.height),w=crop.width*scale,h=crop.height*scale;sc.drawImage(crop,14-w/2,14-h/2,w,h);return small;}
    try { const [model,module] = await Promise.all([fetch('./data/mnist-centroids.json').then(r=>r.json()), createFlowModule({noInitialRun:true})]); wasm=module;centroids=model.centroids.map(c=>new Float32Array(c));status.textContent=`Ready — Flow/WASM kernel loaded; ${model.training_examples.toLocaleString()} MNIST examples built the prototypes.`;status.classList.add('ready'); }
    catch(e){status.textContent='MNIST WASM module failed to load.';status.classList.add('error');console.error(e);}
    $('#run-digit').addEventListener('click',()=>{if(!wasm||!centroids)return;const small=normalise();if(!small){confidence.textContent='Draw a digit first.';return;}const pixels=small.getContext('2d').getImageData(0,0,28,28).data,input=new Float32Array(784);for(let i=0;i<784;i++)input[i]=pixels[i*4]/255;const ip=wasm._malloc(input.byteLength);wasm.HEAPF32.set(input,ip>>2);const scores=centroids.map((centroid,digit)=>{const pp=wasm._malloc(centroid.byteLength);wasm.HEAPF32.set(centroid,pp>>2);const distance=wasm.ccall('mnist_squared_distance_ptr_f32_ptr_f32_i32','number',['number','number','number'],[ip,pp,784]);wasm._free(pp);return{digit,distance};}).sort((a,b)=>a.distance-b.distance);wasm._free(ip);const margin=Math.max(0,scores[1].distance-scores[0].distance),conf=Math.round(Math.min(99,45+margin*8));prediction.textContent=String(scores[0].digit);confidence.textContent=`${conf}% prototype margin · distance computed in Flow WebAssembly`;});
    ctx.strokeStyle='#fff';ctx.lineWidth=24;ctx.lineCap='round';ctx.lineJoin='round';clear();
  }

  $('#iris-run').addEventListener('click',runFlagship); $('#iris-test').addEventListener('input',runFlagship); $('#iris-k').addEventListener('input',runFlagship); $('#iris-scale').addEventListener('change',runFlagship);
  runFlagship(); renderDemos(); initMNIST();
})();

const canvas = document.querySelector("#digit-canvas");
const context = canvas.getContext("2d");
const status = document.querySelector("#wasm-status");
const prediction = document.querySelector("#prediction");
const confidence = document.querySelector("#confidence");
let wasm = null;
let centroids = null;
let drawing = false;

function clearCanvas() {
  context.fillStyle = "#0c1730";
  context.fillRect(0, 0, canvas.width, canvas.height);
  prediction.textContent = "—";
  confidence.textContent = "Draw a single digit, then classify it.";
}

function position(event) {
  const box = canvas.getBoundingClientRect();
  return { x: (event.clientX - box.left) * canvas.width / box.width, y: (event.clientY - box.top) * canvas.height / box.height };
}

function normaliseDrawing() {
  const source = context.getImageData(0, 0, canvas.width, canvas.height).data;
  let left = canvas.width;
  let top = canvas.height;
  let right = -1;
  let bottom = -1;
  for (let y = 0; y < canvas.height; y += 1) {
    for (let x = 0; x < canvas.width; x += 1) {
      if (source[(y * canvas.width + x) * 4] > 80) {
        left = Math.min(left, x); right = Math.max(right, x);
        top = Math.min(top, y); bottom = Math.max(bottom, y);
      }
    }
  }
  if (right < 0) return null;

  const crop = document.createElement("canvas");
  const pad = 24;
  const cropLeft = Math.max(0, left - pad);
  const cropTop = Math.max(0, top - pad);
  const cropRight = Math.min(canvas.width, right + pad);
  const cropBottom = Math.min(canvas.height, bottom + pad);
  crop.width = cropRight - cropLeft;
  crop.height = cropBottom - cropTop;
  crop.getContext("2d").drawImage(canvas, cropLeft, cropTop, crop.width, crop.height, 0, 0, crop.width, crop.height);

  const small = document.createElement("canvas");
  small.width = 28; small.height = 28;
  const smallContext = small.getContext("2d");
  smallContext.fillStyle = "#000000";
  smallContext.fillRect(0, 0, 28, 28);
  const scale = Math.min(20 / crop.width, 20 / crop.height);
  const width = crop.width * scale;
  const height = crop.height * scale;
  smallContext.drawImage(crop, 14 - width / 2, 14 - height / 2, width, height);
  return small;
}

async function loadModel() {
  try {
    const [model] = await Promise.all([
      fetch("./data/mnist-centroids.json").then((response) => response.json()),
      createFlowModule({ noInitialRun: true }).then((module) => { wasm = module; })
    ]);
    centroids = model.centroids.map((centroid) => new Float32Array(centroid));
    status.textContent = `Ready. ${model.training_examples.toLocaleString()} MNIST images trained the ten centroids. Draw a digit and classify it.`;
    status.classList.add("ready");
    initialiseExperiments();
  } catch (error) {
    status.textContent = "The model did not load. Please refresh the page and try again.";
    status.classList.add("error");
    console.error(error);
  }
}

canvas.addEventListener("pointerdown", (event) => {
  drawing = true;
  canvas.setPointerCapture(event.pointerId);
  const point = position(event);
  context.beginPath();
  context.moveTo(point.x, point.y);
});

function flowNumber(name, values) {
  return wasm.ccall(name, "number", values.map(() => "number"), values);
}

function bindSliders(ids, render) {
  ids.forEach((id) => document.querySelector(`#${id}`).addEventListener("input", render));
  render();
}

function initialiseExperiments() {
  initialiseVisualLab();
  bindSliders(["home-area", "home-rooms", "home-age"], () => {
    const area = Number(document.querySelector("#home-area").value);
    const rooms = Number(document.querySelector("#home-rooms").value);
    const age = Number(document.querySelector("#home-age").value);
    document.querySelector("#home-area-output").textContent = `${area} m²`;
    document.querySelector("#home-rooms-output").textContent = rooms;
    document.querySelector("#home-age-output").textContent = `${age} years`;
    const price = flowNumber("home_price_estimate_f32_f32_f32", [area, rooms, age]);
    const rounded = Math.round(price / 1000) * 1000;
    document.querySelector("#home-result").textContent = `Baseline estimate: £${rounded.toLocaleString("en-GB")}`;
  });

  bindSliders(["risk-util", "risk-late", "risk-debt"], () => {
    const utilisation = Number(document.querySelector("#risk-util").value);
    const late = Number(document.querySelector("#risk-late").value);
    const debt = Number(document.querySelector("#risk-debt").value);
    document.querySelector("#risk-util-output").textContent = `${utilisation}%`;
    document.querySelector("#risk-late-output").textContent = late;
    document.querySelector("#risk-debt-output").textContent = `${debt}%`;
    const score = flowNumber("payment_risk_f32_f32_f32", [utilisation, late, debt]);
    const queue = score >= 65 ? "Review now" : score >= 40 ? "Review soon" : "Low priority";
    document.querySelector("#risk-result").textContent = `${queue} · risk score ${Math.round(score)}/100`;
  });

  bindSliders(["scale-value", "scale-mean", "scale-std"], () => {
    const value = Number(document.querySelector("#scale-value").value);
    const mean = Number(document.querySelector("#scale-mean").value);
    const std = Number(document.querySelector("#scale-std").value);
    document.querySelector("#scale-value-output").textContent = `£${value}k`;
    document.querySelector("#scale-mean-output").textContent = `£${mean}k`;
    document.querySelector("#scale-std-output").textContent = `£${std}k`;
    const z = flowNumber("standardise_value_f32_f32_f32", [value, mean, std]);
    document.querySelector("#scale-result").textContent = `${z.toFixed(2)} standard deviations from average`;
  });

  bindSliders(["anomaly-value", "anomaly-mean", "anomaly-std"], () => {
    const value = Number(document.querySelector("#anomaly-value").value);
    const mean = Number(document.querySelector("#anomaly-mean").value);
    const std = Number(document.querySelector("#anomaly-std").value);
    document.querySelector("#anomaly-value-output").textContent = value;
    document.querySelector("#anomaly-mean-output").textContent = mean;
    document.querySelector("#anomaly-std-output").textContent = std;
    const z = flowNumber("absolute_z_score_f32_f32_f32", [value, mean, std]);
    document.querySelector("#anomaly-result").textContent = z >= 3 ? `${z.toFixed(1)}σ · investigate` : `${z.toFixed(1)}σ · within expected range`;
  });

  bindSliders(["eta-distance", "eta-stops", "eta-traffic"], () => {
    const distance = Number(document.querySelector("#eta-distance").value);
    const stops = Number(document.querySelector("#eta-stops").value);
    const traffic = Number(document.querySelector("#eta-traffic").value);
    document.querySelector("#eta-distance-output").textContent = `${distance} km`;
    document.querySelector("#eta-stops-output").textContent = stops;
    document.querySelector("#eta-traffic-output").textContent = `${traffic}%`;
    const eta = flowNumber("delivery_eta_minutes_f32_f32_f32", [distance, stops, traffic]);
    document.querySelector("#eta-result").textContent = `Estimated arrival: ${Math.round(eta)} minutes`;
  });

  bindSliders(["spam-links", "spam-caps", "spam-sender"], () => {
    const links = Number(document.querySelector("#spam-links").value);
    const caps = Number(document.querySelector("#spam-caps").value) / 100;
    const sender = Number(document.querySelector("#spam-sender").value);
    document.querySelector("#spam-links-output").textContent = links;
    document.querySelector("#spam-caps-output").textContent = `${Math.round(caps * 100)}%`;
    document.querySelector("#spam-sender-output").textContent = sender ? "yes" : "no";
    const risk = flowNumber("message_risk_f32_f32_f32", [links, caps, sender]);
    document.querySelector("#spam-result").textContent = risk >= 50 ? `Review queue · score ${Math.round(risk)}/100` : `Deliver normally · score ${Math.round(risk)}/100`;
  });

  bindSliders(["stock-units", "stock-sales", "stock-lead"], () => {
    const units = Number(document.querySelector("#stock-units").value);
    const sales = Number(document.querySelector("#stock-sales").value);
    const lead = Number(document.querySelector("#stock-lead").value);
    document.querySelector("#stock-units-output").textContent = units;
    document.querySelector("#stock-sales-output").textContent = sales;
    document.querySelector("#stock-lead-output").textContent = `${lead} days`;
    const cover = flowNumber("stock_cover_days_f32_f32", [units, sales]);
    document.querySelector("#stock-result").textContent = cover <= lead ? `Reorder now · ${cover.toFixed(1)} days of cover` : `Stock is sufficient · ${cover.toFixed(1)} days of cover`;
  });

  bindSliders(["quality-measured", "quality-target", "quality-tolerance"], () => {
    const measured = Number(document.querySelector("#quality-measured").value) / 10;
    const target = Number(document.querySelector("#quality-target").value) / 10;
    const tolerance = Number(document.querySelector("#quality-tolerance").value) / 10;
    document.querySelector("#quality-measured-output").textContent = `${measured.toFixed(1)} mm`;
    document.querySelector("#quality-target-output").textContent = `${target.toFixed(1)} mm`;
    document.querySelector("#quality-tolerance-output").textContent = `${tolerance.toFixed(1)} mm`;
    const deviation = flowNumber("tolerance_deviation_f32_f32_f32", [measured, target, tolerance]);
    document.querySelector("#quality-result").textContent = deviation <= 1 ? `Pass · ${deviation.toFixed(2)}× tolerance used` : `Hold for inspection · ${deviation.toFixed(2)}× tolerance`;
  });

  initialiseSegmentMap();
}

function initialiseVisualLab() {
  const lab = document.querySelector("#visual-lab");
  const experiments = [
    ["Home prices", "Regression line", "price"], ["Payment reviews", "Risk boundary", "risk"],
    ["Feature scaling", "Before / after", "scale"], ["Sensor alerts", "Normal range", "anomaly"],
    ["Delivery windows", "Route estimate", "eta"], ["Message triage", "Review threshold", "spam"],
    ["Stock cover", "Demand curve", "stock"], ["Part tolerance", "Pass / hold band", "quality"],
    ["Customer segments", "Nearest centroid", "cluster"], ["MNIST digits", "Draw and classify", "mnist"]
  ];
  experiments.forEach(([title, subtitle, kind], index) => {
    const card = document.createElement("article"); card.className = "visual-card";
    card.innerHTML = `<header><div><small>${String(index + 1).padStart(2, "0")} / interactive</small><h3>${title}</h3></div><small>${subtitle}</small></header><canvas width="640" height="360" aria-label="${title} interactive graph"></canvas><footer><span>Click or drag in the chart</span><strong>Loading…</strong></footer>`;
    lab.append(card);
    drawVisualExperiment(card, kind, index);
  });
}

function drawVisualExperiment(card, kind, seed) {
  const canvas = card.querySelector("canvas"), ctx = canvas.getContext("2d"), result = card.querySelector("strong");
  let point = { x: 0.54, y: 0.46 };
  function render() {
    const w = canvas.width, h = canvas.height, x = point.x * w, y = point.y * h;
    ctx.fillStyle = "#0c1730"; ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = "#263b63"; ctx.lineWidth = 1;
    for (let i = 48; i < w; i += 64) { ctx.beginPath(); ctx.moveTo(i, 28); ctx.lineTo(i, h - 36); ctx.stroke(); }
    for (let i = 40; i < h; i += 48) { ctx.beginPath(); ctx.moveTo(36, i); ctx.lineTo(w - 28, i); ctx.stroke(); }
    const colours = ["#5669e8", "#54b6d3", "#ef8068"];
    for (let i = 0; i < 34; i += 1) {
      const px = 54 + ((i * 83 + seed * 41) % 520), py = 70 + ((i * 47 + seed * 29) % 220);
      const drift = Math.sin((i + point.x * 8) * 1.7) * 16;
      ctx.fillStyle = colours[(i + seed) % 3]; ctx.beginPath(); ctx.arc(px, py + drift, 5, 0, Math.PI * 2); ctx.fill();
    }
    if (["price", "eta", "stock"].includes(kind)) { ctx.strokeStyle = "#ef8068"; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(40, h - 65); ctx.bezierCurveTo(w*.3,h*.55,w*.58,h*.7,w-35,48 + y*.18); ctx.stroke(); }
    if (["risk", "spam", "quality", "anomaly"].includes(kind)) { ctx.fillStyle = "rgba(239,128,104,.18)"; ctx.fillRect(x, 30, w - x, h - 66); ctx.strokeStyle = "#ef8068"; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x, 30); ctx.lineTo(x, h - 36); ctx.stroke(); }
    if (kind === "cluster") { [[.2,.72],[.49,.48],[.78,.28]].forEach((p,i)=>{ctx.fillStyle=colours[i];ctx.beginPath();ctx.arc(p[0]*w,p[1]*h,24,0,Math.PI*2);ctx.fill();}); }
    if (kind === "mnist") { ctx.fillStyle="#dce8ff";ctx.font="22px DM Mono";ctx.fillText("Open the full drawing canvas below ↓", 88, 185); }
    ctx.fillStyle = "#fffdf8"; ctx.beginPath(); ctx.arc(x, y, 9, 0, Math.PI * 2); ctx.fill();
    const value = Math.round(point.x * 100);
    if (kind === "price") result.textContent = `£${new Intl.NumberFormat("en-GB").format(Math.round(flowNumber("home_price_estimate_f32_f32_f32", [30 + value * 1.8, 3, 18]) / 1000) * 1000)}`;
    else if (kind === "risk") result.textContent = `${Math.round(flowNumber("payment_risk_f32_f32_f32", [value, 2, 28]))}/100 review score`;
    else if (kind === "scale") result.textContent = `${flowNumber("standardise_value_f32_f32_f32", [value, 50, 18]).toFixed(2)}σ from average`;
    else if (kind === "anomaly") result.textContent = `${flowNumber("absolute_z_score_f32_f32_f32", [value, 50, 12]).toFixed(1)}σ from normal`;
    else if (kind === "eta") result.textContent = `${Math.round(flowNumber("delivery_eta_minutes_f32_f32_f32", [value / 2, 4, 35]))} min ETA`;
    else if (kind === "spam") result.textContent = `${Math.round(flowNumber("message_risk_f32_f32_f32", [value / 20, .12, 1]))}/100 review score`;
    else if (kind === "stock") result.textContent = `${flowNumber("stock_cover_days_f32_f32", [value * 8, 18]).toFixed(1)} days of cover`;
    else if (kind === "quality") result.textContent = `${flowNumber("tolerance_deviation_f32_f32_f32", [value / 10, 10, .4]).toFixed(2)}× tolerance`;
    else if (kind === "cluster") result.textContent = `${flowNumber("point_distance_f32_f32_f32_f32", [x, y, 315, 172]).toFixed(0)} distance to regular`;
    else result.textContent = "Open canvas below";
  }
  function move(event) { const box=canvas.getBoundingClientRect(); point={x:Math.max(.06,Math.min(.94,(event.clientX-box.left)/box.width)),y:Math.max(.1,Math.min(.88,(event.clientY-box.top)/box.height))}; render(); }
  let active=false; canvas.addEventListener("pointerdown",e=>{active=true;canvas.setPointerCapture(e.pointerId);move(e)}); canvas.addEventListener("pointermove",e=>{if(active)move(e)}); canvas.addEventListener("pointerup",()=>active=false); render();
}

function initialiseSegmentMap() {
  const segmentCanvas = document.querySelector("#segment-canvas");
  const segmentContext = segmentCanvas.getContext("2d");
  const groups = [{ name: "Occasional", x: 78, y: 165, color: "#5669e8" }, { name: "Regular", x: 185, y: 112, color: "#54b6d3" }, { name: "High-value", x: 288, y: 62, color: "#ef8068" }];
  let point = { x: 160, y: 138 };
  function draw() {
    segmentContext.fillStyle = "#0c1730"; segmentContext.fillRect(0, 0, 360, 220);
    segmentContext.strokeStyle = "#33496f"; segmentContext.lineWidth = 1;
    for (let x = 40; x < 350; x += 60) segmentContext.beginPath(), segmentContext.moveTo(x, 20), segmentContext.lineTo(x, 190), segmentContext.stroke();
    for (let y = 30; y < 200; y += 40) segmentContext.beginPath(), segmentContext.moveTo(30, y), segmentContext.lineTo(340, y), segmentContext.stroke();
    groups.forEach((group) => { segmentContext.fillStyle = group.color; segmentContext.beginPath(); segmentContext.arc(group.x, group.y, 18, 0, Math.PI * 2); segmentContext.fill(); segmentContext.fillStyle = "#dce8ff"; segmentContext.font = "11px DM Mono"; segmentContext.fillText(group.name, group.x - 24, group.y + 33); });
    segmentContext.fillStyle = "#fffdf8"; segmentContext.beginPath(); segmentContext.arc(point.x, point.y, 8, 0, Math.PI * 2); segmentContext.fill();
    const closest = groups.map((group) => ({ group, distance: flowNumber("point_distance_f32_f32_f32_f32", [point.x, point.y, group.x, group.y]) })).sort((a, b) => a.distance - b.distance)[0];
    document.querySelector("#segment-result").textContent = `Nearest group: ${closest.group.name}`;
  }
  function move(event) { const box = segmentCanvas.getBoundingClientRect(); point = { x: Math.max(30, Math.min(340, (event.clientX - box.left) * 360 / box.width)), y: Math.max(20, Math.min(190, (event.clientY - box.top) * 220 / box.height)) }; draw(); }
  let dragging = false;
  segmentCanvas.addEventListener("pointerdown", (event) => { dragging = true; segmentCanvas.setPointerCapture(event.pointerId); move(event); });
  segmentCanvas.addEventListener("pointermove", (event) => { if (dragging) move(event); });
  segmentCanvas.addEventListener("pointerup", () => { dragging = false; });
  draw();
}
canvas.addEventListener("pointermove", (event) => {
  if (!drawing) return;
  const point = position(event);
  context.lineTo(point.x, point.y);
  context.stroke();
});
canvas.addEventListener("pointerup", () => { drawing = false; });

document.querySelector("#run-digit").addEventListener("click", () => {
  if (!wasm || !centroids) return;
  const small = normaliseDrawing();
  if (!small) {
    confidence.textContent = "Please draw a digit first — a single, centred digit works best.";
    return;
  }
  const smallContext = small.getContext("2d");
  const pixels = smallContext.getImageData(0, 0, 28, 28).data;
  const input = new Float32Array(784);
  for (let index = 0; index < 784; index += 1) input[index] = pixels[index * 4] / 255;
  const inputPointer = wasm._malloc(input.byteLength);
  wasm.HEAPF32.set(input, inputPointer >> 2);
  const distances = centroids.map((centroid) => {
    const prototypePointer = wasm._malloc(centroid.byteLength);
    wasm.HEAPF32.set(centroid, prototypePointer >> 2);
    const distance = wasm.ccall("mnist_squared_distance_ptr_f32_ptr_f32_i32", "number", ["number", "number", "number"], [inputPointer, prototypePointer, 784]);
    wasm._free(prototypePointer);
    return distance;
  });
  wasm._free(inputPointer);
  const sorted = distances.map((distance, digit) => ({ digit, distance })).sort((a, b) => a.distance - b.distance);
  const margin = Math.max(0, sorted[1].distance - sorted[0].distance);
  const score = Math.round(Math.min(99, 45 + margin * 8));
  prediction.textContent = sorted[0].digit;
  confidence.textContent = `${score}% confidence · nearest-centroid distance calculated in Flow WASM`;
});

context.strokeStyle = "#ffffff";
context.lineWidth = 24;
context.lineCap = "round";
context.lineJoin = "round";
clearCanvas();
document.querySelector("#clear-digit").addEventListener("click", clearCanvas);
loadModel();

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

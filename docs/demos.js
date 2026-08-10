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

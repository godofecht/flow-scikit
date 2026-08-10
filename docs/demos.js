const samples = [
  ["00111000","01100110","11000011","11000011","11000011","11000011","01100110","00111000"],
  ["00011000","00111000","01111000","00011000","00011000","00011000","00011000","01111110"],
  ["00111100","01100110","00000110","00001100","00011000","00110000","01100000","01111110"],
  ["00111100","01100110","00000110","00011100","00000110","00000110","01100110","00111100"],
  ["00001100","00011100","00101100","01001100","11111110","00001100","00001100","00011110"],
  ["01111110","01100000","01111100","00000110","00000110","00000110","01100110","00111100"],
  ["00111100","01100000","01111100","01100110","01100110","01100110","01100110","00111100"],
  ["01111110","00000110","00001100","00011000","00110000","00110000","00110000","00110000"],
  ["00111100","01100110","01100110","00111100","01100110","01100110","01100110","00111100"],
  ["00111100","01100110","01100110","00111110","00000110","00000110","00001100","00111000"]
];

const grid = document.querySelector("#pixel-grid");
const status = document.querySelector("#wasm-status");
const prediction = document.querySelector("#prediction");
const confidence = document.querySelector("#confidence");
const noise = document.querySelector("#noise");
const noiseValue = document.querySelector("#noise-value");
let selected = 0;
let wasm = null;

function drawDigit() {
  grid.replaceChildren();
  samples[selected].join("").split("").forEach((pixel, index) => {
    const cell = document.createElement("span");
    const noisy = Math.random() * 100 < Number(noise.value) && index % 5 === 0;
    cell.className = pixel === "1" && !noisy ? "on" : "off";
    grid.append(cell);
  });
}

async function loadWasm() {
  try {
    wasm = await createFlowModule({ noInitialRun: true });
    status.textContent = "WASM module ready. The confidence score will run in Flow-built WebAssembly.";
    status.classList.add("ready");
  } catch (error) {
    status.textContent = "The WASM module did not load. The sample viewer still works, but the recogniser is unavailable.";
    status.classList.add("error");
    console.error(error);
  }
}

document.querySelectorAll(".digit-button").forEach((button) => {
  button.addEventListener("click", () => {
    selected = Number(button.dataset.digit);
    document.querySelectorAll(".digit-button").forEach((item) => item.classList.toggle("active", item === button));
    prediction.textContent = "—";
    confidence.textContent = "Sample changed. Run it when ready.";
    drawDigit();
  });
});

noise.addEventListener("input", () => { noiseValue.textContent = `${noise.value}%`; drawDigit(); });
document.querySelector("#run-digit").addEventListener("click", () => {
  if (!wasm) return;
  const score = wasm.ccall("mnist_confidence_i32_i32", "number", ["number", "number"], [selected, Number(noise.value)]);
  prediction.textContent = selected;
  confidence.textContent = `${score}% confidence · calculated in WASM`;
});

drawDigit();
loadWasm();

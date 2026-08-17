import fs from "node:fs";
import {pathToFileURL} from "node:url";
import {createFlowScikitBrowserApi} from "../docs/wasm/browser_mlir.mjs";

const wasmPath = process.argv[2] ?? "docs/wasm/browser_mlir.wasm";
const bytes = fs.readFileSync(wasmPath);
const module = new WebAssembly.Module(bytes);
const imports = WebAssembly.Module.imports(module);

if (imports.length !== 0) {
  throw new Error(`allocation-free browser facade has unexpected imports: ${JSON.stringify(imports)}`);
}

const instance = await WebAssembly.instantiate(module, {});
const api = createFlowScikitBrowserApi(instance);

const yTrue = [1, 1, 1, 0, 0, 0, 1, 0];
const yPred = [1, 1, 0, 0, 1, 0, 1, 0];
const expected = 0.75;
const tolerance = 1e-6;

const results = {
  accuracy: api.accuracy(yTrue, yPred),
  precision: api.precision(yTrue, yPred),
  recall: api.recall(yTrue, yPred),
  f1: api.f1(yTrue, yPred),
};

for (const [name, value] of Object.entries(results)) {
  if (Math.abs(value - expected) > tolerance) {
    throw new Error(`${name}: expected ${expected}, got ${value}`);
  }
}

console.log(JSON.stringify({wasm: pathToFileURL(wasmPath).href, imports, results}));

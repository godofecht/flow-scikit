import fs from "node:fs";
import {pathToFileURL} from "node:url";
import {createFlowScikitBrowserApi} from "../docs/wasm/browser_mlir.mjs";
import {createFlowScikitDemoApi} from "../docs/wasm/mnist_demo.mjs";

const metricsPath = process.argv[2] ?? "docs/wasm/browser_mlir.wasm";
const demoPath = process.argv[3] ?? "docs/wasm/mnist_demo.wasm";
const tolerance = 1e-5;

function instantiateImportFree(path) {
  const bytes = fs.readFileSync(path);
  const module = new WebAssembly.Module(bytes);
  const imports = WebAssembly.Module.imports(module);
  if (imports.length !== 0) {
    throw new Error(`${path} has unexpected imports: ${JSON.stringify(imports)}`);
  }
  return {instance: new WebAssembly.Instance(module, {}), imports};
}

function expectNear(name, actual, expected) {
  if (Math.abs(actual - expected) > tolerance) {
    throw new Error(`${name}: expected ${expected}, got ${actual}`);
  }
}

const metricsModule = instantiateImportFree(metricsPath);
const metrics = createFlowScikitBrowserApi(metricsModule.instance);
const yTrue = [1, 1, 1, 0, 0, 0, 1, 0];
const yPred = [1, 1, 0, 0, 1, 0, 1, 0];
const metricResults = {
  accuracy: metrics.accuracy(yTrue, yPred),
  precision: metrics.precision(yTrue, yPred),
  recall: metrics.recall(yTrue, yPred),
  f1: metrics.f1(yTrue, yPred),
};
for (const [name, value] of Object.entries(metricResults)) {
  expectNear(name, value, 0.75);
}

const demoModule = instantiateImportFree(demoPath);
const demo = createFlowScikitDemoApi(demoModule.instance);
const demoResults = {
  mnistSquaredDistance: demo.squaredDistance([1, 2, 3], [1, 0, 4]),
  homePriceEstimate: demo.homePriceEstimate(100, 3, 10),
  paymentRisk: demo.paymentRisk(0.5, 2, 0.25),
  standardiseValue: demo.standardiseValue(10, 4, 2),
  absoluteZScore: demo.absoluteZScore(2, 4, 1),
  pointDistance: demo.pointDistance(1, 2, 4, 6),
  deliveryEtaMinutes: demo.deliveryEtaMinutes(10, 2, 50),
  messageRisk: demo.messageRisk(1, 0.2, 1),
  stockCoverDays: demo.stockCoverDays(100, 5),
  toleranceDeviation: demo.toleranceDeviation(12, 10, 0.5),
};
const demoExpected = {
  mnistSquaredDistance: 5,
  homePriceEstimate: 444800,
  paymentRisk: 24.325,
  standardiseValue: 3,
  absoluteZScore: 2,
  pointDistance: 25,
  deliveryEtaMinutes: 53,
  messageRisk: 47,
  stockCoverDays: 20,
  toleranceDeviation: 4,
};
for (const [name, value] of Object.entries(demoResults)) {
  expectNear(name, value, demoExpected[name]);
}

console.log(JSON.stringify({
  metrics: {
    wasm: pathToFileURL(metricsPath).href,
    imports: metricsModule.imports,
    results: metricResults,
  },
  demo: {
    wasm: pathToFileURL(demoPath).href,
    imports: demoModule.imports,
    results: demoResults,
  },
}));

const WASM_PAGE_BYTES = 65536;
const ALIGNMENT = 16;

function alignUp(value, alignment = ALIGNMENT) {
  return Math.ceil(value / alignment) * alignment;
}

function instantiateResult(result) {
  return result instanceof WebAssembly.Instance ? result : result.instance;
}

export function createFlowScikitBrowserApi(instance) {
  const {
    memory,
    browser_accuracy,
    browser_precision,
    browser_recall,
    browser_f1,
  } = instance.exports;

  if (!(memory instanceof WebAssembly.Memory)) {
    throw new Error("flow-scikit wasm module does not export linear memory");
  }

  const required = {browser_accuracy, browser_precision, browser_recall, browser_f1};
  for (const [name, fn] of Object.entries(required)) {
    if (typeof fn !== "function") {
      throw new Error(`flow-scikit wasm export missing: ${name}`);
    }
  }

  let hostOffset = alignUp(memory.buffer.byteLength);

  function reserve(bytes) {
    const ptr = alignUp(hostOffset);
    const end = ptr + bytes;
    if (end > memory.buffer.byteLength) {
      memory.grow(Math.ceil((end - memory.buffer.byteLength) / WASM_PAGE_BYTES));
    }
    hostOffset = end;
    return ptr;
  }

  function writeF32(values) {
    const data = Float32Array.from(values);
    const ptr = reserve(data.byteLength);
    new Float32Array(memory.buffer, ptr, data.length).set(data);
    return ptr;
  }

  function inputs(yTrue, yPred) {
    if (yTrue.length !== yPred.length) {
      throw new RangeError("yTrue and yPred must have equal length");
    }
    if (yTrue.length === 0) {
      throw new RangeError("metric inputs must not be empty");
    }
    return {yTruePtr: writeF32(yTrue), yPredPtr: writeF32(yPred), n: yTrue.length};
  }

  return {
    memory,
    accuracy(yTrue, yPred) {
      const {yTruePtr, yPredPtr, n} = inputs(yTrue, yPred);
      return browser_accuracy(yTruePtr, yPredPtr, n);
    },
    precision(yTrue, yPred, posLabel = 1) {
      const {yTruePtr, yPredPtr, n} = inputs(yTrue, yPred);
      return browser_precision(yTruePtr, yPredPtr, n, posLabel);
    },
    recall(yTrue, yPred, posLabel = 1) {
      const {yTruePtr, yPredPtr, n} = inputs(yTrue, yPred);
      return browser_recall(yTruePtr, yPredPtr, n, posLabel);
    },
    f1(yTrue, yPred, posLabel = 1) {
      const {yTruePtr, yPredPtr, n} = inputs(yTrue, yPred);
      return browser_f1(yTruePtr, yPredPtr, n, posLabel);
    },
  };
}

export async function loadFlowScikitWasm(url = "./browser_mlir.wasm") {
  let result;
  if (typeof WebAssembly.instantiateStreaming === "function") {
    try {
      result = await WebAssembly.instantiateStreaming(fetch(url), {});
    } catch {
      const response = await fetch(url);
      result = await WebAssembly.instantiate(await response.arrayBuffer(), {});
    }
  } else {
    const response = await fetch(url);
    result = await WebAssembly.instantiate(await response.arrayBuffer(), {});
  }
  return createFlowScikitBrowserApi(instantiateResult(result));
}

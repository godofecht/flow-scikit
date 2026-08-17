const WASM_PAGE_BYTES = 65536;
const ALIGNMENT = 16;

function alignUp(value, alignment = ALIGNMENT) {
  return Math.ceil(value / alignment) * alignment;
}

function instantiateResult(result) {
  return result instanceof WebAssembly.Instance ? result : result.instance;
}

export function createFlowScikitDemoApi(instance) {
  const {
    memory,
    mnist_squared_distance,
    home_price_estimate,
    payment_risk,
    standardise_value,
    absolute_z_score,
    point_distance,
    delivery_eta_minutes,
    message_risk,
    stock_cover_days,
    tolerance_deviation,
  } = instance.exports;

  if (!(memory instanceof WebAssembly.Memory)) {
    throw new Error("flow-scikit demo wasm does not export linear memory");
  }

  const required = {
    mnist_squared_distance,
    home_price_estimate,
    payment_risk,
    standardise_value,
    absolute_z_score,
    point_distance,
    delivery_eta_minutes,
    message_risk,
    stock_cover_days,
    tolerance_deviation,
  };
  for (const [name, fn] of Object.entries(required)) {
    if (typeof fn !== "function") {
      throw new Error(`flow-scikit demo wasm export missing: ${name}`);
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

  return {
    memory,

    squaredDistance(input, prototype) {
      if (input.length !== prototype.length) {
        throw new RangeError("input and prototype must have equal length");
      }
      if (input.length === 0) {
        return 0;
      }
      return mnist_squared_distance(writeF32(input), writeF32(prototype), input.length);
    },

    homePriceEstimate: home_price_estimate,
    paymentRisk: payment_risk,
    standardiseValue: standardise_value,
    absoluteZScore: absolute_z_score,
    pointDistance: point_distance,
    deliveryEtaMinutes: delivery_eta_minutes,
    messageRisk: message_risk,
    stockCoverDays: stock_cover_days,
    toleranceDeviation: tolerance_deviation,
  };
}

export async function loadFlowScikitDemoWasm(url = "./mnist_demo.wasm") {
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
  return createFlowScikitDemoApi(instantiateResult(result));
}

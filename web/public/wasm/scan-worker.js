// Web Worker that loads and runs the Aguara WASM scanner off the main thread.
// Messages: { type: "scan", id, content, filename }
// Replies:  { type: "result", id, json } or { type: "error", id, message }

let ready = false;
let readyPromise = null;

function init() {
  if (readyPromise) return readyPromise;
  readyPromise = new Promise(function (resolve, reject) {
    importScripts("/wasm/wasm_exec.js");
    const go = new Go();
    fetch("/wasm/aguara.wasm")
      .then(function (resp) { return WebAssembly.instantiateStreaming(resp, go.importObject); })
      .then(function (result) {
        go.run(result.instance);
        ready = true;
        resolve();
        self.postMessage({ type: "ready", loadTime: performance.now() });
      })
      .catch(reject);
  });
  return readyPromise;
}

self.onmessage = function (e) {
  const msg = e.data;
  if (msg.type === "scan") {
    init()
      .then(function () { return aguaraScanContent(msg.content, msg.filename); })
      .then(function (json) { self.postMessage({ type: "result", id: msg.id, json: json }); })
      .catch(function (err) { self.postMessage({ type: "error", id: msg.id, message: err.message || String(err) }); });
  }
};

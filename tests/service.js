import * as Comlink from 'https://unpkg.com/comlink/dist/esm/comlink.mjs';

let workerInstance = null;

export function createWorker() {
    console.log("Creating new worker instance");
    if (workerInstance) {
        console.log("Reusing existing worker instance");
        return workerInstance;
    }

    const worker = new Worker("./worker.js");
    // workerInstance = Comlink.wrap(worker);
    workerInstance = worker;
    return workerInstance;
}

export function disposeWorker() {
    if (workerInstance) {
        workerInstance.shutdown?.();
        workerInstance = null;
    }
}
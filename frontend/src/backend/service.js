// import * as Comlink from 'https://unpkg.com/comlink/dist/esm/comlink.mjs';
import * as Comlink from 'comlink';

let workerInstance = null;
let initializationPromise = null;

export async function createWorker() {
  // If we're already initialized, return the existing worker
  if (workerInstance) {
    console.log('[Service] Reusing existing worker instance');
    return workerInstance;
  }

  // If we're in the process of initializing, return the promise
  if (initializationPromise) {
    console.log('[Service] Waiting for existing initialization to complete');
    return initializationPromise;
  }

  console.log('[Service] Starting new worker initialization');
  initializationPromise = (async () => {
    try {
      const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
      workerInstance = Comlink.wrap(worker);
      return workerInstance;
    } catch (error) {
      console.error('[Service] Worker initialization failed:', error);
      // Clear state on failure
      workerInstance = null;
      throw error;
    } finally {
      initializationPromise = null;
    }
  })();

  return initializationPromise;
}

export async function disposeWorker() {
  if (workerInstance) {
    try {
      await workerInstance.shutdown?.();
    } catch (error) {
      console.error('[Service] Error during worker shutdown:', error);
    } finally {
      workerInstance = null;
      initializationPromise = null;
    }
  }
}

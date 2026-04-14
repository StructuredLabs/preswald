import * as Comlink from 'comlink';
import { createLogger } from '../lib/logger';

const logger = createLogger('Service');

// import PreswaldWorker from './worker.js?worker&inline';   // ← change

let workerInstance = null;

export function createWorker() {
  // If we're already initialized, return the existing worker
  if (workerInstance) {
    logger.debug('[Service] Reusing existing worker instance');
    return workerInstance;
  }

  logger.debug('[Service] Starting new worker initialization');
  try {
    const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
    //   const worker = new PreswaldWorker();                 // ← no URL needed
    workerInstance = Comlink.wrap(worker);
    return workerInstance;
  } catch (error) {
    logger.error('[Service] Worker initialization failed:', error);
    workerInstance = null;
    throw error;
  }
}

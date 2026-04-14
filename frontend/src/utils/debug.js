export const DEBUG = import.meta.env?.DEV ?? false;
export const debugLog = DEBUG ? console.log.bind(console) : () => {};
export const debugWarn = DEBUG ? console.warn.bind(console) : () => {};
export const debugError = DEBUG ? console.error.bind(console) : () => {};

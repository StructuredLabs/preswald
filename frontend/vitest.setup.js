import '@testing-library/jest-dom';
const store = {};
Object.defineProperty(globalThis, 'sessionStorage', {
  value: {
    getItem: (k) => store[k] || null,
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
    clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
  },
  writable: true,
});

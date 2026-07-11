import '@testing-library/jest-dom';

// Polyfill scrollIntoView for jsdom
Element.prototype.scrollIntoView = () => {};

// Polyfill crypto.randomUUID for jsdom
if (!globalThis.crypto?.randomUUID) {
  Object.defineProperty(globalThis, 'crypto', {
    value: {
      ...globalThis.crypto,
      randomUUID: () => Math.random().toString(36).slice(2) + Date.now().toString(36),
    },
  });
}

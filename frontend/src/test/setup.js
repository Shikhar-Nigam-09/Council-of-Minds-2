import '@testing-library/jest-dom';

// Mock scrollIntoView across both window and global prototype realms in jsdom
const noop = () => {};
if (typeof window !== 'undefined') {
  if (window.HTMLElement) window.HTMLElement.prototype.scrollIntoView = noop;
  if (window.Element) window.Element.prototype.scrollIntoView = noop;
}
if (typeof HTMLElement !== 'undefined') {
  HTMLElement.prototype.scrollIntoView = noop;
}
if (typeof Element !== 'undefined') {
  Element.prototype.scrollIntoView = noop;
}

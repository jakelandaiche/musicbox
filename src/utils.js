/**
 *   Helper functions
 *   @module
 */

export function debounce(callback, delay=1000) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      callback(...args);
    }, delay);
  };
}

export function throttle(callback, delay=1000) {
  let wait = false;

  return (...args) => {
    if (wait) return;

    callback(...args);
    wait = true;

    setTimeout(() => {
      wait = false;
    }, delay);
  };
}

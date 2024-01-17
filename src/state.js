/**
 *   Basic reactive state
 *   @module
 */

const state = {}
const handlers = {}

export function declare(init, name) {
  const sym = name === undefined ? Symbol() : Symbol(name)
  state[sym] = init
  handlers[sym] = []
  return sym
}

export function update(sym, value) {
  console.debug(`[STATE UPDATE] ${sym.description}: ${state[sym]} -> ${value}`)
  state[sym] = value
  handlers[sym].forEach(h => h(value))
}

export function retrieve(sym) {
  return state[sym]
}

export function bind(sym, handler) {
  handlers[sym].push(handler)
}
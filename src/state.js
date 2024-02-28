/**
 *   Basic reactive state
 *   @module
 */

/** Keeps track of current value for each state */
const state = {}
/** Keeps track of initial values for each state */
const inits = {}
/** Keeps track of change handlers for each state */
const handlers = {}

/** 
 * Creates a new state variable with a given name and initial value */
export function declare(init, name) {
  const sym = name === undefined ? Symbol() : Symbol(name)
  inits[sym] = init
  state[sym] = init
  handlers[sym] = []
  return sym
}

/** 
 * Updates a state variable's value, calling all bound handlers */
export function update(sym, value) {
  console.debug(`[STATE UPDATE] ${sym.description}: ${state[sym]} -> ${value}`)
  state[sym] = value
  handlers[sym].forEach(h => h(value))
}

/** 
 * Gets the current value of a state variable */
export function retrieve(sym) {
  return state[sym]
}

/** 
 * Adds a new callback to a state variable's handler list */
export function bind(sym, handler) {
  handlers[sym].push(handler)
}

/** 
 * Resets a state variable to its original value */
export function reset(sym) {
  state[sym] = inits[sym]
  handlers[sym].forEach(h => h(inits[sym]))
}

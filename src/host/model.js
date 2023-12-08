import { declare, update, bind, retrieve } from "/src/state.js";

export const state = declare("GAMESTART");
export const code = declare("####");

export const players = declare([]);
export const ready = declare([]);

export const colors = declare([]);
export const answers = declare([]);

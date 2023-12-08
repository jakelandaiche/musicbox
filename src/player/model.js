import { declare, update, bind, retrieve } from "/src/state.js";

export const state = declare("GAMESTART", "Game State");

export const code = declare("####", "Room Code");

export const Name = declare("", "Player Name");
export const color = declare("#000000", "Player Color");
export const answer = declare("", "Player Is Ready");

import { socket } from "../socket.js";
import { declare, update, bind, retrieve } from "../state.js";

export const STATE = declare("CONNECT", "Game State");
export const CODE = declare("####", "Room Code");

export const PLAYERS = declare([], "Player List");

export const READY = declare([], "Players Ready");

export const COLORS = declare([], "Player Colors");
export const ANSWERS = declare([], "Player Answers");

export const PLAYER_DATA = declare([], "Player Data");
export const ROUND_NUM = declare(0, "Round Number");

socket.addMessageHandler("init", (message) => {
  update(STATE, "LOBBY");
  update(CODE, message.code);
});
socket.addMessageHandler("state", (message) => {
  update(STATE, message.state);
});
socket.addMessageHandler("players", (message) => {
  update(PLAYERS, message.players);
});
socket.addMessageHandler("player_data", (message) => {
  update(PLAYER_DATA, message.player_data);
});
socket.addMessageHandler("round_num", (message) => {
  update(ROUND_NUM, message.round_num);
});

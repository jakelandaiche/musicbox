import { socket } from "/src/socket.js"
import { declare, update, bind, retrieve } from "/src/state.js"

export const STATE = declare("CONNECT", "Game State")
export const CODE = declare("####", "Room Code")

export const PLAYERS = declare([], "Player List")

export const READY = declare([], "Players Ready")

export const COLORS = declare([], "Player Colors")
export const ANSWERS = declare([], "Player Answers")

socket.addMessageHandler("init", (message) => {
  update(STATE, "LOBBY")
  update(CODE, message.code)
})
socket.addMessageHandler("state", (message) => {
  update(STATE, message.state)
})
socket.addMessageHandler("players", (message) => {
  update(PLAYERS, message.players)
})

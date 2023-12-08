import { socket } from "/src/socket.js"
import { declare, update, bind, retrieve } from "/src/state.js"

export const STATE = declare("CONNECT", "Page State")

export const CODE = declare("####", "Room Code")

export const NAME = declare("", "Player Name")

export const COLOR = declare("#000000", "Player Color")
export const READY = declare("", "Player Is Ready")

export const SUBMITTED = declare(false, "Player Submitted Answer")

bind(COLOR, c => {
  socket.send({
    type: "player_info",
    name: retrieve(NAME),
    ready: retrieve(READY),
    color: c 
  })
})

bind(READY, r => {
  socket.send({
    type: "player_info",
    name: retrieve(NAME),
    ready: r,
    color: retrieve(COLOR)
  })
})

socket.addMessageHandler("state", (message) => {
  update(STATE, message.state)
})

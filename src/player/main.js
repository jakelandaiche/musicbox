import { socket } from "/src/socket.js";
import { update } from "/src/state.js"

import { STATE, CODE } from "/src/player/model.js"
import * as View from "/src/player/view.js"

console.log("%cStarting MusicBox! (Player)", "font-size: 18px; font-weight: bold;");

View.initConnect()
View.initJoin()
View.initLobby()

console.info("Finished initializing view");

update(STATE, "CONNECT")

socket.onOpen(() => {
  update(STATE, "JOIN")
})
socket.onClose(() => {
  update(STATE, "CONNECT")
})
socket.addMessageHandler("init", (message) => {
  update(STATE, "LOBBY")
  update(CODE, message.code)
})


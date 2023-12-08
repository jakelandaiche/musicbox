import { socket } from "/src/socket.js";
import { update } from "/src/state.js"

import { state, code } from "/src/player/model.js"
import * as View from "/src/player/view.js"

console.log("%cStarting MusicBox! (Player)", "font-size: 18px; font-weight: bold;");

View.initConnect()
View.initJoin()
View.initGameStart()

console.info("Finished initializing view");

update(state, "CONNECT")

socket.onOpen(() => {
  update(state, "JOIN")
})
socket.onClose(() => {
  update(state, "CONNECT")
})
socket.addMessageHandler("init", (message) => {
  update(state, "GAMESTART")
  update(code, message.code)
})


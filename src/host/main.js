import { socket } from "/src/socket.js";
import { update } from "/src/state.js"

import { state, code } from "/src/host/model.js"
import * as View from "/src/host/view.js"

console.log("%cStarting MusicBox!", "font-size: 18px; font-weight: bold;");

View.initConnect()
View.initGameStart()
View.init

console.info("Finished initializing view");

update(state, "CONNECT")

socket.onOpen(() => {
  socket.send({
    type: "init"
  })
})
socket.onClose(() => {
  update(state, "CONNECT")
})
socket.addMessageHandler("init", (message) => {
  update(state, "GAMESTART")
  update(code, message.code)
})

import { socket } from "/src/socket.js";
import { update } from "/src/state.js"

import { STATE, CODE } from "/src/host/model.js"
import * as View from "/src/host/view.js"

console.log("%cStarting MusicBox!", "font-size: 18px; font-weight: bold;");

View.initVideoPlayer()
View.initViews()

console.info("Finished initializing view");

// Let's go !
update(STATE, "CONNECT")

socket.onOpen(() => {
  socket.send({
    type: "init"
  })
})
socket.onClose(() => {
  update(STATE, "CONNECT")
})

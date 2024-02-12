import { socket } from "../socket.js";
import { update } from "../state.js";

import { STATE, CODE } from "./model.js";
import * as View from "./view.js";

console.log("%cStarting MusicBox!", "font-size: 18px font-weight: bold;");

View.initVideoPlayer();
View.initViews();

console.info("Finished initializing view");

// Let's go !
update(STATE, "CONNECT");

socket.onOpen(() => {
  socket.send({
    type: "init",
  });
});

socket.init("ws://backend.drexel-musicbox.com:8080");

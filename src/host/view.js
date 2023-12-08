import { socket } from "/src/socket.js"
import { state, code, players } from "/src/host/model.js"
import { bind } from "/src/state.js"

const divs = {
  CONNECT: "div-connect",
  GAMESTART: "div-lobby",
}

bind(state, (s) => {
  Object.keys(divs)
    .forEach(k => {
      document.getElementById(divs[k]).style.display = "none"
    })
  document.getElementById(divs[s]).style.display = "block"
})


export function initConnect() {
  const connectform = document.getElementById("connectform")
  connectform.addEventListener("submit", (event) => {
    event.preventDefault(); // prevent browser from reloading (default behavior)

    // init socket
    const formData = new FormData(connectform);
    const ws_host = formData.get("ws-host");
    socket.init(ws_host) 
  });
}

export function initGameStart() {
  const codetext = document.getElementById("gamestart-codetext")
  const playerlist = document.getElementById("gamestart-playerlist")

  bind(code, (c) => {
    codetext.innerText = c
  })

  bind(players, (p) => {
    console.log(p);
  })
}

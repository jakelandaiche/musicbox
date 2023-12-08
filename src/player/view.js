import { socket } from "/src/socket.js"
import { STATE, NAME, COLOR, READY } from "/src/player/model.js"
import { update, bind } from "/src/state.js"

const divs = {
  CONNECT: "div-connect",
  JOIN: "div-join",
  LOBBY: "div-lobby",
  GAMESTART: "div-gamestart",
  ROUNDSTART: "div-roundstart",
  ROUNDCOLLECT: "div-roundcollect",
  ROUNDEND: "div-roundend",
  GAMEEND: "div-gameend",
}

bind(STATE, (s) => {
  Object.keys(divs)
    .forEach(k => {
      document.getElementById(divs[k]).style.display = "none"
    })
  document.getElementById(divs[s]).style.display = "block"
})

export function initConnect() {
  const connectform = document.getElementById("connectform")
  connectform.addEventListener("submit", (event) => {
    event.preventDefault() // prevent browser from reloading (default behavior)

    // init socket
    const formData = new FormData(connectform);
    const ws_host = formData.get("ws-host");
    socket.init(ws_host) 
  });
}

export function initJoin() {
  const joinform = document.getElementById("joinform")

  joinform.addEventListener("submit", (event) => {
    event.preventDefault(); // prevent browser from reloading (default behavior)

    // init socket
    const formData = new FormData(joinform);
    const name = formData.get("name");
    const code = formData.get("code");

    update(NAME, name)
    socket.send({
      type: "join",
      name: name,
      code: code,
    }) 
  });
}

export function initLobby() {
  const nametext = document.getElementById("lobby-nametext")
  const colorinput = document.getElementById("lobby-colorinput")
  const readyinput = document.getElementById("lobby-readyinput")

  colorinput.addEventListener("change", (event) => {
    update(COLOR, colorinput.value)
  })
  readyinput.addEventListener("change", (event) => {
    update(READY, readyinput.checked)
  })

  bind(NAME, (n) => {
    nametext.innerText = n
  })
}

export function initGameStart() {
}

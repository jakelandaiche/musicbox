import { socket } from "/src/socket.js"
import { state, Name } from "/src/player/model.js"
import { update, bind } from "/src/state.js"

const divs = {
  CONNECT: "div-connect",
  JOIN: "div-join",
  GAMESTART: "div-gamestart"
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

export function initJoin() {
  const joinform = document.getElementById("joinform")

  joinform.addEventListener("submit", (event) => {
    event.preventDefault(); // prevent browser from reloading (default behavior)

    // init socket
    const formData = new FormData(joinform);
    const name = formData.get("name");
    const code = formData.get("code");

    update(Name, name)
    socket.send({
      type: "join",
      name: name,
      code: code,
    }) 
  });
}

export function initGameStart() {
  const nametext = document.getElementById("gamestart-nametext")
  bind(Name, (n) => {
    nametext.innerText = n
  })
}

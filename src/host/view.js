import { socket } from "/src/socket.js"
import { STATE, CODE, PLAYERS, PLAYER_DATA, ROUND_NUM } from "/src/host/model.js"
import { bind } from "/src/state.js"

export const stateViews = {
  CONNECT: {
    div: "div-connect",
    init: () => {
      const connectform = document.getElementById("connectform")
      connectform.addEventListener("submit", (event) => {
        event.preventDefault(); // prevent browser from reloading (default behavior)

        // init socket
        const formData = new FormData(connectform);
        const ws_host = formData.get("ws-host");
        socket.init(ws_host) 
      });
    },
    reset: () => {
      const hostinput = document.getElementById("connectform-hostinput")
      hostinput.innerText = "ws://localhost:8080"
    },
  },

  LOBBY: {
    div: "div-lobby",
    init: () => {
      const codetext = document.getElementById("lobby-codetext")
      const playerlist = document.getElementById("lobby-playerlist")
      const startbtn = document.getElementById("lobby-startbtn")

      startbtn.addEventListener("click", (event) => {
        socket.send({
          type: "start"
        })
      })

      bind(CODE, (c) => {
        codetext.innerText = c
      })

      bind(PLAYERS, (p) => {
        while (playerlist.hasChildNodes())
          playerlist.removeChild(playerlist.firstChild)

        p.forEach(player => {
          const entry = document.createElement("p")
          entry.innerText = player.name + (player.ready ? " ✅" : "")
          entry.style.color = player.color
          playerlist.appendChild(entry)
        })
      })
    },
    reset: () => {
      const codetext = document.getElementById("lobby-codetext")
      const playerlist = document.getElementById("lobby-playerlist")

      codetext.innerText = ""
      while (playerlist.hasChildNodes())
        playerlist.removeChild(playerlist.firstChild)
    },
  },

  GAMESTART: {
    div: "div-gamestart",
    init: () => {
    },
    reset: () => {
    },
  },

  ROUNDSTART: {
    div: "div-roundstart",
    init: () => {
      const roundnumtext = document.getElementById("roundstart-roundnumtext")

      bind(ROUND_NUM, round_num => {
        roundnumtext.innerText = `Round ${round_num}`
      })
    },
    reset: () => {
    },
  },

  ROUNDCOLLECT: {
    div: "div-roundcollect",
    init: () => {
      const playerlist = document.getElementById("roundcollect-playerlist")

      bind(PLAYER_DATA, player_data => {
        while (playerlist.hasChildNodes())
          playerlist.removeChild(playerlist.firstChild)

        player_data
          .map(data => {
            const d = document.createElement("div")
            const p = document.createElement("p")
            p.innerText = data.name + (data.answer !== null ? " ✅" : "") + ` (${data.total})`

            p.style.color = data.color

            const p2 = document.createElement("p")
            p2.innerText = (data.answer !== null ? "*".repeat(data.answer.length) : "")

            d.appendChild(p)
            d.appendChild(p2)

            return d
          })
          .forEach(elem => playerlist.appendChild(elem))
      })
    },
    reset: () => {

    },
  },

  ROUNDEND: {
    div: "div-roundend",
    init: () => {
      const playerlist = document.getElementById("roundend-playerlist")

      bind(PLAYER_DATA, player_data => {
        while (playerlist.hasChildNodes())
          playerlist.removeChild(playerlist.firstChild)

        player_data
          .map(data => {
            const d = document.createElement("div")
            const p = document.createElement("p")
            p.innerText = data.name + (data.answer !== null ? " ✅" : "") + ` (${data.total})`
            p.style.color = data.color

            const p2 = document.createElement("p")
            p2.innerText = (data.answer !== null ? data.answer : "")

            const p3 = document.createElement("p")
            p3.innerText = `Score: ${data.score}`

            d.appendChild(p)
            d.appendChild(p2)
            d.appendChild(p3)

            return d
          })
          .forEach(elem => playerlist.appendChild(elem))
      })
    },
    reset: () => {},
  },

  GAMEEND: {
    div: "div-gameend",
    init: () => {
      const playerlist = document.getElementById("gameend-playerlist")

      bind(PLAYER_DATA, player_data => {
        while (playerlist.hasChildNodes())
          playerlist.removeChild(playerlist.firstChild)

        player_data
          .map(data => {
            const d = document.createElement("div")
            const p = document.createElement("p")
            p.innerText = data.name 
            p.style.color = data.color

            const p2 = document.createElement("p")
            p2.innerText = `Final score: ${data.total}`

            d.appendChild(p)
            d.appendChild(p2)

            return d
          })
          .forEach(elem => playerlist.appendChild(elem))
      })
    },
    reset: () => {},
  },
}

const divs = {
  CONNECT: "div-connect",
  LOBBY: "div-lobby",
  GAMESTART: "div-gamestart",
  ROUNDSTART: "div-roundstart",
  ROUNDCOLLECT: "div-roundcollect",
  ROUNDEND: "div-roundend",
  GAMEEND: "div-gameend",
}

bind(STATE, (s) => {
  Object.keys(stateViews)
    .forEach(k => {
      document.getElementById(stateViews[k].div).style.display = "none"
    })
  Object.keys(stateViews)
    .forEach(k => stateViews[k].reset())
  document.getElementById(stateViews[s].div).style.display = "block"
})

export function initViews() {
  Object.keys(stateViews)
    .forEach(k => stateViews[k].init())
}

export function initVideoPlayer() {
  socket.addMessageHandler("video", (message) => {
    play_video(message.id, message.start_time, message.start_time + 10)
  })
}

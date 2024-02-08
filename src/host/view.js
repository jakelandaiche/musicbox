import { socket } from "../socket.js"
import { bind, retrieve, update } from "../state.js"
import {
  STATE,
  CODE,
  PLAYERS,
  ROUND_NUM,
} from "./model.js"

function getRandomColor() {
  const letters = "0123456789ABCDEF";
  let color = "#";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

const colors = [];
for (let x = 0; x < 25; x++) {
  colors.push(getRandomColor());
}

export const stateViews = {
  CONNECT: {
    div: "div-connect",
    init: () => {
      const connectform = document.getElementById("connectform")
      connectform.addEventListener("submit", (event) => {
        event.preventDefault() // prevent browser from reloading (default behavior)

        // init socket
        const formData = new FormData(connectform)
        const ws_host = formData.get("ws-host")
        socket.init(ws_host)
      })
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
      const startbtn = document.getElementById("lobby-startbtn")
      const datasetselect = document.getElementById("lobby-datasetselect")

      datasetselect.addEventListener("change", (event) => {
        socket.send({
          type: "dataset",
          dataset: event.target.value
        })
      })
      startbtn.addEventListener("click", (event) => {
        socket.send({
          type: "start",
        })
      })
      bind(CODE, (c) => {
        codetext.innerText = c
      })
      bind(PLAYERS, (players) => {
        // startbtn.disabled = players.length < 3
      })
      update(PLAYERS, [])
    },
    reset: () => {
      const codetext = document.getElementById("lobby-codetext")
      codetext.innerText = ""
    },
  },

  GAMESTART: {
    div: "div-gamestart",
    init: () => {},
    reset: () => {},
  },

  ROUNDSTART: {
    div: "div-roundstart",
    init: () => {
      const roundnumtext = document.getElementById("roundstart-roundnumtext")

      bind(ROUND_NUM, (round_num) => {
        roundnumtext.innerText = `Round ${round_num}`
      })
    },
    reset: () => {},
  },

  ROUNDCOLLECT: {
    div: "div-roundcollect",
    init: () => {},
    reset: () => {},
  },

  ROUNDEND: {
    div: "div-roundend",
    init: () => {},
    reset: () => {},
  },

  GAMEEND: {
    div: "div-gameend",
    init: () => {},
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
  Object.keys(stateViews).forEach((k) => {
    document.getElementById(stateViews[k].div).style.display = "none"
  })
  Object.keys(stateViews).forEach((k) => stateViews[k].reset())
  document.getElementById(stateViews[s].div).style.display = "block"
})

export function initViews() {
  Object.keys(stateViews).forEach((k) => stateViews[k].init())
}

export function initVideoPlayer() {
  socket.addMessageHandler("video", (message) => {
    play_video(message.id, message.start_time, message.start_time + 10)
  })
}

function renderPlayer(player) {
  const div = document.createElement("div")
  div.style.display = "flex"
  div.style.flexDirection = "column"
  div.style.justifyContent = "flex-start"
  div.style.alignItems = "center"
  div.style.border = `5px solid ${player.color}`
  div.style.grid = "50%"

  const state = retrieve(STATE)

  const entry = document.createElement("p")
  entry.innerText = player.name 
  entry.style.fontSize = "18pt"
  entry.style.fontWeight = "bold"
  entry.innerText += player.connected ? "" : " 🔌"

  const score = document.createElement("p")
  score.style.fontSize = "22pt"
  score.innerText = player.score

  const answerDiv = document.createElement("div")

  div.appendChild(entry)
  switch (state) {
    case "LOBBY":
      entry.innerText += player.ready ? " ✅" : ""
      break
    case "GAMESTART":
      entry.innerText += ` [${player.total}]`
      break;
    case "ROUNDSTART":
      entry.innerText += ` [${player.total}]`
      div.style.justifyContent = "space-between"
      break
    case "ROUNDCOLLECT":
      entry.innerText += ` [${player.total}]`
      const hiddenanswer = document.createElement("p")
      hiddenanswer.innerText = player.answer !== null ? "* ".repeat(player.answer.length) : ""
      answerDiv.appendChild(hiddenanswer)
      div.appendChild(answerDiv)
      break
    case "ROUNDEND":
      entry.innerText += ` [${player.total}]`
      const fullanswer = document.createElement("p")
      const color_list = player.color_list;
      raw_answer = player.answer !== null ? player.answer : ""
      fullanswer.innerText = raw_answer.split(" ")
        .map((word, i) => 
          color_list[i] == 0 ? 
            words[i] 
          :
            `<span style="color: ${colors[color_list[i]]};">${word}</span>`
        )
        .join(" ");
      div.appendChild(fullanswer)
      div.appendChild(score)
      div.style.justifyContent = "space-between"
      break
    case "GAMEEND":
      entry.innerText += ` [${player.total}]`
      break
  }

  return div
}

bind(STATE, (s) => {
  if (s != "CONNECT") {
    document.getElementById("playerdiv").style.display = "flex"
  } else {
    document.getElementById("playerdiv").style.display = "none"
  }
})

const playerlist = document.getElementById("playerlist")
const playercount = document.getElementById("playercount")

bind(PLAYERS, (players) => {
  renderPlayers(players)
})
bind(STATE, () => {
  renderPlayers(retrieve(PLAYERS))
})

function renderPlayers(players) {
  // Clear player list div
  while (playerlist.hasChildNodes())
    playerlist.removeChild(playerlist.firstChild)

  players.map(renderPlayer)
    .forEach(div => playerlist.appendChild(div))
  playercount.innerText = `(${players.length}/8)`

  for (let i = 0; i < 8-players.length; i++) {
    const div = document.createElement("div")
    div.style.border = "5px solid #A9A9A9"
    div.style.grid = "50%"
    playerlist.appendChild(div)
  }
}

const rank = document.getElementById("rankdiv")

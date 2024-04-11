import { socket } from "../socket.js";
import { bind, retrieve, update } from "../state.js";
import { STATE, CODE, PLAYERS, ROUND_NUM } from "./model.js";

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
      const connectform = document.getElementById("connectform");
      connectform.addEventListener("submit", (event) => {
        event.preventDefault(); // prevent browser from reloading (default behavior)

        // init socket
        const formData = new FormData(connectform);
        const ws_host = formData.get("ws-host");
        socket.init(ws_host);
      });
    },
    reset: () => {
      const hostinput = document.getElementById("connectform-hostinput");
      hostinput.innerText = "wss://backend.drexel-musicbox.com:8080";
    },
  },

  LOBBY: {
    div: "div-lobby",
    init: () => {
      const codetext = document.getElementById("lobby-codetext");
      const startbtn = document.getElementById("lobby-startbtn");
      const datasetselect = document.getElementById("lobby-datasetselect");
      const nroundsinput = document.getElementById("lobby-nroundsinput");
      const tutorialinput = document.getElementById("lobby-tutorialinput");

      datasetselect.addEventListener("change", (event) => {
        socket.send({
          type: "dataset",
          dataset: event.target.value,
        });
      });

      nroundsinput.addEventListener("change", (event) => {
        socket.send({
          type: "nrounds",
          nrounds: event.target.value,
        });
      });

      startbtn.addEventListener("click", (event) => {
        socket.send({
          type: "start",
          tutorial: tutorialinput.checked
        });
      });
      bind(CODE, (c) => {
        codetext.innerText = c;
      });
      bind(PLAYERS, (players) => {
        // startbtn.disabled = players.length < 3
      });
      update(PLAYERS, []);
    },
    reset: () => {
      const nroundsinput = document.getElementById("lobby-nroundsinput");
      nroundsinput.value = "5";
    },
  },

  GAMESTART: {
    div: "div-gamestart",
    init: () => {},
    reset: () => {},
  },

  FAKEROUNDSTART: {
    div: "div-fakeroundstart",
    init: () => {},
    reset: () => {},
  },
  FAKEROUNDCOLLECT: {
    div: "div-fakeroundcollect",
    init: () => {},
    reset: () => {},
  },
  FAKEROUNDEND: {
    div: "div-fakeroundend",
    init: () => {},
    reset: () => {},
  },
  FAKEROUNDEND2: {
    div: "div-fakeroundend2",
    init: () => {},
    reset: () => {},
  },

  ROUNDSTART: {
    div: "div-roundstart",
    init: () => {
      const roundnumtext = document.getElementById("roundstart-roundnumtext");

      bind(ROUND_NUM, (round_num) => {
        roundnumtext.innerText = `Round ${round_num}`;
      });
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
    init: () => {
      const restartbtn = document.getElementById("gameend-restartbtn");
      restartbtn.addEventListener("click", (event) => {
        socket.send({
          type: "restart",
        });
      });
    },
    reset: () => {},
  },
};

const divs = {
  CONNECT: "div-connect",
  LOBBY: "div-lobby",
  GAMESTART: "div-gamestart",
  ROUNDSTART: "div-roundstart",
  ROUNDCOLLECT: "div-roundcollect",
  ROUNDEND: "div-roundend",
  GAMEEND: "div-gameend",
};

bind(STATE, (s) => {
  Object.keys(stateViews).forEach((k) => {
    document.getElementById(stateViews[k].div).style.display = "none";
  });
  Object.keys(stateViews).forEach((k) => stateViews[k].reset());
  console.log(stateViews);
  if (s in stateViews) {
    document.getElementById(stateViews[s].div).style.display = "block";
  }
});

export function initViews() {
  Object.keys(stateViews).forEach((k) => stateViews[k].init());
}

export function initVideoPlayer() {
  socket.addMessageHandler("video", (message) => {
    play_video(message.id, message.start_time, message.start_time + 10);
  });
}

function renderPlayer(player) {
  const div = document.createElement("div");
  div.style.display = "flex";
  div.style.flexDirection = "column";
  div.style.justifyContent = "flex-start";
  div.style.alignItems = "center";
  div.style.border = `5px solid ${player.color}`;
  div.style.grid = "50%";

  const state = retrieve(STATE);

  const entry = document.createElement("p");
  entry.innerText = player.name;
  entry.style.fontSize = "18pt";
  entry.style.fontWeight = "bold";
  entry.innerText += player.connected ? "" : " 🔌";

  const score = document.createElement("p");
  score.style.fontSize = "22pt";
  score.innerText = Math.round(player.score);

  const answerDiv = document.createElement("div");

  div.appendChild(entry);
  switch (state) {
    case "LOBBY":
      entry.innerText += player.ready ? " ✅" : "";
      break;
    case "GAMESTART":
      entry.innerText += ` [${Math.round(player.total)}]`;
      break;
    case "FAKEROUNDSTART":
      break;
    case "FAKEROUNDCOLLECT":
      {
        const hiddenanswer = document.createElement("p");
        hiddenanswer.innerText =
          player.answer !== null ? "* ".repeat(player.answer.length) : "";
        answerDiv.appendChild(hiddenanswer);
        div.appendChild(answerDiv);
      }
      break;
    case "FAKEROUNDEND":
      {
        const fullanswer = document.createElement("p");
        console.log(player.color_list);
        console.log(player.answer);
        const color_list = player.color_list;
        const raw_answer = player.answer !== null ? player.answer : "";
        fullanswer.innerHTML = raw_answer
          .split(" ")
          .map((word, i) =>
            color_list[i] == 0
              ? word
              : `<span style="color: ${colors[color_list[i]]};">${word}</span>`
          )
          .join(" ");
        console.log(fullanswer.innerHTML);
        div.appendChild(fullanswer);
        div.appendChild(score);
        div.style.justifyContent = "space-between";
      }
      break;
    case "FAKEROUNDEND2":
      {
        entry.innerText += ` [${Math.round(player.total)}]`;
        const fullanswer = document.createElement("p");
        console.log(player.color_list);
        console.log(player.answer);
        const color_list = player.color_list;
        const raw_answer = player.answer !== null ? player.answer : "";
        fullanswer.innerHTML = raw_answer
          .split(" ")
          .map((word, i) =>
            color_list[i] == 0
              ? word
              : `<span style="color: ${colors[color_list[i]]};">${word}</span>`
          )
          .join(" ");
        console.log(fullanswer.innerHTML);
        const breakdown = document.createElement("div");
        var sim = document.createElement("div");
        var matches = document.createElement("div");
        var bonus = document.createElement("div");
        sim.textContent = "Similarity: " + player.score_info.similarity;
        matches.textContent = "Matches: " + player.score_info.matches;
        bonus.textContent = "Bonus: " + player.score_info.bonus;
        breakdown.appendChild(sim);
        breakdown.appendChild(matches);
        breakdown.appendChild(bonus);
        breakdown.style.fontSize = "small";
        div.appendChild(fullanswer);
        div.appendChild(breakdown);
        div.appendChild(score);
        div.style.justifyContent = "space-between";
      }
      break;
    case "ROUNDSTART":
      entry.innerText += ` [${Math.round(player.total)}]`;
      div.style.justifyContent = "space-between";
      break;
    case "ROUNDCOLLECT":
      entry.innerText += ` [${Math.round(player.total)}]`;
      const hiddenanswer = document.createElement("p");
      hiddenanswer.innerText =
        player.answer !== null ? "* ".repeat(player.answer.length) : "";
      answerDiv.appendChild(hiddenanswer);
      div.appendChild(answerDiv);
      break;
    case "ROUNDEND":
      entry.innerText += ` [${Math.round(player.total)}]`;
      const fullanswer = document.createElement("p");
      const color_list = player.color_list;
      const raw_answer = player.answer !== null ? player.answer : "";
      fullanswer.innerHTML = raw_answer
        .split(" ")
        .map((word, i) =>
          color_list[i] == 0
            ? word
            : `<span style="color: ${colors[color_list[i]]};">${word}</span>`
        )
        .join(" ");
      const breakdown = document.createElement("div");
      var sim = document.createElement("div");
      var matches = document.createElement("div");
      var bonus = document.createElement("div");
      sim.textContent = "Similarity: " + player.score_info.similarity;
      matches.textContent = "Matches: " + player.score_info.matches;
      bonus.textContent = "Bonus: " + player.score_info.bonus;
      breakdown.appendChild(sim);
      breakdown.appendChild(matches);
      breakdown.appendChild(bonus);
      breakdown.style.fontSize = "small";
      div.appendChild(fullanswer);
      div.appendChild(breakdown);
      div.appendChild(score);
      div.style.justifyContent = "space-between";
      break;
    case "GAMEEND":
      entry.innerText += ` [${Math.round(player.total)}]`;
      const stats = document.createElement("ul");
      var len = document.createElement("li");
      var uniq = document.createElement("li");
      len.textContent = player.score_info.avg_len;
      uniq.textContent = player.score_info.unique_words;
      div.appendChild(stats);
      break;
  }

  return div;
}

bind(STATE, (s) => {
  if (s != "CONNECT") {
    document.getElementById("playerdiv").style.display = "flex";
  } else {
    document.getElementById("playerdiv").style.display = "none";
  }
});

const playerlist = document.getElementById("playerlist");
const playercount = document.getElementById("playercount");

bind(PLAYERS, (players) => {
  renderPlayers(players);
});
bind(STATE, () => {
  renderPlayers(retrieve(PLAYERS));
});

function roundSort(a, b) {
  if (a.score > b.score) {
    return -1;
  } else if (a.score < b.score) {
    return 1;
  } else {
    return 0;
  }
}

function renderPlayers(players) {
  // Clear player list div
  while (playerlist.hasChildNodes())
    playerlist.removeChild(playerlist.firstChild);

  players.sort(roundSort);
  players.map(renderPlayer).forEach((div) => playerlist.appendChild(div));
  playercount.innerText = `(${players.length}/8)`;

  for (let i = 0; i < 8 - players.length; i++) {
    const div = document.createElement("div");
    div.style.border = "5px solid #A9A9A9";
    div.style.grid = "50%";
    playerlist.appendChild(div);
  }
}

const rank = document.getElementById("rankdiv");

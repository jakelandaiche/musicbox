import { socket } from "../socket.js";
import { sleep } from "../utils.js";
import { bind, retrieve, update } from "../state.js";
import { STATE, STATE_DURATION, CODE, PLAYERS, ROUND_NUM, MATCHLIST } from "./model.js";

import { CONNECT } from "./views/connect.js"
import { LOBBY } from "./views/lobby.js"
import { GAMESTART } from "./views/gamestart.js"
import { GAMEEND } from "./views/gameend.js"
import { FAKEROUNDSTART, FAKEROUNDCOLLECT, FAKEROUNDEND, FAKEROUNDEND2 } from "./views/tutorial.js"
import { ROUNDSTART, ROUNDCOLLECT, ROUNDEND } from "./views/round.js"

function getRandomColor() {
  const letters = "0123456789ABCDEF";
  let color = "#";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

const colors = [];
for (let x = 0; x < 100; x++) {
  colors.push(getRandomColor());
}

const stateViewMap = {
  CONNECT: CONNECT,
  LOBBY: LOBBY,
  GAMESTART: GAMESTART,
  GAMEEND: GAMEEND,

  ROUNDSTART: ROUNDSTART,
  ROUNDCOLLECT: ROUNDCOLLECT,
  ROUNDEND: ROUNDEND,

  FAKEROUNDSTART: FAKEROUNDSTART,
  FAKEROUNDCOLLECT: FAKEROUNDCOLLECT,
  FAKEROUNDEND: FAKEROUNDEND,
  FAKEROUNDEND2: FAKEROUNDEND2,
}

bind(STATE, (s) => {
  for (const [state, view] of Object.entries(stateViewMap)) {
    if (s == state) {
      view.show()
    } else {
      view.hide()
    }
  }
});

export function initViews() {
  Object.values(stateViewMap).forEach(view => view.init())
}

export function initVideoPlayer() {
  socket.addMessageHandler("video", (message) => {
    play_video(message.id, message.start_time, message.start_time + 10);
  });
}

const playerlist = document.getElementById("playerlist");

async function renderPlayer(player) {
  const div = document.createElement("div");
  playerlist.appendChild(div)
  div.classList.add("playercard");
  div.style.display = "flex";
  div.style.flexDirection = "column";
  div.style.justifyContent = "flex-start";
  div.style.alignItems = "center";
  div.style.border = `10px solid ${player.color}`;
  div.style.grid = "50%";

  const state = retrieve(STATE);
  const matchlist = retrieve(MATCHLIST)

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
    case "FAKEROUNDEND":
      {
        const fullanswer = document.createElement("p");
        console.log(player.answer);
        const raw_answer = player.answer !== null ? player.answer : "";
        fullanswer.innerHTML = raw_answer
        console.log(fullanswer.innerHTML);
        div.appendChild(fullanswer);
        div.appendChild(score);
        div.style.justifyContent = "space-between";
      }
      break;
    case "FAKEROUNDSTART":
    case "ROUNDSTART":
      entry.innerText += ` [${Math.round(player.total)}]`;
      div.style.justifyContent = "space-between";
      break;
    case "FAKEROUNDCOLLECT":
    case "ROUNDCOLLECT":
      entry.innerText += ` [${Math.round(player.total)}]`;
      const hiddenanswer = document.createElement("p");
      hiddenanswer.innerText =
        player.answer !== null ? "* ".repeat(player.answer.length) : "";
      answerDiv.appendChild(hiddenanswer);
      div.appendChild(answerDiv);
      break;
    case "FAKEROUNDEND2":
    case "ROUNDEND":
      entry.innerText += ` [${Math.round(player.total)}]`;
      if (player.score_info === null) break;
      const fullanswer = document.createElement("p");
      const raw_answer = player.answer !== null ? player.answer : "";
      fullanswer.innerHTML = raw_answer
        .replace(/[a-zA-Z]+/g, word => {
          const idx = matchlist.indexOf(word.toLowerCase())
          console.log(idx)
          return idx === -1 ?
            word : `<span style="color: ${colors[idx]};">${word}</span>` 
        })
      const breakdown = document.createElement("div");
      var sim = document.createElement("div");
      var matches = document.createElement("div");
      var bonus = document.createElement("div");
      sim.textContent = "Semantic Similarity: " + player.score_info.similarity;
      matches.textContent = "Matches: " + player.score_info.matches;
      bonus.textContent = "Multiplier from matches: " + player.score_info.bonus;
      div.appendChild(fullanswer);
      div.appendChild(breakdown);
      breakdown.style.fontSize = "small";
      div.style.justifyContent = "space-between";
      await sleep(1000);
      breakdown.appendChild(sim);
      await sleep(1000);
      breakdown.appendChild(matches);
      await sleep(1000);
      breakdown.appendChild(bonus);
      await sleep(1000);
      div.appendChild(score);
      await sleep(4000);
      break;
    case "GAMEEND":
      entry.innerText += ` [${Math.round(player.total)}]`;
      const stats = document.createElement("ul");
      var len = document.createElement("li");
      var uniq = document.createElement("li");
      len.textContent = "Average word length: " + Math.floor(parseInt(player.avg_len));
      uniq.textContent = "Unique words written: " + parseInt(player.unique_words);
      stats.appendChild(len);
      stats.appendChild(uniq);
      div.appendChild(stats);
      await sleep(4000);
      break;
  }

  return div;
}

bind(STATE, async (s) => {
  if (s != "CONNECT") {
    document.getElementById("playerdiv").style.display = "flex";
  } else {
    document.getElementById("playerdiv").style.display = "none";
  }
  await renderPlayers(retrieve(PLAYERS));
  // set off timer
});


bind(PLAYERS, async (players) => {
  await renderPlayers(players);
});

function roundSort(a, b) {
  if (a.score > b.score) {
    return 1;
  } else if (a.score < b.score) {
    return -1;
  } else {
    return 0;
  }
}

async function renderPlayers(players) {
  // Clear player list div
  while (playerlist.hasChildNodes())
    playerlist.removeChild(playerlist.firstChild);

  players.sort(roundSort);

  for (let i = 0; i < players.length; i++) {
    const div = await renderPlayer(players[i])
  }

  for (let i = 0; i < 8 - players.length; i++) {
    const div = document.createElement("div");
    div.classList.add("emptycard");
    div.style.grid = "50%";
    playerlist.appendChild(div);
  }
}


const rank = document.getElementById("rankdiv");

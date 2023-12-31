const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

var socket = null;

function setupPlayer() {}

function hideSection(id) {
  document.getElementById(id).style.visibility = "hidden";
}

function showSection(id) {
  document.getElementById(id).style.visibility = "visible";
}

// Socket Connection
var connectform = document.getElementById("connect");
connectform.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(connectform);
  const data = {};
  for (const [key, value] of formData.entries()) {
    data[key] = value;
  }

  const ws_host = data["ws-host"];

  // Only care if socket is closed or null!
  if (socket !== null && socket.readyState !== 3) return;

  socket = new WebSocket(ws_host);
  const close_socket = () => socket.close();

  socket.addEventListener("open", (event) => {
    console.log({
      user: "system",
      text: `Connected to ${ws_host} successfully`,
    });
    connectform.remove();
    document.getElementById("room_div").style.visibility = "visible";
  });

  socket.addEventListener("error", (event) => {
    push_message(`WebSocket error: ${event}`);
  });

  socket.addEventListener("message", (event) => {
    let data = JSON.parse(event.data);
    console.log(data);
    switch (data.type) {
      case "init":
        let l = document.createElement("p");
        l.innerHTML = "Room code: " + data.join;
        room_div.replaceChildren(l);
        break;
      case "message":
        push_message(data);
        break;
      case "video":
        embedVideo(data);
        break;
      case "user_init":
        setupPlayer();
        break;
      case "begin":
        startGame();
      default:
        break;
    }
  });
  socket.addEventListener("close", (event) => {
    push_message(`Connection to ${ws_host} closed: ${event.reason}`);
    closebtn.removeEventListener("click", close_socket);
    types.forEach((t) => {
      document.getElementById(t).onsubmit = null;
    });

    socket = null;
  });
});

document.getElementById("join_button").addEventListener("click", () => {
  var code = document.getElementById("room_id_entry").value;
  socket.send(
    JSON.stringify({
      type: "init",
      join: code,
    })
  );
  document.getElementById("room_div").remove();
  document.getElementById("player_create_div").style.visibility = "visible";
});

document.getElementById("name_submit").addEventListener("click", () => {
  var name = document.getElementById("player_name_text").value;
  var id = name + Math.floor(Math.random() * 100).toString();

  // Expires in 30 minutes worth of milliseconds
  document.cookie =
    "playerID=" +
    id +
    ";exipires=" +
    new Date(Date.now() + 1800000).toGMTString();

  socket.send(
    JSON.stringify({
      type: "player_data",
      username: name,
      id: id,
    })
  );

  document.getElementById("player_create_div").remove();
});

function startGame() {
  hideSection("player_wait_div");
  showSection("audio_wait_div");
  waitForAudio();
}

// State machine:
//     1. Music is playing, wait for signal
//     2. Sound finished, so write out answer
//     3. Answer is submitted, wait for score to complete

async function waitForScores() {
  await sleep(10000);
  hideSection("score_wait_div");
  showSection("audio_wait_div");
  waitForAudio();
}

function submitDescription() {
  var text = document.getElementById("description_text").value;
  socket.send(
    JSON.stringify({
      type: "answer",
      text: text,
    })
  );
  hideSection("freeform_answer_div");
  showSection("score_wait_div");
  waitForScores();
}

async function waitForAudio() {
  await sleep(10000);
  hideSection("audio_wait_div");
  showSection("freeform_answer_div");
}

document
  .getElementById("description_submit")
  .addEventListener("click", submitDescription);

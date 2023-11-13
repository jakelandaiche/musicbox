var socket = null;
var messages = document.getElementById("messages");

function push_message(data) {
  const p = document.createElement("p");
  p.innerHTML = `${data.user}: ${data.text}`;
  messages.append(p);
  messages.scrollTop = messages.scrollHeight;
}

function submit(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const data = { type: event.target.id };
  for (const [key, value] of formData.entries()) {
    data[key] = value;
  }

  const payload = data;
  socket.send(JSON.stringify(payload));
}

function embedVideo(data) {
  var player = new YT.Player("player", {
    height: "390",
    width: "640",
    videoId: data.id,
    playerVars: {
      playsinline: 1,
    },
    events: {
      onReady: onPlayerReady,
      onStateChange: onPlayerStateChange,
    },
  });
}

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

  push_message({
    user: "system",
    text: `Attempting to connect to ${ws_host}...`,
  });
  socket = new WebSocket(ws_host);
  const closebtn = document.getElementById("close-ws");
  const close_socket = () => socket.close();
  const rhc = document.getElementById("rhc");

  socket.addEventListener("open", (event) => {
    push_message({
      user: "system",
      text: `Connected to ${ws_host} successfully`,
    });
    rhc.style.visibility = "visible";

    closebtn.addEventListener("click", close_socket);
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
      case "player_data":
        push_message({
          user: "system",
          text: `${data.username} has joined.`
        })
        break;
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
    rhc.style.visibility = "hidden";
  });
});

document.getElementById("begin_button").addEventListener("click", () => {
  socket.send(
    JSON.stringify({
      type: "begin"
    })
  )
})

// Initialize room buttons
var join_button = document.getElementById("join_button");
var create_button = document.getElementById("create_button");

join_button.addEventListener("click", function () {
  var code = document.getElementById("room_id_entry").value;
  socket.send(
    JSON.stringify({
      type: "init",
      join: code,
    })
  );
});

create_button.addEventListener("click", function () {
  socket.send(
    JSON.stringify({
      type: "init",
    })
  );
});

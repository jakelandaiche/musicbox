var interval;
var socket = null;

function embedVideo(data) {
    console.log("playing video")
  const { id, start_time } = data
  if (!playerReady) return

  player.loadVideoById({videoId: id, startSeconds: start_time, endSeconds:start_time+10})

    player.playVideo();
}

function push_message(msg) {
  console.log(msg)
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
    socket.send(
      JSON.stringify({
          type: "init",
      })
    );
  });

  socket.addEventListener("error", (event) => {
    push_message(`WebSocket error: ${event}`);
  });

  socket.addEventListener("message", (event) => {
    let data = JSON.parse(event.data);
    console.log(data);
    switch (data.type) {
      case "init":
        room_div.innerHTML = "Room code: " + data.join;
        break;
      case "message":
        push_message(data);
        break;
      case "video":
        embedVideo(data);
        break;
      case "update":
        const names = data.players.map((player) => {
            if (data.show_answers === false) {
                return player.name
            } else {
                return player.name + ': ' + player.answer
            }
        }).join("<br>");
        document.getElementById("player_list").innerHTML = names;
        document.getElementById("room_text").innerHTML = data.text;
      case "countdown":
        clearInterval(interval);
        let T = data.time;
        document.getElementById("countdown").innerHTML = T ? T : "";
        interval = setInterval(() => {
            if (T > 0) {
                document.getElementById("countdown").innerHTML = T;
                T -= 1;
            } else {
                document.getElementById("countdown").innerHTML = "";
                clearInterval(interval);
            }
        }, 1000);
        break;
        break;

      default:
        break;
    }
  });
  socket.addEventListener("close", (event) => {
    push_message(`Connection to ${ws_host} closed: ${event.reason}`);
    // closebtn.removeEventListener("click", close_socket);
    /* types.forEach((t) => {
      document.getElementById(t).onsubmit = null;
    }); */

    socket = null;
  });
});

document.getElementById("start_button").addEventListener("click", (event) => {
    if (socket === null || socket.readyState === 3) return;
    
    socket.send(
      JSON.stringify({
          type: "start",
      })
    );
    document.getElementById("start_button").style.display = "none";
    
});


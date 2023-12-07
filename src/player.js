import { socket } from "./socket.js"

const playerdiv = document.getElementById("div-player");
const playerstartdiv = document.getElementById("div-playerstart");

const roomcodeform = document.getElementById("form-roomcode");

socket.addMessageHandler("join", (message) => {
  console.log("Successfully joined room");
  document.getElementById("h2-username").innerText = message.username
  playerstartdiv.style.display = "block";
  roomcodeform.style.display = "none";
});


roomcodeform.addEventListener("submit", (event) => {
  event.preventDefault()
  const formData = new FormData(roomcodeform);
  code = formData.get("roomcode")
  name = formData.get("username")
  console.log(`Trying to enter room ${code}...`)

  socket.send({
    type: "join",
    code: code, 
    name: name,
  });
});


const colorinput = document.getElementById("input-color");
colorinput.addEventListener("change", (event) => {
  socket.send({ type: "color", color: event.target.value });
  document.getElementById("h2-username").style.color = event.target.value;
});


const readyinput = document.getElementById("input-ready");
readyinput.addEventListener("change", (event) => {
  socket.send({ type: "ready", ready: readyinput.checked });
})


function init_player() {
  playerdiv.style.display = "block";
}

function reset_player() {
  roomcodeform.style.display = "flex";
  playerstartdiv.style.display = "none";
  playerdiv.style.display = "none";
}

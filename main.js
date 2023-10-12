var messages = document.getElementById("messages");
var chatform = document.getElementById("chat");
var textarea = document.getElementById("chat_textarea");
var username = document.getElementById("chat_username");

var socket = new WebSocket("ws://localhost:8080/");

socket.addEventListener("open", (event) => {
    console.log("WebSocket connection opened");
});

socket.addEventListener("close", (event) => {
    console.log("WebSocket connection closed");
});

socket.addEventListener("message", (event) => {
    let p = document.createElement("p");
    let data = JSON.parse(event.data);
    p.innerHTML = `${data.user}: ${data.text}`;
    messages.append(p);
});

chatform.addEventListener("submit", (event) => {
    event.preventDefault();

    if (socket.readyState != 1) return;

    const payload = {
        user: username.value,
        text: textarea.value,
    };
    console.log("submitted");
    console.log(payload);
    console.log("stringified");
    console.log(JSON.stringify(payload));
    
    socket.send(JSON.stringify(payload));
});

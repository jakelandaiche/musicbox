var messages = document.getElementById("messages");
var chatform = document.getElementById("chat");
var textarea = document.getElementById("chat_textarea");
var username = document.getElementById("chat_username");
var room_div = document.getElementById("room_div");

var socket = new WebSocket("ws://localhost:8080/");

socket.addEventListener("open", (event) => {
    console.log("WebSocket connection opened");
});

socket.addEventListener("close", (event) => {
    console.log("WebSocket connection closed");
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
            let p = document.createElement("p");
            p.innerHTML = `${data.user}: ${data.text}`;
            messages.append(p);
            break;
        case "video":
            
    }
    
    
});

chatform.addEventListener("submit", (event) => {
    event.preventDefault();

    if (socket.readyState != 1) return;

    const payload = {
        type: "message",
        user: username.value,
        text: textarea.value,
    };

    textarea.value = "";

    console.log("submitted");
    console.log(payload);
    console.log("stringified");
    console.log(JSON.stringify(payload));
    
    socket.send(JSON.stringify(payload));
});

// Initialize room buttons
var join_button = document.getElementById("join_button");
var create_button = document.getElementById("create_button");

join_button.addEventListener("click", function() {
    var code = document.getElementById("room_id_entry").value;
    socket.send(JSON.stringify({
        type: "init",
        join: code
    }))

})

create_button.addEventListener("click", function() {
    socket.send(JSON.stringify({
        type: "init"
    }))
})

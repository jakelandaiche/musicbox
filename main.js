var socket = null;
var messages = document.getElementById("messages");

function push_message(str) {
    const p = document.createElement("p");
    p.innerHTML = str;
    messages.append(p);
    messages.scrollTop = messages.scrollHeight;
}
function submit (event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    const payload = data;
    socket.send(JSON.stringify(payload));
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

    push_message(`Attempting to connect to ${ws_host}...`);
    socket = new WebSocket(ws_host);
    const closebtn = document.getElementById("close-ws");
    const close_socket = () => socket.close();
    const rhc = document.getElementById("rhc");


    socket.addEventListener("open", (event) => {
        push_message(`Connected to ${ws_host} successfully`);
        rhc.style.visibility = "visible";

        types.forEach(t => {
            document.getElementById(t).onsubmit = submit;
            document.getElementById(t).style.display = "none";
        });
        document.getElementById("message").style.display = "block";

        closebtn.addEventListener("click", close_socket);
    });

    socket.addEventListener("error", (event) => {
        push_message(`WebSocket error: ${event}`);
    });

    socket.addEventListener("message", (event) => {
        const p = document.createElement("p");
        const data = JSON.parse(event.data);
        p.innerHTML = event.data;
        messages.append(p);
    });


    socket.addEventListener("close", (event) => {
        push_message(`Connection to ${ws_host} closed: ${event.reason}`);
        closebtn.removeEventListener("click", close_socket);
        types.forEach(t => {
            document.getElementById(t).onsubmit = null;
        });

        socket = null;
        rhc.style.visibility = "hidden";
    });
});

const types = ["message", "init", "answer", "raw"];
const messagetype = document.getElementById("messagetype");
messagetype.addEventListener("change", (event) => {
    const type = event.target.value;
    document.getElementById(type).style.display = "block";
    types.filter((t) => t !== type).forEach(t => {
        document.getElementById(t).style.display = "none";
    })
});

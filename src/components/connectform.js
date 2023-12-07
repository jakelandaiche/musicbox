import { socket } from "/src/socket.js"

export function init(root) {

  // Set up elements
  const connectform = document.createElement("form");
  connectform.style.width = "200px";

  const label = document.createElement("label");
  label.for = "ws-host"
  
  const textarea = document.createElement("textarea");
  textarea.value = "ws://localhost:8080";
  textarea.name = "ws-host";

  const connectbtn = document.createElement("input");
  connectbtn.type = "submit";
  connectbtn.value = "Connect";

  connectform.appendChild(label);
  connectform.appendChild(textarea);
  connectform.appendChild(connectbtn);


  // Add event listeners
  connectform.addEventListener("submit", (event) => {
    event.preventDefault(); // prevent browser from reloading (default behavior)

    // init socket
    const formData = new FormData(connectform);
    const ws_host = formData.get("ws-host");
    socket.init(ws_host) 
  });


  root.appendChild(connectform);
}

export function destroy(root) {
  while (root.firstChild) {
    root.removeChild(root.lastChild);
  }
}

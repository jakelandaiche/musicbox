import { socket } from "/src/socket.js"
import * as HostLobby from "/src/components/hostlobby.js"

export function init(root) {

  // Set up elements
  const text = document.createTextNode("I am a...");
  const hostbtn = document.createElement("button");
  hostbtn.innerText = "Host";
  const playerbtn = document.createElement("button");
  playerbtn.innerText = "Player";

  // Set up listeners
  hostbtn.addEventListener("click", (event) => {
    console.info("Selected Host");
    destroy(root);
  });
  playerbtn.addEventListener("click", (event) => {
    console.info("Selected Player");
    destroy(root);
  });

  root.appendChild(text);
  root.appendChild(hostbtn);
  root.appendChild(playerbtn);
}


export function destroy(root) {
  while (root.firstChild) {
    root.removeChild(root.lastChild);
  }
}

import { socket } from "/src/socket.js"

export function init(root) {

  // Set up elements
  const text = document.createTextNode("I am a...");
  root.appendChild(text);
}


export function destroy(root) {
  while (root.firstChild) {
    root.removeChild(root.lastChild);
  }
}

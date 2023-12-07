/*
 * main.js
 * 
 * notes: 
 * I created a wrapper around socket to make separation of concerns easier.
 * Handlers can be set up on different files
 * Take a look at socket.js if you want to understand what's happening.
 */

import { socket } from "./socket.js";
import * as ConnectForm from "/src/components/connectform.js";
import * as ChoiceForm from "/src/components/choiceform.js";

console.log("%cStarting MusicBox!", "font-size: 18px; font-weight: bold;");
const root = document.getElementById("root");

// Connection form
ConnectForm.init(root);
socket.onOpen(() => {
  ConnectForm.destroy(root);
  ChoiceForm.init(root);
})
socket.onClose(() => {
  ConnectForm.init(root);
  ChoiceForm.destroy(root);
})


/*
 * CHOICE FORM
 ******************************************************************************/
/*
const choicediv = document.getElementById("div-choice");
socket.onOpen(() => {
  choicediv.style.display = "block";
})
socket.onClose(() => {
  choicediv.style.display = "none";
})

const hostbtn = document.getElementById("btn-host");
const playerbtn = document.getElementById("btn-player");

hostbtn.addEventListener("click", (event) => {
  console.info("Selected Host");
  choicediv.style.display = "none";
  init_videoplayer();
  init_host();
});
playerbtn.addEventListener("click", (event) => {
  console.info("Selected Player");
  choicediv.style.display = "none";
  init_player();
});
*/

import { socket } from "./socket.js"

export const CONNECT = Symbol("Connect")
export const GAMESTART = Symbol("Lobby")
export const ROUNDSTART = Symbol("RoundStart")
export const ROUNDCOLLECT = Symbol("RoundCollect")
export const ROUNDEND = Symbol("RoundEnd")
export const GAMEEND = Symbol("Connect")


class Model {
  constructor() {
    this.state = CONNECT;
  }
}


class View {
  constructor(root) {

  }
  cleanup() {
  }

}


class Controller {
  constructor(model, view) {
    this.model = model;
    this.view = view;
  }
}

export const app = new Controller(new Model(), new View());

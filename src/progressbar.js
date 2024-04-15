import { declare, update, bind, retrieve, reset } from "./state.js"

export function progressbar(name) {
  const PERCENTAGE = declare(0, `<Progress Bar ${name}>`)
  const elem = document.createElement("div")
  const bar = document.createElement("div")
  elem.classList.add('progressbar')
  elem.id = `progressbar-${name}`
  elem.appendChild(bar)

  bind(PERCENTAGE, percentage => bar.style.width = `${Math.trunc(percentage)}%`)
  return [PERCENTAGE, elem]
}

export function progressbar_timer(PERCENTAGE, start, duration) {
    const length = duration*1000
    const end = start + length

    const interval = setInterval(() => {
      const percentage = Math.trunc(100*(1 - ((Date.now() - start)/length)))
      update(PERCENTAGE, percentage, true)
      if (Date.now () >= end) clearInterval(interval)
    }, 33);
}

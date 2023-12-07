const clear = (elem) => elem.innerHTML = "";
const status = document.getElementById("status");

var videoplayer = null;

function init_videoplayer() {
  const tag = document.createElement("script");
  tag.src = "https://www.youtube.com/iframe_api";
  const firstScriptTag = document.getElementsByTagName("script")[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}
function play_video(video_id, start, end) {
  if (videoplayer === null) return;

  let timeout_id;
  videoplayer.err_callbacks.push((error) => {
      clearTimeout(timeout_id);
      const code = error.data;
      switch (code) {
          case 2:
          console.error("Invalid video id");
              break;
          case 5:
          console.error("Player error");
              break;
          case 100:
          console.error("Video not found");
              break;
          case 101:
          case 150:
          console.error("Video not embeddable");
              break;
      }
      alert("Unplayable");
  });

  player.cueVideoById({
    videoId: video_id, 
    startSeconds: start, 
    endSeconds: end
  })

  timeout_id = setTimeout(() => {
      videoplayer.playVideo();
      clearInterval(videoplayer.interval);
      let T = 10;
      interval = setInterval(() => {
        if (T > 0) {
          console.log(T);
          T -= 1;
        } else {
          clearInterval(videoplayer.interval);
        }
      }, 1000);
  }, 1000);
}

function onYouTubeIframeAPIReady () {
  console.info("Player API is ready");

  const err_callbacks = [];
  videoplayer = new YT.Player("player", {
    height: "390",
    width: "640",
    videoId: "y8OnoxKotPQ",
    playerVars: {
      'playsinline': 1,
      'controls': 0,
    },
    events: {
      'onReady': () => {
        console.info("Player is ready", videoplayer);
      },
      'onError': (error) => {
        if (err_callbacks.length > 0) {
            err_callbacks.pop()(e);
        }
      },
    }
  });
  videoplayer.err_callbacks = err_callbacks;
  videoplayer.interval = null;
}

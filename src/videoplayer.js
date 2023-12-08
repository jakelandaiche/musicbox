var videoplayer = null;
var videoreplaybutton = null;

const tag = document.createElement("script");
tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName("script")[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function play_video(video_id, start, end) {
  if (videoplayer === null) return;

  videoplayer.err_callbacks.push((error) => {
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

  videoplayer.cueVideoById({
    videoId: video_id, 
    startSeconds: start, 
    endSeconds: end
  })
}

function onYouTubeIframeAPIReady () {
  console.info("Player API is ready");

  const err_callbacks = [];
  videoplayer = new YT.Player("videoplayer", {
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

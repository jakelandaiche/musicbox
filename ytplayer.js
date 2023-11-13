// YouTube IFrame API init stuff
var tag = document.createElement("script");
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName("script")[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var player;
var playerReady = false;
var interval;
function onYouTubeIframeAPIReady () {
    console.log("ready");
    player = new YT.Player('player', {
        height: '390',
        width: '640',
        videoId: 'y8OnoxKotPQ',
        playerVars: {
            'playsinline': 1,
            'controls': 0,
        },
        events: {
            'onReady': onPlayerReady,
            'onError': onPlayerError,
            'onStateChange': onPlayerStateChange,
        }
    });
}
function onPlayerStateChange(e) {
}
function onPlayerReady(e) {
  playerReady = true;
}
function onPlayerError(e) {
    console.log('player error')
    console.log(e)
}

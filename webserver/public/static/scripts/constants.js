// Video Stream Resolution and Screen Size
var resolutions = [[640,480],[1280,720]],
    resolution = resolutions[0],
    videoHeight = resolution[1],
    videoWidth = resolution[0],
    screenHeight = screen.height,
    screenWidth = screen.width,
    pc = new RTCPeerConnection(),
    video = document.querySelector('#live');
// Data Channel Communication
var dc = null,
    dcInterval = null;

// Canvas Coordinate Locations:
var wc_x, wc_y, wc_x_, wc_y_,
    wc_coords;

// Canvas Variables
// On Screen Canvas For all Draw Operations
var canvas = document.querySelector('#canvas'),
    canvasHeight, headerHeight,
    ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#ff0';
    ctx.lineWidth = 2;
// Temporary offscreen canvas
var wcVideoCanvas = document.createElement('canvas'), 
    ctxWcVideo = wcVideoCanvas.getContext('2d');
    
   
// Update variables
const webcamUpdateIntervalMS = 100;

// ML Result DATA. 
var currentData = "{}",
    tempData = "{}";

// Label Data
var TEXT_BOX_HEIGHT=0.1,
    bbTextSize=12,
    bbTextHPadding=5;

// https://stackoverflow.com/questions/68337654/adding-javascript-to-my-plotly-dash-app-python
// alert('If you see this alert, then your custom JavaScript script has run!')
var video, canvas, context, info, imageData, detector, mpos={}, postimeout=5000;

function onLoad(){
  video = document.getElementById("video");
  canvas = document.getElementById("canvas");
  info = document.getElementById("info");
  context = canvas.getContext("2d");

  canvas.width = parseInt(canvas.style.width);
  canvas.height = parseInt(canvas.style.height);
  
  if (navigator.mediaDevices === undefined) {
    navigator.mediaDevices = {};
  }
  
  if (navigator.mediaDevices.getUserMedia === undefined) {
    navigator.mediaDevices.getUserMedia = function(constraints) {
      var getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
      
      if (!getUserMedia) {
        return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
      }

      return new Promise(function(resolve, reject) {
        getUserMedia.call(navigator, constraints, resolve, reject);
      });
    }
  }

  navigator.mediaDevices
    .getUserMedia({ video: {
      width: { ideal: 4096 },
      height: { ideal: 2160 } 
    } })
    .then(function(stream) {
      let settings = stream.getVideoTracks()[0].getSettings();
      //console.log("Stream found", stream, video, settings, canvas);
      console.log('Camera: ' + settings.deviceId);
      console.log('Camera width: ' + settings.width + 'px');
      console.log('Camera height:' + settings.height + 'px');
      canvas.width=settings.width;
      canvas.height=settings.height;
      if ("srcObject" in video) {
        video.srcObject = stream;
      } else {
        video.src = window.URL.createObjectURL(stream);
      }
    })
    .catch(function(err) {
      console.log(err.name + ": " + err.message);
    }
  );
    
  detector = new AR.Detector();

  requestAnimationFrame(tick);
}

function tick(){
  requestAnimationFrame(tick);
  
  if (video.readyState === video.HAVE_ENOUGH_DATA){
    snapshot();

    var markers = detector.detect(imageData);
    drawCorners(markers);
    drawId(markers);
    drawGrid(markers);
  }
}

function snapshot(){
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  imageData = context.getImageData(0, 0, canvas.width, canvas.height);
}
      
function drawCorners(markers){
  var corners, corner, i, j;

  context.lineWidth = 3;

  for (i = 0; i !== markers.length; ++ i){
    corners = markers[i].corners;
    
    context.strokeStyle = "red";
    context.beginPath();
    
    for (j = 0; j !== corners.length; ++ j){
      corner = corners[j];
      context.moveTo(corner.x, corner.y);
      corner = corners[(j + 1) % corners.length];
      context.lineTo(corner.x, corner.y);
    }

    context.stroke();
    context.closePath();
    
    context.strokeRect((corners[0].x+corners[1].x+corners[2].x+corners[3].x)/4, (corners[0].y+corners[1].y+corners[2].y+corners[3].y)/4, 1, 1);
    
    context.strokeStyle = "green";
    context.strokeRect(corners[0].x - 2, corners[0].y - 2, 4, 4);
  }
}

function drawId(markers){
  var corners, corner, x, y, i, j;
  
  context.strokeStyle = "blue";
  context.lineWidth = 1;
  
  for (i = 0; i !== markers.length; ++ i){
    corners = markers[i].corners;
    
    x = Infinity;
    y = Infinity;
    
    for (j = 0; j !== corners.length; ++ j){
      corner = corners[j];
      
      x = Math.min(x, corner.x);
      y = Math.min(y, corner.y);
    }

    context.strokeText(markers[i].id, x, y)
  }
}

function drawGrid(markers){
  var corners, corner, x, y, i, j, pS, pE, okcnt=0, tnow=Date.now(), statustxt, missing=new Set();

  for (i = 0; i !== markers.length; ++ i){
    markers[i].tstamp=tnow;
    mpos[""+markers[i].id]=markers[i];
  }
  
  context.strokeStyle = "green";
  context.lineWidth = 1;

  maplines=[ // grid
    ["1","2"], ["2","3"], ["3","4"],
    ["5","6"], ["6","7"], ["7","8"],
    ["9","10"], ["10","11"], ["11","12"],
    ["13","14"], ["14","15"], ["15","16"],
    ["1","5"], ["5","9"], ["9","13"],
    ["2","6"], ["6","10"], ["10","14"],
    ["3","7"], ["7","11"], ["11","15"],
    ["4","8"], ["8","12"], ["12","16"],
  ]
  maplines=[ // small perspective
    ["1","4"],
    ["9","12"],
    ["1","9"],
    ["4","12"],
    ["13","16"],
  ]
  maplines.forEach(p => {
    if (!(p[0] in mpos)) missing.add(p[0]);
    if (!(p[1] in mpos)) missing.add(p[0]);
    if ((p[0] in mpos) && (p[1] in mpos)) {
      pS=mpos[p[0]];
      pE=mpos[p[1]];
      if (tnow-pS.tstamp>=postimeout) missing.add("to "+p[0]);
      if (tnow-pE.tstamp>=postimeout) missing.add("to "+p[1]);
      if ((tnow-pS.tstamp<postimeout) && (tnow-pE.tstamp<postimeout)){
        context.moveTo(pS.corners[0].x, pS.corners[0].y);
        context.lineTo(pE.corners[0].x, pE.corners[0].y);
      }
    }
  })
  context.stroke();

  // plot time marker
  if ("0" in mpos && tnow-mpos["0"].tstamp<postimeout) {
    timemarker=mpos["0"];
    cS=timemarker.corners[0];
    cE=timemarker.corners[2];
    context.strokeStyle = "orange";
    context.strokeRect(cE.x+2*(cS.x-cE.x), cE.y+2*(cS.y-cE.y), 1, 1);
  }

  // plot place marker
  if ("20" in mpos && tnow-mpos["20"].tstamp<postimeout) {
    timemarker=mpos["20"];
    cS=timemarker.corners[0];
    cE=timemarker.corners[2];
    context.strokeStyle = "orange";
    context.strokeRect((cS.x+cE.x)/2, (cS.y+cE.y)/2, 1, 1);
  }

  // map perspective correction
  if (!("1" in mpos)) missing.add("1");
  if (!("4" in mpos)) missing.add("4");
  if (!("9" in mpos)) missing.add("9");
  if (!("12" in mpos)) missing.add("12");
  if (!("13" in mpos)) missing.add("13");
  if (!("16" in mpos)) missing.add("16");
  if (!("0" in mpos)) missing.add("timestamp");
  if (!("20" in mpos)) missing.add("place");
  if (missing.size==0){
    statustxt="OK";
  }else{
    statustxt ="Err: "+Array.from(missing).join(', ');
  }

  if (("1" in mpos) && ("4" in mpos) && ("9" in mpos) && ("12" in mpos)) {
    pTL=mpos["1"]; pTR=mpos["4"]; pBL=mpos["9"]; pBR=mpos["12"];

    var srcCorners = [pTL.corners[0].x, pTL.corners[0].y, pTR.corners[0].x, pTR.corners[0].y, pBR.corners[0].x, pBR.corners[0].y, pBL.corners[0].x, pBL.corners[0].y];
    var dstCorners = [90, -180, 90, 180, -90, 180, -90, -180];
    var perspT = PerspT(srcCorners, dstCorners);

    // deal with place marker
    if ("0" in mpos && tnow-mpos["0"].tstamp<postimeout) {
      timemarker=mpos["0"]; cS=timemarker.corners[0]; cE=timemarker.corners[2];
      var srcPt = [(cS.x+cE.x)/2, (cS.y+cE.y)/2];
      var dstPt = perspT.transform(srcPt[0], srcPt[1]);
      //var dstPt = [Math.round(dstPt[0]), Math.round(dstPt[1])]
      //console.log(srcPt, dstPt);
      //statustxt += " " + srcPt + "=>" + dstPt;
      statustxt += "; Loc: " + Math.round(dstPt[1]) + " lat, " + Math.round(dstPt[0]) + " lon";
    }
  }

  if (("9" in mpos) && ("12" in mpos) && ("13" in mpos) && ("16" in mpos)) {
    pTL=mpos["9"]; pTR=mpos["12"]; pBL=mpos["13"]; pBR=mpos["16"];

    var srcCorners = [pTL.corners[0].x, pTL.corners[0].y, pTR.corners[0].x, pTR.corners[0].y, pBR.corners[0].x, pBR.corners[0].y, pBL.corners[0].x, pBL.corners[0].y];
    var dstCorners = [-200, 0, 2100, 0, 2100, 500, -200, 500];
    var perspT = PerspT(srcCorners, dstCorners);

    // deal with time marker
    if ("0" in mpos && tnow-mpos["0"].tstamp<postimeout) {
      timemarker=mpos["0"]; cS=timemarker.corners[0]; cE=timemarker.corners[2];
      var srcPt = [cE.x+2*(cS.x-cE.x), cE.y+2*(cS.y-cE.y)];
      var dstPt = perspT.transform(srcPt[0], srcPt[1]);
      //var dstPt = [Math.round(dstPt[0]), Math.round(dstPt[1])]
      //console.log(srcPt, dstPt);
      statustxt += "; Year: " + Math.round(dstPt[0]);
    }
  }

  info.innerHTML = statustxt;
}


window.onload = onLoad;


/**
 *
 * @param {string} id
 * @param {*} event
 * @param {(this: HTMLElement, ev: any) => any} callback
 * @param {boolean | AddEventListenerOptions} options
 */
function attachEventToDash(id, event, callback, options) {
    debugger;
    var observer = new MutationObserver(function (_mutations, obs) {
        var ele = document.getElementById(id);
        if (ele) {
            debugger;
            ele.addEventListener(event, callback, options)
            obs.disconnect();
        }
    });
    window.addEventListener('DOMContentLoaded', function () {
        observer.observe(document, {
            childList: true,
            subtree: true
        });
    })
}
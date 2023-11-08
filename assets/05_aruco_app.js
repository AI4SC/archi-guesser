var video=null, canvas=null, context, imageData, detector, mpos={}, postimeout=5000, statusobj={};
  
function onLoad(){
  video = document.getElementById("video");
  canvas = document.getElementById("canvas");
  //info = document.getElementById("info");
  if ( video == null || canvas == null) {
    console.log("loading ...");
    setTimeout(onLoad, 1000);
    return;
  }
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
      canvas.width = 1920 || settings.width;
      canvas.height= 1080 || settings.height;
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

  //requestAnimationFrame(tick);
}

function tick(){
  //requestAnimationFrame(tick);
  
  if (video.readyState === video.HAVE_ENOUGH_DATA){
    snapshot();

    var markers = detector.detect(imageData);
    drawCorners(markers);
    drawId(markers);
    drawGrid(markers);
  }
}

function ticktick() {
  if ( video == null || canvas == null ) return {};
  requestAnimationFrame(tick);
  return statusobj;
}

function snapshot(){
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  imageData = context.getImageData(0, 0, canvas.width, canvas.height);
}

function drawCorners(markers){
  for (let i = 0; i !== markers.length; ++ i){
    let corners = markers[i].corners;
    for (let j = 0; j !== corners.length; ++ j){
      let corner = corners[j];
      context.moveTo(corner.x, corner.y);
      corner = corners[(j + 1) % corners.length];
      context.lineTo(corner.x, corner.y);
    }

    context.lineWidth = 3;
    context.strokeStyle = "red";
    context.beginPath();
    context.stroke();
    context.closePath();

    context.strokeRect((corners[0].x+corners[1].x+corners[2].x+corners[3].x)/4, (corners[0].y+corners[1].y+corners[2].y+corners[3].y)/4, 1, 1);
    
    context.strokeStyle = "green";
    context.strokeRect(corners[0].x - 2, corners[0].y - 2, 4, 4);
  }
}

function drawId(markers){
  for (let i = 0; i !== markers.length; ++ i){
    var x = Infinity, y = Infinity;
    
    let corners = markers[i].corners;
    for (let j = 0; j !== corners.length; ++ j){
      let corner = corners[j];
      x = Math.min(x, corner.x);
      y = Math.min(y, corner.y);
    }

    context.strokeStyle = "blue";
    context.lineWidth = 1;
    context.strokeText(markers[i].id, x, y)
  }
}

function drawGrid(markers){
  var tnow=Date.now(), missing=new Set(), statusobj={};

  for (let i = 0; i !== markers.length; ++ i){
    markers[i].tstamp=tnow;
    mpos[""+markers[i].id]=markers[i];
  }

  context.strokeStyle = "green";
  context.lineWidth = 1;

  maplines=[ // old grid 
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
      let pS=mpos[p[0]];
      let pE=mpos[p[1]];
      if (tnow-pS.tstamp>=postimeout) missing.add("to "+p[0]);
      if (tnow-pE.tstamp>=postimeout) missing.add("to "+p[1]);
      if ((tnow-pS.tstamp<postimeout) && (tnow-pE.tstamp<postimeout)){
        context.moveTo(pS.corners[0].x, pS.corners[0].y);
        context.lineTo(pE.corners[0].x, pE.corners[0].y);
      }
    }
  })
  context.stroke();

  if ("0" in mpos && tnow-mpos["0"].tstamp<postimeout) {
    timemarker=mpos["0"];
    cS=timemarker.corners[0];
    cE=timemarker.corners[2];
    context.strokeStyle = "orange";
    context.strokeRect(cE.x+2*(cS.x-cE.x), cE.y+2*(cS.y-cE.y), 1, 1);
  }

  // map perspective correction
  if (!("0" in mpos)) missing.add("TimeMarker 0");
  if (!("1" in mpos)) missing.add("MapCorner 1");
  if (!("4" in mpos)) missing.add("MapCorner 4");
  if (!("9" in mpos)) missing.add("MapCorner 9");
  if (!("12" in mpos)) missing.add("MapCorner 12");
  if (!("13" in mpos)) missing.add("TimeCorner 13");
  if (!("16" in mpos)) missing.add("TimeCorner 16");
  if (!("18" in mpos) && !("19" in mpos)) {missing.add("GoMarker 18");missing.add("StopMarker 19")}
  
  // geographic map projection
  if (("1" in mpos) && ("4" in mpos) && ("9" in mpos) && ("12" in mpos)) {
    pTL=mpos["1"]; pTR=mpos["4"]; pBL=mpos["9"]; pBR=mpos["12"];

    var srcCorners = [pTL.corners[0].x, pTL.corners[0].y, pTR.corners[0].x, pTR.corners[0].y, pBR.corners[0].x, pBR.corners[0].y, pBL.corners[0].x, pBL.corners[0].y];
    var dstCorners = [90, -180, 90, 180, -90, 180, -90, -180];
    var perspT = PerspT(srcCorners, dstCorners);

    // deal with place marker
    // deal with time marker
    found = false;
    for (let index = 20; index < 31; index++) {
      if ((""+index) in mpos && tnow-mpos[(""+index)].tstamp<postimeout) {
        var marker=mpos[(""+index)];
        cS=marker.corners[0];
        cE=marker.corners[2];

        // plot time marker
        context.strokeStyle = "orange";
        context.strokeRect(cE.x+2*(cS.x-cE.x), cE.y+2*(cS.y-cE.y), 1, 1);

        var srcPt = [(cS.x+cE.x)/2, (cS.y+cE.y)/2];
        var dstPt = perspT.transform(srcPt[0], srcPt[1]);
        //var dstPt = [Math.round(dstPt[0]), Math.round(dstPt[1])]
        //console.log(srcPt, dstPt);
        //statustxt += " " + srcPt + "=>" + dstPt;
        statusobj['lat']=Math.round(dstPt[1]);
        statusobj['lon']=Math.round(dstPt[0]);
        statusobj['obj']=index;
        found=true;
      }
    }
    if (!found) missing.add("place");
  }

  // time projection
  if (("9" in mpos) && ("12" in mpos) && ("13" in mpos) && ("16" in mpos)) {
    pTL=mpos["9"]; pTR=mpos["12"]; pBL=mpos["13"]; pBR=mpos["16"];

    var srcCorners = [pTL.corners[0].x, pTL.corners[0].y, pTR.corners[0].x, pTR.corners[0].y, pBR.corners[0].x, pBR.corners[0].y, pBL.corners[0].x, pBL.corners[0].y];
    var dstCorners = [-200, 0, 2100, 0, 2100, 500, -200, 500];
    var perspT = PerspT(srcCorners, dstCorners);

    // deal with time marker
    if ("0" in mpos && tnow-mpos["0"].tstamp<postimeout) {
      timemarker=mpos["0"]; 
      cS=timemarker.corners[0];
      cE=timemarker.corners[2];

      // plot place marker
      context.strokeStyle = "orange";
      context.strokeRect((cS.x+cE.x)/2, (cS.y+cE.y)/2, 1, 1);
      found =true;
      
      var srcPt = [cE.x+2*(cS.x-cE.x), cE.y+2*(cS.y-cE.y)];
      var dstPt = perspT.transform(srcPt[0], srcPt[1]);
      //var dstPt = [Math.round(dstPt[0]), Math.round(dstPt[1])]
      statusobj['year']=Math.round(dstPt[0]);
    }
  }

  // deal with GO and STOP marker
  if ("18" in mpos && tnow-mpos["18"].tstamp<postimeout) {
    statusobj['state']="GO"
  }else if ("19" in mpos && tnow-mpos["19"].tstamp<postimeout) {
    statusobj['state']="STOP"; // deal with STOP marker
  } else {
    statusobj['state']="ERR";
  }

  // err log
  statusobj['err']=missing;
}


document.addEventListener('DOMContentLoaded', () => {
  setTimeout(onLoad, 1000)
})

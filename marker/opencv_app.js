let video;
let canvasOutput;
let canvasInput;
let cap;
let imageCaptured = false;

function onOpenCvReady() {
  // Initialize video and canvas elements
  video = document.getElementById("video");
  canvasOutput = document.getElementById("canvas");
  canvasInput = document.createElement("canvas");
  const constraints = { video: { facingMode: "environment" } };

  // Start the video stream
  navigator.mediaDevices.getUserMedia(constraints)
    .then((stream) => {
      video.srcObject = stream;
      video.play();
      initAruco();
    })
    .catch((error) => console.error("Error accessing webcam:", error));
}

function initAruco() {
  cap = new cv.VideoCapture(video);
  setInterval(processFrame, 33); // Set the frame processing interval (about 30fps)
}

function captureImage() {
  // Draw the current video frame onto the input canvas
  canvasInput.width = video.videoWidth;
  canvasInput.height = video.videoHeight;
  const ctx = canvasInput.getContext("2d");
  ctx.drawImage(video, 0, 0, canvasInput.width, canvasInput.height);
  imageCaptured = true;
}

function processFrame() {
  // Read a frame from the video stream
  let frame = new cv.Mat(video.videoHeight, video.videoWidth, cv.CV_8UC4);
  
  if (imageCaptured) {
    // Convert the captured image to grayscale (ARUCO marker detection works with grayscale images)
    let gray = new cv.Mat();
    const inputCanvasCtx = canvasInput.getContext("2d");
    const imageData = inputCanvasCtx.getImageData(0, 0, canvasInput.width, canvasInput.height);
    cv.cvtColor(cv.matFromImageData(imageData), gray, cv.COLOR_RGBA2GRAY);

    // Create an ARUCO dictionary (DICT_4X4_100 is a 4x4 marker dictionary with 100 unique markers)
    // ARUCO_MIP_36h12
    let dictionary = new cv.Dictionary(cv.DICT_ARUCO_ORIGINAL);

    // Detect ARUCO markers in the captured image
    let corners = new cv.Mat();
    let ids = new cv.Mat();
    let detectorParams = new cv.DetectorParameters();
    cv.detectMarkers(gray, dictionary, corners, ids, detectorParams);

    // Draw marker borders on the input canvas
    cv.drawDetectedMarkers(cv.matFromImageData(imageData), corners, ids, new cv.Scalar(255, 0, 0, 255));

    // Display the processed frame on the output canvas
    cv.imshow(canvasOutput, cv.matFromImageData(imageData));

    // Release the Mats to free up memory
    frame.delete();
    gray.delete();
    corners.delete();
    ids.delete();
    imageCaptured = false;
  }
}
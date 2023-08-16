const activateCameraButton = document.getElementById("activateCameraButton");
const cameraContainer = document.getElementById("cameraContainer");
const captureContainer = document.getElementById("captureContainer");
const previewContainer = document.getElementById("previewContainer");
const captureButton = document.getElementById("captureButton");
const recaptureButton = document.getElementById("recaptureButton");
const closeButton = document.getElementById("closeButton");
const nameInput = document.getElementById("nameInput");
const emailInput = document.getElementById("emailInput");
const maxPhotoCount = 2;
let capturedPhotos = [];
let webcamInstance = null;

// Activate camera when the button is clicked
activateCameraButton.addEventListener("click", () => {
  cameraContainer.innerHTML = "";
  activateCameraButton.style.display = "none";
  captureContainer.style.display = "block";
  previewContainer.innerHTML = "";

  if (!webcamInstance) {
    Webcam.set({
      width: 320,
      height: 240,
      image_format: 'jpeg',
      jpeg_quality: 90
    });
    webcamInstance = Webcam.attach(cameraContainer);
  } else {
    Webcam.reset();
    webcamInstance = Webcam.attach(cameraContainer);
  }
});

// Capture photo when the button is clicked
captureButton.addEventListener("click", () => {
  if (capturedPhotos.length < maxPhotoCount) {
    Webcam.snap(dataUri => {
      capturedPhotos.push(dataUri);
      const img = document.createElement("img");
      img.src = dataUri;
      previewContainer.appendChild(img);

      if (capturedPhotos.length === maxPhotoCount) {
        // Hide the "Activate Camera" button and capture button
        activateCameraButton.style.display = "none";
        captureButton.style.display = "none";
        recaptureButton.style.display = "block";
        closeButton.style.display = "block";
        Webcam.reset(); // Close the webcam
      }
    });
  }
});

// Recapture photo when the button is clicked
recaptureButton.addEventListener("click", () => {
  capturedPhotos = [];
  previewContainer.innerHTML = "";
  activateCameraButton.style.display = "block";
  captureButton.style.display = "block";
  recaptureButton.style.display = "none";
  closeButton.style.display = "none";
  webcamInstance = Webcam.attach(cameraContainer); // Re-attach the webcam
});

// Close webcam when the button is clicked
closeButton.addEventListener("click", () => {
  Webcam.reset();
  cameraContainer.innerHTML = "";
  previewContainer.innerHTML = "";
  activateCameraButton.style.display = "block";
  captureContainer.style.display = "none";
  capturedPhotos = [];
  recaptureButton.style.display = "none";
  closeButton.style.display = "none";
});

// Form submission
document.getElementById("myForm").addEventListener("submit", event => {
  event.preventDefault();


  const formData = new FormData();
  const fileInput = document.getElementById("pdfFiles");
  const files = fileInput.files;
  const fileDetails = [];

  if (files.length > 5) {
    console.error("You can only upload up to 5 files.");
    return;
  }

  Array.from(files).forEach((file, index) => {
    const fileDetail = {
      filename: file.name,
      content_type: file.type,
      file_size: file.size
    };
    fileDetails.push(fileDetail);
    formData.append(`pdfFiles[${index}]`, file);
  });
  formData.append("name", nameInput.value);
  formData.append("email", emailInput.value);

  capturedPhotos.forEach((dataUri, index) => {
    const byteString = atob(dataUri.split(",")[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: "image/jpeg" });
    formData.append(`photo${index + 1}`, blob, `photo${index + 1}.jpg`);
  });
  fetch("/testing", {
    method: "POST",
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      console.log(data);
    })
    .catch(error => {
      console.error("Error:", error);
    });
});


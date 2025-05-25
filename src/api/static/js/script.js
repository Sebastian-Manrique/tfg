function toggleVideo() {
  const video = document.getElementById("video-stream");
  const icon = document.getElementById("icon-stream");
  const button = document.getElementById("btnWatch");

  if (video.style.display === "none") {
    video.style.display = "block";
    icon.style.display = "none";
    button.innerHTML = "Dejar de ver";
    button.style.backgroundColor = "red";
  } else {
    video.style.display = "none";
    icon.style.display = "block";
    button.innerHTML = "Ver camara en linea";
    button.style.backgroundColor = "#008080";
  }
}

function restart() {
  fetch("http://127.0.0.1:5001/restart-camera", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((json) => {
      location.reload();
      console.log(json);
    });
}

var mode = "";
function scanMode(mode) {
  if (mode == "yolo") {
    fetch("/video/yolo", { method: "POST" })
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
      });
  } else {
    fetch("/video/opencv", { method: "POST" })
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
      });
  }

  // Calling the differents modes from the save fetch.
}

function markUseDiscount(summaryId) {
  const urlParams = new URLSearchParams(window.location.search);
  const lang = urlParams.get("lang") || "es";

  fetch(`/summary/${summaryId}?lang=${lang}`, { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        location.reload();
      } else {
        alert("Error al canjear el cupón.");
      }
    });
}

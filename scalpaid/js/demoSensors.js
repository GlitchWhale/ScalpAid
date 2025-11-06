/* ================================
   ScalpAid Demo Sensor Stream
   ================================ */

function generateFakeSensorData() {
  return {
    temperature: (32 + Math.random() * 3).toFixed(1), // °C
    moisture: (55 + Math.random() * 5).toFixed(1),    // %
    tension: (18 + Math.random() * 2).toFixed(1),     // kPa
  };
}

// This function simulates live updates every 3 seconds
function startDemoStream(updateCallback) {
  setInterval(() => {
    const data = generateFakeSensorData();
    updateCallback(data);
  }, 3000);
}

// Example hookup — modify IDs to match your HTML
document.addEventListener("DOMContentLoaded", () => {
  startDemoStream((data) => {
    document.getElementById("tempValue").textContent = `${data.temperature}°C`;
    document.getElementById("moistureValue").textContent = `${data.moisture}%`;
    document.getElementById("tensionValue").textContent = `${data.tension} kPa`;

    // Optionally log it for debugging
    console.log("🔹 New fake sensor data:", data);

    // Example: trigger notification if abnormal values appear
    if (data.temperature > 34.5 || data.moisture < 56) {
      showNotification("⚠️ Check scalp condition — unusual readings detected!");
    }
  });
});

// Simple popup alert system (temporary demo version)
function showNotification(message) {
  const note = document.createElement("div");
  note.textContent = message;
  note.style.position = "fixed";
  note.style.bottom = "20px";
  note.style.right = "20px";
  note.style.background = "#5b7553";
  note.style.color = "white";
  note.style.padding = "10px 16px";
  note.style.borderRadius = "12px";
  note.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
  note.style.zIndex = "1000";
  document.body.appendChild(note);

  setTimeout(() => note.remove(), 4000);
}

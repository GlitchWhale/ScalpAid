// main.js

console.log("ScalpAid frontend loaded.");

// Example: test button interaction
document.addEventListener("DOMContentLoaded", () => {
    const alertButton = document.getElementById("alertButton");
    if (alertButton) {
        alertButton.addEventListener("click", () => {
            alert("Manual alert triggered (for demo).");
        });
    }
});

// Example of polling the Flask backend for sensor data (future use)
async function fetchSensorData() {
    try {
        const response = await fetch("/api/sensor_data");
        if (!response.ok) throw new Error("Failed to fetch data");
        const data = await response.json();
        console.log("Sensor data:", data);
    } catch (error) {
        console.error(error);
    }
}

// Poll every 20 seconds (for live updates)
setInterval(fetchSensorData, 20000);

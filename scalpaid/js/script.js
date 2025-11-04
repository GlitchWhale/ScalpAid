// ScalpAid JS: Chart setup for temperature, tension, and moisture

let chartInstances = {};

document.addEventListener("DOMContentLoaded", () => {
  setupCharts();
});

function setupCharts() {
  if (typeof Chart === "undefined") return;

  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const datasets = {
    tempChart: {
      data: [36.2, 36.4, 36.5, 36.6, 36.5, 36.7, 36.5],
      color: "#5b7553",
    },
    tensionChart: {
      data: [4, 5, 4, 3, 4, 4, 3],
      color: "#7fa174",
    },
    moistureChart: {
      data: [60, 61, 62, 63, 62, 64, 65],
      color: "#4f8da5",
    },
  };

  Object.entries(datasets).forEach(([id, cfg]) => {
    const canvas = document.getElementById(id);
    if (!canvas) return;

    // Destroy any existing chart before re-rendering
    if (chartInstances[id]) {
      chartInstances[id].destroy();
    }

    const ctx = canvas.getContext("2d");

    chartInstances[id] = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            data: cfg.data,
            borderColor: cfg.color,
            backgroundColor: `${cfg.color}33`,
            borderWidth: 2,
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { display: false } },
        },
      },
    });
  });
}

// =========================
// Toggle Switch Buttons (Settings Page)
// =========================

document.addEventListener("DOMContentLoaded", () => {
  const togglePills = document.querySelectorAll(".toggle-pill");

  togglePills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pill.classList.toggle("active");
      if (pill.classList.contains("active")) {
        pill.textContent = pill.textContent === "Connected" ? "Connected" : "On";
      } else {
        pill.textContent = pill.textContent === "Connected" ? "Disconnected" : "Off";
      }
    });
  });
});


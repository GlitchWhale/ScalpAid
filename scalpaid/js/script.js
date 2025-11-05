// script.js

// Get logged-in user from localStorage
const user = JSON.parse(localStorage.getItem("loggedInUser"));

// -------------------
// Logout functionality
// -------------------
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("loggedInUser");
    window.location.href = "index.html";
  });
}

// -------------------
// Profile Page
// -------------------
if (user && document.getElementById("profileName")) {
  // Fill profile details
  document.getElementById("profileName").textContent = user.name || "--";
  document.getElementById("profileUsername").textContent = user.username || "--";
  document.getElementById("profileHairType").textContent = user.hairType || "--";
  document.getElementById("profileHairTexture").textContent = user.hairTexture || "--";
  document.getElementById("profileMemberSince").textContent = user.memberSince || "--";
  document.getElementById("profileAvatar").textContent = user.name
    ? user.name.split(" ").map(n => n[0]).join("")
    : "--";

  // Edit & Save buttons
  const editBtn = document.getElementById("editProfileBtn");
  const saveBtn = document.getElementById("saveProfileBtn");

  if (editBtn && saveBtn) {
    editBtn.addEventListener("click", () => {
      document.querySelectorAll(".profile-detail-value").forEach(span => {
        const input = document.createElement("input");
        input.value = span.textContent;
        input.className = "input-field";
        span.replaceWith(input);
      });
      editBtn.style.display = "none";
      saveBtn.style.display = "inline-block";
    });

    saveBtn.addEventListener("click", () => {
      const inputs = document.querySelectorAll(".input-field");
      inputs.forEach(input => {
        const span = document.createElement("span");
        span.className = "profile-detail-value";
        span.textContent = input.value;
        input.replaceWith(span);
      });
      editBtn.style.display = "inline-block";
      saveBtn.style.display = "none";

      // Update localStorage after editing
      const updatedUser = {
        email: user.email,
        name: document.getElementById("profileName").textContent,
        username: document.getElementById("profileUsername").textContent,
        hairType: document.getElementById("profileHairType").textContent,
        hairTexture: document.getElementById("profileHairTexture").textContent,
        memberSince: document.getElementById("profileMemberSince").textContent,
        temperature: user.temperature,
        tension: user.tension,
        moisture: user.moisture
      };
      localStorage.setItem("loggedInUser", JSON.stringify(updatedUser));
    });
  }
}

// -------------------
// Home & History Charts
// -------------------
const isBrianna = user && user.email === "brianna@example.com";

function fillHomeMetrics() {
  const metrics = [
    { id: "tempValue", statusId: "tempStatus", value: user.temperature + "°C", status: "Normal" },
    { id: "tensionValue", statusId: "tensionStatus", value: user.tension + " / 10", status: "Healthy" },
    { id: "moistureValue", statusId: "moistureStatus", value: user.moisture + "%", status: "Optimal" }
  ];

  metrics.forEach(m => {
    const el = document.getElementById(m.id);
    const statusEl = document.getElementById(m.statusId);
    if(el) el.textContent = m.value;
    if(statusEl) statusEl.textContent = m.status;
  });
}

function initCharts() {
  const charts = [
    { id: "tempChart", label: "Temperature (°C)", data: [36.4,36.5,36.6,36.5,36.5,36.4,36.5], color: "rgb(255,99,132)" },
    { id: "tensionChart", label: "Tension (1–10)", data: [4,4,5,4,4,4,4], color: "rgb(54,162,235)" },
    { id: "moistureChart", label: "Moisture (%)", data: [60,61,62,62,62,63,62], color: "rgb(75,192,192)" }
  ];

  charts.forEach(c => {
    const ctx = document.getElementById(c.id);
    if(ctx){
      new Chart(ctx, {
        type: "line",
        data: {
          labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
          datasets: [{
            label: c.label,
            data: c.data,
            borderColor: c.color,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true }
          }
        }
      });
    }
  });
}

if(isBrianna){
  fillHomeMetrics();
  initCharts();
} else {
  // Empty placeholders for other users
  document.querySelectorAll(".chart-wrapper").forEach(c => {
    c.innerHTML = "<p style='text-align:center; color:var(--text-muted)'>No data available</p>";
  });
  ["tempValue","tensionValue","moistureValue","tempStatus","tensionStatus","moistureStatus"].forEach(id => {
    const el = document.getElementById(id);
    if(el) el.textContent = "--";
  });
}

// -------------------
// Insights Page
// -------------------
if(document.body.classList.contains("insights-page")){
  const summary = document.getElementById("insightSummary");
  const insights = document.querySelectorAll(".insight-item .insight-text-body");

  if(isBrianna){
    if(summary) summary.textContent = "Your scalp readings this week are stable. Hydration and styling habits are balanced.";
    if(insights[0]) insights[0].textContent = "No unusual spikes in scalp temperature detected this week.";
    if(insights[1]) insights[1].textContent = "Average moisture increased 8% after using your conditioning spray.";
    if(insights[2]) insights[2].textContent = "Lower tension readings observed when using looser hairstyles.";
  } else {
    if(summary) summary.textContent = "No data available for this user.";
    insights.forEach(i => i.textContent = "--");
  }
}

// script.js (replace existing file)
document.addEventListener("DOMContentLoaded", () => {
  const userKey = "loggedInUser";
  const goalKey = "userGoal";

  // Helpers
  const getUser = () => {
    try {
      return JSON.parse(localStorage.getItem(userKey));
    } catch (e) {
      return null;
    }
  };
  const setUser = (u) => localStorage.setItem(userKey, JSON.stringify(u));
  const clearSession = () => {
    localStorage.removeItem(userKey);
    // do NOT remove userGoal here unless you want to force users to reselect goal on logout
    // localStorage.removeItem(goalKey);
  };

  // Logout attach (works if logout button exists on the page)
  const attachLogout = () => {
    const logoutEls = document.querySelectorAll("#logoutBtn");
    logoutEls.forEach(btn => {
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        clearSession();
        // ensure redirect to landing page
        window.location.href = "index.html";
      });
    });
  };
  attachLogout();

  const user = getUser();

  /* -------------------------
     PROFILE PAGE HANDLING
     ------------------------- */
  if (document.getElementById("profileName")) {
    // ensure we have a user (should be set after login/register)
    if (!user) {
      // if no user, redirect to login (safer), or show guest placeholders
      console.warn("No loggedInUser found while loading profile. Redirecting to login.");
      window.location.href = "login.html";
      return;
    }

    // populate basic fields
    const setText = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value ?? "--";
    };

    setText("profileName", user.name || "--");
    setText("profileUsername", user.username || "--");
    setText("profileGoal", user.goal || localStorage.getItem(goalKey) || "--");
    setText("profileHairType", user.hairType || "--");
    setText("profileHairTexture", user.hairTexture || "--");
    setText("profileMemberSince", user.memberSince || "--");
    const avatarEl = document.getElementById("profileAvatar");
    if (avatarEl) avatarEl.textContent = user.name ? user.name.split(" ").map(n => n[0]).join("") : "--";

    // show/hide goal sections if they exist
    const goal = user.goal || localStorage.getItem(goalKey) || "Prevent Alopecia";
    const showEl = (id, show) => {
      const e = document.getElementById(id);
      if (e) e.style.display = show ? "block" : "none";
    };
    showEl("preventSection", goal === "Prevent Alopecia");
    showEl("manageSection", goal === "Manage Alopecia");
    showEl("improveSection", goal === "Improve Hair Health");

    // If manage/improve fields exist, populate them from user object
    if (user.treatmentRoutine && document.getElementById("treatmentRoutine")) {
      document.getElementById("treatmentRoutine").value = user.treatmentRoutine;
    }
    if (user.concernAreas && document.getElementById("concernAreas")) {
      document.getElementById("concernAreas").value = user.concernAreas;
    }
    if (user.productsUsed && document.getElementById("productsUsed")) {
      document.getElementById("productsUsed").value = user.productsUsed;
    }
    if (user.careFrequency && document.getElementById("careFrequency")) {
      document.getElementById("careFrequency").value = user.careFrequency;
    }

    // Edit/save: enable inputs when editing, then persist on save
    const editBtn = document.getElementById("editProfileBtn");
    const saveBtn = document.getElementById("saveProfileBtn");
    if (editBtn && saveBtn) {
      editBtn.addEventListener("click", () => {
        // turn static profile-detail-value spans into inputs where appropriate
        document.querySelectorAll(".profile-detail-row").forEach(row => {
          const label = row.querySelector(".profile-detail-label")?.textContent?.trim();
          const valueSpan = row.querySelector(".profile-detail-value");
          if (!valueSpan || !label) return;

          // convert main fields to inputs (except Member Since)
          if (label !== "Member Since") {
            const input = document.createElement("input");
            input.className = "input-field profile-edit-input";
            input.value = (valueSpan.textContent === "--") ? "" : valueSpan.textContent;
            // store the label on the input for save mapping
            input.setAttribute("data-label", label);
            valueSpan.replaceWith(input);
          }
        });

        // enable goal-section inputs if any
        document.querySelectorAll(".goal-section input, .goal-section textarea").forEach(i => i.disabled = false);

        editBtn.style.display = "none";
        saveBtn.style.display = "inline-block";
      });

      saveBtn.addEventListener("click", () => {
        // gather inputs that we created
        const inputs = document.querySelectorAll(".profile-edit-input");
        inputs.forEach(input => {
          const label = input.getAttribute("data-label");
          const value = input.value.trim();
          const span = document.createElement("span");
          span.className = "profile-detail-value";
          span.textContent = value || "--";

          // replace input back to span
          input.replaceWith(span);

          // map back to user fields
          switch (label) {
            case "Username":
              user.username = value || "";
              break;
            case "Goal":
              user.goal = value || user.goal || localStorage.getItem(goalKey) || "Prevent Alopecia";
              break;
            case "Hair Type":
              user.hairType = value || "";
              break;
            case "Hair Texture":
              user.hairTexture = value || "";
              break;
          }
        });

        // save goal-specific fields if present
        if (document.getElementById("treatmentRoutine")) {
          user.treatmentRoutine = document.getElementById("treatmentRoutine").value.trim();
        }
        if (document.getElementById("concernAreas")) {
          user.concernAreas = document.getElementById("concernAreas").value.trim();
        }
        if (document.getElementById("productsUsed")) {
          user.productsUsed = document.getElementById("productsUsed").value.trim();
        }
        if (document.getElementById("careFrequency")) {
          user.careFrequency = document.getElementById("careFrequency").value.trim();
        }

        // persist
        setUser(user);
        // reflect goal changes immediately
        localStorage.setItem(goalKey, user.goal || localStorage.getItem(goalKey) || "Prevent Alopecia");
        // UI updates
        document.getElementById("profileGoal") && (document.getElementById("profileGoal").textContent = user.goal || "--");
        editBtn.style.display = "inline-block";
        saveBtn.style.display = "none";

        alert("Profile saved.");
      });
    }
  } // end profile handling

  /* -------------------------
     HOME & HISTORY CHARTS
     ------------------------- */
  const isChartPage = !!document.getElementById("tempChart") || !!document.getElementById("tensionChart") || !!document.getElementById("moistureChart");
  if (isChartPage) {
    // If no user navigate to login
    if (!user) {
      console.warn("No user for charts - redirecting to login.");
      window.location.href = "login.html";
      return;
    }

    const isBrianna = user.email && user.email.toLowerCase() === "brianna@example.com";

    // Helper to set metric text items (if they exist)
    const setMetric = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value ?? "--";
    };

    if (isBrianna) {
      // Use demo values (prefer history arrays if present)
      const tempVal = user.temperature ?? (user.history && user.history.temp && user.history.temp[user.history.temp.length - 1]) ?? "--";
      const tensionVal = user.tension ?? (user.history && user.history.tension && user.history.tension[user.history.tension.length - 1]) ?? "--";
      const moistureVal = user.moisture ?? (user.history && user.history.moisture && user.history.moisture[user.history.moisture.length - 1]) ?? "--";

      setMetric("tempValue", typeof tempVal === "number" ? `${tempVal}°C` : tempVal);
      setMetric("tensionValue", typeof tensionVal === "number" ? `${tensionVal} / 10` : tensionVal);
      setMetric("moistureValue", typeof moistureVal === "number" ? `${moistureVal}%` : moistureVal);

      setMetric("tempStatus", "Normal");
      setMetric("tensionStatus", "Healthy");
      setMetric("moistureStatus", "Optimal");

      // Initialize charts using Chart.js if canvases exist
      const safeInitChart = (canvasId, label, dataArr, color) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        // eslint-disable-next-line no-undef
        new Chart(canvas, {
          type: "line",
          data: {
            labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].slice(0, dataArr.length),
            datasets: [{
              label,
              data: dataArr,
              borderColor: color,
              tension: 0.3
            }]
          },
          options: { responsive: true }
        });
      };

      const history = user.history || { temp: [], tension: [], moisture: [] };
      safeInitChart("tempChart", "Temperature (°C)", history.temp.length ? history.temp : [36.4,36.5,36.6,36.5,36.5,36.4,36.5], "rgb(255,99,132)");
      safeInitChart("tensionChart", "Tension (1–10)", history.tension.length ? history.tension : [4,4,5,4,4,4,4], "rgb(54,162,235)");
      safeInitChart("moistureChart", "Moisture (%)", history.moisture.length ? history.moisture : [60,61,62,62,62,63,62], "rgb(75,192,192)");
    } else {
      // Non-demo users -- show placeholders
      ["tempValue","tensionValue","moistureValue","tempStatus","tensionStatus","moistureStatus"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "--";
      });
      document.querySelectorAll(".chart-wrapper").forEach(c => {
        c.innerHTML = "<p style='text-align:center; color:var(--text-muted)'>No data available</p>";
      });
    }
  } // end charts

  /* -------------------------
     INSIGHTS PAGE
     ------------------------- */
  if (document.body.classList.contains("insights-page") || document.getElementById("insightSummary")) {
    const summaryEl = document.getElementById("insightSummary") || document.getElementById("insightsSummary");
    if (!summaryEl) {
      // try fallback id insightsSummary
      const fallback = document.getElementById("insightsSummary");
      if (fallback) summaryEl = fallback;
    }
    if (!summaryEl) {
      // nothing to do
    } else {
      if (!user) {
        summaryEl.textContent = "No user logged in.";
      } else if (user.email && user.email.toLowerCase() === "brianna@example.com") {
        // tailored Brianna demo insights
        summaryEl.textContent = user.goal === "Manage Alopecia"
          ? "Demo (Briana) — treatment progress appears stable; continue monitoring."
          : "Demo (Briana) — readings are stable. Maintain hydration and low-tension styling.";
        // populate insight items if present
        document.querySelectorAll(".insight-item .insight-text-body").forEach((el, idx) => {
          if (idx === 0) el.textContent = "Temperature stable this week.";
          if (idx === 1) el.textContent = "Moisture trending slightly up due to recent conditioning.";
          if (idx === 2) el.textContent = "Tension is within healthy range.";
        });
      } else {
        // Generic users
        summaryEl.textContent = "No data yet — start tracking with a connected headband or log sample readings.";
        document.querySelectorAll(".insight-item .insight-text-body").forEach(el => el.textContent = "--");
      }
    }
  }

}); // DOMContentLoaded

/*
 * static/js/dashboard.js
 * -------------------------
 * Chart.js configuration for the main dashboard: equipment status pie
 * chart, top-projects progress bar chart, and per-project progress gauges.
 * Expects `window.dashboardData` to be injected by dashboard/index.html
 * as a small JSON payload rendered server-side.
 */

document.addEventListener("DOMContentLoaded", function () {
  if (typeof Chart === "undefined" || !window.dashboardData) return;

  const data = window.dashboardData;
  const palette = {
    navy: "#1f3864",
    cyan: "#1583a8",
    amber: "#e8a317",
    green: "#1e8449",
    red: "#c0392b",
    grey: "#8a97a8",
  };

  renderStatusPieChart(data.statusDistribution);
  renderProjectBarChart(data.projectProgress);
  renderProgressGauges();

  function renderStatusPieChart(distribution) {
    const el = document.getElementById("statusPieChart");
    if (!el || !distribution) return;
    const labels = Object.keys(distribution);
    const values = Object.values(distribution);
    const colors = [palette.grey, palette.cyan, palette.navy, palette.amber, palette.green, palette.red, "#7a5c9e", "#c9820f"];

    new Chart(el, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length), borderWidth: 2, borderColor: "#fff" }],
      },
      options: {
        plugins: { legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } } },
        cutout: "62%",
      },
    });
  }

  function renderProjectBarChart(progress) {
    const el = document.getElementById("projectBarChart");
    if (!el || !progress) return;
    new Chart(el, {
      type: "bar",
      data: {
        labels: progress.labels,
        datasets: [
          {
            label: "Overall Progress (%)",
            data: progress.values,
            backgroundColor: palette.navy,
            borderRadius: 4,
            maxBarThickness: 32,
          },
        ],
      },
      options: {
        indexAxis: "y",
        plugins: { legend: { display: false } },
        scales: { x: { min: 0, max: 100, ticks: { callback: (v) => v + "%" } } },
      },
    });
  }

  function renderProgressGauges() {
    document.querySelectorAll(".progress-gauge").forEach(function (canvas) {
      const value = parseFloat(canvas.dataset.value || 0);
      new Chart(canvas, {
        type: "doughnut",
        data: {
          datasets: [
            {
              data: [value, 100 - value],
              backgroundColor: [gaugeColor(value), "#e7ebf1"],
              borderWidth: 0,
            },
          ],
        },
        options: {
          rotation: -90,
          circumference: 180,
          cutout: "75%",
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
        },
      });
    });
  }

  function gaugeColor(value) {
    if (value >= 80) return palette.green;
    if (value >= 40) return palette.amber;
    return palette.red;
  }
});

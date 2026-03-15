/* static/js/analytics.js */
/**
 * Handles the rendering of charts using dynamic data from Django.
 */

document.addEventListener("DOMContentLoaded", function () {
  const muscleValuesNode = document.getElementById("muscle-balance-values");
  const historyDataNode = document.getElementById("history-data");
  const radarCanvas = document.getElementById("muscleBalanceChart");
  const trendCanvas = document.getElementById("trendChart");
  const trendSelector = document.getElementById("trendSelector");

  if (!muscleValuesNode || !historyDataNode || !radarCanvas || !trendCanvas || !trendSelector) {
    return;
  }

  const FIXED_LABELS = ["Chest", "Back", "Shoulders", "Arms", "Legs & Glutes", "Core"];
  const backendValues = JSON.parse(muscleValuesNode.textContent || "[]");
  const historyData = JSON.parse(historyDataNode.textContent || "{}");

  const finalValues = backendValues.length === FIXED_LABELS.length ? backendValues : [0, 0, 0, 0, 0, 0];
  const maxUserValue = Math.max(...finalValues, 1);
  const optimalValue = maxUserValue * 0.8;
  const optimalData = [optimalValue, optimalValue, optimalValue, optimalValue, optimalValue, optimalValue];

  // Radar chart
  new Chart(radarCanvas, {
    type: "radar",
    data: {
      labels: FIXED_LABELS,
      datasets: [
        {
          label: "Your Volume",
          data: finalValues,
          fill: true,
          backgroundColor: "rgba(79, 70, 229, 0.25)",
          borderColor: "#4F46E5",
          pointBackgroundColor: "#4F46E5",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#4F46E5",
          borderWidth: 2,
          pointRadius: 4,
          zIndex: 2,
        },
        {
          label: "Optimal Balance",
          data: optimalData,
          fill: true,
          backgroundColor: "rgba(156, 163, 175, 0.08)",
          borderColor: "#9CA3AF",
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
          zIndex: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: -5 },
      scales: {
        r: {
          min: 0,
          angleLines: { color: "#F3F4F6" },
          grid: { color: "#F3F4F6" },
          ticks: { display: false },
          pointLabels: { font: { size: 11, weight: "600" }, color: "#6B7280" },
        },
      },
      plugins: {
        legend: { display: true, position: "bottom", labels: { usePointStyle: true, boxWidth: 8, font: { size: 10 } } },
        tooltip: { backgroundColor: "#111827", cornerRadius: 8 },
      },
    },
  });

  // Line chart
  let trendChartInstance = null;

  function renderTrendChart(exerciseName) {
    if (!exerciseName || !historyData[exerciseName]) {
      return;
    }

    const dataObj = historyData[exerciseName];
    if (trendChartInstance) {
      trendChartInstance.destroy();
    }

    trendChartInstance = new Chart(trendCanvas, {
      type: "line",
      data: {
        labels: dataObj.dates,
        datasets: [
          {
            label: "Weight (KG)",
            data: dataObj.weights,
            borderColor: "#4F46E5",
            backgroundColor: "rgba(79, 70, 229, 0.1)",
            borderWidth: 3,
            pointBackgroundColor: "#ffffff",
            pointBorderColor: "#4F46E5",
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#111827",
            padding: 10,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
              label: function (context) {
                return context.parsed.y + " KG";
              },
            },
          },
        },
        scales: {
          y: { beginAtZero: false, grid: { color: "#F3F4F6" }, border: { display: false } },
          x: { grid: { display: false }, border: { display: false } },
        },
      },
    });
  }

  if (trendSelector.value) {
    renderTrendChart(trendSelector.value);
  }

  trendSelector.addEventListener("change", function (e) {
    renderTrendChart(e.target.value);
  });
});
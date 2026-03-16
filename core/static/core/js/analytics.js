/**
 * static/core/js/analytics.js
 * Handles dynamic chart rendering using Chart.js, separating data hydration from visualization logic.
 */
document.addEventListener("DOMContentLoaded", function () {
    // 1. Data Hydration: Extract serialized payload from Django via the global window object.
    // This approach avoids brittle DOM parsing and securely transfers structured data.
    const pageData = window.IRONLOG_DATA || {};

    // ==========================================
    // 2. Muscle Balance Radar Chart Engine
    // ==========================================
    const radarCtx = document.getElementById('muscleBalanceChart');
    if (radarCtx && pageData.radarValues) {
        const FIXED_LABELS = ["Chest", "Back", "Shoulders", "Arms", "Legs & Glutes", "Core"];
        const backendValues = pageData.radarValues;

        // Data validation: Provide a fallback array to prevent rendering errors if the backend payload is malformed or incomplete.
        const finalValues = backendValues.length === FIXED_LABELS.length ? backendValues : [0, 0, 0, 0, 0, 0];

        // Calculate a dynamic baseline (80% of max volume) to provide users with a visual reference for balanced muscle training.
        const maxUserValue = Math.max(...finalValues, 1);
        const optimalValue = maxUserValue * 0.8;
        const optimalData = Array(6).fill(optimalValue);

        new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: FIXED_LABELS,
                datasets: [
                    {
                        label: 'Your Volume',
                        data: finalValues,
                        borderColor: '#4f6ef7',
                        backgroundColor: 'rgba(79, 110, 247, 0.25)',
                        pointBackgroundColor: '#4f6ef7',
                        pointRadius: 3,
                        borderWidth: 2,
                        zIndex: 2
                    },
                    {
                        label: 'Optimal Balance',
                        data: optimalData,
                        borderColor: '#9CA3AF',
                        backgroundColor: 'rgba(156, 163, 175, 0.08)',
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        zIndex: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    r: {
                        min: 0,
                        /* * Removed static 'max' limit to enable Chart.js auto-scaling.
                         * Since the backend now provides absolute volume counts rather than percentages,
                         * a static max would break the visual proportion and clip the data points.
                         */
                        ticks: { display: false },
                        grid: { color: '#e7ebf3' },
                        angleLines: { color: '#e7ebf3' },
                        pointLabels: { color: '#6a6d7a', font: { size: 12 } }
                    }
                }
            }
        });
    }

    // ==========================================
    // 3. Weight Progress Line Chart Engine
    // ==========================================
    const trendSelector = document.getElementById('trendSelector');
    const trendCtx = document.getElementById('trendChart');
    const historyData = pageData.historyData || {};

    // Memory Management: Store chart instance to allow proper destruction before re-rendering.
    let trendChartInstance = null;

    function renderTrendChart(exerciseName) {
        if (!exerciseName || !historyData[exerciseName] || !trendCtx) return;
        const dataObj = historyData[exerciseName];

        // Destroy existing chart instance before re-rendering to prevent Canvas context pollution and visual overlapping (flickering).
        if (trendChartInstance) {
            trendChartInstance.destroy();
        }

        trendChartInstance = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: dataObj.dates,
                datasets: [{
                    label: 'Weight (kg)',
                    data: dataObj.weights,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#3b82f6',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    // Apply bezier curve tension for smoother visual data progression.
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1b1b1f',
                        padding: 10,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: { label: function(context) { return context.parsed.y + ' KG'; } }
                    }
                },
                scales: {
                    y: { beginAtZero: false, grid: { color: '#e7ebf3' }, border: { display: false } },
                    x: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    }

    // Enable interactive data exploration by binding a change event to update the chart payload dynamically without page reloads.
    if (trendSelector && trendSelector.value) {
        renderTrendChart(trendSelector.value);
        trendSelector.addEventListener('change', function(e) {
            renderTrendChart(e.target.value);
        });
    }
});
/**
 * static/js/analytics.js
 * 处理使用来自 Django 的动态数据渲染图表的逻辑 (Handles rendering of charts using dynamic data from Django).
 */
document.addEventListener("DOMContentLoaded", function () {
    // 1. [核心逻辑 / Core Logic] 从全局 window 对象中提取动态数据 (Fetch dynamic data from the global window object)
    // 这种模式比解析 DOM 文本 (DOM parsing) 更安全、更高效。
    const pageData = window.IRONLOG_DATA || {};

    // ==========================================
    // 2. 肌群均衡雷达图引擎 (Muscle Balance Radar Chart Engine)
    // ==========================================
    const radarCtx = document.getElementById('muscleBalanceChart');
    if (radarCtx && pageData.radarValues) {
        const FIXED_LABELS = ["Chest", "Back", "Shoulders", "Arms", "Legs & Glutes", "Core"];
        const backendValues = pageData.radarValues;

        // 数据校验：如果后端数据长度不匹配，提供回退数组 (Fallback array)
        const finalValues = backendValues.length === FIXED_LABELS.length ? backendValues : [0,0,0,0,0,0];

        // 计算最优基准线 (Calculate Optimal Baseline)
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
                        // 沿用你旧代码中极其优美的强调色 (Accent color)
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
                plugins: { legend: { display: false } }, // 遵循你旧代码隐藏图例的设定
                scales: {
                    r: {
                        min: 0,
                        /* * 【底层逻辑修正】：移除了旧版的 max: 100。
                         * 因为现在的后端 `views.py` 传递的是动作的绝对计数值(如做过2次胸部动作)，
                         * 如果强行锁死 max=100，你的雷达图会缩成一个肉眼看不见的黑点。
                         * 移除 max 属性，让 Chart.js 引擎自动适应数据比例 (Auto-scaling)。
                         */
                        ticks: { display: false },
                        grid: { color: '#e7ebf3' }, // 沿用你的旧网格颜色
                        angleLines: { color: '#e7ebf3' },
                        pointLabels: { color: '#6a6d7a', font: { size: 12 } }
                    }
                }
            }
        });
    }

    // ==========================================
    // 3. 体重进度趋势图引擎 (Weight Progress Line Chart Engine)
    // ==========================================
    const trendSelector = document.getElementById('trendSelector');
    const trendCtx = document.getElementById('trendChart');
    const historyData = pageData.historyData || {};
    let trendChartInstance = null; // 存储图表实例以便后续销毁 (Store instance for later destruction)

    function renderTrendChart(exerciseName) {
        if (!exerciseName || !historyData[exerciseName] || !trendCtx) return;
        const dataObj = historyData[exerciseName];

        // 销毁旧图表实例，防止重叠污染导致 Canvas 闪烁 (Destroy old chart to prevent canvas pollution/flickering)
        if (trendChartInstance) trendChartInstance.destroy();

        trendChartInstance = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: dataObj.dates,
                datasets: [{
                    label: 'Weight (kg)',
                    data: dataObj.weights,
                    borderColor: '#3b82f6', // 沿用你旧代码的趋势蓝
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#3b82f6',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.3 // 平滑曲线 (Smooth bezier curves)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1b1b1f', // 匹配你的 --ink 变量
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

    // 监听下拉菜单的改变事件，动态更新图表数据 (Listen to 'change' event to update chart payload dynamically)
    if (trendSelector && trendSelector.value) {
        renderTrendChart(trendSelector.value);
        trendSelector.addEventListener('change', function(e) {
            renderTrendChart(e.target.value);
        });
    }
});
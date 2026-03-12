/* static/js/analytics.js */
/**
 * Handles the rendering of charts using dynamic data from Django.
 * 处理使用来自 Django 的动态数据渲染图表的逻辑。
 */

document.addEventListener('DOMContentLoaded', function() {
    // [Core Logic] Fetch dynamic data from the script tag | 从脚本标签中提取动态数据
    const dataElement = document.getElementById('analytics-data');
    if (!dataElement) return;
    
    const chartData = JSON.parse(dataElement.textContent);
    const muscleLabels = [
        'Chest',
        'Back',
        'Shoulders',
        'Arms',
        'Legs & Glutes',
        'Core'
    ];
    const balanceLabels = Array.isArray(chartData.muscleBalanceLabels) && chartData.muscleBalanceLabels.length === 6
        ? chartData.muscleBalanceLabels
        : muscleLabels;
    const balanceValues = Array.isArray(chartData.muscleBalanceValues) && chartData.muscleBalanceValues.length === 6
        ? chartData.muscleBalanceValues
        : null;

    // --- Weight Progress Chart | 体重进度图表 ---
    const weightCtx = document.getElementById('analyticsWeightChart');
    if (weightCtx) {
        new Chart(weightCtx, {
            type: 'line',
            data: {
                labels: chartData.weightLabels,
                datasets: [{
                    label: 'Weight (kg)',
                    data: chartData.weightValues,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    // --- Training Volume Chart | 训练容量图表 ---
    const volumeCtx = document.getElementById('volumeChart');
    if (volumeCtx) {
        new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: chartData.volumeLabels,
                datasets: [{
                    label: 'Total Volume (kg)',
                    data: chartData.volumeValues,
                    backgroundColor: '#8b5cf6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    // --- Muscle Balance Radar | 肌群均衡雷达图 ---
    const balanceCtx = document.getElementById('muscleBalanceChart');
    if (balanceCtx) {
        const hasBalanceData = Array.isArray(balanceValues);
        const radarValues = hasBalanceData ? balanceValues : [0, 0, 0, 0, 0, 0];

        new Chart(balanceCtx, {
            type: 'radar',
            data: {
                labels: balanceLabels,
                datasets: [
                    {
                        label: 'Muscle Balance',
                        data: radarValues,
                        borderColor: hasBalanceData ? '#4f6ef7' : 'rgba(0, 0, 0, 0)',
                        backgroundColor: hasBalanceData ? 'rgba(79, 110, 247, 0.25)' : 'rgba(0, 0, 0, 0)',
                        pointRadius: hasBalanceData ? 3 : 0,
                        pointBackgroundColor: '#4f6ef7'
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
                        max: 100,
                        ticks: {
                            display: true,
                            stepSize: 25
                        },
                        grid: { color: '#e7ebf3' },
                        angleLines: { color: '#e7ebf3' },
                        pointLabels: {
                            color: '#6a6d7a',
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }
});
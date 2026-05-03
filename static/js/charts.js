/*
 * charts.js
 * ---------
 * Helper functions for Chart.js charts used in analytics.html
 * This file provides reusable chart utilities.
 */

// ─────────────────────────────────────────────
// Global Chart Defaults
// ─────────────────────────────────────────────
Chart.defaults.font.family = "Poppins, sans-serif";
Chart.defaults.font.size   = 13;
Chart.defaults.color       = "#666";

// ─────────────────────────────────────────────
// Color Palette
// ─────────────────────────────────────────────
const CHART_COLORS = [
    "#27ae60", "#2980b9", "#f39c12",
    "#e74c3c", "#9b59b6", "#1abc9c",
    "#e67e22", "#795548"
];

// ─────────────────────────────────────────────
// Utility: Generate colors array
// ─────────────────────────────────────────────
function getColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(CHART_COLORS[i % CHART_COLORS.length]);
    }
    return colors;
}

// ─────────────────────────────────────────────
// Utility: Create Bar Chart
// ─────────────────────────────────────────────
function createBarChart(canvasId, labels, values, label = "Value") {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: getColors(labels.length),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#1a1a2e",
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(0,0,0,0.05)" }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// ─────────────────────────────────────────────
// Utility: Create Doughnut / Pie Chart
// ─────────────────────────────────────────────
function createDoughnutChart(canvasId, labels, values) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: getColors(labels.length),
                borderWidth: 2,
                borderColor: "#fff"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { padding: 16 }
                },
                tooltip: {
                    backgroundColor: "#1a1a2e",
                    padding: 12,
                    cornerRadius: 8,
                }
            }
        }
    });
}

// ─────────────────────────────────────────────
// Utility: Create Line Chart
// ─────────────────────────────────────────────
function createLineChart(canvasId, labels, values, label = "Value") {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                borderColor: "#27ae60",
                backgroundColor: "rgba(39,174,96,0.1)",
                borderWidth: 2.5,
                pointBackgroundColor: "#27ae60",
                pointRadius: 5,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#1a1a2e",
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(0,0,0,0.05)" }
                },
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 10 }
                }
            }
        }
    });
}
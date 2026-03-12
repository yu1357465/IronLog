document.addEventListener("DOMContentLoaded", function () {
    const heatmap = document.querySelector(".heatmap");

    for (let col = 0; col < 53; col++) {
        for (let row = 0; row < 7; row++) {
            const cell = document.createElement("div");
            cell.classList.add("heatmap-cell");
            heatmap.appendChild(cell);
        }
    }
});
document.addEventListener("DOMContentLoaded", function () {
  const heatmap = document.querySelector(".heatmap");

  if (heatmap) {
    for (let col = 0; col < 53; col++) {
      for (let row = 0; row < 7; row++) {
        const cell = document.createElement("div");
        cell.classList.add("heatmap-cell");
        heatmap.appendChild(cell);
      }
    }
  }

  const quickLogForm = document.querySelector(".quick-log-form");
  if (!quickLogForm) {
    return;
  }

  quickLogForm.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
    }
  });

  quickLogForm.addEventListener("submit", function () {
    const rows = quickLogForm.querySelectorAll(".exercise-row");
    const checkedBoxes = quickLogForm.querySelectorAll(".done-checkbox:checked");

    if (checkedBoxes.length === 0) {
      return;
    }

    rows.forEach((row) => {
      const checkbox = row.querySelector(".done-checkbox");
      if (!checkbox || checkbox.checked) {
        return;
      }

      const inputs = row.querySelectorAll('input[type="text"], input[type="number"]');
      inputs.forEach((input) => {
        input.disabled = true;
      });
    });
  });
});
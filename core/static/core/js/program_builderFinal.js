
function openExerciseModal(programId, dayName) {
  document.getElementById("modalProgramId").value = programId;
  document.getElementById("modalDayTitle").innerText = dayName;
  document.getElementById("exerciseModal").style.display = "flex";
}

function closeExerciseModal() {
  document.getElementById("exerciseModal").style.display = "none";
}

function saveAllChanges() {
  const payloadDiv = document.getElementById("saveWeekPayload");
  payloadDiv.innerHTML = "";

  const titleInputs = document.querySelectorAll(".program-title-input");
  titleInputs.forEach((input) => {
    const pid = input.getAttribute("data-pid");
    const name = input.value;
    payloadDiv.innerHTML += `<input type="hidden" name="p_id" value="${pid}">`;
    payloadDiv.innerHTML += `<input type="hidden" name="p_name" value="${name}">`;
  });

  document.getElementById("saveWeekForm").submit();
}

function filterLibrary() {
  const searchInput = document.getElementById("exerciseSearchInput");
  const filterText = searchInput.value.toLowerCase();
  const cards = document.querySelectorAll(".ex-lib-card");

  cards.forEach((card) => {
    const cardText = card.innerText.toLowerCase();
    card.style.display = cardText.includes(filterText) ? "flex" : "none";
  });
}

function selectMagicOption(name) {
  const magicInput = document.getElementById("magicInput");
  const magicDropdown = document.getElementById("magicDropdown");

  magicInput.value = name;
  magicDropdown.style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
  const magicInput = document.getElementById("magicInput");
  const magicDropdown = document.getElementById("magicDropdown");
  const magicOptions = document.querySelectorAll(".magic-option");

  if (!magicInput || !magicDropdown || magicOptions.length === 0) {
    return;
  }

  magicInput.addEventListener("input", function () {
    const filter = this.value.toLowerCase();
    let hasVisible = false;

    magicOptions.forEach((opt) => {
      const text = opt.innerText.toLowerCase();
      if (text.includes(filter)) {
        opt.style.display = "block";
        hasVisible = true;
      } else {
        opt.style.display = "none";
      }
    });

    magicDropdown.style.display = hasVisible && filter.length > 0 ? "block" : "none";
  });

  document.addEventListener("click", function (e) {
    if (e.target !== magicInput) {
      magicDropdown.style.display = "none";
    }
  });
});


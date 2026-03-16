/**
 * core/static/core/js/program_builderFinal.js
 */
document.addEventListener("DOMContentLoaded", function () {

  // 1. Modal Control
  const modal = document.getElementById('exerciseModal');
  const modalProgramId = document.getElementById('modalProgramId');
  const modalDayTitle = document.getElementById('modalDayTitle');

  // Pass the specific day and program ID to the pop-up so the new exercise goes to the correct list.
  document.querySelectorAll('.add-ex-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      modalProgramId.value = this.getAttribute('data-pid');
      modalDayTitle.innerText = this.getAttribute('data-day');
      modal.style.display = 'flex';
    });
  });

  const closeBtn = document.getElementById('closeModalBtn');
  if (closeBtn) {
    closeBtn.addEventListener('click', function() {
      modal.style.display = 'none';
    });
  }

  // 2. Auto-Save on Blur (Change)
  // Intent: Prevent data loss. In reality, users often forget to click a manual save button.
  // This waits for the user to finish typing and click away, then automatically saves all day titles at once.
  document.querySelectorAll('.program-title-input').forEach(input => {
    input.addEventListener('change', function() {
      const payloadDiv = document.getElementById('saveWeekPayload');
      payloadDiv.innerHTML = '';

      document.querySelectorAll('.program-title-input').forEach(inp => {
        const pid = inp.getAttribute('data-pid');
        const name = inp.value;
        payloadDiv.innerHTML += `<input type="hidden" name="p_id" value="${pid}">`;
        payloadDiv.innerHTML += `<input type="hidden" name="p_name" value="${name}">`;
      });

      document.getElementById('saveWeekForm').submit();
    });
  });

  // 3. Reset Week Confirmation
  // Intent: Stop the form from sending immediately to ask for confirmation, because deleting a full week's data cannot be undone.
  const resetForm = document.getElementById('resetWeekForm');
  if (resetForm) {
    resetForm.addEventListener('submit', function(e) {
      if (!confirm('Are you sure you want to reset the entire week? All exercises will be permanently deleted.')) {
        e.preventDefault();
      }
    });
  }

  // 4. Library Filter (Fast Search)
  // Intent: Hide non-matching exercises instantly in the browser.
  // Doing this locally is decisively faster and smoother than asking the server for new results every time a key is pressed.
  const searchInput = document.getElementById('exerciseSearchInput');
  if (searchInput) {
    searchInput.addEventListener('keyup', function() {
      const filterText = this.value.toLowerCase();
      document.querySelectorAll('.ex-lib-card').forEach(card => {
        const cardText = card.innerText.toLowerCase();
        card.style.display = cardText.includes(filterText) ? 'flex' : 'none';
      });
    });
  }

  // 5. Magic Input Dropdown (Autocomplete)
  const magicInput = document.getElementById('magicInput');
  const magicDropdown = document.getElementById('magicDropdown');
  const magicOptions = document.querySelectorAll('.pb-magic-option');

  if (magicInput && magicDropdown) {
    // Show matches as the user types.
    magicInput.addEventListener('input', function() {
      const filter = this.value.toLowerCase();
      let hasVisible = false;

      magicOptions.forEach(opt => {
        const text = opt.innerText.toLowerCase();
        if (text.includes(filter)) {
          opt.style.display = 'block';
          hasVisible = true;
        } else {
          opt.style.display = 'none';
        }
      });

      magicDropdown.style.display = (hasVisible && filter.length > 0) ? 'block' : 'none';
    });

    // Intent: When the user clicks a name, fill it in.
    // Counter-intuitively, this also secretly updates the dropdown category behind the scenes, saving the user from doing it manually.
    magicOptions.forEach(opt => {
      opt.addEventListener('click', function() {
        magicInput.value = this.getAttribute('data-name');
        const selectedCategory = this.getAttribute('data-category');

        const categoryDropdown = document.querySelector('select[name="new_exercise_category"]');
        if (categoryDropdown && selectedCategory) {
          categoryDropdown.value = selectedCategory;
        }

        magicDropdown.style.display = 'none';
      });
    });

    // Hide the dropdown if the user clicks anywhere else on the screen.
    document.addEventListener('click', function(e) {
      if (e.target !== magicInput) {
        magicDropdown.style.display = 'none';
      }
    });
  }
});
/**
 * static/core/js/dashboard.js
 * Handles client-side interactivity for the dashboard, specifically optimizing the Quick Log form submission.
 */
document.addEventListener("DOMContentLoaded", function () {

    /*
     * Note: Client-side heatmap generation has been removed.
     * Decision: The heatmap DOM nodes are now rendered server-side (SSR) by Django templates.
     * Keeping the JS generation would cause double-rendering conflicts and break the CSS grid layout.
     */

    // ==========================================
    // Quick Log Form Interception & Optimization
    // ==========================================
    const quickLogForm = document.querySelector('.quick-log-form');

    if (quickLogForm) {

        // Prevent accidental premature form submission.
        // Users often press 'Enter' anticipating field navigation rather than committing the entire workout.
        quickLogForm.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                return false;
            }
        });

        // Optimize payload serialization before sending to the Django backend.
        quickLogForm.addEventListener('submit', function (event) {
            const rows = quickLogForm.querySelectorAll('.exercise-row');
            const checkedBoxes = quickLogForm.querySelectorAll('.done-checkbox:checked');

            // If no individual sets are checked, assume the user intends to log the entire routine as completed.
            if (checkedBoxes.length === 0) {
                return true;
            }

            // Selective parsing mode: Disable inputs in unchecked rows so the browser omits them from the POST request payload.
            // This reduces backend parsing overhead and ensures only explicitly completed exercises are saved.
            rows.forEach(row => {
                const checkbox = row.querySelector('.done-checkbox');

                if (!checkbox.checked) {
                    const inputs = row.querySelectorAll('input[type="text"], input[type="number"]');
                    inputs.forEach(input => input.disabled = true);
                }
            });
        });
    }
});
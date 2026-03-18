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
    }
});
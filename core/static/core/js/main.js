/**
 * core/static/core/js/main.js
 * Global utility scripts for application-wide behavior.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Intent: Prevent duplicate form submissions globally for ALL forms on a page.
    // Decision: Use querySelectorAll to create a NodeList. This securely iterates through every form,
    // applying protective listeners without throwing null reference errors on formless pages.
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("submit", function () {
            // Scope the query to the specific form currently triggering the submit event
            const btn = form.querySelector("button[type='submit']");
            if (btn) {
                // Decision: Disable the button physically at the DOM level.
                // Visual feedback (opacity/cursor) for this state is handled exclusively by global.css via the :disabled pseudo-class to maintain strict separation of concerns.
                btn.disabled = true;

                // Optional UX: Update text to indicate processing state
                if (btn.innerText !== "") {
                    btn.innerText = "Processing...";
                }
            }
        });
    });
});
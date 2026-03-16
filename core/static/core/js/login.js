/**
 * core/static/core/js/login.js
 * Manages client-side form interactions and UX optimizations for the authentication workflow.
 */
document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // 1. Form Submission Optimization
    // ==========================================
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function () {
            const btn = form.querySelector("button[type='submit']");
            if (btn) {
                // Decision: Disable the submit button immediately upon form submission.
                // Intent: Prevent race conditions and server overload caused by users double-clicking the button during network latency.
                btn.disabled = true;

                // Intent: Provide immediate visual state feedback to reduce user anxiety and clarify that the system is processing the request.
                btn.innerText = "Logging in...";
            }
        });
    }

    // ==========================================
    // 2. Placeholder Link Interception
    // ==========================================
    const termsLink = document.getElementById('terms-link');
    const privacyLink = document.getElementById('privacy-link');

    // Decision: Intercept clicks on placeholder links for incomplete features.
    // Intent: Prevent default browser navigation (which would cause a jarring page reload or scroll to top) to maintain the current application state.
    if (termsLink) {
        termsLink.addEventListener('click', function(event) {
            event.preventDefault();
        });
    }
    if (privacyLink) {
        privacyLink.addEventListener('click', function(event) {
            event.preventDefault();
        });
    }
});
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    form.addEventListener("submit", function () {
        const btn = form.querySelector("button[type='submit']");
        btn.disabled = true;
    });
});
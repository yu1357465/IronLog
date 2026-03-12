// Login enhancement script
// 登录增强脚本

document.addEventListener("DOMContentLoaded", function () {

    // Prevent double submission
    // 防止重复提交
    const form = document.querySelector("form");
    form.addEventListener("submit", function () {
        const btn = form.querySelector("button[type='submit']");
        btn.disabled = true;
    });

});
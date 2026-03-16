/**
 * 登录页交互逻辑整合版 (Integrated Login Page Interactions)
 * 路径: core/static/core/js/login.js
 */
document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // 1. 防止重复提交 (Prevent double submission) - 继承自你的原版
    // ==========================================
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function () {
            const btn = form.querySelector("button[type='submit']");
            if (btn) {
                // 禁用按钮，切断重复点击的物理途径
                btn.disabled = true;
                // 反直觉提示：顺手加一个状态变更，给用户心理安慰
                btn.innerText = "Logging in...";
            }
        });
    }

    // ==========================================
    // 2. 拦截占位链接 (Intercept dummy links) - 来自最新解耦逻辑
    // ==========================================

    // 拦截服务条款与隐私政策的空链接
    const termsLink = document.getElementById('terms-link');
    const privacyLink = document.getElementById('privacy-link');

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
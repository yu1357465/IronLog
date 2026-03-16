// 监听 HTML 文档完全加载和解析完成的事件 (Listen for DOMContentLoaded event)
document.addEventListener("DOMContentLoaded", function () {

    /*
     * 🚨 错误修复注释 (Error Fix Note):
     * 移除了原有的 JS 热力图生成循环 (Removed the JS heatmap generation loop).
     * 底层逻辑 (Mechanism): 热力图的 DOM 节点目前由 Django 模板引擎进行服务器端渲染 (Server-Side Rendering, SSR).
     * 再次通过客户端脚本插入节点会导致双重渲染 (Double Rendering) 和网格布局破坏.
     */

    // ==========================================
    // 快速录入表单拦截逻辑 (Quick Log Form Interception)
    // ==========================================
    const quickLogForm = document.querySelector('.quick-log-form');

    if (quickLogForm) {

        // 1. 防止回车键误触提交 (Prevent accidental form submission via 'Enter' key)
        quickLogForm.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // 阻止默认的回车换行/提交行为 (Prevent default behavior)
                return false;
            }
        });

        // 2. 监听表单的提交动作 (Listen for the Submit Event)
        quickLogForm.addEventListener('submit', function (event) {
            // 获取所有的运动行和被勾选的复选框 (Select all rows and checked checkboxes)
            const rows = quickLogForm.querySelectorAll('.exercise-row');
            const checkedBoxes = quickLogForm.querySelectorAll('.done-checkbox:checked');

            // 如果一个都没勾选，视为“一键全部完成”，直接放行发给后端
            // (If none are checked, treat as "Complete All" and proceed with payload)
            if (checkedBoxes.length === 0) {
                return true;
            }

            // 如果勾选了部分动作，进入精准切割模式 (Enter selective parsing mode)
            rows.forEach(row => {
                const checkbox = row.querySelector('.done-checkbox');

                // 找出没打勾的那一行 (Identify unchecked rows)
                if (!checkbox.checked) {
                    const inputs = row.querySelectorAll('input[type="text"], input[type="number"]');

                    // 强制添加 disabled 属性，让浏览器丢弃这些多余数据
                    // (Set 'disabled' attribute to omit these inputs from the form payload)
                    inputs.forEach(input => input.disabled = true);
                }
            });
        });
    }
});
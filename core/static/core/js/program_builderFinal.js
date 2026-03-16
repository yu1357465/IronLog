document.addEventListener("DOMContentLoaded", function () {
  // 1. 弹窗控制逻辑 (Modal Control)
  const modal = document.getElementById('exerciseModal');
  const modalProgramId = document.getElementById('modalProgramId');
  const modalDayTitle = document.getElementById('modalDayTitle');

  // 监听所有“添加动作”按钮
  document.querySelectorAll('.add-ex-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      modalProgramId.value = this.getAttribute('data-pid');
      modalDayTitle.innerText = this.getAttribute('data-day');
      modal.style.display = 'flex';
    });
  });

  // 监听关闭按钮
  const closeBtn = document.getElementById('closeModalBtn');
  if (closeBtn) {
    closeBtn.addEventListener('click', function() {
      modal.style.display = 'none';
    });
  }

  // 2. 现代化改造：失焦自动保存逻辑 (Auto-Save on Blur / Change)
  document.querySelectorAll('.program-title-input').forEach(input => {
    // 监听 'change' 事件：当用户输入完内容，并且鼠标点到其他地方失去焦点时触发
    input.addEventListener('change', function() {
      const payloadDiv = document.getElementById('saveWeekPayload');
      payloadDiv.innerHTML = ''; // 清空上一轮的缓存

      // 抓取页面上所有的标题输入框，准备统一打包发送
      document.querySelectorAll('.program-title-input').forEach(inp => {
        const pid = inp.getAttribute('data-pid');
        const name = inp.value;
        payloadDiv.innerHTML += `<input type="hidden" name="p_id" value="${pid}">`;
        payloadDiv.innerHTML += `<input type="hidden" name="p_name" value="${name}">`;
      });

      // 隐藏式提交表单，触发页面瞬间刷新保存
      document.getElementById('saveWeekForm').submit();
    });
  });

  // 3. 重置周计划的二次确认 (Reset Week Confirm)
  const resetForm = document.getElementById('resetWeekForm');
  if (resetForm) {
    resetForm.addEventListener('submit', function(e) {
      if (!confirm('Are you sure you want to reset the entire week? All exercises will be permanently deleted.')) {
        e.preventDefault();
      }
    });
  }

  // 4. 极速前端动作搜索引擎 (Library Filter)
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

  // 5. 手工魔法框联动逻辑 (Magic Input Dropdown)
  const magicInput = document.getElementById('magicInput');
  const magicDropdown = document.getElementById('magicDropdown');
  const magicOptions = document.querySelectorAll('.pb-magic-option');

  if (magicInput && magicDropdown) {
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

    // 点击下拉选项填入输入框
    magicOptions.forEach(opt => {
      opt.addEventListener('click', function() {
        // 🚨 新增完整的双向回填逻辑
        magicInput.value = this.getAttribute('data-name');
        const selectedCategory = this.getAttribute('data-category'); // 提取刚才埋好的分类数据

        // 精准制导：找到右侧的分类下拉框，并强制切换它的值
        const categoryDropdown = document.querySelector('select[name="new_exercise_category"]');
        if (categoryDropdown && selectedCategory) {
          categoryDropdown.value = selectedCategory;
        }

        magicDropdown.style.display = 'none';
      });
    });

    // 点击空白处收起下拉菜单
    document.addEventListener('click', function(e) {
      if (e.target !== magicInput) {
        magicDropdown.style.display = 'none';
      }
    });
  }
});
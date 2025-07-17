// 初始化所有模态框
document.addEventListener('DOMContentLoaded', function() {
    // 为所有模态框添加事件监听
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        // 模态框显示时的事件
        modal.addEventListener('show.bs.modal', function (event) {
            // 可以在这里添加模态框显示时的逻辑
        });

        // 模态框隐藏时的事件
        modal.addEventListener('hide.bs.modal', function (event) {
            // 可以在这里添加模态框隐藏时的逻辑
        });
    });

    // 为所有删除按钮添加确认对话框
    var deleteButtons = document.querySelectorAll('button[type="submit"][onclick]');
    deleteButtons.forEach(function(button) {
        // 确保只处理包含确认对话框的按钮
        if (button.getAttribute('onclick').includes('confirm')) {
            button.addEventListener('click', function(e) {
                // 这里可以添加额外的确认逻辑
            });
        }
    });

    // 为搜索框添加实时搜索功能
    var searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();
            var table = this.closest('div').nextElementSibling;
            if (table && table.tagName === 'TABLE') {
                var rows = table.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    var rowText = row.textContent.toLowerCase();
                    if (rowText.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });
});

// 表单验证
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return false;

    var inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    var isValid = true;

    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            isValid = false;
            // 添加错误样式
            input.classList.add('is-invalid');

            // 添加错误提示
            var errorDiv = input.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = '此字段不能为空';
                input.parentNode.insertBefore(errorDiv, input.nextSibling);
            }
        } else {
            // 移除错误样式
            input.classList.remove('is-invalid');

            // 移除错误提示
            var errorDiv = input.nextElementSibling;
            if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                input.parentNode.removeChild(errorDiv);
            }
        }
    });

    return isValid;
}

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// 自动关闭提示消息
window.setTimeout(function() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        // 淡出效果
        alert.style.transition = 'opacity 1s';
        alert.style.opacity = '0';

        // 完全透明后隐藏元素
        setTimeout(function() {
            alert.style.display = 'none';
        }, 1000);
    });
}, 5000); // 5秒后自动关闭
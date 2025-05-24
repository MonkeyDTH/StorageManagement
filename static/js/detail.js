/**
 * 属性编辑器控制器
 * @description 管理详情页的属性编辑交互逻辑
 */
class PropertyEditor {
    constructor() {
        this.editMode = false;
        this.$form = document.getElementById('propertyForm');
        this.$view = document.getElementById('propertyView');
        this.$toggleBtn = document.getElementById('editToggle');
        this.$cancelBtn = document.getElementById('cancelEdit');
        // 添加表单输入框集合
        this.$inputs = this.$form.querySelectorAll('input, select, textarea');
        this.bindEvents();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        this.$toggleBtn.addEventListener('click', () => this.toggleEdit());
        this.$cancelBtn.addEventListener('click', () => this.cancelEdit());
        this.$form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    /**
     * 切换编辑模式
     */
    toggleEdit() {
        this.editMode = !this.editMode;
        
        if (this.editMode) {
            // 进入编辑模式
            this.originalValues = [...this.$inputs].map(input => input.value);
            this.$view.style.display = 'none';  // 修改为 this.$view
            this.$form.style.display = 'block';  // 修改为 this.$form
            this.$toggleBtn.innerHTML = '<i class="bi bi-x-circle"></i> 取消';
        } else {
            // 退出编辑模式
            this.$view.style.display = 'block';  // 修改为 this.$view
            this.$form.style.display = 'none';  // 修改为 this.$form
            this.$toggleBtn.innerHTML = '<i class="bi bi-pencil-square"></i> 编辑';
        }
    }

    /**
     * 取消编辑操作
     */
    cancelEdit() {
        // 恢复原始值
        [...this.$inputs].forEach((input, index) => {
            input.value = this.originalValues[index];
        });
        
        // 退出编辑模式
        this.editMode = false;
        this.$view.style.display = 'block';
        this.$form.style.display = 'none';
        this.$toggleBtn.innerHTML = '<i class="bi bi-pencil-square"></i> 编辑';
    }

    /**
     * 收集表单数据
     * @returns {Object} 表单数据对象
     */
    collectFormData() {
        const formData = {
            item_id: this.$form.dataset.itemId,
            item_type: this.$form.dataset.itemType
        };

        this.$inputs.forEach(input => {
            formData[input.id] = input.value;
        });

        return formData;
    }

    /**
     * 处理表单提交
     * @param {Event} e 表单提交事件
     */
    async handleSubmit(e) {
        e.preventDefault();
        const formData = this.collectFormData();
        
        try {
            const response = await fetch('/update_properties', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`服务器返回了非JSON数据: ${text.substring(0, 100)}...`);
            }
            
            const result = await response.json();
            if (result.success) {
                this.showSuccessFeedback();
                location.reload(); // 刷新页面获取最新数据
            } else {
                this.showErrorFeedback(result.message);
            }
        } catch (error) {
            this.showErrorFeedback(`请求处理失败: ${error.message}`);
            console.error('API请求错误详情:', error);
        }
    }

    /**
     * 显示成功反馈
     */
    showSuccessFeedback() {
        const toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.innerHTML = `
            <div class="toast show" role="alert">
                <div class="toast-header bg-morandi-green text-white">
                    <strong class="me-auto">操作成功</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    数据已保存成功
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    /**
     * 显示错误反馈
     * @param {string} message 错误消息
     */
    showErrorFeedback(message) {
        // 创建一个Bootstrap警告提示
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // 插入到表单上方
        this.$form.parentNode.insertBefore(alertDiv, this.$form);
        
        // 5秒后自动消失
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// 初始化编辑器
document.addEventListener('DOMContentLoaded', () => {
    new PropertyEditor();
});
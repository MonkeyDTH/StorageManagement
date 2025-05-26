/**
 * @Author: Leili
 * @Date: 2025-05-23
 * @Description: 新建条目页面交互逻辑
 */

/**
 * 新建条目控制器
 * @description 管理新建页面的表单提交逻辑
 */
class NewItemController {
    constructor() {
        this.$form = document.getElementById('newItemForm');
        this.$inputs = this.$form.querySelectorAll('input, select, textarea');
        this.bindEvents();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        this.$form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    /**
     * 收集表单数据
     * @returns {Object} 表单数据对象
     */
    collectFormData() {
        const formData = {
            item_type: this.$form.dataset.itemType
        };

        this.$inputs.forEach(input => {
            if (input.value.trim() !== '') {
                formData[input.id] = input.value;
            }
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
        
        // 验证必填字段
        if (!formData.name || formData.name.trim() === '') {
            alert('请填写手办名称');
            return;
        }
        
        try {
            const response = await fetch('/create_item', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`服务器返回了非JSON数据: ${text.substring(0, 100)}...`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                alert('新建成功！');
                window.location.href = '/figures';
            } else {
                alert(`新建失败: ${result.message}`);
            }
        } catch (error) {
            console.error('提交失败:', error);
            alert(`提交失败: ${error.message}`);
        }
    }
}

// 页面加载完成后初始化控制器
document.addEventListener('DOMContentLoaded', () => {
    new NewItemController();
});
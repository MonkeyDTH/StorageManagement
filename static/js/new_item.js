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
        this.$inputs = this.$form.querySelectorAll('input:not([type="file"]), select, textarea');
        this.$imageUpload = document.getElementById('image_upload');
        this.bindEvents();
        
        // 添加图片预览区域
        if (this.$imageUpload) {
            this.createImagePreview();
        }
    }

    /**
     * 创建图片预览区域
     */
    createImagePreview() {
        // 创建预览容器
        this.$previewContainer = document.createElement('div');
        this.$previewContainer.className = 'mb-3 text-center d-none';
        this.$previewContainer.innerHTML = `
            <div class="border rounded p-2 mb-2">
                <img id="imagePreview" class="img-fluid rounded" style="max-height: 200px;">
            </div>
            <button type="button" class="btn btn-sm btn-outline-secondary" id="removeImage">移除图片</button>
        `;
        
        // 插入到图片上传字段后面
        this.$imageUpload.parentNode.insertAdjacentElement('afterend', this.$previewContainer);
        
        // 获取预览图片元素
        this.$imagePreview = document.getElementById('imagePreview');
        this.$removeImageBtn = document.getElementById('removeImage');
        
        // 绑定图片预览事件
        this.$imageUpload.addEventListener('change', (e) => this.handleImagePreview(e));
        this.$removeImageBtn.addEventListener('click', () => this.removeImage());
    }

    /**
     * 处理图片预览
     * @param {Event} e 图片选择事件
     */
    handleImagePreview(e) {
        const file = e.target.files[0];
        if (file && file.type.match('image.*')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.$imagePreview.src = e.target.result;
                this.$previewContainer.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }
    }

    /**
     * 移除已选择的图片
     */
    removeImage() {
        this.$imageUpload.value = '';
        this.$previewContainer.classList.add('d-none');
        this.$imagePreview.src = '';
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        this.$form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    /**
     * 收集表单数据
     * @returns {FormData} 表单数据对象
     */
    collectFormData() {
        const formData = new FormData();
        formData.append('item_type', this.$form.dataset.itemType);

        // 添加普通字段
        this.$inputs.forEach(input => {
            if (input.value.trim() !== '') {
                formData.append(input.id, input.value);
            }
        });

        // 添加图片文件（如果有）
        if (this.$imageUpload && this.$imageUpload.files[0]) {
            formData.append('image', this.$imageUpload.files[0]);
        }

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
        if (!formData.get('name') || formData.get('name').trim() === '') {
            alert('请填写物品名称');
            return;
        }
        
        try {
            const response = await fetch('/create_item', {
                method: 'POST',
                body: formData // 不设置Content-Type，让浏览器自动处理
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`服务器返回了非JSON数据: ${text.substring(0, 100)}...`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                alert('新建成功！');
                // 根据物品类型跳转到对应列表页
                const itemType = this.$form.dataset.itemType;
                window.location.href = `/${itemType}`;
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
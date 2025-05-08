// 使用字符串变量跟踪当前视图状态：'gallery', 'table', 'stats'
let currentView = 'table';

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化视图
    showView('table');
    
    // 根据屏幕尺寸显示相应控制区域
    if (window.innerWidth < 992) {
        document.querySelector('.mobile-controls').classList.remove('d-none');
        document.querySelector('.mobile-controls').classList.add('d-block');
    }
    
    // 绑定事件监听器
    initEventListeners();
});

// 响应式布局处理
window.addEventListener('resize', function() {
    if (window.innerWidth < 992) {
        document.querySelector('.mobile-controls').classList.remove('d-none');
        document.querySelector('.mobile-controls').classList.add('d-block');
    } else {
        document.querySelector('.mobile-controls').classList.remove('d-block');
        document.querySelector('.mobile-controls').classList.add('d-none');
    }
});

// 初始化所有事件监听器
function initEventListeners() {
    // PC端视图切换功能
    document.getElementById('desktopToggleView').addEventListener('click', function() {
        toggleNextView();
    });
    
    // 移动端视图切换功能
    document.getElementById('mobileToggleView').addEventListener('click', function() {
        toggleNextView();
    });
    
    // 类别筛选功能
    document.getElementById('mainCategorySelect').addEventListener('change', function() {
        const mainCategory = this.value;
        const subSelect = document.getElementById('subCategorySelect');
        
        if (mainCategory) {
            subSelect.disabled = false;
            // 更新子类别选项
            updateSubCategories(mainCategory);
            // 重置子类别选择
            subSelect.value = '';
            // 筛选主类别
            filterByCategory(mainCategory);
        } else {
            subSelect.disabled = true;
            subSelect.value = '';
            // 清除筛选
            filterByCategory('');
        }
    });
    
    document.getElementById('subCategorySelect').addEventListener('change', function() {
        filterByCategory(this.value);
    });
    
    document.getElementById('mobileCategorySelect').addEventListener('change', function() {
        filterByCategory(this.value);
    });
    
    // 卡片点击事件
    document.querySelectorAll('.item-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // 获取当前卡片的物品ID
            const itemId = this.getAttribute('data-id');
            
            if (itemId && !e.target.closest('.btn-outline-danger') && !e.target.closest('.btn-outline-primary')) {
                // 添加点击动画类
                this.classList.add('clicked');
                setTimeout(() => {
                    window.location.href = `/edit/${itemId}`;
                }, 300);
            }
        });
    });
}

// 显示指定视图
function showView(viewName) {
    // 隐藏所有视图
    document.getElementById('galleryView').style.display = 'none';
    document.getElementById('tableView').style.display = 'none';
    
    // 如果存在统计视图，也隐藏它
    const statsView = document.getElementById('statsView');
    if (statsView) {
        statsView.style.display = 'none';
    }
    
    // 显示指定的视图
    if (viewName === 'gallery') {
        document.getElementById('galleryView').style.display = 'flex';
    } else if (viewName === 'table') {
        document.getElementById('tableView').style.display = 'block';
    } else if (viewName === 'stats' && statsView) {
        statsView.style.display = 'block';
    }
    
    // 更新当前视图状态
    currentView = viewName;
    
    // 更新按钮图标
    updateViewButtons();
}

// 更新视图切换按钮的图标
function updateViewButtons() {
    const desktopToggleBtn = document.getElementById('desktopToggleView');
    const mobileToggleBtn = document.getElementById('mobileToggleView');
    
    if (currentView === 'gallery') {
        desktopToggleBtn.innerHTML = '<i class="bi bi-grid"></i> 切换视图';
        mobileToggleBtn.innerHTML = '<i class="bi bi-grid"></i>';
    } else if (currentView === 'table') {
        desktopToggleBtn.innerHTML = '<i class="bi bi-table"></i> 切换视图';
        mobileToggleBtn.innerHTML = '<i class="bi bi-table"></i>';
    } else if (currentView === 'stats') {
        desktopToggleBtn.innerHTML = '<i class="bi bi-bar-chart"></i> 切换视图';
        mobileToggleBtn.innerHTML = '<i class="bi bi-bar-chart"></i>';
    }
}

// 切换到下一个视图
function toggleNextView() {
    if (currentView === 'gallery') {
        showView('table');
    } else if (currentView === 'table') {
        // 检查是否存在统计视图
        if (document.getElementById('statsView')) {
            showView('stats');
        } else {
            showView('gallery');
        }
    } else {
        showView('gallery');
    }
}

// 更新子类别选项
function updateSubCategories(mainCategory) {
    const subSelect = document.getElementById('subCategorySelect');
    
    // 清空现有选项
    while (subSelect.options.length > 1) {
        subSelect.remove(1);
    }
    
    // 添加新的子类别选项
    const categories = JSON.parse(document.getElementById('categoriesData').textContent);
    categories.forEach(cat => {
        if (cat.main === mainCategory && cat.sub) {
            const option = document.createElement('option');
            option.value = cat.full;
            option.textContent = cat.sub;
            subSelect.appendChild(option);
        }
    });
}

// 分类筛选功能
function filterByCategory(category) {
    const baseUrl = '/';
    const url = new URL(baseUrl, window.location.origin);
    
    // 清除现有筛选参数
    url.searchParams.delete('category');
    url.searchParams.delete('main_category');
    
    if (category) {
        url.searchParams.set('category', category);
    }
    
    window.location.href = url.toString();
}
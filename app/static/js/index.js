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
    document.getElementById('categorySelect').addEventListener('change', function() {
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

// 分类筛选功能
function filterByCategory(category) {
    // 构建URL，区分是主分类还是子分类
    const baseUrl = '/';
    
    if (category === '') {
        window.location.href = baseUrl;
        return;
    }
    
    const url = new URL(baseUrl, window.location.origin);
    url.searchParams.set('category', category);
    
    // 添加一个参数来标识是否为主分类
    if (!category.includes('-')) {
        url.searchParams.set('main_category', 'true');
    } else {
        url.searchParams.delete('main_category');
    }
    
    window.location.href = url.toString();
}
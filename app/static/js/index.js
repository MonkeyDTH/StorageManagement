// 使用字符串变量跟踪当前视图状态：'gallery', 'table'
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
    const desktopToggleBtn = document.getElementById('desktopToggleView');
    if (desktopToggleBtn) {
        desktopToggleBtn.addEventListener('click', function() {
            toggleNextView();
        });
    }
    
    // 移动端视图切换功能
    const mobileToggleBtn = document.getElementById('mobileToggleView');
    if (mobileToggleBtn) {
        mobileToggleBtn.addEventListener('click', function() {
            toggleNextView();
        });
    }
    
    // 类别筛选功能
    const mainCategorySelect = document.getElementById('mainCategorySelect');
    
    if (mainCategorySelect) {
        mainCategorySelect.addEventListener('change', function() {
            const mainCategory = this.value;
            filterByCategory(mainCategory);
        });
    }
    
    // 卡片点击事件
    document.querySelectorAll('.item-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // 获取当前卡片的物品ID
            const itemId = this.getAttribute('data-id');
            
            if (itemId && !e.target.closest('.btn-outline-danger') && !e.target.closest('.btn-outline-primary')) {
                // 加载该卡片中的图片（如果有）
                const lazyImage = this.querySelector('.lazy-image');
                if (lazyImage && lazyImage.dataset.src && (!lazyImage.src || lazyImage.src === '')) {
                    lazyImage.src = lazyImage.dataset.src;
                }
                
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
    
    // 显示指定的视图
    if (viewName === 'gallery') {
        document.getElementById('galleryView').style.display = 'flex';
        
    } else if (viewName === 'table') {
        document.getElementById('tableView').style.display = 'block';
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
    
    if (!desktopToggleBtn || !mobileToggleBtn) return;
    
    if (currentView === 'gallery') {
        desktopToggleBtn.innerHTML = '<i class="bi bi-grid"></i> 切换视图';
        mobileToggleBtn.innerHTML = '<i class="bi bi-grid"></i>';
    } else if (currentView === 'table') {
        desktopToggleBtn.innerHTML = '<i class="bi bi-table"></i> 切换视图';
        mobileToggleBtn.innerHTML = '<i class="bi bi-table"></i>';
    }
}

// 切换到下一个视图
function toggleNextView() {
    if (currentView === 'gallery') {
        showView('table');
    } else {
        showView('gallery');
    }
}

// 分类筛选功能
function filterByCategory(main_category) {
    console.log('筛选参数:', main_category);
    const baseUrl = '/';
    const url = new URL(baseUrl, window.location.origin);
    
    // 清除现有筛选参数
    url.searchParams.delete('main_category');
    
    if (main_category) {
        url.searchParams.set('main_category', main_category);
    }
    
    console.log('生成的URL:', url.toString());
    
    // 保存当前视图状态
    const currentView = document.getElementById('galleryView').style.display === 'none' ? 'table' : 'gallery';
    localStorage.setItem('viewPreference', currentView);
    
    // 直接跳转到带参数的URL
    window.location.href = url.toString();
}

// 懒加载图片函数
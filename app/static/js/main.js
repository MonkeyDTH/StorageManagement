// 页面加载时确保只显示画廊视图
document.addEventListener('DOMContentLoaded', function() {
    // 初始化视图
    initializeView();
    
    // 设置事件监听器
    setupEventListeners();
    
    // 根据屏幕尺寸显示相应控制区域
    handleResponsiveDisplay();
});

// 初始化视图
function initializeView() {
    const galleryView = document.getElementById('galleryView');
    const tableView = document.getElementById('tableView');
    
    if (galleryView && tableView) {
        galleryView.style.display = 'flex';
        tableView.style.display = 'none';
    }
    
    // 检查本地存储中的视图偏好
    const viewPreference = localStorage.getItem('viewPreference');
    if (viewPreference === 'table') {
        toggleView();
    }
}

// 设置事件监听器
function setupEventListeners() {
    // PC端视图切换功能
    const desktopToggleBtn = document.getElementById('desktopToggleView');
    if (desktopToggleBtn) {
        desktopToggleBtn.addEventListener('click', function() {
            toggleView();
        });
    }
    
    // 移动端视图切换功能
    const mobileToggleBtn = document.getElementById('mobileToggleView');
    if (mobileToggleBtn) {
        mobileToggleBtn.addEventListener('click', function() {
            toggleView();
        });
    }
    
    // 卡片点击事件
    const itemCards = document.querySelectorAll('.item-card');
    itemCards.forEach(card => {
        card.addEventListener('click', function(e) {
            handleCardClick(this, e);
        });
    });
    
    // 窗口大小变化事件
    window.addEventListener('resize', handleResponsiveDisplay);
}

// 视图切换通用函数
function toggleView() {
    const galleryView = document.getElementById('galleryView');
    const tableView = document.getElementById('tableView');
    const desktopToggleBtn = document.getElementById('desktopToggleView');
    const mobileToggleBtn = document.getElementById('mobileToggleView');
    
    if (!galleryView || !tableView) return;
    
    if (galleryView.style.display === 'none') {
        // 切换回画廊视图
        galleryView.style.display = 'flex';
        tableView.style.display = 'none';
        
        if (desktopToggleBtn) {
            desktopToggleBtn.innerHTML = '<i class="bi bi-grid"></i> 切换视图';
        }
        
        if (mobileToggleBtn) {
            mobileToggleBtn.innerHTML = '<i class="bi bi-grid"></i>';
        }
        
        localStorage.setItem('viewPreference', 'gallery');
    } else {
        // 切换到表格视图
        galleryView.style.display = 'none';
        tableView.style.display = 'block';
        
        if (desktopToggleBtn) {
            desktopToggleBtn.innerHTML = '<i class="bi bi-table"></i> 切换视图';
        }
        
        if (mobileToggleBtn) {
            mobileToggleBtn.innerHTML = '<i class="bi bi-table"></i>';
        }
        
        localStorage.setItem('viewPreference', 'table');
    }
}

// 处理卡片点击事件
function handleCardClick(card, e) {
    // 获取当前卡片的物品ID
    const itemId = card.getAttribute('data-id');
    
    if (itemId && !e.target.closest('.btn-outline-danger') && !e.target.closest('.btn-outline-primary')) {
        // 添加点击动画类
        card.classList.add('clicked');
        setTimeout(() => {
            window.location.href = `/edit/${itemId}`;
        }, 300);
    }
}

// 响应式布局处理
function handleResponsiveDisplay() {
    const mobileControls = document.querySelector('.mobile-controls');
    const filteredResults = document.querySelector('.filtered-results');
    
    if (!mobileControls) return;
    
    if (window.innerWidth < 992) {
        mobileControls.style.display = 'block';
        if (filteredResults) {
            filteredResults.style.marginTop = '20px';
        }
    } else {
        mobileControls.style.display = 'none';
        if (filteredResults) {
            filteredResults.style.marginTop = '0';
        }
    }
}

// 分类筛选函数
function filterByCategory(category) {
    // 构建URL，区分是主分类还是子分类
    let url = new URL(window.location.href);
    if (category === '') {
        // 重置为首页
        url = new URL(window.location.origin + '/');
    } else {
        url.searchParams.set('category', category);
        // 添加一个参数来标识是否为主分类
        if (!category.includes('-')) {
            url.searchParams.set('main_category', 'true');
        } else {
            url.searchParams.delete('main_category');
        }
    }
    window.location.href = url.toString();
}
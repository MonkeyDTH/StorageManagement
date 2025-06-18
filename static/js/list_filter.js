/**
 * @Author: Leili
 * @Date: 2025-05-28
 * @Description: 物品列表筛选功能
 */

/**
 * 列表筛选控制器
 * @description 管理物品列表页面的筛选功能
 */
class ListFilterController {
    /**
     * 构造函数
     * @description 初始化筛选控制器
     */
    constructor() {
        // 获取DOM元素
        this.$categoryFilter = document.getElementById('categoryFilter');
        this.$resetFilter = document.getElementById('resetFilter');
        this.$showAllItems = document.getElementById('showAllItems');
        this.$filterStatus = document.getElementById('filterStatus');
        this.$filterStatusText = document.getElementById('filterStatusText');
        this.$tableBody = document.getElementById('itemsTableBody');
        this.$noDataMessage = document.getElementById('noDataMessage');
        
        // 获取当前页面类型（figures或clothing）
        this.pageType = window.location.pathname.split('/')[1] || '';
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化筛选状态
        this.initFilterState();
    }
    
    /**
     * 绑定事件处理函数
     */
    bindEvents() {
        // 子类别筛选变化事件
        this.$categoryFilter.addEventListener('change', () => this.applyFilter());
        
        // 重置筛选按钮点击事件
        this.$resetFilter.addEventListener('click', () => this.resetFilter());
        
        // 显示全部按钮点击事件
        this.$showAllItems.addEventListener('click', () => this.resetFilter());
    }
    
    /**
     * 初始化筛选状态
     * @description 从localStorage加载上次的筛选设置
     */
    initFilterState() {
        // 尝试从localStorage获取上次的筛选设置
        const savedFilter = localStorage.getItem(`${this.pageType}_category_filter`);
        
        if (savedFilter) {
            // 设置下拉框的值
            this.$categoryFilter.value = savedFilter;
            
            // 应用筛选
            this.applyFilter();
        } else {
            // 如果没有保存的筛选设置，但在figures页面且存在categoryStats，也需要初始化价格统计显示
            if (this.pageType === 'figures' && typeof categoryStats !== 'undefined') {
                this.updatePriceStats('');
            }
        }
    }
    
    /**
     * 应用筛选
     * @description 根据筛选条件过滤表格数据
     */
    applyFilter() {
        const categoryValue = this.$categoryFilter.value;
        
        // 保存筛选设置到localStorage
        if (this.pageType) {
            localStorage.setItem(`${this.pageType}_category_filter`, categoryValue);
        }
        
        // 获取所有行
        const rows = this.$tableBody.querySelectorAll('tr');
        
        // 筛选计数器
        let visibleCount = 0;
        
        // 遍历所有行应用筛选
        rows.forEach(row => {
            const rowCategory = row.getAttribute('data-category');
            
            // 如果没有选择类别或类别匹配，则显示行
            if (!categoryValue || rowCategory === categoryValue) {
                row.classList.remove('d-none');
                visibleCount++;
            } else {
                row.classList.add('d-none');
            }
        });
        
        // 更新筛选状态显示
        this.updateFilterStatus(categoryValue, visibleCount, rows.length);
        
        // 显示或隐藏无数据提示
        if (visibleCount === 0) {
            this.$noDataMessage.classList.remove('d-none');
        } else {
            this.$noDataMessage.classList.add('d-none');
        }
        
        // 更新价格统计显示（如果在figures页面且存在categoryStats）
        if (this.pageType === 'figures' && typeof categoryStats !== 'undefined') {
            this.updatePriceStats(categoryValue);
        }
    }
    
    /**
     * 更新价格统计显示
     * @param {string} category 当前筛选的类别
     */
    updatePriceStats(category) {
        // 获取价格统计显示元素
        const purchasePriceDisplay = document.getElementById('purchasePriceDisplay');
        const soldPriceDisplay = document.getElementById('soldPriceDisplay');
        const profitDisplay = document.getElementById('profitDisplay');
        const categoryLabel = document.getElementById('categoryLabel');
        const itemCountDisplay = document.getElementById('itemCountDisplay');
        const soldCountDisplay = document.getElementById('soldCountDisplay');
        const profitIconContainer = document.getElementById('profitIconContainer');
        const profitIcon = document.getElementById('profitIcon');
        
        // 如果元素不存在，则返回
        if (!purchasePriceDisplay || !soldPriceDisplay || !profitDisplay) return;
        
        // 确定要显示的统计数据
        const statsKey = category || 'all';
        const stats = categoryStats[statsKey] || categoryStats['all'];
        
        // 格式化价格显示
        const formatPrice = (price) => {
            return new Intl.NumberFormat('zh-CN', { 
                style: 'currency', 
                currency: 'CNY',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2 
            }).format(price).replace('CN¥', '¥');
        };
        
        // 更新价格显示
        purchasePriceDisplay.textContent = formatPrice(stats.purchasePrice);
        soldPriceDisplay.textContent = formatPrice(stats.soldPrice);
        
        // 计算利润
        const profit = stats.soldPrice - stats.purchasePrice;
        const profitText = (profit >= 0 ? '+' : '') + formatPrice(profit);
        profitDisplay.textContent = profitText;
        
        // 更新利润样式
        profitDisplay.className = 'mb-0 fw-bold ' + (profit >= 0 ? 'profit-positive' : 'profit-negative');
        profitIconContainer.className = 'stat-icon me-3 ' + 
            (profit >= 0 ? 'bg-success bg-opacity-10' : 'bg-danger bg-opacity-10');
        
        // 更新利润图标
        profitIcon.className = 'fas fa-chart-line ' + 
            (profit >= 0 ? 'text-success' : 'text-danger fa-rotate-180');
        
        // 更新类别标签
        if (category) {
            categoryLabel.textContent = category;
            categoryLabel.classList.remove('d-none');
        } else {
            categoryLabel.classList.add('d-none');
        }
        
        // 更新数量显示
        if (stats.count > 0) {
            itemCountDisplay.textContent = `(${stats.count}件)`;
        } else {
            itemCountDisplay.textContent = '';
        }
        
        if (stats.soldCount > 0) {
            soldCountDisplay.textContent = `(${stats.soldCount}件)`;
        } else {
            soldCountDisplay.textContent = '';
        }
    }
    
    /**
     * 更新筛选状态显示
     * @param {string} category 当前筛选的类别
     * @param {number} visibleCount 可见行数
     * @param {number} totalCount 总行数
     */
    updateFilterStatus(category, visibleCount, totalCount) {
        if (category) {
            // 有筛选条件时显示状态
            this.$filterStatusText.textContent = `当前筛选: ${category} (${visibleCount}/${totalCount})`;
            this.$filterStatus.classList.remove('d-none');
        } else {
            // 无筛选条件时隐藏状态
            this.$filterStatus.classList.add('d-none');
        }
    }
    
    /**
     * 重置筛选
     * @description 清除所有筛选条件
     */
    resetFilter() {
        // 重置下拉框
        this.$categoryFilter.value = '';
        
        // 清除localStorage中的筛选设置
        if (this.pageType) {
            localStorage.removeItem(`${this.pageType}_category_filter`);
        }
        
        // 重新应用筛选（实际上是显示所有行）
        this.applyFilter();
    }
}

// 页面加载完成后初始化筛选控制器
document.addEventListener('DOMContentLoaded', () => {
    new ListFilterController();
});
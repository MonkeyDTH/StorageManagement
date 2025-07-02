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
        
        // 获取统计显示元素
        this.$categoryLabel = document.getElementById('categoryLabel');
        this.$existingPriceDisplay = document.getElementById('existingPriceDisplay');
        this.$existingCountDisplay = document.getElementById('existingCountDisplay');
        this.$profitDisplay = document.getElementById('profitDisplay');
        this.$profitDetail = document.getElementById('profitDetail');
        this.$profitIcon = document.getElementById('profitIcon');
        this.$profitIconContainer = document.getElementById('profitIconContainer');
        this.$totalPriceDisplay = document.getElementById('totalPriceDisplay');
        this.$totalCountDisplay = document.getElementById('totalCountDisplay');
        
        // 获取当前页面类型(figures或clothing)
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
            // 如果没有保存的筛选设置，显示全部数据的统计
            this.updateStatsDisplay('');
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
            
            // 如果没有选择类别或类别匹配,则显示行
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
        
        // 更新统计信息显示
        this.updateStatsDisplay(categoryValue);
    }
    
    /**
     * 更新统计信息显示
     * @param {string} category 当前筛选的类别
     */
    updateStatsDisplay(category) {
        // 如果统计元素不存在，则返回
        if (!this.$existingPriceDisplay || typeof categoryStats === 'undefined') return;
        
        // 确定要显示的统计数据
        const statsKey = category || 'all';
        const stats = categoryStats[statsKey] || categoryStats['all'];
        
        // 格式化价格显示
        const formatPrice = (price) => {
            return '¥' + price.toLocaleString('zh-CN', { 
                minimumFractionDigits: 2,
                maximumFractionDigits: 2 
            });
        };
        
        // 更新类别标签
        if (category && this.$categoryLabel) {
            this.$categoryLabel.textContent = category;
            this.$categoryLabel.classList.remove('d-none');
        } else if (this.$categoryLabel) {
            this.$categoryLabel.classList.add('d-none');
        }
        
        // 更新持有物品统计
        if (this.$existingPriceDisplay && stats.purchasePriceExisting !== undefined) {
            this.$existingPriceDisplay.textContent = formatPrice(stats.purchasePriceExisting);
        }
        if (this.$existingCountDisplay && stats.existingCount !== undefined) {
            this.$existingCountDisplay.textContent = `(${stats.existingCount}件)`;
        }
        
        // 计算并更新盈亏统计
        if (this.$profitDisplay && stats.soldPrice !== undefined && stats.purchasePriceSold !== undefined) {
            const profit = stats.soldPrice - stats.purchasePriceSold;
            const profitText = (profit >= 0 ? '+' : '') + formatPrice(profit);
            this.$profitDisplay.textContent = profitText;
            
            // 更新盈亏样式和图标
            if (profit >= 0) {
                this.$profitDisplay.className = 'mb-0 fw-bold text-success';
                if (this.$profitIcon) {
                    this.$profitIcon.className = 'fas fa-chart-line text-success';
                }
                if (this.$profitIconContainer) {
                    this.$profitIconContainer.className = 'stat-icon me-3 bg-success bg-opacity-10';
                }
            } else {
                this.$profitDisplay.className = 'mb-0 fw-bold text-danger';
                if (this.$profitIcon) {
                    this.$profitIcon.className = 'fas fa-chart-line text-danger fa-rotate-180';
                }
                if (this.$profitIconContainer) {
                    this.$profitIconContainer.className = 'stat-icon me-3 bg-danger bg-opacity-10';
                }
            }
            
            // 更新盈亏详情
            if (this.$profitDetail) {
                this.$profitDetail.textContent = 
                    formatPrice(stats.soldPrice) + ' - ' + formatPrice(stats.purchasePriceSold);
            }
        }
        
        // 更新总投入统计
        if (this.$totalPriceDisplay && stats.purchasePrice !== undefined) {
            this.$totalPriceDisplay.textContent = formatPrice(stats.purchasePrice);
        }
        if (this.$totalCountDisplay && stats.count !== undefined) {
            this.$totalCountDisplay.textContent = `(${stats.count}件)`;
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
        
        // 重新应用筛选(实际上是显示所有行)
        this.applyFilter();
    }
}

// 页面加载完成后初始化筛选控制器
document.addEventListener('DOMContentLoaded', () => {
    new ListFilterController();
});
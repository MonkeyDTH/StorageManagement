// 统计视图相关功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化日历视图
    initializeCalendar();
    
    // 初始化分类统计
    initializeCategoryStats();
});

// 初始化日历视图
function initializeCalendar() {
    const calendarContainer = document.getElementById('calendarContainer');
    if (!calendarContainer) return;
    
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();
    
    // 更新日历标题
    const calendarTitle = document.getElementById('calendarTitle');
    if (calendarTitle) {
        calendarTitle.textContent = `${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}`;
    }
    
    // 获取当月第一天是星期几
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    
    // 获取当月天数
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    // 生成日历网格
    const calendarGrid = document.getElementById('calendarGrid');
    if (!calendarGrid) return;
    
    // 清空现有内容
    calendarGrid.innerHTML = '';
    
    // 添加星期标题
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    weekdays.forEach(day => {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        dayElement.textContent = day;
        calendarGrid.appendChild(dayElement);
    });
    
    // 添加空白格子（上个月的日期）
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-date empty';
        calendarGrid.appendChild(emptyDay);
    }
    
    // 添加当月日期
    for (let i = 1; i <= daysInMonth; i++) {
        const dateElement = document.createElement('div');
        dateElement.className = 'calendar-date';
        dateElement.textContent = i;
        
        // 模拟有物品的日期（这里应该从后端获取实际数据）
        if (Math.random() > 0.7) {
            dateElement.classList.add('has-item');
        }
        
        // 模拟有售出的日期
        if (Math.random() > 0.8) {
            dateElement.classList.add('has-sold');
        }
        
        // 如果同时有购买和售出，添加特殊标记
        if (dateElement.classList.contains('has-item') && dateElement.classList.contains('has-sold')) {
            dateElement.classList.add('has-both');
        }
        
        // 高亮当天
        if (i === currentDate.getDate()) {
            dateElement.style.border = '2px solid #FFFFFF';
        }
        
        calendarGrid.appendChild(dateElement);
    }
}

// 初始化分类统计
function initializeCategoryStats() {
    const categoryGrid = document.getElementById('categoryGrid');
    if (!categoryGrid) return;
    
    // 这里应该从后端获取实际数据
    // 以下是模拟数据
    const categories = [
        { name: '房间', icon: 'bi-house', count: 5 },
        { name: '标签', icon: 'bi-tag', count: 8 },
        { name: '来源', icon: 'bi-shop', count: 3 },
        { name: '状态', icon: 'bi-box', count: 4 },
        { name: '品牌', icon: 'bi-award', count: 6 },
        { name: '季节', icon: 'bi-sun', count: 2 },
        { name: '颜色', icon: 'bi-palette', count: 7 },
        { name: '材质', icon: 'bi-layers', count: 3 },
        { name: '作者', icon: 'bi-person', count: 4 },
        { name: '译者', icon: 'bi-translate', count: 2 },
        { name: '出版社', icon: 'bi-book', count: 5 },
        { name: '付款', icon: 'bi-credit-card', count: 3 }
    ];
    
    // 清空现有内容
    categoryGrid.innerHTML = '';
    
    // 添加分类项
    categories.forEach(category => {
        const categoryElement = document.createElement('div');
        categoryElement.className = 'category-item';
        categoryElement.innerHTML = `
            <i class="bi ${category.icon}"></i>
            <div class="name">${category.name}</div>
            <div class="count">${category.count}</div>
        `;
        categoryGrid.appendChild(categoryElement);
    });
}

// 切换月份
function changeMonth(delta) {
    // 这里应该实现月份切换逻辑
    // 由于需要后端数据支持，这里只是一个示例
    console.log(`Change month by ${delta}`);
    // 重新初始化日历
    initializeCalendar();
}
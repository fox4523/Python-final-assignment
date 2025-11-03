// 主JavaScript文件
let currentPage = 1;
let currentData = [];
let isSearchMode = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    checkDataStatus();
    loadOverviewData();

    // 绑定事件
    document.getElementById('start-scrape-btn').addEventListener('click', startScraping);
    document.getElementById('download-csv-btn').addEventListener('click', downloadCSV);
    document.getElementById('search-btn').addEventListener('click', searchMovies);
    document.getElementById('clear-search-btn').addEventListener('click', clearSearch);

    // 回车搜索
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchMovies();
        }
    });
});

// 标签页切换
function initTabs() {
    const tabButtons = document.querySelectorAll('.nav-tab');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');

            // 移除所有active类
            document.querySelectorAll('.nav-tab').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // 添加active类
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            // 根据标签页加载数据
            if (tabName === 'overview') {
                loadOverviewData();
            } else if (tabName === 'movies') {
                loadMovies(1);
            } else if (tabName === 'analysis') {
                loadAnalysisData();
            }
        });
    });
}

// 检查数据状态
async function checkDataStatus() {
    try {
        const response = await fetch('/api/data-status');
        const result = await response.json();

        if (result.has_data) {
            document.getElementById('scraper-status').innerHTML =
                `✅ 数据已就绪，共 ${result.movie_count} 部电影`;
            document.getElementById('scraper-status').className = 'status-box';
        } else {
            document.getElementById('scraper-status').innerHTML =
                '⚠️ 暂无数据，请先点击"开始爬取"按钮获取数据';
            document.getElementById('scraper-status').className = 'status-box loading';
        }
    } catch (error) {
        console.error('检查数据状态失败:', error);
    }
}

// 加载概览数据
async function loadOverviewData() {
    try {
        // 加载统计数据
        const statsResponse = await fetch('/api/statistics');
        const statsResult = await statsResponse.json();

        if (statsResult.success) {
            const stats = statsResult.data.basic;
            document.getElementById('total-movies').textContent = stats.total_movies || 0;
            document.getElementById('avg-rating').textContent = stats.avg_rating || 0;
            document.getElementById('avg-people').textContent = stats.avg_rating_people ?
                Math.round(stats.avg_rating_people).toLocaleString() : 0;
            document.getElementById('max-rating').textContent = stats.max_rating || 0;
        }

        // 加载Top 10电影
        const topResponse = await fetch('/api/top-movies?top=10');
        const topResult = await topResponse.json();

        if (topResult.success) {
            displayTopMovies(topResult.data);
        }
    } catch (error) {
        console.error('加载概览数据失败:', error);
    }
}

// 显示Top电影
function displayTopMovies(movies) {
    const container = document.getElementById('top-movies-list');

    if (!movies || movies.length === 0) {
        container.innerHTML = '<p>暂无数据，请先爬取电影信息</p>';
        return;
    }

    container.innerHTML = movies.map(movie => `
        <div class="movie-card">
            <span class="movie-rank">Top ${movie.rank}</span>
            <div class="movie-title">${movie.title}</div>
            <div class="movie-rating">⭐ ${movie.rating}分</div>
            <div class="movie-info">
                <p><strong>导演：</strong>${movie.director || '未知'}</p>
                <p><strong>年份：</strong>${movie.year || '未知'}</p>
                <p><strong>类型：</strong>${movie.genre || '未知'}</p>
                <p><strong>评价人数：</strong>${movie.rating_people}人</p>
                ${movie.quote ? `<p style="color:#667eea;font-style:italic;">"${movie.quote}"</p>` : ''}
            </div>
        </div>
    `).join('');
}

// 加载电影列表
async function loadMovies(page) {
    try {
        const response = await fetch(`/api/movies?page=${page}&per_page=25`);
        const result = await response.json();

        if (result.success) {
            currentData = result.data;
            currentPage = page;
            displayMovies(result.data);
            displayPagination(result.page, result.total_pages);
        }
    } catch (error) {
        console.error('加载电影列表失败:', error);
    }
}

// 显示电影列表
function displayMovies(movies) {
    const container = document.getElementById('movies-list');

    if (!movies || movies.length === 0) {
        container.innerHTML = '<p style="text-align:center;padding:40px;">暂无数据</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>电影名称</th>
                    <th>导演</th>
                    <th>年份</th>
                    <th>国家</th>
                    <th>类型</th>
                    <th>评分</th>
                    <th>评价人数</th>
                </tr>
            </thead>
            <tbody>
                ${movies.map(movie => `
                    <tr>
                        <td><strong>${movie.rank}</strong></td>
                        <td><strong>${movie.title}</strong></td>
                        <td>${movie.director || '-'}</td>
                        <td>${movie.year || '-'}</td>
                        <td>${movie.country || '-'}</td>
                        <td>${movie.genre || '-'}</td>
                        <td><strong style="color:#f39c12;">${movie.rating}</strong></td>
                        <td>${movie.rating_people}人</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// 显示分页
function displayPagination(currentPage, totalPages) {
    const container = document.getElementById('pagination');

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // 上一页
    html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} 
             onclick="loadMovies(${currentPage - 1})">上一页</button>`;

    // 页码
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" 
                     onclick="loadMovies(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<span>...</span>';
        }
    }

    // 下一页
    html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} 
             onclick="loadMovies(${currentPage + 1})">下一页</button>`;

    container.innerHTML = html;
}

// 搜索电影
async function searchMovies() {
    const keyword = document.getElementById('search-input').value.trim();

    if (!keyword) {
        alert('请输入搜索关键词');
        return;
    }

    try {
        const response = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`);
        const result = await response.json();

        if (result.success) {
            isSearchMode = true;
            displayMovies(result.data);
            document.getElementById('pagination').innerHTML =
                `<p style="text-align:center;">找到 ${result.count} 个结果</p>`;
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('搜索失败:', error);
        alert('搜索失败，请稍后重试');
    }
}

// 清除搜索
function clearSearch() {
    document.getElementById('search-input').value = '';
    isSearchMode = false;
    loadMovies(1);
}

// 加载分析数据
async function loadAnalysisData() {
    try {
        const response = await fetch('/api/statistics');
        const result = await response.json();

        if (result.success) {
            const data = result.data;

            // 评分分布图
            createChart('ratingChart', 'bar',
                Object.keys(data.rating_distribution),
                Object.values(data.rating_distribution),
                '评分分布'
            );

            // 类型分布图
            createChart('genreChart', 'doughnut',
                Object.keys(data.top_genres),
                Object.values(data.top_genres),
                '电影类型'
            );

            // 产地分布图
            createChart('countryChart', 'pie',
                Object.keys(data.top_countries),
                Object.values(data.top_countries),
                '产地分布'
            );

            // 年代分布图
            createChart('yearChart', 'line',
                Object.keys(data.year_distribution),
                Object.values(data.year_distribution),
                '年代分布'
            );

            // 导演分布图
            createChart('directorChart', 'bar',
                Object.keys(data.top_directors),
                Object.values(data.top_directors),
                '作品数量',
                true
            );
        }
    } catch (error) {
        console.error('加载分析数据失败:', error);
    }
}

// 创建图表
function createChart(canvasId, type, labels, data, label, horizontal = false) {
    const ctx = document.getElementById(canvasId);

    // 销毁已存在的图表
    if (window[canvasId + 'Instance']) {
        window[canvasId + 'Instance'].destroy();
    }

    const config = {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: type === 'line' ? 'rgba(102, 126, 234, 0.2)' : [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)',
                    'rgba(83, 102, 255, 0.8)'
                ],
                borderColor: type === 'line' ? 'rgba(102, 126, 234, 1)' : 'rgba(255, 255, 255, 1)',
                borderWidth: type === 'line' ? 2 : 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: horizontal ? 'y' : 'x',
            plugins: {
                legend: {
                    display: type === 'pie' || type === 'doughnut',
                    position: 'bottom'
                }
            },
            scales: type === 'pie' || type === 'doughnut' ? {} : {
                y: {
                    beginAtZero: true
                }
            }
        }
    };

    window[canvasId + 'Instance'] = new Chart(ctx, config);
}

// 开始爬取
async function startScraping() {
    const button = document.getElementById('start-scrape-btn');
    const statusBox = document.getElementById('scraper-status');

    button.disabled = true;
    button.innerHTML = '<span class="loading"></span> 爬取中...';
    statusBox.className = 'status-box loading';
    statusBox.innerHTML = '⏳ 正在爬取数据，请稍候... (预计2-5分钟)';

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            statusBox.className = 'status-box';
            statusBox.innerHTML = `✅ ${result.message}`;

            // 刷新数据
            setTimeout(() => {
                loadOverviewData();
                checkDataStatus();
            }, 1000);
        } else {
            statusBox.className = 'status-box error';
            statusBox.innerHTML = `❌ ${result.message}`;
        }
    } catch (error) {
        statusBox.className = 'status-box error';
        statusBox.innerHTML = `❌ 爬取失败: ${error.message}`;
    } finally {
        button.disabled = false;
        button.innerHTML = '▶ 开始爬取';
    }
}

// 下载CSV
function downloadCSV() {
    window.location.href = '/api/download-csv';
}


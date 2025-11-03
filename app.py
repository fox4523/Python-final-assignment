"""
Flask Web应用主文件
"""
from flask import Flask, render_template, jsonify, request, send_file
from scrape import DoubanMovieScraper
from analysis import MovieDataAnalyzer
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 全局变量
scraper = DoubanMovieScraper()
analyzer = MovieDataAnalyzer()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape_data():
    """启动爬虫"""
    try:
        movies = scraper.scrape()

        if movies:
            # 保存到CSV
            scraper.save_to_csv()
            # 重新加载分析器数据
            analyzer.load_data()

            return jsonify({
                'success': True,
                'message': f'成功爬取 {len(movies)} 部电影数据',
                'count': len(movies)
            })
        else:
            return jsonify({
                'success': False,
                'message': '爬取失败，请稍后重试'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'爬取出错: {str(e)}'
        })


@app.route('/api/movies')
def get_movies():
    """获取电影列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    movies = analyzer.movies
    total = len(movies)

    start = (page - 1) * per_page
    end = start + per_page

    return jsonify({
        'success': True,
        'data': movies[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/api/search')
def search_movies():
    """搜索电影"""
    keyword = request.args.get('keyword', '')

    if not keyword:
        return jsonify({
            'success': False,
            'message': '请输入搜索关键词'
        })

    results = analyzer.search_movies(keyword)

    return jsonify({
        'success': True,
        'data': results,
        'count': len(results)
    })


@app.route('/api/statistics')
def get_statistics():
    """获取统计数据"""
    try:
        stats = analyzer.get_statistics()
        rating_dist = analyzer.get_rating_distribution()
        year_dist = analyzer.get_year_distribution()
        top_genres = analyzer.get_top_genres()
        top_countries = analyzer.get_top_countries()
        top_directors = analyzer.get_top_directors()

        return jsonify({
            'success': True,
            'data': {
                'basic': stats,
                'rating_distribution': rating_dist,
                'year_distribution': year_dist,
                'top_genres': top_genres,
                'top_countries': top_countries,
                'top_directors': top_directors
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据出错: {str(e)}'
        })


@app.route('/api/top-movies')
def get_top_movies():
    """获取Top电影"""
    top_n = request.args.get('top', 10, type=int)
    top_movies = analyzer.get_top_movies(top_n)

    return jsonify({
        'success': True,
        'data': top_movies
    })


@app.route('/api/download-csv')
def download_csv():
    """下载CSV文件"""
    csv_file = 'data/douban_top250.csv'

    if not os.path.exists(csv_file):
        return jsonify({
            'success': False,
            'message': 'CSV文件不存在，请先爬取数据'
        }), 404

    return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'douban_top250_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.route('/api/data-status')
def data_status():
    """检查数据状态"""
    csv_exists = os.path.exists('data/douban_top250.csv')
    movie_count = len(analyzer.movies)

    return jsonify({
        'success': True,
        'has_data': csv_exists and movie_count > 0,
        'movie_count': movie_count
    })


if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    # 启动应用
    print("="*50)
    print("豆瓣电影Top250 数据分析系统")
    print("="*50)
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务器")
    print("="*50)

    app.run(debug=True, host='0.0.0.0', port=5000)


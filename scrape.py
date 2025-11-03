"""
豆瓣电影Top250爬虫模块
"""
import random
import time
import requests
from bs4 import BeautifulSoup
import csv
import os


class DoubanMovieScraper:
    """豆瓣电影爬虫类"""

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.movies = []

    def scrape(self, callback=None):
        """爬取豆瓣电影Top250数据"""
        self.movies = []

        for start_num in range(0, 250, 25):
            time.sleep(random.uniform(1, 3))  # 随机延迟，避免反爬

            headers = {'User-Agent': random.choice(self.user_agents)}

            try:
                response = requests.get(
                    f'https://movie.douban.com/top250?start={start_num}',
                    headers=headers,
                    timeout=10
                )

                if response.ok:
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')

                    # 查找所有电影项
                    movie_items = soup.find_all('div', class_='item')

                    for item in movie_items:
                        movie_data = self._parse_movie_item(item)
                        if movie_data:
                            self.movies.append(movie_data)

                    if callback:
                        callback(f"已爬取 {len(self.movies)} 部电影...")
                else:
                    print(f"Error: {response.status_code}")

            except Exception as e:
                print(f"爬取出错: {str(e)}")

        return self.movies

    def _parse_movie_item(self, item):
        """解析单个电影数据"""
        try:
            # 排名
            rank_elem = item.find('em')
            rank = rank_elem.string if rank_elem else ''

            # 电影标题
            title_elem = item.find('span', class_='title')
            title = title_elem.string if title_elem else ''

            # 评分
            rating_elem = item.find('span', class_='rating_num')
            rating = rating_elem.string if rating_elem else ''

            # 评价人数 - 修复：在bd > div > span中查找
            rating_people = ''
            bd_div = item.find('div', class_='bd')
            if bd_div:
                rating_div = bd_div.find('div')
                if rating_div:
                    spans = rating_div.find_all('span')
                    for span in spans:
                        text = span.get_text()
                        if '人评价' in text:
                            rating_people = text.replace('人评价', '').strip()
                            break

            # 简介（导演、演员、年份、类型）- 修复：不指定class
            director = ''
            actors = ''
            year = ''
            country = ''
            genre = ''

            if bd_div:
                p_tag = bd_div.find('p')
                if p_tag:
                    # 获取p标签的文本，分行处理
                    p_text = p_tag.get_text(separator='\n', strip=True)
                    lines = [line.strip() for line in p_text.split('\n') if line.strip()]

                    # 第一行：导演和演员
                    if len(lines) > 0:
                        director_actor = lines[0]
                        # 处理导演
                        if '导演:' in director_actor:
                            parts = director_actor.split('主演:')
                            director = parts[0].replace('导演:', '').strip()
                            actors = parts[1].strip() if len(parts) > 1 else ''
                        else:
                            # 没有"导演:"标签时，尝试其他解析
                            director = director_actor

                    # 第二行：年份/国家/类型
                    if len(lines) > 1:
                        details = lines[1].split('/')
                        year = details[0].strip() if len(details) > 0 else ''
                        country = details[1].strip() if len(details) > 1 else ''
                        # 类型可能有多个，全部保留
                        if len(details) > 2:
                            genre = ' '.join([d.strip() for d in details[2:]])

            # 引言
            quote_element = item.find('span', class_='inq')
            quote = quote_element.string if quote_element else ''

            return {
                'rank': rank,
                'title': title,
                'director': director,
                'actors': actors,
                'year': year,
                'country': country,
                'genre': genre,
                'rating': rating,
                'rating_people': rating_people,
                'quote': quote
            }
        except Exception as e:
            print(f"解析电影数据出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def save_to_csv(self, filename='douban_top250.csv'):
        """保存数据到CSV文件"""
        if not self.movies:
            return False

        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = ['rank', 'title', 'director', 'actors', 'year',
                            'country', 'genre', 'rating', 'rating_people', 'quote']
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(self.movies)

            return True
        except Exception as e:
            print(f"保存CSV出错: {str(e)}")
            return False

    def get_movies(self):
        """获取电影数据"""
        return self.movies


if __name__ == '__main__':
    # 测试爬虫
    scraper = DoubanMovieScraper()
    print("开始爬取豆瓣电影Top250...")
    movies = scraper.scrape(callback=print)
    print(f"\n共爬取 {len(movies)} 部电影")

    # 保存到CSV
    if scraper.save_to_csv():
        print("数据已保存到 data/douban_top250.csv")

    # 显示前10部电影
    print("\n前10部电影:")
    for i, movie in enumerate(movies[:10], 1):
        print(f"{i}. {movie['title']}: {movie['rating']}分")

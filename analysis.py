"""
数据分析模块
"""
import csv
import os
from collections import Counter


class MovieDataAnalyzer:
    """电影数据分析类"""

    def __init__(self, csv_file='data/douban_top250.csv'):
        self.csv_file = csv_file
        self.movies = []
        self.load_data()

    def load_data(self):
        """从CSV文件加载数据"""
        if not os.path.exists(self.csv_file):
            return False

        try:
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.movies = list(reader)
            return True
        except Exception as e:
            print(f"加载数据出错: {str(e)}")
            return False

    def get_rating_distribution(self):
        """获取评分分布"""
        if not self.movies:
            return {}

        rating_ranges = {
            '9.0-10.0': 0,
            '8.5-8.9': 0,
            '8.0-8.4': 0,
            '7.5-7.9': 0,
            '7.0-7.4': 0,
            '7.0以下': 0
        }

        for movie in self.movies:
            try:
                rating = float(movie['rating'])
                if rating >= 9.0:
                    rating_ranges['9.0-10.0'] += 1
                elif rating >= 8.5:
                    rating_ranges['8.5-8.9'] += 1
                elif rating >= 8.0:
                    rating_ranges['8.0-8.4'] += 1
                elif rating >= 7.5:
                    rating_ranges['7.5-7.9'] += 1
                elif rating >= 7.0:
                    rating_ranges['7.0-7.4'] += 1
                else:
                    rating_ranges['7.0以下'] += 1
            except:
                continue

        return rating_ranges

    def get_top_genres(self, top_n=10):
        """获取最受欢迎的电影类型"""
        genres = []
        for movie in self.movies:
            genre = movie.get('genre', '')
            if genre:
                # 处理多个类型（用空格分隔）
                genre_list = genre.split()
                genres.extend(genre_list)

        genre_counter = Counter(genres)
        return dict(genre_counter.most_common(top_n))

    def get_top_countries(self, top_n=10):
        """获取电影产地分布"""
        countries = []
        for movie in self.movies:
            country = movie.get('country', '')
            if country:
                # 处理多个国家
                country_list = [c.strip() for c in country.split()]
                countries.extend(country_list)

        country_counter = Counter(countries)
        return dict(country_counter.most_common(top_n))

    def get_year_distribution(self):
        """获取年份分布"""
        years = []
        for movie in self.movies:
            year = movie.get('year', '')
            if year and year.isdigit():
                years.append(year)

        # 按年代分组
        year_ranges = {
            '1920-1949': 0,
            '1950-1959': 0,
            '1960-1969': 0,
            '1970-1979': 0,
            '1980-1989': 0,
            '1990-1999': 0,
            '2000-2009': 0,
            '2010-2019': 0,
            '2020-至今': 0
        }

        for year in years:
            y = int(year)
            if y < 1950:
                year_ranges['1920-1949'] += 1
            elif y < 1960:
                year_ranges['1950-1959'] += 1
            elif y < 1970:
                year_ranges['1960-1969'] += 1
            elif y < 1980:
                year_ranges['1970-1979'] += 1
            elif y < 1990:
                year_ranges['1980-1989'] += 1
            elif y < 2000:
                year_ranges['1990-1999'] += 1
            elif y < 2010:
                year_ranges['2000-2009'] += 1
            elif y < 2020:
                year_ranges['2010-2019'] += 1
            else:
                year_ranges['2020-至今'] += 1

        return year_ranges

    def get_top_directors(self, top_n=10):
        """获取最受欢迎的导演"""
        directors = []
        for movie in self.movies:
            director = movie.get('director', '')
            if director:
                # 处理多个导演
                director_list = [d.strip() for d in director.split('/')]
                directors.extend(director_list)

        director_counter = Counter(directors)
        return dict(director_counter.most_common(top_n))

    def get_statistics(self):
        """获取基本统计信息"""
        if not self.movies:
            return {}

        ratings = []
        rating_people = []

        for movie in self.movies:
            try:
                ratings.append(float(movie['rating']))
            except:
                pass

            try:
                people = movie['rating_people'].replace(',', '')
                rating_people.append(int(people))
            except:
                pass

        return {
            'total_movies': len(self.movies),
            'avg_rating': round(sum(ratings) / len(ratings), 2) if ratings else 0,
            'max_rating': max(ratings) if ratings else 0,
            'min_rating': min(ratings) if ratings else 0,
            'avg_rating_people': round(sum(rating_people) / len(rating_people), 0) if rating_people else 0
        }

    def get_top_movies(self, top_n=10):
        """获取评分最高的电影"""
        sorted_movies = sorted(self.movies, key=lambda x: float(x.get('rating', 0)), reverse=True)
        return sorted_movies[:top_n]

    def search_movies(self, keyword):
        """搜索电影"""
        results = []
        keyword_lower = keyword.lower()

        for movie in self.movies:
            if (keyword_lower in movie.get('title', '').lower() or
                keyword_lower in movie.get('director', '').lower() or
                keyword_lower in movie.get('actors', '').lower() or
                keyword_lower in movie.get('genre', '').lower()):
                results.append(movie)

        return results


if __name__ == '__main__':
    analyzer = MovieDataAnalyzer()

    print("=== 基本统计 ===")
    stats = analyzer.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n=== 评分分布 ===")
    rating_dist = analyzer.get_rating_distribution()
    for range_name, count in rating_dist.items():
        print(f"{range_name}: {count}")

    print("\n=== Top 10 电影类型 ===")
    top_genres = analyzer.get_top_genres()
    for genre, count in top_genres.items():
        print(f"{genre}: {count}")


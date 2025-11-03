"""
测试豆瓣网页结构
"""
import requests
from bs4 import BeautifulSoup
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

headers = {'User-Agent': random.choice(user_agents)}

try:
    response = requests.get('https://movie.douban.com/top250?start=0', headers=headers, timeout=10)

    print(f"状态码: {response.status_code}")
    print(f"返回内容长度: {len(response.text)}")
    print("\n前2000个字符:")
    print(response.text[:2000])

    # 保存HTML到文件以便检查
    with open('debug_html.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\nHTML已保存到 debug_html.html")

    # 尝试不同的选择器
    soup = BeautifulSoup(response.text, 'html.parser')

    print("\n\n=== 测试不同的选择器 ===")

    # 测试1: 原来的选择器
    items1 = soup.find_all('div', class_='item')
    print(f"1. div.item 找到: {len(items1)} 个")

    # 测试2: 电影列表项
    items2 = soup.find_all('li')
    print(f"2. li 找到: {len(items2)} 个")

    # 测试3: 特定class
    items3 = soup.find_all('div', class_='info')
    print(f"3. div.info 找到: {len(items3)} 个")

    # 测试4: ol列表
    ol = soup.find('ol', class_='grid_view')
    if ol:
        print(f"4. 找到 ol.grid_view")
        lis = ol.find_all('li')
        print(f"   其中有 {len(lis)} 个 li")

        if lis:
            print("\n=== 第一个电影项的结构 ===")
            first = lis[0]
            print(first.prettify()[:1000])

except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()


"""
项目快速启动脚本
"""
import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    print("正在检查依赖...")
    try:
        import flask
        import requests
        import bs4
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("\n正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def create_directories():
    """创建必要的目录"""
    directories = ['data', 'templates', 'static/css', 'static/js']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ 目录结构已就绪")

def main():
    """主函数"""
    print("="*60)
    print("豆瓣电影Top250 数据分析系统 - 启动脚本")
    print("="*60)

    # 检查依赖
    if not check_dependencies():
        print("依赖安装失败，请手动执行: pip install -r requirements.txt")
        return

    # 创建目录
    create_directories()

    print("\n✅ 准备完成！")
    print("\n启动Flask应用...")
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务器")
    print("="*60)
    print()

    # 启动Flask应用
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()


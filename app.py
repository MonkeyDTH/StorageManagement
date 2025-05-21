'''
Author: Leili
Date: 2025-05-18 20:41:27
LastEditors: Leili
LastEditTime: 2025-05-21 12:53:49
FilePath: /StorageManagement/app.py
Description: 
'''
"""
家庭物品管理应用后端服务
功能：读取CSV数据，提供物品展示接口
"""
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

def load_figures_data():
    """
    加载手办数据
    :return: 手办数据列表（字典形式）
    """
    # 读取CSV文件并转换为字典列表
    return pd.read_csv('data/figures.csv').to_dict('records')

def load_clothing_data():
    """
    加载衣服数据
    :return: 衣服数据列表（字典形式）
    """
    return pd.read_csv('data/clothing.csv').to_dict('records')

@app.route('/')
def home():
    """
    主页路由：展示物品统计概况
    """
    figures = load_figures_data()
    clothing = load_clothing_data()
    return render_template(
        'index.html',
        total=len(figures) + len(clothing),
        figures_count=len(figures),
        clothing_count=len(clothing)
    )

@app.route('/figures')
def show_figures():
    """
    手办列表路由：展示所有手办数据
    """
    return render_template('figures.html', figures=load_figures_data())

@app.route('/clothing')
def show_clothing():
    """
    衣服列表路由：展示所有衣服数据
    """
    return render_template('clothing.html', clothing=load_clothing_data())

@app.route('/figures/<int:item_id>')
def figures_detail(item_id):
    """
    手办详情路由：展示单个手办的详细信息
    :param item_id: 手办ID
    :return: 详情页模板
    """
    figures_data = load_figures_data()
    item = next((item for item in figures_data if item['id'] == item_id), None)
    if item is None:
        abort(404)
    return render_template('figures_detail.html', item=item)

@app.route('/clothing/<int:item_id>')
def clothing_detail(item_id):
    """
    衣服详情路由：展示单个衣服的详细信息
    :param item_id: 衣服ID
    :return: 详情页模板
    """
    clothing_data = load_clothing_data()
    item = next((item for item in clothing_data if item['id'] == item_id), None)
    if item is None:
        abort(404)
    return render_template('clothing_detail.html', item=item)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7334)  # 开发模式启动（生产环境需调整）
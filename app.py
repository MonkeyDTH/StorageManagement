'''
Author: Leili
Date: 2025-05-18 20:41:27
LastEditors: Leili
LastEditTime: 2025-05-22 09:56:52
FilePath: /StorageManagement/app.py
Description: 
'''
"""
家庭物品管理应用后端服务
功能：读取CSV数据，提供物品展示接口
"""
from flask import Flask, render_template, abort
import pandas as pd
import os
from utils.image_processor import compress_and_convert_to_webp, get_webp_path

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

def check_and_convert_images():
    """检查并转换static/images目录下的图片为WebP格式"""
    image_dir = os.path.join(app.static_folder, 'images')
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            original_path = os.path.join(image_dir, filename)
            webp_path = get_webp_path(original_path)
            if not os.path.exists(webp_path):
                compress_and_convert_to_webp(original_path, webp_path)

@app.route('/')
def home():
    """
    主页路由：展示物品统计概况
    """
    # 自动检查并转换图片
    check_and_convert_images()
    
    # 加载数据并渲染模板
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


""" ========== 详情页面 ============ """
def get_item_detail(item_type, item_id):
    """
    通用详情路由处理函数
    :param item_type: 物品类型 ('figures' 或 'clothing')
    :param item_id: 物品ID
    :return: 详情页模板
    """
    data_loader = {
        'figures': load_figures_data,
        'clothing': load_clothing_data
    }
    template_map = {
        'figures': 'figures_detail.html',
        'clothing': 'clothing_detail.html'
    }
    
    item_data = data_loader[item_type]()
    item = next((item for item in item_data if item['id'] == item_id), None)
    if item is None:
        abort(404)
    return render_template(template_map[item_type], item=item)

@app.route('/figures/<int:item_id>')
def figures_detail(item_id):
    """手办详情路由"""
    return get_item_detail('figures', item_id)

@app.route('/clothing/<int:item_id>')
def clothing_detail(item_id):
    """衣服详情路由"""
    return get_item_detail('clothing', item_id)


""" ========== 主程序入口 ============ """
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7334)  # 开发模式启动（生产环境需调整）
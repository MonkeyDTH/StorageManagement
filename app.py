'''
Author: Leili
Date: 2025-05-18 20:41:27
LastEditors: Leili
LastEditTime: 2025-06-17 18:56:00
FilePath: /StorageManagement/app.py
Description: 
'''
"""
家庭物品管理应用后端服务
功能：读取CSV数据，提供物品展示接口
"""
from flask import Flask, render_template, abort, request, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from utils.image_processor import compress_and_convert_to_webp, get_webp_path
from utils.item_manager import ItemCategory

app = Flask(__name__)

# 创建物品类别实例
figures_category = ItemCategory('figures', app)
clothing_category = ItemCategory('clothing', app)
goods_category = ItemCategory('goods', app)

def load_figures_data():
    """
    加载手办数据
    
    返回:
        list: 手办数据字典列表，按购买日期倒序排列，无购买日期的按名称排列
    
    异常:
        FileNotFoundError: 当数据文件不存在时抛出
        pd.errors.EmptyDataError: 当数据文件为空时抛出
    """
    return figures_category.load_data()

def load_clothing_data():
    """
    加载衣服数据
    
    返回:
        list: 衣服数据列表（字典形式），按购买日期倒序排列，无购买日期的按名称排列
    
    异常:
        FileNotFoundError: 当数据文件不存在时抛出
        pd.errors.EmptyDataError: 当数据文件为空时抛出
    """
    return clothing_category.load_data()

def load_goods_data():
    """
    加载好物数据
    
    返回:
        list: 好物数据列表（字典形式），按购买日期倒序排列，无购买日期的按名称排列
    
    异常:
        FileNotFoundError: 当数据文件不存在时抛出
        pd.errors.EmptyDataError: 当数据文件为空时抛出
    """
    return goods_category.load_data()

def check_and_convert_images():
    """检查并转换图片为WebP格式"""
    for item_type in ['figures', 'clothing', 'goods']:
        image_dir = os.path.join(app.static_folder, 'images', item_type)
        if not os.path.exists(image_dir):
            os.makedirs(image_dir, exist_ok=True)
            continue
            
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(image_dir, filename)
                # 检查是否已经有对应的WebP文件
                webp_path = get_webp_path(image_path, item_type)
                if not os.path.exists(webp_path):
                    try:
                        compress_and_convert_to_webp(image_path, item_type)
                        print(f"转换图片: {filename} -> {os.path.basename(webp_path)}")
                    except Exception as e:
                        print(f"转换图片失败 {filename}: {str(e)}")

@app.route('/')
def home():
    """
    主页路由：展示物品统计概况
    
    返回:
        渲染后的主页模板，包含物品统计数据
    """
    # 自动检查并转换图片
    check_and_convert_images()
    
    # 加载数据
    figures = load_figures_data()
    clothing = load_clothing_data()
    goods = load_goods_data()

    return render_template(
        'index.html',
        total=len(figures) + len(clothing) + len(goods),
        figures_count=len(figures),
        clothing_count=len(clothing),
        goods_count=len(goods)
    )

@app.route('/figures')
def show_figures():
    """手办列表路由：展示所有手办数据"""
    figures_data = figures_category.load_data()
    categories = figures_category.get_categories()
    return render_template('figures/list.html', figures=figures_data, categories=categories)

@app.route('/clothing')
def show_clothing():
    """衣服列表路由：展示所有衣服数据"""
    clothing_data = clothing_category.load_data()
    categories = clothing_category.get_categories()
    return render_template('clothing/list.html', clothing=clothing_data, categories=categories)

@app.route('/goods')
def show_goods():
    """好物列表路由：展示所有好物数据"""
    goods_data = goods_category.load_data()
    categories = goods_category.get_categories()
    return render_template('goods/list.html', goods=goods_data, categories=categories)

@app.route('/figures/<int:item_id>')
def figures_detail(item_id):
    """手办详情路由"""
    return get_item_detail('figures', item_id)

@app.route('/clothing/<int:item_id>')
def clothing_detail(item_id):
    """衣服详情路由"""
    return get_item_detail('clothing', item_id)

@app.route('/goods/<int:item_id>')
def goods_detail(item_id):
    """好物详情路由"""
    return get_item_detail('goods', item_id)

@app.route('/figures/new')
def figures_new():
    """新建手办页面路由"""
    return render_template('figures/new.html')

@app.route('/clothing/new')
def clothing_new():
    """新建衣服页面路由"""
    return render_template('clothing/new.html')

@app.route('/goods/new')
def good_new():
    """新建好物页面路由"""
    return render_template('goods/new.html')

def get_item_detail(item_type, item_id):
    """通用详情路由处理函数"""
    category_map = {
        'figures': figures_category,
        'clothing': clothing_category,
        'goods': goods_category
    }
    template_map = {
        'figures': 'figures/detail.html',
        'clothing': 'clothing/detail.html',
        'goods': 'goods/detail.html'
    }
    
    category = category_map[item_type]
    item = category.get_item_by_id(item_id)
    if item is None:
        abort(404)
    return render_template(template_map[item_type], item=item)


""" ========= 更新属性接口 ========= """
@app.route('/update_properties', methods=['POST'])
def update_properties():
    """
    更新属性接口
    @description: 处理前端提交的属性更新请求
    @param: 表单数据，包含属性数据和可能的图片文件
    @return: 操作结果
    """
    try:
        # 获取表单数据
        item_type = request.form.get('item_type')
        item_id = request.form.get('item_id')
        
        # 根据不同类型选择不同的类别管理器
        category_map = {
            'figures': figures_category,
            'clothing': clothing_category,
            'goods': goods_category
        }
        
        if item_type not in category_map:
            raise ValueError('无效的物品类型')
            
        category = category_map[item_type]
        
        # 获取图片文件
        image_file = request.files.get('image') if 'image' in request.files else None
        
        # 更新物品属性
        success, message = category.update_item(item_id, request.form, image_file)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        print(f"更新失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 400

@app.route('/create_item', methods=['POST'])
def create_item():
    """
    创建新物品接口
    @description: 处理前端提交的新物品创建请求
    @param: 表单数据，包含物品数据和可能的图片文件
    @return: 操作结果
    """
    try:
        # 获取表单数据
        item_type = request.form.get('item_type')
        
        # 根据不同类型选择不同的类别管理器
        category_map = {
            'figures': figures_category,
            'clothing': clothing_category,
            'goods': goods_category
        }
        
        if item_type not in category_map:
            raise ValueError('无效的物品类型')
            
        category = category_map[item_type]
        
        # 获取图片文件
        image_file = request.files.get('image') if 'image' in request.files else None
        
        # 创建新物品
        success, message, new_id = category.create_item(request.form, image_file)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'item_id': new_id
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        print(f"创建失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        }), 400


""" ========== 主程序入口 ============ """
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7334)  # 开发模式启动（生产环境需调整）

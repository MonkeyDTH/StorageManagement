'''
Author: Leili
Date: 2025-05-18 20:41:27
LastEditors: Leili
LastEditTime: 2025-05-26 14:15:00
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
from werkzeug.utils import secure_filename  # 添加这一行
from utils.image_processor import compress_and_convert_to_webp, get_webp_path

app = Flask(__name__)

def load_figures_data():
    """
    加载手办数据
    
    返回:
        list: 手办数据字典列表，按购买日期倒序排列，无购买日期的按名称排列
    
    异常:
        FileNotFoundError: 当数据文件不存在时抛出
        pd.errors.EmptyDataError: 当数据文件为空时抛出
    """
    try:
        df = pd.read_csv('data/figures.csv')
        # 将空的购买日期替换为 NaT，并只保留日期部分
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce').dt.date
        # 先按购买日期倒序排列，对于没有购买日期的按名称排列
        df = df.sort_values(
            by=['purchase_date', 'name'],
            ascending=[False, True],
            na_position='last'
        )
        return df.to_dict('records')
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"加载数据文件失败: {e}")
        return []

def load_clothing_data():
    """
    加载衣服数据
    
    返回:
        list: 衣服数据列表（字典形式），按购买日期倒序排列，无购买日期的按名称排列
    
    异常:
        FileNotFoundError: 当数据文件不存在时抛出
        pd.errors.EmptyDataError: 当数据文件为空时抛出
    """
    try:
        df = pd.read_csv('data/clothing.csv')
        # 将空的购买日期替换为 NaT，并只保留日期部分
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce').dt.date
        # 先按购买日期倒序排列，对于没有购买日期的按名称排列
        df = df.sort_values(
            by=['purchase_date', 'name'],
            ascending=[False, True],
            na_position='last'
        )
        return df.to_dict('records')
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"加载数据文件失败: {e}")
        return []

def check_and_convert_images():
    """检查并转换static/images目录下的图片为WebP格式"""
    base_dir = os.path.join(app.static_folder, 'images')
    types = os.listdir(base_dir)
    for type_name in types:
        type_dir = os.path.join(base_dir, type_name)
        for filename in os.listdir(type_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                original_path = os.path.join(type_dir, filename)

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
    """手办列表路由：展示所有手办数据"""
    return render_template('figures/list.html', figures=load_figures_data())

@app.route('/clothing')
def show_clothing():
    """衣服列表路由：展示所有衣服数据"""
    return render_template('clothing/list.html', clothing=load_clothing_data())

@app.route('/figures/<int:item_id>')
def figures_detail(item_id):
    """手办详情路由"""
    return get_item_detail('figures', item_id)

@app.route('/clothing/<int:item_id>')
def clothing_detail(item_id):
    """衣服详情路由"""
    return get_item_detail('clothing', item_id)

@app.route('/figures/new')
def figures_new():
    """新建手办页面路由"""
    return render_template('figures/new.html')

@app.route('/clothing/new')
def clothing_new():
    """新建衣服页面路由"""
    return render_template('clothing/new.html')

def get_item_detail(item_type, item_id):
    """通用详情路由处理函数"""
    data_loader = {
        'figures': load_figures_data,
        'clothing': load_clothing_data
    }
    template_map = {
        'figures': 'figures/detail.html',
        'clothing': 'clothing/detail.html'
    }
    
    item_data = data_loader[item_type]()
    item = next((item for item in item_data if item['id'] == item_id), None)
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
        
        # 根据不同类型加载不同数据
        if item_type == 'figures':
            df = pd.read_csv('data/figures.csv')
        elif item_type == 'clothing':
            df = pd.read_csv('data/clothing.csv')
        else:
            raise ValueError('无效的物品类型')
        
        # 确保item_id和DataFrame中的id列类型一致
        item_id = str(item_id)  # 统一转为字符串
        df['id'] = df['id'].astype(str)
        
        # 处理图片上传
        image_filename = None
        if 'image' in request.files and request.files['image'].filename:
            image_file = request.files['image']
            # 生成安全的文件名
            filename = secure_filename(image_file.filename)
            # 确保目录存在
            image_dir = os.path.join(app.static_folder, 'images', item_type)
            os.makedirs(image_dir, exist_ok=True)
            # 保存原始图片
            image_path = os.path.join(image_dir, filename)
            image_file.save(image_path)
            # 转换为WebP格式
            compress_and_convert_to_webp(image_path, item_type)
            # 更新数据库中的图片字段
            image_filename = filename
        
        # 更新其他属性
        for key in request.form:
            if key in df.columns and key not in ['item_type', 'item_id']:
                df.loc[df['id'] == item_id, key] = request.form.get(key)
        
        # 如果有新图片，更新图片字段
        if image_filename:
            df.loc[df['id'] == item_id, 'image'] = image_filename
        
        # 保存更新后的数据
        data_path = os.path.join(os.path.dirname(__file__), 'data', f'{item_type}.csv')
        df.to_csv(data_path, index=False, encoding='utf-8')
        
        return jsonify({
            'success': True,
            'message': '属性更新成功'
        })
    except Exception as e:
        print(f"更新失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 400

@app.route('/create_item', methods=['POST'])
def create_item():
    """
    创建新条目接口
    
    功能:
        处理前端提交的新建条目请求
        
    参数:
        表单数据，包含条目数据和可能的图片文件
        
    返回:
        dict: 操作结果
        
    异常:
        ValueError: 当物品类型无效时抛出
        Exception: 当保存失败时抛出
    """
    try:
        # 获取表单数据
        item_type = request.form.get('item_type')
        
        # 验证物品类型
        if item_type not in ['figures', 'clothing']:
            raise ValueError('无效的物品类型')
            
        # 加载现有数据
        data_path = os.path.join(os.path.dirname(__file__), 'data', f'{item_type}.csv')
        
        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            # 如果文件不存在，创建新的DataFrame
            df = pd.DataFrame()
            
        # 生成新ID
        if df.empty:
            new_id = 1
        else:
            new_id = int(df['id'].max()) + 1  # 转换为Python int类型
            
        # 准备新条目数据
        new_item = {'id': new_id}
        
        # 定义字段映射（确保所有必要字段都有默认值）
        field_defaults = {
            'name': '',
            'main_category': '手办' if item_type == 'figures' else '衣服',  # 根据类型设置主类别
            'category': '',
            'purchase_price': 0,
            'shipping_fee': 0,
            'purchase_date': '',
            'arrival_date': '',
            'purchase_channel': '',
            'condition': '',
            'remark': '',
            'sold_price': None,
            'sold_date': '',
            'image': ''  # 图片字段，暂时为空
        }
        
        # 填充数据
        for field, default_value in field_defaults.items():
            if field in request.form and request.form.get(field).strip():
                new_item[field] = request.form.get(field)
            else:
                new_item[field] = default_value
            
        # 数据类型转换
        if new_item['purchase_price']:
            new_item['purchase_price'] = float(new_item['purchase_price'])
        if new_item['shipping_fee']:
            new_item['shipping_fee'] = float(new_item['shipping_fee'])
        if new_item['sold_price'] and new_item['sold_price'] != 'None':
            new_item['sold_price'] = float(new_item['sold_price'])
        
        # 处理图片上传
        image_filename = ''
        if 'image' in request.files and request.files['image'].filename:
            image_file = request.files['image']
            # 生成安全的文件名
            filename = secure_filename(image_file.filename)
            # 确保目录存在
            image_dir = os.path.join(app.static_folder, 'images', item_type)
            os.makedirs(image_dir, exist_ok=True)
            # 保存原始图片
            image_path = os.path.join(image_dir, filename)
            image_file.save(image_path)
            # 转换为WebP格式
            from utils.image_processor import compress_and_convert_to_webp
            compress_and_convert_to_webp(image_path, item_type)
            # 更新数据库中的图片字段
            new_item['image'] = filename
            
        # 添加到DataFrame
        new_df = pd.DataFrame([new_item])
        df = pd.concat([df, new_df], ignore_index=True)
        
        # 保存到CSV
        df.to_csv(data_path, index=False, encoding='utf-8')
        
        return jsonify({
            'success': True,
            'message': '条目创建成功',
            'item_id': int(new_id)  # 确保转换为Python int类型
        })
        
    except Exception as e:
        print(f"创建条目失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        }), 400


""" ========== 主程序入口 ============ """
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7334)  # 开发模式启动（生产环境需调整）

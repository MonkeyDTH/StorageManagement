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
    @param: JSON格式的属性数据
    @return: 操作结果
    """
    try:
        data = request.get_json()
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        
        # 根据不同类型加载不同数据
        if item_type == 'figures':
            df = pd.read_csv('data/figures.csv')
        elif item_type == 'clothing':
            df = pd.read_csv('data/clothing.csv')
        else:
            raise ValueError('无效的物品类型')
            
        # 更新数据并保存
        print(f"正在更新物品 {item_id} 的数据...")
        print(data)
        # 获取指定ID的行数据
        # 确保item_id和DataFrame中的id列类型一致
        item_id = str(data.get('item_id'))  # 统一转为字符串
        
        # 转换DataFrame中的id列为字符串类型
        df['id'] = df['id'].astype(str)
        
        # 查询匹配项
        item_row = df[df['id'] == item_id]
        
        # 安全转换为字典
        if not item_row.empty:
            item_dict = item_row.to_dict('records')[0]
        else:
            print(f"错误: 未找到ID为{item_id}的记录")
            print(f"可用ID列表: {df['id'].unique().tolist()}")
            item_dict = None
        
        # 修改查询方式确保类型匹配
        item_row = df[df['id'].astype(str) == item_id]
        
        # 如果需要转换为字典格式（单行）
        item_dict = item_row.to_dict('records')[0] if not item_row.empty else None

        # 或者直接使用iloc获取第一行（如果确定只有一行）
        item_data = item_row.iloc[0] if not item_row.empty else None
        for key, value in data.items():
            if key in df.columns and key not in ['item_type', 'item_id']:
                df.loc[df['id'] == item_id, key] = value
        
        data_path = os.path.join(os.path.dirname(__file__), 'data', f'{item_type}.csv')
        try:
            df.to_csv(data_path, index=False, encoding='utf-8')
        except Exception as e:
            print(f"保存失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存失败: {str(e)}'
            })
        
        return jsonify({
            'success': True,
            'message': '属性更新成功'
        })
    except Exception as e:
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
        JSON格式的条目数据
        
    返回:
        dict: 操作结果
        
    异常:
        ValueError: 当物品类型无效时抛出
        Exception: 当保存失败时抛出
    """
    try:
        data = request.get_json()
        item_type = data.get('item_type')
        
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
            'main_category': '手办',  # 手办的主类别
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
            new_item[field] = data.get(field, default_value)
            
        # 数据类型转换
        if new_item['purchase_price']:
            new_item['purchase_price'] = float(new_item['purchase_price'])
        if new_item['shipping_fee']:
            new_item['shipping_fee'] = float(new_item['shipping_fee'])
        if new_item['sold_price']:
            new_item['sold_price'] = float(new_item['sold_price'])
            
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

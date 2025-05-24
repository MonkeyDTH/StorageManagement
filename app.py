'''
Author: Leili
Date: 2025-05-18 20:41:27
LastEditors: Leili
LastEditTime: 2025-05-23 19:07:00
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
        list: 手办数据字典列表
    
    异常:
        FileNotFoundError: 当数据文件不存在时抛出
        pd.errors.EmptyDataError: 当数据文件为空时抛出
    """
    try:
        return pd.read_csv('data/figures.csv').to_dict('records')
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"加载数据文件失败: {e}")
        return []

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


""" ========== 主程序入口 ============ """
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7334)  # 开发模式启动（生产环境需调整）
'''
Author: Leili
Date: 2025-06-16 15:59:23
LastEditors: Leili
LastEditTime: 2025-06-18 13:38:09
FilePath: /StorageManagement/utils/item_manager.py
Description: 物品管理类，封装物品数据的加载、保存、更新等功能
'''

import pandas as pd
import os
from werkzeug.utils import secure_filename
from .image_processor import compress_and_convert_to_webp

class ItemCategory:
    """
    物品类别管理类
    
    用于封装物品数据的加载、保存、更新等功能，实现代码复用
    """
    
    def __init__(self, category_type, app=None):
        """
        初始化物品类别管理类
        
        参数:
            category_type (str): 物品类别类型，如'figures', 'clothing', 'goods'
            app (Flask): Flask应用实例，用于获取静态文件路径
            
        属性:
            type (str): 物品类别类型
            data_path (str): 数据文件路径
            template_prefix (str): 模板前缀
            app (Flask): Flask应用实例
        """
        self.type = category_type
        self.data_path = f'data/{category_type}.csv'
        self.template_prefix = f'{category_type}/'
        self.app = app
    
    def load_data(self):
        """
        加载物品数据
        
        返回:
            list: 物品数据字典列表，按购买日期倒序排列，无购买日期的按名称排列
        
        异常:
            FileNotFoundError: 当数据文件不存在时抛出
            pd.errors.EmptyDataError: 当数据文件为空时抛出
        """
        try:
            df = pd.read_csv(self.data_path)
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
    
    def get_categories(self):
        """
        获取所有不重复的子类别
        
        返回:
            list: 子类别列表，按字母顺序排序
        """
        data = self.load_data()
        return sorted(list(set(item['category'] for item in data if item.get('category'))))
    
    def get_item_by_id(self, item_id):
        """
        根据ID获取物品
        
        参数:
            item_id (int): 物品ID
            
        返回:
            dict: 物品数据字典，如果找不到则返回None
        """
        data = self.load_data()
        return next((item for item in data if str(item['id']) == str(item_id)), None)
    
    def update_item(self, item_id, form_data, image_file=None):
        """
        更新物品属性
        
        参数:
            item_id (str): 物品ID
            form_data (dict): 表单数据
            image_file (FileStorage): 上传的图片文件，可选
            
        返回:
            bool: 更新是否成功
            str: 成功或错误消息
            
        异常:
            Exception: 当更新失败时抛出
        """
        try:
            # 加载数据
            df = pd.read_csv(self.data_path)
            
            # 确保item_id和DataFrame中的id列类型一致
            item_id = str(item_id)  # 统一转为字符串
            df['id'] = df['id'].astype(str)
            
            # 处理图片上传
            image_filename = None
            if image_file and image_file.filename:
                # 生成安全的文件名
                filename = secure_filename(image_file.filename)
                # 确保目录存在
                if self.app:
                    image_dir = os.path.join(self.app.static_folder, 'images', self.type)
                else:
                    image_dir = os.path.join('static', 'images', self.type)
                os.makedirs(image_dir, exist_ok=True)
                # 保存原始图片
                image_path = os.path.join(image_dir, filename)
                image_file.save(image_path)
                # 转换为WebP格式
                compress_and_convert_to_webp(image_path, self.type)
                # 更新数据库中的图片字段
                image_filename = filename
            
            # 更新其他属性
            for key, value in form_data.items():
                if key in df.columns and key not in ['item_type', 'item_id']:
                    df.loc[df['id'] == item_id, key] = value
            
            # 如果有新图片，更新图片字段
            if image_filename:
                df.loc[df['id'] == item_id, 'image'] = image_filename
            
            # 保存更新后的数据
            df.to_csv(self.data_path, index=False, encoding='utf-8')
            
            return True, '属性更新成功'
        except Exception as e:
            print(f"更新失败: {str(e)}")
            return False, f'更新失败: {str(e)}'
    
    def create_item(self, form_data, image_file=None):
        """
        创建新物品
        
        参数:
            form_data (dict): 表单数据
            image_file (FileStorage): 上传的图片文件，可选
            
        返回:
            bool: 创建是否成功
            str: 成功或错误消息
            int: 新物品ID
            
        异常:
            Exception: 当创建失败时抛出
        """
        try:
            # 加载现有数据
            try:
                df = pd.read_csv(self.data_path)
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
            main_category = ''
            if self.type == 'figures':
                main_category = '手办'
            elif self.type == 'clothing':
                main_category = '衣服'
            else:
                main_category = '好物'
            field_defaults = {
                'name': '',
                'main_category': main_category,  # 根据类型设置主类别
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
                if field in form_data and form_data.get(field).strip():
                    new_item[field] = form_data.get(field)
                else:
                    new_item[field] = default_value
                
            # 数据类型转换
            if new_item['purchase_price']:
                new_item['purchase_price'] = float(new_item['purchase_price'])
            if new_item['shipping_fee']:
                new_item['shipping_fee'] = float(new_item['shipping_fee'])
                
            # 处理图片上传
            if image_file and image_file.filename:
                # 生成安全的文件名
                filename = secure_filename(image_file.filename)
                # 确保目录存在
                if self.app:
                    image_dir = os.path.join(self.app.static_folder, 'images', self.type)
                else:
                    image_dir = os.path.join('static', 'images', self.type)
                os.makedirs(image_dir, exist_ok=True)
                # 保存原始图片
                image_path = os.path.join(image_dir, filename)
                image_file.save(image_path)
                # 转换为WebP格式
                compress_and_convert_to_webp(image_path, self.type)
                # 更新数据库中的图片字段
                new_item['image'] = filename
                
            # 添加新条目到DataFrame
            new_df = pd.DataFrame([new_item])
            if df.empty:
                df = new_df
            else:
                df = pd.concat([df, new_df], ignore_index=True)
                
            # 保存更新后的数据
            df.to_csv(self.data_path, index=False, encoding='utf-8')
            
            return True, '创建成功', new_id
        except Exception as e:
            print(f"创建失败: {str(e)}")
            return False, f'创建失败: {str(e)}', None
    
    def calculate_price_stats(self):
        """
        计算价格统计信息
        
        计算总买入价格（包含购买价格和运费）、总卖出价格，以及按子类别统计的价格信息
        
        返回:
            tuple: (total_stats, category_stats)
                total_stats (dict): 整体统计信息
                category_stats (dict): 按子类别统计的价格信息
        """
        # 加载数据
        items_data = self.load_data()
        categories = self.get_categories()
        
        # 计算总买入价格（购买价格+运费）
        total_stats = {
            "total_purchase_price": 0,
            "total_sold_price": 0,
            "total_count": len(items_data),
            "sold_count": 0
        }
        
        # 按子类别计算价格统计
        category_stats = {}
        
        # 初始化每个类别的统计数据
        for category in categories:
            category_stats[category] = {
                'purchase_price': 0,
                'sold_price': 0,
                'count': 0,
                'sold_count': 0
            }
        
        for item in items_data:
            # 计算买入价格（购买价格+运费）
            purchase_price = item.get('purchase_price', 0) or 0
            shipping_fee = item.get('shipping_fee', 0) or 0
            item_total_price = purchase_price + shipping_fee
            total_stats['total_purchase_price'] += item_total_price
            
            # 计算卖出价格
            sold_price = item.get('sold_price', 0) or 0
            if sold_price and sold_price == sold_price:  # 检查是否为NaN
                total_stats['total_sold_price'] += sold_price
                total_stats['sold_count'] += 1
            
            # 按类别统计
            category = item.get('category', '')
            if category in category_stats:
                category_stats[category]['purchase_price'] += item_total_price
                category_stats[category]['count'] += 1
                if sold_price and sold_price == sold_price:  # 检查是否为NaN
                    category_stats[category]['sold_price'] += sold_price
                    category_stats[category]['sold_count'] += 1
        
        return total_stats, category_stats
    
from flask import Flask
import os
import json
import csv
from pathlib import Path
from datetime import datetime  # 改为从datetime模块导入datetime类

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 定义不同类型物品的数据文件路径
DATA_DIR = Path(__file__).parent / 'data'
FIGURE_DATA_FILE = DATA_DIR / 'figures.csv'
CLOTHING_DATA_FILE = DATA_DIR / 'clothing.csv'

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# 基类定义
class Item:
    def __init__(self, name, category, purchase_price, image=None, purchase_date=None, id=None):
        self.id = id
        self.name = name
        self.category = category
        self.purchase_price = purchase_price
        self.image = image
        self.purchase_date = purchase_date or datetime.now()
        self.item_type = self.__class__.__name__  # 记录物品类型

    @property
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'purchase_price': self.purchase_price,
            'image': self.image,
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d') if self.purchase_date else None,
            'item_type': self.item_type
        }

    @property
    def csv_dict(self):
        """返回用于CSV存储的字典"""
        return self.dict

# 手办子类
class FigureItem(Item):
    def __init__(self, name, category, purchase_price, quantity=1, image=None, 
                 purchase_date=None, sold_date=None, sold_price=None, id=None,
                 purchase_channel=None, condition=None, remark=None, shipping_fee=0, 
                 arrival_date=None):
        super().__init__(name, category, purchase_price, image, purchase_date, id)
        self.quantity = quantity
        self.sold_date = sold_date
        self.sold_price = sold_price
        self.purchase_channel = purchase_channel
        self.condition = condition
        self.remark = remark
        self.shipping_fee = shipping_fee
        self.arrival_date = arrival_date

    @property
    def dict(self):
        base_dict = super().dict
        figure_dict = {
            'quantity': self.quantity,
            'sold_date': self.sold_date.strftime('%Y-%m-%d') if self.sold_date else None,
            'sold_price': self.sold_price,
            'purchase_channel': self.purchase_channel,
            'condition': self.condition,
            'remark': self.remark,
            'shipping_fee': self.shipping_fee,
            'arrival_date': self.arrival_date.strftime('%Y-%m-%d') if self.arrival_date and hasattr(self.arrival_date, 'strftime') else None
        }
        return {**base_dict, **figure_dict}

    @property
    def csv_dict(self):
        return self.dict

# 衣服子类
class ClothingItem(Item):
    def __init__(self, name, category, purchase_price, image=None, 
                 purchase_date=None, id=None, quantity=1, shipping_fee=0):
        super().__init__(name, category, purchase_price, image, purchase_date, id)
        self.quantity = quantity
        self.shipping_fee = shipping_fee
        
    @property
    def dict(self):
        base_dict = super().dict
        clothing_dict = {
            'quantity': self.quantity,
            'shipping_fee': self.shipping_fee
        }
        return {**base_dict, **clothing_dict}
        
    @property
    def csv_dict(self):
        return self.dict

class StorageManager:
    def __init__(self):
        self.items = []
        self.load_items()

    def load_items(self):
        self.items = []
        # 加载手办数据
        self._load_figures()
        # 加载衣服数据
        self._load_clothing()
        # 按购买日期排序
        self.items.sort(key=lambda x: x.purchase_date, reverse=True)

    def _load_figures(self):
        """从CSV加载手办数据"""
        try:
            if not FIGURE_DATA_FILE.exists():
                return
                
            with open(FIGURE_DATA_FILE, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 移除item_type字段，因为它不是构造函数参数
                    if 'item_type' in row:
                        del row['item_type']
                        
                    # 转换日期字符串为datetime对象
                    if row.get('purchase_date'):
                        row['purchase_date'] = datetime.strptime(row['purchase_date'], '%Y-%m-%d')
                    if row.get('sold_date'):
                        row['sold_date'] = datetime.strptime(row['sold_date'], '%Y-%m-%d')
                    if row.get('arrival_date'):
                        row['arrival_date'] = datetime.strptime(row['arrival_date'], '%Y-%m-%d')
                    
                    # 转换数值类型
                    row['id'] = int(row['id']) if row.get('id') else None
                    row['purchase_price'] = float(row['purchase_price']) if row.get('purchase_price') else 0
                    row['quantity'] = int(row['quantity']) if row.get('quantity') else 1
                    row['shipping_fee'] = float(row['shipping_fee']) if row.get('shipping_fee') else 0
                    if row.get('sold_price'):
                        row['sold_price'] = float(row['sold_price']) if row['sold_price'].strip() else None
                    
                    self.items.append(FigureItem(**row))
        except Exception as e:
            print(f"加载手办数据出错: {e}")

    def _load_clothing(self):
        """从CSV加载衣服数据"""
        try:
            if not CLOTHING_DATA_FILE.exists():
                return
                
            with open(CLOTHING_DATA_FILE, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 移除item_type字段，因为它不是构造函数参数
                    if 'item_type' in row:
                        del row['item_type']
                        
                    # 转换日期字符串为datetime对象
                    if row.get('purchase_date'):
                        row['purchase_date'] = datetime.strptime(row['purchase_date'], '%Y-%m-%d')
                    
                    # 转换数值类型
                    row['id'] = int(row['id']) if row.get('id') else None
                    row['purchase_price'] = float(row['purchase_price']) if row.get('purchase_price') else 0
                    row['quantity'] = int(row['quantity']) if row.get('quantity') else 1
                    row['shipping_fee'] = float(row['shipping_fee']) if row.get('shipping_fee') else 0
                    
                    self.items.append(ClothingItem(**row))
        except Exception as e:
            print(f"加载衣服数据出错: {e}")

    def save_items(self):
        """保存所有物品到对应的CSV文件"""
        # 按类型分组物品
        figures = [item for item in self.items if isinstance(item, FigureItem)]
        clothing = [item for item in self.items if isinstance(item, ClothingItem)]
        
        # 保存手办数据
        self._save_figures(figures)
        # 保存衣服数据
        self._save_clothing(clothing)

    def _save_figures(self, figures):
        """保存手办数据到CSV"""
        if not figures:
            return
            
        # 确保目录存在
        FIGURE_DATA_FILE.parent.mkdir(exist_ok=True)
        
        # 获取所有可能的字段
        fieldnames = list(figures[0].csv_dict.keys())
        
        with open(FIGURE_DATA_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in figures:
                writer.writerow(item.csv_dict)

    def _save_clothing(self, clothing):
        """保存衣服数据到CSV"""
        if not clothing:
            return
            
        # 确保目录存在
        CLOTHING_DATA_FILE.parent.mkdir(exist_ok=True)
        
        # 获取所有可能的字段
        fieldnames = list(clothing[0].csv_dict.keys())
        
        with open(CLOTHING_DATA_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in clothing:
                writer.writerow(item.csv_dict)

storage = StorageManager()
app.storage = storage  # 将storage实例附加到app对象

# 移除重复的load_items方法

from . import routes
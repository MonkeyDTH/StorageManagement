from flask import Flask
import os
import json
from pathlib import Path
from datetime import datetime  # 改为从datetime模块导入datetime类

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = Path(__file__).parent / 'data' / 'items.json'

# 将Item类定义移到__init__.py中
class Item:
    def __init__(self, name, category, purchase_price, quantity=1, image=None, 
                 purchase_date=None, sold_date=None, sold_price=None, id=None,
                 purchase_channel=None, condition=None, remark=None):  # 新增remark参数
        self.id = id or len(app.storage.items) + 1
        self.name = name
        self.category = category
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.image = image
        self.purchase_date = purchase_date or datetime.now()
        self.purchase_channel = purchase_channel  # 新增买入渠道
        self.condition = condition  # 新增成色
        self.sold_date = sold_date
        self.sold_price = sold_price
        self.remark = remark  # 新增备注属性
        
    @property
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'purchase_price': self.purchase_price,
            'quantity': self.quantity,
            'image': self.image,
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d') if self.purchase_date else None,
            'purchase_channel': self.purchase_channel,  # 新增
            'condition': self.condition,  # 新增
            'sold_date': self.sold_date.strftime('%Y-%m-%d') if self.sold_date else None,
            'sold_price': self.sold_price,
            'remark': self.remark  # 新增
        }

class StorageManager:
    def __init__(self):
        self.items = []
        self.load_items()

    def load_items(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.items = []
                for item_data in data:
                    # 转换日期字符串为datetime对象
                    if 'purchase_date' in item_data and item_data['purchase_date']:
                        item_data['purchase_date'] = datetime.strptime(item_data['purchase_date'], '%Y-%m-%d')
                    if 'sold_date' in item_data and item_data['sold_date']:
                        item_data['sold_date'] = datetime.strptime(item_data['sold_date'], '%Y-%m-%d')
                    self.items.append(Item(**item_data))
        except (FileNotFoundError, json.JSONDecodeError):
            self.items = []

    def save_items(self):
        DATA_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([item.dict for item in self.items], f, ensure_ascii=False, indent=2)

storage = StorageManager()
app.storage = storage  # 将storage实例附加到app对象

def load_items(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.items = []
                for item_data in data:
                    # ... 原有日期转换代码保持不变 ...
                    self.items.append(Item(**item_data))
                
                # 添加排序逻辑
                self.items.sort(key=lambda x: x.purchase_date, reverse=True)
        except (FileNotFoundError, json.JSONDecodeError):
            self.items = []

from . import routes
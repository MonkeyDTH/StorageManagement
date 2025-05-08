'''
Author: Leili
Date: 2025-05-08 12:42:42
LastEditors: Leili
LastEditTime: 2025-05-08 12:42:54
FilePath: /StorageManagement/migrate_data.py
Description: 
'''
import json
import csv
from pathlib import Path
from datetime import datetime

# 定义文件路径
DATA_DIR = Path(__file__).parent / 'app' / 'data'
JSON_FILE = DATA_DIR / 'items.json'
FIGURE_DATA_FILE = DATA_DIR / 'figures.csv'
CLOTHING_DATA_FILE = DATA_DIR / 'clothing.csv'

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# 检查是否存在旧的JSON数据文件
if not JSON_FILE.exists():
    print(f"旧数据文件 {JSON_FILE} 不存在，无需迁移")
    exit(0)

# 读取JSON数据
try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"成功读取 {len(data)} 条物品记录")
except Exception as e:
    print(f"读取JSON数据出错: {e}")
    exit(1)

# 分类物品
figures = []
clothing = []

# 根据类别分类物品（这里假设所有带有'衣'或'服'的类别都是衣服，其余为手办）
for item in data:
    category = item.get('category', '')
    if '衣' in category or '服' in category:
        # 只保留衣服需要的字段
        clothing_item = {
            'id': item.get('id'),
            'name': item.get('name'),
            'category': category,
            'purchase_price': item.get('purchase_price'),
            'image': item.get('image'),
            'purchase_date': item.get('purchase_date'),
            'item_type': 'ClothingItem'
        }
        clothing.append(clothing_item)
    else:
        # 保留所有字段作为手办
        item['item_type'] = 'FigureItem'
        figures.append(item)

print(f"分类完成: {len(figures)} 个手办, {len(clothing)} 件衣服")

# 保存手办数据到CSV
if figures:
    try:
        # 获取所有可能的字段
        fieldnames = list(figures[0].keys())
        
        with open(FIGURE_DATA_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in figures:
                writer.writerow(item)
        print(f"手办数据已保存到 {FIGURE_DATA_FILE}")
    except Exception as e:
        print(f"保存手办数据出错: {e}")

# 保存衣服数据到CSV
if clothing:
    try:
        # 获取所有可能的字段
        fieldnames = list(clothing[0].keys())
        
        with open(CLOTHING_DATA_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in clothing:
                writer.writerow(item)
        print(f"衣服数据已保存到 {CLOTHING_DATA_FILE}")
    except Exception as e:
        print(f"保存衣服数据出错: {e}")

print("数据迁移完成！")
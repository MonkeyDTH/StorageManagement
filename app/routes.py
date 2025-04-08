from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image
import io
from . import app

items = app.storage.items

class Item:
    def __init__(self, name, category, purchase_price, quantity=1, image=None, 
                 purchase_date=None, sold_date=None, sold_price=None, id=None):
        self.id = id or len(items) + 1
        self.name = name
        self.category = category
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.image = image
        self.purchase_date = purchase_date or datetime.now()
        self.sold_date = sold_date
        self.sold_price = sold_price
        
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
            'sold_date': self.sold_date.strftime('%Y-%m-%d') if self.sold_date else None,
            'sold_price': self.sold_price
        }

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', items=items)

def compress_image(file, max_size=(800, 800), quality=85):
    """压缩图片并返回BytesIO对象"""
    try:
        img = Image.open(file.stream)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            # 修改这里，使用兼容性更好的方式
            img.thumbnail(max_size, Image.LANCZOS)  # 旧版本Pillow使用Image.LANCZOS
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality)
        output.seek(0)
        return output
    except Exception as e:
        app.logger.error(f"图片压缩失败: {e}")
        return None

# 修改路由函数，使用app.save_items()代替直接调用
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d') if request.form['purchase_date'] else None
        
        # 处理图片上传
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                
                # 压缩图片
                compressed_img = compress_image(file)
                if compressed_img:
                    with open(upload_path, 'wb') as f:
                        f.write(compressed_img.read())
                    image = filename
        
        items.append(Item(
            name=name,
            category=category,
            purchase_price=price,
            quantity=quantity,
            image=image,
            purchase_date=purchase_date
        ))
        app.storage.save_items()  # 修改为调用app.storage.save_items()
        return redirect(url_for('index'))
    
    return render_template('add_item.html')

@app.route('/sell/<int:item_id>', methods=['GET', 'POST'])
def sell_item(item_id):
    item = next((i for i in items if i.id == item_id), None)
    if not item:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        item.sold_price = float(request.form['sold_price'])
        item.sold_date = datetime.strptime(request.form['sold_date'], '%Y-%m-%d')
        app.storage.save_items()  # 修改为调用app.storage.save_items()
        return redirect(url_for('index'))
    
    return render_template('sell_item.html', item=item)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = next((i for i in items if i.id == item_id), None)
    if not item:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.category = request.form['category']
        item.purchase_price = float(request.form['price'])
        item.quantity = int(request.form['quantity'])
        item.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d') if request.form['purchase_date'] else None
        
        # 处理图片更新
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                
                compressed_img = compress_image(file)
                if compressed_img:
                    with open(upload_path, 'wb') as f:
                        f.write(compressed_img.read())
                    item.image = filename
        
        app.storage.save_items()  # 修改为调用app.storage.save_items()
        return redirect(url_for('index'))
    
    return render_template('edit_item.html', item=item)
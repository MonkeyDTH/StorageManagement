from flask import render_template, request, redirect, url_for, flash  # 添加flash导入
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image
import io
from . import app

items = app.storage.items

class Item:
    def __init__(self, name, category, purchase_price, quantity=1, image=None, 
                 purchase_date=None, sold_date=None, sold_price=None, id=None,
                 purchase_channel=None, condition=None, remark=None):  # 添加新参数
        self.id = id or len(items) + 1
        self.name = name
        self.category = category
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.image = image
        self.purchase_date = purchase_date or datetime.now()
        self.sold_date = sold_date
        self.sold_price = sold_price
        self.purchase_channel = purchase_channel  # 新增
        self.condition = condition  # 新增
        self.remark = remark  # 新增

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
    category = request.args.get('category')
    if category:
        items = [item for item in app.storage.items if item.category == category]
    else:
        items = app.storage.items
    
    # 计算统计信息
    total_purchase = sum(item.purchase_price * item.quantity for item in items)
    total_sold = sum(item.sold_price * item.quantity 
                    for item in items if item.sold_price is not None)
    
    categories = list(set(item.category for item in app.storage.items))
    items = sorted(items, key=lambda x: x.purchase_date, reverse=True)
    
    return render_template('index.html', 
                         items=items,
                         categories=categories,
                         current_category=category,
                         total_purchase=total_purchase,
                         total_sold=total_sold)

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

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            price = request.form.get('price', '0').strip()
            quantity = request.form.get('quantity', '1').strip()
            
            if not name or not category:
                flash('物品名称和类别不能为空', 'error')
                return redirect(url_for('add_item'))
                
            # 转换数值类型
            try:
                price = float(price)
                quantity = int(quantity)
            except ValueError:
                flash('价格和数量必须是有效数字', 'error')
                return redirect(url_for('add_item'))
                
            purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d') if request.form['purchase_date'] else None
            purchase_channel = request.form.get('purchase_channel')  # 新增
            condition = request.form.get('condition')  # 新增
            remark = request.form.get('remark')  # 新增
            
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
                purchase_date=purchase_date,
                purchase_channel=purchase_channel,
                condition=condition,
                remark=remark  # 确保这行末尾没有多余的逗号
            ))  # 确保括号正确闭合
            app.storage.save_items()
            return redirect(url_for('index'))
        
        except Exception as e:
            app.logger.error(f"添加物品出错: {str(e)}")
            flash('添加物品时发生错误', 'error')
            return redirect(url_for('add_item'))
    
    return render_template('add_item.html')

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
        item.purchase_channel = request.form.get('purchase_channel')
        item.condition = request.form.get('condition')
        item.remark = request.form.get('remark')
        
        # 处理卖出信息
        sold_price = request.form.get('sold_price')
        item.sold_price = float(sold_price) if sold_price else None
        sold_date = request.form.get('sold_date')
        item.sold_date = datetime.strptime(sold_date, '%Y-%m-%d') if sold_date else None
        
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
        
        app.storage.save_items()
        return redirect(url_for('index'))
    
    return render_template('edit_item.html', item=item)
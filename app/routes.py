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
                 purchase_channel=None, condition=None, remark=None, shipping_fee=0):  # 添加shipping_fee参数
        self.id = id or len(items) + 1
        self.name = name
        self.category = category
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.image = image
        self.purchase_date = purchase_date or datetime.now()
        self.sold_date = sold_date
        self.sold_price = sold_price
        self.purchase_channel = purchase_channel
        self.condition = condition
        self.remark = remark
        self.shipping_fee = shipping_fee  # 添加运费属性

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
            'sold_price': self.sold_price,
            'purchase_channel': self.purchase_channel,
            'condition': self.condition,
            'remark': self.remark,
            'shipping_fee': self.shipping_fee
        }

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    category = request.args.get('category')
    is_main_category = request.args.get('main_category') == 'true'
    
    if category:
        if is_main_category:
            items = [item for item in app.storage.items if item.category.startswith(category)]
        else:
            items = [item for item in app.storage.items if item.category == category]
    else:
        items = app.storage.items
    
    # Process categories for hierarchical display
    all_categories = set(item.category for item in app.storage.items)
    processed_categories = []
    main_categories = set()
    
    for cat in all_categories:
        if '-' in cat:
            main_cat = cat.split('-')[0]
            main_categories.add(main_cat)
            processed_categories.append({
                'full': cat,
                'main': main_cat,
                'sub': cat.split('-')[1]
            })
        else:
            processed_categories.append({
                'full': cat,
                'main': cat,
                'sub': None
            })
            main_categories.add(cat)
    
    # Calculate totals
    total_purchase = sum((item.purchase_price + (item.shipping_fee or 0)) * item.quantity for item in items)
    total_sold = sum(item.sold_price * item.quantity for item in items if item.sold_price is not None)
    
    # Sort categories
    processed_categories.sort(key=lambda x: (x['main'], x['sub'] or ''))
    main_categories = sorted(list(main_categories))
    
    return render_template('index.html', 
                         items=items,
                         categories=processed_categories,
                         main_categories=main_categories,
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
                # 处理运费
                shipping_fee = float(request.form.get('shipping_fee', '0').strip() or '0')
            except ValueError:
                flash('价格、数量或运费必须是有效数字', 'error')
                return redirect(url_for('add_item'))
                
            purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d') if request.form['purchase_date'] else None
            purchase_channel = request.form.get('purchase_channel')
            condition = request.form.get('condition')
            remark = request.form.get('remark')
            
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
        
            # 创建新物品对象，确保包含所有属性
            new_item = Item(
                name=name,
                category=category,
                purchase_price=price,
                quantity=quantity,
                image=image,
                purchase_date=purchase_date,
                purchase_channel=purchase_channel,
                condition=condition,
                remark=remark
            )
            
            # 添加运费属性
            new_item.shipping_fee = shipping_fee
            
            items.append(new_item)
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
        try:
            item.name = request.form['name']
            item.category = request.form['category']
            item.purchase_price = float(request.form['price'])
            item.shipping_fee = float(request.form.get('shipping_fee', 0))
            item.quantity = int(request.form.get('quantity', 1))
            purchase_date = request.form.get('purchase_date')
            item.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d') if purchase_date else None
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
                        # 获取旋转角度
                        rotation_angle = int(request.form.get('rotation_angle', 0))
                        if rotation_angle != 0:
                            # 实际旋转图片
                            img = Image.open(compressed_img)
                            img = img.rotate(-rotation_angle, expand=True)
                            compressed_img = io.BytesIO()
                            img.save(compressed_img, format='JPEG', quality=85)
                            compressed_img.seek(0)
                        
                        with open(upload_path, 'wb') as f:
                            f.write(compressed_img.read())
                        item.image = filename
            
            app.storage.save_items()
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"编辑物品出错: {str(e)}")
            flash('编辑物品时发生错误', 'error')
            return redirect(url_for('edit_item', item_id=item.id))
    
    return render_template('edit_item.html', title='编辑物品', item=item)


@app.route('/stats')
def stats():
    # 获取所有物品
    items = app.storage.items
    
    # 处理分类
    all_categories = set(item.category for item in items)
    processed_categories = []
    main_categories = set()
    
    for cat in all_categories:
        if '-' in cat:
            main_cat = cat.split('-')[0]
            main_categories.add(main_cat)
            processed_categories.append({
                'full': cat,
                'main': main_cat,
                'sub': cat.split('-')[1]
            })
        else:
            processed_categories.append({
                'full': cat,
                'main': cat,
                'sub': None
            })
            main_categories.add(cat)
    
    # 计算总价值
    total_purchase = sum((item.purchase_price + (item.shipping_fee or 0)) * item.quantity for item in items)
    total_sold = sum(item.sold_price * item.quantity for item in items if item.sold_price is not None)
    
    # 排序分类
    processed_categories.sort(key=lambda x: (x['main'], x['sub'] or ''))
    main_categories = sorted(list(main_categories))
    
    return render_template('stats.html', 
                         items=items,
                         categories=processed_categories,
                         main_categories=main_categories,
                         total_purchase=total_purchase,
                         total_sold=total_sold)
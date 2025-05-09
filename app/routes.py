from flask import render_template, request, redirect, url_for, flash  # 添加flash导入
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image
import io
from . import app, Item, FigureItem, ClothingItem

items = app.storage.items

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_totals(items):
    """计算物品总购买价格和总售价"""
    total_purchase = sum((float(item.purchase_price) + float(item.shipping_fee or 0)) * int(item.quantity) for item in items)
    total_sold = sum(float(item.sold_price) * int(item.quantity) for item in items if hasattr(item, 'sold_price') and item.sold_price not in (None, ''))
    return total_purchase, total_sold

@app.route('/')
def index():
    main_category = request.args.get('main_category')
    
    if main_category:
        items = [item for item in app.storage.items if item.main_category == main_category]
    else:
        items = app.storage.items
    
    # Process categories
    main_categories = sorted(set(item.main_category for item in app.storage.items))
    processed_categories = []
    for main_cat in main_categories:
        # 获取该主类别下的所有物品的category属性值
        sub_categories = sorted(set(item.category for item in app.storage.items if item.main_category == main_cat))
        processed_categories.append({
            'main': main_cat,
            'sub': sub_categories
        })
    
    # Calculate totals
    total_purchase, total_sold = calculate_totals(items)
    
    return render_template('index.html', 
                         items=items,
                         categories=processed_categories,
                         main_categories=main_categories,
                         current_main_category=main_category,
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
            item_type = request.form.get('item_type', 'figure').strip()  # 新增物品类型字段
            
            if not name or not category:
                flash('物品名称和类别不能为空', 'error')
                return redirect(url_for('add_item'))
                
            # 转换数值类型
            try:
                price = float(price)
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
                
                # 获取基本属性
                purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d') if request.form['purchase_date'] else None
                
                # 根据物品类型创建不同的对象
                if item_type == 'clothing':
                    # 创建衣服对象
                    new_item = ClothingItem(
                        name=name,
                        category=category,
                        purchase_price=price,
                        image=image,
                        purchase_date=purchase_date,
                        id=len(items) + 1
                    )
                else:  # 默认为手办类型
                    # 获取手办特有属性
                    quantity = int(request.form.get('quantity', '1').strip())
                    shipping_fee = float(request.form.get('shipping_fee', '0').strip() or '0')
                    purchase_channel = request.form.get('purchase_channel')
                    condition = request.form.get('condition')
                    remark = request.form.get('remark')
                    arrival_date = request.form.get('arrival_date')
                    arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d') if arrival_date else None
                    
                    # 创建手办对象
                    new_item = FigureItem(
                        name=name,
                        category=category,
                        purchase_price=price,
                        quantity=quantity,
                        image=image,
                        purchase_date=purchase_date,
                        purchase_channel=purchase_channel,
                        condition=condition,
                        remark=remark,
                        shipping_fee=shipping_fee,
                        arrival_date=arrival_date,
                        id=len(items) + 1
                    )
                
                items.append(new_item)
                app.storage.save_items()
                return redirect(url_for('index'))
            except ValueError:
                flash('价格、数量或运费必须是有效数字', 'error')
                return redirect(url_for('add_item'))
        
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
            # 更新基本属性
            item_type = item.__class__.__name__
            item.name = request.form['name']
            item.category = request.form['category']
            item.purchase_price = float(request.form['price'])
            item.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d') if request.form['purchase_date'] else None
            
            # 根据物品类型更新特定属性
            if item_type == 'FigureItem':
                item.quantity = int(request.form['quantity'])
                item.purchase_channel = request.form.get('purchase_channel')
                item.condition = request.form.get('condition')
                item.remark = request.form.get('remark')
                
                # 处理运费
                shipping_fee = request.form.get('shipping_fee', '0').strip() or '0'
                item.shipping_fee = float(shipping_fee)
                
                # 处理到货日期
                arrival_date = request.form.get('arrival_date')
                item.arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d') if arrival_date else None
            
            # 处理卖出信息（仅对FigureItem类型处理）
            if item_type == 'FigureItem':
                sold_date = request.form.get('sold_date')
                sold_price = request.form.get('sold_price')
                
                if sold_date:
                    item.sold_date = datetime.strptime(sold_date, '%Y-%m-%d')
                    item.sold_price = float(sold_price) if sold_price else None
                else:
                    item.sold_date = None
                    item.sold_price = None
            
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
        except Exception as e:
            app.logger.error(f"编辑物品出错: {str(e)}")
            flash('编辑物品时发生错误', 'error')
            return redirect(url_for('edit_item', item_id=item.id))
    
    return render_template('edit_item.html', title='编辑物品', item=item)

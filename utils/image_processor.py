from PIL import Image
import os

def get_webp_path(original_path, item_type):
    """生成WebP格式的文件路径
    :param original_path: 原始图片路径
    :param item_type: 物品类型（clothing/figures）
    :return: WebP格式的文件路径
    """
    filename = os.path.basename(original_path)
    base_name = os.path.splitext(filename)[0]
    return os.path.join('static', 'images', item_type, base_name + '.webp')

def compress_and_convert_to_webp(original_path, item_type, quality=80, max_size=(1600, 1600)):
    """使用Pillow实现图片压缩和WebP转换
    :param original_path: 原始图片路径
    :param item_type: 物品类型（clothing/figures）
    :param quality: 压缩质量(1-100)
    :param max_size: 最大尺寸(宽,高)
    """
    output_path = get_webp_path(original_path, item_type)
    if os.path.exists(output_path):
        return output_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with Image.open(original_path) as img:
        # 保持宽高比缩放
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 转换为RGB模式(如果是RGBA)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # 直接保存为WebP格式
        img.save(output_path, 'WEBP', quality=quality)
    return output_path
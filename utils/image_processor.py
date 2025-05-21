from PIL import Image
import os

def compress_and_convert_to_webp(original_path, output_path, quality=80, max_size=(1600, 1600)):
    """
    使用Pillow实现图片压缩和WebP转换
    :param original_path: 原始图片路径
    :param output_path: 输出路径(.webp)
    :param quality: 压缩质量(1-100)
    :param max_size: 最大尺寸(宽,高)
    """
    with Image.open(original_path) as img:
        # 保持宽高比缩放
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 转换为RGB模式(如果是RGBA)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # 直接保存为WebP格式
        img.save(output_path, 'WEBP', quality=quality)

def get_webp_path(original_path):
    """生成WebP格式的文件路径"""
    return os.path.splitext(original_path)[0] + '.webp'
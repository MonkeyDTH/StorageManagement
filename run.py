from app import app
import os

if __name__ == '__main__':
    # 确保上传文件夹存在
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # 配置静态文件URL规则
    app.url_map.strict_slashes = False
    
    # 运行应用
    app.run(
        debug=True,  # 启用调试模式
        host='0.0.0.0',
        port=5000
    )
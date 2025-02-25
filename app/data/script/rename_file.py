import os
from PIL import Image

# 定义图片目录
image_dir = r""

# 获取目录下所有文件
for filename in os.listdir(image_dir):
    # 判断文件是否以 pic 开头并以 .jpg 结尾
    if filename.startswith("pic") and filename.endswith(".jpg"):
        # 构建文件路径
        jpg_path = os.path.join(image_dir, filename)
        
        # 打开 .jpg 图片文件
        try:
            with Image.open(jpg_path) as img:
                # 生成新的 .png 文件路径
                png_filename = filename.replace(".jpg", ".png")
                png_path = os.path.join(image_dir, png_filename)
                
                # 将图片保存为 .png 格式
                img.save(png_path, format="PNG")
                print(f"转换成功: {jpg_path} -> {png_path}")
        except Exception as e:
            print(f"转换失败: {jpg_path}, 错误: {e}")
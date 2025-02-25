import os
from PIL import Image

# 定义图片目录
image_dir = r""

# 获取目录下所有文件
for filename in os.listdir(image_dir):
    # 判断文件是否以 pic 开头并以 .jpg 结尾
    if filename.startswith("pic") and filename.endswith(".jpg"):
        jpg_path = os.path.join(image_dir, filename)
        os.remove(jpg_path)
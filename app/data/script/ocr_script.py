from PIL import Image
import pytesseract
import os



# 配置 Tesseract 可执行文件路径（确保 Tesseract 已安装）
pytesseract.pytesseract.tesseract_cmd = r"D:/{{path}}/tess/tesseract.exe"  # Windows 下路径
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Linux 下路径

def extract_text_from_image(image_path):
    """
    从图片中提取文字
    :param image_path: 图片文件路径
    :return: 提取到的文字
    """
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        return None
    
    try:
        # 打开图片
        img = Image.open(image_path)
        # 使用 Tesseract OCR 提取文字
        text = pytesseract.image_to_string(img, lang="eng")  # 默认使用英文，可以切换为其他语言，如 "chi_sim"
        return text
    except Exception as e:
        print(f"提取文字时出错: {e}")
        return None

# 示例：指定截图图片路径
image_path = r"D:\图片\ocr\1.png"  # 替换为你的图片路径
extracted_text = extract_text_from_image(image_path)

if extracted_text:
    print("提取的文字内容如下：")
    print(extracted_text)
else:
    print("未提取到文字内容。")
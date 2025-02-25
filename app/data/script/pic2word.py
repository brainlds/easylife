from PIL import Image
import pytesseract
import os

# 配置 Tesseract 可执行文件路径
pytesseract.pytesseract.tesseract_cmd = r"{{path}}/tess/tesseract.exe"  # 替换为你的路径
os.environ["TESSDATA_PREFIX"] = r"{{path}}/tess/tessdata"  # 替换为 tessdata 的路径

def extract_code_from_images(input_dir, output_file):
    """
    提取指定文件夹中的图片文字，存储为代码文件
    :param input_dir: 图片文件夹路径
    :param output_file: 输出的代码文件路径
    """
    try:
        # 初始化结果字符串
        extracted_code = ""

        # 遍历目录下所有文件
        for filename in sorted(os.listdir(input_dir)):
            # 构造完整路径
            file_path = os.path.join(input_dir, filename)

            # 检查是否为图片文件
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                print(f"正在处理文件: {filename}")

                try:
                    # 打开图片并提取文字
                    img = Image.open(file_path)
                    text = pytesseract.image_to_string(img, lang="eng")  # 设为英文识别

                    # 简单筛选代码内容：以常见代码特征为判断依据（可根据需要调整）
                    code_lines = [line for line in text.splitlines() if line.strip().startswith(("import", "def", "class", "from", "if", "else", "for", "while", "#")) or line.strip()]
                    extracted_code += "\n".join(code_lines) + "\n\n"

                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {e}")

        # 将提取的代码写入到输出文件
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(extracted_code)

        print(f"提取完成，代码已保存到: {output_file}")

    except Exception as e:
        print(f"提取过程出错: {e}")

# 示例使用
input_dir = r"r"  # 替换为你的图片目录路径
output_file = r""  # 替换为保存代码的路径
extract_code_from_images(input_dir, output_file)
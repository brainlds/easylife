import os
from docx import Document
from PIL import Image
import pytesseract

# 配置 Tesseract 可执行文件路径（确保 Tesseract 已安装）
pytesseract.pytesseract.tesseract_cmd = r"D:/{{path}}/tess/tesseract.exe"

def extract_images_from_docx(docx_path, output_dir):
    """
    从 Word 文档中提取所有图片并保存到指定目录
    :param docx_path: Word 文档路径
    :param output_dir: 保存图片的目录
    :return: 保存的图片路径列表
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    document = Document(docx_path)
    image_paths = []
    
    for i, rel in enumerate(document.part.rels.values()):
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            image_path = os.path.join(output_dir, f"image_{i + 1}.png")
            with open(image_path, "wb") as img_file:
                img_file.write(image_data)
            image_paths.append(image_path)
    
    return image_paths

def extract_text_from_images(image_paths):
    """
    对图片路径列表中的每张图片进行OCR文字提取
    :param image_paths: 图片路径列表
    :return: 提取到的文字
    """
    extracted_text = ""
    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img, lang="eng")
            extracted_text += f"\n--- 图片 {img_path} ---\n{text}\n"
        except Exception as e:
            print(f"处理图片 {img_path} 时出错: {e}")
    return extracted_text

if __name__ == "__main__":
    # 指定 Word 文档路径和输出目录
    docx_path = r""  # 替换为你的 Word 文件路径
    output_dir = r"r"  # 替换为保存图片的目录路径

    # 提取图片
    image_paths = extract_images_from_docx(docx_path, output_dir)
    print(f"从 Word 文档中提取了 {len(image_paths)} 张图片，保存至 {output_dir}")

    # 提取文字
    if image_paths:
        extracted_text = extract_text_from_images(image_paths)
        if extracted_text.strip():
            print("提取的文字内容如下：")
            print(extracted_text)
        else:
            print("未提取到文字内容。")
    else:
        print("文档中未找到图片。")
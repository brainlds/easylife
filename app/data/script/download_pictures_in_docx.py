import os
from docx import Document

def extract_images_from_docx(docx_path, output_dir):
    """
    提取 .docx 文件中的所有图片并保存到指定目录。

    :param docx_path: .docx 文件的路径。
    :param output_dir: 图片存储的目标目录。
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 打开 .docx 文件
    doc = Document(docx_path)

    # 统计图片数量
    image_count = 0

    # 遍历文档中每个部分的元素
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:  # 查找图片相关的关系
            image_count += 1
            image_data = rel.target_part.blob

            # 设置文件名并保存
            image_filename = os.path.join(output_dir, f"pic{image_count}.jpg")
            with open(image_filename, "wb") as img_file:
                img_file.write(image_data)

    print(f"提取完成，共提取 {image_count} 张图片，保存在 {output_dir} 中。")

if __name__ == "__main__":
    # 设置输入 .docx 文件路径
    docx_file = r""

    # 设置输出图片目录
    output_directory = r""

    # 调用提取函数
    extract_images_from_docx(docx_file, output_directory)
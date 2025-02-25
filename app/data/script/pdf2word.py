from pdf2docx import Converter

def convert_pdf_to_word(pdf_file, word_file):
    """
    将 PDF 文件转换为 Word 文件
    :param pdf_file: PDF 文件路径
    :param word_file: 目标 Word 文件路径
    """
    try:
        # 创建一个 Converter 对象
        cv = Converter(pdf_file)
        
        # 将 PDF 转换为 Word
        cv.convert(word_file, start=0, end=None)
        
        print(f"转换成功！Word 文件保存为：{word_file}")
    except Exception as e:
        print(f"转换失败: {e}")

# 示例：指定要转换的 PDF 文件路径和目标 Word 文件路径
pdf_file = r""  # 替换为你的 PDF 文件路径
word_file = r""  # 替换为你的输出 Word 文件路径

# 调用转换函数
convert_pdf_to_word(pdf_file, word_file)
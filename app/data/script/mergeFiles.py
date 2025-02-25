import os

# 指定包含 Markdown 文件的目录
input_directory = './md_files/'  # 你的 Markdown 文件所在目录
output_file = 'combined.md'  # 输出的合并文件

# 获取该目录下所有 Markdown 文件
md_files = [f for f in os.listdir(input_directory) if f.endswith('.md')]

# 打开输出文件进行写入
with open(output_file, 'w', encoding='utf-8') as outfile:
    for filename in md_files:
        filepath = os.path.join(input_directory, filename)
        
        # 打开每个文件并将内容写入输出文件
        with open(filepath, 'r', encoding='utf-8') as infile:
            outfile.write(f"\n# {filename}\n\n")  # 可以加一个标题来区分文件内容
            outfile.write(infile.read())
            outfile.write("\n\n")  # 在文件间加两个换行符

# input_directory 是存放 Markdown 文件的文件夹路径。
# md_files 是一个包含所有 .md 文件的列表。
# 每个文件的内容被读入并写入到 combined.md 文件中，且在每个文件的内容之前加上文件名作为一个区分标识。
# 假设你的 C# 程序已经编译成了 my_program.exe
import os
import glob
import subprocess
import sys
# 强制设置环境变量为 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
# 设置标准输出为 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
# 指定要查找的目录
directory = r''

# 使用 glob 模块查找 .ev 文件
ev_files = glob.glob(os.path.join(directory, '*.ev4'))

# 打印找到的 .ev 文件路径
for file in ev_files:
    print(file)
    # 获取文件的目录和文件名（不带扩展名）
    directory, filename = os.path.split(file)
    file_base, _ = os.path.splitext(filename)

    # 生成新的文件路径，后缀改为 .mp4
    decrypted_file_path = os.path.join(directory, f"{file_base}.mp4")  
    print(decrypted_file_path)
    print('----------------------------------------') 
    result = subprocess.run([r'\EVEPlayer解密器\main.exe', file], capture_output=True, text=True)
    print(result.stdout)  # 输出 C# 程序的标准输出
    print(result.stderr)  # 输出 C# 程序的错误输出（如果有）

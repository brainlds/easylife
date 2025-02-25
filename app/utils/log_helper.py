import os
import json
from datetime import datetime

def save_deepseek_response(test_type: str, response: str):
    """
    保存 DeepSeek 的响应到题库文件
    
    @param test_type: 测试类型
    @param response: DeepSeek 的响应
    """
    # 创建 question_bank 目录和对应的测试类型子目录
    question_bank_dir = os.path.join("question_bank", test_type)
    if not os.path.exists(question_bank_dir):
        os.makedirs(question_bank_dir)
    
    # 生成文件名，包含时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(question_bank_dir, f"deepseek_{test_type}_{timestamp}.json")
    
    # 保存响应
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 测试类型: {test_type}\n")
        f.write(f"# 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 原始响应:\n")
        f.write(response)
        
        # 尝试解析并格式化 JSON
        try:
            # 查找 JSON 开始和结束位置
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                parsed_json = json.loads(json_str)
                f.write("\n\n# 格式化的 JSON:\n")
                f.write(json.dumps(parsed_json, ensure_ascii=False, indent=2))
        except Exception as e:
            f.write(f"\n\n# JSON 解析失败: {str(e)}") 
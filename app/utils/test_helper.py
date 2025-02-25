from .llm_clients import create_llm_client
from app.models.test_models import TestGenerator
from .log_helper import save_deepseek_response
import logging
import json
from datetime import datetime
import os
import hashlib

logger = logging.getLogger(__name__)

TEST_PROMPTS = {
    'mbti': """请生成30个MBTI性格测试题目，每个题目包含以下简单格式：
{
    "id": 数字编号,
    "content": "问题内容",
    "option_a": "选项A的内容",
    "option_b": "选项B的内容",
    "dimension_a": "选项A对应的维度(E/I/S/N/T/F/J/P)",
    "dimension_b": "选项B对应的维度(E/I/S/N/T/F/J/P)"
}""",
    
    'career': """请生成30个职业倾向测试题目，每个题目包含以下简单格式：
{
    "id": 数字编号,
    "content": "问题内容",
    "category": "相关的职业类型，如管理,领导"
}""",
    
    'enneagram': """请生成30个九型人格测试题目，每个题目包含以下简单格式：
{
    "id": 数字编号,
    "content": "问题内容",
    "category": "对应的九型人格类型(1-9)"
}"""
}

# 示例格式更简单
EXPECTED_FORMAT = {
    'mbti': [
        {
            "id": 1,
            "content": "在社交场合中，你更倾向于",
            "option_a": "主动与他人交谈",
            "option_b": "等待他人来交谈",
            "dimension_a": "E",
            "dimension_b": "I"
        }
    ],
    'career': [
        {
            "id": 1,
            "content": "我喜欢组织和领导团队",
            "category": "管理,领导"
        }
    ],
    'enneagram': [
        {
            "id": 1,
            "content": "我经常追求完美",
            "category": "1"
        }
    ]
}

def get_test_questions(test_type):
    """生成测试题目"""
    client = create_llm_client('deepseek')
    
    prompt = f"""请生成30个全新的、独特的{test_type.upper()}测试题目，要求：
1. 每个问题都要有独特的视角和内容
2. 避免使用常见或重复的表述
3. 确保问题覆盖{test_type.upper()}测试的所有维度
4. 使用多样化的场景和情境

请严格按照以下格式生成，直接返回JSON数组：
示例格式：
{json.dumps(EXPECTED_FORMAT[test_type], ensure_ascii=False, indent=2)}

要求：
1. 只返回JSON数组，不要包含其他文字
2. 确保生成30个不同的题目
3. 格式必须与示例完全一致
4. {TEST_PROMPTS[test_type]}

注意：每次生成的题目都应该是独特的，不要重复之前的内容。"""
    
    # 添加随机性提示
    messages = [
        {
            "role": "system", 
            "content": f"你是一个专业的{test_type.upper()}测试题目生成器。每次都要生成独特的、富有创意的题目，避免重复和套路化。当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        },
        {
            "role": "user", 
            "content": prompt
        }
    ]
    
    response = client.get_completion(messages)
    
    # 保存响应到题库文件
    save_deepseek_response(test_type, response)
    
    try:
        # 提取JSON
        start = response.find('[')
        end = response.rfind(']') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            raw_questions = json.loads(json_str)
            
            # 转换为对应的数据结构
            if test_type == 'mbti':
                questions = TestGenerator.format_mbti_questions(raw_questions)
            else:
                questions = TestGenerator.format_other_questions(raw_questions)
            
            return {
                'test_type': test_type,
                'total': len(questions),
                'questions': [q.__dict__ for q in questions]
            }
            
        raise ValueError("无法在响应中找到有效的JSON数组")
        
    except Exception as e:
        logger.error(f"处理题目时出错: {str(e)}")
        logger.error(f"原始响应: {response}")
        raise ValueError("生成题目失败，请重试")

def get_test_from_bank(test_type: str):
    """
    从题库中读取测试题目
    
    @param test_type: 测试类型 (mbti/career/enneagram)
    @return: 最新的测试题目
    """
    # 获取题库目录
    question_bank_dir = os.path.join("question_bank", test_type)
    if not os.path.exists(question_bank_dir):
        raise ValueError(f"题库 {test_type} 不存在")
    
    # 获取最新的题库文件
    files = os.listdir(question_bank_dir)
    if not files:
        raise ValueError(f"题库 {test_type} 中没有题目")
    
    # 按文件名排序（因为包含时间戳）
    files.sort(reverse=True)
    latest_file = os.path.join(question_bank_dir, files[0])
    
    # 计算文件名的MD5值
    filename_md5 = hashlib.md5(files[0].encode('utf-8')).hexdigest()
    
    # 读取文件内容
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取JSON部分
    try:
        # 查找格式化的JSON部分（在"# 格式化的 JSON:"之后）
        formatted_json_marker = "# 格式化的 JSON:\n"
        json_start = content.find(formatted_json_marker)
        
        if json_start >= 0:
            # 使用格式化的JSON部分
            json_content = content[json_start + len(formatted_json_marker):]
            raw_questions = json.loads(json_content)
        else:
            # 回退到查找第一个JSON数组
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                raw_questions = json.loads(json_str)
            else:
                raise ValueError("无法在文件中找到有效的JSON")
        
        # 转换为对应的数据结构
        if test_type == 'mbti':
            questions = TestGenerator.format_mbti_questions(raw_questions)
        else:
            questions = TestGenerator.format_other_questions(raw_questions)
        
        return {
            'test_type': test_type,
            'total': len(questions),
            'questions': [q.__dict__ for q in questions],
            'file_id': filename_md5  # 添加加密后的文件名
        }
        
    except Exception as e:
        logger.error(f"处理题目时出错: {str(e)}")
        logger.error(f"文件路径: {latest_file}")
        logger.error(f"文件内容: {content}")
        raise ValueError(f"读取题库失败: {str(e)}")

def analyze_test_result(test_type: str, file_id: str, answers: list):
    """
    分析测试结果
    
    @param test_type: 测试类型 (mbti/career/enneagram)
    @param file_id: 文件MD5值
    @param answers: 答案列表
    @return: 分析结果
    """
    # 获取题库目录
    question_bank_dir = os.path.join("question_bank", test_type)
    if not os.path.exists(question_bank_dir):
        raise ValueError(f"题库 {test_type} 不存在")
    
    # 查找对应的文件
    target_file = None
    for filename in os.listdir(question_bank_dir):
        if hashlib.md5(filename.encode('utf-8')).hexdigest() == file_id:
            target_file = os.path.join(question_bank_dir, filename)
            break
    
    if not target_file:
        raise ValueError(f"找不到对应的题目文件")
    
    # 读取题目文件
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取题目
    formatted_json_marker = "# 格式化的 JSON:\n"
    json_start = content.find(formatted_json_marker)
    
    if json_start >= 0:
        json_content = content[json_start + len(formatted_json_marker):]
        questions = json.loads(json_content)
    else:
        start = content.find('[')
        end = content.rfind(']') + 1
        if start >= 0 and end > start:
            questions = json.loads(content[start:end])
        else:
            raise ValueError("无法解析题目文件")
    
    # 构建分析提示词
    if test_type == 'mbti':
        analysis_prompt = construct_mbti_analysis(questions, answers)
    elif test_type == 'career':
        analysis_prompt = construct_career_analysis(questions, answers)
    else:  # enneagram
        analysis_prompt = construct_enneagram_analysis(questions, answers)
    
    # 调用DeepSeek进行分析
    client = create_llm_client('deepseek')
    print(type(client))
    response = client.get_completion([
        {
            "role": "system",
            "content": f"你是一个专业的{test_type.upper()}测试分析师，请根据用户的答案提供专业、详细的分析。"
        },
        {
            "role": "user",
            "content": analysis_prompt
        }
    ])
    
    return {
        'test_type': test_type,
        'file_id': file_id,
        'analysis': response
    }

def construct_mbti_analysis(questions, answers):
    """构建MBTI分析提示词"""
    # 统计各维度得分
    dimensions = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    answer_details = []
    for answer in answers:
        q_id = answer['questionId']
        q_answer = answer['answer']
        question = next(q for q in questions if q['id'] == q_id)
        
        if q_answer == 'A':
            dimensions[question['dimension_a']] += 1
            selected_option = question['option_a']
        else:
            dimensions[question['dimension_b']] += 1
            selected_option = question['option_b']
            
        answer_details.append(f"问题{q_id}: {question['content']}\n选择: {selected_option}")
    
    mbti_type = ''
    mbti_type += 'E' if dimensions['E'] > dimensions['I'] else 'I'
    mbti_type += 'S' if dimensions['S'] > dimensions['N'] else 'N'
    mbti_type += 'T' if dimensions['T'] > dimensions['F'] else 'F'
    mbti_type += 'J' if dimensions['J'] > dimensions['P'] else 'P'
    
    return f"""请分析以下MBTI测试结果：

测试结果: {mbti_type}

维度得分:
E/I: E({dimensions['E']}) - I({dimensions['I']})
S/N: S({dimensions['S']}) - N({dimensions['N']})
T/F: T({dimensions['T']}) - F({dimensions['F']})
J/P: J({dimensions['J']}) - P({dimensions['P']})

详细答题记录:
{chr(10).join(answer_details)}

请提供:
1. 性格类型的详细解释
2. 主要性格特征
3. 职业发展建议
4. 人际关系建议
5. 个人成长建议"""

def construct_career_analysis(questions, answers):
    """构建职业倾向分析提示词"""
    answer_details = []
    career_types = {}
    
    for answer in answers:
        q_id = answer['questionId']
        q_answer = answer['answer']
        question = next(q for q in questions if q['id'] == q_id)
        
        # 计算分数（A=1, B=2, C=3, D=4, E=5）
        score = ord(q_answer) - ord('A') + 1
        
        # 统计职业类型
        categories = question['category'].split(',')
        for category in categories:
            career_types[category] = career_types.get(category, 0) + score
            
        answer_details.append(f"问题{q_id}: {question['content']}\n选择: {q_answer}（{score}分）")
    
    return f"""请分析以下职业倾向测试结果：

职业类型得分:
{chr(10).join(f'{k}: {v}分' for k, v in career_types.items())}

详细答题记录:
{chr(10).join(answer_details)}

请提供:
1. 最适合的职业方向（前三个）
2. 职业优势分析
3. 职业发展建议
4. 需要提升的能力
5. 职业规划建议"""

def construct_enneagram_analysis(questions, answers):
    """构建九型人格分析提示词"""
    type_scores = {str(i): 0 for i in range(1, 10)}
    answer_details = []
    
    for answer in answers:
        q_id = answer['questionId']
        q_answer = answer['answer']
        question = next(q for q in questions if q['id'] == q_id)
        
        # 计算分数（A=5, B=4, C=3, D=2, E=1）
        score = 5 - (ord(q_answer) - ord('A'))
        type_scores[question['category']] += score
        
        answer_details.append(f"问题{q_id}: {question['content']}\n选择: {q_answer}（{score}分）")
    
    # 找出得分最高的类型
    main_type = max(type_scores.items(), key=lambda x: x[1])[0]
    
    return f"""请分析以下九型人格测试结果：

各类型得分:
{chr(10).join(f'类型{k}: {v}分' for k, v in type_scores.items())}

主要类型: {main_type}

详细答题记录:
{chr(10).join(answer_details)}

请提供:
1. 主要人格类型的详细解释
2. 核心特质和行为模式
3. 个人成长方向
4. 人际关系建议
5. 压力管理建议""" 
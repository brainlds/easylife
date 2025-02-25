from flask import Blueprint, request, jsonify, send_file
from app.utils.llm_helper import get_chat_response
from app.utils.test_helper import get_test_questions, get_test_from_bank, analyze_test_result
import logging
import os
import base64
from volcenginesdkarkruntime import Ark
from app.utils.numerology.bazi import BaziPlannerChain
from pathlib import Path
from app.routes.config import SCRIPT_DIR
# 配置日志
logger = logging.getLogger(__name__)

# 可以选择更新蓝图名称
api_bp = Blueprint('api', __name__)  # 更新蓝图名称

# 初始化大模型客户端
client = Ark(api_key=os.getenv('ARK_API_KEY'),base_url="https://ark.cn-beijing.volces.com/api/v3",)




@api_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    data = request.get_json()
    user_question = data.get('question')
    provider = data.get('provider', 'openai')  # 默认使用OpenAI
    
    if not user_question:
        return jsonify({
            'success': False,
            'error': '请提供问题内容',
            'code': 500
        }), 400
        
    ai_response = get_chat_response(user_question, provider)
    return jsonify({
        'success': True,
        'response': ai_response,
        'code': 200
    })

@api_bp.route('/generate-test', methods=['POST'])
def generate_test():
    """生成心理测试题目"""
    data = request.get_json()
    test_type = data.get('test_type')  # mbti, career, enneagram
    
    if not test_type:
        return jsonify({
            'success': False,
            'error': '请指定测试类型',
            'code': 500
        }), 400
    
    # 生成测试题目
    test_questions = get_test_questions(test_type)
    
    return jsonify({
        'success': True,
        'code': 200,
        'data': {
            'test_type': test_type,
            'questions': test_questions
        }
    })

@api_bp.route('/test', methods=['GET'])
def get_test():
    """获取测试题目"""
    test_type = request.args.get('type')
    
    if not test_type:
        return jsonify({
            'success': False,
            'error': '请指定测试类型',
            'code': 500
        }), 400
        
    if test_type not in ['mbti', 'career', 'enneagram']:
        return jsonify({
            'success': False,
            'error': '不支持的测试类型',
            'code': 500
        }), 400
    
    try:
        # 从题库中获取题目
        test_questions = get_test_from_bank(test_type)
        
        return jsonify({
            'success': True,
            'code': 200,
            'data': test_questions
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 400

@api_bp.route('/test/submit', methods=['POST'])
def submit_test():
    """提交测试答案并获取分析结果"""
    # 添加请求数据验证
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': '请求必须是JSON格式',
            'code': 400
        }), 400
        
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '请求体不能为空',
            'code': 400
        }), 400
    
    test_type = data.get('test_type')
    file_id = data.get('file_id')
    answers = data.get('answers')
    
    if not all([test_type, file_id, answers]):
        return jsonify({
            'success': False,
            'error': '缺少必要参数',
            'code': 400
        }), 400
    
    try:
        # 分析测试结果
        result = analyze_test_result(test_type, file_id, answers)
        
        return jsonify({
            'success': True,
            'code': 200,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 400
        }), 400

@api_bp.route('/photo-qa', methods=['POST'])
def photo_qa():
    """处理图片问答请求"""
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'message': '无效的图片格式或缺少图片'
        }), 400

    image_file = request.files['image']

    # 验证图片格式
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    if not image_file.filename or '.' not in image_file.filename:
        return jsonify({
            'success': False,
            'message': '无效的图片格式'
        }), 400
        
    file_ext = image_file.filename.rsplit('.', 1)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            'success': False,
            'message': f'不支持的图片格式，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    # 限制图片大小（例如：最大5MB）
    if image_file.content_length > 5 * 1024 * 1024:
        return jsonify({
            'success': False,
            'message': '图片大小超过限制（最大5MB）'
        }), 400

    # 读取图片并转换为Base64编码
    image_data = image_file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    # 根据文件扩展名确定MIME类型
    mime_type = f"image/{file_ext}"
    # 调用大模型进行处理
    response = client.chat.completions.create(
        model="ep-20241229173403-qs5cx",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "根据华为公司的企业文化，选择图片中的选项，每一道题都返回一个最符合，和最不符的选项。返回格式为：{最符合的选项：，最不符合的选项：}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
    )

    # 处理模型响应
    if response.choices:
        question = response.choices[0].message.content
        answer = response.choices[0].message.content

        return jsonify({
            'success': True,
            'message': '处理成功',
            'data': {
                'question': question,
                'answer': answer
            }
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '未能生成有效的回答'
        }), 500

@api_bp.route('/bazi/analyze', methods=['POST'])
def analyze_bazi():
    """
    根据用户提供的生辰信息进行八字命理分析。
    
    @return: JSON 命理分析结果
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空',
                'code': 400
            }), 400

        # 验证必要字段
        required_fields = ['birth_time', 'birth_place']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要字段: {field}',
                    'code': 400
                }), 400

        # 创建 BaziPlannerChain 实例
        bazi_planner = BaziPlannerChain()

        # 进行命理分析
        analysis_result = bazi_planner.analyze_bazi(data)

        # 检查分析结果是否为 None
        if analysis_result is None:
            return jsonify({
                'success': False,
                'error': '命理分析失败，未返回有效结果',
                'code': 500
            }), 500

        return jsonify({
            'success': True,
            'code': 200,
            'data': analysis_result 
        })

    except Exception as e:
        logger.error(f"命理分析失败: {str(e)}")
        logger.error("详细错误信息: ", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'命理分析失败: {str(e)}',
            'code': 500
        }), 500 

@api_bp.route('/scripts', methods=['GET'])
def list_scripts():
    """
    获取 data/script 目录下的文件列表
    
    @return: JSON 格式的文件列表
    """
    try:
        # 获取 data/script 目录的绝对路径
        script_dir = Path(SCRIPT_DIR)
        print(script_dir)
        # 确保目录存在
        if not script_dir.exists():
            return jsonify({
                'success': False,
                'error': '脚本目录不存在',
                'code': 404
            }), 404

        # 获取文件列表
        files = []
        for file_path in script_dir.glob('*'):
            if file_path.is_file():  # 只列出文件，不包括目录
                files.append({
                    #文件名的前缀
                    'prefix': file_path.name.split('.')[0],
                    'size': file_path.stat().st_size,  # 文件大小（字节）
                    'modified_time': file_path.stat().st_mtime,  # 最后修改时间
                })

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'total': len(files),
                'files': files
            }
        })

    except Exception as e:
        logger.error(f"获取脚本列表失败: {str(e)}")
        logger.error("详细错误信息: ", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'获取脚本列表失败: {str(e)}',
            'code': 500
        }), 500 

@api_bp.route('/scripts/download/<prefix>', methods=['GET'])
def download_script(prefix):
    """
    根据文件前缀下载对应的脚本文件
    
    @param prefix: 文件前缀
    @return: 文件下载响应
    """
    try:
        # 获取 data/script 目录的绝对路径
        script_dir = Path(SCRIPT_DIR)
        
        # 确保目录存在
        if not script_dir.exists():
            return jsonify({
                'success': False,
                'error': '脚本目录不存在',
                'code': 404
            }), 404

        # 查找匹配前缀的文件
        matching_files = list(script_dir.glob(f'{prefix}*'))
        
        # 如果没有找到匹配的文件
        if not matching_files:
            return jsonify({
                'success': False,
                'error': f'未找到前缀为 {prefix} 的文件',
                'code': 404
            }), 404

        # 获取第一个匹配的文件
        file_path = matching_files[0]
        
        # 检查文件是否存在且可读
        if not file_path.is_file():
            return jsonify({
                'success': False,
                'error': '文件不存在或不可访问',
                'code': 404
            }), 404

        try:
            # 发送文件
            return send_file(
                file_path,
                as_attachment=True,  # 作为附件下载
                download_name=file_path.name,  # 使用原始文件名
                mimetype='application/octet-stream'  # 使用通用的二进制流类型
            )
            
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '文件下载失败',
                'code': 500
            }), 500

    except Exception as e:
        logger.error(f"处理下载请求失败: {str(e)}")
        logger.error("详细错误信息: ", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'处理下载请求失败: {str(e)}',
            'code': 500
        }), 500 
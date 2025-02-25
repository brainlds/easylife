# from flask import Blueprint, request, jsonify
# from app.utils.llm_helper import get_chat_response
# from app.utils.test_helper import get_test_questions, get_test_from_bank, analyze_test_result  # 直接从test_helper导入
# import logging

# # 配置日志
# logger = logging.getLogger(__name__)

# chat_bp = Blueprint('chat', __name__)

# @chat_bp.route('/chat', methods=['POST'])
# def chat():
#     """处理聊天请求"""
#     data = request.get_json()
#     user_question = data.get('question')
#     provider = data.get('provider', 'openai')  # 默认使用OpenAI
    
#     if not user_question:
#         return jsonify({
#             'success': False,
#             'error': '请提供问题内容',
#             'code': 500
#         }), 400
        
#     ai_response = get_chat_response(user_question, provider)
#     return jsonify({
#         'success': True,
#         'response': ai_response,
#         'code': 200
#     })

# @chat_bp.route('/generate-test', methods=['POST'])
# def generate_test():
#     """生成心理测试题目"""
#     data = request.get_json()
#     test_type = data.get('test_type')  # mbti, career, enneagram
    
#     if not test_type:
#         return jsonify({
#             'success': False,
#             'error': '请指定测试类型',
#             'code': 500
#         }), 400
    
#     # 生成测试题目
#     test_questions = get_test_questions(test_type)
    
#     return jsonify({
#         'success': True,
#         'code': 200,
#         'data': {
#             'test_type': test_type,
#             'questions': test_questions
#         }
#     })

# @chat_bp.route('/test', methods=['GET'])
# def get_test():
#     """获取测试题目"""
#     test_type = request.args.get('type')
    
#     if not test_type:
#         return jsonify({
#             'success': False,
#             'error': '请指定测试类型',
#             'code': 500
#         }), 400
        
#     if test_type not in ['mbti', 'career', 'enneagram']:
#         return jsonify({
#             'success': False,
#             'error': '不支持的测试类型',
#             'code': 500
#         }), 400
    
#     try:
#         # 从题库中获取题目
#         test_questions = get_test_from_bank(test_type)
        
#         return jsonify({
#             'success': True,
#             'code': 200,
#             'data': test_questions
#         })
        
#     except ValueError as e:
#         return jsonify({
#             'success': False,
#             'error': str(e),
#             'code': 500
#         }), 400

# @chat_bp.route('/test/submit', methods=['POST'])
# def submit_test():
#     """提交测试答案并获取分析结果"""
#     # 添加请求数据验证
#     if not request.is_json:
#         return jsonify({
#             'success': False,
#             'error': '请求必须是JSON格式',
#             'code': 400
#         }), 400
        
#     data = request.get_json()
#     if not data:
#         return jsonify({
#             'success': False,
#             'error': '请求体不能为空',
#             'code': 400
#         }), 400
    
#     test_type = data.get('test_type')
#     file_id = data.get('file_id')
#     answers = data.get('answers')
    
#     if not all([test_type, file_id, answers]):
#         return jsonify({
#             'success': False,
#             'error': '缺少必要参数',
#             'code': 400
#         }), 400
    
#     try:
#         # 分析测试结果
#         result = analyze_test_result(test_type, file_id, answers)
        
#         return jsonify({
#             'success': True,
#             'code': 200,
#             'data': result
#         })
        
#     except ValueError as e:
#         return jsonify({
#             'success': False,
#             'error': str(e),
#             'code': 400
#         }), 400 
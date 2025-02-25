from flask import Blueprint, request, jsonify
from app.utils.customer_bot import CustomerSupportBot
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
cs_bp = Blueprint('customer_service', __name__)

# 初始化机器人实例
bot = CustomerSupportBot()

@cs_bp.route('/chat', methods=['POST'])
def chat():
    """处理客服对话请求"""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': '请求必须是JSON格式',
            'code': 400
        }), 400
        
    data = request.get_json()
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({
            'success': False,
            'error': '消息内容不能为空',
            'code': 400
        }), 400
    
    try:
        response = bot.handle_query(user_input)
        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'response': response
            }
        })
        
    except Exception as e:
        logger.error(f"处理对话请求时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': '处理请求失败',
            'code': 500
        }), 500 
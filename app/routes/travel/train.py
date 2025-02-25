from flask import Blueprint, jsonify, request
from app.utils.train_service import TrainService
import logging

logger = logging.getLogger(__name__)
train_bp = Blueprint('train', __name__)
train_service = TrainService()

@train_bp.route('/api/train/tickets', methods=['GET'])
def get_train_tickets():
    """获取火车票信息"""
    try:
        # 获取请求参数
        start = request.args.get('start')
        end = request.args.get('end')
        date = request.args.get('date')
        
        # 参数验证
        if not all([start, end, date]):
            return jsonify({
                "success": False,
                "error": "缺少必要参数"
            }), 400
            
        # 查询火车票
        result = train_service.get_train_tickets(start, end, date)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取火车票信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": "获取火车票信息失败"
        }), 500 
from flask import Blueprint, request, jsonify, render_template
from app.utils.travel.planner_chain import TravelPlannerChain
from app.utils.weather_service import WeatherService
import logging

logger = logging.getLogger(__name__)

travel_bp = Blueprint('travel', __name__)

@travel_bp.route('/plan', methods=['POST'])
def create_travel_plan():
    """创建旅行计划"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = [
            'departure', 'destination', 'start_date', 'end_date', 
            'travelers', 'budget'
        ]
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': '缺少必要参数',
                'code': 400
            }), 400
            
        # 创建旅行计划
        planner = TravelPlannerChain()
        plan = planner.create_plan(data)
        
        return jsonify({
            'success': True,
            'data': plan,
            'code': 200
        })
        
    except Exception as e:
        logger.error(f"创建旅行计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500

@travel_bp.route('/purchase', methods=['POST'])
def purchase():
    """处理购买请求"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['tickets', 'activities', 'totalCost']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': '缺少必要参数',
                'code': 400
            }), 400
        
        # 计算总花费
        total_cost = data['totalCost']
        activities = data['activities']
        
        # 这里可以进行更多的验证和处理，例如检查活动的有效性等
        
        # 返回响应，指示前端跳转到支付页面
        return jsonify({
            'success': True,
            'message': '购买成功，跳转到支付页面',
            'totalCost': total_cost,
        }), 200
        
    except Exception as e:
        logger.error(f"处理购买请求失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '处理购买请求失败',
            'code': 500
        }), 500


@travel_bp.route('/weather', methods=['GET'])
def get_weather():
    """测试天气服务"""
    try:
        city = request.args.get('city', '北京')  # 默认城市为北京
        days = int(request.args.get('days', 3))  # 默认3天
        
        weather_service = WeatherService()
        weather_info = weather_service.get_weather_forecast(city, days)
        
        return jsonify({
            'success': True,
            'data': {
                'city': city,
                'days': days,
                'weather': weather_info
            },
            'code': 200
        })
        
    except Exception as e:
        logger.error(f"获取天气信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500 
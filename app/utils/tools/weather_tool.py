from langchain.tools import BaseTool
from app.utils.weather_service import WeatherService
from typing import Optional, Type, Any
from datetime import datetime

class WeatherTool(BaseTool):
    """天气查询工具"""
    
    name: str = "weather_service"
    description: str = """用于查询指定城市的天气预报。
    输入参数需要是一个JSON字符串，包含city(城市名)和days(天数)。
    例如: {"city": "北京", "days": 3}
    返回该城市未来几天的天气预报。"""
    
    weather_service: Any = None
    
    def __init__(self):
        super().__init__()
        self.weather_service = WeatherService()

    def _run(self, query: str) -> str:
        """运行工具"""
        try:
            # 解析输入参数
            params = eval(query)
            city = params.get("city", "")
            days = int(params.get("days", 3))
            
            # 获取天气预报
            return self.weather_service.get_weather_forecast(city, days)
            
        except Exception as e:
            return f"天气查询失败: {str(e)}"

    async def _arun(self, query: str) -> str:
        """异步运行（可选）"""
        raise NotImplementedError("WeatherTool 暂不支持异步操作") 
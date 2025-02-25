import requests
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class WeatherService:
    """高德天气服务"""
    
    def __init__(self):
        self.api_key = os.getenv("AMAP_API_KEY")
        self.base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        self.city_codes = self._load_city_codes()
        
    def _load_city_codes(self) -> Dict[str, str]:
        """从Excel文件加载城市编码"""
        try:
            # 获取 app 目录
            app_dir = Path(__file__).parent.parent
            excel_path = app_dir / "data" / "AMap_adcode_citycode.xlsx"
            
            logger.info(f"尝试读取城市编码文件: {excel_path}")
            
            # 读取Excel文件
            df = pd.read_excel(excel_path)
            
            # 创建城市编码字典 {城市名: adcode}
            city_codes = {}
            for _, row in df.iterrows():
                city_name = row['中文名']  # 根据实际列名调整
                adcode = str(row['adcode'])  # 确保是字符串格式
                city_codes[city_name] = adcode
                
            logger.info(f"成功加载 {len(city_codes)} 个城市编码")
            return city_codes
            
        except Exception as e:
            logger.error(f"加载城市编码失败: {str(e)}")
            # 返回基本城市编码作为后备
            return {
                "城市错误": "00"
            }
        
    def get_weather_forecast(self, city: str, days: int = 3) -> str:
        """获取天气预报"""
        try:
            # 获取城市编码
            city_code = self.city_codes.get(city)
            if not city_code:
                logger.warning(f"未找到城市编码: {city}")
                return "天气状况未知"
            
            # 获取实时天气
            params = {
                "key": self.api_key,
                "city": city_code,
                "extensions": "all"
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data["status"] != "1":
                logger.error(f"天气API错误: {data['info']}")
                return "天气状况未知"
            
            # 格式化天气信息
            forecasts = data["forecasts"][0]["casts"]
            weather_info = []
            
            for i, day in enumerate(forecasts[:days]):
                try:
                    date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                    weather_info.append(
                        f"{date}: {day['dayweather']}转{day['nightweather']}，"
                        f"气温 {day['nighttemp']}-{day['daytemp']}℃，"
                        f"{day['daywind']}风{day['daypower']}级"
                    )
                except Exception as e:
                    logger.error(f"处理天气数据失败: {str(e)}")
                    weather_info.append(f"{date}: 天气状况未知")
            
            return "\n".join(weather_info)
            
        except Exception as e:
            logger.error(f"获取天气预报失败: {str(e)}")
            return "天气状况未知"
    
    def _get_city_code(self, city: str) -> str:
        """获取城市编码"""
        try:
            # 地理编码API
            geo_url = "https://restapi.amap.com/v3/geocode/geo"
            params = {
                "key": self.api_key,
                "address": city
            }
            
            response = requests.get(geo_url, params=params)
            data = response.json()
            
            if data["status"] == "1" and data["geocodes"]:
                return data["geocodes"][0]["adcode"]
            return ""
            
        except Exception as e:
            logger.error(f"获取城市编码失败: {str(e)}")
            return ""
    
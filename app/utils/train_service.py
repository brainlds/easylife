import requests
import os
import ssl
import logging
from typing import Dict
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class TrainService:
    """火车票查询服务"""
    
    def __init__(self):
        self.api_key = os.getenv("JISU_API_KEY")
        if not self.api_key:
            logger.error("未找到 JISU_API_KEY 环境变量")
            raise ValueError("Missing JISU_API_KEY environment variable")
            
        self.host = 'https://jisutrain.market.alicloudapi.com'
        self.path = '/train/ticket'
        
    def get_train_tickets(self, start: str, end: str, date: str) -> Dict:
        """查询火车票信息"""
        try:
            # 准备查询参数
            query_params = {
                'date': date,
                'start': start,
                'end': end
            }
            
            # 构建URL
            url = f"{self.host}{self.path}?{urlencode(query_params)}"
            
            # 准备请求头
            headers = {
                'Authorization': 'APPCODE ' + self.api_key.strip(),
                'Content-Type': 'application/json; charset=UTF-8'
            }
            
            # 记录请求信息
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            
            # 创建SSL上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 发送请求
            response = requests.get(
                url,
                headers=headers,
                verify=False,  # 禁用SSL验证
                timeout=10  # 设置超时时间
            )
            
            # 记录响应信息
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {response.headers}")
            logger.debug(f"响应内容: {response.text[:200]}...")
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if data["status"] == 0:  # 成功
                return {
                    "success": True,
                    "data": self._process_train_data(data["result"])
                }
            else:
                logger.error(f"查询火车票失败: {data.get('msg', '未知错误')}")
                return {
                    "success": False,
                    "error": data.get('msg', '查询失败')
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求失败: {str(e)}")
            return {
                "success": False,
                "error": f"请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"查询火车票出错: {str(e)}")
            return {
                "success": False,
                "error": "查询火车票时发生错误"
            }
            
    def _process_train_data(self, result: Dict) -> Dict:
        """处理火车票数据"""
        processed_data = {
            "start": result["start"],
            "end": result["end"],
            "date": result["date"],
            "trains": []
        }
        
        for train in result["list"]:
            # 处理座位价格和余票
            seats = []
            seat_types = {
                ("二等座", "ed"): "二等座",
                ("一等座", "yd"): "一等座",
                ("商务座", "sw"): "商务座",
                ("特等座", "td"): "特等座",
                ("软座", "rz"): "软座",
                ("硬座", "yz"): "硬座",
                ("高级软卧", "gr1"): "高级软卧",
                ("软卧", "rw1"): "软卧",
                ("硬卧", "yw1"): "硬卧",
                ("无座", "wz"): "无座"
            }
            
            for (seat_name, code), type_name in seat_types.items():
                price = train.get(f"price{code}", "-")
                if price != "-":
                    seats.append({
                        "type": type_name,
                        "price": float(price),
                        "available": train.get(f"num{code}") not in ["-", "无"]
                    })
            
            processed_train = {
                "train_no": train["trainno"],
                "type": train["typename"],
                "departure_station": train["station"],
                "arrival_station": train["endstation"],
                "departure_time": train["departuretime"],
                "arrival_time": train["arrivaltime"],
                "duration": train["costtime"],
                "seats": seats,
                "can_buy": train["canbuy"] == "Y"
            }
            
            processed_data["trains"].append(processed_train)
            
        return processed_data 
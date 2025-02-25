from typing import Type, Optional, Dict, Any
from langchain.tools import BaseTool
from app.utils.train_service import TrainService
from pydantic import Field
import json

class TrainTool(BaseTool):
    """火车票查询工具"""
    
    name: str = "train_ticket_search"
    description: str = """用于查询两个城市之间的火车票信息。
    输入必须是一个JSON字符串，包含以下字段：
    {
        "start": "出发城市",
        "end": "到达城市",
        "date": "出发日期(YYYY-MM-DD格式)"
    }
    返回火车票信息，包括车次、发车时间、到达时间、票价等。
    """
    
    # 添加 train_service 字段定义
    train_service: TrainService = Field(default_factory=TrainService)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _run(self, query: str) -> str:
        """
        执行火车票查询
        
        Args:
            query: JSON格式的查询参数
            
        Returns:
            str: 查询结果的文本描述
        """
        try:
            # 解析输入参数
            params = json.loads(query)
            
            # 验证必要参数
            required_fields = ["start", "end", "date"]
            if not all(field in params for field in required_fields):
                return "请提供完整的查询参数：出发城市、到达城市和出发日期"
            
            # 查询火车票
            result = self.train_service.get_train_tickets(
                params["start"],
                params["end"],
                params["date"]
            )
            
            if not result["success"]:
                return f"查询失败: {result.get('error', '未知错误')}"
            
            # 格式化输出
            return self._format_train_info(result["data"])
            
        except json.JSONDecodeError:
            return "输入参数格式错误，请提供正确的JSON格式"
        except Exception as e:
            return f"查询过程中出现错误: {str(e)}"
    
    def _format_train_info(self, data: Dict) -> str:
        """格式化火车票信息，使其更加人性化并结合天气"""
        trains = data["trains"]
        if not trains:
            return "抱歉，没有找到符合条件的车次"
        
        # 按发车时间排序
        trains.sort(key=lambda x: x["departure_time"])
        
        output = [f"为您找到从{data['start']}到{data['end']}的{len(trains)}个车次（{data['date']}）：\n"]
        
        for train in trains:
            # 基本信息
            train_info = [
                f"{train['type']}车次{train['train_no']}",
                f"从{train['departure_station']}出发（{train['departure_time']}）",
                f"到达{train['arrival_station']}（{train['arrival_time']}）",
                f"全程{train['duration']}"
            ]
            
            # 座位信息
            available_seats = []
            for seat in train["seats"]:
                if seat["available"]:
                    available_seats.append(f"{seat['type']}（¥{seat['price']}）")
            
            # 组合信息
            output.append(" | ".join(train_info))
            if available_seats:
                output.append(f"可选座位: {' / '.join(available_seats)}")
            else:
                output.append("温馨提示：当前车次暂无可预订座位")
            output.append("------------------------")
        
        return "\n".join(output) 
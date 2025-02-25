from langchain.tools import BaseTool
import json
from typing import Dict, List

class CalculatorTool(BaseTool):
    """计算工具"""
    
    name: str = "calculator"
    description: str = """用于计算旅行费用。
    输入必须是一个JSON字符串，包含以下字段：
    {
        "daily_costs": [每日花费列表],
        "operation": "sum"  # 当前仅支持sum操作
    }
    返回计算结果。
    """
    
    def _run(self, query: str) -> str:
        """执行计算"""
        try:
            data = json.loads(query)
            if data["operation"] == "sum":
                total = sum(data["daily_costs"])
                return str(total)
            return "不支持的操作类型"
            
        except json.JSONDecodeError:
            return "输入格式错误，请提供正确的JSON格式"
        except Exception as e:
            return f"计算过程中出现错误: {str(e)}" 
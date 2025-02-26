from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.utils.llm_clients import create_llm_client  # 导入 llm_clients
from typing import List, Dict
import logging
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from app.utils.tools.weather_tool import WeatherTool
from app.utils.tools.train_tool import TrainTool
from app.utils.tools.calculator_tool import CalculatorTool

logger = logging.getLogger(__name__)

class DailyActivity(BaseModel):
    """每日活动模型"""
    time: str = Field(description="活动时间段")
    activity_type: str = Field(description="活动类型：景点/餐饮/交通/住宿")
    name: str = Field(description="活动名称")
    description: str = Field(description="活动描述")
    weather_notice: str = Field(description="天气建议")
    cost: float = Field(description="预计花费")
    content: str = Field(description="""活动的完整描述，要求：

        1. 结合天气情况给出合理建议

        2. 使用自然、流畅的语言

        3. 根据活动类型提供不同的描述风格：

           - 交通类：说明出发时间、耗时、费用，结合天气给出出行建议

           - 景点类：描述天气是否适合游玩，介绍景点特色，说明费用

           - 餐饮类：推荐特色美食，说明价格，结合天气给出就餐建议

           - 住宿类：介绍住宿条件，说明价格，提供入住建议

        

        示例：

        - 交通："今天下午有小雨，建议您提前出发。下午3点的G32次高铁从杭州东站出发，约4.5小时可到达北京南站，二等座票价1947元。"

        - 景点："天气晴朗，非常适合户外活动！下午1点前往龙井村，您可以漫步在茶园间，品尝正宗龙井茶，体验江南茶文化，门票100元。"

        - 餐饮："今晚天气转凉，很适合来一顿暖身的火锅。晚上6点在知味观品尝杭州特色火锅，推荐尝试西湖藕粉和龙井虾仁，人均150元。"

        - 住宿："夜间可能有雨，已为您预订了交通便利的星级酒店。入住西湖边的杭州大酒店，享受湖景房，含双早，498元/晚。"

    """)

class DailyPlan(BaseModel):
    """每日计划模型"""
    date: str = Field(description="日期")
    weather: str = Field(description="天气情况")
    activities: List[DailyActivity] = Field(description="当日活动列表")
    daily_cost: float = Field(description="当日总花费")

class TravelPlan(BaseModel):
    """旅行计划模型"""
    departure: str = Field(description="出发地")
    destination: str = Field(description="目的地")
    duration: int = Field(description="行程天数")
    budget: float = Field(description="预算")
    total_cost: float = Field(description="实际花费")
    daily_plans: List[DailyPlan] = Field(description="每日计划")
    travel_style: str = Field(description="旅行风格")
    accommodation_level: str = Field(description="住宿等级")
    summary: str = Field(description="旅行总结，类似小红书风格的文案，包含吸引人的标题、亮点描述和实用建议")

class TravelActivity(BaseModel):
    """
    @description 旅行活动数据模型
    """
    activity_type: str = Field(description="活动类型，如'景点'、'餐饮'等")
    name: str = Field(description="地点名称")
    time: str = Field(description="活动时间，格式为HH:MM")
    description: str = Field(description="活动描述")
    cost: float = Field(description="预计花费")
    weather_notice: str = Field(description="天气提醒")

class TravelPlannerChain:
    """旅行规划链"""
    def __init__(self):
        self.llm = create_llm_client("deepseek")
        self.output_parser = JsonOutputParser(pydantic_object=TravelPlan)
        
        # 创建工具列表
        self.tools = [WeatherTool(), TrainTool(), CalculatorTool()]
        
        # 创建 Agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的中国旅行规划师。
            
            1. 在制定旅行计划时，你可以：
               - 使用天气查询工具来获取目的地的天气情况
               - 使用火车票查询工具来查询交通信息
               - 使用计算工具来计算费用
               - 需要考虑出发返回的交通时间和车票价格
            
            2. 费用计算规则（必须严格执行）：
               a. 每个活动必须设置合理的 cost 值
               
               b. 计算每日总花费(daily_cost)：
                  - 收集当日所有活动的 cost
                  - 使用 calculator 工具计算总和
                  示例：
                  ```
                  # 假设某天有4个活动：
                  活动1: cost = 1947（交通）
                  活动2: cost = 450（餐饮）
                  活动3: cost = 0（景点）
                  活动4: cost = 498（住宿）
                  
                  # 使用calculator计算daily_cost
                  > calculator {{"daily_costs": [1947, 450, 0, 498], "operation": "sum"}}
                  < 2895  # 这个值就是daily_cost
                  ```
               
               c. 计算总花费(total_cost)：
                  - 收集所有daily_cost
                  - 使用 calculator 工具计算总和
                  示例：
                  ```
                  # 假设三天行程的daily_cost分别是：
                  第1天: daily_cost = 2895
                  第2天: daily_cost = 933
                  第3天: daily_cost = 2427
                  
                  # 使用calculator计算total_cost
                  > calculator {{"daily_costs": [2895, 933, 2427], "operation": "sum"}}
                  < 6255  # 这个值就是total_cost
                  ```
               
               d. 注意事项：
                  - 每个活动都必须有具体的cost值
                  - 每个daily_cost必须使用calculator工具计算
                  - total_cost必须使用calculator工具计算
                  - 禁止手动计算或跳过计算步骤
            
            3. 每个活动的content字段描述必须包含天气情况。
             
            正确示例：
             
               交通类：
               - weather_notice为"小雨"时：
                 content: "今天下午有小雨，建议您带伞并提前出发。下午3点的G32次高铁从杭州东站出发，约4.5小时可到达北京南站，二等座票价649元。"

               景点类：
               - weather_notice为"晴朗"时：
                 content: "今天阳光明媚，是游览西湖的绝佳时节！上午9点开始漫步苏堤春晓，您可以欣赏西湖十景，感受诗情画意的江南美景，免费开放。"

               餐饮类：
               - weather_notice为"寒冷"时：
                 content: "天气较冷，正适合品尝一些暖身的杭帮菜。晚上6点在知味观用餐，推荐您尝试热气腾腾的叫化童鸡和西湖醋鱼，人均150元。"

               住宿类：
               - weather_notice为"阴天"时：
                 content: "今晚天气阴沉，已为您预订了温馨舒适的酒店。入住西湖边的杭州大酒店豪华湖景房，您可以在房间欣赏西湖夜景，含双早，498元/晚。"             
            
            4. 所有输出必须严格遵循指定的JSON格式。
            """),
            ("human", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])
        
        # 创建 agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def create_plan(self, user_input: Dict) -> Dict:
        """创建旅行计划"""
        try:
            # 定义期望的JSON结构
            json_structure = '''{
                "departure": "出发地",
                "destination": "目的地",
                "duration": "行程天数(数字)",
                "budget": "预算(数字)",
                "total_cost": "总花费",
                
                "daily_plans": [
                    {
                        "date": "日期",
                        "weather": "天气情况",
                        "activities": [
                            {
                                "time": "活动时间段",
                                "activity_type": "景点/餐饮/交通/住宿",
                                "name": "活动名称",
                                "description": "活动描述",
                                "weather_notice": "天气建议",
                                "cost": "预计花费(数字)",
                            }
                        ],
                        "daily_cost": "当日总花费(数字)"
                    }
                ],
            
                "travel_style": "旅行风格",
                "accommodation_level": "住宿等级",
                "summary": "旅行总结，需要包含以下内容：
                    1. 吸引人的标题（例如：'魔都上海3日游 | 现代与传统的完美邂逅🌃'）
                    2. 行程亮点（3-5个emoji+文字描述）
                    3. 建议和提醒（交通、住宿、美食等实用信息）
                    4. 适合人群
                    格式要活泼生动，适合社交媒体分享"
            }'''

            # 准备输入数据
            input_message = f"""请根据以下信息制定旅行计划：
            
            基本信息：
            - 出发地：{user_input["departure"]}
            - 目的地：{user_input["destination"]}
            - 日期：{user_input["start_date"]} 至 {user_input["end_date"]}
            - 人数：{user_input["travelers"]}
            - 总预算：{user_input["budget"]}元
            
            用户偏好：
            - 旅行风格：{user_input.get("preferences", {}).get("style", "休闲")}
            - 住宿等级：{user_input.get("preferences", {}).get("accommodation_level", "民宿")}
            
            请先查询天气，再根据天气情况制定合适的行程。
            请直接返回JSON对象，不要包含任何其他格式标记。
            除了详细的行程安排外，还需要生成一段类似小红书风格的旅行总结，放在summary字段中。
            总结要突出行程特色，文案要活泼生动，适合分享。
            
            {json_structure}
            """

            # 使用 Agent 生成计划
            result = self.agent_executor.invoke({
                "input": input_message,
                "schema": TravelPlan.schema()
            })

            # 记录原始输出以便调试
            logger.info(f"Agent 原始输出: {result['output']}")

            # 如果返回的是带有代码块的字符串，提取JSON部分
            output = result["output"]
            if isinstance(output, str):
                # 尝试直接解析
                try:
                    import json
                    plan_data = json.loads(output)
                    
                    # 使用用户输入的预算
                    plan_data["budget"] = float(user_input["budget"])
                    
                    # 计算每日花费和总花费
                    for day in plan_data.get("daily_plans", []):
                        day["daily_cost"] = sum(
                            activity["cost"] 
                            for activity in day.get("activities", [])
                        )
                    
                    # 计算total_cost
                    plan_data["total_cost"] = sum(
                        day["daily_cost"] 
                        for day in plan_data.get("daily_plans", [])
                    )
                    
                    return plan_data
                    
                except json.JSONDecodeError:
                    # 如果直接解析失败，尝试提取代码块
                    if "```" in output:
                        blocks = output.split("```")
                        for block in reversed(blocks):
                            if block.strip():
                                try:
                                    if "json" in block:
                                        block = block.split("json")[-1]
                                    plan_data = json.loads(block.strip())
                                    
                                    # 使用用户输入的预算
                                    plan_data["budget"] = float(user_input["budget"])
                                    
                                    # 计算每日花费和总花费
                                    for day in plan_data.get("daily_plans", []):
                                        day["daily_cost"] = sum(
                                            activity["cost"] 
                                            for activity in day.get("activities", [])
                                        )
                                    
                                    # 计算total_cost
                                    plan_data["total_cost"] = sum(
                                        day["daily_cost"] 
                                        for day in plan_data.get("daily_plans", [])
                                    )
                    
                                    return plan_data
                                except json.JSONDecodeError:
                                    continue

                    logger.error(f"无法解析的输出: {output}")
                    raise ValueError("无法解析为有效的JSON格式")
            
            # 如果输出已经是字典
            if isinstance(output, dict):
                # 使用用户输入的预算
                output["budget"] = float(user_input["budget"])
                
                # 计算每日花费和总花费
                for day in output.get("daily_plans", []):
                    day["daily_cost"] = sum(
                        activity["cost"] 
                        for activity in day.get("activities", [])
                    )
                
                # 计算total_cost
                output["total_cost"] = sum(
                    day["daily_cost"] 
                    for day in output.get("daily_plans", [])
                )
            
            return output
            
        except Exception as e:
            logger.error(f"生成旅行计划失败: {str(e)}")
            logger.error("详细错误信息: ", exc_info=True)
            return {
                "error": True,
                "message": f"生成旅行计划失败: {str(e)}"
            }

    
